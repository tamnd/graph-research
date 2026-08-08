# 2026 graph-engine landscape scorecard

Research cut: `2026-08-08`
Scores are directional engineering assessments, not measured benchmark results.

## Scoring rule

`strong` means public architecture clearly supports the dimension. `partial` means an adjacent capability exists with important constraints. `weak` means the architecture conflicts with the target. `unknown` means public evidence is insufficient. No numeric total is produced because weights depend on workload and unknowns are not zeros.

## Engine summary

### 1. Neo4j

- Family: native property graph.
- Lifecycle confidence: strong — active; calendar-versioned 2026 line.
- Distributed-capacity alignment: strong — standalone, clustered, composite databases, and Infinigraph automatic sharding.
- S3-authoritative alignment: weak — not S3-native for the live query path; object storage is operational/backup infrastructure.
- Scale evidence: single-store formats have finite ID domains; Infinigraph is the 100-TB-plus horizontal path.
- Principal benchmark issue: industry baseline with LDBC and vendor workloads, but edition and runtime must be pinned.
- zu decision: The ecosystem and Cypher compatibility bar are formidable; storage cost, JVM footprint, and distributed-license cost are openings for zu.

### 2. FalkorDB

- Family: matrix property graph.
- Lifecycle confidence: strong — active; Rust transition and Redis-module lineage.
- Distributed-capacity alignment: strong — single node and commercial/cloud scale-out offerings; open core must be separated from service claims.
- S3-authoritative alignment: weak — not an object-store-native live engine.
- Scale evidence: excellent dense set-at-a-time traversal potential; PB evidence is not public.
- Principal benchmark issue: vendor benchmark suite exists; require pinned queries, data, hardware, and durability.
- zu decision: FalkorDB is the most direct sparse-linear-algebra competitor and a required point/traversal baseline.

### 3. LadybugDB

- Family: embedded analytical property graph.
- Lifecycle confidence: strong — active successor fork in 2026.
- Distributed-capacity alignment: strong — embedded single-node, in-process; no native distributed transaction layer.
- S3-authoritative alignment: weak — not object-store-native, though Parquet/Arrow/DuckDB interoperability is central.
- Scale evidence: large single-node analytical graphs; PB/distributed claims are outside the current product shape.
- Principal benchmark issue: must run Kuzu-derived LDBC and microbenchmarks from source with pinned commit.
- zu decision: This is zu's closest embedded architectural competitor and the primary fair same-machine benchmark.

### 4. Kuzu (archived)

- Family: embedded analytical property graph.
- Lifecycle confidence: weak — archived 2025-10-10; historical baseline.
- Distributed-capacity alignment: weak — embedded single-node.
- S3-authoritative alignment: weak — not object-store-native.
- Scale evidence: single-node only.
- Principal benchmark issue: Kuzu 0.9.0 is a reproducible historical baseline, not a current product.
- zu decision: Retain for regression and lineage attribution; do not present it as an active competitor.

### 5. PuppyGraph

- Family: lakehouse graph query engine.
- Lifecycle confidence: strong — active commercial product.
- Distributed-capacity alignment: partial — cluster deployment with independent compute over external data.
- S3-authoritative alignment: weak — directly relevant: queries data in lake/object-backed systems but is not simply an S3 adjacency store.
- Scale evidence: vendor claims petabyte data and deep traversal; independent audited evidence is required.
- Principal benchmark issue: benchmark must include source scan bytes, materialization, cache state, and warehouse cost.
- zu decision: PuppyGraph is the closest commercial graph-lake comparator for zu's remote profile.

### 6. Memgraph

- Family: in-memory operational property graph.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: strong — leader/replica high availability and read scaling; not a general sharded PB store.
- S3-authoritative alignment: weak — not object-store-native.
- Scale evidence: RAM-bound mode targets low latency; on-disk mode broadens capacity with different behavior.
- Principal benchmark issue: benchmark every storage mode separately and include WAL/snapshot settings.
- zu decision: Memgraph is the low-latency mutable baseline; zu must win resource efficiency without comparing unlike durability modes.

### 7. NebulaGraph

- Family: distributed property graph.
- Lifecycle confidence: strong — active; Enterprise 5.2 was current in the 2025 review.
- Distributed-capacity alignment: strong — compute/storage separation, partition buckets, Raft groups, multi-cluster management.
- S3-authoritative alignment: weak — not S3-native in the query path.
- Scale evidence: vendor describes 200-TB clusters; PB qualification not established.
- Principal benchmark issue: separate open-source 3.x from Enterprise 5.x in every result.
- zu decision: Nebula is a major distributed/GQL comparator and a warning against hiding network traversal behind one latency number.

