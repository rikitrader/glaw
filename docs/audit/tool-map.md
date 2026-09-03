# Tool Map

## Current tool families

- Matter lifecycle and gate commands under `bin/`.
- Document extraction, assembly, publishing, redlining, and citation tools.
- Court/research, tax, accounting, regulatory, investigation, and finance tools.
- Host, MCP, Extism, provider, sandbox, oversight, and X402 interfaces.

## Required target metadata

Each tool needs version, JSON input/output schemas, permission list, risk class,
side-effect class, timeout, idempotency support, reconciliation support, and
telemetry identity. No agent should inherit a generic omnipotent credential.

## Primary finding

The repository has breadth of tools but needs a single capability registry and
execution adapter so the same permission and receipt semantics apply everywhere.
