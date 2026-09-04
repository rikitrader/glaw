# PCLC / GCAE Completion Plan

## Purpose

This is the authoritative implementation checklist for the 50-State Property Claims Legal Compiler and GCAE. The source prompt is numbered **0 through 127**, so this tracker contains **128 numbered requirements**. Every item must have implementation evidence before the subsystem can be called complete.

## Status vocabulary

- `[x] DONE` — implemented and validated by code/tests or existing GLAW evidence.
- `[~] PARTIAL` — foundation exists, but production scope or verification remains.
- `[ ] TODO` — not implemented.
- `[!] BLOCKED` — requires an external source, credential, human legal review, or infrastructure decision.

## Completion gates

1. **Foundation gate:** schemas, provenance, safe DSL, temporal model, authority hierarchy, registries, migrations, and validators.
2. **Source gate:** official source registry, source snapshots, hashes, extraction, citation verification, and effective dates.
3. **Jurisdiction gate:** Florida, Texas, California, New York, and Colorado compiled and benchmarked.
4. **Scale gate:** remaining states and DC compiled in controlled batches.
5. **Claim gate:** policy/facts/law/Xactimate integration produces reproducible authority packages.
6. **Adversarial gate:** Red, Blue, White, appellate, contradiction, mutation, and hallucination suites pass.
7. **Production gate:** APIs, CLI, database, observability, dashboard, CI/CD, human approvals, and signed versioned artifacts operate end to end.

## Master checklist

### Requirements and architecture

- [~] **0.** Preserve source law → interpreted rule → computational rule → claim application separation. Evidence: `types/`, `dsl/`, `core/compiler.ts`.
- [~] **1.** Store authority metadata, propositions, prerequisites, remedies, burdens, dates, policy dependencies, and verification state.
- [~] **2.** Support 50 states, DC, territories, tribal overlays, and federal-program overlays. Current: 51-jurisdiction registry; territories pending.
- [~] **3.** Implement the complete property-claims issue taxonomy. Current: core issue codes; full taxonomy pending.
- [~] **4.** Implement nuanced, jurisdiction-aware authority hierarchy. Current: rank engine; exceptions and court-specific nuances pending.
- [~] **5.** Implement source authority tiers and enforce discovery-only treatment for Tier 4 sources.
- [~] **6.** Implement official and licensed source connector interfaces; connect providers without violating access terms.
- [~] **7.** Create and populate state source registries; all current profiles remain `NOT_STARTED`.
- [x] **8.** Implement temporal validity fields and legal-date selection.
- [x] **9.** Implement bitemporal valid-time/system-time model.

### Authority and rule compiler

- [~] **10.** Implement `LegalAuthority` and `AuthorityVersion` persistence/types.
- [~] **11.** Implement `LegalProposition` extraction/storage contract.
- [x] **12.** Implement `LegalRuleCompiler` foundation with source-required rules.
- [x] **13.** Implement safe declarative Rule DSL and allowlisted operators; no `eval`.
- [~] **14.** Implement connected `LegalRuleGraph` with dependency/override/conflict relations.
- [~] **15.** Implement `PolicyLawBridge` mapping policy clauses to doctrines.
- [ ] **16.** Implement policy-language normalization and fingerprints.
- [~] **17.** Implement precedent extraction and internal treatment relationships.
- [~] **18.** Implement multidimensional precedent usability vector and classifications.
- [ ] **19.** Implement conflict-of-laws engine.
- [ ] **20.** Implement Erie prediction engine with court-level tagging.

### Legal-domain compilers

