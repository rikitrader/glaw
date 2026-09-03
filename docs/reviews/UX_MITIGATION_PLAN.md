# GLAW Workflow Studio — Full UX Mitigation Plan

**Purpose:** close the red-team findings in
`UX_RED_TEAM_MITIGATION_REPORT.md` and make the Studio truthful, reviewable,
accessible, and safe for governed legal workflow authoring.

**Primary users:** supervising lawyers, legal operations, knowledge engineers,
security administrators, and matter teams.

**Source of truth:** server-authoritative workflow snapshots and immutable
workflow events. The React Flow canvas is a projection and editing surface;
browser storage is presentation-only recovery state.

**Release rule:** no consequential workflow may be published or executed until
all P0 work is complete, all required P1 work is complete, and the independent
legal, security, and accessibility reviews sign the evidence packet.

## Current state

The Studio is a functional visual sandbox. The following are intentionally
open, not represented as complete:

- [ ] server-authoritative workflow save/publish/run
- [ ] durable tenant/matter/revision scope
- [ ] server-backed dry-run and execution receipts
- [ ] authoritative adapter readiness and reconciliation status
- [ ] real evidence-backed Runs/Red Team/Blue Team/Approvals/Logs panels
- [ ] keyboard-complete canvas editing and mobile emergency flow
- [ ] independent acceptance reviews

## Delivery lanes and accountable owners

| Lane | Owner | Cannot bypass | Deliverable |
|---|---|---|---|
| Business & operations | Legal operations lead | policy and acceptance gates | workflow lifecycle, escalation, operator runbook |
| Product & experience | Staff product designer | authority or external-effect broker | state inventory, journeys, accessible interaction contract |
| Contracts & data | Staff platform engineer | domain policy decisions | versioned snapshot, revision, receipt, and catalog schemas |
| Control plane | Principal control-plane engineer | evidence and adapter truth | commands, authorization, revision fencing, approvals |
| Integrations | Integration lead | direct browser commands | adapter health, capabilities, idempotency, lookup, reconciliation |
| Evidence & compliance | Legal knowledge/security lead | operational approval authority | validation findings, proof packet, audit references |
| Platform & security | Security engineer | business approval semantics | tenant isolation, secrets, CSRF, injection defense, telemetry |
| Quality & release | QA/release lead | modifying product policy | E2E, fault, accessibility, load, and release certification |

## State model

The UI must represent these states separately:

```text
DESIGN_SANDBOX
LOCAL_RECOVERY
SAVING
SAVED_SERVER
STALE_REVISION
CONFLICT
VALIDATION_BLOCKED
READY_FOR_REVIEW
APPROVAL_PENDING
PUBLISH_REQUESTED
PUBLISHED
DRY_RUN_PREPARED
DRY_RUN_RUNNING
LIVE_RUN_REQUESTED
LIVE_RUN_RUNNING
EXTERNAL_EFFECT_UNKNOWN
RECONCILIATION_REQUIRED
FAILED
REVOKED
```

No green visual state may be shown for `PUBLISHED`, `LIVE_RUN_RUNNING`, or
`EXTERNAL_EFFECTIVE` without an authoritative server receipt.

## Phase 0 — Truthful product language and safety containment

**Objective:** prevent user misinterpretation while server work is underway.

- [ ] Replace `autosave on` with an actual state indicator: `Local recovery`,
  `Saving`, `Saved to GLAW`, `Offline`, or `Conflict`.
- [ ] Rename `Publish` to `Request publish` until the server command exists.
- [ ] Rename `Test this workflow` to `Prepare dry run` until a run API exists.
- [ ] Add an always-visible `DESIGN SANDBOX` or `CONNECTED TO GLAW` badge.
- [ ] Add explicit `NO EXTERNAL SIDE EFFECTS` copy to dry-run preparation.
- [ ] Mark demo providers as `DEMO`, `NOT CONFIGURED`, or `SHADOW ONLY`.
- [ ] Disable consequential actions when environment is demo, offline, stale,
  unauthorized, or unconfigured.
- [ ] Add a product copy test that rejects misleading terms such as “sent”,
  “filed”, “executed”, or “published” without a matching receipt.

**Exit evidence:** screenshots and browser tests prove that offline/local/demo
states cannot be mistaken for server execution or external completion.

## Phase 1 — Authoritative scope and revision contract

**Objective:** bind every editing session to the correct tenant, client, matter,
workflow, environment, policy, and server revision.

### Contract

