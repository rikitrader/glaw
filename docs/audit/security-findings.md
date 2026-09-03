# Security Findings

| ID | Severity | Finding | Evidence / impact | Required control |
|---|---|---|---|---|
| SEC-001 | critical | Public intake boundary is separate from authenticated control plane | `app/` is public; matters/evidence must not be exposed through it | identity, tenant resolution, matter authorization before every read |
| SEC-002 | high | Tenant and ethical-wall enforcement is not proven at retrieval boundary | local token comments and gate docs exist; end-to-end negative tests are not evidenced | authorization graph plus retrieval isolation tests |
| SEC-003 | high | KV is used for intake/legal workflow state | `app/src/worker.js`, `app/wrangler.toml` | migrate authoritative relational state behind an adapter |
| SEC-004 | high | External connector and side-effect receipt semantics are not unified | connectors are adapters/handoffs; no universal receipt contract found | command envelope, idempotency, lookup, reconciliation |
| SEC-005 | high | Secrets/provider boundary is distributed | `.env.example` documents optional providers; runtime inventory is fragmented | model gateway and capability-scoped server-side tools |
| SEC-006 | medium | Audit integrity differs by subsystem | local append-only workpapers and X402 observability exist, but no unified chain | tamper-evident audit event contract and signed exports |
| SEC-007 | medium | Supply-chain signing for skills is not evidenced | skills are Markdown/CLI capabilities | signed, hashed, benchmarked, sandboxed skill packages |
| SEC-008 | medium | Prompt/tool injection controls are documented but require runtime proof | retrieved content and tool outputs cross trust boundaries | structured isolation plus adversarial tests |

No live secret was intentionally read or exposed during this audit.
