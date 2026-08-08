# AllegroGraph operations, resources, security, S3, and cost audit

Research cut: `2026-08-08`
Product baseline: `AllegroGraph 9.0.2`
Evidence status: current manual audited; public client/container source pinned; proprietary server internals unavailable
Scope: Memory, CPU, SSD, checkpoints, sessions, maintenance, backup, restore, security, observability and TCO

## Audit outcome

AllegroGraph is engineered for a large local memory-and-SSD working set. Shared memory and memory-mapped files allow useful page-cache reuse across connections, but they also make cache state, NUMA placement, kernel configuration and co-tenancy central to reproducibility. Checkpoints can block commits, index optimization consumes I/O and dedicated sessions trade routing overhead for resource consumption.

S3 appears in data movement and archive workflows. That can lower backup storage cost, but the live store still requires provisioned local capacity and restore time. Therefore “fixed cost to S3” is not an AllegroGraph property. A complete cost model must charge server licenses, peak RAM/SSD, MMR copies, FedShard headroom, backup objects/requests, network, operators and recovery drills.

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

### F033 — Shared cache benefit

- Finding: Connections to the same repository reuse mapped/index pages, while different repositories multiply working-set demands.
- Evidence anchors: S08
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F034 — CPU guidance

- Finding: A rough operational rule is one useful active connection per core, followed by measured saturation rather than unlimited sessions.
- Evidence anchors: S08
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F035 — Dedicated sessions

- Finding: Dedicated backend ports reduce frontend contention but increase per-session resource commitment.
- Evidence anchors: S08,S12
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F036 — Huge pages

- Finding: Transparent Huge Pages should be disabled according to tuning guidance; kernel state belongs in benchmark manifests.
- Evidence anchors: S08
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F037 — Expected size

- Finding: Predeclaring expected store size can avoid resize events during ingestion.
- Evidence anchors: S08,S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F038 — Directory isolation

- Finding: Main data, transaction logs and string table can be placed separately to control contention and failure domains.
- Evidence anchors: S08,S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F039 — String compression

- Finding: Compression trades reduced storage for slower access and must be tested on actual lexical distributions.
- Evidence anchors: S08,S21
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F040 — Archive role

- Finding: agtool archive can target S3, but restore reconstructs local serving state and must meet explicit RTO/RPO.
- Evidence anchors: S19,S20
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F041 — S3 credentials

- Finding: Command-line or environment credential handling must be integrated with short-lived identity and redaction.
- Evidence anchors: S19,S20,S24
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F042 — Authorization

- Finding: Repository permissions, roles and filters provide controls whose overhead and bypass resistance need validation.
- Evidence anchors: S24,S25
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F043 — Container shm

- Finding: Official containers require roughly 1 GiB /dev/shm even before workload-specific sizing.
- Evidence anchors: S22,S40-S42
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F044 — Cost truth

- Finding: A fixed monthly envelope is an admission-control and architecture result, not a claim inferred from cheap S3 capacity pricing.
- Evidence anchors: S05,S07,S18-S21,S50
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

## Qualification matrix

Every case is an independent result cell. Preserve query semantics and failure behavior. Report p50, p95, p99, p99.9 and maximum, plus errors and timeouts; never average percentiles or silently omit failed operations.

### Q001 — 05-operations-resources-security-s3-and-cost: minimum memory

- Purpose: Find functional and latency floor
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `minimum memory` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q002 — 05-operations-resources-security-s3-and-cost: working-set memory

- Purpose: Map hit rate and p99 by RAM ratio
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `working-set memory` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q003 — 05-operations-resources-security-s3-and-cost: cold page cache

- Purpose: Measure restart and eviction latency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `cold page cache` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q004 — 05-operations-resources-security-s3-and-cost: warm page cache

- Purpose: Measure steady best case
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `warm page cache` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q005 — 05-operations-resources-security-s3-and-cost: CPU scaling

- Purpose: Find useful core and connection crossover
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `CPU scaling` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q006 — 05-operations-resources-security-s3-and-cost: dedicated sessions

