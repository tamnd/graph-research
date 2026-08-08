# Aerospike Graph source-code and storage-model audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: Pinned AGS, Database, and Java-client source with record-level graph representation
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Source inventory

The pinned AGS snapshot contains 573 Java/Kotlin files and about 106,699 source lines by the audit's file count, split across graph API, Gremlin service, Spark bulk loader, and Spark OLAP modules. The main Gremlin module is the online engine. The source is far more informative than the previous architecture summary: it names sets, bins, ID allocators, record codecs, traversal strategies, query pagers, caches, transaction wrappers, admin services, and 431 observed test files.

Internal packages use the codename `firefly`. `FireflyServer` wires Gremlin Server and HTTP administration. `FireflyGraph` implements TinkerPop. `AerospikeConnection` and `AerospikeOperations` form the storage boundary. The database source separately exposes partition, storage, transaction, query, secondary-index, and primary-index subsystems, but Enterprise-only behavior is not fully established by the community tree.

## Packed model reconstruction

- One normal vertex is one record in the VERTICES set.
- Vertex bins include an interned label ID, preserved user key/type, vertex-property maps, type hints, meta-properties, inbound/outbound adjacency maps, supernode marker, and optional TTL.
- Labels and property-key strings are interned into small Long IDs stored in schema records, reducing repeated wire/storage bytes.
- Logical edges are grouped by `storageId = floorDiv(packingId, phatEdgeSize)` into records in EDGES.
- The source default `phatEdgeSize` is 10; validation accepts 1 through 100; it is immutable after data exists because IDs encode the mapping.
- A normal packed edge stores label ID, both endpoint IDs, properties, and type hints inside a map keyed by full edge ID.
- Normal vertex adjacency caches composite edge ID and opposing vertex identity, allowing some edge-skipping rewrites.
- Supernode adjacency is represented in special edge-record maps and found through mandatory secondary indexes.
- The transition to supernode is one-way for the vertex lifetime; existing inline adjacency is ignored after the marker flips.
- A larger pack amortizes record count and bulk reads but increases write collision/serialization risk on a shared record.
- Vertex record count still scales with vertex count; packing attacks edge-record primary-index overhead, not vertex primary-index overhead.

## Sets observed in the source design

| Set | Contents | Role |
| --- | --- | --- |
| VERTICES | One record per vertex | OLTP authority |
| EDGES | Packed logical edges | OLTP authority |
| IN_VP / OUT_VP | Spilled vertex-property/meta-property structures | Overflow path |
| SCHEMA | Interning maps/counters | Permanent metadata |
| ID_MANAGER | ID counters and recycle buffers | Allocation hotspot/metadata |
| METADATA | Data-model name and version | Startup compatibility |
| SUMMARY | Approximate cardinality and optimizer metadata | Asynchronous derived state |
| INDEX_METADATA | User index descriptors | Planner metadata |
| USAGE_STATS_SET | Opt-in usage statistics | Operational metadata |
| OLAP_TEMP | GraphComputer temporary state | Analytical scratch |
| OLAP_ALGORITHM_TEMP | Algorithm scratch | Analytical scratch |
| OLAP_JOBS | Job state | Analytical metadata |
| BL_METADATA | Bulk-load metadata | Load scratch |
| BL_DUPE_VID | Duplicate vertex IDs | Load error state |
| BL_BAD_EDGE | Invalid edge records | Load error state |
| BL_BAD_ENTRY | Invalid input rows | Load error state |
| BL_RECOVERY_* | Stage recovery state | Load restart |
| ID_CACHE | User-supplied ID cache | Optional/derived lookup state |

## High-value source symbols inspected

