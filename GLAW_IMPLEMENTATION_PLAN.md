# GLAW Legal AI Operating System — Implementation Plan

## Phase 1 — audit and canonical registries

Complete: current repository inventory, architecture graph, workflow, agent, RAG, API, database, event, and Cloudflare registries. Add target registries for departments, agents, skills, tools, workflows, RAG, and policies.

## Phase 2 — canonical domain model

Add typed schemas for organizations, users, departments, matters, projects, workstreams, workflows, agents, skills, tools, sources, documents, evidence, claims, citations, deadlines, risks, approvals, runs, findings, and audit events. Every record needs organization/matter scope, status, version, and evidence/ownership metadata where applicable.

## Phase 3 — Astro control-plane shell

Build the Astro application and Cloudflare Worker integration. Keep static reports server-rendered. Add React islands only for graph canvases, workflow editing, timelines, and execution viewers. Protect administration and architecture surfaces with appropriate Cloudflare access controls.

## Phase 4 — matters, projects, departments

Implement multi-organization and multi-matter navigation, dynamic intake, conflict screening, department packs, matter workspace, role permissions, deadlines, and approvals. Preserve the existing GLAW matter folder and gate semantics through adapters during migration.

## Phase 5 — agent, skill, and tool governance

Normalize existing SKILL.md files into the skill registry. Add governed tool adapters, model policies, source policies, output schemas, validators, fallback behavior, tests, and risk levels. Do not generate hundreds of new agents before the registry and evaluation harness exist.

## Phase 6 — workflow builder

Implement versioned workflow DSL, graph validator, templates, cloning/forking, swimlanes, Red/Blue review loops, human approval nodes, execution states, retries, timeouts, and idempotency. Store definitions independently from XYFlow layout state.

## Phase 7 — Cloudflare execution plane

Use Workflows for durable multi-step execution, Queues for asynchronous ingestion and batch jobs, Durable Objects for justified coordination, D1 for relational state, and R2 for immutable source/output objects. Add each binding only with tests and environment-specific configuration.

## Phase 8 — RAG and document intelligence

Preserve original documents in R2, classify privilege and confidentiality, parse/OCR through adapters, create permissioned collections, maintain source metadata, and add Vectorize only after tenant/matter filtering and citation lineage are enforced.

## Phase 9 — model governance and AI Gateway

Create a model registry and policy router. Route approved provider calls through AI Gateway where it creates governance and telemetry value. Evaluate Workers AI per task; do not silently replace existing Claude/Codex adapters.

## Phase 10 — Red/Blue, quality, and human approval

Implement adversarial lenses, Blue Team remediation, Judge review, traffic-light status, max review rounds, quality thresholds, critical-failure blocking, and named professional approval. Existing GLAW hard gates remain authoritative.

## Phase 11 — evaluation and observability

Add golden tasks, reference outputs, rubrics, adversarial cases, model/skill/workflow version capture, cost, token, latency, retry, citation, human-acceptance, and Red Team pass metrics. Do not display metrics until telemetry exists.

## Phase 12 — production hardening

Add environment parity checks, migration gates, disaster recovery, retention, access reviews, audit verification, queue dead-letter handling, workflow replay policy, R2 immutability, D1 transaction tests, and performance benchmarks for large graphs.

## First MVP

The initial usable slice is:

```text
Astro Command Center
  -> matter/project list
  -> one matter workspace
  -> static canonical registries
  -> workflow canvas React island
  -> node inspector
  -> source evidence links
  -> current/proposed status
  -> human approval node
  -> validation and Architecture Doctor findings
```

No live autonomous legal execution is required for this MVP.
