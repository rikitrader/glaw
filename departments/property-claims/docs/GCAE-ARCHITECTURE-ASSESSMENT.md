# GCAE architecture assessment and integration contract

## 1. Existing reusable GLAW architecture

Reusable now: shared matter folders and lifecycle, intake/ethics gates, citation corpus and citation gate, adversarial RED/BLUE conventions, evidence/source ledgers, legal-governor direction, audit trails, Cloudflare authenticated API patterns, D1 migrations, publishing, and human-approval controls. These remain authoritative; GCAE is an additive department.

## 2. New integration points

`departments/property-claims/src/domain.ts` supplies claim entities. `src/ingest.ts` supplies document and financial-artifact normalization. `src/claims/adjudication/*` supplies policy compilation, endorsement resolution, coverage-chain guards, authority graph, precedent matching, burden uncertainty, argument graph, and governance. `src/claims/xactimate/*` treats estimating data as evidence. `src/claims/evidence/*` blocks unverified citations. `architecture/*.json` is machine-readable graph/workflow metadata. `control-plane/db/migrations/0014_property_claims_gcae.sql` is the persistence boundary.

## 3. Coverage-chain contract

Coverage is evaluated independently from necessity, quantity, and price. A missing policy, unresolved endorsement conflict, absent evidence, or unresolved causation issue produces a non-final status and human review rather than a binary answer.

## 4. Chambers and teams

The nine chambers are represented as stage-owned interfaces: facts, evidence, causation, policy, law, construction, Xactimate, damages, and adjudication. Red and Blue are independent positions; White records a source-bound finding and may reject both. Appellate review and dissent are reserved for the next phase after the deterministic record contract is stable.

## 5. Database and API

The D1 migration stores claim identity, immutable document metadata, and serialized findings while preserving the local evidence graph as the canonical analysis object. API contracts in `src/api.ts` require organization scope and idempotency keys. Route handlers must use existing `apiRouteWithAuth` and authorization helpers before production exposure.

## 6. Phase status

Implemented: Phase 1 schemas, document identity, provenance requirements, policy compiler, endorsement graph conflict detection, GCAE coverage guard, authority graph, precedent-match scoring, burden-of-proof unknown state, operation evidence decomposition, citation blocking, governance escalation, API contracts, migration, and tests.

Not yet production-complete: OCR/parser adapters, ESX/XML/CSV ingestion, full state-law retrieval, verified case database, construction dependency graph, full Red/Blue rebuttal rounds, White Court opinion generator, appellate chamber, report renderer, route handlers, and end-to-end D1 tests. These are intentionally not simulated.

## 7. Required report rule

Any report must preserve separate findings for entitlement, necessity, quantity, and price. Xactimate cannot decide coverage; contractor invoices cannot prove necessity by themselves; prior internal outcomes cannot become legal precedent; and unverified authorities/evidence remain blocked.
