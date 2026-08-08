# AgensGraph Cypher, SQL, planner, and execution audit

Research cut: `2026-08-08`
Stable baseline: `v2.17.0` / `4174bdeb81e6cb6ee4d85b5835491b8509d04e52` / PostgreSQL 17.10
Unreleased comparison: `2.18-devel` / `9f9297c7008ca0451681a7d992d7e32eee307d8e`
Evidence status: source-audited; claims and issue reports are explicitly qualified
Scope: Query semantics and implementation from parse/lowering through scans, joins, VLE, shortest path, writes and hybrid operators

## Execution model

AgensGraph extends PostgreSQL's grammar and analysis pipeline. Cypher clauses become PostgreSQL parse structures and planned relational operations where possible. Fixed patterns can therefore use ordinary relation scans, indexes, joins, selectivity estimates, parallelism and EXPLAIN infrastructure. Graph-specific executor nodes handle graph writes, variable-length edge walking and shortest-path state.

This design is strongest when a pattern can be rooted by a selective vertex or property index, edge labels are known, endpoint statistics are fresh, and each expansion remains bounded. It is weakest when label inheritance multiplies alternatives, JSONB predicates lack expression indexes, variable-length paths explode, supernodes generate large intermediates, or estimates choose nested work with a much larger actual frontier.

SQL/Cypher composition is not merely an adapter round trip: both surfaces share a backend transaction and plan tree. That is strategically useful for relational filters and graph expansion, but the benchmark must reveal materialization, correlated-subquery and type-conversion boundaries.

## Query findings

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

### F027 — Parser surface

- Finding: Cypher grammar and expression transformation are integrated into the PostgreSQL parser/analyzer tree.
- Evidence class: S26,S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F028 — Fixed pattern

- Finding: Fixed-length relationships lower toward scans and joins over vertex/edge label relations.
- Evidence class: S26
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F029 — Predicate pushdown

- Finding: Property and label predicates can become scan restrictions when expression shape and indexes permit.
- Evidence class: S25-S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F030 — Plan observability

- Finding: EXPLAIN/EXPLAIN ANALYZE, buffers, WAL and ordinary PostgreSQL statistics can expose graph plan cost.
- Evidence class: S04,S19
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F031 — VLE node

- Finding: Variable-length relationships have a dedicated executor maintaining traversal state rather than a pure static join expansion.
- Evidence class: S28
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F032 — VLE algorithm

- Finding: The stable executor uses depth-first traversal state and repeated relation access constrained by endpoints and depth.
- Evidence class: S28
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F033 — Path uniqueness

- Finding: Relationship/path reuse semantics require executor bookkeeping; memory scales with active paths/frontiers.
- Evidence class: S28
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F034 — Shortest path

- Finding: Shortest path uses a custom executor with hash tables and batching/spill-related state.
- Evidence class: S29
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F035 — Write nodes

- Finding: CREATE, MERGE, SET and DELETE use graph-specific executor code to preserve graph invariants.
- Evidence class: S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F036 — Eager boundaries

- Finding: Graph writes may require eager/materialized behavior so reads and writes observe intended clause semantics.
- Evidence class: S30,S33-S35
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F037 — Label selectivity

- Finding: Known relationship labels avoid searching unrelated edge relations; unknown or inherited labels can broaden the plan.
- Evidence class: S24-S26
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F038 — Endpoint selectivity

- Finding: Composite endpoint indexes support directed and reverse expansions but performance remains degree-sensitive.
- Evidence class: S22,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F039 — JSONB semantics

- Finding: Missing keys, explicit nulls, heterogeneous scalar types and casts affect both results and index eligibility.
- Evidence class: S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F040 — Order semantics

- Finding: ORDER BY and projection interactions have received post-release fixes; order must be an explicit oracle.
- Evidence class: S05,S07
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F041 — Optional semantics

- Finding: OPTIONAL MATCH plus collect/null behavior is an active issue-report area.
- Evidence class: S46
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F042 — Union visibility

- Finding: Public reports question write visibility across UNION branches; reproduce before relying on it.
- Evidence class: S07
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F043 — VLE issue density

- Finding: Several reports target directed/undirected, empty and path-function VLE semantics, making differential coverage mandatory.
- Evidence class: S42-S45
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F044 — Main VLE memory

- Finding: 2.18-devel includes explicit release of VLE-built memory and reduced array construction.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F045 — Main column binding

- Finding: 2.18-devel pushes promoted property comparisons and VLE constraints to native columns.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F046 — Main endpoint elision

- Finding: 2.18-devel can avoid reading a labeled endpoint when graphid range proves its label.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F047 — Hybrid relational filter

- Finding: Cypher can appear in SQL FROM and SQL scalar results can constrain Cypher.
- Evidence class: S12
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F048 — Vector hybrid

- Finding: Vector candidate generation and graph expansion can execute in one query but candidate count/recall must be explicit.
- Evidence class: S02,S03,S47
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F049 — Text hybrid

- Finding: GIN candidate retrieval, ranking and graph traversal can be composed with shared SQL operators.
- Evidence class: S02,S03
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F050 — Plan cache

- Finding: Prepared plans can age poorly as label size and degree distributions change; generic/custom behavior needs testing.
- Evidence class: S04,S19
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F051 — Parallelism

- Finding: PostgreSQL parallel plan support does not imply every custom graph executor node is parallel-aware.
- Evidence class: S04
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

## Query and semantic matrix

Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.

### Q001 — query: vertex id lookup

