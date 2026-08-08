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

Each cell is a named comparison, not one row in a blended marketing score. The dataset manifest fixes degree distribution, property widths, index definitions, graph shape, and expected result cardinality. Engines receive equivalent semantics, acknowledgement rules, replication, client locality, and either the same hardware budget or the same monthly cost ceiling.

The load generator submits open-loop traffic and saves offered and achieved QPS, an HDR histogram, errors, timeouts, retries, and result hashes. Server-side plans, traces, command counts, CPU, memory, storage, network, background work, and cost are collected over the same interval. Cold and warm runs are separate. A case is non-comparable when an engine cannot implement the semantics; it is not removed from the published matrix.

### Q001 : benchmark: ID vertex read cold

**Purpose.** Compare authoritative point lookup without cache residency.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q002 : benchmark: ID vertex read warm

**Purpose.** Compare hot point lookup with charged cache memory.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q003 : benchmark: batch 100 vertex IDs

**Purpose.** Compare network and storage batching.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q004 : benchmark: 1-hop degree 4

**Purpose.** Represent small bounded adjacency.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q005 : benchmark: 1-hop degree 32

**Purpose.** Represent common identity expansion.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q006 : benchmark: 1-hop degree 512

**Purpose.** Expose batching and response size.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q007 : benchmark: threshold-minus-one degree

**Purpose.** Stress largest inline adjacency record.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q008 : benchmark: threshold-plus-one degree

**Purpose.** Expose supernode path discontinuity.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q009 : benchmark: supernode 100K unfiltered

**Purpose.** Measure unavoidable output and safety limits.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q010 : benchmark: supernode 100K 0.1% filter

**Purpose.** Measure server-side predicate pushdown.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q011 : benchmark: 2-hop fanout 4

**Purpose.** Bound frontier and path semantics.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q012 : benchmark: 2-hop fanout 32

**Purpose.** Expose intermediate materialization.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q013 : benchmark: 3-hop identity SR5

**Purpose.** Recreate vendor workload pattern exactly.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q014 : benchmark: 4-hop cyclic

**Purpose.** Measure visited/path work on cycles.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q015 : benchmark: label root high selectivity

**Purpose.** Compare indexed root planning.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q016 : benchmark: label root low selectivity

**Purpose.** Expose large-index result stream.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q017 : benchmark: numeric equality index

**Purpose.** Compare root filtering.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q018 : benchmark: numeric range index

**Purpose.** Compare range path.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q019 : benchmark: string substring

**Purpose.** Expose unsupported index and scan behavior.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q020 : benchmark: global vertex scan

**Purpose.** Compare bandwidth-oriented scan separately.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q021 : benchmark: global edge scan

**Purpose.** Reproduce AGS 3.2 version claim and competitors.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q022 : benchmark: local count

**Purpose.** Compare adjacency metadata optimization.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q023 : benchmark: global exact count

**Purpose.** Require exact consistent result.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q024 : benchmark: path materialization

**Purpose.** Charge full path objects.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q025 : benchmark: dedup frontier

**Purpose.** Charge state memory.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q026 : benchmark: top-K order

**Purpose.** Require same ordering/tie semantics.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q027 : benchmark: add vertex

**Purpose.** Compare durable acknowledged creation.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q028 : benchmark: update vertex property

**Purpose.** Compare contention-free update.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q029 : benchmark: add ordinary edge

**Purpose.** Compare three-record graph mutation semantics.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q030 : benchmark: add hot edge

**Purpose.** Compare contention and retries.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q031 : benchmark: update edge property

**Purpose.** Expose packed-record false sharing.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q032 : benchmark: delete edge

**Purpose.** Compare cleanup and read visibility.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q033 : benchmark: delete ordinary vertex

**Purpose.** Compare incident-edge atomicity.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q034 : benchmark: delete supernode

**Purpose.** Mark semantic limitation, not comparable success.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q035 : benchmark: merge vertex

**Purpose.** Require uniqueness and idempotence.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q036 : benchmark: merge edge

**Purpose.** Require same match/lock semantics.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q037 : benchmark: explicit 10-record transaction

**Purpose.** Compare atomic multi-query scope.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q038 : benchmark: explicit 1000-record transaction

**Purpose.** Expose transaction overhead.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q039 : benchmark: read/write 95/5

**Purpose.** Measure mixed online load.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q040 : benchmark: read/write 50/50

**Purpose.** Expose packing contention and cache invalidity.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q041 : benchmark: scan plus point reads

**Purpose.** Measure workload isolation.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q042 : benchmark: supernode plus point reads

**Purpose.** Measure heavy-query isolation.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q043 : benchmark: one compute node

**Purpose.** Establish resource-normalized baseline.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q044 : benchmark: 2 compute nodes

**Purpose.** Measure scale efficiency.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q045 : benchmark: 4 compute nodes

**Purpose.** Measure scale efficiency.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q046 : benchmark: 8 compute nodes

**Purpose.** Measure storage approach to saturation.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q047 : benchmark: 16 compute nodes

**Purpose.** Locate database/network bottleneck.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q048 : benchmark: 32 compute nodes

**Purpose.** Reproduce vendor throughput topology.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q049 : benchmark: one DB node dev

**Purpose.** Keep out of HA headline but measure floor.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q050 : benchmark: three DB nodes RF2

**Purpose.** Production-shaped minimum.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q051 : benchmark: six DB nodes RF2

**Purpose.** Measure storage horizontal scaling.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q052 : benchmark: RF3

**Purpose.** Compare stronger replica capacity.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q053 : benchmark: rack-aware local

**Purpose.** Measure cross-zone avoidance.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q054 : benchmark: rack failure

