# Aerospike Graph Gremlin compiler and query-execution audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: TinkerPop surface, traversal rewrites, storage I/O, batching, pagination, parallelism, caching, and observability
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Execution conclusion

AGS is not a declarative cost-based graph optimizer in the relational sense. TinkerPop builds a traversal, and AGS applies provider strategies that recognize specific step shapes and replace or fold them into Aerospike-aware steps. Performance therefore depends on syntactic traversal shape, IDs versus scans, placement of has/limit/sample/count, property projection, ordinary versus supernode adjacency, supported predicate types, and whether a rewrite fires.

The source exposes strategies for graph-step folding, batch vertex/edge reads, edge-to-vertex and otherV batching, adjacent-ID shortcuts, cached reads, graph/local counts, filter pushdown, hasId, drop, merge, elementMap, query tracing, scan profiling, and verification. The benchmark must capture the optimized traversal/profile and backend operation counts so a fast result cannot be attributed vaguely to "Gremlin optimization."

Two traversals can return the same vertices while asking the provider to do very different work. The first form below starts from an exact ID and gives AGS a point-read root. The second requires a label and property access path. If the matching typed vertex index is absent, it can become a scan. The third form is intentionally dangerous because it starts with every edge.

```groovy
// Point-rooted traversal. This is the latency-friendly shape.
g.V(customerId)
 .out('usesDevice')
 .has('riskScore', gt(700L))
 .limit(20)
 .valueMap('riskScore', 'lastSeen')

// Index-rooted only when a compatible vertex index exists.
g.V()
 .hasLabel('Customer')
 .has('countryCode', 'VN')
 .limit(100)

// Global edge root. Treat this as scan-class work.
g.E()
 .hasLabel('usesDevice')
 .count()
```

The benchmark records the submitted bytecode and the provider-optimized traversal. Reviewing only the Gremlin text misses whether `has`, `limit`, projection, or adjacent-vertex access was folded into a provider step. Reviewing only latency misses whether the query consumed a secondary-index stream or a global scan.

## Read-path classes and decisions

Gremlin bytecode arrives through TinkerPop Gremlin Server over WebSocket, after which provider strategies rewrite eligible traversals before iterator execution. An ID-rooted vertex lookup becomes a direct record read. Multiple known IDs can become a batch read split by cluster node. A compatible vertex `has()` or `hasLabel()` predicate can use a secondary index, and remaining compatible predicates can become Database filter expressions that reject records before they cross the wire.

For ordinary vertices, an adjacent-vertex traversal can use cached endpoint identity and avoid materializing an edge object that the query never projects. Supernodes take a different path: specialized secondary-index queries locate edge records, after which paging, filtering, and endpoint reads continue. Global scans use the paged query machinery and have a completely different tail and resource envelope from point or bounded paths.

Per-query parallelization draws from a shared executor and is not allowed inside transaction traversals. The default record cache belongs to a request or transaction. Global mode shares cached records within one graph instance but may return stale data, and separate AGS instances maintain separate contents. This cache stores records, not completed query results.

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

A traversal that is logically equivalent in Gremlin may miss a provider rewrite because its step arrangement differs.
String indexes support full-string equality, not substring search.
Double values cannot use the documented vertex property indexes; scaled Long is the recommended indexed substitute.
Global edge label/property lookup scans because general edge indexes are absent.
High-cardinality indexes can speed roots; low-cardinality indexes may generate large query streams and consume Aerospike query threads.
MergeE on supernodes can trigger secondary-index queries, and documented query-thread limits can reject excess concurrency.
Parallelize may improve a single high-fanout I/O-bound query while harming aggregate throughput or tail latency.
Global cache is an explicit stale-read tradeoff and is per AGS instance, so a load-balanced fleet has independent cache contents.
Warm-cache comparisons are invalid unless every competitor receives equivalent preconditioning and cache memory is charged.

## Query qualification cases

Every query case uses the same graph snapshot and an independent result oracle. The run captures submitted bytecode, provider-optimized traversal, TinkerPop profile, Zipkin spans, AGS queue and cache metrics, Database command histograms, bytes read, result cardinality, and cancellation behavior. Point, index, supernode, and scan cases run in separate traffic classes so one path does not hide another.

Cold, request-cache, global-cache, steady-state, saturation, and slow-consumer phases are named explicitly. Errors, retries, timeouts, and partial streams stay in the sample set. A semantic mismatch or an unexpected scan fails the case even when its latency is low. A provider rewrite is credited only when the saved optimized traversal and backend counters demonstrate that it fired.

