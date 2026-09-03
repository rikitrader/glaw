---
id: econometric-validation
name: Econometric Validation
description: Provide reproducible quantitative tests with explicit uncertainty and causal warnings.
version: 0.1.0
category: econometrics
topics: [regression, time series, causality, sensitivity]
purpose: Provide reproducible quantitative tests with explicit uncertainty and causal warnings.
inputs: [dataset, hypothesis, method]
outputs: [econometric-report]
required_sources: [versioned-dataset, method-specification]
retrieval_strategy: Freeze dataset vintage and disclose transformations.
calculations: [sensitivity-analysis, scenario-analysis]
assumptions: [Correlation does not establish causation.]
failure_conditions: [Insufficient observations, nonstationarity ignored, unidentified causal design]
evaluation_rubric: [reproducibility, specification, diagnostics, limitations]
red_team_tests: [spurious-regression, omitted-variable, reverse-causality]
blue_team_tests: [alternative-specifications, placebo]
unit_tests: [input-validation]
integration_tests: [scenario-analysis, stress-testing]
---
Every result returns data, method, assumptions, output, error range, and limitations.
