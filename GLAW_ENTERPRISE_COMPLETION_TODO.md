# GLAW Enterprise Design + Engineering Completion TODO

**Review mode:** gstack engineering plan review + gstack design review  
**Date:** 2026-08-23  
**Repository:** `glaw-oss`  
**Branch observed:** `feature/corporate-finance-engine`  
**Status:** planning baseline; implementation not complete

## 0. Executive decision

The current public intake experience is a valid product surface and should remain intact. It is not the enterprise GLAW operating system. The enterprise build must add an authenticated control plane beside it, then migrate capabilities incrementally behind stable adapters.

```text
Existing public intake
        +
Astro authenticated control plane
        +
React graph islands
        +
Cloudflare Worker / D1 / R2 / Queues / Workflows / Durable Objects
        +
Permissioned legal AI execution
```

Do not convert the whole application into a React SPA. Do not introduce live autonomous execution until governance, provenance, approval, and audit contracts are enforced.

## 1. Current baseline

### Confirmed

- The repository has a Worker-backed public intake surface under `app/`.
- Existing public pages are `index.html`, `interview.html`, and `atlas.html`.
- Existing legal work is organized around an eight-stage matter spine: intake, strategy, structure, draft, adversarial, file, docket, and retro.
- Existing CLI, skill, roster, hard-gate, citation, adversarial-review, and audit concepts are the strongest source material for the dashboard.
- GLAW registry artifacts exist for departments, agents, skills, tools, workflows, RAG, and policies.
- Existing repository tests are predominantly shell/Python contract tests.

### Inferred

- The current intake flow can become the public entry point into matter creation.
- Existing stage/gate semantics can be exposed as workflow nodes through adapters.
- Registry normalization is needed before the registries can safely drive UI or execution.

### Proposed

- Astro as the application shell.
- Selective React islands using `@xyflow/react`.
- ELK.js for layered graph layout after benchmark validation.
- Cloudflare Worker control plane with D1, R2, Queues, Workflows, and Durable Objects where justified.
- AI Gateway and Vectorize only after policy and permission boundaries are implemented.

### Unknown and required evidence

- Production identity provider and Cloudflare Access configuration.
- Exact tenant/organization model and billing boundary.
- Authorized legal research providers and licensing constraints.
- Expected matter volume, document volume, graph size, retention, and recovery objectives.
- Whether the first release is internal-only, client-facing, or both.
- Required jurisdictions and professional approval roles for launch.

## 2. gstack design review scorecard

| Dimension | Current | Target | Work required |
|---|---:|---:|---|
| Product information architecture | 4/10 | 10/10 | Add authenticated command center, matter workspace, governance navigation |
| Visual hierarchy | 8/10 public intake | 9/10 control plane | Preserve public editorial mode; add dense operational mode |
| Graph interaction model | 0/10 | 10/10 | React island, canonical graph, inspector, layouts, drill-down |
| Workflow authoring | 1/10 static pipeline | 10/10 | Versioned DSL, validator, templates, approvals, execution adapter |
| Matter operations | 2/10 | 10/10 | Matter/project/workstream/task/deadline data and screens |
| Agent governance | 2/10 | 10/10 | Registry manifests, policy binding, tool/source scopes, scorecards |
| RAG/source lineage | 3/10 lexical baseline | 10/10 | Permissioned collections, citations, provenance, freshness |
| Human review | 3/10 hard-gate concept | 10/10 | Approval nodes, queues, decisions, escalation, audit |
| Security and privilege | 3/10 documented target | 10/10 | Identity, tenant isolation, matter ACL, privilege-aware retrieval |
| Cloudflare readiness | 2/10 | 10/10 | Astro adapter, bindings, migrations, durable execution, environments |
| Observability | 2/10 | 10/10 | Run events, traces, cost, latency, citation and review telemetry |
| Accessibility/responsiveness | 7/10 public page | 10/10 | Keyboard graph controls, reduced motion, mobile fallback, WCAG QA |

## 3. Non-negotiable architecture rules

