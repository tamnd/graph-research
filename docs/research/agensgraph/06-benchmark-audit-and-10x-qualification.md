# AgensGraph benchmark audit and 10x qualification

Research cut: `2026-08-08`
Stable baseline: `v2.17.0` / `4174bdeb81e6cb6ee4d85b5835491b8509d04e52` / PostgreSQL 17.10
Unreleased comparison: `2.18-devel` / `9f9297c7008ca0451681a7d992d7e32eee307d8e`
Evidence status: source-audited; claims and issue reports are explicitly qualified
Scope: What is and is not publicly proven, and the preregistered benchmark required for defensible latency/resource/scale/competitor claims

## Evidence verdict

No current, reproducible, independently audited AgensGraph result was found that proves PB scale, a trillion edges, or a tenfold win over all popular engines. The 2.17 release's approximately 30x DELETE/DETACH DELETE statement is useful evidence of one algorithmic correction: avoid sequentially inspecting every edge label when deleting a highly connected vertex. It is not a cross-engine result, does not cover reads, and gives neither a public harness nor confidence intervals.

A universal 10x statement is scientifically implausible without a declared metric and workload class. An embedded engine can win single-process analytics; an in-memory matrix engine can win shallow pattern throughput; a distributed service can win capacity and availability; a mature transactional server can win correctness and mixed SQL. The project should claim only cells in which it wins under equal semantics and total resource accounting.

The benchmark below therefore separates hot and cold, point and scan, fixed and variable traversal, reads and writes, steady state and recovery, and scale-up versus scale-out. It includes AgensGraph stable, not development main, and pins every competitor version. A 10x ratio must hold at a declared percentile or cost-normalized metric with confidence bounds and no correctness failures.

## Benchmark findings

### F001 — Product form

- Finding: AgensGraph 2.17 is a PostgreSQL 17.10 source fork and complete server distribution, not a loadable extension for arbitrary stock PostgreSQL.
- Evidence class: S01,S04
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F002 — Stable release

- Finding: v2.17.0 is the newest stable GitHub release found at the research cut and was published on 2026-06-19.
- Evidence class: S01,S06
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F003 — Development head

- Finding: Public main identified itself as 2.18-devel at the pinned August 4 commit and differs materially from stable.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F004 — Graph representation

- Finding: A graph is represented by a PostgreSQL schema plus AgensGraph catalogs; every label is a relation inheriting from the graph's base vertex or edge relation.
- Evidence class: S21-S25,S32
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F005 — Vertex tuple

- Finding: A stable vertex tuple stores graphid and non-null JSONB properties; a vertex-label primary key indexes id.
- Evidence class: S21,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F006 — Edge tuple

- Finding: A stable edge tuple stores graphid, start graphid, end graphid, and non-null JSONB properties.
- Evidence class: S22,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F007 — Graph value row identity

- Finding: The vertex/edge composite types also carry a `tid` populated from the heap `ctid`; it is execution identity metadata, not an additional user-declared label-table column.
- Evidence class: S21,S22,S26,S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F008 — Endpoint indexes

- Finding: Every edge label receives B-tree indexes on `(start,end)` and `(end,start)`, plus a BRIN index on edge id.
- Evidence class: S20,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F009 — Identifier layout

- Finding: graphid is 64 bits with a 16-bit label component and a 48-bit local sequence component.
- Evidence class: S23
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F010 — Label ceiling

- Finding: The encoding provides at most 65,535 label identifiers and 2^48 local identifiers per label; these are encoding ceilings, not validated capacity claims.
- Evidence class: S23
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F011 — Properties

- Finding: Stable stores graph properties in JSONB and expresses property indexes using PostgreSQL expression indexes.
- Evidence class: S09,S21,S22,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F012 — Cypher lowering

- Finding: Cypher patterns and expressions are lowered into PostgreSQL query trees, scans and joins rather than sent to a separate graph service.
- Evidence class: S26,S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F013 — Dedicated nodes

