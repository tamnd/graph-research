# Qualification, security, and operations

## No benchmark is a contract without a workload

Every performance statement names:

- commit/build version and feature flags;
- dataset generator/source and digest;
- node/edge/property counts, degree distribution, labels and skew;
- query corpus, parameters, selectivity, result size and concurrency;
- backend/profile, storage/device/provider/region and machine;
- cold/warm/hot cache procedure;
- memory, spill, CPU, request and byte budgets;
- repetitions, warmup, percentile/confidence method, failures and timeouts.

Results report throughput and latency distributions, not only the best or mean. Regressions compare like-for-like artifacts. An estimate derived from cache-hit assumptions or provider price tables is labeled a model, not a measurement.

## Release SLO classes

Initial SLOs are qualification templates; numeric thresholds are set only after representative baselines:

| Class | Required measures |
|---|---|
| local point/adjacency | p50/p95/p99 latency, bytes/pages decoded, cache state |
| local analytical scan | rows/s, compressed/decoded bytes/s, CPU, peak memory |
| write/commit | p50/p99 by durability level, group size, WAL bytes, sync time |
| recovery/open | clean open fixed work; crash replay versus WAL bytes/transactions |
| SQLite | latency/throughput, statement count, busy time, native pushdown fraction |
| object cold/warm | p50/p95/p99, GET/HEAD count, provider/cache bytes and total cost |
| path/skew | explored states, peak frontier, spills, deadline/cap termination |

Qualification includes overload. A service meets its SLO only if admitted requests do; rejection/throttling rates and queue time are reported alongside latency.

## Cost model

Remote estimated cost for an operation is:

```text
request_count_by_class × request_price
+ storage_byte_time × storage_price
+ retrieved_bytes × retrieval_price
+ egress_bytes × egress_price
+ cache_volume/IO cost
+ compute_time × compute price
```

Price tables are versioned by provider, region, storage class, and effective date. The model includes retries and compaction/GC write amplification. “Storage cost” and “total query cost” are not interchangeable.

Local cost reports device bytes, write amplification, CPU, peak resident memory, and spill. The optimizer's cost units need not be monetary but must be calibratable to measured components.

## Correctness qualification

Release gates include:

- parser/binder golden diagnostics and language conformance corpus;
- randomized differential results across reference, zu1, and SQLite;
- bag multiplicity, stable edge IDs, parallel edges, self-loops, nulls, and path modes;
- snapshot/MVCC histories generated against a small executable state-machine model;
- deterministic crash/fault simulation at every persistence transition;
- encoding, file, WAL, manifest and network-input fuzzing;
- full verification after randomized update/checkpoint/compaction/reopen cycles;
- upgrade/downgrade golden artifacts for each supported format/API version;
- sanitizer and concurrency-model checks for unsafe/lifetime/publication code.

A correctness failure blocks performance release. Expected files and known issues are versioned, narrow, and expire; a blanket flaky-test retry is not acceptance.

## Availability and degradation

Health reports components separately: read path, writer lease, WAL, root publication, cache, maintenance debt, and provider access. Modes are explicit:

- `Ready`: full advertised capabilities;
- `ReadOnlyDegraded`: snapshots readable, new commits disabled;
- `Fenced`: this process cannot write; reads may continue;
- `RecoveryRequired`: operator action or full recovery needed;
- `Corrupt`: integrity failure; writes disabled and evidence preserved;
- `BudgetThrottled`: healthy but admission-limited.

The system does not turn a checksum failure into a cache miss unless the corrupt object is an independently disposable cache copy and a verified authoritative refetch succeeds. Authoritative corruption is sticky and surfaced.

## Threat model

Consider:

- malicious query text/parameters and oversized values;
- malformed or adversarial database, WAL, manifest and encoded bytes;
- compromised/incorrect object provider responses and stale data;
- credential leakage through errors, logs, profiles or paths;
- untrusted extensions/functions;
- tenant resource exhaustion;
- local attacker able to read temp/cache files where deployment does not isolate them.

Not initially defended: an attacker with arbitrary code execution as the database OS user; denial of service through unlimited authorized result data when administrators disable budgets; cryptographic authenticity of local files unless signing/encryption is enabled.

## Security requirements

- all byte decoders are bounded, checked, fuzzed, and avoid allocation before validation;
- unsafe code is isolated, justified by invariants, and covered by Miri/sanitizers where applicable;
- SQL lowering is parameterized and generated identifiers derive from checked stable IDs;
- object credentials/tokens are resolved at runtime, redacted, and never persisted in catalog/plan;
- cache/spill directories use restrictive permissions; symlink/path traversal is rejected;
- remote transport verifies TLS by default; insecure modes are explicit test-only flags;
- encryption metadata is authenticated; checksum is not presented as authentication;
- plugins/native extensions are off by default for untrusted inputs;
- dependency advisories, licenses, lockfile integrity and supply-chain provenance are CI gates.

Because `zu-cli` is an application and file compatibility depends on exact codecs, the repository should track `Cargo.lock`. Reproducible release builds pin the Rust toolchain and emit an SBOM and checksums.

## Operator workflows

### Open and inspect

`zu inspect <db>` performs bounded, read-only anchor/catalog validation. It reports format/runtime requirements, lineage/root, clean/dirty state, WAL replay work, encryption key IDs, and detected capabilities. It does not mutate recovery state unless `--recover` is explicit.

### Verify and repair

Verification levels are anchor, metadata, index/table, full content, and cross-index semantic invariants. Output is machine-readable and identifies roots/objects/ranges and whether a verified redundant copy exists.

Repair always creates a new root/database and a report. Destructive salvage requires an explicit destination and never overwrites the sole evidence. Object-store repair does not delete old objects.

### Backup/restore

Backups are pinned-snapshot manifests with end-to-end digests. Restore is tested regularly, not inferred from upload success. Operational targets include recovery point/time objectives with workload and data size.

### Maintenance

Checkpoint, compaction, analyze, index build, re-encoding, backup, verify, and GC expose progress and resource usage. They are cancellable before publication; after publication begins, cancellation completes or safely reconciles that transition. Jobs resume from verified artifacts after restart.

## Compatibility policy

Three versions are independent:

- public API/CLI behavior;
- logical catalog and query semantics;
- physical file/WAL/object format.

The compatibility matrix states readable/writable ranges and migration path. Readers never silently write upgrades. Unknown required features fail with a diagnostic naming the minimum runtime. Once a stable format is declared, at least one previous major reader and export path remain available under the published support window.

## Operational game days

Before GA and periodically afterward, exercise:

- process/host loss during commits and checkpoint;
- device full/read-only/short I/O and WAL corruption;
- object-store throttling, stale/failed reads, lost CAS response and regional outage;
- lease-service loss, expiry, clock skew and stale writer;
- cache loss/corruption with remote-only restore;
- accidental schema change, bad rollout and binary downgrade;
- runaway scan/path query and spill exhaustion;
- GC racing a reader, backup and publication.

Each drill records detection time, allowed state, operator commands, evidence retained, recovery time, data-loss result, and follow-up test. Runbooks link to exact error codes and do not depend on tribal knowledge.
