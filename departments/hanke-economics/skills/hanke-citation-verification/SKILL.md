---
id: hanke-citation-verification
name: Hanke Citation Verification
description: Independently verify every claim attributed to Hanke.
version: 0.1.0
category: evidence
topics: [citations, quotations, provenance]
purpose: Independently verify every claim attributed to Hanke.
inputs: [claim, source_record]
outputs: [citation-audit]
required_sources: [source_record, source_text_or_anchor]
retrieval_strategy: Verify author, title, date, quotation/paraphrase, context, page or section.
calculations: []
assumptions: [A URL alone does not prove a proposition.]
failure_conditions: [Source absent, quotation not found, context changes meaning]
evaluation_rubric: [fidelity, authority, completeness]
red_team_tests: [misquotation, wrong-date, wrong-author]
blue_team_tests: [independent-retrieval]
unit_tests: [blocked-attribution]
integration_tests: [position-reconstruction, report-gate]
---
Unverified claims are never silently downgraded; they remain blocked.
