# GLAW gstack Design Review

**Review date:** 2026-08-23  
**Reviewed surface:** `app/public/index.html` rendered through gstack Browse  
**Review type:** visual QA and product-surface fit review  
**Evidence:** rendered screenshot, accessibility snapshot, browser console check, repository inventory

## Executive result

The current app is a polished public intake and routing page. It is not yet the GLAW Legal AI Operating System dashboard described by the registries and target architecture.

The page should remain the public intake/front door. The dashboard should be introduced as a separate authenticated operational surface, rather than replacing this page.

## What gstack observed

### Strengths

- Clear headline and primary action: “One interview. The right department.”
- Strong information hierarchy with a short intake explanation, staged pipeline, routing explanation, department directory, hard gates, and API overview.
- The eight-stage intake pipeline is understandable and maps well to a future intake workflow template.
- Navigation, skip link, landmarks, heading hierarchy, and link labels are present in the accessibility tree.
- The visual language is intentionally restrained: editorial typography, generous whitespace, monochrome presentation, and compact legal-operations copy.
- The page exposes useful product concepts already present in the repository: departments, gates, intake, adversarial review, filing, docket, and retro.

### Current surface gaps

The rendered application does not expose:

- Command Center metrics or operational alerts.
- Matters, projects, workstreams, tasks, deadlines, or matter-level permissions.
- Agent, skill, tool, model, validator, or adapter registries.
- Workflow canvas, swimlanes, node inspector, edge inspector, or execution state.
- RAG collections, source authority, citation graph, evidence lineage, or privilege boundaries.
- Red Team / Blue Team findings and remediation loops.
- Human approval queues and release gates as interactive workflow states.
- Cloudflare infrastructure bindings, environments, workflow runs, queues, D1, R2, Vectorize, AI Gateway, or Durable Object state.
- Search, filters, current/proposed architecture mode, health overlay, or change-impact analysis.

These are product-scope gaps, not isolated styling defects.

## Visual findings

### P0 — Dashboard shell is absent

The existing page is a marketing/intake document. It cannot answer the operational question: “What is happening in this matter right now?”

**Recommendation:** add an authenticated `/command-center` surface with a persistent GLAW application shell: navigator, command bar, main workspace, inspector, and bottom status rail.

### P0 — No matter workspace

The new registries require the user to open one matter and understand humans, agents, workflow, documents, evidence, authorities, sources, risks, approvals, and deadlines. None of that is currently reachable from the rendered surface.

**Recommendation:** make `/matters/[matterId]` the first operational workspace. Start with Overview, Workflow, Documents, Evidence, Approvals, Risk, and Audit tabs.

### P0 — No graph interaction model

There is no canvas, graph drill-down, swimlane view, or node inspector. The existing eight-stage pipeline is static content rather than a canonical graph projection.

**Recommendation:** preserve the eight stages as a registry-backed intake workflow, then render it through a selective React island using `@xyflow/react`. Keep workflow definitions separate from canvas coordinates.

### P1 — Visual system mismatch needs an explicit decision

The existing intake surface is light, editorial, and document-like. `DESIGN.md` defines a dark, industrial control-plane system for the dashboard.

**Recommendation:** use two related modes rather than forcing one visual treatment everywhere:

1. Public intake: retain the current light editorial style.
2. Authenticated operations: use the dark control-plane shell for dense graph, status, risk, and telemetry work.

Share typography, spacing primitives, status semantics, and accessibility rules between modes.

### P1 — Registry content can drift from marketing copy

The page claims “Fourteen divisions” and “over 180 specialist seats,” while the discovered registries and inventory contain their own counts and statuses. These values must come from one source of truth.

**Recommendation:** make department, agent, and workflow counts generated from the registries, with confirmed/inferred/proposed status visible in internal views.

### P1 — File URL console error

The gstack console check reported a `net::ERR_FILE_NOT_FOUND` during the `file://` inspection. This is expected risk for root-relative assets and routes under a file URL; it is not sufficient evidence of a production failure.

**Recommendation:** repeat the console check against the actual Worker/HTTP serving path before changing assets. Do not treat this finding as a confirmed production defect yet.

## Recommended dashboard composition

```text
GLAW shell
├── left navigator: Command Center, Matters, Workflows, Agents, Knowledge, Governance
├── top command bar: matter selector, global search, environment, run, alerts, user
├── main workspace: metrics, matter queue, active workflow, agent team, approvals, RAG health
├── right inspector: selected matter/node/approval/evidence details
└── bottom rail: validation, Red Team, Blue Team, audit, execution events, errors
```

## Initial dashboard MVP

1. Authenticated Command Center with registry-backed counts.
2. Matter list and matter detail workspace.
3. Workflow run panel using the existing intake stages as the first canonical workflow.
4. Static graph projection in a React island, with selection and inspector.
5. Approval queue and risk/release status.
6. Registry-backed department and agent navigation.
7. Evidence/citation placeholders that clearly state when telemetry or source data is unavailable.
8. Accessibility and responsive behavior for the shell before adding dense graph features.

## Implementation boundary

Do not convert the existing public page into a React SPA. Keep Astro as the target application shell, use React only for interactive graph islands, and expose Cloudflare Worker/D1 control-plane APIs behind authenticated routes. The current app’s intake route can become the public entry point into matter creation.

## Overall assessment

**Public intake design:** strong foundation  
**GLAW operational dashboard readiness:** not started  
**Architecture Explorer readiness:** target design exists, rendered product surface absent  
**Recommended action:** preserve intake, build the authenticated Command Center and matter workspace as the next slice

