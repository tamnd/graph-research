# Aerospike Graph benchmark audit and tenfold-win qualification

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Scope: Deconstruction of published results plus a fair, reproducible competitor protocol
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Published benchmark verdict

The current Aerospike identity-graph report is valuable evidence that one vendor configuration processed a tens-of-billions property graph. It is not an independent benchmark, not a current 3.2 benchmark, not a cross-engine comparison, not PB evidence, and not a universal latency result. Preserve its exact workload shape: many sparse, independent or weakly connected identity subgraphs whose short reads and writes remain localized.

The PDF reports three scale factors. The largest has 3,600 GB input CSV, 38.3 billion vertices, 37.2 billion edges, and 23.35 TB user data. It used 18 `n2d-highmem-64` database nodes with 24×375GB local NVMe each, RF2, one `n2d-standard-8` AGS for latency runs, and an `n2d-standard-32` load generator. The throughput scale test fixed the storage cluster and increased AGS from 1 to 32, reporting 22K to more than 600K QPS. The software was Database 7.1.0.9 and AGS 2.4.2.

The charts do not provide a machine-readable raw sample bundle in the report, exact query text/source repository, optimizer profiles, backend operation counts, error rate, retry accounting, cache state, offered-load schedule, or a competitor result. The reported infrastructure cost uses a one-year commitment and March 5, 2025 GCP prices. These omissions prevent an audit-grade 10x conclusion.

## Published dataset and hardware

| Scale | CSV | Vertices | Edges | User data | DB nodes |
| --- | --- | --- | --- | --- | --- |
| 10M | 35GB | 383M | 373M | 0.219TB | 3 × n2d-highmem-8 |
| 100M | 358GB | 3.83B | 3.73B | 2.306TB | 8 × n2d-highmem-16 |
| 1B | 3,600GB | 38.3B | 37.2B | 23.35TB | 18 × n2d-highmem-64 |

## Published bulk-load results

| Scale | Dataproc worker | Workers | Spark memory | Time |
| --- | --- | --- | --- | --- |
| 10M | n2d-highmem-8 | 30 | 1.875TB | 3.56h |
| 100M | n2d-highmem-16 | 60 | 7.5TB | 8.00h |
| 1B | n2d-highmem-64 | 70 | 35TB | 31.81h |

## Why universal 10x is invalid

- Latency, throughput, resources, cost, load time, freshness, availability, and semantic coverage are different objectives.
- A result is valid only for a workload cell with equal query semantics, durability, replication, consistency, dataset, hardware budget, and completion criteria.
- Unsupported queries cannot be replaced with easier operations or omitted from the geometric mean.
- Timeouts/errors must count as failed requests and remain in the result distribution.
- Open-loop offered load is required to expose queueing; closed-loop clients can hide overload.
- Warm caches must be memory-matched and explicitly disclosed; S3/native cold starts need a separate class.
- Cost claims must use the same region, term, discounts, replicas, storage headroom, licensing, and operational services.
- A 10x claim needs uncertainty intervals and repeat runs; one best run versus one competitor default is not evidence.
- The honest output may be a win/loss frontier: 10x in some cells, parity in others, unsupported or non-comparable elsewhere.

## Cross-engine benchmark cells

Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.

### Q001 — benchmark: ID vertex read cold

- Purpose: Compare authoritative point lookup without cache residency.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `ID vertex read cold`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q002 — benchmark: ID vertex read warm

- Purpose: Compare hot point lookup with charged cache memory.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `ID vertex read warm`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q003 — benchmark: batch 100 vertex IDs

- Purpose: Compare network and storage batching.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `batch 100 vertex IDs`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q004 — benchmark: 1-hop degree 4

- Purpose: Represent small bounded adjacency.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `1-hop degree 4`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q005 — benchmark: 1-hop degree 32

- Purpose: Represent common identity expansion.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `1-hop degree 32`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q006 — benchmark: 1-hop degree 512

- Purpose: Expose batching and response size.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `1-hop degree 512`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q007 — benchmark: threshold-minus-one degree

- Purpose: Stress largest inline adjacency record.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `threshold-minus-one degree`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q008 — benchmark: threshold-plus-one degree

