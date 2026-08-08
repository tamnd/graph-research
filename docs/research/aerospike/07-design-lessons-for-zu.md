# Aerospike-derived design lessons and solution plan for zu

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: Actionable architecture, implementation, and qualification decisions for an S3-authoritative graph engine
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Recommended stance

Copy Aerospike's disciplines, not its storage authority. The useful disciplines are compact schema interning, adjacency-aware point paths, batching by storage destination, server-side predicate pushdown, independent stateless query compute, explicit supernode treatment, scan admission, detailed source-visible operations, and separate bulk/OLAP paths. The non-fit is authoritative mutable record storage on a provisioned database cluster with primary/secondary index RAM and data-volume licensing.

zu should make S3 the durable immutable authority and treat local NVMe/RAM as bounded, reconstructible acceleration. That changes the write contract: acknowledged mutations must enter an inexpensive durable log/manifest path, then compact into immutable graph segments. Low latency comes from deterministic ID routing, sparse indexes, compressed adjacency blocks, cache admission, request coalescing, and vectorized traversal—not from pretending an S3 GET is sub-millisecond.

## Proposed architecture

- Immutable S3 graph segments partitioned by stable vertex-ID hash and optionally label/time locality.
- A small strongly consistent manifest/catalog that maps snapshot epoch and partitions to immutable objects.
- Durable mutation log or micro-batch delta objects with idempotent sequence numbers and explicit visibility epochs.
- Compact per-partition vertex table, out-adjacency blocks, optional in-adjacency blocks, property columns, and sparse indexes.
- Schema/label/property interning with immutable dictionaries versioned by epoch; avoid a single hot allocation counter.
- Stateless native query workers that resolve IDs, build batched object ranges, vectorize decode/filter, and stream results with bounded memory.
- A content-addressed local NVMe cache and smaller RAM index/cache with hard byte budgets, admission policy, tenant quotas, and no correctness role.
- Supernode-specific sharded adjacency chunks with property min/max/bloom metadata and per-label subranges.
- Explicit scan service/admission class separate from low-latency OLTP queues.
- Compaction and index builders as interruptible fixed-budget background jobs; publish read/write amplification and debt.
- Snapshot isolation by manifest epoch for reads; optional transactional mutation service scoped to declared keys/partitions.
- End-to-end counters: objects/ranges/bytes, cache, decode, frontier, spills, retries, S3 requests, cost estimate, and result cardinality per query.

## Direct design comparison

| Aerospike technique | Lesson | zu adaptation |
| --- | --- | --- |
| Vertex record with embedded adjacency | ID-rooted locality dominates hop cost | Immutable vertex header points to compact adjacency blocks/ranges |
| 10-edge packed record | Amortize per-record metadata and RPCs | Pack thousands of sorted adjacency entries per compressed block, sized for range reads |
| Schema interning | Repeated strings are permanent tax | Epoch-versioned dictionaries with local IDs and merge/remap tooling |
| Supernode index path | One layout fails across degree distribution | Chunk and shard supernode adjacency from creation; use block metadata pushdown |
| TinkerPop strategies | Recognize high-value traversal patterns | Typed IR and rule/cost optimizer with observable physical operators |
| Batch per DB node | Group I/O by destination | Coalesce range/object reads by object and byte interval |
| Filter expressions | Push rejection to data access | Evaluate predicates during vectorized decode before materialization |
| Transactional/global cache | Cache policy affects semantics/resources | Cache never affects freshness; epoch keys make invalidation structural |
| Scan disable | Protect OLTP from accidental O(N) | Cost guard, explicit scan capability, budget and queue class |
| Stateless AGS | Compute elasticity should avoid shard ownership | Workers obtain snapshot/partition maps from manifest and hold no authority |
| Spark loader | Bulk creation needs a separate high-throughput path | Distributed segment builder writes final S3 layout directly |
| MRT | Graph mutations span records | Make transaction scope/cost explicit; avoid claiming arbitrary distributed ACID |

