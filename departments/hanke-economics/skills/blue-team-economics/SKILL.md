---
id: blue-team-economics
name: Blue Team Economics
description: Defend or modify the strongest supportable version of a framework after Red Team review.
version: 0.1.0
category: adversarial
topics: [defense, policy engineering, transition]
purpose: Defend or modify the strongest supportable version of a framework after Red Team review.
inputs: [red-team-findings, hanke-sources, policy]
outputs: [blue-team-responses, modified-policy]
required_sources: [verified-hanke-literature, counter-evidence]
retrieval_strategy: Address each finding; concede what cannot be defended.
calculations: [all-relevant-formulas]
assumptions: [A plausible defense is not a resolved finding.]
failure_conditions: [No evidence for defense, ignored residual risk]
evaluation_rubric: [response completeness, evidence, mitigation quality]
red_team_tests: [second-red-team]
blue_team_tests: [residual-risk, status-classification]
unit_tests: [response-schema]
integration_tests: [red-team-economics, policy-design]
---
Required statuses: `RESOLVED`, `PARTIALLY_RESOLVED`, or `UNRESOLVED`.