| Symbol | Why it matters |
| --- | --- |
| runtime.FireflyServer | Bootstraps Gremlin Server and installs the transaction/session processor |
| structure.FireflyGraph | TinkerPop Graph implementation, strategies, transaction feature, and data-model version |
| io.aerospike.AerospikeConnection | Client creation, read/batch/query/pagination operations, policies, and shared executors |
| io.aerospike.AerospikeOperations | Vertex/edge CRUD, edge-cache updates, supernode writes, MRT and non-MRT sequencing |
| io.aerospike.schema.SchemaManager | Atomic label/property-key interning and reserved edge-property IDs |
| io.aerospike.DataModelVersioning | Startup comparison of on-disk and runtime data-model versions |
| structure.id.FireflyPhatEdgeId | 8/16-byte logical ID and floorDiv-derived packed-record storage ID |
| structure.id.FireflyIdFactory | Vertex, edge, composite, and recycled ID construction |
| structure.id.MrtEdgePackingIdManager | Packing-ID allocation behavior when multi-record transactions are active |
| io.aerospike.ReadThroughRecordCache | Caffeine weighted record cache, stats, invalidation, and memory estimate |
| io.aerospike.CacheManager | Transactional versus global cache ownership and lifecycle |
| structure.transaction.FireflyTransaction | Thread-local TinkerPop scope mapped to Aerospike Txn commit/rollback |
| structure.transaction.FireflyTransactionOpProcessor | Session request routing and execution-timeout handling |
| io.aerospike.query.GraphQuery | Scan/secondary-index query construction and page-stream orchestration |
| io.aerospike.query.paged.PageFetcher | Bounded page queue, background read loop, completion and cancellation |
| io.aerospike.query.paged.PartitionedSindexPageFetcher | Partition-filtered secondary-index pagination |
| io.aerospike.indexes.FireflyIndexMetadata | Runtime index inventory/cardinality and expression-index matching |
| io.aerospike.EdgeQueryHelper | Supernode/packed-edge filter-expression construction |
| io.aerospike.FireflyBatchReadHelper | Has-container ordering and multi-key read preparation |
| runtime.tasks.FireflyGraphSummaryUpdater | Asynchronous summary/cardinality updates including transaction staging |
| structure.util.FireflyTtlHandler | Scheduled TTL purge behavior |
| util.config.ConfigurationHelper | Authoritative key names, defaults, immutable settings, and validators |
| bulkloader.SparkBulkLoaderMain | Out-of-process distributed initial/incremental loader entry point |
| olap.DistributedGraphComputerMain | Out-of-process Spark GraphComputer entry point |

## Local source validation performed

- Cloned the public repositories and recorded AGS `ad0983e5519cbd3705f70113afd7df048c568045`, examples `e2300bc201f949c4261ecd88b235dea1877fa088`, server `3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc`, and Java client `9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12`.
- Counted 573 Java/Kotlin files and approximately 106,699 lines in the AGS snapshot; counts are inventory observations, not quality metrics.
- Observed 431 test files across the source snapshot, including TinkerPop structure/process, transaction, concurrency, cache, index, supernode, bulk-loader recovery, and benchmark-oriented tests.
- Built the AGS Gremlin module and dependencies with Maven while skipping tests; the build produced `aerospike-graph-gremlin-3.3.0-SNAPSHOT.jar`.
- The successful source build establishes that the inspected default-branch snapshot compiles in this environment; it does not establish 3.2.3 binary identity, server compatibility, performance, or correctness under a live Aerospike cluster.
- A targeted Maven test selection was attempted without provisioning the expected three-node Aerospike test cluster at 172.17.0.1:3000/3010/3020. Cluster-backed `TestDataModelVersioning` retried connection, errored in setup, then also exposed cleanup null-pointer errors because setup left the database handle null. The run was terminated and is not reported as a source-test pass or product failure; it establishes that these selected tests are integration-dependent and that failed setup currently produces noisy secondary errors.
- Fetched signed `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3` and diffed it against the inspected branch head. The delta changes CI, container, Helm, packaging, and smoke scripts but no Java/Kotlin engine source.

## Important source/code caveats

- Source design prose and source code can drift; derive final record bytes with a qualified backup export or direct record inspection on the pinned image.
- The public source branch is ahead of shipped 3.2.3 and has no matching tag.
- A logical edge add touches the packed edge record and both endpoint vertex records when adjacency is inline.
- Without MRT, the source writes endpoint adjacency first and edge record last; read-side existence checks hide partial adjacency at the cost of stranded bytes.
- With MRT, edge record and endpoint changes share an Aerospike Txn; record packing can cause transaction collisions and ID retarget/retry.
- Global edge/property scans remain qualitatively different from ID-rooted traversals.
- No global edge property or edge label index appears in the audited design; supernode adjacency indexes are specialized, not general edge indexes.
- Maximum Aerospike record size constrains inline adjacency and packed-record risk; raising it changes latency, memory, and write amplification.

## Record-model qualification cases

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — storage: vertex key Long

- Purpose: Verify stable user ID round trip and digest derivation.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex key Long`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — storage: vertex key Integer

- Purpose: Verify type preservation rather than numeric coercion.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex key Integer`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — storage: vertex key String