### Q001 : query: V(id)

**Purpose.** Prove one point-root path and stable ID semantics.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q002 : query: V(id1,id2,...)

**Purpose.** Observe batch partitioning by database node.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q003 : query: V().hasLabel indexed

**Purpose.** Verify secondary index rather than scan.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q004 : query: V().hasLabel unindexed

**Purpose.** Expose scan and scan-disable behavior.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q005 : query: V().has string equality

**Purpose.** Use compatible string index.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q006 : query: V().has numeric equality

**Purpose.** Use compatible numeric index.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q007 : query: V().has numeric range

**Purpose.** Inspect range filter and remaining predicates.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q008 : query: V().has Double

**Purpose.** Expose unindexed fallback.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q009 : query: V().has substring

**Purpose.** Expose full scan and filter cost.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q010 : query: compound equality

**Purpose.** Observe expression-index selection.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q011 : query: two eligible indexes

**Purpose.** Verify cardinality-based most-selective root.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q012 : query: stale cardinality metadata

**Purpose.** Measure plan lag after data distribution changes.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q013 : query: outE label

**Purpose.** Count vertex and packed-edge reads.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q014 : query: out adjacent vertices

**Purpose.** Verify edge-skipping/batch rewrite.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q015 : query: in adjacent vertices

**Purpose.** Verify reverse ordinary adjacency path.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q016 : query: both self-loop

**Purpose.** Verify multiplicity and dedup semantics.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q017 : query: otherV

**Purpose.** Verify batched adjacent endpoint reads.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q018 : query: edge-to-vertex

**Purpose.** Verify specialized batch step.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q019 : query: has after VertexStep

**Purpose.** Verify predicate folding/pushdown.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q020 : query: limit after VertexStep

**Purpose.** Verify early termination and reduced I/O.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q021 : query: sample after VertexStep

**Purpose.** Verify sample semantics without reading all candidates.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q022 : query: local edge count

**Purpose.** Verify adjacency-local count without edge fetch.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q023 : query: global vertex count

**Purpose.** Verify count optimization and exactness during mutation.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q024 : query: global edge count

**Purpose.** Verify summary/scan path and exactness.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q025 : query: properties projection

**Purpose.** Fetch only required map entries.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q026 : query: valueMap

**Purpose.** Measure requested versus materialized properties.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q027 : query: elementMap

**Purpose.** Inspect provider-specific projection rewrite.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q028 : query: path

**Purpose.** Charge path object retention and edge/vertex materialization.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q029 : query: simplePath

**Purpose.** Charge visited-set memory and compare semantics.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q030 : query: dedup

**Purpose.** Measure hash state and spill/limit behavior.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q031 : query: order

**Purpose.** Expose full materialization and memory.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q032 : query: groupCount

**Purpose.** Classify as OLTP traversal or move to OLAP path.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q033 : query: repeat depth 2

**Purpose.** Measure batched frontier behavior.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q034 : query: repeat depth 4

**Purpose.** Expose multiplicative frontier and request limits.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q035 : query: repeat emit

**Purpose.** Verify 3.2.1 optimization and output semantics.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q036 : query: union child traversal

**Purpose.** Verify options and filters propagate into children.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q037 : query: coalesce

**Purpose.** Check rewrite coverage and short-circuit reads.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q038 : query: optional

**Purpose.** Check null/missing branch semantics.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q039 : query: mergeV unique ID

**Purpose.** Avoid index ambiguity and count lock/query operations.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q040 : query: mergeV nonunique predicate

**Purpose.** Expose multi-match behavior documented by AGS.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q041 : query: mergeE ordinary

**Purpose.** Measure lock and adjacency operations.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q042 : query: mergeE supernode

**Purpose.** Expose sindex query-thread consumption.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q043 : query: drop edge

**Purpose.** Verify specialized drop and cleanup.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q044 : query: drop ordinary vertex

**Purpose.** Count incident-edge work and atomicity mode.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q045 : query: drop supernode

**Purpose.** Record best-effort semantics and completion lag.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q046 : query: scan disabled global

**Purpose.** Reject accidental V()/E() without eligible index.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q047 : query: per-query scan opt-in

**Purpose.** Prove explicit escape hatch is auditable.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q048 : query: page size per node

**Purpose.** Measure memory/latency as DB cluster grows.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q049 : query: flat page size

**Purpose.** Bound cluster-wide response buffering.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q050 : query: batch size per node

