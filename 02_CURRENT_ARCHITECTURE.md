# Current Architecture

## System shape

```text
User / host
  -> local GLAW CLI, host adapter, or MCP adapter
  -> matter state under GLAW_HOME
  -> stage skills and bin tools
  -> evidence, gates, workpapers, human review

Public browser
  -> glaw-intake Cloudflare Worker
  -> Assets + INTAKE_KV

Paid-agent client
  -> glaw-x402 Cloudflare Worker
  -> D1 catalog/charges + X402 facilitator when configured
  -> paid-work authorization / execution boundary
```

## Confirmed workflow spine

`intake -> strategy -> structure -> draft -> adversarial -> file -> docket -> matter-retro`.

The gates are not merely visual labels: `bin/glaw-gate` and owning commands block guarded transitions. The graph explorer must model these as governance edges and evidence-backed states, not as executable graph nodes.

## Current vs target boundary

The current system has no architecture graph controller or visual editor. The target must add an Astro shell and selective React islands while preserving the current local CLI and Worker boundaries. The graph model, validator, workflow definition, and execution adapters must remain separate.

## Trust boundaries

- Public intake is a public submission boundary.
- Administrative intake reads require a Worker secret.
- Legal API routes require bearer token tenant resolution.
- Provider adapters cannot create legal PASS decisions.
- Human counsel review is required before reliance on consequential conclusions.
- Host/MCP execution is argv-only and guarded by RBAC and conscience checks.
