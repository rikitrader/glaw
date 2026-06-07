# Vendored seats — GLAW's self-contained skill ecosystem

GLAW is a **self-contained repo with no external skill dependencies**. Every skill
and agent it routes to is vendored here under `seats/<name>/`. `bin/glaw-setup`
deploys them as top-level skills (non-destructively — an already-installed copy
always wins), and `bin/glaw-doctor` enforces self-containment: every skill the
roster routes to must resolve to a vendored seat (or a GLAW sub-skill), else it
fails. There is no "optional/external" tier.

Sanitized on vendoring: nested `.git/`, `.encrypted/`, `*.enc`, `*.key`, `*.pem`,
`.env`, `.venv/`, `__pycache__/`, `node_modules/` are excluded. Third-party
LICENSE/NOTICE files are preserved in-place.

Categories (see each seat's SKILL.md for detail):
- **GLAW-family sub-skills** — `glaw-83b-election`, `glaw-asset-protection`,
  `glaw-chief-counsel`, `glaw-consensus`, `glaw-credit-strategy`, `glaw-forms`,
  `glaw-reasoningbank`, `glaw-valuation-409a`, `glaw-valuation-adversary`.
- **Legal / tax / corporate** — `corporate-counsel`, `elite-corporate-counsel`,
  `pe-vc-counsel`, `fund-regulatory-council`, `tokenization-compliance`,
  `tax-strategy`, `tax-compliance`, `tax-relief`, `tax-legal-intake`,
  `federal-trial-counsel`, `forensic-case-investigator`, `sec-enforcement-swarm`,
  `contract-review` (third-party, own LICENSE).
- **Accounting / finance** — `institutional-finance`, `financial-forensics`,
  `roofer-accounting`, `mc-cfo-agent`, `company-valuation`, and the `fs-*` model
  suite (3-statement, DCF, LBO, merger, comps, KYC, GL-recon, NAV tie-out, etc.).
- **Document / output** — `make-pdf`, `document-generate`, `pdf`, `pitch-deck`,
  `docx`, `copywriting`, `copy-editing`.
- **Research / SEO** — `seo-content`, `seo-geo`.

`seats/.nonseat-tokens` lists backticked roster tokens that are NOT vendorable
skills (e.g. harness-only `deep-research`); the self-containment gate skips them.
