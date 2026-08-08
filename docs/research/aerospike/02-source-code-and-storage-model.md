# Aerospike Graph source-code and storage-model audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Pinned AGS, Database, and Java-client source with record-level graph representation
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Source inventory

The pinned AGS snapshot contains 573 Java/Kotlin files and about 106,699 source lines by the audit's file count, split across graph API, Gremlin service, Spark bulk loader, and Spark OLAP modules. The main Gremlin module is the online engine. The source is far more informative than the previous architecture summary: it names sets, bins, ID allocators, record codecs, traversal strategies, query pagers, caches, transaction wrappers, admin services, and 431 observed test files.

Internal packages use the codename `firefly`. `FireflyServer` wires Gremlin Server and HTTP administration. `FireflyGraph` implements TinkerPop. `AerospikeConnection` and `AerospikeOperations` form the storage boundary. The database source separately exposes partition, storage, transaction, query, secondary-index, and primary-index subsystems, but Enterprise-only behavior is not fully established by the community tree.

## Packed model reconstruction

One normal vertex is one record in the VERTICES set.
Vertex bins include an interned label ID, preserved user key/type, vertex-property maps, type hints, meta-properties, inbound/outbound adjacency maps, supernode marker, and optional TTL.
Labels and property-key strings are interned into small Long IDs stored in schema records, reducing repeated wire/storage bytes.
Logical edges are grouped by `storageId = floorDiv(packingId, phatEdgeSize)` into records in EDGES.
The source default `phatEdgeSize` is 10; validation accepts 1 through 100; it is immutable after data exists because IDs encode the mapping.
A normal packed edge stores label ID, both endpoint IDs, properties, and type hints inside a map keyed by full edge ID.
Normal vertex adjacency caches composite edge ID and opposing vertex identity, allowing some edge-skipping rewrites.
Supernode adjacency is represented in special edge-record maps and found through mandatory secondary indexes.
The transition to supernode is one-way for the vertex lifetime; existing inline adjacency is ignored after the marker flips.
A larger pack amortizes record count and bulk reads but increases write collision/serialization risk on a shared record.
Vertex record count still scales with vertex count; packing attacks edge-record primary-index overhead, not vertex primary-index overhead.

The following sketch is deliberately conceptual. Bin names and codecs must be taken from the pinned implementation, but the sketch makes the amplification boundary visible during design review. A logical edge is not stored as one isolated record. It shares a packed record and is also represented in the endpoint adjacency state.

```text
VERTICES[userVertexId] = {
    labelId:        interned integer,
    properties:     typed property maps,
    outAdjacency:   edgeId -> adjacent vertex identity,
    inAdjacency:    edgeId -> adjacent vertex identity,
    supernode:      boolean,
    ttl:            optional expiration
}

EDGES[floor(packingId / phatEdgeSize)] = {
    edgeIdA: { labelId, outVertexId, inVertexId, properties },
    edgeIdB: { labelId, outVertexId, inVertexId, properties },
    ...
}
```

With the default pack size of ten, one edge update can contend with nine unrelated logical edges that happen to share the record. Larger packs reduce record and primary-index overhead but enlarge the collision and rewrite domain. Smaller packs move in the opposite direction. This is why `phatEdgeSize` belongs in the physical-format manifest and cannot be treated as a harmless runtime tuning knob after data exists.

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

Cloned the public repositories and recorded AGS `ad0983e5519cbd3705f70113afd7df048c568045`, examples `e2300bc201f949c4261ecd88b235dea1877fa088`, server `3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc`, and Java client `9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12`.
Counted 573 Java/Kotlin files and approximately 106,699 lines in the AGS snapshot; counts are inventory observations, not quality metrics.
Observed 431 test files across the source snapshot, including TinkerPop structure/process, transaction, concurrency, cache, index, supernode, bulk-loader recovery, and benchmark-oriented tests.
Built the AGS Gremlin module and dependencies with Maven while skipping tests; the build produced `aerospike-graph-gremlin-3.3.0-SNAPSHOT.jar`.
The successful source build establishes that the inspected default-branch snapshot compiles in this environment; it does not establish 3.2.3 binary identity, server compatibility, performance, or correctness under a live Aerospike cluster.
A targeted Maven test selection was attempted without provisioning the expected three-node Aerospike test cluster at 172.17.0.1:3000/3010/3020. Cluster-backed `TestDataModelVersioning` retried connection, errored in setup, then also exposed cleanup null-pointer errors because setup left the database handle null. The run was terminated and is not reported as a source-test pass or product failure; it establishes that these selected tests are integration-dependent and that failed setup currently produces noisy secondary errors.
Fetched signed `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3` and diffed it against the inspected branch head. The delta changes CI, container, Helm, packaging, and smoke scripts but no Java/Kotlin engine source.

