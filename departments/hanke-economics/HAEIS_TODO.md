# HAEIS Production Completion Plan

Goal: make HAEIS executable, source-locked, auditable, and integrated with GLAW without fabricating evidence.

## Definition of done

- Every workflow node has a registered executor or is explicitly blocked.
- Every gate has persisted evidence, owner, timestamp, status, and failure reason.
- Every material claim resolves to a verified source, observation, calculation, or explicit uncertainty label.
- Every significant number is reproducible from deterministic code and versioned inputs.
- Every posture assessment includes shared facts, assumptions, mechanism, supporting and contradictory evidence, and falsifiers.
- Every Red Team finding receives a Blue Team response and a second Red Team disposition.
- Legal instruments and court authorities remain blocked until official text or authoritative reporting is verified.
- GLAW control-plane registries and runtime resolve the department without dangling references.
- Historical benchmarks run with a historical information cutoff and score forecasts against outcomes.

## Workstreams

### P0 — Execution and controls

- [x] Define typed workflow state, node result, gate evidence, artifact manifest, and run event contracts.
- [x] Implement workflow definition validation: duplicate nodes, dangling edges, cycles, missing executors, and invalid stop conditions.
- [x] Implement deterministic workflow runner with persisted JSONL event log.
- [x] Implement source, data, math, citation, adversarial, and Chief gate contracts.
- [x] Make final recommendation impossible while a critical gate is open.
- [x] Add post-run human-review packet persistence to GLAW; human review is advisory and is emitted at the end rather than gating execution.
- [x] Harden completion auditing so only valid source-bound posture assessments count, while duplicate cells and validation failures remain explicit blockers.

### P0 — Intake and provenance

- [x] Validate intake output mode and required fields by mode.
- [x] Validate every referenced source ID against the source registry.
- [x] Validate observation date, release date, revision, unit, series ID, and vintage where populated; preserve unavailable values as unknown.
- [x] Distinguish research-ready from analysis-ready and recommendation-ready with explicit blockers and warnings.
- [x] Add source hashing, MIME verification, and lawful-access status.
- [x] Add registry-backed duplicate detection and collision-safe remote-download persistence; persisted artifacts remain `FOUND` until integrity/citation verification.

### P1 — RAG and citation system

- [x] Implement provider-independent PDF/HTML retrieval boundary and local integrity inspection.
- [x] Add one-document-at-a-time lawful acquisition orchestration with immutable `FOUND` status and JSONL attempt audit.
- [x] Implement citation resolver and attribution blocker.
- [x] Store document-version fields and reject duplicate IDs, paths, and hashes before ingestion; historical versions remain explicit records.
- [ ] Ingest remaining Hanke and counter-Hanke sources one at a time; corpus auditor now reports every missing/restricted case reference. The current Hanke-Krus web table is now separately verified; restricted and copyrighted records remain explicitly unverified.
- [x] Verify the Hanke major-book corpus in `books/hanke/index.json`; metadata-only commercial books remain blocked for direct quotation until lawful full text exists, while public copies preserve their separate access scopes.
- [x] Resolve and verify the public full-text URLs for SAE 232–234 before attributing Golden Growth Rate or Credit Counterparts formulas to Hanke/Greenwood; PDFs, hashes, extracted text, and physical page anchors are now recorded.
- [x] Add retrieval/evidence-search tests for supporting, contradictory, and alternative evidence lanes.
- [x] Add hash-bound structured-data response ingestion for JSON/CSV provider artifacts; reject unverified sources, hash mismatches, missing release metadata, duplicate observations, and missing citation anchors.

### P1 — Quantitative engine

