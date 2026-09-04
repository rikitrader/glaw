# GLAW Agentic Legal OS — Delivery Plan

Status: proposed target plan  
Date: 2026-08-27  
Owner: GLAW Chief / Platform Lead

Enterprise hardening follow-on: [ENTERPRISE_HARDENING_PLAN.md](ENTERPRISE_HARDENING_PLAN.md)

## 1. Product outcome

GLAW turns a user request and matter record into a governed, reviewable legal
work-product packet. Agents may research, analyze, draft, test, cite, red-team,
repair, and prepare delivery. A human with lawful authority remains the seal for
binding, coercive, irreversible, or externally consequential actions.

Primary outcome: reduce time to a defensible first draft while increasing source
coverage, citation integrity, adverse-authority detection, and review visibility.

## 2. Target architecture

```text
User / Matter
      |
      v
Experience + API Gateway
      |
      v
GLAW Governor
  scope · authority · policy · risk · approvals · kill switch
      |
      v
Canonical Matter Graph + Task Graph
      |
      +------------------+------------------+
      v                  v                  v
 Research Team      Analysis Team       Draft Team
      |                  |                  |
      +------------------+------------------+
                         v
                  Evidence Graph
        facts · claims · sources · conflicts
                         |
                         v
                  Citation Engine
      authority · temporal · quote · pin-cite checks
                         |
              +----------+----------+
              v                     v
          Red Team              Blue Team
        find failure          repair + explain
              +----------+----------+
                         v
                    Judge Agent
       completeness · groundedness · risk · quality
                         |
             PASS / REVIEW_REQUIRED / BLOCK
                         |
                         v
                    Human Lawyer
                         |
              approved work-product packet
```

The execution plane is separate from the graph canvas. UI coordinates never
define business logic. Existing GLAW stage gates remain authoritative.

## 3. Core platform contracts

### Governor contract

Every run carries `organization_id`, `matter_id`, `actor_id`, `risk_class`,
`policy_version`, `workflow_version`, `correlation_id`, `idempotency_key`, and
`input_digest`.

The Governor can authorize analysis and drafting, but cannot approve a legal
filing, signature, payment, service, sanction, or other binding action.

### Task contract

Each task declares its owner agent/team, required human reviewer, typed inputs and
outputs, allowed tools and source collections, jurisdiction and time boundary,
risk class, cost/latency budget, required evidence, retry policy, maximum review
rounds, and success/review/block/escalation conditions.

### Evidence contract

Every material statement links to immutable evidence nodes. Evidence nodes preserve
source URI, title, jurisdiction, effective date, page/section, content hash,
retrieval timestamp, authority class, access scope, and extraction method.
Retrieved text is data, never executable instructions.

### Review contract

Red Team and Blue Team are bounded loops:

```text
max_review_rounds + quality_threshold + critical_failure_threshold
```

The loop terminates as `PASS`, `REVIEW_REQUIRED`, or `BLOCK`; it cannot retry
indefinitely or hide surviving critical findings.

### Receipt contract

For external or consequential commands:

```text
accepted -> authorized -> authority_claimed -> adapter_attempted
         -> observed_effective | unknown | failed
```

Timeouts never become false success. Where supported, GLAW performs authoritative
lookup before retry and reconciles unknown outcomes manually.

## 4. Canonical data model

Add or normalize these entities in the existing registry and schema package:

```text
Organization · User · Role · Permission
Client · Matter · Project · Workstream
Party · Entity · Relationship
Workflow · Task · Run · AgentTeam · Agent · Skill · Tool
Source · Document · Evidence · Fact · Claim · Citation
Finding · Risk · Approval · Deadline · Deliverable
Policy · Validator · ModelPolicy · Integration
Receipt · AuditEvent · ReviewRound · Evaluation
```

Every record has owner, organization scope, status, version, timestamps, and
provenance where applicable. Matter-aware authorization is evaluated before
retrieval, not after generation.

## 5. Agent and skill engineering system

Create a governed Skill Registry that converts each `SKILL.md` into a versioned
capability contract without replacing the source skill.

Required registry fields:

```json
{
  "skill_id": "glaw.case-law-research",
  "version": "1.0.0",
  "input_schema": "...",
  "output_schema": "...",
  "allowed_tools": [],
  "source_policy": "primary-authority-required",
  "risk_class": "high",
  "required_reviewers": ["legal-research"],
  "quality_tests": [],
  "max_rounds": 2,
  "cost_budget": "matter-policy",
  "latency_target_ms": 120000
}
```

The registry must support compatibility checks, deprecation, rollback, test
fixtures, golden outputs, model-policy binding, and capability discovery.
Do not create hundreds of new agents first. Make existing specialist skills
callable, typed, observable, and testable first.

## 6. Workflow implementation

Implement a versioned workflow DSL with nodes for intake/classification, source
ingestion/retrieval, research, analysis, drafting, evidence merge, contradiction
detection, citation validation, Red/Blue review, Judge scoring, human approval,
escalation, deliverable assembly, and close-out.

The graph editor stores layout separately from the executable definition. Every
workflow is compiled and validated before execution. Workflows support pause,
resume, replay-from-safe-boundary, cancellation, dead-letter handling, and
operator recovery.

## 7. Experience and design system

### Design direction

GLAW should feel like a calm legal operations room: evidence-dense, precise,
serious, and transparent. The interface should communicate confidence through
source visibility and state clarity, not decorative AI effects.

### Semantic tokens

