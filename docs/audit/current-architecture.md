# Current Architecture

## Runtime topology

```text
Local user/agent
  → Bash/Python CLI + filesystem matter state

Public user
  → glaw-intake Worker → static assets / INTAKE_KV

Paid-agent client
  → glaw-x402 Worker → D1 catalog/charges + REST/MCP

Architecture/control-plane user
  → Astro scaffold → Worker/Cloudflare bindings (verification pending)
```

## Confirmed strengths

- Matter pipeline and hard gates are already explicit.
- Legal Governor workpapers preserve source hashes and verification bundles.
- Specialist skills and tools are unusually broad.
- Provider availability is explicit and fail-closed.
- X402 and MCP provide a foundation for capability distribution.
- Existing registries and design rules anticipate graph/workflow separation.

## Confirmed gaps

- No single canonical runtime state store spans local matters, intake, X402, and
  the control-plane scaffold.
- Public intake uses KV for request/audit state.
- No authenticated control-plane route is evidenced in the public app.
- Registry artifacts are numerous and require one validated loading contract.
- Durable execution, immutable object storage, semantic retrieval, and unified
  model telemetry are target capabilities rather than confirmed runtime paths.
