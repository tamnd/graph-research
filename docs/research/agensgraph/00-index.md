# AgensGraph 2026 dossier: index and decision verdict

Research cut: `2026-08-08`
Stable baseline: `v2.17.0` / `4174bdeb81e6cb6ee4d85b5835491b8509d04e52` / PostgreSQL 17.10
Unreleased comparison: `2.18-devel` / `9f9297c7008ca0451681a7d992d7e32eee307d8e`
Evidence status: source-audited; claims and issue reports are explicitly qualified
Scope: Navigation, headline verdict, source map, contradictions, and acceptance gates

## Outcome

AgensGraph is the strongest comparator in this corpus for a specific proposition: graph queries do not need to abandon PostgreSQL semantics or its relational ecosystem. Its stable design maps vertex labels and edge labels to inherited PostgreSQL relations, stores properties in JSONB, creates endpoint indexes for every edge label, lowers Cypher into PostgreSQL query trees, and adds custom executor nodes where ordinary scans and joins are insufficient. That gives it real ACID transactions, SQL/Cypher composition, mature backup and observability primitives, and a familiar operational envelope.

It does not meet the target architecture as shipped. One writable PostgreSQL primary remains the write and storage authority. Streaming replicas improve availability and read capacity but do not partition one graph's write path or turn cross-shard traversals into a native distributed operator. Online data and indexes require database storage; S3 is a backup/archive destination through surrounding PostgreSQL tooling, not the random-access graph store. Consequently PB capacity, trillion-edge operation, fixed S3-like marginal cost, and a universal tenfold competitor win are unproven.

The useful design lesson is selective. Reuse PostgreSQL-grade semantics, typed expression indexes, costed plans and hybrid algebra, while avoiding relation-per-label fan-out, duplicated endpoint indexes for every workload, process-per-connection overhead, single-primary capacity, and JSONB extraction on the hottest property predicates. The unreleased 2.18-devel property-promotion and endpoint-elision work independently confirms where stable 2.17 pays avoidable cost.

## Dossier map

| Specification | Purpose |
| --- | --- |
| [01-product-lineage-releases-and-evidence.md](./01-product-lineage-releases-and-evidence.md) | Ownership, releases, PostgreSQL base, documentation drift, claims and issue taxonomy |
| [02-source-storage-indexes-and-identifiers.md](./02-source-storage-indexes-and-identifiers.md) | Physical tuples, inherited labels, graphid, indexes, JSONB, access paths and amplification |
| [03-cypher-sql-planner-and-execution.md](./03-cypher-sql-planner-and-execution.md) | Parsing, lowering, plans, fixed and variable traversal, shortest path and hybrid queries |
| [04-transactions-correctness-concurrency-and-security.md](./04-transactions-correctness-concurrency-and-security.md) | MVCC, graph mutations, constraints, races, privileges, issue-derived semantic tests |
| [05-operations-distribution-resources-s3-and-cost.md](./05-operations-distribution-resources-s3-and-cost.md) | Processes, memory, vacuum, HA, backup, scale ceilings, object storage and TCO |
| [06-benchmark-audit-and-10x-qualification.md](./06-benchmark-audit-and-10x-qualification.md) | Evidence audit and reproducible latency/resource/scale/competitor benchmark |
| [07-design-lessons-and-proposed-architecture.md](./07-design-lessons-and-proposed-architecture.md) | Concrete adoption/avoidance decisions and a PB/S3-oriented architecture response |

## Evidence labels

- Observed: reproduced locally against the exact pinned tag with commands and outcome recorded.
- Source fact: directly visible in a pinned code path; it may describe unreleased behavior if attached to main.
- Official statement: product documentation or release metadata; performance magnitude remains a claim.
- Vendor claim: preserve workload and comparison scope; never promote it to a general result.
- Issue report: a test lead submitted publicly; not a confirmed current defect until reproduced.
- Inference: an architectural conclusion derived from evidence; state the premises and disproof test.
- Unknown: source or artifact is absent; do not invent a favorable implementation.

## Local source and build audit

The stable audit used a detached checkout of tag `v2.17.0` at `4174bdeb81e6cb6ee4d85b5835491b8509d04e52`. The checkout contains 7,188 tracked files. C/H/Y/L files under `src/backend` and `src/include` total 1,280,539 lines; a conservative filename-based graph/Cypher/VLE/shortest-path subset totals 23,999 lines. The stable regression tree contains 15 SQL files whose names identify graph, Cypher, or property-index coverage. These counts describe audit surface, not quality.

The local Apple Silicon configuration was `./configure --prefix=<temporary-install> --without-readline --without-zlib --without-icu`. The first default configure attempt stopped because ICU development dependencies were unavailable; disabling optional ICU allowed configuration. `make -j8` and `make install` completed. The installed server reported `postgres (PostgreSQL) 17.10`.

An initial hand-selected batch of 15 graph tests put tests from different official schedule positions into one shared regression database. Four then differed because objects/data leaked across that nonstandard ordering. Each of those four—`cypher_dml`, `cypher_func`, `cypher_shortestpath2`, and `propertyindex`—passed when run alone in a fresh regression database. The authoritative follow-up was unmodified `make check`: all 241 scheduled tests passed, including every graph group. This is compilation and regression evidence only; it contains no latency, capacity, durability-fault, or competitor benchmark.

Development comparison uses main commit `9f9297c7008ca0451681a7d992d7e32eee307d8e`, identifying as `2.18-devel`. Relative to v2.17.0, the raw tree diff spans 3,963 files with 347,796 insertions and 173,224 deletions because it mixes upstream PostgreSQL evolution with graph work. Every development finding is therefore attributed to inspected graph commits/files, never to the bulk diff magnitude.

