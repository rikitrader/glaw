# GLAW Enterprise Hardening Plan

Status: proposed implementation plan  
Date: 2026-08-27  
Owner: Platform/Security Lead with GLAW Chief approval

## Objective

Close six production-readiness gaps without weakening the existing GLAW gates:

1. signed audit exports;
2. full relationship-based authorization;
3. external connector reconciliation;
4. enforced Model Gateway routing;
5. multi-region deployment and residency;
6. formal chaos, security, and legal-AI evaluation.

The release rule is fail closed: uncertainty, stale authority, revoked access,
unknown external state, or failed evidence integrity produces `REVIEW`, `BLOCK`,
or `RECONCILIATION_REQUIRED`, never a false success.

## Ownership lanes

| Lane | Owner | Cannot bypass |
|---|---|---|
| Control Plane | Platform Engineering | policy, authorization, receipt state |
| Security | Security Engineering | tenant isolation, secrets, revocation |
| Evidence/Audit | Legal Knowledge + Compliance | provenance, retention, signed export |
| Integrations | Integration Engineering | lookup, idempotency, reconciliation |
| Models | AI Systems | registry, benchmark, residency, budget |
| SRE/Regions | SRE | failover, restore, SLO, residency |
| Evaluation | QA + independent legal reviewer | benchmark and release evidence |

## Phase 1 — Signed audit exports

### Design

Extend `governed_audit_events` into a tamper-evident, exportable chain:

```text
event payload
→ canonical serialization
→ previous event hash
→ event hash
→ tenant signing key
→ signed export manifest
```

Add:

- canonical JSON serialization rules;
- sequence number per tenant and stream;
- previous-hash and event-hash validation;
- key version and signing algorithm metadata;
- export manifest with time range, tenant, matter filters, event count, root
  hash, artifact hashes, and policy version;
- detached signature and public-key certificate/verification metadata;
- export access audit and revocation status;
- legal-hold and retention checks before export/deletion.

### Security rules

- Signing keys live in KMS/HSM or an equivalent managed boundary, never in the
  database or model context.
- Audit payloads are minimized; privileged document contents do not enter normal
  logs.
- An export is invalid if events are missing, reordered, duplicated, altered, or
  outside the authorized scope.
- Verification works offline from the export package and published public key.

### Exit criteria

Create, export, verify, tamper, partial-export, wrong-tenant, revoked-key, and
legal-hold test cases. A signed GLAW Proof Packet must verify without contacting
the production database.

## Phase 2 — Full relationship-based authorization

### Canonical relationship model

Implement a Zanzibar-style relation store behind an authorization interface:

```text
tenant#member → organization
team#member → matter
matter#client → client
matter#party → party
matter#opposing_party → party
document#matter → matter
document#privilege → classification
document#ethical_wall → wall
user#reviewer → workflow
```

Every decision evaluates:

```text
actor + action + resource + matter + tenant + role
+ privilege + conflict + jurisdiction + retention + policy version
```

### Implementation

- Add relationship, tuple, policy, decision, and revocation schemas.
- Add `ALLOW`, `DENY`, and `ESCALATE` decision records with explanations.
- Enforce checks before document download, retrieval, embedding, model context,
  tool use, workflow transitions, and exports.
- Add relationship expansion limits and cycle detection.
- Cache only with authorization-context-bound keys and short TTLs.
- Invalidate decisions on membership, ethical-wall, policy, legal-hold, or
  revocation changes.
- Default unknown privilege or conflict status to restrictive handling.

### Exit criteria

Automated negative tests prove that Tenant A, a walled team, an opposing party,
and an unprivileged reviewer cannot retrieve or expose Tenant B/matter-restricted
content through API, search, vector, cache, logs, exports, or model context.

## Phase 3 — External connector reconciliation

### Connector interface

Every connector implements:

```typescript
interface GovernedConnector {
  capabilities(): Promise<ConnectorCapabilities>;
  prepare(command: LegalCommand): Promise<PreparedOperation>;
  submit(operation: PreparedOperation): Promise<SubmissionReceipt>;
  lookup(reference: ExternalReference): Promise<ObservedExternalState>;
  reconcile(expected: ExpectedState, observed: ObservedExternalState): ReconciliationResult;
  compensate?(operation: PreparedOperation): Promise<CompensationReceipt>;
}
```

### State machine

```text
PREPARED
→ VALIDATED
→ HUMAN_APPROVED (when required)
→ SUBMITTED
→ RECEIPT_RECEIVED
→ LOOKUP_PERFORMED
→ EXPECTED_VS_OBSERVED
→ CONFIRMED | RECONCILIATION_REQUIRED | FAILED
```

### Implementation order

1. reference connector with deterministic fake external state;
2. DMS read/write connector;
3. email draft/send connector;
4. DocuSign/signature connector;
5. court/e-filing connector;
6. billing/payment connector only after separate financial controls.

No connector receives a broad credential. Each declares idempotency, lookup,
webhook, rate-limit, and compensation capabilities.

