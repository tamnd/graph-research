# Aerospike Graph benchmark audit and tenfold-win qualification

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Deconstruction of published results plus a fair, reproducible competitor protocol
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Published benchmark verdict

The current Aerospike identity-graph report is valuable evidence that one vendor configuration processed a tens-of-billions property graph. It is not an independent benchmark, not a current 3.2 benchmark, not a cross-engine comparison, not PB evidence, and not a universal latency result. Preserve its exact workload shape: many sparse, independent or weakly connected identity subgraphs whose short reads and writes remain localized.

The PDF reports three scale factors. The largest has 3,600 GB input CSV, 38.3 billion vertices, 37.2 billion edges, and 23.35 TB user data. It used 18 `n2d-highmem-64` database nodes with 24×375GB local NVMe each, RF2, one `n2d-standard-8` AGS for latency runs, and an `n2d-standard-32` load generator. The throughput scale test fixed the storage cluster and increased AGS from 1 to 32, reporting 22K to more than 600K QPS. The software was Database 7.1.0.9 and AGS 2.4.2.

The charts do not provide a machine-readable raw sample bundle in the report, exact query text/source repository, optimizer profiles, backend operation counts, error rate, retry accounting, cache state, offered-load schedule, or a competitor result. The reported infrastructure cost uses a one-year commitment and March 5, 2025 GCP prices. These omissions prevent an audit-grade 10x conclusion.

A benchmark case is stored as data before any load generator starts. The following is the minimum shape used by this dossier. Concrete runs replace every placeholder and commit the exact Gremlin bytecode separately.

```yaml
case: two-hop-identity-degree-32
dataset:
  snapshot: "sha256:replace-with-dataset-manifest"
  vertices: 1000000000
  degree_bucket: [24, 40]
semantics:
  gremlin: "g.V(seed).out('uses').out('belongsTo').dedup()"
  consistency: eventual-read
  mutation_atomicity: none
load:
  model: open-loop
  offered_qps: 20000
  warmup_seconds: 600
  sample_seconds: 1800
limits:
  timeout_ms: 2000
  result_cap: 10000
required_output:
  - hdr_histogram
  - errors_and_timeouts
  - optimized_traversal
  - backend_operation_counts
  - full_resource_ledger
```

The workload is invalid if the result cap changes the logical answer, if retries disappear from the latency history, or if one engine uses a weaker durability or freshness mode. Unsupported behavior remains a failed or non-comparable cell. It is never replaced with an easier query.

## Published dataset and hardware

| Scale | CSV | Vertices | Edges | User data | DB nodes |
| --- | --- | --- | --- | --- | --- |
| 10M | 35GB | 383M | 373M | 0.219TB | 3 × n2d-highmem-8 |
| 100M | 358GB | 3.83B | 3.73B | 2.306TB | 8 × n2d-highmem-16 |
| 1B | 3,600GB | 38.3B | 37.2B | 23.35TB | 18 × n2d-highmem-64 |

## Published bulk-load results

| Scale | Dataproc worker | Workers | Spark memory | Time |
| --- | --- | --- | --- | --- |
| 10M | n2d-highmem-8 | 30 | 1.875TB | 3.56h |
| 100M | n2d-highmem-16 | 60 | 7.5TB | 8.00h |
| 1B | n2d-highmem-64 | 70 | 35TB | 31.81h |

## Why universal 10x is invalid

Latency, throughput, resources, cost, load time, freshness, availability, and semantic coverage are different objectives. A result is valid only for a named workload cell with equal query semantics, durability, replication, consistency, dataset, hardware or cost budget, and completion criteria.

Unsupported queries cannot be replaced with easier operations or removed from an aggregate. Errors and timeouts stay in the result distribution. Open-loop offered load is required for saturation work because a closed-loop client can hide queue growth by slowing its own submissions. Warm-cache runs need matched cache memory and explicit preconditioning; object-store cold starts form a separate class.

Cost comparisons use the same region, pricing term, discounts, replica policy, storage headroom, license scope, and operational services. A tenfold claim needs repeat runs and an uncertainty interval. The useful output is normally a frontier: a tenfold win in some cells, parity or losses in others, and explicit unsupported or non-comparable cells.

## Cross-engine benchmark cells

### Reconstructing what the public benchmark proves

The report establishes that Aerospike ran a large identity workload on a
documented GCP topology and published load, latency, throughput, and cost
summaries. Its largest dataset contains tens of billions of vertices and edges,
which is meaningful engineering evidence. The graph shape is also unusually
important: identity records form many small, localized subgraphs rather than
one globally connected network with deep diameter or a heavy supernode tail.
Short bounded traversals over that shape align well with point and batch record
access. The result cannot be transferred automatically to fraud rings,
recommendation graphs, RDF joins, unrestricted paths, or a graph dominated by
celebrity vertices.

