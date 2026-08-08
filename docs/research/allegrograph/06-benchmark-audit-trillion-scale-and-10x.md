# AllegroGraph benchmark audit, trillion-scale evidence, and 10x protocol

Research cut: `2026-08-08`
Product baseline: `AllegroGraph 9.0.2`
Evidence status: current manual audited; public client/container source pinned; proprietary server internals unavailable
Scope: Historical claims, independent-result gap, reproducibility, scale extrapolation and an honest competitor benchmark

## Audit outcome

Franz publishes four unusually large historical load rows: 1.106 billion and 22.12 billion LUBM triples at about 500 thousand triples per second, plus pre-release 310.269-billion and 1.009-trillion loads at about 1.10 million and 830 thousand triples per second. The machines had 1–2 TB RAM, tens of terabytes of disk and 32–240 cores. These are useful capacity-history artifacts.

They are not a current competitor benchmark. The page lacks 9.0.2 identity, query latency, update mix, result correctness, durability mode, failure behavior, index/storage breakdown, FedShard/MMR topology, S3 economics and raw artifacts. A 10x claim must be earned separately per workload family under semantic, durability, resource and cost parity. “All competitors” is not statistically or operationally meaningful without a declared roster and versioned matrix.

| Dimension | Audited status | Target implication |
| --- | --- | --- |
| Low latency | Plausible with warm mapped indices; workload-specific and unmeasured here | Test cold, warm, checkpoint and saturation tails |
| Low resource | Default index and memory guidance are substantial | Minimize permutations and make caches disposable |
| Distributed | FedShard partitions; MMR replicates | Keep placement, durability and capacity contracts separate |
| Fixed S3 cost | S3 is archive/import, not live authority | Use immutable object segments plus hard budgets |
| PB / extreme edges | Historical trillion load; no PB or thousand-trillion proof | Require measured staged qualification |
| 10x | No current audited universal result | Use correctness-first family-specific ratios |

## Audited findings

### F001 — Current baseline

- Finding: The current manual identifies AllegroGraph 9.0.2 and was updated 2026-06-24; every result must pin the exact server build and license.
- Evidence anchors: S01,S03,S05
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F002 — Product form

- Finding: The server is a proprietary Linux x86-64 distribution; the audit found no public server storage, optimizer or replication implementation.
- Evidence anchors: S05,S23,S40-S43
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F003 — Public source boundary

- Finding: Python, Java and Docker repositories reveal wire contracts and packaging, not server algorithms or physical-format implementation.
- Evidence anchors: S35-S43
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F004 — Data model

- Finding: The core model is RDF triples/quads with unique repository-local triple IDs and optional immutable triple attributes.
- Evidence anchors: S04,S07,S26,S48
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F005 — Query surfaces

- Finding: AllegroGraph supports SPARQL, Prolog and APIs plus reasoning, text, geospatial, temporal, social-network and vector facilities.
- Evidence anchors: S04,S09-S13,S27-S30
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F006 — Index form

- Finding: Disk-resident triple indices are selected permutations of subject, predicate, object and graph followed by triple ID.
- Evidence anchors: S07
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F007 — Default indices

- Finding: New repositories normally carry seven indices: spogi, posgi, psogi, ospgi, gspoi, gposi and i.
- Evidence anchors: S07
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F008 — Storage rule

- Finding: Franz gives roughly 100 bytes per triple for the default index set; this is a planning heuristic, not a measured universal constant.
- Evidence anchors: S07
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F009 — String table

- Finding: IRIs and strings are stored once and indices use identifiers; encoded numeric-like values support range access.
- Evidence anchors: S07
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F010 — Optimization

- Finding: Insert/delete churn degrades index optimality and background or explicit optimization rewrites index structures.
- Evidence anchors: S07,S08
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F011 — Query engines

- Finding: SBQE is the default; MJQE trades different joins, caching and lower-memory/path behavior and is used for FedShard.
- Evidence anchors: S09,S15-S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F012 — Path risk

- Finding: The query-engine manual warns that path evaluation can grow combinatorially and exhaust resources; paging is a mitigation, not a proof of bounded work.
- Evidence anchors: S09
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F013 — Transaction model

- Finding: Transactions use snapshot isolation without triple locking; application-level semantic constraints remain the application's responsibility.
- Evidence anchors: S14
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F014 — Commit durability

