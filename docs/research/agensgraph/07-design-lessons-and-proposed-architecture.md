# AgensGraph design lessons and proposed PB/S3 architecture

Research cut: `2026-08-08`
Stable baseline: `v2.17.0` / `4174bdeb81e6cb6ee4d85b5835491b8509d04e52` / PostgreSQL 17.10
Unreleased comparison: `2.18-devel` / `9f9297c7008ca0451681a7d992d7e32eee307d8e`
Evidence status: source-audited; claims and issue reports are explicitly qualified
Scope: What to adopt, what to avoid, and concrete low-latency/fixed-budget/distributed/object-store design responses

## Design response

AgensGraph demonstrates that graph syntax can be lowered into a mature relational optimizer and that graph writes benefit from full database transaction machinery. The proposed engine should retain those principles: one typed logical algebra, explicit graph identity, costed access paths, snapshot isolation, explainability and differential semantic tests. It should not clone AgensGraph's physical topology if the objective is PB/trillion-edge S3 authority.

The proposed architecture separates immutable authoritative graph segments in S3 from bounded local/NVMe caches, a small strongly consistent metadata/manifest plane, stateless query workers, and partition-aware traversal. Vertices and adjacency are sorted into independently fetchable blocks by stable ownership keys. Properties use typed column groups and late materialization. Updates enter a replicated write-ahead delta tier, then compact into immutable S3 generations. Every query declares budgets for remote bytes, frontier size, CPU and result count; admission and continuation tokens make cost fixed and failure explicit.

Very low latency comes from keeping hot routing, manifests, small indexes and popular adjacency blocks in RAM/NVMe, issuing asynchronous range reads for cold blocks, grouping frontier work by partition/object, and avoiding global coordination for snapshot reads. Distribution is ownership-based, with explicit cross-partition messages and consistent-hash/virtual shard movement. The architecture cannot promise 10x universally; it can target tenfold wins in cold-cost-normalized queries, bytes per edge, scale-out ingest and S3-backed capacity while acknowledging local in-memory competitors may win tiny hot graphs.

## Adopt, adapt, and avoid

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

### F027 — Adopt one algebra

- Finding: Lower Cypher/GQL and APIs into one typed logical plan instead of maintaining independent semantics.
- Evidence class: Lesson from S26,S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F028 — Adopt explainability

- Finding: Expose partitions, remote bytes, cache status, frontier estimates and spill in every physical plan.
- Evidence class: Adaptation of PostgreSQL EXPLAIN
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F029 — Adopt MVCC

- Finding: Use immutable generations plus snapshot manifests and transactional deltas for repeatable reads.
- Evidence class: Lesson from S17
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F030 — Adopt typed indexes

- Finding: Promote hot properties to typed columns/indexes based on workload evidence, echoing 2.18-devel direction.
- Evidence class: S05
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F031 — Adopt bidirectionality selectively

- Finding: Maintain reverse adjacency only for edge types whose query workload justifies doubled bytes.
- Evidence class: Contrast with S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F032 — Adopt statistics

- Finding: Track degree sketches, property selectivity, block min/max and cache residency per generation.
- Evidence class: Lesson from S19,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F033 — Adopt regression discipline

- Finding: Turn every public semantic issue into cross-engine generative and metamorphic tests.
- Evidence class: S33-S46
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F034 — Avoid relation per label

- Finding: Use label dictionaries/partition metadata without one heap and three indexes per label.
- Evidence class: Contrast with S24,S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F035 — Avoid JSONB hot path

- Finding: Use typed column groups for hot predicates and a sparse overflow map for cold properties.
- Evidence class: Contrast with S21,S22,S27
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F036 — Avoid unconditional indexes

- Finding: Do not pay forward, reverse and ID indexes for every edge type by default.
- Evidence class: Contrast with S25
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F037 — Avoid single primary

- Finding: Partition write ownership and transaction coordination so aggregate capacity grows with shards.
- Evidence class: Contrast with S15
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F038 — Avoid process per session

- Finding: Use asynchronous multiplexed workers and bounded arenas.
- Evidence class: Contrast with S11,S18
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F039 — Avoid opaque memory

- Finding: Reserve per-query/frontier budgets and spill deterministic structures.
- Evidence class: Lesson from S18,S28,S29
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F040 — Avoid local authority

- Finding: Make S3 generation manifests the durable source of truth, not backup copies of block volumes.
- Evidence class: Contrast with S16
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F041 — Avoid full-copy replicas