- [ ] **21.** Matching rules: statutory, regulatory, judicial, line-of-sight, availability, and repair feasibility.
- [ ] **22.** Depreciation rules: labor/material/tax/O&P, ACV, RCV, recoverability, and deadlines.
- [ ] **23.** Appraisal rules: scope, causation, coverage, waiver, umpire, award, vacatur, fees, and competing authority.
- [ ] **24.** Prompt-payment deadline compiler with calendar/business days, tolling, exceptions, and interest.
- [ ] **25.** Claims-practices compiler separating regulatory violation, private action, bad-faith evidence, negligence, and no-private-right.
- [ ] **26.** Bad-faith compiler with prerequisites, cure, predicate breach, appraisal, damages, fees, and safe harbors.
- [ ] **27.** Assignment compiler for post-loss assignment, AOB, anti-assignment, standing, notices, and temporal changes.
- [ ] **28.** Ordinance/law compiler separating code requirement from insurance coverage and limits.
- [ ] **29.** Causation compiler for efficient proximate, concurrent, anti-concurrent, sequential, ensuing, and resulting loss.
- [ ] **30.** Proof-of-loss compiler for deadlines, sworn proof, waiver, substantial compliance, prejudice, and extensions.
- [ ] **31.** Attorney-fee compiler for one-way fees, offer of judgment, prevailing party, appraisal, and effective dates.
- [ ] **32.** Suit-limitations compiler for contractual limits, accrual, tolling, appraisal, catastrophe extensions, and repose.
- [ ] **33.** Notice/prejudice compiler for late notice, presumption, rebuttal, actual prejudice, and supplemental claims.

### Jurisdiction and source coverage

- [~] **34.** Generate reproducible jurisdiction artifacts for AL–WY and DC; profiles exist structurally, legal content pending.
- [ ] **35.** Implement PostgreSQL relational schema for authorities, versions, propositions, rules, dependencies, jurisdictions, conflicts, citations, runs, and reviews.
- [ ] **36.** Implement relational + pgvector + graph strategy with embeddings limited to discovery.
- [ ] **37.** Implement structured/temporal/authority/lexical/vector/policy-fingerprint hybrid retrieval.
- [ ] **38.** Implement discovery-only `LegalResearchAgent` that cannot declare governing law.
- [ ] **39.** Implement independent `AuthorityVerifierAgent` workflow.
- [ ] **40.** Implement `RuleExtractionAgent`; candidate rules cannot become active without verification.
- [ ] **41.** Implement Red/Blue/White legal compilation for every material proposition.
- [ ] **42.** Implement independent appellate rule review for high-impact rules.
- [ ] **43.** Implement human legal review actions and immutable overrides.
- [x] **44.** Implement rule confidence vector with weakest-critical-dependency principle.
- [x] **45.** Implement `LegalConflict` object; conflict resolution engine remains pending.
- [ ] **46.** Implement reproducible legal deadline engine.
- [ ] **47.** Ingest and version state emergency orders and catastrophe extensions.
- [ ] **48.** Implement approved-form and mandatory-form regulatory engine without inferring actual policy.
- [ ] **49.** Link policy provisions to materially similar precedent with language-difference metadata.

### APIs, change management, and claim integration

- [ ] **50.** Implement `POST /legal/compile` authority-package endpoint.
- [ ] **51.** Implement `POST /claims/:claimId/legal-context` integration endpoint.
- [ ] **52.** Implement explainability endpoint for rule source, dates, exceptions, dependencies, conflicts, and review history.
- [ ] **53.** Implement temporal rule query endpoint.
- [ ] **54.** Implement detected → fetched → hashed → diffed → verified → reviewed → published legal-change workflow.
- [ ] **55.** Implement semantic legal diff engine and change classifications.
- [ ] **56.** Implement impact analysis for rules, claims, forms, reports, and fixtures while preserving closed analyses.
- [ ] **57.** Implement compiler/ruleset/source/model/embedding/parser/schema version bundle.
- [~] **58.** Establish repository architecture for legal compiler, ontology, sources, connectors, rules, teams, APIs, tests, and migrations.
- [x] **59.** Implement strict TypeScript core types; complete discriminated-union coverage remains pending.
- [~] **60.** Define Python service boundary for NLP, parsing, citation extraction, embeddings, and batch jobs.

### Orchestration, runtime, and safety

- [~] **61.** Implement full legal compilation orchestration from jurisdiction resolution through human gate and publication.
- [~] **62.** Implement claim runtime loading of compiled rules with freshness, date, policy, and authority-alert checks.
- [x] **63.** Enforce RAG safety and explicit unknown/unverified states in the deterministic layer.
- [~] **64.** Implement complete citation validator: existence, support, pinpoint, URL, jurisdiction, date, and precedential status.
- [ ] **65.** Implement internal quotation-range control and minimal source quotations in reports.
- [ ] **66.** Complete security controls for prompt injection, malicious PDFs, path traversal, SSRF, SQL injection, and DSL isolation.
- [ ] **67.** Add explicit document-as-data prompt-injection policy to every provider/model adapter.
- [~] **68.** Extend immutable audit log with actor, timestamps, hashes, sources, model, prompt, tools, rule version, and decision.

