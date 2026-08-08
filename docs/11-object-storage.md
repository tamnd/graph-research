# Object-storage architecture

## Supported profile and consistency boundary

The first remote profile is `object-single`: one writer for one partition epoch, many readers, immutable data objects, and one atomically replaced manifest per partition. It does not promise multi-partition atomicity, linearizable arbitrary object updates, or local-device latency.

An S3-compatible provider must offer read-after-write for new objects and conditional update on the manifest key with a stable entity tag/version. The implementation probes required capabilities and refuses writable mode when semantics are unknown. Provider-specific behavior is isolated behind the `object_store`-style async abstraction.

## Namespace

```text
db/<catalog-id>/catalog/<digest>
db/<catalog-id>/part/<partition-id>/manifest/<generation>-<digest>
db/<catalog-id>/part/<partition-id>/CURRENT
db/<catalog-id>/wal/<writer-epoch>/<txn-id>/<digest>
db/<catalog-id>/data/<content-digest>
db/<catalog-id>/index/<content-digest>
db/<catalog-id>/leases/...
db/<catalog-id>/gc/...
```

Immutable names are content-addressed where practical. `CURRENT` is the only mutable partition publication pointer and contains generation, manifest digest, writer epoch, prior generation, and checksum. Its immutable manifest separately records the committed WAL high-water mark and the materialized-through position. Readers never infer committed state by listing a prefix.

## Manifest

The immutable manifest contains:

- database lineage, partition ID, generation, parent digest, writer epoch;
- schema/catalog digest and commit timestamp range;
- committed WAL high-water mark, materialized-through position, and transaction digest set/index;
- data/index object references with exact length, cryptographic digest, format and key ID;
- partition mapping version, statistics and deletion/tombstone references;
- minimum reader/runtime version and feature requirements.

The complete manifest is checked before a root becomes readable. Metadata is sharded into immutable submanifests when necessary, but opening fetches a small bounded root and only demanded subtrees.

## Writer fencing

Conditional `PUT CURRENT if-match=<old-etag>` prevents two updates from winning that one key, but is not a lease and does not by itself fence a stale writer's WAL acknowledgements. A writable deployment therefore supplies a fencing service with monotonically increasing epochs (for example, an external transactional metadata service). Every prepared commit, immutable WAL object, manifest, and receipt carries the epoch.

A writer must renew before a safety margin. Once renewal is uncertain or expired, it stops acknowledgement immediately. A later writer publishes a greater epoch; readers reject manifests that violate epoch/generation lineage. “Take over now” without lease expiry/election is not a supported operation.

If no fencing service is configured, the backend runs in one of two honest modes: read-only, or administratively single-writer with no automatic failover guarantee.

## Commit protocol

The remote protocol follows [transactions and recovery](08-transactions-and-recovery.md). Key additional rules:

1. Uploaded objects are immutable and retryable by exact key/digest.
2. A manifest references only successfully verified objects.
3. The conditional `CURRENT` update is the linearization point for partition visibility. A generation may advance only the committed WAL tail (`RemoteLog`) or also advance materialized data coverage (`Published`); readers merge the uncovered committed tail.
4. A lost response creates an ambiguous commit; reconcile reads `CURRENT` ancestry/commit index.
5. An orphan upload is invisible and later GC-eligible.
6. Publication never requires atomic rename, directory listing consistency, or in-place append.

AWS documents strong consistency for individual S3 object reads/writes and conditional requests, but object-store atomicity remains key-scoped. The architecture must not extrapolate that into a transaction spanning WAL, data, and catalog keys. SlateDB's manifest evolution is a useful warning: safe fencing includes WAL positions and compactor/writer coordination, not merely a last-writer-wins root string.

## Data layout for graphs

Remote layout minimizes request count, not just bytes. A partition manifest maps node/edge ID ranges and hashed/high-degree exceptions to packs. Each pack contains independently checksummed aligned tiles:

- adjacency directory tile for many source nodes;
- adjacency data tiles containing neighbor and edge IDs;
- projected hot edge properties when configured;
- column data tiles and group metadata;
- optional coarse endpoint/bloom/zone indexes.

Small metadata/chunks are packed to avoid tiny GETs. Large high-degree lists have range-addressable continuation tiles. Forward/reverse views and edge records for one atomic partition commit are referenced by the same manifest generation.