- Astro remains the primary frontend/application framework.
- React is limited to interactive islands: graphs, workflow editor, timelines, execution viewers, and dense inspectors.
- Visual graph state is not business logic.
- Canonical graph model, workflow definition, execution state, and canvas layout are separate records.
- One primary workflow model; Cloudflare Workflows is the first durable execution adapter.
- Durable Objects are used only for stateful coordination, locks, collaboration, or long-lived sessions.
- Queues handle asynchronous ingestion and batch work, not interactive request/response orchestration.
- D1 owns relational control-plane state; R2 owns immutable source and artifact objects.
- KV is cache/config only, never matter transaction state.
- Retrieval always authorizes before similarity search.
- Every consequential AI output carries model, prompt, skill, tool, source, policy, and approval lineage.
- Proposed/unknown/inferred architecture never renders as confirmed.
- Original documents and evidence are immutable; derivatives are separate objects.
- High-risk legal outputs cannot release without configured human approval.

## 4. Completion definition

GLAW is enterprise-design complete when all of the following are true:

- An authorized user can create or open a matter and see humans, agents, workflow, tasks, documents, evidence, authorities, risks, deadlines, approvals, and audit history.
- The Command Center is driven by API/registry data, not hard-coded dashboard counts.
- A workflow can be inspected, validated, versioned, cloned, diffed, and executed through an adapter without coupling business logic to canvas coordinates.
- Every graph edge resolves to valid nodes and has type, direction, confidence/status, and evidence or an explicit unknown state.
- Matter, organization, privilege, role, and source permissions are enforced before data retrieval and tool execution.
- Every run is replayable/auditable with immutable version references and deterministic gate outcomes.
- The application has current/proposed/diff architecture modes and Cloudflare environment visibility.
- All critical paths have automated contract, security, accessibility, graph, workflow, and end-to-end tests.
- Production readiness gates pass for recovery, retention, observability, performance, and human approval.

## 5. Work breakdown structure

### Phase 0 — Lock scope and evidence

- [ ] Confirm the first release audience: internal legal operations, client portal, or both.
- [ ] Confirm launch jurisdictions and professional roles.
- [ ] Confirm identity provider and Cloudflare Access/Zero Trust posture.
- [ ] Confirm matter-volume, document-volume, graph-size, latency, RPO, and RTO targets.
- [ ] Confirm approved legal research providers and data licenses.
- [ ] Record decisions in `GLAW_DECISIONS.md` with `CONFIRMED`, `INFERRED`, `PROPOSED`, and `UNKNOWN` labels.
- [ ] Freeze the existing public intake routes as compatibility requirements.

**Exit gate:** no unresolved decision can change the core data model, identity model, or deployment topology without an explicit architecture decision record.

### Phase 1 — Registry normalization and canonical contracts

- [ ] Create `packages/domain` or repository-equivalent typed schemas for organization, user, role, department, matter, project, workstream, task, workflow, workflow version, workflow run, agent, skill, tool, source, collection, document, evidence, claim, citation, deadline, risk, finding, approval, policy, model, adapter, audit event, and environment resource.
- [ ] Define global ID format and namespace rules.
- [ ] Add `organizationId`, `matterId`, `projectId`, owner, lifecycle status, version, timestamps, and evidence status where applicable.
- [ ] Normalize all JSON registry entries into one canonical shape with schema version.
- [ ] Add JSON Schema validation for every registry.
- [ ] Add registry provenance fields: source file, line range when available, extraction date, confidence, and review state.
- [ ] Add explicit `confirmed`, `inferred`, `proposed`, `unknown`, and `deprecated` statuses.
- [ ] Define stable references between department packs, agent manifests, skills, tools, validators, policies, models, workflows, and RAG collections.
- [ ] Define compatibility rules for registry version upgrades.
- [ ] Build a registry loader that fails closed on malformed or duplicate IDs.
- [ ] Add snapshot fixtures for current registry counts and representative entries.

**Exit gate:** all registry files validate, all references resolve or produce explicit diagnostic findings, and no UI consumes raw unvalidated JSON.

### Phase 2 — Astro + Cloudflare application foundation

