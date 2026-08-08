# Aerospike Graph product, releases, compatibility, and evidence audit

Research cut: `2026-08-08`
Evidence status: current-source audit; vendor claims remain claims until reproduced
Maintenance: manually maintained Markdown; no documentation generator
Scope: What product exists as of the research cut and how confidently each assertion can be made
Pinned AGS source: `ad0983e5519cbd3705f70113afd7df048c568045` (`3.3.0-SNAPSHOT`, branch `3.x-dev`)
Newest prerelease observed: `v3.3.0-rc5` at `f4980a73f64bde1f3db0b30e917f3ec7fb147ce3`; not the stable baseline
Shipped release baseline: `Aerospike Graph 3.2.3`, released 2026-06-30

## Version-qualified conclusion

Use `3.2.3` as the released security baseline, not `latest`. Record the image digest. Treat the public `3.x-dev` source as a forward-looking `3.3.0-SNAPSHOT` anatomy reference. It is unusually valuable because it exposes the AGS implementation, but it is not byte-for-byte evidence for the 3.2.3 image: the public repository has no release tag that closes that chain.

The operational product is a composition: Gremlin driver, load balancer, one or more AGS JVMs, Aerospike Java client, one Aerospike Database namespace, optional Spark bulk/OLAP jobs, metrics/tracing systems, and backup/restore tools. A result that omits any required tier is not a product result.

## Release chronology

| Version | Date | Material change | Audit treatment |
| --- | --- | --- | --- |
| 3.3.0-rc5 | 2026-08-08 | Signed rehearsal/prerelease tag; readiness gate and packaging/CI changes after audited branch head | Freshest code tag, not stable product baseline |
| 3.2.3 | 2026-06-30 | Security patch: fourteen CVEs | Preferred 3.2 baseline |
| 3.2.2 | 2026-05-14 | Removed graph-service feature requirement; health reports AGS version | Does not erase DB edition feature boundaries |
| 3.2.1 | 2026-04-08 | Container-aware memory, rack awareness, repeat/emit and edge-memory changes | Recheck memory and locality |
| 3.2.0 | 2026-03-23 | Set cardinality, global cache, runtime config, 10x g.E scan claim | Major behavior/performance boundary |
| 3.1.1 | 2025-12-02 | Critical Jersey dependency security update | Do not baseline 3.1.0 |
| 3.1.0 | 2025-10-23 | TinkerPop transactions, typed vertex indexes, performance changes | Requires Database 8 for released transaction contract |
| 3.0.0 | 2025-07-24 | New packed representation, multi-properties, datetime, bulk changes | Reload/migration and storage boundary |
| 2.6.0 | 2025-04-18 | Query threading and TLS simplification | Pre-3 storage format |
| 2.5.0 | 2025-02-12 | Query isolation distinctions and tracing-era changes | Historical |
| 2.4.2 | 2024-12-12 | Read-throughput fix | Version used by 2025 identity benchmark |

## Latest-publication freshness sweep

The freshness sweep did not stop at release notes. The material Graph-specific vendor posts found were the 2.5 strong-consistency launch on 2025-04-10, the 3.0 storage-and-load launch on 2025-07-29, and the Graph AI/MCP article on 2025-09-30. The September article is the newest Graph-specific blog found, but it demonstrates an MCP server translating natural-language requests into Gremlin and exposing metadata/configuration resources; it does not announce a newer persistence model, query engine, consistency contract, or scale result. It therefore belongs in the integration/tooling evidence lane and cannot supersede 2026 release documentation.

The 2.5 post is materially useful because it states the boundary marketing summaries often omit: Database 8-backed transactions apply to mutations in an SC namespace, while read-only queries remain eventually consistent. The 3.0 post contributes vendor claims about bulk-load time and footprint, not an independently reproducible cross-engine benchmark. Later 3.2 release notes and the pinned 3.3 prerelease source remain the stronger authorities for current behavior.

A second freshness check found documentation drift in backup guidance. The Graph backup page delegates to Database tools but currently links directly to `asbackup`, whose Database page now labels it legacy. The current Database overview presents Aerospike Backup Service and `absctl` alongside the legacy tools. This audit therefore requires an explicit Graph-qualified restore drill with the chosen modern tool; it does not silently assume that a generic Database backup preserves every Graph index, metadata object, consistency boundary, and query-ready state.

