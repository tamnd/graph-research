#!/usr/bin/env python3
"""Generate the source-audited AgensGraph 2026 dossier."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


OUT = Path(__file__).resolve().parents[2] / "docs" / "research" / "agensgraph"
CUT = "2026-08-08"
STABLE = "4174bdeb81e6cb6ee4d85b5835491b8509d04e52"
HEAD = "9f9297c7008ca0451681a7d992d7e32eee307d8e"


SOURCES = [
    ("S01", "AgensGraph v2.17.0 release", "Official GitHub release", "Released 2026-06-19; PostgreSQL 17.10 base and graph changes", "https://github.com/skaiworldwide-oss/agensgraph/releases/tag/v2.17.0"),
    ("S02", "AgensGraph 2.17 release notes", "Official manual", "Detailed upstream, Cypher, index, delete, and AI integration changes", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/release_notes/agensgraph_release_notes_2_17_0.html"),
    ("S03", "AgensGraph 2.17 manual", "Official manual", "Current documentation root retrieved at the research cut", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/"),
    ("S04", "v2.17.0 source snapshot", "Official source", f"Exact shipped tag commit {STABLE}", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{STABLE}"),
    ("S05", "2.18-devel source snapshot", "Official source", f"Public main observed at {HEAD}; unreleased", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{HEAD}"),
    ("S06", "Repository releases", "Official GitHub metadata", "Release chronology and immutable tag targets", "https://github.com/skaiworldwide-oss/agensgraph/releases"),
    ("S07", "Repository issues", "Public issue tracker", "Reports are leads, not reproduced facts", "https://github.com/skaiworldwide-oss/agensgraph/issues"),
    ("S08", "Repository actions", "Official CI metadata", "Main workflow status and logs", "https://github.com/skaiworldwide-oss/agensgraph/actions"),
    ("S09", "Graph query quick guide", "Official manual", "Graph selection, labels, elements, JSONB properties", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/quick_guide/graph_query.html"),
    ("S10", "Installation and tuning", "Official manual", "Build, Docker, shared_buffers, work_mem, random_page_cost", "https://tech.skaiworldwide.com/docs/en/agensgraph/17/quick_guide/installation.html"),
    ("S11", "Architecture", "Official manual", "PostgreSQL process and memory architecture inherited by AgensGraph", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/operation_manual/architecture.html"),
    ("S12", "Hybrid SQL and Cypher", "Official manual", "Cypher in SQL and SQL subqueries in Cypher", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/developer_manual/hybrid.html"),
    ("S13", "Upgrade guide", "Official manual", "pg_upgrade route from 2.15/2.16 to 2.17 and rollback", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/upgrade_guide/index.html"),
    ("S14", "2.16 release notes", "Official manual", "PostgreSQL 16.9 base, RLS and interoperability context", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/release_notes/agensgraph_release_notes_2_16_0.html"),
    ("S15", "PostgreSQL 17 HA", "Upstream official manual", "Streaming, synchronous, logical replication and failover primitives", "https://www.postgresql.org/docs/17/high-availability.html"),
    ("S16", "PostgreSQL 17 backup", "Upstream official manual", "Base backup, WAL archive, PITR and recovery semantics", "https://www.postgresql.org/docs/17/backup.html"),
    ("S17", "PostgreSQL 17 MVCC", "Upstream official manual", "Isolation, snapshots, locking and serialization behavior", "https://www.postgresql.org/docs/17/mvcc.html"),
    ("S18", "PostgreSQL 17 resource consumption", "Upstream official manual", "shared_buffers, work_mem, maintenance memory and huge pages", "https://www.postgresql.org/docs/17/runtime-config-resource.html"),
    ("S19", "PostgreSQL 17 planner cost", "Upstream official manual", "Planner cost constants and statistics", "https://www.postgresql.org/docs/17/runtime-config-query.html"),
    ("S20", "PostgreSQL 17 BRIN", "Upstream official manual", "Block-range index behavior and correlation dependency", "https://www.postgresql.org/docs/17/brin.html"),
    ("S21", "Graph vertex catalog header", "Pinned stable source", "Vertex tuple shape and graph element type", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/include/catalog/ag_vertex.h"),
    ("S22", "Graph edge catalog header", "Pinned stable source", "Edge tuple shape including start and end graphid", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/include/catalog/ag_edge.h"),
    ("S23", "Graph identifiers", "Pinned stable source", "graphid bit allocation and helper macros", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/include/utils/graph.h"),
    ("S24", "Graph DDL implementation", "Pinned stable source", "Graph/schema/label creation and catalogs", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/commands/graphcmds.c"),
    ("S25", "Graph utility transform", "Pinned stable source", "Inherited label relations and automatic indexes", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/parser/parse_utilcmd.c"),
    ("S26", "Cypher lowering", "Pinned stable source", "Pattern transformation into PostgreSQL query trees", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/parser/parse_graph.c"),
    ("S27", "Cypher expression lowering", "Pinned stable source", "Cypher expression and JSONB handling", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/parser/parse_cypher_expr.c"),
    ("S28", "Variable-length executor", "Pinned stable source", "DFS traversal state, scans, path uniqueness and memory", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/executor/execGraphVle.c"),
    ("S29", "Shortest-path executor", "Pinned stable source", "Custom path node, hash state and batching", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/executor/nodeShortestpath.c"),
    ("S30", "Graph mutation executor", "Pinned stable source", "CREATE, DELETE, SET and MERGE executor paths", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{STABLE}/src/backend/executor"),
    ("S31", "Graph GUCs", "Pinned stable source", "enable_graph_dml and graph/planner controls", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/backend/utils/misc/guc_tables.c"),
    ("S32", "Graph catalogs", "Pinned stable source", "ag_graph and ag_label catalog definitions", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{STABLE}/src/include/catalog"),
    ("S33", "Graph regression SQL", "Pinned stable source", "Graph semantic and executor regression corpus", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{STABLE}/src/test/regress/sql"),
    ("S34", "Graph expected results", "Pinned stable source", "Expected output oracles paired with regression SQL", f"https://github.com/skaiworldwide-oss/agensgraph/tree/{STABLE}/src/test/regress/expected"),
    ("S35", "Official regression schedule", "Pinned stable source", "Ordering and isolation contract for regression tests", f"https://github.com/skaiworldwide-oss/agensgraph/blob/{STABLE}/src/test/regress/parallel_schedule"),
    ("S36", "PostgreSQL announcement for 2.16", "PostgreSQL community announcement", "Independent timestamp and release synopsis", "https://www.postgresql.org/about/news/announcing-the-release-of-agensgraph-v2160-3149/"),
    ("S37", "LDBC / Graph Data Council", "Benchmark authority", "SNB benchmark specifications and implementation policy", "https://ldbcouncil.org/benchmarks/snb/"),
    ("S38", "LDBC implementations", "Benchmark source", "Reference implementation inventory; no maintained AgensGraph result found", "https://github.com/ldbc/ldbc_snb_interactive_v1_impls"),
    ("S39", "AgensGraph issue 503", "Public issue report", "Request for an LDBC benchmark implementation", "https://github.com/skaiworldwide-oss/agensgraph/issues/503"),
    ("S40", "AgensGraph issue 516", "Public issue report", "Privilege/DDL concern; qualify against current stable", "https://github.com/skaiworldwide-oss/agensgraph/issues/516"),
    ("S41", "AgensGraph issue 628", "Public issue report", "Sequence use in parallel operation", "https://github.com/skaiworldwide-oss/agensgraph/issues/628"),
    ("S42", "AgensGraph issue 731", "Public issue report", "Variable-length traversal semantics lead", "https://github.com/skaiworldwide-oss/agensgraph/issues/731"),
    ("S43", "AgensGraph issue 777", "Public issue report", "nodes()/relationships() behavior lead", "https://github.com/skaiworldwide-oss/agensgraph/issues/777"),
    ("S44", "AgensGraph issue 795", "Public issue report", "Undirected VLE asymmetry lead", "https://github.com/skaiworldwide-oss/agensgraph/issues/795"),
    ("S45", "AgensGraph issue 799", "Public issue report", "Simple VLE returning no rows lead", "https://github.com/skaiworldwide-oss/agensgraph/issues/799"),
    ("S46", "AgensGraph issue 803", "Public issue report", "OPTIONAL MATCH collect null semantics lead", "https://github.com/skaiworldwide-oss/agensgraph/issues/803"),
    ("S47", "pgvector", "Upstream extension source", "HNSW and vector operator implementation used by 2.17 examples", "https://github.com/pgvector/pgvector"),
    ("S48", "AgensGraph downloads", "Official product page", "Binary and driver availability; page lag is recorded", "https://tech.skaiworldwide.com/downloads/"),
    ("S49", "Docker image listing", "Official distribution channel", "Mutable latest tag requires digest pinning", "https://hub.docker.com/r/skaiworldwide/agensgraph"),
    ("S50", "Developer manual", "Official manual", "Feature summary, HA claim, indexing and security", "https://tech.skaiworldwide.com/docs/en/agensgraph/latest/developer_manual/index.html"),
]


@dataclass(frozen=True)
class Case:
    name: str
    purpose: str
    setup: str
    workload: str
    metrics: str
    oracle: str
    failure: str
    evidence: str


class Doc:
    def __init__(self, title: str, scope: str):
        self.lines = [
            f"# {title}", "",
            f"Research cut: `{CUT}`",
            f"Stable baseline: `v2.17.0` / `{STABLE}` / PostgreSQL 17.10",
            f"Unreleased comparison: `2.18-devel` / `{HEAD}`",
            "Evidence status: source-audited; claims and issue reports are explicitly qualified",
            f"Scope: {scope}", "",
        ]

    def h(self, n: int, text: str) -> None:
        self.lines += [f"{'#' * n} {text}", ""]

    def p(self, text: str) -> None:
        for para in dedent(text).strip().split("\n\n"):
            self.lines += [line.rstrip() for line in para.splitlines()] + [""]

    def bullets(self, rows: list[str]) -> None:
        self.lines += [f"- {row}" for row in rows] + [""]

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        self.lines.append("| " + " | ".join(headers) + " |")
        self.lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            self.lines.append("| " + " | ".join(v.replace("|", "\\|") for v in row) + " |")
        self.lines.append("")

    def findings(self, title: str, rows: list[tuple[str, str, str]]) -> None:
        self.h(2, title)
        for i, (name, finding, evidence) in enumerate(rows, 1):
            self.h(3, f"F{i:03d} — {name}")
            self.lines += [
                f"- Finding: {finding}",
                f"- Evidence class: {evidence}",
                "- Decision use: retain this statement only with its version and evidence qualifier.",
                "- Revalidation: repeat after a release, storage-layout change, or benchmark-baseline change.",
                "",
            ]

    def cases(self, title: str, rows: list[Case]) -> None:
        self.h(2, title)
        self.p("Each case is an independent result cell. Preserve query semantics, data shape, durability, and failure behavior. Report p50/p95/p99/p99.9 and maximum separately; do not average percentiles or omit failed operations.")
        for i, c in enumerate(rows, 1):
            self.h(3, f"Q{i:03d} — {c.name}")
            self.lines += [
                f"- Purpose: {c.purpose}",
                f"- Setup: {c.setup}",
                f"- Workload: {c.workload}",
                f"- Required metrics: {c.metrics}",
                f"- Correctness oracle: {c.oracle}",
                f"- Failure interpretation: {c.failure}",
                f"- Evidence anchors: {c.evidence}",
                "- Status: `NOT RUN` unless an observation is explicitly recorded in this dossier.",
                "- Artifact set: config, schema, dataset manifest, query text, EXPLAIN output, raw samples, server telemetry, logs, and cost sheet.",
                "",
            ]

    def sources(self, ids: set[str] | None = None) -> None:
        self.h(2, "Source register")
        self.p("Official status proves what a project states or ships, not performance. Git links are commit-pinned. Public issue reports are test leads until reproduced on the pinned stable build.")
        for sid, title, kind, note, url in SOURCES:
            if ids is None or sid in ids:
                self.h(3, f"{sid} — {title}")
                self.lines += [f"- Type: {kind}", f"- Audit note: {note}", f"- URL: {url}", ""]

    def write(self, name: str) -> None:
        while self.lines and self.lines[-1] == "":
            self.lines.pop()
        self.lines.append("")
        (OUT / name).write_text("\n".join(self.lines).rstrip() + "\n", encoding="utf-8")


def mk_cases(prefix: str, items: list[tuple[str, str]], setup: str, evidence: str, write: bool = False) -> list[Case]:
    rows = []
    for name, purpose in items:
        rows.append(Case(
            f"{prefix}: {name}", purpose, setup,
            f"Execute `{name}` at controlled concurrency against cold, warm, steady-state, and pressure states" + ("; verify after commit, checkpoint, crash, and restart" if write else ""),
            "latency distribution, throughput, CPU time, RSS, shared buffers, page-cache reads, logical/physical I/O, WAL, temp bytes, locks, plans, rows estimated/actual, errors",
            "Compare exact rows, bags, order, graph element identity, path uniqueness, and committed durable state with an independent model oracle",
            "Any semantic mismatch, crash, hidden sequential scan, timeout, unbounded memory, replica inconsistency, or omitted failure is a failed cell",
            evidence,
        ))
    return rows


CORE_FINDINGS = [
    ("Product form", "AgensGraph 2.17 is a PostgreSQL 17.10 source fork and complete server distribution, not a loadable extension for arbitrary stock PostgreSQL.", "S01,S04"),
    ("Stable release", "v2.17.0 is the newest stable GitHub release found at the research cut and was published on 2026-06-19.", "S01,S06"),
    ("Development head", "Public main identified itself as 2.18-devel at the pinned August 4 commit and differs materially from stable.", "S05"),
    ("Graph representation", "A graph is represented by a PostgreSQL schema plus AgensGraph catalogs; every label is a relation inheriting from the graph's base vertex or edge relation.", "S21-S25,S32"),
    ("Vertex tuple", "A stable vertex tuple stores graphid and non-null JSONB properties; a vertex-label primary key indexes id.", "S21,S25"),
    ("Edge tuple", "A stable edge tuple stores graphid, start graphid, end graphid, and non-null JSONB properties.", "S22,S25"),
    ("Graph value row identity", "The vertex/edge composite types also carry a `tid` populated from the heap `ctid`; it is execution identity metadata, not an additional user-declared label-table column.", "S21,S22,S26,S27"),
    ("Endpoint indexes", "Every edge label receives B-tree indexes on `(start,end)` and `(end,start)`, plus a BRIN index on edge id.", "S20,S25"),
    ("Identifier layout", "graphid is 64 bits with a 16-bit label component and a 48-bit local sequence component.", "S23"),
    ("Label ceiling", "The encoding provides at most 65,535 label identifiers and 2^48 local identifiers per label; these are encoding ceilings, not validated capacity claims.", "S23"),
    ("Properties", "Stable stores graph properties in JSONB and expresses property indexes using PostgreSQL expression indexes.", "S09,S21,S22,S25"),
    ("Cypher lowering", "Cypher patterns and expressions are lowered into PostgreSQL query trees, scans and joins rather than sent to a separate graph service.", "S26,S27"),
    ("Dedicated nodes", "CREATE, DELETE, MERGE, SET, variable-length expansion and shortest path have graph-specific executor paths.", "S28-S30"),
    ("Hybrid strength", "SQL and Cypher can participate in one backend query, allowing relational, graph, JSONB, full-text and vector operators to compose.", "S03,S12"),
    ("ACID base", "Graph operations execute inside PostgreSQL transactions and inherit MVCC, WAL, crash recovery and locking machinery.", "S04,S17"),
    ("Distribution boundary", "The audited core has PostgreSQL primary/standby replication but no native shared-nothing graph partitioner or multi-writer distributed transaction layer.", "S04,S15"),
    ("Object-store boundary", "S3 may hold base backups or WAL via external tools, but stable source has no S3-backed online graph page manager.", "S04,S16"),
    ("Scale evidence", "No reproducible PB or trillion-edge AgensGraph result was found in the audited official sources.", "S01-S08,S37-S39"),
    ("Competitor evidence", "No audited same-hardware, same-semantics result establishes a universal 10x win over popular graph engines.", "S37-S39"),
    ("Delete claim", "2.17 reports up to roughly 30x faster DELETE/DETACH DELETE in internal tests by avoiding sequential checks of every edge label; this is version-over-version vendor evidence.", "S02"),
    ("Build observation", "The exact v2.17 tag configured, compiled and installed successfully on Apple Silicon after optional ICU/readline/zlib were disabled for the local environment.", "Local observation, 2026-08-08"),
    ("Regression observation", "The official core regression schedule passed locally; four graph tests also passed individually after an invalid custom shared-database grouping produced contamination.", "Local observation,S35"),
    ("Documentation drift", "The main README release badge lagged the actual 2.17 release and the download page listed only through 2.16 at retrieval time.", "S01,S05,S48"),
    ("License diligence", "Repository prose says Apache-2.0 while the PostgreSQL-derived tree contains upstream PostgreSQL notices; distributions must preserve all applicable notices.", "S04"),
    ("Connection model", "It retains PostgreSQL's process-per-connection architecture; a pooler is normally required for large client fan-out.", "S11"),
    ("Maintenance", "Autovacuum, analyze, checkpoints, WAL retention, relation bloat and index maintenance remain part of graph operations.", "S04,S18,S19"),
]


def make_index() -> None:
    d = Doc("AgensGraph 2026 dossier: index and decision verdict", "Navigation, headline verdict, source map, contradictions, and acceptance gates")
    d.h(2, "Outcome")
    d.p("""
    AgensGraph is the strongest comparator in this corpus for a specific proposition: graph queries do not need to abandon PostgreSQL semantics or its relational ecosystem. Its stable design maps vertex labels and edge labels to inherited PostgreSQL relations, stores properties in JSONB, creates endpoint indexes for every edge label, lowers Cypher into PostgreSQL query trees, and adds custom executor nodes where ordinary scans and joins are insufficient. That gives it real ACID transactions, SQL/Cypher composition, mature backup and observability primitives, and a familiar operational envelope.

    It does not meet the target architecture as shipped. One writable PostgreSQL primary remains the write and storage authority. Streaming replicas improve availability and read capacity but do not partition one graph's write path or turn cross-shard traversals into a native distributed operator. Online data and indexes require database storage; S3 is a backup/archive destination through surrounding PostgreSQL tooling, not the random-access graph store. Consequently PB capacity, trillion-edge operation, fixed S3-like marginal cost, and a universal tenfold competitor win are unproven.

    The useful design lesson is selective. Reuse PostgreSQL-grade semantics, typed expression indexes, costed plans and hybrid algebra, while avoiding relation-per-label fan-out, duplicated endpoint indexes for every workload, process-per-connection overhead, single-primary capacity, and JSONB extraction on the hottest property predicates. The unreleased 2.18-devel property-promotion and endpoint-elision work independently confirms where stable 2.17 pays avoidable cost.
    """)
    d.h(2, "Dossier map")
    files = [
        ("01-product-lineage-releases-and-evidence.md", "Ownership, releases, PostgreSQL base, documentation drift, claims and issue taxonomy"),
        ("02-source-storage-indexes-and-identifiers.md", "Physical tuples, inherited labels, graphid, indexes, JSONB, access paths and amplification"),
        ("03-cypher-sql-planner-and-execution.md", "Parsing, lowering, plans, fixed and variable traversal, shortest path and hybrid queries"),
        ("04-transactions-correctness-concurrency-and-security.md", "MVCC, graph mutations, constraints, races, privileges, issue-derived semantic tests"),
        ("05-operations-distribution-resources-s3-and-cost.md", "Processes, memory, vacuum, HA, backup, scale ceilings, object storage and TCO"),
        ("06-benchmark-audit-and-10x-qualification.md", "Evidence audit and reproducible latency/resource/scale/competitor benchmark"),
        ("07-design-lessons-and-proposed-architecture.md", "Concrete adoption/avoidance decisions and a PB/S3-oriented architecture response"),
    ]
    d.table(["Specification", "Purpose"], [[f"[{x}](./{x})", y] for x, y in files])
    d.h(2, "Evidence labels")
    d.bullets([
        "Observed: reproduced locally against the exact pinned tag with commands and outcome recorded.",
        "Source fact: directly visible in a pinned code path; it may describe unreleased behavior if attached to main.",
        "Official statement: product documentation or release metadata; performance magnitude remains a claim.",
        "Vendor claim: preserve workload and comparison scope; never promote it to a general result.",
        "Issue report: a test lead submitted publicly; not a confirmed current defect until reproduced.",
        "Inference: an architectural conclusion derived from evidence; state the premises and disproof test.",
        "Unknown: source or artifact is absent; do not invent a favorable implementation.",
    ])
    d.h(2, "Local source and build audit")
    d.p("""
    The stable audit used a detached checkout of tag `v2.17.0` at `4174bdeb81e6cb6ee4d85b5835491b8509d04e52`. The checkout contains 7,188 tracked files. C/H/Y/L files under `src/backend` and `src/include` total 1,280,539 lines; a conservative filename-based graph/Cypher/VLE/shortest-path subset totals 23,999 lines. The stable regression tree contains 15 SQL files whose names identify graph, Cypher, or property-index coverage. These counts describe audit surface, not quality.

    The local Apple Silicon configuration was `./configure --prefix=<temporary-install> --without-readline --without-zlib --without-icu`. The first default configure attempt stopped because ICU development dependencies were unavailable; disabling optional ICU allowed configuration. `make -j8` and `make install` completed. The installed server reported `postgres (PostgreSQL) 17.10`.

    An initial hand-selected batch of 15 graph tests put tests from different official schedule positions into one shared regression database. Four then differed because objects/data leaked across that nonstandard ordering. Each of those four—`cypher_dml`, `cypher_func`, `cypher_shortestpath2`, and `propertyindex`—passed when run alone in a fresh regression database. The authoritative follow-up was unmodified `make check`: all 241 scheduled tests passed, including every graph group. This is compilation and regression evidence only; it contains no latency, capacity, durability-fault, or competitor benchmark.

    Development comparison uses main commit `9f9297c7008ca0451681a7d992d7e32eee307d8e`, identifying as `2.18-devel`. Relative to v2.17.0, the raw tree diff spans 3,963 files with 347,796 insertions and 173,224 deletions because it mixes upstream PostgreSQL evolution with graph work. Every development finding is therefore attributed to inspected graph commits/files, never to the bulk diff magnitude.
    """)
    d.findings("Decision-grade findings", CORE_FINDINGS + [
        ("One label per element", "Stable documentation and DDL encode one concrete vertex or edge label per element, with label inheritance providing hierarchy rather than arbitrary multi-label membership.", "S09,S24,S25"),
        ("Unlabeled behavior", "Creating an unlabeled vertex uses the base ag_vertex label; an edge label cannot be omitted.", "S09"),
        ("Typo hazard", "The graph query guide warns that a mistyped label may create an unintended label during writes.", "S09"),
        ("Index statistics", "Stable raises statistics targets for edge endpoints, trading analyze/statistics work for better skew estimates.", "S25"),
        ("BRIN caveat", "The automatic edge-id BRIN index is valuable only to the extent heap order correlates with graphid ranges.", "S20,S25"),
        ("HNSW integration", "2.17 property expression indexes can use pgvector HNSW; that proves composition, not distributed vector capacity.", "S02,S47"),
        ("Full-text integration", "2.17 examples use PostgreSQL tsvector/GIN expression indexes over properties.", "S02,S03"),
        ("Direct graph DML", "enable_graph_dml is superuser-controlled and off by default because direct relational DML can violate graph invariants.", "S31"),
        ("Main property promotion", "2.18-devel adds typed promoted property columns and native-column reads; it must not be attributed to stable 2.17.", "S05"),
        ("Main endpoint elision", "2.18-devel can elide unread labeled endpoints using graphid ranges, signaling planner work beyond stable.", "S05"),
        ("Main correctness churn", "Post-2.17 commits include concurrent-write rechecks, VLE memory release, DDL gates and property-shape fixes.", "S05"),
        ("Open semantic reports", "Recent issues include OPTIONAL MATCH aggregation, UNION visibility, IN/list behavior and VLE results; each becomes a regression cell.", "S07,S42-S46"),
        ("LDBC absence", "An open request for LDBC implementation and absence from the audited reference inventory mean no official audited LDBC result was found.", "S38,S39"),
        ("Tuning warning", "The vendor's half-RAM shared_buffers and extremely low random_page_cost advice is workload-specific and requires plan/I/O validation.", "S10,S18,S19"),
        ("Fixed cost verdict", "A continuously provisioned primary, replicas, block storage, WAL, indexes, vacuum and backup make cost capacity-bound rather than S3-only fixed.", "S04,S15-S18"),
    ])
    gate_items = [
        ("stable artifact pin", "Reject mutable Docker latest and record image digest, source commit and PostgreSQL base"),
        ("semantic oracle", "Pass exact bag/order/null/path identity checks for every supported Cypher shape"),
        ("single-hop hot", "Demonstrate warm ID-rooted one-hop latency at target concurrency"),
        ("single-hop cold", "Bound random-device misses without hiding page cache warm-up"),
        ("multi-hop skew", "Survive power-law degrees and supernodes without percentile collapse"),
        ("variable length", "Bound work, memory and path explosion across depth/selectivity cells"),
        ("write atomicity", "Prove endpoint and edge invariants across conflict, abort, crash and replay"),
        ("replica failover", "Measure RPO/RTO and stale-read window under planned and unplanned promotion"),
        ("vacuum debt", "Include churn, dead tuples, autovacuum lag, index bloat and wraparound safety"),
        ("backup restore", "Restore a graph and independently verify catalogs, sequences, labels and paths"),
        ("PB projection", "Use measured bytes/element and IOPS, not graphid theoretical capacity"),
        ("trillion edge", "Show load, steady reads, updates, failure recovery and maintenance at stated scale"),
        ("S3 authority", "Require online reads after local-cache eviction with S3 as durable source"),
        ("fixed budget", "Enforce admission and report throttling rather than silently autoscaling cost"),
        ("10x claim", "Require confidence bounds and wins across predeclared workload classes"),
        ("resource claim", "Charge client, pooler, primary, replicas, page cache, WAL, backups and operators"),
        ("security", "Reproduce least-privilege graph DDL/DML and row-level visibility behavior"),
        ("upgrade", "Exercise pg_upgrade plus rollback with property indexes and graph catalogs"),
        ("extension compatibility", "Test every extension against this PostgreSQL fork and exact ABI"),
        ("main separation", "Never mix unreleased 2.18-devel results into a 2.17 score"),
    ]
    d.cases("Acceptance gates", mk_cases("gate", gate_items, "Exact v2.17 binary plus the proposed engine on immutable equivalent infrastructure", "S01-S05,S15-S19,S33-S39"))
    d.sources()
    d.write("00-index.md")


def make_lineage() -> None:
    d = Doc("AgensGraph product lineage, releases, and evidence audit", "Stable/development separation, provenance, packaging, documentation, claims, blogs, issues, and reproducibility")
    d.h(2, "Release ledger")
    d.table(["Release", "Date", "PostgreSQL base", "Audit interpretation"], [
        ["2.14.1", "2025-01-16", "older line", "Historical maintenance baseline"],
        ["2.15.0", "2025-04-04", "15 line", "Upgrade source supported by current guide"],
        ["2.16.0", "2025-09-12", "16.9", "RLS, pgvector interoperability, Cypher fixes"],
        ["2.17.0", "2026-06-19", "17.10", "Stable research baseline"],
        ["2.18-devel", "2026-08-04 pin", "development", "Unreleased; architecture preview only"],
    ])
    d.p("The project advances by rebasing a complete PostgreSQL-derived server, so a version number conveys two moving surfaces: upstream PostgreSQL behavior and AgensGraph graph patches. Upgrade and extension qualification must cover both. A stock PostgreSQL extension compatibility statement is not automatically transitive to a fork compiled at a different server ABI.")
    d.findings("Lineage and evidence findings", CORE_FINDINGS + [
        ("Archived extension lineage", "The older AgensGraph-Extension repository moved into Apache AGE and was archived; it is a distinct extension lineage, not current AgensGraph server source.", "Official repository history"),
        ("Manual freshness", "The latest manual resolves to 2.17 and includes release, upgrade, vector, full-text, hybrid and AI sections.", "S02,S03,S13"),
        ("Download lag", "The official download page displayed server buttons only through v2.16 while GitHub and the manual exposed v2.17.", "S01,S03,S48"),
        ("README lag", "The development README badge lagged stable release metadata; automate version consistency checks.", "S01,S05"),
        ("Docker mutability", "The installation guide's unqualified image pull resolves a mutable latest tag; reproducible deployments require a digest.", "S10,S49"),
        ("AI scope", "LangChain, LlamaIndex, LightRAG and MCP adapters are integration surface, not evidence for storage latency, capacity or correctness.", "S02,S03"),
        ("Release claim scope", "The 30x delete statement is tied to internal high-connectivity delete testing and an algorithmic removal of label-wide scans.", "S02"),
        ("Upstream benefits", "Incremental base backup, MERGE, JSON_TABLE and vacuum changes in 2.17 derive substantially from PostgreSQL 17.", "S01,S02"),
        ("Property index novelty", "HNSW and full-text expression-index examples are 2.17 integration enhancements, not a new native index implementation.", "S02,S47"),
        ("Public development velocity", "August main shows dense graph planner, typed-property and correctness work soon after stable; pinning is mandatory.", "S05"),
        ("CI boundary", "A green main workflow establishes that its configured suite passed, not that stable passes all platforms or external semantics.", "S08"),
        ("Local build boundary", "The local Apple Silicon build excluded optional ICU/readline/zlib due environment availability, so it is compile/regression evidence, not production performance evidence.", "Local observation"),
        ("Test scheduling lesson", "Graph regression tests share objects and rely on the official schedule; arbitrary aggregation can create false failures.", "S33-S35,local observation"),
        ("Issue population", "Open-issue count combines requests, defects and pull requests; it is not a defect-rate metric.", "S07"),
        ("Recent issue value", "Issue reports reveal semantic boundary cases absent from marketing material and should be converted to differential tests.", "S42-S46"),
        ("No popular benchmark", "No current official LDBC submission or reproducible competitor suite was found.", "S37-S39"),
        ("Brand change", "Current repository ownership and documentation use SKAI/Skaiworldwide naming while historical material uses Bitnine; provenance searches must cover both.", "S01-S06,S36"),
        ("License claim", "README licensing must be read with upstream PostgreSQL copyright files and bundled component notices.", "S04"),
        ("Support unknown", "The public source and manuals do not establish commercial SLA, exact support price or guaranteed scale envelope.", "S01-S06"),
        ("Compatibility unknown", "Claims that PostgreSQL extensions work require exact extension/build/runtime qualification against AgensGraph 2.17.", "S03,S04,S47"),
    ])
    items = [
        ("release tag immutability", "Verify tags, commits, tarball hashes and image digest agree"),
        ("version string consistency", "Compare server, CLI, README, manual, image labels and download page"),
        ("PostgreSQL patch level", "Confirm server behavior and CVE posture correspond to 17.10 plus downstream patches"),
        ("source-to-image provenance", "Rebuild and compare SBOM, binaries and compiler flags with distributed artifacts"),
        ("license inventory", "Enumerate upstream and bundled licenses and redistribution obligations"),
        ("reproducible build", "Build twice in pinned toolchains and compare artifacts or explain variance"),
        ("Linux build", "Compile on every supported production architecture and libc"),
        ("Apple build", "Retain local compile regression as development-only coverage"),
        ("optional dependency matrix", "Test ICU, OpenSSL, readline, zlib, XML, LDAP, Kerberos and language options"),
        ("official regression schedule", "Run the exact schedule without custom reordering"),
        ("graph tests isolated", "Run graph cases in clean databases to identify hidden dependencies"),
        ("main workflow replay", "Reproduce public CI in a pinned environment"),
        ("2.16 to 2.17 upgrade", "Follow published pg_upgrade path and validate graphs"),
        ("2.15 to 2.17 upgrade", "Exercise the oldest documented direct source version"),
        ("rollback", "Prove published rollback boundaries before production cutover"),
        ("extension ABI", "Compile and run pgvector, PostGIS and required extensions"),
        ("driver matrix", "Exercise JDBC, Python, Node and Go against exact server semantics"),
        ("mutable latest drift", "Detect and reject image tag mutation"),
        ("manual link integrity", "Crawl current docs and flag stale version selectors and dead links"),
        ("release note traceability", "Map every graph release claim to source diff and regression"),
        ("30x delete reproduction", "Recover the internal workload assumptions or construct a transparent equivalent"),
        ("HNSW feature", "Confirm extension version, operator class, recall and update behavior"),
        ("GIN full-text feature", "Confirm expression and collation semantics over JSONB properties"),
        ("AI adapter isolation", "Measure adapter overhead separately from engine execution"),
        ("issue 503 benchmark", "Determine whether a maintained LDBC implementation now exists"),
        ("issue 516 privilege", "Reproduce read-only graph DDL mutation concern on 2.17"),
        ("issue 628 sequence", "Reproduce parallel nextval concern under supported plans"),
        ("issue 731 VLE", "Turn report into minimal semantic oracle"),
        ("issue 777 path functions", "Validate nodes and relationships outputs"),
        ("issue 795 undirected VLE", "Validate directional symmetry"),
        ("issue 799 empty VLE", "Validate simple variable expansion result"),
        ("issue 803 optional collect", "Validate null and empty-list aggregation"),
        ("support SLA", "Obtain written response, patch and end-of-life terms"),
        ("pricing", "Obtain a quote with cores, data, replicas, environments and support"),
        ("security disclosure", "Locate advisories and coordinated disclosure policy"),
        ("SBOM", "Produce package and dependency inventory for every image"),
        ("development separation", "Prevent main-only property promotion from entering stable claims"),
        ("future release rebase", "Diff graph patches separately from upstream PostgreSQL churn"),
    ]
    d.cases("Evidence qualification program", mk_cases("evidence", items, "Fresh immutable environment and exact release artifacts", "S01-S08,S13-S14,S33-S49"))
    d.sources()
    d.write("01-product-lineage-releases-and-evidence.md")


def make_storage() -> None:
    d = Doc("AgensGraph source code, storage, indexes, and identifiers", "Pinned stable physical model, catalogs, tuple layout, access paths, amplification, limits, and 2.18-devel contrast")
    d.h(2, "Physical reconstruction")
    d.p("""
    A graph is not one opaque file or adjacency store. CREATE GRAPH creates a namespace and catalog entry. Base vertex and edge relations define graph element tuple shapes. Each concrete label is an inherited child relation. Endpoint graphids encode label identity, allowing relation/range pruning opportunities, but stable traversal still resolves relationships through label relations and their endpoint indexes.

    The stable vertex payload is `id graphid` plus `properties jsonb`; vertex labels receive a primary B-tree on id. The stable edge payload is `id graphid`, `start graphid`, `end graphid`, and `properties jsonb`. Each edge label automatically receives BRIN(id), B-tree(start,end), and B-tree(end,start). This is robust and queryable but creates at least three persistent index structures per edge label before user property indexes, with WAL and vacuum consequences.

    graphid packs a 16-bit label identifier over a 48-bit per-label sequence value. That provides fast label extraction and broad theoretical space, but capacity is bounded much earlier by bytes per tuple, page/index fan-out, relation size, WAL generation, checkpoint bandwidth, vacuum, backup time, filesystem and single-primary I/O.
    """)
    d.findings("Storage findings", CORE_FINDINGS + [
        ("Schema catalog", "ag_graph maps graph names to namespace OIDs; ag_label maps labels to graph, relation and label identifiers.", "S24,S32"),
        ("Inheritance", "Label hierarchy uses PostgreSQL relation inheritance, so parent scans may append across descendants.", "S24,S25"),
        ("Base labels", "ag_vertex and ag_edge act as graph base relations; concrete labels inherit their tuple contract.", "S21,S22,S24,S25"),
        ("ID allocation", "A sequence allocates the low graphid component per label while the label ID occupies high bits.", "S23-S25"),
        ("Endpoint locality", "start/end indexes group edges by endpoint key order, providing adjacency lookup without physically embedding edge arrays in a vertex.", "S22,S25"),
        ("Reverse traversal", "The reversed composite index prevents reverse hops from depending on the forward index's second column.", "S25"),
        ("Edge id BRIN", "BRIN compresses range summaries but false positives increase when heap order and graphid diverge.", "S20,S25"),
        ("Property storage", "JSONB provides flexible values but incurs key/type metadata, extraction and possible TOAST access.", "S21,S22,S27"),
        ("Property index", "Stable property indexes are expression indexes and duplicate extracted values into PostgreSQL index tuples.", "S02,S25"),
        ("Vector property", "2.17 permits an HNSW expression over a vector extracted/cast from properties when pgvector is installed.", "S02,S47"),
        ("Text property", "Full-text search materializes tsvector expressions into GIN indexes over property content.", "S02,S03"),
        ("Analyze cost", "Large endpoint statistics targets increase sample/catalog cost to improve estimates for skewed endpoints.", "S25"),
        ("Many-label tax", "Every edge label adds relations, indexes, statistics and planning alternatives even before it contains much data.", "Inference from S24,S25"),
        ("One-label constraint", "An element has one concrete label; multi-label modeling requires hierarchy, properties or extra graph structure.", "S09,S24,S25"),
        ("Referential invariant", "Edge endpoints are graphids, but safe graph mutation is enforced by graph executor logic rather than ordinary foreign keys on every edge tuple.", "S22,S30,S31"),
        ("Raw DML hazard", "Direct SQL writes can bypass endpoint and graph invariants, motivating the disabled superuser GUC.", "S31"),
        ("Delete fan-out", "Detaching a vertex must find incident edges across relevant edge labels; 2.17 prunes label work using endpoint label knowledge.", "S02,S30"),
        ("Hot adjacency cost", "A bounded hop is an index probe plus heap visibility/property work, not pointer chasing in a packed adjacency record.", "Inference from S22,S25"),
        ("Covering opportunity", "Endpoint composite indexes carry both endpoints but not JSONB properties; property projection may require heap fetches.", "S22,S25"),
        ("Write amplification", "An edge insert updates heap, WAL, visibility metadata and three automatic indexes, plus every property index and replica stream.", "S15-S18,S22,S25"),
        ("Sequence contention", "Per-label sequence allocation and WAL must be measured at high concurrent ingest; theoretical ID width says nothing about rate.", "S23,S41"),
        ("Relation ceiling", "PostgreSQL relation and tablespace constraints apply in addition to graphid limits.", "S04"),
        ("2.18 property promotion", "Development main can promote selected properties into typed relation columns and read them natively.", "S05"),
        ("Promotion migration", "Typed promotion adds DDL/catalog/backfill/index lifecycle complexity and is not a free read optimization.", "Inference from S05"),
        ("2.18 endpoint elision", "Development code can answer some labeled endpoint predicates from encoded graphid ranges without reading endpoint rows.", "S05"),
    ])
    items = [
        ("empty graph footprint", "Measure catalogs, base relations and sequences before user labels"),
        ("one vertex label footprint", "Measure relation and primary-index fixed cost"),
        ("one edge label footprint", "Measure heap plus three automatic index structures"),
        ("ten thousand labels", "Expose catalog, planning, relcache and file-count scaling"),
        ("label hierarchy depth", "Measure inherited scan planning and execution"),
        ("vertex bytes minimal", "Measure tiny id-only-equivalent JSONB object overhead"),
        ("vertex bytes wide", "Measure large heterogeneous property maps and TOAST"),
        ("edge bytes minimal", "Measure endpoint and automatic-index amplification"),
        ("edge bytes wide", "Measure JSONB/TOAST and property-index amplification"),
        ("graphid boundary", "Validate label and local-id packing at range boundaries"),
        ("sequence concurrency", "Measure allocation throughput, WAL and contention"),
        ("BRIN ordered load", "Measure pruning when heap order follows graphid"),
        ("BRIN randomized heap", "Measure false positives after churn and rewrite"),
        ("forward endpoint lookup", "Probe start,end index at uniform degree"),
        ("reverse endpoint lookup", "Probe end,start index at uniform degree"),
        ("endpoint-only projection", "Determine index-only scan and visibility-map dependence"),
        ("edge property projection", "Quantify heap and TOAST fetches after endpoint probe"),
        ("JSONB scalar predicate", "Measure extraction, casting and null/missing semantics"),
        ("B-tree property expression", "Measure selectivity and update amplification"),
        ("GIN JSONB property", "Measure containment index size and pending-list behavior"),
        ("GIN full-text expression", "Measure ranking, update and vacuum cost"),
        ("HNSW vector expression", "Measure build memory, recall, updates and graph traversal composition"),
        ("skew statistics", "Compare estimates at default and high endpoint statistics targets"),
        ("stale statistics", "Measure plan drift after bulk skew changes"),
        ("append descendants", "Inspect parent-label scans across many inherited children"),
        ("partition pruning", "Determine whether graphid label ranges avoid irrelevant relations"),
        ("unlabeled vertices", "Measure base relation behavior and access path"),
        ("label typo creation", "Validate accidental schema growth and permission controls"),
        ("edge insert amplification", "Count heap/index/WAL bytes per logical edge"),
        ("edge update amplification", "Separate HOT-eligible and indexed-property updates"),
        ("edge delete amplification", "Measure dead tuples, WAL and vacuum debt"),
        ("detach delete low labels", "Reproduce incident-edge deletion with a small label set"),
        ("detach delete many labels", "Measure 2.17 pruning versus label-wide work"),
        ("detach delete supernode", "Bound locks, WAL, latency and replica lag"),
        ("checkpoint pressure", "Measure tail latency during dirty-buffer flushing"),
        ("vacuum pressure", "Measure latency while reclaiming edge churn"),
        ("index bloat", "Track page density after random insert/delete cycles"),
        ("promotion candidate read", "Compare stable JSONB with 2.18-devel typed column in separate result tracks"),
        ("promotion write", "Charge dual representation and DDL lifecycle on development main"),
        ("endpoint elision", "Measure main-only read avoidance without contaminating stable score"),
        ("bytes per billion edges", "Project measured physical and replicated bytes with confidence ranges"),
        ("restore physical layout", "Verify catalogs, sequences and every automatic index after recovery"),
    ]
    d.cases("Storage qualification matrix", mk_cases("storage", items, "Generated graphs with controlled labels, degree, property width, order and churn on pinned storage", "S20-S25,S31-S35,S47", True))
    d.sources({f"S{i:02d}" for i in range(1, 36)} | {"S47"})
    d.write("02-source-storage-indexes-and-identifiers.md")


def make_query() -> None:
    d = Doc("AgensGraph Cypher, SQL, planner, and execution audit", "Query semantics and implementation from parse/lowering through scans, joins, VLE, shortest path, writes and hybrid operators")
    d.h(2, "Execution model")
    d.p("""
    AgensGraph extends PostgreSQL's grammar and analysis pipeline. Cypher clauses become PostgreSQL parse structures and planned relational operations where possible. Fixed patterns can therefore use ordinary relation scans, indexes, joins, selectivity estimates, parallelism and EXPLAIN infrastructure. Graph-specific executor nodes handle graph writes, variable-length edge walking and shortest-path state.

    This design is strongest when a pattern can be rooted by a selective vertex or property index, edge labels are known, endpoint statistics are fresh, and each expansion remains bounded. It is weakest when label inheritance multiplies alternatives, JSONB predicates lack expression indexes, variable-length paths explode, supernodes generate large intermediates, or estimates choose nested work with a much larger actual frontier.

    SQL/Cypher composition is not merely an adapter round trip: both surfaces share a backend transaction and plan tree. That is strategically useful for relational filters and graph expansion, but the benchmark must reveal materialization, correlated-subquery and type-conversion boundaries.
    """)
    d.findings("Query findings", CORE_FINDINGS + [
        ("Parser surface", "Cypher grammar and expression transformation are integrated into the PostgreSQL parser/analyzer tree.", "S26,S27"),
        ("Fixed pattern", "Fixed-length relationships lower toward scans and joins over vertex/edge label relations.", "S26"),
        ("Predicate pushdown", "Property and label predicates can become scan restrictions when expression shape and indexes permit.", "S25-S27"),
        ("Plan observability", "EXPLAIN/EXPLAIN ANALYZE, buffers, WAL and ordinary PostgreSQL statistics can expose graph plan cost.", "S04,S19"),
        ("VLE node", "Variable-length relationships have a dedicated executor maintaining traversal state rather than a pure static join expansion.", "S28"),
        ("VLE algorithm", "The stable executor uses depth-first traversal state and repeated relation access constrained by endpoints and depth.", "S28"),
        ("Path uniqueness", "Relationship/path reuse semantics require executor bookkeeping; memory scales with active paths/frontiers.", "S28"),
        ("Shortest path", "Shortest path uses a custom executor with hash tables and batching/spill-related state.", "S29"),
        ("Write nodes", "CREATE, MERGE, SET and DELETE use graph-specific executor code to preserve graph invariants.", "S30"),
        ("Eager boundaries", "Graph writes may require eager/materialized behavior so reads and writes observe intended clause semantics.", "S30,S33-S35"),
        ("Label selectivity", "Known relationship labels avoid searching unrelated edge relations; unknown or inherited labels can broaden the plan.", "S24-S26"),
        ("Endpoint selectivity", "Composite endpoint indexes support directed and reverse expansions but performance remains degree-sensitive.", "S22,S25"),
        ("JSONB semantics", "Missing keys, explicit nulls, heterogeneous scalar types and casts affect both results and index eligibility.", "S27"),
        ("Order semantics", "ORDER BY and projection interactions have received post-release fixes; order must be an explicit oracle.", "S05,S07"),
        ("Optional semantics", "OPTIONAL MATCH plus collect/null behavior is an active issue-report area.", "S46"),
        ("Union visibility", "Public reports question write visibility across UNION branches; reproduce before relying on it.", "S07"),
        ("VLE issue density", "Several reports target directed/undirected, empty and path-function VLE semantics, making differential coverage mandatory.", "S42-S45"),
        ("Main VLE memory", "2.18-devel includes explicit release of VLE-built memory and reduced array construction.", "S05"),
        ("Main column binding", "2.18-devel pushes promoted property comparisons and VLE constraints to native columns.", "S05"),
        ("Main endpoint elision", "2.18-devel can avoid reading a labeled endpoint when graphid range proves its label.", "S05"),
        ("Hybrid relational filter", "Cypher can appear in SQL FROM and SQL scalar results can constrain Cypher.", "S12"),
        ("Vector hybrid", "Vector candidate generation and graph expansion can execute in one query but candidate count/recall must be explicit.", "S02,S03,S47"),
        ("Text hybrid", "GIN candidate retrieval, ranking and graph traversal can be composed with shared SQL operators.", "S02,S03"),
        ("Plan cache", "Prepared plans can age poorly as label size and degree distributions change; generic/custom behavior needs testing.", "S04,S19"),
        ("Parallelism", "PostgreSQL parallel plan support does not imply every custom graph executor node is parallel-aware.", "S04"),
    ])
    items = [
        ("vertex id lookup", "Establish minimum graph lookup overhead"),
        ("vertex property indexed", "Measure expression-index predicate and heap access"),
        ("vertex property unindexed", "Expose label scan and JSONB extraction"),
        ("one-hop directed", "Measure forward endpoint expansion"),
        ("one-hop reverse", "Measure reverse endpoint expansion"),
        ("one-hop undirected", "Measure union/dedup and self-loop semantics"),
        ("two-hop chain", "Expose join order and intermediate cardinality"),
        ("three-hop selective root", "Measure stable bounded traversal"),
        ("three-hop late filter", "Expose intermediate explosion"),
        ("unknown edge label", "Measure append/search across edge labels"),
        ("parent edge label", "Measure inherited descendant scans"),
        ("supernode one-hop", "Measure degree-driven latency and memory"),
        ("supernode filtered edge", "Test predicate pushdown before materialization"),
        ("VLE zero length", "Validate identity path semantics"),
        ("VLE one to three", "Measure DFS work and uniqueness"),
        ("VLE unbounded", "Verify limits, timeout and admission"),
        ("VLE directed", "Validate direction and relationship uniqueness"),
        ("VLE undirected", "Validate symmetry and duplicate handling"),
        ("VLE multiple labels", "Measure scan-slot and constraint behavior"),
        ("VLE property predicate", "Validate property binding and pushdown"),
        ("VLE path projection", "Charge arrays/elements only when requested"),
        ("shortest path unweighted", "Measure custom executor frontier/hash state"),
        ("all shortest paths", "Expose result explosion and tie semantics"),
        ("weighted path", "Validate weight extraction, nulls and negative policy"),
        ("cycle graph", "Validate termination and relationship uniqueness"),
        ("self loops", "Validate fixed and variable path multiplicity"),
        ("parallel edges", "Validate identity and count semantics"),
        ("OPTIONAL MATCH empty", "Validate null row semantics"),
        ("OPTIONAL collect", "Reproduce issue-803 boundary"),
        ("UNION bag", "Validate deduplication, type and empty branch semantics"),
        ("UNION ALL write visibility", "Validate intra-statement observation"),
        ("IN empty list", "Validate false/null and plan behavior"),
        ("heterogeneous IN", "Validate JSONB type coercion and errors"),
        ("ORDER BY hidden expression", "Validate projection/order semantics"),
        ("aggregation path identity", "Validate grouping by graph element identity"),
        ("Cypher in SQL", "Measure one-plan hybrid execution"),
        ("SQL in Cypher", "Measure scalar-subquery correlation and cardinality errors"),
        ("relational prefilter", "Compare SQL-first versus Cypher-first plan shapes"),
        ("vector then graph", "Measure HNSW recall/latency plus traversal"),
        ("text then graph", "Measure GIN candidates, ranking and traversal"),
        ("hybrid RRF then graph", "Measure dual ranking fusion and graph expansion"),
        ("prepared generic plan", "Expose skew sensitivity after repeated execution"),
        ("stale statistics plan", "Measure misestimation and tail amplification"),
        ("cold plan cache", "Separate parse/plan from execution"),
        ("JIT off and on", "Report compile threshold and steady benefit"),
        ("parallel plan", "Identify graph nodes that block or benefit from workers"),
        ("timeout cancellation", "Verify prompt cleanup of VLE and shortest-path memory"),
        ("EXPLAIN fidelity", "Compare estimated/actual rows and buffer/WAL counters"),
    ]
    d.cases("Query and semantic matrix", mk_cases("query", items, "Controlled graph families: chain, tree, cycle, clique, power-law, multi-label, mixed relational/graph and vector/text", "S09,S12,S19,S22,S25-S30,S33-S35,S42-S47"))
    d.sources({f"S{i:02d}" for i in range(1, 48)})
    d.write("03-cypher-sql-planner-and-execution.md")


def make_correctness() -> None:
    d = Doc("AgensGraph transactions, correctness, concurrency, and security", "MVCC/isolation, mutation invariants, conflicts, recovery, privileges and issue-driven semantic qualification")
    d.h(2, "Correctness contract")
    d.p("""
    The stable engine inherits PostgreSQL transaction snapshots, locks, WAL and recovery, while graph-specific executor paths are responsible for cross-relation graph invariants. This is stronger than an eventually consistent graph service but creates a sharp safety boundary: direct SQL DML against label relations is disabled by default because ordinary row operations can bypass graph-aware endpoint and mutation checks.

    Snapshot isolation does not by itself prove graph serializability. Concurrent MERGE, SET, detach delete and endpoint creation can interact across vertex relations, edge relations, property expression indexes, triggers and uniqueness constraints. Every claimed invariant requires a race test at each supported isolation level and after abort/crash recovery.

    Security also spans two layers. PostgreSQL authentication, roles, schemas, RLS, TLS and auditing primitives are available, but graph DDL and custom executor nodes must call the correct privilege hooks and respect row-level policies. Historical fixes and open reports justify explicit least-privilege regression rather than inheritance assumptions.
    """)
    d.findings("Correctness findings", CORE_FINDINGS + [
        ("Autocommit", "A standalone graph statement commits or aborts through ordinary PostgreSQL transaction control.", "S04,S17"),
        ("Multi-statement", "SQL and Cypher changes may share an explicit transaction and snapshot.", "S12,S17"),
        ("Isolation levels", "Read committed, repeatable read and serializable behavior derives from PostgreSQL but graph executor access patterns determine conflicts.", "S17,S30"),
        ("Atomic edge create", "Graph-aware execution must coordinate endpoint validation and edge insertion in the same transaction.", "S30"),
        ("Detach delete", "Deleting a vertex and incident edges spans relations and can lock/write many tuples.", "S02,S30"),
        ("MERGE", "Graph MERGE has dedicated execution and has received crash/correctness fixes historically; uniqueness is schema-dependent.", "S30,S33-S35"),
        ("SET", "Graph SET updates JSONB/property state through a custom executor and must recheck concurrently changed rows.", "S05,S30"),
        ("Eager execution", "Write/read clause ordering needs eager boundaries to prevent Halloween-style reprocessing or visibility mistakes.", "S30,S33-S35"),
        ("Raw DML off", "enable_graph_dml defaults false and is superuser-settable, intentionally fencing unsafe relational writes.", "S31"),
        ("Crash durability", "Committed graph heap and index changes are WAL-protected through PostgreSQL; restore still needs graph-catalog validation.", "S16,S17,S24-S25"),
        ("Sequence gaps", "Aborts may consume sequence values; graphid continuity must never be a correctness assumption.", "S23"),
        ("Constraint coverage", "Unique, mandatory/check and property indexes operate through relational mechanisms adapted to graph labels.", "S02,S03,S25"),
        ("Inheritance constraint", "Constraint and uniqueness scope across parent/descendant labels must be tested; inheritance semantics can surprise SQL users.", "S24,S25"),
        ("RLS", "2.16 explicitly added/fixed row-level security behavior for Cypher, so current coverage matters.", "S14"),
        ("Privilege report", "Issue 516 is a lead that read-only roles may alter/remove graph objects; no current conclusion without reproduction.", "S40"),
        ("DDL ownership", "Development main includes ownership/DDL gates, indicating this surface remains actively hardened.", "S05"),
        ("Trigger interaction", "Development fixes re-examine rows modified by before-row triggers, a concurrency/correctness boundary.", "S05"),
        ("Concurrent SET", "Development main adds row re-examination before graph SET writes, separating stable confidence from future fixes.", "S05"),
        ("Concurrent delete", "Development main reports a concurrent delete during graph write as a conflict.", "S05"),
        ("Property shape", "Development main rejects scalar replacement of a property map and strengthens promoted-column shape checks.", "S05"),
        ("Optional aggregation", "Issue 803 raises `[null]` versus empty-list behavior; oracle must state the chosen language version.", "S46"),
        ("VLE correctness", "Recent VLE reports span missing rows, directional asymmetry, constraint binding and path functions.", "S42-S45"),
        ("Upgrade correctness", "pg_upgrade must preserve graph catalogs, label IDs, sequences, relation inheritance and expression indexes.", "S13,S24-S25"),
        ("Replication visibility", "Asynchronous standbys can serve stale reads; synchronous commit adds latency and still needs routing/failover policy.", "S15"),
        ("Logical replication unknown", "Graph safety over table-level logical replication is not established by generic PostgreSQL availability.", "S15,inference"),
    ])
    items = [
        ("edge endpoint existence", "Reject or define edges whose start/end vertex is missing"),
        ("cross-graph endpoint", "Reject an edge pointing into another graph"),
        ("concurrent endpoint delete", "Race edge creation against vertex deletion"),
        ("detach delete atomicity", "Ensure no committed orphan edges remain"),
        ("detach delete abort", "Restore every vertex/edge after transaction abort"),
        ("detach delete crash", "Recover an all-or-nothing graph state"),
        ("concurrent detach same vertex", "Classify conflicts and final state"),
        ("concurrent SET same key", "Measure lost-update and serialization behavior"),
        ("concurrent SET different keys", "Validate JSONB merge versus row conflict semantics"),
        ("MERGE same vertex", "Validate uniqueness and duplicate creation under race"),
        ("MERGE same edge", "Validate relationship identity under race"),
        ("MERGE crash", "Validate WAL recovery across matched/create branches"),
        ("CREATE then MATCH transaction", "Validate read-your-write semantics"),
        ("DELETE then MATCH transaction", "Validate clause and statement visibility"),
        ("UNION write visibility", "Reproduce report with explicit expected state"),
        ("read committed phantoms", "Observe graph growth across statements"),
        ("repeatable read graph", "Preserve snapshot across labels and edges"),
        ("serializable write skew", "Force graph invariant conflict across relations"),
        ("deadlock two paths", "Verify detection, victim rollback and retry safety"),
        ("statement timeout write", "Ensure partial graph mutation is rolled back"),
        ("client disconnect write", "Ensure backend abort and cleanup"),
        ("backend kill before WAL flush", "Classify committed and uncommitted state"),
        ("primary crash after commit", "Verify durable graph and index consistency"),
        ("async failover", "Measure acknowledged transaction loss window"),
        ("sync failover", "Measure commit latency and zero-loss assumptions"),
        ("replica stale graph", "Verify endpoint/edge snapshot consistency on standby"),
        ("sequence gap", "Ensure gaps do not break label/range logic"),
        ("sequence parallelism", "Reproduce issue-628 lead"),
        ("unique property race", "Validate expression-index constraint"),
        ("mandatory property", "Validate create, set-null and remove behavior"),
        ("check constraint", "Validate JSONB cast/error/null behavior"),
        ("parent-label uniqueness", "Define uniqueness across descendants"),
        ("direct DML default", "Prove unsafe SQL mutation is denied"),
        ("direct DML superuser", "Demonstrate corruption modes in disposable environment"),
        ("read-only role MATCH", "Allow intended graph reads"),
        ("read-only role DDL", "Reproduce issue-516 lead"),
        ("schema owner graph DDL", "Validate ownership and grants"),
        ("RLS vertex", "Hide forbidden vertices in Cypher"),
        ("RLS edge", "Prevent edge/path leakage through counts or existence"),
        ("RLS hybrid", "Preserve policy through SQL/Cypher composition"),
        ("security definer", "Validate role context in graph functions"),
        ("malicious property expression", "Validate casts, errors and index expression safety"),
        ("backup concurrent writes", "Recover a consistent graph snapshot"),
        ("PITR before graph DDL", "Recover catalogs and data to target"),
        ("PITR during detach", "Recover atomic state at WAL boundary"),
        ("pg_upgrade graph", "Validate labels, IDs, paths and indexes"),
        ("optional collect semantics", "Reproduce issue-803 lead"),
        ("VLE missing rows", "Reproduce issue-799 lead"),
        ("undirected symmetry", "Reproduce issue-795 lead"),
        ("path function identity", "Reproduce issue-777 lead"),
    ]
    d.cases("Transaction, race, and security matrix", mk_cases("correctness", items, "Pinned stable cluster with deterministic barriers, fault injection, primary/standby topology and independent graph invariant checker", "S13-S17,S23-S25,S30-S35,S40-S46", True))
    d.sources({f"S{i:02d}" for i in range(1, 47)})
    d.write("04-transactions-correctness-concurrency-and-security.md")


def make_ops() -> None:
    d = Doc("AgensGraph operations, distribution, resources, S3, and cost", "Deployment and capacity truth: process/memory/I/O, vacuum, replication, recovery, PB projection, object storage and fixed-budget fit")
    d.h(2, "Operational verdict")
    d.p("""
    Operationally, AgensGraph is PostgreSQL with a graph-aware fork. That is a major maturity advantage for WAL recovery, base backup, monitoring and administrators, but it also fixes the topology: a database cluster has one writable primary unless an external distributed system is introduced. Standbys replicate the whole write stream and can serve read-only traffic. They do not divide a trillion-edge graph into independently writable ownership ranges.

    Memory is not only shared_buffers. Count one backend process per active connection, private executor state, work_mem per eligible plan node, maintenance memory, WAL buffers, kernel page cache, extension memory, autovacuum workers and replica replay. VLE and shortest-path work can amplify private memory or spill. A pooler controls connection count but does not eliminate query-state cost.

    S3 is suitable for retained base backups, WAL archives and exported datasets through external tooling. The online engine still expects PostgreSQL relation/index pages on a filesystem/block device. Replacing that layer with object-store demand paging is a new storage engine design, not a configuration setting. Therefore a fixed-cost claim must be phrased as an enforced resource budget with admission control; AgensGraph itself is provisioned capacity plus storage, replication and operations.
    """)
    d.findings("Operations findings", CORE_FINDINGS + [
        ("Server processes", "A postmaster accepts sessions and forks backend processes; background writer, checkpointer, WAL writer and autovacuum processes remain.", "S11,S18"),
        ("Connection cost", "Thousands of direct sessions imply process and private-memory overhead; PgBouncer-like pooling is external.", "S11,S18"),
        ("Shared buffers", "Vendor guidance recommends roughly half RAM and even data-size caching, but upstream guidance is more conservative and workload-dependent.", "S10,S18"),
        ("work_mem multiplier", "work_mem can be consumed by multiple sorts/hashes per query and by many concurrent backends.", "S18"),
        ("Graph private memory", "VLE/path nodes allocate traversal and hash state in addition to ordinary plan nodes.", "S28,S29"),
        ("Temp spill", "Sorts, hashes and graph path state can drive temp files and latency when memory is bounded.", "S18,S28,S29"),
        ("Double caching", "PostgreSQL shared buffers coexist with the OS page cache; charge both in resident resource accounting.", "S18"),
        ("Planner knob risk", "random_page_cost 0.005 assumes fully cached random access and can force bad nested/index plans when cache assumptions fail.", "S10,S19"),
        ("Autovacuum", "Edge churn creates dead heap and index tuples requiring analyze/vacuum bandwidth.", "S04,S18"),
        ("Checkpoint tails", "Dirty-page and WAL checkpoint behavior can affect p99.9 write/read latency.", "S04,S18"),
        ("Replication", "Physical streaming replication provides active/standby HA and read replicas, synchronous or asynchronous.", "S15,S50"),
        ("Failover control", "Core primitives do not by themselves provide consensus leader election, fencing, routing or an SLA.", "S15"),
        ("Write scaling", "Replicas replay writes and do not raise primary write capacity.", "S15"),
        ("Read scaling", "Hot standbys can scale stale/read-only workloads subject to replay conflicts and full-copy cost.", "S15"),
        ("Sharding absent", "No source-level graph partition map, distributed planner, remote traversal operator or cross-shard transaction coordinator was found.", "S04"),
        ("Citus caution", "A PostgreSQL sharding extension cannot be assumed compatible with inherited graph label tables or custom graph executors.", "Inference; qualification required"),
        ("Backup", "pg_basebackup, WAL archiving and PITR are available; 2.17 inherits incremental backup/combine tooling.", "S01,S02,S16"),
        ("S3 archive", "External archive commands/tools can place WAL/base backups in S3; object store is outside the online buffer manager.", "S16"),
        ("Restore time", "PB restore and WAL replay can dominate recovery even if S3 storage is cheap.", "Inference from S16"),
        ("Index replication cost", "Physical replicas copy heap and all automatic/property index changes.", "S15,S22,S25"),
        ("PB addressability", "PostgreSQL physical limits, relation management, backup and maintenance must be demonstrated before graphid space matters.", "S04,S23"),
        ("Trillion-edge bytes", "Three automatic edge indexes, heap tuple headers, JSONB, WAL and replicas make logical property bytes a poor capacity estimator.", "S22,S25"),
        ("Cost unknown", "No public fixed production price or scale SLA was found; open source removes license fee but not infrastructure/operations cost.", "S01-S06"),
        ("Fork maintenance", "Security patches and extension compatibility arrive through the AgensGraph rebase cadence rather than stock PostgreSQL packages.", "S01,S04,S14"),
        ("Low-resource fit", "It can be efficient for moderate hybrid workloads, but process, indexes and maintenance are structurally heavier than a compact embedded read engine.", "Inference from S11,S18,S22,S25"),
    ])
    items = [
        ("idle connection floor", "Measure backend RSS/PSS per idle direct session"),
        ("pooler floor", "Measure total cost with bounded server backends"),
        ("shared buffer sweep", "Find latency/throughput versus memory curve"),
        ("work_mem sweep", "Find spill versus OOM/concurrency curve"),
        ("OS cache accounting", "Report cgroup and host cache consistently"),
        ("VLE memory cap", "Bound private traversal state under concurrency"),
        ("shortest-path spill", "Measure hash batches and temp bytes"),
        ("mixed query memory", "Expose per-node work_mem multiplication"),
        ("autovacuum steady churn", "Hold dead-tuple debt stable under writes"),
        ("vacuum burst", "Measure foreground tails during catch-up"),
        ("analyze large endpoints", "Charge high statistics targets"),
        ("checkpoint", "Measure p99.9 around flush events"),
        ("WAL saturation", "Find primary and replica bandwidth ceilings"),
        ("replication one async", "Measure lag and read staleness"),
        ("replication one sync", "Measure commit latency and durability"),
        ("replication three", "Charge network, disk and replay resources"),
        ("read replica scale", "Measure read-only scaling and replay conflicts"),
        ("planned switchover", "Measure routing downtime and transaction outcome"),
        ("unplanned failover", "Measure detection, fencing, RPO and RTO"),
        ("split brain", "Prove external fencing prevents dual primary"),
        ("replica rebuild", "Measure network/time while serving load"),
        ("base backup full", "Measure duration, bytes and foreground impact"),
        ("base backup incremental", "Measure 2.17 inherited delta workflow"),
        ("WAL archive S3", "Measure archive lag, requests and cost"),
        ("PITR from S3", "Measure download, replay, correctness and RTO"),
        ("backup retention", "Model storage growth and lifecycle policy"),
        ("PB full restore projection", "Project from measured throughput with bottleneck bounds"),
        ("relation file count", "Measure many labels/tables/indexes operationally"),
        ("inode and catalog pressure", "Track schema growth at high label counts"),
        ("monitoring", "Capture pg_stat, graph plans, locks, WAL and OS telemetry"),
        ("log volume", "Charge slow-query and audit logging"),
        ("TLS", "Measure connection and steady query overhead"),
        ("rolling minor patch", "Determine downtime and replica compatibility"),
        ("major pg_upgrade", "Measure disk headroom and service window"),
        ("extension upgrade", "Qualify pgvector/PostGIS ABI and data"),
        ("single-node maximum", "Find CPU, memory, IOPS and relation-size ceiling"),
        ("one billion edge", "Measure bytes, load, maintenance and restore"),
        ("ten billion edge", "Validate projections and label/index behavior"),
        ("trillion edge projection", "Publish measured extrapolation uncertainty"),
        ("PB projection", "Include heap, all indexes, WAL, replicas and backups"),
        ("object-store eviction", "Demonstrate that vanilla stable cannot serve evicted online pages from S3"),
        ("NVMe replacement", "Measure live storage cost and failure behavior"),
        ("fixed budget admission", "Cap cores/RAM/IOPS and expose overload"),
        ("tenant isolation", "Measure noisy neighbor and per-role limits"),
        ("TCO one year", "Charge hardware/cloud, replicas, backup, egress and labor"),
        ("TCO three years", "Include upgrades, growth and disaster recovery"),
    ]
    d.cases("Operations and cost matrix", mk_cases("operations", items, "Production-like Linux primary/standby cluster with cgroup limits, deterministic block storage and metered object storage", "S10-S20,S22-S25,S28-S29,S48-S50", True))
    d.sources({f"S{i:02d}" for i in range(1, 36)} | {"S47","S48","S49","S50"})
    d.write("05-operations-distribution-resources-s3-and-cost.md")


def make_benchmark() -> None:
    d = Doc("AgensGraph benchmark audit and 10x qualification", "What is and is not publicly proven, and the preregistered benchmark required for defensible latency/resource/scale/competitor claims")
    d.h(2, "Evidence verdict")
    d.p("""
    No current, reproducible, independently audited AgensGraph result was found that proves PB scale, a trillion edges, or a tenfold win over all popular engines. The 2.17 release's approximately 30x DELETE/DETACH DELETE statement is useful evidence of one algorithmic correction: avoid sequentially inspecting every edge label when deleting a highly connected vertex. It is not a cross-engine result, does not cover reads, and gives neither a public harness nor confidence intervals.

    A universal 10x statement is scientifically implausible without a declared metric and workload class. An embedded engine can win single-process analytics; an in-memory matrix engine can win shallow pattern throughput; a distributed service can win capacity and availability; a mature transactional server can win correctness and mixed SQL. The project should claim only cells in which it wins under equal semantics and total resource accounting.

    The benchmark below therefore separates hot and cold, point and scan, fixed and variable traversal, reads and writes, steady state and recovery, and scale-up versus scale-out. It includes AgensGraph stable, not development main, and pins every competitor version. A 10x ratio must hold at a declared percentile or cost-normalized metric with confidence bounds and no correctness failures.
    """)
    d.findings("Benchmark findings", CORE_FINDINGS + [
        ("No official LDBC result", "No maintained AgensGraph implementation/result was found in the audited current LDBC/GDC sources.", "S37-S39"),
        ("Open benchmark request", "Issue 503 explicitly requests LDBC benchmark support, reinforcing the evidence gap.", "S39"),
        ("Delete comparison", "The 2.17 30x figure compares old and new AgensGraph behavior in internal tests.", "S02"),
        ("Mechanism credible", "Source architecture supports the stated mechanism: pruning incident-edge work by associated labels and endpoint ranges.", "S22-S25,S30"),
        ("Magnitude unverified", "No raw samples, hardware, dataset generator, scripts or old/new commit matrix accompanies the release note.", "S02"),
        ("PostgreSQL benchmark caution", "TPC-style relational performance cannot substitute for graph traversal evidence.", "S04"),
        ("AI demo caution", "GraphRAG adapter/demo latency mixes embeddings, retrieval and LLM work and cannot establish engine latency.", "S02,S03"),
        ("Correctness prerequisite", "A faster cell with wrong bags, nulls, path identity or durability loses before latency comparison.", "S33-S46"),
        ("Warm-cache disclosure", "shared_buffers/page cache can turn a storage test into a memory test; residency must be measured.", "S10,S18"),
        ("Resource disclosure", "Charge backend processes, OS cache, indexes, replicas, poolers and benchmark clients.", "S11,S15,S18,S22,S25"),
        ("Write disclosure", "Report WAL durability, synchronous_commit, checkpoints and replica mode.", "S15-S18"),
        ("Scale disclosure", "A graphid address range is not a loaded dataset result.", "S23"),
        ("Data-shape disclosure", "Uniform, power-law, temporal, community and adversarial graphs exercise different operators.", "Benchmark design requirement"),
        ("Query disclosure", "Publish exact Cypher/SQL and plans; syntactically similar queries may not have equal semantics.", "S26-S29"),
        ("Parameter disclosure", "Depth, selectivity, result cap, order and timeout are part of the operation definition.", "Benchmark design requirement"),
        ("Tail disclosure", "p50 cannot support very-low-latency claims when p99.9 collapses under vacuum/checkpoint/skew.", "Benchmark design requirement"),
        ("Failure disclosure", "Failover throughput must include errors, retries, duplicates and stale reads.", "S15"),
        ("Cost disclosure", "Throughput per dollar requires a dated price sheet and all provisioned replicas/storage.", "Benchmark design requirement"),
        ("10x aggregation", "Do not average ratios across queries; report per-cell ratios and geometric summaries only as secondary views.", "Benchmark methodology"),
        ("Statistical rule", "Use repeated independent trials, bootstrap confidence intervals and preregistered outlier policy.", "Benchmark methodology"),
        ("Load rule", "Measure load rate, write amplification, post-load analyze/index time and database-ready time separately.", "S18,S25"),
        ("Steady-state rule", "A run begins only after caches, vacuum debt, replica lag and checkpoint cycle meet declared conditions.", "S15,S18"),
        ("Comparable durability", "fsync, full_page_writes, synchronous replicas and acknowledgement semantics must match intended guarantees.", "S15-S18"),
        ("Client saturation", "Use open-loop offered load for latency curves and identify coordinated omission.", "Benchmark methodology"),
        ("Independent replay", "Raw request/response and final-state digests must be replayable by a third party.", "Benchmark methodology"),
    ])
    items = [
        ("load vertices", "Measure accepted and durable vertex ingestion"),
        ("load edges", "Measure accepted and durable edge ingestion with indexes"),
        ("database-ready time", "Include index build, analyze, checkpoint and compaction-equivalent work"),
        ("bytes per vertex", "Measure heap/index/WAL/replica footprint"),
        ("bytes per edge", "Measure three automatic indexes and properties"),
        ("hot id lookup", "Compare minimum serving latency"),
        ("cold id lookup", "Compare storage miss path"),
        ("hot indexed property", "Compare selective secondary lookup"),
        ("cold indexed property", "Compare index and heap misses"),
        ("unindexed scan", "Expose scan engines without confusing it with traversal"),
        ("one-hop degree 1", "Measure constant-small adjacency"),
        ("one-hop degree 16", "Measure common bounded fan-out"),
        ("one-hop degree 1K", "Measure wide fan-out"),
        ("one-hop degree 1M", "Measure supernode behavior"),
        ("reverse hop", "Ensure reverse index/layout fairness"),
        ("two-hop selective", "Compare optimizer and adjacency locality"),
        ("three-hop selective", "Measure bounded interactive traversal"),
        ("three-hop late filter", "Measure intermediate explosion"),
        ("VLE depth 1-3", "Compare variable traversal machinery"),
        ("VLE depth 1-8", "Expose path growth and admission"),
        ("shortest path", "Compare exact unweighted semantics"),
        ("all shortest paths", "Compare ties and result amplification"),
        ("triangle count local", "Compare repeated neighborhood intersection"),
        ("hybrid relational graph", "Measure AgensGraph's genuine co-location strength"),
        ("vector graph", "Compare equal vector recall plus graph semantics"),
        ("text graph", "Compare equal analyzer/ranking plus traversal"),
        ("point insert", "Measure durable small mutation"),
        ("edge insert", "Measure endpoint and index write amplification"),
        ("property update", "Measure JSONB/index and MVCC cost"),
        ("edge delete", "Measure dead tuples and WAL"),
        ("detach degree 16", "Reproduce ordinary delete"),
        ("detach degree 1M", "Qualify the release's high-connectivity claim"),
        ("MERGE contention", "Compare atomic idempotent upsert behavior"),
        ("mixed 95R5W", "Measure interactive steady state"),
        ("mixed 50R50W", "Measure write-heavy steady state"),
        ("checkpoint window", "Compare tail under persistence work"),
        ("maintenance window", "Compare vacuum/compaction tail"),
        ("memory 16GiB", "Compare constrained footprint and throughput"),
        ("memory 64GiB", "Build latency-resource curve"),
        ("memory 256GiB", "Identify diminishing returns"),
        ("one node", "Compare scale-up baseline"),
        ("three nodes HA", "Compare availability cost, not sharding"),
        ("three shards proposed", "Compare actual horizontal partitioning in zu"),
        ("network partition", "Compare availability, errors and correctness"),
        ("primary failover", "Compare RPO/RTO and tail"),
        ("restart warm", "Measure recovery and cache preservation"),
        ("restart cold", "Measure WAL replay and cache refill"),
        ("backup foreground", "Measure protection overhead"),
        ("restore", "Compare RTO and verified graph state"),
        ("100M edges", "Validate harness and correctness"),
        ("1B edges", "Measure full resource behavior"),
        ("10B edges", "Validate scaling curve"),
        ("100B edges", "Require distributed capacity for target candidates"),
        ("1T edges", "Target qualification with no extrapolated pass"),
        ("1PB logical", "Target qualification with online query and recovery"),
        ("cost-normalized", "Report correct operations per dollar at SLO"),
        ("resource-normalized", "Report correct operations per core/GiB/IOPS"),
        ("10x latency", "Require ratio confidence bound above ten for declared cell"),
        ("10x cost", "Require equal SLO/durability and full TCO"),
        ("10x composite", "Reject a composite that hides losing critical cells"),
    ]
    d.cases("Preregistered benchmark cells", mk_cases("benchmark", items, "Same dataset bytes and semantics; immutable versions; equivalent durability; isolated clients; metered total infrastructure", "S02,S10-S12,S15-S19,S22-S30,S33-S39"))
    d.h(2, "Competitor matrix")
    competitors = [
        ("Neo4j", "native transactional property graph", "Cypher semantics and mature planner"),
        ("FalkorDB", "Redis/module sparse-matrix graph", "shallow traversal throughput and memory"),
        ("LadybugDB", "embedded columnar graph", "analytical joins and compact local execution"),
        ("Kuzu", "historical embedded predecessor", "published historical baselines only"),
        ("PuppyGraph", "lakehouse graph compute", "object-storage data and elastic analytics"),
        ("Aerospike Graph", "distributed KV-backed Gremlin", "partitioned online capacity and service resources"),
        ("TigerGraph", "distributed native graph", "scale-out traversal and commercial boundary"),
        ("NebulaGraph", "shared-nothing graph", "partition routing and distributed traversal"),
        ("JanusGraph", "distributed graph over storage backends", "Gremlin semantics and operational stack"),
        ("Apache AGE", "PostgreSQL extension", "fork-versus-extension integration tradeoff"),
        ("Memgraph", "in-memory transactional graph", "hot latency and streaming"),
        ("Dgraph", "distributed predicate graph", "write distribution and query semantics"),
        ("Amazon Neptune", "managed graph service", "HA/operations and cloud price"),
        ("ArangoDB", "distributed multi-model", "hybrid model and shard behavior"),
    ]
    d.table(["Engine", "Class", "Why it must remain a separate comparison track"], [list(x) for x in competitors])
    d.sources()
    d.write("06-benchmark-audit-and-10x-qualification.md")


def make_design() -> None:
    d = Doc("AgensGraph design lessons and proposed PB/S3 architecture", "What to adopt, what to avoid, and concrete low-latency/fixed-budget/distributed/object-store design responses")
    d.h(2, "Design response")
    d.p("""
    AgensGraph demonstrates that graph syntax can be lowered into a mature relational optimizer and that graph writes benefit from full database transaction machinery. The proposed engine should retain those principles: one typed logical algebra, explicit graph identity, costed access paths, snapshot isolation, explainability and differential semantic tests. It should not clone AgensGraph's physical topology if the objective is PB/trillion-edge S3 authority.

    The proposed architecture separates immutable authoritative graph segments in S3 from bounded local/NVMe caches, a small strongly consistent metadata/manifest plane, stateless query workers, and partition-aware traversal. Vertices and adjacency are sorted into independently fetchable blocks by stable ownership keys. Properties use typed column groups and late materialization. Updates enter a replicated write-ahead delta tier, then compact into immutable S3 generations. Every query declares budgets for remote bytes, frontier size, CPU and result count; admission and continuation tokens make cost fixed and failure explicit.

    Very low latency comes from keeping hot routing, manifests, small indexes and popular adjacency blocks in RAM/NVMe, issuing asynchronous range reads for cold blocks, grouping frontier work by partition/object, and avoiding global coordination for snapshot reads. Distribution is ownership-based, with explicit cross-partition messages and consistent-hash/virtual shard movement. The architecture cannot promise 10x universally; it can target tenfold wins in cold-cost-normalized queries, bytes per edge, scale-out ingest and S3-backed capacity while acknowledging local in-memory competitors may win tiny hot graphs.
    """)
    d.findings("Adopt, adapt, and avoid", CORE_FINDINGS + [
        ("Adopt one algebra", "Lower Cypher/GQL and APIs into one typed logical plan instead of maintaining independent semantics.", "Lesson from S26,S27"),
        ("Adopt explainability", "Expose partitions, remote bytes, cache status, frontier estimates and spill in every physical plan.", "Adaptation of PostgreSQL EXPLAIN"),
        ("Adopt MVCC", "Use immutable generations plus snapshot manifests and transactional deltas for repeatable reads.", "Lesson from S17"),
        ("Adopt typed indexes", "Promote hot properties to typed columns/indexes based on workload evidence, echoing 2.18-devel direction.", "S05"),
        ("Adopt bidirectionality selectively", "Maintain reverse adjacency only for edge types whose query workload justifies doubled bytes.", "Contrast with S25"),
        ("Adopt statistics", "Track degree sketches, property selectivity, block min/max and cache residency per generation.", "Lesson from S19,S25"),
        ("Adopt regression discipline", "Turn every public semantic issue into cross-engine generative and metamorphic tests.", "S33-S46"),
        ("Avoid relation per label", "Use label dictionaries/partition metadata without one heap and three indexes per label.", "Contrast with S24,S25"),
        ("Avoid JSONB hot path", "Use typed column groups for hot predicates and a sparse overflow map for cold properties.", "Contrast with S21,S22,S27"),
        ("Avoid unconditional indexes", "Do not pay forward, reverse and ID indexes for every edge type by default.", "Contrast with S25"),
        ("Avoid single primary", "Partition write ownership and transaction coordination so aggregate capacity grows with shards.", "Contrast with S15"),
        ("Avoid process per session", "Use asynchronous multiplexed workers and bounded arenas.", "Contrast with S11,S18"),
        ("Avoid opaque memory", "Reserve per-query/frontier budgets and spill deterministic structures.", "Lesson from S18,S28,S29"),
        ("Avoid local authority", "Make S3 generation manifests the durable source of truth, not backup copies of block volumes.", "Contrast with S16"),
        ("Avoid full-copy replicas", "Erasure-code/replicate immutable objects and replicate only hot cache/delta state as required.", "Contrast with S15"),
        ("Avoid unlimited VLE", "Require depth, path/result, remote-byte and CPU budgets with resumable partial execution.", "Lesson from S28"),
        ("Segment layout", "Store adjacency in endpoint-sorted compressed blocks with offsets, label/type metadata and optional reverse blocks.", "Proposed design"),
        ("Property layout", "Store typed property columns separately so adjacency-only traversals do not read payloads.", "Proposed design"),
        ("Snapshot manifest", "Atomically publish immutable object generations through a compact consensus metadata plane.", "Proposed design"),
        ("Delta tier", "Replicate recent mutations synchronously in bounded logs/memtables, then compact to S3.", "Proposed design"),
        ("Read path", "Resolve snapshot and partition, check RAM/NVMe, range-read S3 block, decode only needed columns, batch next frontier.", "Proposed design"),
        ("Cache policy", "Pin manifests/routing and cost-aware hot blocks; never require all graph data in DRAM.", "Proposed design"),
        ("Partition policy", "Use many virtual shards and locality-aware placement; expose cross-shard edges explicitly.", "Proposed design"),
        ("Transaction scope", "Fast single-shard commits; explicit two-phase/consensus path for cross-shard invariants; no hidden weakening.", "Proposed design"),
        ("Fixed cost", "Cap workers, cache, object requests and background compaction; overload returns queue/retry instead of autoscaling invisibly.", "Proposed design"),
        ("PB recovery", "Recover metadata and warm caches from immutable objects without reconstructing one monolithic local volume.", "Proposed design"),
        ("10x target", "Predeclare cells: storage bytes/edge, cold correct queries per dollar, scale-out ingest and restore readiness.", "Proposed design"),
        ("Non-target", "Do not promise 10x against an embedded in-memory engine for a tiny fully cached graph.", "Honest claim boundary"),
        ("Migration", "Bulk-read AgensGraph label tables under a consistent snapshot, map graphids/labels, validate counts and path hashes, then dual-read.", "Proposed migration"),
        ("Compatibility", "Offer Cypher subset with an explicit conformance manifest and reject unsupported clauses predictably.", "Proposed design"),
    ])
    items = [
        ("immutable adjacency block", "Prototype endpoint-sorted compressed block format"),
        ("forward-only edge type", "Measure bytes saved where reverse traversal is absent"),
        ("optional reverse block", "Measure reverse latency and write amplification"),
        ("typed property column", "Compare against JSONB extraction and expression index"),
        ("sparse overflow map", "Preserve schema flexibility without taxing hot columns"),
        ("graph identity", "Encode stable vertex/edge IDs independent of physical generation"),
        ("label dictionary", "Support many labels without per-label files/indexes"),
        ("manifest consensus", "Publish atomic snapshots with small metadata quorum"),
        ("delta single shard", "Commit low-latency mutations with explicit durability"),
        ("delta cross shard", "Measure coordination and abort semantics"),
        ("delta compaction", "Bound write amplification and S3 request cost"),
        ("snapshot read", "Read a stable generation while compaction publishes next"),
        ("read your write", "Overlay session/transaction deltas correctly"),
        ("RAM cache hit", "Establish hot lower bound"),
        ("NVMe cache hit", "Establish warm lower bound"),
        ("S3 range miss", "Measure cold request and bytes"),
        ("coalesced frontier fetch", "Group edges by object and partition"),
        ("prefetch", "Predict next blocks without excess remote bytes"),
        ("cache admission", "Reject scans that would evict interactive hot data"),
        ("cache eviction", "Maintain bounded memory under mixed tenants"),
        ("one-hop S3", "Meet cold latency with one/few range requests"),
        ("three-hop S3", "Batch frontiers and bound sequential remote rounds"),
        ("supernode pages", "Page adjacency and push predicates before decode"),
        ("VLE budget", "Stop/resume at CPU, path and remote-byte limits"),
        ("shortest-path spill", "Use bounded external frontier structures"),
        ("partition-local traversal", "Avoid network for owned neighborhoods"),
        ("cross-partition traversal", "Batch remote frontier RPCs"),
        ("virtual-shard rebalance", "Move ownership without rewriting all S3 data"),
        ("worker loss", "Retry idempotent snapshot reads without coordinator state"),
        ("metadata leader loss", "Preserve published snapshots and bounded write pause"),
        ("region loss", "Recover manifests/deltas and reuse replicated S3"),
        ("object corruption", "Validate checksums and alternate replicas"),
        ("S3 throttling", "Backpressure and report budget exhaustion"),
        ("fixed worker cap", "Hold cost while offered load rises"),
        ("fixed cache cap", "Hold memory while graph reaches PB"),
        ("fixed request cap", "Enforce per-query and per-tenant object requests"),
        ("foreground/background isolation", "Prevent compaction from violating latency SLO"),
        ("bytes per edge", "Target tenfold reduction versus relational heap plus indexes"),
        ("cold queries per dollar", "Target tenfold cost-normalized win"),
        ("scale-out ingest", "Target linear shard throughput"),
        ("PB namespace", "List/plan without loading PB metadata into every worker"),
        ("trillion-edge traversal", "Run real loaded scale with correctness hashes"),
        ("backup-free recovery", "Rebuild caches directly from authoritative objects"),
        ("AgensGraph export", "Stream stable snapshot label tables and preserve identity map"),
        ("dual read", "Compare result bags and paths during migration"),
        ("dual write", "Validate transaction gaps before cutover"),
        ("Cypher conformance", "Publish supported syntax and semantic differential suite"),
        ("SQL interoperability", "Define federation boundary without one monolithic backend"),
        ("EXPLAIN remote cost", "Expose object count, bytes, partitions and cache assumptions"),
        ("admission overload", "Return deterministic queue/retry/partial status"),
        ("tenant quota", "Enforce CPU, frontier, storage and request budgets"),
        ("10x claim audit", "Release raw artifacts and confidence bounds"),
    ]
    d.cases("Prototype and acceptance experiments", mk_cases("zu design", items, "Prototype engine and exact AgensGraph 2.17 comparator on metered S3-compatible storage, bounded RAM/NVMe and deterministic network", "S04,S15-S29,S33-S39", True))
    d.sources()
    d.write("07-design-lessons-and-proposed-architecture.md")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_index()
    make_lineage()
    make_storage()
    make_query()
    make_correctness()
    make_ops()
    make_benchmark()
    make_design()


if __name__ == "__main__":
    main()