### 8. TigerGraph

- Family: distributed native property graph.
- Lifecycle confidence: strong — active; 4.2.4 released 2026-07-20.
- Distributed-capacity alignment: strong — automatic partitioning, MPP execution, leaderless replicated self-managed architecture; Savanna workspaces.
- S3-authoritative alignment: weak — Savanna is disaggregated but public docs do not establish an S3-range-native adjacency path.
- Scale evidence: public material cites hundreds of billions of edges; exact audited configurations matter.
- Principal benchmark issue: use LDBC disclosures and self-run compatible subsets; compiled-query warmup must be explicit.
- zu decision: TigerGraph sets the mature distributed analytics bar; zu's likely win is cost/resource efficiency and embedded simplicity, not every throughput regime.

### 9. GraphScope Flex Interactive

- Family: distributed interactive graph system.
- Lifecycle confidence: strong — active Apache-2.0 project.
- Distributed-capacity alignment: strong — distributed service with per-core shards and scale-out deployment.
- S3-authoritative alignment: weak — not object-store-native for interactive serving; GraphAr/lake integration is adjacent.
- Scale evidence: audited LDBC SNB at SF1000 and hundreds of billions of edges.
- Principal benchmark issue: audited LDBC results are the throughput credibility bar.
- zu decision: GraphScope is the strongest public audited throughput comparator and must not be reduced to a laptop microbenchmark.

### 10. JanusGraph

- Family: storage-agnostic distributed graph layer.
- Lifecycle confidence: strong — active 1.x.
- Distributed-capacity alignment: weak — horizontal scale through chosen backend and stateless-ish JanusGraph servers.
- S3-authoritative alignment: weak — possible indirectly through cloud backends, but not S3-native and pointer/request economics are unfavorable.
- Scale evidence: large distributed capacity is plausible through backends; supernodes and bulk load have documented limits.
- Principal benchmark issue: benchmark is a full stack: JanusGraph, backend, index service, consistency, and cache.
- zu decision: JanusGraph proves modular scale but also shows why a synchronous fine-grained storage SPI is a latency and operations trap.

### 11. Apache HugeGraph

- Family: pluggable OLTP plus OLAP graph platform.
- Lifecycle confidence: strong — active Apache top-level project.
- Distributed-capacity alignment: partial — PD plus HStore horizontal mode with HA.
- S3-authoritative alignment: weak — not S3-native live serving; external storage is an ingest/analytics concern.
- Scale evidence: official 2026 docs scope standalone below 4 TB and distributed below 1000 TB.
- Principal benchmark issue: run server/HStore and analytics components as separate systems.
- zu decision: HugeGraph's explicit 1000-TB envelope is highly relevant, but it reaches it with a distributed store rather than cheap object-only serving.

### 12. TuGraph

- Family: HTAP native property graph.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: strong — community single-node/HA features and enterprise distributed architecture.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: large production claims exist; PB public qualification is insufficient.
- Principal benchmark issue: use LDBC implementation disclosures and pin Community versus Enterprise.
- zu decision: TuGraph is a serious C++ HTAP comparator, particularly for local mutable traversal and compiled procedures.

### 13. Ultipa Powerhouse

- Family: hybrid distributed and high-density graph system.
- Lifecycle confidence: strong — active v5 line.
- Distributed-capacity alignment: strong — shard, name, meta, and HDC server roles.
- S3-authoritative alignment: weak — not presented as S3-native live storage.
- Scale evidence: billions of nodes; no public PB proof.
- Principal benchmark issue: GQL conformance can be tested; performance claims require independent harness.
- zu decision: Ultipa is important for its explicit two-mode design: economical sharded authority plus high-density acceleration.

### 14. ArangoDB

- Family: native multi-model database.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: partial — CP master/master cluster with coordinators, DB-Servers, agency; SmartGraphs optimize locality.
- S3-authoritative alignment: weak — not S3-native live serving.
- Scale evidence: horizontal document/graph scale; efficient graph scale depends on sharding locality.
- Principal benchmark issue: Community General Graph and Enterprise SmartGraph are distinct baselines.
- zu decision: ArangoDB shows the benefit and cost of multi-model integration; SmartGraph locality is a mandatory partitioning comparison.

