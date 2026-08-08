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

These cases form the release and procurement checklist. Start from a fresh namespace and record the AGS image digest, Database build, driver coordinates, namespace configuration, feature-key output, and license assumptions. Historical replays use their original Database and AGS versions in isolated environments; they never replace the current 3.2.3 qualification run.

For each case, keep the raw command output and timestamps. A version mismatch, undocumented feature rejection, mutable image, incomplete SBOM, or missing contract definition is the result. Do not turn it into a performance number. Price, entitlement, and support questions remain unknown until the corresponding written vendor document is attached.

### Q001 : product: image digest pinning

**Purpose.** Prove all nodes run the same immutable AGS build.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q002 : product: 3.2.3 health version

**Purpose.** Verify health output reflects the intended patch.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q003 : product: container SBOM

**Purpose.** Identify dependency and CVE closure, including transitive libraries.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q004 : product: TinkerPop 3.7.3 driver

**Purpose.** Prove client/server bytecode compatibility.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q005 : product: TinkerPop 3.8 rejection

**Purpose.** Record the exact incompatible-client failure.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q006 : product: Java 17 container runtime

**Purpose.** Measure actual runtime and GC defaults.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q007 : product: Database 8.1.2 compatibility

**Purpose.** Use the latest supported DB patch as of the cut.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q008 : product: Database 7.1 benchmark replay

**Purpose.** Separate historical-paper reproduction from current-product qualification.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q009 : product: Community Edition startup

**Purpose.** Discover whether basic AGS CRUD starts after the 3.2.2 feature-check removal.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q010 : product: Community Edition scale cap

**Purpose.** Verify enforced and contractual limits rather than extrapolating.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q011 : product: Enterprise feature key

**Purpose.** Inventory exact licensed capabilities needed by the selected mode.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q012 : product: SC add-on

**Purpose.** Confirm contract, entitlement, and runtime namespace mode.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q013 : product: MRT add-on

**Purpose.** Confirm transaction availability and server stats.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q014 : product: rack-awareness add-on

**Purpose.** Confirm client preference and server rack topology.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q015 : product: XDR add-on

**Purpose.** Keep asynchronous cross-cluster replication out of local-ACID claims.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q016 : product: production price quote

**Purpose.** Convert contact pricing into a reproducible monthly cost model.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q017 : product: unique-data definition

**Purpose.** Determine whether graph expansion, indexes, replicas, backup, and DR are licensed bytes.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q018 : product: non-production terms

**Purpose.** Separate free development from production cost.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q019 : product: Graph entitlement

**Purpose.** Determine whether AGS has a separate commercial/support line item.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q020 : product: support SLA

**Purpose.** Charge required support tier and response commitments.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q021 : product: 3.0 reload boundary

**Purpose.** Prove upgrade/migration behavior for 2.x data.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q022 : product: 3.1 transaction boundary

**Purpose.** Prove explicit transaction behavior only on supported Database versions.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q023 : product: 3.2 global cache boundary

**Purpose.** Treat cache mode as semantic configuration.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q024 : product: 3.2.0 scan improvement

**Purpose.** Reproduce version-over-version g.E claim on fixed hardware.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q025 : product: 3.2.1 memory change

**Purpose.** Measure RSS/heap before and after edge materialization.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q026 : product: 3.2.3 CVE closure

**Purpose.** Scan the exact baseline image.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q027 : product: 3.3.0-rc5

**Purpose.** Track prerelease packaging/readiness changes without promoting it to stable evidence.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q028 : product: latest tag drift

**Purpose.** Detect mutable-tag changes during a benchmark campaign.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q029 : product: multi-tenant graph names

**Purpose.** Prove tenant routing and config isolation.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q030 : product: slim image

**Purpose.** Measure attack surface and missing bulk-loader behavior.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q031 : product: standard image

**Purpose.** Charge bundled tooling and image footprint.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q032 : product: Docker deployment

**Purpose.** Qualify local reproducibility, not distributed production readiness.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q033 : product: Kubernetes chart

**Purpose.** Pin chart/app/image versions independently.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q034 : product: Aerospike Cloud

**Purpose.** Keep managed service results separate from same-hardware results.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q035 : product: aerolab examples

**Purpose.** Treat provisioning scripts as examples, not support contracts.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q036 : product: source license inventory

**Purpose.** Verify AGS plus dependency redistribution obligations.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q037 : product: server dual license files

**Purpose.** Distinguish community source from closed Enterprise additions.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q038 : product: client Apache license

**Purpose.** Establish driver integration license posture.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q039 : product: Spark dependency

**Purpose.** Pin Spark runtime and cloud distribution.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q040 : product: S3 SDK dependency

**Purpose.** Qualify bulk-load credential and endpoint behavior.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q041 : product: security advisory feed

**Purpose.** Make patch monitoring part of baseline lifecycle.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q042 : product: release note completeness

**Purpose.** Cross-check behavior changes against issues/tests and runtime diff.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q043 : product: configuration migration

**Purpose.** Diff defaults across 3.0, 3.1, and 3.2.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q044 : product: data-model metadata

