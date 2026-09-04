# GLAW Dashboard Design

## Registry-driven information architecture

The dashboard is derived from the new registries:

```text
Command Center
  -> Departments / confirmed + proposed packs
  -> Matters / projects / workspaces
  -> Workflows / confirmed and target templates
  -> Agents / existing seats + proposed governance agents
  -> Skills / 233 current files, normalized manifests proposed
  -> Tools / 179 current commands through governed adapters
  -> RAG / source-locked baseline + proposed Vectorize pipeline
  -> Governance / policies, Red Team, Blue Team, approvals
  -> Architecture / current vs proposed infrastructure graph
```

## Initial screen

The first screen should be the Command Center, not the architecture graph. The user needs to know what requires attention before exploring topology.

### Primary metrics

- Open matters
- Active workflows
- Pending human approvals
- Critical findings
- Upcoming deadlines
- RAG/citation health

### Primary operational panels

- Matter queue with risk/status/deadline
- Active workflow execution timeline
- Agent team activity and blocked agents
- Approval queue
- Red Team findings
- RAG health and citation failures

## Graph views

| View | Default focus | Main action |
|---|---|---|
| Matter graph | people, documents, evidence, claims, deadlines | trace matter lineage |
| Workflow graph | steps, agents, tools, approvals | inspect/edit workflow |
| Agent graph | orchestrators, specialists, skills, tools, RAG | inspect governance |
| RAG graph | sources, collections, retrieval, citations | inspect authority path |
| Department graph | packs, workflows, skills, validators | manage modular capability |
| Cloudflare graph | Astro, Workers, D1, R2, Queues, Workflows, DOs | inspect runtime topology |

## First dashboard MVP

Build one responsive Astro page with one React canvas island:

```text
/architecture
  - registry-derived sidebar
  - command-center header
  - 6 KPI cards
  - matter queue
  - workflow activity panel
  - approval/risk rail
  - ArchitectureCanvas React island
  - selected-node inspector
```

The first canvas loads the 43-node canonical graph, filters to confirmed nodes by default, and exposes a Current / Proposed toggle.