### 15. Dgraph

- Family: distributed predicate-sharded graph database.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: strong — Zero control plane plus Alpha Raft groups; predicate sharding and rebalancing.
- S3-authoritative alignment: weak — not S3-native; backups may use object storage.
- Scale evidence: horizontal scale, but hot predicates and cross-group queries are key constraints.
- Principal benchmark issue: measure predicate skew, network fanout, Raft durability, and GraphQL translation separately.
- zu decision: Dgraph is the canonical predicate-sharding counterpoint to source-range adjacency partitioning.

### 16. OrientDB

- Family: multi-model graph/document database.
- Lifecycle confidence: weak — active 4.0 line but legacy architecture remains relevant.
- Distributed-capacity alignment: strong — Hazelcast-coordinated multi-master replication and class/cluster sharding.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: distributed scale constrained by manual sharding/index limitations in documented designs.
- Principal benchmark issue: use as compatibility/resource baseline, not a PB front-runner.
- zu decision: OrientDB is valuable chiefly as a warning about physical identity, multi-master conflict handling, and application-directed sharding.

### 17. ArcadeDB

- Family: multi-model native graph database.
- Lifecycle confidence: strong — active 26.x.
- Distributed-capacity alignment: strong — leader/replica Raft HA scales reads and availability, not sharded capacity.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: single-database capacity plus replicated copies; no PB claim.
- Principal benchmark issue: benchmark embedded and server modes; disclose protocol translation.
- zu decision: ArcadeDB is a strong low-resource JVM/multi-model comparison and a fast-moving 2026 target.

### 18. TypeDB

- Family: typed polymorphic database.
- Lifecycle confidence: strong — active 3.x; clustering was experimental/alpha in current docs.
- Distributed-capacity alignment: partial — Raft replicated leader/follower cluster; writes remain leader-bound; clustering status must be pinned.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: read scale through replication, not data sharding; capacity remains full-copy bounded.
- Principal benchmark issue: semantic/inference workloads require a separate corpus from ordinary LPG traversal.
- zu decision: TypeDB competes on modeling correctness and inference, not PB topology economics; zu should borrow explicit schema invariants, not its full-copy scale model.

### 19. TerminusDB

- Family: version-controlled document graph database.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: strong — federation/version exchange rather than transparent sharded query execution.
- S3-authoritative alignment: weak — immutable objects are conceptually compatible with object storage, but current serving is not documented as S3-native.
- Scale evidence: versioned knowledge graphs; not demonstrated at PB interactive topology scale.
- Principal benchmark issue: benchmark revision/diff/merge separately from traversal.
- zu decision: TerminusDB is the strongest lesson for immutable lineage, content addressing, and branchable metadata.

### 20. CozoDB

- Family: embedded relational-graph-vector database.
- Lifecycle confidence: strong — maintenance activity appears limited after late 2024; verify before adoption.
- Distributed-capacity alignment: strong — single-process/embedded; TiKV-era distributed options are not a simple turnkey cluster.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: local and backend-dependent; no PB evidence.
- Principal benchmark issue: include recursive-query and algorithm microbenchmarks, but flag lifecycle risk.
- zu decision: CozoDB is a compact Datalog design reference; limited recent activity weakens it as a production comparator.

### 21. SurrealDB

- Family: distributed multi-model database.
- Lifecycle confidence: strong — active 3.x.
- Distributed-capacity alignment: weak — compute/storage separation; SurrealDS for multi-node Enterprise/Cloud.
- S3-authoritative alignment: partial — 2026 materials describe object-storage-based distributed storage, but public internals and cost evidence are incomplete.
- Scale evidence: distributed promises are significant; independent PB graph evidence absent.
- Principal benchmark issue: test native RELATE traversal separately from generic document links and cloud-only SurrealDS.
- zu decision: SurrealDB is a high-priority Rust/multi-model competitor and a useful check on zu's storage-query boundary.

### 22. HelixDB

- Family: Rust graph-vector database.
- Lifecycle confidence: strong — active and fast-moving; 3.0.2 listed in May 2026.
- Distributed-capacity alignment: strong — local server and commercial cloud; public distributed mechanics are incomplete.
- S3-authoritative alignment: partial — current marketing says built on object storage, making it directly relevant, but technical evidence is sparse.
- Scale evidence: early-stage; no credible PB proof.
- Principal benchmark issue: reproduce vendor claims and include compile/deploy, dynamic query, and durability behavior.
- zu decision: HelixDB is an emerging direct Rust/object-storage/GraphRAG competitor, but unknowns must be treated as unknowns.

