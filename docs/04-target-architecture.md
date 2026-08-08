# Target architecture and crate boundaries

## Architecture overview

```text
Public API / CLI / bindings
        |
Session + transaction coordinator
        |--- CatalogService (immutable catalog per snapshot)
        |--- Compiler (parse -> semantic IR -> logical IR -> physical IR)
        |--- Runtime (pipelines, tasks, budgets, spill, cancellation)
        |
SnapshotReader + MutationSink + MaintenanceService
        |
   +----+-------------------+--------------------+
   |                        |                    |
zu1 adapter             SQLite adapter       object adapter
   |                        |                    |
page/chunk I/O           SQL/read pool        range I/O/cache
local WAL/CoW root       SQLite WAL           fenced WAL/roots
```

The query engine never imports `zu_zu1`, `rusqlite`, or `object_store`. Engine crates never import parser/optimizer/executor. `zu-core` is the composition root.

## Control plane versus data plane

### In-process control plane

`DatabaseInner` owns:

- engine instance and immutable capability descriptor;
- transaction coordinator and writer queue;
- current catalog/root generation registry;
- snapshot pin registry and safe-reclamation watermark;
- plan cache keyed by semantic dependencies;
- global memory/I/O/request budgets;
- maintenance scheduler;
- metrics and lifecycle state.

It does not own query-local vectors, hash tables, path state, or a global async runtime.

### Query data plane

Each query owns:

- one immutable snapshot token;
- one `QueryBudget` child reservation;
- physical pipelines and bounded channels;
- a cancellation token/deadline;
- per-worker arenas and spill files;
- source cursors created from the snapshot reader;
- profile counters and remote-cost ledger.

No mutable catalog or engine global is accessed from hot operators.

## Proposed workspace

| Crate | Responsibility | Allowed dependencies |
|---|---|---|
| `zu-types` | IDs, types, scalar/vector ABI, errors, limits | std only by default |
| `zu-format` | canonical segment envelopes, encoding trees, checksums, compatibility | `zu-types`, `zu-encoding` |
| `zu-encoding` | pure codecs and compute-on-encoded kernels | `zu-types` |
| `zu-catalog` | immutable schema, names, constraints, stats descriptors | `zu-types` |
| `zu-storage` | SPI request/response types and capability model | types/format/catalog |
| `zu-txn` | public transaction state machine, logical mutations, validation orchestration | types/catalog/storage |
| `zu-query` | syntax, semantic IR, logical/physical planning | types/catalog/storage interfaces |
| `zu-runtime` | vector/factorized execution, scheduling, budgets, spill | query/storage/format |
| `zu-zu1` | local persistence adapter, WAL, allocator, buffer manager | storage/format/txn protocol |
| `zu-sqlite` | relational persistence adapter and native pushdown | storage/catalog/txn protocol/rusqlite |
| `zu-object` | object packs, cache, fenced log/root, provider adapter | storage/format/object_store |
| `zu-core` | `Database`, `Connection`, feature-gated composition | selected engines + compiler/runtime |
| `zu-cli` | CLI only | `zu-core` |

Names may be consolidated to avoid premature crate explosion, but dependency direction is normative. In particular, `zu-zu1` MUST implement `zu-storage`; `zu-query` MUST NOT depend on `zu-zu1`; and `zu-storage` MUST contain real contract types with conformance tests.

## Canonical objects, not one physical format

The shared unit is a `SegmentEnvelope`:

```text
SegmentEnvelope {
  format_epoch, logical_type, encoding_tree,
  value_count, null_count, uncompressed_bytes,
  stats, chunk_directory, content_digest,
  chunk payloads...
}
```

`zu1` stores envelopes in local extents. Object storage stores them in immutable packs. SQLite MAY synthesize canonical batches without persisting envelope bytes; forcing SQLite to store opaque compressed blobs would sacrifice interop and native index benefits. Export/conversion materializes envelopes through the read SPI.

## Ownership and lifetime model

### Snapshot token

