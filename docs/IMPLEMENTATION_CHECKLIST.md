# GLAW Enterprise Implementation Checklist

This is the authoritative delivery checklist. A checked item requires code or a signed external artifact plus verification evidence.

## Product and experience

- [x] Live Matter Room reads authorized server snapshot when authenticated
- [x] Workflow run/task/evidence states are visible and fresh when snapshot is available
- [x] Human approval and rejection/revocation API controls
- [x] Pause, resume, freeze, and terminate workflow controls
- [x] Evidence-to-claim inspection with source/version/span metadata
- [ ] Accessible keyboard, screen-reader, contrast, reduced-motion, and 375px checks
- [ ] Word, Outlook/Gmail, Portal, and Mobile production surfaces

## Control plane

- [x] Canonical command envelope and idempotency
- [x] Risk-based escalation and fail-closed authorization ordering
- [x] Recursive relationship graph with bounded traversal
- [x] Ethical-wall and privilege denial primitives
- [ ] OIDC identity federation
- [ ] SCIM provisioning/deprovisioning
- [ ] JIT access and revocation epoch enforcement
- [ ] Full conflict graph and entity resolution
- [ ] Legal holds, retention, deletion, and incident freezes

## Evidence and legal intelligence

- [x] Matter/workflow/task/evidence persistence contracts
- [x] Signed audit export contract and hash chain
- [x] KMS/HSM provider-agnostic signing adapter contract
- [ ] KMS/HSM production provider binding
- [x] Claim/evidence graph write and matter snapshot read APIs
- [ ] Authority graph and negative-treatment pipeline
- [ ] Temporal/bitemporal law queries
- [ ] Hybrid lexical/vector/graph retrieval
- [ ] Citation verification against exact source spans
- [ ] Contradiction and research-completeness engine
- [ ] Attorney-reviewed jurisdiction/practice benchmark packs

## Agent and model platform

- [x] Model policy contract
- [x] Mandatory model-gateway invocation boundary
- [x] Model registry persistence/API
- [x] Rollout stage policy and rollback decision logic
- [x] Runtime model invocation audit helper
- [ ] Prove every production model call is intercepted
- [ ] Benchmark runner and golden datasets
- [x] Benchmark-gated canary promotion and rollback API
- [ ] Shadow traffic controller
- [x] Agent budget and loop-detection primitives
- [x] Skill manifest signature/version validation primitive

## Integrations and external effects

- [x] Connector operation state machine
- [x] Receipt/lookup/reconciliation contract
- [x] Retry and dead-letter persistence
- [x] Connector worker retry/receipt/reconciliation logic
- [ ] Durable queue worker implementation
- [ ] DMS connector
- [ ] Email connector
- [ ] DocuSign connector
- [ ] Court/e-filing connector
- [ ] Billing connector
- [ ] CRM connector
- [ ] Duplicate webhook and timeout recovery tests

## Platform and operations

- [x] Region policy and fencing contract
- [x] Replication-job persistence
- [x] SLO and cost metric contracts
- [ ] Multi-region replication and failover
- [ ] Residency enforcement at every storage/index/cache/queue boundary
- [ ] Disaster recovery restore test
- [x] OpenTelemetry-compatible exporter adapter and redaction
- [ ] SIEM integration and redaction verification
- [ ] Backup, restore, incident, failover, and rollback runbooks
- [ ] Production deployment and staged canary

## Security and quality

- [x] STRIDE + AI threat model
- [x] Security evaluation plan and baseline fixtures
- [x] Chaos fault disposition contract
- [x] Executable cross-tenant and privilege regression suite
- [x] Local command and Matter snapshot authorization regression smoke
- [x] Prompt-injection and malicious-document policy fixture suite
- [ ] Provider outage and queue chaos execution
- [ ] Load/performance/latency evaluation
- [ ] Supply-chain SBOM/signing/SAST/DAST/secret/license gates
- [ ] Independent legal review
- [ ] Independent security review

## Release gate

The GLAW release is not production-ready until every applicable unchecked item has either been implemented and verified or has an approved external dependency record with owner, evidence request, and target date. No unchecked item may be represented as complete in product messaging.

## Active implementation backlog

- [x] API: workflow task create with audit and duplicate protection
- [x] API: evidence item create/validate/quarantine with privilege defaults
- [x] API: claim-to-evidence links and unsupported-claim blocking
- [x] API: dead-letter list/review/replay/discard controls
- [x] API: signed audit verification response
- [x] API: model benchmark registration
- [x] API: canary promotion/rollback controller
- [x] Contract: OIDC/SCIM provider-neutral identity lifecycle
- [x] Contract: OpenTelemetry/SIEM export with content redaction
- [x] Schema: conflict graph, legal holds, and retention controls
- [x] Tests: new workflow, evidence, claim, model, connector, and security endpoints in local E2E smoke
