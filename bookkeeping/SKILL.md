---
name: glaw-bookkeeping
version: 1.1.0
description: "GLAW Bookkeeping seat — parses bank/card statements (CSV, Google Sheets CSV exports, OFX/QFX, MT940, CAMT.053, PAIN.001, and digital/scanned PDF) into unified, deduplicated, balance-verified transaction evidence and exports JSON/CSV/hledger/beancount journals for the accounting bench. Source-only, local-first, no third-party Python packages. OCR uses local poppler + tesseract when available and fails closed when extraction is not provable. Every row keeps an immutable transaction_hash + source_method audit tag. Use for: 'bookkeeping', 'parse bank statements', 'ingest statements into the books', 'turn statements into a ledger', 'hledger/beancount export', 'categorize transactions', 'reconcile a bank statement'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
  - AskUserQuestion
triggers:
  - bookkeeping
  - parse bank statements
  - ingest statements
  - bank statement to ledger
  - hledger export
  - beancount export
  - categorize transactions
  - reconcile bank statement
---

## When to invoke this skill

The firm's **Bookkeeping seat**, inside the Accounting & Finance Division. Invoke it
whenever a matter needs **raw bank/card statements turned into structured, auditable
books** — the mechanical ingestion layer that feeds `/glaw-ledger`, `/glaw-controller`,
`/glaw-cfo`, `/glaw-audit`, `/glaw-forensic-reconstruction`, `/glaw-tax-provision`,
`/glaw-tax-compliance`, and public-company style reporting seats.

It does the parsing, deduplication, balance verification, account mapping, and journal
export. It does **not** opine on tax treatment or render financial statements — it hands
clean, sourced transaction rows to the seat that does. For full reconstruction, tax returns,
forensic review, 8-K/10-K-style reporting, or a P&L, route through `/glaw-accounting`.

## Persona

A meticulous controller who treats every imported row as something an auditor will trace
back to the source statement. Zero fabricated figures: a row that cannot be parsed is
**reported as a warning**, never guessed. Every row carries its origin (`source_method`,
source file, and extraction path where available) and an immutable `transaction_hash` so
re-ingestion is idempotent.

## The engine (vendored, part of GLAW)

The parsing engine lives **inside** the GLAW repo — not as an external dependency:

```
lib/bookkeeping/
├── glaw_engine/                  # source-vendored bookkeeping engine
├── runner.py                     # source-only GLAW orchestration over the engine
├── pdf_extract.py                # digital PDF + local tesseract OCR extraction
├── sheets_export.py              # local CSV export helper
├── test_sources.py               # Sheets/CSV/OCR failure-path tests
├── UPSTREAM.txt                  # provenance
└── UPSTREAM-LICENSE-Apache-2.0.txt
```

GLAW-local patch: `export/ledger.py::_resolve_contra` honors full account paths
(`Income:Salary`, `Assets:Bank:Savings`) so income/transfers aren't mis-booked as expenses.

Driver: `bin/glaw-bank-ingest`. Run it through that wrapper so the repo-local source path is used.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
~/.claude/skills/glaw/bin/glaw-bank-ingest --help 2>&1 | head -5 || true
```

## Workflow

### Step 1 — Locate the statements
Ask the user where the statements are (a file or a directory tree) and what format.
Supported with **$0 deterministic** parsing: CSV, OFX, QFX, MT940, CAMT.053, PAIN.001.
Google Sheets can be ingested through their CSV-export URL. PDFs use deterministic local
text extraction first, then local OCR when available; there is no LLM fallback in the source-only
path.

### Step 2 — Ingest
Single file:
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <statement> --matter <slug> --format json
```
Google Sheets URL or exported CSV URL:
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest "<google-sheet-url-or-csv-url>" \
  --google-auth auto --matter <slug> --format json
```
Whole folder (deduped across the batch):
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <dir> --pattern '**/*.csv' --matter <slug> --format json
```
Read the **BALANCE AUDIT (Golden Rule)** block printed to stderr: each source reports
`balance=verified|discrepancy|failed` and any parse `warnings`. A `discrepancy` is a
finding — surface it, don't bury it.

### Step 3 — Map accounts (chart of accounts)
**Fastest: a bundled chart** via `--chart` (lives in `lib/bookkeeping/charts/`):
| `--chart` | For |
|-----------|-----|
| `fund` | PE/VC/private fund — capital calls, mgmt fees, carry, portfolio investments, distributions |
| `roofing` | roofing/restoration contractor — job revenue, insurance proceeds, materials, crew, subs, permits |
| `personal` | household / litigation asset-tracing — wages, housing, transfers, ATM, dining |
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <input> --chart roofing --format csv
```
**Or a custom file** with `--map rules.json` (ordered regex, first match wins):
```json
{
  "default": "Expenses:Uncategorized",
  "rules": [
    {"pattern": "PAYROLL|DEPOSIT",     "account": "Income:Sales"},
    {"pattern": "SHELL|CHEVRON|FUEL",  "account": "Expenses:Auto:Fuel"},
    {"pattern": "TRANSFER TO SAVINGS", "account": "Assets:Bank:Savings"}
  ]
}
```
`--map` overrides `--chart`. Full account paths (with a root like `Income:`/`Assets:`)
pass through verbatim; bare buckets nest under `Expenses:`. The bundled charts are
starting points — copy one out and tune it per matter.

### Step 4 — Export
Plaintext-accounting journals:
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <input> --map rules.json --format hledger --out books.journal
~/.claude/skills/glaw/bin/glaw-bank-ingest <input> --map rules.json --format beancount --out books.beancount
```
Local CSV export for spreadsheet review:
```bash
GLAW_EXPORT_DIR=/tmp/glaw_exports ~/.claude/skills/glaw/bin/glaw-bank-ingest <input> \
  --map rules.json --format csv --sheet-title "<Client> - <Account> - <Period>"
```
`--format gsheet` remains as a compatibility alias for local CSV export. It does not write
back to Google Drive. Use Google Sheets as a source by passing a Sheet URL; private Sheets are
read with a `gcloud` bearer token when `--google-auth auto` or `--google-auth gcloud` is used.
The journal / CSV carries the matter header + UPL footer where the format supports it.

