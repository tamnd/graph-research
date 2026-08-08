# Oxigraph: 2026 deep technical and competitive specification

Research cut: `2026-08-08`
Status: evidence-backed competitor audit; not a vendor endorsement
Family: `embedded Rust RDF store`
Evidence convention: **Observed/official**, **Vendor claim**, **Research inference**, **Unknown**, **Qualification target**.

## 1. Decision summary

Oxigraph is the closest Rust RDF implementation reference and a useful fuzz/conformance comparator.

This document answers two questions: what this engine actually proves in 2026, and what zu must build or measure to earn a defensible advantage. A missing public detail remains unknown; it is never silently filled with a favorable assumption.

### Snapshot card

- Lifecycle: active and explicitly still optimizing.
- Data model: RDF triples/quads.
- Query surface: SPARQL 1.1.
- Persistent layout: RocksDB persistent backend or in-memory store with encoded term dictionaries and tuple indices.
- Execution: Rust SPARQL parser/evaluator.
- Transactions: transactional KV-backed updates; exact isolation should be tested.
- Distribution: single-node library/server.
- Object-storage posture: not S3-native.
- License/commercial boundary: Apache-2.0 and MIT dual licensing.
- Scale evidence: single-node; no PB proof.
- Benchmark posture: conformance and resource efficiency matter more than headline throughput.

### Facts that materially affect comparison

- F01 — The project emphasizes standards compliance and safety.
- F02 — It implements SPARQL query, update, federation, and graph-store protocols.
- F03 — Persistent mode builds on RocksDB.
- F04 — Official README warns query evaluation is not fully optimized.
- F05 — Rust library embedding makes process overhead comparisons fair.

### Bottom-line fit against zu's target

- Very-low latency: compare hot point and bounded traversal paths; never extrapolate from scans or algorithms.
- Very-low resources: charge resident set, page cache, remote cache, background services, and replicas.
- Distributed: distinguish read replication, partitioned capacity, distributed transactions, and elastic stateless compute.
- Fixed cost: no engine has fixed marginal cost by declaration; admission, batching, and capacity reservations create the bound.
- S3 authority: backups, imports, lake scans, and S3-native demand paging are four different architectures.
- PB / trillion-edge scale: require a capacity derivation plus a run at the largest affordable scale; marketing adjectives do not qualify.
- Tenfold win: can be a per-cell qualification result, never a universal statement across incomparable workloads.

## 2. Product and ecosystem boundary

The audited unit is **Oxigraph** in the exact release, edition, deployment, and durability mode recorded by the harness. The family classification is **embedded Rust RDF store**. The current lifecycle statement is: active and explicitly still optimizing.

The harness must record binary/container digest, source commit when available, build flags, plugins, license/edition, language mode, storage mode, cluster topology, replication factor, durability settings, cache sizes, thread counts, NUMA policy, kernel, filesystem, cloud region, and all environment variables that affect execution.

A managed service is not placed in a same-hardware chart. It receives a service-level result with provisioned units, region, public price, and observed provider metrics. A historical engine remains useful for regression but cannot support a claim about beating all current competitors.

## 3. Architecture reconstruction

### 3.1 Logical model

Oxigraph exposes RDF triples/quads. The conformance corpus must test nulls, missing properties, labels/types, direction, self-loops, parallel edges, element equality, path equality, bag semantics, ordering, numeric overflow, string collation, temporal values, and schema evolution.

### 3.2 Language and compiler

The public query surface is SPARQL 1.1. Syntax similarity is not semantic equivalence. Every supported construct needs a result oracle and an unsupported-feature declaration.

### 3.3 Storage

The best supported storage summary is: RocksDB persistent backend or in-memory store with encoded term dictionaries and tuple indices. This statement must be refined from code, format documentation, or provider counters before using it in a performance explanation.

### 3.4 Execution

The best supported execution summary is: Rust SPARQL parser/evaluator. The benchmark profiler must confirm which runtime and operators actually executed.

### 3.5 Transactions and recovery

The public contract is: transactional KV-backed updates; exact isolation should be tested. Exact acknowledgement, isolation anomalies, recovery bounds, and failover behavior remain separate qualification items.

### 3.6 Distribution

The deployment shape is: single-node library/server. Replication is not capacity sharding; sharding is not distributed ACID; stateless readers are not stateless storage.

### 3.7 Object storage and cost

The 2026 posture is: not S3-native. The audit distinguishes authoritative live bytes, derived acceleration, backup, import/export, and spill.

