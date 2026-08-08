# Aerospike-derived design lessons and solution plan for zu

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Actionable architecture, implementation, and qualification decisions for an S3-authoritative graph engine
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Recommended stance

Copy Aerospike's disciplines, not its storage authority. The useful disciplines are compact schema interning, adjacency-aware point paths, batching by storage destination, server-side predicate pushdown, independent stateless query compute, explicit supernode treatment, scan admission, detailed source-visible operations, and separate bulk/OLAP paths. The non-fit is authoritative mutable record storage on a provisioned database cluster with primary/secondary index RAM and data-volume licensing.

zu should make S3 the durable immutable authority and treat local NVMe and RAM as bounded, reconstructible acceleration. That changes the write contract: acknowledged mutations must enter an inexpensive durable log or manifest path, then compact into immutable graph segments. Low latency comes from deterministic ID routing, sparse indexes, compressed adjacency blocks, cache admission, request coalescing, and vectorized traversal. It does not come from pretending an S3 GET is sub-millisecond.

## Proposed architecture

The durable unit is an immutable S3 graph segment partitioned by stable vertex-ID hash, with optional label or time locality inside the partition. A small strongly consistent catalog maps a snapshot epoch and logical partition to content-addressed objects. Mutations first enter a durable log or micro-batch delta object carrying an idempotency key and visibility epoch. Compaction later folds those deltas into the next immutable generation.

Each partition contains a compact vertex table, out-adjacency blocks, optional in-adjacency blocks, property columns, and sparse indexes. Schema, label, and property names use immutable, epoch-versioned dictionaries rather than one hot global allocation counter. Supernode adjacency is chunked from the beginning and carries label ranges plus min, max, and Bloom summaries so filters can skip blocks.

Stateless native workers resolve IDs, coalesce object ranges, decode and filter batches, and stream results under a hard memory budget. The local NVMe cache is content-addressed, while the smaller RAM cache and index have byte limits, admission policy, and tenant quotas. Neither cache participates in correctness. Scans use a separate admission class from latency-sensitive traffic. Compaction and index builders are interruptible background jobs with fixed CPU, request, and byte budgets.

Reads bind to one manifest epoch. A transactional mutation service, if provided, declares its key and partition scope rather than claiming arbitrary distributed ACID. Every query reports objects, ranges, bytes, cache decisions, decode time, frontier size, spills, retries, S3 requests, estimated cost, and result cardinality.

```rust
struct Snapshot {
    epoch: u64,
    manifest_etag: [u8; 32],
}

struct AdjacencyBlockRef {
    object: ObjectId,
    range: std::ops::Range<u64>,
    edge_label: u32,
    min_neighbor: u64,
    max_neighbor: u64,
    bloom: BloomRef,
}

struct QueryBudget {
    deadline: std::time::Instant,
    max_frontier: usize,
    max_memory_bytes: usize,
    max_s3_requests: u32,
    max_s3_bytes: u64,
}
```

The snapshot value travels with every operator. Object and range identifiers key the cache, so a cache hit cannot return data from the wrong epoch. `QueryBudget` is checked before issuing I/O and before growing a frontier, which makes cost and overload controls part of execution rather than an after-the-fact dashboard.

## Direct design comparison

