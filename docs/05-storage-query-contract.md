# Storage/query service interface

## Why a service interface

The storage boundary must preserve graph semantics while allowing radically different access costs. A local encoded group can be read in microseconds; SQLite may answer best with a native indexed SQL query; object storage needs batched ranges and async completion. A trait returning one `SegmentRef` or neighbor list cannot express these choices.

The SPI is split by responsibility so reads, mutations, and maintenance cannot accidentally share locks or acknowledgement semantics.

## Core interfaces

```rust
pub trait StorageEngine: Send + Sync + 'static {
    fn capabilities(&self) -> &StorageCapabilities;
    fn catalog_service(&self) -> &dyn CatalogService;
    fn snapshots(&self) -> &dyn SnapshotService;
    fn mutations(&self) -> &dyn MutationService;
    fn maintenance(&self) -> &dyn MaintenanceService;
}

pub trait SnapshotService: Send + Sync {
    fn latest(&self, opts: SnapshotOptions) -> BoxFuture<Result<SnapshotHandle>>;
    fn at(&self, selector: SnapshotSelector) -> BoxFuture<Result<SnapshotHandle>>;
}

pub trait SnapshotReader: Send + Sync {
    fn token(&self) -> &SnapshotToken;
    fn plan_scan(&self, request: ScanRequest) -> Result<Box<dyn BatchSource>>;
    fn plan_adjacency(&self, request: AdjacencyRequest)
        -> Result<Box<dyn AdjacencySource>>;
    fn lookup(&self, request: LookupRequest) -> BoxFuture<Result<LookupBatch>>;
}
```

`SnapshotHandle` contains an `Arc<dyn SnapshotReader>`, the exact `CatalogSnapshot`, and backend accounting context. It is acquired once per read transaction/query, not once per operator.

## Batch source contract

```rust
pub trait BatchSource: Send {
    fn schema(&self) -> &BatchSchema;
    fn next(&mut self, cx: &mut SourceContext)
        -> Poll<Result<Option<DataBatch>>>;
    fn cancel(&mut self);
}
```

The poll-shaped internal interface avoids selecting a public async runtime. `SourceContext` contains deadline, cancellation, memory reservation, I/O submitter, request/byte budget, and profile sink. A synchronous local source may return `Ready` immediately; a remote source schedules vectored reads and returns `Pending`.

`DataBatch` is 1–8192 rows (default target 2048) and owns/pins:

- schema and row selection;
- canonical arrays (`Flat`, `Constant`, `Dictionary`, `FOR`, `List`, etc.);
- optional row/element IDs;
- nullability bitmap;
- ordering and factorization metadata;
- budget reservation released on drop.

The runtime may compute directly on supported compressed arrays. Canonicalization to flat vectors is explicit and budgeted.

## Scan request

```rust
pub struct ScanRequest {
    pub table: TableId,
    pub snapshot: SnapshotToken,
    pub projection: Vec<ColumnId>,
    pub filter: StorageExpr,
    pub order: RequiredOrder,
    pub row_id: RowIdProjection,
    pub partitioning: SplitPreference,
    pub limit_hint: Option<u64>,
    pub budget: ReadEnvelope,
}
```

Rules:

- `StorageExpr` is a small typed, versioned expression language; it does not embed query-engine AST nodes.
- The engine returns a `PushdownReport` marking each conjunct `Exact`, `PruningOnly`, or `Unsupported`.
- `PruningOnly` never authorizes dropping the runtime filter.
- Projection includes filter-only fields but allows the source to discard them before output.
- Splits are independently executable and carry deterministic IDs for replay/profiling.
- `limit_hint` is not semantically binding unless the engine proves order/filter equivalence.

This follows the useful N×M separation in Vortex's evolving scan API: a request describes filter/projection, a source returns independent splits, and pruning is distinguished from exact evaluation.

## Adjacency request

```rust
pub struct AdjacencyRequest {
    pub edge_types: SmallVec<[RelTableId; 4]>,
    pub direction: Direction,
    pub sources: IdBatch<NodeId>,
    pub neighbor_labels: LabelPredicate,
    pub edge_filter: StorageExpr,
    pub projection: AdjacencyProjection,
    pub order: AdjacencyOrder,
    pub mode: AdjacencyMode,
    pub budget: ReadEnvelope,
}

pub struct AdjacencyProjection {
    pub neighbor_id: bool,
    pub edge_id: bool,
    pub edge_columns: Vec<ColumnId>,
    pub neighbor_columns: Vec<ColumnId>,
}
```