### 23. MillenniumDB

- Family: research persistent graph database.
- Lifecycle confidence: strong — active research project with small community.
- Distributed-capacity alignment: weak — single-node.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: research-scale, no PB serving claim.
- Principal benchmark issue: use for optimizer/index research comparisons, not product TCO claims.
- zu decision: MillenniumDB is a valuable research baseline for succinct indexes and path algorithms, though not a deployment peer.

### 24. DuckPGQ

- Family: analytical SQL/PGQ extension.
- Lifecycle confidence: strong — active CWI project.
- Distributed-capacity alignment: weak — embedded single-node.
- S3-authoritative alignment: weak — DuckDB can query object files, but DuckPGQ CSR construction is not an S3-native persistent graph index.
- Scale evidence: single-node analytics; CSR memory limits matter.
- Principal benchmark issue: include CSR-build time and memory, never report query-only numbers alone.
- zu decision: DuckPGQ is the fairest relational/SQL standards baseline and exposes the cost of rebuilding topology indexes.

### 25. Apache AGE

- Family: PostgreSQL graph extension.
- Lifecycle confidence: strong — active Apache project.
- Distributed-capacity alignment: strong — PostgreSQL HA options; AGE tables are not currently transparently distributed by Citus.
- S3-authoritative alignment: weak — not S3-native live serving.
- Scale evidence: PostgreSQL-node scale; no native PB graph sharding.
- Principal benchmark issue: compare both graph-only and hybrid SQL/Cypher, including join and JSON-property costs.
- zu decision: AGE is the strongest open PostgreSQL extension baseline; zu should win deep traversal and storage density while conceding ecosystem maturity.

### 26. AgensGraph

- Family: PostgreSQL-derived multi-model graph database.
- Lifecycle confidence: strong — active 2.17 documentation line.
- Distributed-capacity alignment: strong — active-standby HA; no native horizontally sharded property graph in public docs.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: single-primary scale.
- Principal benchmark issue: hybrid-query correctness and optimizer quality are the main comparisons.
- zu decision: AgensGraph provides a mature SQL/Cypher hybrid baseline but is not a PB or object-storage competitor.

### 27. Amazon Neptune Database

- Family: managed cloud graph database.
- Lifecycle confidence: strong — active AWS service.
- Distributed-capacity alignment: partial — one writer, up to fifteen read replicas sharing storage; automatic 10-GiB segment growth.
- S3-authoritative alignment: weak — backups are on S3, but live database storage is a managed shared block service, not user-priced S3 objects.
- Scale evidence: 128-TiB cluster-volume maximum in most regions.
- Principal benchmark issue: managed-service comparison must include instance, I/O/storage mode, replicas, and network.
- zu decision: Neptune is a production durability/availability baseline but cannot satisfy a 1-PB single-graph target today.

### 28. Amazon Neptune Analytics

- Family: managed in-memory graph analytics.
- Lifecycle confidence: strong — active AWS service.
- Distributed-capacity alignment: weak — managed provisioned graph endpoint.
- S3-authoritative alignment: weak — S3 is an import/source path, not demand-paged live graph storage.
- Scale evidence: capacity bound by provisioned analytics graph sizes; not PB resident.
- Principal benchmark issue: charge load time, provisioned capacity, and algorithm duration.
- zu decision: Neptune Analytics is a strong hot analytical baseline but its economics fundamentally differ from S3-authoritative cold data.

### 29. Google Cloud Spanner Graph

- Family: managed relational-property-graph database.
- Lifecycle confidence: strong — active Enterprise/Enterprise Plus feature; docs updated 2026-07-22.
- Distributed-capacity alignment: strong — transparent sharding and managed scale-out.
- S3-authoritative alignment: weak — managed storage is not exposed as fixed-cost S3 object access.
- Scale evidence: algorithms documented for tens of billions of edges; no public PB proof.
- Principal benchmark issue: compare query and algorithm compute separately; include Spanner edition and processing units.
- zu decision: Spanner Graph is the standards and managed-consistency baseline; zu's opening is cost, portability, and graph-native density.

