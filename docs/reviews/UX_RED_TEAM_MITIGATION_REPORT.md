# GLAW Workflow Studio — UX Red-Team & Mitigation Report

**Review type:** hostile product/security UX review  
**Surface:** `/workflows/studio`  
**Reviewer posture:** opposing counsel, supervising lawyer, accessibility tester, confused operator, malicious document author, and incident responder  
**Review date:** 2026-08-27  
**Status:** findings recorded; selected mitigations remain open unless marked implemented elsewhere

## Executive judgment

The Studio has a strong canvas-first visual direction and a useful governed-node
vocabulary. It is not yet safe to present as a production workflow control
surface. The primary risk is **trust miscalibration**: the UI looks authoritative,
but several actions are local simulations and the canvas is not the source of
truth. A lawyer can mistake a draft, a test preparation message, or a local
browser save for a server-authorized workflow state.

The current design should be treated as a **design sandbox** until the P0 gates
below are closed.

## Findings

| ID | Severity | Attack | Evidence | Required mitigation | Acceptance test |
|---|---|---|---|---|---|
| UX-001 | P0 | An operator clicks **Publish**, sees a successful validation state, and assumes the governed workflow is active. No D1 workflow version is created and no server authorization/approval is invoked. | `WorkflowStudio.tsx:80-83` writes only to `localStorage`; message says publish is simulated. | Replace local publish with a server command: validate snapshot, resolve tenant/matter/policy, create immutable workflow version, require configured approvals, return receipt state. Label unsubmitted drafts explicitly. | Browser publish with network disabled cannot show “published”; authorized publish returns a server receipt and version ID; unauthorized publish is blocked. |
| UX-002 | P0 | A user creates an agent, persona, adapter, or payment node and the canvas can look complete before required bindings are persisted or server-validated. Client validation is not an authority boundary. | `validator.ts`; client-only node state in `WorkflowStudio.tsx`. | Server-side graph validation must re-run catalog, signature, permission, tenant, ethical-wall, model, and approval checks before save/publish/run. | Tampered POST with an unknown persona, skill, adapter, or tenant is rejected even when the browser says valid. |
| UX-003 | P0 | **Test this workflow** sounds like execution but only sets a local finding. This can cause a lawyer to believe tools, models, or external systems were exercised. | `WorkflowStudio.tsx:82`, copy “Test run prepared locally.” | Split actions into `Validate graph`, `Dry run / shadow`, and `Execute`. Show execution receipt, side effects, model calls, and external reconciliation. Never call a preparation state a test run. | Every test state has a run ID and explicit `NO_EXTERNAL_SIDE_EFFECTS`; real execution cannot occur from the dry-run path. |
| UX-004 | P0 | A localStorage draft uses a fixed key, so multiple users, matters, tenants, or workflow versions sharing a browser can load the wrong graph. | `WorkflowStudio.tsx:41,80-81`, fixed `glaw:workflow-studio:litigation-analysis`. | Scope drafts by tenant, matter, workflow ID, user, and schema version; prefer server drafts. Detect stale revision and show conflict resolution. | Two tenants using the same browser never see each other’s draft; stale revision produces a merge/review state. |
| UX-005 | P0 | x402 usage payment is visible as a node but the UI does not clearly distinguish compute authorization from legal authorization, and does not show wallet, quote, settlement, or approval status. | Payment node is represented by a simple label/config; no live receipt UI. | Add a dedicated payment policy panel with quote, budget, wallet/facilitator, settlement receipt, approval threshold, and permanent “does not authorize legal action” warning. Keep all payment actions server-side. | A payment approval cannot advance a filing, communication, signature, settlement, or disclosure command. |
| UX-006 | P1 | The toolbar does not show tenant, matter, environment, policy version, workflow revision, or current authoritative server state. A user may edit the wrong matter or publish into the wrong environment. | Toolbar only displays “Litigation Analysis”, “Draft v3”, and breadcrumbs. | Add a persistent scope strip: tenant/client/matter, environment, policy version, revision, freshness, and server connection. Make scope changes a guarded transition. | Scope change invalidates the snapshot and disables save/publish until reauthorized. |
| UX-007 | P1 | Node status is editable from the inspector. A user can set an agent to `complete`, `approval`, or `running` even though execution state must come from the workflow runtime. | `WorkflowStudio.tsx:97` status `<select>`. | Separate `design status` from `runtime status`; runtime status must be read-only and receipt-backed. For design, use lifecycle fields such as enabled, draft, and disabled. | Editing a node cannot fabricate a completed run or approval state in any API response or audit record. |
| UX-008 | P1 | New nodes are visually added without a guided binding step. A blank Agent or MCP/API adapter can be left in the graph and only discovered later during validation. | `addNode()` creates a default node; inspector fields are optional. | Use typed creation flows: choose catalog item first, preview permissions/risk, then place a fully identified node. Show “Unbound / blocked” directly on the node. | Every unbound required node has a visible blocked badge and publish is disabled. |
| UX-009 | P1 | Adapter configuration does not show whether a provider is configured, healthy, authorized for this tenant, idempotent, or reconcilable. “MCP Adapter” and “API Adapter” look equally ready. | Catalog has `configured`, capability metadata, but node UI only shows a generic adapter chip. | Add adapter readiness card with protocol, provider, capability list, configured state, last health check, residency, idempotency, lookup, and reconciliation support. | An unconfigured or unhealthy consequential adapter cannot pass the readiness gate. |
| UX-010 | P1 | The visual graph can hide critical nodes and crossings. The minimap is not a substitute for a readable execution order, especially with parallel branches and court/payment paths. | Dense 13+ node demo graph; no lane/grouping or critical-path view. | Add swimlanes by phase, explicit edge labels, fit-to-critical-path, branch collapse, dependency warnings, and a list view synchronized with the canvas. | A reviewer can identify all high-risk nodes and the complete path to output without relying on pixel-level edge tracing. |
| UX-011 | P1 | The left palette exposes infrastructure, external API, court, and payment primitives alongside harmless nodes without consequence guidance. A novice can drag an irreversible boundary into a workflow with no upfront warning. | Palette lists all node types uniformly. | Group by intent and consequence; show risk, side-effect class, required role, and setup state before drag. Confirm when adding irreversible nodes. | Adding a court/API/payment node displays the exact approval and reconciliation requirements before placement. |
| UX-012 | P1 | The canvas has no keyboard equivalent for connecting, deleting, moving, or inspecting nodes. Handles and drag interactions are mouse-centric. | `WorkflowStudio.tsx:72,89`; React Flow handles used without keyboard command layer. | Add keyboard command mode, node focus model, accessible edge creation, delete confirmation, focus restoration, and shortcuts help. | A keyboard-only reviewer can create, inspect, validate, and undo a workflow at 375px and desktop widths. |
| UX-013 | P1 | Icon-only controls and symbols (`‹`, `›`, `⋯`, `＋`, minimap controls) lack accessible names and several palette buttons omit descriptions from the accessible name. | Multiple buttons in `WorkflowStudio.tsx:86-100`. | Add `aria-label`, visible tooltips, focus rings, semantic headings, live-region announcements, and non-color status text. | Automated accessibility checks plus manual screen-reader pass find no unlabeled actionable controls. |
| UX-014 | P1 | The fixed full-screen layout hides overflow at `html, body`, while mobile overlays can cover the inspector, palette, validation rail, or action controls. | `studio.astro` global `overflow:hidden`; CSS mobile absolute panels and fixed heights. | Define an emergency mobile mode: one active rail at a time, bottom-sheet inspector, reachable validation, safe-area padding, and no content-only mouse access. | 375px viewport supports scope read, validation, review, pause, and reject without horizontal clipping or inaccessible overlays. |
| UX-015 | P1 | Validation findings are rendered as a stream of inline spans without severity grouping, node focus, remediation action, or stable list keys. The operator must infer what to do next. | `WorkflowStudio.tsx:100`; findings have IDs but no actionable presentation. | Create a validation inbox with severity, affected node/edge, “show on canvas”, rule ID, owner, remediation, and blocking status. | A blocking finding links to the exact node and gives a deterministic next action. |
| UX-016 | P1 | The bottom tabs (`Runs`, `Red Team`, `Blue Team`, `Approvals`, `Logs`) are decorative buttons. They imply deep operational views that do not open. | `WorkflowStudio.tsx:100`. | Implement real tab panels or remove the tabs until backed by APIs. Each tab must display authoritative freshness and empty/error states. | Every visible tab either opens a working view or is absent; no dead controls remain. |
| UX-017 | P1 | The Design Assistant promises to “adjust the canvas” but only emits a local queue message. This is an expectation gap and eventually a prompt-injection boundary if user/retrieved content is sent to an agent without explicit preview. | `WorkflowStudio.tsx:83,92-96`. | Change copy to “Propose a change”; show structured patch preview, affected nodes, permissions, risk, cost, and approval before applying. Treat all imported text as untrusted data. | Assistant never mutates the graph without a diff and explicit confirmation; prompt text cannot bypass policy. |
| UX-018 | P1 | Undo history does not capture all graph mutations, notably React Flow node movement and edge changes unless they pass custom callbacks; history is in-memory and disappears on reload. | `checkpoint()` is called for selected actions only; `onNodesChange` and `onEdgesChange` are passed through. | Use a command-based editor with durable revision history, coalesced drag transactions, undo/redo receipts, and conflict handling. | Move, connect, delete, bind, and rename each produce reversible revisions and survive reload. |
| UX-019 | P2 | “autosave on” is displayed while only explicit local Save draft writes, and the feedback does not distinguish local persistence from server persistence. | Toolbar copy plus `saveDraft()` behavior. | Replace with explicit `Saved locally`, `Saving`, `Saved to GLAW`, `Offline`, or `Conflict`; never claim autosave without a server receipt. | Copy is derived from actual persistence state, not static text. |
| UX-020 | P2 | The hard-coded `v3` is not connected to a workflow revision. Reviewers cannot tell whether they are looking at a current, stale, or superseded definition. | `WorkflowStudio.tsx:86,89`. | Bind revision to server snapshot and show revision digest, last author, timestamp, and superseded state. | Reloading after another user publishes shows a revision conflict instead of silently overwriting. |
| UX-021 | P2 | Demo data includes configured-looking labels such as Court Search Adapter and Legal Research MCP, while the catalog marks some providers unconfigured. This can be mistaken for a live connector. | Demo graph plus catalog `configured` metadata. | Use explicit `DEMO`, `NOT CONFIGURED`, or `SHADOW ONLY` badges and disable consequential actions in demo mode. | A screenshot or screen reader output cannot imply a live court, DMS, email, DocuSign, or payment connection when none exists. |
| UX-022 | P2 | Publish validation requires a human-approval node but does not show the actual named reviewer, approval policy, expiration, or two-person rule. | `validator.ts` only checks node presence and config fields. | Display approval policy as a first-class gate with reviewer identity, role, expiry, evidence, and quorum. | A generic Human Approval node cannot satisfy a critical workflow without a valid reviewer and policy. |
| UX-023 | P2 | Destructive node deletion is one click and there is no visible impact summary. A user can remove an approval, red-team, adapter, or evidence branch accidentally. | `deleteSelected()` and `danger-button`. | Add confirm dialog with impacted downstream nodes, side effects, and undo window; block deletion if it breaks a protected gate without elevated permission. | Deleting the only approval or reconciliation path requires explicit confirmation and leaves a validation block. |
| UX-024 | P2 | Color and small dots carry too much semantic weight. Low/moderate/high, executing, adapter, and human gate are difficult to distinguish under contrast loss or color vision differences. | Chips/dots in `WorkflowStudio.tsx:10-12` and CSS status colors. | Pair color with text, icons, patterns, and a legend tied to accessible labels; verify contrast and focus states. | Status remains understandable in grayscale and with a screen reader. |