```typescript
type WorkflowSnapshot = {
  tenantId: string;
  clientId?: string;
  matterId?: string;
  workflowId: string;
  revision: number;
  revisionHash: string;
  policyVersion: string;
  environment: "sandbox" | "staging" | "production";
  nodes: unknown[];
  edges: unknown[];
  status: "DRAFT" | "PUBLISHED" | "REVOKED";
  updatedBy: string;
  updatedAt: string;
};
```

- [ ] Add `GET /api/workflows/:id/snapshot` with `no-store` and authorization.
- [ ] Add `PUT /api/workflows/:id/draft` using `If-Match` revision fencing.
- [ ] Add `POST /api/workflows/:id/publish` as a governed command.
- [ ] Add server-side tenant, matter, policy, ethical-wall, skill-signature,
  adapter, model, evidence, and approval validation.
- [ ] Add persistent toolbar scope strip: tenant, client, matter, environment,
  workflow ID, revision, policy version, freshness, and connection status.
- [ ] Scope recovery storage by tenant, client, matter, workflow, revision, and
  authenticated actor; never use a fixed global localStorage key.
- [ ] On scope change, clear the projection, re-fetch authority, and disable
  mutations until the new snapshot is verified.
- [ ] On stale revision, present compare/merge/discard; never silently overwrite.

**Acceptance tests:** cross-tenant snapshot denial; wrong-matter denial;
stale-write rejection; reconnect recovery; policy/fence change disables publish;
same browser with two tenants keeps drafts isolated.

## Phase 2 — Server-backed save, publish, and run lifecycle

**Objective:** align action labels, commands, receipts, and audit events.

### Commands

```text
SAVE_DRAFT
REQUEST_PUBLISH
PREPARE_DRY_RUN
START_SHADOW_RUN
REQUEST_LIVE_RUN
PAUSE_RUN
REJECT_APPROVAL
REVOKE_WORKFLOW
```

- [ ] Convert each mutation into a `LegalCommand` with actor, policy, scope,
  idempotency key, payload hash, risk class, evidence references, and correlation.
- [ ] Persist command and workflow events before returning an optimistic UI state.
- [ ] Return `accepted`, `authorized`, `blocked`, `approval_required`, or
  `reconciliation_required` rather than a generic success message.
- [ ] Implement durable receipts for save, publish, dry-run, and live run.
- [ ] Show receipt ID, run ID, revision, actor, timestamp, and external-effect
  status in the UI.
- [ ] Ensure browser refresh rehydrates from the server receipt, not local state.
- [ ] Keep live execution unavailable unless every configured gate passes.

**Acceptance tests:** network loss before/after command; duplicate command;
worker restart; revoked actor; expired approval; receipt reload; audit record
contains exact revision and payload hash.

## Phase 3 — Runtime/status separation

**Objective:** stop design edits from fabricating runtime facts.

- [ ] Remove the editable runtime `status` select from the inspector.
- [ ] Replace it with editable `designState`: `enabled`, `disabled`, `draft`.
- [ ] Display runtime state as read-only and receipt-backed.
- [ ] Separate node configuration, execution state, and validation state in the
  data model and UI.
- [ ] Add status provenance: `server event`, `human approval`, `adapter receipt`,
  or `not started`.
- [ ] Prevent client payloads from setting `complete`, `approved`, `filed`, or
  `effective` states.

**Acceptance tests:** tampered browser payload cannot create a completed run;
runtime status changes only after a signed/server event; design changes retain
runtime history.

## Phase 4 — Governed node creation and adapter readiness

**Objective:** make unsafe or incomplete nodes impossible to miss.

- [ ] Replace drag-first creation with catalog selection plus configuration
  preview for personas, skills, packs, MCP, API, court, and payment nodes.
- [ ] Show risk class, side-effect class, owner role, required approval, data
  residency, configured state, and required capabilities before placement.
- [ ] Mark unbound nodes `BLOCKED · binding required` on the node itself.
- [ ] Display signed skill version and benchmark status.
- [ ] Display adapter protocol, provider, health, tenant authorization,
  idempotency, lookup, reconciliation, and last check time.
- [ ] Require a confirmation step for irreversible adapters and payment gates.
- [ ] Disable publish if a consequential adapter is unconfigured, unhealthy,
  non-reconcilable, or outside residency policy.
- [ ] Add adapter capability API backed by the connector registry; never infer
  readiness from a node label.

**Acceptance tests:** unknown adapter blocked; stale health blocked; missing
lookup blocked for an idempotent connector; court adapter requires approval and
reconciliation; node badge matches server capability data.

