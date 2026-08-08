# Aerospike Graph operations, resources, security, S3, and cost audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: Production topology, resource accounting, observability, backup, tenancy, security, and economic fit
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Operational conclusion

Aerospike Graph can separate query compute from storage capacity, but it is not a serverless object-store graph. The minimum production system has a load-balanced AGS fleet and an Aerospike Database cluster; large initial loads add Spark; tracing adds Zipkin-compatible infrastructure; monitoring adds Prometheus; backups add temporary capacity and object storage. All must appear in the resource and cost denominator.

The low-resource story is workload-dependent. Edge packing lowers underlying record count. HMA keeps record data on NVMe while retaining primary and secondary index structures in RAM. AGS has JVM heap, off-heap/native buffers, thread stacks, code cache, record/path objects, caches, queues, and client connections. Global cache can trade database I/O for fleet RAM and weaker freshness. A claim based only on AGS heap or only on database RAM is incomplete.

## S3 and fixed-cost verdict

- S3/GCS may hold bulk-loader input; Spark reads it and writes authoritative Aerospike records.
- Backups may be stored in object storage through Aerospike tools, but online queries do not demand-page the live graph from S3. Current Database documentation favors ABS/absctl while the Graph page still links the legacy asbackup path, so tool choice and Graph completeness must be qualified explicitly.
- An Aerospike namespace uses memory and/or device/file-backed storage modes; S3 is not a namespace storage engine in the cited graph contract.
- The published Enterprise pricing model is primarily based on unique production data volume, with add-on feature uplifts; this is variable with graph size even if query count is free.
- Infrastructure is provisioned capacity with replica and free-space headroom. It can be budgeted, but `fixed cost` only holds inside a declared capacity/SLO envelope.
- Community Edition cannot prove the PB target because the current published cap is 2.5 TB and 8 nodes, and it omits important production features.
- A PB graph also multiplies backups, restores, migrations, secondary indexes, and operational time; stored object bytes alone are not the cost.

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

## Security boundary

- Client-to-AGS and AGS-to-Database TLS are independently configured; verify both with packet capture and certificate rotation.
- Graph-level JWT RBAC controls Gremlin/HTTP graph operations; database RBAC protects AGS's backend credentials.
- Multi-tenant graph routing and role mapping are logical isolation; resource starvation, cache leakage, index names, logs, and backup separation need testing.
- Audit logging requires graph RBAC for user attribution and adds synchronous/asynchronous log cost that must be measured.
- The 3.2.3 dependency CVE patch makes image patch discipline an operational control, not optional hygiene.
- Secrets in environment variables, property files, Helm values, logs, traces, and process inspection need separate controls.

## Operational and economic qualification cases

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — operations: one AGS idle floor

- Purpose: Measure minimum RSS/CPU/threads/connections.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `one AGS idle floor`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — operations: two AGS HA floor

- Purpose: Charge redundant stateless compute and load balancer.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `two AGS HA floor`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — operations: AGS heap cap

- Purpose: Validate container-aware sizing and OOM behavior.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `AGS heap cap`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — operations: AGS direct memory

- Purpose: Detect native growth not visible in heap.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `AGS direct memory`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — operations: AGS thread stacks

- Purpose: Charge Gremlin, event-loop, cache, pager, and parallel workers.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `AGS thread stacks`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — operations: transactional cache weight

- Purpose: Relate weight units to real heap by record shape.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `transactional cache weight`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — operations: global cache weight

- Purpose: Relate hot-set improvement to fleet memory.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `global cache weight`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — operations: multi-tenant caches

- Purpose: Measure per-graph multiplication and eviction fairness.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `multi-tenant caches`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — operations: normal traversal allocation

- Purpose: Record bytes allocated per result and hop.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `normal traversal allocation`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — operations: supernode traversal allocation

- Purpose: Bound edge-ID/result materialization.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `supernode traversal allocation`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — operations: slow client buffering

- Purpose: Bound heap and queue occupancy.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `slow client buffering`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — operations: Prometheus scrape

- Purpose: Measure endpoint cost and metric cardinality.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `Prometheus scrape`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — operations: 100% Zipkin sampling

- Purpose: Quantify tracing perturbation.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `100% Zipkin sampling`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — operations: threshold Zipkin sampling

- Purpose: Preserve slow-query evidence at lower overhead.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `threshold Zipkin sampling`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — operations: log volume

- Purpose: Charge supernode warnings, audit, errors, and access logs.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `log volume`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — operations: Database three-node RF2 floor

- Purpose: Measure smallest production-shaped storage footprint.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `Database three-node RF2 floor`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — operations: Database RF3

- Purpose: Measure latency/capacity/recovery tradeoff.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `Database RF3`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — operations: primary index RAM per vertex

- Purpose: Derive PB-scale memory floor.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `primary index RAM per vertex`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — operations: primary index RAM per edge pack

- Purpose: Quantify benefit of pack size.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `primary index RAM per edge pack`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — operations: vertex label SI RAM

