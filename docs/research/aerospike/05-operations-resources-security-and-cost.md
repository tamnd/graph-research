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

Operational cases use tagged cloud resources and the ledger schema above. Fleet totals include both AGS and Database tiers, replicas, load balancers, Spark jobs, backup staging, metrics, traces, logs, and any temporary restore cluster. Measurements report RSS as well as JVM heap, primary and secondary index memory, allocated and used device bytes, network by path, and the price term used for every line item.

Security cases save the effective configuration and exercise certificate rotation, expired credentials, role changes, tenant boundaries, audit attribution, and secret redaction. Backup cases end only after a query-ready restore and semantic verification. Missing commercial price or labor inputs stay null, because treating them as zero would manufacture a low-cost result.

### Q001 : operations: one AGS idle floor

**Purpose.** Measure minimum RSS/CPU/threads/connections.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q002 : operations: two AGS HA floor

**Purpose.** Charge redundant stateless compute and load balancer.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q003 : operations: AGS heap cap

**Purpose.** Validate container-aware sizing and OOM behavior.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q004 : operations: AGS direct memory

**Purpose.** Detect native growth not visible in heap.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q005 : operations: AGS thread stacks

**Purpose.** Charge Gremlin, event-loop, cache, pager, and parallel workers.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q006 : operations: transactional cache weight

**Purpose.** Relate weight units to real heap by record shape.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q007 : operations: global cache weight

**Purpose.** Relate hot-set improvement to fleet memory.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q008 : operations: multi-tenant caches

**Purpose.** Measure per-graph multiplication and eviction fairness.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q009 : operations: normal traversal allocation

**Purpose.** Record bytes allocated per result and hop.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q010 : operations: supernode traversal allocation

**Purpose.** Bound edge-ID/result materialization.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q011 : operations: slow client buffering

**Purpose.** Bound heap and queue occupancy.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q012 : operations: Prometheus scrape

**Purpose.** Measure endpoint cost and metric cardinality.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q013 : operations: 100% Zipkin sampling

**Purpose.** Quantify tracing perturbation.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q014 : operations: threshold Zipkin sampling

**Purpose.** Preserve slow-query evidence at lower overhead.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q015 : operations: log volume

**Purpose.** Charge supernode warnings, audit, errors, and access logs.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q016 : operations: Database three-node RF2 floor

**Purpose.** Measure smallest production-shaped storage footprint.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q017 : operations: Database RF3

**Purpose.** Measure latency/capacity/recovery tradeoff.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q018 : operations: primary index RAM per vertex

**Purpose.** Derive PB-scale memory floor.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q019 : operations: primary index RAM per edge pack

**Purpose.** Quantify benefit of pack size.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q020 : operations: vertex label SI RAM

**Purpose.** Charge label index.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q021 : operations: property SI RAM

**Purpose.** Charge each indexed property and type.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q022 : operations: supernode SI RAM

**Purpose.** Charge mandatory adjacency index entries.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q023 : operations: TTL SI RAM

**Purpose.** Charge TTL enablement.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q024 : operations: storage 50% free

**Purpose.** Match vendor benchmark headroom and cost.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q025 : operations: storage minimum safe free

**Purpose.** Measure defrag/migration risk envelope.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q026 : operations: steady-state churn

**Purpose.** Capture write amplification and fragmentation.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q027 : operations: migration headroom

**Purpose.** Prove node loss/addition completes without high-water failure.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q028 : operations: local NVMe

**Purpose.** Qualify HMA latency and instance-loss recovery.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q029 : operations: network block storage

**Purpose.** Measure latency tails and provisioned IOPS cost.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q030 : operations: in-memory namespace

**Purpose.** Separate durability and restart behavior.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q031 : operations: all-flash primary index

**Purpose.** Qualify edition and latency/resource tradeoff.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q032 : operations: S3 bulk input

**Purpose.** Charge requests, throughput, Spark, and egress.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q033 : operations: GCS bulk input

**Purpose.** Charge equivalent cloud path.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q034 : operations: standalone bulk loader

