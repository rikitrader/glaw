# PCLC TODO — execution queue

## Now

- [ ] Create official Florida and Texas source registries.
- [ ] Add source snapshot, SHA-256, retrieval date, and effective-date ingestion records.
- [ ] Implement `LegalIssueCode` expansion for the complete property-claims taxonomy.
- [ ] Implement policy-language fingerprints and policy-law bridge.
- [ ] Implement legal deadline DSL and reproducible date calculations.
- [ ] Add `LEGAL_RULE_UNRESOLVED` package output and production status validator.

## Next

- [ ] Build primary-source Florida compilation for prompt payment, matching, depreciation, appraisal, bad faith, assignment, ordinance/law, causation, proof of loss, fees, claims practices, notice, and limitations.
- [ ] Build the equivalent Texas compilation.
- [ ] Add authority verifier and precedent-treatment workflow.
- [ ] Implement `/legal/questions`, `/legal/compile`, `/legal/evaluate`, authority/rule/explain/jurisdiction/compare/change endpoints.
- [ ] Implement `glaw legal` CLI commands.
- [ ] Add first 10 golden fixtures and wrong-state leakage tests.

## Later

- [ ] Add CA, NY, and CO source-backed profiles.
- [ ] Expand the remaining jurisdictions in batches.
- [ ] Build 612 benchmark scenarios.
- [ ] Add OCR, ESX/XML/CSV, licensed legal connectors, and provider-neutral model adapters.
- [ ] Build dashboard, legal timeline UI, 50-state comparison, observability, CI/CD, signed artifacts, and production deployment.

## Required evidence for closing any TODO

Every completed item must link to: source code, schema/migration, test, source snapshot or authority record, review decision, and—where legally material—human approval. “The model knows it” is not completion evidence.
