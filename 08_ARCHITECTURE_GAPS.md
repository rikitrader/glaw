# Architecture Gaps

| Capability | Status | Evidence | Recommendation |
|---|---|---|---|
| Astro application shell | MISSING | No Astro files/config | ADD, preserving Worker deployment boundary |
| Interactive architecture graph | MISSING | No graph library or canvas | ADD as React island in Astro |
| Canonical graph registry | PARTIAL | Existing firm roster, schemas, docs; no graph model | ADD registry and validator |
| Workflow state model | PRESENT | `bin/glaw`, timeline, gates | KEEP; adapt through read-only adapters |
| Agent registry | PRESENT/PARTIAL | roster + 233 skills | KEEP source; normalize IDs/evidence |
| Prompt registry | UNKNOWN | Prompt-like content is distributed in Markdown | INVESTIGATE before consolidating |
| RAG provenance | PRESENT | `RAG.md`, provenance/retrieval modules | KEEP; add graph lineage |
| RAG permission filtering | UNKNOWN | Not evidenced in retrieval contract | INVESTIGATE; do not claim present |
| Architecture persistence | MISSING | No graph DB/table | ADD D1; R2 for large artifacts |
| Durable orchestration for scans | MISSING | No Workflows/Queue binding | ADD only when scan jobs need durability |
| Collaborative graph editing | UNKNOWN | No collaboration requirement/implementation | INVESTIGATE; Durable Object only if needed |
| Runtime telemetry | PARTIAL | X402 observability enabled; no unified execution schema | IMPROVE with normalized telemetry adapter |
| Environment graph | PARTIAL | Wrangler configs show local vars and bindings | IMPROVE with explicit env registry |
| Cloudflare resource discovery | PARTIAL | Two configs inspectable | IMPROVE scanner; account inventory remains unknown |
| Security overlay | PRESENT/PARTIAL | RBAC, conscience, bearer tokens, human gates | IMPROVE tenant/Access posture for explorer |

## Cloudflare service fit

| Requirement | Best Cloudflare service | Fit | Decision |
|---|---|---|---|
| Explorer API and adapters | Workers | Strong; existing platform | USE |
| Relational graph metadata | D1 | Strong for normalized current/proposed graph | USE |
| Large evidence and exports | R2 | Strong; absent today | PROPOSE |
| Async repository scans | Queues | Strong for decoupling and retries | PROPOSE when scan volume justifies |
| Durable multi-step scan/rebuild | Workflows | Strong for long-running stages | PROPOSE after MVP |
| Collaboration/locks | Durable Objects | Strong but unnecessary for read-only MVP | CONDITIONAL |
| Hot config/cache | KV | Existing, appropriate for read-heavy data only | KEEP for intake/config; do not use for graph transactions |
| Vector retrieval | Vectorize | Potential fit, but current RAG is source-locked lexical/citation graph | INVESTIGATE, not automatic |
| Model execution | Workers AI | Potential fit; capability/economics unverified | INVESTIGATE |
| Provider governance/observability | AI Gateway | Good target boundary if external models remain | PROPOSE after telemetry requirements |
| Internal explorer access | Access/Zero Trust | Appropriate for architecture control plane | PROPOSE for privileged surface |