- Purpose: Charge label index.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `vertex label SI RAM`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — operations: property SI RAM

- Purpose: Charge each indexed property and type.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `property SI RAM`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — operations: supernode SI RAM

- Purpose: Charge mandatory adjacency index entries.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `supernode SI RAM`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — operations: TTL SI RAM

- Purpose: Charge TTL enablement.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `TTL SI RAM`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — operations: storage 50% free

- Purpose: Match vendor benchmark headroom and cost.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `storage 50% free`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — operations: storage minimum safe free

- Purpose: Measure defrag/migration risk envelope.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `storage minimum safe free`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — operations: steady-state churn

- Purpose: Capture write amplification and fragmentation.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `steady-state churn`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — operations: migration headroom

- Purpose: Prove node loss/addition completes without high-water failure.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `migration headroom`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — operations: local NVMe

- Purpose: Qualify HMA latency and instance-loss recovery.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `local NVMe`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — operations: network block storage

- Purpose: Measure latency tails and provisioned IOPS cost.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `network block storage`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — operations: in-memory namespace

- Purpose: Separate durability and restart behavior.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `in-memory namespace`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — operations: all-flash primary index

- Purpose: Qualify edition and latency/resource tradeoff.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `all-flash primary index`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — operations: S3 bulk input

- Purpose: Charge requests, throughput, Spark, and egress.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `S3 bulk input`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — operations: GCS bulk input

- Purpose: Charge equivalent cloud path.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `GCS bulk input`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — operations: standalone bulk loader

- Purpose: Qualify small-load JVM resource floor.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `standalone bulk loader`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — operations: distributed Spark loader

- Purpose: Measure driver/executor/shuffle peak and cost.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `distributed Spark loader`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — operations: bulk resume

- Purpose: Verify idempotence and extra staging bytes.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `bulk resume`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — operations: bulk bad rows

- Purpose: Bound error-record growth and operator workflow.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `bulk bad rows`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — operations: bulk supernode sampling

- Purpose: Measure driver memory versus classification errors.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `bulk supernode sampling`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — operations: bulk index build

- Purpose: Separate write, index, migration, and ready time.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `bulk index build`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — operations: absctl or ABS full graph

- Purpose: Measure throughput, load impact, object requests, bytes, consistency, and whether every Graph set/metadata record is included.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `absctl or ABS full graph`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — operations: absctl or ABS restore into empty cluster

- Purpose: Measure RTO until query-ready including Graph metadata and indexes.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `absctl or ABS restore into empty cluster`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — operations: legacy asbackup/asrestore compatibility

- Purpose: Document why legacy tooling is retained or reject it after restoring and semantically auditing a pinned artifact.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `legacy asbackup/asrestore compatibility`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — operations: restore to changed topology

- Purpose: Validate redistribution time and headroom.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `restore to changed topology`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — operations: backup retention 7

- Purpose: Compute object bytes and request cost.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `backup retention 7`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — operations: cross-region backup

- Purpose: Charge egress and recovery latency.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `cross-region backup`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — operations: TLS client-to-AGS

- Purpose: Measure handshake, connection reuse, CPU, and p99.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `TLS client-to-AGS`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — operations: TLS AGS-to-DB

- Purpose: Measure per-command crypto and connection behavior.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `TLS AGS-to-DB`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — operations: certificate rotation

- Purpose: Prove no unsafe fallback or outage.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `certificate rotation`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — operations: JWT validation

- Purpose: Measure per-request/session cost and expiry.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `JWT validation`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — operations: database RBAC

- Purpose: Verify least privileges and startup/admin requirements.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `database RBAC`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — operations: audit logging

- Purpose: Measure throughput/tail and user attribution.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `audit logging`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — operations: tenant noisy query

- Purpose: Measure cross-tenant queue/cache/DB interference.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `tenant noisy query`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — operations: tenant index collision

- Purpose: Verify graph-scoped names and metadata.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `tenant index collision`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — operations: tenant backup

- Purpose: Verify restore/isolation granularity.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `tenant backup`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — operations: CVE image scan

- Purpose: Prove 3.2.3 dependency closure and remaining findings.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `CVE image scan`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — operations: secret masking

- Purpose: Inspect logs, endpoints, traces, environment, and crash dumps.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `secret masking`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — operations: Enterprise unique bytes

- Purpose: Reconcile contract bytes with graph physical/logical bytes.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `Enterprise unique bytes`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — operations: SC/MRT uplift

- Purpose: Add licensed feature cost to transaction result.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `SC/MRT uplift`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — operations: support tier

- Purpose: Charge required 24x7 response level.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `support tier`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — operations: DR cluster license

- Purpose: Clarify unique data and active cluster treatment.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `DR cluster license`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q061 — operations: annual commit

- Purpose: State term and discount; do not call on-demand price.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `annual commit`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q062 — operations: per-query cost

- Purpose: Amortize full monthly cost at achieved SLO-qualified throughput.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `per-query cost`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q063 — operations: per-billion-edge cost

