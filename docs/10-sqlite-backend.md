# SQLite backend

## Role

SQLite is a complete storage-engine implementation for portability and transactional embedding, not an import/export shim. It implements the common catalog, snapshot, scan, adjacency, lookup, mutation, and maintenance contracts while exploiting SQLite's native transactions and planner where semantics match.

The backend has no dependency on zu1. The query crate has no dependency on SQLite. All backend-specific lowering is selected through capabilities and a typed pushdown compiler.

## Physical schema

One database contains metadata tables plus user table families. Illustrative layout:

```sql
CREATE TABLE _zu_meta(key TEXT PRIMARY KEY, value BLOB NOT NULL) WITHOUT ROWID;
CREATE TABLE _zu_schema(version INTEGER NOT NULL, catalog BLOB NOT NULL, digest BLOB NOT NULL);

CREATE TABLE n_<table_id>(
  node_id INTEGER PRIMARY KEY,
  pk <TYPE> NOT NULL UNIQUE,
  begin_ts INTEGER NOT NULL,
  end_ts INTEGER NOT NULL,
  ... properties ...
);

CREATE TABLE e_<table_id>(
  edge_hi INTEGER NOT NULL,
  edge_lo INTEGER NOT NULL,
  src INTEGER NOT NULL,
  dst INTEGER NOT NULL,
  begin_ts INTEGER NOT NULL,
  end_ts INTEGER NOT NULL,
  ... properties ...,
  PRIMARY KEY(edge_hi, edge_lo)
) WITHOUT ROWID;
CREATE INDEX e_<id>_out ON e_<id>(src, dst, edge_hi, edge_lo);
CREATE INDEX e_<id>_in  ON e_<id>(dst, src, edge_hi, edge_lo);
```

Production DDL quotes generated identifiers defensively and derives them only from numeric stable IDs. Type mapping and collation are fixed in catalog metadata. User-provided names or expressions are never interpolated into SQL.

If historical MVCC is not enabled, tables may store only current versions and the capability matrix says so. If enabled, version history is represented explicitly or by history tables; SQLite's WAL snapshot alone is not advertised as arbitrary historical snapshot support.

## Connection model

Each database owns a bounded connection pool. A read snapshot pins one connection/read transaction for its lifetime. A write transaction owns a dedicated connection and uses `BEGIN IMMEDIATE` by default to make writer contention explicit. Busy handling respects query deadline/cancellation; it is not an unbounded sleep loop.

Pragmas are configured and reported, including journal mode, synchronous level, foreign keys, cache size, temp store, mmap policy, and busy timeout. Durability receipts reflect `synchronous` and filesystem assumptions. The backend never claims `Local` if configured in a mode that cannot meet it.

## Adjacency

For a batch of source IDs, the engine uses a temporary input table or an equivalent bounded set mechanism and executes one indexed join per relationship-table/direction group. Results return source position, neighbor ID, and full edge ID, ordered as requested.

Large batches are chunked below parameter/temporary-space budgets. The backend reports actual statements, rows, page-cache activity where observable, and temporary bytes. A loop issuing one query per source is a guarded tiny-input fallback and visible in the profile.

## Typed pushdown

The pushdown compiler accepts only the storage expression IR. It returns SQL plus bound parameters and a proof classification:

- exact: SQLite comparison, null, collation, overflow, and function behavior match the logical language;
- pruning-only: safe necessary condition; runtime evaluates the original predicate;
- unsupported: no pushdown.

Floating NaN, decimal scaling, timestamps/timezones, Unicode collation, integer overflow, pattern matching, and user functions require explicit conformance tests. Backend truthiness or implicit type coercion is not allowed to redefine query semantics.

Whole safe subplans may lower to SQL: scans, joins, projection, filters, grouping, ordering, and limit. The lowering boundary returns canonical batches and preserves bag semantics. `EXPLAIN` includes sanitized generated SQL and SQLite's plan in verbose mode.

## Mutations and IDs

Logical mutations execute inside one SQLite transaction. ID counters, node/edge rows, both adjacency indexes, property values, constraints, catalog version, and commit metadata commit atomically. Transaction ID and mutation digest are recorded in `_zu_commits` so retries reconcile to the original receipt.

User primary keys are independent of logical IDs. Deletes follow the catalog's edge policy. Native foreign keys may reinforce invariants, but portable pre-commit validation and conformance remain authoritative.

## Backup and migration

Online backup uses SQLite's supported backup mechanism or a documented consistent file procedure; copying the main file while WAL writes continue is prohibited. Import/export streams canonical batches with logical IDs and schema metadata. Migration is versioned, transactional where SQLite allows it, resumable for table rewrites, and leaves a recovery record.

## Limits and security

The backend sets and tests limits for SQL length, variables, expression depth, attached databases, result size, and temp storage. It disables extension loading unless explicitly enabled. Paths, URI parameters, and pragmas are validated. Cancellation interrupts the active statement and cleans temporary tables before returning the pooled connection.

## Conformance and performance gates

- all common storage conformance tests run against file and memory databases;
- parallel edge identity and self-loop multiplicity match the reference engine;
- randomized logical plans compare native pushdown on/off;
- kill/reopen tests cover every mutation and migration phase;
- busy, disk-full, corrupt, read-only, and cancelled cases map to stable errors;
- batched adjacency demonstrates bounded statement count as source cardinality rises;
- durable configurations document and measure commit latency without weakening defaults invisibly.
