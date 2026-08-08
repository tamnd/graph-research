# 2026 graph database research corpus

Research cut: `2026-08-08`
Minimum generated length: 520 lines per Markdown file
Purpose: evidence base for zu's low-latency, low-resource, distributed, S3-authoritative, fixed-cost, PB-scale design.

## Scope rule

The word `all` is operationalized as all engines with material 2026 adoption, benchmark relevance, architectural novelty, standards relevance, or historical baseline value found during the survey. It is not a claim that every private, abandoned, academic prototype, or graph API over a general database is included.

Every engine receives one file. Kuzu and RedisGraph remain separate historical files because benchmark reports still cite them, while LadybugDB and FalkorDB receive active successor files. Managed analytical services that are separate engines, such as Neptune Analytics, receive separate files.

## Reading order

1. Read `system-target-architecture.md` for the proposed design.
2. Read `system-benchmark-and-10x-claim.md` before using any performance statement.
3. Read `system-landscape-scorecard.md` for cross-engine classification.
4. Use the engine files for evidence, risks, and exact qualification work.

## Engine files

- [Neo4j](./engine-neo4j.md) — native property graph; active; calendar-versioned 2026 line.
- [FalkorDB](./engine-falkordb.md) — matrix property graph; active; Rust transition and Redis-module lineage.
- [LadybugDB](./engine-ladybugdb.md) — embedded analytical property graph; active successor fork in 2026.
- [Kuzu (archived)](./engine-kuzu.md) — embedded analytical property graph; archived 2025-10-10; historical baseline.
- [PuppyGraph](./engine-puppygraph.md) — lakehouse graph query engine; active commercial product.
- [Memgraph](./engine-memgraph.md) — in-memory operational property graph; active.
- [NebulaGraph](./engine-nebulagraph.md) — distributed property graph; active; Enterprise 5.2 was current in the 2025 review.
- [TigerGraph](./engine-tigergraph.md) — distributed native property graph; active; 4.2.4 released 2026-07-20.
- [GraphScope Flex Interactive](./engine-graphscope_flex.md) — distributed interactive graph system; active Apache-2.0 project.
- [JanusGraph](./engine-janusgraph.md) — storage-agnostic distributed graph layer; active 1.x.
- [Apache HugeGraph](./engine-apache_hugegraph.md) — pluggable OLTP plus OLAP graph platform; active Apache top-level project.
- [TuGraph](./engine-tugraph.md) — HTAP native property graph; active.
- [Ultipa Powerhouse](./engine-ultipa.md) — hybrid distributed and high-density graph system; active v5 line.
- [ArangoDB](./engine-arangodb.md) — native multi-model database; active.
- [Dgraph](./engine-dgraph.md) — distributed predicate-sharded graph database; active.
- [OrientDB](./engine-orientdb.md) — multi-model graph/document database; active 4.0 line but legacy architecture remains relevant.
- [ArcadeDB](./engine-arcadedb.md) — multi-model native graph database; active 26.x.
- [TypeDB](./engine-typedb.md) — typed polymorphic database; active 3.x; clustering was experimental/alpha in current docs.
- [TerminusDB](./engine-terminusdb.md) — version-controlled document graph database; active.
- [CozoDB](./engine-cozodb.md) — embedded relational-graph-vector database; maintenance activity appears limited after late 2024; verify before adoption.
- [SurrealDB](./engine-surrealdb.md) — distributed multi-model database; active 3.x.
- [HelixDB](./engine-helixdb.md) — Rust graph-vector database; active and fast-moving; 3.0.2 listed in May 2026.
- [MillenniumDB](./engine-millenniumdb.md) — research persistent graph database; active research project with small community.
- [DuckPGQ](./engine-duckpgq.md) — analytical SQL/PGQ extension; active CWI project.
- [Apache AGE](./engine-apache_age.md) — PostgreSQL graph extension; active Apache project.
- [AgensGraph — dedicated 2026 source audit](./agensgraph/00-index.md) — PostgreSQL-derived multi-model graph database; v2.17.0 plus separately pinned public 2.18-devel source. [Breadth overview](./engine-agensgraph.md).
- [Amazon Neptune Database](./engine-amazon_neptune.md) — managed cloud graph database; active AWS service.
- [Amazon Neptune Analytics](./engine-amazon_neptune_analytics.md) — managed in-memory graph analytics; active AWS service.
- [Google Cloud Spanner Graph](./engine-google_spanner_graph.md) — managed relational-property-graph database; active Enterprise/Enterprise Plus feature; docs updated 2026-07-22.
- [Azure Cosmos DB for Apache Gremlin](./engine-azure_cosmosdb_gremlin.md) — managed partitioned multi-model graph API; active.
- [Graph in Microsoft Fabric](./engine-microsoft_fabric_graph.md) — lakehouse graph analytics; active 2026 feature.
- [Oracle Database Property Graph](./engine-oracle_property_graph.md) — relational-integrated graph platform; active Oracle Database 26ai line.
- [SAP HANA Cloud Property Graph Engine](./engine-sap_hana_graph.md) — in-memory relational-integrated graph engine; active QRC 1/2026.
- [Stardog](./engine-stardog.md) — enterprise RDF knowledge graph platform; active 12.x-era platform.
- [Ontotext GraphDB](./engine-ontotext_graphdb.md) — RDF store and reasoner; active 11.x.
- [Apache Jena TDB2](./engine-apache_jena_tdb2.md) — embedded RDF store; active Apache project.
- [OpenLink Virtuoso](./engine-openlink_virtuoso.md) — multi-model SQL/RDF server; active commercial/open-source lineage.
- [Oxigraph](./engine-oxigraph.md) — embedded Rust RDF store; active and explicitly still optimizing.
- [AllegroGraph](./engine-allegrograph.md) — commercial RDF/knowledge graph database; active 9.x line.
- [Blazegraph (legacy)](./engine-blazegraph.md) — RDF graph database; archived repository; historical benchmark baseline.
- [RedisGraph (legacy)](./engine-redisgraph.md) — matrix property graph; end-of-life lineage continued by FalkorDB.
- [Aerospike Graph — dedicated 2026 source audit](./aerospike/00-index.md) — stateless Gremlin compute over distributed KV storage; released 3.2.3 plus pinned public 3.3.0-SNAPSHOT source. [Breadth overview](./engine-aerospike_graph.md).
- [Huawei Cloud Graph Engine Service (GES)](./engine-huawei_ges.md) — managed distributed graph engine; active; GQL added in 2025 and docs refreshed in 2026.
- [DataStax Enterprise Graph](./engine-datastax_enterprise_graph.md) — Cassandra-integrated distributed graph; maintained DSE 6.9 documentation; legacy strategic baseline rather than a modern standalone graph focus.
- [IBM Db2 Graph](./engine-ibm_db2_graph.md) — Gremlin layer over Db2 relational data; legacy/limited: current IBM page says standalone support is tied to Db2 11.5.6–11.5.8.