| Publication | Date | What it actually adds | What it does not prove |
| --- | --- | --- | --- |
| Graph 2.5 strong consistency | 2025-04-10 | Mutation transaction positioning, DB 8 dependency, eventual-read caveat | Snapshot-consistent read traversals or AP-mode transactions |
| Graph 3.0 launch | 2025-07-29 | Vendor load-time and footprint claims for the new representation | Competitor-normalized 10x or PB/trillion scale |
| Graph AI/MCP | 2025-09-30 | Natural-language/demo integration and exposed operational resources | A new AGS engine release or latency result |
| Graph 3.2.3 release docs | 2026-06-30 | Current stable security baseline | Source-to-image equivalence for public 3.x-dev |
| AGS v3.3.0-rc5 tag | 2026-08-08 | Freshest public prerelease packaging/readiness state | Stable production status |

## Product and licensing boundary

The AGS repository is Apache-2.0. Aerospike Database Community Edition uses the AGPLv3 core, while Standard, Enterprise, and Federal editions add commercial capabilities. The published edition table caps Community Edition at eight nodes and 2.5 TB of cluster data. That makes Community Edition useful for functional work but unsuitable as evidence for the intended PB deployment.

Strong consistency, multi-record transactions, rack awareness, TLS and ACL support, XDR, and several operational features cross edition or add-on boundaries. Aerospike describes production Enterprise licensing primarily in terms of unique production data volume rather than operations, servers, or cores. A real cost model therefore needs a written definition of billable graph data plus a quote covering Graph entitlement, SC, MRT, disaster recovery, support, and non-production environments.

Release 3.2.2 removed a graph-service feature check at startup. That code change does not move every underlying Database feature into Community Edition. Likewise, a one-node evaluation key proves neither production entitlement nor distributed fixed cost.

## Source-to-release gap

The audited AGS source commit was dated 2026-08-07, identifies itself as `3.3.0-SNAPSHOT`, and pins TinkerPop 3.7.3, Java source target 11, Spark 3.5.8, and Aerospike Java client 10.3.0. Its compatibility prose says client 9.3.x, demonstrating documentation drift inside the repository. The POM is the build authority for the commit.

The repository has signed `v3.3.0-rc1` through `v3.3.0-rc5` tags but no observed `3.2.x` source tag or GitHub release object that closes the stable-image provenance chain. The diff from the audited default-branch commit to rc5 changes packaging, container, Helm, smoke-test, and CI files, not Java or Kotlin engine source. The implementation anatomy is therefore current enough to study, while rc5 still remains a prerelease. The audit cannot assert that the 3.2.3 Docker image has identical source.

A benchmark checkout should include a small, boring artifact manifest. The important property is that another engineer can identify the exact image without trusting a mutable tag.

```bash
image='aerospike/aerospike-graph-service:3.2.3'
docker pull "$image"
docker image inspect "$image" \
  --format '{{json .RepoDigests}}' > ags-image-digests.json
docker image inspect "$image" > ags-image-inspect.json

# Save the runtime response and deployed configuration beside the image data.
curl --fail --silent "http://ags.example.internal/health" > ags-health.json
kubectl get deployment ags -o yaml > ags-deployment.yaml
```

The same bundle needs the container SBOM, Maven coordinates, Database build, namespace configuration, feature-key output, Gremlin driver version, and the date on which the image was pulled. Without those files, a later rerun can silently execute different code.

## Product qualification cases

### Reading release evidence without mixing versions

The released product, the public development source, and the historical
benchmark are three different artifacts. Release 3.2.3 is the supported
security baseline at the research cut. The public source commit identifies
itself as 3.3.0-SNAPSHOT and is useful for reconstructing modules, record
layouts, strategies, defaults, and test intent. The identity benchmark uses
AGS 2.4.2 and Database 7.1.0.9. None of these identities can be silently
substituted for another. A source observation is written as a statement about
the pinned commit; a released behavior is tied to the 3.2.3 documentation and
image; a benchmark observation remains tied to 2.4.2. This discipline matters
because releases 3.0, 3.1, and 3.2 changed storage representation,
transactions, cache behavior, scan controls, and dependency security.

The top-level POM is executable evidence for the development snapshot. Its
relevant literal extract is short:

```xml
<aerospike-client.version>10.3.0</aerospike-client.version>
<tinkerpop.version>3.7.3</tinkerpop.version>
```

