# AgensGraph transactions, correctness, concurrency, and security

Research cut: `2026-08-08`
Stable baseline: `v2.17.0` / `4174bdeb81e6cb6ee4d85b5835491b8509d04e52` / PostgreSQL 17.10
Unreleased comparison: `2.18-devel` / `9f9297c7008ca0451681a7d992d7e32eee307d8e`
Evidence status: source-audited; claims and issue reports are explicitly qualified
Scope: MVCC/isolation, mutation invariants, conflicts, recovery, privileges and issue-driven semantic qualification

## Correctness contract

The stable engine inherits PostgreSQL transaction snapshots, locks, WAL and recovery, while graph-specific executor paths are responsible for cross-relation graph invariants. This is stronger than an eventually consistent graph service but creates a sharp safety boundary: direct SQL DML against label relations is disabled by default because ordinary row operations can bypass graph-aware endpoint and mutation checks.

Snapshot isolation does not by itself prove graph serializability. Concurrent MERGE, SET, detach delete and endpoint creation can interact across vertex relations, edge relations, property expression indexes, triggers and uniqueness constraints. Every claimed invariant requires a race test at each supported isolation level and after abort/crash recovery.

Security also spans two layers. PostgreSQL authentication, roles, schemas, RLS, TLS and auditing primitives are available, but graph DDL and custom executor nodes must call the correct privilege hooks and respect row-level policies. Historical fixes and open reports justify explicit least-privilege regression rather than inheritance assumptions.

## Correctness findings

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

### F027 — Autocommit

- Finding: A standalone graph statement commits or aborts through ordinary PostgreSQL transaction control.
- Evidence class: S04,S17
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F028 — Multi-statement

- Finding: SQL and Cypher changes may share an explicit transaction and snapshot.
- Evidence class: S12,S17
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F029 — Isolation levels

- Finding: Read committed, repeatable read and serializable behavior derives from PostgreSQL but graph executor access patterns determine conflicts.
- Evidence class: S17,S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F030 — Atomic edge create

- Finding: Graph-aware execution must coordinate endpoint validation and edge insertion in the same transaction.
- Evidence class: S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F031 — Detach delete

- Finding: Deleting a vertex and incident edges spans relations and can lock/write many tuples.
- Evidence class: S02,S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F032 — MERGE

- Finding: Graph MERGE has dedicated execution and has received crash/correctness fixes historically; uniqueness is schema-dependent.
- Evidence class: S30,S33-S35
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F033 — SET

- Finding: Graph SET updates JSONB/property state through a custom executor and must recheck concurrently changed rows.
- Evidence class: S05,S30
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F034 — Eager execution

- Finding: Write/read clause ordering needs eager boundaries to prevent Halloween-style reprocessing or visibility mistakes.
- Evidence class: S30,S33-S35
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F035 — Raw DML off

- Finding: enable_graph_dml defaults false and is superuser-settable, intentionally fencing unsafe relational writes.
- Evidence class: S31
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F036 — Crash durability

- Finding: Committed graph heap and index changes are WAL-protected through PostgreSQL; restore still needs graph-catalog validation.
- Evidence class: S16,S17,S24-S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F037 — Sequence gaps

- Finding: Aborts may consume sequence values; graphid continuity must never be a correctness assumption.
- Evidence class: S23
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F038 — Constraint coverage

- Finding: Unique, mandatory/check and property indexes operate through relational mechanisms adapted to graph labels.
- Evidence class: S02,S03,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F039 — Inheritance constraint

- Finding: Constraint and uniqueness scope across parent/descendant labels must be tested; inheritance semantics can surprise SQL users.
- Evidence class: S24,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F040 — RLS

- Finding: 2.16 explicitly added/fixed row-level security behavior for Cypher, so current coverage matters.
- Evidence class: S14
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F041 — Privilege report

- Finding: Issue 516 is a lead that read-only roles may alter/remove graph objects; no current conclusion without reproduction.
- Evidence class: S40
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F042 — DDL ownership

- Finding: Development main includes ownership/DDL gates, indicating this surface remains actively hardened.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F043 — Trigger interaction

- Finding: Development fixes re-examine rows modified by before-row triggers, a concurrency/correctness boundary.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F044 — Concurrent SET

- Finding: Development main adds row re-examination before graph SET writes, separating stable confidence from future fixes.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F045 — Concurrent delete

- Finding: Development main reports a concurrent delete during graph write as a conflict.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F046 — Property shape

- Finding: Development main rejects scalar replacement of a property map and strengthens promoted-column shape checks.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F047 — Optional aggregation

- Finding: Issue 803 raises `[null]` versus empty-list behavior; oracle must state the chosen language version.
- Evidence class: S46
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F048 — VLE correctness

- Finding: Recent VLE reports span missing rows, directional asymmetry, constraint binding and path functions.
- Evidence class: S42-S45
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F049 — Upgrade correctness

- Finding: pg_upgrade must preserve graph catalogs, label IDs, sequences, relation inheritance and expression indexes.
- Evidence class: S13,S24-S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F050 — Replication visibility

- Finding: Asynchronous standbys can serve stale reads; synchronous commit adds latency and still needs routing/failover policy.
- Evidence class: S15
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F051 — Logical replication unknown

- Finding: Graph safety over table-level logical replication is not established by generic PostgreSQL availability.
- Evidence class: S15,inference
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

## Transaction, race, and security matrix

Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.

### Q001 — correctness: edge endpoint existence

- Purpose: Reject or define edges whose start/end vertex is missing
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `edge endpoint existence` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q002 — correctness: cross-graph endpoint

- Purpose: Reject an edge pointing into another graph
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `cross-graph endpoint` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q003 — correctness: concurrent endpoint delete

