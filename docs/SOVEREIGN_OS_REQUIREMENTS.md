# GLAW Sovereign Legal Intelligence OS — Governing Requirements

This document incorporates the supplied Sovereign Legal Intelligence OS
directive into the repository architecture. It governs future implementation;
it does not claim that proposed capabilities are already shipped.

## Mission

GLAW is a governed legal execution operating system, not a chatbot, generic RAG
application, or Legora/Harvey clone. Its core value is governed execution,
evidence provenance, matter intelligence, adversarial verification, and
accountable automation.

## Non-negotiable invariants

1. Authorization is resolved before retrieval, embedding exposure, model context,
   tool execution, document download, external submission, and workflow advance.
2. Consequential actions use a command envelope, idempotency, durable receipts,
   external lookup, and reconciliation.
3. Retrieved content and tool output are untrusted data, never policy or
   executable instructions.
4. Tenant, matter, privilege, conflict, ethical-wall, jurisdiction, and
   retention filters apply at every data and execution boundary.
5. High-risk work requires evidence verification, contradiction search,
   Red/Blue review, Judge disposition, and configured human approval.
6. No unverified AI inference becomes a canonical matter fact automatically.
7. Every material conclusion, model invocation, tool call, approval, edit,
   external receipt, and final artifact is versioned and attributable.
8. Critical state is reconstructable from immutable events; materialized views
   are performance projections, not the audit authority.
9. Models, providers, storage, search, vector, queue, identity, and observability
   systems are replaceable behind contracts.
10. No feature is production-ready until threat modeled, isolated, observable,
    tested under failure, benchmarked, and rollback-capable.

## Canonical state machine

```text
REQUESTED → IDENTIFIED → CONFLICT_CHECKED → AUTHORIZED → POLICY_RESOLVED
→ PLANNED → EVIDENCE_REQUESTED → EVIDENCE_ACQUIRED → EVIDENCE_VALIDATED
→ ANALYZED → DRAFTED → CITATION_VERIFIED → RED_TEAMED → BLUE_TEAMED
→ JUDGED → HUMAN_REVIEW → APPROVED → EXECUTION_AUTHORIZED
→ EXTERNALLY_SUBMITTED → EXTERNAL_RECEIPT_RECEIVED → EXTERNAL_STATE_VERIFIED
→ CLOSED
```

Exceptional states include `BLOCKED`, `QUARANTINED`, `REVOKED`, `EXPIRED`,
`FAILED`, `TIMED_OUT`, `PARTIALLY_COMPLETED`, `COMPENSATING`,
`RECONCILIATION_REQUIRED`, `HUMAN_ESCALATION`, `LEGAL_HOLD`, and `INCIDENT`.

## Required planes

```text
Control Plane → Matter / Conflict / Authorization Graphs
→ Workflow and Agent Execution → Model Gateway
→ Evidence / Authority / Claim Graphs → Data and Event Plane
→ Integration Fabric → Trust, Audit, Evaluation, and Observability Plane
```

## First implementation dependency order

```text
audit → canonical schemas/IDs/events → control plane → matter/evidence graph
→ secure retrieval/citation → model gateway → agent runtime
→ Red/Blue/Judge → durable workflows → integrations → evaluation → UX
```

The first safe vertical slice is a cited research memo that passes through
Evidence, Citation, Red/Blue, Judge, and human approval before export.
