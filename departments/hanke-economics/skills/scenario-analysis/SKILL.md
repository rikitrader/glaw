---
id: scenario-analysis
name: Scenario Analysis
description: Compare policy outcomes across explicit deterministic scenarios.
version: 0.1.0
category: quantitative
topics: [base, bull, bear, extreme stress, failure]
purpose: Compare policy outcomes across explicit deterministic scenarios.
inputs: [model, assumptions, policy_options]
outputs: [scenario-report]
required_sources: [versioned-inputs]
retrieval_strategy: Freeze assumptions per scenario and label all scenario-only values.
calculations: [all-relevant-formulas]
assumptions: [Scenarios are not forecasts or certainties.]
failure_conditions: [Hidden assumption, non-reproducible output]
evaluation_rubric: [coverage, reproducibility, interpretability]
red_team_tests: [policy-failure-case, combined-shock]
blue_team_tests: [mitigation-case]
unit_tests: [scenario-schema]
integration_tests: [policy-design, counterfactual-analysis]
---
Required cases: base, bull, bear, extreme stress, and policy failure.
