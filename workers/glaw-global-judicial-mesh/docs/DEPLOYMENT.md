# Production deployment

The repository is configuration-valid, but sentinel placeholder values intentionally block deployment until real Cloudflare resources and approved provider credentials exist. The deployment validator detects placeholder names and all-zero resource IDs, required bindings, production mode, and versioned migrations. It does not verify secret values or human legal review; those remain explicit deployment gates.

## Provision resources

Create these resources in the target account:

    npx wrangler d1 create glaw-judicial-mesh
    npx wrangler r2 bucket create glaw-judicial-documents
    npx wrangler kv namespace create CACHE
    npx wrangler queues create glaw-judicial-ingestion
    npx wrangler vectorize create glaw-legal-v1 --dimensions=1536 --metric=cosine

Copy the returned D1 and KV IDs into wrangler.jsonc and replace the Worker, bucket, queue, database, and Vectorize placeholders. Never put secrets in the config file.

## Configure secrets

    npx wrangler secret put GLAW_API_KEY --config wrangler.jsonc
    npx wrangler secret put GLAW_ADMIN_API_KEY --config wrangler.jsonc
    npx wrangler secret put GLAW_TENANT_ID --config wrangler.jsonc
    npx wrangler secret put COURTLISTENER_TOKEN --config wrangler.jsonc

Configure `GLAW_ALLOWED_ORIGINS` as an environment-specific secret or deployment variable when a browser client is used. Production CORS is deny-by-default; local development allows all origins.

Use separate secrets and resources for staging and production.

## Migrate and deploy

    npm run db:migrate:remote
    npm run predeploy
    npm run deploy

After deployment, run the read-only live verifier with `GLAW_LIVE_BASE_URL`, `GLAW_LIVE_API_KEY`, and `GLAW_LIVE_TENANT_ID` (optionally `GLAW_LIVE_OTHER_TENANT_ID`) set in the shell: `npm run verify:live`. It checks liveness, all readiness checks, missing-tenant rejection, wrong-tenant rejection, and authenticated routing without creating case or discovery records. It does not replace live backup/restore, failure-mode, or human legal-review validation.

The predeploy check blocks placeholder IDs, secrets in configuration, type errors, and failing tests. deploy:dry-run is available before deployment.

For local runtime verification, start `npm run dev -- --port 8788` in one terminal and run `npm run smoke:local` in another. The smoke test verifies liveness, D1/KV/R2 readiness, tenant rejection, and fail-closed discovery auditing, then writes a uniquely identified local matter/request to exercise the end-to-end audit state machine. `/health` is liveness only; `/ready` returns 503 unless the required bindings respond. The local-only smoke credential is configured in `wrangler.local.jsonc` and must never be copied to production.

## Activate providers

The migrations also create the judge-profile identity, source, observation, case-observation, adversarial-review, matter, procedural-event, discovery-object, filing-artifact, and human-review tables. The migration seeds every provider as DISCOVERED and non-routable. For each provider, submit evidence-backed review decisions to POST /v1/providers/:id/review for termsReviewed, schemaValidated, authorityValidated, and securityReviewed. Then call POST /v1/providers/:id/activate with the admin credential.

No provider becomes routable without all four gates and explicit approval.

## Remaining production gates

