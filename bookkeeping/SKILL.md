---
name: glaw-bookkeeping
version: 1.0.0
description: "GLAW Bookkeeping seat — parses bank/card statements (CSV, OFX/QFX, MT940, CAMT.053, PAIN.001, and PDF) into a unified, deduplicated, balance-verified ledger and exports plaintext-accounting journals (hledger / beancount) for the firm's accounting bench. Deterministic ISO/exchange parsers run first ($0, local); PDFs fall through to an opt-in LLM. Every row keeps an immutable transaction_hash + source_method audit tag. Use for: 'bookkeeping', 'parse bank statements', 'ingest statements into the books', 'turn statements into a ledger', 'hledger/beancount export', 'categorize transactions', 'reconcile a bank statement'."
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
books** — the mechanical ingestion layer that feeds `glaw-financial-forensics` (reconstruction),
`glaw-roofer-accounting` (job costing), and `glaw-institutional-finance` (modeling).

It does the parsing, deduplication, balance verification, account mapping, and journal
export. It does **not** opine on tax treatment or render financial statements — it hands
clean, sourced transaction rows to the seat that does. For full reconstruction or a P&L,
route to `glaw-financial-forensics` via `/glaw-accounting`.

## Persona

A meticulous controller who treats every imported row as something an auditor will trace
back to the source statement. Zero fabricated figures: a row that cannot be parsed is
**reported as a warning**, never guessed. Every row carries its origin (`source_method`:
deterministic / llm / vision) and an immutable `transaction_hash` so re-ingestion is
idempotent.

## The engine (vendored, part of GLAW)

The parsing engine lives **inside** the GLAW repo — not as an external dependency:

```
lib/bookkeeping/
├── glaw_engine/          # vendored Apache-2.0 engine (sebastienrousseau/glaw_engine)
├── .venv/                        # dedicated venv (pydantic, lxml, defusedxml, pandas, pypdf)
├── runner.py                     # GLAW orchestration over the engine
├── UPSTREAM.txt                  # pinned commit + provenance
└── UPSTREAM-LICENSE-Apache-2.0.txt
```

GLAW-local patch: `export/ledger.py::_resolve_contra` honors full account paths
(`Income:Salary`, `Assets:Bank:Savings`) so income/transfers aren't mis-booked as expenses.

Driver: `bin/glaw-bank-ingest`. Run it through that wrapper — it pins the venv + PYTHONPATH.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
~/.claude/skills/glaw/bin/glaw-bank-ingest --help 2>&1 | head -5 || true
```

## Workflow

### Step 1 — Locate the statements
Ask the user where the statements are (a file or a directory tree) and what format.
Supported with **$0 deterministic** parsing: CSV, OFX, QFX, MT940, CAMT.053, PAIN.001.
PDFs (digital or scanned) need the opt-in LLM path — see "PDF path" below.

### Step 2 — Ingest
Single file:
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <statement> --matter <slug> --format json
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
~/.claude/skills/glaw/bin/glaw-bank-ingest <input> --chart roofing --format gsheet
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
**Google Sheet** (categorized, two tabs — Transactions + per-category Summary):
```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest <input> --map rules.json --format gsheet \
  --sheet-title "<Client> — <Account> — <Period>"
```
The `gsheet` path uses the authorized-user creds at `~/.gcp/token.json` (scopes:
spreadsheets + drive) and prints the new sheet URL. The journal / sheet carries the
matter header + UPL footer.

### Step 5 — Hand to the accounting bench
The deduped, mapped, balance-verified rows are the raw material for:
- `glaw-financial-forensics` → reconstruct P&L / balance sheet / cash flow, fraud scan
- `glaw-roofer-accounting` → job/crew costing from the mapped expense rows
- `glaw-institutional-finance` → EBITDA normalization, modeling
Route through `/glaw-accounting`, then:
```bash
~/.claude/skills/glaw/bin/glaw timeline-log bookkeeping_ledger_ready
```

## PDF path — both digital and scanned, deterministic, $0, no model
A `.pdf` input auto-selects the right reader (`lib/bookkeeping/pdf_extract.py`):

1. **Digital (text) PDFs → `glaw-opendataloader-pdf`.** Lifts the transaction table,
   normalizes the date column to ISO (US M/D/Y vs D/M/Y auto-detected, so no rows are
   dropped), sniffs opening/closing balances for the Golden Rule.
2. **Scanned / image-only PDFs → `tesseract` OCR.** When path 1 finds no table, each
   page is rasterized with `pdftoppm` and OCR'd with tesseract (psm 4), then parsed
   one-transaction-per-line. Balances are sniffed from the OCR text too. Rows are
   audit-tagged `extracted via tesseract OCR`.

```bash
~/.claude/skills/glaw/bin/glaw-bank-ingest statement.pdf --chart roofing --format gsheet
~/.claude/skills/glaw/bin/glaw-bank-ingest scanned.pdf  --chart roofing --ocr force   # force OCR
```
Requires OS binaries on PATH: `glaw-opendataloader-pdf`, and for scans `tesseract` + `pdftoppm`
(poppler). `--ocr off` disables the OCR fallback; `--ocr force` always OCRs (use when a
digital PDF has a garbled text layer). If OCR also finds nothing (very low-quality scan
or a non-tabular layout), the runner says so rather than inventing rows.

## CLI reference
| Flag | Meaning |
|------|---------|
| `<input>` | Statement file (CSV/OFX/QFX/MT940/CAMT/PAIN/**PDF**) **or** directory |
| `--matter <slug>` | Stamp the matter on the journal / sheet header |
| `--chart fund\|roofing\|personal` | Bundled chart of accounts (`lib/bookkeeping/charts/`) |
| `--map rules.json` | Custom AccountMapper regex → account rules (overrides `--chart`) |
| `--ocr auto\|force\|off` | Scanned-PDF OCR: fallback (default), always, or disabled |
| `--format hledger\|beancount\|json\|gsheet` | Output (default `hledger`) |
| `--sheet-title <t>` | Title for the Google Sheet (`--format gsheet`) |
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