- Purpose: Establish minimum graph lookup overhead
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `vertex id lookup` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q002 — query: vertex property indexed

- Purpose: Measure expression-index predicate and heap access
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `vertex property indexed` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q003 — query: vertex property unindexed

- Purpose: Expose label scan and JSONB extraction
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `vertex property unindexed` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q004 — query: one-hop directed

- Purpose: Measure forward endpoint expansion
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `one-hop directed` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q005 — query: one-hop reverse

- Purpose: Measure reverse endpoint expansion
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `one-hop reverse` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q006 — query: one-hop undirected

- Purpose: Measure union/dedup and self-loop semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `one-hop undirected` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q007 — query: two-hop chain

- Purpose: Expose join order and intermediate cardinality
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `two-hop chain` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q008 — query: three-hop selective root

- Purpose: Measure stable bounded traversal
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `three-hop selective root` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q009 — query: three-hop late filter

- Purpose: Expose intermediate explosion
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `three-hop late filter` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q010 — query: unknown edge label

- Purpose: Measure append/search across edge labels
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `unknown edge label` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q011 — query: parent edge label

- Purpose: Measure inherited descendant scans
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `parent edge label` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q012 — query: supernode one-hop

- Purpose: Measure degree-driven latency and memory
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `supernode one-hop` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q013 — query: supernode filtered edge

- Purpose: Test predicate pushdown before materialization
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `supernode filtered edge` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q014 — query: VLE zero length

- Purpose: Validate identity path semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE zero length` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q015 — query: VLE one to three

- Purpose: Measure DFS work and uniqueness
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE one to three` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q016 — query: VLE unbounded

- Purpose: Verify limits, timeout and admission
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE unbounded` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q017 — query: VLE directed

- Purpose: Validate direction and relationship uniqueness
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE directed` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q018 — query: VLE undirected

- Purpose: Validate symmetry and duplicate handling
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE undirected` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q019 — query: VLE multiple labels

- Purpose: Measure scan-slot and constraint behavior
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE multiple labels` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q020 — query: VLE property predicate

- Purpose: Validate property binding and pushdown
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE property predicate` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q021 — query: VLE path projection

- Purpose: Charge arrays/elements only when requested
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `VLE path projection` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q022 — query: shortest path unweighted

- Purpose: Measure custom executor frontier/hash state
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `shortest path unweighted` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q023 — query: all shortest paths

- Purpose: Expose result explosion and tie semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `all shortest paths` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q024 — query: weighted path

- Purpose: Validate weight extraction, nulls and negative policy
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `weighted path` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q025 — query: cycle graph

- Purpose: Validate termination and relationship uniqueness
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `cycle graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q026 — query: self loops

- Purpose: Validate fixed and variable path multiplicity
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `self loops` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q027 — query: parallel edges

- Purpose: Validate identity and count semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `parallel edges` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q028 — query: OPTIONAL MATCH empty

- Purpose: Validate null row semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `OPTIONAL MATCH empty` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q029 — query: OPTIONAL collect

- Purpose: Reproduce issue-803 boundary
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `OPTIONAL collect` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q030 — query: UNION bag

- Purpose: Validate deduplication, type and empty branch semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `UNION bag` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q031 — query: UNION ALL write visibility

- Purpose: Validate intra-statement observation
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `UNION ALL write visibility` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q032 — query: IN empty list

- Purpose: Validate false/null and plan behavior
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `IN empty list` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q033 — query: heterogeneous IN

- Purpose: Validate JSONB type coercion and errors
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `heterogeneous IN` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q034 — query: ORDER BY hidden expression

- Purpose: Validate projection/order semantics
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `ORDER BY hidden expression` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q035 — query: aggregation path identity

- Purpose: Validate grouping by graph element identity
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `aggregation path identity` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q036 — query: Cypher in SQL

- Purpose: Measure one-plan hybrid execution
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `Cypher in SQL` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q037 — query: SQL in Cypher

- Purpose: Measure scalar-subquery correlation and cardinality errors
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `SQL in Cypher` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q038 — query: relational prefilter

- Purpose: Compare SQL-first versus Cypher-first plan shapes
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `relational prefilter` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q039 — query: vector then graph

- Purpose: Measure HNSW recall/latency plus traversal
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `vector then graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q040 — query: text then graph

- Purpose: Measure GIN candidates, ranking and traversal
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `text then graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q041 — query: hybrid RRF then graph

- Purpose: Measure dual ranking fusion and graph expansion
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `hybrid RRF then graph` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q042 — query: prepared generic plan

- Purpose: Expose skew sensitivity after repeated execution
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `prepared generic plan` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q043 — query: stale statistics plan

- Purpose: Measure misestimation and tail amplification
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `stale statistics plan` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q044 — query: cold plan cache

- Purpose: Separate parse/plan from execution
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `cold plan cache` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q045 — query: JIT off and on

- Purpose: Report compile threshold and steady benefit
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `JIT off and on` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q046 — query: parallel plan

- Purpose: Identify graph nodes that block or benefit from workers
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `parallel plan` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q047 — query: timeout cancellation

- Purpose: Verify prompt cleanup of VLE and shortest-path memory
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `timeout cancellation` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q048 — query: EXPLAIN fidelity

- Purpose: Compare estimated/actual rows and buffer/WAL counters
- Setup: Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text
- Workload: Execute `EXPLAIN fidelity` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S09,S12,S19,S22,S25-S30,S33-S35,S42-S47
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

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