**Purpose.** Measure degraded latency and cost.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q055 : benchmark: DB node failure

**Purpose.** Measure p99.9 and errors through recovery.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q056 : benchmark: AGS node failure

**Purpose.** Measure load balancer and in-flight requests.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q057 : benchmark: rebalance

**Purpose.** Measure performance during add/remove.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q058 : benchmark: cold restart

**Purpose.** Measure query-ready time and cache state.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q059 : benchmark: rolling patch

**Purpose.** Measure operational availability.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q060 : benchmark: 1GB load

**Purpose.** Small-loader overhead.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q061 : benchmark: 100GB load

**Purpose.** Standalone/distributed crossover.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q062 : benchmark: 1TB load

**Purpose.** Reproduce 3.0 ingest claim.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q063 : benchmark: 10TB load

**Purpose.** Measure scale and Spark cost.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q064 : benchmark: incremental 1% load

**Purpose.** Measure daily refresh economics.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q065 : benchmark: backup

**Purpose.** Measure throughput and online impact.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q066 : benchmark: restore

**Purpose.** Measure query-ready RTO.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q067 : benchmark: storage bytes per edge

**Purpose.** Compare physical bytes including indexes/replicas.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q068 : benchmark: RAM bytes per edge

**Purpose.** Compare full-cluster resident memory.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q069 : benchmark: CPU per million queries

**Purpose.** Compare work efficiency at same SLO.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q070 : benchmark: joules per million queries

**Purpose.** Optional energy efficiency.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q071 : benchmark: monthly cost at 10K QPS

**Purpose.** Amortize all provisioned and licensed cost.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q072 : benchmark: monthly cost at 100K QPS

**Purpose.** Measure scale and headroom.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q073 : benchmark: monthly cost at 600K QPS

**Purpose.** Challenge vendor-scale claim fairly.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q074 : benchmark: cost per billion edges

**Purpose.** Include vertex ratio and properties.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q075 : benchmark: cost per PB logical

**Purpose.** Use capacity model with uncertainty.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q076 : benchmark: S3 cold point read zu

**Purpose.** Measure zu's object-authoritative cold path.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q077 : benchmark: S3 warm point read zu

**Purpose.** Measure bounded-cache steady state.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q078 : benchmark: S3 outage zu

**Purpose.** Preserve system semantics and availability disclosure.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q079 : benchmark: semantic conformance corpus

**Purpose.** Gate performance publication on equal results.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


### Q080 : benchmark: unsupported feature ledger

**Purpose.** Prevent silent workload deletion.

**Evidence anchors.** S05,S10–S16,S18,S19,S25,S26,S28,S33–S45


## Tenfold claim acceptance rule

Publish `10x` only when the lower 95% confidence bound of the improvement ratio exceeds 10 for the named metric and cell, all correctness gates pass, achieved throughput meets offered load, error/timeout rate is within the common SLO, and total charged resources/cost obey the declared comparison mode. Label the numerator and denominator, version, hardware, cache state, consistency, RF, dataset, query, percentile, and run date in the claim sentence.

Never publish “10x faster than all graph databases.” A defensible sentence is narrower: for example, “zu commit X achieved 10.8–12.1x lower p99 latency than Aerospike Graph 3.2.3 on ID-rooted two-hop traversal Q17 at 20K offered QPS, RF2-equivalent durability, cold 8GB cache, and equal monthly infrastructure cost.”

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S05 : AGS 3.2.0 release notes

**Type.** Official documentation

**Audit note.** Global cache, set cardinality, performance changes

**URL.** https://aerospike.com/docs/graph/release/3-2-0/


### S10 : Transaction contract

**Type.** Official documentation

**Audit note.** Read, mutation, SC, AP, and MRT distinctions

**URL.** https://aerospike.com/docs/graph/develop/query/transactions/


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


### S18 : Metrics reference

**Type.** Official documentation

**Audit note.** Prometheus metric inventory

**URL.** https://aerospike.com/docs/graph/reference/metrics/


### S19 : Query tracing

**Type.** Official documentation

**Audit note.** Zipkin tracing contract

**URL.** https://aerospike.com/docs/graph/observe/query-tracing/


### S25 : Identity graph benchmark PDF

**Type.** Vendor benchmark

**Audit note.** AGS 2.4.2 / Database 7.1.0.9 test

**URL.** https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf


### S26 : Graph 3.0 launch blog

**Type.** Vendor blog

**Audit note.** Ingest and footprint claims

**URL.** https://aerospike.com/blog/aerospike-graph-3-release/


### S28 : Product editions and pricing

**Type.** Official commercial page

**Audit note.** Edition limits and data-volume licensing

**URL.** https://aerospike.com/products/features-and-editions/


### S33 : AGS public source snapshot

**Type.** Apache-2.0 source

**Audit note.** 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045


### S34 : AGS data model design

**Type.** Apache-2.0 source documentation

**Audit note.** Packed record layout

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md


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


### S40 : AGS transaction implementation

**Type.** Apache-2.0 source

**Audit note.** TinkerPop transaction wrapper

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java


### S41 : AGS tests

**Type.** Apache-2.0 source

**Audit note.** 431 test files observed in snapshot

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test


### S43 : Database server source snapshot

**Type.** AGPL/community core source

**Audit note.** Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

**URL.** https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc


### S44 : Java client source snapshot

**Type.** Apache-2.0 source

**Audit note.** Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12

**URL.** https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12


### S45 : Apache TinkerPop 3.7.3 reference

**Type.** Upstream documentation

**Audit note.** Language/runtime semantic oracle

**URL.** https://tinkerpop.apache.org/docs/3.7.3/reference/