## Important source/code caveats

Source design prose and source code can drift; derive final record bytes with a qualified backup export or direct record inspection on the pinned image.
The public source branch is ahead of shipped 3.2.3 and has no matching tag.
A logical edge add touches the packed edge record and both endpoint vertex records when adjacency is inline.
Without MRT, the source writes endpoint adjacency first and edge record last; read-side existence checks hide partial adjacency at the cost of stranded bytes.
With MRT, edge record and endpoint changes share an Aerospike Txn; record packing can cause transaction collisions and ID retarget/retry.
Global edge/property scans remain qualitatively different from ID-rooted traversals.
No global edge property or edge label index appears in the audited design; supernode adjacency indexes are specialized, not general edge indexes.
Maximum Aerospike record size constrains inline adjacency and packed-record risk; raising it changes latency, memory, and write amplification.

## Record-model qualification cases

### What edge packing changes in practice

The storage record for an edge is selected from its packing ID rather than from
the user-visible edge identity alone. The critical source expression is only
one line:

```java
return Math.floorDiv(packingId, phatEdgeSize);
```

It appears in the pinned
[`FireflyPhatEdgeId.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/id/FireflyPhatEdgeId.java).
The result is the Database record key for a pack. With a pack size of ten,
packing IDs zero through nine share one record, ten through nineteen share the
next, and so on. A point read of one edge may therefore fetch nearby logical
edges, which is useful when traversal consumes several of them. A property
update also rewrites the shared record, which means edge packing trades index
and command efficiency for a larger contention and write-amplification domain.
The correct pack size depends on mutation rate, edge property width, adjacency
locality, record-size limits, and the ratio of point to batch reads.

The endpoint vertex records create a second representation of connectivity.
For ordinary vertices, inbound and outbound adjacency maps hold the edge
identity and the opposing vertex identity. That cache lets an `out()` or `in()`
shape move directly toward vertices when no edge projection is required. It
also means that adding or deleting one logical relationship involves more than
the packed edge record. Without MRT, source ordering and existence checks are
used to keep partial adjacency from becoming a visible edge. With MRT, the edge
record and endpoint mutations can participate in one Database transaction, but
the pack is also a transaction conflict unit. Record count alone therefore
understates both the write path and the correctness work.

Supernodes are not merely large ordinary vertices. Once the marker flips, AGS
uses specialized edge-record structures and secondary indexes to find incident
edges. The transition is intentionally one way, so a benchmark that loads a
high-degree vertex and later deletes most of its edges does not return to the
ordinary inline path. Degree buckets immediately below and above the configured
threshold must be separate benchmark cells. Filtered and unfiltered supernode
queries also belong in separate cells because server-side label or property
rejection can change the number of edge records and endpoint vertices that must
be materialized.

| Physical concern | Ordinary vertex path | Supernode path | Measurement needed |
| --- | --- | --- | --- |
| Adjacency location | Vertex record maps | Specialized edge records located by secondary index | Commands, records, bytes, and index pages per hop |
| Edge grouping | Shared packed edge record | Shared records plus supernode indexing | Collision rate and bytes rewritten per mutation |
| Direction lookup | Inline inbound or outbound map | Direction included in specialized query keys | Forward and reverse p99 by degree |
| State transition | Inline until threshold | One-way after marker is set | Latency and storage immediately around threshold |
| Delete behavior | Endpoint and packed-record cleanup | Best-effort large cleanup with separate risks | Orphans, completion time, retries, and post-audit |
| Capacity pressure | One vertex primary-index entry plus packed edges | Additional secondary-index state and query load | PI RAM, SI RAM, device bytes, and query-thread use |

Each storage case begins with the same raw-record procedure. Pin the AGS and Database artifacts, load only the records needed for the case, capture namespace and set statistics, export or inspect the affected records, perform one mutation, and capture the records again. The inspection records command counts, record generations, logical and physical sizes, primary and secondary index memory, device bytes, and defragmentation work.

The semantic oracle verifies ID type, labels, parallel-edge identity, property values, direction, adjacency visibility, and state after restart. A hidden scan, unexpected record fan-out, stranded adjacency, pack collision, unsupported type, or mismatch between the source model and shipped image is reported directly. Nothing in this catalog has a measured result unless a linked artifact says so.

<table>
<thead>
<tr>
<th>Case</th>
<th>Subject</th>
<th>Engineering question</th>
<th>Evidence</th>
</tr>
</thead>
<tbody>
<tr>
<td>Q001</td>
<td>storage: vertex key Long</td>
<td>Verify stable user ID round trip and digest derivation.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q002</td>
<td>storage: vertex key Integer</td>
<td>Verify type preservation rather than numeric coercion.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q003</td>
<td>storage: vertex key String</td>
<td>Measure digest/key memory and collision handling.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q004</td>
<td>storage: generated vertex ID</td>
<td>Measure buffered decrementing allocation and crash gaps.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q005</td>
<td>storage: schema first label</td>
<td>Observe atomic intern assignment under concurrency.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q006</td>
<td>storage: schema repeated label</td>
<td>Confirm cache hit and no counter increment.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q007</td>
<td>storage: schema concurrent new key</td>
<td>Prove a single permanent interned ID.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q008</td>
<td>storage: schema restart</td>
<td>Rebuild in-memory maps from records without remapping.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q009</td>
<td>storage: single vertex property</td>
<td>Inspect VP_DATA and type-hint encoding.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q010</td>
<td>storage: list cardinality</td>
<td>Inspect multiple property IDs and meta-property behavior.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q011</td>
<td>storage: set cardinality</td>
<td>Qualify 3.2 semantics for equality and type mixing.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q012</td>
<td>storage: meta-property spill</td>
<td>Trigger IN_VP/OUT_VP and measure extra I/O.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q013</td>
<td>storage: datetime property</td>
<td>Prove source/storage/client round trip and indexed range.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q014</td>
<td>storage: double property</td>
<td>Confirm no index path and exact comparison behavior.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q015</td>
<td>storage: scaled long</td>
<td>Compare indexed range path with Double scan path.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q016</td>
<td>storage: normal edge add</td>
<td>Count edge-record and both vertex-record operations.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q017</td>
<td>storage: self-loop add</td>
<td>Detect duplicate endpoint operations and path semantics.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q018</td>
<td>storage: parallel edges</td>
<td>Preserve distinct edge IDs and properties.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q019</td>
<td>storage: edge property update</td>
<td>Measure packed-record contention and byte rewrite.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q020</td>
<td>storage: edge delete</td>
<td>Verify record-first visibility and adjacency cleanup.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q021</td>
<td>storage: pack size 1</td>
<td>Establish record-count and contention baseline.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q022</td>
<td>storage: pack size 10</td>
<td>Qualify source default under mixed reads/writes.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q023</td>
<td>storage: pack size 100</td>
<td>Expose large-record reads and writer collision tradeoff.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q024</td>
<td>storage: pack immutability</td>
<td>Reject runtime pack-size change on existing data.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q025</td>
<td>storage: pack partial occupancy</td>
<td>Measure waste under random deletes and recycled IDs.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q026</td>
<td>storage: packing collision</td>
<td>Force concurrent writes to one packed record.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q027</td>
<td>storage: recycled edge ID</td>
<td>Verify 16-byte identity and no alias with deleted edge.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q028</td>
<td>storage: allocator crash gap</td>
<td>Prove gaps do not become identity reuse.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q029</td>
<td>storage: ordinary adjacency degree 1</td>
<td>Establish minimum hop I/O.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q030</td>
<td>storage: ordinary adjacency degree 100</td>
<td>Measure batch grouping and response materialization.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q031</td>
<td>storage: ordinary adjacency near threshold</td>
<td>Expose record-size and update tail latency.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q032</td>
<td>storage: automatic supernode transition</td>
<td>Verify irreversible ECACHE_OFF change.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q033</td>
<td>storage: manual supernode flag</td>
<td>Avoid populating adjacency that will be abandoned.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q034</td>
<td>storage: supernode inbound</td>
<td>Trace E_IN secondary-index query and filters.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q035</td>
<td>storage: supernode outbound</td>
<td>Trace E_OUT secondary-index query and filters.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q036</td>
<td>storage: supernode both</td>
<td>Measure two index streams, deduplication, and self-loops.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q037</td>
<td>storage: supernode property pushdown</td>
<td>Count records/edges eliminated server-side.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q038</td>
<td>storage: unfiltered supernode</td>
<td>Capture worst-case transfer and memory.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q039</td>
<td>storage: vertex max-record-size 128KiB</td>
<td>Validate documented ~800-edge transition estimate.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q040</td>
<td>storage: vertex max-record-size 1MiB</td>
<td>Validate documented ~6,500-edge transition estimate.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q041</td>
<td>storage: vertex max-record-size 8MiB memory</td>
<td>Validate documented ~50,000-edge transition estimate.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q042</td>
<td>storage: record-size exceed</td>
<td>Verify error mapping and absence of partial visible edge.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q043</td>
<td>storage: vertex label index</td>
<td>Inspect numeric interned label index path.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q044</td>
<td>storage: vertex string property index</td>
<td>Verify full-string equality only.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q045</td>
<td>storage: vertex numeric property index</td>
<td>Verify range bounds and type matching.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q046</td>
<td>storage: compound expression index</td>
<td>Qualify exact predicate coverage and fallback.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q047</td>
<td>storage: edge label global lookup</td>
<td>Prove scan fallback and disable-scan rejection.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q048</td>
<td>storage: edge property global lookup</td>
<td>Prove lack of general secondary index.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q049</td>
<td>storage: TTL vertex</td>
<td>Trace index, sweeper, incident-edge cleanup, and lag.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q050</td>
<td>storage: TTL edge</td>
<td>Trace per-edge TTL map and packed-record cleanup.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q051</td>
<td>storage: data-model major mismatch</td>
<td>Prove startup refuses incompatible on-disk major.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q052</td>
<td>storage: data-model newer minor</td>
<td>Prove older service refuses newer disk minor.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q053</td>
<td>storage: data-model rolling minor</td>
<td>Prove newer service reads older disk minor.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q054</td>
<td>storage: backup record reconstruction</td>
<td>Validate all sets, bins, indexes, and metadata after restore.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q055</td>
<td>storage: database partition migration</td>
<td>Validate record availability and traversal completeness during rebalance.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q056</td>
<td>storage: primary-index RAM</td>
<td>Measure bytes per vertex and packed edge record at scale.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q057</td>
<td>storage: secondary-index RAM</td>
<td>Measure per-entry cost for labels, properties, TTL, and supernodes.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q058</td>
<td>storage: defrag amplification</td>
<td>Measure device writes after churn in packed records.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q059</td>
<td>storage: compression</td>
<td>Measure CPU/latency/storage tradeoff where licensed/supported.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
<tr>
<td>Q060</td>
<td>storage: namespace storage engine</td>
<td>Compare HMA, memory, and all-flash without conflating modes.</td>
<td>S11,S12,S15,S33–S44</td>
</tr>
</tbody>
</table>

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

<table>
<thead>
<tr>
<th>ID</th>
<th>Source</th>
<th>Class</th>
<th>Audit use</th>
<th>Link</th>
</tr>
</thead>
<tbody>
<tr>
<td>S11</td>
<td>Indexing</td>
<td>Official documentation</td>
<td>Vertex index and scan controls</td>
<td>https://aerospike.com/docs/graph/develop/query/indexing/</td>
</tr>
<tr>
<td>S12</td>
<td>Supernodes</td>
<td>Official documentation</td>
<td>Thresholds and filtered traversal guidance</td>
<td>https://aerospike.com/docs/graph/develop/query/supernodes/</td>
</tr>
<tr>
<td>S15</td>
<td>Data types</td>
<td>Official documentation</td>
<td>Property and index type limitations</td>
<td>https://aerospike.com/docs/graph/develop/query/data-type-support/</td>
</tr>
<tr>
<td>S31</td>
<td>Database storage configuration</td>
<td>Official documentation</td>
<td>Memory, device, and persistence modes</td>
<td>https://aerospike.com/docs/database/manage/namespace/storage/config/</td>
</tr>
<tr>
<td>S33</td>
<td>AGS public source snapshot</td>
<td>Apache-2.0 source</td>
<td>3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045</td>
</tr>
<tr>
<td>S34</td>
<td>AGS data model design</td>
<td>Apache-2.0 source documentation</td>
<td>Packed record layout</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md</td>
</tr>
<tr>
<td>S35</td>
<td>AGS architecture source map</td>
<td>Apache-2.0 source documentation</td>
<td>Modules and entry points</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/ARCHITECTURE.md</td>
</tr>
<tr>
<td>S36</td>
<td>AGS AerospikeOperations</td>
<td>Apache-2.0 source</td>
<td>Read/write and edge mutation pipeline</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java</td>
</tr>
<tr>
<td>S37</td>
<td>AGS configuration source</td>
<td>Apache-2.0 source</td>
<td>Code defaults and validators</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java</td>
</tr>
<tr>
<td>S38</td>
<td>AGS query code</td>
<td>Apache-2.0 source</td>
<td>Paged scans and secondary-index queries</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query</td>
</tr>
<tr>
<td>S39</td>
<td>AGS traversal strategies</td>
<td>Apache-2.0 source</td>
<td>Rewrite implementations</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy</td>
</tr>
<tr>
<td>S40</td>
<td>AGS transaction implementation</td>
<td>Apache-2.0 source</td>
<td>TinkerPop transaction wrapper</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java</td>
</tr>
<tr>
<td>S41</td>
<td>AGS tests</td>
<td>Apache-2.0 source</td>
<td>431 test files observed in snapshot</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/test</td>
</tr>
<tr>
<td>S43</td>
<td>Database server source snapshot</td>
<td>AGPL/community core source</td>
<td>Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
<td>https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
</tr>

<tr>
<td>S44</td>
<td>Java client source snapshot</td>
<td>Apache-2.0 source</td>
<td>Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12</td>
<td>https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12</td>
</tr>
</tbody>
</table>