| Aerospike technique | Lesson | zu adaptation |
| --- | --- | --- |
| Vertex record with embedded adjacency | ID-rooted locality dominates hop cost | Immutable vertex header points to compact adjacency blocks/ranges |
| 10-edge packed record | Amortize per-record metadata and RPCs | Pack thousands of sorted adjacency entries per compressed block, sized for range reads |
| Schema interning | Repeated strings are permanent tax | Epoch-versioned dictionaries with local IDs and merge/remap tooling |
| Supernode index path | One layout fails across degree distribution | Chunk and shard supernode adjacency from creation; use block metadata pushdown |
| TinkerPop strategies | Recognize high-value traversal patterns | Typed IR and rule/cost optimizer with observable physical operators |
| Batch per DB node | Group I/O by destination | Coalesce range/object reads by object and byte interval |
| Filter expressions | Push rejection to data access | Evaluate predicates during vectorized decode before materialization |
| Transactional/global cache | Cache policy affects semantics/resources | Cache never affects freshness; epoch keys make invalidation structural |
| Scan disable | Protect OLTP from accidental O(N) | Cost guard, explicit scan capability, budget and queue class |
| Stateless AGS | Compute elasticity should avoid shard ownership | Workers obtain snapshot/partition maps from manifest and hold no authority |
| Spark loader | Bulk creation needs a separate high-throughput path | Distributed segment builder writes final S3 layout directly |
| MRT | Graph mutations span records | Make transaction scope/cost explicit; avoid claiming arbitrary distributed ACID |

## PB and trillion-edge capacity model

Capacity must be algebraic before it is empirical. For each edge, model encoded neighbor ID delta, label/type, property references/values, block index share, object overhead share, replication/version retention, and compression. For each vertex, model ID/key, label, property columns, out/in block pointers, sparse-index entries, and dictionary share. Add snapshot retention, uncompacted deltas, compaction overlap, checksums, manifests, and safety margin.

A trillion edges at 12 logical encoded bytes per direction is already 24 TB before properties, vertices, indexes, object overhead, deltas, history, and replicas; at 50 bytes it is 50 TB for one direction. A PB target is therefore plausible only with transparent definitions of logical versus physical bytes. “Thousands of billions” means multiple trillions, not the 37.2B public Aerospike benchmark. Every capacity claim must state degree distribution, both-direction storage, property mix, compression, and retained epochs.

## zu implementation and experiment backlog

### Translating the useful parts without copying the authority model

Aerospike's most reusable idea is not its specific record schema; it is the
discipline of recognizing high-value traversal shapes before execution and
grouping remote work by destination. In an S3-authoritative engine, the same
discipline groups reads by immutable object and byte range instead of Database
node. A point-rooted traversal resolves a stable vertex ID, finds the partition
and block through the snapshot manifest, coalesces adjacent ranges, decodes
columnar or adjacency blocks in batches, and applies predicates before creating
edge objects. The operator reports object requests and bytes so a fast path is
visible rather than hidden behind a generic traversal step.

Aerospike's edge packing also provides a warning. Packing reduces per-record
metadata and commands, but mutable packed records introduce false sharing. An
immutable design can pack much more aggressively because readers address a
content hash and writers publish a new generation instead of rewriting the
shared object in place. The remaining tradeoff is read amplification: a block
that is too large wastes S3 bytes and cache space for point access, while a block
that is too small increases requests and metadata. Block targets should be
chosen in bytes, with separate layouts for ordinary adjacency and supernodes,
and validated against actual degree and property distributions.

The source contains a useful constraint in the transaction configuration:

```java
// MRT operation can handle only 4096 records
```

