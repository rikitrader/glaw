---
id: hyperinflation-analysis
name: Hyperinflation Analysis
description: Test episodes against documented definitions and reconstruct dates, peaks, and endings.
version: 0.1.0
category: crisis-economics
topics: [Hanke-Krus, hyperinflation, black markets]
purpose: Test episodes against documented definitions and reconstruct dates, peaks, and endings.
inputs: [price_data, fx_data, monetary_data, fiscal_data]
outputs: [hyperinflation-dossier]
required_sources: [Hanke-Krus-source, primary-price-or-fx-data]
retrieval_strategy: State the definition and measurement proxy before classifying.
calculations: [inflationRate, compoundInflation, parallelPremium]
assumptions: [Exchange-rate-derived estimates are estimates, not CPI observations.]
failure_conditions: [No reliable date, proxy not disclosed]
evaluation_rubric: [definition fidelity, chronology, proxy disclosure]
red_team_tests: [classification-threshold, proxy-substitution]
blue_team_tests: [multiple measurement methods]
unit_tests: [compound-inflation]
integration_tests: [historical-case-comparison, citation-verification]
---
Do not claim a Hanke-Krus classification without a verified source and stated method.
