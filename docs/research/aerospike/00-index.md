# Aerospike Graph 2026 dossier: index, verdict, and evidence map

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Navigation and decision summary for all Aerospike-specific specifications
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Outcome

Aerospike Graph is a serious comparator for low-latency distributed property-graph serving, especially when the graph is much larger than DRAM and the workload is bounded, ID-rooted, and dominated by ordinary-degree vertices. Its key design is not a graph-native distributed storage engine. It is a stateless TinkerPop and Gremlin JVM service that maps graph operations onto Aerospike Database records, collection operations, batch operations, filter expressions, secondary indexes, and, when explicitly enabled on the right edition, multi-record transactions.

It does not satisfy the project's S3-authoritative fixed-cost goal. S3 and GCS are bulk-loader inputs or backup destinations, while live authoritative graph records remain in an Aerospike namespace backed by memory and/or block/NVMe-class storage. Enterprise scale, strong consistency, rack awareness, TLS/ACLs, XDR, and multi-record transactions introduce commercial edition or add-on boundaries. The official pricing page says production licensing is primarily based on unique data volume, which is directly opposed to an S3-only fixed marginal-cost target.

There is no evidence for a universal tenfold win by Aerospike or against Aerospike. The current public identity benchmark is useful scale evidence: up to 38.3 billion vertices and 37.2 billion edges, a 23.35 TB user dataset, and a vendor-reported 600K QPS with 32 AGS nodes. It is still a vendor-run test on AGS 2.4.2 and Database 7.1.0.9. The PDF does not expose a raw sample archive or a competitor run, and its graphs are sparse, localized identity subgraphs. It is not PB or trillion-edge proof.

The request path below is the mental model used throughout this dossier. A Gremlin step is not a direct storage instruction. Provider strategies first reshape the traversal, then the service translates the remaining work into point, batch, secondary-index, or scan operations against Aerospike Database.

```text
Gremlin bytecode
    |
    v
load balancer -> stateless AGS JVM -> traversal strategies
                                      | point read
                                      | batch read
                                      | secondary-index query
                                      | paged scan
                                      v
                              Aerospike Database
                                      |
                                      v
                     replicated memory or NVMe records
```

## Dossier files

| File | Purpose |
| --- | --- |
| [01-product-releases-and-evidence.md](./01-product-releases-and-evidence.md) | Release chronology, product/edition boundary, source freshness, conflicts, claims |
| [02-source-code-and-storage-model.md](./02-source-code-and-storage-model.md) | Pinned source audit, sets/bins, packed edges, IDs, schema, indexes, supernodes |
| [03-gremlin-query-execution.md](./03-gremlin-query-execution.md) | TinkerPop contract, compiler strategies, I/O paths, caching, scans, profiling |
| [04-transactions-distribution-and-failure.md](./04-transactions-distribution-and-failure.md) | Read consistency, AP/SC mutations, MRT, TinkerPop transactions, failover |
| [05-operations-resources-security-and-cost.md](./05-operations-resources-security-and-cost.md) | Deployment, sizing, JVM/DB resources, monitoring, backup, S3, security, price |
| [06-benchmark-audit-and-10x-qualification.md](./06-benchmark-audit-and-10x-qualification.md) | Vendor benchmark deconstruction and reproducible comparison program |
| [07-design-lessons-for-zu.md](./07-design-lessons-for-zu.md) | Concrete design choices, avoidances, experiments, and acceptance gates for zu |

## Architectural reading of the product

The most useful way to understand Aerospike Graph is to stop treating the word
Graph as the name of a storage engine. AGS is a provider implementation above
Aerospike Database. It accepts Gremlin bytecode, applies TinkerPop provider
strategies, and turns the resulting physical steps into Database commands. The
separation is genuine: AGS instances can be added without moving graph records,
and Database nodes can rebalance partitions without assigning graph shards to
AGS. That is a strong operational property for read-heavy workloads because
query compute and record capacity can be scaled independently. It is not the
same as limitless independent scaling. More AGS instances create more client
connections, batches, secondary-index queries, and scans against the same
Database cluster. Once that tier reaches its CPU, device, query-thread, or
network limit, another AGS instance mostly increases contention.