### Testing and benchmark system

- [~] **69.** Build unit, integration, adversarial, temporal, citation, hierarchy, and security test pyramid.
- [ ] **70.** Create golden fixtures for FL, TX, CO, CA, NY, IL, MN, LA, NC, and GA without presupposed outcomes.
- [ ] **71.** Build 612 benchmark scenarios: 51 jurisdictions × 12 issues.
- [ ] **72.** Build Red legal mutation suite for stale law, false precedent, wrong exclusion, burden, and deadlines.
- [ ] **73.** Build Blue legal mutation suite for universal matching, automatic code coverage, unsupported invoices, and wrong-state law.
- [ ] **74.** Build mutation tests for dates, citations, jurisdictions, court levels, policy terms, and numeric deadlines.
- [ ] **75.** Build fake-authority hallucination benchmark expecting `AUTHORITY_NOT_FOUND`.
- [~] **76.** Integrate PCLC authority packages into Coverage Authority Engine; technical bridge exists, production API pending.
- [~] **77.** Integrate PCLC legal constraints into Xactimate scope/quantity/price flow; adapter contracts exist.
- [ ] **78.** Implement bidirectional legal-query escalation from Xactimate and building-science engines.
- [~] **79.** Complete Claim Legal Graph linking claims, policies, facts, damages, issues, authorities, propositions, rules, arguments, and decisions.
- [~] **80.** Produce explainable claim decisions with issue, date, policy, rule, authority, elements, arguments, conclusion, confidence, and missing evidence.
- [x] **81.** Enforce authority hierarchy rather than Red/Blue majority voting.
- [ ] **82.** Add automated prohibition on unsupported “most states” or consensus-law claims.
- [~] **83.** Model NAIC sources as reference-only with state adoption maps.
- [ ] **84.** Implement rule publication lifecycle from DRAFT through PRODUCTION, DEPRECATED, and SUPERSEDED.
- [x] **85.** Fail closed as `LEGAL_RULE_UNRESOLVED` when critical authority is unavailable.
- [ ] **86.** Add performance budgets, caching, async compiler jobs, and truthful request-state reporting.
- [ ] **87.** Add compiler/query/authority/conflict/override/staleness/coverage/latency observability metrics.

### Administration, deployment, and model governance

- [ ] **88.** Build legal compiler administration dashboard.
- [ ] **89.** Build 50-state issue comparison UI.
- [ ] **90.** Build legal timeline UI with source diffs and historical versions.
- [~] **91.** Align implementation with Astro/React, authenticated API, D1/Postgres boundary, strict TypeScript, and optional Python workers.
- [x] **92.** Add real temporal/legal compiler database migrations with jurisdiction, issue, authority, and date indexes.
- [~] **93.** Enforce hashes, snapshots, deduplication, unique citation keys, foreign-key relationships, and immutable history.
- [ ] **94.** Generate deterministic signed artifact `ruleset-US-property-claims-{version}.json`.
- [ ] **95.** Add CI/CD schema, citation, temporal, authority, security, lint, benchmark, snapshot, and impact gates.
- [ ] **96.** Implement provider-neutral LLM interface and provider adapters.
- [~] **97.** Support multi-model extraction/challenge/adjudication only where deterministic validation cannot decide.
- [x] **98.** Enforce issue-specific retrieval rather than injecting entire state-law corpora.
- [ ] **99.** Complete source-backed initial coverage build for FL, TX, CA, NY, and CO.
- [ ] **100.** Compile legal domains in required bootstrap order.
- [~] **101.** Implement source-first ingest → parse → proposition → verify → compile → adversarial → publish workflow.
- [ ] **102.** Maintain current architecture map, dependency graph, legal/claims modules, data/auth/API/jobs/model/RAG/tests/deployment inventory.
- [~] **103.** Produce and maintain Mermaid diagrams for system, workflow, authority, rules, claim integration, teams, temporal versioning, and ingestion.
- [~] **104.** Maintain complete schema output for authorities, versions, propositions, rules, conditions, conflicts, jurisdictions, sources, contexts, packages, decisions, citations, temporal ranges, and confidence.
- [x] **105.** Write SQL migrations with tables, constraints, audit fields, and temporal/jurisdiction indexes.
- [~] **106.** Implement required service interfaces; remaining production services are tracked above.
- [ ] **107.** Implement all required REST endpoints with authorization and audit controls.
- [ ] **108.** Implement `glaw legal ingest|compile|verify|benchmark|diff|query|explain` CLI commands.
- [~] **109.** Establish legal benchmark fixture format and validation; 612 fixtures remain.
- [ ] **110.** Enforce production-ready gate requiring source, citation, date, rules, adversarial review, temporal tests, and benchmark.
- [ ] **111.** Compute completeness vectors for source, issue, temporal, precedent, citation, and tests.
- [x] **112.** Enforce jurisdiction/issue status vocabulary.
- [x] **113.** Preserve distinction between internal analysis, research assistance, claim support, and licensed legal advice.

