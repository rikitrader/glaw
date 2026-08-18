# GLAW Legal RAG + Governor Architecture

GLAW is currently a zero-dependency Python/Bash matter system with a Cloudflare
Worker intake surface. The production safety boundary is the matter folder and
its append-only, hash-checked workpapers. Provider-backed services are adapters;
they are not treated as legal authority.

```text
question
  -> premise + jurisdiction
  -> immutable source universe
  -> lexical / semantic-adapter / citation-graph retrieval
  -> completeness gate
  -> independent Claude + Codex records
  -> atomic claims and claim-source graph
  -> citation / quote / holding / precedent / temporal checks
  -> adverse authority + two red-team lenses
  -> deterministic Legal Governor
  -> PASS | REVIEW_REQUIRED | BLOCK
```

The repository's existing stage gates remain authoritative for intake, ethics,
adversarial review, final-packet readiness, and filing. The Governor chain is
activated by `bin/glaw-legal-governor matrix --matter-slug <slug>` or
`legal_governor_required: true` in `intake.json`. Once activated, missing or
stale Governor workpapers block final-packet and file readiness.

## Trust boundaries

- Raw source text is immutable and hashed before normalization or chunking.
- Retrieved documents are data, never instructions.
- Provider adapters may propose analysis but cannot write a PASS decision.
- Drafting reads verified claims and cannot mutate verification records.
- Human counsel remains required for consequential legal instruments.

Semantic retrieval, external legal databases, PostgreSQL/pgvector, and live model
providers are intentionally unavailable until configured. The system reports
`UNAVAILABLE` or `REVIEW_REQUIRED`; it never substitutes fake data.
