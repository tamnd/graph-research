#!/usr/bin/env python3
"""Generate the Aerospike deep-audit dossier.

The prose and test cases in this file are deliberately Aerospike-specific.
This is not the broad engine template used by the parent research corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


OUT = Path(__file__).resolve().parents[2] / "docs" / "research" / "aerospike"
RESEARCH_DATE = "2026-08-08"
AGS_COMMIT = "ad0983e5519cbd3705f70113afd7df048c568045"
AGS_RC5_COMMIT = "f4980a73f64bde1f3db0b30e917f3ec7fb147ce3"
GRAPH_COMMIT = "e2300bc201f949c4261ecd88b235dea1877fa088"
SERVER_COMMIT = "3c13b0de02f5ccaa6fffd8b9bbf3387b0c6a12dc"
CLIENT_COMMIT = "9d1f99a66f6590a3c489f6b0dd1589adcb8a1c12"


SOURCES = [
    ("S01", "AGS release index", "Official documentation", "2026-06-30 latest listed release", "https://aerospike.com/docs/graph/release"),
    ("S02", "AGS 3.2.3 release notes", "Official documentation", "Security-only patch; 14 CVEs listed", "https://aerospike.com/docs/graph/release/3-2-3/"),
    ("S03", "AGS 3.2.2 release notes", "Official documentation", "Removed graph-service feature check", "https://aerospike.com/docs/graph/release/3-2-2/"),
    ("S04", "AGS 3.2.1 release notes", "Official documentation", "Container memory and rack awareness", "https://aerospike.com/docs/graph/release/3-2-1/"),
    ("S05", "AGS 3.2.0 release notes", "Official documentation", "Global cache, set cardinality, performance changes", "https://aerospike.com/docs/graph/release/3-2-0/"),
    ("S06", "AGS 3.1.1 release notes", "Official documentation", "CVE-2025-12383 fix", "https://aerospike.com/docs/graph/release/3-1-1/"),
    ("S07", "AGS 3.1.0 release notes", "Official documentation", "TinkerPop transactions and typed indexes", "https://aerospike.com/docs/graph/release/3-1-0/"),
    ("S08", "AGS 3.0.0 release notes", "Official documentation", "Packed model revision and reload boundary", "https://aerospike.com/docs/graph/release/3-0-0/"),
    ("S09", "Architecture", "Official documentation", "Three-layer request path", "https://aerospike.com/docs/graph/overview/architecture/"),
    ("S10", "Transaction contract", "Official documentation", "Read, mutation, SC, AP, and MRT distinctions", "https://aerospike.com/docs/graph/develop/query/transactions/"),
    ("S11", "Indexing", "Official documentation", "Vertex index and scan controls", "https://aerospike.com/docs/graph/develop/query/indexing/"),
    ("S12", "Supernodes", "Official documentation", "Thresholds and filtered traversal guidance", "https://aerospike.com/docs/graph/develop/query/supernodes/"),
    ("S13", "Query threading", "Official documentation", "Per-query parallelization and batch/page controls", "https://aerospike.com/docs/graph/develop/query/query-threading/"),
    ("S14", "Cache management", "Official documentation", "Transactional and global record caches", "https://aerospike.com/docs/graph/manage/cache/"),
    ("S15", "Data types", "Official documentation", "Property and index type limitations", "https://aerospike.com/docs/graph/develop/query/data-type-support/"),
    ("S16", "TinkerPop feature support", "Official documentation", "Feature compatibility matrix", "https://aerospike.com/docs/graph/overview/tinkerpop/"),
    ("S17", "Configuration reference", "Official documentation", "AGS runtime knobs", "https://aerospike.com/docs/graph/reference/config/"),
    ("S18", "Metrics reference", "Official documentation", "Prometheus metric inventory", "https://aerospike.com/docs/graph/reference/metrics/"),
    ("S19", "Query tracing", "Official documentation", "Zipkin tracing contract", "https://aerospike.com/docs/graph/observe/query-tracing/"),
    ("S20", "Bulk load overview", "Official documentation", "Standalone and Spark paths", "https://aerospike.com/docs/graph/load/overview/"),
    ("S21", "Distributed bulk load", "Official documentation", "EMR and Dataproc workflow", "https://aerospike.com/docs/graph/load/distributed/"),
    ("S22", "Graph backup and restore", "Official documentation", "Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page", "https://aerospike.com/docs/graph/manage/backup/"),
    ("S23", "Security", "Official documentation", "TLS, JWT RBAC, database RBAC, audit", "https://aerospike.com/docs/graph/manage/security/"),
    ("S24", "Multi-tenancy", "Official documentation", "Graph scoping in a shared namespace", "https://aerospike.com/docs/graph/manage/multi-tenant/"),
    ("S25", "Identity graph benchmark PDF", "Vendor benchmark", "AGS 2.4.2 / Database 7.1.0.9 test", "https://aerospike.com/files/benchmarks/aerospike-graph-performance-benchmark.pdf"),
    ("S26", "Graph 3.0 launch blog", "Vendor blog", "Ingest and footprint claims", "https://aerospike.com/blog/aerospike-graph-3-release/"),
    ("S27", "Architecture deep-dive blog", "Vendor blog", "Optimizer and record-model explanation", "https://aerospike.com/blog/graphing-database-architecture/"),
    ("S28", "Product editions and pricing", "Official commercial page", "Edition limits and data-volume licensing", "https://aerospike.com/products/features-and-editions/"),
    ("S29", "Database platform support", "Official documentation", "Current Database release matrix", "https://aerospike.com/docs/database/reference/platform-support"),
    ("S30", "Database limits", "Official documentation", "Cluster and object limits", "https://aerospike.com/docs/database/reference/limitations/"),
    ("S31", "Database storage configuration", "Official documentation", "Memory, device, and persistence modes", "https://aerospike.com/docs/database/manage/namespace/storage/config/"),
    ("S32", "Database FAQ", "Official documentation", "CE/SE/EE/FE boundaries", "https://aerospike.com/docs/database/reference/faq"),
    ("S33", "AGS public source snapshot", "Apache-2.0 source", f"3.x-dev at {AGS_COMMIT}", f"https://github.com/aerospike/aerospike-graph-service/tree/{AGS_COMMIT}"),
    ("S34", "AGS data model design", "Apache-2.0 source documentation", "Packed record layout", f"https://github.com/aerospike/aerospike-graph-service/blob/{AGS_COMMIT}/docs/DATA_MODEL_DESIGN.md"),
    ("S35", "AGS architecture source map", "Apache-2.0 source documentation", "Modules and entry points", f"https://github.com/aerospike/aerospike-graph-service/blob/{AGS_COMMIT}/docs/ARCHITECTURE.md"),
    ("S36", "AGS AerospikeOperations", "Apache-2.0 source", "Read/write and edge mutation pipeline", f"https://github.com/aerospike/aerospike-graph-service/blob/{AGS_COMMIT}/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/AerospikeOperations.java"),
    ("S37", "AGS configuration source", "Apache-2.0 source", "Code defaults and validators", f"https://github.com/aerospike/aerospike-graph-service/blob/{AGS_COMMIT}/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/util/config/ConfigurationHelper.java"),
    ("S38", "AGS query code", "Apache-2.0 source", "Paged scans and secondary-index queries", f"https://github.com/aerospike/aerospike-graph-service/tree/{AGS_COMMIT}/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/io/aerospike/query"),
    ("S39", "AGS traversal strategies", "Apache-2.0 source", "Rewrite implementations", f"https://github.com/aerospike/aerospike-graph-service/tree/{AGS_COMMIT}/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/process/traversal/strategy"),
    ("S40", "AGS transaction implementation", "Apache-2.0 source", "TinkerPop transaction wrapper", f"https://github.com/aerospike/aerospike-graph-service/blob/{AGS_COMMIT}/aerospike-graph-gremlin/src/main/java/com/aerospike/firefly/structure/transaction/FireflyTransaction.java"),
    ("S41", "AGS tests", "Apache-2.0 source", "431 test files observed in snapshot", f"https://github.com/aerospike/aerospike-graph-service/tree/{AGS_COMMIT}/aerospike-graph-gremlin/src/test"),
    ("S42", "Graph examples", "Apache-2.0 source", f"Examples at {GRAPH_COMMIT}", f"https://github.com/aerospike/aerospike-graph/tree/{GRAPH_COMMIT}"),
    ("S43", "Database server source snapshot", "AGPL/community core source", f"Server at {SERVER_COMMIT}", f"https://github.com/aerospike/aerospike-server/tree/{SERVER_COMMIT}"),
    ("S44", "Java client source snapshot", "Apache-2.0 source", f"Client at {CLIENT_COMMIT}", f"https://github.com/aerospike/aerospike-client-java/tree/{CLIENT_COMMIT}"),
    ("S45", "Apache TinkerPop 3.7.3 reference", "Upstream documentation", "Language/runtime semantic oracle", "https://tinkerpop.apache.org/docs/3.7.3/reference/"),
    ("S46", "AGS v3.3.0-rc5 prerelease tag", "Signed public source tag", f"Newest public prerelease observed on {RESEARCH_DATE}; commit {AGS_RC5_COMMIT}", f"https://github.com/aerospike/aerospike-graph-service/tree/{AGS_RC5_COMMIT}"),
    ("S47", "Graph 2.5 strong-consistency launch blog", "Vendor blog", "Database 8 transaction positioning and the explicit eventual-read caveat", "https://aerospike.com/blog/aerospike-graph-2-5-0-strong-consistency"),
    ("S48", "Aerospike Graph AI and MCP blog", "Vendor blog", "Newest Graph-specific blog found in the publication sweep; an integration/demo layer, not a storage-engine release", "https://aerospike.com/blog/aerospike-graph-ai-mcp-natural-language-queries/"),
    ("S49", "Legacy asbackup documentation", "Official documentation", "The target of the current Graph backup-page link; explicitly labeled legacy", "https://aerospike.com/docs/database/tools/backup-and-restore/asbackup"),
    ("S50", "Current Database backup and restore overview", "Official documentation", "ABS and absctl are current choices while asbackup/asrestore are legacy", "https://aerospike.com/docs/database/tools/backup-and-restore/overview/"),
]


@dataclass(frozen=True)
class Case:
    name: str
    purpose: str
    setup: str
    workload: str
    counters: str
    oracle: str
    failure: str
    sources: str


class Markdown:
    def __init__(self, title: str, scope: str):
        self.lines: list[str] = [
            f"# {title}", "",
            f"Research cut: `{RESEARCH_DATE}`",
            "Evidence status: current-source audit; vendor claims remain claims until reproduced",
            f"Scope: {scope}",
            f"Pinned AGS source: `{AGS_COMMIT}` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)",
            f"Newest prerelease observed: `v3.3.0-rc5` at `{AGS_RC5_COMMIT}`; not the stable baseline",
            "Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30", "",
        ]

    def h(self, level: int, text: str) -> None:
        self.lines += [f"{'#' * level} {text}", ""]

    def p(self, text: str) -> None:
        for para in dedent(text).strip().split("\n\n"):
            self.lines.extend(line.rstrip() for line in para.splitlines())
            self.lines.append("")

    def bullets(self, rows: list[str]) -> None:
        self.lines.extend(f"- {row}" for row in rows)
        self.lines.append("")

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        self.lines.append("| " + " | ".join(headers) + " |")
        self.lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            self.lines.append("| " + " | ".join(cell.replace("|", "\\|") for cell in row) + " |")
        self.lines.append("")

    def cases(self, title: str, cases: list[Case]) -> None:
        self.h(2, title)
        self.p("Every case is a separate result cell. Do not average across cases, silently retry failures, or substitute a smaller semantic operation. Capture cold, warm, steady-state, degraded, and recovery intervals where applicable.")
        for i, c in enumerate(cases, 1):
            self.h(3, f"Q{i:03d} — {c.name}")
            self.lines += [
                f"- Purpose: {c.purpose}",
                f"- Setup: {c.setup}",
                f"- Workload: {c.workload}",
                f"- Required counters: {c.counters}",
                f"- Correctness oracle: {c.oracle}",
                f"- Failure interpretation: {c.failure}",
                f"- Evidence anchors: {c.sources}",
                "- Result status: `NOT RUN`; no number from this protocol is claimed by this audit.",
                "- Artifact requirement: immutable config, dataset manifest, query text/bytecode, raw samples, traces, server stats, and cost sheet.",
                "",
            ]

    def sources(self, ids: set[str] | None = None) -> None:
        self.h(2, "Source register")
        self.p("The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.")
        for sid, title, kind, note, url in SOURCES:
            if ids is None or sid in ids:
                self.h(3, f"{sid} — {title}")
                self.lines += [f"- Type: {kind}", f"- Audit note: {note}", f"- URL: {url}", ""]

    def write(self, name: str) -> None:
        while self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.lines.append("")
        (OUT / name).write_text("\n".join(self.lines).rstrip() + "\n", encoding="utf-8")


def expand_cases(prefix: str, items: list[tuple[str, str]], setup: str, counters: str, sources: str) -> list[Case]:
    cases = []
    for name, purpose in items:
        cases.append(Case(
            f"{prefix}: {name}", purpose, setup,
            f"Execute the smallest semantically complete operation for `{name}`, then repeat under controlled concurrency and skew.",
            counters,
            "Compare exact result bags/order/path identity and durable state against the model oracle; verify after restart when writes occur.",
            "Any unsupported behavior, timeout, stale value, semantic mismatch, hidden scan, or unbounded resource growth is a first-class result.",
            sources,
        ))
    return cases


def make_index() -> None:
    d = Markdown("Aerospike Graph 2026 dossier: index, verdict, and evidence map", "Navigation and decision summary for all Aerospike-specific specifications")
    d.h(2, "Outcome")
    d.p("""
    Aerospike Graph is a serious comparator for low-latency distributed property-graph serving, especially when the graph is much larger than DRAM and the workload is bounded, ID-rooted, and dominated by ordinary-degree vertices. Its key design is not a graph-native distributed storage engine: it is a stateless TinkerPop/Gremlin JVM service that maps graph operations onto Aerospike Database records, collection operations, batch operations, filter expressions, secondary indexes, and—when explicitly enabled on the right edition—multi-record transactions.

    It does not satisfy the project's S3-authoritative fixed-cost goal. S3 and GCS are bulk-loader inputs or backup destinations, while live authoritative graph records remain in an Aerospike namespace backed by memory and/or block/NVMe-class storage. Enterprise scale, strong consistency, rack awareness, TLS/ACLs, XDR, and multi-record transactions introduce commercial edition or add-on boundaries. The official pricing page says production licensing is primarily based on unique data volume, which is directly opposed to an S3-only fixed marginal-cost target.

    There is no evidence for a universal tenfold win by Aerospike or against Aerospike. The current public identity benchmark is useful scale evidence—up to 38.3 billion vertices and 37.2 billion edges, 23.35 TB user dataset, and a vendor-reported 600K QPS with 32 AGS nodes—but it is vendor-run, uses AGS 2.4.2 and Database 7.1.0.9, exposes no raw sample archive in the PDF, contains no competitor run, and tests sparse localized identity subgraphs. It is not PB or trillion-edge proof.
    """)
    d.h(2, "Dossier files")
    files = [
        ("01-product-releases-and-evidence.md", "Release chronology, product/edition boundary, source freshness, conflicts, claims"),
        ("02-source-code-and-storage-model.md", "Pinned source audit, sets/bins, packed edges, IDs, schema, indexes, supernodes"),
        ("03-gremlin-query-execution.md", "TinkerPop contract, compiler strategies, I/O paths, caching, scans, profiling"),
        ("04-transactions-distribution-and-failure.md", "Read consistency, AP/SC mutations, MRT, TinkerPop transactions, failover"),
        ("05-operations-resources-security-and-cost.md", "Deployment, sizing, JVM/DB resources, monitoring, backup, S3, security, price"),
        ("06-benchmark-audit-and-10x-qualification.md", "Vendor benchmark deconstruction and reproducible comparison program"),
        ("07-design-lessons-for-zu.md", "Concrete design choices, avoidances, experiments, and acceptance gates for zu"),
    ]
    d.table(["File", "Purpose"], [[f"[{f}](./{f})", p] for f, p in files])
    d.h(2, "Evidence precedence")
    d.bullets([
        "A reproducible observation from a pinned shipped artifact outranks documentation.",
        "Released 3.2.3 documentation outranks the 3.3.0-SNAPSHOT source tree for supported-product claims.",
        "Pinned source is authoritative for what that commit implements, not for what the 3.2.3 container contains.",
        "Release notes are authoritative for declared changes, not the magnitude of performance outside the vendor workload.",
        "Vendor benchmark numbers are recorded as vendor results until raw artifacts are independently rerun.",
        "Blogs are context and claim sources; they are never the sole semantic or durability oracle.",
        "Unknown remains Unknown when commercial internals, license terms, or raw benchmark data are absent.",
    ])
    findings = [
        ("Current release", "3.2.3 is the newest released version in the official release index on the research date.", "S01,S02"),
        ("Source head", "The audited public AGS branch is 3.x-dev and declares 3.3.0-SNAPSHOT; signed v3.3.0-rc5 appeared on the research date.", "S33,S46"),
        ("Open source", "AGS source carries Apache-2.0; the underlying Community Database core is AGPL while Enterprise features are commercial.", "S32,S33,S43"),
        ("Protocol", "Clients send TinkerPop 3.7.x Gremlin bytecode over WebSocket; 3.8.x and 4.x are incompatible.", "S09,S16,S33,S45"),
        ("Compute", "AGS instances are durable-state-free compute nodes and can be load balanced without AGS-to-AGS coordination.", "S09,S35"),
        ("Storage authority", "Aerospike Database is authoritative; object storage is not on the online read/write path.", "S09,S20,S22,S31"),
        ("Vertex layout", "A normal vertex maps to one record and carries label, properties, and cached adjacency.", "S27,S34,S36"),
        ("Edge layout", "Logical edges are packed into shared edge records; the source default is 10 and accepted range is 1–100.", "S34,S37"),
        ("Hop cost", "An ordinary traversal can exploit embedded adjacency and batch fetches, but it is not literally one storage read for every out() result.", "S34,S36,S39"),
        ("Supernodes", "Large-degree vertices irreversibly leave the inline adjacency path and use secondary-index-backed edge records.", "S12,S34"),
        ("Threshold", "Documentation estimates ~6,500 edges at 1 MiB max-record-size and ~800 at 128 KiB in HMA mode.", "S12"),
        ("Indexes", "Vertex label/property indexes are supported; global edge label/property indexes are absent in the audited source design.", "S11,S34"),
        ("Scan hazard", "Global V()/E() patterns may scan; 3.2.0 added global and per-traversal scan disable controls.", "S05,S11"),
        ("Optimizer", "The code exposes more than twenty traversal strategies for batching, pushdown, local counts, IDs, caching, drop, and merge.", "S39"),
        ("Default execution", "A query normally uses one Gremlin worker; per-query parallelize is intended for I/O-heavy high-fanout work.", "S13,S37"),
        ("Read cache", "Transactional cache is default and request-local; global cache can be stale even after AGS writes.", "S14,S37"),
        ("Read consistency", "The shipped transaction page explicitly classifies read-only queries as eventual-consistency reads.", "S10"),
        ("Mutation consistency", "Atomic/isolated multi-record graph mutations require SC plus enabled MRT on Enterprise Database 8+.", "S10"),
        ("AP risk", "AP mode lacks MRT/TinkerPop transactions and can lose writes during splits; only enumerated mutation forms are atomic.", "S10"),
        ("Transaction limit", "A TinkerPop transaction can modify at most 4096 records and cannot use scans or indexes.", "S10"),
        ("Supernode drop", "Dropping a supernode is best-effort even in the documented transaction mode.", "S10,S36"),
        ("MRT default", "Both aerospike.graph.mrt.enabled and aerospike.graph.tx.enabled default false in source.", "S37"),
        ("Release storage change", "3.0 introduced a new data layout and vendor-claimed up to 50% lower footprint; migration/reload must be qualified.", "S08,S26"),
        ("3.2 cache", "Global cache arrived in 3.2.0 and is a correctness/performance mode, not a transparent optimization.", "S05,S14"),
        ("3.2 scan claim", "3.2.0 claims 10x faster g.E() scans, which is version-over-version and not competitor evidence.", "S05"),
        ("3.2 security", "3.2.3 lists fourteen CVE fixes, so earlier 3.2 images should not be baseline candidates.", "S02"),
        ("Bulk path", "Large loads are external Spark jobs and may stage input on S3/GCS; Spark cost must be charged.", "S20,S21"),
        ("3.0 ingest claim", "The launch blog reports 1 TB under three hours versus more than 32 hours on 2.6 using the same infrastructure.", "S26"),
        ("Published large run", "The identity benchmark reaches 38.3B vertices, 37.2B edges, and 23.35TB user data.", "S25"),
        ("Benchmark workload shape", "The dataset is many sparse localized subgraphs, not one deep/high-diameter or supernode-heavy graph.", "S25"),
        ("Benchmark topology", "Largest latency run used 18 database nodes, one 8-vCPU AGS, RF2, and HMA on local NVMe.", "S25"),
        ("Throughput claim", "The vendor reports 22K QPS on one AGS to over 600K on 32 AGS nodes with fixed storage.", "S25"),
        ("Missing raw data", "The PDF charts do not provide a machine-readable raw latency sample bundle or exact query source archive.", "S25"),
        ("No comparison", "The identity report contains no same-hardware competitor run and cannot support a 10x competitor claim.", "S25"),
        ("No PB proof", "Neither current public benchmark nor release material demonstrates a PB live graph.", "S01,S25,S26"),
        ("No trillion-edge proof", "37.2B edges is substantial but ~27x below one trillion and ~27,000x below one quadrillion.", "S25"),
        ("Primary-index pressure", "Edge packing reduces record count and therefore underlying primary-index metadata, but vertices remain record-per-vertex.", "S34,S43"),
        ("Resource floor", "AGS is a JVM/TinkerPop service plus an Aerospike cluster; one process RSS is not the system resource footprint.", "S09,S35"),
        ("Cost boundary", "Enterprise pricing is contact-only and primarily unique-production-data-volume based.", "S28"),
        ("CE boundary", "Community Edition is free but capped at 8 nodes and 2.5TB on the current edition page and lacks key enterprise features.", "S28"),
        ("S3 mismatch", "S3 lowers load/backup storage cost but cannot replace the live namespace without changing the engine.", "S20,S22,S31"),
        ("Backup", "Graph backup delegates to Aerospike backup/restore; consistency, indexes, metadata, and restore time need an end-to-end drill.", "S22"),
        ("Multi-tenancy", "Graphs can share a namespace, but logical tenancy does not prove performance or failure isolation.", "S24"),
        ("Security layers", "Client-to-AGS TLS/JWT and AGS-to-Database TLS/RBAC are distinct configurations and failure domains.", "S23"),
        ("Rack-aware reads", "AGS 3.2.1 exposes Aerospike client rack awareness; it affects locality, not data placement by itself.", "S04,S44"),
        ("Observability", "Prometheus, health, query tracing, scan profiling, cache stats, and database stats must be correlated.", "S18,S19"),
        ("Conflict: client version", "The source POM pins 10.3.0 while its compatibility prose says 9.3.x; the POM wins for that commit.", "S33"),
        ("Conflict: MRT minimum", "Shipped docs require EE 8.0+, while source prose contains broader 7.0+/6.0 statements; qualify against shipped docs.", "S10,S33"),
        ("Upgrade evidence", "The public tags observed are 3.3 release candidates; no tag maps the audited source to the 3.2.3 shipped image, so source-to-binary equivalence is unproven.", "S02,S33,S46"),
        ("zu opportunity", "S3 authority, compact immutable adjacency, bounded caching, vectorized native execution, and transparent cost counters target its gaps.", "inference"),
    ]
    d.h(2, "Fifty decision-relevant findings")
    for i, (name, fact, src) in enumerate(findings, 1):
        d.h(3, f"F{i:02d} — {name}")
        d.lines += [f"- Finding: {fact}", f"- Evidence: {src}", "- Status: verified statement about the cited source; performance remains unverified unless explicitly described as an observation.", ""]
    d.h(2, "Immediate competitive stance")
    d.table(["Goal", "Aerospike posture", "Qualification consequence"], [
        ["Very low latency", "Strong candidate for bounded ID-rooted traversals on HMA/NVMe", "Split normal, threshold, and supernode regimes; report p50/p95/p99/p99.9 and backend operations"],
        ["Very low resources", "Edge packing helps DB metadata; AGS JVM and PI/SI RAM remain", "Charge all AGS, DB replicas, Spark, page cache, and storage headroom"],
        ["Distributed", "Stateless compute over sharded replicated DB", "Test compute scale and storage saturation separately"],
        ["Fixed cost", "Commercial licensing is data-volume based; infra is provisioned", "Cannot label fixed-cost without a quoted contract and capacity envelope"],
        ["S3 authority", "Unsupported for live graph", "Treat as architectural non-fit, not a tuning gap"],
        ["PB/trillion scale", "Public proof stops at tens of TB/billions", "Require derived capacity plus staged empirical validation"],
        ["10x", "No comparable public proof", "Claim only per workload cell under equal semantics and resources"],
    ])
    d.h(2, "Open evidence that blocks stronger conclusions")
    unknowns = [
        ("3.2.3 source equivalence", "No public tag or attestation maps the audited 3.3 snapshot to the shipped 3.2.3 image.", "Archive image/SBOM and request vendor source provenance."),
        ("Raw benchmark samples", "The public identity PDF provides charts and summaries but no raw HDR/sample archive.", "Obtain raw output or rerun from a published harness."),
        ("Exact benchmark Gremlin", "Descriptions of SR1–SR5 and SW1–SW5 are not executable query definitions.", "Publish bytecode/scripts, parameters, and result-cardinality distributions."),
        ("Benchmark cache state", "The report does not fully specify AGS/database cache preconditioning for every graph.", "Run named cold, warm, and steady-state phases."),
        ("Benchmark errors/retries", "The report does not expose per-query timeout, error, and retry counts alongside QPS.", "Require offered/achieved load and all outcomes."),
        ("Current 3.2 performance", "The large identity run used AGS 2.4.2, not 3.2.3.", "Repeat on 3.2.3 with Database 8.1.2 and publish deltas."),
        ("Independent competitor results", "No same-hardware Neo4j, TigerGraph, Neptune, JanusGraph, FalkorDB, Kuzu, or zu run is cited.", "Use the cross-engine protocol in specification 06."),
        ("PB deployment", "No public configuration demonstrates a PB live graph with query SLOs.", "Build capacity model, then validate by a scale ladder."),
        ("Trillion-edge deployment", "The largest cited public run is 37.2B edges.", "Do not extrapolate linearly through supernode, index, and operational limits."),
        ("Graph license quote", "The public page explains general data-volume pricing but not a reproducible Graph quote.", "Obtain written quote including SC/MRT, DR, non-prod, and support."),
        ("Graph on Community Edition", "3.2.2 removed a feature check, but the supported production combination and limitations remain ambiguous.", "Run basic compatibility and obtain a support statement."),
        ("Unique-data accounting", "It is unclear which logical/physical graph bytes enter commercial billing.", "Reconcile contract definitions with record/index/replica expansion."),
        ("Exact record expansion 3.2", "Source documents explain layout but do not replace measured physical bytes for each workload.", "Inspect namespace/storage statistics and backups on the pinned image."),
        ("Global cache freshness bound", "Documentation says cache can be stale but gives no maximum staleness.", "Treat it as unbounded until an invalidation/freshness mechanism is proven."),
        ("Read snapshot semantics", "Read-only traversals are eventual, but exact per-hop snapshot guarantees are not stated.", "Run concurrent graph-history tests across multi-hop queries."),
        ("AP partial-write repair", "Source design hides partial adjacency, but operational reclamation guarantees are not fully quantified.", "Inject failures and measure stranded bytes and repair behavior."),
        ("Supernode drop completion", "Best-effort is documented without a universal completion/RTO guarantee.", "Test degree ladder, faults, retries, and post-drop audits."),
        ("Index build isolation", "Release/docs describe asynchronous creation but not an SLO under concurrent production load.", "Measure CPU/RAM/I/O and short-query p99.9 during build/drop."),
        ("Migration tail at scale", "Stateless AGS scaling does not establish query tails while DB partitions rebalance.", "Fault/add/remove nodes under open-loop traffic."),
        ("Restore query-ready RTO", "Backup delegation alone does not establish full graph recovery including indexes and metadata.", "Time complete restore and semantic verification drills."),
        ("Cross-region graph consistency", "XDR branding does not define atomic ordering of related graph records remotely.", "Record remote histories for vertex/edge mutations and conflict."),
        ("OLAP maturity", "Source contains a Spark GraphComputer path, but current product support/performance coverage is not established here.", "Qualify algorithms separately from online Gremlin."),
        ("Long-running query admission", "Scan disable helps, but fleet-wide resource governance and fairness need empirical proof.", "Mix scans/supernodes with latency-critical point traffic."),
        ("Container resource formula", "3.2.1 is container-aware, but actual heap/native/RSS behavior depends on runtime flags and workload.", "Measure cgroup limits, OOM, GC, and direct memory."),
        ("Source documentation drift", "POM/client and MRT compatibility prose conflict inside the public snapshot.", "Prefer executable metadata and open upstream issues for drift."),
    ]
    for i, (name, gap, closure) in enumerate(unknowns, 1):
        d.h(3, f"U{i:02d} — {name}")
        d.lines += [f"- Current gap: {gap}", f"- Closure condition: {closure}", "- Until closed: report `Unknown` or the narrower verified statement; do not interpolate a favorable answer.", ""]
    d.sources({"S01","S02","S05","S09","S10","S12","S14","S25","S26","S28","S33","S34","S43","S46"})
    d.write("00-index.md")


def make_product() -> None:
    d = Markdown("Aerospike Graph product, releases, compatibility, and evidence audit", "What product exists as of the research cut and how confidently each assertion can be made")
    d.h(2, "Version-qualified conclusion")
    d.p("""
    Use `3.2.3` as the released security baseline, not `latest`. Record the image digest. Treat the public `3.x-dev` source as a forward-looking `3.3.0-SNAPSHOT` anatomy reference. It is unusually valuable because it exposes the AGS implementation, but it is not byte-for-byte evidence for the 3.2.3 image: the public repository has no release tag that closes that chain.

    The operational product is a composition: Gremlin driver, load balancer, one or more AGS JVMs, Aerospike Java client, one Aerospike Database namespace, optional Spark bulk/OLAP jobs, metrics/tracing systems, and backup/restore tools. A result that omits any required tier is not a product result.
    """)
    releases = [
        ["3.3.0-rc5", "2026-08-08", "Signed rehearsal/prerelease tag; readiness gate and packaging/CI changes after audited branch head", "Freshest code tag, not stable product baseline"],
        ["3.2.3", "2026-06-30", "Security patch: fourteen CVEs", "Preferred 3.2 baseline"],
        ["3.2.2", "2026-05-14", "Removed graph-service feature requirement; health reports AGS version", "Does not erase DB edition feature boundaries"],
        ["3.2.1", "2026-04-08", "Container-aware memory, rack awareness, repeat/emit and edge-memory changes", "Recheck memory and locality"],
        ["3.2.0", "2026-03-23", "Set cardinality, global cache, runtime config, 10x g.E scan claim", "Major behavior/performance boundary"],
        ["3.1.1", "2025-12-02", "Critical Jersey dependency security update", "Do not baseline 3.1.0"],
        ["3.1.0", "2025-10-23", "TinkerPop transactions, typed vertex indexes, performance changes", "Requires Database 8 for released transaction contract"],
        ["3.0.0", "2025-07-24", "New packed representation, multi-properties, datetime, bulk changes", "Reload/migration and storage boundary"],
        ["2.6.0", "2025-04-18", "Query threading and TLS simplification", "Pre-3 storage format"],
        ["2.5.0", "2025-02-12", "Query isolation distinctions and tracing-era changes", "Historical"],
        ["2.4.2", "2024-12-12", "Read-throughput fix", "Version used by 2025 identity benchmark"],
    ]
    d.h(2, "Release chronology")
    d.table(["Version", "Date", "Material change", "Audit treatment"], releases)
    d.h(2, "Latest-publication freshness sweep")
    d.p("""
    The freshness sweep did not stop at release notes. The material Graph-specific vendor posts found were the 2.5 strong-consistency launch on 2025-04-10, the 3.0 storage-and-load launch on 2025-07-29, and the Graph AI/MCP article on 2025-09-30. The September article is the newest Graph-specific blog found, but it demonstrates an MCP server translating natural-language requests into Gremlin and exposing metadata/configuration resources; it does not announce a newer persistence model, query engine, consistency contract, or scale result. It therefore belongs in the integration/tooling evidence lane and cannot supersede 2026 release documentation.

    The 2.5 post is materially useful because it states the boundary marketing summaries often omit: Database 8-backed transactions apply to mutations in an SC namespace, while read-only queries remain eventually consistent. The 3.0 post contributes vendor claims about bulk-load time and footprint, not an independently reproducible cross-engine benchmark. Later 3.2 release notes and the pinned 3.3 prerelease source remain the stronger authorities for current behavior.

    A second freshness check found documentation drift in backup guidance. The Graph backup page delegates to Database tools but currently links directly to `asbackup`, whose Database page now labels it legacy. The current Database overview presents Aerospike Backup Service and `absctl` alongside the legacy tools. This audit therefore requires an explicit Graph-qualified restore drill with the chosen modern tool; it does not silently assume that a generic Database backup preserves every Graph index, metadata object, consistency boundary, and query-ready state.
    """)
    d.table(
        ["Publication", "Date", "What it actually adds", "What it does not prove"],
        [
            ["Graph 2.5 strong consistency", "2025-04-10", "Mutation transaction positioning, DB 8 dependency, eventual-read caveat", "Snapshot-consistent read traversals or AP-mode transactions"],
            ["Graph 3.0 launch", "2025-07-29", "Vendor load-time and footprint claims for the new representation", "Competitor-normalized 10x or PB/trillion scale"],
            ["Graph AI/MCP", "2025-09-30", "Natural-language/demo integration and exposed operational resources", "A new AGS engine release or latency result"],
            ["Graph 3.2.3 release docs", "2026-06-30", "Current stable security baseline", "Source-to-image equivalence for public 3.x-dev"],
            ["AGS v3.3.0-rc5 tag", "2026-08-08", "Freshest public prerelease packaging/readiness state", "Stable production status"],
        ],
    )
    d.h(2, "Product and licensing boundary")
    d.bullets([
        "AGS source is Apache-2.0 in the pinned public repository.",
        "Aerospike Database Community Edition core is AGPLv3; Enterprise/Standard/Federal editions add closed/commercial capabilities.",
        "The current edition page caps Community Edition at 8 nodes and 2.5 TB cluster data.",
        "The same page places strong consistency, multi-record transactions, rack awareness, TLS/ACLs, XDR, and operational features behind Enterprise/additional licensing boundaries.",
        "Production Enterprise licensing is described as primarily unique-data-volume based, not per operation, server, or core; actual Graph entitlement and quote must be obtained in writing.",
        "The 3.2.2 removal of a graph-service feature startup check is not evidence that all underlying features became Community Edition features.",
        "A one-node evaluation key is not a production license and cannot establish distributed fixed cost.",
    ])
    d.h(2, "Source-to-release gap")
    d.p("""
    The audited AGS source commit was dated 2026-08-07, identifies itself as `3.3.0-SNAPSHOT`, and pins TinkerPop 3.7.3, Java source target 11, Spark 3.5.8, and Aerospike Java client 10.3.0. Its compatibility prose says client 9.3.x, demonstrating documentation drift inside the repository. The POM is the build authority for the commit.

    The repository has signed `v3.3.0-rc1` through `v3.3.0-rc5` tags but no observed `3.2.x` source tag or GitHub release object that closes the stable-image provenance chain. The diff from the audited default-branch commit to rc5 changes packaging, container, Helm, smoke-test, and CI files—not Java/Kotlin engine source—so the implementation anatomy remains current while rc5 is still classified as prerelease. The audit cannot assert that the 3.2.3 Docker image has identical source. A defensible benchmark must archive the container SBOM, Maven artifact metadata, image digest, runtime info endpoint, and config export.
    """)
    items = [
        ("image digest pinning", "Prove all nodes run the same immutable AGS build."),
        ("3.2.3 health version", "Verify health output reflects the intended patch."),
        ("container SBOM", "Identify dependency and CVE closure, including transitive libraries."),
        ("TinkerPop 3.7.3 driver", "Prove client/server bytecode compatibility."),
        ("TinkerPop 3.8 rejection", "Record the exact incompatible-client failure."),
        ("Java 17 container runtime", "Measure actual runtime and GC defaults."),
        ("Database 8.1.2 compatibility", "Use the latest supported DB patch as of the cut."),
        ("Database 7.1 benchmark replay", "Separate historical-paper reproduction from current-product qualification."),
        ("Community Edition startup", "Discover whether basic AGS CRUD starts after the 3.2.2 feature-check removal."),
        ("Community Edition scale cap", "Verify enforced and contractual limits rather than extrapolating."),
        ("Enterprise feature key", "Inventory exact licensed capabilities needed by the selected mode."),
        ("SC add-on", "Confirm contract, entitlement, and runtime namespace mode."),
        ("MRT add-on", "Confirm transaction availability and server stats."),
        ("rack-awareness add-on", "Confirm client preference and server rack topology."),
        ("XDR add-on", "Keep asynchronous cross-cluster replication out of local-ACID claims."),
        ("production price quote", "Convert contact pricing into a reproducible monthly cost model."),
        ("unique-data definition", "Determine whether graph expansion, indexes, replicas, backup, and DR are licensed bytes."),
        ("non-production terms", "Separate free development from production cost."),
        ("Graph entitlement", "Determine whether AGS has a separate commercial/support line item."),
        ("support SLA", "Charge required support tier and response commitments."),
        ("3.0 reload boundary", "Prove upgrade/migration behavior for 2.x data."),
        ("3.1 transaction boundary", "Prove explicit transaction behavior only on supported Database versions."),
        ("3.2 global cache boundary", "Treat cache mode as semantic configuration."),
        ("3.2.0 scan improvement", "Reproduce version-over-version g.E claim on fixed hardware."),
        ("3.2.1 memory change", "Measure RSS/heap before and after edge materialization."),
        ("3.2.3 CVE closure", "Scan the exact baseline image."),
        ("3.3.0-rc5", "Track prerelease packaging/readiness changes without promoting it to stable evidence."),
        ("latest tag drift", "Detect mutable-tag changes during a benchmark campaign."),
        ("multi-tenant graph names", "Prove tenant routing and config isolation."),
        ("slim image", "Measure attack surface and missing bulk-loader behavior."),
        ("standard image", "Charge bundled tooling and image footprint."),
        ("Docker deployment", "Qualify local reproducibility, not distributed production readiness."),
        ("Kubernetes chart", "Pin chart/app/image versions independently."),
        ("Aerospike Cloud", "Keep managed service results separate from same-hardware results."),
        ("aerolab examples", "Treat provisioning scripts as examples, not support contracts."),
        ("source license inventory", "Verify AGS plus dependency redistribution obligations."),
        ("server dual license files", "Distinguish community source from closed Enterprise additions."),
        ("client Apache license", "Establish driver integration license posture."),
        ("Spark dependency", "Pin Spark runtime and cloud distribution."),
        ("S3 SDK dependency", "Qualify bulk-load credential and endpoint behavior."),
        ("security advisory feed", "Make patch monitoring part of baseline lifecycle."),
        ("release note completeness", "Cross-check behavior changes against issues/tests and runtime diff."),
        ("configuration migration", "Diff defaults across 3.0, 3.1, and 3.2."),
        ("data-model metadata", "Capture on-disk major/minor compatibility before upgrade."),
        ("rollback", "Prove whether old AGS can reopen data after a new version starts."),
        ("backup compatibility", "Restore into exact, newer, and unsupported older versions."),
    ]
    d.cases("Product qualification cases", expand_cases("product", items, "Fresh namespace plus a production-shaped three-node database and two AGS nodes unless the case specifies a historical artifact.", "image digest, runtime version, feature-key report, namespace config, logs, client coordinates, license cost inputs", "S01–S08,S28–S33,S45–S50"))
    d.sources({"S01","S02","S03","S04","S05","S06","S07","S08","S16","S22","S26","S28","S29","S32","S33","S45","S46","S47","S48","S49","S50"})
    d.write("01-product-releases-and-evidence.md")


def make_storage() -> None:
    d = Markdown("Aerospike Graph source-code and storage-model audit", "Pinned AGS, Database, and Java-client source with record-level graph representation")
    d.h(2, "Source inventory")
    d.p("""
    The pinned AGS snapshot contains 573 Java/Kotlin files and about 106,699 source lines by the audit's file count, split across graph API, Gremlin service, Spark bulk loader, and Spark OLAP modules. The main Gremlin module is the online engine. The source is far more informative than the previous architecture summary: it names sets, bins, ID allocators, record codecs, traversal strategies, query pagers, caches, transaction wrappers, admin services, and 431 observed test files.

    Internal packages use the codename `firefly`. `FireflyServer` wires Gremlin Server and HTTP administration. `FireflyGraph` implements TinkerPop. `AerospikeConnection` and `AerospikeOperations` form the storage boundary. The database source separately exposes partition, storage, transaction, query, secondary-index, and primary-index subsystems, but Enterprise-only behavior is not fully established by the community tree.
    """)
    d.h(2, "Packed model reconstruction")
    d.bullets([
        "One normal vertex is one record in the VERTICES set.",
        "Vertex bins include an interned label ID, preserved user key/type, vertex-property maps, type hints, meta-properties, inbound/outbound adjacency maps, supernode marker, and optional TTL.",
        "Labels and property-key strings are interned into small Long IDs stored in schema records, reducing repeated wire/storage bytes.",
        "Logical edges are grouped by `storageId = floorDiv(packingId, phatEdgeSize)` into records in EDGES.",
        "The source default `phatEdgeSize` is 10; validation accepts 1 through 100; it is immutable after data exists because IDs encode the mapping.",
        "A normal packed edge stores label ID, both endpoint IDs, properties, and type hints inside a map keyed by full edge ID.",
        "Normal vertex adjacency caches composite edge ID and opposing vertex identity, allowing some edge-skipping rewrites.",
        "Supernode adjacency is represented in special edge-record maps and found through mandatory secondary indexes.",
        "The transition to supernode is one-way for the vertex lifetime; existing inline adjacency is ignored after the marker flips.",
        "A larger pack amortizes record count and bulk reads but increases write collision/serialization risk on a shared record.",
        "Vertex record count still scales with vertex count; packing attacks edge-record primary-index overhead, not vertex primary-index overhead.",
    ])
    d.h(2, "Sets observed in the source design")
    sets = [
        ["VERTICES", "One record per vertex", "OLTP authority"], ["EDGES", "Packed logical edges", "OLTP authority"],
        ["IN_VP / OUT_VP", "Spilled vertex-property/meta-property structures", "Overflow path"], ["SCHEMA", "Interning maps/counters", "Permanent metadata"],
        ["ID_MANAGER", "ID counters and recycle buffers", "Allocation hotspot/metadata"], ["METADATA", "Data-model name and version", "Startup compatibility"],
        ["SUMMARY", "Approximate cardinality and optimizer metadata", "Asynchronous derived state"], ["INDEX_METADATA", "User index descriptors", "Planner metadata"],
        ["USAGE_STATS_SET", "Opt-in usage statistics", "Operational metadata"], ["OLAP_TEMP", "GraphComputer temporary state", "Analytical scratch"],
        ["OLAP_ALGORITHM_TEMP", "Algorithm scratch", "Analytical scratch"], ["OLAP_JOBS", "Job state", "Analytical metadata"],
        ["BL_METADATA", "Bulk-load metadata", "Load scratch"], ["BL_DUPE_VID", "Duplicate vertex IDs", "Load error state"],
        ["BL_BAD_EDGE", "Invalid edge records", "Load error state"], ["BL_BAD_ENTRY", "Invalid input rows", "Load error state"],
        ["BL_RECOVERY_*", "Stage recovery state", "Load restart"], ["ID_CACHE", "User-supplied ID cache", "Optional/derived lookup state"],
    ]
    d.table(["Set", "Contents", "Role"], sets)
    d.h(2, "High-value source symbols inspected")
    symbols = [
        ["runtime.FireflyServer", "Bootstraps Gremlin Server and installs the transaction/session processor"],
        ["structure.FireflyGraph", "TinkerPop Graph implementation, strategies, transaction feature, and data-model version"],
        ["io.aerospike.AerospikeConnection", "Client creation, read/batch/query/pagination operations, policies, and shared executors"],
        ["io.aerospike.AerospikeOperations", "Vertex/edge CRUD, edge-cache updates, supernode writes, MRT and non-MRT sequencing"],
        ["io.aerospike.schema.SchemaManager", "Atomic label/property-key interning and reserved edge-property IDs"],
        ["io.aerospike.DataModelVersioning", "Startup comparison of on-disk and runtime data-model versions"],
        ["structure.id.FireflyPhatEdgeId", "8/16-byte logical ID and floorDiv-derived packed-record storage ID"],
        ["structure.id.FireflyIdFactory", "Vertex, edge, composite, and recycled ID construction"],
        ["structure.id.MrtEdgePackingIdManager", "Packing-ID allocation behavior when multi-record transactions are active"],
        ["io.aerospike.ReadThroughRecordCache", "Caffeine weighted record cache, stats, invalidation, and memory estimate"],
        ["io.aerospike.CacheManager", "Transactional versus global cache ownership and lifecycle"],
        ["structure.transaction.FireflyTransaction", "Thread-local TinkerPop scope mapped to Aerospike Txn commit/rollback"],
        ["structure.transaction.FireflyTransactionOpProcessor", "Session request routing and execution-timeout handling"],
        ["io.aerospike.query.GraphQuery", "Scan/secondary-index query construction and page-stream orchestration"],
        ["io.aerospike.query.paged.PageFetcher", "Bounded page queue, background read loop, completion and cancellation"],
        ["io.aerospike.query.paged.PartitionedSindexPageFetcher", "Partition-filtered secondary-index pagination"],
        ["io.aerospike.indexes.FireflyIndexMetadata", "Runtime index inventory/cardinality and expression-index matching"],
        ["io.aerospike.EdgeQueryHelper", "Supernode/packed-edge filter-expression construction"],
        ["io.aerospike.FireflyBatchReadHelper", "Has-container ordering and multi-key read preparation"],
        ["runtime.tasks.FireflyGraphSummaryUpdater", "Asynchronous summary/cardinality updates including transaction staging"],
        ["structure.util.FireflyTtlHandler", "Scheduled TTL purge behavior"],
        ["util.config.ConfigurationHelper", "Authoritative key names, defaults, immutable settings, and validators"],
        ["bulkloader.SparkBulkLoaderMain", "Out-of-process distributed initial/incremental loader entry point"],
        ["olap.DistributedGraphComputerMain", "Out-of-process Spark GraphComputer entry point"],
    ]
    d.table(["Symbol", "Why it matters"], symbols)
    d.h(2, "Local source validation performed")
    d.bullets([
        f"Cloned the public repositories and recorded AGS `{AGS_COMMIT}`, examples `{GRAPH_COMMIT}`, server `{SERVER_COMMIT}`, and Java client `{CLIENT_COMMIT}`.",
        "Counted 573 Java/Kotlin files and approximately 106,699 lines in the AGS snapshot; counts are inventory observations, not quality metrics.",
        "Observed 431 test files across the source snapshot, including TinkerPop structure/process, transaction, concurrency, cache, index, supernode, bulk-loader recovery, and benchmark-oriented tests.",
        "Built the AGS Gremlin module and dependencies with Maven while skipping tests; the build produced `aerospike-graph-gremlin-3.3.0-SNAPSHOT.jar`.",
        "The successful source build establishes that the inspected default-branch snapshot compiles in this environment; it does not establish 3.2.3 binary identity, server compatibility, performance, or correctness under a live Aerospike cluster.",
        "A targeted Maven test selection was attempted without provisioning the expected three-node Aerospike test cluster at 172.17.0.1:3000/3010/3020. Cluster-backed `TestDataModelVersioning` retried connection, errored in setup, then also exposed cleanup null-pointer errors because setup left the database handle null. The run was terminated and is not reported as a source-test pass or product failure; it establishes that these selected tests are integration-dependent and that failed setup currently produces noisy secondary errors.",
        f"Fetched signed `v3.3.0-rc5` at `{AGS_RC5_COMMIT}` and diffed it against the inspected branch head. The delta changes CI, container, Helm, packaging, and smoke scripts but no Java/Kotlin engine source.",
    ])
    d.h(2, "Important source/code caveats")
    d.bullets([
        "Source design prose and source code can drift; derive final record bytes with a qualified backup export or direct record inspection on the pinned image.",
        "The public source branch is ahead of shipped 3.2.3 and has no matching tag.",
        "A logical edge add touches the packed edge record and both endpoint vertex records when adjacency is inline.",
        "Without MRT, the source writes endpoint adjacency first and edge record last; read-side existence checks hide partial adjacency at the cost of stranded bytes.",
        "With MRT, edge record and endpoint changes share an Aerospike Txn; record packing can cause transaction collisions and ID retarget/retry.",
        "Global edge/property scans remain qualitatively different from ID-rooted traversals.",
        "No global edge property or edge label index appears in the audited design; supernode adjacency indexes are specialized, not general edge indexes.",
        "Maximum Aerospike record size constrains inline adjacency and packed-record risk; raising it changes latency, memory, and write amplification.",
    ])
    items = [
        ("vertex key Long", "Verify stable user ID round trip and digest derivation."),
        ("vertex key Integer", "Verify type preservation rather than numeric coercion."),
        ("vertex key String", "Measure digest/key memory and collision handling."),
        ("generated vertex ID", "Measure buffered decrementing allocation and crash gaps."),
        ("schema first label", "Observe atomic intern assignment under concurrency."),
        ("schema repeated label", "Confirm cache hit and no counter increment."),
        ("schema concurrent new key", "Prove a single permanent interned ID."),
        ("schema restart", "Rebuild in-memory maps from records without remapping."),
        ("single vertex property", "Inspect VP_DATA and type-hint encoding."),
        ("list cardinality", "Inspect multiple property IDs and meta-property behavior."),
        ("set cardinality", "Qualify 3.2 semantics for equality and type mixing."),
        ("meta-property spill", "Trigger IN_VP/OUT_VP and measure extra I/O."),
        ("datetime property", "Prove source/storage/client round trip and indexed range."),
        ("double property", "Confirm no index path and exact comparison behavior."),
        ("scaled long", "Compare indexed range path with Double scan path."),
        ("normal edge add", "Count edge-record and both vertex-record operations."),
        ("self-loop add", "Detect duplicate endpoint operations and path semantics."),
        ("parallel edges", "Preserve distinct edge IDs and properties."),
        ("edge property update", "Measure packed-record contention and byte rewrite."),
        ("edge delete", "Verify record-first visibility and adjacency cleanup."),
        ("pack size 1", "Establish record-count and contention baseline."),
        ("pack size 10", "Qualify source default under mixed reads/writes."),
        ("pack size 100", "Expose large-record reads and writer collision tradeoff."),
        ("pack immutability", "Reject runtime pack-size change on existing data."),
        ("pack partial occupancy", "Measure waste under random deletes and recycled IDs."),
        ("packing collision", "Force concurrent writes to one packed record."),
        ("recycled edge ID", "Verify 16-byte identity and no alias with deleted edge."),
        ("allocator crash gap", "Prove gaps do not become identity reuse."),
        ("ordinary adjacency degree 1", "Establish minimum hop I/O."),
        ("ordinary adjacency degree 100", "Measure batch grouping and response materialization."),
        ("ordinary adjacency near threshold", "Expose record-size and update tail latency."),
        ("automatic supernode transition", "Verify irreversible ECACHE_OFF change."),
        ("manual supernode flag", "Avoid populating adjacency that will be abandoned."),
        ("supernode inbound", "Trace E_IN secondary-index query and filters."),
        ("supernode outbound", "Trace E_OUT secondary-index query and filters."),
        ("supernode both", "Measure two index streams, deduplication, and self-loops."),
        ("supernode property pushdown", "Count records/edges eliminated server-side."),
        ("unfiltered supernode", "Capture worst-case transfer and memory."),
        ("vertex max-record-size 128KiB", "Validate documented ~800-edge transition estimate."),
        ("vertex max-record-size 1MiB", "Validate documented ~6,500-edge transition estimate."),
        ("vertex max-record-size 8MiB memory", "Validate documented ~50,000-edge transition estimate."),
        ("record-size exceed", "Verify error mapping and absence of partial visible edge."),
        ("vertex label index", "Inspect numeric interned label index path."),
        ("vertex string property index", "Verify full-string equality only."),
        ("vertex numeric property index", "Verify range bounds and type matching."),
        ("compound expression index", "Qualify exact predicate coverage and fallback."),
        ("edge label global lookup", "Prove scan fallback and disable-scan rejection."),
        ("edge property global lookup", "Prove lack of general secondary index."),
        ("TTL vertex", "Trace index, sweeper, incident-edge cleanup, and lag."),
        ("TTL edge", "Trace per-edge TTL map and packed-record cleanup."),
        ("data-model major mismatch", "Prove startup refuses incompatible on-disk major."),
        ("data-model newer minor", "Prove older service refuses newer disk minor."),
        ("data-model rolling minor", "Prove newer service reads older disk minor."),
        ("backup record reconstruction", "Validate all sets, bins, indexes, and metadata after restore."),
        ("database partition migration", "Validate record availability and traversal completeness during rebalance."),
        ("primary-index RAM", "Measure bytes per vertex and packed edge record at scale."),
        ("secondary-index RAM", "Measure per-entry cost for labels, properties, TTL, and supernodes."),
        ("defrag amplification", "Measure device writes after churn in packed records."),
        ("compression", "Measure CPU/latency/storage tradeoff where licensed/supported."),
        ("namespace storage engine", "Compare HMA, memory, and all-flash without conflating modes."),
    ]
    d.cases("Record-model qualification cases", expand_cases("storage", items, "Pin AGS and Database artifacts; expose a dedicated namespace; archive raw records and server stats before and after each operation.", "Aerospike command count, batch subcommands, bytes read/written, record generation/size, PI/SI RAM, device IOPS, defrag, AGS allocations", "S11,S12,S15,S33–S44"))
    d.sources({"S11","S12","S15","S31","S33","S34","S35","S36","S37","S38","S39","S40","S41","S43","S44"})
    d.write("02-source-code-and-storage-model.md")


def make_query() -> None:
    d = Markdown("Aerospike Graph Gremlin compiler and query-execution audit", "TinkerPop surface, traversal rewrites, storage I/O, batching, pagination, parallelism, caching, and observability")
    d.h(2, "Execution conclusion")
    d.p("""
    AGS is not a declarative cost-based graph optimizer in the relational sense. TinkerPop builds a traversal, and AGS applies provider strategies that recognize specific step shapes and replace or fold them into Aerospike-aware steps. Performance therefore depends on syntactic traversal shape, IDs versus scans, placement of has/limit/sample/count, property projection, ordinary versus supernode adjacency, supported predicate types, and whether a rewrite fires.

    The source exposes strategies for graph-step folding, batch vertex/edge reads, edge-to-vertex and otherV batching, adjacent-ID shortcuts, cached reads, graph/local counts, filter pushdown, hasId, drop, merge, elementMap, query tracing, scan profiling, and verification. The benchmark must capture the optimized traversal/profile and backend operation counts so a fast result cannot be attributed vaguely to "Gremlin optimization."
    """)
    d.h(2, "Read-path classes and decisions")
    d.bullets([
        "Gremlin bytecode arrives through TinkerPop Gremlin Server over WebSocket.",
        "Provider strategies rewrite eligible traversals before iterator execution.",
        "ID-rooted vertex lookup becomes a direct Aerospike record read.",
        "Multiple known IDs can become an Aerospike batch read split by cluster node.",
        "Vertex has()/hasLabel() can use a secondary index when a compatible index exists.",
        "Remaining predicates may compile into Aerospike filter expressions for server-side rejection.",
        "Ordinary vertex adjacency can skip individual edge materialization for out()/in() shapes that only need adjacent vertices.",
        "Supernode adjacency starts with specialized secondary-index queries against edge records.",
        "Global scans use paged query machinery and are qualitatively more expensive than point/bounded paths.",
        "Per-query parallelization draws from a shared executor and is disallowed in transaction traversals.",
        "The default record cache is transaction/request local; the global mode is shared within one graph instance and may be stale.",
        "Query results themselves are not cached by the AGS cache feature.",
    ])
    d.h(2, "Key source defaults observed at the pinned commit")
    defaults = [
        ["scan enabled", "true", "Production should normally disable accidental scans and opt in explicitly"],
        ["read socket / total timeout", "150 ms / 450 ms", "Retry multiplication and tail clipping must be reported"],
        ["write socket / total timeout", "500 ms / 2500 ms", "Not an SLA by itself"],
        ["max retries", "2", "Count attempts and both successful/failed user requests"],
        ["batch flat size", "0", "Per-node control applies"],
        ["batch size per node", "20", "Total batch grows with DB node count"],
        ["batch threshold per node", "1", "Affects single versus batch path"],
        ["pagination flat page", "0", "Per-node page applies"],
        ["pagination page per node", "200", "Total in-flight data grows with cluster"],
        ["pagination queue", "10", "Backpressure/memory dimension"],
        ["cache mode", "TRANSACTIONAL", "Reset per traversal"],
        ["cache weight", "1,000,000", "Weight is not raw bytes"],
        ["global cache documented default", "20,000,000", "Applied when switching modes without explicit weight"],
        ["event loops", "2", "Separate from Gremlin workers and parallel read executor"],
        ["commands per event loop", "50", "Client async capacity input"],
        ["query/scan socket timeout", "30,000 ms", "Global operations have different tail envelope"],
    ]
    d.table(["Control", "Source default", "Audit consequence"], defaults)
    d.h(2, "Traversal strategies present in the source")
    strategies = [
        ["FireflyGraphStepStrategy", "Folds root GraphStep plus eligible has/label constraints into provider access"],
        ["FireflyBatchVertexReadStrategy", "Replaces per-vertex access with multi-key vertex reads"],
        ["FireflyBatchEdgeReadStrategy", "Batches packed-edge record access"],
        ["FireflyBatchEdgeReadLocalStrategy", "Local-child variant of batched edge access"],
        ["FireflyEdgeToVertexBatchReadStrategy", "Batches endpoint materialization following edges"],
        ["FireflyOtherVBatchReadStrategy", "Batches otherV endpoint lookup"],
        ["FireflyAdjacentVertexIdStrategy", "Uses cached adjacent identity where edge materialization is unnecessary"],
        ["FireflyHasIdVertexFilterStrategy", "Avoids general reads for eligible hasId filters"],
        ["FireflyBatchTraversalFilterStrategy", "Combines/filter-batches eligible child traversals"],
        ["FireflyGraphFilterStrategy", "Pushes compatible graph filters toward storage"],
        ["FireflyReadThroughCacheStrategy", "Routes eligible record reads through the configured cache"],
        ["FireflyCountGlobalLocalStrategy", "Recognizes count shapes with provider-local shortcuts"],
        ["FireflyGraphCountStrategy", "Optimizes graph-wide count forms where supported"],
        ["FireflyVertexEdgeLocalCountStrategy", "Counts adjacency locally without full edge materialization"],
        ["FireflyElementMapStrategy", "Projects element maps through a provider step"],
        ["FireflyGraphDropStrategy", "Replaces general drop with provider mutation logic"],
        ["FireflyMergeStepStrategy", "Installs provider mergeV/mergeE implementations"],
        ["FireflyAuthenticationStrategy", "Carries authenticated graph permissions into traversal processing"],
        ["FireflyTraversalOptionsStrategy", "Reads provider options such as parallelize and scan control"],
        ["FireflyQueryTracingStrategy", "Instruments eligible execution for distributed tracing"],
        ["FireflyScanProfileStrategy", "Adds scan/profile observability"],
        ["FireflyComputerVerificationStrategy", "Rejects invalid GraphComputer traversal use"],
    ]
    d.table(["Strategy", "Audited role"], strategies)
    d.h(2, "Semantic hazards")
    d.bullets([
        "A traversal that is logically equivalent in Gremlin may miss a provider rewrite because its step arrangement differs.",
        "String indexes support full-string equality, not substring search.",
        "Double values cannot use the documented vertex property indexes; scaled Long is the recommended indexed substitute.",
        "Global edge label/property lookup scans because general edge indexes are absent.",
        "High-cardinality indexes can speed roots; low-cardinality indexes may generate large query streams and consume Aerospike query threads.",
        "MergeE on supernodes can trigger secondary-index queries, and documented query-thread limits can reject excess concurrency.",
        "Parallelize may improve a single high-fanout I/O-bound query while harming aggregate throughput or tail latency.",
        "Global cache is an explicit stale-read tradeoff and is per AGS instance, so a load-balanced fleet has independent cache contents.",
        "Warm-cache comparisons are invalid unless every competitor receives equivalent preconditioning and cache memory is charged.",
    ])
    items = [
        ("V(id)", "Prove one point-root path and stable ID semantics."),
        ("V(id1,id2,...)", "Observe batch partitioning by database node."),
        ("V().hasLabel indexed", "Verify secondary index rather than scan."),
        ("V().hasLabel unindexed", "Expose scan and scan-disable behavior."),
        ("V().has string equality", "Use compatible string index."),
        ("V().has numeric equality", "Use compatible numeric index."),
        ("V().has numeric range", "Inspect range filter and remaining predicates."),
        ("V().has Double", "Expose unindexed fallback."),
        ("V().has substring", "Expose full scan and filter cost."),
        ("compound equality", "Observe expression-index selection."),
        ("two eligible indexes", "Verify cardinality-based most-selective root."),
        ("stale cardinality metadata", "Measure plan lag after data distribution changes."),
        ("outE label", "Count vertex and packed-edge reads."),
        ("out adjacent vertices", "Verify edge-skipping/batch rewrite."),
        ("in adjacent vertices", "Verify reverse ordinary adjacency path."),
        ("both self-loop", "Verify multiplicity and dedup semantics."),
        ("otherV", "Verify batched adjacent endpoint reads."),
        ("edge-to-vertex", "Verify specialized batch step."),
        ("has after VertexStep", "Verify predicate folding/pushdown."),
        ("limit after VertexStep", "Verify early termination and reduced I/O."),
        ("sample after VertexStep", "Verify sample semantics without reading all candidates."),
        ("local edge count", "Verify adjacency-local count without edge fetch."),
        ("global vertex count", "Verify count optimization and exactness during mutation."),
        ("global edge count", "Verify summary/scan path and exactness."),
        ("properties projection", "Fetch only required map entries."),
        ("valueMap", "Measure requested versus materialized properties."),
        ("elementMap", "Inspect provider-specific projection rewrite."),
        ("path", "Charge path object retention and edge/vertex materialization."),
        ("simplePath", "Charge visited-set memory and compare semantics."),
        ("dedup", "Measure hash state and spill/limit behavior."),
        ("order", "Expose full materialization and memory."),
        ("groupCount", "Classify as OLTP traversal or move to OLAP path."),
        ("repeat depth 2", "Measure batched frontier behavior."),
        ("repeat depth 4", "Expose multiplicative frontier and request limits."),
        ("repeat emit", "Verify 3.2.1 optimization and output semantics."),
        ("union child traversal", "Verify options and filters propagate into children."),
        ("coalesce", "Check rewrite coverage and short-circuit reads."),
        ("optional", "Check null/missing branch semantics."),
        ("mergeV unique ID", "Avoid index ambiguity and count lock/query operations."),
        ("mergeV nonunique predicate", "Expose multi-match behavior documented by AGS."),
        ("mergeE ordinary", "Measure lock and adjacency operations."),
        ("mergeE supernode", "Expose sindex query-thread consumption."),
        ("drop edge", "Verify specialized drop and cleanup."),
        ("drop ordinary vertex", "Count incident-edge work and atomicity mode."),
        ("drop supernode", "Record best-effort semantics and completion lag."),
        ("scan disabled global", "Reject accidental V()/E() without eligible index."),
        ("per-query scan opt-in", "Prove explicit escape hatch is auditable."),
        ("page size per node", "Measure memory/latency as DB cluster grows."),
        ("flat page size", "Bound cluster-wide response buffering."),
        ("batch size per node", "Measure RPC count and result latency."),
        ("flat batch size", "Hold total batch constant across node count."),
        ("parallelize 1", "Establish default-equivalent baseline."),
        ("parallelize 2", "Measure single-query gain and fleet interference."),
        ("parallelize CPU count", "Expose executor saturation and tail risk."),
        ("parallelize in transaction", "Verify explicit rejection."),
        ("transactional cache cold", "Establish per-request backend I/O."),
        ("transactional cache repeated vertex", "Observe within-traversal hit only."),
        ("global cache warm", "Measure best-case repeated hot-set reads."),
        ("global cache stale local write", "Demonstrate documented correctness risk."),
        ("global cache stale other AGS", "Demonstrate fleet incoherence."),
        ("global cache reset", "Measure invalidation latency and traffic surge."),
        ("query trace threshold", "Correlate spans with backend calls without full-sampling overhead."),
        ("query profile", "Capture rewritten step plan and per-step timing."),
        ("timeout cancellation", "Verify work stops in AGS and Database after client timeout."),
        ("client disconnect", "Verify iterator/query resources are reclaimed."),
        ("backpressure slow client", "Bound result buffering and heap."),
        ("mixed short and scan", "Verify scan admission does not destroy short-query tail."),
        ("mixed short and supernode", "Verify heavy traversal isolation."),
        ("32 AGS scale", "Locate storage saturation and load-balancer skew."),
    ]
    d.cases("Query qualification cases", expand_cases("query", items, "Use identical graph state and semantic result oracle; capture TinkerPop profile, Zipkin spans, AGS metrics, and Aerospike command histograms.", "client HDR latency, AGS queue/worker/heap/GC, cache hits, record reads, batch keys, sindex records, bytes, result cardinality, cancellations", "S09,S11–S19,S27,S33,S36–S41,S45"))
    d.sources({"S09","S11","S12","S13","S14","S15","S16","S17","S18","S19","S27","S33","S36","S37","S38","S39","S41","S45"})
    d.write("03-gremlin-query-execution.md")


def make_transactions() -> None:
    d = Markdown("Aerospike Graph transactions, distribution, and failure audit", "Consistency modes, graph mutation atomicity, record transactions, partitions, replicas, and recovery")
    d.h(2, "Corrected consistency matrix")
    d.table(["Operation/mode", "Released contract", "Critical limitation"], [
        ["Read-only traversal", "Eventual consistency", "May observe stale or internally inconsistent graph state during concurrent mutations"],
        ["AP single-record-like mutations", "Only documented enumerated steps are atomic/isolated", "Cluster split can lose writes; graph-wide mutation shapes are not protected"],
        ["AP addE/dropE/dropV", "Eventual/retry-oriented", "Multi-record endpoint/edge updates can be partial internally"],
        ["SC without AGS MRT", "Namespace SC does not automatically make a graph mutation multi-record atomic", "Generation-check path and retries still matter"],
        ["SC + aerospike.graph.mrt.enabled", "Each mutation iteration that touches records can be atomic/isolated", "Requires Enterprise 8.0+ per released docs; defaults false"],
        ["SC + aerospike.graph.tx.enabled", "Explicit client transaction scopes", "No scans/indexes; 4096-record maximum; locks persist until close"],
        ["Supernode vertex drop", "Best effort", "Exception to otherwise transactional mutation language"],
        ["Cross-datacenter XDR", "Asynchronous replication", "Not synchronous graph transaction or zero-RPO evidence"],
    ])
    d.h(2, "Source mutation reconstruction")
    d.p("""
    An edge logically spans at least three graph records: the packed edge record plus inbound and outbound vertex records when adjacency is inline. In the transaction path, `AerospikeOperations` creates or reuses an Aerospike `Txn`, writes the packed edge, then updates both vertices, and commits. If the target packed record is transaction-blocked, code recycles/changes the proposed edge ID and retries a different target pack.

    In the no-transaction path, the source updates both endpoint adjacency caches first, then writes the edge record. Reads check that the edge record exists before exposing cached adjacency. That protects visible bidirectional consistency but can strand edge-ID bytes in a vertex if cleanup fails. This is a deliberate availability/storage-leak tradeoff, not ACID.

    TinkerPop transactions are thread-local/session-bound wrappers around the Java client's multi-record transaction object. The code stages edge IDs for recycling according to commit/rollback outcome. Released docs add stricter constraints: resolve indexed IDs outside the transaction, touch at most 4096 records, keep scopes short, and retry contention.
    """)
    d.h(2, "Distribution boundaries")
    d.bullets([
        "AGS compute instances do not own shards and do not coordinate query state with one another.",
        "The Aerospike client discovers the database cluster and maps record digests to partitions/nodes.",
        "Database partitioning and replication provide storage distribution; adding AGS only increases compute/client pressure until the database saturates.",
        "Rack-aware client preference can reduce cross-zone reads but must be paired with database rack configuration and measured fallback behavior.",
        "Rebalance/migration affects where records live; correctness tests must run while topology changes, not only before and after.",
        "SC availability under partition differs from AP availability; latency SLOs need explicit minority/majority behavior.",
        "Cross-region active-active or XDR semantics are separate from local cluster transactions and must not be inferred from `distributed` branding.",
        "Object-storage durability is not involved in acknowledged online writes.",
    ])
    items = [
        ("read after vertex write", "Measure stale-read window on same and different AGS instances."),
        ("read during edge add", "Detect impossible half-edge/path observations."),
        ("read during edge delete", "Detect stale adjacency and edge-record disappearance ordering."),
        ("read during vertex drop", "Detect orphan or partially removed incident edges."),
        ("AP addV", "Validate documented single-element atomic behavior."),
        ("AP property update", "Validate generation and last-write behavior."),
        ("AP addE", "Exercise three-record partial-failure path."),
        ("AP dropE", "Exercise record-first delete and cleanup."),
        ("AP dropV", "Exercise many-record eventual cleanup."),
        ("AP mergeV", "Validate documented atomic case and match ambiguity."),
        ("AP mergeE", "Exercise lock record and partial graph update."),
        ("AP cluster split", "Quantify lost/conflicting graph mutations after heal."),
        ("SC point write", "Establish namespace SC latency baseline."),
        ("SC addE without MRT", "Prove SC alone does not imply graph-level atomicity."),
        ("SC addE with MRT", "Prove all-or-nothing packed-edge and endpoint update."),
        ("SC dropE with MRT", "Prove all-or-nothing removal within record budget."),
        ("SC drop ordinary vertex", "Count records and confirm atomic completion."),
        ("SC drop supernode", "Record documented best-effort exception."),
        ("TinkerPop two vertices/two edges", "Reproduce official all-or-nothing example."),
        ("TinkerPop rollback", "Verify no visible data and correct ID recycling."),
        ("TinkerPop timeout", "Verify server rollback and lock release."),
        ("TinkerPop 4096 records", "Confirm exact accepted boundary."),
        ("TinkerPop 4097 records", "Confirm clean rejection/rollback."),
        ("TinkerPop indexed read", "Verify documented prohibition."),
        ("TinkerPop scan", "Verify documented prohibition."),
        ("TinkerPop ID read", "Verify allowed record addressing."),
        ("TinkerPop parallelize", "Verify explicit incompatibility."),
        ("same-vertex contention", "Measure blocking, aborts, retries, and fairness."),
        ("same-packed-edge contention", "Expose false contention from edge packing."),
        ("disjoint writes", "Establish scalable transaction throughput."),
        ("hot supernode writes", "Measure sindex/record contention and retry storms."),
        ("client retry idempotence", "Prevent duplicate addV/addE after ambiguous timeout."),
        ("commit response loss", "Resolve unknown commit outcome safely."),
        ("AGS kill before commit", "Verify transaction timeout/rollback and IDs."),
        ("AGS kill after commit", "Verify acknowledged state and cache effects."),
        ("database leader kill", "Measure transaction outcome and tail latency."),
        ("database replica kill", "Measure RF2 resilience and rebuild load."),
        ("network drop AGS-to-DB", "Verify timeouts, retry budget, and cancellation."),
        ("network delay AGS-to-DB", "Expose retry amplification and tail collapse."),
        ("minority partition AP", "Document availability and later conflict behavior."),
        ("minority partition SC", "Document unavailable partitions and error surface."),
        ("majority partition SC", "Measure commit latency and fencing."),
        ("split heal", "Verify no resurrection/orphan paths after migrations."),
        ("rolling DB restart", "Measure availability and read consistency throughout."),
        ("rolling AGS restart", "Verify stateless handoff and load-balancer draining."),
        ("add DB node", "Measure migration impact on p99.9 and correctness."),
        ("remove DB node", "Measure safe migration and capacity headroom."),
        ("add AGS node", "Verify no warm-state dependence and load distribution."),
        ("remove AGS node", "Verify in-flight query/transaction behavior."),
        ("rack-local replica", "Measure preferred-rack hit rate."),
        ("rack loss", "Measure fallback replica selection and cross-zone cost."),
        ("XDR normal mutation", "Measure remote lag and graph record ordering."),
        ("XDR edge mutation", "Detect remote partial graph visibility."),
        ("XDR conflict", "Document conflict resolution for related records."),
        ("backup during writes", "Prove graph-consistent restore or document quiesce requirement."),
        ("restore transaction metadata", "Ensure no provisional/locked state leaks."),
        ("clock skew", "Exercise TTL, transaction duration, and trace timestamps."),
        ("disk full", "Verify failed graph writes remain invisible and cluster recoverable."),
        ("record too large", "Verify transaction rollback at storage constraint."),
        ("secondary-index unavailable", "Verify startup/query behavior for supernodes."),
        ("summary lag", "Ensure optimizer metadata does not affect correctness."),
        ("global cache plus mutation", "Expose consistency weaker than database mode."),
        ("load balancer retry", "Prevent replay of non-idempotent mutation bytecode."),
        ("session transaction routing", "Ensure every scope operation reaches the correct AGS session."),
        ("transaction abandonment", "Release locks after client disappears."),
        ("transaction starvation", "Measure hot-key fairness and bounded retry."),
    ]
    d.cases("Consistency and failure qualification cases", expand_cases("failure", items, "Use RF2/RF3 production-shaped clusters with fault injection, a linearizability/history recorder, stable client IDs, and independent raw-record inspection.", "operation history, Aerospike transaction/partition/migration stats, retries, record generations, AGS errors, lock duration, stale window, RPO/RTO", "S04,S09,S10,S22,S28,S33,S36,S37,S40,S43,S44"))
    d.sources({"S04","S09","S10","S22","S28","S29","S30","S32","S33","S36","S37","S40","S43","S44"})
    d.write("04-transactions-distribution-and-failure.md")


def make_ops() -> None:
    d = Markdown("Aerospike Graph operations, resources, security, S3, and cost audit", "Production topology, resource accounting, observability, backup, tenancy, security, and economic fit")
    d.h(2, "Operational conclusion")
    d.p("""
    Aerospike Graph can separate query compute from storage capacity, but it is not a serverless object-store graph. The minimum production system has a load-balanced AGS fleet and an Aerospike Database cluster; large initial loads add Spark; tracing adds Zipkin-compatible infrastructure; monitoring adds Prometheus; backups add temporary capacity and object storage. All must appear in the resource and cost denominator.

    The low-resource story is workload-dependent. Edge packing lowers underlying record count. HMA keeps record data on NVMe while retaining primary and secondary index structures in RAM. AGS has JVM heap, off-heap/native buffers, thread stacks, code cache, record/path objects, caches, queues, and client connections. Global cache can trade database I/O for fleet RAM and weaker freshness. A claim based only on AGS heap or only on database RAM is incomplete.
    """)
    d.h(2, "S3 and fixed-cost verdict")
    d.bullets([
        "S3/GCS may hold bulk-loader input; Spark reads it and writes authoritative Aerospike records.",
        "Backups may be stored in object storage through Aerospike tools, but online queries do not demand-page the live graph from S3. Current Database documentation favors ABS/absctl while the Graph page still links the legacy asbackup path, so tool choice and Graph completeness must be qualified explicitly.",
        "An Aerospike namespace uses memory and/or device/file-backed storage modes; S3 is not a namespace storage engine in the cited graph contract.",
        "The published Enterprise pricing model is primarily based on unique production data volume, with add-on feature uplifts; this is variable with graph size even if query count is free.",
        "Infrastructure is provisioned capacity with replica and free-space headroom. It can be budgeted, but `fixed cost` only holds inside a declared capacity/SLO envelope.",
        "Community Edition cannot prove the PB target because the current published cap is 2.5 TB and 8 nodes, and it omits important production features.",
        "A PB graph also multiplies backups, restores, migrations, secondary indexes, and operational time; stored object bytes alone are not the cost." ,
    ])
    d.h(2, "Full resource ledger")
    resources = [
        ["AGS JVM", "heap committed/used, GC, threads, code cache, direct/native, RSS", "per instance and fleet total"],
        ["AGS caches", "transactional/global weights, hit/miss, supernode ID cache", "per graph per instance"],
        ["AGS queues", "Gremlin queue, event loops, page queues, parallel read executor", "peak and steady"],
        ["Database RAM", "primary index, secondary indexes, set indexes, metadata, buffers", "per node and RF total"],
        ["Database storage", "live bytes, write blocks, fragmentation/free headroom, replica bytes", "physical allocated and used"],
        ["Database I/O", "read/write IOPS, bytes, latency, defrag and migration I/O", "per device/node"],
        ["Network", "client↔AGS, AGS↔DB, replication, migration, backup, cross-zone", "bytes and billed topology"],
        ["Spark loader", "driver/executors, shuffle, temp storage, S3 requests/egress", "job-hour total"],
        ["Backup", "snapshot/read load, staging, object bytes, requests, restore cluster", "per retention policy"],
        ["Observability", "metrics cardinality, trace sampling/storage, log volume", "monthly total"],
        ["License/support", "unique data, add-ons, support tier, non-prod/DR terms", "contracted monthly amortization"],
        ["Operations", "on-call, upgrades, rebalances, restore drills, capacity engineering", "human and downtime cost"],
    ]
    d.table(["Tier", "Charge", "Reporting scope"], resources)
    d.h(2, "Security boundary")
    d.bullets([
        "Client-to-AGS and AGS-to-Database TLS are independently configured; verify both with packet capture and certificate rotation.",
        "Graph-level JWT RBAC controls Gremlin/HTTP graph operations; database RBAC protects AGS's backend credentials.",
        "Multi-tenant graph routing and role mapping are logical isolation; resource starvation, cache leakage, index names, logs, and backup separation need testing.",
        "Audit logging requires graph RBAC for user attribution and adds synchronous/asynchronous log cost that must be measured.",
        "The 3.2.3 dependency CVE patch makes image patch discipline an operational control, not optional hygiene.",
        "Secrets in environment variables, property files, Helm values, logs, traces, and process inspection need separate controls.",
    ])
    items = [
        ("one AGS idle floor", "Measure minimum RSS/CPU/threads/connections."),
        ("two AGS HA floor", "Charge redundant stateless compute and load balancer."),
        ("AGS heap cap", "Validate container-aware sizing and OOM behavior."),
        ("AGS direct memory", "Detect native growth not visible in heap."),
        ("AGS thread stacks", "Charge Gremlin, event-loop, cache, pager, and parallel workers."),
        ("transactional cache weight", "Relate weight units to real heap by record shape."),
        ("global cache weight", "Relate hot-set improvement to fleet memory."),
        ("multi-tenant caches", "Measure per-graph multiplication and eviction fairness."),
        ("normal traversal allocation", "Record bytes allocated per result and hop."),
        ("supernode traversal allocation", "Bound edge-ID/result materialization."),
        ("slow client buffering", "Bound heap and queue occupancy."),
        ("Prometheus scrape", "Measure endpoint cost and metric cardinality."),
        ("100% Zipkin sampling", "Quantify tracing perturbation."),
        ("threshold Zipkin sampling", "Preserve slow-query evidence at lower overhead."),
        ("log volume", "Charge supernode warnings, audit, errors, and access logs."),
        ("Database three-node RF2 floor", "Measure smallest production-shaped storage footprint."),
        ("Database RF3", "Measure latency/capacity/recovery tradeoff."),
        ("primary index RAM per vertex", "Derive PB-scale memory floor."),
        ("primary index RAM per edge pack", "Quantify benefit of pack size."),
        ("vertex label SI RAM", "Charge label index."),
        ("property SI RAM", "Charge each indexed property and type."),
        ("supernode SI RAM", "Charge mandatory adjacency index entries."),
        ("TTL SI RAM", "Charge TTL enablement."),
        ("storage 50% free", "Match vendor benchmark headroom and cost."),
        ("storage minimum safe free", "Measure defrag/migration risk envelope."),
        ("steady-state churn", "Capture write amplification and fragmentation."),
        ("migration headroom", "Prove node loss/addition completes without high-water failure."),
        ("local NVMe", "Qualify HMA latency and instance-loss recovery."),
        ("network block storage", "Measure latency tails and provisioned IOPS cost."),
        ("in-memory namespace", "Separate durability and restart behavior."),
        ("all-flash primary index", "Qualify edition and latency/resource tradeoff."),
        ("S3 bulk input", "Charge requests, throughput, Spark, and egress."),
        ("GCS bulk input", "Charge equivalent cloud path."),
        ("standalone bulk loader", "Qualify small-load JVM resource floor."),
        ("distributed Spark loader", "Measure driver/executor/shuffle peak and cost."),
        ("bulk resume", "Verify idempotence and extra staging bytes."),
        ("bulk bad rows", "Bound error-record growth and operator workflow."),
        ("bulk supernode sampling", "Measure driver memory versus classification errors."),
        ("bulk index build", "Separate write, index, migration, and ready time."),
        ("absctl or ABS full graph", "Measure throughput, load impact, object requests, bytes, consistency, and whether every Graph set/metadata record is included."),
        ("absctl or ABS restore into empty cluster", "Measure RTO until query-ready including Graph metadata and indexes."),
        ("legacy asbackup/asrestore compatibility", "Document why legacy tooling is retained or reject it after restoring and semantically auditing a pinned artifact."),
        ("restore to changed topology", "Validate redistribution time and headroom."),
        ("backup retention 7", "Compute object bytes and request cost."),
        ("cross-region backup", "Charge egress and recovery latency."),
        ("TLS client-to-AGS", "Measure handshake, connection reuse, CPU, and p99."),
        ("TLS AGS-to-DB", "Measure per-command crypto and connection behavior."),
        ("certificate rotation", "Prove no unsafe fallback or outage."),
        ("JWT validation", "Measure per-request/session cost and expiry."),
        ("database RBAC", "Verify least privileges and startup/admin requirements."),
        ("audit logging", "Measure throughput/tail and user attribution."),
        ("tenant noisy query", "Measure cross-tenant queue/cache/DB interference."),
        ("tenant index collision", "Verify graph-scoped names and metadata."),
        ("tenant backup", "Verify restore/isolation granularity."),
        ("CVE image scan", "Prove 3.2.3 dependency closure and remaining findings."),
        ("secret masking", "Inspect logs, endpoints, traces, environment, and crash dumps."),
        ("Enterprise unique bytes", "Reconcile contract bytes with graph physical/logical bytes."),
        ("SC/MRT uplift", "Add licensed feature cost to transaction result."),
        ("support tier", "Charge required 24x7 response level."),
        ("DR cluster license", "Clarify unique data and active cluster treatment."),
        ("annual commit", "State term and discount; do not call on-demand price."),
        ("per-query cost", "Amortize full monthly cost at achieved SLO-qualified throughput."),
        ("per-billion-edge cost", "Include vertices, indexes, replicas, headroom, backup, and license."),
        ("PB capacity model", "Derive node/RAM/device count with uncertainty bands."),
        ("operator hours", "Track routine and incident effort."),
        ("upgrade drain", "Measure capacity and labor during rolling patch."),
        ("restore drill", "Charge duplicate infrastructure and time."),
    ]
    d.cases("Operational and economic qualification cases", expand_cases("operations", items, "Production-shaped topology with tagged cloud resources, dedicated telemetry, exact license assumptions, and no uncharged support services.", "fleet RSS/heap/CPU, PI/SI memory, storage/IO/network, cloud billing export, object requests, Spark hours, trace/log bytes, license and labor", "S02–S05,S14,S17–S24,S28–S32,S33,S37,S42–S44,S49,S50"))
    d.sources({"S02","S03","S04","S05","S14","S17","S18","S19","S20","S21","S22","S23","S24","S28","S29","S30","S31","S32","S33","S37","S42","S43","S44","S49","S50"})
    d.write("05-operations-resources-security-and-cost.md")


def make_benchmark() -> None:
    d = Markdown("Aerospike Graph benchmark audit and tenfold-win qualification", "Deconstruction of published results plus a fair, reproducible competitor protocol")
    d.h(2, "Published benchmark verdict")
    d.p("""
    The current Aerospike identity-graph report is valuable evidence that one vendor configuration processed a tens-of-billions property graph. It is not an independent benchmark, not a current 3.2 benchmark, not a cross-engine comparison, not PB evidence, and not a universal latency result. Preserve its exact workload shape: many sparse, independent or weakly connected identity subgraphs whose short reads and writes remain localized.

    The PDF reports three scale factors. The largest has 3,600 GB input CSV, 38.3 billion vertices, 37.2 billion edges, and 23.35 TB user data. It used 18 `n2d-highmem-64` database nodes with 24×375GB local NVMe each, RF2, one `n2d-standard-8` AGS for latency runs, and an `n2d-standard-32` load generator. The throughput scale test fixed the storage cluster and increased AGS from 1 to 32, reporting 22K to more than 600K QPS. The software was Database 7.1.0.9 and AGS 2.4.2.

    The charts do not provide a machine-readable raw sample bundle in the report, exact query text/source repository, optimizer profiles, backend operation counts, error rate, retry accounting, cache state, offered-load schedule, or a competitor result. The reported infrastructure cost uses a one-year commitment and March 5, 2025 GCP prices. These omissions prevent an audit-grade 10x conclusion.
    """)
    d.h(2, "Published dataset and hardware")
    d.table(["Scale", "CSV", "Vertices", "Edges", "User data", "DB nodes"], [
        ["10M", "35GB", "383M", "373M", "0.219TB", "3 × n2d-highmem-8"],
        ["100M", "358GB", "3.83B", "3.73B", "2.306TB", "8 × n2d-highmem-16"],
        ["1B", "3,600GB", "38.3B", "37.2B", "23.35TB", "18 × n2d-highmem-64"],
    ])
    d.h(2, "Published bulk-load results")
    d.table(["Scale", "Dataproc worker", "Workers", "Spark memory", "Time"], [
        ["10M", "n2d-highmem-8", "30", "1.875TB", "3.56h"],
        ["100M", "n2d-highmem-16", "60", "7.5TB", "8.00h"],
        ["1B", "n2d-highmem-64", "70", "35TB", "31.81h"],
    ])
    d.h(2, "Why universal 10x is invalid")
    d.bullets([
        "Latency, throughput, resources, cost, load time, freshness, availability, and semantic coverage are different objectives.",
        "A result is valid only for a workload cell with equal query semantics, durability, replication, consistency, dataset, hardware budget, and completion criteria.",
        "Unsupported queries cannot be replaced with easier operations or omitted from the geometric mean.",
        "Timeouts/errors must count as failed requests and remain in the result distribution.",
        "Open-loop offered load is required to expose queueing; closed-loop clients can hide overload.",
        "Warm caches must be memory-matched and explicitly disclosed; S3/native cold starts need a separate class.",
        "Cost claims must use the same region, term, discounts, replicas, storage headroom, licensing, and operational services.",
        "A 10x claim needs uncertainty intervals and repeat runs; one best run versus one competitor default is not evidence.",
        "The honest output may be a win/loss frontier: 10x in some cells, parity in others, unsupported or non-comparable elsewhere.",
    ])
    benchmark_items = [
        ("ID vertex read cold", "Compare authoritative point lookup without cache residency."),
        ("ID vertex read warm", "Compare hot point lookup with charged cache memory."),
        ("batch 100 vertex IDs", "Compare network and storage batching."),
        ("1-hop degree 4", "Represent small bounded adjacency."),
        ("1-hop degree 32", "Represent common identity expansion."),
        ("1-hop degree 512", "Expose batching and response size."),
        ("threshold-minus-one degree", "Stress largest inline adjacency record."),
        ("threshold-plus-one degree", "Expose supernode path discontinuity."),
        ("supernode 100K unfiltered", "Measure unavoidable output and safety limits."),
        ("supernode 100K 0.1% filter", "Measure server-side predicate pushdown."),
        ("2-hop fanout 4", "Bound frontier and path semantics."),
        ("2-hop fanout 32", "Expose intermediate materialization."),
        ("3-hop identity SR5", "Recreate vendor workload pattern exactly."),
        ("4-hop cyclic", "Measure visited/path work on cycles."),
        ("label root high selectivity", "Compare indexed root planning."),
        ("label root low selectivity", "Expose large-index result stream."),
        ("numeric equality index", "Compare root filtering."),
        ("numeric range index", "Compare range path."),
        ("string substring", "Expose unsupported index and scan behavior."),
        ("global vertex scan", "Compare bandwidth-oriented scan separately."),
        ("global edge scan", "Reproduce AGS 3.2 version claim and competitors."),
        ("local count", "Compare adjacency metadata optimization."),
        ("global exact count", "Require exact consistent result."),
        ("path materialization", "Charge full path objects."),
        ("dedup frontier", "Charge state memory."),
        ("top-K order", "Require same ordering/tie semantics."),
        ("add vertex", "Compare durable acknowledged creation."),
        ("update vertex property", "Compare contention-free update."),
        ("add ordinary edge", "Compare three-record graph mutation semantics."),
        ("add hot edge", "Compare contention and retries."),
        ("update edge property", "Expose packed-record false sharing."),
        ("delete edge", "Compare cleanup and read visibility."),
        ("delete ordinary vertex", "Compare incident-edge atomicity."),
        ("delete supernode", "Mark semantic limitation, not comparable success."),
        ("merge vertex", "Require uniqueness and idempotence."),
        ("merge edge", "Require same match/lock semantics."),
        ("explicit 10-record transaction", "Compare atomic multi-query scope."),
        ("explicit 1000-record transaction", "Expose transaction overhead."),
        ("read/write 95/5", "Measure mixed online load."),
        ("read/write 50/50", "Expose packing contention and cache invalidity."),
        ("scan plus point reads", "Measure workload isolation."),
        ("supernode plus point reads", "Measure heavy-query isolation."),
        ("one compute node", "Establish resource-normalized baseline."),
        ("2 compute nodes", "Measure scale efficiency."),
        ("4 compute nodes", "Measure scale efficiency."),
        ("8 compute nodes", "Measure storage approach to saturation."),
        ("16 compute nodes", "Locate database/network bottleneck."),
        ("32 compute nodes", "Reproduce vendor throughput topology."),
        ("one DB node dev", "Keep out of HA headline but measure floor."),
        ("three DB nodes RF2", "Production-shaped minimum."),
        ("six DB nodes RF2", "Measure storage horizontal scaling."),
        ("RF3", "Compare stronger replica capacity."),
        ("rack-aware local", "Measure cross-zone avoidance."),
        ("rack failure", "Measure degraded latency and cost."),
        ("DB node failure", "Measure p99.9 and errors through recovery."),
        ("AGS node failure", "Measure load balancer and in-flight requests."),
        ("rebalance", "Measure performance during add/remove."),
        ("cold restart", "Measure query-ready time and cache state."),
        ("rolling patch", "Measure operational availability."),
        ("1GB load", "Small-loader overhead."),
        ("100GB load", "Standalone/distributed crossover."),
        ("1TB load", "Reproduce 3.0 ingest claim."),
        ("10TB load", "Measure scale and Spark cost."),
        ("incremental 1% load", "Measure daily refresh economics."),
        ("backup", "Measure throughput and online impact."),
        ("restore", "Measure query-ready RTO."),
        ("storage bytes per edge", "Compare physical bytes including indexes/replicas."),
        ("RAM bytes per edge", "Compare full-cluster resident memory."),
        ("CPU per million queries", "Compare work efficiency at same SLO."),
        ("joules per million queries", "Optional energy efficiency."),
        ("monthly cost at 10K QPS", "Amortize all provisioned and licensed cost."),
        ("monthly cost at 100K QPS", "Measure scale and headroom."),
        ("monthly cost at 600K QPS", "Challenge vendor-scale claim fairly."),
        ("cost per billion edges", "Include vertex ratio and properties."),
        ("cost per PB logical", "Use capacity model with uncertainty."),
        ("S3 cold point read zu", "Measure zu's object-authoritative cold path."),
        ("S3 warm point read zu", "Measure bounded-cache steady state."),
        ("S3 outage zu", "Preserve system semantics and availability disclosure."),
        ("semantic conformance corpus", "Gate performance publication on equal results."),
        ("unsupported feature ledger", "Prevent silent workload deletion."),
    ]
    d.cases("Cross-engine benchmark cells", expand_cases("benchmark", benchmark_items, "Use dataset snapshots with fixed degree/property distributions; equal logical query, consistency, RF, durability, client locality, and dollar/resource budget.", "open-loop latency HDR, achieved/offered QPS, errors/timeouts/retries, CPU/RAM/storage/network, backend operations, freshness, recovery, dollars", "S05,S10–S16,S18,S19,S25,S26,S28,S33–S45"))
    d.h(2, "Tenfold claim acceptance rule")
    d.p("""
    Publish `10x` only when the lower 95% confidence bound of the improvement ratio exceeds 10 for the named metric and cell, all correctness gates pass, achieved throughput meets offered load, error/timeout rate is within the common SLO, and total charged resources/cost obey the declared comparison mode. Label the numerator and denominator, version, hardware, cache state, consistency, RF, dataset, query, percentile, and run date in the claim sentence.

    Never publish “10x faster than all graph databases.” A defensible sentence is narrower: for example, “zu commit X achieved 10.8–12.1x lower p99 latency than Aerospike Graph 3.2.3 on ID-rooted two-hop traversal Q17 at 20K offered QPS, RF2-equivalent durability, cold 8GB cache, and equal monthly infrastructure cost.”
    """)
    d.sources({"S05","S10","S11","S12","S13","S14","S15","S16","S18","S19","S25","S26","S28","S33","S34","S36","S37","S38","S39","S40","S41","S43","S44","S45"})
    d.write("06-benchmark-audit-and-10x-qualification.md")


def make_zu() -> None:
    d = Markdown("Aerospike-derived design lessons and solution plan for zu", "Actionable architecture, implementation, and qualification decisions for an S3-authoritative graph engine")
    d.h(2, "Recommended stance")
    d.p("""
    Copy Aerospike's disciplines, not its storage authority. The useful disciplines are compact schema interning, adjacency-aware point paths, batching by storage destination, server-side predicate pushdown, independent stateless query compute, explicit supernode treatment, scan admission, detailed source-visible operations, and separate bulk/OLAP paths. The non-fit is authoritative mutable record storage on a provisioned database cluster with primary/secondary index RAM and data-volume licensing.

    zu should make S3 the durable immutable authority and treat local NVMe/RAM as bounded, reconstructible acceleration. That changes the write contract: acknowledged mutations must enter an inexpensive durable log/manifest path, then compact into immutable graph segments. Low latency comes from deterministic ID routing, sparse indexes, compressed adjacency blocks, cache admission, request coalescing, and vectorized traversal—not from pretending an S3 GET is sub-millisecond.
    """)
    d.h(2, "Proposed architecture")
    d.bullets([
        "Immutable S3 graph segments partitioned by stable vertex-ID hash and optionally label/time locality.",
        "A small strongly consistent manifest/catalog that maps snapshot epoch and partitions to immutable objects.",
        "Durable mutation log or micro-batch delta objects with idempotent sequence numbers and explicit visibility epochs.",
        "Compact per-partition vertex table, out-adjacency blocks, optional in-adjacency blocks, property columns, and sparse indexes.",
        "Schema/label/property interning with immutable dictionaries versioned by epoch; avoid a single hot allocation counter.",
        "Stateless native query workers that resolve IDs, build batched object ranges, vectorize decode/filter, and stream results with bounded memory.",
        "A content-addressed local NVMe cache and smaller RAM index/cache with hard byte budgets, admission policy, tenant quotas, and no correctness role.",
        "Supernode-specific sharded adjacency chunks with property min/max/bloom metadata and per-label subranges.",
        "Explicit scan service/admission class separate from low-latency OLTP queues.",
        "Compaction and index builders as interruptible fixed-budget background jobs; publish read/write amplification and debt.",
        "Snapshot isolation by manifest epoch for reads; optional transactional mutation service scoped to declared keys/partitions.",
        "End-to-end counters: objects/ranges/bytes, cache, decode, frontier, spills, retries, S3 requests, cost estimate, and result cardinality per query.",
    ])
    d.h(2, "Direct design comparison")
    d.table(["Aerospike technique", "Lesson", "zu adaptation"], [
        ["Vertex record with embedded adjacency", "ID-rooted locality dominates hop cost", "Immutable vertex header points to compact adjacency blocks/ranges"],
        ["10-edge packed record", "Amortize per-record metadata and RPCs", "Pack thousands of sorted adjacency entries per compressed block, sized for range reads"],
        ["Schema interning", "Repeated strings are permanent tax", "Epoch-versioned dictionaries with local IDs and merge/remap tooling"],
        ["Supernode index path", "One layout fails across degree distribution", "Chunk and shard supernode adjacency from creation; use block metadata pushdown"],
        ["TinkerPop strategies", "Recognize high-value traversal patterns", "Typed IR and rule/cost optimizer with observable physical operators"],
        ["Batch per DB node", "Group I/O by destination", "Coalesce range/object reads by object and byte interval"],
        ["Filter expressions", "Push rejection to data access", "Evaluate predicates during vectorized decode before materialization"],
        ["Transactional/global cache", "Cache policy affects semantics/resources", "Cache never affects freshness; epoch keys make invalidation structural"],
        ["Scan disable", "Protect OLTP from accidental O(N)", "Cost guard, explicit scan capability, budget and queue class"],
        ["Stateless AGS", "Compute elasticity should avoid shard ownership", "Workers obtain snapshot/partition maps from manifest and hold no authority"],
        ["Spark loader", "Bulk creation needs a separate high-throughput path", "Distributed segment builder writes final S3 layout directly"],
        ["MRT", "Graph mutations span records", "Make transaction scope/cost explicit; avoid claiming arbitrary distributed ACID"],
    ])
    d.h(2, "PB and trillion-edge capacity model")
    d.p("""
    Capacity must be algebraic before it is empirical. For each edge, model encoded neighbor ID delta, label/type, property references/values, block index share, object overhead share, replication/version retention, and compression. For each vertex, model ID/key, label, property columns, out/in block pointers, sparse-index entries, and dictionary share. Add snapshot retention, uncompacted deltas, compaction overlap, checksums, manifests, and safety margin.

    A trillion edges at 12 logical encoded bytes per direction is already 24 TB before properties, vertices, indexes, object overhead, deltas, history, and replicas; at 50 bytes it is 50 TB for one direction. A PB target is therefore plausible only with transparent definitions of logical versus physical bytes. “Thousands of billions” means multiple trillions, not the 37.2B public Aerospike benchmark. Every capacity claim must state degree distribution, both-direction storage, property mix, compression, and retained epochs.
    """)
    items = [
        ("stable vertex routing", "Choose a hash/partition scheme that survives compute scaling."),
        ("partition map epoch", "Route every query against an immutable snapshot."),
        ("manifest atomic publish", "Make new snapshots all-or-nothing."),
        ("manifest service failure", "Define read availability with cached signed manifests."),
        ("schema dictionary allocation", "Avoid central hot counter while preserving stable decode."),
        ("dictionary merge", "Reconcile distributed builders deterministically."),
        ("vertex block layout", "Minimize point-read ranges and decode."),
        ("out adjacency block", "Optimize dominant directed hop."),
        ("in adjacency optionality", "Trade storage for reverse traversal SLO."),
        ("edge identity", "Preserve parallel edges, deletes, and path identity."),
        ("edge property columns", "Avoid reading unused values."),
        ("vertex property columns", "Support projection and predicate pushdown."),
        ("normal degree packing", "Tune block target by bytes, not edge count alone."),
        ("supernode preclassification", "Avoid costly one-way layout migration at threshold."),
        ("supernode chunk key", "Distribute hot reads/writes across chunks."),
        ("supernode label clustering", "Skip irrelevant edge labels."),
        ("supernode property metadata", "Use min/max/bloom/dictionary indexes to skip blocks."),
        ("S3 range coalescing", "Combine adjacent reads per object."),
        ("S3 request hedging", "Bound tails without uncontrolled request cost."),
        ("S3 retry budget", "Prevent retry storms and duplicate billed requests."),
        ("S3 multipart builder", "Write large immutable objects efficiently."),
        ("small-object avoidance", "Control request cost and listing/metadata burden."),
        ("NVMe content cache", "Make cached blocks reusable across epochs when content-identical."),
        ("RAM metadata cache", "Bound routing/index state by bytes."),
        ("cache admission", "Protect hot small blocks from scans."),
        ("tenant cache quota", "Prevent noisy tenant eviction."),
        ("cold point lookup", "Meet an honest object-store cold SLO."),
        ("warm point lookup", "Target Aerospike-class latency from bounded cache."),
        ("frontier batching", "Group next-hop IDs before I/O."),
        ("vectorized decode", "Reduce CPU and allocations per edge."),
        ("predicate pushdown", "Reject edges before object creation."),
        ("projection pushdown", "Read/decode only needed property streams."),
        ("limit pushdown", "Stop block reads after sufficient results while preserving order."),
        ("sample semantics", "Avoid biased block-level samples."),
        ("local count", "Answer from block metadata when semantically exact."),
        ("path memory", "Bound path retention or spill explicitly."),
        ("cycle detection", "Use compact visited structures with exact/approx modes."),
        ("typed physical IR", "Make operator choices and semantics inspectable."),
        ("rule optimizer", "Capture reliable ID/batch/pushdown rewrites."),
        ("cost optimizer", "Choose scan/index/block paths from current stats."),
        ("stats freshness", "Keep stale estimates from causing unbounded work."),
        ("plan fingerprint", "Attach physical plan identity to every benchmark sample."),
        ("scan admission", "Require explicit budget for O(N) operations."),
        ("heavy query queue", "Isolate scans/supernodes from short OLTP."),
        ("memory admission", "Reject before operator allocations exceed budget."),
        ("result backpressure", "Stream with bounded buffers."),
        ("request cancellation", "Stop S3 reads/decode after timeout/disconnect."),
        ("mutation idempotency", "Use client operation IDs and sequence numbers."),
        ("delta visibility", "Define when new vertices/edges enter snapshots."),
        ("read-your-writes", "Offer session overlay or explicit wait-for-epoch."),
        ("snapshot isolation", "Keep multi-hop traversal on one manifest epoch."),
        ("delete tombstone", "Prevent resurrection across compaction/late writes."),
        ("transaction key set", "Declare bounded atomic scope and failure behavior."),
        ("compaction budget", "Cap CPU/network/S3 cost and publish debt."),
        ("compaction overlap", "Charge temporary bytes and request cost."),
        ("incremental index build", "Publish index atomically with compatible epoch."),
        ("bulk import", "Build final layout without replaying online mutations."),
        ("bulk validation", "Detect orphan edges, duplicate IDs, and type errors."),
        ("backup semantics", "S3 authority makes snapshots native but catalog recovery still matters."),
        ("cross-region copy", "Define RPO/RTO and manifest ordering."),
        ("object corruption", "Use checksums, redundancy, and repair."),
        ("S3 outage", "Define cached-read and write-log behavior."),
        ("worker loss", "Retry stateless query fragments safely."),
        ("manifest split brain", "Fence publishers and verify monotonic epochs."),
        ("fixed monthly request budget", "Admission-control requests/bytes to a declared envelope."),
        ("per-query cost estimate", "Expose S3 requests, bytes, CPU, cache, and egress."),
        ("per-tenant budget", "Enforce predictable cost and fairness."),
        ("PB capacity derivation", "Publish uncertainty bands and retained-history factor."),
        ("trillion-edge generator", "Create realistic skew without materializing verbose input."),
        ("scale ladder", "Run 1B, 10B, 100B, 1T and validate model error."),
        ("Aerospike normal-degree comparison", "Target equal bounded traversal semantics."),
        ("Aerospike supernode comparison", "Target filtered/unfiltered discontinuity."),
        ("Aerospike resource comparison", "Charge AGS, DB, RF, headroom, indexes, and license."),
        ("Aerospike failure comparison", "Match consistency and degraded-state requirements."),
        ("10x p99 gate", "Require confidence-bound ratio and correctness."),
        ("10x resource gate", "Require full-system bytes/CPU, not process cherry-picking."),
        ("10x cost gate", "Require same term/region/SLO and all services."),
        ("regression corpus", "Retain every winning cell as continuous performance test."),
        ("public reproducibility", "Publish data generator, harness, raw samples, configs, and analysis."),
    ]
    d.cases("zu implementation and experiment backlog", expand_cases("zu", items, "Implement behind a versioned physical-format flag; test on deterministic datasets and fault-injected S3-compatible storage before promoting the design.", "object/range requests, bytes, cache, decode CPU, allocations, frontier, queue, tail latency, errors, dollars, compaction debt, correctness history", "Aerospike evidence S09–S45 plus zu-owned implementation artifacts"))
    d.h(2, "Release gates")
    d.bullets([
        "G0: semantic conformance for IDs, parallel edges, properties, direction, paths, bags, order, null/missing, and mutations.",
        "G1: deterministic physical format, checksums, upgrade reader, and snapshot manifest recovery.",
        "G2: bounded-memory point and traversal operators under slow consumers and cancellation.",
        "G3: cold/warm latency results with object-request and byte counters; no hidden unbounded cache.",
        "G4: fault results for S3, worker, manifest, network, and compaction failures.",
        "G5: capacity-model prediction within declared error at each scale-ladder step.",
        "G6: full cost sheet at target SLO, including requests, compute, cache, storage, egress, operations, and redundancy.",
        "G7: Aerospike 3.2.3 comparison with equal semantics and current Database release.",
        "G8: per-cell 10x claims only where the confidence and correctness rules pass.",
        "G9: public artifact bundle sufficient for an independent rerun.",
    ])
    d.sources(None)
    d.write("07-design-lessons-for-zu.md")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_index()
    make_product()
    make_storage()
    make_query()
    make_transactions()
    make_ops()
    make_benchmark()
    make_zu()


if __name__ == "__main__":
    main()
