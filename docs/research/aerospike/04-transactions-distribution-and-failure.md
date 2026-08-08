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

### Transaction scope seen in source

The public transaction class begins with a narrow declaration:

```java
public class FireflyTransaction extends AbstractThreadLocalTransaction
```

The extract is from
[`FireflyTransaction.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java).
The thread-local base matches TinkerPop session processing and maps the active
scope to the Aerospike Java client transaction. It does not turn every Gremlin
request into a transaction. Both relevant AGS flags default to false in the
pinned source, released documentation requires an SC namespace and Database 8
Enterprise support for the advertised multi-record path, and an explicit
transaction cannot discover its working set through scans or indexes. IDs are
resolved first, then the bounded set of records is touched inside the scope.

An edge add illustrates why record accounting matters. The logical operation
can touch a packed edge record and both endpoint vertex records. If a packed
record is already transaction-blocked, the implementation can move to another
packing ID and retry. The 4096-record Database transaction limit therefore
constrains graph operations indirectly: one logical vertex drop may consume
multiple record operations per incident edge, and packed-record collisions can
change the attempted key set. The configuration source uses a smaller edge
bound for transactional vertex deletion rather than assuming that 4096 logical
elements fit.

Read semantics stay separate. Released guidance classifies read-only graph
queries as eventually consistent even when mutation transactions are enabled.
A multi-hop traversal can overlap concurrent mutation and does not automatically
bind every record read to one database-wide snapshot. A correctness harness
must record impossible path observations, stale endpoint properties, and
read-after-write behavior across the same and different AGS instances. Passing
an atomic mutation test does not prove snapshot-consistent traversal.

| Mode | Mutation guarantee to test | Read guarantee to test | Failure question |
| --- | --- | --- | --- |
| AP without MRT | Enumerated single-record atomicity only | Eventual visibility | Can a split lose or strand part of a graph mutation? |
| SC without AGS MRT | Strong record behavior, not automatic graph-wide atomicity | Eventual graph reads | Do generation conflicts and retries preserve adjacency? |
| SC plus mutation MRT | Atomic bounded record set for one mutation iteration | Still test stale multi-record reads | What happens on conflict, timeout, or process death before acknowledgement? |
| Explicit TinkerPop transaction | Session-bound scope, no scans or index queries, 4096-record ceiling | Reads within documented transaction behavior | Are locks released on every rollback, timeout, and disconnect path? |
| XDR or cross-region replication | Asynchronous remote application | Remote freshness is topology dependent | Can related graph records arrive or conflict in different order? |

The failure harness records invocation and completion times, client operation IDs, AGS instance, Database partition ownership, record generations, transaction IDs, retries, and the raw state of every touched graph record. A separate history checker evaluates acknowledgement, atomicity, isolation, read visibility, and convergence. RF2 and RF3, AP and SC, MRT disabled and enabled, and same-AGS versus cross-AGS reads are distinct runs.

Faults are injected during the operation rather than only between phases. The catalog includes process death, node loss, network partition, migration, restart, backup, and restore. A timed-out operation is unresolved until the final state is inspected. Retrying an unresolved mutation with no idempotency analysis can create a second edge, so the retry itself belongs in the recorded history.

<table>
<thead>
<tr>
<th>Case</th>
<th>Subject</th>
<th>Engineering question</th>
<th>Evidence</th>
</tr>
</thead>
<tbody>
<tr>
<td>Q001</td>
<td>failure: read after vertex write</td>
<td>Measure stale-read window on same and different AGS instances.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q002</td>
<td>failure: read during edge add</td>
<td>Detect impossible half-edge/path observations.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q003</td>
<td>failure: read during edge delete</td>
<td>Detect stale adjacency and edge-record disappearance ordering.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q004</td>
<td>failure: read during vertex drop</td>
<td>Detect orphan or partially removed incident edges.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q005</td>
<td>failure: AP addV</td>
<td>Validate documented single-element atomic behavior.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q006</td>
<td>failure: AP property update</td>
<td>Validate generation and last-write behavior.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q007</td>
<td>failure: AP addE</td>
<td>Exercise three-record partial-failure path.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q008</td>
<td>failure: AP dropE</td>
<td>Exercise record-first delete and cleanup.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q009</td>
<td>failure: AP dropV</td>
<td>Exercise many-record eventual cleanup.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q010</td>
<td>failure: AP mergeV</td>
<td>Validate documented atomic case and match ambiguity.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q011</td>
<td>failure: AP mergeE</td>
<td>Exercise lock record and partial graph update.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q012</td>
<td>failure: AP cluster split</td>
<td>Quantify lost/conflicting graph mutations after heal.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q013</td>
<td>failure: SC point write</td>
<td>Establish namespace SC latency baseline.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q014</td>
<td>failure: SC addE without MRT</td>
<td>Prove SC alone does not imply graph-level atomicity.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q015</td>
<td>failure: SC addE with MRT</td>
<td>Prove all-or-nothing packed-edge and endpoint update.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q016</td>
<td>failure: SC dropE with MRT</td>
<td>Prove all-or-nothing removal within record budget.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q017</td>
<td>failure: SC drop ordinary vertex</td>
<td>Count records and confirm atomic completion.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q018</td>
<td>failure: SC drop supernode</td>
<td>Record documented best-effort exception.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q019</td>
<td>failure: TinkerPop two vertices/two edges</td>
<td>Reproduce official all-or-nothing example.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q020</td>
<td>failure: TinkerPop rollback</td>
<td>Verify no visible data and correct ID recycling.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q021</td>
<td>failure: TinkerPop timeout</td>
<td>Verify server rollback and lock release.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q022</td>
<td>failure: TinkerPop 4096 records</td>
<td>Confirm exact accepted boundary.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q023</td>
<td>failure: TinkerPop 4097 records</td>
<td>Confirm clean rejection/rollback.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q024</td>
<td>failure: TinkerPop indexed read</td>
<td>Verify documented prohibition.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q025</td>
<td>failure: TinkerPop scan</td>
<td>Verify documented prohibition.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q026</td>
<td>failure: TinkerPop ID read</td>
<td>Verify allowed record addressing.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q027</td>
<td>failure: TinkerPop parallelize</td>
<td>Verify explicit incompatibility.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q028</td>
<td>failure: same-vertex contention</td>
<td>Measure blocking, aborts, retries, and fairness.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q029</td>
<td>failure: same-packed-edge contention</td>
<td>Expose false contention from edge packing.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q030</td>
<td>failure: disjoint writes</td>
<td>Establish scalable transaction throughput.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q031</td>
<td>failure: hot supernode writes</td>
<td>Measure sindex/record contention and retry storms.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q032</td>
<td>failure: client retry idempotence</td>
<td>Prevent duplicate addV/addE after ambiguous timeout.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q033</td>
<td>failure: commit response loss</td>
<td>Resolve unknown commit outcome safely.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q034</td>
<td>failure: AGS kill before commit</td>
<td>Verify transaction timeout/rollback and IDs.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q035</td>
<td>failure: AGS kill after commit</td>
<td>Verify acknowledged state and cache effects.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q036</td>
<td>failure: database leader kill</td>
<td>Measure transaction outcome and tail latency.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q037</td>
<td>failure: database replica kill</td>
<td>Measure RF2 resilience and rebuild load.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q038</td>
<td>failure: network drop AGS-to-DB</td>
<td>Verify timeouts, retry budget, and cancellation.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q039</td>
<td>failure: network delay AGS-to-DB</td>
<td>Expose retry amplification and tail collapse.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q040</td>
<td>failure: minority partition AP</td>
<td>Document availability and later conflict behavior.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q041</td>
<td>failure: minority partition SC</td>
<td>Document unavailable partitions and error surface.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q042</td>
<td>failure: majority partition SC</td>
<td>Measure commit latency and fencing.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q043</td>
<td>failure: split heal</td>
<td>Verify no resurrection/orphan paths after migrations.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q044</td>
<td>failure: rolling DB restart</td>
<td>Measure availability and read consistency throughout.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q045</td>
<td>failure: rolling AGS restart</td>
<td>Verify stateless handoff and load-balancer draining.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q046</td>
<td>failure: add DB node</td>
<td>Measure migration impact on p99.9 and correctness.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q047</td>
<td>failure: remove DB node</td>
<td>Measure safe migration and capacity headroom.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q048</td>
<td>failure: add AGS node</td>
<td>Verify no warm-state dependence and load distribution.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q049</td>
<td>failure: remove AGS node</td>
<td>Verify in-flight query/transaction behavior.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q050</td>
<td>failure: rack-local replica</td>
<td>Measure preferred-rack hit rate.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q051</td>
<td>failure: rack loss</td>
<td>Measure fallback replica selection and cross-zone cost.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q052</td>
<td>failure: XDR normal mutation</td>
<td>Measure remote lag and graph record ordering.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q053</td>
<td>failure: XDR edge mutation</td>
<td>Detect remote partial graph visibility.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q054</td>
<td>failure: XDR conflict</td>
<td>Document conflict resolution for related records.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q055</td>
<td>failure: backup during writes</td>
<td>Prove graph-consistent restore or document quiesce requirement.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q056</td>
<td>failure: restore transaction metadata</td>
<td>Ensure no provisional/locked state leaks.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q057</td>
<td>failure: clock skew</td>
<td>Exercise TTL, transaction duration, and trace timestamps.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q058</td>
<td>failure: disk full</td>
<td>Verify failed graph writes remain invisible and cluster recoverable.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q059</td>
<td>failure: record too large</td>
<td>Verify transaction rollback at storage constraint.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q060</td>
<td>failure: secondary-index unavailable</td>
<td>Verify startup/query behavior for supernodes.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q061</td>
<td>failure: summary lag</td>
<td>Ensure optimizer metadata does not affect correctness.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q062</td>
<td>failure: global cache plus mutation</td>
<td>Expose consistency weaker than database mode.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q063</td>
<td>failure: load balancer retry</td>
<td>Prevent replay of non-idempotent mutation bytecode.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q064</td>
<td>failure: session transaction routing</td>
<td>Ensure every scope operation reaches the correct AGS session.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q065</td>
<td>failure: transaction abandonment</td>
<td>Release locks after client disappears.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
<tr>
<td>Q066</td>
<td>failure: transaction starvation</td>
<td>Measure hot-key fairness and bounded retry.</td>
<td>S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44</td>
</tr>
</tbody>
</table>

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

<table>
<thead>
<tr>
<th>ID</th>
<th>Source</th>
<th>Class</th>
<th>Audit use</th>
<th>Link</th>
</tr>
</thead>
<tbody>
<tr>
<td>S04</td>
<td>AGS 3.2.1 release notes</td>
<td>Official documentation</td>
<td>Container memory and rack awareness</td>
<td>https://aerospike.com/docs/graph/release/3-2-1/</td>
</tr>
<tr>
<td>S09</td>
<td>Architecture</td>
<td>Official documentation</td>
<td>Three-layer request path</td>
<td>https://aerospike.com/docs/graph/overview/architecture/</td>
</tr>
<tr>
<td>S10</td>
<td>Transaction contract</td>
<td>Official documentation</td>
<td>Read, mutation, SC, AP, and MRT distinctions</td>
<td>https://aerospike.com/docs/graph/develop/query/transactions/</td>
</tr>
<tr>
<td>S22</td>
<td>Graph backup and restore</td>
<td>Official documentation</td>
<td>Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page</td>
<td>https://aerospike.com/docs/graph/manage/backup/</td>
</tr>
<tr>
<td>S28</td>
<td>Product editions and pricing</td>
<td>Official commercial page</td>
<td>Edition limits and data-volume licensing</td>
<td>https://aerospike.com/products/features-and-editions/</td>
</tr>
<tr>
<td>S29</td>
<td>Database platform support</td>
<td>Official documentation</td>
<td>Current Database release matrix</td>
<td>https://aerospike.com/docs/database/reference/platform-support</td>
</tr>
<tr>
<td>S30</td>
<td>Database limits</td>
<td>Official documentation</td>
<td>Cluster and object limits</td>
<td>https://aerospike.com/docs/database/reference/limitations/</td>
</tr>
<tr>
<td>S32</td>
<td>Database FAQ</td>
<td>Official documentation</td>
<td>CE/SE/EE/FE boundaries</td>
<td>https://aerospike.com/docs/database/reference/faq</td>
</tr>
<tr>
<td>S33</td>
<td>AGS public source snapshot</td>
<td>Apache-2.0 source</td>
<td>3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045</td>
</tr>
<tr>
<td>S36</td>
<td>AGS AerospikeOperations</td>
<td>Apache-2.0 source</td>
<td>Read/write and edge mutation pipeline</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java</td>
</tr>
<tr>
<td>S37</td>
<td>AGS configuration source</td>
<td>Apache-2.0 source</td>
<td>Code defaults and validators</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java</td>
</tr>
<tr>
<td>S40</td>
<td>AGS transaction implementation</td>
<td>Apache-2.0 source</td>
<td>TinkerPop transaction wrapper</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java</td>
</tr>
<tr>
<td>S43</td>
<td>Database server source snapshot</td>
<td>AGPL/community core source</td>
<td>Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
<td>https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
</tr>

<tr>
<td>S44</td>
<td>Java client source snapshot</td>
<td>Apache-2.0 source</td>
<td>Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12</td>
<td>https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12</td>
</tr>
</tbody>
</table>
