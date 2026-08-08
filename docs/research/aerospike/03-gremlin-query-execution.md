# Aerospike Graph Gremlin compiler and query-execution audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: TinkerPop surface, traversal rewrites, storage I/O, batching, pagination, parallelism, caching, and observability
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Execution conclusion

AGS is not a declarative cost-based graph optimizer in the relational sense. TinkerPop builds a traversal, and AGS applies provider strategies that recognize specific step shapes and replace or fold them into Aerospike-aware steps. Performance therefore depends on syntactic traversal shape, IDs versus scans, placement of has/limit/sample/count, property projection, ordinary versus supernode adjacency, supported predicate types, and whether a rewrite fires.

The source exposes strategies for graph-step folding, batch vertex/edge reads, edge-to-vertex and otherV batching, adjacent-ID shortcuts, cached reads, graph/local counts, filter pushdown, hasId, drop, merge, elementMap, query tracing, scan profiling, and verification. The benchmark must capture the optimized traversal/profile and backend operation counts so a fast result cannot be attributed vaguely to "Gremlin optimization."

## Read-path classes and decisions

- Gremlin bytecode arrives through TinkerPop Gremlin Server over WebSocket.
- Provider strategies rewrite eligible traversals before iterator execution.
- ID-rooted vertex lookup becomes a direct Aerospike record read.
- Multiple known IDs can become an Aerospike batch read split by cluster node.
- Vertex has()/hasLabel() can use a secondary index when a compatible index exists.
- Remaining predicates may compile into Aerospike filter expressions for server-side rejection.
- Ordinary vertex adjacency can skip individual edge materialization for out()/in() shapes that only need adjacent vertices.
- Supernode adjacency starts with specialized secondary-index queries against edge records.
- Global scans use paged query machinery and are qualitatively more expensive than point/bounded paths.
- Per-query parallelization draws from a shared executor and is disallowed in transaction traversals.
- The default record cache is transaction/request local; the global mode is shared within one graph instance and may be stale.
- Query results themselves are not cached by the AGS cache feature.

## Key source defaults observed at the pinned commit

| Control | Source default | Audit consequence |
| --- | --- | --- |
| scan enabled | true | Production should normally disable accidental scans and opt in explicitly |
| read socket / total timeout | 150 ms / 450 ms | Retry multiplication and tail clipping must be reported |
| write socket / total timeout | 500 ms / 2500 ms | Not an SLA by itself |
| max retries | 2 | Count attempts and both successful/failed user requests |
| batch flat size | 0 | Per-node control applies |
| batch size per node | 20 | Total batch grows with DB node count |
| batch threshold per node | 1 | Affects single versus batch path |
| pagination flat page | 0 | Per-node page applies |
| pagination page per node | 200 | Total in-flight data grows with cluster |
| pagination queue | 10 | Backpressure/memory dimension |
| cache mode | TRANSACTIONAL | Reset per traversal |
| cache weight | 1,000,000 | Weight is not raw bytes |
| global cache documented default | 20,000,000 | Applied when switching modes without explicit weight |
| event loops | 2 | Separate from Gremlin workers and parallel read executor |
| commands per event loop | 50 | Client async capacity input |
| query/scan socket timeout | 30,000 ms | Global operations have different tail envelope |

## Traversal strategies present in the source

