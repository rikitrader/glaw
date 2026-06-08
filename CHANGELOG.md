# Changelog

## 1.1.0 — self-contained ecosystem

- **Self-contained: zero external skill dependencies.** Every specialist seat the firm
  routes to is now **vendored under [`seats/`](seats/)** — **62 seats** (`glaw-*`),
  discovered by transitive closure over the roster + all SKILL.md to a fixpoint. With the
  **65 native sub-skills** that's **127 deployed `/glaw-*` commands**. `./setup` deploys
  the seats non-destructively (an already-installed copy always wins).
- **GLAW rebrand.** All vendored seats and the bookkeeping engine carry the GLAW name
  (`bankstatementparser` → `glaw_engine`); every routing reference rewritten to `glaw-*`.
- **Bookkeeping engine** (`glaw-bank-ingest` + bundled `glaw_engine`): bank/card statements
  (CSV·OFX·QFX·MT940·CAMT·PAIN·**PDF**) → deduped, **balance-verified** ledger →
  hledger / beancount / **Google Sheet**. Scanned PDFs via Tesseract OCR; **$0**, no LLM
  for structured formats. `./setup` builds its venv automatically.
- **Deterministic no-gaps gate.** `glaw-doctor` now enforces a **MANIFEST bijection** +
  full `glaw-*` reference resolution (every routed skill resolves, 0 ignored tokens).
- **Secrets & PII guard.** `glaw-doctor [6/6]` fails the build on any live key, credential
  file, or real client data — and the `doctor` check is **required** on `main`. GLAW ships
  no secrets and no personal data. Added [`SECURITY.md`](SECURITY.md), [`.env.example`](.env.example),
  and [`ATTRIBUTIONS.md`](ATTRIBUTIONS.md) (Apache-2.0 engine + MIT seats credited).

## 1.0.0 — first open-source release

- **59 skills** across **10 departments** (Corporate, Securities/Funds, Tax/IRS,
  Accounting, Litigation, Investigations Bureau, Intelligence Super-Structure,
  Regulatory/Licensing, Private Client, Firm Management).
- **8-stage matter pipeline** (intake → strategy → structure → draft → adversarial →
  file → docket → close) with three tracks (litigation / corp-build / investigation).
- **Four hard gates**: conflicts cleared, citations verified, adversarial RED→BLUE,
  UPL disclaimer.
- **20-tool toolbelt**, including the contract-review chain: `glaw-contract-score`
  (scorecard), `glaw-redline` / `glaw-redline-docx` (real Word tracked changes),
  `glaw-review-chain` (one-shot), `glaw-publish` (PDF/Doc/Slides).
- **`glaw-doctor`** health harness — asserts all skills resolve, all tools run, no
  dangling references.
- Interoperates with `legal-redline-tools` and `claude-legal-skill` (both MIT).