- Finding: CREATE, DELETE, MERGE, SET, variable-length expansion and shortest path have graph-specific executor paths.
- Evidence class: S28-S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F014 — Hybrid strength

- Finding: SQL and Cypher can participate in one backend query, allowing relational, graph, JSONB, full-text and vector operators to compose.
- Evidence class: S03,S12
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F015 — ACID base

- Finding: Graph operations execute inside PostgreSQL transactions and inherit MVCC, WAL, crash recovery and locking machinery.
- Evidence class: S04,S17
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F016 — Distribution boundary

- Finding: The audited core has PostgreSQL primary/standby replication but no native shared-nothing graph partitioner or multi-writer distributed transaction layer.
- Evidence class: S04,S15
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F017 — Object-store boundary

- Finding: S3 may hold base backups or WAL via external tools, but stable source has no S3-backed online graph page manager.
- Evidence class: S04,S16
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F018 — Scale evidence

- Finding: No reproducible PB or trillion-edge AgensGraph result was found in the audited official sources.
- Evidence class: S01-S08,S37-S39
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F019 — Competitor evidence

- Finding: No audited same-hardware, same-semantics result establishes a universal 10x win over popular graph engines.
- Evidence class: S37-S39
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F020 — Delete claim

- Finding: 2.17 reports up to roughly 30x faster DELETE/DETACH DELETE in internal tests by avoiding sequential checks of every edge label; this is version-over-version vendor evidence.
- Evidence class: S02
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F021 — Build observation

- Finding: The exact v2.17 tag configured, compiled and installed successfully on Apple Silicon after optional ICU/readline/zlib were disabled for the local environment.
- Evidence class: Local observation, 2026-08-08
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F022 — Regression observation

- Finding: The official core regression schedule passed locally; four graph tests also passed individually after an invalid custom shared-database grouping produced contamination.
- Evidence class: Local observation,S35
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F023 — Documentation drift

- Finding: The main README release badge lagged the actual 2.17 release and the download page listed only through 2.16 at retrieval time.
- Evidence class: S01,S05,S48
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F024 — License diligence

- Finding: Repository prose says Apache-2.0 while the PostgreSQL-derived tree contains upstream PostgreSQL notices; distributions must preserve all applicable notices.
- Evidence class: S04
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F025 — Connection model

- Finding: It retains PostgreSQL's process-per-connection architecture; a pooler is normally required for large client fan-out.
- Evidence class: S11
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F026 — Maintenance

- Finding: Autovacuum, analyze, checkpoints, WAL retention, relation bloat and index maintenance remain part of graph operations.
- Evidence class: S04,S18,S19
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F027 — No official LDBC result

- Finding: No maintained AgensGraph implementation/result was found in the audited current LDBC/GDC sources.
- Evidence class: S37-S39
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F028 — Open benchmark request

- Finding: Issue 503 explicitly requests LDBC benchmark support, reinforcing the evidence gap.
- Evidence class: S39
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F029 — Delete comparison

- Finding: The 2.17 30x figure compares old and new AgensGraph behavior in internal tests.
- Evidence class: S02
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F030 — Mechanism credible

- Finding: Source architecture supports the stated mechanism: pruning incident-edge work by associated labels and endpoint ranges.
- Evidence class: S22-S25,S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F031 — Magnitude unverified

- Finding: No raw samples, hardware, dataset generator, scripts or old/new commit matrix accompanies the release note.
- Evidence class: S02
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F032 — PostgreSQL benchmark caution

- Finding: TPC-style relational performance cannot substitute for graph traversal evidence.
- Evidence class: S04
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F033 — AI demo caution

- Finding: GraphRAG adapter/demo latency mixes embeddings, retrieval and LLM work and cannot establish engine latency.
- Evidence class: S02,S03
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F034 — Correctness prerequisite

- Finding: A faster cell with wrong bags, nulls, path identity or durability loses before latency comparison.
- Evidence class: S33-S46
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F035 — Warm-cache disclosure