### 30. Azure Cosmos DB for Apache Gremlin

- Family: managed partitioned multi-model graph API.
- Lifecycle confidence: strong — active.
- Distributed-capacity alignment: strong — automatic partitioning by user-chosen key.
- S3-authoritative alignment: weak — managed cloud storage, not an S3-native portable engine.
- Scale evidence: large horizontal capacity; graph latency is sensitive to partition key and direction.
- Principal benchmark issue: report request units, partitions touched, throttling, and retry latency.
- zu decision: Cosmos is the clearest counterexample showing why edge direction and partition-key-aware planning are mandatory.

### 31. Graph in Microsoft Fabric

- Family: lakehouse graph analytics.
- Lifecycle confidence: strong — active 2026 feature.
- Distributed-capacity alignment: strong — managed scale-out within Fabric.
- S3-authoritative alignment: partial — directly lake/object aligned through OneLake, but materializes a queryable graph.
- Scale evidence: officially targets billions of relationships; PB evidence absent.
- Principal benchmark issue: include graph build/rebuild, capacity units, schema evolution, and cold/warm state.
- zu decision: Fabric Graph is a new direct lakehouse competitor and validates GQL plus read-optimized materialization over object-backed tables.

### 32. Oracle Database Property Graph

- Family: relational-integrated graph platform.
- Lifecycle confidence: strong — active Oracle Database 26ai line.
- Distributed-capacity alignment: weak — Oracle RAC/Exadata/cloud database scale plus separate graph server.
- S3-authoritative alignment: weak — object storage may feed/load data, not the primary low-latency graph index.
- Scale evidence: large enterprise scale but public PB interactive evidence is workload-specific.
- Principal benchmark issue: separate in-database query from PGX-loaded algorithm execution.
- zu decision: Oracle is the mature SQL/PGQ and enterprise-integration baseline; it also demonstrates the cost of maintaining an analytical graph projection.

### 33. SAP HANA Cloud Property Graph Engine

- Family: in-memory relational-integrated graph engine.
- Lifecycle confidence: strong — active QRC 1/2026.
- Distributed-capacity alignment: strong — HANA scale-up/scale-out deployment depending edition.
- S3-authoritative alignment: weak — not S3-native live serving.
- Scale evidence: enterprise analytical scale; no public PB graph evidence.
- Principal benchmark issue: measure graph workspace creation, memory footprint, and mixed SQL/graph execution.
- zu decision: HANA Graph is a strong in-memory integrated baseline, but resource cost is the likely zu differentiator.

### 34. Stardog

- Family: enterprise RDF knowledge graph platform.
- Lifecycle confidence: strong — active 12.x-era platform.
- Distributed-capacity alignment: partial — HA cluster and federated/virtual query capabilities.
- S3-authoritative alignment: weak — not S3-native adjacency serving; cloud deployment and backups may use object storage.
- Scale evidence: enterprise knowledge graphs; PB interactive claim not public.
- Principal benchmark issue: benchmark SPARQL, reasoning, virtualization, and materialized data separately.
- zu decision: Stardog is the enterprise semantic/federation baseline rather than a direct LPG traversal peer.

### 35. Ontotext GraphDB

- Family: RDF store and reasoner.
- Lifecycle confidence: strong — active 11.x.
- Distributed-capacity alignment: partial — Raft-based HA cluster in current Enterprise line.
- S3-authoritative alignment: weak — not S3-native live serving.
- Scale evidence: large RDF stores; audited LDBC SNB result exists but workload/language fit must be examined.
- Principal benchmark issue: include materialization time/space and inferred versus explicit query modes.
- zu decision: GraphDB is the principal materialized-reasoning baseline and a lesson in separating explicit from derived bytes.

### 36. Apache Jena TDB2

- Family: embedded RDF store.
- Lifecycle confidence: strong — active Apache project.
- Distributed-capacity alignment: strong — single JVM; Fuseki provides network access, not distributed storage.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: single-node and filesystem-bound.
- Principal benchmark issue: strong correctness/reference baseline for RDF, not PB latency competitor.
- zu decision: TDB2 is a valuable compact local-store reference for CoW MVCC, dictionary IDs, and tuple permutations.

### 37. OpenLink Virtuoso