- Purpose: Include vertices, indexes, replicas, headroom, backup, and license.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `per-billion-edge cost`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q064 — operations: PB capacity model

- Purpose: Derive node/RAM/device count with uncertainty bands.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `PB capacity model`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q065 — operations: operator hours

- Purpose: Track routine and incident effort.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `operator hours`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q066 — operations: upgrade drain

- Purpose: Measure capacity and labor during rolling patch.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `upgrade drain`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q067 — operations: restore drill

- Purpose: Charge duplicate infrastructure and time.
- Setup: Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.
- Workload: Execute the smallest semantically complete operation for `restore drill`, then repeat under controlled concurrency and skew.
- Required counters: fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S02 — AGS 3.2.3 release notes

- Type: Official documentation
- Audit note: Security-only patch; 14 CVEs listed
- URL: https://aerospike.com/docs/graph/release/3-2-3/

### S03 — AGS 3.2.2 release notes

- Type: Official documentation
- Audit note: Removed graph-service feature check
- URL: https://aerospike.com/docs/graph/release/3-2-2/

### S04 — AGS 3.2.1 release notes

- Type: Official documentation
- Audit note: Container memory and rack awareness
- URL: https://aerospike.com/docs/graph/release/3-2-1/

### S05 — AGS 3.2.0 release notes

- Type: Official documentation
- Audit note: Global cache, set cardinality, performance changes
- URL: https://aerospike.com/docs/graph/release/3-2-0/

### S14 — Cache management

- Type: Official documentation
- Audit note: Transactional and global record caches
- URL: https://aerospike.com/docs/graph/manage/cache/

### S17 — Configuration reference

- Type: Official documentation
- Audit note: AGS runtime knobs
- URL: https://aerospike.com/docs/graph/reference/config/

### S18 — Metrics reference

- Type: Official documentation
- Audit note: Prometheus metric inventory
- URL: https://aerospike.com/docs/graph/reference/metrics/

### S19 — Query tracing

- Type: Official documentation
- Audit note: Zipkin tracing contract
- URL: https://aerospike.com/docs/graph/observe/query-tracing/

### S20 — Bulk load overview

- Type: Official documentation
- Audit note: Standalone and Spark paths
- URL: https://aerospike.com/docs/graph/load/overview/

### S21 — Distributed bulk load

- Type: Official documentation
- Audit note: EMR and Dataproc workflow
- URL: https://aerospike.com/docs/graph/load/distributed/

### S22 — Graph backup and restore

- Type: Official documentation
- Audit note: Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page
- URL: https://aerospike.com/docs/graph/manage/backup/

### S23 — Security

- Type: Official documentation
- Audit note: TLS, JWT RBAC, database RBAC, audit
- URL: https://aerospike.com/docs/graph/manage/security/

### S24 — Multi-tenancy

- Type: Official documentation
- Audit note: Graph scoping in a shared namespace
- URL: https://aerospike.com/docs/graph/manage/multi-tenant/

### S28 — Product editions and pricing

- Type: Official commercial page
- Audit note: Edition limits and data-volume licensing
- URL: https://aerospike.com/products/features-and-editions/

### S29 — Database platform support

- Type: Official documentation
- Audit note: Current Database release matrix
- URL: https://aerospike.com/docs/database/reference/platform-support

### S30 — Database limits

- Type: Official documentation
- Audit note: Cluster and object limits
- URL: https://aerospike.com/docs/database/reference/limitations/

### S31 — Database storage configuration

- Type: Official documentation
- Audit note: Memory, device, and persistence modes
- URL: https://aerospike.com/docs/database/manage/namespace/storage/config/

### S32 — Database FAQ

- Type: Official documentation
- Audit note: CE/SE/EE/FE boundaries
- URL: https://aerospike.com/docs/database/reference/faq

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S37 — AGS configuration source

- Type: Apache-2.0 source
- Audit note: Code defaults and validators
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java

### S42 — Graph examples

- Type: Apache-2.0 source
- Audit note: Examples at e2300bc201f949c4261ecd88b235dea1877fa088
- URL: https://github.com/aerospike/aerospike-graph/tree/e2300bc201f949c4261ecd88b235dea1877fa088

### S43 — Database server source snapshot

- Type: AGPL/community core source
- Audit note: Server at 3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc
- URL: https://github.com/aerospike/aerospike-server/tree/3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc

### S44 — Java client source snapshot

- Type: Apache-2.0 source
- Audit note: Client at 9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12
- URL: https://github.com/aerospike/aerospike-client-java/tree/9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12

### S49 — Legacy asbackup documentation

- Type: Official documentation
- Audit note: The target of the current Graph backup-page link; explicitly labeled legacy
- URL: https://aerospike.com/docs/database/tools/backup-and-restore/asbackup

### S50 — Current Database backup and restore overview

- Type: Official documentation
- Audit note: ABS and absctl are current choices while asbackup/asrestore are legacy
- URL: https://aerospike.com/docs/database/tools/backup-and-restore/overview/
