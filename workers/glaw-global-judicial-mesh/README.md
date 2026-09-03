# GLAW Global Judicial Mesh

Phase 1 implementation of the GLAW Global Legal Research Router: a Hono API on Cloudflare Workers with typed provider adapters, deterministic jurisdiction resolution, parallel source fan-out, canonical normalization, authority scoring, D1 metadata, R2 provenance artifacts, KV caching, Queue ingestion, and a Durable Object coordination primitive.

## Current vertical slice

`question → Hono → jurisdiction resolver → CourtListener / RECAP adapters → normalize → deduplicate → rank → D1/R2 → Queue`

CourtListener and RECAP are separate adapter identities over the authorized CourtListener REST surface. RECAP/PACER access is intentionally not implemented as scraping or credential bypass. Credentials are Worker secrets only, and providers with no approved API return no data until their terms and schema are reviewed.

The priority provider adapters now include Juriscraper, WorldLII, CommonLII, AsianLII, PacLII, HKLII, and Kenya Law. They are explicit `GenericLegalSourceAdapter` subclasses with coverage metadata in `src/coverage.ts`; they are not network clients yet and remain `DISCOVERED`/non-routable. Juriscraper is modeled as a future remote scraper-service boundary because the upstream project is Python-based and court-specific scraping must be separately governed.

## Judge profile engine

The Worker also exposes an evidence-backed judge-profile layer. It records versionable observations with provenance and status, stores them in D1, sequences profile events through the `JudgeProfileCoordinator` Durable Object, and generates a transparent evidence-weighted heuristic prediction. Predictions are explicitly `humanReview: REQUIRED`; the system does not infer personal traits or claim to know a judge's private psychology.

Routes: `GET /v1/judges/:judgeId/profile`, admin-only `POST /v1/judges/:judgeId/identity`, `POST /v1/judges/:judgeId/observations`, `POST /v1/judges/:judgeId/predictions`, `POST /v1/judges/:judgeId/engine`, `POST /v1/judges/:judgeId/sources`, `POST /v1/judges/:judgeId/sources/official`, `POST /v1/judges/:judgeId/source-reviews`, `POST /v1/judges/:judgeId/case-observations`, `POST /v1/judges/:judgeId/observation-reviews`, `POST /v1/judges/:judgeId/case-observation-reviews`, `POST /v1/judges/:judgeId/authorities`, `POST /v1/judges/:judgeId/authority-reviews`, `POST /v1/judges/:judgeId/authority-edges`, `POST /v1/judges/:judgeId/authority-edge-reviews`, `POST /v1/judges/:judgeId/profile-reviews`, `POST /v1/judges/:judgeId/adversarial-reviews`, and `POST /v1/judges/:judgeId/adversarial-review-decisions`. The profile endpoint returns tenant/judge-scoped identity, sources, observations, comparable cases, authorities, predictions, adversarial runs, and engine reports; each remains visibly review-gated. The engine returns six transparent decision modes, three strategies, and a reproducible 1,000-iteration uncertainty simulation; all are evidence-bound, non-psychological, model-based leads and require human choice. The simulation is expressly not an empirical judicial probability. Every judge route requires `x-tenant-id`; production also requires the configured `GLAW_TENANT_ID` binding to match it. New observations, sources, predictions, case observations, authority records, authority edges, and adversarial reports remain human-review gated. Source content is hashed and stored in R2; only an administrator can register source material or verify evidence, and every source, authority, or authority-edge verification requires independent evidence. Run `npm run db:migrate:local` before using the routes locally. The engine is deployable with the existing Workers, D1, R2, Queue, KV, Vectorize, and Durable Object bindings; configure placeholder production resource IDs and tenant secrets before deployment.