- [x] Add all required formulas: multiplier, credit/GDP, loan/deposit, reserve ratio, liquidity gap, FX mismatch, current account, interest/revenue, fiscal deficit/GDP, real credit growth, capitalization, and debt sustainability.
- [x] Add scenario engine: base, bull, bear, extreme stress, and policy failure.
- [x] Add reproducible Monte Carlo with seed and distribution metadata.
- [x] Add econometric adapter contracts and causal warnings.
- [x] Add independent math-audit recomputation.
- [x] Add reproducible ADF-style and cointegration-screen diagnostics that explicitly refuse unsupported formal conclusions.
- [x] Add source-locked Golden Growth Rate arithmetic and Credit Counterparts identity reconciliation with independent math-audit coverage.
- [x] Integrate the source-locked monetary-flow executor into the Venezuela workflow; reject unverified SAE leads and preserve non-reconciled residuals as interpretation blocks.
- [x] Execute a historical-only Venezuela Golden-Growth fixture through the real workflow, including diagnostic continuation and Red/Blue/second-Red review; preserve current-policy gates as blocked.
- [x] Add a Venezuela source-gap register and verify an official IMF data-limitation source; retain BCV, banking, fiscal, FX, reserve, oil, debt, and USD-circulation series as unavailable until individually sourced.
- [x] Acquire and hash-verify five official World Bank Venezuela API context artifacts (GDP, GDP growth, annual CPI inflation, oil rents, and remittances); preserve incomplete coverage and keep them out of the critical BCV/banking intake without release metadata.
- [x] Acquire and page-verify four lawful secondary Venezuela monetary reports (Banesco H1 2025, Banco de Venezuela H2 2024, CEDICE December 2024, and UNDP Q3 2025); preserve their BCV-referenced figures as disputed external context rather than primary data.
- [x] Acquire and OCR-verify the official IMF 1999 Venezuela Statistical Appendix; bind only historical 1994–98 monetary tables to the evidence graph and preserve current-series gaps.
- [x] Query and hash-verify five official IMF MFS_CBS Venezuela SDMX historical series (currency in circulation, net foreign assets, net claims on central government, claims on private sector, and claims on nonresidents); preserve 2001–2014 scope and missing release metadata.
- [x] Execute and hash-verify the recorded IMF IRFCL Venezuela SDMX query; preserve the zero-observation result as a bounded query finding and keep reserve/liquidity intake unavailable.
- [x] Query and hash-verify six official IMF MFS_ODC Venezuela SDMX historical series (private-sector claims, central-bank currency claims, broad-money deposit components, loans, and net central-government claims); preserve 2001–2015 scope and missing release metadata.
- [x] Acquire and verify official IMF comparative chapters on high-inflation fiscal/monetary stabilization and Latin American banking/dollarization; bind bounded external-view claims without converting them into Hanke attribution.
- [x] Acquire and verify the RBZ-hosted Reserve Bank of Zimbabwe Act text; bind sections 44A/45 with consolidated-text and historical-implementation limitations.
- [x] Acquire and verify the official IMF sovereign-debt restructuring paper; bind Ecuador/Argentina banking, currency, deposit-freeze, and restructuring evidence with scope limitations.
- [x] Normalize inaccessible BNB and ZimLII leads from `FOUND` to `RESTRICTED`; add a registry invariant preventing unacquired records from being treated as available artifacts.

### P1 — Postures and adversarial review

- [x] Implement posture assessment schema and evidence binding.
- [x] Populate all 14 postures for every indexed case from verified sources; all 308 cells across 22 cases are now source-bound, with Angola, Poland, and Turkey explicitly marked `INSUFFICIENT_EVIDENCE` where the verified corpus lacks episode-specific data.
- [ ] Run the monetary-flow posture through Red Team/Blue Team/second-Red review using verified SAE 232–234 framework anchors and a complete Venezuela data bundle.
- [x] Implement steelman requirement.
- [x] Implement Red Team → Blue Team → Red Team II loop contract.
- [x] Implement Economic Court and advisory Economic Jury.
- [x] Implement confidence scoring and disagreement preservation contract.

### P1 — Legal and historical evidence

