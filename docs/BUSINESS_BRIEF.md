# GLAW Agentic Legal OS — Business Brief

## Outcome

Produce faster, more defensible legal work-product from a matter request by
coordinating specialist agents under evidence, citation, adversarial-review, and
human-approval gates.

## Users

- Licensed lawyers and legal operations teams
- Firm knowledge, risk, and innovation leaders
- In-house legal departments
- Clients receiving controlled, matter-scoped collaboration

## Primary entity

The primary entity is a **Matter**. A matter owns its parties, documents,
jurisdiction, tasks, evidence, claims, citations, findings, approvals, deadlines,
runs, and deliverables.

## Decision and side effect

GLAW may perform informational and preparatory work autonomously. Filing,
signing, serving, charging, paying, sanctioning, or other binding actions require
lawful human authority and a durable approval receipt.

## Source of truth

Canonical matter state is the governed matter graph and its immutable evidence
records. Existing GLAW workpapers remain authoritative during migration. UI
canvas state, caches, model output, and event streams are not authoritative.

## Success metrics

- time from intake to usable first draft;
- citation and source-groundedness rate;
- unsupported-claim and stale-source rate;
- Red Team critical findings detected before approval;
- human correction hours per deliverable;
- workflow completion and external-integration reconciliation rate;
- cost and latency per matter.

## Stop conditions

Stop or route to human review on unresolved conflicts, missing authority,
stale evidence, tenant or ethical-wall uncertainty, critical Red Team findings,
Judge failure, revoked authority, evidence outage, or unknown external effect.

## Governed workflow composition

Every executable workflow is composed from a versioned department, persona,
skill, adapter, and jurisdiction/practice pack. A lawyer or agent persona cannot
exist as an unowned canvas node: it must be attached to a workflow and resolved
to an allowed department, signed skill set, capability-scoped tools, and a
configured review policy.

API and MCP adapters are provider boundaries, not direct credentials. x402 is an
optional usage-settlement policy for agent/tool work; it can meter or authorize
compute spend, but it never authorizes a filing, client communication,
signature, settlement, payment, or disclosure.