The matter/discovery workflow adds tenant-scoped routes for `POST /v1/matters`, `GET /v1/matters/:matterId`, procedural events, discovery objects, `GET /v1/matters/:matterId/discovery-audit`, admin-only `GET /v1/matters/:matterId/audit-log`, filing artifacts, and filing-state transitions. Human review uses `POST /v1/matters/:matterId/events/:eventId/reviews` and `POST /v1/matters/:matterId/discovery/:discoveryId/reviews`; each decision is recorded in an append-only D1 ledger. The discovery audit is deliberately fail-closed: it reports missing requests, service dates, response deadlines, responses, objections, conference evidence, and post-judgment predicates as record requirements instead of inferring them. Filing artifacts cannot transition directly to `READY_TO_FILE`; they must pass the ordered review stages and require named human confirmation at the final gate.

Profile access is globally judge-scoped by default and excludes matter-private records. Supply an authorized `matterId` query parameter to include global records plus that matter's records. New identity metadata starts as `NEEDS_VERIFICATION`; administrators use `POST /v1/judges/:judgeId/identity-reviews`, and reviewers can inspect the scoped ledger with `GET /v1/judges/:judgeId/profile-reviews`.

Authority treatment/version relationships are available from `GET /v1/judges/:judgeId/authority-edges`, with the same optional authorized `matterId` scope; edges remain human-review gated.

## Layout

`src/types.ts` defines the provider, lifecycle, normalized-case, judge-profile, and discovery contracts. `src/coverage.ts` is the provider-to-court/jurisdiction coverage registry. `src/registry.ts` contains the centralized provider registry. `src/adapters/` contains provider implementations and the safe generic template. `src/services/` contains routing, jurisdiction, normalization, ranking, citations, research orchestration, judge-profile analysis, discovery auditing, review ledgers, and filing gates. `migrations/0001_initial.sql` through `migrations/0026_prediction_review_scope.sql` define the versioned D1 schema.

## Local development

```sh
npm install
npm run db:migrate:local
npm test
npm run typecheck
npm run dev
```

Set `COURTLISTENER_TOKEN` as a Wrangler secret for authorized higher-rate API access. Do not place credentials in source or client payloads. Local development uses `wrangler.local.jsonc`; production uses `wrangler.jsonc`, which contains intentional placeholders until real Cloudflare resources exist.

Local mode includes a complete synthetic fixture catalog for all 22 registered providers. Fixtures are marked `mock: true`, use `mock://` provenance, and are never legal authority. Production hard-codes `MOCK_PROVIDER_MODE` to false and the deployment validator rejects local mock mode.

## API

`GET /health`, `GET /ready`, `POST /v1/search`, `POST /v1/cases/search`, `POST /v1/research`, `POST /v1/citations/verify`, and `GET /v1/providers` are available. Dashboard endpoints are `GET /v1/dashboard/summary`, `/providers`, and `/activity`. Provider governance adds admin-only `POST /v1/providers/:id/review`, `/activate`, and `/deactivate` routes. Job status is intentionally unavailable until a durable job store is implemented; `/v1/jobs/:id` returns 501 rather than inventing a status. Set `GLAW_API_KEY` and `GLAW_ADMIN_API_KEY` as Worker secrets; provider routing remains disabled until the D1 migration and review workflow are completed.

The Astro dashboard is in `dashboard/`. It is a read-only operator surface for runtime posture, provider review gates, corpus counts, and ingestion activity. Build it with `cd dashboard && npm run build`.

## Accuracy boundary

The Phase 1 router never treats a search hit as verified authority. Citation extraction is unverified until a source-backed lookup succeeds. Subsequent-history validation, semantic retrieval, MCP, Astro admin UI, and additional adapters are planned behind the same contracts and must retain provenance, matter isolation, and fail-closed citation behavior.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for resource provisioning, secret setup, migrations, deployment, provider activation, and the read-only `npm run verify:live` release check. See [docs/PRODUCTION_READINESS.md](docs/PRODUCTION_READINESS.md) for the requirement-by-requirement gate matrix. Production deployment remains blocked until dedicated resources, secrets, live isolation checks, and human review are complete.

The tenant-scoped `GET /v1/judges` directory accepts optional `court`, `county`, `judicialCircuit`, and `division` filters plus bounded `limit`/`offset` pagination (maximum 100 per page). It returns judge identities with their recorded verification status; practitioners can follow each `judgeId` to the corresponding profile endpoint.
