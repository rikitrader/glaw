# PROPHET-ACTUARY Department

## Objective

Growing risks and stricter regulations put insurers under pressure, elevating the need for powerful, comprehensive modeling technology to help increase profits, protect capital and keep money hard at work. FIS® Insurance Risk Suite – Prophet delivers the end-to-end capabilities needed to coordinate actuarial modeling, risk management and reporting across the enterprise.

GLAW's PROPHET-ACTUARY department operationalizes that objective under a zero-trust control standard: no retrieved source, assumption, calculation, model output, regulatory conclusion, or AI-generated artifact is accepted merely because it exists.

## Execution spine

`RETRIEVAL → SOURCE VALIDATION → ACTUARIAL REASONING → INDEPENDENT CALCULATION → ADVERSARIAL REVIEW → REGULATORY REVIEW → QA → FINAL VERDICT`

## Prophet capability map

| Prophet capability | Department control |
|---|---|
| Model Developer | formulas, variables, libraries, product, asset and liability logic |
| Enterprise Manager | controlled production runs, scheduling, parallel execution, versioning, audit trails |
| Assumptions Manager | mortality, morbidity, lapse, expense, claims, inflation, economic assumptions and approvals |
| Production Manager | scalable controlled workloads and release governance |
| Process Orchestrator | sequencing, dependencies, integrations, scheduled workflows and traceability |
| Data Integration | source ingestion, mappings, IFRS 17/financial interfaces and lineage |
| Flexible Results | seriatim/aggregated outputs, reporting, analytics and regulatory units of account |
| Quality Assurance | regression, test packs, intended/unintended change analysis and release validation |

## Required output

Every substantive review produces a structured evidence package, explicit assumptions, methodology, independent calculation, Prophet implementation view, validation results, stress tests, adversarial findings, regulatory review, missing information, confidence scores, materiality, and one of `PASS`, `REVIEW`, or `BLOCK`. A qualified human actuary must approve material production use.

The machine contract is `lib/schemas/prophet-actuary-review-schema.json`; the deterministic engine is `bin/glaw-prophet-actuary`; lane routing is in `lib/lane-catalog.json`.

The complete AGENT 00–37 swarm assignment is preserved in `lib/prophet-actuary-agent-map.json`, including the Governor, source/RAG, Prophet, actuarial product, regulatory, quantitative, adversarial, and model-audit roles.
