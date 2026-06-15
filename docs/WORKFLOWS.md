# GLAW Workflow Playbook

Every matter runs through the same gates:

```text
intake -> conflicts -> strategy -> structure -> draft -> adversarial -> file -> docket -> retro
```

## Matter Opening

```bash
bin/glaw matter new "Acme contract review"
bin/glaw matter list
bin/glaw matter use acme-contract-review
bin/glaw stage intake
```

Required gates:

1. Conflicts and engagement must clear before strategy.
2. Legal citations must be verified before file.
3. Adversarial review must pass before file.
4. External deliverables must include the attorney-review / not-legal-advice guardrail.

## Contract Review

```bash
bin/glaw-contract-score scaffold > findings.json
bin/glaw-redline-docx contract.docx findings.json -o out/contract
bin/glaw-review-chain contract.docx findings.json --matter acme-contract-review
```

Output: scorecard, local redline artifact, DOCX replacement output, and local publish bundle.

## Federal Trial Counsel

```bash
cd federal-trial-counsel/scripts
python3 -m ftc_engine.cli doctor
python3 -m ftc_engine.cli claims
python3 -m ftc_engine.cli info 1983_fourth_excessive_force
python3 -m ftc_engine.cli draft -i sample_case.json -o complaint.md
```

TXT, MD, and DOCX intake documents are handled locally. PDFs that require binary parsing or OCR return a clear handoff message in the bundled zero-dependency build.

## Bookkeeping and Forensics

```bash
printf 'date,description,amount\n2026-01-01,Test deposit,100.00\n' > /tmp/glaw-sample.csv
GLAW="$PWD" bin/glaw-bank-ingest /tmp/glaw-sample.csv --format json
GLAW="$PWD" bin/glaw-bank-ingest "https://docs.google.com/spreadsheets/d/<id>/edit#gid=0" --format json
bin/glaw-books-doctor
bin/glaw-bank-rec
```

The bookkeeping engine lives inside `lib/bookkeeping/glaw_engine` and uses in-repo compatibility shims for table, model, and XML behavior. Google Sheets input is read through the sheet CSV export URL with Python stdlib. PDF/OCR ingestion is repo-owned orchestration over local binaries (`pdftotext` or `opendataloader-pdf`; scans need `pdftoppm` + `tesseract`).

## Publishing

```bash
bin/glaw-publish matters/acme-contract-review --local-only
```

Output is local HTML plus a manifest. Google Docs, Sheets, Slides, and Drive SDKs are not bundled.

## Validation Before Commit

```bash
GLAW_SKILL_DIR="$PWD" bash bin/glaw-test
tmp="$(mktemp -d)"
GLAW_SKILLS_ROOT="$tmp/skills" GLAW_SKILL_DIR="$PWD" bash bin/glaw-setup
GLAW_SKILLS_ROOT="$tmp/skills" GLAW_SKILL_DIR="$PWD" bash bin/glaw-doctor
```

Fix any failing skill contract, dangling path, or smoke failure before publishing.
