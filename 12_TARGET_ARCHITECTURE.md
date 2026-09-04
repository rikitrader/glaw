# Target Architecture

The expanded Legal AI Operating System design is governed by [GLAW_DESIGN_RULES.md](GLAW_DESIGN_RULES.md) and detailed in [GLAW_TARGET_ARCHITECTURE.md](GLAW_TARGET_ARCHITECTURE.md). This file remains the concise Cloudflare/Astro platform topology.

```text
Astro application
  ├── server-rendered reports, inventory, docs, filters, navigation
  └── React islands
       ├── ArchitectureCanvas
       ├── WorkflowCanvas
       ├── AgentCanvas
       └── DataLineageCanvas
              ↓
       canonical graph model + graph validator
              ↓
       Cloudflare Worker control-plane API
         ├── D1: nodes, edges, evidence, versions, findings
         ├── R2: large scan artifacts and exports
         ├── Queues: asynchronous repository scans
         ├── Workflows: durable scan/rebuild jobs when needed
         └── Durable Object: collaboration/locks only if required
```

## Execution separation

`visual editor -> graph model -> validator -> workflow definition -> orchestration adapter -> execution adapters`.

The current GLAW CLI, stage gates, provider adapters, and X402 execution boundary remain adapters. Cloudflare Workflows is the first orchestration candidate for new durable architecture operations; Durable Objects and Queues are specialized support, not competing workflow engines.

## RAG and AI target

Preserve source-locked provenance as the authority boundary. Add a canonical agent, tool, skill, prompt, model, and RAG registry. Use AI Gateway only when a central provider/cost/observability boundary is required. Use Vectorize only after tenant filtering, freshness, citation, and retrieval-quality requirements are specified. Workers AI is an option, not a default replacement for current Claude/Codex adapters.

The expanded target adds permissioned global, jurisdiction, department, client, matter, private-document, and evidence collections; fact/evidence/timeline/research/drafting/review agents; Red/Blue review loops; traffic-light governance; and first-class human approval nodes. These are proposed capabilities unless marked confirmed in the registries.

## Environment model

Store local, development, staging, and production resource maps separately. Never infer production bindings from local Wrangler config. Each environment row must identify Worker, D1, KV, R2, Queue, Workflow, Durable Object, secret reference, and deployment version.
