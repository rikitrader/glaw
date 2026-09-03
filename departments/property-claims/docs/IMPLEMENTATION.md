# Implementation roadmap

## Architecture assessment

Existing GLAW provides shared matter state, intake/ethics/citation/adversarial gates, evidence and legal-research patterns, publishing, and a Cloudflare control plane. It does not yet provide a typed property-claim digital twin or estimate/invoice canonical model.

## Phase 1 shipped

- domain interfaces for claim, policy, endorsement, provision, evidence, causation, damage, estimate, invoice, equipment, readings, arguments, and findings;
- pipeline state machine and role-agent registry;
- immutable document registration requiring SHA-256 and original path;
- policy-first and human-escalation guards;
- canonical Xactimate-compatible line-item normalizer with explicit UNKNOWN values;
- invoice normalizer with transparent calculations;
- JSON Schemas for the digital twin and estimate lines;
- synthetic unit tests for both unsupported carrier assumptions and unsupported contractor assumptions.

## Target modules

`policy-reader`, `policy-form-classifier`, `endorsement-resolver`, `state-law`, `causation`, `building-science`, `xactimate`, `estimate-normalizer`, `line-item-audit`, `invoice-audit`, `water-mitigation`, `roofing`, `contents`, `mold`, `depreciation`, `overhead-profit`, `code-upgrade`, `matching`, `weather`, `equipment`, `claim-timeline`, `expert-review`, `red-team`, `blue-team`, `white-team`, `litigation`, `damages`, `appraisal`, and `settlement`.

## Hard production gates

No coverage or payment conclusion without the complete policy record. No legal conclusion without jurisdiction and verified authority. No quantity conclusion without evidence. No price conclusion without method and market evidence. No final report without White Team reconciliation and human review where required.
