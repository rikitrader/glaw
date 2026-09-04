# Migration Plan

The expanded Legal AI Operating System plan is maintained in [GLAW_IMPLEMENTATION_PLAN.md](GLAW_IMPLEMENTATION_PLAN.md). The steps below remain the platform migration spine.

## Phase 0 — discovery and registry (current)

- Keep application code unchanged.
- Maintain the evidence-backed registry and reports.
- Add invariant validation for node/edge references, status, and evidence paths.

## Phase 1 — Astro shell

- Add an Astro application boundary without reorganizing unrelated skill directories.
- Render inventory, reports, breadcrumbs, filters, and inspectors as Astro components.
- Put only graph canvases in React islands.
- Deploy through Cloudflare with an explicit environment plan.

## Phase 2 — graph MVP

- Add typed graph model and serialization.
- Add enterprise, workflow, swimlane, agent, and data views.
- Add XYFlow island, MiniMap, fit/pan/zoom, selection, search, and inspector.
- Add ELK layout adapter behind a tested interface.

## Phase 3 — extraction and governance

- Scan Wrangler configs, SKILL frontmatter, bin commands, API routes, schemas, and documented workflows.
- Add source evidence line ranges and confidence/status classification.
- Add graph validator, orphan/cycle/duplicate checks, health findings, and current/proposed diff.

## Phase 4 — Cloudflare control plane

- Persist normalized architecture metadata in D1.
- Store large scan artifacts and exports in R2.
- Add Queue/Workflow only after scan duration/volume justifies asynchronous durability.
- Add Access/Zero Trust before exposing privileged architecture control surfaces.

## Phase 5 — runtime integrations

- Add execution telemetry adapter without faking live runs.
- Add model/cost/latency/retry fields when real telemetry exists.
- Add Vectorize/AI Gateway only after RAG/provider requirements are evidenced.

## Phase 6 — Legal AI operating system layers

- Add organization, department, project, matter, workstream, and role scopes.
- Normalize the existing skill/seat population before creating new agent packs.
- Add governed tool adapters, model policies, permissioned RAG collections, and versioned workflow DSL.
- Implement Red Team, Blue Team, Judge, traffic-light, and named human approval nodes.
- Use Workflows, Queues, Durable Objects, D1, R2, Vectorize, AI Gateway, and Workers AI only according to the design rules and fit tests.

## Refactor gate

Every proposed code change must state: what exists, evidence, problem, replacement, benefit, breakage risk, migration path, and whether action is justified. No large-scale GLAW pipeline rewrite is justified by this discovery pass.
