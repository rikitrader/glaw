---
id: inflation-analysis
name: Inflation Analysis
description: Measure and explain inflation with frequency and base-period clarity.
version: 0.1.0
category: monetary-economics
topics: [price levels, inflation, deflation]
purpose: Measure and explain inflation with frequency and base-period clarity.
inputs: [price_index_series]
outputs: [inflation-report]
required_sources: [official-price-data]
retrieval_strategy: Preserve index base, frequency, seasonality, and revision.
calculations: [inflationRate, compoundInflation]
assumptions: [Annualized and period rates are not interchangeable.]
failure_conditions: [Index break, missing base period]
evaluation_rubric: [rate correctness, temporal clarity]
red_team_tests: [annualization, base-effect]
blue_team_tests: [alternative price indices]
unit_tests: [inflation-formulas]
integration_tests: [hyperinflation-analysis, exchange-rate-analysis]
---
Report period, annualized, and cumulative inflation separately.
