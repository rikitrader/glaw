# ADR-0005: Model and Skill Governance

Status: proposed

## Decision

No application service calls a model vendor directly. A Model Gateway routes by
task, risk, residency, measured benchmark, cost, and latency. Skills are signed,
versioned, schema-bound, permission-scoped, benchmarked, and sandboxed.

## Consequence

Provider and community-skill changes require policy checks, canaries, rollback,
and explicit compatibility; model brand is not a business or safety authority.