- [ ] Create the Astro application shell without deleting or rewriting the current public Worker routes.
- [ ] Decide whether Astro lives in `app/` or a new `control-plane/` package; document the choice.
- [ ] Add Astro Cloudflare adapter and Wrangler configuration for local, development, staging, and production.
- [ ] Add shared tokens based on `DESIGN.md` and preserve public intake tokens separately where needed.
- [ ] Add layouts for public intake, authenticated operations, matter workspace, and administration.
- [ ] Add route guards for authenticated/internal surfaces.
- [ ] Add error, loading, empty, unauthorized, forbidden, and degraded-state pages.
- [ ] Add server-rendered navigation, breadcrumbs, reports, audit views, and documentation.
- [ ] Add React island build path with strict hydration boundaries.
- [ ] Add environment/config validation at startup.
- [ ] Add Content Security Policy and secure headers.
- [ ] Add source maps and deployment version metadata.

**Exit gate:** public intake behavior is unchanged; `/command-center` renders in Astro; only designated interactive islands hydrate.

### Phase 3 — Cloudflare control-plane data layer

- [ ] Design D1 migrations for organizations, users, roles, memberships, departments, packs, matters, projects, workstreams, tasks, deadlines, workflows, workflow versions, workflow runs, agents, skills, tools, sources, collections, documents, evidence, claims, citations, risks, findings, approvals, policies, models, adapters, audit events, and environment resources.
- [ ] Define foreign keys, uniqueness constraints, tenant scoping, soft deletion, retention, and immutable-record rules.
- [ ] Add migration runner and local D1 fixtures.
- [ ] Add R2 object key convention separating originals, derivatives, exports, and run artifacts.
- [ ] Add immutable object metadata and checksum verification.
- [ ] Add Queue producers/consumers for ingestion, parsing, OCR, embedding, batch validation, notifications, and analytics.
- [ ] Add dead-letter queue strategy and replay metadata.
- [ ] Add Durable Object design only for matter sessions, workflow coordination, approvals, collaborative canvas state, or locks that require serialized state.
- [ ] Add Workflows definitions for durable matter intake, document ingestion, review loops, approvals, and artifact generation.
- [ ] Add environment-specific binding manifests; never assume development equals production.
- [ ] Add health endpoints that report binding availability without exposing secrets.

**Exit gate:** local integration tests prove tenant-safe D1 reads/writes, R2 immutability, queue retry/dead-letter behavior, workflow resume behavior, and environment binding validation.

### Phase 4 — Identity, authorization, privilege, and audit

- [ ] Implement organization membership and role model.
- [ ] Implement matter ACLs and department/jurisdiction restrictions.
- [ ] Implement approval authority policies by role, matter risk, jurisdiction, and output type.
- [ ] Implement document classification: public, confidential, attorney-client, work product, restricted, sealed, unknown.
- [ ] Implement privilege-aware access checks for documents, evidence, sources, graph nodes, and tool calls.
- [ ] Add service-to-service authorization for Worker adapters.
- [ ] Add least-privilege binding access per environment.
- [ ] Add secret management and rotation procedure.
- [ ] Add append-only audit events for login, access, retrieval, tool execution, model call, workflow transition, approval, export, and deletion request.
- [ ] Add audit event integrity checks and export format.
- [ ] Add redaction policy for logs, prompts, documents, and telemetry.
- [ ] Add access-review workflow and emergency revoke path.

**Exit gate:** authorization tests prove no cross-organization, cross-matter, privilege, or unauthorized tool/source access.

### Phase 5 — Command Center and navigation

- [ ] Build persistent Astro shell: left navigator, top command bar, main workspace, inspector rail, bottom event rail.
- [ ] Add navigation for Command Center, Matters, Projects, Departments, Workflows, Agents, Skills, Tools, RAG, Documents, Evidence, Research, Deadlines, Approvals, Red Team, Blue Team, Risk, Audit, Knowledge, Models, Integrations, Administration, and Architecture.
- [ ] Build registry-driven counts; label confirmed/proposed counts separately.
- [ ] Add organization, environment, matter, and current/proposed selectors.
- [ ] Add global search across IDs, names, files, matters, workflows, agents, tools, sources, tables, events, and evidence.
- [ ] Add filters for department, node type, status, risk, owner, environment, model, database, and matter.
- [ ] Add keyboard shortcuts and command palette.
- [ ] Add notifications for approvals, deadlines, failures, critical findings, citation failures, stale sources, and blocked runs.
- [ ] Add responsive fallback: table/list views for mobile; graph canvas remains desktop-first with accessible detail mode.
- [ ] Add density controls without changing semantic hierarchy.

