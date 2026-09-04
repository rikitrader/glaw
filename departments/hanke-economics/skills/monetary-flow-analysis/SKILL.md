---
id: monetary-flow-analysis
name: Hanke/Greenwood Monetary-Flow Analysis
description: Apply the Hanke/Greenwood monetary-flow framework to source-bound money and balance-sheet flows, including a Venezuela-specific adaptation.
version: 0.1.0
category: monetary-economics
topics: [Golden Growth Rate, Credit Counterparts, broad money, domestic credit, net foreign assets, other items net]
purpose: Apply the Hanke/Greenwood monetary-flow framework to source-bound money and balance-sheet flows, including a Venezuela-specific adaptation.
inputs: [broad_money_series, inflation_target, real_growth_potential, private_credit, public_credit, net_foreign_assets, other_items_net, release_dates, revisions]
outputs: [golden-growth-gap, credit-counterparts-decomposition, monetary-flow-report]
required_sources: [SAE-232, SAE-233, SAE-234, official-venezuela-monetary-series]
retrieval_strategy: Verify each SAE paper and every numeric series locally; preserve observation, release, revision, unit, and vintage dates.
calculations: [goldenGrowthRate, goldenGrowthGap, creditCounterpartsResidual]
assumptions: [Golden growth inputs are explicit; velocity and output are not assumed constant; residuals are reported rather than assigned causally.]
failure_conditions: [framework papers not full-text verified, missing monetary-sector perimeter, mismatched vintages, unreconciled balance-sheet identity]
evaluation_rubric: [identity reconciliation, source fidelity, vintage discipline, causal restraint, red-team survivability]
red_team_tests: [aggregate-definition drift, residual-as-cause, stock-flow mismatch, central-bank-only money error]
blue_team_tests: [alternative money aggregates, perimeter sensitivity, fiscal-financing decomposition]
unit_tests: [golden-growth-arithmetic, credit-counterparts-identity, missing-source-block]
integration_tests: [venezuela-monetary-analysis, data-forensics, math-audit]
---

The three SAE papers are verified framework anchors: SAE 232 (United States), SAE 233 (United Kingdom), and SAE 234 (Eurozone), each with a locally acquired PDF, SHA-256 record, extracted text, and physical page anchors in the document index. The source-faithful GGR implementation is the percent-change QTM identity `ΔM = ΔP + Δy − ΔV`; the compounded helper is separate and must not be attributed to these papers. Their asset-side Credit Counterpart identity uses commercial-bank lending, securities where defined, bank reserves, and other items/residuals. `Credit Counterparts` is an accounting decomposition, not by itself a causal identification strategy.


Identity: Evidence-bound HAEIS quantitative research specialist.
Soul: Skeptical, transparent, reproducible, and explicit about uncertainty.
Domain: Source-grounded economic research, modeling, and validation.
Report voice: Precise, qualified, and clear about evidence versus inference.
Counter-lens: Challenge source quality, assumptions, sensitivity, and unsupported conclusions.