- Finding: shared_buffers/page cache can turn a storage test into a memory test; residency must be measured.
- Evidence class: S10,S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F036 — Resource disclosure

- Finding: Charge backend processes, OS cache, indexes, replicas, poolers and benchmark clients.
- Evidence class: S11,S15,S18,S22,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F037 — Write disclosure

- Finding: Report WAL durability, synchronous_commit, checkpoints and replica mode.
- Evidence class: S15-S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F038 — Scale disclosure

- Finding: A graphid address range is not a loaded dataset result.
- Evidence class: S23
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F039 — Data-shape disclosure

- Finding: Uniform, power-law, temporal, community and adversarial graphs exercise different operators.
- Evidence class: Benchmark design requirement
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F040 — Query disclosure

- Finding: Publish exact Cypher/SQL and plans; syntactically similar queries may not have equal semantics.
- Evidence class: S26-S29
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F041 — Parameter disclosure

- Finding: Depth, selectivity, result cap, order and timeout are part of the operation definition.
- Evidence class: Benchmark design requirement
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F042 — Tail disclosure

- Finding: p50 cannot support very-low-latency claims when p99.9 collapses under vacuum/checkpoint/skew.
- Evidence class: Benchmark design requirement
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F043 — Failure disclosure

- Finding: Failover throughput must include errors, retries, duplicates and stale reads.
- Evidence class: S15
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F044 — Cost disclosure

- Finding: Throughput per dollar requires a dated price sheet and all provisioned replicas/storage.
- Evidence class: Benchmark design requirement
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F045 — 10x aggregation

- Finding: Do not average ratios across queries; report per-cell ratios and geometric summaries only as secondary views.
- Evidence class: Benchmark methodology
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F046 — Statistical rule

- Finding: Use repeated independent trials, bootstrap confidence intervals and preregistered outlier policy.
- Evidence class: Benchmark methodology
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F047 — Load rule

- Finding: Measure load rate, write amplification, post-load analyze/index time and database-ready time separately.
- Evidence class: S18,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F048 — Steady-state rule

- Finding: A run begins only after caches, vacuum debt, replica lag and checkpoint cycle meet declared conditions.
- Evidence class: S15,S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F049 — Comparable durability

- Finding: fsync, full_page_writes, synchronous replicas and acknowledgement semantics must match intended guarantees.
- Evidence class: S15-S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F050 — Client saturation

- Finding: Use open-loop offered load for latency curves and identify coordinated omission.
- Evidence class: Benchmark methodology
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F051 — Independent replay

- Finding: Raw request/response and final-state digests must be replayable by a third party.
- Evidence class: Benchmark methodology
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

## Preregistered benchmark cells

Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.

### Q001 — benchmark: load vertices

- Purpose: Measure accepted and durable vertex ingestion
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `load vertices` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q002 — benchmark: load edges