- Purpose: Quantify latency and resource tradeoff
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `dedicated sessions` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q007 — 05-operations-resources-security-s3-and-cost: frontend saturation

- Purpose: Measure queueing and admission behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `frontend saturation` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q008 — 05-operations-resources-security-s3-and-cost: checkpoint default

- Purpose: Measure five-minute periodic tail
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `checkpoint default` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q009 — 05-operations-resources-security-s3-and-cost: checkpoint large

- Purpose: Measure commit blocking and recovery tradeoff
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `checkpoint large` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q010 — 05-operations-resources-security-s3-and-cost: separate tx log

- Purpose: Measure contention reduction
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `separate tx log` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q011 — 05-operations-resources-security-s3-and-cost: separate strings

- Purpose: Measure dictionary I/O isolation
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `separate strings` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q012 — 05-operations-resources-security-s3-and-cost: index optimization

- Purpose: Measure foreground interference
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `index optimization` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q013 — 05-operations-resources-security-s3-and-cost: string compression

- Purpose: Measure bytes and query CPU
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `string compression` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q014 — 05-operations-resources-security-s3-and-cost: THP enabled

- Purpose: Record unsupported kernel-state impact
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `THP enabled` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q015 — 05-operations-resources-security-s3-and-cost: THP disabled

- Purpose: Establish supported baseline
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `THP disabled` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q016 — 05-operations-resources-security-s3-and-cost: Docker shm floor

- Purpose: Validate startup and workload sizing
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `Docker shm floor` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q017 — 05-operations-resources-security-s3-and-cost: native versus Docker

- Purpose: Measure packaging overhead
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `native versus Docker` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q018 — 05-operations-resources-security-s3-and-cost: backup local

- Purpose: Measure archive throughput and pause behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `backup local` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q019 — 05-operations-resources-security-s3-and-cost: backup S3

- Purpose: Measure upload, requests, cost and integrity
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `backup S3` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q020 — 05-operations-resources-security-s3-and-cost: restore S3

- Purpose: Measure RTO, egress and local capacity
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `restore S3` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q021 — 05-operations-resources-security-s3-and-cost: distributed backup

- Purpose: Measure coordination and failure behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `distributed backup` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q022 — 05-operations-resources-security-s3-and-cost: incremental lifecycle

- Purpose: Measure retained objects and cleanup
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `incremental lifecycle` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q023 — 05-operations-resources-security-s3-and-cost: credential rotation

- Purpose: Use temporary identity without interruption
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `credential rotation` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q024 — 05-operations-resources-security-s3-and-cost: TLS overhead

- Purpose: Measure handshake, reuse and CPU
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `TLS overhead` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q025 — 05-operations-resources-security-s3-and-cost: role matrix

- Purpose: Validate least privilege across every endpoint
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `role matrix` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q026 — 05-operations-resources-security-s3-and-cost: statement filters

- Purpose: Validate enforcement and latency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `statement filters` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q027 — 05-operations-resources-security-s3-and-cost: audit logs

- Purpose: Verify completeness, redaction and storage cost
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `audit logs` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q028 — 05-operations-resources-security-s3-and-cost: secret in logs

- Purpose: Prevent generated or supplied credential leakage
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `secret in logs` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q029 — 05-operations-resources-security-s3-and-cost: one-billion TCO

- Purpose: Charge license, compute, SSD, backup and labor
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `one-billion TCO` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q030 — 05-operations-resources-security-s3-and-cost: one-trillion TCO

- Purpose: Charge shards, replicas, headroom and recovery
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `one-trillion TCO` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q031 — 05-operations-resources-security-s3-and-cost: idle cost

- Purpose: Measure minimum always-on cluster
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `idle cost` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q032 — 05-operations-resources-security-s3-and-cost: peak cost

- Purpose: Measure bounded overload without surprise scaling
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `peak cost` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q033 — 05-operations-resources-security-s3-and-cost: operator drill

- Purpose: Time restore, split, failover and reindex procedures
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `operator drill` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q034 — 05-operations-resources-security-s3-and-cost: support incident

- Purpose: Measure evidence bundle and escalation path
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `support incident` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
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
