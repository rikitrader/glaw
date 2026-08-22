# M&A, Public Markets, and AI Analytical Assurance — Production Checklist

This is the master delivery checklist for the finance expansion. An item is complete only
when its skill, structured contract, artifact contract, deterministic checks, fixtures, and
documentation are present and tested. `PARTIAL` means an existing skill is usable but does
not yet satisfy the production contract.

## 0. Operating foundation

- [x] Define the three departments: `ma`, `public-markets`, and `assurance`.
- [x] Define canonical review statuses: `draft`, `review`, `approved_with_conditions`, `approved`, `revise_required`, `rejected`.
- [x] Add machine-readable analytical-review schema.
- [x] Add deterministic review CLI with scaffold, validate, and score commands.
- [x] Add shell contract test for the review CLI.
- [x] Add canonical deal, company, quarter, shareholder, and portfolio schemas.
- [x] Add source/provenance ledger shared by all new lanes.
- [x] Add artifact manifest linking JSON, XLSX, PPTX, DOCX, and review outputs.
- [x] Add version and approval-state propagation across artifacts.
- [x] Add routing entries to the firm roster and module documentation.

## 1. M&A economics

- [x] `glaw-fs-transaction-comps`: precedent transaction universe, multiples, control premiums, valuation range foundation.
- [x] `glaw-fs-cap-table-waterfall`: fully diluted cap table, preferences, conversion, waterfall, holder proceeds foundation.
- [x] `glaw-fs-transaction-terms`: IOI, LOI, term sheet, consideration, protections, conditions, economics.
- [x] `glaw-fs-bid-comparison`: certainty-adjusted value, price/terms matrix, recommendation contract.
- [x] Connect transaction comps to company valuation and merger model through shared workpaper contracts.
- [x] Connect cap table/waterfall to merger model, closing, and deal announcement through shared workpaper contracts.
- [x] Add formula, reconciliation, sensitivity, and edge-case tests for implemented engines.

## 2. M&A process execution

- [x] `glaw-fs-buyer-universe`: strategic/financial buyers, rationale, capacity, outreach status.
- [x] `glaw-fs-ma-process-manager`: process timetable, data room, Q&A, bid rounds, request tracker.
- [x] `glaw-fs-dd-findings`: findings synthesis, red flags, purchase-price adjustments, indemnity recommendations.
- [x] `glaw-fs-ma-board-materials`: management, board, special committee, and IC materials.
- [x] Add process-state transitions and owner/deadline enforcement.
- [x] Add board recommendation tie-out to valuation, terms, diligence, and financing through lane gates.

## 3. Closing and post-close

- [x] `glaw-fs-closing-funds-flow`: closing checklist, sources/uses, wires, payoffs, escrow, rollover, final cap table.
- [x] `glaw-fs-synergy-model`: initiative-level revenue/cost/tax synergies, timing, probability, realization tracking.
- [x] `glaw-fs-carveout-model`: perimeter, standalone financials, TSAs, stranded costs, separation costs.
- [x] `glaw-fs-integration-100-day`: day-one readiness, 30/60/90/100-day plan, owners, milestones, KPI dashboard.
- [x] Add signing-to-closing and closing-to-integration workflow gates.
- [x] Add post-close actual-versus-plan reporting contract.

## 4. Public markets and investor relations

- [x] `glaw-fs-earnings-communications`: release, prepared remarks, Q&A briefing, KPI/variance bridge.
- [x] `glaw-fs-guidance-scenarios`: guidance setting/revision with base/upside/downside/stress support.
- [x] `glaw-fs-ir-materials`: investor day, IR, equity story, positioning, segment, and KPI decks.
- [x] `glaw-fs-agm-materials`: AGM presentation, scripts, resolutions, voting, shareholder Q&A.
- [x] `glaw-fs-deal-announcement`: announcement, FAQ, remarks, accretion/synergy and ownership summary.
- [x] `glaw-fs-shareholder-register`: ownership base, concentration, passive/index, holder changes, voting risk.
- [x] `glaw-fs-activist-vulnerability`: activist thesis, vulnerability score, defenses, engagement plan.
- [x] `glaw-fs-capital-return`: dividend, buyback, special dividend, debt paydown, liquidity and covenant analysis.
- [x] Add disclosure-control, Reg FD, non-GAAP, forward-looking, and materiality review gates to the lane contracts.

## 5. AI analytical assurance

- [x] `glaw-fs-analytical-artifact-review`: structured review contract and deterministic scoring foundation.
- [x] `glaw-fs-model-quality-audit`: spreadsheet/model integrity audit connected to existing audit-xls.
- [x] `glaw-fs-investment-recommendation-review`: thesis, valuation, downside, suitability, and conclusion support.
- [x] `glaw-fs-head-to-head-analysis`: blind pairwise comparison with material-error penalties.
- [x] `glaw-fs-scenario-review`: valuation, capital structure, and portfolio scenario challenge.
- [x] Add benchmark fixture format and adjudicated result ingestion contract.
- [x] Add confidence calibration and abstention reporting fields.
- [x] Add human approval and high-impact escalation gates.

## 6. Production hardening

- [x] Add golden contract fixtures for every lane.
- [x] Add malformed-input, missing-source, conflicting-source, and stale-version gate coverage.
- [x] Add cross-artifact manifest and lane-state tie-out tests.
- [x] Add untrusted-source handling and human-approval hard stops.
- [x] Add `glaw-doctor` checks for all new seats and schemas through deployment parity.
- [x] Add setup/deployment parity checks for new seats.
- [x] Add end-to-end lane-contract coverage for screen → valuation → bid → diligence → board → close → integration.
- [x] Add public-company lane-contract coverage for close → earnings → guidance → IR → ownership → capital return.
- [x] Add assurance contract coverage for AI artifact review.
- [x] Run the expansion test suite and bounded repository health checks.
- [x] Record human finance, accounting, securities, and governance approval as a required external gate.
- [x] Mark production-ready only after all required gates pass; otherwise remain `REVIEW_REQUIRED`.

## Production definition

The expansion is 100% complete only when every unchecked item above is closed, every new seat
has a tested structured contract and artifact output, every workflow has an owner and gate, and
the end-to-end fixtures pass without unresolved placeholders, stale sources, broken formulas,
or unreviewed high-impact recommendations.
