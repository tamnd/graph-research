# Aerospike Graph transactions, distribution, and failure audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
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

## Distribution boundaries

- AGS compute instances do not own shards and do not coordinate query state with one another.
- The Aerospike client discovers the database cluster and maps record digests to partitions/nodes.
- Database partitioning and replication provide storage distribution; adding AGS only increases compute/client pressure until the database saturates.
- Rack-aware client preference can reduce cross-zone reads but must be paired with database rack configuration and measured fallback behavior.
- Rebalance/migration affects where records live; correctness tests must run while topology changes, not only before and after.
- SC availability under partition differs from AP availability; latency SLOs need explicit minority/majority behavior.
- Cross-region active-active or XDR semantics are separate from local cluster transactions and must not be inferred from `distributed` branding.
- Object-storage durability is not involved in acknowledged online writes.

## Consistency and failure qualification cases

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — failure: read after vertex write

- Purpose: Measure stale-read window on same and different AGS instances.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `read after vertex write`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — failure: read during edge add

- Purpose: Detect impossible half-edge/path observations.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `read during edge add`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — failure: read during edge delete

- Purpose: Detect stale adjacency and edge-record disappearance ordering.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `read during edge delete`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — failure: read during vertex drop

- Purpose: Detect orphan or partially removed incident edges.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `read during vertex drop`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — failure: AP addV

- Purpose: Validate documented single-element atomic behavior.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP addV`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — failure: AP property update

- Purpose: Validate generation and last-write behavior.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP property update`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — failure: AP addE

- Purpose: Exercise three-record partial-failure path.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP addE`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — failure: AP dropE

- Purpose: Exercise record-first delete and cleanup.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP dropE`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — failure: AP dropV

- Purpose: Exercise many-record eventual cleanup.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP dropV`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — failure: AP mergeV

- Purpose: Validate documented atomic case and match ambiguity.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP mergeV`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — failure: AP mergeE

- Purpose: Exercise lock record and partial graph update.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP mergeE`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — failure: AP cluster split

- Purpose: Quantify lost/conflicting graph mutations after heal.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AP cluster split`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — failure: SC point write

- Purpose: Establish namespace SC latency baseline.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC point write`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — failure: SC addE without MRT

- Purpose: Prove SC alone does not imply graph-level atomicity.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC addE without MRT`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — failure: SC addE with MRT

- Purpose: Prove all-or-nothing packed-edge and endpoint update.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC addE with MRT`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — failure: SC dropE with MRT

- Purpose: Prove all-or-nothing removal within record budget.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC dropE with MRT`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — failure: SC drop ordinary vertex

- Purpose: Count records and confirm atomic completion.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC drop ordinary vertex`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — failure: SC drop supernode

- Purpose: Record documented best-effort exception.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `SC drop supernode`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — failure: TinkerPop two vertices/two edges

- Purpose: Reproduce official all-or-nothing example.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop two vertices/two edges`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — failure: TinkerPop rollback

- Purpose: Verify no visible data and correct ID recycling.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop rollback`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — failure: TinkerPop timeout

- Purpose: Verify server rollback and lock release.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop timeout`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — failure: TinkerPop 4096 records

- Purpose: Confirm exact accepted boundary.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop 4096 records`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — failure: TinkerPop 4097 records

- Purpose: Confirm clean rejection/rollback.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop 4097 records`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — failure: TinkerPop indexed read

- Purpose: Verify documented prohibition.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop indexed read`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — failure: TinkerPop scan

- Purpose: Verify documented prohibition.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop scan`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — failure: TinkerPop ID read

- Purpose: Verify allowed record addressing.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop ID read`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — failure: TinkerPop parallelize

- Purpose: Verify explicit incompatibility.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `TinkerPop parallelize`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — failure: same-vertex contention

- Purpose: Measure blocking, aborts, retries, and fairness.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `same-vertex contention`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — failure: same-packed-edge contention

- Purpose: Expose false contention from edge packing.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `same-packed-edge contention`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — failure: disjoint writes

- Purpose: Establish scalable transaction throughput.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `disjoint writes`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — failure: hot supernode writes

- Purpose: Measure sindex/record contention and retry storms.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `hot supernode writes`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — failure: client retry idempotence

- Purpose: Prevent duplicate addV/addE after ambiguous timeout.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `client retry idempotence`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — failure: commit response loss

- Purpose: Resolve unknown commit outcome safely.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `commit response loss`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — failure: AGS kill before commit

- Purpose: Verify transaction timeout/rollback and IDs.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AGS kill before commit`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — failure: AGS kill after commit

- Purpose: Verify acknowledged state and cache effects.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `AGS kill after commit`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — failure: database leader kill

- Purpose: Measure transaction outcome and tail latency.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `database leader kill`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — failure: database replica kill

- Purpose: Measure RF2 resilience and rebuild load.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `database replica kill`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — failure: network drop AGS-to-DB

- Purpose: Verify timeouts, retry budget, and cancellation.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `network drop AGS-to-DB`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — failure: network delay AGS-to-DB