## PB and trillion-edge capacity model

Capacity must be algebraic before it is empirical. For each edge, model encoded neighbor ID delta, label/type, property references/values, block index share, object overhead share, replication/version retention, and compression. For each vertex, model ID/key, label, property columns, out/in block pointers, sparse-index entries, and dictionary share. Add snapshot retention, uncompacted deltas, compaction overlap, checksums, manifests, and safety margin.

A trillion edges at 12 logical encoded bytes per direction is already 24 TB before properties, vertices, indexes, object overhead, deltas, history, and replicas; at 50 bytes it is 50 TB for one direction. A PB target is therefore plausible only with transparent definitions of logical versus physical bytes. “Thousands of billions” means multiple trillions, not the 37.2B public Aerospike benchmark. Every capacity claim must state degree distribution, both-direction storage, property mix, compression, and retained epochs.

## zu implementation and experiment backlog

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — zu: stable vertex routing

- Purpose: Choose a hash/partition scheme that survives compute scaling.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `stable vertex routing`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — zu: partition map epoch

- Purpose: Route every query against an immutable snapshot.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `partition map epoch`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — zu: manifest atomic publish

- Purpose: Make new snapshots all-or-nothing.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `manifest atomic publish`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — zu: manifest service failure

- Purpose: Define read availability with cached signed manifests.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `manifest service failure`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — zu: schema dictionary allocation

- Purpose: Avoid central hot counter while preserving stable decode.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `schema dictionary allocation`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — zu: dictionary merge

- Purpose: Reconcile distributed builders deterministically.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `dictionary merge`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — zu: vertex block layout

- Purpose: Minimize point-read ranges and decode.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `vertex block layout`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — zu: out adjacency block

- Purpose: Optimize dominant directed hop.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `out adjacency block`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — zu: in adjacency optionality

- Purpose: Trade storage for reverse traversal SLO.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `in adjacency optionality`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — zu: edge identity

- Purpose: Preserve parallel edges, deletes, and path identity.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `edge identity`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — zu: edge property columns

- Purpose: Avoid reading unused values.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `edge property columns`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — zu: vertex property columns

- Purpose: Support projection and predicate pushdown.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `vertex property columns`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — zu: normal degree packing

- Purpose: Tune block target by bytes, not edge count alone.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `normal degree packing`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — zu: supernode preclassification

- Purpose: Avoid costly one-way layout migration at threshold.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `supernode preclassification`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — zu: supernode chunk key

- Purpose: Distribute hot reads/writes across chunks.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `supernode chunk key`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — zu: supernode label clustering

- Purpose: Skip irrelevant edge labels.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `supernode label clustering`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — zu: supernode property metadata

- Purpose: Use min/max/bloom/dictionary indexes to skip blocks.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `supernode property metadata`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — zu: S3 range coalescing

- Purpose: Combine adjacent reads per object.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `S3 range coalescing`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — zu: S3 request hedging

- Purpose: Bound tails without uncontrolled request cost.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `S3 request hedging`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — zu: S3 retry budget

- Purpose: Prevent retry storms and duplicate billed requests.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `S3 retry budget`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — zu: S3 multipart builder

- Purpose: Write large immutable objects efficiently.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `S3 multipart builder`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — zu: small-object avoidance

- Purpose: Control request cost and listing/metadata burden.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `small-object avoidance`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — zu: NVMe content cache

- Purpose: Make cached blocks reusable across epochs when content-identical.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `NVMe content cache`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — zu: RAM metadata cache

- Purpose: Bound routing/index state by bytes.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `RAM metadata cache`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — zu: cache admission

- Purpose: Protect hot small blocks from scans.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `cache admission`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — zu: tenant cache quota

- Purpose: Prevent noisy tenant eviction.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `tenant cache quota`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — zu: cold point lookup