The values come from the pinned
[`pom.xml`](https://github.com/aerospike/aerospike-graph-service/blob/ad0983e5519cbd3705f70113afd7df048c568045/pom.xml).
They are more precise for that commit than compatibility prose elsewhere in the
repository that still refers to a 9.3.x client line. They do not establish the
dependencies inside the released 3.2.3 image. That image needs its own digest,
SBOM, Maven metadata, runtime health response, and effective configuration. A
serious regression report attaches those artifacts rather than writing
`version: latest` in a chart caption.

Licensing has a similar evidence boundary. Removing an AGS startup feature
check in 3.2.2 says what the service no longer refuses at boot; it does not
grant Community Edition strong consistency, MRT, XDR, rack awareness, or the
production support terms advertised for paid editions. The public edition page
is enough to identify decision points but not enough to calculate a quote. The
procurement record must define unique production data for graph records,
replicas, indexes, DR copies, and retained backups, then state which add-ons and
non-production clusters are billable. Until the contract answers those points,
license cost is unknown rather than zero.

| Evidence object | What it can establish | What it cannot establish |
| --- | --- | --- |
| 3.2.3 release notes | Declared fixes and supported release chronology | Exact container dependencies or performance magnitude |
| 3.2.3 image digest and SBOM | Exact shipped packages in the tested artifact | Proprietary Database internals or future support terms |
| Pinned 3.3.0-SNAPSHOT source | Implementation anatomy and defaults at that commit | Byte identity with the 3.2.3 image |
| Signed 3.3.0-rc5 tag | Prerelease packaging and readiness state | General availability or production support |
| Identity benchmark PDF | Vendor-observed scale, hardware, and summary results | Current 3.2 behavior, raw distributions, or competitor ranking |
| Edition page | Public feature and scale boundaries | Reproducible production price |
| Written quote and order form | Billable units, add-ons, support, and environments | Technical performance without a measured run |

These cases form the release and procurement checklist. Start from a fresh namespace and record the AGS image digest, Database build, driver coordinates, namespace configuration, feature-key output, and license assumptions. Historical replays use their original Database and AGS versions in isolated environments; they never replace the current 3.2.3 qualification run.

For each case, keep the raw command output and timestamps. A version mismatch, undocumented feature rejection, mutable image, incomplete SBOM, or missing contract definition is the result. Do not turn it into a performance number. Price, entitlement, and support questions remain unknown until the corresponding written vendor document is attached.

<table>
<thead>
<tr>
<th>Case</th>
<th>Subject</th>
<th>Engineering question</th>
<th>Evidence</th>
</tr>
</thead>
<tbody>
<tr>
<td>Q001</td>
<td>product: image digest pinning</td>
<td>Prove all nodes run the same immutable AGS build.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q002</td>
<td>product: 3.2.3 health version</td>
<td>Verify health output reflects the intended patch.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q003</td>
<td>product: container SBOM</td>
<td>Identify dependency and CVE closure, including transitive libraries.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q004</td>
<td>product: TinkerPop 3.7.3 driver</td>
<td>Prove client/server bytecode compatibility.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q005</td>
<td>product: TinkerPop 3.8 rejection</td>
<td>Record the exact incompatible-client failure.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q006</td>
<td>product: Java 17 container runtime</td>
<td>Measure actual runtime and GC defaults.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q007</td>
<td>product: Database 8.1.2 compatibility</td>
<td>Use the latest supported DB patch as of the cut.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q008</td>
<td>product: Database 7.1 benchmark replay</td>
<td>Separate historical-paper reproduction from current-product qualification.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q009</td>
<td>product: Community Edition startup</td>
<td>Discover whether basic AGS CRUD starts after the 3.2.2 feature-check removal.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q010</td>
<td>product: Community Edition scale cap</td>
<td>Verify enforced and contractual limits rather than extrapolating.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q011</td>
<td>product: Enterprise feature key</td>
<td>Inventory exact licensed capabilities needed by the selected mode.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q012</td>
<td>product: SC add-on</td>
<td>Confirm contract, entitlement, and runtime namespace mode.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q013</td>
<td>product: MRT add-on</td>
<td>Confirm transaction availability and server stats.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q014</td>
<td>product: rack-awareness add-on</td>
<td>Confirm client preference and server rack topology.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q015</td>
<td>product: XDR add-on</td>
<td>Keep asynchronous cross-cluster replication out of local-ACID claims.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q016</td>
<td>product: production price quote</td>
<td>Convert contact pricing into a reproducible monthly cost model.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q017</td>
<td>product: unique-data definition</td>
<td>Determine whether graph expansion, indexes, replicas, backup, and DR are licensed bytes.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q018</td>
<td>product: non-production terms</td>
<td>Separate free development from production cost.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q019</td>
<td>product: Graph entitlement</td>
<td>Determine whether AGS has a separate commercial/support line item.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q020</td>
<td>product: support SLA</td>
<td>Charge required support tier and response commitments.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q021</td>
<td>product: 3.0 reload boundary</td>
<td>Prove upgrade/migration behavior for 2.x data.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q022</td>
<td>product: 3.1 transaction boundary</td>
<td>Prove explicit transaction behavior only on supported Database versions.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q023</td>
<td>product: 3.2 global cache boundary</td>
<td>Treat cache mode as semantic configuration.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q024</td>
<td>product: 3.2.0 scan improvement</td>
<td>Reproduce version-over-version g.E claim on fixed hardware.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q025</td>
<td>product: 3.2.1 memory change</td>
<td>Measure RSS/heap before and after edge materialization.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q026</td>
<td>product: 3.2.3 CVE closure</td>
<td>Scan the exact baseline image.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q027</td>
<td>product: 3.3.0-rc5</td>
<td>Track prerelease packaging/readiness changes without promoting it to stable evidence.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q028</td>
<td>product: latest tag drift</td>
<td>Detect mutable-tag changes during a benchmark campaign.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q029</td>
<td>product: multi-tenant graph names</td>
<td>Prove tenant routing and config isolation.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q030</td>
<td>product: slim image</td>
<td>Measure attack surface and missing bulk-loader behavior.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q031</td>
<td>product: standard image</td>
<td>Charge bundled tooling and image footprint.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q032</td>
<td>product: Docker deployment</td>
<td>Qualify local reproducibility, not distributed production readiness.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q033</td>
<td>product: Kubernetes chart</td>
<td>Pin chart/app/image versions independently.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q034</td>
<td>product: Aerospike Cloud</td>
<td>Keep managed service results separate from same-hardware results.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q035</td>
<td>product: aerolab examples</td>
<td>Treat provisioning scripts as examples, not support contracts.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q036</td>
<td>product: source license inventory</td>
<td>Verify AGS plus dependency redistribution obligations.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q037</td>
<td>product: server dual license files</td>
<td>Distinguish community source from closed Enterprise additions.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q038</td>
<td>product: client Apache license</td>
<td>Establish driver integration license posture.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q039</td>
<td>product: Spark dependency</td>
<td>Pin Spark runtime and cloud distribution.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q040</td>
<td>product: S3 SDK dependency</td>
<td>Qualify bulk-load credential and endpoint behavior.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q041</td>
<td>product: security advisory feed</td>
<td>Make patch monitoring part of baseline lifecycle.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q042</td>
<td>product: release note completeness</td>
<td>Cross-check behavior changes against issues/tests and runtime diff.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q043</td>
<td>product: configuration migration</td>
<td>Diff defaults across 3.0, 3.1, and 3.2.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q044</td>
<td>product: data-model metadata</td>
<td>Capture on-disk major/minor compatibility before upgrade.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q045</td>
<td>product: rollback</td>
<td>Prove whether old AGS can reopen data after a new version starts.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
<tr>
<td>Q046</td>
<td>product: backup compatibility</td>
<td>Restore into exact, newer, and unsupported older versions.</td>
<td>S01–S08,S28–S33,S45–S50</td>
</tr>
</tbody>
</table>

## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

<table>
<thead>
<tr>
<th>ID</th>
<th>Source</th>
<th>Class</th>
<th>Audit use</th>
<th>Link</th>
</tr>
</thead>
<tbody>
<tr>
<td>S01</td>
<td>AGS release index</td>
<td>Official documentation</td>
<td>2026-06-30 latest listed release</td>
<td>https://aerospike.com/docs/graph/release</td>
</tr>
<tr>
<td>S02</td>
<td>AGS 3.2.3 release notes</td>
<td>Official documentation</td>
<td>Security-only patch; 14 CVEs listed</td>
<td>https://aerospike.com/docs/graph/release/3-2-3/</td>
</tr>
<tr>
<td>S03</td>
<td>AGS 3.2.2 release notes</td>
<td>Official documentation</td>
<td>Removed graph-service feature check</td>
<td>https://aerospike.com/docs/graph/release/3-2-2/</td>
</tr>
<tr>
<td>S04</td>
<td>AGS 3.2.1 release notes</td>
<td>Official documentation</td>
<td>Container memory and rack awareness</td>
<td>https://aerospike.com/docs/graph/release/3-2-1/</td>
</tr>
<tr>
<td>S05</td>
<td>AGS 3.2.0 release notes</td>
<td>Official documentation</td>
<td>Global cache, set cardinality, performance changes</td>
<td>https://aerospike.com/docs/graph/release/3-2-0/</td>
</tr>
<tr>
<td>S06</td>
<td>AGS 3.1.1 release notes</td>
<td>Official documentation</td>
<td>CVE-2025-12383 fix</td>
<td>https://aerospike.com/docs/graph/release/3-1-1/</td>
</tr>
<tr>
<td>S07</td>
<td>AGS 3.1.0 release notes</td>
<td>Official documentation</td>
<td>TinkerPop transactions and typed indexes</td>
<td>https://aerospike.com/docs/graph/release/3-1-0/</td>
</tr>
<tr>
<td>S08</td>
<td>AGS 3.0.0 release notes</td>
<td>Official documentation</td>
<td>Packed model revision and reload boundary</td>
<td>https://aerospike.com/docs/graph/release/3-0-0/</td>
</tr>
<tr>
<td>S16</td>
<td>TinkerPop feature support</td>
<td>Official documentation</td>
<td>Feature compatibility matrix</td>
<td>https://aerospike.com/docs/graph/overview/tinkerpop/</td>
</tr>
<tr>
<td>S22</td>
<td>Graph backup and restore</td>
<td>Official documentation</td>
<td>Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page</td>
<td>https://aerospike.com/docs/graph/manage/backup/</td>
</tr>
<tr>
<td>S26</td>
<td>Graph 3.0 launch blog</td>
<td>Vendor blog</td>
<td>Ingest and footprint claims</td>
<td>https://aerospike.com/blog/aerospike-graph-3-release/</td>
</tr>
<tr>
<td>S28</td>
<td>Product editions and pricing</td>
<td>Official commercial page</td>
<td>Edition limits and data-volume licensing</td>
<td>https://aerospike.com/products/features-and-editions/</td>
</tr>
<tr>
<td>S29</td>
<td>Database platform support</td>
<td>Official documentation</td>
<td>Current Database release matrix</td>
<td>https://aerospike.com/docs/database/reference/platform-support</td>
</tr>
<tr>
<td>S32</td>
<td>Database FAQ</td>
<td>Official documentation</td>
<td>CE/SE/EE/FE boundaries</td>
<td>https://aerospike.com/docs/database/reference/faq</td>
</tr>
<tr>
<td>S33</td>
<td>AGS public source snapshot</td>
<td>Apache-2.0 source</td>
<td>3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045</td>
</tr>
<tr>
<td>S45</td>
<td>Apache TinkerPop 3.7.3 reference</td>
<td>Upstream documentation</td>
<td>Language/runtime semantic oracle</td>
<td>https://tinkerpop.apache.org/docs/3.7.3/reference/</td>
</tr>
<tr>
<td>S46</td>
<td>AGS v3.3.0-rc5 prerelease tag</td>
<td>Signed public source tag</td>
<td>Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
<td>https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3</td>
</tr>
<tr>
<td>S47</td>
<td>Graph 2.5 strong-consistency launch blog</td>
<td>Vendor blog</td>
<td>Database 8 transaction positioning and the explicit eventual-read caveat</td>
<td>https://aerospike.com/blog/aerospike-graph-2-5-0-strong-consistency</td>
</tr>
<tr>
<td>S48</td>
<td>Aerospike Graph AI and MCP blog</td>
<td>Vendor blog</td>
<td>Newest Graph-specific blog found in the publication sweep; an integration/demo layer, not a storage-engine release</td>
<td>https://aerospike.com/blog/aerospike-graph-ai-mcp-natural-language-queries/</td>
</tr>
<tr>
<td>S49</td>
<td>Legacy asbackup documentation</td>
<td>Official documentation</td>
<td>The target of the current Graph backup-page link; explicitly labeled legacy</td>
<td>https://aerospike.com/docs/database/tools/backup-and-restore/asbackup</td>
</tr>
<tr>
<td>S50</td>
<td>Current Database backup and restore overview</td>
<td>Official documentation</td>
<td>ABS and absctl are current choices while asbackup/asrestore are legacy</td>
<td>https://aerospike.com/docs/database/tools/backup-and-restore/overview/</td>
</tr>
</tbody>
</table>