- [x] Verify remaining monetary statutes, banking laws, convertibility rules, dollarization instruments, and restructuring authorities; Argentina Law 23.928, Ecuador Law 4, Bosnia law, Zimbabwe instruments, and the Bulgarian 1997 BNB provisions are now covered by verified official or authoritative local texts, with translation/consolidation/reporter limitations disclosed.
- [x] Verify Zimbabwe's 2009 multicurrency statutory basis from a lawful authoritative reporter copy, preserving the distinction from an official government-hosted text and recording bounded legal reliance.
- [x] Add official gazette and judgment retrieval status; `legal/retrieval-attempts.jsonl` preserves official failures, restricted records, and independently verified reporter copies.
- [x] Implement historical cutoff benchmark runner and execute one verified CBBH source-bound benchmark with an explicit governing-board-adoption release basis.
- [x] Add Hanke forecast audit records only where primary documentation exists; the verified Hanke/Kargı Venezuela conditional forecast is recorded as `UNTESTABLE` because its reform condition and horizon cannot be established.
- [x] Define a non-cherry-picking Hanke forecast-audit schema, validator, and empty registry; populate only after primary documentation is verified.

### P0 — GLAW integration

- [x] Register department, agents, skills, RAG collections, workflows, posture evidence, legal index, schemas, and benchmarks in the HAEIS control-plane catalog; target deployment parity remains open.
- [x] Add read-only runtime adapter and health check.
- [x] Add authenticated control-plane API exposure after local execution passes.
- [x] Run local deployment-parity and dangling-reference checks with `npm run parity`; remote deployment parity remains environment-dependent.

### P0 — Institutional economic-review report enforcement

- [x] Enforce the 24-part Venezuela final-report index with required chapter IDs, page targets, data domains, formulas, status labels, and blocked-gate disclosure.
- [x] Enforce observation-level provenance: variable, value, unit, dates, source, dataset, methodology, transformation, confidence, verification, revision, and domain.
- [x] Preserve source conflicts as separate records and add deterministic redenomination canonicalization using only verified factors.
- [x] Register the seven-level source hierarchy, 16-scenario library, policy stop/go conditions, and non-scoring readiness rubric.
- [x] Generate and validate 200 chart specifications with required metadata and `UNAVAILABLE` confidence until source-bound series exist.
- [x] Generate a complete 136-section indexed final report that remains `BLOCKED` when required evidence is missing; human review remains optional and post-run only.
- [x] Add machine-validated data-completeness and evidence-table outputs; coverage, missing observations, latest observation, reporting lag, source count, confidence, supporting/contradictory evidence, sensitivity, and unresolved status are preserved without imputation.

## Stop conditions

Never mark this plan complete if source ingestion, citation verification, calculation reproduction, adversarial review, or GLAW integration remains unverified. Unknown is a valid result; fabricated certainty is not.

## P0 — Venezuela bank-by-bank source-of-truth intake

- [x] Separate banking availability from the monetary-data gap.
- [x] Create the bank-by-bank registry and normalized field map.
- [x] Register current Banca y Negocios ranking and Banesco statement leads as `FOUND_UNREAD`, not verified evidence.
- [x] Define deposit, loan, NPL, provision, liquidity, capital, government-exposure, FX-mismatch, and maturity fields.
- [x] Define independent bank stress-test schema and GREEN/YELLOW/ORANGE/RED/BLACK classifications.
- [ ] Download and read the April 2026 Banca y Negocios banking ranking PDF.
- [ ] Acquire and read Banesco January–July 2026 statements and indicators.
- [ ] Acquire current monthly statements for every bank in `datasets/venezuela-bank-registry.json`.
- [ ] Acquire SUDEBAN accounting manuals, publication formats, and FX subaccount definitions.
- [ ] Normalize all statements into immutable bank-month observations.
- [ ] Reconcile bank totals against SUDEBAN, BCV, and secondary rankings.
- [ ] Build and independently audit bank-level stress results.
- [ ] Replace banking posture `ABSTAIN` with `CONDITIONAL` or `VALID` only when the declared coverage rule is met.

## P0 — Venezuela reserve and external-liquidity waterfall

