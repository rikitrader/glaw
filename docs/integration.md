# GLAW Host Integration

GLAW embeds into autonomous hosts through `bin/glaw-host`. The adapter is source-only:
no package server, no shell eval, no background daemon, and no authority expansion.

## Contract

- Discover tools with `bin/glaw-host manifest --json`.
- Execute tools with `bin/glaw-host execute --tool <glaw-tool> --args '<json-array>' --json`.
- Pass arguments as a JSON array of strings. Shell strings are rejected.
- Tool names must be executable `bin/glaw*` files in this repo. Paths and traversal are rejected.
- Every execution runs `glaw-conscience check-call` before the tool and
  `glaw-conscience check-response` after the tool.
- Human-seal acts still require a named human actor plus RBAC `ADMIN`.

## Examples

```bash
bin/glaw-host manifest --json
bin/glaw-host execute --tool glaw --args '["version"]' --json
bin/glaw-host execute --tool glaw-loop --args '["status","--json"]' --matter "$SLUG" --json
```

## Host Mapping

For zeroclaw-x0, map `manifest.tools[]` to host tool metadata and call `execute` with
the selected tool and argv array. The host should treat any `status` other than `pass`
as fail-closed.

For MCP, expose `manifest`, `status`, and `execute` as three tools. Do not expose a raw
shell command. The adapter already returns the pre-call and post-response guard evidence
that a host can store in its own audit ledger.

GLAW prepares work product. It does not autonomously file, serve, sign, transmit, pay,
charge, or bind anyone.