**Exit gate:** an authorized user can navigate from Command Center to a matter, workflow, agent, source, and audit event using deep links and breadcrumbs.

### Phase 6 — Matters, projects, departments, and intake

- [ ] Implement matter creation wizard with client, matter type, jurisdiction, parties, goals, deadlines, documents, department, attorney, and AI workflow recommendation.
- [ ] Implement conflict-screen workflow before substantive work.
- [ ] Implement matter overview with status, risk, team, deadlines, gates, outputs, and next action.
- [ ] Implement project/workstream/task hierarchy under a matter.
- [ ] Implement department registry and installable department packs.
- [ ] Implement department pack manifests for agents, skills, workflows, RAG, documents, forms, rules, and validators.
- [ ] Implement dynamic intake question selection by department and matter type.
- [ ] Preserve existing eight-stage gate semantics through an adapter.
- [ ] Implement people/team assignment for lawyers, paralegals, professionals, experts, clients, and AI agents.
- [ ] Implement deadline ownership, source, timezone, reminders, escalation, and completion evidence.
- [ ] Implement matter activity timeline.

**Exit gate:** create a matter, complete conflict screening, assign a team, generate a proposed workflow, and see all records scoped to that matter.

### Phase 7 — Graph model, canvas, and inspectors

- [ ] Implement canonical `ArchitectureNode`, `ArchitectureEdge`, graph view, hierarchy, lane, evidence, and health schemas.
- [ ] Implement graph invariants: unique IDs, valid references, no silent proposed-to-confirmed conversion, valid hierarchy, valid evidence references.
- [ ] Create `ArchitectureCanvas` React island inside Astro.
- [ ] Add `WorkflowCanvas`, `MatterGraph`, `AgentGraph`, `RAGGraph`, `CitationGraph`, `TimelineCanvas`, and `CloudflareGraph` as focused islands or shared canvas modes.
- [ ] Add node renderers for trigger, workflow, service, API, agent, swarm, skill, tool, RAG, source, vector store, model, database, queue, event, decision, approval, human, security, validation, error, and output.
- [ ] Encode meaning through icon, label, shape, status text, and edge style; do not rely on color alone.
- [ ] Add pan, zoom, fit view, MiniMap, keyboard navigation, selection, multi-select, collapse/expand, lane visibility, and deep links.
- [ ] Add Current / Proposed / Diff modes with accessible labels.
- [ ] Add horizontal, vertical, swimlane, hierarchy, dependency, and radial layouts where appropriate.
- [ ] Integrate ELK.js after testing; keep layout engine replaceable.
- [ ] Add node inspector for identity, source, runtime, AI, data, operations, security, architecture, risks, and recommendations.
- [ ] Add edge inspector for interaction type, sync/async, payload, protocol, latency, retry, failure, and evidence.
- [ ] Add upstream/downstream impact highlighting.
- [ ] Add graph partitioning, lazy loading, viewport culling, memoization, and 1,000+ node benchmark fixtures.

**Exit gate:** a user can open a matter workflow, select any node/edge, view evidence and dependencies, switch current/proposed, and navigate to source context.

### Phase 8 — Workflow DSL, editor, validator, and execution adapter

- [ ] Define versioned JSON/YAML workflow DSL.
- [ ] Define node contracts for trigger, agent, skill, tool, RAG, parallel, condition, loop, human approval, red team, blue team, validator, deadline, notification, and output.
- [ ] Define input/output schemas and data contracts for every executable node.
- [ ] Define retry, timeout, idempotency, compensation, fallback, and failure policies.
- [ ] Define approval and rejection transitions.
- [ ] Build graph-to-DSL serializer and DSL-to-graph loader.
- [ ] Build structural validator and governance validator.
- [ ] Reject cycles unless explicitly marked as bounded loops with max iterations.
- [ ] Reject orphan executable nodes, unbounded tools, missing RAG permissions, missing owners, and missing failure behavior.
- [ ] Implement templates for intake, legal research, litigation analysis, contract review, tax analysis, corporate action, investigation, Red/Blue review, and approval.
- [ ] Implement clone, fork, save-as-template, version, diff, publish, archive, and rollback.
- [ ] Implement Cloudflare Workflows adapter behind an execution interface.
- [ ] Implement dry-run/simulation mode that never calls external systems.
- [ ] Persist workflow definition version on every run.

