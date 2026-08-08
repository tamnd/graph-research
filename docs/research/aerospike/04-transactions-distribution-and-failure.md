# Aerospike Graph transactions, distribution, and failure audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Consistency modes, graph mutation atomicity, record transactions, partitions, replicas, and recovery
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Corrected consistency matrix

| Operation/mode | Released contract | Critical limitation |
| --- | --- | --- |
| Read-only traversal | Eventual consistency | May observe stale or internally inconsistent graph state during concurrent mutations |
| AP single-record-like mutations | Only documented enumerated steps are atomic/isolated | Cluster split can lose writes; graph-wide mutation shapes are not protected |
| AP addE/dropE/dropV | Eventual/retry-oriented | Multi-record endpoint/edge updates can be partial internally |
| SC without AGS MRT | Namespace SC does not automatically make a graph mutation multi-record atomic | Generation-check path and retries still matter |
| SC + aerospike.graph.mrt.enabled | Each mutation iteration that touches records can be atomic/isolated | Requires Enterprise 8.0+ per released docs; defaults false |
| SC + aerospike.graph.tx.enabled | Explicit client transaction scopes | No scans/indexes; 4096-record maximum; locks persist until close |
| Supernode vertex drop | Best effort | Exception to otherwise transactional mutation language |
| Cross-datacenter XDR | Asynchronous replication | Not synchronous graph transaction or zero-RPO evidence |

## Source mutation reconstruction

An edge logically spans at least three graph records: the packed edge record plus inbound and outbound vertex records when adjacency is inline. In the transaction path, `AerospikeOperations` creates or reuses an Aerospike `Txn`, writes the packed edge, then updates both vertices, and commits. If the target packed record is transaction-blocked, code recycles/changes the proposed edge ID and retries a different target pack.

In the no-transaction path, the source updates both endpoint adjacency caches first, then writes the edge record. Reads check that the edge record exists before exposing cached adjacency. That protects visible bidirectional consistency but can strand edge-ID bytes in a vertex if cleanup fails. This is a deliberate availability/storage-leak tradeoff, not ACID.

TinkerPop transactions are thread-local/session-bound wrappers around the Java client's multi-record transaction object. The code stages edge IDs for recycling according to commit/rollback outcome. Released docs add stricter constraints: resolve indexed IDs outside the transaction, touch at most 4096 records, keep scopes short, and retry contention.

Both transaction switches are false by default in the audited configuration source. A deployment that expects atomic graph mutation must make the choice explicit and verify that the namespace and commercial entitlement support it.

```properties
aerospike.graph.mrt.enabled=true
aerospike.graph.tx.enabled=true
```

An explicit Gremlin transaction should remain small and ID-rooted. Index and scan discovery belongs before the transaction because the released contract does not allow those operations inside the scope.

```groovy
tx = g.tx()
tx.begin()
try {
    a = g.V(accountA).next()
    b = g.V(accountB).next()
    a.addEdge('transferredTo', b, 'amountCents', 12500L)
    tx.commit()
} catch (Throwable failure) {
    tx.rollback()
    throw failure
} finally {
    tx.close()
}
```

This example is not a claim of arbitrary distributed serializability. It is a test fixture for the bounded record transaction that AGS exposes. The history checker still needs to verify acknowledgement, conflict, retry, read visibility, rollback, and state after node failure.

## Distribution boundaries

AGS compute instances do not own shards and do not coordinate query state with one another. The Aerospike client discovers the Database cluster and maps record digests to partitions and nodes. Database partitioning and replication provide the storage distribution. Adding AGS instances increases query compute and client concurrency only until the Database tier becomes the bottleneck.

Rack-aware client preference can reduce cross-zone reads when the Database rack configuration agrees with it. Fallback behavior still has to be measured. Rebalance and migration change record placement, so correctness and tail-latency tests must run during topology changes rather than only before and after them.

SC and AP make different availability choices during a partition. Cross-region active-active or XDR behavior is separate from local multi-record transactions and cannot be inferred from the word distributed. Object-store durability is not part of the acknowledged online write path.

## Consistency and failure qualification cases

The failure harness records invocation and completion times, client operation IDs, AGS instance, Database partition ownership, record generations, transaction IDs, retries, and the raw state of every touched graph record. A separate history checker evaluates acknowledgement, atomicity, isolation, read visibility, and convergence. RF2 and RF3, AP and SC, MRT disabled and enabled, and same-AGS versus cross-AGS reads are distinct runs.

