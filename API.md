# Legal Governor API boundary

The Cloudflare Worker exposes public intake and an authenticated, source-backed
legal workflow ledger. The legal routes persist workflow evidence and audit
events in the configured KV namespace; they do not execute providers, verify
law autonomously, or authorize filing, signature, payment, or other binding
acts. The supported service boundary is:

```text
POST /legal/analyze      -> create a source-backed matter request
POST /legal/research     -> record retrieval evidence
POST /legal/verify       -> record a verification bundle and verifier
POST /legal/red-team     -> record adverse/red-team work
GET  /legal/requests/:id/governor -> return workflow and gate status
POST /legal/review/:id   -> append named human counsel review
```

Every legal route requires `Authorization: Bearer $LEGAL_API_TOKEN`. For
multi-tenant deployments, prefer the encrypted `LEGAL_TENANT_TOKENS` JSON
secret (`{"tenant-id":"token"}`); each request and audit event is bound to the
tenant resolved from the token. Configure the secret in the Worker environment
before use. Provider execution remains
local and command-driven through `bin/glaw-legal-governor`; remote route calls
only record evidence supplied by an authenticated operator. Human approval is
required before reliance on any conclusion.