## 4. Forty-control deep audit

### 4.1 `product_boundary`

Audit question: What exact executable, edition, and storage mode is the system under test?

Current assessment: Pin Oxigraph, lifecycle `active and explicitly still optimizing`, and its edition/mode.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.2 `authority`

Audit question: Which durable component is the source of truth after every acknowledged write?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.3 `identity`

Audit question: Are node and edge identities stable across compaction, export, replication, and restore?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.4 `parallel_edges`

Audit question: Can distinct parallel edges retain properties and trail identity end to end?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.5 `schema`

Audit question: Is the schema open, closed, optional, inferred, or externally mapped?

Current assessment: Start from `RDF triples/quads` and test actual constraints.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.6 `labels`

Audit question: How are multiple labels represented and indexed?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.7 `adjacency_out`

Audit question: How is outgoing adjacency located, encoded, split, cached, and updated?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.8 `adjacency_in`

Audit question: Is incoming adjacency first-class, derived, replicated, or a fan-out operation?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.9 `supernodes`

Audit question: How are million-to-billion-degree vertices represented and scheduled?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.10 `properties`

Audit question: Are properties co-located, columnar, row-oriented, document-encoded, or remote?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.11 `compression`

Audit question: Which topology, integer, string, null, and floating encodings are implemented?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.12 `checksums`

Audit question: What integrity unit is verified on point reads and range reads?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.13 `snapshot`

Audit question: What exact token pins graph data, schema, statistics, and indexes?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.14 `isolation`

Audit question: Which anomalies are forbidden at the documented isolation level?

Current assessment: Published summary: transactional KV-backed updates; exact isolation should be tested.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.15 `durability`

Audit question: What device/service acknowledgement is required before commit returns?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.16 `recovery`

Audit question: What bounds restart work after a clean stop and a crash?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.17 `writer_fencing`

Audit question: Can a stale writer acknowledge after failover or lease expiry?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.18 `partitioning`

Audit question: What key determines placement and what happens to cross-partition edges?

Current assessment: Published distribution summary: single-node library/server.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.19 `rebalancing`

Audit question: Can placement change online without changing logical identity?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.20 `replication`

Audit question: Are replicas full, sharded, synchronous, asynchronous, or shared-storage readers?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.21 `optimizer`

Audit question: Does the optimizer cost graph expansion, joins, network, cache, and remote requests?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.22 `statistics`

Audit question: Which degree, correlation, path, and property statistics are persistent?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.23 `execution`

Audit question: Is execution tuple-at-a-time, vectorized, factorized, compiled, matrix, or actor based?

Current assessment: Expected family: Rust SPARQL parser/evaluator.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.24 `recursion`

Audit question: How are BFS, shortest paths, trails, simple paths, and arbitrary reachability executed?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.25 `parallelism`

Audit question: How does the engine avoid skew and nested parallelism under mixed queries?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.26 `memory`

Audit question: Are all variable allocations charged to bounded query and system budgets?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.27 `spill`

Audit question: Which operators spill, in what format, and with what admission controls?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.28 `cancellation`

Audit question: Can cancellation stop CPU, local I/O, remote I/O, retries, and prefetch?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.29 `cache`

Audit question: What is cached, how is it keyed, admitted, pinned, and evicted?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.30 `cold_start`

Audit question: What metadata and data round trips are required with empty caches?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.31 `object_requests`

Audit question: Can a query issue one remote request per node, edge, or result row?

Current assessment: Published object-store posture: not S3-native.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.32 `cost_admission`

Audit question: Are request, byte, CPU, spill, and result limits enforced before work?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.33 `observability`

Audit question: Can operators report rows, edges, bytes, requests, stalls, memory, and spill?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.34 `language`

Audit question: Which GQL/Cypher/SQL-PGQ/Gremlin/SPARQL semantics are declared and tested?

Current assessment: Declared surface: SPARQL 1.1.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.35 `updates`

Audit question: Are DDL, insert, merge, update, detach delete, and constraints complete?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.36 `bulk_load`

Audit question: Does bulk load preserve transactional and index invariants?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.37 `backup`

Audit question: Is backup consistent, incremental, immutable, and restore-tested?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.38 `gc`

Audit question: How are old snapshots, orphan objects, tombstones, and indexes reclaimed safely?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.39 `security`

Audit question: Are authentication, authorization, encryption, audit, and tenant isolation in scope?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

