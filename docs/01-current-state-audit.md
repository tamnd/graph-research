# Current-state audit

## Baseline and method

The audit used commit `1f2c7834a3069fe458ee056c0478efc206f87454` from 2026-08-07. The worktree was clean. `cargo test --workspace --all-features` passed: 321 tests across the workspace, including 108 `zu1`, 106 query, 68 encoding, 18 S3-manifest, 12 SQLite, and 9 facade/common tests. This is strong evidence for the implemented slices, not evidence that the documented end-state exists.

Tracked production source is roughly 22 K lines. The largest modules are `zu-query/src/exec.rs` (~4.3 K), `zu-query` as a crate (~9.8 K), and `zu-zu1` (~7.7 K). `zu-storage`, nominally the architectural center, is 62 lines and has no tests.

## Baseline evidence map

Line anchors below refer to the audited commit and are intended to make each major finding independently checkable.

| Finding | Baseline source evidence |
|---|---|
| storage SPI is declarations/placeholders | `crates/zu-storage/src/lib.rs:29–60` (`Catalog`, `CommitBatch`, `SealedNodeGroup`, `SegmentRef`, `CsrRef`, `Snapshot`, `GraphStore`) |
| executor has a second storage trait | `crates/zu-query/src/exec.rs:72–137` (`Value`, `Graph`) |
| relationship value lacks edge identity | `crates/zu-query/src/exec.rs:79`; trail equality at `:1670`; pair expansion at `:2115–2132` |
| zu1 is wired directly into the query facade | `crates/zu/src/query.rs:132–280`; worker fork reopens at `:260` |
| packed IDs validate only in debug | `crates/zu-common/src/id.rs:40–50`; unused physical `RelId` begins at `:92` |
| MVCC/WAL/fold are zu1-local | `crates/zu-zu1/src/txn.rs:61–190`, `wal.rs`, and `fold.rs:105–180` |
| fold retains a 32-bit relationship row ceiling | `crates/zu-zu1/src/fold.rs:315–336` |
| open eagerly materializes the free list | `crates/zu-zu1/src/file.rs:219–263`; it is decoded again in `lib.rs:183–186` |
| point/range path skips the whole payload CRC | `crates/zu-zu1/src/segment.rs:29–30`, full validation at `:211–235`, partial paths at `:284` and `:358` |
| object layer is a manifest-only CAS prototype | `crates/zu-s3/src/manifest.rs:4–30`, `store.rs:1–18`, takeover at `store.rs:107–129` |
| facade engines are unconditional dependencies | `crates/zu/Cargo.toml:15–19`; only `arrow` is feature-gated at `:28–29` |
| DML clauses are deliberately rejected | `crates/zu-query/src/parser.rs:25–28`, test at `:914` |

The principal design claims being compared are in `README.md`, `docs/00-overview.md`, `docs/02-architecture.md`, `docs/04-storage-zu1-format.md`, `docs/06-storage-s3.md`, `docs/08-transactions-mvcc.md`, and `docs/10-api-and-tooling.md`.

## What is genuinely strong

### Encoding and defensive parsing

- Stable numeric encoding IDs exist for Plain, Constant, RLE, Dict, FOR, Delta, ALP, ALP-RD, FSST, Bool, Frequency, Zstd, and DeltaPatch.
- Integer MiniBlock chunks select one encoding from sampled candidates and fall back to Plain if the full encoding expands.
- Decoders take caller ceilings, reject hostile counts, and have extensive unit/fuzz coverage.
- FullZip, float, FSST, Zstd, validity, point-range, fence, and zone-map slices are separately implemented and tested.
- Miri covers the encoding roundtrip sweep; CI fuzzes a useful subset of decoders and file verification.

The implementation is more honest than the prose in one respect: `bench/budgets.toml` records that LiveJournal adjacency is currently about 21–22 bits/edge, not the 4–8 bits/edge headline.

### `zu1` file mechanics

- A 4 KiB file header and two alternating 4 KiB database headers are implemented.
- Data is placed in 256 KiB blocks; metadata chains, a delayed free list, catalog, table index, props, CSR directions, key index, and whole-file verifier exist.
- Publication writes data, syncs, flips the alternate database header, and syncs again.
- Open validates the two headers and chooses the highest valid epoch.
- Segment point reads access only required chunk spans, while full reads validate CRC, fences, counts, and zones.
- WAL frames are length/CRC protected; replay recognizes committed prefixes and ignores torn tails.
- The latest slices implement in-memory epoch-stamped overlays and checkpoint folding into new roots.

