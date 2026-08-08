# Proposed zu architecture for low latency, low resources, S3 authority, and PB scale

Research cut: `2026-08-08`
Status: proposal and qualification plan, not a current performance claim.

## 1. Outcome

Build one semantic graph database with three execution profiles, not one magical deployment that pretends remote object storage behaves like RAM. The profiles share logical IDs, schema, query semantics, immutable segment envelopes, and conformance tests. They differ in persistence, writer coordination, cache/SLO class, and distributed guarantees.

- `zu1-local`: one process writer broker, snapshot readers, local WAL plus immutable extents, sub-millisecond hot point/traversal target.
- `object-single`: one fenced writer per partition, immutable S3 packs, stateless readers with RAM/NVMe caches, bounded-staleness or strong-root reads.
- `object-partitioned`: many independently fenced partitions, workload-aware placement, read scale-out, and explicit restrictions on cross-partition writes.

A future distributed-write profile requires a transactional metadata service and a clear atomic-edge placement protocol. It is not smuggled into v1 through optimistic manifest language.

## 2. Non-negotiable mathematics

At one trillion edges, every additional byte per stored directed projection consumes roughly one terabyte before replication, versions, indexes, or object overhead. Storing two adjacency directions means the edge budget is paid twice. A 16-byte neighbor-plus-edge reference is already about 32 TB for two directions at one trillion edges; a thousand trillion edges is three orders of magnitude larger and cannot be casually called one petabyte.

Therefore `thousands of billions` must be expressed numerically. One thousand billion is one trillion. One million billion is one quadrillion. A 1-PB physical budget can hold only a bounded number of edges determined by topology bytes, properties, compression, indexes, history, and replication. The capacity calculator is a release artifact.

## 3. Stable identity and partition map

- Assign 128-bit logical NodeId and EdgeId values independent of location.
- Keep table/schema IDs stable and versioned.
- Treat row group, CSR slot, tile offset, pack range, and shard as locators.
- Store logical-to-physical mapping in immutable partition manifests and compact indices.
- Preserve parallel edges by carrying EdgeId in both adjacency directions.
- Order adjacency entries by neighbor ID then EdgeId for merge, search, and deterministic export.
- Give high-degree vertices continuation tiles addressed by logical key range.
- Version partition-map changes and pin the map in every SnapshotToken.

## 4. Physical graph layout

Each immutable partition generation contains a small root manifest, sharded metadata trees, adjacency directory tiles, adjacency data tiles, stable edge records, column tiles, primary-key indices, optional secondary indices, statistics, and tombstone/delta references. Packs combine many tiles to amortize PUT and GET overhead while preserving tile-level offsets and checksums.

Adjacency directory tiles cover contiguous node-ID ranges and encode degree, first tile, continuation count, min/max neighbor, compressed byte length, and a high-degree exception pointer. Data tiles store neighbor deltas, EdgeId deltas or local dictionaries, optional hot projected properties, validity/version information, and a checksum over exactly the independently fetched bytes.

Do not place update slack inside sealed CSR. Mutations enter a WAL-backed delta adjacency organized by partition and source bucket. Readers merge base plus visible deltas. Checkpoint rewrites only affected partition ranges and publishes a new immutable root.

## 5. Hot/warm/cold topology tiers

- Tier 0: compact degree/partition routing metadata in RAM.
- Tier 1: hot adjacency and dictionaries in compressed RAM cache.
- Tier 2: larger content-addressed NVMe cache shared by local workers.
- Tier 3: S3 Standard authoritative immutable packs and manifests.
- Optional Tier 3W: low-latency object class for WAL only when its durability/availability tradeoff is accepted.

The engine never promises one latency number across tiers. Plans carry a cache certainty class and estimated remote rounds. Admission can reject a query whose cold path exceeds the user's latency or cost budget.

## 6. Remote-read algorithm