### Exit criteria

Test duplicate submit, timeout before effect, timeout after effect, reordered
webhooks, stale lookup, provider outage, changed authorization, partial batch,
and compensation failure. Unknown external state always enters a visible
reconciliation queue.

## Phase 4 — Enforced Model Gateway

### Boundary

All model calls pass through one gateway. Direct provider imports are rejected by
lint/CI for application services.

The gateway resolves:

```text
task + risk + matter jurisdiction + residency + policy
→ approved model/version/provider
→ budget and timeout
→ structured output contract
→ telemetry and benchmark binding
```

### Model registry

Track provider, model/version, region, capabilities, pricing, latency, legal
benchmark scores, citation accuracy, unsupported-claim rate, failure rate, data
policy, approved risk classes, and deprecation status.

### Enforcement

- Pin provider/model versions per workflow run.
- Reject unregistered or disallowed models.
- Reject residency violations.
- Reject structured-output and tool-use contract failures.
- Enforce token, cost, call-count, and latency budgets.
- Permit fallback only when policy explicitly allows it.
- Record every model request and response digest, not privileged raw content in
  ordinary logs.
- Use benchmark, shadow, canary, and rollback gates before global rollout.

### Exit criteria

CI proves that direct provider calls fail policy checks. Runtime tests prove
disallowed provider, budget exhaustion, timeout, schema failure, silent
substitution, and canary regression all fail closed or escalate.

## Phase 5 — Multi-region and deployment modes

### Region model

Treat region as a tenant policy, not a deployment detail:

```text
Tenant → residency policy → allowed region(s) → data/control placement
```

Initial region classes:

```text
US · EU · UK · LATAM · APAC · PRIVATE · ON_PREM · AIR_GAPPED
```

### Data placement

- Tenant-scoped relational state resides in the assigned region.
- Original documents and proof packets never replicate outside policy scope.
- Global control metadata contains identifiers and health only unless explicitly
  permitted.
- Keys are region-bound and rotated independently.
- Model routing rejects providers outside the tenant’s residency policy.

### Availability

- Single-region failure: fail over only to policy-approved region.
- Cross-region replication: versioned, encrypted, and tested by restore.
- Writes use region authority and fencing epochs to prevent split-brain.
- External commands are region-pinned and never replayed blindly after failover.
- Read-only degraded mode is available when write authority is unavailable.

### Exit criteria

Prove tenant placement, region failover, fencing, restore, key rotation, queue
replay, legal-hold preservation, and no cross-region privileged-data leakage.
Document RPO/RTO per deployment tier.

## Phase 6 — Formal chaos, security, and legal-AI evaluation

### Threat model

Run STRIDE plus AI-specific analysis for:

```text
cross-tenant leakage · privilege escalation · prompt/tool injection
malicious documents · connector compromise · provider compromise
workflow replay · duplicate side effects · evidence tampering
audit tampering · insider abuse · supply-chain compromise
```

### Chaos matrix

Inject failures in:

```text
model provider · retrieval · database · object storage · queue
connector · webhook · network · region · identity provider · KMS
```

For every failure, assert one of:

```text
safe retry · visible unknown state · human escalation · fail closed
```

### Evaluation suites

- authorization and tenant-isolation suite;
- citation and authority suite;
- jurisdiction/temporal-law suite;
- privilege and DLP suite;
- Red/Blue/Judge suite;
- connector receipt/reconciliation suite;
- model routing and substitution suite;
- malicious PDF/prompt/tool injection suite;
- performance, cost, and latency suite;
- disaster recovery and proof-packet verification suite.

Every defect produces a regression test or benchmark case with owner, severity,
root cause, blast radius, remediation, and status.

### Production exit criteria

A release requires:

- independent security review;
- independent legal-professional review for high-risk workflows;
- zero critical tenant-isolation failures;
- zero unhandled consequential-command paths;
- signed proof-packet verification;
- successful chaos run at the declared deployment tier;
- benchmark thresholds met with confidence intervals where applicable;
- runbooks, rollback, restore, and incident drills completed;
- telemetry for quality, cost, latency, retries, and reconciliation.

## Dependency-ordered delivery schedule

```text
1. contracts and migration fixtures
2. relationship authorization and pre-retrieval enforcement
3. signed audit chain/export
4. connector interface and reconciliation queue
5. Model Gateway enforcement
6. single-region production hardening
7. multi-region/residency rollout
8. formal chaos/security/evaluation certification
```

Do not begin multi-region replication or broad connector rollout before the
authorization, command receipt, and audit contracts are proven.

## First executable hardening slice

Build one fully tested path:

```text
authenticated actor
→ relationship authorization
→ matter-scoped command
→ model gateway decision
→ signed audit event
→ fake external connector
→ receipt + lookup + reconciliation
→ signed proof export
```

This slice provides the shortest meaningful proof that GLAW can explain who acted,
what was authorized, what model ran, what evidence was used, what external state
changed, and whether the final record can be independently verified.
