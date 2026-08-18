# Legal Governor Contract

## Internal statuses

`PASS`, `PASS_WITH_RISK`, `RESEARCH_REQUIRED`, `LEGAL_REVIEW_REQUIRED`, and
`BLOCK` are preserved internally. External consumers may render them as
`PASS`, `REVIEW_REQUIRED`, or `BLOCK`.

## PASS requirements

A governed PASS requires resolved jurisdiction and premise handling, verified
primary authority, complete or calibrated-likely-complete retrieval, supported
material claims, complete adverse-authority search, verified quotation/holding/
precedent/temporal records, independent model parity, surviving red-team review,
and an evidence-derived confidence vector. A model's self-reported confidence is
never sufficient.

## Commands

```bash
bin/glaw-legal-governor scaffold --matter-slug SLUG
bin/glaw-legal-governor source-ingest --matter-slug SLUG --input source.json
bin/glaw-legal-governor context-build --matter-slug SLUG --input rag.json
bin/glaw-legal-governor parity-record --matter-slug SLUG --agent claude --context-sha256 HASH --analysis claude.md
bin/glaw-legal-governor parity-record --matter-slug SLUG --agent codex --context-sha256 HASH --analysis codex.md
bin/glaw-legal-governor bundle-check --matter-slug SLUG --input verification-bundle.json
bin/glaw-legal-governor assess --matter-slug SLUG --input legal-governor-input.json
bin/glaw-legal-governor final-check --matter-slug SLUG
```

`final-check` is fail-closed and is also enforced by `glaw-final-packet` and
`glaw-gate` for activated matters.
