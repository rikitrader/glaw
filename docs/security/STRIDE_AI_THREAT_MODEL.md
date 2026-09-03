# GLAW STRIDE + AI Threat Model

Status: baseline control design; independent review required before production.

## Trust boundaries

1. User surfaces to API gateway.
2. Gateway to control plane and authorization decision point.
3. Control plane to evidence/retrieval plane.
4. Agent runtime to model gateway and capability-scoped tools.
5. Connector fabric to external systems.
6. Tenant data to storage, queues, logs, backups, and exports.

## Primary assets

Tenant and matter data, privileged documents, identity and policy state, evidence provenance, audit chain, model/provider credentials, external-action receipts, and customer export packages.

## Threat register

| ID | Threat | Control | Required evaluation |
| --- | --- | --- | --- |
| T1 | Cross-tenant read or context exposure | tenant-scoped auth at API, DB, search, object, cache, queue, export | negative access matrix |
| T2 | Privilege escalation or ethical-wall bypass | relationship tuples, recursive graph checks, default deny, policy versioning | graph traversal tests |
| T3 | Spoofed identity or replayed command | OIDC/SCIM, short-lived identity, command expiry, idempotency | token/replay tests |
| T4 | Audit tampering | append-only chain, KMS/HSM signatures, signed exports | signature and continuity tests |
| T5 | Prompt injection in evidence/tool output | trust hierarchy, structural isolation, capability tools | malicious-document fixtures |
| T6 | Hallucinated or stale legal authority | authority graph, temporal filters, citation verification, red team | legal benchmark regression |
| T7 | Duplicate external side effect | prepare/approve/commit/verify, idempotency, reconciliation | duplicate webhook and retry chaos |
| T8 | Connector compromise or overreach | scoped capabilities, connector policy, secret isolation | permission boundary tests |
| T9 | Model substitution or provider outage | model gateway enforcement, pinned registry, fail-closed high risk | outage/canary tests |
| T10 | Queue loss or unknown workflow state | durable events, checkpoints, DLQ, replay and reconciliation | worker crash/partition chaos |
| T11 | Region leakage or split brain | residency policy, fencing epoch, region-local keys, fail-closed writes | region failover simulation |
| T12 | Sensitive data in telemetry | content-free structured logs, redaction, SIEM filters | log inspection tests |
| T13 | Supply-chain compromise | lockfiles, SBOM, signed artifacts, sandboxed skills, CI gates | dependency/artifact tests |
| T14 | Insider misuse or unauthorized export | approval gates, export audit, DLP, legal hold | insider scenario review |

## Security invariants

- Deny before retrieval or model exposure.
- No consequential command without policy authorization and required approval.
- No high-risk result without evidence, contradiction, citation, and human gates configured by policy.
- No external completion without authoritative reconciliation.
- No unverified inference becomes a canonical matter fact.
- No secret enters model context or ordinary logs.

## Review ownership

Security engineering owns the control tests; legal operations owns authority and privilege policy; SRE owns resilience and recovery; an independent legal/security reviewer must sign the production readiness decision.