### End-to-end acceptance and operating model

- [ ] **114.** Implement source-backed matching example flow with policy, date, material, availability, line-of-sight, and Red/Blue/White review.
- [~] **115.** Implement Claim → Law → Xactimate loop; legal bridge and Xactimate evidence engine exist, full bidirectional runtime pending.
- [~] **116.** Operate as compiler/clerk/citator/appellate engine rather than chatbot; deterministic foundation exists, production corpus pending.
- [x] **117.** Block final legal determination for unresolved jurisdiction/date/policy/authority/citation/conflict/facts/negative treatment/supersession.
- [~] **118.** Record claim-level decision observability fields; complete production trace integration pending.
- [ ] **119.** Add future-extension interfaces for commercial, surplus lines, builders risk, condo/HOA, NFIP, earthquake, BI, cyber-property, equipment breakdown, marine, reinsurance, and subrogation.
- [~] **120.** Optimize for legal, temporal, jurisdictional, evidentiary, policy, adversarial, reproducible, explainable outcomes; production measurement pending.
- [x] **121.** Complete first-response inspection/design/ADR/ontology/DSL/temporal/source/test planning requirement.
- [x] **122.** Implement PCLC Phase 1 foundation directories, types, DSL, temporal, authority, citations, jurisdictions, migrations, and tests.
- [ ] **123.** Fully compile Florida from verified primary sources across all required domains.
- [ ] **124.** Fully compile Texas, California, New York, and Colorado and run cross-jurisdiction leakage tests.
- [ ] **125.** Expand remaining jurisdictions through controlled ingestion, verification, benchmarks, adversarial review, and publication batches.
- [ ] **126.** Pass final end-to-end acceptance with policy, loss date, state, facts, estimates, issue detection, authority package, technical loop, and reproducible determination.
- [~] **127.** Operate the system as infrastructure—not a chatbot, not vector-similarity law, not NAIC-as-state-law, not current-law substitution, not Xactimate-as-coverage, and not LLM-confidence-as-validation.

## Definition of complete

PCLC is complete only when every item above is `[x] DONE`, every jurisdiction/issue has a production artifact or an explicitly approved `NOT_APPLICABLE` rationale, all critical legal sources are verified, all benchmark and adversarial gates pass, historical queries reproduce the correct rule version, and a qualified human reviewer approves material or ambiguous rules.

## Current next actions

1. Build the source-registry and snapshot pipeline for Florida and Texas.
2. Implement the 13 legal-domain rule schemas and deadline engine.
3. Add policy-language fingerprints and precedent matching.
4. Implement authenticated legal compiler APIs and CLI.
5. Create the first 10 golden fixtures and cross-jurisdiction leakage tests.
6. Add completeness scoring and production artifact publication.

## Latest implementation snapshot

The deterministic infrastructure pass added the full ontology vocabulary, policy-language fingerprint interface, safe deadline engine, rule lifecycle gate, conflict resolver, completeness scoring, legal-change diff/monitor contracts, source registry service, benchmark fixture validation, source-safety validators, expanded jurisdiction/authority/citation services, and additional persistence migrations. The combined PCLC/GCAE suite now passes **34 tests** with TypeScript typecheck passing.

The remaining legal-domain and jurisdiction rows cannot be honestly marked complete by writing placeholder rules. They require actual primary-source ingestion, historical versioning, citation verification, precedent treatment, adversarial review, benchmark results, and—where required—qualified human approval.
