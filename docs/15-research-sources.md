# 2026 research and system evidence

Research cut: 2026-08-08. Sources are primary papers or official project/provider documentation. They motivate design choices; they do not prove zu implements a result or will reproduce another system's performance.

## Graph storage and execution

### Kùzu / factorized graph processing

- Source: [Kùzu Graph Database Management System, CIDR 2023](https://www.vldb.org/cidrdb/2023/kuzu-graph-database-management-system.html)
- Evidence: a modern embedded graph DBMS combines columnar storage, CSR-style adjacency, factorized/vectorized processing, and graph-aware optimization rather than treating graph access as only repeated key/value neighbor calls.
- Constraint on zu: preserve adjacency structure and factorization metadata across the storage/runtime boundary; do not expose only per-node iterators.
- Caveat: Kùzu/Ladybug's implementation and workload results are not zu targets without equivalent experiments.

### Current Ladybug baseline

- Sources: [Ladybug documentation](https://docs.ladybugdb.com/), [database internals](https://docs.ladybugdb.com/developer-guide/database-internal), [relationship table DDL](https://docs.ladybugdb.com/cypher/data-definition/create-table/), [Icebug import](https://docs.ladybugdb.com/import/icebug/)
- Evidence as observed by the research cut: the actively documented successor to Kùzu presents embedded columnar/CSR and vectorized/factorized execution; relationship rows have identifiers supporting multiple relationships between endpoints; Icebug describes graph-aware access over remote Parquet-style data.
- Constraint on zu: claims that competitors lack these capabilities are stale. Stable relationship identity and graph-aware remote layout are baseline design concerns, not optional polish.
- Caveat: official product documentation is evidence of documented behavior, not an independent benchmark.

### Robust recursive execution

- Source: [Robust Recursive Query Parallelism, PVLDB 2025](https://www.vldb.org/pvldb/vol18/p4465-chakraborty.pdf)
- Evidence: recursive graph workloads are skewed and difficult to estimate; scheduling can be designed to remain robust when the initial recursive plan or partitioning is imperfect.
- Constraint on zu: variable-length traversal needs resumable morsels, frontier budgets and adaptive work redistribution. Correctness and resource limits cannot depend on a precise single cardinality estimate.

### Relational graph representations

- Source: [Raqlet, CIDR 2026](https://www.vldb.org/cidrdb/papers/2026/p7-shaikhha.pdf)
- Evidence: recent work continues exploring graph representations and graph operations through relational/array abstractions rather than a hard separation between a graph runtime and columnar execution.
- Constraint on zu: retain typed batch algebra and permit graph operations to lower into general vector/relational machinery; do not bake zu1 pointers into graph values.

### Graph analytics over relational systems

- Source: [GraphAlg, 2026 preprint](https://arxiv.org/abs/2601.06705)
- Evidence: graph-algorithm integration with relational processing remains an active 2026 topic.
- Constraint on zu: treat future algorithms as bounded physical operators over snapshots/batches with explicit frontier state, not as a second storage API. The preprint status means it is directional evidence, not a release dependency.

### Dynamic graph storage

- Sources: [LSMGraph, 2024 preprint](https://arxiv.org/abs/2411.06392), [An Experimental Study of Dynamic Graph Storage, 2025 preprint](https://arxiv.org/abs/2502.10959)
- Evidence: dynamic graph layout is a multidimensional trade-off across updates, locality, amplification, degree skew, and concurrency; there is no basis for assuming fixed CSR slack alone solves update behavior.
- Constraint on zu: keep sealed dense adjacency plus visible deltas, measure amplification, and make checkpoint scope explicit. Evaluate alternatives on zu workloads before selecting a more complex dynamic structure.

## Encodings and columnar layout

### Structural encodings

- Source: [Lance: Efficient Random Access in Columnar Storage through Adaptive Structural Encodings, 2025](https://arxiv.org/abs/2504.15247)
- Evidence: encoding can be modeled compositionally and selected for both compression and access behavior, rather than as a single terminal codec per column.
- Constraint on zu: represent arrays as bounded encoding trees with kernel capabilities, and include point/gather/filter cost in selection. The exact Lance layout is not copied automatically.

### FastLanes

- Sources: [The FastLanes Compression Layout, PVLDB 2023](https://www.vldb.org/pvldb/vol16/p2132-afroozeh.pdf), [FastLanes File Format, PVLDB 2025](https://vldb.org/pvldb/vol18/p4629-afroozeh.pdf)
- Evidence: vector-sized, layout-aware compression primitives can improve portability and decode/compute behavior; the later file-format work illustrates composing those ideas into self-describing storage.
- Constraint on zu: benchmark portable vector primitives, preserve an explicit format version, and qualify decode-on-query kernels. Hardware-specific fast paths need a correct scalar fallback.

### Vortex

- Sources: [Vortex layouts](https://docs.vortex.dev/concepts/layouts), [scan API](https://docs.vortex.dev/concepts/scanning), [architecture](https://docs.vortex.dev/developer-guide/internals/architecture)
- Evidence: current official design separates logical arrays/encodings, physical layouts, and scan orchestration; scan requests support projection/filter while layouts produce executable splits and pruning.
- Constraint on zu: use a typed scan request, independent splits and an exact/pruning-only pushdown report. Separate canonical semantic batches from backend layout.
- Caveat: these pages describe an evolving project. zu must pin any dependency/API version and maintain its own compatibility layer.

## Joins, factorization, and cardinality

### Binary and worst-case-optimal convergence

- Source: [Unifying Binary and Worst-Case Optimal Joins, 2025 preprint](https://arxiv.org/abs/2505.19918)
- Evidence: current research explores a continuum/shared execution mechanisms rather than an absolute choice between binary and worst-case-optimal joins.
- Constraint on zu: optimizer IR should express ordered intersections/multiway plans without requiring a separate executor universe; choose per subproblem and measured distribution.

### Conservative cardinality bounds

- Sources: [Pessimistic Cardinality Estimation, 2024 preprint](https://arxiv.org/abs/2412.00642), [LpBound, 2025 preprint](https://arxiv.org/abs/2502.05912), [Degree-Based Cardinality Estimation: An Ambidextrous Perspective, 2025 preprint](https://arxiv.org/abs/2510.04249)
- Evidence: pessimistic and degree-based bounds can protect against severe underestimation for joins/graph patterns, complementing expected-value estimates.
- Constraint on zu: return estimate ranges/confidence; use conservative bounds for admission and catastrophic memory/request decisions. Do not market a bound technique as universally tight.

### Learned/feedback estimation

- Source: [COLOR: a Learned Cardinality Estimator, PVLDB 2025](https://www.vldb.org/pvldb/vol18/p130-deeds.pdf)
- Evidence: learned/representation-based estimation continues to improve, but introduces model lifecycle, training and generalization concerns.
- Constraint on zu: retain a pluggable estimator interface and runtime feedback. A learned estimator is post-v1 and may never be the sole guard for hard resource limits.

### Adaptive factorization and semijoin filtering

- Sources: [Adaptive Factorization Using Linear Chained Hash Tables, CIDR 2025](https://www.vldb.org/cidrdb/2025/adaptive-factorization-using-linear-chained-hash-tables.html), [I Can't Believe It's Not Yannakakis: Pragmatic Bitmap Filters in Microsoft SQL Server, CIDR 2026](https://www.vldb.org/cidrdb/2026/i-cant-believe-its-not-yannakakis-pragmatic-bitmap-filters-in-microsoft-sql-server.html)
- Evidence: factorization choices can adapt at runtime, and practical bitmap/semijoin reductions can bring classic acyclic-join ideas into production engines.
- Constraint on zu: carry factorization metadata, allow adaptive materialization at safe boundaries, and cost bitmap reduction before broad edge/property scans.

## Buffer management and execution plumbing

### SIEVE cache policy

- Sources: [SIEVE project page, NSDI 2024](https://www.usenix.org/conference/nsdi24/presentation/zhang-yazhuo), [paper PDF](https://www.usenix.org/system/files/nsdi24-zhang-yazhuo.pdf)
- Evidence: SIEVE offers a simple, scalable eviction approach with strong reported results, but the paper explicitly does not make it inherently scan-resistant.
- Constraint on zu: SIEVE is a candidate eviction policy only. Protect metadata and handle one-pass scans with admission/bypass; never infer scan resistance from the algorithm name.

### SSD-conscious buffer managers

- Sources: [How to Write to SSDs, or ZLeanStore, PVLDB 2026](https://www.vldb.org/pvldb/vol19/p1469-lee.pdf), [Predictive Translation, 2026](https://db.in.tum.de/~zinsmeister/papers/predictive-translation.pdf)
- Evidence: storage-device behavior, translation, and asynchronous/batched access continue to affect buffer-manager design on modern SSDs.
- Constraint on zu: keep I/O backend and cache policy pluggable, record physical I/O amplification, and qualify direct/async paths. Do not hard-wire a research algorithm before representative hardware tests.

### DuckDB execution and storage comparison

- Sources: [DuckDB storage internals](https://duckdb.org/docs/stable/internals/storage), [analytics-optimized concurrent transactions](https://duckdb.org/2024/10/30/analytics-optimized-concurrent-transactions), [test-driving Lance, 2026](https://duckdb.org/2026/05/21/test-driving-lance)
- Evidence: an embedded analytical system can combine compressed columnar storage and MVCC with explicit concurrency trade-offs; the 2026 Lance work is further evidence that external columnar formats require workload-driven integration testing.
- Constraint on zu: distinguish transactional deltas from immutable analytical layout and test format/kernel integration end-to-end. DuckDB's concurrency/format details are comparators, not drop-in semantics.

### Acero

- Source: [Apache Arrow Acero user guide](https://arrow.apache.org/docs/cpp/acero/user_guide.html)
- Evidence: production vector execution exposes push-based/backpressured execution concerns, schemas, batches, and bounded pipelines.
- Constraint on zu: make demand, cancellation and batch ownership first-class. zu need not adopt Arrow as its internal ABI, but interoperability should preserve typed batch semantics.

## Object storage and remote durability

### Rust object_store abstraction

- Sources: [`object_store` crate documentation](https://docs.rs/object_store/latest/object_store/), [`ObjectStore` trait](https://docs.rs/object_store/latest/object_store/trait.ObjectStore.html)
- Evidence: the Rust ecosystem exposes an asynchronous multi-provider object API including range operations and conditional/multipart capabilities.
- Constraint on zu: isolate provider details behind an adapter, pin tested versions/features, and negotiate actual conditional semantics. A common trait does not make provider guarantees identical.

### S3 consistency and conditional operations

- Sources: [Amazon S3 user guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html), [conditional requests](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-requests.html)
- Evidence: S3 documents strong read-after-write consistency for individual object operations and supports conditional requests. Those guarantees are object/key scoped; they do not provide a multi-object database transaction or writer lease.
- Constraint on zu: publish one partition through one conditional root pointer after immutable uploads, and supply separate fencing. Do not derive cross-key atomicity from strong consistency.

### SlateDB

- Sources: [SlateDB file design](https://slatedb.io/docs/design/files/), [manifest fencing RFC](https://slatedb.io/rfcs/0001-manifest/)
- Evidence: a serious object-store database separates immutable WAL/SST/manifest objects, and its manifest design must coordinate writer/compactor epochs and WAL positions.
- Constraint on zu: a manifest containing only `epoch`, `writer_id`, and segment strings is insufficient. Publication/recovery need WAL high-water marks, epoch lineage, immutable references, reconcile, and GC roots.

### Turbopuffer

- Source: [Turbopuffer architecture](https://turbopuffer.com/docs/architecture)
- Evidence: the official architecture describes object storage as authoritative, WAL batching, caching, and an object-friendly coarse vector index; its published example shows a large cold-versus-warm latency difference (874 ms versus 14 ms p50 at the time observed).
- Constraint on zu: batch durable writes, design request-efficient coarse/tiled structures, and publish separate cold/warm results. The values are that system's documented example, not zu targets and not guaranteed current beyond the research cut.

## Standards and product landscape

### ISO GQL

- Source: [ISO/IEC 39075:2024 — GQL](https://www.iso.org/standard/76120.html?browse=tc)
- Evidence: graph query language now has an international standard baseline.
- Constraint on zu: document its language as a precise subset/dialect, keep semantic IR concepts such as graph element identity and path modes explicit, and use stable unsupported-feature diagnostics. Full GQL conformance is not a v1 assumption.

### Spanner Graph

- Source: [Google Cloud Spanner Graph](https://cloud.google.com/products/spanner/graph?e=48754805)
- Evidence: current managed systems combine graph and relational models over transactional infrastructure.
- Constraint on zu: avoid claiming that one physical graph layout is necessary for every backend; share graph semantics while allowing relational lowering. This does not change zu's embedded/read-mostly scope.

## Synthesis: what this evidence changes

The sources support six architectural conclusions:

1. **Identity and semantics first.** Current graph systems and the GQL landscape make distinct edge identity, path semantics, and typed catalogs non-negotiable.
2. **Batched structural interfaces.** Graph-native adjacency, columnar batches, factorization and multiway joins all require more structure than `neighbors(node) -> Vec<NodeId>`.
3. **Immutable base plus explicit transactional delta.** Analytical encodings and update/recovery concerns have different optimal forms; the API must merge them at one snapshot.
4. **Encoding is a tree with compute capabilities.** Recent format work argues against representing compression as a single opaque codec chosen only by byte size.
5. **Bounds matter more remotely.** Cardinality ranges, request-aware planning, backpressure and admission are correctness/operability mechanisms, not later tuning.
6. **Object CAS is publication, not a database protocol.** Immutable objects and a conditional root are useful primitives, but fencing, WAL position, ambiguity, pins and GC complete the protocol.

None of these sources justifies a zu performance claim without the qualification framework in document 13. Research features enter the roadmap only with a correctness fallback, reproducible workload, resource envelope, and evidence artifact.