- Purpose: Race edge creation against vertex deletion
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `concurrent endpoint delete` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q004 — correctness: detach delete atomicity

- Purpose: Ensure no committed orphan edges remain
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `detach delete atomicity` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q005 — correctness: detach delete abort

- Purpose: Restore every vertex/edge after transaction abort
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `detach delete abort` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q006 — correctness: detach delete crash

- Purpose: Recover an all-or-nothing graph state
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `detach delete crash` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q007 — correctness: concurrent detach same vertex

- Purpose: Classify conflicts and final state
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `concurrent detach same vertex` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q008 — correctness: concurrent SET same key

- Purpose: Measure lost-update and serialization behavior
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `concurrent SET same key` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q009 — correctness: concurrent SET different keys

- Purpose: Validate JSONB merge versus row conflict semantics
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `concurrent SET different keys` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q010 — correctness: MERGE same vertex

- Purpose: Validate uniqueness and duplicate creation under race
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `MERGE same vertex` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q011 — correctness: MERGE same edge

- Purpose: Validate relationship identity under race
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `MERGE same edge` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q012 — correctness: MERGE crash

- Purpose: Validate WAL recovery across matched/create branches
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `MERGE crash` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q013 — correctness: CREATE then MATCH transaction

- Purpose: Validate read-your-write semantics
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `CREATE then MATCH transaction` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q014 — correctness: DELETE then MATCH transaction

- Purpose: Validate clause and statement visibility
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `DELETE then MATCH transaction` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q015 — correctness: UNION write visibility

- Purpose: Reproduce report with explicit expected state
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `UNION write visibility` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q016 — correctness: read committed phantoms

- Purpose: Observe graph growth across statements
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `read committed phantoms` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q017 — correctness: repeatable read graph

- Purpose: Preserve snapshot across labels and edges
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `repeatable read graph` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q018 — correctness: serializable write skew

- Purpose: Force graph invariant conflict across relations
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `serializable write skew` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q019 — correctness: deadlock two paths

- Purpose: Verify detection, victim rollback and retry safety
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `deadlock two paths` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q020 — correctness: statement timeout write

- Purpose: Ensure partial graph mutation is rolled back
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `statement timeout write` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q021 — correctness: client disconnect write

- Purpose: Ensure backend abort and cleanup
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `client disconnect write` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q022 — correctness: backend kill before WAL flush

- Purpose: Classify committed and uncommitted state
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `backend kill before WAL flush` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q023 — correctness: primary crash after commit

- Purpose: Verify durable graph and index consistency
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `primary crash after commit` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q024 — correctness: async failover

- Purpose: Measure acknowledged transaction loss window
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `async failover` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q025 — correctness: sync failover

- Purpose: Measure commit latency and zero-loss assumptions
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `sync failover` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q026 — correctness: replica stale graph

- Purpose: Verify endpoint/edge snapshot consistency on standby
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `replica stale graph` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q027 — correctness: sequence gap

- Purpose: Ensure gaps do not break label/range logic
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `sequence gap` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q028 — correctness: sequence parallelism

- Purpose: Reproduce issue-628 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `sequence parallelism` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q029 — correctness: unique property race

- Purpose: Validate expression-index constraint
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `unique property race` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q030 — correctness: mandatory property

- Purpose: Validate create, set-null and remove behavior
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `mandatory property` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q031 — correctness: check constraint

- Purpose: Validate JSONB cast/error/null behavior
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `check constraint` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q032 — correctness: parent-label uniqueness

- Purpose: Define uniqueness across descendants
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `parent-label uniqueness` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q033 — correctness: direct DML default

- Purpose: Prove unsafe SQL mutation is denied
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `direct DML default` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q034 — correctness: direct DML superuser

- Purpose: Demonstrate corruption modes in disposable environment
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `direct DML superuser` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q035 — correctness: read-only role MATCH

- Purpose: Allow intended graph reads
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `read-only role MATCH` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q036 — correctness: read-only role DDL

- Purpose: Reproduce issue-516 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `read-only role DDL` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q037 — correctness: schema owner graph DDL

- Purpose: Validate ownership and grants
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `schema owner graph DDL` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q038 — correctness: RLS vertex

- Purpose: Hide forbidden vertices in Cypher
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `RLS vertex` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q039 — correctness: RLS edge

- Purpose: Prevent edge/path leakage through counts or existence
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `RLS edge` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q040 — correctness: RLS hybrid

- Purpose: Preserve policy through SQL/Cypher composition
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `RLS hybrid` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q041 — correctness: security definer

- Purpose: Validate role context in graph functions
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `security definer` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q042 — correctness: malicious property expression

- Purpose: Validate casts, errors and index expression safety
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `malicious property expression` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q043 — correctness: backup concurrent writes

- Purpose: Recover a consistent graph snapshot
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `backup concurrent writes` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q044 — correctness: PITR before graph DDL

- Purpose: Recover catalogs and data to target
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `PITR before graph DDL` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q045 — correctness: PITR during detach

- Purpose: Recover atomic state at WAL boundary
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `PITR during detach` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q046 — correctness: pg_upgrade graph

- Purpose: Validate labels, IDs, paths and indexes
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `pg_upgrade graph` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q047 — correctness: optional collect semantics

- Purpose: Reproduce issue-803 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `optional collect semantics` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q048 — correctness: VLE missing rows

- Purpose: Reproduce issue-799 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `VLE missing rows` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q049 — correctness: undirected symmetry

- Purpose: Reproduce issue-795 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `undirected symmetry` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q050 — correctness: path function identity

- Purpose: Reproduce issue-777 lead
- Setup: Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker
- Workload: Execute `path function identity` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S13-S17,S23-S25,S30-S35,S40-S46
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