- Purpose: Measure digest/key memory and collision handling.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex key String`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — storage: generated vertex ID

- Purpose: Measure buffered decrementing allocation and crash gaps.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `generated vertex ID`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — storage: schema first label

- Purpose: Observe atomic intern assignment under concurrency.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `schema first label`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — storage: schema repeated label

- Purpose: Confirm cache hit and no counter increment.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `schema repeated label`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — storage: schema concurrent new key

- Purpose: Prove a single permanent interned ID.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `schema concurrent new key`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — storage: schema restart

- Purpose: Rebuild in-memory maps from records without remapping.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `schema restart`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — storage: single vertex property

- Purpose: Inspect VP_DATA and type-hint encoding.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `single vertex property`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — storage: list cardinality

- Purpose: Inspect multiple property IDs and meta-property behavior.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `list cardinality`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — storage: set cardinality

- Purpose: Qualify 3.2 semantics for equality and type mixing.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `set cardinality`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — storage: meta-property spill

- Purpose: Trigger IN_VP/OUT_VP and measure extra I/O.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `meta-property spill`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — storage: datetime property

- Purpose: Prove source/storage/client round trip and indexed range.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `datetime property`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — storage: double property

- Purpose: Confirm no index path and exact comparison behavior.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `double property`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — storage: scaled long

- Purpose: Compare indexed range path with Double scan path.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `scaled long`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — storage: normal edge add

- Purpose: Count edge-record and both vertex-record operations.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `normal edge add`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — storage: self-loop add

- Purpose: Detect duplicate endpoint operations and path semantics.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `self-loop add`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — storage: parallel edges

- Purpose: Preserve distinct edge IDs and properties.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `parallel edges`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — storage: edge property update

- Purpose: Measure packed-record contention and byte rewrite.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `edge property update`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — storage: edge delete

- Purpose: Verify record-first visibility and adjacency cleanup.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `edge delete`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — storage: pack size 1

- Purpose: Establish record-count and contention baseline.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `pack size 1`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — storage: pack size 10

- Purpose: Qualify source default under mixed reads/writes.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `pack size 10`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — storage: pack size 100

- Purpose: Expose large-record reads and writer collision tradeoff.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `pack size 100`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — storage: pack immutability

- Purpose: Reject runtime pack-size change on existing data.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `pack immutability`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — storage: pack partial occupancy

- Purpose: Measure waste under random deletes and recycled IDs.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `pack partial occupancy`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — storage: packing collision

- Purpose: Force concurrent writes to one packed record.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `packing collision`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — storage: recycled edge ID

- Purpose: Verify 16-byte identity and no alias with deleted edge.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `recycled edge ID`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — storage: allocator crash gap

- Purpose: Prove gaps do not become identity reuse.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `allocator crash gap`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — storage: ordinary adjacency degree 1

- Purpose: Establish minimum hop I/O.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `ordinary adjacency degree 1`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — storage: ordinary adjacency degree 100

- Purpose: Measure batch grouping and response materialization.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `ordinary adjacency degree 100`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — storage: ordinary adjacency near threshold

- Purpose: Expose record-size and update tail latency.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `ordinary adjacency near threshold`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — storage: automatic supernode transition

- Purpose: Verify irreversible ECACHE_OFF change.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `automatic supernode transition`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — storage: manual supernode flag

- Purpose: Avoid populating adjacency that will be abandoned.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `manual supernode flag`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — storage: supernode inbound

- Purpose: Trace E_IN secondary-index query and filters.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `supernode inbound`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — storage: supernode outbound

- Purpose: Trace E_OUT secondary-index query and filters.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `supernode outbound`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — storage: supernode both

- Purpose: Measure two index streams, deduplication, and self-loops.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `supernode both`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — storage: supernode property pushdown

- Purpose: Count records/edges eliminated server-side.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `supernode property pushdown`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — storage: unfiltered supernode

- Purpose: Capture worst-case transfer and memory.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `unfiltered supernode`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — storage: vertex max-record-size 128KiB

- Purpose: Validate documented ~800-edge transition estimate.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex max-record-size 128KiB`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — storage: vertex max-record-size 1MiB