## Phase 5 — x402 payment separation

**Objective:** make metered compute explicit without allowing payment to grant
legal authority.

- [ ] Add a payment policy schema with quote, currency, maximum run/agent spend,
  wallet/facilitator reference, approval threshold, and settlement status.
- [ ] Show `COMPUTE PAYMENT ONLY — DOES NOT AUTHORIZE LEGAL ACTION` adjacent to
  every payment gate.
- [ ] Keep wallet credentials and settlement calls server-side.
- [ ] Require a separate legal command and human approval for filing, sending,
  signing, settlement, disclosure, or client communication.
- [ ] Show quote, authorization, settlement receipt, and failed/unknown states
  independently from workflow status.
- [ ] Add spend budget exhaustion, duplicate settlement, timeout-after-payment,
  and compensation/reconciliation handling.

**Acceptance tests:** paid compute cannot advance a court filing; duplicate
settlement is idempotent; timeout becomes `UNKNOWN`; legal approval is required
even when payment is already settled.

## Phase 6 — Real review surfaces and evidence navigation

**Objective:** turn implied operational tabs into authoritative review tools.

- [ ] Implement `Validation` as a filterable inbox with severity, rule ID, owner,
  affected node/edge, remediation, and block status.
- [ ] Implement `Runs` with run ID, snapshot revision, model calls, tool calls,
  cost, latency, output state, and receipt/reconciliation status.
- [ ] Implement `Red Team` with attacks, evidence, severity, surviving claims,
  and unresolved findings.
- [ ] Implement `Blue Team` with proposed repairs, changed nodes, and re-checks.
- [ ] Implement `Approvals` with reviewer identity, role, policy, expiry,
  quorum/two-person requirements, evidence, and decision history.
- [ ] Implement `Logs` with filtered audit events and proof-packet links; do not
  expose privileged content in ordinary logs.
- [ ] Add `show on canvas` and `open source passage` for every finding.
- [ ] Add evidence-backed empty, loading, stale, error, and permission-denied
  states to every panel.

**Acceptance tests:** every visible tab has a working panel; a finding focuses
the exact node; an approval links to its command and policy; a run links to its
model/tool/evidence lineage.

## Phase 7 — Assistant governance

**Objective:** make AI design assistance proposal-based, reviewable, and safe.

- [ ] Change copy from “I’ll adjust the canvas” to “Propose a workflow change”.
- [ ] Send prompts only through the model gateway; never directly to a provider.
- [ ] Treat user text, retrieved text, tool output, and uploaded documents as
  untrusted data.
- [ ] Return a typed proposal: add/remove/update nodes, edges, bindings,
  permissions, risk delta, cost, latency, and affected scope.
- [ ] Render a diff before applying any proposal.
- [ ] Require explicit confirmation; route high-risk proposals to human review.
- [ ] Re-run server validation after proposal application and before save.
- [ ] Record prompt template, model, context references, proposal hash, reviewer,
  and applied revision in the audit trail.

**Acceptance tests:** assistant cannot alter graph without confirmation; prompt
injection in a document cannot modify policy; unknown tool/capability is blocked;
proposal against stale revision requires refresh.

## Phase 8 — Revision history, undo, deletion, and recovery

**Objective:** make editing reversible and safe under collaboration.

- [ ] Convert edits into typed editor commands: move, connect, bind, rename,
  configure, delete, duplicate, and apply proposal.
- [ ] Coalesce drag movement into one revision on pointer release.
- [ ] Persist revisions server-side with author, timestamp, reason, and diff.
- [ ] Support undo/redo against a revision, not only in-memory React state.
- [ ] Add delete confirmation with impacted downstream gates and side effects.
- [ ] Block deletion of the only approval, evidence, red-team, or reconciliation
  path without elevated permission and explicit confirmation.
- [ ] Add recovery after reload, reconnect, worker restart, and conflicting edit.

**Acceptance tests:** every edit is undoable; deleted gate shows impact summary;
reload restores server revision; concurrent edit produces conflict UI.

## Phase 9 — Accessibility and responsive emergency mode

**Objective:** ensure lawyers can review, reject, pause, and inspect without a
mouse or large screen.

- [ ] Add accessible names to every icon-only button, handle, control, and tab.
- [ ] Add visible focus states and keyboard shortcuts help.
- [ ] Implement keyboard node focus, inspect, move, connect, delete, undo, and
  validation navigation.
- [ ] Add screen-reader live announcements for save, block, approval, pause,
  error, stale, and reconciliation states.
