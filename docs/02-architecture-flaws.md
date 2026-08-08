# Architecture flaw register

## Severity model

- **P0**: makes documented semantics impossible or risks acknowledged-data loss/corruption.
- **P1**: forces a rewrite, invalidates a headline property, or prevents one product/API.
- **P2**: important production gap with a contained migration path.
- **P3**: documentation, ergonomics, or later optimization.

## P0: relationship identity is not represented end to end

**Evidence:** query values use `(table, src, dst)`; trail visited checks compare that tuple; storage neighbor arrays contain only destinations; `has_edge` is boolean; checkpoint rebuild sorts edges; physical `RelId` is unused.

**Failure:** parallel relationships collapse for equality and path restrictions. Relationship property lookup and delete cannot name the intended edge. Reordering or rebuilding can change a slot-based ID.

**Decision:** introduce logical `EdgeId(u128)` (serializable as two `u64` words where an ABI requires it), allocated at insert/bulk load. Every adjacency entry carries `(neighbor, edge_id)` in parallel compressed streams. Edge properties are keyed/densely located by `edge_id` through a versioned locator index. All query `Rel` values contain `edge_id`; `(src,dst)` is metadata.

**Gate:** generated multigraph corpus with parallel self-loops must match a reference evaluator for equality, trail, simple path, delete-one, update-property, checkpoint, reorder, export/import, and both directions.

## P0: commits and queries use disconnected state

**Evidence:** `Mvcc` exists in `zu-zu1`; the only query facade receives `&mut Zu1File`; it never receives `Mvcc` or an epoch.

**Failure:** a successful commit may not be visible to a new query until checkpoint. There is no API-level read-your-writes, repeatable read, or pinned historical snapshot.

**Decision:** `DatabaseInner` owns engine, transaction manager, catalog registry, epoch pins, and maintenance. `Connection` begins a `ReadTxn` with a `SnapshotToken`; `WriteTxn` exposes an overlay view and commits through one coordinator. Storage adapters merge base and overlay into snapshot batches or provide native snapshot reads.

**Gate:** API-level tests, not module tests, prove read-your-writes, old-reader stability across commit/checkpoint, rollback, recovery, and concurrent readers.

## P0: S3 fencing is insufficient for acknowledgement semantics

**Evidence:** `take_over()` unconditionally advances writer ID via manifest CAS. Current code has no WAL, but docs plan to acknowledge after WAL PUT. CAS-fencing only `CURRENT` does not stop a stale writer from successfully PUTting a WAL object or reporting success.

**Failure:** two writers can each acknowledge transactions, while only one lineage becomes reachable; automatic takeover can oscillate under a partition; ambiguous timeouts can duplicate or lose logical commits.

**Decision:** separate writer arbitration, log-position fencing, and root publication. A writer obtains a monotonically increasing `WriterEpoch` from a fencing authority; each WAL position is create-only and names that epoch; a commit is acknowledged only after the WAL batch is durably recorded and an authoritative log-tail CAS includes its digest. Takeover requires lease expiry/external election or an explicit operator force token. Every uncertain response is reconciled by `(txn_id, epoch, log_seq, digest)`.

**Gate:** deterministic state-machine tests and real-provider tests cover delayed/duplicated requests, timeouts after success, zombie writers, takeover, stale credentials, and GC.

## P0: partitioning breaks graph consistency

**Evidence:** docs allow an edge spanning independently committed partitions and call it eventually visible. Forward CSR belongs naturally to source partition; backward CSR belongs to destination partition.

**Failure:** an edge may exist forward but not backward. The answer changes with query direction, violating one property graph snapshot. Node deletion/constraints cannot be atomic.

**Decision for v1:** strict ownership. A partition owns nodes and canonical edge records by source. Reverse adjacency for remote destinations is an asynchronous derived index and MUST NOT be used for strict snapshot queries. Strict queries either route through canonical source ownership or reject plans requiring stale reverse indexes. Cross-partition writes are rejected in ACID transactions. A future global snapshot/control plane is a separate profile.

## P1: the architectural SPI is dead code and has the wrong shape

**Failure:** implementing SQLite/S3 against it would force decompression/copies, serialize remote reads, and omit pushdown/cancellation. Keeping the executor's `Graph` trait would create object-store pointer chasing.

**Decision:** replace both traits with `CatalogService`, `SnapshotReader`, `MutationSink`, and `MaintenanceService`. Read requests are vector/batch-oriented and return owned/pinned views or streams. Capabilities are explicit. See [05](./05-storage-query-contract.md).

## P1: physical location is confused with logical identity

**Evidence:** dense row offsets double as default user ID; packed NodeId encodes group/row; reorder relies on a partial key index; `RelId` encodes CSR slot.

**Failure:** vacuum/reorder/schema migration conflict with stable identity; keyed tables without a relationship can return any requested key as if it existed; invalid packed values can truncate in release.

**Decision:** `NodeId` and `EdgeId` are immutable logical IDs. A snapshot-specific locator maps them to table/row/group/slot. User primary key is a separately typed unique key. Packed physical locators never cross the public API or WAL semantic layer.