**Exit gate:** the same workflow definition can render in the canvas, validate offline, execute in a test adapter, resume after interruption, and produce an auditable run record.

### Phase 9 — Agent, skill, tool, model, and policy governance

- [ ] Normalize existing `SKILL.md` files into manifests with inputs, outputs, allowed tools, sources, models, risk, review, validators, fallback, and tests.
- [ ] Build central agent registry with owner, department, role, responsibilities, skills, tools, sources, model policy, risk, output schema, and tests.
- [ ] Build governed tool adapter registry; wrap existing CLIs and APIs instead of scattering calls through prompts.
- [ ] Add tool permission scopes by organization, matter, role, and agent.
- [ ] Add source permission scopes and jurisdiction restrictions.
- [ ] Add model registry with provider, capability, cost, context, data permissions, risk, fallback, and availability.
- [ ] Add model policy router and AI Gateway adapter.
- [ ] Evaluate Workers AI per task; record use/do-not-use decision.
- [ ] Implement reusable core agents: intake, matter orchestrator, fact, evidence, timeline, research, case law, statutory, adverse authority, strategy, drafting, citation, review, judge, red team, blue team.
- [ ] Keep new agents proposed until manifest, tests, owner, permissions, and review policy exist.
- [ ] Add agent scorecard schema; display unknown where telemetry is absent.
- [ ] Add agent-to-agent governance checks and loop detection.

**Exit gate:** every executable agent resolves to a manifest, bounded skills/tools/sources, model policy, output schema, validators, and review requirement.

### Phase 10 — RAG, documents, evidence, and citation lineage

- [ ] Preserve current source-locked lexical/citation-graph retrieval as the confirmed baseline.
- [ ] Add document intake, checksum, immutable R2 original, metadata extraction, classification, privilege, matter link, and audit event.
- [ ] Add parse/OCR adapters with explicit capability and failure states.
- [ ] Add normalization, chunking, metadata, source authority, effective date, jurisdiction, court, publication, precedential status, and verification date.
- [ ] Implement permission check before retrieval.
- [ ] Define global, jurisdiction, department, client, matter, private, evidence, and authority collections.
- [ ] Add Vectorize only after permission and lineage tests pass.
- [ ] Add embedding model registry and re-index/version strategy.
- [ ] Add retrieval, filtering, reranking, context construction, citation attachment, and citation validation.
- [ ] Add citation graph from issue to proposition to authority to case/quote/holding.
- [ ] Add freshness and stale-source health checks.
- [ ] Add unsupported-proposition detector.
- [ ] Add source viewer with page/line/paragraph anchors where available.
- [ ] Ensure generated artifacts never overwrite originals.

**Exit gate:** a retrieval request proves user/matter/role/client/privilege/source authorization before returning context, and every high-risk proposition has traceable support or a blocking finding.

### Phase 11 — Red Team, Blue Team, Judge, and human approval

- [ ] Define Red Team lenses: opposition, regulator, judge, citation attack, evidence attack, procedural attack, contract exploit, tax, compliance, security/privacy.
- [ ] Define Blue Team remediation lenses and output contracts.
- [ ] Implement bounded Red → issues → Blue → revised draft loop.
- [ ] Configure max review rounds, quality threshold, and critical-failure threshold per workflow/department.
- [ ] Implement traffic-light release state: green, yellow, red with reasons.
- [ ] Implement human approval as a first-class workflow node.
- [ ] Add approval queue, delegation, expiry, return, reject, comment, and escalation.
- [ ] Enforce professional approval for configured high-risk output types.
- [ ] Prevent suppression of adverse authority or unresolved critical findings.
- [ ] Add final packet manifest with source, evidence, reviewer, policy, and artifact digests.

**Exit gate:** no configured high-risk output can be released without required approval, and every red-team finding is resolved, accepted by an authorized human, or blocks release.

### Phase 12 — Command Center telemetry and Architecture Doctor

