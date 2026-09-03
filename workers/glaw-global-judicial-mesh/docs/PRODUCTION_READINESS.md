# Production readiness matrix

This document is an operational gate, not a claim that the Worker is deployed or that a filing is ready to file.

| Requirement | Implementation evidence | Verification state |
| --- | --- | --- |
| Durable judge/matter memory | D1 judge, source, authority, matter, discovery, filing, review, and audit tables; tenant-isolated Durable Objects; immutable matter-judge assignment; composite tenant/judge/matter profile indexes, discovery provenance index/backfill, identity review evidence, and prediction-review scope | Local migrations verified through `0026`; live D1 not provisioned |
| Source and authority verification | Source reviews, authority reviews, authority-edge reviews, evidence-backed identity reviews; URL/SHA-256 evidence required; linked records and newly ingested procedural/discovery records cannot verify until reviewed | Code and schema tests verified; human administrator review required |
| Tenant and matter authorization | API tenant guard, scoped D1 queries, matter/judge/source checks, judge-bound filing evidence, tenant-named Durable Objects | Unit/route tests verified; production tenant secret required |
| Adversarial workflow | Red/Blue/Purple review generation, case-observation-aware analysis, atomic persistence of prediction/adversarial/report records, decision endpoint, immutable decision ledger | Code, schema, and local smoke tests verified; human review required |
| Prediction safeguards | Verified-only scoring, uncertainty reporting, non-psychological posture, model limitation, deterministic simulation disclaimer | Regression tests verified; output is not empirical judicial probability |
| Florida discovery workflow | Request-object storage, rule-family mapping, conservative deadline candidates, request-by-request recommendations, procedural audit, post-judgment posture warning, filing gate state machine | Record-bound audit verified; complete records remain `REQUIRES_AUTHORITY` until rule/current-authority verification; candidate dates remain `DATE_VERIFICATION_REQUIRED` until service method, orders, extensions, and current authority are verified |
| Filing safety | Sequential review stages, per-stage evidence IDs, status-verified evidence references, exact eight-gate check, named human confirmation before `READY_TO_FILE` | Fail-closed tests verified; never bypass human review |
| Operational traceability | D1 action audit log and bounded matter audit-log endpoint | Code verified; live D1 required |
| Deployment safety | Placeholder/secret/binding/contiguous-migration checks plus Wrangler dry-run | Dry-run verified; production validator intentionally blocks placeholders |
| Dependency reproducibility | Locked npm dependency graph and `npm ci --dry-run --ignore-scripts` | Lockfile check passed; npm advisory service was unreachable in this environment, so vulnerability status is `REQUIRES_EXTERNAL_AUDIT` |

## Required external gates

1. Enable R2 and provision the dedicated production documents bucket.
2. Provision a dedicated production D1 database with capacity; do not repurpose another application’s database.
3. Replace Worker, D1, and R2 placeholders in `wrangler.jsonc`.
4. Run `npm run db:migrate:remote` against the dedicated D1 database.
5. Configure `GLAW_API_KEY`, `GLAW_ADMIN_API_KEY`, `GLAW_TENANT_ID`, and any provider credentials with Wrangler secrets.
6. Complete provider/source/authority review evidence and human review of generated outputs.
7. Run live integration, tenant-isolation, backup/restore, and failure-mode tests.
8. Run `npm run predeploy`, then obtain human approval before deployment.

The deadline engine never represents a candidate as a legal due date. For written discovery it may add the rule-family default interval to a recorded service date, but it does not apply service-method adjustments, initial-pleading exceptions, stipulations, court orders, weekends/holidays, or amendments. Those inputs require record and authority verification.

Until every gate passes, the valid system states are `DRAFT`, `HUMAN_REVIEW_REQUIRED`, `REQUIRES_RECORD`, `REQUIRES_AUTHORITY`, or `BLOCKED`; the system must not be represented as deployed production legal-advice infrastructure.

## Remaining workflow

The code path is locally verified. Production handoff remains operational and human-controlled:

1. Provision dedicated Cloudflare D1 and R2 resources and replace the configuration placeholders.
2. Configure production secrets, including the tenant boundary and API/admin credentials.
3. Apply migrations `0001` through `0026` to the dedicated remote D1 database.
4. Register and independently verify sources, authorities, procedural records, discovery records, and adversarial reviews.
5. Run live tenant-isolation, authorization, backup/restore, and failure-mode checks.
6. Have a qualified human review every generated filing, its evidence, authorities, exhibits, relief, and procedural posture.
7. Run `npm run predeploy`, then deploy only through the authorized human release workflow.

The prediction and judge-profile features are evidence-bound decision-support tools. They do not model private judicial traits, guarantee outcomes, or replace legal judgment. `READY_TO_FILE` remains unavailable until the human-review gate is expressly completed.