- Family: multi-model SQL/RDF server.
- Lifecycle confidence: strong — active commercial/open-source lineage.
- Distributed-capacity alignment: partial — Enterprise cluster and replication options.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: very large public RDF deployments, but PB interactive evidence is not current.
- Principal benchmark issue: use WatDiv/BSBM plus SQL/RDF hybrid cases and pin edition.
- zu decision: Virtuoso is the long-lived high-scale RDF/SQL baseline and a source of index-ordering lessons.

### 38. Oxigraph

- Family: embedded Rust RDF store.
- Lifecycle confidence: strong — active and explicitly still optimizing.
- Distributed-capacity alignment: weak — single-node library/server.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: single-node; no PB proof.
- Principal benchmark issue: conformance and resource efficiency matter more than headline throughput.
- zu decision: Oxigraph is the closest Rust RDF implementation reference and a useful fuzz/conformance comparator.

### 39. AllegroGraph

- Family: commercial RDF/knowledge graph database.
- Lifecycle confidence: strong — active 9.x line.
- Distributed-capacity alignment: strong — warm-standby replication and distributed/federated features.
- S3-authoritative alignment: weak — not S3-native live serving.
- Scale evidence: large knowledge graphs; current PB evidence unavailable.
- Principal benchmark issue: benchmark RDF semantics, reasoning, vector, and replication independently.
- zu decision: AllegroGraph matters for semantic workloads and mature operational features, not as the primary LPG latency target.

### 40. Blazegraph (legacy)

- Family: RDF graph database.
- Lifecycle confidence: weak — archived repository; historical benchmark baseline.
- Distributed-capacity alignment: strong — historical HA/scale-out commercial features.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: historically large Wikidata deployments; active-product status is unsuitable.
- Principal benchmark issue: retain for RDF regression only.
- zu decision: Blazegraph is historically important but must be labeled legacy to avoid a misleading 2026 comparison.

### 41. RedisGraph (legacy)

- Family: matrix property graph.
- Lifecycle confidence: strong — end-of-life lineage continued by FalkorDB.
- Distributed-capacity alignment: weak — Redis deployment topology.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: memory-oriented single-shard baseline.
- Principal benchmark issue: use only to show lineage or reproduce old papers.
- zu decision: RedisGraph should not be counted as an active separate competitor; FalkorDB is the maintained comparison.

### 42. Aerospike Graph

- Family: stateless Gremlin compute over distributed KV storage.
- Lifecycle confidence: strong — active commercial product.
- Distributed-capacity alignment: strong — independently scalable stateless AGS compute over automatically sharded Aerospike Database.
- S3-authoritative alignment: weak — not S3-native; Aerospike's flash/storage engine remains authoritative.
- Scale evidence: official docs target billions of graph elements; no public PB proof.
- Principal benchmark issue: measure graph-service fanout and underlying Aerospike record operations, not only client latency.
- zu decision: Aerospike Graph is a major low-latency distributed Gremlin comparator and a close analogue to stateless graph compute over a non-graph storage service.

### 43. Huawei Cloud Graph Engine Service (GES)

- Family: managed distributed graph engine.
- Lifecycle confidence: strong — active; GQL added in 2025 and docs refreshed in 2026.
- Distributed-capacity alignment: strong — managed distributed cloud service.
- S3-authoritative alignment: weak — not documented as S3-native live serving.
- Scale evidence: official material claims tens of billions of vertices and hundreds of billions of edges.
- Principal benchmark issue: 2025 LDBC audited results are the current public throughput bar.
- zu decision: GES must be included because its audited SF100/SF300/SF1000 results lead the public LDBC table; zu cannot claim 'all competitors' while omitting it.

### 44. DataStax Enterprise Graph

- Family: Cassandra-integrated distributed graph.
- Lifecycle confidence: weak — maintained DSE 6.9 documentation; legacy strategic baseline rather than a modern standalone graph focus.
- Distributed-capacity alignment: partial — shared-nothing Cassandra distribution and replication.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: DSE platform advertises petabyte data and graph billions, but graph-specific interactive proof must be separated.
- Principal benchmark issue: include Cassandra replication, consistency, Solr/Search, and Spark sidecars in resources.
- zu decision: DSE Graph is a historical PB-distributed reference and exposes the latency cost of building graph semantics on Cassandra-scale storage.

### 45. IBM Db2 Graph