- Purpose: Meet an honest object-store cold SLO.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `cold point lookup`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — zu: warm point lookup

- Purpose: Target Aerospike-class latency from bounded cache.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `warm point lookup`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — zu: frontier batching

- Purpose: Group next-hop IDs before I/O.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `frontier batching`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — zu: vectorized decode

- Purpose: Reduce CPU and allocations per edge.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `vectorized decode`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — zu: predicate pushdown

- Purpose: Reject edges before object creation.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `predicate pushdown`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — zu: projection pushdown

- Purpose: Read/decode only needed property streams.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `projection pushdown`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — zu: limit pushdown

- Purpose: Stop block reads after sufficient results while preserving order.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `limit pushdown`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — zu: sample semantics

- Purpose: Avoid biased block-level samples.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `sample semantics`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — zu: local count

- Purpose: Answer from block metadata when semantically exact.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `local count`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — zu: path memory

- Purpose: Bound path retention or spill explicitly.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `path memory`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — zu: cycle detection

- Purpose: Use compact visited structures with exact/approx modes.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `cycle detection`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — zu: typed physical IR

- Purpose: Make operator choices and semantics inspectable.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `typed physical IR`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — zu: rule optimizer

- Purpose: Capture reliable ID/batch/pushdown rewrites.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `rule optimizer`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — zu: cost optimizer

- Purpose: Choose scan/index/block paths from current stats.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `cost optimizer`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — zu: stats freshness

- Purpose: Keep stale estimates from causing unbounded work.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `stats freshness`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — zu: plan fingerprint

- Purpose: Attach physical plan identity to every benchmark sample.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `plan fingerprint`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — zu: scan admission

- Purpose: Require explicit budget for O(N) operations.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `scan admission`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — zu: heavy query queue

- Purpose: Isolate scans/supernodes from short OLTP.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `heavy query queue`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — zu: memory admission

- Purpose: Reject before operator allocations exceed budget.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `memory admission`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — zu: result backpressure

- Purpose: Stream with bounded buffers.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `result backpressure`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — zu: request cancellation

- Purpose: Stop S3 reads/decode after timeout/disconnect.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `request cancellation`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — zu: mutation idempotency

- Purpose: Use client operation IDs and sequence numbers.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `mutation idempotency`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — zu: delta visibility

- Purpose: Define when new vertices/edges enter snapshots.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `delta visibility`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — zu: read-your-writes

- Purpose: Offer session overlay or explicit wait-for-epoch.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `read-your-writes`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — zu: snapshot isolation

- Purpose: Keep multi-hop traversal on one manifest epoch.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `snapshot isolation`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — zu: delete tombstone

- Purpose: Prevent resurrection across compaction/late writes.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `delete tombstone`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — zu: transaction key set

- Purpose: Declare bounded atomic scope and failure behavior.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `transaction key set`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — zu: compaction budget

- Purpose: Cap CPU/network/S3 cost and publish debt.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `compaction budget`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — zu: compaction overlap

- Purpose: Charge temporary bytes and request cost.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `compaction overlap`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — zu: incremental index build

- Purpose: Publish index atomically with compatible epoch.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `incremental index build`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — zu: bulk import

- Purpose: Build final layout without replaying online mutations.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `bulk import`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — zu: bulk validation

- Purpose: Detect orphan edges, duplicate IDs, and type errors.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `bulk validation`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — zu: backup semantics

- Purpose: S3 authority makes snapshots native but catalog recovery still matters.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `backup semantics`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — zu: cross-region copy

- Purpose: Define RPO/RTO and manifest ordering.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `cross-region copy`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q061 — zu: object corruption

- Purpose: Use checksums, redundancy, and repair.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `object corruption`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q062 — zu: S3 outage

- Purpose: Define cached-read and write-log behavior.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `S3 outage`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q063 — zu: worker loss

- Purpose: Retry stateless query fragments safely.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `worker loss`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q064 — zu: manifest split brain

