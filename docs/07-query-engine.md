# Query engine specification

## Scope

The query layer owns parsing, semantic analysis, logical planning, optimization, physical lowering, vectorized execution, and result streaming. It does not open zu1 files, issue SQLite statements, or construct object keys. All data access goes through the storage/query SPI.

The v1 language is the documented read subset plus explicit transactional DML only when its storage path is complete. Unsupported syntax fails during analysis with a stable feature code. It must never parse successfully and then silently weaken graph semantics.

## Pipeline

```text
text -> CST -> typed AST -> bound logical graph plan
     -> normalized IR -> memo/optimizer -> backend-aware physical plan
     -> bounded batch pipeline -> result stream + profile
```

Each boundary is serializable for tests. The bound plan records catalog lineage/version, table and column IDs, parameter types, nullability, uniqueness, and ordering. Cached plans rebind or fail on incompatible schema change.

## Logical algebra

Required operators include:

- `NodeScan`, `EdgeScan`, `Expand`, `ExpandInto`, `PathExpand`;
- `Filter`, `Project`, `Unwind`, `Distinct`, `Sort`, `TopK`, `Limit`;
- `HashJoin`, `MergeJoin`, `IndexJoin`, `IntersectJoin`, `OptionalJoin`;
- `Aggregate`, `Window` when supported by grammar;
- `Create`, `Update`, `Delete`, `Merge` only behind completed mutation capabilities.

Logical `Expand` carries direction, edge types, endpoint predicates, path mode (`walk`, `trail`, `simple`), length bounds, and whether edge identity is bound. Multiplicity is part of the operator contract, not an optimizer accident.

## Cardinality and cost model

Statistics are versioned catalog objects:

- exact row/edge counts per table and group;
- degree count, mean, variance, max, and equi-depth/log histograms;
- heavy hitters and joint endpoint-label counts;
- null fraction, min/max, distinct estimates and selected multi-column sketches;
- storage locality: bytes, groups, object ranges, compression, cache residency class;
- confidence, sample rate, generation, and staleness.

The estimator returns `(low, expected, high, confidence)`, not a misleading scalar. Pessimistic bounds and degree-sequence bounds guide memory admission and catastrophic-plan avoidance; expected cost selects among acceptable plans. Feedback is keyed by normalized plan and snapshot/statistics generation, bounded in influence, and never changes semantics.

Cost has separate dimensions:

```text
cpu_units, decoded_bytes, peak_memory,
local_io_bytes + seeks,
remote_requests + remote_bytes,
spill_bytes, startup_latency
```

Profiles calibrate weights. A single number may rank candidates within one profile, but EXPLAIN exposes the vector and estimates. Object-store request cost cannot be hidden inside a nominal byte count.

## Join and traversal strategy

The optimizer must consider both binary and multiway plans:

- adjacency expansion for selective bound endpoints;
- scan/hash join for broad edge access;
- ordered intersection or worst-case-optimal join for cyclic motifs;
- semijoin/bitmap reduction before expensive fact scans;
- factorized intermediate batches where repeated prefixes would explode;
- robust recursive scheduling for variable-length paths.

The recent research direction is convergence, not one universal algorithm: worst-case-optimal and binary joins can share infrastructure; robust recursive execution reduces dependence on perfect path cardinalities; factorization should be adaptive. These features enter behind plan-rule flags and differential tests.

## Physical operators

Operators consume and produce `DataBatch`. They implement:

```rust
trait Operator {
    fn open(&mut self, cx: &mut ExecContext) -> Result<()>;
    fn poll_next(&mut self, cx: &mut ExecContext)
        -> Poll<Result<Option<DataBatch>>>;
    fn close(&mut self, cx: &mut ExecContext);
}
```

Every operator declares its memory behavior (`streaming`, `bounded_state`, `blocking`, `spillable`), preserved ordering, multiplicity, and cancellation granularity. Blocking operators reserve memory before building. Failure to reserve triggers an alternative/spill or `BudgetExceeded`; it never relies on allocator OOM.

Expression kernels accept flat, constant, dictionary, FOR/bit-packed, and selected structural encodings. Unsupported combinations explicitly materialize through a budgeted adapter. Selection vectors are preferred over copying. Null semantics are defined once in the typed expression layer.

## Backpressure and cancellation

The result consumer drives demand. At most the configured number of batches may be queued per pipeline edge. Remote sources have request and byte semaphores; cancellation stops new work, attempts provider cancellation, discards late results, and releases all reservations/pins.

The executor checks deadline/cancellation at least once per batch and inside long graph loops. A client that stops reading cannot leave a producer, SQLite statement, range request, spill file, or pinned snapshot live indefinitely.

## Variable-length paths

Path execution has explicit guards:

- length bounds are mandatory for object-store profiles unless an administrator enables bounded-runtime search;
- maximum frontier entries, path states, result rows, bytes, and wall time are enforced;
- visited edge/node state uses stable IDs;
- breadth/depth/bidirectional strategy is costed from degree bounds and endpoint selectivity;
- frontier expansion is batched and deduplicated only where path semantics permit;
- optional recursive morsel stealing may rebalance skew without changing deterministic results.

Spilled frontier state is checksummed and query-scoped. Unbounded enumeration is rejected at admission when no safe envelope is available.

## SQLite lowering

The SQLite backend may return a native statement source for scans, joins, filters, or aggregates it can exactly implement. Lowering uses bound identifiers and parameters, never string substitution. A pushed fragment returns its exact output schema, ordering, null/multiplicity proof, and residual predicate.

Graph-specific lowering batches source IDs into a temporary/virtual table and joins an indexed edge table once. Per-source SQL queries are prohibited in a physical plan except for a proven tiny cardinality under a configured threshold.

## Object-store lowering

Plans group adjacency sources by tile/object, coalesce allowed byte ranges, and schedule bounded concurrent reads. A cold-plan estimate includes metadata fetches and range request count. If projected requests or bytes exceed the read envelope, optimization must choose a scan/coarser tile or reject before execution.

## DML execution

DML produces a logical mutation batch. The executor performs expression evaluation and eager local validation; the storage mutation service performs authoritative validation and publication. `RETURNING` rows are released only at the promised durability/publication point. A failed multi-row statement has no partial effect.

## Determinism and observability

Without `ORDER BY`, row order is unspecified but multiplicity is exact. With order, ties follow documented expressions and a stable ID tie-breaker when pagination tokens require repeatability.

`EXPLAIN` reports logical/physical plans, pushdown classification, capability assumptions, estimated ranges, remote request/byte estimates, and admission decision. `PROFILE` adds actual rows, batches, time, CPU, waits, peak memory, decoded/read bytes, cache tiers, spills, and source requests. Secrets and property values are redacted by default.

## Correctness gates

- differential query generation compares zu1, SQLite, and an in-memory reference at the same logical snapshot;
- parallel edges, nulls, empty adjacency, self-loops, cycles, disconnected patterns, and skew are mandatory corpora;
- every rewrite has equivalence/property tests including bag semantics;
- fault injection proves cancellation releases memory, pins, statements, and I/O;
- optimizer fuzzing validates every chosen plan against the interpreter;
- cold and warm object-store request counts are regression metrics, not anecdotes.