This short extract is from pinned
[`AerospikeConnectionConfig.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeConnectionConfig.java).
The lesson is to expose transaction scope as a concrete budget. The proposed
engine should not advertise arbitrary distributed graph ACID if its inexpensive
path can atomically publish only one manifest partition or a bounded key set.
It should state the maximum keys, partitions, bytes, and time, provide
idempotency tokens, and define how a client observes the published epoch.

| Aerospike observation | Direct copy would cause | Proposed adaptation |
| --- | --- | --- |
| Mutable packed edge records | False sharing and collision under hot writes | Immutable adjacency blocks plus small delta segments |
| Vertex record caches endpoint identity | Low-hop latency but duplicated mutable state | Versioned adjacency block with endpoint IDs in one snapshot |
| One-way supernode transition | Performance cliff and irreversible layout state | Degree-aware chunking from initial build with online manifest rewrite |
| Provider strategy batching | Efficient remote commands for recognized syntax | Typed physical IR with object-range coalescing and observable rules |
| Global cache mode | Faster hot reads with stale, per-instance state | Epoch-keyed content cache with no correctness role |
| Bounded MRT record count | Honest scope for multi-record mutation | Declared key, partition, byte, and deadline transaction budget |
| Spark bulk loader | Separate path for high-volume creation | Direct immutable segment builder that writes final S3 format |
| Scan disable control | Protects OLTP from accidental global work | Separate scan queue with request, byte, CPU, and result budgets |

This backlog is ordered by dependency even though the case numbers are not release milestones. Format, manifest, dictionary, and snapshot correctness come before cache and latency work. Query operators are tested first with empty caches and fault-injected S3-compatible storage, then with bounded RAM and NVMe caches. Every experiment records object requests, byte ranges, decoded bytes, allocations, frontier size, spills, retries, compaction debt, and estimated request cost.

An experiment graduates into a claim only after its semantic oracle, crash recovery, cancellation, and budget checks pass. Aerospike comparisons use the same logical traversal, result rules, durability, and cost boundary described in specification 06. A locally warm prototype that depends on unbounded cache is not a qualification result for an S3-authoritative engine.

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
<td>zu: stable vertex routing</td>
<td>Choose a hash/partition scheme that survives compute scaling.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q002</td>
<td>zu: partition map epoch</td>
<td>Route every query against an immutable snapshot.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q003</td>
<td>zu: manifest atomic publish</td>
<td>Make new snapshots all-or-nothing.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q004</td>
<td>zu: manifest service failure</td>
<td>Define read availability with cached signed manifests.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q005</td>
<td>zu: schema dictionary allocation</td>
<td>Avoid central hot counter while preserving stable decode.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q006</td>
<td>zu: dictionary merge</td>
<td>Reconcile distributed builders deterministically.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q007</td>
<td>zu: vertex block layout</td>
<td>Minimize point-read ranges and decode.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q008</td>
<td>zu: out adjacency block</td>
<td>Optimize dominant directed hop.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q009</td>
<td>zu: in adjacency optionality</td>
<td>Trade storage for reverse traversal SLO.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q010</td>
<td>zu: edge identity</td>
<td>Preserve parallel edges, deletes, and path identity.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q011</td>
<td>zu: edge property columns</td>
<td>Avoid reading unused values.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q012</td>
<td>zu: vertex property columns</td>
<td>Support projection and predicate pushdown.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q013</td>
<td>zu: normal degree packing</td>
<td>Tune block target by bytes, not edge count alone.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q014</td>
<td>zu: supernode preclassification</td>
<td>Avoid costly one-way layout migration at threshold.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q015</td>
<td>zu: supernode chunk key</td>
<td>Distribute hot reads/writes across chunks.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q016</td>
<td>zu: supernode label clustering</td>
<td>Skip irrelevant edge labels.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q017</td>
<td>zu: supernode property metadata</td>
<td>Use min/max/bloom/dictionary indexes to skip blocks.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q018</td>
<td>zu: S3 range coalescing</td>
<td>Combine adjacent reads per object.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q019</td>
<td>zu: S3 request hedging</td>
<td>Bound tails without uncontrolled request cost.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q020</td>
<td>zu: S3 retry budget</td>
<td>Prevent retry storms and duplicate billed requests.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q021</td>
<td>zu: S3 multipart builder</td>
<td>Write large immutable objects efficiently.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q022</td>
<td>zu: small-object avoidance</td>
<td>Control request cost and listing/metadata burden.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q023</td>
<td>zu: NVMe content cache</td>
<td>Make cached blocks reusable across epochs when content-identical.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q024</td>
<td>zu: RAM metadata cache</td>
<td>Bound routing/index state by bytes.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q025</td>
<td>zu: cache admission</td>
<td>Protect hot small blocks from scans.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q026</td>
<td>zu: tenant cache quota</td>
<td>Prevent noisy tenant eviction.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q027</td>
<td>zu: cold point lookup</td>
<td>Meet an honest object-store cold SLO.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q028</td>
<td>zu: warm point lookup</td>
<td>Target Aerospike-class latency from bounded cache.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q029</td>
<td>zu: frontier batching</td>
<td>Group next-hop IDs before I/O.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q030</td>
<td>zu: vectorized decode</td>
<td>Reduce CPU and allocations per edge.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q031</td>
<td>zu: predicate pushdown</td>
<td>Reject edges before object creation.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q032</td>
<td>zu: projection pushdown</td>
<td>Read/decode only needed property streams.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q033</td>
<td>zu: limit pushdown</td>
<td>Stop block reads after sufficient results while preserving order.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q034</td>
<td>zu: sample semantics</td>
<td>Avoid biased block-level samples.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q035</td>
<td>zu: local count</td>
<td>Answer from block metadata when semantically exact.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q036</td>
<td>zu: path memory</td>
<td>Bound path retention or spill explicitly.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q037</td>
<td>zu: cycle detection</td>
<td>Use compact visited structures with exact/approx modes.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q038</td>
<td>zu: typed physical IR</td>
<td>Make operator choices and semantics inspectable.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q039</td>
<td>zu: rule optimizer</td>
<td>Capture reliable ID/batch/pushdown rewrites.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q040</td>
<td>zu: cost optimizer</td>
<td>Choose scan/index/block paths from current stats.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q041</td>
<td>zu: stats freshness</td>
<td>Keep stale estimates from causing unbounded work.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q042</td>
<td>zu: plan fingerprint</td>
<td>Attach physical plan identity to every benchmark sample.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q043</td>
<td>zu: scan admission</td>
<td>Require explicit budget for O(N) operations.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q044</td>
<td>zu: heavy query queue</td>
<td>Isolate scans/supernodes from short OLTP.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q045</td>
<td>zu: memory admission</td>
<td>Reject before operator allocations exceed budget.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q046</td>
<td>zu: result backpressure</td>
<td>Stream with bounded buffers.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q047</td>
<td>zu: request cancellation</td>
<td>Stop S3 reads/decode after timeout/disconnect.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q048</td>
<td>zu: mutation idempotency</td>
<td>Use client operation IDs and sequence numbers.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q049</td>
<td>zu: delta visibility</td>
<td>Define when new vertices/edges enter snapshots.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q050</td>
<td>zu: read-your-writes</td>
<td>Offer session overlay or explicit wait-for-epoch.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q051</td>
<td>zu: snapshot isolation</td>
<td>Keep multi-hop traversal on one manifest epoch.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q052</td>
<td>zu: delete tombstone</td>
<td>Prevent resurrection across compaction/late writes.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q053</td>
<td>zu: transaction key set</td>
<td>Declare bounded atomic scope and failure behavior.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q054</td>
<td>zu: compaction budget</td>
<td>Cap CPU/network/S3 cost and publish debt.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q055</td>
<td>zu: compaction overlap</td>
<td>Charge temporary bytes and request cost.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q056</td>
<td>zu: incremental index build</td>
<td>Publish index atomically with compatible epoch.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q057</td>
<td>zu: bulk import</td>
<td>Build final layout without replaying online mutations.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q058</td>
<td>zu: bulk validation</td>
<td>Detect orphan edges, duplicate IDs, and type errors.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q059</td>
<td>zu: backup semantics</td>
<td>S3 authority makes snapshots native but catalog recovery still matters.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q060</td>
<td>zu: cross-region copy</td>
<td>Define RPO/RTO and manifest ordering.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q061</td>
<td>zu: object corruption</td>
<td>Use checksums, redundancy, and repair.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q062</td>
<td>zu: S3 outage</td>
<td>Define cached-read and write-log behavior.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q063</td>
<td>zu: worker loss</td>
<td>Retry stateless query fragments safely.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q064</td>
<td>zu: manifest split brain</td>
<td>Fence publishers and verify monotonic epochs.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q065</td>
<td>zu: fixed monthly request budget</td>
<td>Admission-control requests/bytes to a declared envelope.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q066</td>
<td>zu: per-query cost estimate</td>
<td>Expose S3 requests, bytes, CPU, cache, and egress.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q067</td>
<td>zu: per-tenant budget</td>
<td>Enforce predictable cost and fairness.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q068</td>
<td>zu: PB capacity derivation</td>
<td>Publish uncertainty bands and retained-history factor.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q069</td>
<td>zu: trillion-edge generator</td>
<td>Create realistic skew without materializing verbose input.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q070</td>
<td>zu: scale ladder</td>
<td>Run 1B, 10B, 100B, 1T and validate model error.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q071</td>
<td>zu: Aerospike normal-degree comparison</td>
<td>Target equal bounded traversal semantics.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q072</td>
<td>zu: Aerospike supernode comparison</td>
<td>Target filtered/unfiltered discontinuity.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q073</td>
<td>zu: Aerospike resource comparison</td>
<td>Charge AGS, DB, RF, headroom, indexes, and license.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q074</td>
<td>zu: Aerospike failure comparison</td>
<td>Match consistency and degraded-state requirements.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q075</td>
<td>zu: 10x p99 gate</td>
<td>Require confidence-bound ratio and correctness.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q076</td>
<td>zu: 10x resource gate</td>
<td>Require full-system bytes/CPU, not process cherry-picking.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q077</td>
<td>zu: 10x cost gate</td>
<td>Require same term/region/SLO and all services.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q078</td>
<td>zu: regression corpus</td>
<td>Retain every winning cell as continuous performance test.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
<tr>
<td>Q079</td>
<td>zu: public reproducibility</td>
<td>Publish data generator, harness, raw samples, configs, and analysis.</td>
<td>Aerospike evidence S09–S45 plus zu-owned implementation artifacts</td>
</tr>
</tbody>
</table>

## Release gates

G0: semantic conformance for IDs, parallel edges, properties, direction, paths, bags, order, null/missing, and mutations.
G1: deterministic physical format, checksums, upgrade reader, and snapshot manifest recovery.
G2: bounded-memory point and traversal operators under slow consumers and cancellation.
G3: cold/warm latency results with object-request and byte counters; no hidden unbounded cache.
G4: fault results for S3, worker, manifest, network, and compaction failures.
G5: capacity-model prediction within declared error at each scale-ladder step.
G6: full cost sheet at target SLO, including requests, compute, cache, storage, egress, operations, and redundancy.
G7: Aerospike 3.2.3 comparison with equal semantics and current Database release.
G8: per-cell 10x claims only where the confidence and correctness rules pass.
G9: public artifact bundle sufficient for an independent rerun.

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
<td>S01</td>
<td>AGS release index</td>
<td>Official documentation</td>
<td>2026-06-30 latest listed release</td>
<td>https://aerospike.com/docs/graph/release</td>
</tr>
<tr>
<td>S02</td>
<td>AGS 3.2.3 release notes</td>
<td>Official documentation</td>
<td>Security-only patch; 14 CVEs listed</td>
<td>https://aerospike.com/docs/graph/release/3-2-3/</td>
</tr>
<tr>
<td>S03</td>
<td>AGS 3.2.2 release notes</td>
<td>Official documentation</td>
<td>Removed graph-service feature check</td>
<td>https://aerospike.com/docs/graph/release/3-2-2/</td>
</tr>
<tr>
<td>S04</td>
<td>AGS 3.2.1 release notes</td>
<td>Official documentation</td>
<td>Container memory and rack awareness</td>
<td>https://aerospike.com/docs/graph/release/3-2-1/</td>
</tr>
<tr>
<td>S05</td>
<td>AGS 3.2.0 release notes</td>
<td>Official documentation</td>
<td>Global cache, set cardinality, performance changes</td>
<td>https://aerospike.com/docs/graph/release/3-2-0/</td>
</tr>
<tr>
<td>S06</td>
<td>AGS 3.1.1 release notes</td>
<td>Official documentation</td>
<td>CVE-2025-12383 fix</td>
<td>https://aerospike.com/docs/graph/release/3-1-1/</td>
</tr>
<tr>
<td>S07</td>
<td>AGS 3.1.0 release notes</td>
<td>Official documentation</td>
<td>TinkerPop transactions and typed indexes</td>
<td>https://aerospike.com/docs/graph/release/3-1-0/</td>
</tr>
<tr>
<td>S08</td>
<td>AGS 3.0.0 release notes</td>
<td>Official documentation</td>
<td>Packed model revision and reload boundary</td>
<td>https://aerospike.com/docs/graph/release/3-0-0/</td>
</tr>
<tr>
<td>S09</td>
<td>Architecture</td>
<td>Official documentation</td>
<td>Three-layer request path</td>
<td>https://aerospike.com/docs/graph/overview/architecture/</td>
</tr>
<tr>
<td>S10</td>
<td>Transaction contract</td>
<td>Official documentation</td>
<td>Read, mutation, SC, AP, and MRT distinctions</td>
<td>https://aerospike.com/docs/graph/develop/query/transactions/</td>
</tr>
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
<td>S13</td>
<td>Query threading</td>
<td>Official documentation</td>
<td>Per-query parallelization and batch/page controls</td>
<td>https://aerospike.com/docs/graph/develop/query/query-threading/</td>
</tr>
<tr>
<td>S14</td>
<td>Cache management</td>
<td>Official documentation</td>
<td>Transactional and global record caches</td>
<td>https://aerospike.com/docs/graph/manage/cache/</td>
</tr>
<tr>
<td>S15</td>
<td>Data types</td>
<td>Official documentation</td>
<td>Property and index type limitations</td>
<td>https://aerospike.com/docs/graph/develop/query/data-type-support/</td>
</tr>
<tr>
<td>S16</td>
<td>TinkerPop feature support</td>
<td>Official documentation</td>
<td>Feature compatibility matrix</td>
<td>https://aerospike.com/docs/graph/overview/tinkerpop/</td>
</tr>
<tr>
<td>S17</td>
<td>Configuration reference</td>
<td>Official documentation</td>
<td>AGS runtime knobs</td>
<td>https://aerospike.com/docs/graph/reference/config/</td>
</tr>
<tr>
<td>S18</td>
<td>Metrics reference</td>
<td>Official documentation</td>
<td>Prometheus metric inventory</td>
<td>https://aerospike.com/docs/graph/reference/metrics/</td>
</tr>
<tr>
<td>S19</td>
<td>Query tracing</td>
<td>Official documentation</td>
<td>Zipkin tracing contract</td>
<td>https://aerospike.com/docs/graph/observe/query-tracing/</td>
</tr>
<tr>
<td>S20</td>
<td>Bulk load overview</td>
<td>Official documentation</td>
<td>Standalone and Spark paths</td>
<td>https://aerospike.com/docs/graph/load/overview/</td>
</tr>
<tr>
<td>S21</td>
<td>Distributed bulk load</td>
<td>Official documentation</td>
<td>EMR and Dataproc workflow</td>
<td>https://aerospike.com/docs/graph/load/distributed/</td>
</tr>
<tr>
<td>S22</td>
<td>Graph backup and restore</td>
<td>Official documentation</td>
<td>Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page</td>
<td>https://aerospike.com/docs/graph/manage/backup/</td>
</tr>
<tr>
<td>S23</td>
<td>Security</td>
<td>Official documentation</td>
<td>TLS, JWT RBAC, database RBAC, audit</td>
<td>https://aerospike.com/docs/graph/manage/security/</td>
</tr>
<tr>
<td>S24</td>
<td>Multi-tenancy</td>
<td>Official documentation</td>
<td>Graph scoping in a shared namespace</td>
<td>https://aerospike.com/docs/graph/manage/multi-tenant/</td>
</tr>
<tr>
<td>S25</td>
<td>Identity graph benchmark PDF</td>
<td>Vendor benchmark</td>
<td>AGS 2.4.2 / Database 7.1.0.9 test</td>
<td>https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf</td>
</tr>
<tr>
<td>S26</td>
<td>Graph 3.0 launch blog</td>
<td>Vendor blog</td>
<td>Ingest and footprint claims</td>
<td>https://aerospike.com/blog/aerospike-graph-3-release/</td>
</tr>
<tr>
<td>S27</td>
<td>Architecture deep-dive blog</td>
<td>Vendor blog</td>
<td>Optimizer and record-model explanation</td>
<td>https://aerospike.com/blog/graphing-database-architecture/</td>
</tr>
<tr>
<td>S28</td>
<td>Product editions and pricing</td>
<td>Official commercial page</td>
<td>Edition limits and data-volume licensing</td>
<td>https://aerospike.com/products/features-and-editions/</td>
</tr>
<tr>
<td>S29</td>
<td>Database platform support</td>
<td>Official documentation</td>
<td>Current Database release matrix</td>
<td>https://aerospike.com/docs/database/reference/platform-support</td>
</tr>
<tr>
<td>S30</td>
<td>Database limits</td>
<td>Official documentation</td>
<td>Cluster and object limits</td>
<td>https://aerospike.com/docs/database/reference/limitations/</td>
</tr>
<tr>
<td>S31</td>
<td>Database storage configuration</td>
<td>Official documentation</td>
<td>Memory, device, and persistence modes</td>
<td>https://aerospike.com/docs/database/manage/namespace/storage/config/</td>
</tr>
<tr>
<td>S32</td>
<td>Database FAQ</td>
<td>Official documentation</td>
<td>CE/SE/EE/FE boundaries</td>
<td>https://aerospike.com/docs/database/reference/faq</td>
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
<td>S42</td>
<td>Graph examples</td>
<td>Apache-2.0 source</td>
<td>Examples at e2300bc201f949c4261ecd88b235dea1877fa088</td>
<td>https://github.com/aerospike/aerospike-graph/tree/e2300bc201f949c4261ecd88b235dea1877fa088</td>
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
<tr>
<td>S45</td>
<td>Apache TinkerPop 3.7.3 reference</td>
<td>Upstream documentation</td>
<td>Language/runtime semantic oracle</td>
<td>https://tinkerpop.apache.org/docs/3.7.3/reference/</td>
</tr>
<tr>
<td>S46</td>
<td>AGS v3.3.0-rc5 prerelease tag</td>
<td>Signed public source tag</td>
<td>Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
</tr>
<tr>
<td>S47</td>
<td>Graph 2.5 strong-consistency launch blog</td>
<td>Vendor blog</td>
<td>Database 8 transaction positioning and the explicit eventual-read caveat</td>
<td>https://aerospike.com/blog/aerospike-graph-2-5-0-strong-consistency</td>
</tr>
<tr>
<td>S48</td>
<td>Aerospike Graph AI and MCP blog</td>
<td>Vendor blog</td>
<td>Newest Graph-specific blog found in the publication sweep; an integration/demo layer, not a storage-engine release</td>
<td>https://aerospike.com/blog/aerospike-graph-ai-mcp-natural-language-queries/</td>
</tr>
<tr>
<td>S49</td>
<td>Legacy asbackup documentation</td>
<td>Official documentation</td>
<td>The target of the current Graph backup-page link; explicitly labeled legacy</td>
<td>https://aerospike.com/docs/database/tools/backup-and-restore/asbackup</td>
</tr>
<tr>
<td>S50</td>
<td>Current Database backup and restore overview</td>
<td>Official documentation</td>
<td>ABS and absctl are current choices while asbackup/asrestore are legacy</td>
<td>https://aerospike.com/docs/database/tools/backup-and-restore/overview/</td>
</tr>
</tbody>
</table>