| Strategy | Audited role |
| --- | --- |
| FireflyGraphStepStrategy | Folds root GraphStep plus eligible has/label constraints into provider access |
| FireflyBatchVertexReadStrategy | Replaces per-vertex access with multi-key vertex reads |
| FireflyBatchEdgeReadStrategy | Batches packed-edge record access |
| FireflyBatchEdgeReadLocalStrategy | Local-child variant of batched edge access |
| FireflyEdgeToVertexBatchReadStrategy | Batches endpoint materialization following edges |
| FireflyOtherVBatchReadStrategy | Batches otherV endpoint lookup |
| FireflyAdjacentVertexIdStrategy | Uses cached adjacent identity where edge materialization is unnecessary |
| FireflyHasIdVertexFilterStrategy | Avoids general reads for eligible hasId filters |
| FireflyBatchTraversalFilterStrategy | Combines/filter-batches eligible child traversals |
| FireflyGraphFilterStrategy | Pushes compatible graph filters toward storage |
| FireflyReadThroughCacheStrategy | Routes eligible record reads through the configured cache |
| FireflyCountGlobalLocalStrategy | Recognizes count shapes with provider-local shortcuts |
| FireflyGraphCountStrategy | Optimizes graph-wide count forms where supported |
| FireflyVertexEdgeLocalCountStrategy | Counts adjacency locally without full edge materialization |
| FireflyElementMapStrategy | Projects element maps through a provider step |
| FireflyGraphDropStrategy | Replaces general drop with provider mutation logic |
| FireflyMergeStepStrategy | Installs provider mergeV/mergeE implementations |
| FireflyAuthenticationStrategy | Carries authenticated graph permissions into traversal processing |
| FireflyTraversalOptionsStrategy | Reads provider options such as parallelize and scan control |
| FireflyQueryTracingStrategy | Instruments eligible execution for distributed tracing |
| FireflyScanProfileStrategy | Adds scan/profile observability |
| FireflyComputerVerificationStrategy | Rejects invalid GraphComputer traversal use |

## Semantic hazards

- A traversal that is logically equivalent in Gremlin may miss a provider rewrite because its step arrangement differs.
- String indexes support full-string equality, not substring search.
- Double values cannot use the documented vertex property indexes; scaled Long is the recommended indexed substitute.
- Global edge label/property lookup scans because general edge indexes are absent.
- High-cardinality indexes can speed roots; low-cardinality indexes may generate large query streams and consume Aerospike query threads.
- MergeE on supernodes can trigger secondary-index queries, and documented query-thread limits can reject excess concurrency.
- Parallelize may improve a single high-fanout I/O-bound query while harming aggregate throughput or tail latency.
- Global cache is an explicit stale-read tradeoff and is per AGS instance, so a load-balanced fleet has independent cache contents.
- Warm-cache comparisons are invalid unless every competitor receives equivalent preconditioning and cache memory is charged.

## Query qualification cases

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — query: V(id)

- Purpose: Prove one point-root path and stable ID semantics.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V(id)`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — query: V(id1,id2,...)

- Purpose: Observe batch partitioning by database node.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V(id1,id2,...)`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — query: V().hasLabel indexed

- Purpose: Verify secondary index rather than scan.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().hasLabel indexed`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — query: V().hasLabel unindexed

- Purpose: Expose scan and scan-disable behavior.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().hasLabel unindexed`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — query: V().has string equality

- Purpose: Use compatible string index.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().has string equality`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — query: V().has numeric equality

- Purpose: Use compatible numeric index.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().has numeric equality`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — query: V().has numeric range

- Purpose: Inspect range filter and remaining predicates.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().has numeric range`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — query: V().has Double

- Purpose: Expose unindexed fallback.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().has Double`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — query: V().has substring

- Purpose: Expose full scan and filter cost.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `V().has substring`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — query: compound equality

- Purpose: Observe expression-index selection.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `compound equality`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — query: two eligible indexes

- Purpose: Verify cardinality-based most-selective root.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `two eligible indexes`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — query: stale cardinality metadata

- Purpose: Measure plan lag after data distribution changes.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `stale cardinality metadata`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — query: outE label

- Purpose: Count vertex and packed-edge reads.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `outE label`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — query: out adjacent vertices

- Purpose: Verify edge-skipping/batch rewrite.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `out adjacent vertices`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — query: in adjacent vertices

- Purpose: Verify reverse ordinary adjacency path.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `in adjacent vertices`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — query: both self-loop

- Purpose: Verify multiplicity and dedup semantics.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `both self-loop`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — query: otherV

- Purpose: Verify batched adjacent endpoint reads.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `otherV`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — query: edge-to-vertex