**Purpose.** Measure RPC count and result latency.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q051 : query: flat batch size

**Purpose.** Hold total batch constant across node count.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q052 : query: parallelize 1

**Purpose.** Establish default-equivalent baseline.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q053 : query: parallelize 2

**Purpose.** Measure single-query gain and fleet interference.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q054 : query: parallelize CPU count

**Purpose.** Expose executor saturation and tail risk.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q055 : query: parallelize in transaction

**Purpose.** Verify explicit rejection.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q056 : query: transactional cache cold

**Purpose.** Establish per-request backend I/O.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q057 : query: transactional cache repeated vertex

**Purpose.** Observe within-traversal hit only.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q058 : query: global cache warm

**Purpose.** Measure best-case repeated hot-set reads.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q059 : query: global cache stale local write

**Purpose.** Demonstrate documented correctness risk.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q060 : query: global cache stale other AGS

**Purpose.** Demonstrate fleet incoherence.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q061 : query: global cache reset

**Purpose.** Measure invalidation latency and traffic surge.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q062 : query: query trace threshold

**Purpose.** Correlate spans with backend calls without full-sampling overhead.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q063 : query: query profile

**Purpose.** Capture rewritten step plan and per-step timing.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q064 : query: timeout cancellation

**Purpose.** Verify work stops in AGS and Database after client timeout.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q065 : query: client disconnect

**Purpose.** Verify iterator/query resources are reclaimed.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q066 : query: backpressure slow client

**Purpose.** Bound result buffering and heap.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q067 : query: mixed short and scan

**Purpose.** Verify scan admission does not destroy short-query tail.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q068 : query: mixed short and supernode

**Purpose.** Verify heavy traversal isolation.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


### Q069 : query: 32 AGS scale

**Purpose.** Locate storage saturation and load-balancer skew.

**Evidence anchors.** S09,S11–S19,S27,S33,S36–S41,S45


## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S09 : Architecture

**Type.** Official documentation

**Audit note.** Three-layer request path

**URL.** https://aerospike.com/docs/graph/overview/architecture/


### S11 : Indexing

**Type.** Official documentation

**Audit note.** Vertex index and scan controls

**URL.** https://aerospike.com/docs/graph/develop/query/indexing/


### S12 : Supernodes

**Type.** Official documentation

**Audit note.** Thresholds and filtered traversal guidance

**URL.** https://aerospike.com/docs/graph/develop/query/supernodes/


### S13 : Query threading

**Type.** Official documentation

**Audit note.** Per-query parallelization and batch/page controls

**URL.** https://aerospike.com/docs/graph/develop/query/query-threading/


### S14 : Cache management

**Type.** Official documentation

**Audit note.** Transactional and global record caches

**URL.** https://aerospike.com/docs/graph/manage/cache/


### S15 : Data types

**Type.** Official documentation

**Audit note.** Property and index type limitations

**URL.** https://aerospike.com/docs/graph/develop/query/data-type-support/


### S16 : TinkerPop feature support

**Type.** Official documentation

**Audit note.** Feature compatibility matrix

**URL.** https://aerospike.com/docs/graph/overview/tinkerpop/


### S17 : Configuration reference

**Type.** Official documentation

**Audit note.** AGS runtime knobs

**URL.** https://aerospike.com/docs/graph/reference/config/


### S18 : Metrics reference

**Type.** Official documentation

**Audit note.** Prometheus metric inventory

**URL.** https://aerospike.com/docs/graph/reference/metrics/


### S19 : Query tracing

**Type.** Official documentation

**Audit note.** Zipkin tracing contract

**URL.** https://aerospike.com/docs/graph/observe/query-tracing/


### S27 : Architecture deep-dive blog

**Type.** Vendor blog

**Audit note.** Optimizer and record-model explanation

**URL.** https://aerospike.com/blog/graphing-database-architecture/


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


### S38 : AGS query code

**Type.** Apache-2.0 source

**Audit note.** Paged scans and secondary-index queries

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query


### S39 : AGS traversal strategies

**Type.** Apache-2.0 source

**Audit note.** Rewrite implementations

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy


### S41 : AGS tests

**Type.** Apache-2.0 source

**Audit note.** 431 test files observed in snapshot

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test


### S45 : Apache TinkerPop 3.7.3 reference

**Type.** Upstream documentation

**Audit note.** Language/runtime semantic oracle

**URL.** https://tinkerpop.apache.org/docs/3.7.3/reference/