## Decision-grade findings

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

### F027 — One label per element

- Finding: Stable documentation and DDL encode one concrete vertex or edge label per element, with label inheritance providing hierarchy rather than arbitrary multi-label membership.
- Evidence class: S09,S24,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F028 — Unlabeled behavior

- Finding: Creating an unlabeled vertex uses the base ag_vertex label; an edge label cannot be omitted.
- Evidence class: S09
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F029 — Typo hazard

- Finding: The graph query guide warns that a mistyped label may create an unintended label during writes.
- Evidence class: S09
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F030 — Index statistics

- Finding: Stable raises statistics targets for edge endpoints, trading analyze/statistics work for better skew estimates.
- Evidence class: S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F031 — BRIN caveat

- Finding: The automatic edge-id BRIN index is valuable only to the extent heap order correlates with graphid ranges.
- Evidence class: S20,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F032 — HNSW integration

- Finding: 2.17 property expression indexes can use pgvector HNSW; that proves composition, not distributed vector capacity.
- Evidence class: S02,S47
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F033 — Full-text integration

- Finding: 2.17 examples use PostgreSQL tsvector/GIN expression indexes over properties.
- Evidence class: S02,S03
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F034 — Direct graph DML

- Finding: enable_graph_dml is superuser-controlled and off by default because direct relational DML can violate graph invariants.
- Evidence class: S31
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F035 — Main property promotion

- Finding: 2.18-devel adds typed promoted property columns and native-column reads; it must not be attributed to stable 2.17.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F036 — Main endpoint elision

- Finding: 2.18-devel can elide unread labeled endpoints using graphid ranges, signaling planner work beyond stable.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F037 — Main correctness churn

- Finding: Post-2.17 commits include concurrent-write rechecks, VLE memory release, DDL gates and property-shape fixes.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F038 — Open semantic reports

- Finding: Recent issues include OPTIONAL MATCH aggregation, UNION visibility, IN/list behavior and VLE results; each becomes a regression cell.
- Evidence class: S07,S42-S46
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F039 — LDBC absence

- Finding: An open request for LDBC implementation and absence from the audited reference inventory mean no official audited LDBC result was found.
- Evidence class: S38,S39
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F040 — Tuning warning

- Finding: The vendor's half-RAM shared_buffers and extremely low random_page_cost advice is workload-specific and requires plan/I/O validation.
- Evidence class: S10,S18,S19
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F041 — Fixed cost verdict

- Finding: A continuously provisioned primary, replicas, block storage, WAL, indexes, vacuum and backup make cost capacity-bound rather than S3-only fixed.
- Evidence class: S04,S15-S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

## Acceptance gates

Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.

### Q001 — gate: stable artifact pin

- Purpose: Reject mutable Docker latest and record image digest, source commit and PostgreSQL base
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `stable artifact pin` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q002 — gate: semantic oracle

- Purpose: Pass exact bag/order/null/path identity checks for every supported Cypher shape
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `semantic oracle` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q003 — gate: single-hop hot

- Purpose: Demonstrate warm ID-rooted one-hop latency at target concurrency
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `single-hop hot` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q004 — gate: single-hop cold

- Purpose: Bound random-device misses without hiding page cache warm-up
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `single-hop cold` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q005 — gate: multi-hop skew

- Purpose: Survive power-law degrees and supernodes without percentile collapse
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `multi-hop skew` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q006 — gate: variable length

- Purpose: Bound work, memory and path explosion across depth/selectivity cells
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `variable length` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q007 — gate: write atomicity

- Purpose: Prove endpoint and edge invariants across conflict, abort, crash and replay
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `write atomicity` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q008 — gate: replica failover

- Purpose: Measure RPO/RTO and stale-read window under planned and unplanned promotion
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `replica failover` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q009 — gate: vacuum debt

- Purpose: Include churn, dead tuples, autovacuum lag, index bloat and wraparound safety
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `vacuum debt` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q010 — gate: backup restore

- Purpose: Restore a graph and independently verify catalogs, sequences, labels and paths
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `backup restore` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q011 — gate: PB projection

- Purpose: Use measured bytes/element and IOPS, not graphid theoretical capacity
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `PB projection` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q012 — gate: trillion edge

- Purpose: Show load, steady reads, updates, failure recovery and maintenance at stated scale
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `trillion edge` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q013 — gate: S3 authority

- Purpose: Require online reads after local-cache eviction with S3 as durable source
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `S3 authority` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q014 — gate: fixed budget

- Purpose: Enforce admission and report throttling rather than silently autoscaling cost
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `fixed budget` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q015 — gate: 10x claim

- Purpose: Require confidence bounds and wins across predeclared workload classes
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `10x claim` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q016 — gate: resource claim

- Purpose: Charge client, pooler, primary, replicas, page cache, WAL, backups and operators
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `resource claim` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q017 — gate: security

- Purpose: Reproduce least-privilege graph DDL/DML and row-level visibility behavior
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `security` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q018 — gate: upgrade

- Purpose: Exercise pg_upgrade plus rollback with property indexes and graph catalogs
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `upgrade` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q019 — gate: extension compatibility

- Purpose: Test every extension against this PostgreSQL fork and exact ABI
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `extension compatibility` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q020 — gate: main separation

- Purpose: Never mix unreleased 2.18-devel results into a 2.17 score
- Setup: Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure
- Workload: Execute `main separation` at controlled concurrency against cold, warm, steady-state, and pressure states
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S01-S05,S15-S19,S33-S39
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
