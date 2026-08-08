# Graph Database Research

Source-audited research on graph database architecture, correctness, latency,
resource efficiency, distributed execution, object-storage economics, and
reproducible benchmark qualification.

This repository asks a deliberately difficult systems question: what would an
engine need to prove to serve very-low-latency graph queries over PB-scale and
trillion-edge datasets while using bounded compute and S3-class durable
storage? It audits existing engines for reusable ideas and evidence gaps; it
does not turn vendor claims into measured facts.

## Research principles

- Pin released source, documentation, images, and benchmark artifacts.
- Separate shipped behavior from development branches.
- Label source facts, official statements, vendor claims, issue reports,
  local observations, inferences, and unknowns.
- Treat exact result semantics and durability as benchmark prerequisites.
- Account for clients, caches, replicas, indexes, background work, recovery,
  and operator time when comparing resources or cost.
- Publish raw, reproducible artifacts before making a 10x claim.

## Repository layout

- [`docs/`](./docs/) contains architecture specifications, the engine
  landscape, source audits, and benchmark protocols.
- [`src/`](./src/) contains corpus maintenance scripts and repository
  validation tools. Dedicated Aerospike research is maintained directly as
  reviewed Markdown rather than generated output.
- [CONTRIBUTING.md](./CONTRIBUTING.md) defines evidence and change standards.

## Status

Research is current to the date recorded in each specification. Database
releases, pricing, source heads, issues, and managed-service behavior change;
revalidate decision-critical claims before adopting them.

Start with:

- [Research corpus index](./docs/research/000-index.md)
- [Cross-engine landscape](./docs/research/system-landscape-scorecard.md)
- [Target architecture](./docs/research/system-target-architecture.md)
- [Reproducible benchmark and 10x protocol](./docs/research/system-benchmark-and-10x-claim.md)

Deep source audits:

- [Aerospike Graph](./docs/research/aerospike/00-index.md)
- [AgensGraph](./docs/research/agensgraph/00-index.md)
- [AllegroGraph](./docs/research/allegrograph/00-index.md)

## License

The repository's original text and scripts are available under the
[MIT License](./LICENSE). Linked third-party sources, product names, and quoted
material remain subject to their respective owners and licenses.
