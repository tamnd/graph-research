# Benchmark and proof plan for a defensible tenfold advantage

Research cut: `2026-08-08`
Status: qualification protocol; no tenfold result is claimed yet.

## 1. Claim grammar

Allowed: `zu 0.x at commit X was 12.4x faster in p99 latency than LadybugDB Y for query Q on dataset D, hot-cache, 16 cores, equal result semantics, with peak RSS within Z, 95% bootstrap CI [a,b]`.

Forbidden: `zu is 10x faster than all graph databases`.

A competitor can win a different cell. The public scorecard reports latency, throughput, memory, physical bytes, build time, recovery, and dollars rather than selecting whichever metric favors zu.

## 2. Competitor tiers

- Tier A same-machine source builds: LadybugDB, Kuzu historical, FalkorDB, Memgraph, Neo4j Community, DuckPGQ, Apache AGE, Oxigraph, Jena TDB2, ArcadeDB, CozoDB, HelixDB.
- Tier B self-hosted distributed: Neo4j Enterprise/Infinigraph when licensed, NebulaGraph, TigerGraph, GraphScope Flex, JanusGraph+Cassandra/Scylla, HugeGraph HStore, Dgraph, ArangoDB, TuGraph Enterprise when available.
- Tier C managed: Neptune Database, Neptune Analytics, Spanner Graph, Cosmos Gremlin, Fabric Graph, PuppyGraph deployment, commercial semantic systems.
- Tier D historical/research: RedisGraph, Blazegraph, MillenniumDB, Kuzu archived.

## 3. Datasets

- LDBC SNB Interactive v1 at SF1/10/30/100/300/1000 as resources permit.
- LDBC SNB BI for scan, join, aggregation, and path-heavy analytics.
- Graphalytics canonical datasets and six algorithms with official reference outputs.
- GAP Benchmark graphs for kernel comparison.
- LiveJournal and Friendster for common topology microbenchmarks.
- Uniform synthetic graph to expose cache-friendly best cases.
- power-law and smooth-Kronecker graphs with recorded generator seed.
- adversarial supernode graph.
- high parallel-edge and self-loop correctness graph.
- property-heavy graph with compressible and incompressible columns.
- partition-local graph at multiple edge-cut ratios.
- temporal update stream with hot-vertex skew.

Every dataset has a URI, content digest, generator version/seed, exact node/edge counts including zero-degree nodes, ID ordering description, property distributions, connected-component statistics, degree quantiles, and expected-result digest.

## 4. Scale ladder

Run 10M, 100M, 1B, 10B, 100B, 1T edges. Beyond affordable physical runs, execute format/capacity validation with generated manifests and sampled partitions, but label it simulation. A PB claim requires at least one end-to-end remote namespace large enough to exercise sharded manifests, cache churn, GC, and repartitioning—not just multiplication from a 1-GB file.

## 5. Hardware classes

- Tiny: 4 cores, 8 GiB RAM, commodity SSD; tests resource efficiency and edge deployment.
- Standard: 16 physical cores, 64 GiB RAM, one enterprise NVMe.
- Memory: 32-64 cores, 512 GiB RAM for in-memory competitors.
- Distributed: identical nodes, 25/100-Gbit network, fixed aggregate CPU/RAM/NVMe.
- Remote: same-region S3 Standard and optional low-latency object tier, explicit cache nodes.

Record firmware, CPU governor, SMT, turbo, NUMA, kernel, mitigations, filesystem, mount flags, container limits, background processes, and ambient network measurements.

## 6. Measurement rules

Use a coordinated-omission-safe load generator. Run correctness before timing. Warm up to a declared state. Randomize engine and query order. Preserve raw per-operation timestamps. Use independent process restarts for cold trials. Publish confidence intervals and effect sizes. Do not average ratios. Do not discard outliers without a pre-registered hardware-failure rule.

Measure client-to-client latency, server service time, queue time, CPU time, cycles/instructions, context switches, page faults, RSS, allocator bytes, cache occupancy, local read/write bytes, network bytes, remote requests and bytes, retries, compaction, WAL, result bytes, and errors.