- [ ] Add semantic tablist/tab/tabpanel behavior to the bottom rail.
- [ ] Pair every color state with text/icon/pattern.
- [ ] Support reduced motion and verify contrast.
- [ ] Replace mobile overlapping panels with one active bottom sheet/rail at a
  time, with safe-area padding and a persistent emergency action strip.
- [ ] Ensure 375px supports inspect, validate, approve/reject, pause, and revoke.

**Acceptance tests:** automated accessibility scan; manual keyboard pass;
screen-reader pass; grayscale/contrast pass; 375px emergency flow; reduced
motion pass.

## Phase 10 — Critical-path information architecture

**Objective:** make complex legal workflows understandable at a glance.

- [ ] Add swimlanes: Intake, Research, Analysis, Draft, Verify, Review, Approval,
  External Effect, Reconcile.
- [ ] Add edge labels for data, evidence, control, and side-effect transitions.
- [ ] Add critical-path mode that hides non-critical detail without hiding risk.
- [ ] Add branch collapse/expand and synchronized list view.
- [ ] Add filters for risk, owner, status, adapter, jurisdiction, and blocked state.
- [ ] Keep the minimap as navigation only; never rely on it for meaning.
- [ ] Show high-risk path to output as a distinct review route.

**Acceptance tests:** reviewer can find all high-risk nodes and the path to every
external effect without tracing ambiguous crossing lines.

## Phase 11 — Security, fault, and legal acceptance

- [ ] Cross-tenant negative tests for snapshot, draft, catalog, run, logs, and
  recovery data.
- [ ] Privilege/ethical-wall tests before node catalog exposure and model context.
- [ ] Prompt-injection tests through assistant prompts, PDFs, OCR, adapter output,
  and source passages.
- [ ] Malicious-document tests for scripts, oversized files, malformed metadata,
  and hidden instructions.
- [ ] Duplicate command, duplicate webhook, retry, timeout-before-effect, and
  timeout-after-effect tests.
- [ ] Provider outage, queue redelivery, DLQ, region fence, and database restore
  simulations.
- [ ] Verify signed audit/proof packet includes snapshot hash, revision, policy,
  approvals, model/tool calls, and external receipts.
- [ ] Run load/latency tests for interactive canvas, snapshot, validation, and
  review panels.
- [ ] Obtain independent legal operations sign-off.
- [ ] Obtain independent security sign-off.
- [ ] Obtain independent accessibility sign-off.

## Release gates

### Sandbox release

- [ ] P0 truthfulness findings closed.
- [ ] Demo/connected environment clearly labeled.
- [ ] No external side effects available from sandbox.
- [ ] Accessibility baseline passes.

### Internal governed release

- [ ] Server snapshot/save/publish contracts live.
- [ ] Tenant/matter/revision fencing verified.
- [ ] Server validation and approval gates verified.
- [ ] Runs and approvals panels are authoritative.
- [ ] Security and legal operations review complete.

### Production consequential release

- [ ] Real connectors configured with lookup/reconciliation.
- [ ] x402 settlement and legal-authorization separation verified.
- [ ] Signed audit export and proof packet verified.
- [ ] OTel/SIEM and SLO dashboards live.
- [ ] Chaos, restore, load, rollback, and DR rehearsals passed.
- [ ] Independent legal/security/accessibility approvals recorded.

## Recommended implementation order

1. Phase 0 truthful containment.
2. Phase 1 snapshot/revision contract.
3. Phase 2 save/publish/dry-run receipts.
4. Phase 3 runtime/status separation.
5. Phase 4 adapter readiness and governed creation.
6. Phase 5 x402 separation.
7. Phase 6 review surfaces.
8. Phase 7 assistant proposals.
9. Phase 8 durable revisions and recovery.
10. Phase 9 accessibility/mobile.
11. Phase 10 critical-path IA.
12. Phase 11 independent certification and staged rollout.

## Definition of done

The mitigation is complete only when a supervising lawyer can answer, from the
Studio itself and without inference:

```text
Which tenant/client/matter am I editing?
Which authoritative revision and policy apply?
What is design state versus runtime state?
Which persona, skill, model, evidence, and adapter are bound?
What can this workflow do externally?
What approvals, payment, and reconciliation gates apply?
What did the red team find?
What changed since the prior revision?
Who approved it?
What actually ran, and what external receipt proves it?
```

If any answer depends on a local browser message, a node label, a color, or an
unverified model response, the Studio remains in mitigation.
