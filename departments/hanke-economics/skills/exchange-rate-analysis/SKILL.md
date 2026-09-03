---
id: exchange-rate-analysis
name: Exchange Rate Analysis
description: Compare exchange-rate regimes and price signals without conflating depreciation and devaluation.
version: 0.1.0
category: exchange-rates
topics: [official FX, parallel FX, depreciation, pegs]
purpose: Compare exchange-rate regimes and price signals without conflating depreciation and devaluation.
inputs: [official_fx, parallel_fx, regime_history]
outputs: [fx-analysis]
required_sources: [official-series, market-observations]
retrieval_strategy: Preserve quote convention, date, market segment, and source quality.
calculations: [fxDepreciation, parallelPremium]
assumptions: [Parallel prices may be noisy and are not automatically inflation measures.]
failure_conditions: [Quote convention unclear, dates misaligned]
evaluation_rubric: [quote clarity, premium reproducibility]
red_team_tests: [quote-inversion, stale-rate]
blue_team_tests: [multiple market sources]
unit_tests: [fx-formulas]
integration_tests: [hyperinflation-analysis, monetary-analysis]
---
Use `parallel / official - 1` only after aligning quote conventions.