- Finding: Erasure-code/replicate immutable objects and replicate only hot cache/delta state as required.
- Evidence class: Contrast with S15
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F042 — Avoid unlimited VLE

- Finding: Require depth, path/result, remote-byte and CPU budgets with resumable partial execution.
- Evidence class: Lesson from S28
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F043 — Segment layout

- Finding: Store adjacency in endpoint-sorted compressed blocks with offsets, label/type metadata and optional reverse blocks.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F044 — Property layout

- Finding: Store typed property columns separately so adjacency-only traversals do not read payloads.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F045 — Snapshot manifest

- Finding: Atomically publish immutable object generations through a compact consensus metadata plane.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F046 — Delta tier

- Finding: Replicate recent mutations synchronously in bounded logs/memtables, then compact to S3.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F047 — Read path

- Finding: Resolve snapshot and partition, check RAM/NVMe, range-read S3 block, decode only needed columns, batch next frontier.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F048 — Cache policy

- Finding: Pin manifests/routing and cost-aware hot blocks; never require all graph data in DRAM.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F049 — Partition policy

- Finding: Use many virtual shards and locality-aware placement; expose cross-shard edges explicitly.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F050 — Transaction scope

- Finding: Fast single-shard commits; explicit two-phase/consensus path for cross-shard invariants; no hidden weakening.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F051 — Fixed cost

- Finding: Cap workers, cache, object requests and background compaction; overload returns queue/retry instead of autoscaling invisibly.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F052 — PB recovery

- Finding: Recover metadata and warm caches from immutable objects without reconstructing one monolithic local volume.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F053 — 10x target

- Finding: Predeclare cells: storage bytes/edge, cold correct queries per dollar, scale-out ingest and restore readiness.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F054 — Non-target

- Finding: Do not promise 10x against an embedded in-memory engine for a tiny fully cached graph.
- Evidence class: Honest claim boundary
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F055 — Migration

- Finding: Bulk-read AgensGraph label tables under a consistent snapshot, map graphids/labels, validate counts and path hashes, then dual-read.
- Evidence class: Proposed migration
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

### F056 — Compatibility

- Finding: Offer Cypher subset with an explicit conformance manifest and reject unsupported clauses predictably.
- Evidence class: Proposed design
- Decision use: retain this statement only with its version and evidence qualifier.
- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.

## Prototype and acceptance experiments

Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.

### Q001 — zu design: immutable adjacency block

- Purpose: Prototype endpoint-sorted compressed block format
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `immutable adjacency block` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q002 — zu design: forward-only edge type

- Purpose: Measure bytes saved where reverse traversal is absent
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `forward-only edge type` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q003 — zu design: optional reverse block

- Purpose: Measure reverse latency and write amplification
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `optional reverse block` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q004 — zu design: typed property column

- Purpose: Compare against JSONB extraction and expression index
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `typed property column` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q005 — zu design: sparse overflow map

- Purpose: Preserve schema flexibility without taxing hot columns
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `sparse overflow map` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q006 — zu design: graph identity

- Purpose: Encode stable vertex/edge IDs independent of physical generation
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `graph identity` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q007 — zu design: label dictionary

- Purpose: Support many labels without per-label files/indexes
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `label dictionary` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q008 — zu design: manifest consensus

- Purpose: Publish atomic snapshots with small metadata quorum
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `manifest consensus` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q009 — zu design: delta single shard

- Purpose: Commit low-latency mutations with explicit durability
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `delta single shard` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q010 — zu design: delta cross shard

- Purpose: Measure coordination and abort semantics
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `delta cross shard` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q011 — zu design: delta compaction

- Purpose: Bound write amplification and S3 request cost
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `delta compaction` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q012 — zu design: snapshot read

- Purpose: Read a stable generation while compaction publishes next
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `snapshot read` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q013 — zu design: read your write

- Purpose: Overlay session/transaction deltas correctly
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `read your write` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q014 — zu design: RAM cache hit

- Purpose: Establish hot lower bound
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `RAM cache hit` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q015 — zu design: NVMe cache hit

- Purpose: Establish warm lower bound
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `NVMe cache hit` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q016 — zu design: S3 range miss

- Purpose: Measure cold request and bytes
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `S3 range miss` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q017 — zu design: coalesced frontier fetch

- Purpose: Group edges by object and partition
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `coalesced frontier fetch` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q018 — zu design: prefetch

