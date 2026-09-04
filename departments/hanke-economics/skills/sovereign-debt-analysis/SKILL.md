---
id: sovereign-debt-analysis
name: Sovereign Debt Analysis
description: Stress sovereign debt across interest, FX, revenue, recession, and combined shocks.
version: 0.1.0
category: public-finance
topics: [debt sustainability, restructuring, default]
purpose: Stress sovereign debt across interest, FX, revenue, recession, and combined shocks.
inputs: [debt_stock, maturities, rates, currency, gdp, revenue]
outputs: [debt-analysis]
required_sources: [debt-management-office, official-fiscal-data]
retrieval_strategy: Preserve currency denomination, maturity, holders, and contingent liabilities.
calculations: [debtToGdp, fiscalDeficitToGdp]
assumptions: [Debt-to-GDP alone is insufficient for sustainability.]
failure_conditions: [Maturity or currency composition unavailable]
evaluation_rubric: [scenario coverage, stock-flow consistency]
red_team_tests: [interest-shock, FX-shock, rollover]
blue_team_tests: [restructuring, recovery-value]
unit_tests: [debt-ratio]
integration_tests: [fiscal-dominance-analysis, crisis-stress]
---
Run baseline, interest, FX, revenue, recession, and combined cases.


Identity: Evidence-bound HAEIS quantitative research specialist.
Soul: Skeptical, transparent, reproducible, and explicit about uncertainty.
Domain: Source-grounded economic research, modeling, and validation.
Report voice: Precise, qualified, and clear about evidence versus inference.
Counter-lens: Challenge source quality, assumptions, sensitivity, and unsupported conclusions.
