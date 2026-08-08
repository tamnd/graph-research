# Aerospike Graph operations, resources, security, S3, and cost audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: Production topology, resource accounting, observability, backup, tenancy, security, and economic fit
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Operational conclusion

Aerospike Graph can separate query compute from storage capacity, but it is not a serverless object-store graph. The minimum production system has a load-balanced AGS fleet and an Aerospike Database cluster; large initial loads add Spark; tracing adds Zipkin-compatible infrastructure; monitoring adds Prometheus; backups add temporary capacity and object storage. All must appear in the resource and cost denominator.

The low-resource story is workload-dependent. Edge packing lowers underlying record count. HMA keeps record data on NVMe while retaining primary and secondary index structures in RAM. AGS has JVM heap, off-heap/native buffers, thread stacks, code cache, record/path objects, caches, queues, and client connections. Global cache can trade database I/O for fleet RAM and weaker freshness. A claim based only on AGS heap or only on database RAM is incomplete.

## S3 and fixed-cost verdict

S3 or GCS can hold bulk-loader input. Spark reads those objects and writes authoritative Aerospike records. Backup tooling can also write object storage, but online queries do not demand-page the live graph from S3. Current Database documentation favors ABS and `absctl`, while the Graph page still points at the legacy `asbackup` path. The chosen tool therefore needs a Graph-specific restore drill rather than a generic Database assumption.

An Aerospike namespace uses memory, device, or file-backed storage modes. S3 is not a namespace storage engine in the cited Graph contract. The published Enterprise pricing model is primarily based on unique production data volume, with additional feature uplifts, so the license varies with graph size even when query count is unmetered.

Provisioned infrastructure can be held inside a budget, but the word fixed only applies inside a declared capacity and SLO envelope. Replica copies, free-space headroom, secondary indexes, backup retention, restore capacity, migrations, and operator time all grow with the deployment. Community Edition, capped publicly at 2.5 TB and eight nodes, cannot establish the PB case.

## Full resource ledger

| Tier | Charge | Reporting scope |
| --- | --- | --- |
| AGS JVM | heap committed/used, GC, threads, code cache, direct/native, RSS | per instance and fleet total |
| AGS caches | transactional/global weights, hit/miss, supernode ID cache | per graph per instance |
| AGS queues | Gremlin queue, event loops, page queues, parallel read executor | peak and steady |
| Database RAM | primary index, secondary indexes, set indexes, metadata, buffers | per node and RF total |
| Database storage | live bytes, write blocks, fragmentation/free headroom, replica bytes | physical allocated and used |
| Database I/O | read/write IOPS, bytes, latency, defrag and migration I/O | per device/node |
| Network | client↔AGS, AGS↔DB, replication, migration, backup, cross-zone | bytes and billed topology |
| Spark loader | driver/executors, shuffle, temp storage, S3 requests/egress | job-hour total |
| Backup | snapshot/read load, staging, object bytes, requests, restore cluster | per retention policy |
| Observability | metrics cardinality, trace sampling/storage, log volume | monthly total |
| License/support | unique data, add-ons, support tier, non-prod/DR terms | contracted monthly amortization |
| Operations | on-call, upgrades, rebalances, restore drills, capacity engineering | human and downtime cost |

A measurement run should produce one machine-readable ledger, even if the commercial price fields remain redacted. Keeping the schema beside the raw samples prevents a later chart from silently dropping a tier.

```yaml
run_id: ags-3.2.3-id-hop-rf2-001
software:
  ags_image_digest: "sha256:replace-with-observed-digest"
  database_build: "replace-with-observed-build"
topology:
  ags_instances: 2
  database_nodes: 3
  replication_factor: 2
resources:
  ags_rss_bytes: []
  database_primary_index_bytes: []
  database_secondary_index_bytes: []
  device_bytes_allocated: []
traffic:
  client_to_ags_bytes: 0
  ags_to_database_bytes: 0
  replication_bytes: 0
cost:
  compute_usd: null
  storage_usd: null
  license_usd: null
  operator_hours: null
```

