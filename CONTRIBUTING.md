# Contributing

Contributions should make the research more reproducible, current, or
decision-useful.

## Evidence requirements

1. Attach a retrieval date to mutable web evidence.
2. Pin source links to a commit or immutable release tag where possible.
3. Distinguish observations from documentation, claims, issue reports, and
   inferences.
4. Preserve workload scope around every performance number.
5. Do not infer PB capacity, distribution, or object-store authority from an
   identifier limit, backup feature, or small benchmark.
6. Record unknowns instead of filling commercial or closed-source gaps with
   assumptions.

## Research pull requests

Keep one deeply audited engine or one cross-engine concern per pull request.
Include the source/release baseline, the important architectural findings,
validation performed, and any remaining evidence gaps. Generated Markdown and
its generator must change together.

## Validation

Run the repository validator before publishing:

```sh
python3 src/validate_repository.py
```

When changing a generator, run it and ensure the working tree remains clean.