- Purpose: Fence publishers and verify monotonic epochs.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `manifest split brain`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q065 — zu: fixed monthly request budget

- Purpose: Admission-control requests/bytes to a declared envelope.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `fixed monthly request budget`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q066 — zu: per-query cost estimate

- Purpose: Expose S3 requests, bytes, CPU, cache, and egress.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `per-query cost estimate`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q067 — zu: per-tenant budget

- Purpose: Enforce predictable cost and fairness.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `per-tenant budget`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q068 — zu: PB capacity derivation

- Purpose: Publish uncertainty bands and retained-history factor.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `PB capacity derivation`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q069 — zu: trillion-edge generator

- Purpose: Create realistic skew without materializing verbose input.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `trillion-edge generator`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q070 — zu: scale ladder

- Purpose: Run 1B, 10B, 100B, 1T and validate model error.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `scale ladder`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q071 — zu: Aerospike normal-degree comparison

- Purpose: Target equal bounded traversal semantics.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `Aerospike normal-degree comparison`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q072 — zu: Aerospike supernode comparison

- Purpose: Target filtered/unfiltered discontinuity.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `Aerospike supernode comparison`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q073 — zu: Aerospike resource comparison

- Purpose: Charge AGS, DB, RF, headroom, indexes, and license.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `Aerospike resource comparison`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q074 — zu: Aerospike failure comparison

- Purpose: Match consistency and degraded-state requirements.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `Aerospike failure comparison`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q075 — zu: 10x p99 gate

- Purpose: Require confidence-bound ratio and correctness.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `10x p99 gate`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q076 — zu: 10x resource gate

- Purpose: Require full-system bytes/CPU, not process cherry-picking.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `10x resource gate`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q077 — zu: 10x cost gate

- Purpose: Require same term/region/SLO and all services.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `10x cost gate`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q078 — zu: regression corpus

- Purpose: Retain every winning cell as continuous performance test.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `regression corpus`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q079 — zu: public reproducibility

- Purpose: Publish data generator, harness, raw samples, configs, and analysis.
- Setup: Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.
- Workload: Execute the smallest semantically complete operation for `public reproducibility`, then repeat under controlled concurrency and skew.
- Required counters: object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: Aerospike evidence S09–S45 plus zu-owned implementation artifacts
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Release gates

- G0: semantic conformance for IDs, parallel edges, properties, direction, paths, bags, order, null/missing, and mutations.
- G1: deterministic physical format, checksums, upgrade reader, and snapshot manifest recovery.
- G2: bounded-memory point and traversal operators under slow consumers and cancellation.
- G3: cold/warm latency results with object-request and byte counters; no hidden unbounded cache.
- G4: fault results for S3, worker, manifest, network, and compaction failures.
- G5: capacity-model prediction within declared error at each scale-ladder step.
- G6: full cost sheet at target SLO, including requests, compute, cache, storage, egress, operations, and redundancy.
- G7: Aerospike 3.2.3 comparison with equal semantics and current Database release.
- G8: per-cell 10x claims only where the confidence and correctness rules pass.
- G9: public artifact bundle sufficient for an independent rerun.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S01 — AGS release index

- Type: Official documentation
- Audit note: 2026-06-30 latest listed release
- URL: https://aerospike.com/docs/graph/release

### S02 — AGS 3.2.3 release notes

- Type: Official documentation
- Audit note: Security-only patch; 14 CVEs listed
- URL: https://aerospike.com/docs/graph/release/3-2-3/

### S03 — AGS 3.2.2 release notes

- Type: Official documentation
- Audit note: Removed graph-service feature check
- URL: https://aerospike.com/docs/graph/release/3-2-2/

### S04 — AGS 3.2.1 release notes

- Type: Official documentation
- Audit note: Container memory and rack awareness
- URL: https://aerospike.com/docs/graph/release/3-2-1/

