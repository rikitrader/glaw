---
id: economic-data-verification
name: Economic Data Verification
description: Verify every material statistic and flag impossible comparisons.
version: 0.1.0
category: evidence
topics: [data forensics, revisions, comparability]
purpose: Verify every material statistic and flag impossible comparisons.
inputs: [observations, source_records]
outputs: [data-audit]
required_sources: [original-data, official-methodology]
retrieval_strategy: Retain observation, release, revision, source, value, unit, and series ID.
calculations: []
assumptions: [A newer vintage does not erase an older vintage.]
failure_conditions: [Unit mismatch, date mismatch, gross-net mismatch]
evaluation_rubric: [lineage, vintage integrity, comparability]
red_team_tests: [June-M2-vs-December-reserves, nominal-real]
blue_team_tests: [vintage-reconciliation]
unit_tests: [observation-schema]
integration_tests: [all-quantitative-skills]
---
Material conflicts stay visible and open; they are not averaged away.