## 7. Tenfold gates

- Correctness gate: identical canonical results and supported semantics.
- Durability gate: equal acknowledgement level and fault tolerance.
- Resource gate: competitor and zu receive the same class limit; OOM is reported.
- Statistics gate: lower bound of the 95% confidence interval exceeds 10.0x.
- Repeatability gate: two independent operators reproduce within 10%.
- Transparency gate: configs, source patches, scripts, plans, and raw samples are public.
- Scope gate: title names the query, dataset, scale, cache state, hardware, and metric.

## 8. Required workloads

### 8.1 `point_pk`

Workload: primary-key node lookup with one projected property.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.2 `point_edge`

Workload: stable edge-ID lookup including endpoints and one property.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.3 `degree_1`

Workload: degree-one outgoing expansion.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.4 `degree_32`

Workload: small adjacency expansion around degree 32.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.5 `degree_1k`

Workload: medium adjacency expansion around degree 1,024.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.6 `supernode`

Workload: range-limited expansion of a ten-million-degree supernode.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.7 `expand_2`

Workload: selective two-hop expansion.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.8 `expand_3`

Workload: three-hop frontier expansion with duplicate control.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.9 `expand_into`

Workload: edge-existence/expand-into between already-bound endpoints.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.10 `multi_edge`

Workload: parallel-edge identity and property projection.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.11 `shortest`

Workload: bidirectional point-to-point unweighted shortest path.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.12 `weighted`

Workload: weighted shortest path with property access.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.13 `var_walk`

Workload: bounded variable-length walk.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.14 `trail`

Workload: DIFFERENT EDGES trail enumeration.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.15 `simple`

Workload: simple-path enumeration with explicit bound.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.16 `triangle`

Workload: triangle pattern with worst-case-sensitive join.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.17 `cycle4`

Workload: four-cycle pattern.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.18 `star_join`

Workload: high-fanout star pattern with property filters.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.19 `optional`

Workload: optional match preserving null/bag semantics.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.20 `aggregate`

Workload: grouped aggregate after traversal.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.21 `topk`

Workload: ordered top-k with late property materialization.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.22 `scan`

Workload: full projected property scan.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.23 `selective_scan`

Workload: zone/index-pruned selective property scan.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.24 `mixed`

Workload: concurrent short reads, complex reads, and updates.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.25 `ingest`

Workload: sustained transactional ingest with indexes enabled.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.26 `bulk`

Workload: initial bulk load including index/CSR build.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.27 `checkpoint`

Workload: checkpoint or compaction while readers remain active.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.28 `recovery`

Workload: crash recovery at bounded dirty-log size.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.29 `cold`

Workload: same query after clearing engine and OS/cache tiers.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

### 8.30 `remote`

Workload: same query with authoritative bytes only in object storage.

Variants: hot, warm, cold; one client and saturation; read-only and update interference; uniform and skewed parameters; small and large results.

Outputs: correctness digest, p50/p95/p99/p99.9, throughput, CPU/query, peak RSS, bytes read, requests/query, physical bytes, and cost per million operations.

Failure rule: an unsupported semantic feature is `unsupported`; timeout, OOM, wrong result, crash, and admission rejection are distinct outcomes.

## 9. S3-specific experiments

- Empty-cache first query at 1M, 1B, and multi-partition namespaces.
- One-hop and three-hop request count versus frontier size.
- Coalescing tradeoff curve: extra bytes versus saved requests.
- Cache hit bytes and hit operations separately.
- Cache loss storm with admission enabled.
- Tenfold QPS spike under fixed monthly envelope.
- SlowDown/429/503 injection and retry budget.
- Range corruption, truncation, wrong-content, and stale-manifest injection.
- Writer lease expiry and stale writer acknowledgement attempt.
- Lost response at every commit phase.
- GC race with publication, long reader pins, backups, and repartitioning.
- Cross-region and cross-zone traffic accounting.

## 10. Cost model