**Purpose.** Capture on-disk major/minor compatibility before upgrade.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q045 : product: rollback

**Purpose.** Prove whether old AGS can reopen data after a new version starts.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


### Q046 : product: backup compatibility

**Purpose.** Restore into exact, newer, and unsupported older versions.

**Evidence anchors.** S01–S08,S28–S33,S45–S50


## Source register

The retrieval date for web sources is the research cut. Git sources are pinned by commit. A source being official establishes what was stated or implemented; it does not independently establish a performance claim.

### S01 : AGS release index

**Type.** Official documentation

**Audit note.** 2026-06-30 latest listed release

**URL.** https://aerospike.com/docs/graph/release


### S02 : AGS 3.2.3 release notes

**Type.** Official documentation

**Audit note.** Security-only patch; 14 CVEs listed

**URL.** https://aerospike.com/docs/graph/release/3-2-3/


### S03 : AGS 3.2.2 release notes

**Type.** Official documentation

**Audit note.** Removed graph-service feature check

**URL.** https://aerospike.com/docs/graph/release/3-2-2/


### S04 : AGS 3.2.1 release notes

**Type.** Official documentation

**Audit note.** Container memory and rack awareness

**URL.** https://aerospike.com/docs/graph/release/3-2-1/


### S05 : AGS 3.2.0 release notes

**Type.** Official documentation

**Audit note.** Global cache, set cardinality, performance changes

**URL.** https://aerospike.com/docs/graph/release/3-2-0/


### S06 : AGS 3.1.1 release notes

**Type.** Official documentation

**Audit note.** CVE-2025-12383 fix

**URL.** https://aerospike.com/docs/graph/release/3-1-1/


### S07 : AGS 3.1.0 release notes

**Type.** Official documentation

**Audit note.** TinkerPop transactions and typed indexes

**URL.** https://aerospike.com/docs/graph/release/3-1-0/


### S08 : AGS 3.0.0 release notes

**Type.** Official documentation

**Audit note.** Packed model revision and reload boundary

**URL.** https://aerospike.com/docs/graph/release/3-0-0/


### S16 : TinkerPop feature support

**Type.** Official documentation

**Audit note.** Feature compatibility matrix

**URL.** https://aerospike.com/docs/graph/overview/tinkerpop/


### S22 : Graph backup and restore

**Type.** Official documentation

**Audit note.** Graph delegates recovery to the underlying Database tooling; its current link still lands on the legacy asbackup page

**URL.** https://aerospike.com/docs/graph/manage/backup/


### S26 : Graph 3.0 launch blog

**Type.** Vendor blog

**Audit note.** Ingest and footprint claims

**URL.** https://aerospike.com/blog/aerospike-graph-3-release/


### S28 : Product editions and pricing

**Type.** Official commercial page

**Audit note.** Edition limits and data-volume licensing

**URL.** https://aerospike.com/products/features-and-editions/


### S29 : Database platform support

**Type.** Official documentation

**Audit note.** Current Database release matrix

**URL.** https://aerospike.com/docs/database/reference/platform-support


### S32 : Database FAQ

**Type.** Official documentation

**Audit note.** CE/SE/EE/FE boundaries

**URL.** https://aerospike.com/docs/database/reference/faq


### S33 : AGS public source snapshot

**Type.** Apache-2.0 source

**Audit note.** 3.x-dev at ad0983e5519cbd3705f70113afd7df048c568045

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/ad0983e5519cbd3705f70113afd7df048c568045


### S45 : Apache TinkerPop 3.7.3 reference

**Type.** Upstream documentation

**Audit note.** Language/runtime semantic oracle

**URL.** https://tinkerpop.apache.org/docs/3.7.3/reference/


### S46 : AGS v3.3.0-rc5 prerelease tag

**Type.** Signed public source tag

**Audit note.** Newest public prerelease observed on 2026-08-08; commit f4980a73f64bde1f3db0b30e917f3ec7fb147ce3

**URL.** https://github.com/aerospike/aerospike-graph-service/tree/f4980a73f64bde1f3db0b30e917f3ec7fb147ce3


### S47 : Graph 2.5 strong-consistency launch blog

**Type.** Vendor blog

**Audit note.** Database 8 transaction positioning and the explicit eventual-read caveat

**URL.** https://aerospike.com/blog/aerospike-graph-2-5-0-strong-consistency


### S48 : Aerospike Graph AI and MCP blog

**Type.** Vendor blog

**Audit note.** Newest Graph-specific blog found in the publication sweep; an integration/demo layer, not a storage-engine release

**URL.** https://aerospike.com/blog/aerospike-graph-ai-mcp-natural-language-queries/


### S49 : Legacy asbackup documentation

**Type.** Official documentation

**Audit note.** The target of the current Graph backup-page link; explicitly labeled legacy

**URL.** https://aerospike.com/docs/database/tools/backup-and-restore/asbackup


### S50 : Current Database backup and restore overview

**Type.** Official documentation

**Audit note.** ABS and absctl are current choices while asbackup/asrestore are legacy

**URL.** https://aerospike.com/docs/database/tools/backup-and-restore/overview/