- Purpose: Verify specialized batch step.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `edge-to-vertex`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — query: has after VertexStep

- Purpose: Verify predicate folding/pushdown.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `has after VertexStep`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — query: limit after VertexStep

- Purpose: Verify early termination and reduced I/O.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `limit after VertexStep`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — query: sample after VertexStep

- Purpose: Verify sample semantics without reading all candidates.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `sample after VertexStep`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — query: local edge count

- Purpose: Verify adjacency-local count without edge fetch.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `local edge count`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — query: global vertex count

- Purpose: Verify count optimization and exactness during mutation.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global vertex count`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — query: global edge count

- Purpose: Verify summary/scan path and exactness.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global edge count`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — query: properties projection

- Purpose: Fetch only required map entries.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `properties projection`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — query: valueMap

- Purpose: Measure requested versus materialized properties.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `valueMap`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — query: elementMap

- Purpose: Inspect provider-specific projection rewrite.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `elementMap`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — query: path

- Purpose: Charge path object retention and edge/vertex materialization.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `path`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — query: simplePath

- Purpose: Charge visited-set memory and compare semantics.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `simplePath`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — query: dedup

- Purpose: Measure hash state and spill/limit behavior.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `dedup`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — query: order

- Purpose: Expose full materialization and memory.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `order`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — query: groupCount

- Purpose: Classify as OLTP traversal or move to OLAP path.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `groupCount`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — query: repeat depth 2

- Purpose: Measure batched frontier behavior.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `repeat depth 2`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — query: repeat depth 4

- Purpose: Expose multiplicative frontier and request limits.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `repeat depth 4`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — query: repeat emit

- Purpose: Verify 3.2.1 optimization and output semantics.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `repeat emit`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — query: union child traversal

- Purpose: Verify options and filters propagate into children.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `union child traversal`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — query: coalesce

- Purpose: Check rewrite coverage and short-circuit reads.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `coalesce`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — query: optional

- Purpose: Check null/missing branch semantics.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `optional`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — query: mergeV unique ID

- Purpose: Avoid index ambiguity and count lock/query operations.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mergeV unique ID`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — query: mergeV nonunique predicate

- Purpose: Expose multi-match behavior documented by AGS.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mergeV nonunique predicate`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — query: mergeE ordinary

- Purpose: Measure lock and adjacency operations.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mergeE ordinary`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — query: mergeE supernode

- Purpose: Expose sindex query-thread consumption.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mergeE supernode`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — query: drop edge

- Purpose: Verify specialized drop and cleanup.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `drop edge`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — query: drop ordinary vertex

- Purpose: Count incident-edge work and atomicity mode.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `drop ordinary vertex`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — query: drop supernode

- Purpose: Record best-effort semantics and completion lag.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `drop supernode`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — query: scan disabled global

- Purpose: Reject accidental V()/E() without eligible index.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `scan disabled global`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — query: per-query scan opt-in

- Purpose: Prove explicit escape hatch is auditable.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `per-query scan opt-in`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — query: page size per node

- Purpose: Measure memory/latency as DB cluster grows.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `page size per node`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — query: flat page size

- Purpose: Bound cluster-wide response buffering.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `flat page size`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — query: batch size per node

- Purpose: Measure RPC count and result latency.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `batch size per node`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — query: flat batch size

- Purpose: Hold total batch constant across node count.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `flat batch size`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — query: parallelize 1

- Purpose: Establish default-equivalent baseline.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `parallelize 1`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — query: parallelize 2

- Purpose: Measure single-query gain and fleet interference.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `parallelize 2`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — query: parallelize CPU count

- Purpose: Expose executor saturation and tail risk.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `parallelize CPU count`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — query: parallelize in transaction

- Purpose: Verify explicit rejection.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `parallelize in transaction`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — query: transactional cache cold

- Purpose: Establish per-request backend I/O.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `transactional cache cold`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — query: transactional cache repeated vertex

- Purpose: Observe within-traversal hit only.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `transactional cache repeated vertex`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — query: global cache warm