### 4.40 `operations`

Audit question: What compaction, upgrade, repair, verification, and capacity procedures exist?

Current assessment: No universal public answer; obtain code evidence, trace evidence, or mark Unknown.

Evidence required: a versioned manual or source reference, a minimal conformance test, an execution/profile trace, and a failure test when durability or distribution is involved.

zu consequence: preserve the semantic invariant in the common layer, expose backend capability honestly, and add a benchmark counter that makes hidden work visible.

## 5. Benchmark contract for this engine

Every case runs correctness first, then isolated latency, then closed-loop concurrency, then open-loop overload. Report median, p95, p99, p99.9, timeout/rejection rate, throughput, CPU-seconds, peak RSS, cache bytes, disk bytes, network bytes, remote requests, write amplification, and estimated monthly cost.

Warm means all intended engine caches are populated without changing the query parameters. Hot means the exact working set is resident. Cold means process-local, engine, OS, NVMe, and remote cache state are explicitly reset or a fresh namespace is used. Those words are never inferred from repetition count.

### 5.1 `point_pk` — primary-key node lookup with one projected property

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.2 `point_edge` — stable edge-ID lookup including endpoints and one property

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.3 `degree_1` — degree-one outgoing expansion

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.4 `degree_32` — small adjacency expansion around degree 32

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.5 `degree_1k` — medium adjacency expansion around degree 1,024

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.6 `supernode` — range-limited expansion of a ten-million-degree supernode

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.7 `expand_2` — selective two-hop expansion

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.8 `expand_3` — three-hop frontier expansion with duplicate control

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.9 `expand_into` — edge-existence/expand-into between already-bound endpoints

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.10 `multi_edge` — parallel-edge identity and property projection

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.11 `shortest` — bidirectional point-to-point unweighted shortest path

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.12 `weighted` — weighted shortest path with property access

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.13 `var_walk` — bounded variable-length walk

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.14 `trail` — DIFFERENT EDGES trail enumeration

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.15 `simple` — simple-path enumeration with explicit bound

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.16 `triangle` — triangle pattern with worst-case-sensitive join

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.17 `cycle4` — four-cycle pattern

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.18 `star_join` — high-fanout star pattern with property filters

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.19 `optional` — optional match preserving null/bag semantics

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.20 `aggregate` — grouped aggregate after traversal

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.21 `topk` — ordered top-k with late property materialization

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.22 `scan` — full projected property scan

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.23 `selective_scan` — zone/index-pruned selective property scan

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.24 `mixed` — concurrent short reads, complex reads, and updates

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.25 `ingest` — sustained transactional ingest with indexes enabled

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.26 `bulk` — initial bulk load including index/CSR build

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.27 `checkpoint` — checkpoint or compaction while readers remain active

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.28 `recovery` — crash recovery at bounded dirty-log size

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.29 `cold` — same query after clearing engine and OS/cache tiers

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

### 5.30 `remote` — same query with authoritative bytes only in object storage

- Applicability to Oxigraph: required unless the feature is unsupported, in which case publish `unsupported` rather than zero or timeout.
- Correctness oracle: canonical logical IDs, complete multiplicity, typed values, explicit ordering, and snapshot epoch.
- Latency protocol: 30-second warmup, at least 30 independent measured windows, bootstrap confidence interval, coordinated-omission-safe load generation.
- Resource protocol: isolated cgroup/container, fixed CPU affinity, NUMA locality recorded, peak and integrated CPU/RSS measured.
- Storage protocol: record logical bytes, physical bytes, indexes, WAL, snapshots, replicas, temporary and cache bytes.
- Cost protocol: apply a dated price sheet to measured instance time, storage, requests, retrieval, cross-zone traffic, and egress.
- Tenfold rule: claim 10x only if the confidence interval clears 10x for the named metric while correctness and durability match.

## 6. Fairness controls

- Same logical dataset and update stream; engine-native physical layouts are allowed and disclosed.
- Same result semantics; unsupported queries remain unsupported rather than rewritten into easier questions.
- Same durable acknowledgement class for write comparisons.
- Same number of physical cores and memory limit for self-hosted single-node tests.
- Same aggregate resources and replication fault tolerance for distributed tests.
- Officially recommended tuning may be applied before the freeze and is committed with rationale.
- Query-specific hints are allowed only when equivalent hints are offered to every engine and separately charted.
- Load/build/index time and bytes are first-class results.
- Cold, warm, and hot results are separate charts.
- Managed services use public configurations and cannot borrow hidden same-machine resource claims.
- Failed runs, OOMs, correctness mismatches, and timeouts stay in the dataset.
- Every chart links raw samples and the exact reproduction command.

