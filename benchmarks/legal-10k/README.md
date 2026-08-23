# GLAW 10,000-Question Attorney Benchmark

This package is a source-controlled benchmark lifecycle, not a claim that the
draft rows are legally validated. The scaffold creates exactly 10,000 rows with
the approved domain allocation, deterministic splits, and typed challenge cases.
Questions, authorities, and gold decisions remain empty until imported from
source-backed packets and reviewed by two independent named attorneys.

The `source-packets.jsonl` file contains a small primary-source-backed pilot
covering DGCL §122(18), *In re Match Group*, and Meta's SEC-filed 2025 proxy.
`source-backed-pilot.jsonl` is import-ready but intentionally has no gold
decisions: attorney reviews and adjudication are still required before release.

## Workflow

```bash
bin/glaw-legal-benchmark scaffold
bin/glaw-legal-benchmark validate
bin/glaw-legal-benchmark reviewer-register --input counsel-001.json
bin/glaw-legal-benchmark import --input sourced-items.jsonl
bin/glaw-legal-benchmark review --input review-packet.json
bin/glaw-legal-benchmark adjudicate --input adjudication.json
bin/glaw-legal-benchmark release
bin/glaw-legal-benchmark evaluate --input model-results.jsonl
```

Import the pilot with:

```bash
bin/glaw-legal-benchmark import --input benchmarks/legal-10k/source-backed-pilot.jsonl
bin/glaw-legal-benchmark audit
```

Run the source-loaded pilot through both independent attorney-AI lanes:

```bash
bin/glaw-dual-attorney
```

The default adapters are Anthropic for Alexandra and OpenAI for Victor. If
credentials or SDK adapters are unavailable, the run is recorded as
`AGENT_UNAVAILABLE` and the Governor returns `REVIEW_REQUIRED`; no synthetic
opinion or gold label is created.

Use `--require-complete` in release automation when both provider passes are a
hard prerequisite. It exits nonzero with `BLOCKED` if either selected agent is
unavailable or returns invalid output; exploratory runs may still emit a
review-required evidence package.

Only released rows enter evaluation. Disagreements require an independent third
attorney adjudicator. `items.jsonl` contains gold records; model outputs belong
under a separate run directory and cannot mutate the gold files.

After both first passes complete, initialize the cross-review protocol with
`bin/glaw-dual-attorney --cross-review`. The resulting run directory is then
advanced only by the hash-bound sequence
`bin/glaw-cross-review record`: red cross-review, blue rebuttal, red
sur-rebuttal, and independent adjudication. `check` remains `BLOCK` until all
four phases are present and the adjudicator records `RESOLVED`; even then the
Governor remains `REVIEW_REQUIRED` pending human counsel approval.