- [x] Separate gross reported reserves, liquid readily realizable reserves, net unencumbered reserves, and effective dollarization liquidity.
- [x] Create reserve-asset schema with ownership, custodian, jurisdiction, liquidity, legal, encumbrance, haircut, and eligibility fields.
- [x] Create reserve-liquidity waterfall and dollarization-coverage schema.
- [x] Ingest IMF Venezuela SDR holdings, allocations, and projected charges with source URLs and scope labels.
- [ ] Acquire current BCV gross international-reserve series and full reserve composition.
- [ ] Reconstruct gold by domestic/foreign custody, encumbrance, litigation, frozen status, and legal access.
- [ ] Acquire World Gold Council reserve dataset and reconcile with BCV/IMF reporting.
- [ ] Reconstruct foreign securities and deposits with custodian, maturity, haircut, and sanctions status.
- [ ] Audit legal attachments, collateral, Bank of England custody, sanctions restrictions, and contested assets.
- [ ] Build oil export receipts, net government FX, and PDVSA operating-flow ledger.
- [ ] Build remittance and FDI flow lanes without treating flows as reserve stocks.
- [ ] Estimate capital flight using residual, BIS, mirror-statistics, and composite methods with confidence intervals.
- [ ] Build creditor-by-creditor external debt-service schedule for 12- and 24-month horizons.
- [ ] Calculate reserve coverage against currency, base-plus-reserves, M1, and M2 liabilities.

## P0 — Congressional-style opposition committee

- [x] Create an independent opposition-counsel mandate against the Venezuela dollarization thesis.
- [x] Define simulated intellectual personas for Friedman, Cagan, Sargent, Calvo, Reinhart/Rogoff, Minsky, Bagehot, Bernanke, Goodhart, Hausmann, and the Hanke respondent.
- [x] Define committee members, chambers, judges, quorum, roll-call options, dissent rules, and hard stops.
- [x] Define the debate protocol: Hanke steelman → cross-examination → source-bound response → rebuttal → falsifier → judge disposition.
- [x] Generate a blocked committee opinion docket with every member’s questions and Hanke-response status.
- [ ] Acquire and verify primary source texts for each economist before promoting persona claims to `VERIFIED`.
- [ ] Extract report claims and assign each claim to every relevant committee member.
- [ ] Conduct the full written-testimony and cross-examination round.
- [ ] Run evidence, mathematics, legal/institutional, historical, banking, and stress-test hearings.
- [ ] Generate member votes and preserve dissenting opinions.
- [ ] Publish final committee opinion only after all hard stops are either closed or explicitly resolved as conditions.

## P0 — Venezuela 80-case primary-evidence audit

Goal: ingest the complete user-supplied Venezuela loss, debt, PDVSA, CITGO, ISDS, criminal, sanctions, international, and enforcement universe as an evidence ledger. A case is not `VERIFIED` from metadata, a search snippet, a news summary, or an amount copied from an unverified table.

### Required record for every case

- [ ] Primary judgment, award, indictment, docket, official case database record, or authoritative reporter copy acquired.
- [ ] Document is readable; OCR performed when necessary.
- [ ] SHA-256 and local path recorded.
- [ ] Claimants/prosecutor and respondent/defendant verified from the document.
- [ ] Case number, tribunal, date, procedural posture, and jurisdiction verified.
- [ ] Claims and defenses summarized from the actual record.
- [ ] Evidence exhibits, memoranda, declarations, and financial documents listed separately.
- [ ] Every amount has currency, date, amount basis, and page/paragraph locator.
- [ ] Award, judgment, settlement, principal, interest, penalty, forfeiture, and enforcement amounts are kept separate.
- [ ] Resolution, sentence/custody, and current status verified from the latest available primary record.
- [ ] Political or institutional connection recorded only when directly sourced; no party affiliation inferred.
- [ ] Overlap with related cases identified; no double counting.
- [ ] Evidence summary written and reviewed against the underlying document.
- [ ] Status assigned: `VERIFIED`, `FOUND`, `UNVERIFIED`, `RESTRICTED`, `DISPUTED`, or `UNAVAILABLE`.

### Case-by-case execution queue