### S05 — AGS 3.2.0 release notes

- Type: Official documentation
- Audit note: Global cache, set cardinality, performance changes
- URL: https://aerospike.com/docs/graph/release/3-2-0/

### S06 — AGS 3.1.1 release notes

- Type: Official documentation
- Audit note: CVE-2025-12383 fix
- URL: https://aerospike.com/docs/graph/release/3-1-1/

### S07 — AGS 3.1.0 release notes

- Type: Official documentation
- Audit note: TinkerPop transactions and typed indexes
- URL: https://aerospike.com/docs/graph/release/3-1-0/

### S08 — AGS 3.0.0 release notes

- Type: Official documentation
- Audit note: Packed model revision and reload boundary
- URL: https://aerospike.com/docs/graph/release/3-0-0/

### S09 — Architecture

- Type: Official documentation
- Audit note: Three-layer request path
- URL: https://aerospike.com/docs/graph/overview/architecture/

### S10 — Transaction contract

- Type: Official documentation
- Audit note: Read, mutation, SC, AP, and MRT distinctions
- URL: https://aerospike.com/docs/graph/develop/query/transactions/

### S11 — Indexing

- Type: Official documentation
- Audit note: Vertex index and scan controls
- URL: https://aerospike.com/docs/graph/develop/query/indexing/

### S12 — Supernodes

- Type: Official documentation
- Audit note: Thresholds and filtered traversal guidance
- URL: https://aerospike.com/docs/graph/develop/query/supernodes/

### S13 — Query threading

- Type: Official documentation
- Audit note: Per-query parallelization and batch/page controls
- URL: https://aerospike.com/docs/graph/develop/query/query-threading/

### S14 — Cache management

- Type: Official documentation
- Audit note: Transactional and global record caches
- URL: https://aerospike.com/docs/graph/manage/cache/

### S15 — Data types

- Type: Official documentation
- Audit note: Property and index type limitations
- URL: https://aerospike.com/docs/graph/develop/query/data-type-support/

### S16 — TinkerPop feature support

- Type: Official documentation
- Audit note: Feature compatibility matrix
- URL: https://aerospike.com/docs/graph/overview/tinkerpop/

### S17 — Configuration reference

- Type: Official documentation
- Audit note: AGS runtime knobs
- URL: https://aerospike.com/docs/graph/reference/config/

### S18 — Metrics reference

- Type: Official documentation
- Audit note: Prometheus metric inventory
- URL: https://aerospike.com/docs/graph/reference/metrics/

### S19 — Query tracing

- Type: Official documentation
- Audit note: Zipkin tracing contract
- URL: https://aerospike.com/docs/graph/observe/query-tracing/

### S20 — Bulk load overview

- Type: Official documentation
- Audit note: Standalone and Spark paths
- URL: https://aerospike.com/docs/graph/load/overview/

### S21 — Distributed bulk load

- Type: Official documentation
- Audit note: EMR and Dataproc workflow
- URL: https://aerospike.com/docs/graph/load/distributed/

### S22 — Graph backup and restore

- Type: Official documentation
- Audit note: Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page
- URL: https://aerospike.com/docs/graph/manage/backup/

### S23 — Security

- Type: Official documentation
- Audit note: TLS, JWT RBAC, database RBAC, audit
- URL: https://aerospike.com/docs/graph/manage/security/

### S24 — Multi-tenancy

- Type: Official documentation
- Audit note: Graph scoping in a shared namespace
- URL: https://aerospike.com/docs/graph/manage/multi-tenant/

### S25 — Identity graph benchmark PDF

- Type: Vendor benchmark
- Audit note: AGS 2.4.2 / Database 7.1.0.9 test
- URL: https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf

### S26 — Graph 3.0 launch blog

- Type: Vendor blog
- Audit note: Ingest and footprint claims
- URL: https://aerospike.com/blog/aerospike-graph-3-release/