- Purpose: Measure accepted and durable edge ingestion with indexes
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `load edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q003 — benchmark: database-ready time

- Purpose: Include index build, analyze, checkpoint and compaction-equivalent work
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `database-ready time` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q004 — benchmark: bytes per vertex

- Purpose: Measure heap/index/WAL/replica footprint
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `bytes per vertex` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q005 — benchmark: bytes per edge

- Purpose: Measure three automatic indexes and properties
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `bytes per edge` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q006 — benchmark: hot id lookup

- Purpose: Compare minimum serving latency
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `hot id lookup` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q007 — benchmark: cold id lookup

- Purpose: Compare storage miss path
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `cold id lookup` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q008 — benchmark: hot indexed property

- Purpose: Compare selective secondary lookup
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `hot indexed property` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q009 — benchmark: cold indexed property

- Purpose: Compare index and heap misses
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `cold indexed property` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q010 — benchmark: unindexed scan

- Purpose: Expose scan engines without confusing it with traversal
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `unindexed scan` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q011 — benchmark: one-hop degree 1

- Purpose: Measure constant-small adjacency
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `one-hop degree 1` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q012 — benchmark: one-hop degree 16

- Purpose: Measure common bounded fan-out
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `one-hop degree 16` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q013 — benchmark: one-hop degree 1K

- Purpose: Measure wide fan-out
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `one-hop degree 1K` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q014 — benchmark: one-hop degree 1M

- Purpose: Measure supernode behavior
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `one-hop degree 1M` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q015 — benchmark: reverse hop

- Purpose: Ensure reverse index/layout fairness
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `reverse hop` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q016 — benchmark: two-hop selective

- Purpose: Compare optimizer and adjacency locality
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `two-hop selective` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q017 — benchmark: three-hop selective

- Purpose: Measure bounded interactive traversal
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `three-hop selective` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q018 — benchmark: three-hop late filter

- Purpose: Measure intermediate explosion
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `three-hop late filter` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q019 — benchmark: VLE depth 1-3

- Purpose: Compare variable traversal machinery
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `VLE depth 1-3` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q020 — benchmark: VLE depth 1-8

- Purpose: Expose path growth and admission
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `VLE depth 1-8` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q021 — benchmark: shortest path

- Purpose: Compare exact unweighted semantics
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `shortest path` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q022 — benchmark: all shortest paths

- Purpose: Compare ties and result amplification
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `all shortest paths` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q023 — benchmark: triangle count local

- Purpose: Compare repeated neighborhood intersection
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `triangle count local` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q024 — benchmark: hybrid relational graph

- Purpose: Measure AgensGraph's genuine co-location strength
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `hybrid relational graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q025 — benchmark: vector graph

- Purpose: Compare equal vector recall plus graph semantics
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `vector graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q026 — benchmark: text graph

- Purpose: Compare equal analyzer/ranking plus traversal
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `text graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q027 — benchmark: point insert

- Purpose: Measure durable small mutation
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `point insert` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q028 — benchmark: edge insert

- Purpose: Measure endpoint and index write amplification
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `edge insert` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q029 — benchmark: property update

- Purpose: Measure JSONB/index and MVCC cost
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `property update` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q030 — benchmark: edge delete

- Purpose: Measure dead tuples and WAL
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `edge delete` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q031 — benchmark: detach degree 16

- Purpose: Reproduce ordinary delete
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `detach degree 16` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q032 — benchmark: detach degree 1M

- Purpose: Qualify the release's high-connectivity claim
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `detach degree 1M` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q033 — benchmark: MERGE contention

- Purpose: Compare atomic idempotent upsert behavior
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `MERGE contention` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q034 — benchmark: mixed 95R5W

- Purpose: Measure interactive steady state
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `mixed 95R5W` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q035 — benchmark: mixed 50R50W

- Purpose: Measure write-heavy steady state
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `mixed 50R50W` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q036 — benchmark: checkpoint window

- Purpose: Compare tail under persistence work
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `checkpoint window` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q037 — benchmark: maintenance window

- Purpose: Compare vacuum/compaction tail
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `maintenance window` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q038 — benchmark: memory 16GiB

- Purpose: Compare constrained footprint and throughput
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `memory 16GiB` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q039 — benchmark: memory 64GiB

- Purpose: Build latency-resource curve
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `memory 64GiB` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q040 — benchmark: memory 256GiB

- Purpose: Identify diminishing returns
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `memory 256GiB` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q041 — benchmark: one node

- Purpose: Compare scale-up baseline
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `one node` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q042 — benchmark: three nodes HA

- Purpose: Compare availability cost, not sharding
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `three nodes HA` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q043 — benchmark: three shards proposed

- Purpose: Compare actual horizontal partitioning in zu
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `three shards proposed` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q044 — benchmark: network partition

- Purpose: Compare availability, errors and correctness
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `network partition` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q045 — benchmark: primary failover

- Purpose: Compare RPO/RTO and tail
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `primary failover` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q046 — benchmark: restart warm

- Purpose: Measure recovery and cache preservation
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `restart warm` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q047 — benchmark: restart cold