- [ ] C01–C10: ConocoPhillips, Crystallex, Gold Reserve, Rusoro, Mobil Cerro Negro, OI European, Tenaris, Venezuela US, Anglo American, Valores Mundiales.
- [ ] C11–C20: Venoklim, Transban, Diamante Trading, Highbury I, Highbury III, Williams I, Williams II, Maeso, Trapote, SGO.
- [ ] C21–C30: Nacato, Autopista Concesionada, Longreef, Saint-Gobain, Blue Bank, Fábrica de Vidrios/Owens-Illinois, Clorox España, Air Canada, Tenaris II, aggregate mining/oil concession matters.
- [ ] C31–C40: ConocoPhillips commercial arbitration, PDVSA 2020 bonds, Crystallex/PDVH attachment, ConocoPhillips enforcement, OI enforcement, Rusoro enforcement, Gold Reserve enforcement, DRFP promissory-note default, Red Tree Investments, Siemens Energy.
- [ ] C41–C50: United States v. Convit Guru, Matthias Krull, Abraham Ortega, Luis Vuteff/Ralph Steinmann, Raúl Gorrín, Naman Wakil, José Luis De Jongh Atencio, César Rincón, Roberto Rincón, Abraham Shiera.
- [ ] C51–C60: José Manuel Gonzalez Testino, Tulio Farías Pérez, José Luis Ramos Castillo, Rafael Reiter Muñoz, Javier Alvarado Ochoa, Rafael Ramírez-related matters, former prosecutor/PDVSA bribery matters, Francisco Illarramendi, Sargeant Marine, Juan Carlos Márquez Cabrera.
- [ ] C61–C70: Gustavo Hernández Frieri, Alejandro Andrade, Raúl Gorrín/Andrade related matter, Claudia Díaz, Adrián Velásquez, Alex Saab, Álvaro Pulido, Nicolás Maduro, Diosdado Cabello, Hugo Carvajal.
- [ ] C71–C80: Clíver Alcalá, Tareck El Aissami, Samark López, Adel El Zabayar, Maikel Moreno, Carlos Malpica, Rafael Sarría, ICC Venezuela I, ICC Venezuela II, Guyana v. Venezuela/ICJ and Bank of England Venezuelan-gold litigation.

### Batch gates

- [ ] Batch 1: C01–C10 read, extracted, indexed, and independently checked.
- [ ] Batch 2: C11–C20 read, extracted, indexed, and independently checked.
- [ ] Batch 3: C21–C30 read, extracted, indexed, and independently checked.
- [ ] Batch 4: C31–C40 read, extracted, indexed, and independently checked.
- [ ] Batch 5: C41–C50 read, extracted, indexed, and independently checked.
- [ ] Batch 6: C51–C60 read, extracted, indexed, and independently checked.
- [ ] Batch 7: C61–C70 read, extracted, indexed, and independently checked.
- [ ] Batch 8: C71–C80 read, extracted, indexed, and independently checked.
- [ ] Final overlap audit completed across awards, judgments, bond claims, criminal allegations, asset enforcement, and related proceedings.
- [ ] Final source-conflict registry completed; unresolved matters remain blocked rather than inferred.

## P0 — Venezuela fiscal, debt, PDVSA, and legal-transition engine

### Governing controls

- [ ] Register this workstream in the control-plane catalog and bind it to the Venezuela dollarization workflow.
- [ ] Enforce `FACT`, `INTERPRETATION`, `MODELED`, `DISPUTED`, `SOURCE_REQUIRED`, and `UNAVAILABLE` labels on every fiscal, debt, legal, and restructuring item.
- [ ] Enforce immutable vintages: budgeted, appropriated, modified, committed, accrued, and paid must never be collapsed into one expenditure value.
- [ ] Enforce issuer separation: `REPUBLIC`, `PDVSA`, `ELECAR`, `OTHER_SOE`, `BILATERAL`, `MULTILATERAL`, `DOMESTIC`, and `CONTINGENT_CLAIM`.
- [ ] Enforce the no-double-counting invariant: never sum an underlying obligation with its claim, award, judgment, enforcement claim, or recovery record.
- [ ] Require currency, as-of date, release date, source URL, document ID, page/paragraph locator, amount basis, and verification status for every amount.
- [ ] Preserve conflicting estimates as separate records in `source_conflict_registry`; do not average or overwrite them.