### S27 — Architecture deep-dive blog

- Type: Vendor blog
- Audit note: Optimizer and record-model explanation
- URL: https://aerospike.com/blog/graphing-database-architecture/

### S28 — Product editions and pricing

- Type: Official commercial page
- Audit note: Edition limits and data-volume licensing
- URL: https://aerospike.com/products/features-and-editions/

### S29 — Database platform support

- Type: Official documentation
- Audit note: Current Database release matrix
- URL: https://aerospike.com/docs/database/reference/platform-support

### S30 — Database limits

- Type: Official documentation
- Audit note: Cluster and object limits
- URL: https://aerospike.com/docs/database/reference/limitations/

### S31 — Database storage configuration

- Type: Official documentation
- Audit note: Memory, device, and persistence modes
- URL: https://aerospike.com/docs/database/manage/namespace/storage/config/

### S32 — Database FAQ

- Type: Official documentation
- Audit note: CE/SE/EE/FE boundaries
- URL: https://aerospike.com/docs/database/reference/faq

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S34 — AGS data model design

- Type: Apache-2.0 source documentation
- Audit note: Packed record layout
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md

### S35 — AGS architecture source map

- Type: Apache-2.0 source documentation
- Audit note: Modules and entry points
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/ARCHITECTURE.md

### S36 — AGS AerospikeOperations

- Type: Apache-2.0 source
- Audit note: Read/write and edge mutation pipeline
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java

### S37 — AGS configuration source

- Type: Apache-2.0 source
- Audit note: Code defaults and validators
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java

### S38 — AGS query code

- Type: Apache-2.0 source
- Audit note: Paged scans and secondary-index queries
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query

### S39 — AGS traversal strategies

- Type: Apache-2.0 source
- Audit note: Rewrite implementations
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy

### S40 — AGS transaction implementation

- Type: Apache-2.0 source
- Audit note: TinkerPop transaction wrapper
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java

### S41 — AGS tests

- Type: Apache-2.0 source
- Audit note: 431 test files observed in snapshot
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test

### S42 — Graph examples

- Type: Apache-2.0 source
- Audit note: Examples at e2300bc201f949c4261ecd88b235dea1877fa088
- URL: https://github.com/aerospike/aerospike-graph/tree/e2300bc201f949c4261ecd88b235dea1877fa088

### S43 — Database server source snapshot

- Type: AGPL/community core source
- Audit note: Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc
- URL: https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

### S44 — Java client source snapshot

- Type: Apache-2.0 source
- Audit note: Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
- URL: https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12

### S45 — Apache TinkerPop 3.7.3 reference

- Type: Upstream documentation
- Audit note: Language/runtime semantic oracle
- URL: https://tinkerpop.apache.org/docs/3.7.3/reference/

### S46 — AGS v3.3.0-rc5 prerelease tag

- Type: Signed public source tag
- Audit note: Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3
- URL: https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3

### S47 — Graph 2.5 strong-consistency launch blog

- Type: Vendor blog
- Audit note: Database 8 transaction positioning and the explicit eventual-read caveat
- URL: https://aerospike.com/blog/aerospike-graph-2-5-0-strong-consistency

### S48 — Aerospike Graph AI and MCP blog

- Type: Vendor blog
- Audit note: Newest Graph-specific blog found in the publication sweep; an integration/demo layer, not a storage-engine release
- URL: https://aerospike.com/blog/aerospike-graph-ai-mcp-natural-language-queries/

### S49 — Legacy asbackup documentation

- Type: Official documentation
- Audit note: The target of the current Graph backup-page link; explicitly labeled legacy
- URL: https://aerospike.com/docs/database/tools/backup-and-restore/asbackup

### S50 — Current Database backup and restore overview

- Type: Official documentation
- Audit note: ABS and absctl are current choices while asbackup/asrestore are legacy
- URL: https://aerospike.com/docs/database/tools/backup-and-restore/overview/
