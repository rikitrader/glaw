# GLAW Global Judicial Mesh — Coding Plan

This is the execution backlog for completing the production coding work. The system must remain fail-closed: an adapter cannot route, ingest, or expose legal authority until its review gates and source evidence are complete.

## Immediate task — Provider activation governance

**Status:** `COMPLETE`  
**Priority:** P0  
**Owner:** Mesh platform  
**Depends on:** existing provider lifecycle types and registry

Build a D1-backed provider approval workflow so activation cannot be achieved by editing source code alone.

### Required work

- [x] Add D1 tables for `provider_reviews`, `provider_coverage`, `provider_review_evidence`, and `provider_activation_events`.
- [x] Seed every registered provider as `DISCOVERED` with its current coverage metadata.
- [x] Add typed repository methods for reading provider state and review evidence.
- [x] Make the router use D1 provider state, with source-code metadata as immutable defaults only.
- [x] Add an admin-only review endpoint for recording terms, schema, authority, and security decisions.
- [x] Require reviewer identity, evidence URL/hash, decision timestamp, and notes for every gate.
- [x] Add an activation endpoint that requires all four gates plus explicit approval.
- [x] Write an audit event for every review, rejection, activation, and deactivation.
- [x] Fail closed when D1 state is missing, stale, rejected, or inconsistent.
- [x] Add tests proving an unreviewed provider cannot search, ingest, or appear as routable.

### Acceptance criteria

- A generic provider remains non-routable with no D1 approval record.
- One failed review gate prevents activation.
- Activation requires all four review gates and an explicit approver.
- Deactivation immediately removes the provider from fan-out.
- Every state transition has immutable audit evidence.
- `GET /v1/providers` reports database-backed lifecycle, coverage, and review evidence.

## Ordered implementation roadmap

### P0 — Governance and source safety

- [ ] Complete the provider activation governance task above.
- [ ] Add source terms/licensing policy records and retention rules.
- [ ] Add provider-specific rate limits, circuit breakers, retries, and backoff.
- [ ] Add coverage validation fixtures for every registered court/jurisdiction ID.

### P1 — Retrieval adapters

- [ ] Implement authorized Juriscraper service boundary and signed response contract.
- [ ] Implement WorldLII, CommonLII, AsianLII, PacLII, and HKLII clients only after terms/schema review.
- [ ] Implement Kenya Law official-source client.
- [ ] Implement CanLII, EUR-Lex, CURIA, HUDOC, ICJ, ICC, ICSID, PCA, ITLOS, BAILII, AustLII, NZLII, and SAFLII clients.
- [ ] Add adapter contract tests, fixture tests, timeout tests, and provider failure tests.

### P1 — Normalized legal data

- [ ] Expand D1 schema for courts, jurisdictions, aliases, parties, judges, documents, dockets, and provenance.
- [ ] Improve CourtListener/RECAP normalization for parties, judges, citations, dates, opinions, filings, and docket entries.
- [ ] Implement canonical entity resolution across provider records.
- [ ] Store immutable raw artifacts and content hashes in R2.

### P2 — Citations and authority

- [ ] Implement citation parser coverage for U.S., Commonwealth, EU, ECLI, and international formats.
- [ ] Persist citation entities and graph edges in D1.
- [ ] Add evidence-backed treatment classification.
- [ ] Implement GLAW Authority Validation Engine with `VALID`, `CAUTION`, `NEGATIVE`, and `UNKNOWN` results.
- [ ] Add adverse-authority and conflict-search workflows.

### P2 — Retrieval and RAG

- [ ] Implement legal-section-aware chunking.
- [ ] Add hybrid D1/keyword/vector retrieval with permission filters.
- [ ] Add Vectorize indexing only after provenance and tenant-isolation tests pass.
- [ ] Add reranking and context assembly with source-bound evidence blocks.
- [ ] Add citation-to-proposition validation and fail-closed answer generation.

### P2 — Security and matter isolation

- [ ] Replace the single bearer key with tenant/workspace/matter RBAC.
- [ ] Add scoped provider credentials and Cloudflare Secrets integration.
- [ ] Add prompt-injection filtering for retrieved legal documents.
- [ ] Add audit logging for searches, document access, exports, and administrative actions.
- [ ] Add retention, deletion, legal hold, and private-RAG isolation tests.

### P3 — Agent and operator surfaces

- [ ] Generate MCP tool schemas from Zod contracts.
- [ ] Implement MCP tools for search, case lookup, citation verification, authority validation, and adverse authority.
- [ ] Add Astro admin UI for provider review, activation, health, coverage, and audit evidence.
- [ ] Add research-job status, queue retry/dead-letter visibility, and operational dashboards.

### P3 — Production readiness

- [ ] Add integration tests against local D1, R2, KV, Queue, and Durable Object emulators.
- [ ] Add deployment environments and real Cloudflare resource IDs.
- [ ] Add migration, rollback, backup, restore, and disaster-recovery procedures.
- [ ] Add latency, provider failure, queue backlog, citation precision, and cost observability.
- [ ] Complete red-team review for hallucination, source poisoning, tenant leakage, and unauthorized scraping.

## Definition of done

The project is complete only when every active adapter has source-backed review evidence, every returned authority has provenance, every private retrieval path is matter-isolated, every citation is verified or explicitly marked unverified, and the Worker passes unit, integration, security, and deployment checks.