## Coverage classes

### Native and embedded property graph

Neo4j, FalkorDB, LadybugDB, Kuzu, Memgraph, TuGraph, and emerging HelixDB cover direct adjacency, low-latency serving, analytical factorization, sparse matrices, and Rust-native designs.

### Distributed property graph

NebulaGraph, TigerGraph, GraphScope Flex, JanusGraph, Apache HugeGraph, Ultipa, Dgraph, ArangoDB, and managed Neptune cover shared-nothing, replicated, predicate-sharded, locality-sharded, and shared-storage patterns.

### Lakehouse and relational graph

PuppyGraph, DuckPGQ, Apache AGE, AgensGraph, Spanner Graph, Fabric Graph, Oracle Property Graph, SAP HANA Graph, and Cosmos DB Gremlin cover graph-over-tables, materialized traversal projections, SQL/PGQ, and source-partition-aware APIs.

### Semantic and RDF

Stardog, GraphDB, Jena TDB2, Virtuoso, Oxigraph, AllegroGraph, Blazegraph, TerminusDB, TypeDB, and MillenniumDB cover RDF permutations, reasoning, Datalog, strong schemas, versioning, and path-query research.

## Evidence hierarchy

- Level 1: reproducible local source inspection and a pinned benchmark artifact.
- Level 2: official versioned documentation or a standards conformance declaration.
- Level 3: audited benchmark full-disclosure report.
- Level 4: peer-reviewed paper tied to a specific version/configuration.
- Level 5: vendor benchmark or capacity claim, explicitly labeled.
- Level 6: inference that creates a hypothesis, never a fact.

## Global conclusions

- No surveyed engine simultaneously proves local-class hot latency, tiny resource footprint, distributed transactional writes, S3-only authority, predictable fixed cost, PB capacity, and a tenfold win on every graph workload.
- The attainable product is a set of honest profiles sharing semantics: embedded/local, remote single-writer, and partitioned read-scale. A universal profile would conceal contradictions.
- S3 can be the durable authority, but low latency then comes from immutable IDs, coarse range-addressable tiles, batched frontier reads, and RAM/NVMe caches—not from remote pointer chasing.
- Fixed cost is an admission-control contract backed by bounded compute and remote I/O, not an emergent property of S3 pricing.
- PB scale is mostly a metadata, partitioning, compaction, GC, and skew problem after the per-edge byte budget is solved.
- A tenfold advantage must be a matrix of qualified wins. Some cells will target parity, lower memory, lower dollars, or unique capability instead of latency.

## Known exclusions and why

Graph processing frameworks without an online database contract, visualization products, pure vector databases, generic SQL databases without a maintained graph surface, and private internal engines without enough public evidence are not assigned engine files. They can still appear as architectural sources or benchmark references.

## Maintenance protocol

At every quarterly refresh: recheck product lifecycle, latest stable release, license, distribution capability, object-storage claims, GQL/SQL-PGQ support, audited results, and any public scale limit. A changed fact updates the engine file and the scorecard in one commit.

## Appendix A. Release-gate assertions