- [ ] Add run event ingestion for queued, running, waiting, retry, success, failure, blocked, and approval states.
- [ ] Add execution viewer with duration, model, tokens, cost, latency, retries, errors, dependencies, and source lineage when telemetry exists.
- [ ] Add dashboard metrics sourced from events, not placeholders.
- [ ] Add RAG health: source freshness, retrieval failures, citation failures, permission denials, and index status.
- [ ] Add agent health: failures, blocked tools, review pass rate, latency, cost, and human acceptance; show unknown when absent.
- [ ] Implement Architecture Doctor rules for duplicate agents/skills/tools, orphan nodes, circular dependencies, missing validators, missing human review, stale RAG, cross-matter risks, dead ends, unhandled failures, and excessive cost.
- [ ] Add evidence, impact, severity, recommendation, complexity, risk, owner, and remediation status to every finding.
- [ ] Add simulator for proposed infrastructure/workflow changes with affected modules, routes, bindings, tests, env vars, and downstream workflows.

**Exit gate:** every dashboard number links to an event/query definition, and every Doctor finding links to evidence and a remediation path.

### Phase 13 — Test and verification system

- [ ] Add schema tests for every registry and database contract.
- [ ] Add graph parser/extraction tests.
- [ ] Add graph invariants and invalid-graph fixtures.
- [ ] Add hierarchy, filter, search, layout, serialization, inspector, diff, impact, orphan, and circular dependency tests.
- [ ] Add workflow DSL round-trip tests.
- [ ] Add workflow validator tests for retries, timeouts, loops, approvals, failure, and idempotency.
- [ ] Add authorization tests for tenant, matter, privilege, source, and tool boundaries.
- [ ] Add R2 immutability, checksum, metadata, and artifact tests.
- [ ] Add Queue retry/dead-letter/replay tests.
- [ ] Add Workflow resume/replay/idempotency tests.
- [ ] Add Durable Object serialization/lock/session tests where used.
- [ ] Add model policy and provider fallback tests.
- [ ] Add citation and unsupported-proposition golden tests.
- [ ] Add Red/Blue bounded-loop tests.
- [ ] Add human approval and release-gate tests.
- [ ] Add Astro route and React island hydration tests.
- [ ] Add accessibility tests for keyboard, screen reader tree, contrast, focus, reduced motion, and error states.
- [ ] Add visual regression screenshots for public intake, Command Center, matter workspace, workflow editor, inspector, approval queue, and mobile fallback.
- [ ] Add performance benchmarks for registry loading, search, graph layout, 1,000+ nodes, and 5,000+ edges.
- [ ] Add end-to-end smoke test: intake → matter → conflict → workflow → research → citation → Red/Blue → approval → artifact → audit.

**Exit gate:** CI blocks release on schema, authorization, graph, approval, citation, accessibility, visual, or critical workflow regressions.

### Phase 14 — Production hardening and release

- [ ] Define local/development/staging/production resource manifests.
- [ ] Add migration promotion and rollback procedure.
- [ ] Add D1 backup/export and restore verification.
- [ ] Add R2 retention, legal hold, deletion request, and immutability policy.
- [ ] Add queue capacity, backoff, dead-letter monitoring, and replay runbook.
- [ ] Add Workflow timeout, cancellation, replay, and stuck-run runbook.
- [ ] Add Durable Object alarm/session recovery procedure.
- [ ] Add provider outage and model fallback runbook.
- [ ] Add citation provider outage and stale-source behavior.
- [ ] Add rate limits, abuse protection, upload limits, and Turnstile where appropriate.
- [ ] Add Cloudflare Access/Zero Trust protection for administration and architecture surfaces.
- [ ] Add structured logs, traces, metrics, alerts, and dashboards.
- [ ] Add cost budgets for models, queues, storage, and workflow runs.
- [ ] Add threat model and security review.
- [ ] Add privacy/privilege review and data processing register.
- [ ] Add operator training, attorney review guidance, and incident response playbook.
- [ ] Add deployment smoke test and post-deploy graph/registry consistency scan.
- [ ] Record production readiness sign-offs.

**Exit gate:** disaster recovery, security, privacy, observability, cost, and human-review sign-offs are complete; deployment can be rolled back without data corruption.

## 6. Required first implementation slice

Do these tasks first, in this order:

