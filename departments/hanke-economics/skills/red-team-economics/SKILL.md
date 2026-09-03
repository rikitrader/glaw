---
id: red-team-economics
name: Red Team Economics
description: Try to falsify the strongest version of a Hanke-based conclusion.
version: 0.1.0
category: adversarial
topics: [monetary, banking, fiscal, data, causality, institutions]
purpose: Try to falsify the strongest version of a Hanke-based conclusion.
inputs: [claim, evidence_graph, calculations, policy]
outputs: [red-team-findings]
required_sources: [supporting-and-contradictory-evidence]
retrieval_strategy: Steelman first, then attack monetary, banking, fiscal, historical, data, causal, institutional, political, and crisis assumptions.
calculations: [stressLoss, reserveCoverage]
assumptions: [Token criticism does not count as adversarial review.]
failure_conditions: [No serious counterargument, no evidence trail]
evaluation_rubric: [specificity, falsifiability, severity, evidence]
red_team_tests: [all-specialized-attackers]
blue_team_tests: [issue-by-issue-defense]
unit_tests: [finding-schema]
integration_tests: [blue-team-economics, report-gate]
---
Every criticism must state the assumption attacked, evidence, residual risk, and status.