- Purpose: Expose supernode path discontinuity.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `threshold-plus-one degree`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q009 — benchmark: supernode 100K unfiltered

- Purpose: Measure unavoidable output and safety limits.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `supernode 100K unfiltered`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q010 — benchmark: supernode 100K 0.1% filter

- Purpose: Measure server-side predicate pushdown.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `supernode 100K 0.1% filter`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q011 — benchmark: 2-hop fanout 4

- Purpose: Bound frontier and path semantics.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `2-hop fanout 4`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q012 — benchmark: 2-hop fanout 32

- Purpose: Expose intermediate materialization.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `2-hop fanout 32`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q013 — benchmark: 3-hop identity SR5

- Purpose: Recreate vendor workload pattern exactly.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `3-hop identity SR5`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q014 — benchmark: 4-hop cyclic

- Purpose: Measure visited/path work on cycles.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `4-hop cyclic`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q015 — benchmark: label root high selectivity

- Purpose: Compare indexed root planning.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `label root high selectivity`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q016 — benchmark: label root low selectivity

- Purpose: Expose large-index result stream.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `label root low selectivity`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q017 — benchmark: numeric equality index

- Purpose: Compare root filtering.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `numeric equality index`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q018 — benchmark: numeric range index

- Purpose: Compare range path.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `numeric range index`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q019 — benchmark: string substring

- Purpose: Expose unsupported index and scan behavior.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `string substring`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q020 — benchmark: global vertex scan

- Purpose: Compare bandwidth-oriented scan separately.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `global vertex scan`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q021 — benchmark: global edge scan

- Purpose: Reproduce AGS 3.2 version claim and competitors.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `global edge scan`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q022 — benchmark: local count

- Purpose: Compare adjacency metadata optimization.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `local count`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q023 — benchmark: global exact count

- Purpose: Require exact consistent result.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `global exact count`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q024 — benchmark: path materialization

- Purpose: Charge full path objects.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `path materialization`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q025 — benchmark: dedup frontier

- Purpose: Charge state memory.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `dedup frontier`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q026 — benchmark: top-K order

- Purpose: Require same ordering/tie semantics.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `top-K order`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q027 — benchmark: add vertex

- Purpose: Compare durable acknowledged creation.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `add vertex`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q028 — benchmark: update vertex property

- Purpose: Compare contention-free update.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `update vertex property`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q029 — benchmark: add ordinary edge

- Purpose: Compare three-record graph mutation semantics.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `add ordinary edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q030 — benchmark: add hot edge

- Purpose: Compare contention and retries.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `add hot edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q031 — benchmark: update edge property

- Purpose: Expose packed-record false sharing.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `update edge property`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q032 — benchmark: delete edge

- Purpose: Compare cleanup and read visibility.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `delete edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q033 — benchmark: delete ordinary vertex

- Purpose: Compare incident-edge atomicity.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `delete ordinary vertex`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q034 — benchmark: delete supernode

- Purpose: Mark semantic limitation, not comparable success.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `delete supernode`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q035 — benchmark: merge vertex

- Purpose: Require uniqueness and idempotence.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `merge vertex`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q036 — benchmark: merge edge

- Purpose: Require same match/lock semantics.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `merge edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q037 — benchmark: explicit 10-record transaction

- Purpose: Compare atomic multi-query scope.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `explicit 10-record transaction`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q038 — benchmark: explicit 1000-record transaction

- Purpose: Expose transaction overhead.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `explicit 1000-record transaction`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q039 — benchmark: read/write 95/5

- Purpose: Measure mixed online load.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `read/write 95/5`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q040 — benchmark: read/write 50/50

- Purpose: Expose packing contention and cache invalidity.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `read/write 50/50`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q041 — benchmark: scan plus point reads

- Purpose: Measure workload isolation.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `scan plus point reads`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q042 — benchmark: supernode plus point reads

- Purpose: Measure heavy-query isolation.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `supernode plus point reads`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q043 — benchmark: one compute node

- Purpose: Establish resource-normalized baseline.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `one compute node`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q044 — benchmark: 2 compute nodes