### Query prototype

- Lexer, recursive-descent parser, binder, logical plan, join ordering, optimizer, factorized pull executor, profiling, and a work-stealing morsel path exist.
- Supported query slices include `MATCH`, `OPTIONAL MATCH`, `WHERE`, `WITH`, `UNWIND`, `RETURN`, expressions, ordering, pagination, fixed expansions, variable-length trail enumeration, aggregations, and an ASP-style edge-set closure.
- Flat execution is used as a differential oracle for factorized execution in tests.
- Queries run end-to-end against actual `zu1` catalogs and properties.

### SQLite and object-storage prototypes

- SQLite opens/claims a database, sets WAL/NORMAL, creates safe identifiers and adjacency indexes, inserts rows, and serves neighbor/count reads.
- The S3 crate serializes a CRC-protected manifest and exercises conditional create/update against the in-memory `object_store` backend.
- Tests correctly record that `object_store::local::LocalFileSystem` does not implement conditional update; the current S3 test is therefore not a real-provider conformance test.

## The architecture described in docs does not exist

### Two incompatible storage interfaces

`zu-storage` declares:

```rust
pub trait Snapshot {
    fn scan_column(...) -> Result<SegmentRef>;
    fn csr(...) -> Result<CsrRef>;
    fn lookup_pk(...) -> Result<Option<NodeOffset>>;
}
```

Every payload (`Catalog`, `CommitBatch`, `SealedNodeGroup`, `SegmentRef`, `CsrRef`) is empty. No engine implements `GraphStore` or `Snapshot`; repository search finds only declarations, re-exports, and comments promising future implementation.

The working executor instead declares a second trait:

```rust
pub trait Graph {
    fn neighbors(&mut self, rel, node, reversed, out) -> Result<()>;
    fn has_edge(&mut self, rel, src, dst) -> Result<bool>;
    fn degree_sum(...);
    fn lookup_key(...);
    fn property(...);
    fn fork(&self) -> Option<Box<dyn Graph + Send>>;
}
```

`zu/src/query.rs` implements that trait directly for `Zu1File`, imports the `zu1` catalog/props/CSR types, and loads a fresh catalog on every preparation. SQLite and S3 cannot execute a query. Therefore the central README claim—three storage engines sharing one query processor—is not currently true.

### Dependency direction contradicts the design

The docs say `zu-storage` owns node groups, segments, buffer management, WAL abstraction, and depends on `zu-encoding`; `zu-zu1` should depend on it. In code, `zu-zu1` depends only on common/encoding, owns its own segment, catalog, graph, WAL, and MVCC types, and does not reference `zu-storage`. The facade unconditionally depends on `zu1`, SQLite, S3, query, storage, Parquet-related optional paths, and bundled SQLite; advertised engine feature isolation does not exist.

### Public API does not exist

The documented `Database`, `Config`, `Connection`, prepared statement, transaction, Arrow iterator, timeout, and engine selection APIs do not exist. `zu/src/lib.rs` is a re-export plus `query`; the actual API requires callers to own a mutable `Zu1File`. The CLI has useful copy/stat/query commands but is not proof of the documented embedded contract.

## Semantic gaps

### Relationship identity is lost

The data model permits multi-edges and says an internal relationship offset distinguishes them. The executor represents a relationship as only `{ table, src, dst }`. Trail detection calls `path.contains(rel_value)`, so two parallel edges are the same logical edge. `ExpandInto` returns at most one relationship for a pair. Edge properties cannot select a specific parallel edge. A physical `RelId` type exists but is unused by storage/query and its CSR slot would move during rebuild.

This is a correctness blocker for GQL `DIFFERENT EDGES`, relationship equality, relationship properties, deletes, exports, and checkpoint/reorder.

### Current capacity and identity differ from docs

- `NodeId` has the documented 14/22/17/11-bit layout, but `NodeId::new` uses `debug_assert!`; invalid public inputs silently truncate in release.
- The implemented graph loader and edges use `u32` rows. Checkpoint fold explicitly rejects a relationship table beyond the `u32` row domain. The 2^39 rows/table design limit is therefore not implemented.
- Query `Value::Node` uses `(table: u32, offset: u64)` rather than the packed `NodeId`.
- Primary keys are `u64` only in the working adapter, despite docs specifying general typed primary keys.
- Secondary labels, nulls in property storage, edge properties, multiple endpoint pairs, and declared cardinalities are not implemented.

### MVCC is isolated from queries and API

