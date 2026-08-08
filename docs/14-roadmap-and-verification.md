# Migration and verification roadmap

## Delivery principle

Build a vertical, semantically complete local slice before expanding remote scale. The current prototypes remain valuable as test inputs, but no new backend feature should deepen the direct `zu-query -> zu-zu1` dependency or the empty `zu-storage` abstraction.

Each phase ends in an executable gate. Feature flags mark incomplete work as experimental; documentation never describes later phases as current behavior.

## Phase 0 — freeze claims and preserve evidence

Deliverables:

- classify existing docs and benchmarks as implemented, experimental, target, or model;
- capture golden zu1 files, queries, and current benchmark artifacts at baseline commit;
- add CI for all workspace features, release-mode tests, formatting/lints, dependency audit, and tracked lockfile;
- make current unchecked ID constructors checked and add release-boundary tests;
- document that DML, unified transactions, true S3 persistence, and multi-edge trail correctness are not released.

Exit gate: baseline behavior is reproducible; misleading claims are removed; known format inputs can be read or deliberately rejected by future work.

## Phase 1 — semantic foundation and real SPI

Deliverables:

- stable `NodeId`, `EdgeId`, table/column/catalog IDs and versioned types;
- immutable `CatalogSnapshot`, capability descriptors, `SnapshotToken` and pin registry;
- `StorageEngine`/reader/source/mutation interfaces from document 05;
- canonical `DataBatch`/`AdjacencyBatch` ownership and budget guards;
- in-memory reference engine implementing the whole semantic contract;
- common storage conformance suite.

Exit gate: the query interpreter runs only through the new SPI and passes generated multi-edge/snapshot tests. Empty placeholder types and the executor's legacy `Graph` trait have a dated removal plan.

## Phase 2 — query migration

Deliverables:

- separate bound logical and physical IRs;
- stable edge identity in values, equality, property lookup, and path visited state;
- batch source/adjacency operators, backpressure, cancellation and memory accounting;
- typed pushdown classification and capability validation;
- reference differential harness and optimizer rewrite tests;
- public `Database`, `Connection`, read transaction, prepared query, and result-stream APIs.

Exit gate: all supported read queries match the reference engine on deterministic generated corpora; no query crate imports an engine crate; cancellation leaks zero pins/reservations in fault tests.

## Phase 3 — local transaction vertical slice

Deliverables:

- logical mutation batches and write transaction API;
- node/edge insert/update/delete plus constraints and both adjacency directions;
- framed WAL, commit state machine, immediately visible committed overlay;
- deterministic recovery simulator and fault injection;
- checkpoint to an immutable root and safe snapshot-based reclamation.

Exit gate: acknowledged local commits survive every injected crash; unacknowledged commits resolve only to documented old/new outcomes; queries see committed deltas before checkpoint; parallel edges survive recovery and checkpoint.

## Phase 4 — zu1 pre-freeze redesign

Deliverables:

- bounded anchor/open and copy-on-write root publication;
- per-consumed-chunk integrity and full verifier;
- stable-ID indexes and tiled bidirectional adjacency;
- encoding trees and compute capability metadata;
- shared buffer manager/positioned I/O and cheap reader cloning;
- partial partition/group checkpoint and measured reclamation.

Exit gate: format fuzz/crash/golden tests pass, corrupt point-read chunks fail closed, clean open performs bounded I/O, and benchmark artifacts demonstrate no unacceptable regression. Only then assign a stable format epoch.

## Phase 5 — SQLite parity

Deliverables:

- full SPI implementation with bounded connection pool;
- schema/ID/edge model and transactional DML;
- snapshot capability stated exactly;
- batched adjacency and typed native pushdown;
- backup/migration/reconcile and error mapping.

Exit gate: common conformance plus randomized cross-engine differential tests pass; native pushdown on/off produces identical results; configured durability has crash-test evidence.

## Phase 6 — runtime hardening and optimizer

Deliverables:

- global/query/operator resource hierarchy, spill and fair scheduler;
- vector kernels over selected encodings and explicit materialization;
- robust degree/statistics ranges and backend-aware multi-dimensional costing;
- binary/multiway join choices, bitmap/semijoin reduction, adaptive factorization;
- bounded variable-length path execution and full observability.

Exit gate: adversarial overload remains within memory/I/O bounds, plan differential tests pass, estimated versus actual telemetry is recorded, and representative local/SQLite SLO templates have thresholds.

## Phase 7 — object-single

Deliverables:

- provider capability qualification and immutable pack/range reader;
- content-addressed disk/memory cache with scan admission;
- externally fenced writer epochs and manifest/WAL commit/reconcile;
- request/byte/cost-aware planning and admission;
- backup/restore, retention pins and quarantined mark/sweep GC.

Exit gate: stale writers cannot acknowledge, ambiguous commits reconcile, GC never removes live data under deterministic races, empty-cache restore succeeds, and cold/warm request-count/SLO gates pass. Until then `zu-s3` remains a manifest experiment, not a remote database engine.

## Phase 8 — partitioned datasets

Deliverables:

- stable partition map/version and routing;
- explicit edge co-location/projection rule preserving directional consistency;
- partition-local transactions and query fan-out budgets;
- resharding job with dual-read/publication state machine;
- clear rejection or saga semantics for cross-partition mutation.

Exit gate: partition movement, stale maps, partial outage, and high-degree exceptions pass model/fault tests. No distributed ACID claim is permitted without a separate transactional control-plane project.

## Dependency graph

```text
identity/catalog -> storage SPI -> query migration
                         |              |
                         v              v
                  local txn/WAL -> runtime/optimizer
                         |              |
                         v              +--> SQLite parity
                    zu1 pre-freeze      |
                         +--------------+--> object-single -> partitioned
```

Object-store work may prototype packs in parallel, but cannot become the authoritative write path before transaction identity, fencing, snapshot pins, and budgets exist.

## Compatibility and rollout

Use side-by-side readers and explicit conversion:

1. retain the baseline reader as `zu1-experimental-0`;
2. implement new semantic exports from old readable files;
3. write new-format output to a separate destination;
4. verify counts, IDs where representable, properties and query corpus;
5. atomically select the new database only after validation;
6. retain source according to rollback policy.

The old relationship representation cannot always reconstruct distinct edge identity if input already collapsed parallel edges. Migration reports this as data loss/ambiguity and requires user policy; it must not invent equivalence silently.

## Verification pyramid

### Per change

- unit/property tests and parser/format golden cases;
- common conformance subset;
- format/lint and unsafe review;
- deterministic seed recorded on failure.

### Per merge

- all features in debug and release;
- randomized differential engine/query histories;
- crash points touched by persistence changes;
- resource leak/bound tests touched by runtime changes;
- benchmark smoke tests with request-count assertions.

### Nightly

- long fuzz campaigns for parsers, codecs, file/WAL/manifest readers;
- thousands of model-based MVCC/recovery histories;
- optimizer query generation and cross-engine differential runs;
- concurrency sanitizers/model checking subsets;
- provider fault proxy and GC/publication races.

### Release

- supported-version golden matrix and upgrade/restore rehearsal;
- full integrity scan after stress/update/compaction;
- security/advisory/license/SBOM gates;
- workload-specific SLO and cost report, including overload and cold cache;
- signed artifacts/checksums and operator runbooks.

## Traceability matrix

Every normative requirement gets an ID in implementation issues and tests:

| Prefix | Area | Example evidence |
|---|---|---|
| `ID-*` | element/schema identity | parallel-edge compaction test |
| `SNAP-*` | MVCC/snapshots | generated history model |
| `DUR-*` | WAL/commit/recovery | crash-point matrix |
| `FMT-*` | format/integrity | corrupt point-read corpus |
| `QRY-*` | language/optimizer | reference differential seed |
| `RES-*` | resources/runtime | peak reservation assertion |
| `OBJ-*` | remote/fencing/GC | stale writer simulator |
| `OPS-*` | backup/security/upgrade | restore/game-day artifact |

A release checklist links requirement, code, test, and evidence artifact. A test count alone is not traceability.

## First ten implementation changes

1. Add checked stable `EdgeId` and use it in executor relationship values/visited sets.
2. Define canonical catalog/snapshot/batch types in dependency-leaf crates.
3. Replace empty `zu-storage` payloads with the read-only SPI and in-memory adapter.
4. Move the current zu1 query adapter behind `SnapshotReader`.
5. Add common multi-edge/self-loop/snapshot tests and a reference interpreter.
6. Introduce public database/connection/read-transaction APIs with engine features.
7. Route current zu1 WAL overlay through snapshot reads.
8. Specify/implement framed WAL and deterministic crash harness before more DML.
9. Add per-chunk checksums and bounded root/open metadata in a pre-freeze format epoch.
10. Implement SQLite through the same SPI and use it as a differential oracle.

These are ordered to remove semantic and dependency risk before optimizing storage or promising remote scale.
