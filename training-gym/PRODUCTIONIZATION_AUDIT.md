# Training Gym Productionization Audit

Date: 2026-09-01

## EXISTING

- Versioned gym/task abstractions, deterministic reset/seed, snapshots, replay, state deltas, evaluators, trajectory recording, benchmark runner, exports, skills, synthetic organization data, and fail-closed sandbox policy.
- Spreadsheet, Salesforce, Slack, composite, and professional-domain adapters.
- Baseline: 14 tests passed before productionization work.

## PARTIAL

- Durable execution contracts are now present for episode states, retryable jobs, idempotency, quotas, object references, provider normalization, tenant context, browser-to-simulation bridging, reproducibility pins, persistence interfaces, aggregation, experiment expansion, a SQL repository adapter, and a local runner worker loop.
- These contracts currently use in-process adapters for local tests; a production deployment must bind them to the repository's durable database, queue, object storage, and identity systems.
- Composite gyms route to subgyms but do not yet provide a shared cross-application world state.
- The worker loop can run locally; a production deployment still must bind the SQL repository and queue interfaces to managed services and execute crash-recovery tests.

## MISSING

- PostgreSQL repository implementation; a reference migration is present at `migrations/0001_training_gym_postgres.sql` but has not been applied or integration-tested in this repository.
- S3-compatible object-store adapter and signed URLs.
- Durable queue adapter, worker processes, heartbeats across restarts, and dead-letter dashboard.
- Real provider HTTP adapters and secret-manager integration.
- Playwright/browser worker, frontend dashboard, OpenTelemetry exporter, deployment manifests, and load/chaos harness.

## BROKEN

- No known baseline failures. Production defects cannot be ruled out until durable integration tests run against PostgreSQL, queue, object storage, and isolated browser workers.

## MOCKED

- `DeterministicProvider` is intentionally test-only.
- `MemoryObjectStore` and `InMemoryJobQueue` are local adapters, not production persistence.

## PRODUCTION-RISK

- Do not claim 100k-episode readiness until distributed load, tenant-isolation, crash-recovery, and cost/telemetry tests execute against deployed dependencies.
- Do not expose hidden task criteria or provider credentials to agents.
- Existing core abstractions remain stable; adapters must be added without changing evaluator authority.