### Fiscal ledger

- [ ] Acquire and read the 2026 Ley de Presupuesto, Ley Especial de Endeudamiento Anual, ONAPRE formulation/execution documents, Ministry of Finance/Treasury records, SENIAT data, and public-enterprise budget material.
- [ ] Build fiscal coverage variants: `VE_FISCAL_OFFICIAL`, `VE_FISCAL_IMF`, and `VE_FISCAL_RECONSTRUCTED`.
- [ ] Normalize revenue by income tax, VAT, customs, hydrocarbon taxes, royalties, dividends, PDVSA transfers, non-tax revenue, borrowing, and other financing.
- [ ] Normalize spending by payroll, pensions, transfers, health, education, subsidies, investment, interest, principal, and other expenditure.
- [ ] Preserve budgeted/appropriated/modified/committed/accrued/paid status at line-item level.
- [ ] Calculate primary balance, overall balance, deficit/GDP, interest/revenue, revenue/GDP, and financing composition.
- [ ] Reconstruct BCV monetary financing from claims on government/public enterprises, Treasury deposits, BCV securities, and public-sector deposits.
- [ ] Build public-payroll ledger by central government, decentralized entities, military, education, health, and SOEs; separate salary, bonuses, benefits, and contributions.
- [ ] Build pension ledger from IVSS, civil-service, military, survivor, disability, and social-transfer obligations.
- [ ] Run pension scenarios at $30/$50/$70/$100/$150/$200 monthly and public-wage scenarios at $50/$100/$150/$200/$300/$500.

### Debt instruments and arrears

- [ ] Acquire official Republic and PDVSA prospectuses, indentures, OFAC security annexes, paying-agent records, exchange listings, and lawful market/restructuring documents.
- [ ] Create one immutable record per ISIN/CUSIP with issuer, original principal, outstanding principal, coupon, frequency, maturity, currency, governing law, security, collateral, CAC, last payment, default date, unpaid interest, and restructuring status.
- [ ] Keep Republic, PDVSA, Elecar, SOE, bilateral, multilateral, domestic, and contingent liabilities in separate ledgers.
- [ ] Build arrears ledger for suppliers, contractors, oil services, JV partners, bilateral creditors, multilateral creditors, bond coupons, judgments, trade credits, and promissory notes.
- [ ] For every arrear, record original obligation, accrued amount, as-of date, creditor, debtor, recognition status, dispute status, and overlap IDs.
- [ ] Build coupon-level default ledger with scheduled date, principal due, interest due, amount paid, amount unpaid, grace-period end, default event, acceleration, judgment, and recovery status.
- [ ] Construct contractual maturity profile by 2026, 2027, 2028, 2029–2040, and 2040+; keep defaulted past-due principal outside contractual maturity buckets.
- [ ] Build 12-month and 24-month external debt-service schedules with payment priority, currency, secured status, legal status, and expected cash payment.

### Claims, arbitration, judgments, and enforcement

- [ ] Link every case to an `economic_exposure_id` representing the underlying obligation.
- [ ] Separate claim, arbitration, award, judgment, enforcement, attachment, and recovery tables.
- [ ] Acquire and read the actual pleadings, awards, judgments, memoranda, exhibits, declarations, financial schedules, and enforcement orders—not metadata alone.
- [ ] Record principal, accrued interest, post-award/post-judgment interest, costs, penalties, forfeiture, payment, recovery, and outstanding amount separately.
- [ ] Link Crystallex/PDVH, ConocoPhillips, O-I, Rusoro, Gold Reserve, PDVSA bond, and Citgo enforcement records to underlying obligations before any debt aggregation.
- [ ] Identify attachments, collateral, pledged assets, OFAC requirements, priority rank, expected recovery, and actual recovery.
- [ ] Run final overlap audit across bond claims, arbitration awards, court judgments, enforcement claims, and settlements.