| Token | Value | Use |
|---|---:|---|
| Ink | `#102033` | primary text and navigation |
| Slate | `#526174` | secondary text and metadata |
| Paper | `#F7F9FC` | application background |
| White | `#FFFFFF` | cards and work surfaces |
| Blue | `#1D5FD1` | primary action and selected state |
| Teal | `#087F73` | verified / healthy |
| Amber | `#B77908` | review required / uncertain |
| Red | `#B42318` | blocked / critical finding |
| Violet | `#6E56CF` | agent activity and automation |
| Rule | `#D7DEE8` | dividers and evidence boundaries |

### UI rules

- Use a restrained 8px spacing grid and compact density for professional work.
- Use 6px card radius, 4px controls, and minimal shadows.
- Use a readable sans-serif UI font plus a high-legibility document font.
- Every state shows status text, freshness, owner, evidence count, and permitted
  next action; never rely on color alone.
- Evidence, citations, and findings are always one click from the decision.
- Keyboard navigation, visible focus, screen-reader labels, reduced motion, and
  375px emergency flows are release requirements.

### Primary screens

1. **Decision Queue** — items needing approval, review, or escalation.
2. **Matter Workspace** — graph, timeline, facts, claims, tasks, sources, and
   deliverables.
3. **Run Inspector** — task graph execution, model/tool calls, latency, cost,
   retries, and evidence lineage.
4. **Evidence Explorer** — source-to-claim-to-citation graph with conflicts.
5. **Review Room** — Red findings, Blue repairs, Judge score, and human decision.
6. **Workflow Studio** — versioned graph editor with node contracts and tests.
7. **Governance Console** — policies, access, ethical walls, retention, exports,
   kill switch, and audit verification.

Word and Outlook should be focused work surfaces. Mobile should be limited to
alerts, review decisions, approvals, and incident response.

## 8. Delivery phases

### Phase 0 — Baseline and contracts

Freeze current GLAW gate semantics; inventory registries, commands, schemas, and
workpapers; define canonical IDs and versioning; and add architecture decisions
and the business brief.

Exit: every target component is labeled `confirmed`, `inferred`, `proposed`, or
`unknown`; no proposed component is presented as shipped.

### Phase 1 — Governor vertical slice

Build one complete workflow: **matter intake → cited research memo → Red Team →
Blue Team → Judge → human approval → exportable packet**.

Use one matter, one jurisdiction pack, one research skill, one drafting skill,
and the existing lexical/citation baseline.

Exit: normal path, duplicate request, restart, stale source, authorization
denial, Red failure, Judge block, and human approval are tested.

### Phase 2 — Task Graph and skill registry

Normalize the first 10 high-value skills; add typed contracts, capability
declarations, budgets, and golden fixtures; compile workflows into executable
task graphs; and add bounded parallel execution for independent research tasks.

Exit: workflows can be cloned, validated, versioned, paused, resumed, and
replayed without losing provenance.

### Phase 3 — Evidence Graph and citation engine

Promote source-universe and verification workpapers into graph nodes; add
fact/claim/citation relationships and contradiction detection; add authority,
temporal, quote, pin-cite, and adverse-authority validators; and add permission-
filtered semantic retrieval only after lineage tests pass.

Exit: every final claim is traceable to evidence, and unsupported or stale claims
are marked `REVIEW_REQUIRED` or `BLOCK`.

### Phase 4 — Review room and Judge

Implement Red Team lens registry, Blue Team repair proposals with diff and
explanation, deterministic Judge scoring, critical-failure blocking, and named
human review for high-risk findings.

Exit: the system never silently suppresses a Red finding and never self-approves
a consequential legal deliverable.

### Phase 5 — Production execution plane

Map responsibilities to the existing targets: Workers for API/control, D1 for
relational state, R2 for immutable evidence/output, Queues for async ingestion,
Workflows for durable execution, Durable Objects only for justified serialized
coordination, KV only for non-authoritative hot configuration, Vectorize only
with permission and lineage gates, and AI Gateway for model policy/telemetry.

Exit: load, fault, tenancy, recovery, retention, export, and disaster-recovery
tests pass for the vertical slice.

### Phase 6 — Surface expansion and ecosystem

Add Word and Outlook actions backed by the same BFF and Governor; client portal
with matter-scoped sharing; monitoring for deadlines, dockets, regulations, and
obligations; skill, jurisdiction-pack, and integration SDKs; and hosted,
self-hosted, and API deployment modes.

Exit: every surface uses the same matter graph, policy, receipts, evidence, and
approval semantics.

## 9. Business model

1. **Open-source core:** local matter engine, CLI, baseline skills, schemas, and
   workflow runner.
2. **Hosted enterprise:** governance, SSO, ethical walls, audit, retention, BYOK,
   analytics, managed integrations, and support.
3. **Usage-based execution:** matter, document, workflow, or verified-deliverable
   pricing with transparent model-cost controls.
4. **Marketplace:** jurisdiction packs, practice workflows, integrations, firm
   playbooks, and certified implementation services.

Payment authorizes compute or service access; it never substitutes for legal
authority, professional review, or a matter approval gate.

## 10. Quality and release gates

Require schema compatibility, tenant/matter/privilege/ethical-wall isolation,
duplicate delivery, restart, timeout-before-effect, timeout-after-effect,
stale-source, changed-policy, citation groundedness, adverse-authority,
Red/Blue convergence, Judge-block, accessibility, mobile-flow, cost, latency,
retry, human-acceptance, audit-export, and independent professional-review tests
before each production slice.

## 11. First build order

```text
Decision Queue
  -> Matter Workspace
  -> one governed Task Graph
  -> one Research Agent
  -> Evidence Graph
  -> Citation Engine
  -> Red/Blue Review Room
  -> Judge decision card
  -> Human approval
  -> reproducible export packet
```

Do not begin with mobile, a general chatbot, broad semantic search, or a large
agent marketplace. The first proof is a complete, inspectable, fail-closed legal
work-product loop.
