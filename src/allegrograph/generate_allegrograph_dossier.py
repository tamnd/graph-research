#!/usr/bin/env python3
"""Generate the source- and documentation-audited AllegroGraph 9.0.2 dossier."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent


OUT = Path(__file__).resolve().parents[2] / "docs" / "research" / "allegrograph"
CUT = "2026-08-08"
VERSION = "9.0.2"
PYTHON_COMMIT = "e344c12e9664f257c2793d245702dc4afcc1ee3f"
JAVA_COMMIT = "6e7858f90d86410109ff66e4ec11da75c35c752c"
DOCKER_COMMIT = "b2a50ece125cb4646594f33fd3a08074efe5f339"


SOURCES = [
    ("S01", "9.0.2 release notes", "Official documentation", "Current maintenance release and change chronology", "https://franz.com/agraph/support/documentation/release-notes.html"),
    ("S02", "9.0.0 release notes", "Official documentation", "GraphTalker introduction and removal of the legacy distributed-store system", "https://franz.com/agraph/support/documentation/9.0.0/release-notes.html"),
    ("S03", "Documentation index", "Official documentation", "Current 9.0.2 manual surface", "https://franz.com/agraph/support/documentation/"),
    ("S04", "Introduction", "Official documentation", "Product model, query languages, reasoning, transactions and APIs", "https://franz.com/agraph/support/documentation/agraph-introduction.html"),
    ("S05", "Downloads", "Official distribution", "9.0.2 Linux x86-64 artifact and clients", "https://franz.com/agraph/downloads/"),
    ("S06", "Quick start", "Official documentation", "Installation requirements and first repository", "https://franz.com/agraph/support/documentation/agraph-quick-start.html"),
    ("S07", "Triple indices", "Official documentation", "Index permutations, defaults, optimization and storage rule of thumb", "https://franz.com/agraph/support/documentation/triple-index.html"),
    ("S08", "Performance tuning", "Official documentation", "Memory mapping, shared memory, checkpoints, sessions and resource sizing", "https://franz.com/agraph/support/documentation/performance-tuning.html"),
    ("S09", "Query engines", "Official documentation", "SBQE and MJQE behavior, limits, caching and path tradeoffs", "https://franz.com/agraph/support/documentation/query-engines.html"),
    ("S10", "SPARQL reference", "Official documentation", "SPARQL surface and Franz query options", "https://franz.com/agraph/support/documentation/sparql-reference.html"),
    ("S11", "Prolog tutorial", "Official documentation", "Prolog query model and integration", "https://franz.com/agraph/support/documentation/prolog-tutorial.html"),
    ("S12", "HTTP protocol", "Official documentation", "Public wire protocol and transaction/session operations", "https://franz.com/agraph/support/documentation/http-protocol.html"),
    ("S13", "HTTP reference", "Official documentation", "REST endpoint inventory", "https://franz.com/agraph/support/documentation/http-reference.html"),
    ("S14", "Transactions section in introduction", "Official documentation", "Snapshot isolation, transaction logs, conflicts and commit behavior", "https://franz.com/agraph/support/documentation/agraph-introduction.html#transactions"),
    ("S15", "FedShard tutorial", "Official documentation", "Horizontal sharding workflow and query behavior", "https://franz.com/agraph/support/documentation/dynamic-cluster-tutorial.html"),
    ("S16", "FedShard setup", "Official documentation", "Partitioning, common knowledge bases, replicas and split operations", "https://franz.com/agraph/support/documentation/dynamic-cluster-setup.html"),
    ("S17", "FedShard definition", "Official documentation", "Shard definition syntax and partition-key contract", "https://franz.com/agraph/support/documentation/fedshard-def.html"),
    ("S18", "Multi-master replication", "Official documentation", "Active-active replication, controller, queues and consistency caveats", "https://franz.com/agraph/support/documentation/multi-master.html"),
    ("S19", "Backup and restore", "Official documentation", "Online archives, S3 transport and distributed backup constraints", "https://franz.com/agraph/support/documentation/backup-and-restore.html"),
    ("S20", "agtool", "Official documentation", "Administrative, archive, MMR and repository utilities", "https://franz.com/agraph/support/documentation/agtool.html"),
    ("S21", "Server configuration", "Official documentation", "Repository, memory, directory, checkpoint and license settings", "https://franz.com/agraph/support/documentation/daemon-config.html"),
    ("S22", "Docker", "Official documentation", "Container distribution and shared-memory requirement", "https://franz.com/agraph/support/documentation/docker.html"),
    ("S23", "Virtual machine", "Official documentation", "Native Linux x86-64 boundary and virtualization warning", "https://franz.com/agraph/support/documentation/virtual-machine.html"),
    ("S24", "Security overview", "Official documentation", "Authentication, authorization, TLS and operational security model", "https://franz.com/agraph/support/documentation/security-overview.html"),
    ("S25", "User and role management", "Official documentation", "Repository permissions, roles and filters", "https://franz.com/agraph/support/documentation/userrole.html"),
    ("S26", "Triple attributes", "Official documentation", "Attribute semantics, aggregation, immutability and non-indexed values", "https://franz.com/agraph/support/documentation/triple-attributes.html"),
    ("S27", "RDFS++ reasoner", "Official documentation", "Dynamic entailment rules and query-time behavior", "https://franz.com/agraph/support/documentation/reasoner-tutorial.html"),
    ("S28", "OWL2 RL materializer", "Official documentation", "Materialization workflow and operational consequences", "https://franz.com/agraph/support/documentation/materializer.html"),
    ("S29", "SHACL", "Official documentation", "Shape validation interface and semantics", "https://franz.com/agraph/support/documentation/shacl.html"),
    ("S30", "LLM and vector store", "Official documentation", "Embedding, vector comparison and natural-language integration", "https://franz.com/agraph/support/documentation/llmembed.html"),
    ("S31", "AGWebView", "Official documentation", "Plans, logs and administrative observability", "https://franz.com/agraph/support/documentation/webview.html"),
    ("S32", "Historical scale results", "Vendor benchmark page", "Load-only LUBM-like claims through 1.009 trillion triples", "https://franz.com/agraph/allegrograph/index.lhtml"),
    ("S33", "AllegroGraph 9 launch", "Vendor announcement", "GraphTalker positioning; marketing evidence only", "https://allegrograph.com/allegrograph-9-0-launches-with-graphtalker/"),
    ("S34", "Free edition", "Official product page", "Free-use limit and commercial-license boundary", "https://franz.com/agraph/downloads/"),
    ("S35", "Python client snapshot", "Pinned public source", f"MIT client source at {PYTHON_COMMIT}; not server internals", f"https://github.com/franzinc/agraph-python/tree/{PYTHON_COMMIT}"),
    ("S36", "Python REST implementation", "Pinned public source", "Commit, rollback, index, warmup, vector and MMR endpoint wrappers", f"https://github.com/franzinc/agraph-python/blob/{PYTHON_COMMIT}/src/franz/miniclient/repository.py"),
    ("S37", "Python client license", "Pinned public source", "MIT license for the client", f"https://github.com/franzinc/agraph-python/blob/{PYTHON_COMMIT}/LICENSE"),
    ("S38", "Java client snapshot", "Pinned public source", f"Eclipse Public License 1.0 client at {JAVA_COMMIT}", f"https://github.com/franzinc/agraph-java-client/tree/{JAVA_COMMIT}"),
    ("S39", "Java transaction settings", "Pinned public source", "Client-visible transaction and MMR commit controls", f"https://github.com/franzinc/agraph-java-client/tree/{JAVA_COMMIT}/src/main/java/com/franz/agraph/repository"),
    ("S40", "Docker snapshot", "Pinned public source", f"Container build and entry point at {DOCKER_COMMIT}; downloads closed binary", f"https://github.com/franzinc/docker-agraph/tree/{DOCKER_COMMIT}"),
    ("S41", "Dockerfile", "Pinned public source", "Build stage downloads the server distribution rather than compiling server source", f"https://github.com/franzinc/docker-agraph/blob/{DOCKER_COMMIT}/Dockerfile"),
    ("S42", "Container entry point", "Pinned public source", "Shared memory, ownership, generated credentials and license injection", f"https://github.com/franzinc/docker-agraph/blob/{DOCKER_COMMIT}/entrypoint.sh"),
    ("S43", "Franz GitHub organization", "Official public source inventory", "Clients, examples and packaging are public; server engine source was not found", "https://github.com/franzinc"),
    ("S44", "LDBC SNB", "Independent benchmark authority", "Current benchmark specification and audited-result framework", "https://ldbcouncil.org/benchmarks/snb/"),
    ("S45", "LDBC results", "Independent benchmark authority", "Published audited-result inventory; no current AllegroGraph result found", "https://ldbcouncil.org/benchmarks/snb-bi/"),
    ("S46", "SP2Bench", "Academic benchmark specification", "SPARQL performance workload; historical relevance does not imply a 9.0.2 result", "https://dbis.informatik.uni-freiburg.de/forschung/projekte/SP2B/"),
    ("S47", "BSBM publication record", "Academic benchmark source", "Original RDF e-commerce benchmark publication and DOI", "https://madoc.bib.uni-mannheim.de/34767/"),
    ("S48", "RDF 1.2 concepts", "W3C standard", "RDF graph, dataset and term semantics", "https://www.w3.org/TR/rdf12-concepts/"),
    ("S49", "SPARQL 1.1 query", "W3C standard", "Independent semantic oracle for query results", "https://www.w3.org/TR/sparql11-query/"),
    ("S50", "S3 consistency", "AWS official documentation", "Object-store behavior for backup/control-plane design", "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html#ConsistencyModel"),
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
            f"Product baseline: `AllegroGraph {VERSION}`",
            "Evidence status: current manual audited; public client/container source pinned; proprietary server internals unavailable",
            f"Scope: {scope}", "",
        ]

    def h(self, n: int, text: str) -> None:
        self.lines += [f"{'#' * n} {text}", ""]

    def p(self, text: str) -> None:
        for para in dedent(text).strip().split("\n\n"):
            self.lines += [line.rstrip() for line in para.splitlines()] + [""]

    def table(self, headers: list[str], rows: list[list[str]]) -> None:
        self.lines.append("| " + " | ".join(headers) + " |")
        self.lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            self.lines.append("| " + " | ".join(x.replace("|", "\\|") for x in row) + " |")
        self.lines.append("")

    def findings(self, title: str, rows: list[tuple[str, str, str]]) -> None:
        self.h(2, title)
        for i, (name, finding, evidence) in enumerate(rows, 1):
            self.h(3, f"F{i:03d} — {name}")
            self.lines += [
                f"- Finding: {finding}",
                f"- Evidence anchors: {evidence}",
                "- Confidence rule: official documentation describes the supported contract; inference and vendor performance claims remain explicitly qualified.",
                "- Decision use: retain the version, topology, durability, dataset and cache-state qualifiers whenever this finding is cited.",
                "- Revalidation trigger: a release, index-format change, query-engine change, replication change, licensing change, or new audited result.",
                "",
            ]

    def cases(self, title: str, rows: list[Case]) -> None:
        self.h(2, title)
        self.p("Every case is an independent result cell. Preserve query semantics and failure behavior. Report p50, p95, p99, p99.9 and maximum, plus errors and timeouts; never average percentiles or silently omit failed operations.")
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
                "- Artifact set: version/license, config, topology, dataset manifest, query text, plans, raw samples, telemetry, logs, failure timeline and cost sheet.",
                "",
            ]

    def sources(self, ids: set[str] | None = None) -> None:
        self.h(2, "Source register")
        self.p("Official status establishes what Franz documents or distributes, not measured performance. Public source links are commit-pinned, but they cover clients and packaging rather than the proprietary server engine. Historical and marketing evidence is never promoted to a current audited benchmark.")
        for sid, title, kind, note, url in SOURCES:
            if ids is None or sid in ids:
                self.h(3, f"{sid} — {title}")
                self.lines += [f"- Type: {kind}", f"- Audit note: {note}", f"- URL: {url}", ""]

    def write(self, name: str) -> None:
        while self.lines and not self.lines[-1]:
            self.lines.pop()
        self.lines.append("")
        (OUT / name).write_text("\n".join(self.lines), encoding="utf-8")


def cases(prefix: str, names: list[tuple[str, str]], setup: str, evidence: str, mutate: bool = False) -> list[Case]:
    result = []
    for name, purpose in names:
        result.append(Case(
            f"{prefix}: {name}", purpose, setup,
            f"Run `{name}` at concurrency 1, saturation and overload in cold, warm and steady states" + ("; repeat across commit, checkpoint, crash and recovery boundaries" if mutate else ""),
            "client and server latency distributions, throughput, CPU, RSS/shared memory, cache reads, storage I/O, temp/spill bytes, network bytes, queue depth, errors and cost",
            "Compare RDF terms, solution multisets, ordering where specified, inferred statements, committed state and replica/shard observations with an independent reference model",
            "A mismatch, lost acknowledged write, stale result outside the declared contract, crash, unbounded resource use, hidden timeout, unavailable shard or excluded retry is a failed cell",
            evidence,
        ))
    return result


COMMON = [
    ("Current baseline", "The current manual identifies AllegroGraph 9.0.2 and was updated 2026-06-24; every result must pin the exact server build and license.", "S01,S03,S05"),
    ("Product form", "The server is a proprietary Linux x86-64 distribution; the audit found no public server storage, optimizer or replication implementation.", "S05,S23,S40-S43"),
    ("Public source boundary", "Python, Java and Docker repositories reveal wire contracts and packaging, not server algorithms or physical-format implementation.", "S35-S43"),
    ("Data model", "The core model is RDF triples/quads with unique repository-local triple IDs and optional immutable triple attributes.", "S04,S07,S26,S48"),
    ("Query surfaces", "AllegroGraph supports SPARQL, Prolog and APIs plus reasoning, text, geospatial, temporal, social-network and vector facilities.", "S04,S09-S13,S27-S30"),
    ("Index form", "Disk-resident triple indices are selected permutations of subject, predicate, object and graph followed by triple ID.", "S07"),
    ("Default indices", "New repositories normally carry seven indices: spogi, posgi, psogi, ospgi, gspoi, gposi and i.", "S07"),
    ("Storage rule", "Franz gives roughly 100 bytes per triple for the default index set; this is a planning heuristic, not a measured universal constant.", "S07"),
    ("String table", "IRIs and strings are stored once and indices use identifiers; encoded numeric-like values support range access.", "S07"),
    ("Optimization", "Insert/delete churn degrades index optimality and background or explicit optimization rewrites index structures.", "S07,S08"),
    ("Query engines", "SBQE is the default; MJQE trades different joins, caching and lower-memory/path behavior and is used for FedShard.", "S09,S15-S17"),
    ("Path risk", "The query-engine manual warns that path evaluation can grow combinatorially and exhaust resources; paging is a mitigation, not a proof of bounded work.", "S09"),
    ("Transaction model", "Transactions use snapshot isolation without triple locking; application-level semantic constraints remain the application's responsibility.", "S14"),
    ("Commit durability", "Commit records the transaction log and waits for log I/O before returning under the documented local contract.", "S14"),
    ("FedShard role", "FedShard horizontally partitions a logical repository across shard repositories using a required part or attribute key.", "S15-S17"),
    ("Broadcast execution", "FedShard modifies and sends queries to shards in parallel, then combines results; shards execute isolated from each other.", "S15-S17"),
    ("Partition-key sensitivity", "Locality and cross-shard work depend on the selected subject, predicate, object, graph or attribute partition key.", "S15-S17"),
    ("Elasticity boundary", "Splitting a shard is offline and is the supported topology change; arbitrary redefinition can make triples inaccessible.", "S16,S17"),
    ("MMR role", "MMR is active-active replication for availability and read/write service, separate from capacity partitioning.", "S18"),
    ("Replication ordering", "MMR commits can reach a replica in a different causal order; documentation warns transient triple counts can be inaccurate or even negative.", "S18"),
    ("Controller risk", "A forced controller replacement can leave two nodes believing they control configuration when the old controller returns, demanding external fencing discipline.", "S18"),
    ("S3 boundary", "S3 is supported for import and archive backup/restore, not as the authoritative online random-access triple/index store.", "S19,S20,S50"),
    ("Distributed backup", "A FedShard archive requires all participating servers to be available; the backup path is not shard-failure independent.", "S19"),
    ("Memory model", "The server relies heavily on shared memory and memory-mapped files, allowing the OS page cache to dominate warm-query behavior.", "S08,S21"),
    ("Checkpoint tails", "The default checkpoint interval is five minutes and commits are blocked during checkpoint; large checkpoints can take tens of seconds.", "S08,S21"),
    ("Connection resources", "Dedicated sessions bypass frontend routing but consume server resources; throughput eventually declines beyond the useful concurrency point.", "S08,S12"),
    ("Sizing floor", "Franz recommends SSD, at least 16 GB for initial use and substantially more memory and cores for multi-billion-triple production stores.", "S06,S08"),
    ("Free limit", "The free edition is capped at five million triples; larger and clustered evaluation requires a commercial license and a quote.", "S05,S34"),
    ("Historical trillion claim", "The vendor page reports a pre-release 1.009-trillion-triple load, but not a current 9.0.2 query, durability, failure or cost benchmark.", "S32"),
    ("No current audited 10x proof", "No same-hardware, same-data, same-semantics audited result was found that proves AllegroGraph or the proposed design is 10x faster than all competitors.", "S32,S44-S47"),
    ("PB gap", "A trillion triples is not automatically a petabyte, and the historical result does not establish PB online operation or thousand-trillion-edge capacity.", "S07,S32"),
    ("Cost gap", "Contact pricing, local SSD/RAM authority and replica/index amplification prevent a defensible fixed-cost-to-S3 claim without a written quote and measured footprint.", "S05,S07,S18-S21"),
]


TOPICS = {
    "00-index.md": {
        "title": "AllegroGraph 9.0.2 deep audit: index and decision verdict",
        "scope": "Navigation, executive verdict, evidence boundaries, target-fit score and acceptance gates",
        "intro": """
        AllegroGraph is a mature, feature-dense RDF database with a documented disk-index design, two query engines, reasoning, ACID snapshot transactions, active-active MMR and FedShard horizontal partitioning. It deserves serious comparison for knowledge-graph workloads, especially when SPARQL, Prolog and rule systems matter.

        It does not satisfy the target architecture as shipped. S3 is an import/archive destination rather than the online authority; seven default index permutations create material amplification; FedShard broadcasts work and depends on partition-key locality; shard splitting is offline; MMR and FedShard are separate layers with explicit consistency and controller caveats; commercial cost is not public. The historical trillion-triple load remains noteworthy but cannot establish current low latency, PB online scale, fixed S3 cost or a universal 10x win.

        The decisive reuse is conceptual: compact term dictionaries, permutation choices driven by workload, explicit query-engine selection, RDF reasoning and partition-aware execution. The proposed system should replace mutable local-only authority with immutable S3 segments, use a thin metadata/lease plane, bound every traversal, separate serving replicas from durable data and publish reproducible correctness-first benchmarks.
        """,
        "extra": [
            ("Verdict", "Use AllegroGraph as an RDF/SPARQL/reasoning comparator and semantic oracle candidate, not as evidence that the target S3-native design already exists.", "S03-S32"),
            ("Strongest feature", "Its integrated semantic stack and long-lived operational documentation are more differentiated than raw adjacency traversal.", "S03-S31"),
            ("Strongest scale feature", "FedShard is real horizontal partitioning and can place replicas for each shard, but its broadcast/combine model exposes locality costs.", "S15-S18"),
            ("Strongest correctness feature", "Documented snapshot transactions and log-synchronous commit create a testable local durability contract.", "S14"),
            ("Main rejection", "No authoritative-online-S3 mode, transparent elastic repartitioning, public engine code or current audited 10x result meets the requested acceptance bar.", "S05,S15-S21,S32,S44-S47"),
            ("Evidence honesty", "All performance cells remain NOT RUN; this dossier records claims, mechanisms and benchmark designs, not invented measurements.", "S01-S50"),
        ],
        "tests": [
            ("release artifact identity", "Pin server build, license capabilities, client commits and container digest"),
            ("five-million boundary", "Verify free-edition behavior exactly at and beyond the stated limit"),
            ("single-node acceptance", "Run semantic, latency, resource and crash gates on one repository"),
            ("FedShard acceptance", "Prove partition-aware results and bounded scatter across topology changes"),
            ("MMR acceptance", "Prove acknowledged-write visibility, recovery and controller fencing"),
            ("S3 archive acceptance", "Prove backup integrity, restore RTO and object-cost accounting"),
            ("trillion claim reconstruction", "Recover enough historical methodology to identify what the result actually proves"),
            ("current LDBC track", "Publish a rules-compliant result or label the comparison non-audited"),
            ("10x gate", "Require geometric-mean and per-family results with correctness and cost parity"),
            ("PB projection", "Base extrapolation on measured bytes, restore time, partitions and operational limits"),
            ("closed-source risk", "Obtain architectural evidence and support obligations under NDA without overstating public auditability"),
            ("exit test", "Export complete standards-valid RDF and restore it into an independent implementation"),
            ("price quote", "Include cores, replicas, shards, environments, support and upgrade rights"),
            ("security gate", "Validate TLS, authentication, roles, filters, auditability and secret rotation"),
            ("operational gate", "Exercise checkpoint, optimization, backup, restore, expansion and failure runbooks"),
            ("resource gate", "Enforce CPU, memory, SSD, network and temporary-space ceilings at p99"),
            ("cold-start gate", "Measure first query after restart and after page-cache eviction"),
            ("semantic gate", "Differentially validate SPARQL bags, nulls, paths, inference and updates"),
            ("overload gate", "Require admission, cancellation and recovery instead of resource collapse"),
            ("migration gate", "Prove 8.x to 9.0.2 upgrade and legacy distributed-store export/import"),
            ("documentation drift", "Snapshot every cited page and detect changed contracts"),
            ("client compatibility", "Cross-test Python, Java and raw HTTP against the exact server"),
            ("container parity", "Compare native and container results without hiding shared-memory differences"),
            ("query-engine parity", "Confirm SBQE/MJQE results and explain ordering differences"),
            ("reasoning parity", "Separate asserted, dynamically entailed and materialized triples"),
            ("cost parity", "Normalize hardware, license, operators, backup, network and object requests"),
            ("failure disclosure", "Publish every timeout, retry, stale read, incomplete result and excluded sample"),
            ("reproducibility", "Release manifests, generators, queries, raw samples, plans and telemetry"),
        ],
    },
    "01-product-releases-licensing-and-evidence.md": {
        "title": "AllegroGraph product, releases, licensing, and evidence audit",
        "scope": "Version chronology, editions, platform, licensing, public source, documentation drift and claim classification",
        "intro": """
        The auditable product baseline is AllegroGraph 9.0.2, documented on 2026-06-24. Version 9.0 introduced GraphTalker and removed the old distributed-triple-store mechanism; FedShard, introduced earlier, is now the supported sharding path. Migration from the removed mechanism requires manual export and import, which is an operational compatibility break rather than an in-place topology upgrade.

        The engine is not open source. Franz publishes client libraries, examples and Docker build machinery, while the container recipe downloads a proprietary server archive. The Python client is MIT; the pinned Java client declares EPL-1.0. Neither license transfers to the server. A serious procurement must retain server-license text, feature limits, support lifecycle, core/cluster constraints and price quote alongside benchmark artifacts.
        """,
        "extra": [
            ("9.0.2 status", "9.0.2 is a maintenance release with AGWebView and GraphTalker fixes, not a documented storage-engine redesign.", "S01"),
            ("9.0 transition", "The legacy distributed-store system was removed and FedShard became the only current sharding architecture.", "S02,S15-S17"),
            ("Migration boundary", "Legacy distributed repositories require manual export/import into FedShard.", "S02"),
            ("Native platform", "The current native distribution is Linux x86-64; macOS and Windows use virtualization or Docker with potential performance loss.", "S05,S22,S23"),
            ("Server opacity", "No public engine implementation was located, so storage and optimizer claims stop at documented interfaces and observed behavior.", "S40-S43"),
            ("Python source", "The pinned Python tree reported client version 105.2.0 and exposes broad REST coverage under MIT.", "S35-S37"),
            ("Java source", "The pinned Java client is EPL-1.0 and contains transaction, pooling, index and XA integration surfaces.", "S38,S39"),
            ("Docker source", "The Dockerfile downloads and installs a binary tarball; it is packaging evidence, not server-source disclosure.", "S40-S42"),
            ("Container secrets", "The entry point supports secret files but can generate and print credentials when none are supplied, which requires log-handling review.", "S42"),
            ("License scope", "Paid licenses may constrain triples, expiry, entitlement, server cores, cluster cores and allowed versions.", "S05,S21,S34"),
            ("Price opacity", "Commercial pricing is contact-only, defeating a public fixed-cost comparison.", "S05,S34"),
            ("Claim classes", "Manual contracts, marketing claims, historical benchmarks, public client code, independent standards and local observations must remain separate evidence classes.", "S01-S50"),
        ],
        "tests": [(x, y) for x, y in [
            ("9.0.2 checksum", "Archive exact native and container artifact identity"), ("license inventory", "Record every capability and limit in the supplied license"),
            ("free cap", "Observe reads, writes, imports and errors around five million triples"), ("expiry", "Test documented behavior before and after a staged expiry"),
            ("core enforcement", "Verify CPU and cluster-core licensing under containers and VMs"), ("upgrade entitlement", "Confirm which future versions the contract permits"),
            ("9.0.0 migration", "Export a legacy distributed store and import to FedShard"), ("9.0.1 regression", "Replay changed query and administration cases"),
            ("9.0.2 regression", "Reproduce GraphTalker and WebView fixes"), ("native Linux", "Establish the reference performance platform"),
            ("Docker parity", "Quantify container and shared-memory overhead"), ("VM parity", "Quantify the documented virtualization penalty"),
            ("Python client", "Run its unit and integration suites against 9.0.2"), ("Java client", "Run its suite and transaction/XA cases"),
            ("raw HTTP", "Remove client overhead from server measurements"), ("source inventory", "Detect newly published or removed Franz repositories"),
            ("SBOM", "Inventory the binary distribution and container packages"), ("CVE process", "Obtain disclosure and remediation SLAs"),
            ("support matrix", "Record distribution, kernel, filesystem and cloud support"), ("end-of-life", "Obtain dates and patch commitments for 9.x"),
            ("pricing model", "Quote dev, test, prod, DR and burst capacity"), ("audit rights", "Determine access to architectural and security evidence"),
            ("benchmark rights", "Confirm contractual permission to publish results"), ("export rights", "Confirm standards-based data portability"),
            ("documentation snapshot", "Archive every page with retrieval metadata"), ("release alert", "Detect changes after the research cut"),
            ("marketing diff", "Flag claims unsupported by current manuals or artifacts"), ("procurement exit", "Measure complete export and independent reload"),
        ]],
    },
    "02-storage-indices-ids-and-data-model.md": {
        "title": "AllegroGraph storage, indices, IDs, and RDF data-model audit",
        "scope": "Physical documented model, dictionary encoding, index permutations, amplification, attributes, optimization and capacity",
        "intro": """
        AllegroGraph stores RDF statements and repository-local IDs behind disk-resident sorted index permutations. The default seven-index set favors many access patterns, but the vendor's own rule of thumb—about 100 bytes per triple—makes amplification a first-order design constraint. One trillion triples at that heuristic is about 100 TB before replicas, backups, free space, logs, temporary data and operational headroom; it is not evidence of a petabyte logical graph.

        The string table deduplicates IRIs and lexical strings. Index optimization and deletion handling mean physical health changes with workload history, so every benchmark needs both freshly built and churned stores, index Oscore, deleted-triple state and exact index set. Triple attributes add security/provenance metadata but are immutable after creation and are not indexed, limiting selective retrieval.
        """,
        "extra": [
            ("Permutation grammar", "Supported full indices permute spog and end in i; i also exists as a direct triple-ID index.", "S07"),
            ("Graph-leading cost", "gspoi and gposi can be removed when named-graph access is not required, trading disk/write cost for access paths.", "S07"),
            ("Repository-local ID", "Triple IDs are unique only inside one repository; federated members can expose identical IDs from different repositories.", "S07,S15-S17"),
            ("Numeric encoding", "Recognized numeric-like literals receive encodings intended to support ordered range access.", "S07"),
            ("Duplicate lifecycle", "Duplicate removal is not automatic in all paths and must be treated as explicit maintenance and semantic policy.", "S07,S20"),
            ("Oscore", "Oscore 1.0 denotes an optimally organized index; lower values identify rewrite opportunity.", "S07"),
            ("Attribute immutability", "Triple attributes are assigned at creation and cannot be edited later; replacement requires statement lifecycle changes.", "S26"),
            ("Attribute non-indexing", "Attribute values are not indexed, so they should not be assumed to provide low-latency selective access.", "S26"),
            ("Attribute aggregation", "Commit-time aggregation can replace a duplicate statement according to configured attribute rules.", "S26"),
            ("Capacity evidence", "Documented bit widths, IDs and a historical load do not prove usable capacity under query, update, recovery and cost SLOs.", "S07,S26,S32"),
            ("Online authority", "Mapped local files and SSD are the serving substrate; archive objects cannot satisfy random index probes without restore.", "S08,S19,S21"),
            ("Proposed lesson", "An S3-native challenger should store immutable dictionary and adjacency segments, minimize permutations and rebuild secondary indices asynchronously.", "Inference from S07-S21"),
        ],
        "tests": [(x, y) for x, y in [
            ("empty repository", "Measure fixed files, shared memory and catalog footprint"), ("one million triples", "Measure bytes by component with all defaults"),
            ("one billion projection", "Validate extrapolation against measured nonlinearities"), ("one trillion projection", "Include headroom, replicas, logs and backups"),
            ("spogi only", "Measure minimal chosen-permutation tradeoff"), ("default seven", "Measure query benefit and write/storage amplification"),
            ("drop graph indices", "Validate workloads with and without named graphs"), ("add all valid indices", "Expose upper-bound storage and maintenance cost"),
            ("uniform strings", "Measure dictionary reuse"), ("unique long strings", "Stress string table and access"),
            ("numeric ranges", "Validate encoding, ordering and index selection"), ("language tags", "Validate term identity and collation"),
            ("RDF-star terms", "Measure nested-term representation and query"), ("blank nodes", "Validate import/export identity"),
            ("many graphs", "Measure graph-leading index locality"), ("single graph", "Quantify unnecessary graph-index overhead"),
            ("ordered bulk load", "Establish best Oscore and throughput"), ("random insert", "Measure fragmentation and write tails"),
            ("delete churn", "Track tombstones, footprint and query cost"), ("optimize online", "Measure foreground latency during rewrite"),
            ("optimize recovery", "Crash during optimization and validate state"), ("duplicate ingest", "Validate identity, count and deletion policy"),
            ("triple-ID lookup", "Measure i-index path and repository locality"), ("federated ID collision", "Ensure member identity is retained"),
            ("attributes sparse", "Measure metadata overhead"), ("attributes wide", "Measure string and commit aggregation cost"),
            ("attribute filter", "Expose lack of index and latency"), ("attribute replace", "Validate immutable update workflow"),
            ("checkpoint footprint", "Measure dirty pages and writeback per logical write"), ("archive footprint", "Compare local, compressed archive and S3 bytes"),
        ]],
    },
    "03-sparql-prolog-query-engines-and-reasoning.md": {
        "title": "AllegroGraph SPARQL, Prolog, query-engine, and reasoning audit",
        "scope": "SBQE/MJQE planning, SPARQL semantics, paths, Prolog, federation, reasoning, SHACL, text and vectors",
        "intro": """
        AllegroGraph's query breadth is a major strength, but the server optimizer is closed source. The auditable contract comes from standards, manuals, plans and black-box differential tests. SBQE is documented as the default and fastest choice for most queries. MJQE emphasizes merge joins, caching, lower memory and FedShard/path behavior. Engine selection must be part of every result because plans, order and resource envelopes differ.

        Property paths are the central adversarial family: cyclic and high-degree graphs can create combinatorial work, and the manual acknowledges exhaustion and paging. Reasoning further changes what constitutes a result. Asserted-only, dynamic RDFS++ entailment and OWL2 RL materialization must be separate tracks with explicit maintenance and update costs.
        """,
        "extra": [
            ("SBQE default", "SBQE remains the normal default and vendor-preferred engine for most non-distributed queries.", "S09"),
            ("MJQE selection", "A query option selects MJQE explicitly; benchmark artifacts must retain engine choice.", "S09,S10"),
            ("Result order", "Without ORDER BY, differing row order is not a semantic mismatch; LIMIT without order can expose different valid subsets.", "S09,S49"),
            ("Memory behavior", "MJQE is positioned as using less memory in important path/join cases, but that must be measured per workload.", "S09"),
            ("Federated engine", "FedShard depends on distributed query rewriting and MJQE-like combination behavior.", "S09,S15-S17"),
            ("Plan visibility", "AGWebView plan and log views help black-box diagnosis but cannot replace source-level optimizer audit.", "S31"),
            ("RDFS++", "Dynamic reasoning changes query answers without necessarily materializing every entailed statement.", "S27"),
            ("OWL2 RL", "Materialization moves reasoning cost into writes/jobs and creates lifecycle and storage obligations.", "S28"),
            ("SHACL", "Validation must report shape semantics, scope, updates and failure handling independently of query latency.", "S29"),
            ("Vector layer", "Embedding features add model, dimensionality, recall and external-service variables that must not be attributed to core graph execution.", "S30"),
            ("Prolog", "Prolog is a native differentiator but requires its own termination, tabling, recursion and result-semantic tests.", "S11"),
            ("Standards oracle", "W3C RDF/SPARQL specifications are the independent baseline; extensions require separately declared semantics.", "S48,S49"),
        ],
        "tests": [(x, y) for x, y in [
            ("SPO lookup", "Establish minimum indexed pattern latency"), ("join star", "Measure selective hub joins"),
            ("join chain", "Measure cardinality propagation"), ("join cycle", "Expose duplicate and planning behavior"),
            ("OPTIONAL", "Validate unbound variables and bags"), ("UNION", "Validate bag versus set behavior"),
            ("MINUS", "Validate compatibility semantics"), ("FILTER NOT EXISTS", "Validate correlation semantics"),
            ("GROUP BY", "Validate errors, unbound values and aggregates"), ("ORDER LIMIT", "Validate deterministic top-k"),
            ("LIMIT no order", "Record engine-dependent valid subsets"), ("subquery", "Measure materialization and scoping"),
            ("VALUES", "Measure bind joins and large input tables"), ("SERVICE", "Separate remote failures and latency"),
            ("path fixed", "Compare static joins with property paths"), ("path star cycle", "Bound combinatorial expansion"),
            ("path alternatives", "Validate duplicate and reachability semantics"), ("path paging", "Prove completeness across pages"),
            ("SBQE parity", "Run semantic corpus under SBQE"), ("MJQE parity", "Run identical corpus under MJQE"),
            ("engine crossover", "Find latency, memory and spill crossover"), ("plan cache", "Measure repeated-query warmup and invalidation"),
            ("RDFS++ cold", "Measure first dynamic entailment query"), ("RDFS++ warm", "Measure steady cache behavior"),
            ("OWL materialize", "Measure time, space and atomic visibility"), ("OWL incremental update", "Measure refresh and stale inference"),
            ("SHACL valid", "Measure validation with no violations"), ("SHACL invalid", "Validate complete violation reporting"),
            ("Prolog recursion", "Test termination and resource ceilings"), ("Prolog SPARQL mix", "Validate shared transaction/results"),
            ("freetext graph join", "Separate candidate generation from expansion"), ("vector graph join", "Report recall and graph latency separately"),
        ]],
    },
    "04-transactions-mmr-fedshard-and-correctness.md": {
        "title": "AllegroGraph transactions, MMR, FedShard, and correctness audit",
        "scope": "Isolation, durability, conflicts, replication, sharding, partitions, recovery and topology correctness",
        "intro": """
        Local AllegroGraph transactions offer a concrete snapshot-isolation and log-durability contract, but snapshot isolation permits anomalies such as write skew unless applications coordinate invariants. FedShard and MMR add different distributed dimensions: FedShard partitions capacity, whereas MMR replicates members for availability and multi-writer access. Combining them does not collapse their failure semantics into one serializable global database.

        The most important manual disclosure is that MMR can apply related commits out of causal order at a replica, temporarily making even triple counts inaccurate or negative. This does not mean committed data is necessarily lost; it means visibility, lag and convergence must be measured rather than inferred from “real-time” language. Controller replacement also needs fencing. FedShard partition keys, isolated shard execution, offline split and all-servers-required backup are explicit operational correctness boundaries.
        """,
        "extra": [
            ("Snapshot write skew", "No triple locks or application constraints automatically prevent two writers from violating a cross-triple invariant.", "S14"),
            ("Metadata conflicts", "Some concurrent metadata changes fail at commit and require explicit retry policy.", "S14"),
            ("Acknowledgement scope", "Local log I/O acknowledgement is not by itself proof that every MMR replica has applied the commit.", "S14,S18"),
            ("MMR lag", "Queue and commits-behind state are necessary observability signals for read routing and failover.", "S18"),
            ("Causal inversion", "Delete-before-add application at a replica explains transient negative counts and creates read-your-writes hazards.", "S18"),
            ("Convergence obligation", "The acceptance test must distinguish temporary divergence, bounded lag, permanent divergence and lost acknowledgement.", "S18"),
            ("Partition key", "FedShard offers part keys over RDF positions or an attribute key; all matching key values colocate.", "S15-S17,S26"),
            ("Common KB", "Read-only common knowledge bases may be federated into distributed queries and need version consistency.", "S15-S17"),
            ("Cross-shard path", "Shard isolation during execution makes general cross-shard traversal a semantic/performance test target.", "S15-S17"),
            ("Split downtime", "Shard split requires the database closed and is not a transparent online rebalance.", "S16"),
            ("Topology immutability", "Unsupported definition changes can hide existing triples because routing no longer matches placement.", "S16,S17"),
            ("Recovery composition", "A credible design must test local crash recovery, MMR convergence and FedShard membership as separate layers and together.", "S14-S20"),
        ],
        "tests": [(x, y) for x, y in [
            ("read committed snapshot", "Validate statement and transaction visibility"), ("repeatable read", "Validate stable snapshot behavior"),
            ("write skew", "Demonstrate or prevent cross-triple invariant violation"), ("lost update", "Validate conflicts on overlapping mutations"),
            ("duplicate add", "Validate statement identity and attributes"), ("delete/add race", "Validate final state and replica sequence"),
            ("commit crash before fsync", "Require no acknowledged phantom commit"), ("commit crash after ack", "Require durable recovery"),
            ("checkpoint crash", "Validate recovery and tail latency"), ("metadata conflict", "Validate error and idempotent retry"),
            ("MMR single writer", "Measure apply lag and read routing"), ("MMR multi writer", "Measure conflicts and convergence"),
            ("causal add-delete", "Reproduce or bound transient inversion"), ("negative count", "Observe documented count caveat safely"),
            ("replica disconnect", "Measure queue growth, storage and catch-up"), ("replica restart", "Validate exact convergence"),
            ("controller loss", "Validate no unsafe configuration mutation"), ("forced controller", "Use external fencing and test rejoin"),
            ("network partition", "Classify availability and divergence per side"), ("asymmetric partition", "Test one-way communication failures"),
            ("FedShard subject key", "Measure subject-local patterns"), ("FedShard object key", "Measure reverse-local patterns"),
            ("FedShard predicate key", "Expose hot predicate imbalance"), ("FedShard graph key", "Measure named-graph isolation"),
            ("attribute partition", "Validate aggregation and routing"), ("cross-shard join", "Validate complete results and network cost"),
            ("cross-shard path", "Validate reachability semantics"), ("common KB outage", "Classify query availability"),
            ("offline split", "Measure downtime and data verification"), ("unsupported redefine", "Prove guardrails prevent inaccessible triples"),
            ("shard replica loss", "Combine FedShard routing with MMR failover"), ("distributed archive outage", "Validate documented all-server dependency"),
            ("restore topology", "Validate partitions, replicas and counts after restore"), ("global invariant", "Test constraints spanning shards and replicas"),
        ]],
    },
    "05-operations-resources-security-s3-and-cost.md": {
        "title": "AllegroGraph operations, resources, security, S3, and cost audit",
        "scope": "Memory, CPU, SSD, checkpoints, sessions, maintenance, backup, restore, security, observability and TCO",
        "intro": """
        AllegroGraph is engineered for a large local memory-and-SSD working set. Shared memory and memory-mapped files allow useful page-cache reuse across connections, but they also make cache state, NUMA placement, kernel configuration and co-tenancy central to reproducibility. Checkpoints can block commits, index optimization consumes I/O and dedicated sessions trade routing overhead for resource consumption.

        S3 appears in data movement and archive workflows. That can lower backup storage cost, but the live store still requires provisioned local capacity and restore time. Therefore “fixed cost to S3” is not an AllegroGraph property. A complete cost model must charge server licenses, peak RAM/SSD, MMR copies, FedShard headroom, backup objects/requests, network, operators and recovery drills.
        """,
        "extra": [
            ("Shared cache benefit", "Connections to the same repository reuse mapped/index pages, while different repositories multiply working-set demands.", "S08"),
            ("CPU guidance", "A rough operational rule is one useful active connection per core, followed by measured saturation rather than unlimited sessions.", "S08"),
            ("Dedicated sessions", "Dedicated backend ports reduce frontend contention but increase per-session resource commitment.", "S08,S12"),
            ("Huge pages", "Transparent Huge Pages should be disabled according to tuning guidance; kernel state belongs in benchmark manifests.", "S08"),
            ("Expected size", "Predeclaring expected store size can avoid resize events during ingestion.", "S08,S21"),
            ("Directory isolation", "Main data, transaction logs and string table can be placed separately to control contention and failure domains.", "S08,S21"),
            ("String compression", "Compression trades reduced storage for slower access and must be tested on actual lexical distributions.", "S08,S21"),
            ("Archive role", "agtool archive can target S3, but restore reconstructs local serving state and must meet explicit RTO/RPO.", "S19,S20"),
            ("S3 credentials", "Command-line or environment credential handling must be integrated with short-lived identity and redaction.", "S19,S20,S24"),
            ("Authorization", "Repository permissions, roles and filters provide controls whose overhead and bypass resistance need validation.", "S24,S25"),
            ("Container shm", "Official containers require roughly 1 GiB /dev/shm even before workload-specific sizing.", "S22,S40-S42"),
            ("Cost truth", "A fixed monthly envelope is an admission-control and architecture result, not a claim inferred from cheap S3 capacity pricing.", "S05,S07,S18-S21,S50"),
        ],
        "tests": [(x, y) for x, y in [
            ("minimum memory", "Find functional and latency floor"), ("working-set memory", "Map hit rate and p99 by RAM ratio"),
            ("cold page cache", "Measure restart and eviction latency"), ("warm page cache", "Measure steady best case"),
            ("CPU scaling", "Find useful core and connection crossover"), ("dedicated sessions", "Quantify latency and resource tradeoff"),
            ("frontend saturation", "Measure queueing and admission behavior"), ("checkpoint default", "Measure five-minute periodic tail"),
            ("checkpoint large", "Measure commit blocking and recovery tradeoff"), ("separate tx log", "Measure contention reduction"),
            ("separate strings", "Measure dictionary I/O isolation"), ("index optimization", "Measure foreground interference"),
            ("string compression", "Measure bytes and query CPU"), ("THP enabled", "Record unsupported kernel-state impact"),
            ("THP disabled", "Establish supported baseline"), ("Docker shm floor", "Validate startup and workload sizing"),
            ("native versus Docker", "Measure packaging overhead"), ("backup local", "Measure archive throughput and pause behavior"),
            ("backup S3", "Measure upload, requests, cost and integrity"), ("restore S3", "Measure RTO, egress and local capacity"),
            ("distributed backup", "Measure coordination and failure behavior"), ("incremental lifecycle", "Measure retained objects and cleanup"),
            ("credential rotation", "Use temporary identity without interruption"), ("TLS overhead", "Measure handshake, reuse and CPU"),
            ("role matrix", "Validate least privilege across every endpoint"), ("statement filters", "Validate enforcement and latency"),
            ("audit logs", "Verify completeness, redaction and storage cost"), ("secret in logs", "Prevent generated or supplied credential leakage"),
            ("one-billion TCO", "Charge license, compute, SSD, backup and labor"), ("one-trillion TCO", "Charge shards, replicas, headroom and recovery"),
            ("idle cost", "Measure minimum always-on cluster"), ("peak cost", "Measure bounded overload without surprise scaling"),
            ("operator drill", "Time restore, split, failover and reindex procedures"), ("support incident", "Measure evidence bundle and escalation path"),
        ]],
    },
    "06-benchmark-audit-trillion-scale-and-10x.md": {
        "title": "AllegroGraph benchmark audit, trillion-scale evidence, and 10x protocol",
        "scope": "Historical claims, independent-result gap, reproducibility, scale extrapolation and an honest competitor benchmark",
        "intro": """
        Franz publishes four unusually large historical load rows: 1.106 billion and 22.12 billion LUBM triples at about 500 thousand triples per second, plus pre-release 310.269-billion and 1.009-trillion loads at about 1.10 million and 830 thousand triples per second. The machines had 1–2 TB RAM, tens of terabytes of disk and 32–240 cores. These are useful capacity-history artifacts.

        They are not a current competitor benchmark. The page lacks 9.0.2 identity, query latency, update mix, result correctness, durability mode, failure behavior, index/storage breakdown, FedShard/MMR topology, S3 economics and raw artifacts. A 10x claim must be earned separately per workload family under semantic, durability, resource and cost parity. “All competitors” is not statistically or operationally meaningful without a declared roster and versioned matrix.
        """,
        "extra": [
            ("1.106B row", "The vendor reports 36m49s and 500,679 triples/s on a 32-core, 1 TB system.", "S32"),
            ("22.12B row", "The vendor reports 12h18m16s and 499,188 triples/s on the same stated machine class.", "S32"),
            ("310.269B row", "A pre-release row reports 78h9m23s and 1,102,737 triples/s on 64 cores, 2 TB RAM and 22 TB disk.", "S32"),
            ("1.009T row", "A pre-release row reports 338h5m and 829,556 triples/s on 240 cores, 1.28 TB RAM and 88 TB disk.", "S32"),
            ("Version ambiguity", "Pre-release identity cannot be mapped to the present query, storage or distributed implementation.", "S02,S32"),
            ("Load-only boundary", "Bulk-load throughput does not predict point lookup, traversal, SPARQL join, update or recovery latency.", "S32,S44-S49"),
            ("Scale conversion", "At the 100-byte heuristic, a trillion triples suggests roughly 100 TB for defaults, before operational copies and headroom.", "S07,S32"),
            ("Independent gap", "No current LDBC audited AllegroGraph submission was found; absence is not evidence of poor performance, only of missing public proof.", "S44,S45"),
            ("Historical SPARQL suites", "LUBM, SP2Bench and BSBM cover useful RDF behaviors but must be updated, versioned and combined with operational tests.", "S32,S46,S47"),
            ("10x statistic", "Use per-query ratios and workload-family geometric means with confidence intervals; never hide regressions in one grand throughput number.", "Benchmark design"),
            ("Cost parity", "Normalize total monthly cost and fixed ceilings as well as identical hardware, because the target explicitly values fixed S3 economics.", "Benchmark design,S50"),
            ("Correctness first", "Any wrong, partial or stale result outside the declared contract scores as failure regardless of speed.", "S44,S48,S49"),
        ],
        "tests": [(x, y) for x, y in [
            ("historical row transcription", "Preserve exact published counts, rates, time and hardware"), ("artifact request", "Seek configs, data generator, logs and raw results"),
            ("LUBM small", "Validate semantics and measurement harness"), ("LUBM one billion", "Compare current load and query behavior"),
            ("BSBM explore", "Measure read-heavy SPARQL"), ("BSBM update", "Measure mixed transactions and correctness"),
            ("SP2Bench", "Exercise SPARQL operator diversity"), ("LDBC SNB BI", "Exercise analytical graph joins under rules"),
            ("LDBC SNB interactive", "Exercise updates and latency if a compliant adapter exists"), ("point lookup", "Measure minimum serving latency"),
            ("one-hop", "Measure degree-stratified adjacency"), ("multi-hop bounded", "Measure selective traversal"),
            ("property path adversarial", "Expose combinatorial resource behavior"), ("reasoning", "Separate dynamic and materialized costs"),
            ("bulk load", "Report parse, commit, index and optimize phases"), ("stream ingest", "Report durable small-batch p99"),
            ("update churn", "Include delete, optimize and storage debt"), ("cold query", "Charge first-touch local storage"),
            ("warm query", "Declare cache residency"), ("checkpoint query", "Capture periodic tails"),
            ("node failure", "Score availability and lost acknowledgements"), ("network partition", "Score consistency and convergence"),
            ("shard split", "Charge downtime and operator work"), ("backup restore", "Charge RPO, RTO and all storage"),
            ("one-billion scale", "Publish exact resources and cost"), ("one-trillion scale", "Require measured run rather than linear extrapolation"),
            ("PB physical", "Define logical versus physical bytes"), ("thousand-trillion projection", "Label infeasible or unvalidated dimensions honestly"),
            ("competitor roster", "Pin popular engines, editions and tuning rules"), ("same semantics", "Map RDF/property-graph differences without weakening workloads"),
            ("same durability", "Align acknowledgement and replica policy"), ("same cost", "Cap compute, RAM, SSD, network, licenses and labor"),
            ("10x confidence", "Bootstrap ratios and publish uncertainty"), ("regression veto", "Reject universal claim when a declared family loses"),
            ("raw release", "Publish every sample, timeout and exclusion"), ("third-party audit", "Have independent reviewers reproduce headline cells"),
        ]],
    },
    "07-design-lessons-and-proposed-architecture.md": {
        "title": "AllegroGraph design lessons and proposed S3-native architecture",
        "scope": "What to reuse, what to reject, and a concrete low-latency distributed fixed-cost architecture and validation path",
        "intro": """
        AllegroGraph demonstrates the value of term dictionaries, explicit index permutations, two execution strategies, standards-based semantics and separation between partitioning and replication. Its documented operational caveats also make the target architecture sharper: avoid making local SSD replicas the durable source of truth; avoid seven universal permutations; avoid broadcast as the default distributed plan; avoid offline split as normal elasticity; and fence metadata control with epochs and leases.

        The proposed engine stores immutable, content-addressed graph segments in S3. A small strongly consistent catalog publishes manifests and epochs. Compute nodes cache dictionary, vertex and adjacency blocks on local NVMe and RAM; disaggregated cache loss never loses committed data. Writes enter bounded replicated ingest logs, are sorted into partitioned immutable segments, uploaded and atomically published. Compaction rewrites objects without mutating published generations. Query planning uses partition summaries, learned/histogram statistics and strict fan-out budgets.
        """,
        "extra": [
            ("Immutable authority", "S3 objects should be the durable data plane, with checksummed manifests and atomic metadata publication.", "Design proposal,S50"),
            ("Thin control plane", "A consensus catalog should store epochs, manifests, schemas, leases and placement—not graph payloads.", "Design proposal"),
            ("Term dictionary", "Reuse dictionary encoding but shard immutable term tables and cache hot IDs to avoid one global mutable bottleneck.", "Lesson from S07"),
            ("Minimal indices", "Build only query-justified permutations and projections, using workload telemetry rather than seven defaults.", "Lesson from S07"),
            ("Adjacency segments", "Partition by stable vertex/edge locality and encode compressed neighbor blocks for low-I/O bounded hops.", "Design proposal"),
            ("Cache contract", "RAM/NVMe caches are disposable accelerators with versioned keys; cold S3 access remains correct and measurable.", "Design proposal,S50"),
            ("Write path", "Replicated ingest journals acknowledge according to declared durability, then flush immutable sorted objects and publish manifests.", "Design proposal"),
            ("Compaction", "Generation-based compaction preserves snapshot readers and makes rollback an atomic manifest choice.", "Design proposal"),
            ("Partition pruning", "Min/max, Bloom, predicate, degree and graph summaries should prevent broadcast before execution.", "Lesson from S15-S17"),
            ("Bounded traversal", "Every query receives hop, frontier, byte, shard, CPU and deadline budgets with resumable continuations.", "Lesson from S09"),
            ("Replication separation", "Durable objects, metadata consensus, ingest durability and serving replicas must expose distinct health and consistency contracts.", "Lesson from S14-S19"),
            ("Fixed-cost mechanism", "Hard concurrency, cache, compaction, request and egress budgets—not autoscaling promises—enforce the monthly envelope.", "Design proposal"),
            ("RDF/property bridge", "Use stable IDs and typed columns so RDF terms and property-graph adjacency share physical segments without semantic ambiguity.", "Design proposal,S48,S49"),
            ("Benchmark discipline", "A 10x target is a falsifiable workload-family hypothesis, never a universal adjective.", "Lesson from S32,S44-S49"),
        ],
        "tests": [(x, y) for x, y in [
            ("manifest atomicity", "Publish one complete generation or none"), ("catalog leader loss", "Fence stale writers with epochs"),
            ("object checksum", "Detect corruption before serving"), ("object immutability", "Prevent overwrite of published content"),
            ("journal quorum", "Align acknowledgement with declared durability"), ("journal replay", "Recover idempotently after crash"),
            ("flush publication", "Make uploaded segments visible atomically"), ("compaction snapshot", "Preserve readers across generation rewrite"),
            ("compaction rollback", "Return to the previous manifest without data copy"), ("dictionary race", "Assign stable IDs under concurrent ingest"),
            ("dictionary cache miss", "Bound cold term resolution"), ("adjacency cache hit", "Target sub-millisecond local block access"),
            ("adjacency S3 miss", "Measure request count and tail latency"), ("range coalescing", "Minimize object requests for multi-hop expansion"),
            ("partition summary", "Prove no false negatives in pruning"), ("hot vertex", "Split or replicate supernode adjacency safely"),
            ("skew rebalance", "Move serving placement without rewriting durable ownership"), ("online repartition", "Publish new segment generations without query downtime"),
            ("frontier budget", "Stop adversarial traversal predictably"), ("continuation token", "Resume with snapshot and no duplicates"),
            ("shard budget", "Reject or degrade plans before broadcast"), ("memory budget", "Spill or stop without process death"),
            ("cold start", "Serve correctly from catalog and S3 with empty caches"), ("cache loss", "Lose every NVMe cache without data recovery"),
            ("region loss", "Restore catalog and objects under stated RPO/RTO"), ("read snapshot", "Bind queries to immutable manifests"),
            ("write conflict", "Provide explicit serializable or constrained semantics"), ("RDF oracle", "Differentially test terms and SPARQL"),
            ("property graph oracle", "Differentially test paths and mutation semantics"), ("one-billion prototype", "Measure bytes, p99 and S3 requests"),
            ("one-trillion qualification", "Measure distributed query and recovery"), ("PB qualification", "Measure physical object footprint and restore"),
            ("fixed-cost soak", "Run a month-equivalent request and compaction model"), ("10x comparator", "Apply same semantics, durability and monthly cost"),
            ("upgrade generation", "Change encodings via side-by-side immutable rewrite"), ("exit export", "Produce standards-valid RDF and open columnar segments"),
        ]],
    },
}


def build(name: str, spec: dict[str, object]) -> None:
    d = Doc(str(spec["title"]), str(spec["scope"]))
    d.h(2, "Audit outcome")
    d.p(str(spec["intro"]))
    if name == "00-index.md":
        d.h(2, "Dossier map")
        d.p("""
        1. [Product, releases, licensing, and evidence](./01-product-releases-licensing-and-evidence.md)
        2. [Storage, indices, IDs, and data model](./02-storage-indices-ids-and-data-model.md)
        3. [SPARQL, Prolog, query engines, and reasoning](./03-sparql-prolog-query-engines-and-reasoning.md)
        4. [Transactions, MMR, FedShard, and correctness](./04-transactions-mmr-fedshard-and-correctness.md)
        5. [Operations, resources, security, S3, and cost](./05-operations-resources-security-s3-and-cost.md)
        6. [Benchmark audit, trillion scale, and 10x protocol](./06-benchmark-audit-trillion-scale-and-10x.md)
        7. [Design lessons and proposed S3-native architecture](./07-design-lessons-and-proposed-architecture.md)
        """)
    d.table(
        ["Dimension", "Audited status", "Target implication"],
        [
            ["Low latency", "Plausible with warm mapped indices; workload-specific and unmeasured here", "Test cold, warm, checkpoint and saturation tails"],
            ["Low resource", "Default index and memory guidance are substantial", "Minimize permutations and make caches disposable"],
            ["Distributed", "FedShard partitions; MMR replicates", "Keep placement, durability and capacity contracts separate"],
            ["Fixed S3 cost", "S3 is archive/import, not live authority", "Use immutable object segments plus hard budgets"],
            ["PB / extreme edges", "Historical trillion load; no PB or thousand-trillion proof", "Require measured staged qualification"],
            ["10x", "No current audited universal result", "Use correctness-first family-specific ratios"],
        ],
    )
    d.findings("Audited findings", COMMON + list(spec["extra"]))
    d.cases(
        "Qualification matrix",
        cases(name.removesuffix(".md"), list(spec["tests"]), "Pinned AllegroGraph 9.0.2 topology plus an independent semantic oracle and fault-controlled harness", "S01-S50", True),
    )
    d.sources()
    d.write(name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.md"):
        old.unlink()
    for name, spec in TOPICS.items():
        build(name, spec)
    print(f"generated {len(TOPICS)} AllegroGraph specs in {OUT}")


if __name__ == "__main__":
    main()
