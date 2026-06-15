# GLAW Modules and Commands

GLAW is one app. The orchestrator routes work to skills, seats, and local CLIs from this repository.

## Core Orchestration

| Module | Command | Purpose |
|---|---|---|
| Managing partner | `/glaw` | Open matters and route the full pipeline |
| Intake | `/glaw-intake` | Capture parties, facts, jurisdiction, and goals |
| Conflicts | `/glaw-ethics-conflicts` | Conflicts, engagement, UPL guardrail |
| Strategy | `/glaw-strategy` | Case/deal thesis and workplan |
| Structure | `/glaw-structure` | Entity, claims, tax, and evidence structure |
| Draft | `/glaw-draft` | First-pass documents |
| Adversarial | `/glaw-adversarial` | Red-team review before filing |
| File | `/glaw-file` | Filing packet and checklist |
| Docket | `/glaw-docket` | Deadlines and reminders |
| Retro | `/glaw-matter-retro` | Closeout, lessons, and state update |

## Legal Modules

| Area | Modules |
|---|---|
| Contracts | `/glaw-contract-review`, `/glaw-commercial-contracts` |
| Litigation | `/glaw-federal-trial-counsel`, `/glaw-motion-drafting`, `/glaw-appellate`, `/glaw-evidence-timeline` |
| Research and writing | `/glaw-legal-research`, `/glaw-case-law-research`, `/glaw-legal-writing` |
| Corporate | `/glaw-corporate-counsel`, `/glaw-83b-election`, `/glaw-chief-counsel` |
| Securities | `/glaw-sec`, `/glaw-sec-reporting`, `/glaw-sec-enforcement`, `/glaw-sec-disclosure` |
| Tax | `/glaw-tax-strategy`, `/glaw-tax-compliance`, `/glaw-tax-provision`, `/glaw-irs-audit`, `/glaw-tax-court` |
| Regulatory | `/glaw-fincen`, `/glaw-fincen-aml`, `/glaw-fincen-ofac`, `/glaw-privacy-data` |
| Private client | `/glaw-estate-trusts`, `/glaw-asset-protection`, `/glaw-real-estate-counsel` |

## Finance and Forensic Modules

| Area | Modules |
|---|---|
| Accounting | `/glaw-accounting`, `/glaw-bookkeeping`, `/glaw-controller`, `/glaw-cfo` |
| Close and reporting | `/glaw-close`, `/glaw-consolidation`, `/glaw-dashboard`, `/glaw-budget` |
| Forensics | `/glaw-financial-forensics`, `/glaw-forensic-reconstruction`, `/glaw-forensic-case-investigator` |
| Financial services | `/glaw-fs-3-statement-model`, `/glaw-fs-dcf-model`, `/glaw-fs-lbo-model`, `/glaw-fs-merger-model` |
| Financial deliverables | `/glaw-fs-accrual-schedule`, `/glaw-fs-financial-plan`, `/glaw-fs-roll-forward`, `/glaw-fs-teaser`, `/glaw-fs-variance-commentary` |

## Local CLI Commands

| Command | Purpose |
|---|---|
| `bin/glaw` | matter state, docket, timeline, config |
| `bin/glaw-setup` | deploy skills and seats |
| `bin/glaw-doctor` | end-to-end health check |
| `bin/glaw-test` | skill contract validation |
| `bin/glaw-bank-ingest` | source-first bank CSV ingest |
| `bin/glaw-cites` | stdlib citation extraction |
| `bin/glaw-court-scrape` | local court handoff/list |
| `bin/glaw-assemble` | stdlib DOCX template fill |
| `bin/glaw-redline-docx` | local redline artifact generation |
| `bin/glaw-publish` | local HTML/manifest publishing |
| `bin/glaw-tax-report` | local tax form scaffold/validation |

Run any command without arguments to print its usage.
