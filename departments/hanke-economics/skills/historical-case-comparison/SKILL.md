---
id: historical-case-comparison
name: Historical Case Comparison
description: Compare cases on matched monetary, fiscal, banking, institutional, and political facts.
version: 0.1.0
category: economic-history
topics: [country dossiers, analogies, outcomes]
purpose: Compare cases on matched monetary, fiscal, banking, institutional, and political facts.
inputs: [country_cases, comparison_question]
outputs: [historical-comparison]
required_sources: [primary-history, official-data, verified-research]
retrieval_strategy: Use a fixed dossier template and expose missing comparators.
calculations: [reserveCoverage, debtToGdp, parallelPremium]
assumptions: [Similarity on one variable does not establish causal comparability.]
failure_conditions: [Critical comparator unavailable]
evaluation_rubric: [analogy discipline, chronology, outcome fidelity]
red_team_tests: [Ecuador-Venezuela analogy, survivorship bias]
blue_team_tests: [matched-case robustness]
unit_tests: [dossier-schema]
integration_tests: [hyperinflation-analysis, policy-comparison]
---
Use the country dossier fields: crisis, causes, prior regime, inflation, FX, banks, fiscal, reform, outcome, criticism, lessons.