1. Resolve and pin `CURRENT` using an ETag/version-aware metadata cache.
2. Read the bounded root and only the partition submanifests needed by the plan.
3. Group frontier node IDs by partition, pack, and coalescible byte range.
4. Check RAM then NVMe using immutable content/range keys.
5. Deduplicate concurrent misses through a single-flight table.
6. Issue bounded parallel range GETs with reserved in-flight byte credits.
7. Verify per-tile checksums before exposing decoded values.
8. Decode into ownership-carrying vector batches.
9. Emit the next frontier early enough to overlap prefetch with current-level processing.
10. Cancel speculative reads immediately when the query completes or reaches its budget.

Pointer chasing against cold S3 is forbidden. A k-hop cold traversal should require approximately one batched remote phase per dependent frontier level, not one GET per node or edge.

## 7. Query execution

Use a hybrid engine rather than forcing every workload through one abstraction:

- Vectorized column scans with predicate/projection pushdown.
- Factorized intermediate tables for join-heavy graph patterns.
- Batched adjacency expansion keyed by input positions.
- ExpandInto using sorted adjacency or endpoint indices.
- Worst-case-aware multiway joins for cyclic patterns.
- Dedicated frontier/fixpoint operators for reachability and BFS.
- Bidirectional search for point-to-point shortest paths.
- Compact path representations for path-returning queries.
- Matrix/bitset kernels only when frontier density crosses a calibrated threshold.
- Late materialization of cold properties.
- Morsel scheduling with degree-aware work splitting.

The storage SPI accepts batch requests and returns asynchronous streams. It exposes capabilities and cost estimates, never raw S3 calls or a synchronous `neighbors(node)` loop.

## 8. Cost-based optimizer

The cost vector contains rows, edges, compressed bytes, decoded bytes, CPU cycles, peak memory, disk reads, remote requests, remote bytes, network shuffle bytes, spill bytes, cache certainty, and expected tail latency. It is not collapsed too early into one scalar. Admission uses hard dimensions; plan ranking uses a configurable weighted score.

Persist degree histograms by type/direction, joint endpoint statistics, label/property correlations, heavy hitters, high-degree exceptions, tile compressed sizes, zone maps, index selectivity, delta depth, partition-crossing ratios, and observed cache residency. Stats generation is pinned by the snapshot token.

## 9. Transactions and publication

A commit has an idempotency key, logical mutation digest, writer epoch, partition, base generation, validation read set, and durability class. The writer validates constraints and conflicts, uploads immutable WAL/data objects, verifies them, writes an immutable manifest, then conditionally advances the partition root. Lost responses are reconciled by transaction identity and manifest ancestry.

Conditional PUT of `CURRENT` prevents two root updates from both succeeding, but it is not a writer lease. A fencing authority assigns monotonic epochs. The writer stops acknowledging before lease uncertainty. WAL objects, manifests, and receipts all carry the epoch so stale acknowledgements are detectable.

## 10. Partitioning for PB scale

Use a two-level scheme: tenant/table isolation first, then graph-locality partitions. The default is stable source-ID range/hash hybrid with optional community/locality remapping during offline optimization. Very high-degree vertices receive explicit split ownership with deterministic read assembly.

An edge has one transactional home. Both directional projections for a strict commit must be published under one atomic partition root or through a transactional metadata record that binds both partitions. If that is not available, cross-partition mutations are asynchronous and labeled accordingly.

Partition roots are small and independent. A catalog root maps logical ranges to partition generations. Readers pin one catalog epoch. Repartitioning writes new partitions, validates equivalence, atomically changes the catalog mapping, and retains old partitions until all pinned readers and retention policies release them.

## 11. Resource minimization

- Compressed-cache-first: decode only selected columns/adjacency tiles.
- Use 32-bit local ordinals inside partitions while preserving 128-bit external identity.
- Delta-code sorted neighbors and local edge ordinals; choose encoding per tile from samples then verify full-size benefit.
- Intern repeated labels, types, strings, and partition-local ID prefixes.
- Separate scan admission from reusable point/traversal cache admission.
- Reserve bytes before allocation and before I/O.
- Bound every queue and propagate backpressure to clients.
- Isolate maintenance CPU/I/O with explicit budgets.
- Run stateless query workers only when the namespace working set justifies them.
- Scale to zero for inactive namespaces while retaining a small manifest/metadata cache.

## 12. Fixed-cost service contract

