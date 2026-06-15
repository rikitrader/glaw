# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, use GitHub's
private **[Report a vulnerability](https://github.com/rikitrader/glaw/security/advisories/new)**
(Security → Advisories) to disclose privately. We aim to acknowledge within a few days.

## No secrets, no personal data — enforced

GLAW ships **no** API keys, credentials, or personal data, and the build enforces it:

- **Core needs no secrets.** Matters, the pipeline, drafting, and structured-format
  bookkeeping run locally with nothing configured. Optional Google Sheets reads use a
  local `gcloud` OAuth bearer token when requested — never a repo-stored credential file.
- **Git-ignored by default:** `.env`, `*.key`, `*.pem`, `*.enc`, and token JSON.
- **Content-level guard:** `bin/glaw-doctor` step `[6/6]` scans the tree and **fails CI**
  if it finds (a) a live key/token format, (b) a credential file, or (c) real client
  case data. A PR that reintroduces any of these cannot pass the GLAW Doctor check.

If you handle real matters with GLAW, keep client data **out of the repo** — work under
`~/.glaw/matters/<slug>/` (git-ignored state), never inside the skill tree.

## Scope

GLAW produces **attorney work-product drafts** for a licensed attorney to review and
sign. It does not practice law and is not a substitute for counsel. See
[the disclaimer in the README](README.md#%EF%B8%8F-not-legal-advice-read-this).