Partitioning begins with a declared strategy (source range/hash, table, or tenant). The v1 rule is source ownership: the canonical edge record and outbound projection commit in the source partition; a remote-destination reverse projection is an explicitly asynchronous derived index. Strict queries route through canonical source ownership or reject a stale reverse-index plan. A `SnapshotVector` reports each partition generation. Independent forward/reverse publication must never be presented as one atomic property-graph snapshot.

## Read path

Cold query execution is:

```text
resolve/pin CURRENT -> fetch root/submanifest -> plan tile ranges
-> memory cache -> disk cache -> coalesced ranged GETs
-> checksum/decode -> bounded batches
```

The reader keys caches by immutable digest, so stale bytes cannot alias a new generation. It coalesces only ranges whose excess bytes are cheaper than another request under current provider/pricing weights. Concurrency, in-flight bytes, retries, and decoded memory are separately bounded.

Remote adjacency is always batched by source IDs and tile. The optimizer sees projected GET count, bytes, cold/warm class, and cache certainty. A “95% hit rate” is an observation, never a latency or cost bound. Cold latency includes manifest and data requests; total latency includes queue, fetch, checksum, decode, compute, spill, and result backpressure.

## Cache

The disk cache is an optional content-addressed store with an atomic local index, byte quota, checksum on fill/use policy, and cross-process locking. A partial download is written under a temporary unique name, verified, then installed. Eviction never affects correctness.

Admission distinguishes metadata, reused point tiles, and one-pass scans. Scan resistance is implemented via admission/bypass and protected metadata quotas; an eviction policy alone is insufficient. Prefetch uses lower priority and is dropped first under pressure.

## Retry and error policy

Only idempotent object operations retry automatically. Retry classification uses provider status, honors server hints, applies jittered exponential backoff, and consumes a deadline/attempt budget. Authentication, conditional failure, checksum mismatch, and semantic not-found are not blindly retried. Metrics record attempts, throttling, bytes repeated, and ambiguity.

## Encryption and credentials

TLS is required in transit. Server-side encryption settings are explicit; optional client-side envelope encryption records key ID and authenticated metadata in each object header. Nonces are unique per object/chunk. Credentials use the provider chain and are never stored in manifests, logs, plans, or cache metadata.

Key rotation rewrites references by publishing a new immutable generation. Deleting old keys waits until retention, backups, and pinned readers no longer depend on them.

## Garbage collection

GC is mark-and-sweep over a consistent set of retained roots: current roots, manifest ancestry within retention, backups, pins/leases, and in-progress jobs. It writes a mark epoch, observes a quarantine interval longer than maximum publication/clock uncertainty, then deletes only unreferenced immutable objects older than the epoch.

Listing is discovery, never proof of liveness. Delete batches are idempotent and audited. Dry-run reports exact keys, sizes, roots considered, and earliest deletion time. By default, GC is disabled until pin/retention accounting passes crash and race tests.

## SLO and cost contract

Performance is reported by workload and state:

- cold/warm/hot latency percentiles;
- queries admitted/rejected/throttled;
- requests and provider bytes per query;
- cache hit bytes by tier, not only hit operations;
- compute/decoded bytes, spill and peak memory;
- commit upload bytes, requests, CAS conflicts and ambiguous outcomes;
- estimated provider cost under a named price table and date.

There is no universal “flat query cost.” Admission enforces `max_remote_requests`, `max_remote_bytes`, time, and result limits. Public targets name graph size, selectivity, degree distribution, projection, cache state, region, concurrency, and hardware.

## Qualification

- provider contract tests against supported S3 implementations and fault proxies;
- stale-writer/lease-expiry tests proving no acknowledgement after fencing;
- crash and response-loss tests at every commit step;
- corrupt/truncated/range-shifted object detection;
- no-listing read correctness and GC races with publication/pins;
- high-degree, random-source, full-scan, and cross-partition workloads;
- request-bound assertions in CI for canonical query plans;
- restore from remote-only state with empty caches.

Turbopuffer is a useful systems comparator for object-storage economics: it batches WAL persistence and uses an object-friendly coarse index rather than assuming a pointer-heavy local index transfers directly. Its published cold/warm latency gap also reinforces that remote performance must be specified by cache state, not one headline number.
