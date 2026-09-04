# Current vs Target Gap Analysis

| Capability | Current | Target | Gap | Risk | Priority | Migration |
|---|---|---|---|---|---|---|
| Command envelope | partial gate/CLI semantics | universal typed envelope | no shared contract | high | P0 | wrap existing commands |
| Legal state machine | pipeline and gates | explicit lifecycle + exceptions | state vocabularies differ | high | P0 | adapter over existing stages |
| Control plane | partial Worker/Astro scaffolds | authoritative tenants, policy, approvals, receipts | fragmented persistence/auth | critical | P0 | build contracts first |
| Matter graph | docs/registries/workpapers | canonical graph with temporal provenance | no unified runtime graph | high | P0 | preserve workpaper IDs |
| Conflict graph | ethics skill/checks | entity-resolution graph traversal | text/skill checks not universal | critical | P0 | add read-only conflict service |
| Authorization graph | token/RBAC pieces | pre-retrieval relationship authorization | end-to-end proof missing | critical | P0 | deny-by-default adapter |
| Evidence ledger | source hashes and verification bundle | claim/evidence/authority graph | partial graph lineage | high | P0 | promote workpapers |
| Citation engine | strong source/citation gates | span/version/jurisdiction/temporal binding | richer binding needed | high | P1 | extend current validators |
| Model Gateway | provider adapters/config | registry, routing, canary, budgets | no unified policy plane | high | P1 | adapter around providers |
| Agent registry | broad skills/roster | typed, signed, scoped capabilities | normalization and signing gap | high | P1 | registry-first |
| Durable workflow | local pipeline/scaffold | event-sourced durable DAG/state machine | no confirmed production runtime | high | P1 | shadow existing pipeline |
| Integration fabric | MCP/adapters | capability + receipt + reconciliation | inconsistent connector semantics | high | P1 | connector contract |
| Observability | doctor, X402, local artifacts | traces, SLOs, cost, security, quality | fragmented telemetry | high | P1 | normalized events |
| Evaluation | benchmarks and smoke tests | jurisdiction/practice/security/chaos suites | coverage classification and gates | high | P1 | golden fixtures first |
| UX | static intake + Astro scaffold/design docs | authenticated decision queue and evidence/review rooms | control-plane UX incomplete | medium | P2 | build after P0/P1 |
| Deployment | local + Workers targets | SaaS, single-tenant, VPC, on-prem, air-gapped | provider abstraction and packaging gap | medium | P2 | interface-first |

Priority: P0 = authority and safety foundation; P1 = governed execution;
P2 = product surface and deployment expansion.
