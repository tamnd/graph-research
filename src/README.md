# Documentation generators

Generators in this directory produce deterministic Markdown under `docs/`.
Each dedicated engine dossier has its own subdirectory so released and
development source pins, source registers, and qualification matrices can
evolve independently.

Current dedicated generators cover Aerospike Graph, AgensGraph, and
AllegroGraph. The AllegroGraph generator deliberately distinguishes its
proprietary server from the commit-pinned public clients and container tooling.
