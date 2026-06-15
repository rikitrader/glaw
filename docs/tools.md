# GLAW Toolbelt — CLI Reference

The firm's reasoning lives in markdown skills; its deterministic work lives in source-only
CLIs under [`../bin/`](../bin/). The toolbelt is source-first and zero third-party package:
no `pip install`, no `npm install`, no virtualenv bootstrap, and no remote package fetch.
Tools use bash, Python 3, repository libraries, and the Python standard library.

Run any tool with no arguments for its usage. `bin/glaw-doctor` smoke-tests them all.

## State & ops
| Tool | Usage |
|---|---|
| `glaw` | `matter new "<name>"` · `matter list` · `matter use <slug>` · `stage <stage>` · `docket add <YYYY-MM-DD> "<desc>"` · `docket upcoming [days]` · `timeline-log <event>` · `config get/set <k> [v]` |
| `glaw-intake` | `init [slug] --track <track>` · `set <field> <value>` · `status` · `complete` · `show` for the structured `intake.json` gate |
| `glaw-ethics` | `record-conflicts --status cleared\|waived\|conflict` · `draft-engagement` · `status` · `complete`; logs `conflicts_cleared` only after conflicts and engagement are ready |
| `glaw-council` | `record --profile auto --role <lens> --decision approve\|fix\|deny` · `status` · `complete` for required multi-agent signoff |
| `glaw-adversarial` | `record --profile auto --lens <government/regulatory lens> --decision survive\|fix\|strike` · `status` · `complete`; logs `adversarial_done` only when every required RED-team lens survives |
| `glaw-red-flags` | `add --severity critical\|high\|medium\|low ...` · `resolve <id> --evidence <text>` · `status` · `list` for blocking issue control |
| `glaw-upl-check` | `<matter-slug-or-dir>` → fail-closed check that text deliverables carry attorney-work-product / not-legal-advice footer language |
| `glaw-citation-gate` | `record --id <id> --proposition ... --authority ... --status verified --source-url <url>` · `status` · `complete`; logs `citations_verified` only when every latest citation row is verified |
| `glaw-final-packet` | `build --profile auto` → `final_packet.json` + `final_packet.md`; logs `final_packet_ready` only when gates are clear |
| `glaw-setup` | deploy every sub-skill as a `/glaw-*` command (symlink model) |
| `glaw-doctor` | health harness: skills resolve · tools run · no dangling refs → `HEALTHY`/`PROBLEMS` |
| `glaw-preamble.sh` | shared preamble emitted by each stage skill |

## Contract-review chain
| Tool | Usage |
|---|---|
| `glaw-contract-score` | `scaffold` · `<findings.json>` → scorecard (risk 0–100, tier, grade A–F, red-flag card). Severity 🔴critical/🟡important/🟢acceptable. |
| `glaw-redline` | `annotate <contract> <findings.json>` → highlighted HTML + comments · `decide <file> <id> accept\|deny` · `status <file>` |
| `glaw-redline-docx` | `<contract.docx> <findings.json> [-o base]` → local normalized redline JSON plus replacement DOCX |
| `glaw-review-chain` | `<contract.docx> <findings.json> --matter <slug>` → one-shot local scorecard, redline artifact, and publish bundle |

`findings.json` (the shared shape): `[{ "id","quote","severity","issue","suggestion" }]`.

## Documents & research
| Tool | Usage |
|---|---|
| `glaw-doc-extract` | `<file\|dir> [-o out]` → text + metadata for local text/DOCX inputs; PDFs use local binaries when installed |
| `glaw-cites` | `<file>` or `-` (stdin) `[--json]` → extracted/normalized citations (stdlib citation extractor) |
| `glaw-court-scrape` | `--list [filter]` · `<court_id>` → dockets/opinions (zero-dependency court handoff, 300+ courts + PACER) |
| `glaw-assemble` | `vars <template.docx>` · `<template.docx> <data.json> -o out.docx` using stdlib DOCX merge |
| `glaw-publish` | `<matter-slug\|dir> [--folder NAME] [--local-only]` → local HTML/manifest publish bundle in the house style |

## Tax & regulatory
| Tool | Usage |
|---|---|
| `glaw-tax-report` | `types` · `validate <f.json>` · `scaffold <form>` using the in-repo stdlib schema validator |
| `glaw-fill-form` | `--form FORM --data return.json --out out/form` → `.fill.json` + `.fill.txt` manual-entry package |
| `glaw-irs-file` | `scaffold <form>` · `submit <payload.json> [--live]` · `status <id>` · `efw2 <payload.json>` (W-2→SSA) · `list <year>` |
| `glaw-compliance-audit` | `<docs-dir> [--type s-corp\|c-corp\|llc\|fund] [-o out.md]` → ✅have / 🟡action / ❌gap per item |
| `glaw-exempt-org` | `search "<name>"` · `<EIN>` → nonprofit lookup + financial-risk read (ProPublica API, no key) |

## Scoring & sign-off
| Tool | Usage |
|---|---|
| `glaw-bureau-score` | `competency <json>` · `fraud <json>` → deterministic fraud score (0–100) + FBI competency scorecard |
| `glaw-chief-decision` | record the Chief's PROCEED / WITH-FIXES / WITH-CONDITIONS sign-off → matter timeline + decision card; `--approve-final` requires a ready `final_packet.json` |

## Zero-Dependency Policy

GLAW ships no third-party package manifest. The supported install path is:

```bash
./setup
bin/glaw-doctor
```

Library code that historically depended on packages such as pandas, pydantic, lxml,
python-docx, docxtpl, eyecite, juriscraper, jsonschema, or Google SDKs now uses in-repo
compatibility modules or local stdlib fallbacks. Google Sheets input uses CSV export URLs.
PDF/OCR bank ingestion uses repo code plus local binaries, not Python packages.