`null` means unknown, not zero. That distinction matters most for license and operator cost, where public documentation cannot supply a reproducible number.

## Security boundary

Client-to-AGS TLS and AGS-to-Database TLS are separate configurations. Both legs need packet-level verification and certificate-rotation tests. Graph-level JWT RBAC controls Gremlin and HTTP operations, while Database RBAC protects the backend credentials used by AGS.

Graph names and role mappings provide logical tenancy. They do not establish isolation from resource starvation, cache leakage, index-name collisions, log exposure, or shared backups. Audit logging also consumes CPU, I/O, and storage, and its user attribution depends on the Graph authorization layer being configured correctly.

Release 3.2.3 is a dependency security patch, which makes image patch discipline part of the production control set. Secrets can surface independently through environment variables, property files, Helm values, logs, traces, and process inspection; each path needs its own test.

## Operational and economic qualification cases

### Cache memory is a fleet decision

The pinned cache implementation starts in transactional mode:

```java
private CacheMode cacheMode = CacheMode.TRANSACTIONAL;
```

That line is from
[`CacheManager.java`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/CacheManager.java).
The same class maintains global per-graph caches and a global supernode edge-ID
cache when the mode changes. Its weight unit is not raw bytes. Consequently, a
configuration value cannot be copied directly into a cost sheet. The operator
must measure heap occupancy, retained object shape, entry count, hit rate, and
RSS for the actual graph. A load-balanced fleet multiplies that state because
each AGS instance owns an independent cache.

Database memory must be reported separately. HMA can place record data on NVMe
while keeping primary-index and selected secondary-index structures in memory.
Edge packing reduces edge record count, but every vertex still has a record and
every replica keeps its required physical state. Supernode indexes, user vertex
indexes, set indexes, buffers, migration headroom, and defragmentation free
space add to the live footprint. Reporting only namespace user bytes or only
AGS heap makes the system look smaller than the production topology.

Backup cost is also a query-readiness problem rather than an object-copy
problem. A valid drill captures a consistent backup with the selected current
tool, restores metadata and records into a clean cluster, recreates or verifies
indexes, starts AGS against the recovered data-model version, and runs semantic
checks before stopping the RTO clock. S3 object size and request cost are only
part of that path. Restore nodes, network, temporary storage, index rebuild
load, and operator time usually dominate the deadline.

| Cost boundary | Often omitted | Required accounting |
| --- | --- | --- |
| AGS compute | Direct memory, thread stacks, load balancer, duplicated caches | Fleet RSS, CPU, GC, connections, cache bytes, and HA minimum |
| Database memory | Primary and secondary indexes when data sits on NVMe | Per-node and replica-total index memory plus buffers |
| Database storage | Replica bytes, free-space headroom, defrag and migration overlap | Allocated, used, rewritten, and temporary bytes |
| Bulk loading | Spark driver, workers, shuffle, staging, and failed retries | Complete job-hour, storage, request, and egress ledger |
| Backup and restore | Restore cluster and query-ready verification | Object requests, network, compute, index work, RPO, RTO, and labor |
| Commercial terms | SC, MRT, XDR, DR, support, and non-production environments | Written quote and billable unique-data definition |

Operational cases use tagged cloud resources and the ledger schema above. Fleet totals include both AGS and Database tiers, replicas, load balancers, Spark jobs, backup staging, metrics, traces, logs, and any temporary restore cluster. Measurements report RSS as well as JVM heap, primary and secondary index memory, allocated and used device bytes, network by path, and the price term used for every line item.

