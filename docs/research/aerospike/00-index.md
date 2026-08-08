# Aerospike Graph 2026 dossier: index, verdict, and evidence map

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: Navigation and decision summary for all Aerospike-specific specifications
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Outcome

Aerospike Graph is a serious comparator for low-latency distributed property-graph serving, especially when the graph is much larger than DRAM and the workload is bounded, ID-rooted, and dominated by ordinary-degree vertices. Its key design is not a graph-native distributed storage engine: it is a stateless TinkerPop/Gremlin JVM service that maps graph operations onto Aerospike Database records, collection operations, batch operations, filter expressions, secondary indexes, and—when explicitly enabled on the right edition—multi-record transactions.

It does not satisfy the project's S3-authoritative fixed-cost goal. S3 and GCS are bulk-loader inputs or backup destinations, while live authoritative graph records remain in an Aerospike namespace backed by memory and/or block/NVMe-class storage. Enterprise scale, strong consistency, rack awareness, TLS/ACLs, XDR, and multi-record transactions introduce commercial edition or add-on boundaries. The official pricing page says production licensing is primarily based on unique data volume, which is directly opposed to an S3-only fixed marginal-cost target.

There is no evidence for a universal tenfold win by Aerospike or against Aerospike. The current public identity benchmark is useful scale evidence—up to 38.3 billion vertices and 37.2 billion edges, 23.35 TB user dataset, and a vendor-reported 600K QPS with 32 AGS nodes—but it is vendor-run, uses AGS 2.4.2 and Database 7.1.0.9, exposes no raw sample archive in the PDF, contains no competitor run, and tests sparse localized identity subgraphs. It is not PB or trillion-edge proof.

## Dossier files

| File | Purpose |
| --- | --- |
| [01-product-releases-and-evidence.md](./01-product-releases-and-evidence.md) | Release chronology, product/edition boundary, source freshness, conflicts, claims |
| [02-source-code-and-storage-model.md](./02-source-code-and-storage-model.md) | Pinned source audit, sets/bins, packed edges, IDs, schema, indexes, supernodes |
| [03-gremlin-query-execution.md](./03-gremlin-query-execution.md) | TinkerPop contract, compiler strategies, I/O paths, caching, scans, profiling |
| [04-transactions-distribution-and-failure.md](./04-transactions-distribution-and-failure.md) | Read consistency, AP/SC mutations, MRT, TinkerPop transactions, failover |
| [05-operations-resources-security-and-cost.md](./05-operations-resources-security-and-cost.md) | Deployment, sizing, JVM/DB resources, monitoring, backup, S3, security, price |
| [06-benchmark-audit-and-10x-qualification.md](./06-benchmark-audit-and-10x-qualification.md) | Vendor benchmark deconstruction and reproducible comparison program |
| [07-design-lessons-for-zu.md](./07-design-lessons-for-zu.md) | Concrete design choices, avoidances, experiments, and acceptance gates for zu |

## Evidence precedence

- A reproducible observation from a pinned shipped artifact outranks documentation.
- Released 3.2.3 documentation outranks the 3.3.0-SNAPSHOT source tree for supported-product claims.
- Pinned source is authoritative for what that commit implements, not for what the 3.2.3 container contains.
- Release notes are authoritative for declared changes, not the magnitude of performance outside the vendor workload.
- Vendor benchmark numbers are recorded as vendor results until raw artifacts are independently rerun.
- Blogs are context and claim sources; they are never the sole semantic or durability oracle.
- Unknown remains Unknown when commercial internals, license terms, or raw benchmark data are absent.

## Fifty decision-relevant findings

### F01 — Current release

- Finding: 3.2.3 is the newest released version in the official release index on the research date.
- Evidence: S01,S02
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F02 — Source head

- Finding: The audited public AGS branch is 3.x-dev and declares 3.3.0-SNAPSHOT; signed v3.3.0-rc5 appeared on the research date.
- Evidence: S33,S46
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F03 — Open source