**Purpose.** Qualify small-load JVM resource floor.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q035 : operations: distributed Spark loader

**Purpose.** Measure driver/executor/shuffle peak and cost.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q036 : operations: bulk resume

**Purpose.** Verify idempotence and extra staging bytes.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q037 : operations: bulk bad rows

**Purpose.** Bound error-record growth and operator workflow.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q038 : operations: bulk supernode sampling

**Purpose.** Measure driver memory versus classification errors.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q039 : operations: bulk index build

**Purpose.** Separate write, index, migration, and ready time.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q040 : operations: absctl or ABS full graph

**Purpose.** Measure throughput, load impact, object requests, bytes, consistency, and whether every Graph set/metadata record is included.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q041 : operations: absctl or ABS restore into empty cluster

**Purpose.** Measure RTO until query-ready including Graph metadata and indexes.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q042 : operations: legacy asbackup/asrestore compatibility

**Purpose.** Document why legacy tooling is retained or reject it after restoring and semantically auditing a pinned artifact.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q043 : operations: restore to changed topology

**Purpose.** Validate redistribution time and headroom.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q044 : operations: backup retention 7

**Purpose.** Compute object bytes and request cost.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q045 : operations: cross-region backup

**Purpose.** Charge egress and recovery latency.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q046 : operations: TLS client-to-AGS

**Purpose.** Measure handshake, connection reuse, CPU, and p99.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q047 : operations: TLS AGS-to-DB

**Purpose.** Measure per-command crypto and connection behavior.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q048 : operations: certificate rotation

**Purpose.** Prove no unsafe fallback or outage.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q049 : operations: JWT validation

**Purpose.** Measure per-request/session cost and expiry.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q050 : operations: database RBAC

**Purpose.** Verify least privileges and startup/admin requirements.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q051 : operations: audit logging

**Purpose.** Measure throughput/tail and user attribution.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q052 : operations: tenant noisy query

**Purpose.** Measure cross-tenant queue/cache/DB interference.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q053 : operations: tenant index collision

**Purpose.** Verify graph-scoped names and metadata.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q054 : operations: tenant backup

**Purpose.** Verify restore/isolation granularity.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q055 : operations: CVE image scan

**Purpose.** Prove 3.2.3 dependency closure and remaining findings.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q056 : operations: secret masking

**Purpose.** Inspect logs, endpoints, traces, environment, and crash dumps.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q057 : operations: Enterprise unique bytes

**Purpose.** Reconcile contract bytes with graph physical/logical bytes.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q058 : operations: SC/MRT uplift

**Purpose.** Add licensed feature cost to transaction result.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q059 : operations: support tier

**Purpose.** Charge required 24x7 response level.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q060 : operations: DR cluster license

**Purpose.** Clarify unique data and active cluster treatment.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q061 : operations: annual commit

**Purpose.** State term and discount; do not call on-demand price.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q062 : operations: per-query cost

**Purpose.** Amortize full monthly cost at achieved SLO-qualified throughput.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q063 : operations: per-billion-edge cost

**Purpose.** Include vertices, indexes, replicas, headroom, backup, and license.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q064 : operations: PB capacity model

**Purpose.** Derive node/RAM/device count with uncertainty bands.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q065 : operations: operator hours

**Purpose.** Track routine and incident effort.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q066 : operations: upgrade drain

**Purpose.** Measure capacity and labor during rolling patch.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


### Q067 : operations: restore drill

**Purpose.** Charge duplicate infrastructure and time.

**Evidence anchors.** S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50


## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S02 : AGS 3.2.3 release notes

**Type.** Official documentation

**Audit note.** Security-only patch; 14 CVEs listed

**URL.** https://aerospike.com/docs/graph/release/3-2-3/


### S03 : AGS 3.2.2 release notes

**Type.** Official documentation

**Audit note.** Removed graph-service feature check

**URL.** https://aerospike.com/docs/graph/release/3-2-2/


### S04 : AGS 3.2.1 release notes

**Type.** Official documentation

