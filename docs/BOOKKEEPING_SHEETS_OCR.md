# Bookkeeping: Google Sheets and OCR Workflow

GLAW bookkeeping is source-first: Python owns ingestion, validation, audit output, and reporting from in-repo code. It does not install Python packages or use Google SDKs.

## Google Sheets Input

Use a Google Sheet that can export CSV:

```bash
GLAW="$PWD" bin/glaw-bank-ingest "https://docs.google.com/spreadsheets/d/<id>/edit#gid=0" --format json
```

Required columns:

| Column | Notes |
|---|---|
| `date` | ISO or common slash date |
| `description` | Bank memo or counterparty |
| `amount` | Positive deposits, negative withdrawals |

Private Sheets can use local gcloud OAuth:

```bash
gcloud auth application-default login
GLAW="$PWD" bin/glaw-bank-ingest "<sheet-url>" --google-auth gcloud --format json
```

`--google-auth auto` is the default: it uses a local gcloud token when available and otherwise attempts normal CSV export.

## OCR/PDF Input

Digital PDFs use local text extraction when available:

```bash
brew install poppler
GLAW="$PWD" bin/glaw-bank-ingest statement.pdf --ocr off --format json
```

Scanned PDFs use Python-owned OCR orchestration over local binaries:

```bash
brew install poppler tesseract
GLAW="$PWD" bin/glaw-bank-ingest statement.pdf --ocr auto --ocr-profile bank-statement --format json
```

Profiles:

| Profile | Use |
|---|---|
| `bank-statement` | Default multi-DPI, multi-PSM pass for statement rows |
| `dense` | Higher-DPI attempts for crowded scans |
| `simple` | Faster pass for clean scans |

OCR output carries audit metadata in the ingestion result warnings, including source method and row counts. Low-confidence parses return explicit warnings or fail cleanly; GLAW does not silently invent rows.

## Full Cycle

```bash
GLAW="$PWD" bin/glaw-bank-ingest "<sheet-or-file>" --format json > /tmp/glaw-book.json
GLAW="$PWD" bin/glaw-books-doctor /tmp/glaw-book.json
GLAW="$PWD" bin/glaw-bank-rec --books /tmp/glaw-book.json --bank /tmp/glaw-book.json --format json
GLAW="$PWD" bin/glaw-bookkeeping-doctor
```

## Tax Forms and Tie-Out

Business return lines are generated from the posted ledger, not freehand:

```bash
GLAW_HOME="$HOME/.glaw" GLAW="$PWD" bin/glaw-return-map --book company --form 1120 --format json > /tmp/1120.json
GLAW="$PWD" bin/glaw-fill-form --form 1120 --data /tmp/1120.json --out /tmp/1120
GLAW_HOME="$HOME/.glaw" GLAW="$PWD" bin/glaw-tax-provision --book company --rate 21 --post --date 2026-12-31
GLAW_HOME="$HOME/.glaw" GLAW="$PWD" bin/glaw-tax-tieout --book company --rate 21
```

`glaw-fill-form` writes a `.fill.json` payload and `.fill.txt` review checklist for manual entry into official IRS PDFs, e-file systems, or tax software. It does not rewrite official PDF binaries without a PDF library.

All downloaded Sheets, OCR images, and CSV exports should remain in temp paths or `~/.glaw/work`, never in the repository.