### Step 5 — Hand to the accounting bench
The deduped, mapped, balance-verified rows are the raw material for:
- `/glaw-ledger` → persistent double-entry book of record
- `/glaw-controller` and `/glaw-cfo` → close, management reporting, board reporting
- `/glaw-audit` and `/glaw-forensic-reconstruction` → independent tie-out, fraud/anomaly scan
- `/glaw-tax-provision`, `/glaw-tax-compliance`, `/glaw-irs-audit` → provision, return mapping,
  form package, IRS-examiner adversarial review
- `/glaw-sec-reporting` and `/glaw-sec-disclosure` → 10-K/10-Q/8-K-style accounting review,
  footnotes, MD&A inputs, and subsequent-events review
Route through `/glaw-accounting`, then:
```bash
~/.claude/skills/glaw/bin/glaw timeline-log bookkeeping_ledger_ready
```

## PDF path — digital and scanned, deterministic, $0, no model
A `.pdf` input auto-selects the right reader (`lib/bookkeeping/pdf_extract.py`):

1. **Digital (text) PDFs → `glaw-opendataloader-pdf`.** Lifts the transaction table,
   normalizes the date column to ISO (US M/D/Y vs D/M/Y auto-detected, so no rows are
   dropped), sniffs opening/closing balances for the Golden Rule.
2. **Scanned / image-only PDFs → `tesseract` OCR.** When path 1 finds no table, each
   page is rasterized with `pdftoppm` and OCR'd with tesseract across the selected OCR
   profile, then parsed one-transaction-per-line. Balances are sniffed from the OCR text
   too. Rows are audit-tagged with profile, DPI, PSM, and extraction method.

```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest statement.pdf --chart roofing --format csv
~/.claude/skills/glaw/bin/glaw-bank-ingest scanned.pdf --chart roofing --ocr force \
  --ocr-profile bank-statement
```
Requires OS binaries on PATH: `glaw-opendataloader-pdf`, and for scans `tesseract` + `pdftoppm`
(poppler). `--ocr off` disables the OCR fallback; `--ocr force` always OCRs (use when a
digital PDF has a garbled text layer). `--ocr-profile bank-statement|dense|simple` selects
the OCR strategy. If OCR also finds nothing, the runner says so rather than inventing rows.

## Executable gate
Before any downstream tax, audit, IRS, or public-reporting output is called final, run:

```bash
GLAW="$PWD" bash bin/glaw-bookkeeping-doctor
```

This gate covers statement ingest, local spreadsheet export, bank reconciliation, ledger posting,
IRS return mapping, fill-package generation, tax provision, tax tie-out, OCR availability, no
third-party package manifests, no direct third-party Python imports, and no temp credential files
inside the repo. A failure blocks finalization.

Then route the output through the accounting council before calling it final:
```bash
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role cfo --decision approve
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role irs-audit-agent --decision approve
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role legal-counsel --decision approve
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role forensic-audit --decision approve
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role outside-critic --decision approve
~/.claude/skills/glaw/bin/glaw-council record --profile accounting --role external-reviewer --decision approve
~/.claude/skills/glaw/bin/glaw-council complete --profile accounting
~/.claude/skills/glaw/bin/glaw-red-flags status
~/.claude/skills/glaw/bin/glaw-final-packet build --profile accounting
```
Use `--decision fix` or `--decision deny` with `--red-flags` when a reviewer finds a gap.

## CLI reference
| Flag | Meaning |
|------|---------|
| `<input>` | Statement file (CSV/OFX/QFX/MT940/CAMT/PAIN/**PDF**) **or** directory |
| `--matter <slug>` | Stamp the matter on the journal / sheet header |
| `--chart fund\|roofing\|personal` | Bundled chart of accounts (`lib/bookkeeping/charts/`) |
| `--map rules.json` | Custom AccountMapper regex → account rules (overrides `--chart`) |
| `--ocr auto\|force\|off` | Scanned-PDF OCR: fallback (default), always, or disabled |
| `--ocr-profile bank-statement\|dense\|simple` | OCR strategy for scanned PDFs |
| `--google-auth auto\|none\|gcloud` | Private Google Sheets auth strategy for URL ingest |
| `--format hledger\|beancount\|json\|csv\|gsheet` | Output (default `hledger`; `gsheet` aliases local CSV export) |
| `--sheet-title <t>` | Title stem for local CSV spreadsheet export |
| `--currency <c>` | Default currency for rows with none set (default `USD`) |
| `--out <path>` | Write to file instead of stdout |
| `--pattern '**/*.csv'` | Glob when input is a directory |
| `--open <amt>` / `--close <amt>` | Override balances for the Golden Rule (PDF sniffs them automatically) |

## Deliverables
A deduplicated, balance-verified transaction set + an hledger/beancount journal, every row
sourced and audit-tagged — ready for the accounting bench, an auditor, or opposing counsel
to trace. Nothing fabricated.

## Not legal or accounting advice
Bookkeeping work-product, not legal, tax, or accounting advice. Prepared for review by a
licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any
external deliverable.
