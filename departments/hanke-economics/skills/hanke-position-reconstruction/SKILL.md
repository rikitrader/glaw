---
id: hanke-position-reconstruction
name: Hanke Position Reconstruction
description: Separate what Hanke explicitly wrote from framework inference and system analysis.
version: 0.1.0
category: scholarship
topics: [direct claims, methodology, evolution]
purpose: Separate what Hanke explicitly wrote from framework inference and system analysis.
inputs: [verified_source_records, question]
outputs: [hanke-position-record]
required_sources: [verified_hanke_publication]
retrieval_strategy: Read source context around the proposition; retain page or section anchor.
calculations: []
assumptions: [No position is inferred from reputation or topic association.]
failure_conditions: [No verified Hanke-authored source, missing context]
evaluation_rubric: [attribution accuracy, context, chronology]
red_team_tests: [quote-context, authorship, contradiction-over-time]
blue_team_tests: [strongest-direct-source]
unit_tests: [attribution-block]
integration_tests: [citation-verification, disagreement-engine]
---
Output `ATTRIBUTION_BLOCKED` when the source does not establish the proposition.
