# Model Map

## Current evidence

- Claude and Codex CLI provider modes are documented and explicit.
- Optional API/provider and embedding configuration is documented in `.env.example`.
- Provider absence is intended to fail closed.
- No canonical model registry, benchmark router, canary mechanism, or unified
  cost/latency telemetry store is confirmed.

## Required target

Introduce a Model Gateway and registry with pinned versions, residency policy,
structured-output enforcement, budgets, fallback policy, benchmark thresholds,
shadow/canary rollout, and no silent substitution.