A monthly plan includes logical stored bytes, retained history, maximum cached bytes, admitted query CPU-seconds, remote GET count/bytes, write bytes/PUTs, result egress, and maintenance budget. The system enforces token buckets at namespace and tenant levels. Once exhausted, it queues, degrades to eventual consistency where authorized, requires a cost override, or rejects—never silently creates an unbounded bill.

The plan price reserves worst-case included capacity plus risk margin. S3 itself is variable cost. `Fixed price` is a commercial envelope enforced by technical limits and multiplexing, not a physical property.

## 13. SLO classes

- Hot local point: target p50 under 100 µs and p99 under 1 ms on qualified hardware.
- Warm NVMe point/one-hop: target p50 under 1 ms and p99 under 5 ms.
- Warm remote-profile point/one-hop served from local cache: target p99 under 10 ms including network.
- Cold S3 Standard point: target bounded request count and p99 under 300 ms, not local latency.
- Cold k-hop: target no more than metadata rounds plus one dependent frontier round per hop.
- Overload: preserve bounded memory and p99 by rejecting before resource exhaustion.

These are qualification targets. They are not claims about the current repository.

## 14. Implementation order

1. Replace the disconnected storage/query traits with SnapshotReader and typed batch streams.
2. Fix stable EdgeId and query-visible MVCC overlays.
3. Implement positioned I/O, shared cache ownership, per-chunk integrity, and bounded open/recovery.
4. Freeze a pre-v1 immutable segment envelope only after golden readers and fuzzing.
5. Make local factorized/vectorized execution correct and resource-accounted.
6. Add object packs, manifests, range planning, cache, request accounting, and provider contract tests.
7. Add fencing and ambiguous-commit reconciliation.
8. Add partition catalog, repartitioning, pins, and GC.
9. Publish benchmark harness and only then evaluate tenfold cells.

## 15. Kill criteria

Stop or redesign the remote profile if cold point queries require unbounded object requests, if the cache cannot preserve reusable topology under scans, if writer fencing cannot prove acknowledgement safety, if cross-partition edge consistency is unspecified, if GC cannot avoid live-object deletion, or if cost admission cannot enforce the sold envelope.

## 16. Architecture evidence