An `AdjacencyBatch` is list-structured: source IDs, offsets, neighbor IDs, edge IDs, and projected property arrays. Sources may be reordered internally only if a source-position map is returned. Empty lists are represented, not dropped.

Modes:

- `Enumerate`: exact edges with identity; required for relationship binding and path semantics.
- `DegreeOnly`: exact visible degree after filters; no neighbor values.
- `ExistencePairs`: many `(src,dst)` probes returning count or edge IDs, not only boolean.
- `Intersect`: optional backend WCOJ primitive over ordered lists, with exact identity/multiplicity rules.
- `Prefetch`: materialize/pin predicted tiles without returning rows.

The minimum useful batch is many source nodes. The physical planner MUST NOT lower a remote expansion to repeated single-source requests.

## Lookup request

Lookup supports typed keys and IDs:

```rust
pub enum LookupKeyBatch {
    Primary { table: TableId, values: Array },
    NodeIds(IdBatch<NodeId>),
    EdgeIds(IdBatch<EdgeId>),
}
```

Results preserve input order and include an explicit found bitmap. Dense fallback MUST range-check against visibility; it cannot return `Some(key)` merely because no index exists.

## Mutation interface

```rust
pub trait MutationService: Send + Sync {
    fn prepare(&self, base: &SnapshotToken, txn: TxnId,
               mutations: LogicalMutationBatch,
               ctx: &CommitContext) -> BoxFuture<Result<PreparedCommit>>;
    fn make_durable(&self, prepared: PreparedCommit,
                    level: DurabilityLevel,
                    ctx: &CommitContext) -> BoxFuture<Result<DurableCommit>>;
    fn publish(&self, durable: DurableCommit,
               ctx: &CommitContext) -> BoxFuture<Result<CommitReceipt>>;
    fn reconcile(&self, key: CommitKey) -> BoxFuture<Result<CommitStatus>>;
}
```

The split phases make remote ambiguity and local publication explicit. Backends may fuse phases but must emit the same state transitions. `PreparedCommit` is single-use and carries base generation, mutation digest, reserved IDs, and validation proof. Retrying uses `TxnId` and digest; changing payload under the same ID is conflict/corruption.

Logical mutations include typed node/edge insert, property update, label membership change, delete, and DDL. They contain logical IDs and primary keys, never block pointers or CSR slots.

## Maintenance interface

Checkpoint, compaction, analyze, verify, vacuum, GC, and export are jobs:

```rust
pub trait MaintenanceService {
    fn submit(&self, job: MaintenanceJob,
              budget: MaintenanceBudget) -> Result<JobHandle>;
}
```

Jobs have progress, cancellation, resumability, generated artifacts, and publication phase. `verify` is read-only. `repair` is a distinct, explicit operation that writes a new root and preserves evidence.

## Capability examples

| Capability | zu1 | SQLite | object-single |
|---|---:|---:|---:|
| ordered exact adjacency with edge IDs | required | via indexed SQL | required when canonical tile cached/fetched |
| exact scalar predicate pushdown | selected encoded kernels | broad SQL subset | selected encoded kernels |
| async vectored ranges | local gather | no; statement source | required |
| historical snapshot by generation | pinned local epochs, bounded | optional SQLite snapshot support | immutable roots |
| native aggregate pushdown | limited metadata counts | selected safe SQL | limited metadata counts |
| DDL | yes | yes | single-partition only |
| cross-partition transaction | n/a | n/a | false |

## Error contract

Errors are structured and stable:

- `Corrupt { object, range, expected, actual }`
- `Unsupported { capability, backend, alternative }`
- `Conflict { kind, current_generation }`
- `Fenced { expected_epoch, current_epoch }`
- `AmbiguousCommit { key }`
- `BudgetExceeded { resource, requested, remaining }`
- `Cancelled`, `DeadlineExceeded`
- `SnapshotExpired`, `SnapshotMismatch`
- `ConstraintViolation { constraint, element }`
- `Io { class, retryability, source }`

No backend error string is the semantic API. Provider/SQLite/OS errors are retained as sources and mapped deterministically.

## Conformance kit

Every engine implementation runs the same suite for:

- empty and multi-table catalogs;
- typed PK hits/misses and duplicates;
- multi-edge/self-loop adjacency both directions;
- filters/nulls/projections and order;
- snapshot stability across commits;
- cancellation and budget exhaustion;
- idempotent commit/reconcile;
- constraint failure atomicity;
- export to canonical batches and reimport parity.