Faults are injected during the operation rather than only between phases. The catalog includes process death, node loss, network partition, migration, restart, backup, and restore. A timed-out operation is unresolved until the final state is inspected. Retrying an unresolved mutation with no idempotency analysis can create a second edge, so the retry itself belongs in the recorded history.

### Q001 : failure: read after vertex write

**Purpose.** Measure stale-read window on same and different AGS instances.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q002 : failure: read during edge add

**Purpose.** Detect impossible half-edge/path observations.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q003 : failure: read during edge delete

**Purpose.** Detect stale adjacency and edge-record disappearance ordering.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q004 : failure: read during vertex drop

**Purpose.** Detect orphan or partially removed incident edges.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q005 : failure: AP addV

**Purpose.** Validate documented single-element atomic behavior.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q006 : failure: AP property update

**Purpose.** Validate generation and last-write behavior.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q007 : failure: AP addE

**Purpose.** Exercise three-record partial-failure path.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q008 : failure: AP dropE

**Purpose.** Exercise record-first delete and cleanup.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q009 : failure: AP dropV

**Purpose.** Exercise many-record eventual cleanup.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q010 : failure: AP mergeV

**Purpose.** Validate documented atomic case and match ambiguity.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q011 : failure: AP mergeE

**Purpose.** Exercise lock record and partial graph update.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q012 : failure: AP cluster split

**Purpose.** Quantify lost/conflicting graph mutations after heal.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q013 : failure: SC point write

**Purpose.** Establish namespace SC latency baseline.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q014 : failure: SC addE without MRT

**Purpose.** Prove SC alone does not imply graph-level atomicity.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q015 : failure: SC addE with MRT

**Purpose.** Prove all-or-nothing packed-edge and endpoint update.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q016 : failure: SC dropE with MRT

**Purpose.** Prove all-or-nothing removal within record budget.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q017 : failure: SC drop ordinary vertex

**Purpose.** Count records and confirm atomic completion.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q018 : failure: SC drop supernode

**Purpose.** Record documented best-effort exception.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q019 : failure: TinkerPop two vertices/two edges

**Purpose.** Reproduce official all-or-nothing example.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q020 : failure: TinkerPop rollback

**Purpose.** Verify no visible data and correct ID recycling.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q021 : failure: TinkerPop timeout

**Purpose.** Verify server rollback and lock release.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q022 : failure: TinkerPop 4096 records

**Purpose.** Confirm exact accepted boundary.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q023 : failure: TinkerPop 4097 records

**Purpose.** Confirm clean rejection/rollback.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q024 : failure: TinkerPop indexed read

**Purpose.** Verify documented prohibition.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q025 : failure: TinkerPop scan

**Purpose.** Verify documented prohibition.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q026 : failure: TinkerPop ID read

**Purpose.** Verify allowed record addressing.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q027 : failure: TinkerPop parallelize

**Purpose.** Verify explicit incompatibility.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q028 : failure: same-vertex contention

**Purpose.** Measure blocking, aborts, retries, and fairness.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q029 : failure: same-packed-edge contention

**Purpose.** Expose false contention from edge packing.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q030 : failure: disjoint writes

**Purpose.** Establish scalable transaction throughput.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q031 : failure: hot supernode writes

**Purpose.** Measure sindex/record contention and retry storms.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q032 : failure: client retry idempotence

**Purpose.** Prevent duplicate addV/addE after ambiguous timeout.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q033 : failure: commit response loss

**Purpose.** Resolve unknown commit outcome safely.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q034 : failure: AGS kill before commit

**Purpose.** Verify transaction timeout/rollback and IDs.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q035 : failure: AGS kill after commit

**Purpose.** Verify acknowledged state and cache effects.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q036 : failure: database leader kill

**Purpose.** Measure transaction outcome and tail latency.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q037 : failure: database replica kill

**Purpose.** Measure RF2 resilience and rebuild load.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q038 : failure: network drop AGS-to-DB

**Purpose.** Verify timeouts, retry budget, and cancellation.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q039 : failure: network delay AGS-to-DB

**Purpose.** Expose retry amplification and tail collapse.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q040 : failure: minority partition AP

**Purpose.** Document availability and later conflict behavior.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q041 : failure: minority partition SC

**Purpose.** Document unavailable partitions and error surface.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q042 : failure: majority partition SC

**Purpose.** Measure commit latency and fencing.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q043 : failure: split heal

