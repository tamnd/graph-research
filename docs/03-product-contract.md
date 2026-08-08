# Product contract and system invariants

## Product thesis

zu is an embedded property-graph query engine with portable local storage and an optional object-native read-mostly profile. Its differentiator is not merely “three engines”; it is predictable semantics and query plans across storage with deliberate capability specialization.

The local `zu1` profile competes on mixed traversal/analytics latency and small deployment footprint. SQLite competes on interop and trusted small-write durability, not analytical parity. Object storage competes on capacity and stateless read scale, not local latency or unrestricted transactions.

## Supported consistency contract

### Local profiles

- One write transaction at a time per `Database` instance.
- Read-only transactions use snapshot isolation and may span statements.
- Write transactions are serialized by begin/commit order and read their own staged writes.
- DDL and DML are atomic within the same write transaction unless an operation is explicitly documented as offline bulk build.
- Connections in the same process share one transaction manager. Opening the same local file through two independent `Database` objects in write mode MUST fail through an OS-level exclusive writer lock.
- Read-only independent processes MAY open a committed root. They do not see in-process uncheckpointed overlay commits unless the WAL-tail reader protocol is explicitly enabled and qualified.

“Serializable” MUST be used only after tests/model prove the actual isolation contract. A single writer removes write/write anomalies but does not alone make an arbitrary read-then-write API serializable if read snapshots or predicate validation are wrong.

### Object-single profile

- One fenced writer per namespace; many readers.
- A strong read names a published log-tail/root generation and includes all commits through it.
- A bounded-stale read names its observed generation and maximum polling interval.
- Read-your-writes is provided by a commit receipt containing `txn_id`, `writer_epoch`, `log_seq`, and digest; a subsequent read waits until its snapshot covers that receipt.
- The system does not promise low-latency strong reads during object-store unavailability.

### Partitioned profile

- A query returns a `SnapshotVector` of `(partition_id, generation)`.
- It is not a globally atomic time unless a future coordinator certifies it.
- Strict queries MUST reject cross-partition reverse-index reads that are behind their canonical edge generation.
- Cross-partition write transactions are unsupported in v1.

## Durability levels

Every commit API accepts or inherits one level and returns it in the receipt:

| Level | `zu1` | SQLite | Object storage |
|---|---|---|---|
| `Memory` | overlay only; process loss loses it | transaction not committed | memory batch only |
| `Local` | WAL commit synced to qualified local device | SQLite commit at configured sync | local spill synced; node loss may lose it |
| `RemoteLog` | not applicable | not applicable | WAL object and authoritative tail committed |
| `Published` | same as Local; overlay visible in process | same as SQLite commit | root/manifest generation includes transaction |

Default is `Local` for local profiles and `RemoteLog` for object-single. `Memory` and object `Local` require an explicit unsafe/relaxed configuration name; they must never be described as durable.

## Failure model

Supported failures:

- process crash or kill at any instrumented syscall boundary;
- torn/short local file or WAL write within the qualified filesystem/device assumptions;
- reordered completion of independent object-store requests;
- object request retry, duplicate, timeout-after-success, 412 conflict, and bounded unavailability;
- stale writer continuing after takeover;
- cache loss at any point;
- corruption detected by checksum/digest;
- cancellation, memory exhaustion, disk-full, and budget exhaustion.

Not automatically tolerated in v1:

- malicious storage rewriting both data and digests without encryption/authentication;
- loss of the only local device;
- object store violating documented single-key atomicity/conditional-write semantics;
- atomic mutation spanning object partitions;
- arbitrary filesystem/network filesystems not in the qualification matrix;
- Byzantine writer credentials.

## Data correctness invariants

1. `NodeId` and `EdgeId` are never reused within a database UUID.
2. User primary keys are unique among visible nodes in a table at a snapshot.
3. An edge's source, destination, type, and `EdgeId` are immutable; changing endpoints is delete+insert.
4. A visible edge has visible endpoints unless the query explicitly opens a relaxed/import-repair snapshot.
5. Forward and backward local adjacency indexes contain the same visible `EdgeId` set.
6. Relationship properties resolve by `EdgeId`, never solely by endpoints or CSR slot.
7. Every operator obeys bag semantics unless the language requests set semantics. Storage must not deduplicate parallel edges.
8. Null, absent property, and type error are distinct according to the language rules.
9. A snapshot's catalog and values are from the same commit lineage.
10. Export/import preserves logical IDs when requested, or emits an explicit old→new ID mapping.

## Operational invariants

- Maintenance is cancellable and budgeted.
- Checkpoint/compaction never blocks readers on data I/O; publication may briefly serialize with commit.
- Disk/object GC is reachability-based with snapshot/checkpoint pins and a grace period. Time alone is never proof of safety.
- A health endpoint distinguishes ready, read-only degraded, recovery required, fenced, budget-throttled, and corrupt.
- Metrics are bounded-cardinality. Query text/keys/properties are not logged by default.
- Secrets never enter manifests, WAL payload diagnostics, tracing fields, or error strings.

## Non-goals for v1

- multi-writer distributed transactions or Raft;
- a globally consistent PB graph;
- arbitrary schema-less values;
- online stable-ID-preserving physical repartition across object partitions;
- graph-shaped vector indexes traversed directly from cold object storage;
- every optional GQL feature;
- automatic repair of undetected corruption;
- general server product, authentication system, or tenant control plane.

## Capacity policy

Format bit widths are not supported capacities. Each profile has qualification ceilings:

| Dimension | v1 default policy |
|---|---:|
| tables/database | 16,384 format maximum; 4,096 qualified |
| labels/database | semantic `u32`; 65,536 qualified |
| nodes/table local | 2^39 format target; qualify at tested dataset sizes |
| edges/table local | `u64`; no `usize`-dependent on-disk count |
| value/chunk | 16 MiB default maximum; continuation required above |
| transaction | 256 MiB logical default and 1 M mutations, whichever first |
| query path enumeration | explicit result/visited/PMR budgets |
| object pack | 8–64 MiB target, ≤128 MiB hard v1 limit |

Every conversion from on-disk `u64` to `usize` MUST check platform and budget before allocation.

## API-level contract

The primary API is synchronous at the call boundary for embedded users, but internally supports asynchronous I/O sources. Blocking methods accept a deadline/cancellation token through options; convenience methods use configured defaults.

```rust
let db = Database::open(uri, OpenOptions::default())?;
let conn = db.connect()?;
let read = conn.begin_read(ReadOptions::latest())?;
let stmt = read.prepare("MATCH ...")?;
let mut rows = stmt.query(params, QueryOptions::default())?;
while let Some(batch) = rows.next_batch()? { /* borrowed until next call */ }
```

`Database` is `Send + Sync`; `Connection` is `Send` but not concurrently used; `ReadTxn` and `WriteTxn` are neither implicitly cloned nor detached. Result buffers have explicit ownership lifetimes and may be copied into Arrow.