- The current authenticated Cloudflare account has a production Queue (`glaw-judicial-ingestion-production`), Vectorize index (`glaw-legal-v1-production`, 1536 dimensions/cosine), and KV namespace bound in the config. The account currently reports its D1 database limit and R2 is not enabled, so no unrelated D1 may be repurposed and deployment remains blocked until an administrator provisions capacity and enables R2.
- Generic international adapters remain metadata-only until their source contracts are implemented and reviewed.
- PACER requires separately authorized credentials and terms review.
- Vectorize is bound but semantic ingestion and RAG are not complete.
- Full multi-tenant RBAC, MCP, Astro administration, citation graph expansion, and source-backed automated legal QA remain roadmap work. The current judge API uses a configured single-tenant boundary (`GLAW_TENANT_ID`) and admin-gated profile writes.
- In production, every `/v1/*` request must include `x-tenant-id` matching `GLAW_TENANT_ID`; judge and matter routes additionally enforce their scoped matter/judge relationships. Local development retains the explicit local-only exception.
- Tenant context is included in research fan-out context, search-cache keys, and queued ingestion envelopes; verify this isolation in live multi-tenant integration tests before release.
- The filing state machine ends at `HUMAN_REVIEW_REQUIRED`; `READY_TO_FILE` is unavailable until a named human reviewer confirms it. Automated prediction and adversarial outputs are model-based leads, not rulings or legal advice.
- Filing advancement requires evidence/review-artifact IDs at each substantive gate; the final gate also checks that all eight review stages have recorded evidence. Missing or legacy gate metadata causes a fail-closed transition error.
- Filing evidence references must resolve to tenant-scoped records using `source:<id>`, `event:<id>`, `discovery:<id>`, `authority:<id>`, `adversarial:<id>`, or `prediction:<id>`; arbitrary labels are rejected.
- Filing evidence references must also be status-verified: sources/events/discovery/authorities must be `VERIFIED`, adversarial runs must be `APPROVED`, and predictions must be human-approved.
- Request findings distinguish `CONCEDE`, `SUPPLEMENT`, `OBJECT`, and `NO_RESPONSIVE_DOCUMENTS` from `RECORD_REQUIRED`; the latter is reserved for missing source record fields.
- Filing evidence is additionally bound to the matter’s assigned judge. A matter without a recorded judge cannot advance a filing gate using evidence references.
- Matter discovery audits include both verified matter-specific authorities and verified judge-level authorities; records remain tenant- and judge-scoped.
- Matter judge assignment is immutable after first assignment; reassignments are blocked to preserve the provenance of historical evidence, predictions, and filing reviews.
- Judge-linked matter records require an assigned judge; an unassigned matter cannot receive judge observations, predictions, authorities, or comparable-case records.
- Authenticated `/v1` requests write a non-sensitive action record to D1 `audit_logs`, including request ID, route, tenant, and matter scope when available. Audit-write failures are logged operationally and never alter the legal payload returned to the caller.
- Known scope, verification, integrity, and filing-transition failures return safe deterministic 4xx responses with a request ID; unexpected failures remain generic 500 responses.
- Authority relationships and adversarial runs have separate review ledgers. They remain `UNVERIFIED`/`HUMAN_REVIEW_REQUIRED` until an administrator records a scoped decision with required evidence or review notes.
- A judge observation, comparable case, authority, or authority edge linked to a source cannot be promoted to `VERIFIED` while that source remains unverified.
- Client-supplied `VERIFIED` status is ignored for newly ingested procedural events and discovery objects; ingestion always starts at `UNVERIFIED` and requires a later evidence-backed review workflow.
- Human reviewers use `POST /v1/matters/:matterId/events/:eventId/reviews` and `POST /v1/matters/:matterId/discovery/:discoveryId/reviews`; review decisions are recorded in append-only D1 ledgers and require independent evidence for `VERIFIED`.
- Review history is available through the tenant/matter-scoped `GET /v1/matters/:matterId/events/:eventId/reviews` and `GET /v1/matters/:matterId/discovery/:discoveryId/reviews` endpoints.
- Filing transitions are also recorded in `filing_gate_events` and exposed through `GET /v1/matters/:matterId/filings/:artifactId/gate-events`, including prior state, evidence references, blockers, and final human confirmation. The local smoke test exercises this ledger with a real first-stage transition.
- Restarting a blocked filing at `DRAFT` clears prior gate evidence; every subsequent review cycle must establish fresh evidence for every gate.
- Written-discovery deadline output is conservative: the audit can expose a labeled candidate date from a recorded service date, but always requires verification of service method, exceptions, extensions, orders, and current rule text. It does not calculate deposition deadlines.
- Request throttling fails safe: a missing or non-numeric `GLAW_RATE_LIMIT_PER_MINUTE` uses the bounded default, and configured values are limited to a finite integer range.

Do not represent this system as production legal-advice infrastructure until those controls pass independent review and live integration tests.
