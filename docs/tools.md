# GLAW Toolbelt — CLI reference

The firm's reasoning lives in markdown skills; its deterministic work lives in 20 small
CLIs under [`../bin/`](../bin/). The **core (matter state) needs only bash**; the rest are
progressive enhancement (`pip install -r ../requirements.txt` + a few system tools).

Run any tool with no arguments for its usage. `bin/glaw-doctor` smoke-tests them all.

## State & ops
| Tool | Usage |
|---|---|
| `glaw` | `matter new "<name>"` · `matter list` · `matter use <slug>` · `stage <stage>` · `docket add <YYYY-MM-DD> "<desc>"` · `docket upcoming [days]` · `timeline-log <event>` · `config get/set <k> [v]` |
| `glaw-setup` | deploy every sub-skill as a `/glaw-*` command (symlink model) |
| `glaw-doctor` | health harness: skills resolve · tools run · no dangling refs → `HEALTHY`/`PROBLEMS` |
| `glaw-preamble.sh` | shared preamble emitted by each stage skill |

## Contract-review chain
| Tool | Usage |
|---|---|
| `glaw-contract-score` | `scaffold` · `<findings.json>` → scorecard (risk 0–100, tier, grade A–F, red-flag card). Severity 🔴critical/🟡important/🟢acceptable. |
| `glaw-redline` | `annotate <contract> <findings.json>` → highlighted HTML + comments · `decide <file> <id> accept\|deny` · `status <file>` |
| `glaw-redline-docx` | `<contract.docx> <findings.json> [-o base]` → real Word tracked changes (`w:ins`/`w:del`) + redline/summary/memo PDFs (via legal-redline-tools) |
| `glaw-review-chain` | `<contract.docx> <findings.json> --matter <slug>` → one-shot: scorecard + Word track-changes + publish, all to one Drive folder |

`findings.json` (the shared shape): `[{ "id","quote","severity","issue","suggestion" }]`.

## Documents & research
| Tool | Usage |
|---|---|
| `glaw-doc-extract` | `<file\|dir> [-o out]` → text + metadata (Apache Tika / opendataloader-pdf; OCR via Tesseract) |
| `glaw-cites` | `<file>` or `-` (stdin) `[--json]` → extracted/normalized citations (eyecite) |
| `glaw-court-scrape` | `--list [filter]` · `<court_id>` → dockets/opinions (juriscraper, 300+ courts + PACER) |
| `glaw-assemble` | `vars <template.docx>` · `<template.docx> <data.json> -o out.docx` (Jinja-in-Word, docxtpl) |
| `glaw-publish` | `<matter-slug\|dir> [--folder NAME] [--local-only]` → PDF + Google Doc + Google Slides in the house style |

## Tax & regulatory
| Tool | Usage |
|---|---|
| `glaw-tax-report` | `types` · `validate <f.json>` · `scaffold <form>` (JSON Schema; 1040/1120/1120-S/1065/W-2/1099/941/… ) |
| `glaw-irs-file` | `scaffold <form>` · `submit <payload.json> [--live]` · `status <id>` · `efw2 <payload.json>` (W-2→SSA) · `list <year>` |
| `glaw-compliance-audit` | `<docs-dir> [--type s-corp\|c-corp\|llc\|fund] [-o out.md]` → ✅have / 🟡action / ❌gap per item |
| `glaw-exempt-org` | `search "<name>"` · `<EIN>` → nonprofit lookup + financial-risk read (ProPublica API, no key) |

## Scoring & sign-off
| Tool | Usage |
|---|---|
| `glaw-bureau-score` | `competency <json>` · `fraud <json>` → deterministic fraud score (0–100) + FBI competency scorecard |
| `glaw-chief-decision` | record the Chief's PROCEED / WITH-FIXES / WITH-CONDITIONS sign-off → matter timeline + decision card |

## Dependencies
Python deps are in [`../requirements.txt`](../requirements.txt). System tools (install
separately): `pandoc` + `weasyprint` (publishing), `tesseract` + `poppler` (OCR),
Java 21 + Apache Tika jar (extraction), `opendataloader-pdf` (PDF→Markdown). Each tool
degrades gracefully when an optional dependency is absent.
