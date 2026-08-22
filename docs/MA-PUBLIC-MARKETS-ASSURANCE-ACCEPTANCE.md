# Production Acceptance Gates

The M&A, public-markets, and analytical-assurance expansion is production-ready only when
these gates pass for the relevant lane.

## Gate 1 — Source and provenance

- Every material input has a `SRC-####` source ID.
- Source hashes are recorded in the append-only source ledger.
- Stale or changed source hashes fail validation.
- Untrusted documents are treated as data, not instructions.

## Gate 2 — Structured workpaper

- The lane exists in `lib/lane-catalog.json`.
- The seat exists under `seats/` with the canonical identity/soul markers.
- The workpaper validates against the lane engine.
- Owner, version, status, artifacts, and next action are present.

## Gate 3 — Calculation and reconciliation

- Model-specific calculations use the relevant deterministic engine where one exists.
- Ownership, proceeds, multiples, certainty-adjusted values, and totals reconcile.
- Model-quality review covers formulas, links, units, sensitivities, and scenario behavior.
- Material errors force `revise_required`.

## Gate 4 — Artifact integrity

- JSON, XLSX, PPTX, DOCX, Markdown, and HTML outputs are listed in an artifact manifest.
- Each artifact has a SHA-256 hash and status.
- Approved lane workpapers may reference only approved artifacts.

## Gate 5 — Analytical assurance

- Valuations, recommendations, scenarios, and public-market analyses receive a structured review.
- Head-to-head comparisons use the rubric and material-error penalties.
- Missing evidence produces abstention or `insufficient_evidence`.

## Gate 6 — Human authority

- High-impact transaction, capital-structure, portfolio, public-disclosure, payment, and board
  decisions remain human-approved.
- The system never signs, files, pays, publishes, or communicates solely on an automated score.

## Gate 7 — Deployment and regression

- `./setup` deploys every seat to both Claude and Codex mirrors.
- `./bin/glaw-test` passes with zero violations.
- The M&A/public-markets/assurance contract tests pass.
- `glaw-doctor` reports mirror parity and seat deployment parity.

## Verification commands

```bash
./bin/glaw-test
./test/analytical_review_test.sh
./test/transaction_comps_test.sh
./test/cap_table_waterfall_test.sh
./test/transaction_terms_test.sh
./test/lane_engine_test.sh
./test/ma_public_assurance_contract_test.sh
./test/source_ledger_test.sh
./test/all_lanes_test.sh
./test/extended_finance_engines_test.sh
```