- Finding: Commit records the transaction log and waits for log I/O before returning under the documented local contract.
- Evidence anchors: S14
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F015 — FedShard role

- Finding: FedShard horizontally partitions a logical repository across shard repositories using a required part or attribute key.
- Evidence anchors: S15-S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F016 — Broadcast execution

- Finding: FedShard modifies and sends queries to shards in parallel, then combines results; shards execute isolated from each other.
- Evidence anchors: S15-S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F017 — Partition-key sensitivity

- Finding: Locality and cross-shard work depend on the selected subject, predicate, object, graph or attribute partition key.
- Evidence anchors: S15-S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F018 — Elasticity boundary

- Finding: Splitting a shard is offline and is the supported topology change; arbitrary redefinition can make triples inaccessible.
- Evidence anchors: S16,S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F019 — MMR role

- Finding: MMR is active-active replication for availability and read/write service, separate from capacity partitioning.
- Evidence anchors: S18
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F020 — Replication ordering

- Finding: MMR commits can reach a replica in a different causal order; documentation warns transient triple counts can be inaccurate or even negative.
- Evidence anchors: S18
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F021 — Controller risk

- Finding: A forced controller replacement can leave two nodes believing they control configuration when the old controller returns, demanding external fencing discipline.
- Evidence anchors: S18
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F022 — S3 boundary

- Finding: S3 is supported for import and archive backup/restore, not as the authoritative online random-access triple/index store.
- Evidence anchors: S19,S20,S50
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F023 — Distributed backup

- Finding: A FedShard archive requires all participating servers to be available; the backup path is not shard-failure independent.
- Evidence anchors: S19
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F024 — Memory model

- Finding: The server relies heavily on shared memory and memory-mapped files, allowing the OS page cache to dominate warm-query behavior.
- Evidence anchors: S08,S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F025 — Checkpoint tails

- Finding: The default checkpoint interval is five minutes and commits are blocked during checkpoint; large checkpoints can take tens of seconds.
- Evidence anchors: S08,S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F026 — Connection resources

- Finding: Dedicated sessions bypass frontend routing but consume server resources; throughput eventually declines beyond the useful concurrency point.
- Evidence anchors: S08,S12
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F027 — Sizing floor

- Finding: Franz recommends SSD, at least 16 GB for initial use and substantially more memory and cores for multi-billion-triple production stores.
- Evidence anchors: S06,S08
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F028 — Free limit

- Finding: The free edition is capped at five million triples; larger and clustered evaluation requires a commercial license and a quote.
- Evidence anchors: S05,S34
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F029 — Historical trillion claim

- Finding: The vendor page reports a pre-release 1.009-trillion-triple load, but not a current 9.0.2 query, durability, failure or cost benchmark.
- Evidence anchors: S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F030 — No current audited 10x proof

- Finding: No same-hardware, same-data, same-semantics audited result was found that proves AllegroGraph or the proposed design is 10x faster than all competitors.
- Evidence anchors: S32,S44-S47
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F031 — PB gap

- Finding: A trillion triples is not automatically a petabyte, and the historical result does not establish PB online operation or thousand-trillion-edge capacity.
- Evidence anchors: S07,S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F032 — Cost gap

- Finding: Contact pricing, local SSD/RAM authority and replica/index amplification prevent a defensible fixed-cost-to-S3 claim without a written quote and measured footprint.
- Evidence anchors: S05,S07,S18-S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F033 — 1.106B row

- Finding: The vendor reports 36m49s and 500,679 triples/s on a 32-core, 1 TB system.
- Evidence anchors: S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F034 — 22.12B row

- Finding: The vendor reports 12h18m16s and 499,188 triples/s on the same stated machine class.
- Evidence anchors: S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F035 — 310.269B row

- Finding: A pre-release row reports 78h9m23s and 1,102,737 triples/s on 64 cores, 2 TB RAM and 22 TB disk.
- Evidence anchors: S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F036 — 1.009T row

- Finding: A pre-release row reports 338h5m and 829,556 triples/s on 240 cores, 1.28 TB RAM and 88 TB disk.
- Evidence anchors: S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F037 — Version ambiguity

- Finding: Pre-release identity cannot be mapped to the present query, storage or distributed implementation.
- Evidence anchors: S02,S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F038 — Load-only boundary

- Finding: Bulk-load throughput does not predict point lookup, traversal, SPARQL join, update or recovery latency.
- Evidence anchors: S32,S44-S49
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F039 — Scale conversion