- Finding: AGS source carries Apache-2.0; the underlying Community Database core is AGPL while Enterprise features are commercial.
- Evidence: S32,S33,S43
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F04 — Protocol

- Finding: Clients send TinkerPop 3.7.x Gremlin bytecode over WebSocket; 3.8.x and 4.x are incompatible.
- Evidence: S09,S16,S33,S45
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F05 — Compute

- Finding: AGS instances are durable-state-free compute nodes and can be load balanced without AGS-to-AGS coordination.
- Evidence: S09,S35
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F06 — Storage authority

- Finding: Aerospike Database is authoritative; object storage is not on the online read/write path.
- Evidence: S09,S20,S22,S31
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F07 — Vertex layout

- Finding: A normal vertex maps to one record and carries label, properties, and cached adjacency.
- Evidence: S27,S34,S36
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F08 — Edge layout

- Finding: Logical edges are packed into shared edge records; the source default is 10 and accepted range is 1–100.
- Evidence: S34,S37
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F09 — Hop cost

- Finding: An ordinary traversal can exploit embedded adjacency and batch fetches, but it is not literally one storage read for every out() result.
- Evidence: S34,S36,S39
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F10 — Supernodes

- Finding: Large-degree vertices irreversibly leave the inline adjacency path and use secondary-index-backed edge records.
- Evidence: S12,S34
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F11 — Threshold

- Finding: Documentation estimates ~6,500 edges at 1 MiB max-record-size and ~800 at 128 KiB in HMA mode.
- Evidence: S12
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F12 — Indexes

- Finding: Vertex label/property indexes are supported; global edge label/property indexes are absent in the audited source design.
- Evidence: S11,S34
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F13 — Scan hazard

- Finding: Global V()/E() patterns may scan; 3.2.0 added global and per-traversal scan disable controls.
- Evidence: S05,S11
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F14 — Optimizer

- Finding: The code exposes more than twenty traversal strategies for batching, pushdown, local counts, IDs, caching, drop, and merge.
- Evidence: S39
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F15 — Default execution

- Finding: A query normally uses one Gremlin worker; per-query parallelize is intended for I/O-heavy high-fanout work.
- Evidence: S13,S37
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F16 — Read cache

- Finding: Transactional cache is default and request-local; global cache can be stale even after AGS writes.
- Evidence: S14,S37
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F17 — Read consistency

- Finding: The shipped transaction page explicitly classifies read-only queries as eventual-consistency reads.
- Evidence: S10
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F18 — Mutation consistency

- Finding: Atomic/isolated multi-record graph mutations require SC plus enabled MRT on Enterprise Database 8+.
- Evidence: S10
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F19 — AP risk

- Finding: AP mode lacks MRT/TinkerPop transactions and can lose writes during splits; only enumerated mutation forms are atomic.
- Evidence: S10
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F20 — Transaction limit

- Finding: A TinkerPop transaction can modify at most 4096 records and cannot use scans or indexes.
- Evidence: S10
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F21 — Supernode drop

- Finding: Dropping a supernode is best-effort even in the documented transaction mode.
- Evidence: S10,S36
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F22 — MRT default

- Finding: Both aerospike.graph.mrt.enabled and aerospike.graph.tx.enabled default false in source.
- Evidence: S37
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F23 — Release storage change

- Finding: 3.0 introduced a new data layout and vendor-claimed up to 50% lower footprint; migration/reload must be qualified.
- Evidence: S08,S26
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F24 — 3.2 cache

- Finding: Global cache arrived in 3.2.0 and is a correctness/performance mode, not a transparent optimization.
- Evidence: S05,S14
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F25 — 3.2 scan claim

- Finding: 3.2.0 claims 10x faster g.E() scans, which is version-over-version and not competitor evidence.
- Evidence: S05
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F26 — 3.2 security

- Finding: 3.2.3 lists fourteen CVE fixes, so earlier 3.2 images should not be baseline candidates.
- Evidence: S02
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F27 — Bulk path