**Audit note.** Container memory and rack awareness

**URL.** https://aerospike.com/docs/graph/release/3-2-1/


### S05 : AGS 3.2.0 release notes

**Type.** Official documentation

**Audit note.** Global cache, set cardinality, performance changes

**URL.** https://aerospike.com/docs/graph/release/3-2-0/


### S14 : Cache management

**Type.** Official documentation

**Audit note.** Transactional and global record caches

**URL.** https://aerospike.com/docs/graph/manage/cache/


### S17 : Configuration reference

**Type.** Official documentation

**Audit note.** AGS runtime knobs

**URL.** https://aerospike.com/docs/graph/reference/config/


### S18 : Metrics reference

**Type.** Official documentation

**Audit note.** Prometheus metric inventory

**URL.** https://aerospike.com/docs/graph/reference/metrics/


### S19 : Query tracing

**Type.** Official documentation

**Audit note.** Zipkin tracing contract

**URL.** https://aerospike.com/docs/graph/observe/query-tracing/


### S20 : Bulk load overview

**Type.** Official documentation

**Audit note.** Standalone and Spark paths

**URL.** https://aerospike.com/docs/graph/load/overview/


### S21 : Distributed bulk load

**Type.** Official documentation

**Audit note.** EMR and Dataproc workflow

**URL.** https://aerospike.com/docs/graph/load/distributed/


### S22 : Graph backup and restore

**Type.** Official documentation

**Audit note.** Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page

**URL.** https://aerospike.com/docs/graph/manage/backup/


### S23 : Security

**Type.** Official documentation

**Audit note.** TLS, JWT RBAC, database RBAC, audit

**URL.** https://aerospike.com/docs/graph/manage/security/


### S24 : Multi-tenancy

**Type.** Official documentation

**Audit note.** Graph scoping in a shared namespace

**URL.** https://aerospike.com/docs/graph/manage/multi-tenant/


### S28 : Product editions and pricing

**Type.** Official commercial page

**Audit note.** Edition limits and data-volume licensing

**URL.** https://aerospike.com/products/features-and-editions/


### S29 : Database platform support

**Type.** Official documentation

**Audit note.** Current Database release matrix

**URL.** https://aerospike.com/docs/database/reference/platform-support


### S30 : Database limits

**Type.** Official documentation

**Audit note.** Cluster and object limits

**URL.** https://aerospike.com/docs/database/reference/limitations/


### S31 : Database storage configuration

**Type.** Official documentation

**Audit note.** Memory, device, and persistence modes

**URL.** https://aerospike.com/docs/database/manage/namespace/storage/config/


### S32 : Database FAQ

**Type.** Official documentation

**Audit note.** CE/SE/EE/FE boundaries

**URL.** https://aerospike.com/docs/database/reference/faq


### S33 : AGS public source snapshot

**Type.** Apache-2.0 source

**Audit note.** 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045


### S37 : AGS configuration source

**Type.** Apache-2.0 source

**Audit note.** Code defaults and validators

**URL.** https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java


### S42 : Graph examples

**Type.** Apache-2.0 source

**Audit note.** Examples at e2300bc201f949c4261ecd88b235dea1877fa088

**URL.** https://github.com/aerospike/aerospike-graph/tree/e2300bc201f949c4261ecd88b235dea1877fa088


### S43 : Database server source snapshot

**Type.** AGPL/community core source

**Audit note.** Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

**URL.** https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc


### S44 : Java client source snapshot

**Type.** Apache-2.0 source

**Audit note.** Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12

**URL.** https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12


### S49 : Legacy asbackup documentation

**Type.** Official documentation

**Audit note.** The target of the current Graph backup-page link; explicitly labeled legacy

**URL.** https://aerospike.com/docs/database/tools/backup-and-restore/asbackup


### S50 : Current Database backup and restore overview

**Type.** Official documentation

**Audit note.** ABS and absctl are current choices while asbackup/asrestore are legacy

**URL.** https://aerospike.com/docs/database/tools/backup-and-restore/overview/