- [BG3: A Cost Effective and I/O Efficient Graph Database in ByteDance](https://doi.org/10.1145/3626246.3653373) — published graph-on-cloud-storage evidence.
- [SlateDB design overview](https://slatedb.io/docs/design/overview/) — object-store LSM, WAL, manifests, and tradeoffs.
- [SlateDB introduction](https://slatedb.io/docs/get-started/introduction/) — single writer, multiple readers, cache, snapshots, and fencing posture.
- [SlateDB manifest RFC](https://slatedb.io/rfcs/0001-manifest/) — why writer/WAL fencing is more than replacing one pointer.
- [turbopuffer architecture](https://turbopuffer.com/docs/architecture) — measured cold/warm gap, WAL batching, NVMe locality, and object-oriented index design.
- [PuppyGraph architecture/docs](https://docs.puppygraph.com/) — current commercial graph-over-lake comparator.
- [Microsoft Fabric Graph architecture](https://learn.microsoft.com/en-us/fabric/graph/how-graph-works) — read-optimized graph materialization over OneLake.
- [SurrealDB architecture](https://surrealdb.com/docs/architecture) — compute/storage separation and current storage-engine matrix.
- [LDBC SNB Interactive](https://ldbcouncil.org/benchmarks/snb/interactive/) — audited interactive throughput and full-disclosure methodology.
- [LDBC Graphalytics](https://ldbcouncil.org/benchmarks/graphalytics/) — standardized graph algorithm work.
- [SoK: The Faults in our Graph Benchmarks](https://arxiv.org/abs/2404.00766) — ID ordering, zero-degree nodes, dataset realism, and reporting hazards.

## Appendix A. Release-gate assertions

- RG-001: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-002: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-003: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-004: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-005: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-006: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-007: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-008: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-009: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-010: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-011: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-012: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-013: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-014: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-015: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-016: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-017: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-018: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-019: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-020: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-021: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-022: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-023: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-024: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-025: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-026: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-027: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-028: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-029: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-030: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-031: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-032: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-033: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-034: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-035: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-036: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-037: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-038: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-039: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-040: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-041: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-042: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-043: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-044: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-045: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-046: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-047: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-048: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-049: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-050: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-051: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-052: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-053: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-054: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-055: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-056: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-057: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-058: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-059: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-060: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-061: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-062: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-063: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-064: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-065: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-066: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-067: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-068: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-069: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-070: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-071: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-072: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-073: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-074: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-075: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-076: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-077: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-078: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-079: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-080: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-081: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-082: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-083: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-084: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-085: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-086: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-087: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-088: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-089: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-090: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-091: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-092: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-093: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-094: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-095: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-096: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-097: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-098: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-099: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-100: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-101: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-102: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-103: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-104: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-105: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-106: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-107: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-108: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-109: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-110: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-111: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-112: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-113: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-114: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-115: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-116: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-117: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-118: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-119: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-120: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-121: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-122: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-123: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-124: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-125: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-126: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-127: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-128: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-129: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-130: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-131: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-132: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-133: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-134: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-135: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-136: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-137: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-138: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-139: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-140: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-141: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-142: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-143: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-144: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-145: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-146: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-147: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-148: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-149: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-150: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-151: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-152: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-153: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-154: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-155: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-156: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-157: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-158: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-159: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-160: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-161: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-162: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-163: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-164: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-165: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-166: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-167: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-168: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-169: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-170: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-171: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-172: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-173: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-174: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-175: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-176: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-177: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-178: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-179: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-180: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-181: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-182: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-183: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-184: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-185: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-186: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-187: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-188: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-189: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-190: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-191: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-192: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-193: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-194: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-195: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-196: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-197: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-198: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-199: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-200: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-201: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-202: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-203: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-204: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-205: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-206: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-207: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-208: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-209: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-210: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-211: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-212: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-213: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-214: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-215: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-216: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-217: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-218: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-219: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-220: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-221: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-222: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-223: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-224: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-225: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-226: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-227: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-228: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-229: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-230: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-231: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-232: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-233: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-234: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-235: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-236: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-237: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-238: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-239: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-240: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-241: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-242: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-243: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-244: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-245: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-246: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-247: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-248: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-249: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-250: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-251: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-252: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-253: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-254: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-255: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-256: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-257: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-258: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-259: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-260: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-261: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-262: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-263: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-264: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-265: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-266: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-267: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-268: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-269: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-270: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-271: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-272: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-273: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-274: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-275: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-276: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-277: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-278: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-279: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-280: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-281: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-282: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-283: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-284: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-285: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-286: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-287: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-288: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-289: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-290: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-291: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-292: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-293: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-294: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-295: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-296: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-297: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-298: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-299: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-300: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-301: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-302: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-303: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-304: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-305: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-306: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-307: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-308: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-309: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-310: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-311: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-312: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-313: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-314: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-315: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-316: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-317: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-318: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-319: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-320: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-321: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-322: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-323: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-324: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-325: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-326: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-327: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-328: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-329: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-330: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-331: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-332: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-333: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-334: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-335: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-336: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-337: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-338: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-339: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-340: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
- RG-341: For the target architecture, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-342: For the target architecture, release is blocked until the dataset and update-stream digests are immutable.
- RG-343: For the target architecture, release is blocked until the query plan/profile is archived.
- RG-344: For the target architecture, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-345: For the target architecture, release is blocked until a second operator can reproduce the run from a clean host.
- RG-346: For the target architecture, release is blocked until the raw samples and aggregated chart agree.
- RG-347: For the target architecture, release is blocked until the query result matches the canonical oracle.
- RG-348: For the target architecture, release is blocked until the engine version and artifact digest are recorded.
- RG-349: For the target architecture, release is blocked until the selected durability level matches the comparison class.
- RG-350: For the target architecture, release is blocked until cache state is explicit and reproducible.
- RG-351: For the target architecture, release is blocked until peak memory includes engine and required sidecars.
- RG-352: For the target architecture, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-353: For the target architecture, release is blocked until timeouts and rejected operations remain in the result set.
- RG-354: For the target architecture, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-355: For the target architecture, release is blocked until background maintenance is either quiesced or reported.
