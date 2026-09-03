# Workflow Studio UX Completion Plan

**Goal:** close every remaining UX gap in the Workflow Studio without creating
false confidence about server state, legal approval, model execution, or
external effects.

## Delivery order

- [x] Read APIs and scope contract
- [x] Review rail and authoritative status
- [x] Safe editing and assistant proposals
- [x] Accessibility and mobile emergency mode
- [x] Critical-path/swimlane visualization
- [x] Fault, reload, and release verification

## Acceptance contract

Every visible state must answer:

```text
What is true on the server?
What is only local design state?
What is blocked?
What evidence or receipt proves it?
Who may act next?
What external side effect can occur?
```

## UX work items

### Authoritative review rail

- [x] Runs panel reads tenant/matter-scoped workflow runs and receipts.
- [x] Red Team panel reads review findings with severity and evidence links.
- [x] Blue Team panel reads repairs and re-check state.
- [x] Approvals panel reads pending decisions and supports guarded approve/reject.
- [x] Logs panel reads tenant-scoped audit events without privileged payload leakage.
- [x] All panels show loading, empty, stale, error, denied, and refreshed states.

### Safe editing

- [x] Delete requires impact confirmation.
- [ ] Protected gates cannot be deleted without explicit elevated confirmation.
- [x] Assistant creates a typed proposal and never mutates directly.
- [ ] Proposal preview shows diff, risk, capabilities, cost, and approval impact.
- [ ] Applying a proposal creates a revision and revalidates the graph.
- [x] Save state is server-backed and distinguishes local recovery from server save.
- [x] Concurrent edits show a stale revision conflict with reload/compare options.

### Accessibility and responsive behavior

- [ ] All actionable icons have accessible names.
- [x] Nodes are keyboard focusable and inspectable.
- [x] Keyboard shortcuts support focus, delete, undo, validate, and review tabs.
- [ ] Screen-reader live region announces state transitions.
- [ ] Review tabs have correct tablist/tab/tabpanel semantics.
- [x] Mobile uses one active rail/bottom sheet at a time.
- [ ] 375px supports validate, approve/reject, pause, and revoke.

### Graph comprehension

- [ ] Swimlanes expose workflow phases.
- [ ] Critical-path mode highlights routes to external effects.
- [ ] List view mirrors graph nodes and dependencies.
- [ ] Edges distinguish data, evidence, control, and side-effect transitions.
- [ ] Filters expose blocked, high-risk, unconfigured, and stale nodes.

## Release gates

- [ ] No dead buttons or misleading action labels.
- [ ] No client-only state presented as authoritative.
- [ ] Cross-tenant read and mutation tests pass.
- [ ] Revision conflict and reload recovery pass.
- [ ] Keyboard/screen-reader/contrast/mobile checks pass.
- [ ] Build and local integration suite pass.
- [ ] Independent legal operations, security, and accessibility review remains
  required before consequential production use.
