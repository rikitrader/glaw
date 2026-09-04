# GLAW Master Completion Checklist

Owner: GLAW engineering workflow
Last audited: 2026-09-01

Status values: `[x]` verified implemented and tested, `[~]` partial/contract-only, `[ ]` open.

## A. Repository and GStack controls

- [x] Inventory control-plane, legal compiler, property claims, and Training Gym.
- [x] Preserve stable interfaces and document integration boundaries.
- [x] Run type checks and production build.
- [x] Run unit and contract tests.
- [x] Run operational restore, chaos-disposition, redaction, rollback, and local-load checks.
- [~] Run full GStack plan → review → QA → ship → deploy → canary loop.
- [ ] Add CI gates for typecheck, tests, security, migrations, benchmarks, and legal-rule changes.
- [ ] Add release checklist requiring evidence, rollback plan, and canary result.

## B. GLAW control plane

- [x] Matter, workflow, approval, authorization, and audit tables exist.
- [x] Authenticated control-plane routes exist.
- [x] Tenant predicates exist on current control-plane routes.
- [~] Connect Training Gym experiments and episodes to control-plane identity and tenants (tenant-aware service boundary and authenticated D1 routes implemented; deployed worker-service mounting remains).
- [~] Add Training Gym experiment/episode/replay/review API routes (experiment create/list, launch, cancel, episode list/detail, evaluation, and replay-reference routes implemented; human review and signed artifact delivery remain).
- [ ] Add pagination, request validation, idempotency, and cancellation to those routes.
- [ ] Add API authorization tests for every Training Gym resource.
- [ ] Add rate limits and abuse controls.

## C. Property Claims and Legal Compiler

- [x] Policy-first claim architecture and safe rule DSL.
- [x] Temporal, provenance, citation, authority hierarchy, conflict, and human-gate interfaces.
- [x] Florida matching policy dependency and fail-closed tests.
- [~] Florida statutory and case-law source corpus.
- [ ] Complete historical Florida §626.9744 versions and applicability.
- [ ] Retrieve and hash full Florida opinions with verified pinpoints.
- [ ] Complete Florida DCA conflict analysis.
- [ ] Ingest actual claim policy, declarations, forms, and endorsements.
- [ ] Complete Florida production rules after source and human gates.
- [ ] Populate Texas primary corpus and historical rules.
- [ ] Complete California, New York, Colorado, and remaining jurisdictions in batches.
- [ ] Add live official-source fetch, snapshot, re-verification, and change promotion.
- [ ] Replace placeholder research loop with authority-specific retrieval and parsing.
- [ ] Add legal corpus observability and state completeness dashboard.

## D. Training Gym foundation

- [x] Deterministic reset, seed, snapshots, restore, replay, and state deltas.
- [x] Spreadsheet, Salesforce, Slack, composite, professional, and Insurance Claims Gym fixtures.
- [x] Task generation, evaluators, trajectory capture, exports, skills, and benchmarks.
- [x] Episode state machine, quotas, idempotency, retries, heartbeat, and dead-letter contracts.
- [x] Experiment expansion and local worker execution.
- [~] Composite gyms share routing but not one durable world state.
- [ ] Build shared digital-twin state service for cross-application workflows.
- [ ] Add independent evaluator process and protected hidden ground truth.
- [~] Add durable trajectory artifact-reference API and lease-aware worker submission (object-store worker wiring and state-snapshot persistence remain).

## E. Durable infrastructure

- [x] PostgreSQL reference migration and parameterized episode repository adapter.
- [x] Object-store interface, local adapter, checksums, and path safety.
- [~] PostgreSQL adapter wired to a driver and runtime configuration.
- [ ] Connect the canonical production database strategy: D1-compatible control plane or PostgreSQL boundary, with documented ownership.
- [ ] Add real queue adapter with visibility timeout, lease recovery, retries, and DLQ.
- [~] Implement remote runner protocol with claim, heartbeat, trajectory submission, completion, and failure endpoints (deployment, evaluator/browser/export workers remain).
- [ ] Add transactional outbox or equivalent event delivery guarantee.
- [ ] Add crash recovery and duplicate-delivery integration tests.
- [ ] Add S3-compatible object store, signed URLs, retention, and checksum verification.

## F. Model and browser execution