1. [ ] Create typed canonical registry schemas and validators.
2. [ ] Create Astro control-plane shell alongside the current public intake.
3. [ ] Create D1 schema for organizations, users, matters, workflows, agents, sources, approvals, and audit events.
4. [ ] Add authenticated `/command-center` route.
5. [ ] Add registry-backed matter queue and approval queue with empty/loading/unknown states.
6. [ ] Add one matter detail route.
7. [ ] Add one React `ArchitectureCanvas` island.
8. [ ] Render the eight-stage confirmed intake workflow from canonical graph data.
9. [ ] Add node inspector with source evidence and status classification.
10. [ ] Add Current / Proposed toggle without execution.
11. [ ] Add graph and workflow validation diagnostics.
12. [ ] Add one human approval node and a non-live execution mock adapter clearly labeled `simulated`.
13. [ ] Add tests for registry loading, graph invariants, route authorization, and visual smoke coverage.

## 7. Definition of done for the first MVP

- [ ] Astro route renders without converting public intake to React.
- [ ] Registry counts and records are loaded through a typed loader.
- [ ] User can open a matter and see its team, status, deadlines, risks, workflow, and approvals.
- [ ] User can inspect the eight-stage workflow in a React graph island.
- [ ] User can select a node and see status, evidence, upstream/downstream links, and recommendations.
- [ ] Current/proposed states are visually and textually distinct.
- [ ] No simulated telemetry is presented as live telemetry.
- [ ] Unauthorized user receives a real access boundary, not a hidden UI.
- [ ] Graph validation errors are visible and actionable.
- [ ] Public intake regression tests pass.

## 8. Release gates for the full enterprise system

### Design gate

- [ ] All primary workflows have desktop, tablet, mobile fallback, loading, empty, error, unauthorized, and degraded states.
- [ ] The public editorial mode and private operational mode share a coherent token system.
- [ ] Status meaning is never communicated by color alone.
- [ ] Graph interactions are keyboard-operable and have a list/detail fallback.
- [ ] gstack visual review passes on every primary route.

### Architecture gate

- [ ] Astro, Worker, D1, R2, Queues, Workflows, Durable Objects, Vectorize, AI Gateway, and Workers AI decisions are individually justified.
- [ ] No competing workflow engine is introduced without an ADR.
- [ ] No unbounded agent/tool/source access exists.
- [ ] Graph, workflow definition, execution, and layout remain separate.

### Legal-AI governance gate

- [ ] No unsourced legal authority.
- [ ] No fabricated citation.
- [ ] No silent fact assumption.
- [ ] No cross-matter retrieval.
- [ ] No original evidence mutation.
- [ ] No adverse-authority suppression.
- [ ] Required professional review enforced.
- [ ] Red Team failures are visible and release-blocking when configured.

### Operations gate

- [ ] Every consequential action is auditable.
- [ ] Every run captures exact versions used.
- [ ] Queue, workflow, DO, D1, R2, and provider failures have recovery procedures.
- [ ] Metrics distinguish measured, inferred, and unavailable.
- [ ] Cost and rate limits are enforced.
- [ ] Restore and rollback have been tested.

## 9. Recommended execution sequence

```text
Registry contracts
  ↓
Astro shell + identity
  ↓
D1/R2 control plane
  ↓
Command Center + matter workspace
  ↓
Graph island + inspectors
  ↓
Workflow DSL + validator
  ↓
Agent/skill/tool/model governance
  ↓
RAG permission + citation lineage
  ↓
Red/Blue + human approval
  ↓
Cloudflare durable execution
  ↓
Telemetry + Architecture Doctor
  ↓
Security, performance, recovery, release
```

## 10. Explicit non-goals until prerequisites pass

- [ ] Do not generate hundreds of autonomous agents.
- [ ] Do not enable cross-matter semantic search.
- [ ] Do not expose unreviewed legal outputs as final advice.
- [ ] Do not claim live execution telemetry before telemetry exists.
- [ ] Do not add Vectorize before permission filtering and citation lineage.
- [ ] Do not add every Cloudflare product without a workload fit analysis.
- [ ] Do not replace the existing intake surface before route and gate compatibility tests pass.

## Final recommendation

Build the enterprise system as a governed control plane around the existing GLAW legal pipeline. The first visible milestone is not a giant graph: it is an authenticated Command Center that opens one matter, shows one canonical workflow, exposes evidence and approval state, and proves that every displayed relationship has a source, status, owner, and permission boundary.

