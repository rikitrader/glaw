# GLAW Training Gym — Durable Project Memory

Last updated: 2026-09-01

## Current state

The Training Gym core and productionization foundation are implemented under `training-gym/`.

Implemented and tested:

- deterministic/resettable gym interfaces;
- Spreadsheet, Salesforce, Slack, composite, and professional-domain gyms;
- task generation, evaluators, trajectories, replay, benchmark comparison, exports, skills, and synthetic organizations;
- explicit episode state machine;
- idempotent retryable job queue with heartbeats and dead-letter handling;
- experiment expansion and local episode worker execution;
- remote worker protocol with lease claim, heartbeat, trajectory submission, evaluation, completion, and failure handling;
- PostgreSQL episode repository adapter using parameterized SQL and tenant predicates;
- Insurance Claims Gym with synthetic policy/evidence/estimate review tasks;
- Claim-to-law bridge and defensible report pipeline that fails closed on unresolved legal authority and preserves the executed episode state;
- Tenant-aware experiment service with immutable version configuration, paired-seed expansion, launch validation, and cancellation state;
- object-store abstraction with hashing and local in-memory adapters;
- provider, browser-boundary, quota, concurrency, tenant-isolation, reproducibility, and aggregation contracts;
- PostgreSQL reference migration at `migrations/0001_training_gym_postgres.sql`;
- audit, risk, and production test documentation.

## Verified result

The local suite currently passes **22/22 tests**. `git diff --check` passes.

## Explicitly open production integrations

These must not be represented as complete until executed against real dependencies:

- managed PostgreSQL connection and repository integration tests;
- durable queue backend and independently deployed worker processes;
- S3-compatible object storage and signed URLs;
- real OpenAI, Anthropic, Gemini, OpenRouter, and custom-endpoint adapters;
- external secret management;
- isolated Playwright/browser workers;
- authenticated dashboard and replay UI;
- OpenTelemetry logs, metrics, and traces;
- Docker/deployment manifests;
- load and chaos testing at meaningful scale;
- shared world state for cross-application composite gyms.

## Next milestone

Wire the SQL repository and queue interfaces to the repository's actual runtime/database stack, add worker/API entrypoints, and run an end-to-end experiment through durable persistence. Preserve the existing gym interfaces and keep all unverified integrations explicitly marked open.

## Strategic assessment

The Training Gym can create a meaningful competitive advantage for GLAW because it turns legal and claims work into reproducible, resettable, adversarially evaluated simulations. It can test whether an AI actually follows policy-first reasoning, uses evidence, preserves uncertainty, cites authority, calculates damages correctly, and survives Red/Blue/White review. This is materially stronger than a law-firm chatbot that is evaluated mainly by prose quality.

The advantage is not automatic. It becomes defensible only when GLAW has proprietary high-quality claim fixtures, verified legal/policy ground truth, independent evaluators, realistic multi-application workflows, private benchmarks, human-reviewed failure labels, and measured improvement across model versions. The gym measures and improves an AI law firm; it does not replace authoritative legal sources, licensed counsel, or production integrations.

## Readiness conclusion

Current status: strong architecture and local contract testing; pilot-ready with limitations; not yet production-ready for real legal decisions or 100k distributed episodes. Full details are in `../GLAW_SYSTEM_READINESS_AUDIT.md`.

## Important engineering rule

Do not claim production-scale readiness based only on local in-memory tests. Keep infrastructure failures, agent failures, and evaluator failures separately classified.
