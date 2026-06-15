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
bin/glaw-intake status
```

`matter new` creates both `matter.md` and `intake.json`. Every workflow must complete
the structured intake before strategy:

```bash
bin/glaw-intake set workflow_track contract-review
bin/glaw-intake set client_names 'Acme Inc.'
bin/glaw-intake set parties 'Acme Inc.; Vendor LLC'
bin/glaw-intake set jurisdiction 'Florida; Delaware'
bin/glaw-intake set goal 'review vendor MSA and produce risk/redline package'
bin/glaw-intake set source_documents 'vendor-msa.docx'
bin/glaw-intake set deadlines '2026-07-01 signature target'
bin/glaw-intake set facts_timeline '2026-06-15 received draft'
bin/glaw-intake set open_questions 'confirm business owner; confirm governing law'
bin/glaw-intake set conflicts_parties 'Acme Inc.; Vendor LLC; affiliates'
bin/glaw-intake set authorized_scope 'review and draft only; no filing/signature authority'
bin/glaw-intake set track_specific.contract_type 'MSA'
bin/glaw-intake set track_specific.counterparty 'Vendor LLC'
bin/glaw-intake set track_specific.governing_law 'Florida'
bin/glaw-intake set track_specific.review_standard 'client-favorable'
bin/glaw-intake complete
bin/glaw-ethics record-conflicts --status cleared --notes 'no conflict identified'
bin/glaw-ethics draft-engagement --scope 'review and draft only' --responsible-professional 'licensed reviewer'
bin/glaw-ethics complete
```

Required gates:

1. Structured intake and conflicts/engagement must clear before strategy.
2. Legal citations must be verified through `glaw-citation-gate complete` before file.
3. Adversarial review must pass before file.
4. Critical/high red flags must be resolved before file.
5. Final packet manifest must be ready before file.
6. Chief/Council must approve final entry before file.
7. External deliverables must include the attorney-review / not-legal-advice guardrail.

Final approval is recorded by the Chief layer:

```bash
bin/glaw-final-packet build --profile auto
bin/glaw-chief-decision --chief "GLAW Chief Counsel" \
  --decision "PROCEED" \
  --risks "none" \
  --conditions "licensed signer final review" \
  --approve-final
```

If the Council denies the final entry, record it with `--deny-final`; unresolved red flags
route back to the owning department until fixed.
`--approve-final` is fail-closed: it refuses to log `chief_approved` unless
`final_packet.json` is ready and `final_packet_ready` is already in the matter timeline.
The Chief approval records the approved packet's `generated_at`; if the packet is rebuilt later,
the file gate blocks until the Chief approves the current packet.
Guarded stage transitions are fail-closed: `glaw stage strategy --force`,
`glaw stage file --force`, and `glaw stage matter-retro --force` cannot bypass missing
events or backing ledgers.

Accounting/bookkeeping has its own required review council before Chief approval:

```bash
bin/glaw-council record --profile auto --role cfo --decision approve --evidence "bank reconciliation and ledger tie-out reviewed"
bin/glaw-council record --profile auto --role irs-audit-agent --decision approve --evidence "return map and source support reviewed"
bin/glaw-council record --profile auto --role legal-counsel --decision approve --evidence "scope, UPL footer, and filing posture reviewed"
bin/glaw-council record --profile auto --role forensic-audit --decision approve --evidence "fraud and unsupported-number checks reviewed"
bin/glaw-council record --profile auto --role outside-critic --decision approve --evidence "independent challenge reviewed"
bin/glaw-council record --profile auto --role external-reviewer --decision approve --evidence "outside review basis recorded"
bin/glaw-council complete --profile auto
```
Every approving council role must record source-backed evidence. `fix` decisions must state the red flags and conditions so the orchestrator can route the matter back before final packet approval.

Use `--decision fix` or `--decision deny` plus `--red-flags` and `--conditions` for any
reviewer that finds a gap. The workflow loops back to the owning department until all required
lenses approve.

Government/regulatory adversarial review is also executable. For accounting/tax work the required
RED-team lenses include IRS, state-tax, forensic-accounting, CFO/controller, and outside critic:

```bash
bin/glaw-adversarial record --profile auto --lens irs-examiner --decision survive --evidence "return tie-out reviewed"
bin/glaw-adversarial record --profile auto --lens state-tax-auditor --decision survive --evidence "state nexus reviewed"
bin/glaw-adversarial record --profile auto --lens forensic-accountant --decision survive --evidence "forensics pass reviewed"
bin/glaw-adversarial record --profile auto --lens cfo-controller --decision survive --evidence "financial statements reviewed"
bin/glaw-adversarial record --profile auto --lens outside-critic --decision survive --evidence "independent challenge complete"
bin/glaw-adversarial complete --profile auto
```

Use `--decision fix` or `--decision strike` with `--attack` and `--cure` when a government,
regulatory, or litigation adversary finds a fatal or curable weakness. The command opens a blocking
red flag automatically.
Every `survive` decision must carry source-backed evidence, so a RED-team pass cannot be logged as
ready from an unsupported conclusion.

Ethics, red flags, UPL footer, and the final packet are explicit gates:

```bash
bin/glaw-ethics status
bin/glaw-citation-gate status
bin/glaw-red-flags status
bin/glaw-upl-check "$(bin/glaw slug)"
bin/glaw-red-flags complete
bin/glaw-council complete --profile auto
bin/glaw-adversarial complete --profile auto
bin/glaw-final-packet build --profile auto
```

`glaw-final-packet` writes `final_packet.json` and `final_packet.md`, then logs
`final_packet_ready` only when intake/conflicts/ethics/citation ledger/adversarial, UPL footer
checks, red flags, the required council profile, and at least one external-facing text deliverable
are all explicitly completed and clear. Each external text deliverable must also pass the
professional-report marker gate: `Owner:`, `Report voice:`, `Findings:`, `Evidence:`,
`Red flags:`, and `Sign-off conditions:`. Evidence must cite a hashed source artifact ID
from the packet's source manifest, e.g. `Evidence: SRC-0001 bank statement`; source artifacts
live under `evidence/`, `sources/`, or `source_documents/`.

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

For bookkeeping/tax workflows, intake must identify the source records and tax scope:

```bash
bin/glaw-intake set workflow_track accounting-tax
bin/glaw-intake set track_specific.bank_statement_sources 'statements/*.pdf; Google Sheet URL'
bin/glaw-intake set track_specific.tax_years '2024; 2025'
bin/glaw-intake set track_specific.entity_tax_type 'C-corp'
bin/glaw-intake set track_specific.books_status 'raw bank statements only'
bin/glaw-intake set track_specific.irs_forms_needed '1120; 1099; 941'
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
