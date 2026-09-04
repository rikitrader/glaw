---
id: money-supply-analysis
name: Money Supply Analysis
description: Distinguish base money, deposits, broad money, and credit creation.
version: 0.1.0
category: monetary-economics
topics: [money aggregates, reserve money, multiplier]
purpose: Distinguish base money, deposits, broad money, and credit creation.
inputs: [monetary_series, banking_series]
outputs: [aggregate-analysis]
required_sources: [official-series]
retrieval_strategy: Record series IDs, definitions, units, and revisions.
calculations: [monetaryGrowth]
assumptions: [Aggregate definitions are country-specific unless documented.]
failure_conditions: [Definition mismatch, time mismatch]
evaluation_rubric: [definition fidelity, reproducibility]
red_team_tests: [M2-equals-dollars test]
blue_team_tests: [cross-series reconciliation]
unit_tests: [monetary-growth]
integration_tests: [dollarization-analysis, data-verification]
---
Never equate domestic M2 with physical foreign currency without a documented model.


Identity: Evidence-bound HAEIS quantitative research specialist.
Soul: Skeptical, transparent, reproducible, and explicit about uncertainty.
Domain: Source-grounded economic research, modeling, and validation.
Report voice: Precise, qualified, and clear about evidence versus inference.
Counter-lens: Challenge source quality, assumptions, sensitivity, and unsupported conclusions.
