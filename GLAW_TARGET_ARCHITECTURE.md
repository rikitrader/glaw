# GLAW Legal AI Operating System — Target Architecture

This is the expanded target architecture. Current-state facts remain in `02_CURRENT_ARCHITECTURE.md`; proposed elements in this document are not claims that the repository already implements them.

## System hierarchy

```text
GLAW
  -> Organization
  -> Department
  -> Matter / Project
  -> Workstream
  -> Workflow
  -> Agent Team
  -> Specialist Agent
  -> Skill
  -> Tool Adapter
  -> RAG Collection
  -> Source / Evidence
  -> Validator
  -> Human Approval
  -> Output
```

## Control plane

The Astro dashboard exposes Command Center, Matters, Projects, Departments, Workflows, Agents, Skills, Tools, RAG, Documents, Evidence, Research, Deadlines, Approvals, Red Team, Blue Team, Risk, Audit, Knowledge, Models, Integrations, Administration, and Architecture.

Astro renders reports, navigation, matter pages, forms, and audit data. React islands provide `WorkflowDesigner`, `ArchitectureCanvas`, `AgentGraph`, `MatterGraph`, `EvidenceGraph`, `CitationGraph`, `TimelineCanvas`, `KnowledgeGraph`, and `ExecutionViewer`.

## Agent operating model

```text
User / lawyer
  -> GLAW intake
  -> Matter orchestrator
  -> Department orchestrator
  -> fact / evidence / research / specialist agents
  -> strategy
  -> drafting
  -> citation validation
  -> Red Team
  -> Blue Team
  -> Judge / quality review
  -> required human review
  -> final output
```

The existing Managing Partner and specialist seat system are the confirmed foundation. Chief Legal AI, Matter Orchestrator, department orchestrators, reusable Fact/Evidence/Timeline/Strategy/Drafting/Judge/Red/Blue agents are proposed layers that must route through existing GLAW gates and roster ownership.

## Cloudflare topology

```text
Astro + React islands
  -> Worker control plane
  -> D1: organizations, users, departments, matters, projects, workflows,
         agents, skills, tools, sources, citations, documents, evidence,
         deadlines, approvals, risks, audit events
  -> R2: original documents, evidence, generated artifacts, exports
  -> Queues: ingestion, OCR, embeddings, batch analysis, notifications
  -> Workflows: durable matter, research, document, Red/Blue, and approval runs
  -> Durable Objects: matter sessions, workflow coordination, locks, collaboration
  -> Vectorize: permissioned semantic indexes
  -> AI Gateway: model policy, routing, cost, and telemetry
  -> Workers AI: optional native inference
```

KV remains appropriate for hot configuration and cache, not transactional matter or graph state.

## Matter workspace

Each matter has overview, workflow, timeline, people, documents, evidence, research, agents, tasks, deadlines, drafts, risk, Red Team, Blue Team, approvals, and audit views. All records are matter-scoped and permission-aware.

## Workflow DSL

The visual builder edits a versioned YAML/JSON workflow definition. It does not store business logic only in canvas coordinates. A validator converts the definition into a Cloudflare Workflow adapter with idempotency, retry, timeout, failure, approval, and audit semantics.

