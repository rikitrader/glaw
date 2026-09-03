---
id: policy-design
name: Monetary Policy Design
description: Design options that survive evidence, quantitative, institutional, and adversarial review.
version: 0.1.0
category: policy
topics: [currency boards, dollarization, dual currency, reform sequencing]
purpose: Design options that survive evidence, quantitative, institutional, and adversarial review.
inputs: [analysis_bundle, policy_options, constraints]
outputs: [policy-decision-matrix]
required_sources: [verified-evidence, legal-institutional-sources]
retrieval_strategy: Compare current system, reformed central bank, currency board, dollarization, dual currency, free competition, and other credible regimes.
calculations: [reserveCoverage, debtToGdp, fiscalDeficitToGdp, stressLoss]
assumptions: [Economic feasibility and political feasibility are separate dimensions.]
failure_conditions: [Critical missing data, failed red-team gate, unverified attribution]
evaluation_rubric: [option completeness, conditions, implementation, stop rules]
red_team_tests: [catastrophic-risk, institutional-capacity]
blue_team_tests: [staged-policy, mitigation]
unit_tests: [policy-option]
integration_tests: [all-analysis-skills, report-gating]
---
Allowed conclusions: `HANKE FRAMEWORK SUPPORTED`, `SUPPORTED WITH CONDITIONS`, or `NOT SUPPORTED IN THIS CASE`.