The source also makes clear why bounded, ID-rooted traversal is the favorable
case. A vertex ID maps to one record key, known IDs can be grouped into batch
commands, and ordinary adjacency carries enough endpoint information for some
provider strategies to avoid materializing an edge object. The behavior changes
at several cliffs. An unindexed root can become a global scan. A large-degree
vertex crosses into the supernode representation and relies on specialized
secondary indexes. A property path that projects full edges cannot use the same
shortcut as `out()`. A packed edge update rewrites a shared Database record and
can contend with otherwise unrelated edges in the same pack. A useful latency
claim therefore names the root access method, degree bucket, projection, cache
mode, pack size, Database storage mode, and concurrency. A single p99 number for
Gremlin hides too many different physical paths.

One small line from the pinned configuration source captures a larger design
decision. The literal extract is intentionally short:

```java
put(Keys.PHAT_EDGE_SIZE, "10");
```

That default comes from
[`ConfigurationHelper.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java).
Ten logical edges share a packed record by default. The choice saves primary
index entries and amortizes record operations, but it also defines a false
sharing domain for mutations. The source validates a range from one to one
hundred and treats the setting as immutable once data exists because the edge
ID determines its storage record. This is not merely a throughput knob. It is a
physical-format parameter that belongs in every dataset and benchmark manifest.

The same reasoning prevents an S3 conclusion from being inferred from backup
or bulk loading. Spark can read source files from S3, and Database backup tools
can write objects to S3, but the online record and index authority remains the
Aerospike namespace. The live path still pays for Database nodes, replica
copies, primary and secondary index memory, storage headroom, migrations, and
the commercial feature set selected for the run. Aerospike Graph can fit inside
a fixed provisioned envelope, but its public contract is not an S3-native graph
whose authoritative bytes can sit idle at object-storage cost.

| Question | Aerospike Graph answer | Consequence for the target engine |
| --- | --- | --- |
| Where is authoritative graph state? | Aerospike Database records and indexes | S3 authority requires a different storage design, not a configuration change |
| What scales independently? | Stateless AGS query compute and Database capacity | Measure the saturation point of both tiers and the pressure one creates on the other |
| What is the favorable query shape? | Known-ID, bounded traversal over ordinary-degree vertices | Benchmark root path and degree regime rather than averaging all traversals |
| What changes at high degree? | One-way transition to specialized supernode storage and secondary-index access | Treat the threshold as a physical-plan discontinuity |
| What supplies graph mutation atomicity? | SC namespace plus explicitly enabled MRT or transaction support | Do not infer atomic graph updates from replication alone |
| What does object storage do? | Bulk input and backup destination | Charge restore and loading separately; do not call it online S3 serving |
| What public scale is demonstrated? | Tens of billions of vertices and edges in a vendor identity workload | Valuable evidence, but not PB, trillion-edge, or universal-query proof |

## Evidence precedence

A reproducible observation from a pinned, shipped artifact outranks documentation. For supported-product claims, the released 3.2.3 documentation outranks the 3.3.0-SNAPSHOT development tree. The pinned source remains authoritative for the implementation at that commit, but it does not establish the contents of the 3.2.3 container.

Release notes establish declared changes. They do not establish the size of a performance improvement outside the workload used by Aerospike. Vendor benchmark numbers remain vendor results until the raw artifacts are available and the run can be repeated independently. Blog posts provide useful engineering context but are not the sole oracle for semantics or durability.

When commercial internals, contract terms, or benchmark artifacts are unavailable, this dossier records the answer as unknown. It does not fill an evidence gap with an optimistic extrapolation.

## Fifty decision-relevant findings

<table>
<thead>
<tr>
<th>ID</th>
<th>Finding</th>
<th>Technical conclusion</th>
<th>Evidence</th>
</tr>
</thead>
<tbody>
<tr>
<td>F01</td>
<td>Current release</td>
<td>3.2.3 is the newest released version in the official release index on the research date.</td>
<td>S01,S02</td>
</tr>
<tr>
<td>F02</td>
<td>Source head</td>
<td>The audited public AGS branch is 3.x-dev and declares 3.3.0-SNAPSHOT; signed v3.3.0-rc5 appeared on the research date.</td>
<td>S33,S46</td>
</tr>
<tr>
<td>F03</td>
<td>Open source</td>
<td>AGS source carries Apache-2.0; the underlying Community Database core is AGPL while Enterprise features are commercial.</td>
<td>S32,S33,S43</td>
</tr>
<tr>
<td>F04</td>
<td>Protocol</td>
<td>Clients send TinkerPop 3.7.x Gremlin bytecode over WebSocket; 3.8.x and 4.x are incompatible.</td>
<td>S09,S16,S33,S45</td>
</tr>
<tr>
<td>F05</td>
<td>Compute</td>
<td>AGS instances are durable-state-free compute nodes and can be load balanced without AGS-to-AGS coordination.</td>
<td>S09,S35</td>
</tr>
<tr>
<td>F06</td>
<td>Storage authority</td>
<td>Aerospike Database is authoritative; object storage is not on the online read/write path.</td>
<td>S09,S20,S22,S31</td>
</tr>
<tr>
<td>F07</td>
<td>Vertex layout</td>
<td>A normal vertex maps to one record and carries label, properties, and cached adjacency.</td>
<td>S27,S34,S36</td>
</tr>
<tr>
<td>F08</td>
<td>Edge layout</td>
<td>Logical edges are packed into shared edge records; the source default is 10 and accepted range is 1–100.</td>
<td>S34,S37</td>
</tr>
<tr>
<td>F09</td>
<td>Hop cost</td>
<td>An ordinary traversal can exploit embedded adjacency and batch fetches, but it is not literally one storage read for every out() result.</td>
<td>S34,S36,S39</td>
</tr>
<tr>
<td>F10</td>
<td>Supernodes</td>
<td>Large-degree vertices irreversibly leave the inline adjacency path and use secondary-index-backed edge records.</td>
<td>S12,S34</td>
</tr>
<tr>
<td>F11</td>
<td>Threshold</td>
<td>Documentation estimates ~6,500 edges at 1 MiB max-record-size and ~800 at 128 KiB in HMA mode.</td>
<td>S12</td>
</tr>
<tr>
<td>F12</td>
<td>Indexes</td>
<td>Vertex label/property indexes are supported; global edge label/property indexes are absent in the audited source design.</td>
<td>S11,S34</td>
</tr>
<tr>
<td>F13</td>
<td>Scan hazard</td>
<td>Global V()/E() patterns may scan; 3.2.0 added global and per-traversal scan disable controls.</td>
<td>S05,S11</td>
</tr>
<tr>
<td>F14</td>
<td>Optimizer</td>
<td>The code exposes more than twenty traversal strategies for batching, pushdown, local counts, IDs, caching, drop, and merge.</td>
<td>S39</td>
</tr>
<tr>
<td>F15</td>
<td>Default execution</td>
<td>A query normally uses one Gremlin worker; per-query parallelize is intended for I/O-heavy high-fanout work.</td>
<td>S13,S37</td>
</tr>
<tr>
<td>F16</td>
<td>Read cache</td>
<td>Transactional cache is default and request-local; global cache can be stale even after AGS writes.</td>
<td>S14,S37</td>
</tr>
<tr>
<td>F17</td>
<td>Read consistency</td>
<td>The shipped transaction page explicitly classifies read-only queries as eventual-consistency reads.</td>
<td>S10</td>
</tr>
<tr>
<td>F18</td>
<td>Mutation consistency</td>
<td>Atomic/isolated multi-record graph mutations require SC plus enabled MRT on Enterprise Database 8+.</td>
<td>S10</td>
</tr>
<tr>
<td>F19</td>
<td>AP risk</td>
<td>AP mode lacks MRT/TinkerPop transactions and can lose writes during splits; only enumerated mutation forms are atomic.</td>
<td>S10</td>
</tr>
<tr>
<td>F20</td>
<td>Transaction limit</td>
<td>A TinkerPop transaction can modify at most 4096 records and cannot use scans or indexes.</td>
<td>S10</td>
</tr>
<tr>
<td>F21</td>
<td>Supernode drop</td>
<td>Dropping a supernode is best-effort even in the documented transaction mode.</td>
<td>S10,S36</td>
</tr>
<tr>
<td>F22</td>
<td>MRT default</td>
<td>Both aerospike.graph.mrt.enabled and aerospike.graph.tx.enabled default false in source.</td>
<td>S37</td>
</tr>
<tr>
<td>F23</td>
<td>Release storage change</td>
<td>3.0 introduced a new data layout and vendor-claimed up to 50% lower footprint; migration/reload must be qualified.</td>
<td>S08,S26</td>
</tr>
<tr>
<td>F24</td>
<td>3.2 cache</td>
<td>Global cache arrived in 3.2.0 and is a correctness/performance mode, not a transparent optimization.</td>
<td>S05,S14</td>
</tr>
<tr>
<td>F25</td>
<td>3.2 scan claim</td>
<td>3.2.0 claims 10x faster g.E() scans, which is version-over-version and not competitor evidence.</td>
<td>S05</td>
</tr>
<tr>
<td>F26</td>
<td>3.2 security</td>
<td>3.2.3 lists fourteen CVE fixes, so earlier 3.2 images should not be baseline candidates.</td>
<td>S02</td>
</tr>
<tr>
<td>F27</td>
<td>Bulk path</td>
<td>Large loads are external Spark jobs and may stage input on S3/GCS; Spark cost must be charged.</td>
<td>S20,S21</td>
</tr>
<tr>
<td>F28</td>
<td>3.0 ingest claim</td>
<td>The launch blog reports 1 TB under three hours versus more than 32 hours on 2.6 using the same infrastructure.</td>
<td>S26</td>
</tr>
<tr>
<td>F29</td>
<td>Published large run</td>
<td>The identity benchmark reaches 38.3B vertices, 37.2B edges, and 23.35TB user data.</td>
<td>S25</td>
</tr>
<tr>
<td>F30</td>
<td>Benchmark workload shape</td>
<td>The dataset is many sparse localized subgraphs, not one deep/high-diameter or supernode-heavy graph.</td>
<td>S25</td>
</tr>
<tr>
<td>F31</td>
<td>Benchmark topology</td>
<td>Largest latency run used 18 database nodes, one 8-vCPU AGS, RF2, and HMA on local NVMe.</td>
<td>S25</td>
</tr>
<tr>
<td>F32</td>
<td>Throughput claim</td>
<td>The vendor reports 22K QPS on one AGS to over 600K on 32 AGS nodes with fixed storage.</td>
<td>S25</td>
</tr>
<tr>
<td>F33</td>
<td>Missing raw data</td>
<td>The PDF charts do not provide a machine-readable raw latency sample bundle or exact query source archive.</td>
<td>S25</td>
</tr>
<tr>
<td>F34</td>
<td>No comparison</td>
<td>The identity report contains no same-hardware competitor run and cannot support a 10x competitor claim.</td>
<td>S25</td>
</tr>
<tr>
<td>F35</td>
<td>No PB proof</td>
<td>Neither current public benchmark nor release material demonstrates a PB live graph.</td>
<td>S01,S25,S26</td>
</tr>
<tr>
<td>F36</td>
<td>No trillion-edge proof</td>
<td>37.2B edges is substantial but ~27x below one trillion and ~27,000x below one quadrillion.</td>
<td>S25</td>
</tr>
<tr>
<td>F37</td>
<td>Primary-index pressure</td>
<td>Edge packing reduces record count and therefore underlying primary-index metadata, but vertices remain record-per-vertex.</td>
<td>S34,S43</td>
</tr>
<tr>
<td>F38</td>
<td>Resource floor</td>
<td>AGS is a JVM/TinkerPop service plus an Aerospike cluster; one process RSS is not the system resource footprint.</td>
<td>S09,S35</td>
</tr>
<tr>
<td>F39</td>
<td>Cost boundary</td>
<td>Enterprise pricing is contact-only and primarily unique-production-data-volume based.</td>
<td>S28</td>
</tr>
<tr>
<td>F40</td>
<td>CE boundary</td>
<td>Community Edition is free but capped at 8 nodes and 2.5TB on the current edition page and lacks key enterprise features.</td>
<td>S28</td>
</tr>
<tr>
<td>F41</td>
<td>S3 mismatch</td>
<td>S3 lowers load/backup storage cost but cannot replace the live namespace without changing the engine.</td>
<td>S20,S22,S31</td>
</tr>
<tr>
<td>F42</td>
<td>Backup</td>
<td>Graph backup delegates to Aerospike backup/restore; consistency, indexes, metadata, and restore time need an end-to-end drill.</td>
<td>S22</td>
</tr>
<tr>
<td>F43</td>
<td>Multi-tenancy</td>
<td>Graphs can share a namespace, but logical tenancy does not prove performance or failure isolation.</td>
<td>S24</td>
</tr>
<tr>
<td>F44</td>
<td>Security layers</td>
<td>Client-to-AGS TLS/JWT and AGS-to-Database TLS/RBAC are distinct configurations and failure domains.</td>
<td>S23</td>
</tr>
<tr>
<td>F45</td>
<td>Rack-aware reads</td>
<td>AGS 3.2.1 exposes Aerospike client rack awareness; it affects locality, not data placement by itself.</td>
<td>S04,S44</td>
</tr>
<tr>
<td>F46</td>
<td>Observability</td>
<td>Prometheus, health, query tracing, scan profiling, cache stats, and database stats must be correlated.</td>
<td>S18,S19</td>
</tr>
<tr>
<td>F47</td>
<td>Conflict: client version</td>
<td>The source POM pins 10.3.0 while its compatibility prose says 9.3.x; the POM wins for that commit.</td>
<td>S33</td>
</tr>
<tr>
<td>F48</td>
<td>Conflict: MRT minimum</td>
<td>Shipped docs require EE 8.0+, while source prose contains broader 7.0+/6.0 statements; qualify against shipped docs.</td>
<td>S10,S33</td>
</tr>
<tr>
<td>F49</td>
<td>Upgrade evidence</td>
<td>The public tags observed are 3.3 release candidates; no tag maps the audited source to the 3.2.3 shipped image, so source-to-binary equivalence is unproven.</td>
<td>S02,S33,S46</td>
</tr>
<tr>
<td>F50</td>
<td>zu opportunity</td>
<td>S3 authority, compact immutable adjacency, bounded caching, vectorized native execution, and transparent cost counters target its gaps.</td>
<td>inference</td>
</tr>
</tbody>
</table>

## Immediate competitive stance

| Goal | Aerospike posture | Qualification consequence |
| --- | --- | --- |
| Very low latency | Strong candidate for bounded ID-rooted traversals on HMA/NVMe | Split normal, threshold, and supernode regimes; report p50/p95/p99/p99.9 and backend operations |
| Very low resources | Edge packing helps DB metadata; AGS JVM and PI/SI RAM remain | Charge all AGS, DB replicas, Spark, page cache, and storage headroom |
| Distributed | Stateless compute over sharded replicated DB | Test compute scale and storage saturation separately |
| Fixed cost | Commercial licensing is data-volume based; infra is provisioned | Cannot label fixed-cost without a quoted contract and capacity envelope |
| S3 authority | Unsupported for live graph | Treat as architectural non-fit, not a tuning gap |
| PB/trillion scale | Public proof stops at tens of TB/billions | Require derived capacity plus staged empirical validation |
| 10x | No comparable public proof | Claim only per workload cell under equal semantics and resources |

## Open evidence that blocks stronger conclusions

<table>
<thead>
<tr>
<th>ID</th>
<th>Open question</th>
<th>What is missing</th>
<th>Closure condition</th>
</tr>
</thead>
<tbody>
<tr>
<td>U01</td>
<td>3.2.3 source equivalence</td>
<td>No public tag or attestation maps the audited 3.3 snapshot to the shipped 3.2.3 image.</td>
<td>Archive image/SBOM and request vendor source provenance.</td>
</tr>
<tr>
<td>U02</td>
<td>Raw benchmark samples</td>
<td>The public identity PDF provides charts and summaries but no raw HDR/sample archive.</td>
<td>Obtain raw output or rerun from a published harness.</td>
</tr>
<tr>
<td>U03</td>
<td>Exact benchmark Gremlin</td>
<td>Descriptions of SR1–SR5 and SW1–SW5 are not executable query definitions.</td>
<td>Publish bytecode/scripts, parameters, and result-cardinality distributions.</td>
</tr>
<tr>
<td>U04</td>
<td>Benchmark cache state</td>
<td>The report does not fully specify AGS/database cache preconditioning for every graph.</td>
<td>Run named cold, warm, and steady-state phases.</td>
</tr>
<tr>
<td>U05</td>
<td>Benchmark errors/retries</td>
<td>The report does not expose per-query timeout, error, and retry counts alongside QPS.</td>
<td>Require offered/achieved load and all outcomes.</td>
</tr>
<tr>
<td>U06</td>
<td>Current 3.2 performance</td>
<td>The large identity run used AGS 2.4.2, not 3.2.3.</td>
<td>Repeat on 3.2.3 with Database 8.1.2 and publish deltas.</td>
</tr>
<tr>
<td>U07</td>
<td>Independent competitor results</td>
<td>No same-hardware Neo4j, TigerGraph, Neptune, JanusGraph, FalkorDB, Kuzu, or zu run is cited.</td>
<td>Use the cross-engine protocol in specification 06.</td>
</tr>
<tr>
<td>U08</td>
<td>PB deployment</td>
<td>No public configuration demonstrates a PB live graph with query SLOs.</td>
<td>Build capacity model, then validate by a scale ladder.</td>
</tr>
<tr>
<td>U09</td>
<td>Trillion-edge deployment</td>
<td>The largest cited public run is 37.2B edges.</td>
<td>Do not extrapolate linearly through supernode, index, and operational limits.</td>
</tr>
<tr>
<td>U10</td>
<td>Graph license quote</td>
<td>The public page explains general data-volume pricing but not a reproducible Graph quote.</td>
<td>Obtain written quote including SC/MRT, DR, non-prod, and support.</td>
</tr>
<tr>
<td>U11</td>
<td>Graph on Community Edition</td>
<td>3.2.2 removed a feature check, but the supported production combination and limitations remain ambiguous.</td>
<td>Run basic compatibility and obtain a support statement.</td>
</tr>
<tr>
<td>U12</td>
<td>Unique-data accounting</td>
<td>It is unclear which logical/physical graph bytes enter commercial billing.</td>
<td>Reconcile contract definitions with record/index/replica expansion.</td>
</tr>
<tr>
<td>U13</td>
<td>Exact record expansion 3.2</td>
<td>Source documents explain layout but do not replace measured physical bytes for each workload.</td>
<td>Inspect namespace/storage statistics and backups on the pinned image.</td>
</tr>
<tr>
<td>U14</td>
<td>Global cache freshness bound</td>
<td>Documentation says cache can be stale but gives no maximum staleness.</td>
<td>Treat it as unbounded until an invalidation/freshness mechanism is proven.</td>
</tr>
<tr>
<td>U15</td>
<td>Read snapshot semantics</td>
<td>Read-only traversals are eventual, but exact per-hop snapshot guarantees are not stated.</td>
<td>Run concurrent graph-history tests across multi-hop queries.</td>
</tr>
<tr>
<td>U16</td>
<td>AP partial-write repair</td>
<td>Source design hides partial adjacency, but operational reclamation guarantees are not fully quantified.</td>
<td>Inject failures and measure stranded bytes and repair behavior.</td>
</tr>
<tr>
<td>U17</td>
<td>Supernode drop completion</td>
<td>Best-effort is documented without a universal completion/RTO guarantee.</td>
<td>Test degree ladder, faults, retries, and post-drop audits.</td>
</tr>
<tr>
<td>U18</td>
<td>Index build isolation</td>
<td>Release/docs describe asynchronous creation but not an SLO under concurrent production load.</td>
<td>Measure CPU/RAM/I/O and short-query p99.9 during build/drop.</td>
</tr>
<tr>
<td>U19</td>
<td>Migration tail at scale</td>
<td>Stateless AGS scaling does not establish query tails while DB partitions rebalance.</td>
<td>Fault/add/remove nodes under open-loop traffic.</td>
</tr>
<tr>
<td>U20</td>
<td>Restore query-ready RTO</td>
<td>Backup delegation alone does not establish full graph recovery including indexes and metadata.</td>
<td>Time complete restore and semantic verification drills.</td>
</tr>
<tr>
<td>U21</td>
<td>Cross-region graph consistency</td>
<td>XDR branding does not define atomic ordering of related graph records remotely.</td>
<td>Record remote histories for vertex/edge mutations and conflict.</td>
</tr>
<tr>
<td>U22</td>
<td>OLAP maturity</td>
<td>Source contains a Spark GraphComputer path, but current product support/performance coverage is not established here.</td>
<td>Qualify algorithms separately from online Gremlin.</td>
</tr>
<tr>
<td>U23</td>
<td>Long-running query admission</td>
<td>Scan disable helps, but fleet-wide resource governance and fairness need empirical proof.</td>
<td>Mix scans/supernodes with latency-critical point traffic.</td>
</tr>
<tr>
<td>U24</td>
<td>Container resource formula</td>
<td>3.2.1 is container-aware, but actual heap/native/RSS behavior depends on runtime flags and workload.</td>
<td>Measure cgroup limits, OOM, GC, and direct memory.</td>
</tr>
<tr>
<td>U25</td>
<td>Source documentation drift</td>
<td>POM/client and MRT compatibility prose conflict inside the public snapshot.</td>
<td>Prefer executable metadata and open upstream issues for drift.</td>
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
<td>S05</td>
<td>AGS 3.2.0 release notes</td>
<td>Official documentation</td>
<td>Global cache, set cardinality, performance changes</td>
<td>https://aerospike.com/docs/graph/release/3-2-0/</td>
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
<td>S12</td>
<td>Supernodes</td>
<td>Official documentation</td>
<td>Thresholds and filtered traversal guidance</td>
<td>https://aerospike.com/docs/graph/develop/query/supernodes/</td>
</tr>
<tr>
<td>S14</td>
<td>Cache management</td>
<td>Official documentation</td>
<td>Transactional and global record caches</td>
<td>https://aerospike.com/docs/graph/manage/cache/</td>
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
<td>S28</td>
<td>Product editions and pricing</td>
<td>Official commercial page</td>
<td>Edition limits and data-volume licensing</td>
<td>https://aerospike.com/products/features-and-editions/</td>
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
<td>S43</td>
<td>Database server source snapshot</td>
<td>AGPL/community core source</td>
<td>Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
<td>https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc</td>
</tr>
<tr>
<td>S46</td>
<td>AGS v3.3.0-rc5 prerelease tag</td>
<td>Signed public source tag</td>
<td>Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
</tr>
</tbody>
</table>