- Purpose: Expose retry amplification and tail collapse.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `network delay AGS-to-DB`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — failure: minority partition AP

- Purpose: Document availability and later conflict behavior.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `minority partition AP`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — failure: minority partition SC

- Purpose: Document unavailable partitions and error surface.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `minority partition SC`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — failure: majority partition SC

- Purpose: Measure commit latency and fencing.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `majority partition SC`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — failure: split heal

- Purpose: Verify no resurrection/orphan paths after migrations.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `split heal`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — failure: rolling DB restart

- Purpose: Measure availability and read consistency throughout.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `rolling DB restart`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — failure: rolling AGS restart

- Purpose: Verify stateless handoff and load-balancer draining.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `rolling AGS restart`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — failure: add DB node

- Purpose: Measure migration impact on p99.9 and correctness.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `add DB node`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — failure: remove DB node

- Purpose: Measure safe migration and capacity headroom.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `remove DB node`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — failure: add AGS node

- Purpose: Verify no warm-state dependence and load distribution.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `add AGS node`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — failure: remove AGS node

- Purpose: Verify in-flight query/transaction behavior.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `remove AGS node`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — failure: rack-local replica

- Purpose: Measure preferred-rack hit rate.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `rack-local replica`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — failure: rack loss

- Purpose: Measure fallback replica selection and cross-zone cost.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `rack loss`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — failure: XDR normal mutation

- Purpose: Measure remote lag and graph record ordering.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `XDR normal mutation`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — failure: XDR edge mutation

- Purpose: Detect remote partial graph visibility.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `XDR edge mutation`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — failure: XDR conflict

- Purpose: Document conflict resolution for related records.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `XDR conflict`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — failure: backup during writes

- Purpose: Prove graph-consistent restore or document quiesce requirement.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `backup during writes`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — failure: restore transaction metadata

- Purpose: Ensure no provisional/locked state leaks.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `restore transaction metadata`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — failure: clock skew

- Purpose: Exercise TTL, transaction duration, and trace timestamps.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `clock skew`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — failure: disk full

- Purpose: Verify failed graph writes remain invisible and cluster recoverable.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `disk full`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — failure: record too large

- Purpose: Verify transaction rollback at storage constraint.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `record too large`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — failure: secondary-index unavailable

- Purpose: Verify startup/query behavior for supernodes.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `secondary-index unavailable`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q061 — failure: summary lag

- Purpose: Ensure optimizer metadata does not affect correctness.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `summary lag`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q062 — failure: global cache plus mutation

- Purpose: Expose consistency weaker than database mode.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `global cache plus mutation`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q063 — failure: load balancer retry

- Purpose: Prevent replay of non-idempotent mutation bytecode.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `load balancer retry`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q064 — failure: session transaction routing

- Purpose: Ensure every scope operation reaches the correct AGS session.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `session transaction routing`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q065 — failure: transaction abandonment

- Purpose: Release locks after client disappears.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `transaction abandonment`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q066 — failure: transaction starvation

- Purpose: Measure hot-key fairness and bounded retry.
- Setup: Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.
- Workload: Execute the smallest semantically complete operation for `transaction starvation`, then repeat under controlled concurrency and skew.
- Required counters: operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S04 — AGS 3.2.1 release notes

- Type: Official documentation
- Audit note: Container memory and rack awareness
- URL: https://aerospike.com/docs/graph/release/3-2-1/

### S09 — Architecture

- Type: Official documentation
- Audit note: Three-layer request path
- URL: https://aerospike.com/docs/graph/overview/architecture/

### S10 — Transaction contract

- Type: Official documentation
- Audit note: Read, mutation, SC, AP, and MRT distinctions
- URL: https://aerospike.com/docs/graph/develop/query/transactions/

### S22 — Graph backup and restore

- Type: Official documentation
- Audit note: Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page
- URL: https://aerospike.com/docs/graph/manage/backup/

### S28 — Product editions and pricing

- Type: Official commercial page
- Audit note: Edition limits and data-volume licensing
- URL: https://aerospike.com/products/features-and-editions/

### S29 — Database platform support

- Type: Official documentation
- Audit note: Current Database release matrix
- URL: https://aerospike.com/docs/database/reference/platform-support

### S30 — Database limits

- Type: Official documentation
- Audit note: Cluster and object limits
- URL: https://aerospike.com/docs/database/reference/limitations/

### S32 — Database FAQ

- Type: Official documentation
- Audit note: CE/SE/EE/FE boundaries
- URL: https://aerospike.com/docs/database/reference/faq

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S36 — AGS AerospikeOperations

- Type: Apache-2.0 source
- Audit note: Read/write and edge mutation pipeline
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java

### S37 — AGS configuration source

- Type: Apache-2.0 source
- Audit note: Code defaults and validators
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java

### S40 — AGS transaction implementation

- Type: Apache-2.0 source
- Audit note: TinkerPop transaction wrapper
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java

### S43 — Database server source snapshot

- Type: AGPL/community core source
- Audit note: Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc
- URL: https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

### S44 — Java client source snapshot

- Type: Apache-2.0 source
- Audit note: Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
- URL: https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