```rust
pub struct SnapshotToken {
    pub database: DatabaseId,
    pub data_generation: Generation,
    pub catalog_generation: Generation,
    pub stats_generation: Generation,
    pub visible_epoch: Epoch,
    pub durability_floor: CommitPosition,
    pin: Arc<SnapshotPin>,
}
```

The token is unforgeable outside storage/core. Dropping the last clone advances possible reclamation. A backend validates that all locators used with a token belong to its generation.

### Pinned bytes

`PinnedBuffer` owns an `Arc` to a cache/page/object slice and a budget charge. `EncodedArray` references only a `PinnedBuffer` or owned bytes. An eviction removes lookup reachability but cannot free bytes until pins drop. Raw borrowed slices never escape without an owner.

### Immutable metadata

Catalogs, group directories, manifests, and stats are immutable content-addressed values. Publication swaps one root. Mutable caches point to immutable values and may be rebuilt.

## Threading model

- CPU worker pool: fixed, database-wide by default, work-stealing with per-query fairness.
- I/O driver: a small backend-specific service produces completions; local synchronous reads may run on dedicated blocking I/O threads; object reads use the provider's async API.
- Writer broker: exactly one task serializes local logical commits; it does not perform expensive encoding while holding publication locks.
- Maintenance: low-priority tasks with explicit CPU/I/O/memory quotas.
- Result consumer: backpressure stops upstream pipelines when result buffers reach the configured bound.

The existing “fork a graph by reopening the file” mechanism is transitional. Target workers share snapshot directories and buffer cache; they do not independently duplicate catalog and decoded-group state.

## Compilation boundaries

1. Parser produces lossless syntax AST and diagnostics.
2. Semantic binder resolves names/labels/types against `CatalogSnapshot` and produces stable IDs.
3. Graph-normalization IR makes edge identity, path mode, match mode, null extension, and bag semantics explicit.
4. Logical optimizer performs equivalence-preserving rewrites.
5. Physical optimizer consults `StorageCapabilities`, stats, budgets, and remote-cost model.
6. Runtime executes `PhysicalPlan` with a fixed snapshot token.

Physical plans may contain backend leaf operators (`SqliteIndexRange`, `EncodedGroupScan`, `RemoteAdjacencyGather`) selected from declared capabilities. Backend-specific leaves terminate at typed batch outputs; engine details do not leak upward.

## Capability negotiation

Capabilities are immutable for an open engine except transient health/cost availability:

```rust
pub struct StorageCapabilities {
    pub snapshot: SnapshotCapabilities,
    pub scan: ScanCapabilities,
    pub adjacency: AdjacencyCapabilities,
    pub mutation: MutationCapabilities,
    pub io: IoCapabilities,
    pub limits: StorageLimits,
}
```

Examples: exact filter pushdown, ordered adjacency, edge-ID projection, typed PK lookup, batch ranges, SQL aggregation pushdown, remote request estimates, historical snapshots, DDL, and bulk atomicity. Unsupported operations are rejected during planning or lowered to a correct generic path. There is no optimistic call-and-fallback after partial query execution.

## State machines

Database lifecycle:

```text
Opening -> Recovering -> Ready
                      -> ReadOnlyDegraded
                      -> RecoveryRequired
Ready -> Fenced | BudgetThrottled | Closing -> Closed
Ready -> Corrupt (sticky; writes disabled)
```

Write transaction:

```text
Active -> Validating -> Prepared -> Durable -> Published -> Committed
   |          |            |          |           |
   +----------+------------+----------+-----------+-> Aborted/Unknown
```

`Unknown` is required for ambiguous remote outcomes. The client reconciles by transaction ID; it never blindly reapplies mutations.

## Extension points

Extensions register functions, logical rewrite rules, table/index providers, or file readers through versioned interfaces. They cannot allocate outside budgets, bypass snapshot tokens, introduce unversioned on-disk bytes, or call engine internals. Native extensions are disabled by default for untrusted databases; WASM or process isolation is future work.