- Finding: Large loads are external Spark jobs and may stage input on S3/GCS; Spark cost must be charged.
- Evidence: S20,S21
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F28 — 3.0 ingest claim

- Finding: The launch blog reports 1 TB under three hours versus more than 32 hours on 2.6 using the same infrastructure.
- Evidence: S26
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F29 — Published large run

- Finding: The identity benchmark reaches 38.3B vertices, 37.2B edges, and 23.35TB user data.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F30 — Benchmark workload shape

- Finding: The dataset is many sparse localized subgraphs, not one deep/high-diameter or supernode-heavy graph.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F31 — Benchmark topology

- Finding: Largest latency run used 18 database nodes, one 8-vCPU AGS, RF2, and HMA on local NVMe.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F32 — Throughput claim

- Finding: The vendor reports 22K QPS on one AGS to over 600K on 32 AGS nodes with fixed storage.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F33 — Missing raw data

- Finding: The PDF charts do not provide a machine-readable raw latency sample bundle or exact query source archive.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F34 — No comparison

- Finding: The identity report contains no same-hardware competitor run and cannot support a 10x competitor claim.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F35 — No PB proof

- Finding: Neither current public benchmark nor release material demonstrates a PB live graph.
- Evidence: S01,S25,S26
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F36 — No trillion-edge proof

- Finding: 37.2B edges is substantial but ~27x below one trillion and ~27,000x below one quadrillion.
- Evidence: S25
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F37 — Primary-index pressure

- Finding: Edge packing reduces record count and therefore underlying primary-index metadata, but vertices remain record-per-vertex.
- Evidence: S34,S43
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F38 — Resource floor

- Finding: AGS is a JVM/TinkerPop service plus an Aerospike cluster; one process RSS is not the system resource footprint.
- Evidence: S09,S35
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F39 — Cost boundary

- Finding: Enterprise pricing is contact-only and primarily unique-production-data-volume based.
- Evidence: S28
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F40 — CE boundary

- Finding: Community Edition is free but capped at 8 nodes and 2.5TB on the current edition page and lacks key enterprise features.
- Evidence: S28
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F41 — S3 mismatch

- Finding: S3 lowers load/backup storage cost but cannot replace the live namespace without changing the engine.
- Evidence: S20,S22,S31
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F42 — Backup

- Finding: Graph backup delegates to Aerospike backup/restore; consistency, indexes, metadata, and restore time need an end-to-end drill.
- Evidence: S22
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F43 — Multi-tenancy

- Finding: Graphs can share a namespace, but logical tenancy does not prove performance or failure isolation.
- Evidence: S24
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F44 — Security layers

- Finding: Client-to-AGS TLS/JWT and AGS-to-Database TLS/RBAC are distinct configurations and failure domains.
- Evidence: S23
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F45 — Rack-aware reads

- Finding: AGS 3.2.1 exposes Aerospike client rack awareness; it affects locality, not data placement by itself.
- Evidence: S04,S44
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F46 — Observability

- Finding: Prometheus, health, query tracing, scan profiling, cache stats, and database stats must be correlated.
- Evidence: S18,S19
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F47 — Conflict: client version

- Finding: The source POM pins 10.3.0 while its compatibility prose says 9.3.x; the POM wins for that commit.
- Evidence: S33
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F48 — Conflict: MRT minimum

- Finding: Shipped docs require EE 8.0+, while source prose contains broader 7.0+/6.0 statements; qualify against shipped docs.
- Evidence: S10,S33
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F49 — Upgrade evidence

- Finding: The public tags observed are 3.3 release candidates; no tag maps the audited source to the 3.2.3 shipped image, so source-to-binary equivalence is unproven.
- Evidence: S02,S33,S46
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

### F50 — zu opportunity

- Finding: S3 authority, compact immutable adjacency, bounded caching, vectorized native execution, and transparent cost counters target its gaps.
- Evidence: inference
- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.

## Immediate competitive stance