- Purpose: Measure scale efficiency.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `2 compute nodes`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q045 — benchmark: 4 compute nodes

- Purpose: Measure scale efficiency.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `4 compute nodes`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q046 — benchmark: 8 compute nodes

- Purpose: Measure storage approach to saturation.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `8 compute nodes`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q047 — benchmark: 16 compute nodes

- Purpose: Locate database/network bottleneck.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `16 compute nodes`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q048 — benchmark: 32 compute nodes

- Purpose: Reproduce vendor throughput topology.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `32 compute nodes`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q049 — benchmark: one DB node dev

- Purpose: Keep out of HA headline but measure floor.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `one DB node dev`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q050 — benchmark: three DB nodes RF2

- Purpose: Production-shaped minimum.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `three DB nodes RF2`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q051 — benchmark: six DB nodes RF2

- Purpose: Measure storage horizontal scaling.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `six DB nodes RF2`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q052 — benchmark: RF3

- Purpose: Compare stronger replica capacity.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `RF3`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q053 — benchmark: rack-aware local

- Purpose: Measure cross-zone avoidance.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `rack-aware local`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q054 — benchmark: rack failure

- Purpose: Measure degraded latency and cost.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `rack failure`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q055 — benchmark: DB node failure

- Purpose: Measure p99.9 and errors through recovery.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `DB node failure`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q056 — benchmark: AGS node failure

- Purpose: Measure load balancer and in-flight requests.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `AGS node failure`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q057 — benchmark: rebalance

- Purpose: Measure performance during add/remove.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `rebalance`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q058 — benchmark: cold restart

- Purpose: Measure query-ready time and cache state.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `cold restart`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q059 — benchmark: rolling patch

- Purpose: Measure operational availability.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `rolling patch`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q060 — benchmark: 1GB load

- Purpose: Small-loader overhead.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `1GB load`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q061 — benchmark: 100GB load

- Purpose: Standalone/distributed crossover.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `100GB load`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q062 — benchmark: 1TB load

- Purpose: Reproduce 3.0 ingest claim.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `1TB load`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q063 — benchmark: 10TB load

- Purpose: Measure scale and Spark cost.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `10TB load`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q064 — benchmark: incremental 1% load

- Purpose: Measure daily refresh economics.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `incremental 1% load`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q065 — benchmark: backup

- Purpose: Measure throughput and online impact.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `backup`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q066 — benchmark: restore

- Purpose: Measure query-ready RTO.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `restore`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q067 — benchmark: storage bytes per edge

