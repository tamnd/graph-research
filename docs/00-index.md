# zu architecture correction and v1 technical specification

Status: proposed replacement architecture
Research cut: 2026-08-08
Repository baseline: `tamnd/zu` commit `1f2c7834a3069fe458ee056c0478efc206f87454`
Audit scope: tracked source, tests, benchmarks, CI, Git history, and `docs/00` through `docs/13`

## Purpose

This set turns zu's promising prototypes into one coherent database architecture. It preserves the parts that are already strong—defensive decoders, a compact single-file skeleton, vector/factorized query experiments, deterministic tests, and object-store CAS experiments—while replacing the boundary that currently prevents them from becoming one product.

The decisive correction is:

> zu has one semantic transaction and query model, one canonical immutable segment model, and backend-specific persistence protocols. The query engine consumes typed vector streams and adjacency batches from a snapshot; it does not consume engine-specific files, raw object-store calls, or a per-node virtual API.

The current `GraphStore` cannot be incrementally “filled in.” It is unused by every engine, its payload types are empty, and it cannot express batched asynchronous reads, pushdown, resource ownership, transaction validation, or backend capabilities. Meanwhile the working query engine uses a second `Graph` trait and a direct `zu1` adapter. The new design replaces both with a snapshot-oriented storage service interface and makes `zu1`, SQLite, and object storage conform through adapters.

## Normative language and evidence labels

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are normative. Each important statement belongs to one of these categories:

- **Observed**: verified in baseline source or a command run on that baseline.
- **Qualification target**: a measurable release gate, not a current performance claim.
- **Proposal**: a design requirement to implement and validate.
- **Research inference**: a conclusion drawn from cited primary literature or official system documentation; it is not represented as a fact about zu.

## Documents

1. [Current-state audit](./01-current-state-audit.md) — what exists, what is tested, and where documentation and code diverge.
2. [Architecture flaw register](./02-architecture-flaws.md) — severity-ranked flaws, failure modes, and required decisions.
3. [Product contract and invariants](./03-product-contract.md) — supported profiles, consistency, durability, failure model, and non-goals.
4. [Target architecture and crates](./04-target-architecture.md) — control/data planes, ownership, dependency direction, and component responsibilities.
5. [Storage/query service interface](./05-storage-query-contract.md) — the replacement SPI, capabilities, batching, pushdown, streams, and cancellation.
6. [Identity, schema, and graph semantics](./06-identity-and-data-model.md) — stable node/edge identity, multi-edges, labels, constraints, and path semantics.
7. [Query compiler and execution](./07-query-engine.md) — language conformance, IRs, factorization, joins, recursion, scheduling, and spilling.
8. [Transactions, MVCC, WAL, and recovery](./08-transactions-and-recovery.md) — one semantic layer with backend-specific durability adapters.
9. [`zu1` format, buffer manager, and integrity](./09-zu1-format-and-io.md) — byte ownership, chunk integrity, bounded open, CoW publication, and compatibility.
10. [SQLite engine](./10-sqlite-backend.md) — oracle scope, read/write pools, native plans, semantic parity, and interop limits.
11. [Object-storage engine](./11-object-storage.md) — fencing, ambiguity, WAL publication, cache-aware planning, partitions, GC, and cost admission.
12. [Memory, I/O, scheduling, and observability](./12-runtime-and-resources.md) — budget hierarchy, backpressure, I/O futures, cache admission, and metrics.
13. [Performance, cost, security, and operations](./13-qualification-and-operations.md) — honest SLO classes, equations, overload policy, and threat model.
14. [Migration and verification roadmap](./14-roadmap-and-verification.md) — dependency-ordered delivery, compatibility, deterministic simulation, and release gates.
15. [2026 research and system evidence](./15-research-sources.md) — primary sources and the exact constraints they impose.
16. [2026 graph-engine research corpus](./research/000-index.md) — one 500+ line audit per engine, cross-engine scorecard, S3/PB target architecture, and a defensible tenfold benchmark protocol.

## Product profiles

