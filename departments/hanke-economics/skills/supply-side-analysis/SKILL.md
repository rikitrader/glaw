---
id: supply-side-analysis
name: Supply-Side Analysis
description: Separate stabilization effects from structural-growth effects.
version: 0.1.0
category: structural-economics
topics: [taxation, incentives, regulation, productivity]
purpose: Separate stabilization effects from structural-growth effects.
inputs: [tax_policy, regulation, investment, productivity, institutions]
outputs: [supply-side-report]
required_sources: [laws, official-economic-data, research]
retrieval_strategy: Distinguish direct Hanke claims, competing evidence, and system inference.
calculations: [realInterestRate]
assumptions: [Long-run supply responses are not immediate stabilization results.]
failure_conditions: [No baseline, no policy timing]
evaluation_rubric: [mechanism clarity, time horizon, distributional analysis]
red_team_tests: [growth-attribution, incidence]
blue_team_tests: [implementation sequencing]
unit_tests: [real-rate]
integration_tests: [policy-design, posture-matrix]
---
Do not credit monetary stabilization to supply reforms or vice versa without evidence.