The source's query implementation carries a fixed Database partition fact:

```java
final int partitions = 4096;
```

The extract is from pinned
[`GraphQuery.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query/GraphQuery.java).
Paged query code reasons about those partitions, while point reads route by key
digest. This distinction helps explain why AGS compute scale for a localized
point workload does not prove equivalent scaling for global scans. Adding AGS
instances can increase point-read concurrency against a fixed storage cluster;
global query streams still share Database partition, query-thread, device, and
network capacity.

A credible rerun publishes the exact Gremlin bytecode, parameters, expected
result cardinality distribution, optimized traversals, raw latency histograms,
offered and achieved load, every error and timeout, retry attempts, cache
preconditioning, Database command counts, and full configuration. The public
PDF does not provide that complete artifact set. Its numbers remain useful
vendor observations, but the missing material prevents recalculating percentiles
or determining whether retry, warmup, or omitted failures affect a chart.

| Claim form | Minimum evidence | Result if evidence is missing |
| --- | --- | --- |
| Faster point lookup | Same IDs, projection, cache budget, durability, concurrency, and raw latency distributions | Product-specific observation only |
| Faster traversal | Same path semantics, degree buckets, result cardinality, cycle rules, and optimized plans | Non-comparable workload |
| Higher throughput | Open-loop offered load, achieved load, errors, queueing, and saturated resource | Closed-loop QPS is insufficient |
| Lower resource use | Complete AGS, Database, replica, index, storage, network, and background ledger | Partial-process comparison rejected |
| Lower cost | Same region, term, replicas, SLO, support, license, backup, and operator scope | Cost marked unknown |
| Tenfold win | Lower confidence bound above ten with correctness gates passing | No tenfold claim |
| PB or trillion scale | Measured capacity, query SLO, recovery, and operational run at the named scale | Extrapolation labeled as a model only |

Each cell is a named comparison, not one row in a blended marketing score. The dataset manifest fixes degree distribution, property widths, index definitions, graph shape, and expected result cardinality. Engines receive equivalent semantics, acknowledgement rules, replication, client locality, and either the same hardware budget or the same monthly cost ceiling.

The load generator submits open-loop traffic and saves offered and achieved QPS, an HDR histogram, errors, timeouts, retries, and result hashes. Server-side plans, traces, command counts, CPU, memory, storage, network, background work, and cost are collected over the same interval. Cold and warm runs are separate. A case is non-comparable when an engine cannot implement the semantics; it is not removed from the published matrix.

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
<td>benchmark: ID vertex read cold</td>
<td>Compare authoritative point lookup without cache residency.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q002</td>
<td>benchmark: ID vertex read warm</td>
<td>Compare hot point lookup with charged cache memory.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q003</td>
<td>benchmark: batch 100 vertex IDs</td>
<td>Compare network and storage batching.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q004</td>
<td>benchmark: 1-hop degree 4</td>
<td>Represent small bounded adjacency.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q005</td>
<td>benchmark: 1-hop degree 32</td>
<td>Represent common identity expansion.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q006</td>
<td>benchmark: 1-hop degree 512</td>
<td>Expose batching and response size.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q007</td>
<td>benchmark: threshold-minus-one degree</td>
<td>Stress largest inline adjacency record.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q008</td>
<td>benchmark: threshold-plus-one degree</td>
<td>Expose supernode path discontinuity.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q009</td>
<td>benchmark: supernode 100K unfiltered</td>
<td>Measure unavoidable output and safety limits.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q010</td>
<td>benchmark: supernode 100K 0.1% filter</td>
<td>Measure server-side predicate pushdown.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q011</td>
<td>benchmark: 2-hop fanout 4</td>
<td>Bound frontier and path semantics.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q012</td>
<td>benchmark: 2-hop fanout 32</td>
<td>Expose intermediate materialization.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q013</td>
<td>benchmark: 3-hop identity SR5</td>
<td>Recreate vendor workload pattern exactly.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q014</td>
<td>benchmark: 4-hop cyclic</td>
<td>Measure visited/path work on cycles.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q015</td>
<td>benchmark: label root high selectivity</td>
<td>Compare indexed root planning.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q016</td>
<td>benchmark: label root low selectivity</td>
<td>Expose large-index result stream.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q017</td>
<td>benchmark: numeric equality index</td>
<td>Compare root filtering.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q018</td>
<td>benchmark: numeric range index</td>
<td>Compare range path.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q019</td>
<td>benchmark: string substring</td>
<td>Expose unsupported index and scan behavior.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q020</td>
<td>benchmark: global vertex scan</td>
<td>Compare bandwidth-oriented scan separately.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q021</td>
<td>benchmark: global edge scan</td>
<td>Reproduce AGS 3.2 version claim and competitors.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q022</td>
<td>benchmark: local count</td>
<td>Compare adjacency metadata optimization.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q023</td>
<td>benchmark: global exact count</td>
<td>Require exact consistent result.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q024</td>
<td>benchmark: path materialization</td>
<td>Charge full path objects.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q025</td>
<td>benchmark: dedup frontier</td>
<td>Charge state memory.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q026</td>
<td>benchmark: top-K order</td>
<td>Require same ordering/tie semantics.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q027</td>
<td>benchmark: add vertex</td>
<td>Compare durable acknowledged creation.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q028</td>
<td>benchmark: update vertex property</td>
<td>Compare contention-free update.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q029</td>
<td>benchmark: add ordinary edge</td>
<td>Compare three-record graph mutation semantics.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q030</td>
<td>benchmark: add hot edge</td>
<td>Compare contention and retries.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q031</td>
<td>benchmark: update edge property</td>
<td>Expose packed-record false sharing.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q032</td>
<td>benchmark: delete edge</td>
<td>Compare cleanup and read visibility.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q033</td>
<td>benchmark: delete ordinary vertex</td>
<td>Compare incident-edge atomicity.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q034</td>
<td>benchmark: delete supernode</td>
<td>Mark semantic limitation, not comparable success.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q035</td>
<td>benchmark: merge vertex</td>
<td>Require uniqueness and idempotence.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q036</td>
<td>benchmark: merge edge</td>
<td>Require same match/lock semantics.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q037</td>
<td>benchmark: explicit 10-record transaction</td>
<td>Compare atomic multi-query scope.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q038</td>
<td>benchmark: explicit 1000-record transaction</td>
<td>Expose transaction overhead.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q039</td>
<td>benchmark: read/write 95/5</td>
<td>Measure mixed online load.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q040</td>
<td>benchmark: read/write 50/50</td>
<td>Expose packing contention and cache invalidity.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q041</td>
<td>benchmark: scan plus point reads</td>
<td>Measure workload isolation.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q042</td>
<td>benchmark: supernode plus point reads</td>
<td>Measure heavy-query isolation.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q043</td>
<td>benchmark: one compute node</td>
<td>Establish resource-normalized baseline.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q044</td>
<td>benchmark: 2 compute nodes</td>
<td>Measure scale efficiency.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q045</td>
<td>benchmark: 4 compute nodes</td>
<td>Measure scale efficiency.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q046</td>
<td>benchmark: 8 compute nodes</td>
<td>Measure storage approach to saturation.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q047</td>
<td>benchmark: 16 compute nodes</td>
<td>Locate database/network bottleneck.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q048</td>
<td>benchmark: 32 compute nodes</td>
<td>Reproduce vendor throughput topology.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q049</td>
<td>benchmark: one DB node dev</td>
<td>Keep out of HA headline but measure floor.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q050</td>
<td>benchmark: three DB nodes RF2</td>
<td>Production-shaped minimum.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q051</td>
<td>benchmark: six DB nodes RF2</td>
<td>Measure storage horizontal scaling.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q052</td>
<td>benchmark: RF3</td>
<td>Compare stronger replica capacity.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q053</td>
<td>benchmark: rack-aware local</td>
<td>Measure cross-zone avoidance.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q054</td>
<td>benchmark: rack failure</td>
<td>Measure degraded latency and cost.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q055</td>
<td>benchmark: DB node failure</td>
<td>Measure p99.9 and errors through recovery.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q056</td>
<td>benchmark: AGS node failure</td>
<td>Measure load balancer and in-flight requests.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q057</td>
<td>benchmark: rebalance</td>
<td>Measure performance during add/remove.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q058</td>
<td>benchmark: cold restart</td>
<td>Measure query-ready time and cache state.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q059</td>
<td>benchmark: rolling patch</td>
<td>Measure operational availability.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q060</td>
<td>benchmark: 1GB load</td>
<td>Small-loader overhead.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q061</td>
<td>benchmark: 100GB load</td>
<td>Standalone/distributed crossover.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q062</td>
<td>benchmark: 1TB load</td>
<td>Reproduce 3.0 ingest claim.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q063</td>
<td>benchmark: 10TB load</td>
<td>Measure scale and Spark cost.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q064</td>
<td>benchmark: incremental 1% load</td>
<td>Measure daily refresh economics.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q065</td>
<td>benchmark: backup</td>
<td>Measure throughput and online impact.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q066</td>
<td>benchmark: restore</td>
<td>Measure query-ready RTO.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q067</td>
<td>benchmark: storage bytes per edge</td>
<td>Compare physical bytes including indexes/replicas.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q068</td>
<td>benchmark: RAM bytes per edge</td>
<td>Compare full-cluster resident memory.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q069</td>
<td>benchmark: CPU per million queries</td>
<td>Compare work efficiency at same SLO.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q070</td>
<td>benchmark: joules per million queries</td>
<td>Optional energy efficiency.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q071</td>
<td>benchmark: monthly cost at 10K QPS</td>
<td>Amortize all provisioned and licensed cost.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q072</td>
<td>benchmark: monthly cost at 100K QPS</td>
<td>Measure scale and headroom.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q073</td>
<td>benchmark: monthly cost at 600K QPS</td>
<td>Challenge vendor-scale claim fairly.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q074</td>
<td>benchmark: cost per billion edges</td>
<td>Include vertex ratio and properties.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q075</td>
<td>benchmark: cost per PB logical</td>
<td>Use capacity model with uncertainty.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q076</td>
<td>benchmark: S3 cold point read zu</td>
<td>Measure zu's object-authoritative cold path.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q077</td>
<td>benchmark: S3 warm point read zu</td>
<td>Measure bounded-cache steady state.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q078</td>
<td>benchmark: S3 outage zu</td>
<td>Preserve system semantics and availability disclosure.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q079</td>
<td>benchmark: semantic conformance corpus</td>
<td>Gate performance publication on equal results.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
<tr>
<td>Q080</td>
<td>benchmark: unsupported feature ledger</td>
<td>Prevent silent workload deletion.</td>
<td>S05,S10–S16,S18,S19,S25,S26,S28,S33–S45</td>
</tr>
</tbody>
</table>

## Tenfold claim acceptance rule

Publish `10x` only when the lower 95% confidence bound of the improvement ratio exceeds 10 for the named metric and cell, all correctness gates pass, achieved throughput meets offered load, error/timeout rate is within the common SLO, and total charged resources/cost obey the declared comparison mode. Label the numerator and denominator, version, hardware, cache state, consistency, RF, dataset, query, percentile, and run date in the claim sentence.

Never publish “10x faster than all graph databases.” A defensible sentence is narrower: for example, “zu commit X achieved 10.8–12.1x lower p99 latency than Aerospike Graph 3.2.3 on ID-rooted two-hop traversal Q17 at 20K offered QPS, RF2-equivalent durability, cold 8GB cache, and equal monthly infrastructure cost.”

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
<td>S05</td>
<td>AGS 3.2.0 release notes</td>
<td>Official documentation</td>
<td>Global cache, set cardinality, performance changes</td>
<td>https://aerospike.com/docs/graph/release/3-2-0/</td>
</tr>
<tr>
<td>S10</td>
<td>Transaction contract</td>
<td>Official documentation</td>
<td>Read, mutation, SC, AP, and MRT distinctions</td>
<td>https://aerospike.com/docs/graph/develop/query/transactions/</td>
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
<td>S25</td>
<td>Identity graph benchmark PDF</td>
<td>Vendor benchmark</td>
<td>AGS 2.4.2 / Database 7.1.0.9 test</td>
<td>https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf</td>
</tr>
<tr>
<td>S26</td>
<td>Graph 3.0 launch blog</td>
<td>Vendor blog</td>
<td>Ingest and footprint claims</td>
<td>https://aerospike.com/blog/aerospike-graph-3-release/</td>
</tr>
<tr>
<td>S28</td>
<td>Product editions and pricing</td>
<td>Official commercial page</td>
<td>Edition limits and data-volume licensing</td>
<td>https://aerospike.com/products/features-and-editions/</td>
</tr>
<tr>
<td>S33</td>
<td>AGS public source snapshot</td>
<td>Apache-2.0 source</td>
<td>3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045</td>
</tr>
<tr>
<td>S34</td>
<td>AGS data model design</td>
<td>Apache-2.0 source documentation</td>
<td>Packed record layout</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md</td>
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
<td>S40</td>
<td>AGS transaction implementation</td>
<td>Apache-2.0 source</td>
<td>TinkerPop transaction wrapper</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java</td>
</tr>
<tr>
<td>S41</td>
<td>AGS tests</td>
<td>Apache-2.0 source</td>
<td>431 test files observed in snapshot</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test</td>
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

<tr>
<td>S45</td>
<td>Apache TinkerPop 3.7.3 reference</td>
<td>Upstream documentation</td>
<td>Language/runtime semantic oracle</td>
<td>https://tinkerpop.apache.org/docs/3.7.3/reference/</td>
</tr>
</tbody>
</table>