`Mvcc`, `WriteTxn`, recovery, and checkpoint fold are used only inside `zu-zu1` modules/tests. `zu::query::run` reads the sealed file through `GraphReader`; it has no overlay reference or snapshot epoch. Consequently a committed overlay is not query-visible through the public query facade until a fold. There is no connection-owned snapshot, epoch pin registry, or old-segment retention tied to active readers.

The docs say MVCC is shared above the engine trait. The code puts it in `zu-zu1` and SQLite delegates to independent SQLite transactions. Sharing semantic rules is desirable; pretending their physical MVCC is common is not.

### DML and constraints are absent

The parser explicitly rejects `CREATE`, `SET`, `DELETE`, `DETACH`, `MERGE`, `CALL`, `FILTER`, `LET`, and `NEXT`. Transaction operations accept numeric table/column/row values directly and do not perform catalog type checks, primary-key uniqueness, endpoint existence, detach rules, or write-write validation. WAL replay rejects DDL and ingest reference records as unsupported.

## Storage and integrity gaps

### Open is not strictly O(1)

`Zu1File::open` reads the 12 KiB headers, then eagerly reads and decodes the complete free-list metadata chain and walks it again for block IDs. Open cost is O(free blocks / metadata capacity), not O(1). The 10 GB benchmark can still pass because it does not imply a highly fragmented free list.

### Point reads can return silent corruption

Full segment reads verify the segment CRC. Point/range/probe paths intentionally skip it to avoid reading the whole payload. They validate bounds and structure but cannot detect a bit flip that remains structurally valid. A corrupt neighbor or property can therefore be returned without error. Per-chunk checksums or authenticated content IDs are required for the claimed integrity posture.

### I/O and buffer manager are not implemented

`Zu1File` uses `seek` plus `read_exact`/`write_all`, allocates a 256 KiB `Vec` for every full block read, and has no `IoBackend`, buffer manager, page state machine, budget accounting, prefetch, direct I/O, async interface, or cache. Query workers reopen the file read-write and maintain private decoded-group caches. This is functional prototyping, not the documented vmcache-style design.

### Format description and bytes have drifted

Docs describe a recursive `EncodingNode` cascade depth ≤3, while integer chunk payloads store one encoding ID; “cascade” is currently a name, not an encoding tree. Docs describe group-local CSR slack, continuation chains, tombstone validity, relationship columns, and 16-byte generic zones; current CSR is dense offsets/neighbors, fold rebuilds an entire relationship table, and segment zones are `u64` only.

The current format version is already `1`, but these incompatible fundamentals remain open. It MUST be treated as experimental, not frozen v1.

## S3 and cost gaps

- The implemented manifest contains only epoch, writer ID, and segment key strings. There are no packs, byte ranges, catalog, WAL interval, checksums/content IDs, checkpoints, GC boundary, partition root, or cost metadata.
- `CURRENT` stores the full manifest, unlike the documented small pointer object.
- `take_over()` lets any caller that can write immediately replace the current writer. No lease, external election, manual force token, or grace/failure detector exists.
- A CAS on `CURRENT` fences root publication but does not by itself prevent an old writer from uploading WAL/segments or acknowledging a WAL-only commit. SlateDB's own fencing design is more involved and fences WAL positions, not merely a manifest field.
- The cost table assumes a 95% hit rate; it does not bound misses. A 10× scan over new data raises GETs and bytes. The claim “flat ±10%” requires admission control or request shedding.
- “Total bill” excludes compute, NVMe, cache replication, retrieval, egress, observability, and operations. It is only a modeled object-storage subtotal.
- Independent partition manifests make the two adjacency directions of a cross-partition edge non-atomic. Readers can see different graphs depending on traversal direction.

## Build and release gaps

- `Cargo.lock` is ignored even though the workspace builds an application binary and database format; identical commits can resolve different transitive versions.
- Advertised default feature isolation is absent; all engines are unconditional facade dependencies.
- CI does not run deterministic crash injection, Loom, real object-store CAS conformance, differential zu1/SQLite queries, format golden files, backward compatibility, sanitizer jobs, or benchmark gates on normal pull requests.
- README says “nothing is usable” and “specification complete,” while substantial slices are implemented and the spec has material contradictions. Status needs generated feature/conformance tables.

## Conclusion

The repository is not an empty prototype. It contains valuable, well-tested algorithms. Its main risk is that continued vertical slices will harden the wrong seams: engine-specific query access, physical identity leaking into semantics, and separate transaction paths. The next milestone should be an architecture correction, not another feature.
