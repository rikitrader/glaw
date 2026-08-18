# Legal Governor Provider Execution

The project defaults to subscription-backed local CLI execution:

```text
Alexandra Vale → Claude Code → subscription_cli
Victor Sterling → Codex CLI   → subscription_cli
```

API execution is a separate explicit mode. `subscription_cli` removes the
corresponding API-key variable from the subprocess environment and never
falls back to the API adapter. `ALLOW_API_FAILOVER` is recorded but is not
enabled by default; an unavailable primary therefore remains unavailable.

## Verified CLI interfaces

The installed versions inspected on 2026-08-18 were:

```text
Claude Code 2.1.220
Codex CLI 0.139.0
```

Claude invocation:

```text
claude --print --output-format json --no-session-persistence --tools "" --permission-mode plan
```

Codex invocation:

```text
codex exec --json --ephemeral --skip-git-repo-check --ignore-user-config --ignore-rules --sandbox read-only --output-schema FILE --output-last-message FILE
```

Both are passed as argument arrays through `subprocess.run`; no shell is used.

## Commands

```bash
bin/glaw-providers status
bin/glaw-providers check claude
bin/glaw-providers check codex
bin/glaw-providers smoke codex
```

`status` checks executable/version and local authentication state. `smoke`
performs one minimal model invocation and is the stronger execution check.

The Cloudflare Worker cannot inspect a developer machine's local subscription
session. Local provider status must be collected by the trusted Python runtime;
the Worker must not display local status as live unless that status is sent by
an authenticated backend.
