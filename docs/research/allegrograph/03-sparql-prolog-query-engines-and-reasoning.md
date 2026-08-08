# AllegroGraph SPARQL, Prolog, query-engine, and reasoning audit

Research cut: `2026-08-08`
Product baseline: `AllegroGraph 9.0.2`
Evidence status: current manual audited; public client/container source pinned; proprietary server internals unavailable
Scope: SBQE/MJQE planning, SPARQL semantics, paths, Prolog, federation, reasoning, SHACL, text and vectors

## Audit outcome

AllegroGraph's query breadth is a major strength, but the server optimizer is closed source. The auditable contract comes from standards, manuals, plans and black-box differential tests. SBQE is documented as the default and fastest choice for most queries. MJQE emphasizes merge joins, caching, lower memory and FedShard/path behavior. Engine selection must be part of every result because plans, order and resource envelopes differ.

Property paths are the central adversarial family: cyclic and high-degree graphs can create combinatorial work, and the manual acknowledges exhaustion and paging. Reasoning further changes what constitutes a result. Asserted-only, dynamic RDFS++ entailment and OWL2 RL materialization must be separate tracks with explicit maintenance and update costs.

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

### F033 — SBQE default

- Finding: SBQE remains the normal default and vendor-preferred engine for most non-distributed queries.
- Evidence anchors: S09
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F034 — MJQE selection

- Finding: A query option selects MJQE explicitly; benchmark artifacts must retain engine choice.
- Evidence anchors: S09,S10
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F035 — Result order

- Finding: Without ORDER BY, differing row order is not a semantic mismatch; LIMIT without order can expose different valid subsets.
- Evidence anchors: S09,S49
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F036 — Memory behavior

- Finding: MJQE is positioned as using less memory in important path/join cases, but that must be measured per workload.
- Evidence anchors: S09
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F037 — Federated engine

- Finding: FedShard depends on distributed query rewriting and MJQE-like combination behavior.
- Evidence anchors: S09,S15-S17
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F038 — Plan visibility

- Finding: AGWebView plan and log views help black-box diagnosis but cannot replace source-level optimizer audit.
- Evidence anchors: S31
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F039 — RDFS++

- Finding: Dynamic reasoning changes query answers without necessarily materializing every entailed statement.
- Evidence anchors: S27
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F040 — OWL2 RL

- Finding: Materialization moves reasoning cost into writes/jobs and creates lifecycle and storage obligations.
- Evidence anchors: S28
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F041 — SHACL

- Finding: Validation must report shape semantics, scope, updates and failure handling independently of query latency.
- Evidence anchors: S29
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F042 — Vector layer

- Finding: Embedding features add model, dimensionality, recall and external-service variables that must not be attributed to core graph execution.
- Evidence anchors: S30
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F043 — Prolog

- Finding: Prolog is a native differentiator but requires its own termination, tabling, recursion and result-semantic tests.
- Evidence anchors: S11
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

### F044 — Standards oracle

- Finding: W3C RDF/SPARQL specifications are the independent baseline; extensions require separately declared semantics.
- Evidence anchors: S48,S49
- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.
- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.
- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.

## Qualification matrix

Every case is an independent result cell. Preserve query semantics and failure behavior. Report p50, p95, p99, p99.9 and maximum, plus errors and timeouts; never average percentiles or silently omit failed operations.

### Q001 — 03-sparql-prolog-query-engines-and-reasoning: SPO lookup

