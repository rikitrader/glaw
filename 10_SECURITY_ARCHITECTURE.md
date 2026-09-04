# Security Architecture

## Confirmed controls

- Public intake has a body-size limit and validates required fields.
- Administrative intake reads require `INTAKE_ADMIN_TOKEN`.
- Legal API routes require bearer token authentication and tenant resolution.
- Legal audit events are append-only KV records with request/tenant association.
- Provider adapters are not legal authority and cannot create PASS decisions.
- Human review is a hard boundary before reliance on conclusions.
- Host/MCP execution is argv-only, RBAC-aware, and wrapped by conscience checks.
- Repository docs prohibit committing secrets and keep provider credentials external.

## Risks and unknowns

1. Public intake has no repository-evidenced Turnstile or abuse control.
2. The proposed architecture explorer has no access policy yet.
3. Tenant isolation in the RAG retrieval stage is not evidenced.
4. `glaw-x402` D1 config contains a placeholder database ID; deployment readiness must be verified separately.
5. Cloudflare account-level Access, secret, and environment configuration are outside the repository evidence.
6. PII, financial, and legal-data classification is described in policy/docs but not normalized into the graph.

## Proposed overlay

Use Cloudflare Access/Zero Trust for the internal explorer, Worker-side authorization, D1 row ownership/tenant columns, R2 object policies, and explicit source/evidence classification. Add Turnstile to public intake only if abuse evidence or launch requirements justify it.
