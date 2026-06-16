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
bin/glaw --headless --goal "summarize open gates for orchestrator" --json
```

## Host Mapping

For zeroclaw-x0, map `manifest.tools[]` to host tool metadata and call `execute` with
the selected tool and argv array. The host should treat any `status` other than `pass`
as fail-closed.

For MCP, use `bin/glaw-mcp`. It exposes exactly three tools:

- `glaw_manifest`
- `glaw_status`
- `glaw_execute`

`glaw-mcp serve` reads one JSON-RPC object per line from stdin and writes one response per
line to stdout. It handles `initialize`, `tools/list`, `tools/call`, and `ping`. It never
exposes a raw shell command; `glaw_execute` delegates to `glaw-host`, so the same argv-only,
conscience-guarded, RBAC-preserving contract applies.

```bash
bin/glaw-mcp tools --json
bin/glaw-mcp call glaw_execute --arguments '{"tool":"glaw","args":["version"]}' --json
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | bin/glaw-mcp serve
```

GLAW prepares work product. It does not autonomously file, serve, sign, transmit, pay,
charge, or bind anyone.

## Extism / zeroclaw

`bin/glaw-extism` is the source-only Extism contract shim. It exports the two host-facing
operations zeroclaw expects:

- `tool_metadata`
- `execute`

The local shim does not download or load an Extism runtime. It produces the deterministic
metadata and execute payload shape a Rust/WASM wrapper can expose, and all execution still
delegates to `glaw-host`.

```bash
bin/glaw-extism tool_metadata --json
bin/glaw-extism execute --payload '{"tool":"glaw","args":["version"]}' --json
```

The metadata declares host permissions explicitly: raw shell denied, hardware denied, network
controlled by the host runtime, filesystem limited to the repo and `$GLAW_HOME`, and human-seal
acts limited to a named lawful human actor with RBAC `ADMIN`.

## Headless Orchestrator Report

OpenClaw, ZeroClaw, and spawned agents can call:

```bash
bin/glaw --headless --goal "<objective>" --json
```

The report is read-only. It returns the active matter, workflow track, current stage, `glaw-loop`
decision, open gate list, next owner, next command, recent Chief decisions, shipped artifacts,
compliance/government-adversary manifests, accounting-control failures for bank reconciliation or
tax tie-out routing, and the human-seal authority boundary. A blocked report is useful signal: it
tells the host exactly which GLAW department/gate owns the next fix.