- Family: Gremlin layer over Db2 relational data.
- Lifecycle confidence: weak — legacy/limited: current IBM page says standalone support is tied to Db2 11.5.6–11.5.8.
- Distributed-capacity alignment: strong — inherits Db2 deployment and read-scale features; graph layer is not native PB sharding.
- S3-authoritative alignment: weak — not S3-native.
- Scale evidence: Db2 platform scale; current graph lifecycle limits its competitive weight.
- Principal benchmark issue: retain as SQL/Gremlin compatibility baseline only if supported artifacts are obtainable.
- zu decision: Db2 Graph is included for completeness but labeled legacy so it cannot inflate current competitor coverage.

## Structural winners by dimension

- Embedded analytical execution: LadybugDB/Kuzu lineage and DuckPGQ.
- Sparse matrix traversal: FalkorDB.
- Hot mutable in-memory graph: Memgraph.
- Cypher ecosystem and mature operational database: Neo4j.
- Audited distributed throughput: GraphScope Flex and Huawei GES disclosures.
- Mature MPP graph analytics: TigerGraph.
- Distributed open graph stores: NebulaGraph, HugeGraph HStore, JanusGraph, Dgraph.
- Graph over lake/warehouse authority: PuppyGraph and Fabric Graph.
- Standards-integrated relational graph: Spanner Graph, Oracle SQL/PGQ, DuckPGQ.
- RDF reasoning and semantic operations: Stardog, GraphDB, Virtuoso, AllegroGraph.
- Immutable versioned graph: TerminusDB.
- Rust-native emerging graph/vector: HelixDB and SurrealDB; Rust RDF: Oxigraph.

## White space

No open system in this inventory conclusively combines immutable object-authoritative graph packs, stable logical edge identity, batched frontier range reads, vector/factorized GQL execution, enforced per-query request budgets, independently fenced partition writers, stateless horizontal readers, and FDR-quality cost benchmarks. That combination is zu's opportunity and its verification burden.

## Architecture choices rejected

- Remote KV call per adjacency entry.
- Reusing physical CSR slots as logical edge identity.
- Treating a manifest conditional write as a complete writer-fencing protocol.
- Claiming distributed ACID across independently published partition roots.
- Promising fixed cost from an assumed cache-hit rate.
- Benchmarking only query execution while excluding graph build/index time.
- Comparing hot in-memory execution with cold remote execution under one label.
- Claiming PB scale only by multiplying a compression ratio.
- Claiming universal 10x based on a selected latency microbenchmark.

## Appendix A. Release-gate assertions

- RG-001: For the landscape scorecard, release is blocked until the raw samples and aggregated chart agree.
- RG-002: For the landscape scorecard, release is blocked until the query result matches the canonical oracle.
- RG-003: For the landscape scorecard, release is blocked until the engine version and artifact digest are recorded.
- RG-004: For the landscape scorecard, release is blocked until the selected durability level matches the comparison class.
- RG-005: For the landscape scorecard, release is blocked until cache state is explicit and reproducible.
- RG-006: For the landscape scorecard, release is blocked until peak memory includes engine and required sidecars.
- RG-007: For the landscape scorecard, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-008: For the landscape scorecard, release is blocked until timeouts and rejected operations remain in the result set.
- RG-009: For the landscape scorecard, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-010: For the landscape scorecard, release is blocked until background maintenance is either quiesced or reported.
- RG-011: For the landscape scorecard, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-012: For the landscape scorecard, release is blocked until the dataset and update-stream digests are immutable.
- RG-013: For the landscape scorecard, release is blocked until the query plan/profile is archived.
- RG-014: For the landscape scorecard, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-015: For the landscape scorecard, release is blocked until a second operator can reproduce the run from a clean host.
- RG-016: For the landscape scorecard, release is blocked until the raw samples and aggregated chart agree.
- RG-017: For the landscape scorecard, release is blocked until the query result matches the canonical oracle.
- RG-018: For the landscape scorecard, release is blocked until the engine version and artifact digest are recorded.
- RG-019: For the landscape scorecard, release is blocked until the selected durability level matches the comparison class.
- RG-020: For the landscape scorecard, release is blocked until cache state is explicit and reproducible.
- RG-021: For the landscape scorecard, release is blocked until peak memory includes engine and required sidecars.
- RG-022: For the landscape scorecard, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-023: For the landscape scorecard, release is blocked until timeouts and rejected operations remain in the result set.
- RG-024: For the landscape scorecard, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-025: For the landscape scorecard, release is blocked until background maintenance is either quiesced or reported.
- RG-026: For the landscape scorecard, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