- Purpose: Validate documented ~6,500-edge transition estimate.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex max-record-size 1MiB`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — storage: vertex max-record-size 8MiB memory

- Purpose: Validate documented ~50,000-edge transition estimate.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex max-record-size 8MiB memory`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — storage: record-size exceed

- Purpose: Verify error mapping and absence of partial visible edge.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `record-size exceed`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — storage: vertex label index

- Purpose: Inspect numeric interned label index path.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex label index`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — storage: vertex string property index

- Purpose: Verify full-string equality only.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex string property index`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — storage: vertex numeric property index

- Purpose: Verify range bounds and type matching.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `vertex numeric property index`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — storage: compound expression index

- Purpose: Qualify exact predicate coverage and fallback.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `compound expression index`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — storage: edge label global lookup

- Purpose: Prove scan fallback and disable-scan rejection.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `edge label global lookup`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — storage: edge property global lookup

- Purpose: Prove lack of general secondary index.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `edge property global lookup`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — storage: TTL vertex

- Purpose: Trace index, sweeper, incident-edge cleanup, and lag.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `TTL vertex`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — storage: TTL edge

- Purpose: Trace per-edge TTL map and packed-record cleanup.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `TTL edge`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — storage: data-model major mismatch

- Purpose: Prove startup refuses incompatible on-disk major.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `data-model major mismatch`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — storage: data-model newer minor

- Purpose: Prove older service refuses newer disk minor.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `data-model newer minor`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — storage: data-model rolling minor

- Purpose: Prove newer service reads older disk minor.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `data-model rolling minor`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — storage: backup record reconstruction

- Purpose: Validate all sets, bins, indexes, and metadata after restore.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `backup record reconstruction`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — storage: database partition migration

- Purpose: Validate record availability and traversal completeness during rebalance.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `database partition migration`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — storage: primary-index RAM

- Purpose: Measure bytes per vertex and packed edge record at scale.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `primary-index RAM`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — storage: secondary-index RAM

- Purpose: Measure per-entry cost for labels, properties, TTL, and supernodes.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `secondary-index RAM`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — storage: defrag amplification

- Purpose: Measure device writes after churn in packed records.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `defrag amplification`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — storage: compression

- Purpose: Measure CPU/latency/storage tradeoff where licensed/supported.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `compression`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — storage: namespace storage engine

- Purpose: Compare HMA, memory, and all-flash without conflating modes.
- Setup: Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.
- Workload: Execute the smallest semantically complete operation for `namespace storage engine`, then repeat under controlled concurrency and skew.
- Required counters: Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S11,S12,S15,S33–S44
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S11 — Indexing

- Type: Official documentation
- Audit note: Vertex index and scan controls
- URL: https://aerospike.com/docs/graph/develop/query/indexing/

### S12 — Supernodes

- Type: Official documentation
- Audit note: Thresholds and filtered traversal guidance
- URL: https://aerospike.com/docs/graph/develop/query/supernodes/

### S15 — Data types

- Type: Official documentation
- Audit note: Property and index type limitations
- URL: https://aerospike.com/docs/graph/develop/query/data-type-support/

### S31 — Database storage configuration

- Type: Official documentation
- Audit note: Memory, device, and persistence modes
- URL: https://aerospike.com/docs/database/manage/namespace/storage/config/

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S34 — AGS data model design

- Type: Apache-2.0 source documentation
- Audit note: Packed record layout
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md

### S35 — AGS architecture source map

- Type: Apache-2.0 source documentation
- Audit note: Modules and entry points
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/ARCHITECTURE.md

### S36 — AGS AerospikeOperations

- Type: Apache-2.0 source
- Audit note: Read/write and edge mutation pipeline
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java

### S37 — AGS configuration source

- Type: Apache-2.0 source
- Audit note: Code defaults and validators
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java

### S38 — AGS query code

- Type: Apache-2.0 source
- Audit note: Paged scans and secondary-index queries
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query

### S39 — AGS traversal strategies

- Type: Apache-2.0 source
- Audit note: Rewrite implementations
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy

### S40 — AGS transaction implementation

- Type: Apache-2.0 source
- Audit note: TinkerPop transaction wrapper
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java

### S41 — AGS tests

- Type: Apache-2.0 source
- Audit note: 431 test files observed in snapshot
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test

### S43 — Database server source snapshot

- Type: AGPL/community core source
- Audit note: Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc
- URL: https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

### S44 — Java client source snapshot

- Type: Apache-2.0 source
- Audit note: Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
- URL: https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