- Purpose: Measure best-case repeated hot-set reads.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global cache warm`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — query: global cache stale local write

- Purpose: Demonstrate documented correctness risk.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global cache stale local write`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — query: global cache stale other AGS

- Purpose: Demonstrate fleet incoherence.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global cache stale other AGS`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q061 — query: global cache reset

- Purpose: Measure invalidation latency and traffic surge.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `global cache reset`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q062 — query: query trace threshold

- Purpose: Correlate spans with backend calls without full-sampling overhead.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `query trace threshold`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q063 — query: query profile

- Purpose: Capture rewritten step plan and per-step timing.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `query profile`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q064 — query: timeout cancellation

- Purpose: Verify work stops in AGS and Database after client timeout.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `timeout cancellation`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q065 — query: client disconnect

- Purpose: Verify iterator/query resources are reclaimed.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `client disconnect`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q066 — query: backpressure slow client

- Purpose: Bound result buffering and heap.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `backpressure slow client`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q067 — query: mixed short and scan

- Purpose: Verify scan admission does not destroy short-query tail.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mixed short and scan`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q068 — query: mixed short and supernode

- Purpose: Verify heavy traversal isolation.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `mixed short and supernode`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q069 — query: 32 AGS scale

- Purpose: Locate storage saturation and load-balancer skew.
- Setup: Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.
- Workload: Execute the smallest semantically complete operation for `32 AGS scale`, then repeat under controlled concurrency and skew.
- Required counters: client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S09,S11–S19,S27,S33,S36–S41,S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S09 — Architecture

- Type: Official documentation
- Audit note: Three-layer request path
- URL: https://aerospike.com/docs/graph/overview/architecture/

### S11 — Indexing

- Type: Official documentation
- Audit note: Vertex index and scan controls
- URL: https://aerospike.com/docs/graph/develop/query/indexing/

### S12 — Supernodes

- Type: Official documentation
- Audit note: Thresholds and filtered traversal guidance
- URL: https://aerospike.com/docs/graph/develop/query/supernodes/

### S13 — Query threading

- Type: Official documentation
- Audit note: Per-query parallelization and batch/page controls
- URL: https://aerospike.com/docs/graph/develop/query/query-threading/

### S14 — Cache management

- Type: Official documentation
- Audit note: Transactional and global record caches
- URL: https://aerospike.com/docs/graph/manage/cache/

### S15 — Data types

- Type: Official documentation
- Audit note: Property and index type limitations
- URL: https://aerospike.com/docs/graph/develop/query/data-type-support/

### S16 — TinkerPop feature support

- Type: Official documentation
- Audit note: Feature compatibility matrix
- URL: https://aerospike.com/docs/graph/overview/tinkerpop/

### S17 — Configuration reference

- Type: Official documentation
- Audit note: AGS runtime knobs
- URL: https://aerospike.com/docs/graph/reference/config/

### S18 — Metrics reference

- Type: Official documentation
- Audit note: Prometheus metric inventory
- URL: https://aerospike.com/docs/graph/reference/metrics/

### S19 — Query tracing

- Type: Official documentation
- Audit note: Zipkin tracing contract
- URL: https://aerospike.com/docs/graph/observe/query-tracing/

### S27 — Architecture deep-dive blog

- Type: Vendor blog
- Audit note: Optimizer and record-model explanation
- URL: https://aerospike.com/blog/graphing-database-architecture/

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

### S38 — AGS query code

- Type: Apache-2.0 source
- Audit note: Paged scans and secondary-index queries
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query

### S39 — AGS traversal strategies

- Type: Apache-2.0 source
- Audit note: Rewrite implementations
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy

### S41 — AGS tests

- Type: Apache-2.0 source
- Audit note: 431 test files observed in snapshot
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test

### S45 — Apache TinkerPop 3.7.3 reference

- Type: Upstream documentation
- Audit note: Language/runtime semantic oracle
- URL: https://tinkerpop.apache.org/docs/3.7.3/reference/