Monthly cost equals compute reservations plus ephemeral/NVMe cache plus object stored bytes plus PUT/COPY/LIST/GET/HEAD requests plus retrieval plus cross-zone and egress bytes plus metadata/control-plane services plus license/support. Every term names provider, region, price sheet date, and free-tier assumptions.

Fixed-price qualification replays the worst admitted workload for the plan and proves cost stays within reserve. A higher offered load may be rejected; the rejection is part of the contract and chart.

## 11. Publication artifacts

- Immutable harness repository commit.
- Engine adapters with license-safe patches.
- Container and binary digests.
- Datasets and expected-result digests.
- All configuration files.
- Commands and orchestration logs.
- Raw samples in an open columnar format.
- Plans, profiles, and traces.
- System telemetry.
- Analysis notebook or script.
- Failure and exclusion ledger.
- Signed result manifest.
- Independent reproduction report.

## 12. Competitive strategy

Target tenfold wins where architecture creates a structural advantage: compressed local adjacency, factorized property-heavy patterns, resource-bounded embedded operation, fast open/recovery, storage density, S3 request count, stateless read scaling, and total cost for cold large datasets. Target parity and compatibility where ecosystems dominate. Do not spend credibility trying to beat in-memory engines on all-hot algorithms with an S3 cold path.

## 13. Stop conditions

Do not publish if results depend on unequal durability, missing output materialization, hand-selected query parameters, hidden enterprise features, unreported wrong answers, disabled constraints, different datasets, cache-state ambiguity, a single run, or a competitor configuration rejected by its maintainers as unreasonable.

## 14. Sources

- [LDBC SNB Interactive](https://ldbcouncil.org/benchmarks/snb/interactive/)
- [LDBC Graphalytics](https://ldbcouncil.org/benchmarks/graphalytics/)
- [LDBC datasets](https://ldbcouncil.org/benchmarks/snb/datasets/)
- [SoK: The Faults in our Graph Benchmarks](https://arxiv.org/abs/2404.00766)

## Appendix A. Release-gate assertions

- RG-001: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-002: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-003: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-004: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-005: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-006: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-007: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-008: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-009: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-010: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-011: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-012: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-013: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-014: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-015: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-016: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-017: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-018: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-019: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-020: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-021: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-022: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-023: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-024: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-025: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-026: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-027: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-028: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-029: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-030: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-031: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-032: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-033: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-034: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-035: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-036: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-037: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-038: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-039: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-040: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-041: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-042: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-043: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-044: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-045: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-046: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-047: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-048: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-049: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-050: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-051: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-052: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-053: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-054: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-055: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-056: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-057: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-058: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-059: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-060: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-061: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-062: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-063: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-064: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-065: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-066: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-067: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-068: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-069: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-070: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-071: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-072: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-073: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-074: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-075: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-076: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-077: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-078: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-079: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-080: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-081: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-082: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-083: For the benchmark publication, release is blocked until timeouts and rejected operations remain in the result set.
- RG-084: For the benchmark publication, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-085: For the benchmark publication, release is blocked until background maintenance is either quiesced or reported.
- RG-086: For the benchmark publication, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-087: For the benchmark publication, release is blocked until the dataset and update-stream digests are immutable.
- RG-088: For the benchmark publication, release is blocked until the query plan/profile is archived.
- RG-089: For the benchmark publication, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-090: For the benchmark publication, release is blocked until a second operator can reproduce the run from a clean host.
- RG-091: For the benchmark publication, release is blocked until the raw samples and aggregated chart agree.
- RG-092: For the benchmark publication, release is blocked until the query result matches the canonical oracle.
- RG-093: For the benchmark publication, release is blocked until the engine version and artifact digest are recorded.
- RG-094: For the benchmark publication, release is blocked until the selected durability level matches the comparison class.
- RG-095: For the benchmark publication, release is blocked until cache state is explicit and reproducible.
- RG-096: For the benchmark publication, release is blocked until peak memory includes engine and required sidecars.
- RG-097: For the benchmark publication, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