- Finding: At the 100-byte heuristic, a trillion triples suggests roughly 100 TB for defaults, before operational copies and headroom.
- Evidence anchors: S07,S32
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F040 — Independent gap

- Finding: No current LDBC audited AllegroGraph submission was found; absence is not evidence of poor performance, only of missing public proof.
- Evidence anchors: S44,S45
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F041 — Historical SPARQL suites

- Finding: LUBM, SP2Bench and BSBM cover useful RDF behaviors but must be updated, versioned and combined with operational tests.
- Evidence anchors: S32,S46,S47
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F042 — 10x statistic

- Finding: Use per-query ratios and workload-family geometric means with confidence intervals; never hide regressions in one grand throughput number.
- Evidence anchors: Benchmark design
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F043 — Cost parity

- Finding: Normalize total monthly cost and fixed ceilings as well as identical hardware, because the target explicitly values fixed S3 economics.
- Evidence anchors: Benchmark design,S50
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F044 — Correctness first

- Finding: Any wrong, partial or stale result outside the declared contract scores as failure regardless of speed.
- Evidence anchors: S44,S48,S49
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

## Qualification matrix

Every case is an independent result cell. Preserve query semantics and failure behavior. Report p50, p95, p99, p99.9 and maximum, plus errors and timeouts; never average percentiles or silently omit failed operations.

### Q001 — 06-benchmark-audit-trillion-scale-and-10x: historical row transcription

- Purpose: Preserve exact published counts, rates, time and hardware
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `historical row transcription` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q002 — 06-benchmark-audit-trillion-scale-and-10x: artifact request

- Purpose: Seek configs, data generator, logs and raw results
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `artifact request` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q003 — 06-benchmark-audit-trillion-scale-and-10x: LUBM small

- Purpose: Validate semantics and measurement harness
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `LUBM small` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q004 — 06-benchmark-audit-trillion-scale-and-10x: LUBM one billion

- Purpose: Compare current load and query behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `LUBM one billion` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q005 — 06-benchmark-audit-trillion-scale-and-10x: BSBM explore

- Purpose: Measure read-heavy SPARQL
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `BSBM explore` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q006 — 06-benchmark-audit-trillion-scale-and-10x: BSBM update

- Purpose: Measure mixed transactions and correctness
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `BSBM update` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q007 — 06-benchmark-audit-trillion-scale-and-10x: SP2Bench