**Purpose.** Verify no resurrection/orphan paths after migrations.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q044 : failure: rolling DB restart

**Purpose.** Measure availability and read consistency throughout.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q045 : failure: rolling AGS restart

**Purpose.** Verify stateless handoff and load-balancer draining.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q046 : failure: add DB node

**Purpose.** Measure migration impact on p99.9 and correctness.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q047 : failure: remove DB node

**Purpose.** Measure safe migration and capacity headroom.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q048 : failure: add AGS node

**Purpose.** Verify no warm-state dependence and load distribution.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q049 : failure: remove AGS node

**Purpose.** Verify in-flight query/transaction behavior.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q050 : failure: rack-local replica

**Purpose.** Measure preferred-rack hit rate.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q051 : failure: rack loss

**Purpose.** Measure fallback replica selection and cross-zone cost.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q052 : failure: XDR normal mutation

**Purpose.** Measure remote lag and graph record ordering.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q053 : failure: XDR edge mutation

**Purpose.** Detect remote partial graph visibility.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q054 : failure: XDR conflict

**Purpose.** Document conflict resolution for related records.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q055 : failure: backup during writes

**Purpose.** Prove graph-consistent restore or document quiesce requirement.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q056 : failure: restore transaction metadata

**Purpose.** Ensure no provisional/locked state leaks.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q057 : failure: clock skew

**Purpose.** Exercise TTL, transaction duration, and trace timestamps.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q058 : failure: disk full

**Purpose.** Verify failed graph writes remain invisible and cluster recoverable.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q059 : failure: record too large

**Purpose.** Verify transaction rollback at storage constraint.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q060 : failure: secondary-index unavailable

**Purpose.** Verify startup/query behavior for supernodes.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q061 : failure: summary lag

**Purpose.** Ensure optimizer metadata does not affect correctness.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q062 : failure: global cache plus mutation

**Purpose.** Expose consistency weaker than database mode.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q063 : failure: load balancer retry

**Purpose.** Prevent replay of non-idempotent mutation bytecode.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q064 : failure: session transaction routing

**Purpose.** Ensure every scope operation reaches the correct AGS session.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q065 : failure: transaction abandonment

**Purpose.** Release locks after client disappears.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


### Q066 : failure: transaction starvation

**Purpose.** Measure hot-key fairness and bounded retry.

**Evidence anchors.** S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44


## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S04 : AGS 3.2.1 release notes

**Type.** Official documentation

**Audit note.** Container memory and rack awareness

**URL.** https://aerospike.com/docs/graph/release/3-2-1/


### S09 : Architecture

**Type.** Official documentation

**Audit note.** Three-layer request path

**URL.** https://aerospike.com/docs/graph/overview/architecture/


### S10 : Transaction contract

**Type.** Official documentation

**Audit note.** Read, mutation, SC, AP, and MRT distinctions

**URL.** https://aerospike.com/docs/graph/develop/query/transactions/


### S22 : Graph backup and restore

**Type.** Official documentation

**Audit note.** Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page

**URL.** https://aerospike.com/docs/graph/manage/backup/


### S28 : Product editions and pricing

**Type.** Official commercial page

**Audit note.** Edition limits and data-volume licensing

**URL.** https://aerospike.com/products/features-and-editions/


### S29 : Database platform support

**Type.** Official documentation

**Audit note.** Current Database release matrix

**URL.** https://aerospike.com/docs/database/reference/platform-support


### S30 : Database limits

**Type.** Official documentation

**Audit note.** Cluster and object limits

**URL.** https://aerospike.com/docs/database/reference/limitations/


### S32 : Database FAQ

**Type.** Official documentation

**Audit note.** CE/SE/EE/FE boundaries

**URL.** https://aerospike.com/docs/database/reference/faq


### S33 : AGS public source snapshot

**Type.** Apache-2.0 source

**Audit note.** 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045


### S36 : AGS AerospikeOperations

**Type.** Apache-2.0 source

**Audit note.** Read/write and edge mutation pipeline

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java


### S37 : AGS configuration source

**Type.** Apache-2.0 source

**Audit note.** Code defaults and validators

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java


### S40 : AGS transaction implementation

**Type.** Apache-2.0 source

**Audit note.** TinkerPop transaction wrapper

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java


### S43 : Database server source snapshot

**Type.** AGPL/community core source

**Audit note.** Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

**URL.** https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc


### S44 : Java client source snapshot

**Type.** Apache-2.0 source

**Audit note.** Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12

**URL.** https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
