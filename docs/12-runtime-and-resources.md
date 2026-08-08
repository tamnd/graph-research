# Runtime, resources, and observability

## Runtime contract

The runtime turns a physical plan into bounded work. Correctness includes predictable ownership under overload: no query, writer, scan, prefetcher, or maintenance job can allocate or issue I/O without a reservation.

The runtime is internal and poll-based. Public APIs may expose synchronous iterators and opt-in async streams without committing storage traits to Tokio or another runtime. Backend adapters bridge their completion mechanisms into the common scheduler.

## Resource hierarchy

```text
process
└── database
    ├── foreground pool
    │   ├── connection/session
    │   └── query or transaction
    │       ├── operator
    │       └── source/task
    ├── caches
    └── maintenance pool
```

Budgets cover at least:

- resident and decoded memory bytes;
- pinned cache bytes;
- temporary/spill bytes;
- CPU time/work units;
- local read/write bytes and concurrent operations;
- remote requests, bytes, concurrent operations, retries, and estimated charge;
- output rows/bytes;
- wall-clock deadline.

Child reservations debit parents. Reserved-but-unused capacity is reclaimable; committed allocations are released by RAII guards. Counters use checked arithmetic. A request exceeding a hard limit fails before allocation or I/O.

## Memory protocol

```rust
pub trait MemoryPool: Send + Sync {
    fn try_reserve(&self, bytes: usize, class: MemoryClass)
        -> Result<MemoryReservation>;
}
```

Operators estimate minimum and preferred reservations during admission. Execution grants memory incrementally. Hash tables and frontiers grow only after acquiring the next reservation. Variable-length decoders validate decoded size and reserve it before allocation.

Memory classes distinguish operator state, input/output batches, pinned encoded bytes, decoded cache, metadata, writer/WAL buffers, and maintenance. A fixed emergency reserve remains available for error reporting, cancellation, and cleanup; normal work cannot consume it.

Global pressure proceeds in this order:

1. stop speculative prefetch and low-value cache admission;
2. evict unpinned cache entries;
3. ask spillable foreground operators to spill at safe points;
4. throttle new work and maintenance;
5. reject admission with a structured limit error.

The runtime never depends on the operating-system OOM killer as policy.

## Scheduling

CPU work is split into morsels with a target execution time, initially 0.25–2 ms after calibration. Tasks carry database/query identity, priority class, cancellation token, and resource reservation. Work stealing is allowed within fairness constraints.

Weighted deficit scheduling prevents one broad scan or recursive traversal from monopolizing workers. Interactive, batch, ingestion, and maintenance weights are configurable. Aging prevents starvation. A per-query runnable-task cap controls fan-out even when many graph partitions exist.

Long kernels and recursive expansions yield at batch/morsel boundaries. Blocking OS/SQLite calls run on a bounded blocking pool. An exhausted blocking pool backpressures submitters rather than spawning threads.

## I/O scheduling

I/O requests declare ranges, priority, deadline, expected bytes, checksum scope, and coalescing key. The scheduler:

- merges compatible adjacent reads within a bounded amplification ratio;
- limits per-backend/per-query operations and bytes in flight;
- schedules metadata ahead of speculative data but behind demanded foreground data;
- supports cancellation before dispatch and discards late completion safely;
- accounts actual bytes, retries, and provider requests to the originating query/job.

Local and remote I/O share accounting, not identical policies. Local seek/queue depth, object-store GET count, and SQLite statement concurrency remain distinct metrics and cost dimensions.

## Backpressure

Pipeline channels are bounded by batches and bytes. A producer may not retain an unbounded batch while waiting for output capacity. Source polling stops when downstream has no demand, except for a strictly bounded read-ahead window.

Result streams own the query until exhausted, cancelled, or dropped. Drop triggers cancellation and bounded cleanup. If cleanup requires asynchronous completion, the database lifecycle retains the cleanup task and its charges; resources do not leak merely because the client abandoned a future.

## Spill

Spill files live in a database-configured directory, never an implicit current directory. Each query has a unique subdirectory with restrictive permissions and a manifest. Blocks are length-delimited and checksummed; optional authenticated encryption is required where temp storage is not trusted.

Spill algorithms include partitioned hash join/aggregate, external sort, distinct, and recursive frontier state. Operators reserve spill quota before writing. Disk-full becomes `BudgetExceeded`/I/O error with cleanup. Startup scavenging removes abandoned query directories only after validating ownership and age; active instances use locks/leases.

Spill bytes are not durable database state and are never replayed after crash.

## Cache policy

Cache capacity is a database-level resource with protected metadata quota. Entries are immutable and keyed by database lineage, root/content digest, object/range, representation, and schema/codec version. No key may alias bytes across generations.

Admission uses reuse evidence and scan classification. Sequential one-pass input may bypass the cache. Eviction policy is independently replaceable and measured against skew, scans, and mixed workloads. Pinned entries may lose cache membership but remain alive and charged to their pin owner until release.

Negative cache entries have short explicit TTLs and are invalidated by root generation. Authorization or transient provider errors are never negative-cached as absence.

## Admission

Before execution, the planner supplies low/expected/high estimates and minimum viable resources. Admission checks:

```text
hard semantic limits
available memory and spill
CPU/runnable capacity
local I/O envelope
remote request/byte/cost envelope
deadline feasibility
```

Uncertain estimates use the high bound for hard remote/cost limits and a configured confidence policy for elastic resources. During execution, approaching an envelope can select a preplanned fallback at a checkpoint; otherwise execution stops cleanly. Semantics never change to stay under budget.

## Observability schema

Every operation has trace ID, database/partition ID, snapshot/root generation, query fingerprint, backend, and outcome. Raw query text, parameter/property values, credentials, object authorization tokens, and filesystem secrets are excluded by default.

Minimum counters/histograms:

- parse/bind/optimize/admission/queue/execute/result durations;
- rows and batches at each operator, estimated versus actual;
- current/peak reserved memory, pins, cache and spill bytes;
- local reads/writes/seeks/sync latency;
- object requests by operation/status/retry, requested/fetched bytes, cache tier;
- SQLite statement count, time, busy time, rows and temp use;
- WAL append/sync/group size, commit phase latency, conflicts and ambiguity;
- snapshot age/pins, root generations, checkpoint/compaction/GC debt;
- cancellation latency and cleanup failures.

Cardinality labels are bounded: table/column names, query text, node IDs, object keys, and transaction IDs do not become metric labels. Detailed identifiers belong in sampled/redacted traces.

## Profiles and reproducibility

`EXPLAIN ANALYZE` records engine/version, format/root, schema/stats version, optimizer flags, hardware/profile ID, memory/request envelopes, cache state declaration, and per-operator measurements. Benchmark artifacts capture these fields plus dataset digest and random seed.

Timing instrumentation is sampled or batched so profiling overhead is measured. A no-profile baseline and counter-only mode quantify observer effects.

## Runtime qualification

- adversarial allocation sizes never exceed configured resident memory beyond a small measured allocator allowance;
- dropping results at every operator releases pins, tasks, statements, and requests;
- slow consumers keep bounded queued bytes;
- concurrent high-degree traversals respect fairness and runnable caps;
- maintenance cannot starve foreground commits or consume emergency reserve;
- disk-full, cache corruption, delayed I/O, retry storms, and provider throttling stay bounded;
- ThreadSanitizer/Loom-style state tests cover publication, cancellation, pins, and queues where practical;
- profiles reconcile operator totals with backend requests/bytes and global resource counters.