- [x] Model-independent provider interface and deterministic test provider.
- [x] Browser-to-simulation boundary contract.
- [ ] Implement OpenAI adapter.
- [ ] Implement Anthropic adapter.
- [ ] Implement Gemini adapter.
- [ ] Implement OpenRouter/OpenAI-compatible adapter.
- [ ] Add provider retries, rate limits, request IDs, usage, cost, and timeout handling.
- [ ] Add external secret management and agent-visible secret denial.
- [ ] Implement isolated browser worker using approved automation runtime.
- [ ] Add browser reset, recording, screenshot, upload/download, and network policy tests.

## G. Security and governance

- [x] Explicit tool allowlists and fail-closed mutation model.
- [x] Tenant assertion contract and audit-oriented identifiers.
- [~] Control-plane auth/RBAC exists; Training Gym enforcement is not end-to-end.
- [ ] Complete RBAC for gyms, datasets, tasks, experiments, episodes, exports, and reviews.
- [ ] Test tenant isolation at API, database, object store, queue, and UI layers.
- [ ] Prevent evaluator/hidden-ground-truth modification by agents.
- [ ] Add prompt-injection tests for policies, emails, documents, and browser pages.
- [ ] Add artifact malware/type/size scanning and path traversal tests.
- [ ] Add secret scanning, dependency scanning, and OWASP/STRIDE review.
- [ ] Add immutable audit event retention and access review.

## H. Dashboard and user workflow

- [x] Existing control-plane dashboard builds.
- [~] Operational pages and static registries exist.
- [ ] Add authenticated Training Gym overview.
- [ ] Add experiment creation, progress, cancellation, and result pages.
- [x] Add authenticated episode detail, evaluation, trajectory-reference, and replay-reference routes.
- [ ] Add browser screenshot/state-diff viewer.
- [ ] Add model comparison, skills, costs, and failure taxonomy.
- [ ] Add human review queue and automatic/human score separation.
- [ ] Run browser QA against deployed staging environment.

## I. Observability and operations

- [~] Local operational scripts and deterministic load baseline.
- [ ] Add structured logs with experiment/episode/worker/tenant IDs.
- [ ] Add metrics for queue, workers, providers, browser, database, storage, cost, and failures.
- [ ] Add distributed traces and redaction.
- [ ] Add health/readiness endpoints for API and workers.
- [ ] Add alert thresholds and runbooks.
- [ ] Add cost accounting by organization, experiment, model, and episode.
- [ ] Add live dashboards and retention policies.

## J. Scale, recovery, and release

- [ ] Run 10-episode smoke test on deployed stack.
- [ ] Run 100-episode integration test.
- [ ] Run 1,000 paired-model episode test.
- [ ] Run 10,000 episode load test.
- [ ] Establish 100,000 queued-episode capacity test.
- [ ] Run worker crash recovery.
- [ ] Run queue interruption/redelivery test.
- [ ] Run database restart/failover test.
- [ ] Run object-storage outage test.
- [ ] Run provider timeout/429/5xx test.
- [ ] Run browser crash/isolation test.
- [ ] Run evaluator crash/retry test.
- [ ] Produce measured load and chaos reports.
- [ ] Containerize API, workers, browser worker, database, queue, and object storage substitute.
- [ ] Deploy staging, run GStack QA, canary, rollback, and post-deploy verification.

## K. Data, benchmarks, and training

- [x] JSONL training export and preference-pair foundation.
- [ ] Add Parquet export.
- [ ] Enforce TRAIN/DEV/VALIDATION/PRIVATE_TEST export boundaries.
- [ ] Make published benchmarks immutable and versioned.
- [ ] Add 40+ tasks per initial Gym across difficulty levels.
- [ ] Add adversarial, permission, prompt-injection, and reward-hacking tasks.
- [ ] Add reference solutions and task validation.
- [ ] Add model comparison with paired seeds and confidence intervals.
- [ ] Add human-approved training sample workflow.

## Definition of done

- [ ] Live authenticated researcher creates an experiment.
- [ ] Experiment expands into durable idempotent episode jobs.
- [ ] Independent workers execute isolated environments.
- [ ] Trajectories and large artifacts persist durably.
- [ ] Evaluators execute outside agent control.
- [ ] Results aggregate and display in the dashboard.
- [ ] A trajectory replays deterministically.
- [ ] The same experiment can be reproduced from pinned versions and seed.
- [ ] Live load and chaos evidence is recorded.
- [ ] Legal/claims outputs remain source-verified, policy-specific, temporal, and human-gated where required.