- Purpose: Exercise SPARQL operator diversity
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SP2Bench` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q008 — 06-benchmark-audit-trillion-scale-and-10x: LDBC SNB BI

- Purpose: Exercise analytical graph joins under rules
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `LDBC SNB BI` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q009 — 06-benchmark-audit-trillion-scale-and-10x: LDBC SNB interactive

- Purpose: Exercise updates and latency if a compliant adapter exists
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `LDBC SNB interactive` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q010 — 06-benchmark-audit-trillion-scale-and-10x: point lookup

- Purpose: Measure minimum serving latency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `point lookup` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q011 — 06-benchmark-audit-trillion-scale-and-10x: one-hop

- Purpose: Measure degree-stratified adjacency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `one-hop` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q012 — 06-benchmark-audit-trillion-scale-and-10x: multi-hop bounded

- Purpose: Measure selective traversal
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `multi-hop bounded` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q013 — 06-benchmark-audit-trillion-scale-and-10x: property path adversarial

- Purpose: Expose combinatorial resource behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `property path adversarial` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q014 — 06-benchmark-audit-trillion-scale-and-10x: reasoning

- Purpose: Separate dynamic and materialized costs
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `reasoning` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q015 — 06-benchmark-audit-trillion-scale-and-10x: bulk load

- Purpose: Report parse, commit, index and optimize phases
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `bulk load` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q016 — 06-benchmark-audit-trillion-scale-and-10x: stream ingest

- Purpose: Report durable small-batch p99
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `stream ingest` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q017 — 06-benchmark-audit-trillion-scale-and-10x: update churn

- Purpose: Include delete, optimize and storage debt
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `update churn` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q018 — 06-benchmark-audit-trillion-scale-and-10x: cold query

- Purpose: Charge first-touch local storage
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `cold query` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q019 — 06-benchmark-audit-trillion-scale-and-10x: warm query

- Purpose: Declare cache residency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `warm query` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q020 — 06-benchmark-audit-trillion-scale-and-10x: checkpoint query

- Purpose: Capture periodic tails
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `checkpoint query` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q021 — 06-benchmark-audit-trillion-scale-and-10x: node failure

- Purpose: Score availability and lost acknowledgements
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `node failure` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q022 — 06-benchmark-audit-trillion-scale-and-10x: network partition

- Purpose: Score consistency and convergence
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `network partition` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q023 — 06-benchmark-audit-trillion-scale-and-10x: shard split

- Purpose: Charge downtime and operator work
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `shard split` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q024 — 06-benchmark-audit-trillion-scale-and-10x: backup restore

- Purpose: Charge RPO, RTO and all storage
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `backup restore` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q025 — 06-benchmark-audit-trillion-scale-and-10x: one-billion scale

- Purpose: Publish exact resources and cost
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `one-billion scale` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q026 — 06-benchmark-audit-trillion-scale-and-10x: one-trillion scale

- Purpose: Require measured run rather than linear extrapolation
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `one-trillion scale` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q027 — 06-benchmark-audit-trillion-scale-and-10x: PB physical

- Purpose: Define logical versus physical bytes
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `PB physical` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q028 — 06-benchmark-audit-trillion-scale-and-10x: thousand-trillion projection

- Purpose: Label infeasible or unvalidated dimensions honestly
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `thousand-trillion projection` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q029 — 06-benchmark-audit-trillion-scale-and-10x: competitor roster

- Purpose: Pin popular engines, editions and tuning rules
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `competitor roster` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q030 — 06-benchmark-audit-trillion-scale-and-10x: same semantics

- Purpose: Map RDF/property-graph differences without weakening workloads
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `same semantics` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q031 — 06-benchmark-audit-trillion-scale-and-10x: same durability

- Purpose: Align acknowledgement and replica policy
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `same durability` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q032 — 06-benchmark-audit-trillion-scale-and-10x: same cost

- Purpose: Cap compute, RAM, SSD, network, licenses and labor
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `same cost` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q033 — 06-benchmark-audit-trillion-scale-and-10x: 10x confidence

- Purpose: Bootstrap ratios and publish uncertainty
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `10x confidence` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q034 — 06-benchmark-audit-trillion-scale-and-10x: regression veto

- Purpose: Reject universal claim when a declared family loses
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `regression veto` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q035 — 06-benchmark-audit-trillion-scale-and-10x: raw release

- Purpose: Publish every sample, timeout and exclusion
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `raw release` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q036 — 06-benchmark-audit-trillion-scale-and-10x: third-party audit

- Purpose: Have independent reviewers reproduce headline cells
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `third-party audit` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

## Source register

Official status establishes what Franz documents or distributes, not measured performance. Public source links are commit-pinned, but they cover clients and packaging rather than the proprietary server engine. Historical and marketing evidence is never promoted to a current audited benchmark.

### S01 — 9.0.2 release notes

- Type: Official documentation
- Audit note: Current maintenance release and change chronology
- URL: https://franz.com/agraph/support/documentation/release-notes.html

### S02 — 9.0.0 release notes

- Type: Official documentation
- Audit note: GraphTalker introduction and removal of the legacy distributed-store system
- URL: https://franz.com/agraph/support/documentation/9.0.0/release-notes.html

### S03 — Documentation index

- Type: Official documentation
- Audit note: Current 9.0.2 manual surface
- URL: https://franz.com/agraph/support/documentation/

### S04 — Introduction

- Type: Official documentation
- Audit note: Product model, query languages, reasoning, transactions and APIs
- URL: https://franz.com/agraph/support/documentation/agraph-introduction.html

### S05 — Downloads

- Type: Official distribution
- Audit note: 9.0.2 Linux x86-64 artifact and clients
- URL: https://franz.com/agraph/downloads/

### S06 — Quick start

- Type: Official documentation
- Audit note: Installation requirements and first repository
- URL: https://franz.com/agraph/support/documentation/agraph-quick-start.html

### S07 — Triple indices

- Type: Official documentation
- Audit note: Index permutations, defaults, optimization and storage rule of thumb
- URL: https://franz.com/agraph/support/documentation/triple-index.html

### S08 — Performance tuning

- Type: Official documentation
- Audit note: Memory mapping, shared memory, checkpoints, sessions and resource sizing
- URL: https://franz.com/agraph/support/documentation/performance-tuning.html

### S09 — Query engines

- Type: Official documentation
- Audit note: SBQE and MJQE behavior, limits, caching and path tradeoffs
- URL: https://franz.com/agraph/support/documentation/query-engines.html

### S10 — SPARQL reference

- Type: Official documentation
- Audit note: SPARQL surface and Franz query options
- URL: https://franz.com/agraph/support/documentation/sparql-reference.html

### S11 — Prolog tutorial

- Type: Official documentation
- Audit note: Prolog query model and integration
- URL: https://franz.com/agraph/support/documentation/prolog-tutorial.html

### S12 — HTTP protocol

- Type: Official documentation
- Audit note: Public wire protocol and transaction/session operations
- URL: https://franz.com/agraph/support/documentation/http-protocol.html

### S13 — HTTP reference

- Type: Official documentation
- Audit note: REST endpoint inventory
- URL: https://franz.com/agraph/support/documentation/http-reference.html

### S14 — Transactions section in introduction

- Type: Official documentation
- Audit note: Snapshot isolation, transaction logs, conflicts and commit behavior
- URL: https://franz.com/agraph/support/documentation/agraph-introduction.html#transactions

### S15 — FedShard tutorial

- Type: Official documentation
- Audit note: Horizontal sharding workflow and query behavior
- URL: https://franz.com/agraph/support/documentation/dynamic-cluster-tutorial.html

### S16 — FedShard setup

- Type: Official documentation
- Audit note: Partitioning, common knowledge bases, replicas and split operations
- URL: https://franz.com/agraph/support/documentation/dynamic-cluster-setup.html

### S17 — FedShard definition

- Type: Official documentation
- Audit note: Shard definition syntax and partition-key contract
- URL: https://franz.com/agraph/support/documentation/fedshard-def.html

### S18 — Multi-master replication

- Type: Official documentation
- Audit note: Active-active replication, controller, queues and consistency caveats
- URL: https://franz.com/agraph/support/documentation/multi-master.html

### S19 — Backup and restore

- Type: Official documentation
- Audit note: Online archives, S3 transport and distributed backup constraints
- URL: https://franz.com/agraph/support/documentation/backup-and-restore.html

### S20 — agtool

- Type: Official documentation
- Audit note: Administrative, archive, MMR and repository utilities
- URL: https://franz.com/agraph/support/documentation/agtool.html

### S21 — Server configuration

- Type: Official documentation
- Audit note: Repository, memory, directory, checkpoint and license settings
- URL: https://franz.com/agraph/support/documentation/daemon-config.html

### S22 — Docker

- Type: Official documentation
- Audit note: Container distribution and shared-memory requirement
- URL: https://franz.com/agraph/support/documentation/docker.html

### S23 — Virtual machine

- Type: Official documentation
- Audit note: Native Linux x86-64 boundary and virtualization warning
- URL: https://franz.com/agraph/support/documentation/virtual-machine.html

### S24 — Security overview

- Type: Official documentation
- Audit note: Authentication, authorization, TLS and operational security model
- URL: https://franz.com/agraph/support/documentation/security-overview.html

### S25 — User and role management

- Type: Official documentation
- Audit note: Repository permissions, roles and filters
- URL: https://franz.com/agraph/support/documentation/userrole.html

### S26 — Triple attributes

- Type: Official documentation
- Audit note: Attribute semantics, aggregation, immutability and non-indexed values
- URL: https://franz.com/agraph/support/documentation/triple-attributes.html

### S27 — RDFS++ reasoner

- Type: Official documentation
- Audit note: Dynamic entailment rules and query-time behavior
- URL: https://franz.com/agraph/support/documentation/reasoner-tutorial.html

### S28 — OWL2 RL materializer

- Type: Official documentation
- Audit note: Materialization workflow and operational consequences
- URL: https://franz.com/agraph/support/documentation/materializer.html

### S29 — SHACL

- Type: Official documentation
- Audit note: Shape validation interface and semantics
- URL: https://franz.com/agraph/support/documentation/shacl.html

### S30 — LLM and vector store

- Type: Official documentation
- Audit note: Embedding, vector comparison and natural-language integration
- URL: https://franz.com/agraph/support/documentation/llmembed.html

### S31 — AGWebView

- Type: Official documentation
- Audit note: Plans, logs and administrative observability
- URL: https://franz.com/agraph/support/documentation/webview.html

### S32 — Historical scale results

- Type: Vendor benchmark page
- Audit note: Load-only LUBM-like claims through 1.009 trillion triples
- URL: https://franz.com/agraph/allegrograph/index.lhtml

### S33 — AllegroGraph 9 launch

- Type: Vendor announcement
- Audit note: GraphTalker positioning; marketing evidence only
- URL: https://allegrograph.com/allegrograph-9-0-launches-with-graphtalker/

### S34 — Free edition

- Type: Official product page
- Audit note: Free-use limit and commercial-license boundary
- URL: https://franz.com/agraph/downloads/

### S35 — Python client snapshot

- Type: Pinned public source
- Audit note: MIT client source at e344c12e9664f257c2793d245702dc4afcc1ee3f; not server internals
- URL: https://github.com/franzinc/agraph-python/tree/e344c12e9664f257c2793d245702dc4afcc1ee3f

### S36 — Python REST implementation

- Type: Pinned public source
- Audit note: Commit, rollback, index, warmup, vector and MMR endpoint wrappers
- URL: https://github.com/franzinc/agraph-python/blob/e344c12e9664f257c2793d245702dc4afcc1ee3f/src/franz/miniclient/repository.py

### S37 — Python client license

- Type: Pinned public source
- Audit note: MIT license for the client
- URL: https://github.com/franzinc/agraph-python/blob/e344c12e9664f257c2793d245702dc4afcc1ee3f/LICENSE

### S38 — Java client snapshot

- Type: Pinned public source
- Audit note: Eclipse Public License 1.0 client at 6e7858f90d86410109ff66e4ec11da75c35c752c
- URL: https://github.com/franzinc/agraph-java-client/tree/6e7858f90d86410109ff66e4ec11da75c35c752c

### S39 — Java transaction settings

- Type: Pinned public source
- Audit note: Client-visible transaction and MMR commit controls
- URL: https://github.com/franzinc/agraph-java-client/tree/6e7858f90d86410109ff66e4ec11da75c35c752c/src/main/java/com/franz/agraph/repository

### S40 — Docker snapshot

- Type: Pinned public source
- Audit note: Container build and entry point at b2a50ece125cb4646594f33fd3a08074efe5f339; downloads closed binary
- URL: https://github.com/franzinc/docker-agraph/tree/b2a50ece125cb4646594f33fd3a08074efe5f339

### S41 — Dockerfile

- Type: Pinned public source
- Audit note: Build stage downloads the server distribution rather than compiling server source
- URL: https://github.com/franzinc/docker-agraph/blob/b2a50ece125cb4646594f33fd3a08074efe5f339/Dockerfile

### S42 — Container entry point

- Type: Pinned public source
- Audit note: Shared memory, ownership, generated credentials and license injection
- URL: https://github.com/franzinc/docker-agraph/blob/b2a50ece125cb4646594f33fd3a08074efe5f339/entrypoint.sh

### S43 — Franz GitHub organization

- Type: Official public source inventory
- Audit note: Clients, examples and packaging are public; server engine source was not found
- URL: https://github.com/franzinc

### S44 — LDBC SNB

- Type: Independent benchmark authority
- Audit note: Current benchmark specification and audited-result framework
- URL: https://ldbcouncil.org/benchmarks/snb/

### S45 — LDBC results

- Type: Independent benchmark authority
- Audit note: Published audited-result inventory; no current AllegroGraph result found
- URL: https://ldbcouncil.org/benchmarks/snb-bi/

### S46 — SP2Bench

- Type: Academic benchmark specification
- Audit note: SPARQL performance workload; historical relevance does not imply a 9.0.2 result
- URL: https://dbis.informatik.uni-freiburg.de/forschung/projekte/SP2B/

### S47 — BSBM publication record

- Type: Academic benchmark source
- Audit note: Original RDF e-commerce benchmark publication and DOI
- URL: https://madoc.bib.uni-mannheim.de/34767/

### S48 — RDF 1.2 concepts

- Type: W3C standard
- Audit note: RDF graph, dataset and term semantics
- URL: https://www.w3.org/TR/rdf12-concepts/

### S49 — SPARQL 1.1 query

- Type: W3C standard
- Audit note: Independent semantic oracle for query results
- URL: https://www.w3.org/TR/sparql11-query/

### S50 — S3 consistency

- Type: AWS official documentation
- Audit note: Object-store behavior for backup/control-plane design
- URL: https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel
