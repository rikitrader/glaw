# Changelog

## Unreleased — Tax & IRS coverage: 5 new seats + doctor green

Closes five IRS/tax gaps from a coverage review. Each is a new firm-authored native seat
(deployed `/glaw-*` via `glaw-setup`, routed from `lib/firm-roster.md`):

- **`/glaw-exempt-org`** — nonprofit/foundation tax: §501(c) posture + 1023/1024 recognition,
  990 family gating + 990-T UBIT + §509(a) public-support test (`bin/glaw-form990`),
  inurement/self-dealing/excise screen. (Preparer counterpart to the `bin/glaw-exempt-org`
  ProPublica diligence tool.)
- **`/glaw-international-tax`** — COMPUTE counterpart to flag-only `/glaw-international`: reuses
  the GILTI/Subpart F/FDII/BEAT/§163(j)/5471-5472 engines and adds the foreign-asset reporting
  layer — FBAR + Form 8938 thresholds + §962 election (`bin/glaw-fbar-8938`), 8865/8858, and
  the streamlined / voluntary-disclosure path.
- **`/glaw-tax-court`** — the U.S. Tax Court forum `/glaw-irs-audit` only drafts a petition for:
  90-day jurisdictional clock, §7463 small-case (S) election, IRS Counsel / Branerton settlement
  + docketed Appeals, trial.
- **`/glaw-estate-gift-returns`** — Form 706 (`bin/glaw-form706`) + Form 709 (`bin/glaw-form709`)
  on the §2001(c) schedule, portability/DSUE + GST elections; the preparer counterpart to
  flag-only `/glaw-estate-trusts`.
- **`/glaw-irs-whistleblower`** — IRC §7623 Form 211 eligibility/originality screen +
  collected-proceeds award-range model (`bin/glaw-wbo-award`); the IRS analog to
  `/glaw-sec-whistleblower`.

Shared IRS-PDF AcroForm filler promoted to `bin/glaw-fill-form` + `bin/glaw-inspect-fields`
(single source of truth = credit-strategy filler, run under the bookkeeping venv/pypdf), wired
into the four filing seats via per-seat `forms/`.

**Doctor green (two pre-existing failures fixed):**
- `glaw-cites` ran as a bare `python3` script while `eyecite` was uninstalled → installed eyecite
  into the bookkeeping venv and converted to the firm's bin-wrapper idiom (`lib/bookkeeping/cites.py`).
- `glaw-test` imposed the firm's internal frontmatter/UPL contract on **vendored third-party
  seats** (62 false `name 'glaw-X' != 'glaw-glaw-X'` + frontmatter violations). Scoped the
  contract test to firm-authored skills (its documented purpose); seat resolution stays covered by
  deploy parity + the MANIFEST bijection. Name rule is now glaw-prefix-aware. → **100/100 pass,
  `glaw-doctor` HEALTHY**.

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
