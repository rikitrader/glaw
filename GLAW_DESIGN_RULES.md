# GLAW Autonomous Legal AI Operating System — Design Rules

Status: **target architecture / mandatory design contract**  
Date: 2026-08-23

This document extends the existing GLAW Architecture Explorer design. It does not replace the current-state evidence in `01_ARCHITECTURE_INVENTORY.md`, `02_CURRENT_ARCHITECTURE.md`, or `architecture/registry/architecture.json`.

## Non-negotiable platform rules

```text
Frontend: Astro
Interactive graph: @xyflow/react through Astro React Islands
Backend: Cloudflare Workers
Stateful coordination: Durable Objects
Durable multi-step execution: Cloudflare Workflows
Async jobs: Cloudflare Queues
Relational state: D1 where appropriate
Object storage: R2
Cache/config: KV where appropriate
Vector search: Vectorize
Model routing: AI Gateway
Optional native inference: Workers AI
```

These are architectural requirements. External infrastructure requires a documented fit analysis and explicit approval.

## Operating-system model

```text
Organization
  -> Department
  -> Matter / Project
  -> Workstream
  -> Workflow
  -> Agent Team
  -> Specialist Agent
  -> Skill
  -> Tool
  -> RAG Collection
  -> Source / Evidence
  -> Validator
  -> Human Approval
  -> Output
```

GLAW is not a single-answer chatbot. Every consequential workflow must make its intake, jurisdiction, risk, sources, agents, validators, adverse review, approval state, and output lineage inspectable.

## Graph and execution separation

```text
Astro UI / React island
  -> canonical graph model
  -> graph validator
  -> workflow definition / DSL
  -> Cloudflare Workflow adapter
  -> agent, tool, RAG, model, and human adapters
```

Canvas coordinates are presentation state. They are never the business workflow definition and never contain irreversible execution logic.

## Governance rules

- No unsourced legal authority.
- No fabricated citations.
- No silent fact assumptions.
- No cross-matter retrieval without an explicit permission decision.
- No original evidence mutation.
- No suppression of adverse authority.
- No high-risk release without required human review.
- No hidden Red Team failures.
- No unbounded agent tool access.
- No agent may bypass policy, authorization, provenance, or audit adapters.
- Every proposed architecture element must remain visibly proposed until implemented and verified.

## Core workflow pattern

```text
Intake
  -> classification
  -> jurisdiction
  -> legal domain
  -> risk classification
  -> workflow selection
  -> specialist work
  -> source retrieval
  -> analysis
  -> adverse authority
  -> citation validation
  -> Red Team
  -> Blue Team remediation
  -> Judge / quality review
  -> required human approval
  -> governed output
```

## Red / Blue controls

Every review loop must define `maxReviewRounds`, `qualityThreshold`, and `criticalFailureThreshold`. The loop terminates as `GREEN`, `YELLOW`, or `RED`; it may not retry indefinitely.

```text
Draft -> Red Team -> findings -> Blue Team -> revision -> recheck -> threshold
```

## RAG permission rules

Retrieval authorization is evaluated before similarity search using:

```text
user + organization + matter + role + privilege + classification + source authorization
```

Current source-locked lexical/citation retrieval remains the confirmed baseline. Vectorize is a proposed semantic index and cannot bypass source provenance, tenant/matter boundaries, citation checks, or human review.

## Cloudflare service rules

| Responsibility | Service | Rule |
|---|---|---|
| API/control plane | Workers | Use bindings and explicit auth policies |
| Matter/project/registry state | D1 | Use transactions and ownership columns; do not use KV for relational writes |
| Original documents/evidence/outputs | R2 | Preserve immutable originals and version generated artifacts |
| Scan/OCR/embedding batches | Queues | Use idempotent jobs with retry/dead-letter behavior |
| Durable multi-step workflows | Workflows | Persist step state and execution identity |
| Matter sessions/collaboration/locks | Durable Objects | Add only for justified serialized state or collaboration |
| Hot config/read cache | KV | Never treat as authoritative transactional state |
| Vector retrieval | Vectorize | Add only with permission filters, freshness, and citation lineage |
| Model policy/routing | AI Gateway | Centralize approved provider/model policy and telemetry |
| Native inference | Workers AI | Optional per capability, cost, privacy, and quality evaluation |

## Human and agent teams

Humans and agents are team members in the same matter graph. Human approval is a first-class workflow node with approve, return, reject, and escalation transitions.

## Versioning

Version agents, skills, tools, prompts, workflows, policies, validators, RAG configurations, and model policies. A run must preserve the versions actually used.

## Evidence status vocabulary

```text
confirmed  directly evidenced in repository/runtime
inferred   derived from evidence but not an explicit contract
proposed   target design, not current implementation
unknown    not discoverable from current evidence
deprecated retired but retained for traceability
```

