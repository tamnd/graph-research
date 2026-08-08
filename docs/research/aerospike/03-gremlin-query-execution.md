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

### Provider strategies are the physical planner

The strategy tree is the closest public source equivalent to a physical
optimizer. For example, the pinned source declares:

```java
public class FireflyBatchVertexReadStrategy extends FireflyStrategyBase
```

The declaration is from
[`FireflyBatchVertexReadStrategy.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy/optimization/FireflyBatchVertexReadStrategy.java).
The inheritance matters because AGS registers provider strategies that inspect
and replace recognizable TinkerPop step patterns. This is not a global
cost-based search over arbitrary equivalent plans. Syntactic placement can
therefore determine whether IDs are batched, whether an adjacent endpoint is
read directly, whether a predicate becomes a Database filter expression, or
whether a graph root becomes a secondary-index query or scan. Query reviews
need the optimized traversal, not just the submitted Gremlin string.

Batching also has a cluster-dependent shape. Known keys are grouped by target
Database node, and source defaults include a per-node batch size. Increasing
Database nodes can increase the total in-flight key count even when the AGS
setting is unchanged. That can improve device parallelism, but it can also
increase response buffers, allocations, and tail exposure. A batch setting is
therefore recorded with the Database node count and partition state. The same
principle applies to paged scans and secondary-index streams: a per-node page
size becomes a fleet-wide memory and network quantity.

Cache results need equally careful language. Transactional mode is request or
thread local and is reset at the traversal boundary. Global mode shares record
objects inside one AGS graph instance and maintains additional supernode edge
ID state. It can reduce Database commands for repeated hot reads, but separate
AGS instances have separate contents and the documented mode permits stale
records. A warm global-cache latency result is not a transparent improvement
over transactional mode. It is a different freshness and memory configuration
that must be scored separately.

| Traversal shape | Likely physical root | Main optimization opportunity | Main failure mode |
| --- | --- | --- | --- |
| `g.V(id)` | Direct vertex record read | Single-key path and request-local cache | Client or record timeout |
| `g.V(id1, id2, ...)` | Node-grouped batch reads | Fewer round trips and parallel device access | Oversized buffers or straggler node |
| Indexed `hasLabel` plus property | Secondary-index query followed by reads | Selective root and filter expression | Low selectivity floods query threads |
| Unindexed `g.V()` predicate | Paged global scan | Scan profiling and strict admission | OLTP interference and unbounded work |
| Ordinary `out(label)` | Inline adjacency plus batched endpoint reads | Adjacent-ID shortcut | Degree and projection expansion |
| Supernode `out(label)` | Specialized secondary-index edge lookup | Label and property pushdown | Query-thread pressure and paging tails |
| `g.E()` | Global edge scan | Version-specific scan improvements | Treating scan throughput as traversal latency |

Every query case uses the same graph snapshot and an independent result oracle. The run captures submitted bytecode, provider-optimized traversal, TinkerPop profile, Zipkin spans, AGS queue and cache metrics, Database command histograms, bytes read, result cardinality, and cancellation behavior. Point, index, supernode, and scan cases run in separate traffic classes so one path does not hide another.

Cold, request-cache, global-cache, steady-state, saturation, and slow-consumer phases are named explicitly. Errors, retries, timeouts, and partial streams stay in the sample set. A semantic mismatch or an unexpected scan fails the case even when its latency is low. A provider rewrite is credited only when the saved optimized traversal and backend counters demonstrate that it fired.

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
<td>query: V(id)</td>
<td>Prove one point-root path and stable ID semantics.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q002</td>
<td>query: V(id1,id2,...)</td>
<td>Observe batch partitioning by database node.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q003</td>
<td>query: V().hasLabel indexed</td>
<td>Verify secondary index rather than scan.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q004</td>
<td>query: V().hasLabel unindexed</td>
<td>Expose scan and scan-disable behavior.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q005</td>
<td>query: V().has string equality</td>
<td>Use compatible string index.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q006</td>
<td>query: V().has numeric equality</td>
<td>Use compatible numeric index.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q007</td>
<td>query: V().has numeric range</td>
<td>Inspect range filter and remaining predicates.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q008</td>
<td>query: V().has Double</td>
<td>Expose unindexed fallback.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q009</td>
<td>query: V().has substring</td>
<td>Expose full scan and filter cost.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q010</td>
<td>query: compound equality</td>
<td>Observe expression-index selection.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q011</td>
<td>query: two eligible indexes</td>
<td>Verify cardinality-based most-selective root.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q012</td>
<td>query: stale cardinality metadata</td>
<td>Measure plan lag after data distribution changes.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q013</td>
<td>query: outE label</td>
<td>Count vertex and packed-edge reads.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q014</td>
<td>query: out adjacent vertices</td>
<td>Verify edge-skipping/batch rewrite.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q015</td>
<td>query: in adjacent vertices</td>
<td>Verify reverse ordinary adjacency path.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q016</td>
<td>query: both self-loop</td>
<td>Verify multiplicity and dedup semantics.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q017</td>
<td>query: otherV</td>
<td>Verify batched adjacent endpoint reads.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q018</td>
<td>query: edge-to-vertex</td>
<td>Verify specialized batch step.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q019</td>
<td>query: has after VertexStep</td>
<td>Verify predicate folding/pushdown.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q020</td>
<td>query: limit after VertexStep</td>
<td>Verify early termination and reduced I/O.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q021</td>
<td>query: sample after VertexStep</td>
<td>Verify sample semantics without reading all candidates.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q022</td>
<td>query: local edge count</td>
<td>Verify adjacency-local count without edge fetch.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q023</td>
<td>query: global vertex count</td>
<td>Verify count optimization and exactness during mutation.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q024</td>
<td>query: global edge count</td>
<td>Verify summary/scan path and exactness.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q025</td>
<td>query: properties projection</td>
<td>Fetch only required map entries.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q026</td>
<td>query: valueMap</td>
<td>Measure requested versus materialized properties.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q027</td>
<td>query: elementMap</td>
<td>Inspect provider-specific projection rewrite.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q028</td>
<td>query: path</td>
<td>Charge path object retention and edge/vertex materialization.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q029</td>
<td>query: simplePath</td>
<td>Charge visited-set memory and compare semantics.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q030</td>
<td>query: dedup</td>
<td>Measure hash state and spill/limit behavior.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q031</td>
<td>query: order</td>
<td>Expose full materialization and memory.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q032</td>
<td>query: groupCount</td>
<td>Classify as OLTP traversal or move to OLAP path.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q033</td>
<td>query: repeat depth 2</td>
<td>Measure batched frontier behavior.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q034</td>
<td>query: repeat depth 4</td>
<td>Expose multiplicative frontier and request limits.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q035</td>
<td>query: repeat emit</td>
<td>Verify 3.2.1 optimization and output semantics.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q036</td>
<td>query: union child traversal</td>
<td>Verify options and filters propagate into children.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q037</td>
<td>query: coalesce</td>
<td>Check rewrite coverage and short-circuit reads.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q038</td>
<td>query: optional</td>
<td>Check null/missing branch semantics.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q039</td>
<td>query: mergeV unique ID</td>
<td>Avoid index ambiguity and count lock/query operations.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q040</td>
<td>query: mergeV nonunique predicate</td>
<td>Expose multi-match behavior documented by AGS.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q041</td>
<td>query: mergeE ordinary</td>
<td>Measure lock and adjacency operations.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q042</td>
<td>query: mergeE supernode</td>
<td>Expose sindex query-thread consumption.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q043</td>
<td>query: drop edge</td>
<td>Verify specialized drop and cleanup.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q044</td>
<td>query: drop ordinary vertex</td>
<td>Count incident-edge work and atomicity mode.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q045</td>
<td>query: drop supernode</td>
<td>Record best-effort semantics and completion lag.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q046</td>
<td>query: scan disabled global</td>
<td>Reject accidental V()/E() without eligible index.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q047</td>
<td>query: per-query scan opt-in</td>
<td>Prove explicit escape hatch is auditable.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q048</td>
<td>query: page size per node</td>
<td>Measure memory/latency as DB cluster grows.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q049</td>
<td>query: flat page size</td>
<td>Bound cluster-wide response buffering.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q050</td>
<td>query: batch size per node</td>
<td>Measure RPC count and result latency.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q051</td>
<td>query: flat batch size</td>
<td>Hold total batch constant across node count.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q052</td>
<td>query: parallelize 1</td>
<td>Establish default-equivalent baseline.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q053</td>
<td>query: parallelize 2</td>
<td>Measure single-query gain and fleet interference.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q054</td>
<td>query: parallelize CPU count</td>
<td>Expose executor saturation and tail risk.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q055</td>
<td>query: parallelize in transaction</td>
<td>Verify explicit rejection.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q056</td>
<td>query: transactional cache cold</td>
<td>Establish per-request backend I/O.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q057</td>
<td>query: transactional cache repeated vertex</td>
<td>Observe within-traversal hit only.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q058</td>
<td>query: global cache warm</td>
<td>Measure best-case repeated hot-set reads.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q059</td>
<td>query: global cache stale local write</td>
<td>Demonstrate documented correctness risk.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q060</td>
<td>query: global cache stale other AGS</td>
<td>Demonstrate fleet incoherence.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q061</td>
<td>query: global cache reset</td>
<td>Measure invalidation latency and traffic surge.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q062</td>
<td>query: query trace threshold</td>
<td>Correlate spans with backend calls without full-sampling overhead.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q063</td>
<td>query: query profile</td>
<td>Capture rewritten step plan and per-step timing.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q064</td>
<td>query: timeout cancellation</td>
<td>Verify work stops in AGS and Database after client timeout.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q065</td>
<td>query: client disconnect</td>
<td>Verify iterator/query resources are reclaimed.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q066</td>
<td>query: backpressure slow client</td>
<td>Bound result buffering and heap.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q067</td>
<td>query: mixed short and scan</td>
<td>Verify scan admission does not destroy short-query tail.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q068</td>
<td>query: mixed short and supernode</td>
<td>Verify heavy traversal isolation.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
</tr>
<tr>
<td>Q069</td>
<td>query: 32 AGS scale</td>
<td>Locate storage saturation and load-balancer skew.</td>
<td>S09,S11–S19,S27,S33,S36–S41,S45</td>
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
<td>S09</td>
<td>Architecture</td>
<td>Official documentation</td>
<td>Three-layer request path</td>
<td>https://aerospike.com/docs/graph/overview/architecture/</td>
</tr>
<tr>
<td>S11</td>
<td>Indexing</td>
<td>Official documentation</td>
<td>Vertex index and scan controls</td>
<td>https://aerospike.com/docs/graph/develop/query/indexing/</td>
</tr>
<tr>
<td>S12</td>
<td>Supernodes</td>
<td>Official documentation</td>
<td>Thresholds and filtered traversal guidance</td>
<td>https://aerospike.com/docs/graph/develop/query/supernodes/</td>
</tr>
<tr>
<td>S13</td>
<td>Query threading</td>
<td>Official documentation</td>
<td>Per-query parallelization and batch/page controls</td>
<td>https://aerospike.com/docs/graph/develop/query/query-threading/</td>
</tr>
<tr>
<td>S14</td>
<td>Cache management</td>
<td>Official documentation</td>
<td>Transactional and global record caches</td>
<td>https://aerospike.com/docs/graph/manage/cache/</td>
</tr>
<tr>
<td>S15</td>
<td>Data types</td>
<td>Official documentation</td>
<td>Property and index type limitations</td>
<td>https://aerospike.com/docs/graph/develop/query/data-type-support/</td>
</tr>
<tr>
<td>S16</td>
<td>TinkerPop feature support</td>
<td>Official documentation</td>
<td>Feature compatibility matrix</td>
<td>https://aerospike.com/docs/graph/overview/tinkerpop/</td>
</tr>
<tr>
<td>S17</td>
<td>Configuration reference</td>
<td>Official documentation</td>
<td>AGS runtime knobs</td>
<td>https://aerospike.com/docs/graph/reference/config/</td>
</tr>
<tr>
<td>S18</td>
<td>Metrics reference</td>
<td>Official documentation</td>
<td>Prometheus metric inventory</td>
<td>https://aerospike.com/docs/graph/reference/metrics/</td>
</tr>
<tr>
<td>S19</td>
<td>Query tracing</td>
<td>Official documentation</td>
<td>Zipkin tracing contract</td>
<td>https://aerospike.com/docs/graph/observe/query-tracing/</td>
</tr>
<tr>
<td>S27</td>
<td>Architecture deep-dive blog</td>
<td>Vendor blog</td>
<td>Optimizer and record-model explanation</td>
<td>https://aerospike.com/blog/graphing-database-architecture/</td>
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
<td>S38</td>
<td>AGS query code</td>
<td>Apache-2.0 source</td>
<td>Paged scans and secondary-index queries</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query</td>
</tr>
<tr>
<td>S39</td>
<td>AGS traversal strategies</td>
<td>Apache-2.0 source</td>
<td>Rewrite implementations</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy</td>
</tr>
<tr>
<td>S41</td>
<td>AGS tests</td>
<td>Apache-2.0 source</td>
<td>431 test files observed in snapshot</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test</td>
</tr>

<tr>
<td>S45</td>
<td>Apache TinkerPop 3.7.3 reference</td>
<td>Upstream documentation</td>
<td>Language/runtime semantic oracle</td>
<td>https://tinkerpop.apache.org/docs/3.7.3/reference/</td>
</tr>
</tbody>
</table>