- Purpose: Measure WAL replay and cache refill
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `restart cold` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q048 — benchmark: backup foreground

- Purpose: Measure protection overhead
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `backup foreground` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q049 — benchmark: restore

- Purpose: Compare RTO and verified graph state
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `restore` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q050 — benchmark: 100M edges

- Purpose: Validate harness and correctness
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `100M edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q051 — benchmark: 1B edges

- Purpose: Measure full resource behavior
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `1B edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q052 — benchmark: 10B edges

- Purpose: Validate scaling curve
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `10B edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q053 — benchmark: 100B edges

- Purpose: Require distributed capacity for target candidates
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `100B edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q054 — benchmark: 1T edges

- Purpose: Target qualification with no extrapolated pass
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `1T edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q055 — benchmark: 1PB logical

- Purpose: Target qualification with online query and recovery
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `1PB logical` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q056 — benchmark: cost-normalized

- Purpose: Report correct operations per dollar at SLO
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `cost-normalized` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q057 — benchmark: resource-normalized

- Purpose: Report correct operations per core/GiB/IOPS
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `resource-normalized` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q058 — benchmark: 10x latency

- Purpose: Require ratio confidence bound above ten for declared cell
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `10x latency` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q059 — benchmark: 10x cost

- Purpose: Require equal SLO/durability and full TCO
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `10x cost` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q060 — benchmark: 10x composite

- Purpose: Reject a composite that hides losing critical cells
- Setup: Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure
- Workload: Execute `10x composite` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S02,S10-S12,S15-S19,S22-S30,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

## Competitor matrix

| Engine | Class | Why it must remain a separate comparison track |
| --- | --- | --- |
| Neo4j | native transactional property graph | Cypher semantics and mature planner |
| FalkorDB | Redis/module sparse-matrix graph | shallow traversal throughput and memory |
| LadybugDB | embedded columnar graph | analytical joins and compact local execution |
| Kuzu | historical embedded predecessor | published historical baselines only |
| PuppyGraph | lakehouse graph compute | object-storage data and elastic analytics |
| Aerospike Graph | distributed KV-backed Gremlin | partitioned online capacity and service resources |
| TigerGraph | distributed native graph | scale-out traversal and commercial boundary |
| NebulaGraph | shared-nothing graph | partition routing and distributed traversal |
| JanusGraph | distributed graph over storage backends | Gremlin semantics and operational stack |
| Apache AGE | PostgreSQL extension | fork-versus-extension integration tradeoff |
| Memgraph | in-memory transactional graph | hot latency and streaming |
| Dgraph | distributed predicate graph | write distribution and query semantics |
| Amazon Neptune | managed graph service | HA/operations and cloud price |
| ArangoDB | distributed multi-model | hybrid model and shard behavior |

## Source register

Official status proves what a project states or ships, not performance. Git links are commit-pinned. Public issue reports are test leads until reproduced on the pinned stable build.

### S01 — AgensGraph v2.17.0 release

- Type: Official GitHub release
- Audit note: Released 2026-06-19; PostgreSQL 17.10 base and graph changes
- URL: https://github.com/skaiworldwide-oss/agensgraph/releases/tag/v2.17.0

### S02 — AgensGraph 2.17 release notes

- Type: Official manual
- Audit note: Detailed upstream, Cypher, index, delete, and AI integration changes
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/release_notes/agensgraph_release_notes_2_17_0.html

### S03 — AgensGraph 2.17 manual

- Type: Official manual
- Audit note: Current documentation root retrieved at the research cut
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/

### S04 — v2.17.0 source snapshot

- Type: Official source
- Audit note: Exact shipped tag commit 4174bdeb81e6cb6ee4d85b5835491b8509d04e52
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/4174bdeb81e6cb6ee4d85b5835491b8509d04e52

### S05 — 2.18-devel source snapshot

- Type: Official source
- Audit note: Public main observed at 9f9297c7008ca0451681a7d992d7e32eee307d8e; unreleased
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/9f9297c7008ca0451681a7d992d7e32eee307d8e

### S06 — Repository releases

- Type: Official GitHub metadata
- Audit note: Release chronology and immutable tag targets
- URL: https://github.com/skaiworldwide-oss/agensgraph/releases

### S07 — Repository issues

- Type: Public issue tracker
- Audit note: Reports are leads, not reproduced facts
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues

### S08 — Repository actions

- Type: Official CI metadata
- Audit note: Main workflow status and logs
- URL: https://github.com/skaiworldwide-oss/agensgraph/actions

### S09 — Graph query quick guide

- Type: Official manual
- Audit note: Graph selection, labels, elements, JSONB properties
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/quick_guide/graph_query.html

### S10 — Installation and tuning

- Type: Official manual
- Audit note: Build, Docker, shared_buffers, work_mem, random_page_cost
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/17/quick_guide/installation.html

### S11 — Architecture

- Type: Official manual
- Audit note: PostgreSQL process and memory architecture inherited by AgensGraph
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/operation_manual/architecture.html

### S12 — Hybrid SQL and Cypher

- Type: Official manual
- Audit note: Cypher in SQL and SQL subqueries in Cypher
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/developer_manual/hybrid.html

### S13 — Upgrade guide

- Type: Official manual
- Audit note: pg_upgrade route from 2.15/2.16 to 2.17 and rollback
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/upgrade_guide/index.html

### S14 — 2.16 release notes

- Type: Official manual
- Audit note: PostgreSQL 16.9 base, RLS and interoperability context
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/release_notes/agensgraph_release_notes_2_16_0.html

### S15 — PostgreSQL 17 HA

- Type: Upstream official manual
- Audit note: Streaming, synchronous, logical replication and failover primitives
- URL: https://www.postgresql.org/docs/17/high-availability.html

### S16 — PostgreSQL 17 backup

- Type: Upstream official manual
- Audit note: Base backup, WAL archive, PITR and recovery semantics
- URL: https://www.postgresql.org/docs/17/backup.html

### S17 — PostgreSQL 17 MVCC

- Type: Upstream official manual
- Audit note: Isolation, snapshots, locking and serialization behavior
- URL: https://www.postgresql.org/docs/17/mvcc.html

### S18 — PostgreSQL 17 resource consumption

- Type: Upstream official manual
- Audit note: shared_buffers, work_mem, maintenance memory and huge pages
- URL: https://www.postgresql.org/docs/17/runtime-config-resource.html

### S19 — PostgreSQL 17 planner cost

- Type: Upstream official manual
- Audit note: Planner cost constants and statistics
- URL: https://www.postgresql.org/docs/17/runtime-config-query.html

### S20 — PostgreSQL 17 BRIN

- Type: Upstream official manual
- Audit note: Block-range index behavior and correlation dependency
- URL: https://www.postgresql.org/docs/17/brin.html

### S21 — Graph vertex catalog header

- Type: Pinned stable source
- Audit note: Vertex tuple shape and graph element type
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/include/catalog/ag_vertex.h

### S22 — Graph edge catalog header

- Type: Pinned stable source
- Audit note: Edge tuple shape including start and end graphid
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/include/catalog/ag_edge.h

### S23 — Graph identifiers

- Type: Pinned stable source
- Audit note: graphid bit allocation and helper macros
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/include/utils/graph.h

### S24 — Graph DDL implementation

- Type: Pinned stable source
- Audit note: Graph/schema/label creation and catalogs
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/commands/graphcmds.c

### S25 — Graph utility transform

- Type: Pinned stable source
- Audit note: Inherited label relations and automatic indexes
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/parser/parse_utilcmd.c

### S26 — Cypher lowering

- Type: Pinned stable source
- Audit note: Pattern transformation into PostgreSQL query trees
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/parser/parse_graph.c

### S27 — Cypher expression lowering

- Type: Pinned stable source
- Audit note: Cypher expression and JSONB handling
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/parser/parse_cypher_expr.c

### S28 — Variable-length executor

- Type: Pinned stable source
- Audit note: DFS traversal state, scans, path uniqueness and memory
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/executor/execGraphVle.c

### S29 — Shortest-path executor

- Type: Pinned stable source
- Audit note: Custom path node, hash state and batching
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/executor/nodeShortestpath.c

### S30 — Graph mutation executor

- Type: Pinned stable source
- Audit note: CREATE, DELETE, SET and MERGE executor paths
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/executor

### S31 — Graph GUCs

- Type: Pinned stable source
- Audit note: enable_graph_dml and graph/planner controls
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/backend/utils/misc/guc_tables.c

### S32 — Graph catalogs

- Type: Pinned stable source
- Audit note: ag_graph and ag_label catalog definitions
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/include/catalog

### S33 — Graph regression SQL

- Type: Pinned stable source
- Audit note: Graph semantic and executor regression corpus
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/test/regress/sql

### S34 — Graph expected results

- Type: Pinned stable source
- Audit note: Expected output oracles paired with regression SQL
- URL: https://github.com/skaiworldwide-oss/agensgraph/tree/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/test/regress/expected

### S35 — Official regression schedule

- Type: Pinned stable source
- Audit note: Ordering and isolation contract for regression tests
- URL: https://github.com/skaiworldwide-oss/agensgraph/blob/4174bdeb81e6cb6ee4d85b5835491b8509d04e52/src/test/regress/parallel_schedule

### S36 — PostgreSQL announcement for 2.16

- Type: PostgreSQL community announcement
- Audit note: Independent timestamp and release synopsis
- URL: https://www.postgresql.org/about/news/announcing-the-release-of-agensgraph-v2160-3149/

### S37 — LDBC / Graph Data Council

- Type: Benchmark authority
- Audit note: SNB benchmark specifications and implementation policy
- URL: https://ldbcouncil.org/benchmarks/snb/

### S38 — LDBC implementations

- Type: Benchmark source
- Audit note: Reference implementation inventory; no maintained AgensGraph result found
- URL: https://github.com/ldbc/ldbc_snb_interactive_v1_impls

### S39 — AgensGraph issue 503

- Type: Public issue report
- Audit note: Request for an LDBC benchmark implementation
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/503

### S40 — AgensGraph issue 516

- Type: Public issue report
- Audit note: Privilege/DDL concern; qualify against current stable
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/516

### S41 — AgensGraph issue 628

- Type: Public issue report
- Audit note: Sequence use in parallel operation
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/628

### S42 — AgensGraph issue 731

- Type: Public issue report
- Audit note: Variable-length traversal semantics lead
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/731

### S43 — AgensGraph issue 777

- Type: Public issue report
- Audit note: nodes()/relationships() behavior lead
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/777

### S44 — AgensGraph issue 795

- Type: Public issue report
- Audit note: Undirected VLE asymmetry lead
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/795

### S45 — AgensGraph issue 799

- Type: Public issue report
- Audit note: Simple VLE returning no rows lead
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/799

### S46 — AgensGraph issue 803

- Type: Public issue report
- Audit note: OPTIONAL MATCH collect null semantics lead
- URL: https://github.com/skaiworldwide-oss/agensgraph/issues/803

### S47 — pgvector

- Type: Upstream extension source
- Audit note: HNSW and vector operator implementation used by 2.17 examples
- URL: https://github.com/pgvector/pgvector

### S48 — AgensGraph downloads

- Type: Official product page
- Audit note: Binary and driver availability; page lag is recorded
- URL: https://tech.skaiworldwide.com/downloads/

### S49 — Docker image listing

- Type: Official distribution channel
- Audit note: Mutable latest tag requires digest pinning
- URL: https://hub.docker.com/r/skaiworldwide/agensgraph

### S50 — Developer manual

- Type: Official manual
- Audit note: Feature summary, HA claim, indexing and security
- URL: https://tech.skaiworldwide.com/docs/en/agensgraph/latest/developer_manual/index.html
