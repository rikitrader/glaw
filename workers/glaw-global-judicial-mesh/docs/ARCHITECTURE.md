# GLAW Global Judicial Mesh — Phase 1 architecture

The Worker is the policy boundary. Requests are authenticated, assigned a request ID, validated with Zod, resolved deterministically where possible, and fanned out to adapters with per-provider timeouts. Adapter output remains raw and provenance-bearing until normalization. D1 stores searchable metadata and R2 stores immutable metadata/source artifacts. KV is cache/config only. Queue messages are idempotent ingestion events. The RouterCoordinator Durable Object is reserved for short-lived coordination locks; it is not the source of truth.

Authority is layered: official court/government sources are eligible for a higher source score than nonprofit repositories, and repositories are never silently labeled official. Citation extraction is separate from citation verification; the API returns `NOT_FOUND` rather than manufacturing a case or citation.

Provider status lifecycle for future adapters: `DISCOVERED → SECURITY_REVIEW → TERMS_REVIEW → SCHEMA_TEST → DATA_QUALITY_TEST → AUTHORITY_TEST → APPROVED → ACTIVE`. Routing requires `ACTIVE` plus all four boolean gates: `termsReviewed`, `schemaValidated`, `authorityValidated`, and `securityReviewed`. Generic adapters advertise zero capabilities, are excluded from fan-out, and throw `ProviderInactiveError` if called directly. Their registry metadata remains visible for planning and review only.

## Priority adapter coverage

| Adapter | Coverage registry | Implementation boundary |
|---|---|---|
| Juriscraper | U.S. federal, SCOTUS, CA2, SDNY, state supreme/appellate | Future authorized remote Python service; not Worker scraping |
| WorldLII | Global discovery | Future reviewed search/discovery client |
| CommonLII | Commonwealth | Future reviewed repository client |
| AsianLII | Asia | Future reviewed repository client |
| PacLII | Pacific Island jurisdictions | Future reviewed repository client |
| HKLII | Hong Kong, CFA, High Court, District Court | Future reviewed repository client |
| Kenya Law | Kenya, Supreme Court, Court of Appeal, High Court, ELC, ELRC | Future official-source client |

Coverage describes intended source scope; it does not assert that the provider currently exposes an API or that every listed court is available. Activation requires evidence for each provider and court lane.
