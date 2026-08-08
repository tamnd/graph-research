# Transactions, durability, and recovery

## Public contract

The default isolation level is snapshot isolation with explicit write-write conflict detection. A transaction reads one immutable `SnapshotToken` plus its own writes. Serializable isolation is future work unless predicate/range conflicts are implemented and tested; documentation must not imply it.

```rust
pub trait Transaction {
    fn snapshot(&self) -> &SnapshotToken;
    fn query(&mut self, query: BoundQuery) -> Result<ResultStream>;
    fn mutate(&mut self, batch: LogicalMutationBatch) -> Result<()>;
    fn commit(self, level: DurabilityLevel) -> Result<CommitReceipt>;
    fn rollback(self) -> Result<()>;
}
```

A connection may own only one active write transaction. Read transactions are independent snapshot handles. Dropping an uncommitted write transaction rolls it back; it never commits implicitly.

## Commit timestamps and conflicts

`CommitTs` is a monotonically published 64-bit sequence within one database lineage. It is not wall-clock time. The commit coordinator assigns it after validating the base snapshot and before writing the durable commit record.

Conflict detection covers:

- the same logical element version written after the base snapshot;
- uniqueness/index keys introduced or removed after the base snapshot;
- schema objects changed since binding;
- endpoint deletes conflicting with new edges;
- compare-and-set catalog/root generation.

Snapshot isolation permits write skew across disjoint keys. APIs label this behavior. Operations requiring stronger invariants use a catalog-defined validation key or wait for serializable support.

## Durability levels

| Level | Acknowledgement condition | Crash expectation |
|---|---|---|
| `Memory` | transaction published in process | may be lost on process failure |
| `Local` | WAL and commit marker synced to configured local device | survives process/OS restart subject to device contract |
| `RemoteLog` | immutable WAL exists and fenced authoritative metadata commits its digest/high-water mark | survives loss of local cache; readers may merge committed log |
| `Published` | selected data/root representation covers the commit | readable without an uncovered transaction-log tail |
| `Replicated(n)` | durable receipt from a separately qualified quorum/service | depends on its declared failure model; post-v1 unless implemented |

The receipt states the achieved level, commit timestamp, root generation, transaction ID, mutation digest, writer epoch, and backend evidence. The API never returns a stronger enum than actually achieved.

## Local WAL format

The WAL is a sequence of framed records:

```text
magic | version | type | flags | header_len | payload_len
txn_id | sequence | base_ts | payload_digest | header_crc
payload | payload_crc | frame_len_copy
```

Record types include `Begin`, logical/physical mutation chunks, `Prepare`, `Commit`, `Abort`, `Checkpoint`, and `RootPublish`. Maximum sizes are bounded before allocation. Unknown required versions fail closed; optional fields use a length-delimited extension area.

One transaction's payload may span frames. `Commit` contains the digest of the ordered mutation frames, assigned commit timestamp, and resulting catalog/root digest. A torn or corrupt tail is truncated only after the last fully verified frame. Corruption in an acknowledged committed prefix is a hard error, not treated as an ordinary tail.

## Local commit protocol

For `Local` durability:

1. Freeze the logical write set and compute its digest.
2. Under commit serialization, validate conflicts and constraints against current published state.
3. Reserve IDs and assign `CommitTs`.
4. Append mutation and `Commit` frames.
5. Sync WAL according to the configured device policy.
6. Apply/publish the in-memory delta root with a release barrier.
7. Return a receipt.

Readers acquiring a snapshot after step 6 see the commit; earlier snapshots do not. If step 5 succeeds and the process dies before step 6, recovery publishes the committed record. If step 5 fails, no success is returned.

Group commit may combine steps 4–5, but each receipt remains tied to its own verified commit record. An explicit maximum delay and byte threshold bound latency.

## Overlay and checkpoint

Committed WAL-backed deltas are immediately queryable. The canonical reader merges:

```text
immutable checkpoint root + committed delta layers <= snapshot + txn-local writes
```

The query facade cannot bypass the overlay by opening a sealed `Zu1File` directly. Delta indexes cover ID/PK lookup, property versions, tombstones, and both adjacency directions including edge IDs.

Checkpoint builds a new immutable root without blocking readers, verifies it, then publishes a small atomic root record. Only after the root is durable and no pinned snapshot needs older state may WAL prefixes and old roots be reclaimed.

## Recovery state machine

On open:

1. Select the newest valid root record by generation and checksum; never just the newest bytes.
2. Load bounded root metadata and catalog.
3. Scan WAL from the root's replay position, validating every frame and transaction digest.
4. Redo committed transactions not incorporated in the root; discard incomplete/aborted transactions.
5. Reconstruct indexes, next-ID counters, commit clock, and delta root.
6. Run invariant checks before accepting writers.

Recovery is idempotent. Reopening after a crash during recovery produces the same state. Normal open time is proportional to post-checkpoint WAL, with a configured threshold that can force read-only open or recovery checkpoint rather than unbounded surprise.

## Ambiguous commits

Timeout or transport failure after durable submission yields `AmbiguousCommit { key }`. The client calls `reconcile(key)`; blindly retrying with a new transaction can duplicate effects. Retrying the same `(TxnId, mutation_digest)` returns the original result. The same `TxnId` with another digest is rejected.

## Object-store transaction protocol

Single-partition object commits use immutable objects plus a fenced manifest. Updating that manifest with an advanced committed WAL high-water mark achieves `RemoteLog`; advancing its materialized-through position after validated packs achieves `Published`:

1. Acquire/renew a writer lease and monotonically increasing writer epoch from the configured coordinator.
2. Write immutable WAL/data objects under content-addressed or transaction-scoped keys.
3. Verify object length/checksum through provider response or read-back policy.
4. Conditional-write the partition manifest from generation `g` to `g+1`, including writer epoch, commit digest, immutable object references, and WAL high-water mark.
5. Re-read or otherwise verify the winning manifest before acknowledging `RemoteLog` or `Published`, as applicable.

Every publication checks the writer epoch. A stale writer cannot acknowledge merely because it uploaded an object. S3 conditional writes serialize one manifest key but do not create a cross-key transaction; the protocol derives atomic visibility solely from the final manifest reference.

Multi-partition atomic transactions are out of scope for v1. A cross-partition operation must be rejected, explicitly executed as a saga with visible partial-state semantics, or delegated to an external transactional coordinator. Forward and reverse adjacency for one edge therefore live in the same atomic partition unit or are published by a protocol that proves their joint visibility.

## Backup and restore

A backup captures one pinned immutable root, all referenced objects, catalog lineage, and a manifest with sizes and cryptographic digests. Completion means every referenced object has been verified. Restore writes a new unpublished root, verifies it, then atomically installs it. Point-in-time restore replays only complete commits through a specified `CommitTs`.

## Fault-injection matrix

Tests terminate or fail I/O:

- before/after every WAL append, sync, root write, rename/manifest CAS, and acknowledgement;
- on short writes, torn sectors, stale reads, duplicate delivery, timeout, throttling, and checksum mismatch;
- with concurrent checkpoint, compaction, readers, and writers;
- while allocating IDs and updating uniqueness/adjacency indexes;
- during lease expiry and stale-writer continuation.

For each point, the allowed outcome is precisely old state or new committed state; never half an edge, orphan properties, duplicate commit, a visible uncommitted row, or acknowledgement followed by loss under the selected durability model.