### Restructuring engine

- [ ] Record restructuring status as a time-varying field; never treat a reported proposal as settled terms.
- [ ] Version each proposal by publication date, adviser, eligible debt, principal haircut, interest treatment, coupon, maturity, grace period, warrants, CAC threshold, and treatment of PDVSA, bilateral, multilateral, arbitration, and court claims.
- [ ] Model no restructuring, 20%, 40%, 60%, and 80% haircuts with 5-, 10-, 20-, and 30-year maturity extensions.
- [ ] Calculate recovery values and debt-service paths without counting procedural-stage duplicates.

### Constitutional and statutory legal workstream

- [ ] Acquire and read the Constitution, especially Articles 318 and 320, and classify each conclusion as fact, interpretation, or unresolved legal question.
- [ ] Test USD alongside bolívar, USD-dominant use, full dollarization, currency board, and constitutional-amendment scenarios separately.
- [ ] Acquire and read the BCV Law, including Article 128, currency issuance, reserve, exchange, government-financing, and foreign-currency-obligation provisions.
- [ ] Acquire and read the Banking Sector Law (Gaceta Oficial No. 40.557 / Extraordinary No. 6.154), SUDEBAN authority, FOGADE, intervention, resolution, and liquidation provisions.
- [ ] Map existing legal authority against required transition authority; do not mark dollarization legally operative merely because banking law exists.
- [ ] Draft a required deposit-conversion instrument covering date, rate, accounts, blocked funds, accrued interest, rounding, deposit insurance, capital translation, and disputes.
- [ ] Draft contract-conversion rules for leases, mortgages, loans, labor obligations, insurance, utilities, judgments, and government contracts while preserving currency-of-account/payment clauses.
- [ ] Draft wage and pension conversion rules covering base pay, bonuses, vacation, severance, social benefits, collective agreements, IVSS, military, survivor, and disability benefits.
- [ ] Draft tax-conversion rules for assessments, debt, refunds, credits, loss carryforwards, VAT, withholding, penalties, interest, accounting, and returns.
- [ ] Separate domestic VES debt, indexed debt, Venezuela-law USD debt, foreign-law USD debt, PDVSA debt, secured debt, judgments, and awards; prohibit automatic conversion of foreign-law debt by domestic statute.
- [ ] Map payment-system authority for clearing, settlement, RTGS, ATM, POS, interbank balances, reserve accounts, and accounting-ledger conversion.

### Emergency liquidity and implementation

- [ ] Design the emergency liquidity facility with funding sources, eligible solvent banks, collateral classes, haircuts, limits, terms, and default rules.
- [ ] Test facility buffers at 10%, 15%, 20%, 25%, 30%, and 40% of eligible deposits.
- [ ] Specify the post-dollarization BCV/successor role in supervision, reserve management, payments, statistics, macroprudential policy, financial stability, and resolution.
- [ ] Create GO/NO-GO gates for constitutional authority, deposit conversion, fiscal financing, debt path, payment-system readiness, and USD liquidity backstop.
- [ ] Add committee hearing questions for fiscal, sovereign-debt, constitutional, banking, and creditor-rights postures.
- [ ] Re-run the opposition committee only after the fiscal/debt/legal evidence bundle is source-bound.

### Validation and report integration

- [ ] Add unit tests for debt-stage non-additivity, principal/interest separation, budget-state separation, maturity/past-due separation, and recovery netting.
- [ ] Add integration tests tying fiscal financing to the Hanke/Greenwood monetary-flow agent, reserve waterfall, bank stress engine, and dollarization funding gap.
- [ ] Add chart/data-appendix specifications for fiscal revenue/expenditure, monetary financing, debt stock, maturity wall, arrears, restructuring scenarios, legal readiness, and emergency liquidity.
- [ ] Update the final white-paper index with a Fiscal/Debt/Legal Source-of-Truth appendix and a debt-overlap audit table.
- [ ] Keep the policy verdict blocked until critical fiscal, debt, legal, and liquidity gates are either verified or explicitly resolved as conditional assumptions.