| Goal | Aerospike posture | Qualification consequence |
| --- | --- | --- |
| Very low latency | Strong candidate for bounded ID-rooted traversals on HMA/NVMe | Split normal, threshold, and supernode regimes; report p50/p95/p99/p99.9 and backend operations |
| Very low resources | Edge packing helps DB metadata; AGS JVM and PI/SI RAM remain | Charge all AGS, DB replicas, Spark, page cache, and storage headroom |
| Distributed | Stateless compute over sharded replicated DB | Test compute scale and storage saturation separately |
| Fixed cost | Commercial licensing is data-volume based; infra is provisioned | Cannot label fixed-cost without a quoted contract and capacity envelope |
| S3 authority | Unsupported for live graph | Treat as architectural non-fit, not a tuning gap |
| PB/trillion scale | Public proof stops at tens of TB/billions | Require derived capacity plus staged empirical validation |
| 10x | No comparable public proof | Claim only per workload cell under equal semantics and resources |

## Open evidence that blocks stronger conclusions

### U01 — 3.2.3 source equivalence

- Current gap: No public tag or attestation maps the audited 3.3 snapshot to the shipped 3.2.3 image.
- Closure condition: Archive image/SBOM and request vendor source provenance.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U02 — Raw benchmark samples

- Current gap: The public identity PDF provides charts and summaries but no raw HDR/sample archive.
- Closure condition: Obtain raw output or rerun from a published harness.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U03 — Exact benchmark Gremlin

- Current gap: Descriptions of SR1–SR5 and SW1–SW5 are not executable query definitions.
- Closure condition: Publish bytecode/scripts, parameters, and result-cardinality distributions.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U04 — Benchmark cache state

- Current gap: The report does not fully specify AGS/database cache preconditioning for every graph.
- Closure condition: Run named cold, warm, and steady-state phases.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U05 — Benchmark errors/retries

- Current gap: The report does not expose per-query timeout, error, and retry counts alongside QPS.
- Closure condition: Require offered/achieved load and all outcomes.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U06 — Current 3.2 performance

- Current gap: The large identity run used AGS 2.4.2, not 3.2.3.
- Closure condition: Repeat on 3.2.3 with Database 8.1.2 and publish deltas.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U07 — Independent competitor results

- Current gap: No same-hardware Neo4j, TigerGraph, Neptune, JanusGraph, FalkorDB, Kuzu, or zu run is cited.
- Closure condition: Use the cross-engine protocol in specification 06.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U08 — PB deployment

- Current gap: No public configuration demonstrates a PB live graph with query SLOs.
- Closure condition: Build capacity model, then validate by a scale ladder.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U09 — Trillion-edge deployment

- Current gap: The largest cited public run is 37.2B edges.
- Closure condition: Do not extrapolate linearly through supernode, index, and operational limits.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U10 — Graph license quote

- Current gap: The public page explains general data-volume pricing but not a reproducible Graph quote.
- Closure condition: Obtain written quote including SC/MRT, DR, non-prod, and support.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U11 — Graph on Community Edition

- Current gap: 3.2.2 removed a feature check, but the supported production combination and limitations remain ambiguous.
- Closure condition: Run basic compatibility and obtain a support statement.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U12 — Unique-data accounting

- Current gap: It is unclear which logical/physical graph bytes enter commercial billing.
- Closure condition: Reconcile contract definitions with record/index/replica expansion.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U13 — Exact record expansion 3.2

- Current gap: Source documents explain layout but do not replace measured physical bytes for each workload.
- Closure condition: Inspect namespace/storage statistics and backups on the pinned image.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U14 — Global cache freshness bound

- Current gap: Documentation says cache can be stale but gives no maximum staleness.
- Closure condition: Treat it as unbounded until an invalidation/freshness mechanism is proven.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U15 — Read snapshot semantics

- Current gap: Read-only traversals are eventual, but exact per-hop snapshot guarantees are not stated.
- Closure condition: Run concurrent graph-history tests across multi-hop queries.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U16 — AP partial-write repair

