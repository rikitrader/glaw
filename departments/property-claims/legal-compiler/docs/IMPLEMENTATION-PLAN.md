# PCLC implementation plan and architecture delta

## Reusable GLAW services

Matter-scoped storage, immutable evidence conventions, citation gates, legal-governor direction, adversarial review, human approval, authenticated API patterns, D1 migrations, model governance, and audit logging are reused. PCLC owns legal-source compilation and does not replace those controls.

## PCLC data flow

`ClaimLegalContext → issue classifier → jurisdiction/date resolver → source registry → authority ingestion → citation verification → proposition extraction → hierarchy/temporal validation → policy-language match → safe rule DSL → Red/Blue/White → appellate/human gate → versioned authority package`

## Rule DSL safety

Rules contain declarative conditions and effects only. The evaluator uses an allowlisted operator switch; it does not call `eval`, execute generated JavaScript, or permit source text to mutate prompts or code.

## Current completeness

The registry contains 51 jurisdiction placeholders and 13 issue codes, all marked `NOT_STARTED`. No jurisdiction is represented as production-ready. Florida, Texas, California, New York, and Colorado require source acquisition and verification before legal rules are added.

## Next batches

1. Build official source registries and snapshot/hash ingestion for FL, TX, CA, NY, and CO.
2. Add primary-source citation and temporal fixtures for prompt payment, matching, depreciation, appraisal, bad faith, assignment, ordinance/law, causation, proof of loss, fees, notice, and limitations.
3. Add policy-language fingerprints and state-specific precedent matching.
4. Add authenticated API routes using existing GLAW authorization and audit helpers.
5. Expand remaining jurisdictions in controlled, benchmarked batches.