## 7. Likely advantages and limits

The strongest known reason to choose this engine is tied to its family `embedded Rust RDF store`, its execution path `Rust SPARQL parser/evaluator`, and its existing ecosystem. The strongest reason to reject it for zu's target is the gap between `not S3-native` and an S3-authoritative, request-budgeted, PB-scale graph service.

Capacity statement: single-node; no PB proof. This is not converted into an edge-count claim without a physical byte model including IDs, both adjacency directions, properties, indexes, MVCC, WAL, replicas, and free space.

Commercial statement: Apache-2.0 and MIT dual licensing. License cost, support cost, and unavailable enterprise capabilities remain visible in TCO and feature tables.

## 8. Concrete lessons for zu

1. Keep stable logical node and edge identity independent of row group, CSR slot, shard, and object range.
2. Store forward and reverse adjacency as immutable range-addressable tiles carrying edge IDs.
3. Feed queries adjacency batches and typed vectors; prohibit one storage call per logical element.
4. Use vectorized/factorized execution for property-heavy patterns and dedicated frontier operators for recursion.
5. Cost topology, properties, network, cache certainty, remote requests, and result materialization together.
6. Separate the local embedded profile from the object-authoritative distributed read profile.
7. Fence writers with monotonic epochs and make ambiguous commits reconcilable by transaction ID.
8. Pack small graph tiles into large immutable objects while retaining independent checksums and range offsets.
9. Keep the hot topology working set in RAM/NVMe; batch cold frontier misses into few remote rounds.
10. Admission-control remote requests and bytes so fixed-price plans have an enforceable upper bound.
11. Partition by workload-aware graph locality, and expose cross-partition semantics rather than hiding them.
12. Publish qualified wins per workload cell; never promise a universal tenfold advantage.

## 9. Evidence gaps to close before publication

- Exact current version and release date.
- Exact license text for the benchmarked artifact.
- Storage bytes per node/edge/property on all standard datasets.
- Stable-edge-ID and parallel-edge semantics.
- Isolation litmus results and commit acknowledgement point.
- Crash recovery time versus dirty WAL size.
- Supernode behavior and maximum tested degree.
- Cold-start metadata and request count.
- Distributed cross-partition query amplification.
- Peak memory under skew, cancellation, and overload.
- Background compaction/GC effect on tail latency.
- Full load/index/checkpoint/backup resource cost.
- Reproducible largest-scale result.
- Independent or audited benchmark evidence.

## 10. Primary and official sources

- [Source repository](https://github.com/oxigraph/oxigraph)
- [Project docs](https://docs.rs/oxigraph/)
- [LDBC SNB Interactive and audited disclosures](https://ldbcouncil.org/benchmarks/snb/interactive/)
- [LDBC Graphalytics](https://ldbcouncil.org/benchmarks/graphalytics/)
- [SoK: The Faults in our Graph Benchmarks](https://arxiv.org/abs/2404.00766)

## 11. Source-handling rules

- Official documentation and source are evidence for implemented or declared behavior, not independent performance.
- A vendor benchmark is labeled vendor claim until the harness reproduces it.
- A peer-reviewed paper establishes only the version, configuration, and workload it evaluated.
- Search snippets, comparison sites, and unsourced blogs are discovery aids, not final evidence.
- Unknown is a valid result and creates a concrete experiment or source-inspection task.
- All web facts are rechecked at benchmark freeze because this corpus is current only through the research date.

## 12. Reproduction record template

- engine: `Oxigraph`
- version: `TBD at benchmark freeze`
- artifact digest: `TBD`
- source commit: `TBD or managed-service N/A`
- edition/license: `TBD`
- query language/version: `TBD`
- storage and durability mode: `TBD`
- cluster and replication: `TBD`
- CPU/RAM/NVMe/network: `TBD`
- OS/kernel/filesystem: `TBD`
- dataset URI and digest: `TBD`
- loader command and duration: `TBD`
- physical bytes by category: `TBD`
- tuning file: `TBD`
- query corpus commit: `TBD`
- raw result URI/digest: `TBD`
- profiler/trace URI: `TBD`
- correctness status: `TBD`
- reviewer and rerun date: `TBD`
