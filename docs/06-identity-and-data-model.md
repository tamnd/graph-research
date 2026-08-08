# Identity and data model

## Decision

Element identity is logical, immutable, snapshot-independent, and distinct from physical position. A CSR offset, row number, SQLite `rowid`, object key, or encoded-array slot is never a public node or edge identity.

This corrects the current executor, which represents a relationship as `(table, src, dst)`. That representation cannot distinguish parallel edges and therefore gives incorrect trail semantics, deletes, property lookup, and cardinality whenever two edges share endpoints.

## Identifier layout

The portable logical forms are:

```rust
#[repr(transparent)]
pub struct NodeId(u64);

#[repr(transparent)]
pub struct EdgeId(u128);

pub struct ElementRef {
    pub kind: ElementKind,
    pub table: TableId,
    pub id: ElementId,
}
```

`NodeId` is a 64-bit database-lineage-local value in v1. `EdgeId` is 128-bit because object-store partitions must allocate concurrently without coordinating every insert. Neither exposes bit fields through the public API. A backend may internally use a compact 64-bit edge ID only when import/export and uniqueness are lossless.

Recommended allocation:

- local zu1 and SQLite: monotonic 64-bit sequence persisted in commit metadata; widen edge IDs to 128 bits at the boundary;
- object store: `writer_epoch:32 | writer_id:32 | counter:64`, encoded big-endian for stable ordering;
- imported user IDs remain properties or primary keys unless an explicit preserve-ID import validates the namespace;
- IDs are never reused, including after abort, deletion, vacuum, or restore.

Constructors are checked in every build. `try_from_raw`, `try_from_parts`, and deserialization reject reserved values and overflow. `new_unchecked` is crate-private and documents its proof obligation. Debug assertions are not validation.

## Table and schema identity

Names are mutable catalog attributes; IDs are immutable:

```text
CatalogId       u128, unique database lineage
SchemaVersion   u64, monotonically published
TableId         u32, never reused within lineage
ColumnId        u32, never reused within table
ConstraintId    u64
IndexId         u64
```

A rename changes only the name mapping. Dropping and recreating `Person` creates a new `TableId`. Plans embed catalog lineage, schema version, and stable IDs, then revalidate name-dependent assumptions before execution.

## Edge semantics

An edge record contains:

```rust
pub struct EdgeHeader {
    pub id: EdgeId,
    pub table: RelTableId,
    pub src: NodeId,
    pub dst: NodeId,
    pub begin: CommitTs,
    pub end: CommitTs, // infinity until deleted
}
```

For undirected syntax, storage still chooses a canonical endpoint ordering and preserves the logical edge once. Directional expansion produces the appropriate orientation without duplicating identity. Self-loops appear once per logical expansion unless the language construct explicitly has two endpoint roles.

Parallel edges are first-class. Existence probes return a count or IDs; boolean results are only valid when the consumer explicitly requests existential semantics. Trail uniqueness uses `EdgeId`; simple-path uniqueness uses `NodeId`; walk semantics use neither visited set.

## Physical locators

Physical locators are hints scoped to one immutable root:

```rust
pub struct PhysicalLocator {
    pub root: RootId,
    pub object: ObjectId,
    pub group: u32,
    pub ordinal: u32,
}
```

They may be cached beside an ID, but lookup must fall back through an ID index when the root changes. Compaction is free to rewrite every locator. No WAL entry, query value, foreign key, or client-visible token may rely on one after its root is unpinned.

## Logical schema

Node tables define a primary key and zero or more labels. Relationship tables define allowed source/destination table sets, directionality, and property columns. The minimum portable type system is:

- `Bool`, signed/unsigned integers, `Float32/64`, `Decimal128(scale)`;
- UTF-8 string and binary;
- date, time, timestamp with explicit unit and timezone semantics, duration;
- list and struct with bounded nesting;
- `NodeId` and `EdgeId` as non-arithmetic internal types.

Null and absent are distinct in schema evolution. A nullable column has a validity bitmap. A column absent from an older segment evaluates to its schema-version default; a stored null remains null. Defaults must be deterministic and side-effect-free to support replay.

## Constraints

The catalog represents, and commit validation enforces:

- node primary-key uniqueness;
- optional unique and non-null constraints;
- relationship endpoint existence in the same commit snapshot plus the transaction's writes;
- source/destination table admissibility;
- optional relationship uniqueness on declared endpoint/property keys;
- delete policy: `RESTRICT`, `CASCADE`, or `DETACH`.

Validation operates over the complete write set. It cannot publish the forward edge without the reverse edge, or a relationship without both visible endpoints. Constraint indexes are part of the commit unit; asynchronous index maintenance is allowed only for non-constraint indexes.

## Snapshot visibility

For snapshot timestamp `S`, an element version is visible iff `begin <= S < end`. A transaction sees its own writes over that snapshot. Update creates a new version; delete closes the old interval. Physical encodings may replace intervals with base-plus-delta structures, but must produce identical results.

Every `DataBatch` that can bind graph elements carries logical IDs. Property lookup uses those IDs at the same `SnapshotToken`; mixing batches or tokens is a `SnapshotMismatch`, never a best-effort lookup.

## Adjacency invariants

For every committed directed edge `e=(id, table, src, dst)`:

1. Enumerating `OUT(src, table)` yields exactly one entry with `(dst, id)`.
2. Enumerating `IN(dst, table)` yields exactly one entry with `(src, id)`.
3. Both entries resolve to the same property version.
4. The two entries become visible and invisible in the same published commit.
5. Sorting is deterministic by `(neighbor_id, edge_id)` unless the request states another order.

These invariants are checked at prepare time for deltas and by offline verification for sealed structures.

## Evolution and interchange

Schema changes publish a new immutable schema version. Readers bind by stable column ID and use adapters for widening conversions. Destructive or narrowing conversions require a rewrite job and cannot reinterpret bytes in place.

Canonical export includes catalog lineage, stable schema IDs, logical element IDs, commit timestamp, and format version. A backup restore preserves IDs and lineage; a logical copy intentionally creates new lineage and records an ID mapping.

## Required tests

- two, ten, and 100 parallel edges between identical endpoints retain distinct bindings;
- self-loop expansion has specified multiplicity in inbound, outbound, and both modes;
- compaction changes all physical positions without changing IDs or query results;
- abort burns allocated IDs and retry with the same transaction remains idempotent;
- rename/drop/recreate cannot bind a stale plan to the new table;
- boundary values and malformed binary IDs fail identically in debug and release;
- forward/reverse/property indexes agree after crash recovery at every injected write point.