## Highest-risk mitigation sequence

### Gate 1 — Truthful state

1. Remove “autosave on”, “Publish”, and “Test this workflow” claims until each is
   connected to a server receipt, or rename them to `Save local draft`,
   `Request publish`, and `Prepare dry run`.
2. Add a visible `DESIGN SANDBOX` or `CONNECTED TO GLAW` environment badge.
3. Show tenant, matter, workflow ID, revision, policy version, and freshness.

### Gate 2 — Server authority

1. Add a server snapshot endpoint and a versioned workflow command endpoint.
2. Revalidate every node binding and edge on the server.
3. Require approval policy resolution before high-risk publish/run.
4. Make the browser canvas a projection of the authoritative workflow definition,
   not the source of truth.

### Gate 3 — Consequence visibility

1. Add adapter readiness, side-effect, idempotency, lookup, reconciliation, and
   residency status to every boundary node.
2. Add x402 quote/approval/settlement states and permanent legal-authority
   separation language.
3. Distinguish dry-run, shadow-run, and live execution in the action model and UI.

### Gate 4 — Reviewability

1. Replace decorative bottom tabs with real evidence-backed panels.
2. Add critical-path/list view and validation inbox.
3. Add diff-before-apply for assistant proposals and revision conflicts.
4. Make approval, red-team, blue-team, judge, and audit status inspectable from
   the affected node.

### Gate 5 — Accessibility and recovery

1. Add names and keyboard paths for every action.
2. Add mobile emergency workflow for review/reject/pause.
3. Add durable undo/revision history, delete confirmation, and recovery after
   reconnect.

## Red-team conclusion

**Destroyed assumptions:**

- A polished white canvas is not evidence of a governed workflow.
- A green validation message is not server authorization.
- A visible adapter is not a configured integration.
- A payment node is not legal authority.
- A local draft is not a tenant-scoped workflow version.
- A “test” label is not proof that a model, tool, or external system ran.

**Release recommendation:** BLOCK production-facing workflow authoring until
UX-001 through UX-006 are closed and independently tested. The design can remain
available as a clearly labeled sandbox while the server-backed control path is
implemented.

**Independent review required:** legal operations owner, security reviewer, and
accessibility reviewer must sign the acceptance evidence before this surface can
authorize or publish consequential workflows.