- Purpose: Compare physical bytes including indexes/replicas.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `storage bytes per edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q068 — benchmark: RAM bytes per edge

- Purpose: Compare full-cluster resident memory.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `RAM bytes per edge`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q069 — benchmark: CPU per million queries

- Purpose: Compare work efficiency at same SLO.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `CPU per million queries`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q070 — benchmark: joules per million queries

- Purpose: Optional energy efficiency.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `joules per million queries`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q071 — benchmark: monthly cost at 10K QPS

- Purpose: Amortize all provisioned and licensed cost.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `monthly cost at 10K QPS`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q072 — benchmark: monthly cost at 100K QPS

- Purpose: Measure scale and headroom.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `monthly cost at 100K QPS`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q073 — benchmark: monthly cost at 600K QPS

- Purpose: Challenge vendor-scale claim fairly.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `monthly cost at 600K QPS`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q074 — benchmark: cost per billion edges

- Purpose: Include vertex ratio and properties.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `cost per billion edges`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q075 — benchmark: cost per PB logical

- Purpose: Use capacity model with uncertainty.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `cost per PB logical`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q076 — benchmark: S3 cold point read zu

- Purpose: Measure zu's object-authoritative cold path.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `S3 cold point read zu`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q077 — benchmark: S3 warm point read zu

- Purpose: Measure bounded-cache steady state.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `S3 warm point read zu`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q078 — benchmark: S3 outage zu

- Purpose: Preserve system semantics and availability disclosure.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `S3 outage zu`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q079 — benchmark: semantic conformance corpus

- Purpose: Gate performance publication on equal results.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `semantic conformance corpus`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

### Q080 — benchmark: unsupported feature ledger

- Purpose: Prevent silent workload deletion.
- Setup: Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.
- Workload: Execute the smallest semantically complete operation for `unsupported feature ledger`, then repeat under controlled concurrency and skew.
- Required counters: open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars
- Correctness oracle: Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.
- Failure interpretation: Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.
- Evidence anchors: S05,S10–S16,S18,S19,S25,S26,S28,S33–S45
- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.
- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.

## Tenfold claim acceptance rule

Publish `10x` only when the lower 95% confidence bound of the improvement ratio exceeds 10 for the named metric and cell, all correctness gates pass, achieved throughput meets offered load, error/timeout rate is within the common SLO, and total charged resources/cost obey the declared comparison mode. Label the numerator and denominator, version, hardware, cache state, consistency, RF, dataset, query, percentile, and run date in the claim sentence.

Never publish “10x faster than all graph databases.” A defensible sentence is narrower: for example, “zu commit X achieved 10.8–12.1x lower p99 latency than Aerospike Graph 3.2.3 on ID-rooted two-hop traversal Q17 at 20K offered QPS, RF2-equivalent durability, cold 8GB cache, and equal monthly infrastructure cost.”

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S05 — AGS 3.2.0 release notes

- Type: Official documentation
- Audit note: Global cache, set cardinality, performance changes
- URL: https://aerospike.com/docs/graph/release/3-2-0/

### S10 — Transaction contract

- Type: Official documentation
- Audit note: Read, mutation, SC, AP, and MRT distinctions
- URL: https://aerospike.com/docs/graph/develop/query/transactions/

### S11 — Indexing

- Type: Official documentation
- Audit note: Vertex index and scan controls
- URL: https://aerospike.com/docs/graph/develop/query/indexing/

### S12 — Supernodes

- Type: Official documentation
- Audit note: Thresholds and filtered traversal guidance
- URL: https://aerospike.com/docs/graph/develop/query/supernodes/

### S13 — Query threading

- Type: Official documentation
- Audit note: Per-query parallelization and batch/page controls
- URL: https://aerospike.com/docs/graph/develop/query/query-threading/

### S14 — Cache management

- Type: Official documentation
- Audit note: Transactional and global record caches
- URL: https://aerospike.com/docs/graph/manage/cache/

### S15 — Data types

- Type: Official documentation
- Audit note: Property and index type limitations
- URL: https://aerospike.com/docs/graph/develop/query/data-type-support/

### S16 — TinkerPop feature support

- Type: Official documentation
- Audit note: Feature compatibility matrix
- URL: https://aerospike.com/docs/graph/overview/tinkerpop/

### S18 — Metrics reference

- Type: Official documentation
- Audit note: Prometheus metric inventory
- URL: https://aerospike.com/docs/graph/reference/metrics/

### S19 — Query tracing

- Type: Official documentation
- Audit note: Zipkin tracing contract
- URL: https://aerospike.com/docs/graph/observe/query-tracing/

### S25 — Identity graph benchmark PDF

- Type: Vendor benchmark
- Audit note: AGS 2.4.2 / Database 7.1.0.9 test
- URL: https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf

### S26 — Graph 3.0 launch blog

- Type: Vendor blog
- Audit note: Ingest and footprint claims
- URL: https://aerospike.com/blog/aerospike-graph-3-release/

### S28 — Product editions and pricing

- Type: Official commercial page
- Audit note: Edition limits and data-volume licensing
- URL: https://aerospike.com/products/features-and-editions/

### S33 — AGS public source snapshot

- Type: Apache-2.0 source
- Audit note: 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045
- URL: https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045

### S34 — AGS data model design

- Type: Apache-2.0 source documentation
- Audit note: Packed record layout
- URL: https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/docs/DATA_MODEL_DESIGN.md

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

### S45 — Apache TinkerPop 3.7.3 reference

- Type: Upstream documentation
- Audit note: Language/runtime semantic oracle
- URL: https://tinkerpop.apache.org/docs/3.7.3/reference/
