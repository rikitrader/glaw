# GLAW Workflow Studio Implementation Plan

## Current audit

- **Confirmed:** Astro + Cloudflare control-plane scaffold exists under `control-plane/`.
- **Confirmed:** `@xyflow/react` is installed and an architecture graph island exists.
- **Confirmed:** Local D1, R2, KV, and Queue bindings are available through `wrangler.local.jsonc`.
- **Confirmed:** The existing public intake Worker remains under `app/` and must not be replaced.
- **Partial:** The current React Flow surface is a read-only architecture graph with node selection.
- **Missing:** n8n-style palette, drag/drop creation, compatible connection validation, editable inspector, save/load, workflow DSL persistence, versioning, nested graphs, edge inspector, run history, and Cloudflare Workflow execution.

## Product decision

The first real Workflow Studio slice will be a generic, department-independent graph editor. It will ship with a litigation demonstration graph but its node registry and connection rules will support Tax, Corporate, Compliance, Investigation, and other departments without engine changes.

## Architecture

```text
Astro shell
  -> WorkflowStudio React island
  -> canonical graph state
  -> graph validator
  -> workflow definition serializer
  -> D1 workflow version API
  -> Cloudflare Workflows adapter (later execution phase)
```

Canvas positions remain presentation state. Workflow semantics live in node `config`, edge `type`, and versioned graph definitions.

## MVP acceptance criteria

- [ ] Open `/workflows/studio`.
- [ ] Search and drag node types from the palette onto the canvas.
- [ ] Move, select, multi-select, duplicate, delete, undo, redo, zoom, pan, fit view, and use the minimap.
- [ ] Connect Department → Workflow → Agent → Skill → Adapter → Tool/RAG → Review → Approval → Output.
- [ ] Invalid connections are rejected with a visible reason.
- [ ] Selecting a node opens an editable inspector based on node metadata.
- [ ] Selecting an edge opens a connection inspector.
- [ ] Save and reload the draft graph locally through an API contract.
- [ ] Validate the graph and show actionable errors/warnings.
- [ ] Publish is blocked when critical validation errors remain.
- [ ] Current/proposed status is visible and never conflated.
- [ ] The demo can be reused for a Tax workflow by changing registry data, not engine code.

## Implementation phases

### Phase 1 — canonical registry and editor state

Node metadata, node/edge types, default configs, handles, connection rules, graph invariants, reducer state, undo/redo history.

### Phase 2 — Studio layout

Astro route, React island, toolbar, palette, canvas, inspector, bottom validation/run rail, breadcrumbs, responsive detail fallback.

### Phase 3 — interaction

Palette search, drag/drop, quick-add, connect validation, multi-select, duplicate, delete, keyboard shortcuts, context menu, auto layout.

### Phase 4 — persistence

Workflow drafts, graph snapshots, versions, save/load API, D1 tables, publish guard, exact version references.

### Phase 5 — governance and execution

Policy validation, human approval requirements, RAG permissions, red/blue nodes, run history, Cloudflare Workflows adapter, telemetry only when measured.

## Do not change

- Existing `app/` public intake Worker and routes.
- Existing legal hard gates and source-locked RAG semantics.
- Astro as the primary application framework.
- React Flow as the graph engine.
- Cloudflare-first deployment boundary.