- Current gap: Source design hides partial adjacency, but operational reclamation guarantees are not fully quantified.
- Closure condition: Inject failures and measure stranded bytes and repair behavior.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U17 — Supernode drop completion

- Current gap: Best-effort is documented without a universal completion/RTO guarantee.
- Closure condition: Test degree ladder, faults, retries, and post-drop audits.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U18 — Index build isolation

- Current gap: Release/docs describe asynchronous creation but not an SLO under concurrent production load.
- Closure condition: Measure CPU/RAM/I/O and short-query p99.9 during build/drop.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U19 — Migration tail at scale

- Current gap: Stateless AGS scaling does not establish query tails while DB partitions rebalance.
- Closure condition: Fault/add/remove nodes under open-loop traffic.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U20 — Restore query-ready RTO

- Current gap: Backup delegation alone does not establish full graph recovery including indexes and metadata.
- Closure condition: Time complete restore and semantic verification drills.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U21 — Cross-region graph consistency

- Current gap: XDR branding does not define atomic ordering of related graph records remotely.
- Closure condition: Record remote histories for vertex/edge mutations and conflict.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U22 — OLAP maturity

- Current gap: Source contains a Spark GraphComputer path, but current product support/performance coverage is not established here.
- Closure condition: Qualify algorithms separately from online Gremlin.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U23 — Long-running query admission

- Current gap: Scan disable helps, but fleet-wide resource governance and fairness need empirical proof.
- Closure condition: Mix scans/supernodes with latency-critical point traffic.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U24 — Container resource formula

- Current gap: 3.2.1 is container-aware, but actual heap/native/RSS behavior depends on runtime flags and workload.
- Closure condition: Measure cgroup limits, OOM, GC, and direct memory.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

### U25 — Source documentation drift

- Current gap: POM/client and MRT compatibility prose conflict inside the public snapshot.
- Closure condition: Prefer executable metadata and open upstream issues for drift.
- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S01 — AGS release index

- Type: Official documentation
- Audit note: 2026-06-30 latest listed release
- URL: https://aerospike.com/docs/graph/release

### S02 — AGS 3.2.3 release notes

- Type: Official documentation
- Audit note: Security-only patch; 14 CVEs listed
- URL: https://aerospike.com/docs/graph/release/3-2-3/

### S05 — AGS 3.2.0 release notes

- Type: Official documentation
- Audit note: Global cache, set cardinality, performance changes
- URL: https://aerospike.com/docs/graph/release/3-2-0/

### S09 — Architecture

- Type: Official documentation
- Audit note: Three-layer request path
- URL: https://aerospike.com/docs/graph/overview/architecture/

### S10 — Transaction contract

- Type: Official documentation
- Audit note: Read, mutation, SC, AP, and MRT distinctions
- URL: https://aerospike.com/docs/graph/develop/query/transactions/

### S12 — Supernodes

- Type: Official documentation
- Audit note: Thresholds and filtered traversal guidance
- URL: https://aerospike.com/docs/graph/develop/query/supernodes/

### S14 — Cache management

- Type: Official documentation
- Audit note: Transactional and global record caches
- URL: https://aerospike.com/docs/graph/manage/cache/

### S25 — Identity graph benchmark PDF

- Type: Vendor benchmark
- Audit note: AGS 2.4.2 / Database 7.1.0.9 test
- URL: https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf

### S26 — Graph 3.0 launch blog

- Type: Vendor blog
- Audit note: Ingest and footprint claims
- URL: https://aerospike.com/blog/aerospike-graph-3-release/

### S28 — Product editions and pricing

- Type: Official commercial page
- Audit note: Edition limits and data-volume licensing
- URL: https://aerospike.com/products/features-and-editions/

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S34 — AGS data model design

- Type: Apache-2.0 source documentation
- Audit note: Packed record layout
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md

### S43 — Database server source snapshot

- Type: AGPL/community core source
- Audit note: Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc
- URL: https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

### S46 — AGS v3.3.0-rc5 prerelease tag

- Type: Signed public source tag
- Audit note: Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3
- URL: https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3
