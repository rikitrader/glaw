# GLAW Toolbelt — CLI Reference

The firm's reasoning lives in markdown skills; its deterministic work lives in source-only
CLIs under [`../bin/`](../bin/). The toolbelt is source-first and zero third-party package:
no `pip install`, no `npm install`, no virtualenv bootstrap, and no remote package fetch.
Tools use bash, Python 3, repository libraries, and the Python standard library.

Run any tool with no arguments for its usage. `bin/glaw-doctor` smoke-tests them all.

## State & ops
| Tool | Usage |
|---|---|
| `glaw` | `matter new "<name>"` · `matter list` · `matter use <slug>` · `stage <stage>` · `docket add --owner <owner> --source "SRC-0001 <basis>" <YYYY-MM-DD> "<desc>"` · `docket upcoming [days]` · `timeline-log <event>` · `config get/set <k> [v]` |
| `glaw-docket-gate` | `status` · `complete` after owned/source-backed deadlines are docketed; `no-deadlines --source "SRC-0001 <basis>" --rationale <why>` for explicit no-deadline close-out |
| `glaw-intake` | `init [slug] --track <track>` · `set <field> <value>` · `status` · `complete` · `show`; strategy and file gates revalidate the current structured `intake.json`, including universal and track-specific fields |
| `glaw-ethics` | `record-conflicts --status cleared\|waived\|conflict --source "SRC-0001 <basis>"` · `draft-engagement --source "SRC-0001 <basis>"` · `status` · `complete`; logs `conflicts_cleared` only after source-backed conflicts and engagement are ready |
| `glaw-council` | `record --profile auto --role <lens> --decision approve\|fix\|deny` · `status` · `complete`; `approve` requires source-backed `--evidence` plus role-specific `--notes`, `fix/deny` red flags must cite `SRC-####`, `fix` requires `--conditions`, and every required role must approve before final packet |
| `glaw-adversarial` | `record --profile auto --lens <government/regulatory lens> --decision survive\|fix\|strike` · `status` · `complete`; `survive` requires source-backed `--evidence` plus an `--attack` challenge summary, `fix/strike` attacks must cite `SRC-####`, `fix` requires `--cure`, and `adversarial_done` logs only when every required RED-team lens survives |
| `glaw-red-flags` | `add --severity critical\|high\|medium\|low ...` · `resolve <id> --evidence "SRC-0001 <fix support>"` · `status` · `complete` · `list`; resolution evidence must cite a source ID and final packet/gate revalidates critical/high closures against current source artifacts |
| `glaw-upl-check` | `<matter-slug-or-dir>` → fail-closed check that text deliverables carry attorney-work-product / not-legal-advice footer language |
| `glaw-citation-gate` | `record --id <id> --proposition ... --authority ... --status verified --source-url https://... --reviewer <name>` · `status` · `complete`; logs `citations_verified` only when every latest citation row is verified with proposition, authority, reviewer, and HTTP(S) source URL |
| `glaw-final-packet` | `build --profile auto` → `final_packet.json` + `final_packet.md`; logs `final_packet_ready` only when gates are clear, at least one external text deliverable exists, every external report includes `Owner:`, `Report voice:`, `Findings:`, `Evidence:`, `Red flags:`, and `Sign-off conditions:`, has no unresolved bracket placeholders such as `[VERIFY]` and no unresolved `REVIEW:` markers, the report plus required council/adversarial reviews and resolved critical/high red flags cite hashed nonempty source files such as `SRC-0001` from `evidence/`, `sources/`, or `source_documents/`, every required reviewer/lens resolves to a hashed GLAW skill identity file, and the markdown packet digest matches `final_packet.json` |
| `glaw-setup` | deploy every sub-skill as a `/glaw-*` command (symlink model) |
| `glaw-doctor` | health harness: skills resolve · tools run · no dangling refs · Codex/Claude parity · no weak review-gate examples → `HEALTHY`/`PROBLEMS` |
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
| `glaw-chief-decision` | record the Chief's PROCEED / WITH-FIXES / WITH-CONDITIONS sign-off → matter timeline + decision card; final approve/deny requires `--score`, `--grade`, `--risks`, `--conditions`, and `--rationale`; `--approve-final` rebuilds `final_packet.json`, requires it to be ready, requires a proceed/approve decision, requires the Chief rationale to cite a current `SRC-####`, and binds approval to that packet's `generated_at` plus SHA-256 digest |

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