- RG-001: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-002: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-003: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-004: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-005: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-006: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-007: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-008: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-009: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-010: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-011: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-012: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-013: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-014: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-015: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-016: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-017: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-018: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-019: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-020: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-021: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-022: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-023: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-024: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-025: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-026: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-027: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-028: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-029: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-030: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-031: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-032: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-033: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-034: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-035: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-036: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-037: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-038: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-039: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-040: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-041: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-042: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-043: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-044: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-045: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-046: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-047: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-048: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-049: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-050: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-051: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-052: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-053: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-054: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-055: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-056: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-057: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-058: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-059: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-060: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-061: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-062: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-063: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-064: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-065: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-066: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-067: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-068: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-069: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-070: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-071: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-072: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-073: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-074: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-075: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-076: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-077: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-078: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-079: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-080: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-081: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-082: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-083: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-084: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-085: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-086: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-087: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-088: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-089: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-090: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-091: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-092: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-093: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-094: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-095: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-096: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-097: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-098: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-099: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-100: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-101: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-102: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-103: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-104: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-105: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-106: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-107: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-108: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-109: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-110: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-111: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-112: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-113: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-114: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-115: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-116: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-117: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-118: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-119: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-120: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-121: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-122: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-123: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-124: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-125: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-126: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-127: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-128: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-129: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-130: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-131: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-132: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-133: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-134: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-135: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-136: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-137: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-138: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-139: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-140: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-141: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-142: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-143: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-144: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-145: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-146: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-147: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-148: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-149: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-150: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-151: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-152: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-153: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-154: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-155: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-156: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-157: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-158: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-159: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-160: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-161: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-162: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-163: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-164: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-165: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-166: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-167: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-168: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-169: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-170: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-171: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-172: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-173: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-174: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-175: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-176: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-177: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-178: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-179: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-180: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-181: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-182: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-183: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-184: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-185: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-186: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-187: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-188: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-189: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-190: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-191: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-192: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-193: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-194: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-195: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-196: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-197: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-198: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-199: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-200: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-201: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-202: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-203: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-204: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-205: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-206: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-207: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-208: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-209: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-210: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-211: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-212: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-213: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-214: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-215: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-216: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-217: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-218: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-219: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-220: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-221: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-222: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-223: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-224: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-225: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-226: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-227: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-228: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-229: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-230: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-231: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-232: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-233: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-234: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-235: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-236: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-237: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-238: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-239: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-240: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-241: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-242: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-243: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-244: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-245: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-246: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-247: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-248: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-249: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-250: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-251: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-252: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-253: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-254: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-255: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-256: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-257: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-258: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-259: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-260: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-261: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-262: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-263: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-264: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-265: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-266: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-267: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-268: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-269: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-270: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-271: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-272: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-273: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-274: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-275: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-276: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-277: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-278: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-279: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-280: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-281: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-282: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-283: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-284: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-285: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-286: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-287: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-288: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-289: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-290: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-291: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-292: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-293: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-294: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-295: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-296: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-297: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-298: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-299: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-300: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-301: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-302: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-303: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-304: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-305: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-306: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-307: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-308: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-309: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-310: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-311: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-312: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-313: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-314: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-315: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-316: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-317: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-318: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-319: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-320: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-321: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-322: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-323: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-324: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-325: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-326: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-327: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-328: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-329: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-330: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-331: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-332: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-333: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-334: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-335: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-336: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-337: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-338: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-339: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-340: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-341: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-342: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-343: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-344: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-345: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-346: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-347: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-348: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-349: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-350: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-351: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-352: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-353: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-354: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-355: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-356: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-357: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-358: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-359: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-360: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-361: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-362: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-363: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-364: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-365: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-366: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-367: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-368: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-369: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-370: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-371: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-372: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-373: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-374: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-375: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-376: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-377: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-378: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-379: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-380: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-381: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-382: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-383: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-384: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-385: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-386: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-387: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-388: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-389: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-390: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-391: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-392: For the research inventory, release is blocked until the query result matches the canonical oracle.
- RG-393: For the research inventory, release is blocked until the engine version and artifact digest are recorded.
- RG-394: For the research inventory, release is blocked until the selected durability level matches the comparison class.
- RG-395: For the research inventory, release is blocked until cache state is explicit and reproducible.
- RG-396: For the research inventory, release is blocked until peak memory includes engine and required sidecars.
- RG-397: For the research inventory, release is blocked until storage size includes indexes, logs, replicas, and temporary space.
- RG-398: For the research inventory, release is blocked until timeouts and rejected operations remain in the result set.
- RG-399: For the research inventory, release is blocked until remote requests and bytes are measured rather than estimated.
- RG-400: For the research inventory, release is blocked until background maintenance is either quiesced or reported.
- RG-401: For the research inventory, release is blocked until thread, NUMA, and CPU-affinity settings are captured.
- RG-402: For the research inventory, release is blocked until the dataset and update-stream digests are immutable.
- RG-403: For the research inventory, release is blocked until the query plan/profile is archived.
- RG-404: For the research inventory, release is blocked until unsupported features are not replaced by weaker semantics.
- RG-405: For the research inventory, release is blocked until a second operator can reproduce the run from a clean host.
- RG-406: For the research inventory, release is blocked until the raw samples and aggregated chart agree.
- RG-407: For the research inventory, release is blocked until the query result matches the canonical oracle.
