# GLAW Architecture Inventory

Date: 2026-08-23  
Scope: `/Users/ricardoprieto/projects/glaw-oss`  
Method: repository files, executable configuration, tests, and safe doctor output. No runtime telemetry or external account inspection was used.

## Executive finding

GLAW is a self-contained legal-work-product and agent-skill system. Its current core is zero-dependency local Bash/Python execution with filesystem matter state. It has two Cloudflare Worker surfaces: `glaw-intake` (Assets + KV) and `glaw-x402` (D1 + daily cron + observability). It is not currently an Astro application and contains no React/XYFlow implementation.

All claims in the registry are classified as `confirmed`, `inferred`, `proposed`, or `unknown`. The Astro + Cloudflare-first requirements are treated as mandatory target constraints, not as current-state facts.

## Repository structure and runtime

| Area | Current evidence | Status |
|---|---|---|
| Agent skills | 233 `SKILL.md` files; 116 under `seats/` | CONFIRMED |
| CLI layer | 179 executable files under `bin/` | CONFIRMED |
| Runtime | Bash + Python standard library; source-first local execution | CONFIRMED |
| Matter state | `$GLAW_HOME/matters/<slug>` with Markdown, JSON, JSONL, and workpapers | CONFIRMED |
| Frontend | Static HTML/CSS assets served through `glaw-intake` Worker Assets | CONFIRMED |
| Astro | No Astro config, package, route, or component found | CONFIRMED ABSENT |
| React/XYFlow | No dependency or implementation found | CONFIRMED ABSENT |
| JavaScript package runtime | `x402/` has a Node/Workers package; no package exists for the core app | CONFIRMED |

## Major systems

1. GLAW Managing Partner and matter pipeline.
2. Specialist skill and seat registry, routed through `lib/firm-roster.md`.
3. Fail-closed gate and compliance machinery.
4. Source-locked Legal Governor and local RAG workpapers.
5. Local provider adapters for Claude CLI and Codex CLI.
6. Host, MCP, Extism, RBAC, and conscience integration adapters.
7. Cloudflare public intake Worker.
8. Cloudflare X402 paid-agent Worker and D1 catalog/charge service.
9. Accounting, finance, actuarial, litigation, investigations, intelligence, regulatory, and private-client practice modules.

## APIs and external surfaces

Confirmed Worker endpoints are recorded in `architecture/registry/apis.json`. The public intake POST is unauthenticated by design; administrative intake reads use `INTAKE_ADMIN_TOKEN`. Legal Governor routes use a single token or tenant-token map. X402 exposes REST and stateless MCP JSON-RPC surfaces. Court and provider integrations are adapters/handoffs and do not autonomously file, sign, transmit, or bind.

## Data systems

- Local matter workpapers are the current authoritative persistence boundary.
- `INTAKE_KV` stores intake records and legal workflow/audit records using explicit key prefixes.
- `glaw-x402` D1 stores paid-agent/catalog state; the repository config still has a placeholder database ID.
- The repository contains JSON schemas for financial, registry, source-ledger, lane-workpaper, and pipeline artifacts.
- No current relational schema owns the architecture graph itself.

## AI, agents, and RAG

- The Managing Partner routes to specialist skills and vendored seats.
- Claude and Codex are local subscription CLI adapters; provider availability is explicit and fail-closed.
- Source-locked RAG hashes raw source metadata and supports lexical/citation-graph retrieval.
- Semantic embeddings/vector storage are explicitly unavailable unless configured.
- No canonical prompt registry, model registry, execution telemetry store, or vector database binding was found.

## Infrastructure inventory

| Resource | Current state |
|---|---|
| Workers | `glaw-intake`, `glaw-x402` confirmed |
| Assets | `glaw-intake` static assets binding confirmed |
| KV | `INTAKE_KV` confirmed |
| D1 | `glaw-x402` binding `DB` confirmed; ID placeholder |
| Cron | `0 5 * * *` on `glaw-x402` confirmed |
| Durable Objects | no application binding found; UNKNOWN |
| Workflows | no application binding found; UNKNOWN |
| Queues | no application binding found; UNKNOWN |
| R2 | no application binding found; UNKNOWN |
| Vectorize | no application binding found; UNKNOWN |
| Workers AI | no application binding found; UNKNOWN |
| AI Gateway | no application binding found; UNKNOWN |
| Access / Zero Trust | no repository configuration found; UNKNOWN |

## Validation evidence

`GLAW_DOCTOR_CORE=1 bash bin/glaw-doctor` completed its core checks, reporting 233 source skills, 224 deployed `/glaw-*` commands, parity across Claude/Codex mirrors, and safe smoke checks. Some smoke commands intentionally exit non-zero when invoked without required matter inputs; that is not evidence of a production failure.

## Missing information

- Cloudflare account/resource inventory for non-repository resources.
- Production/staging binding differences and deployment history.
- Runtime execution traces, cost, latency, retries, and error rates.
- Actual active matters and their current workpaper graph.
- Whether semantic RAG providers exist outside this checkout.
- Ownership metadata for domains, skills, tools, data, and deployments.
- Product requirements for the architecture explorer's authenticated audience and edit permissions.