- Purpose: Predict next blocks without excess remote bytes
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `prefetch` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q019 — zu design: cache admission

- Purpose: Reject scans that would evict interactive hot data
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `cache admission` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q020 — zu design: cache eviction

- Purpose: Maintain bounded memory under mixed tenants
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `cache eviction` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q021 — zu design: one-hop S3

- Purpose: Meet cold latency with one/few range requests
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `one-hop S3` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q022 — zu design: three-hop S3

- Purpose: Batch frontiers and bound sequential remote rounds
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `three-hop S3` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q023 — zu design: supernode pages

- Purpose: Page adjacency and push predicates before decode
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `supernode pages` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q024 — zu design: VLE budget

- Purpose: Stop/resume at CPU, path and remote-byte limits
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `VLE budget` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q025 — zu design: shortest-path spill

- Purpose: Use bounded external frontier structures
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `shortest-path spill` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q026 — zu design: partition-local traversal

- Purpose: Avoid network for owned neighborhoods
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `partition-local traversal` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q027 — zu design: cross-partition traversal

- Purpose: Batch remote frontier RPCs
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `cross-partition traversal` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q028 — zu design: virtual-shard rebalance

- Purpose: Move ownership without rewriting all S3 data
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `virtual-shard rebalance` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q029 — zu design: worker loss

- Purpose: Retry idempotent snapshot reads without coordinator state
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `worker loss` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q030 — zu design: metadata leader loss

- Purpose: Preserve published snapshots and bounded write pause
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `metadata leader loss` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q031 — zu design: region loss

- Purpose: Recover manifests/deltas and reuse replicated S3
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `region loss` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q032 — zu design: object corruption

- Purpose: Validate checksums and alternate replicas
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `object corruption` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q033 — zu design: S3 throttling

- Purpose: Backpressure and report budget exhaustion
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `S3 throttling` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q034 — zu design: fixed worker cap

- Purpose: Hold cost while offered load rises
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `fixed worker cap` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q035 — zu design: fixed cache cap

- Purpose: Hold memory while graph reaches PB
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `fixed cache cap` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q036 — zu design: fixed request cap

- Purpose: Enforce per-query and per-tenant object requests
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `fixed request cap` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q037 — zu design: foreground/background isolation

- Purpose: Prevent compaction from violating latency SLO
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `foreground/background isolation` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q038 — zu design: bytes per edge

- Purpose: Target tenfold reduction versus relational heap plus indexes
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `bytes per edge` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q039 — zu design: cold queries per dollar

- Purpose: Target tenfold cost-normalized win
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `cold queries per dollar` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q040 — zu design: scale-out ingest

- Purpose: Target linear shard throughput
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `scale-out ingest` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q041 — zu design: PB namespace

- Purpose: List/plan without loading PB metadata into every worker
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `PB namespace` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q042 — zu design: trillion-edge traversal

- Purpose: Run real loaded scale with correctness hashes
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `trillion-edge traversal` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q043 — zu design: backup-free recovery

- Purpose: Rebuild caches directly from authoritative objects
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `backup-free recovery` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q044 — zu design: AgensGraph export

- Purpose: Stream stable snapshot label tables and preserve identity map
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `AgensGraph export` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q045 — zu design: dual read

- Purpose: Compare result bags and paths during migration
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `dual read` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q046 — zu design: dual write

- Purpose: Validate transaction gaps before cutover
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `dual write` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q047 — zu design: Cypher conformance

- Purpose: Publish supported syntax and semantic differential suite
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `Cypher conformance` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q048 — zu design: SQL interoperability

- Purpose: Define federation boundary without one monolithic backend
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `SQL interoperability` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q049 — zu design: EXPLAIN remote cost

- Purpose: Expose object count, bytes, partitions and cache assumptions
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `EXPLAIN remote cost` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q050 — zu design: admission overload

- Purpose: Return deterministic queue/retry/partial status
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `admission overload` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q051 — zu design: tenant quota

- Purpose: Enforce CPU, frontier, storage and request budgets
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `tenant quota` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.

### Q052 — zu design: 10x claim audit

- Purpose: Release raw artifacts and confidence bounds
- Setup: Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network
- Workload: Execute `10x claim audit` at controlled concurrency against cold, warm, steady-state, and pressure states; verify after commit, checkpoint, crash, and restart
- Required metrics: latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors
- Correctness oracle: Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle
- Failure interpretation: Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell
- Evidence anchors: S04,S15-S29,S33-S39
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