## P1: the persistence model cannot be shared exactly as documented

**Failure:** SQLite native MVCC/locking and object-store immutable roots do not use zu1's in-memory version chains. Forcing one physical MVCC either defeats SQLite or leaks engine behavior.

**Decision:** share isolation contract, logical mutations, validation rules, transaction IDs, and conformance tests. Each backend implements `begin_snapshot`, durable commit, and recovery using its native mechanism. The coordinator owns public transaction lifecycle and single-writer policy.

## P1: format version 1 is premature

**Failure:** adding edge IDs, chunk checksums, typed zones, group-local directories, labels, nullability, and a real encoding tree changes bytes and metadata. Pretending compatibility now creates permanent baggage.

**Decision:** mark existing files `experimental_epoch=0`; the next writer emits format epoch 1 but still declares `stability=experimental`. Freeze only after independent reader, golden corpus, mutation/recovery, and compatibility gates. Public v1 software version is independent from on-disk format number.

## P1: synchronous point API conflicts with remote and parallel I/O

**Failure:** `neighbors(node)` encourages one call/read per node; `block_on` creates hidden runtime nesting; private reader caches duplicate memory; no cancellation or deadlines reach I/O.

**Decision:** requests describe many adjacency lists, projections, row selections, and an I/O budget. They return futures/streams of splits. Local adapters may complete immediately. The pipeline uses bounded async-source operators feeding CPU workers with backpressure; no Tokio requirement leaks into public core.

## P1: performance goals are inconsistent with evidence

**Evidence:** G5 says ≤8 bits/edge, current budget permits 22; G1 says p99 <100 µs but gates mostly p50; SQLite and S3 targets are mixed with zu1; cold and warm definitions vary.

**Decision:** publish profile-specific SLOs with dataset, cache state, concurrency, durability mode, hardware, percentile, and correctness checksum. Current numbers remain engineering observations. Aspirational goals remain qualification targets until a reproducible artifact passes.

## P2: checksum granularity is wrong for point access

**Decision:** every independently fetched/decoded chunk has CRC32C; immutable object/pack descriptors also carry BLAKE3-256 content digests. Metadata binds chunk range, logical type, count, encoding, and digest. Point reads validate chunk checksum before decode; full verification additionally validates object digest and graph invariants.

## P2: open and recovery bounds are unspecified in actual structures

**Decision:** headers point to a bounded root page containing allocator summary and root directory. Free space is a persistent bitmap/radix tree loaded lazily; startup reads a fixed maximum (target ≤64 KiB local). WAL recovery is capped by bytes and transactions; exceeding the cap switches to explicit recovery progress, not an “open <10 ms” claim.

## P2: fixed group size is overloaded

The same 131,072-row group is called compression, zone-map, MVCC, rewrite, cache, and S3 packing unit. These concerns have different optimal sizes. High-degree adjacency and wide strings make group bytes unbounded.

**Decision:** separate logical row group (ID/visibility), column page/chunk (encoding and checksum), adjacency tile (source range and edge budget), and pack object (remote request economics). Directories map between them. Targets are byte-bounded, not only row-bounded.

## P2: catalog and plan lifetime are under-specified

**Decision:** catalog is immutable and versioned; every snapshot token names a catalog digest. Plans bind stable object IDs and carry a compatibility predicate. DDL invalidates only plans whose dependency set changed. Catalog fetch, stats, and data root are atomic from the reader's perspective.

## P2: memory accounting and cancellation are absent

**Decision:** hierarchical reservations cover decoded batches, factorized lists, hash tables, PMRs, overlays, cache entries, inflight I/O, and maintenance. Operators acquire before allocating and spill/yield/error deterministically. Cancellation propagates to queued morsels, object reads, SQLite statements, and maintenance waiters.

## P2: cost model is an estimate without enforcement

**Decision:** the optimizer produces an estimated remote request/byte envelope; runtime charges actual operations. Namespace token buckets bound GET, PUT, bytes, and concurrency. Policies choose wait, reject, degrade-to-stale, or require explicit override. Reports separate object-storage, compute, NVMe, network, and operational cost.

## P2: reproducibility and compatibility controls are missing

**Decision:** track `Cargo.lock` for workspace binaries, pin toolchain and external fixtures, record benchmark dataset digests, generate an SBOM, test previous released readers/writers, and require format corpus review for byte changes.

## P3 corrections

- Replace “Kùzu is dead and the lane is open” with current competition: Ladybug is actively maintained in July 2026 and offers the same embedded columnar/CSR/factorized baseline.
- Do not call vector/FTS/MCP “table stakes” in architecture requirements; make them product features with measured demand and isolated indexes.
- Do not promise “no fsck”; promise automatic recovery for supported failure classes and a verifier/repair tool for corruption.
- Do not say a general graph query is GQL-conformant until a clause-by-clause conformance declaration and tests exist.
- Generate README status from a capability manifest so implementation milestones cannot drift from prose.