| Profile | Purpose | Authority | Concurrency | Durability acknowledgement |
|---|---|---|---|---|
| `zu1-local` | embedded analytics and traversal | one `.zu1` plus sidecar WAL | one process writer broker, snapshot readers | WAL commit record plus qualified sync chain |
| `sqlite-local` | interop, small OLTP, differential oracle | SQLite database/WAL | SQLite single writer, read connection pool | selected SQLite synchronous mode, reported exactly |
| `object-single` | large read-mostly namespace | immutable packs + fenced root/WAL protocol | one externally arbitrated writer, many readers | committed WAL object and published log/root metadata |
| `object-partitioned` | independent graph partitions | root directory + partition roots | one writer per partition; cross-partition semantics restricted | per-partition only; no atomic cross-partition claim |

`object-partitioned` is not a distributed ACID graph. Cross-partition mutations MUST be rejected in strict mode or exposed as an explicitly asynchronous workflow. A future distributed-transaction profile requires a transactional control plane and is outside v1.

## Irreducible invariants

1. Every query reads one immutable `SnapshotToken` that binds data root, catalog root, stats generation, and transaction epoch.
2. Every returned node or relationship has a stable logical element ID. Physical row, group, CSR slot, and object range are locators, never identity.
3. Parallel edges remain distinct through storage, traversal, equality, `DIFFERENT EDGES`, properties, checkpoint, reorder, and export.
4. An acknowledged commit has a single documented recovery point. `Memory`, `Local`, `RemoteLog`, and `Published` are distinct acknowledgement levels even when a backend maps two levels to the same physical transition.
5. A stale writer cannot produce an acknowledged commit after fencing. CAS of one manifest key alone is not sufficient proof of this property.
6. A snapshot pins every byte and schema object it can reach until its final consumer releases it; eviction and GC cannot invalidate borrowed data.
7. Query operators request batches/splits. No executor loop is allowed to issue one object-store request per node, edge, or row.
8. All variable-size allocations are charged before allocation to a query, transaction, cache, or maintenance budget.
9. Point reads verify the exact bytes they consume. A checksum that only full scans validate is not end-to-end integrity.
10. Recovery after a clean shutdown is independent of database size. Crash recovery has explicit WAL byte/object/count bounds.
11. Cost control is enforced by admission and request/byte budgets. Cache hit rate is an observation, not a bound.
12. Backend differences are surfaced as capabilities and plan choices; they never silently alter graph semantics.

## Decision ledger

| Question | Decision |
|---|---|
| Keep the current `GraphStore` and fill placeholders? | No; replace before more engines integrate. |
| Let the executor use raw encoded segments? | Only behind stable typed `Batch`/`AdjacencyBatch` views whose owners pin bytes and expose encoding capabilities. |
| Share one physical layout across all engines? | No. Share canonical segment envelopes and semantic objects; SQLite remains relational internally. |
| Put MVCC “above all engines”? | Share transaction semantics and validation; persistence/visibility adapters remain backend-specific. |
| Store relationship identity as CSR slot or `(type,src,dst)`? | No; use stable `EdgeId`, with CSR slot as a versioned locator. |
| Promise multi-label nodes via a fixed 256-bit column? | No fixed global cap in semantics; use label membership tables/bitmaps selected per table and versioned in schema. |
| Call S3 request cost flat because writes batch? | No; enforce per-namespace budgets and report compute, cache, storage, request, retrieval, and egress separately. |
| Allow automatic writer takeover with no lease/arbitration? | No; explicit fencing authority or manual force token is required. |
| Claim PB scale through independent manifests? | Only as partitioned, non-atomic datasets until a control plane exists. |
| Freeze `zu1` version 1 now? | No; current bytes are experimental. Introduce a pre-freeze format epoch and golden-reader gate first. |

## Definition of v1-ready

v1 is ready only when one public `Database`/`Connection` API can execute the conformance corpus against `zu1` and SQLite, all updates are visible through snapshot reads before checkpoint, edge identity and multi-edge semantics survive every storage transformation, recovery passes deterministic fault injection, memory and request budgets apply under overload, and the supported format/API compatibility matrix is frozen. Passing unit tests for isolated crates is necessary but not sufficient.
