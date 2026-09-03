---
id: fiscal-dominance-analysis
name: Fiscal Dominance Analysis
description: Trace whether fiscal needs constrain monetary policy and destabilize money.
version: 0.1.0
category: fiscal-monetary
topics: [primary balance, deficit financing, seigniorage]
purpose: Trace whether fiscal needs constrain monetary policy and destabilize money.
inputs: [revenue, spending, interest, debt, financing_sources]
outputs: [fiscal-dominance-report]
required_sources: [fiscal-accounts, debt-data, central-bank-data]
retrieval_strategy: Reconcile primary balance, overall balance, and financing by source.
calculations: [fiscalDeficitToGdp, debtToGdp]
assumptions: [Fiscal causality requires timing and financing evidence.]
failure_conditions: [Off-budget items unknown, financing not classified]
evaluation_rubric: [financing traceability, stock-flow consistency]
red_team_tests: [deficit-monetization, contingent-liability]
blue_team_tests: [fiscal-rule, debt-restructuring]
unit_tests: [deficit-formula]
integration_tests: [sovereign-debt-analysis, monetary-analysis]
---
Show revenue, spending, primary balance, interest, overall balance, and financing separately.
