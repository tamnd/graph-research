# zu1 format, encoding, and local I/O

## Format posture

zu1 is an immutable, checksummed local checkpoint format with append-only publication metadata. It is not itself the database transaction layer. WAL/delta state is composed through the storage engine and becomes a new zu1 root during checkpoint.

The format is explicitly versioned and has a compatibility policy. Readers accept the current major version and documented older versions; writers emit one configured version. A major bump is required for a semantic reinterpretation. Minor extensions are length-delimited and ignorable only when marked optional.

## File layout

```text
superblock A (4 KiB)
superblock B (4 KiB)
root journal / bounded anchor area
immutable metadata pages
immutable data extents
optional append-only free-space/checkpoint records
```

Each superblock contains magic, format version, page-size log2, database lineage, root generation, root pointer/length, WAL replay position, feature flags, and checksum. Publication writes an inactive root/superblock, syncs required bytes, then advances the chosen superblock. Open selects the highest generation whose full dependency graph verifies.

The root contains a bounded directory of catalogs, table manifests, indexes, statistics, and extent maps. Opening a healthy file reads `O(1)` anchor pages plus requested metadata—not the complete free-list chain and not every segment. Free-space summaries are checkpoint artifacts with a bounded top-level index; rebuilding them is maintenance, not a prerequisite for read-only open.

## Page and object integrity

Every independently addressed unit has:

- type, version, logical object ID, generation, encoded and decoded lengths;
- codec/encoding ID and required feature flags;
- CRC32C for accidental corruption;
- parent manifests with a cryptographic digest (BLAKE3-256 or a specified equivalent) for identity and end-to-end validation.

A point lookup or range scan validates every chunk it consumes. Whole-segment checksums alone are insufficient because a fast path can skip untouched bytes and otherwise return silently corrupted values. Chunk size is selected so validation amplification remains bounded, initially 16–64 KiB.

Lengths, offsets, counts, bit widths, nesting, and allocation products are checked before pointer arithmetic or allocation. Decoding untrusted/corrupt files never invokes unchecked slicing. The verifier reports object and range; repair never silently edits the only copy.

## Row groups and arrays

The unit of pruning, fetching, and parallel scan is a row group. The initial target is 64K–1M logical rows depending on width, with a byte-size cap. Each group manifest records row range, column chunk locations, min/max/null/distinct metadata, encoding tree, checksums, and optional learned/selectivity metadata.

An array is a typed encoding tree, not one enum choice:

```text
ArrayNode := Flat
           | Constant
           | BitPacked(bit_width, child/domain)
           | FOR(base, deltas)
           | Delta(base, deltas)
           | RLE(values, runs)
           | Dictionary(dictionary, codes)
           | Sparse(present, values, default)
           | List(offsets, child)
           | Struct(children)
           | Validity(bitmap, child)
```

Nesting depth, child count, and decoded expansion are bounded. Each node declares supported kernels (`filter`, `compare`, `gather`, `sum`, `minmax`) so execution can operate compressed or request materialization. The encoder samples candidates and minimizes a calibrated objective over bytes, decode CPU, point access, and filter kernels. The current `encode_auto` single-choice behavior is retained only as a baseline.

Structural encodings should borrow the separable layout/scan ideas demonstrated by Lance and Vortex, while FastLanes motivates portable vector-sized primitives. Adoption requires zu-specific benchmarks and fuzzed round trips; a paper result is not a format guarantee.

## Adjacency layout

Each relationship table stores edge records by stable `EdgeId` plus two adjacency projections:

```text
out: src -> [(dst, edge_id, optional inline columns)]
in:  dst -> [(src, edge_id, optional inline columns)]
```

Lists are ordered by `(neighbor_id, edge_id)`, and high-degree lists are split into continuation tiles with explicit first/last keys. A two-level degree/offset index locates a node without decoding unrelated groups. Empty nodes remain representable through the node-domain index.

The sealed base is dense. Update slack is not placed inside immutable CSR; changes live in WAL-backed delta adjacency and are merged during reads. Checkpoint compacts selected relationship partitions/groups, not necessarily the entire table. A partition map and change heat determine rebuild scope. Claiming group-local rebuild is prohibited until this machinery exists.

## Indexes

Mandatory indexes:

- logical ID to group/ordinal for node and edge records;
- node primary key to `NodeId` with uniqueness metadata;
- source and destination adjacency directory;
- edge property locator by `EdgeId`;
- group-level zone maps/statistics.

Optional indexes are cataloged with build root, covered columns, state (`building`, `ready`, `stale`, `failed`), and checksum. Plans can use only `ready` indexes whose root/schema compatibility is proved.

## I/O backend

```rust
trait IoBackend: Send + Sync {
    fn read_many(&self, reqs: &[ReadRange], cx: &IoContext)
        -> BoxFuture<Result<Vec<ReadBuf>>>;
    fn write_extent(&self, req: WriteExtent, cx: &IoContext)
        -> BoxFuture<Result<WriteReceipt>>;
    fn sync(&self, scope: SyncScope) -> BoxFuture<Result<()>>;
}
```

Implementations include positioned buffered I/O first, optional mmap for immutable verified regions, and an experimental direct/async backend. Reads are positioned (`pread`-style), not shared seek state. Runtime capability detection and benchmarks choose the backend; unsupported kernels/filesystems fall back safely.

`GraphReader::fork` becomes a cheap clone of immutable metadata and shared cache handles. It must not reopen the file read-write, duplicate catalog walks, or create isolated caches. Write handles are separately typed and never required for a query.

## Buffer and decoded cache

The buffer manager has global budgets and two accounting domains:

- compressed page/chunk cache keyed by `(file identity, root, object, range)`;
- decoded/vector cache keyed by encoding node and selection/projection.

Entries carry checksum status, byte charge, pin count, and admission class. Scans use low-retention admission; point/metadata reuse is protected. SIEVE is a candidate low-overhead eviction policy, but it is not inherently scan-resistant, so scan admission/bypass is a separate rule. No per-reader unbounded cache is allowed.

All reads reserve bytes before issuance. Oversized results are rejected before allocation. Prefetch is cancellable and subordinate to demand. Metrics distinguish requested, fetched, validated, decoded, pinned, evicted, and wasted-prefetch bytes.

## Compaction and free space

Checkpoint/compaction writes new immutable extents, validates them, then publishes a new root. Readers pinned to old roots keep their extents live. Reclamation uses the minimum pinned root plus retained backup/history policy. A crash between extent creation and root publication leaves unreachable garbage discoverable by verify/GC, never visible partial data.

The allocator cannot trust an unverified free-list entry. Extent reuse occurs only after the root that last referenced it is unpinned and a durable reclamation record exists.

## Tooling and acceptance

`zu inspect` prints version/root/catalog without scanning data. `zu verify` supports anchor, metadata, selected table, and full modes. `zu salvage` writes a new file and emits an evidence report; it never mutates the source.

Format acceptance requires:

- golden files for every supported version and endian-independent scalar tests;
- property/fuzz tests over every encoding tree and corrupted length/offset;
- point, range, and predicate reads that detect a bit flip in every consumed chunk;
- crash tests around root publication and extent reuse;
- cold/warm open complexity measurements proving bounded anchor work;
- scan, lookup, adjacency, and high-degree benchmarks against the current baseline.