Security cases save the effective configuration and exercise certificate rotation, expired credentials, role changes, tenant boundaries, audit attribution, and secret redaction. Backup cases end only after a query-ready restore and semantic verification. Missing commercial price or labor inputs stay null, because treating them as zero would manufacture a low-cost result.

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
<td>operations: one AGS idle floor</td>
<td>Measure minimum RSS/CPU/threads/connections.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q002</td>
<td>operations: two AGS HA floor</td>
<td>Charge redundant stateless compute and load balancer.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q003</td>
<td>operations: AGS heap cap</td>
<td>Validate container-aware sizing and OOM behavior.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q004</td>
<td>operations: AGS direct memory</td>
<td>Detect native growth not visible in heap.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q005</td>
<td>operations: AGS thread stacks</td>
<td>Charge Gremlin, event-loop, cache, pager, and parallel workers.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q006</td>
<td>operations: transactional cache weight</td>
<td>Relate weight units to real heap by record shape.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q007</td>
<td>operations: global cache weight</td>
<td>Relate hot-set improvement to fleet memory.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q008</td>
<td>operations: multi-tenant caches</td>
<td>Measure per-graph multiplication and eviction fairness.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q009</td>
<td>operations: normal traversal allocation</td>
<td>Record bytes allocated per result and hop.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q010</td>
<td>operations: supernode traversal allocation</td>
<td>Bound edge-ID/result materialization.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q011</td>
<td>operations: slow client buffering</td>
<td>Bound heap and queue occupancy.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q012</td>
<td>operations: Prometheus scrape</td>
<td>Measure endpoint cost and metric cardinality.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q013</td>
<td>operations: 100% Zipkin sampling</td>
<td>Quantify tracing perturbation.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q014</td>
<td>operations: threshold Zipkin sampling</td>
<td>Preserve slow-query evidence at lower overhead.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q015</td>
<td>operations: log volume</td>
<td>Charge supernode warnings, audit, errors, and access logs.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q016</td>
<td>operations: Database three-node RF2 floor</td>
<td>Measure smallest production-shaped storage footprint.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q017</td>
<td>operations: Database RF3</td>
<td>Measure latency/capacity/recovery tradeoff.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q018</td>
<td>operations: primary index RAM per vertex</td>
<td>Derive PB-scale memory floor.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q019</td>
<td>operations: primary index RAM per edge pack</td>
<td>Quantify benefit of pack size.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q020</td>
<td>operations: vertex label SI RAM</td>
<td>Charge label index.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q021</td>
<td>operations: property SI RAM</td>
<td>Charge each indexed property and type.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q022</td>
<td>operations: supernode SI RAM</td>
<td>Charge mandatory adjacency index entries.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q023</td>
<td>operations: TTL SI RAM</td>
<td>Charge TTL enablement.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q024</td>
<td>operations: storage 50% free</td>
<td>Match vendor benchmark headroom and cost.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q025</td>
<td>operations: storage minimum safe free</td>
<td>Measure defrag/migration risk envelope.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q026</td>
<td>operations: steady-state churn</td>
<td>Capture write amplification and fragmentation.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q027</td>
<td>operations: migration headroom</td>
<td>Prove node loss/addition completes without high-water failure.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q028</td>
<td>operations: local NVMe</td>
<td>Qualify HMA latency and instance-loss recovery.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q029</td>
<td>operations: network block storage</td>
<td>Measure latency tails and provisioned IOPS cost.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q030</td>
<td>operations: in-memory namespace</td>
<td>Separate durability and restart behavior.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q031</td>
<td>operations: all-flash primary index</td>
<td>Qualify edition and latency/resource tradeoff.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q032</td>
<td>operations: S3 bulk input</td>
<td>Charge requests, throughput, Spark, and egress.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q033</td>
<td>operations: GCS bulk input</td>
<td>Charge equivalent cloud path.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q034</td>
<td>operations: standalone bulk loader</td>
<td>Qualify small-load JVM resource floor.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q035</td>
<td>operations: distributed Spark loader</td>
<td>Measure driver/executor/shuffle peak and cost.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q036</td>
<td>operations: bulk resume</td>
<td>Verify idempotence and extra staging bytes.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q037</td>
<td>operations: bulk bad rows</td>
<td>Bound error-record growth and operator workflow.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q038</td>
<td>operations: bulk supernode sampling</td>
<td>Measure driver memory versus classification errors.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q039</td>
<td>operations: bulk index build</td>
<td>Separate write, index, migration, and ready time.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q040</td>
<td>operations: absctl or ABS full graph</td>
<td>Measure throughput, load impact, object requests, bytes, consistency, and whether every Graph set/metadata record is included.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q041</td>
<td>operations: absctl or ABS restore into empty cluster</td>
<td>Measure RTO until query-ready including Graph metadata and indexes.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q042</td>
<td>operations: legacy asbackup/asrestore compatibility</td>
<td>Document why legacy tooling is retained or reject it after restoring and semantically auditing a pinned artifact.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q043</td>
<td>operations: restore to changed topology</td>
<td>Validate redistribution time and headroom.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q044</td>
<td>operations: backup retention 7</td>
<td>Compute object bytes and request cost.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q045</td>
<td>operations: cross-region backup</td>
<td>Charge egress and recovery latency.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q046</td>
<td>operations: TLS client-to-AGS</td>
<td>Measure handshake, connection reuse, CPU, and p99.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q047</td>
<td>operations: TLS AGS-to-DB</td>
<td>Measure per-command crypto and connection behavior.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q048</td>
<td>operations: certificate rotation</td>
<td>Prove no unsafe fallback or outage.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q049</td>
<td>operations: JWT validation</td>
<td>Measure per-request/session cost and expiry.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q050</td>
<td>operations: database RBAC</td>
<td>Verify least privileges and startup/admin requirements.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q051</td>
<td>operations: audit logging</td>
<td>Measure throughput/tail and user attribution.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q052</td>
<td>operations: tenant noisy query</td>
<td>Measure cross-tenant queue/cache/DB interference.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q053</td>
<td>operations: tenant index collision</td>
<td>Verify graph-scoped names and metadata.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q054</td>
<td>operations: tenant backup</td>
<td>Verify restore/isolation granularity.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q055</td>
<td>operations: CVE image scan</td>
<td>Prove 3.2.3 dependency closure and remaining findings.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q056</td>
<td>operations: secret masking</td>
<td>Inspect logs, endpoints, traces, environment, and crash dumps.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q057</td>
<td>operations: Enterprise unique bytes</td>
<td>Reconcile contract bytes with graph physical/logical bytes.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q058</td>
<td>operations: SC/MRT uplift</td>
<td>Add licensed feature cost to transaction result.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q059</td>
<td>operations: support tier</td>
<td>Charge required 24x7 response level.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q060</td>
<td>operations: DR cluster license</td>
<td>Clarify unique data and active cluster treatment.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q061</td>
<td>operations: annual commit</td>
<td>State term and discount; do not call on-demand price.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q062</td>
<td>operations: per-query cost</td>
<td>Amortize full monthly cost at achieved SLO-qualified throughput.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q063</td>
<td>operations: per-billion-edge cost</td>
<td>Include vertices, indexes, replicas, headroom, backup, and license.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q064</td>
<td>operations: PB capacity model</td>
<td>Derive node/RAM/device count with uncertainty bands.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q065</td>
<td>operations: operator hours</td>
<td>Track routine and incident effort.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q066</td>
<td>operations: upgrade drain</td>
<td>Measure capacity and labor during rolling patch.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
</tr>
<tr>
<td>Q067</td>
<td>operations: restore drill</td>
<td>Charge duplicate infrastructure and time.</td>
<td>S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50</td>
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
<td>S14</td>
<td>Cache management</td>
<td>Official documentation</td>
<td>Transactional and global record caches</td>
<td>https://aerospike.com/docs/graph/manage/cache/</td>
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
<td>S37</td>
<td>AGS configuration source</td>
<td>Apache-2.0 source</td>
<td>Code defaults and validators</td>
<td>https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java</td>
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