- Purpose: Establish minimum indexed pattern latency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SPO lookup` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q002 — 03-sparql-prolog-query-engines-and-reasoning: join star

- Purpose: Measure selective hub joins
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `join star` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q003 — 03-sparql-prolog-query-engines-and-reasoning: join chain

- Purpose: Measure cardinality propagation
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `join chain` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q004 — 03-sparql-prolog-query-engines-and-reasoning: join cycle

- Purpose: Expose duplicate and planning behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `join cycle` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q005 — 03-sparql-prolog-query-engines-and-reasoning: OPTIONAL

- Purpose: Validate unbound variables and bags
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `OPTIONAL` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q006 — 03-sparql-prolog-query-engines-and-reasoning: UNION

- Purpose: Validate bag versus set behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `UNION` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q007 — 03-sparql-prolog-query-engines-and-reasoning: MINUS

- Purpose: Validate compatibility semantics
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `MINUS` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q008 — 03-sparql-prolog-query-engines-and-reasoning: FILTER NOT EXISTS

- Purpose: Validate correlation semantics
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `FILTER NOT EXISTS` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q009 — 03-sparql-prolog-query-engines-and-reasoning: GROUP BY

- Purpose: Validate errors, unbound values and aggregates
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `GROUP BY` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q010 — 03-sparql-prolog-query-engines-and-reasoning: ORDER LIMIT

- Purpose: Validate deterministic top-k
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `ORDER LIMIT` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q011 — 03-sparql-prolog-query-engines-and-reasoning: LIMIT no order

- Purpose: Record engine-dependent valid subsets
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `LIMIT no order` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q012 — 03-sparql-prolog-query-engines-and-reasoning: subquery

- Purpose: Measure materialization and scoping
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `subquery` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q013 — 03-sparql-prolog-query-engines-and-reasoning: VALUES

- Purpose: Measure bind joins and large input tables
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `VALUES` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q014 — 03-sparql-prolog-query-engines-and-reasoning: SERVICE

- Purpose: Separate remote failures and latency
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SERVICE` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q015 — 03-sparql-prolog-query-engines-and-reasoning: path fixed

- Purpose: Compare static joins with property paths
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `path fixed` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q016 — 03-sparql-prolog-query-engines-and-reasoning: path star cycle

- Purpose: Bound combinatorial expansion
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `path star cycle` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q017 — 03-sparql-prolog-query-engines-and-reasoning: path alternatives

- Purpose: Validate duplicate and reachability semantics
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `path alternatives` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q018 — 03-sparql-prolog-query-engines-and-reasoning: path paging

- Purpose: Prove completeness across pages
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `path paging` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q019 — 03-sparql-prolog-query-engines-and-reasoning: SBQE parity

- Purpose: Run semantic corpus under SBQE
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SBQE parity` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q020 — 03-sparql-prolog-query-engines-and-reasoning: MJQE parity

- Purpose: Run identical corpus under MJQE
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `MJQE parity` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q021 — 03-sparql-prolog-query-engines-and-reasoning: engine crossover

- Purpose: Find latency, memory and spill crossover
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `engine crossover` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q022 — 03-sparql-prolog-query-engines-and-reasoning: plan cache

- Purpose: Measure repeated-query warmup and invalidation
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `plan cache` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q023 — 03-sparql-prolog-query-engines-and-reasoning: RDFS++ cold

- Purpose: Measure first dynamic entailment query
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `RDFS++ cold` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q024 — 03-sparql-prolog-query-engines-and-reasoning: RDFS++ warm

- Purpose: Measure steady cache behavior
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `RDFS++ warm` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q025 — 03-sparql-prolog-query-engines-and-reasoning: OWL materialize

- Purpose: Measure time, space and atomic visibility
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `OWL materialize` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q026 — 03-sparql-prolog-query-engines-and-reasoning: OWL incremental update

- Purpose: Measure refresh and stale inference
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `OWL incremental update` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q027 — 03-sparql-prolog-query-engines-and-reasoning: SHACL valid

- Purpose: Measure validation with no violations
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SHACL valid` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q028 — 03-sparql-prolog-query-engines-and-reasoning: SHACL invalid

- Purpose: Validate complete violation reporting
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `SHACL invalid` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q029 — 03-sparql-prolog-query-engines-and-reasoning: Prolog recursion

- Purpose: Test termination and resource ceilings
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `Prolog recursion` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q030 — 03-sparql-prolog-query-engines-and-reasoning: Prolog SPARQL mix

- Purpose: Validate shared transaction/results
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `Prolog SPARQL mix` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q031 — 03-sparql-prolog-query-engines-and-reasoning: freetext graph join

- Purpose: Separate candidate generation from expansion
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `freetext graph join` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
- Required metrics: client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost
- Correctness oracle: Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model
- Failure interpretation: A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell
- Evidence anchors: S01-S50
- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.
- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.

### Q032 — 03-sparql-prolog-query-engines-and-reasoning: vector graph join

- Purpose: Report recall and graph latency separately
- Setup: Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness
- Workload: Run `vector graph join` at concurrency 1, saturation and overload in cold, warm and steady states; repeat across commit, checkpoint, crash and recovery boundaries
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
