# GLAW Firm Roster — single source of truth for who does what

Every GLAW stage routes work to a **seat**. A seat is either an existing skill you
already own (delegate via the Skill tool) or a GLAW skill (a `glaw-*` SKILL.md in
this repo). Stages MUST consult this table before drafting — never improvise a
position a seat already owns. This roster is the firm's no-gaps guarantee: every
domain below maps to a seat.

## Firm management
| Seat | Skill | Role |
|------|-------|------|
| Managing Partner | `/glaw` | Opens matter, drives the pipeline, assigns seats |
| **Chief Counsel (autonomous decision authority)** | `/glaw-chief-counsel` | Runs the loop-until-bulletproof multi-persona debate (relentless IRS/government lead adversary with veto), verifies every cite, ingests Drive comments, routes fixes to seats, and issues the result-oriented file-readiness decision ("yes, we are ready"). Engine: `assets/glaw-chief-counsel-loop.js` |
| Consensus gate | `/glaw-consensus` | Reusable scored gate (panel 0-10 + IRS veto) → BULLETPROOF / DRAFTING-CLEAN / NEEDS-WORK; logic unit-tested in `glaw-chief-counsel/test/loop-selftest.mjs` |
| ReasoningBank | `/glaw-reasoningbank` | Trajectory store (task→verdict→outcome→score) + outcome-aware retrieval; distills to `glaw-learnings`, mirrors to Qdrant/AgentDB |
| Forms library + fill-engine | `/glaw-forms` | Picks the right SEC-derived master (option/plan/RSU/SAFE/note), fills from the cap table, renders house style, gates issuance |
| Review bench | `/glaw-autocounsel` | Runs strategy + structure + adversarial back-to-back |
| Autonomy daemon | `/glaw-daemon` | Source-only standing-goal and docket watcher. Engine: `bin/glaw-daemon`; scans all matters, routes via `glaw-loop`, and stops under the Oversight Board kill-switch |
| Sandbox Simulation | `/glaw-sandbox` | Source-only failure-mode lab. Engine: `bin/glaw-sandbox`; creates isolated temp matters and proves conscience, oversight, daemon, jurisdiction, and profile-map gates fail closed |
| Oversight Board | `/glaw-oversight-board` | Human-governance kill-switch, non-convergence escalation, high-impact autonomy review, and Board decision ledger. Engine: `bin/glaw-oversight`; `glaw-loop` stops while halted |
| General Counsel | `/glaw-ethics-conflicts` | Conflicts, engagement letters, RPC ethics, UPL gate |
| Legal Research | `/glaw-legal-research` | Citation verification — anti-hallucination guardrail |
| Chief Compliance Officer | `/glaw-compliance` | Owns the final packet `compliance_manifest`, ties ethics/UPL, citation grounding, government adversaries, red flags, source evidence, report quality, reviewer identity, and accounting controls into one file-readiness compliance record |
| Jurisdiction Pack | `/glaw-jurisdiction` | Source-backed state/federal/international matrix for governing law, forum, tax, licensing, filings, deadlines, and adversarial government lenses. Engine: `bin/glaw-jurisdiction-pack` |
| Writing desk (**house writing standard, all workflows**) | `/glaw-legal-writing` | Legal Writing Master: IRAC/CREAC/CRRACC, active voice, Bluebook (binding/persuasive/secondary + pin cites), counterargument refutation; **deterministic QC** `bin/glaw-writing-check [--motion]` + the Court Motion Style Sheet (`lib/style/court-motion-style-sheet.md`) + the **Federal Filing Style Directive** (`lib/style/federal-filing-style.md`, `--federal`) with **auto-render** `bin/glaw-federal-format` + **auto-assert** `bin/glaw-format-check` (TNR/double/justified/1.25") |

## Firm-wide output rules (STANDING — every deliverable)
1. **House style + publishing.** Every dossier, drafted `.md`, motion, memo, matrix, and
   briefing is published via **`bin/glaw-publish <matter>`** → local HTML/manifest matter bundle.
   Styling = `lib/house-style.css`
   (Helvetica, justified 12pt/1.5, centered ALL-CAPS title, blue directive callouts, gray
   dividers, 1in margins). Full spec: `lib/house-style.md`.
2. **Scorecard rule.** Every contract review emits a **`bin/glaw-contract-score`** scorecard
   (risk 0-100, tier, grade A-F, red-flag card). **Any document a user uploads as a sample**
   gets scored: `glaw-doc-extract` it → contract → `glaw-contract-score`; financial/fraud →
   `glaw-bureau-score fraud`; compliance docs → `glaw-compliance-audit`; foundation/990 →
   `glaw-exempt-org`. The scorecard is itself a deliverable (publish it).
3. **Chief decision auto-recorded.** At each workflow's decision point, the Chief's card (score,
   grade, decision, conditions, sign-off) is written to the active matter via
   **`bin/glaw-chief-decision`** → appends to `timeline.jsonl` + `decisions.jsonl` + a markdown
   card under `decisions/`. Non-blocking: it records PROCEED / WITH-FIXES / WITH-CONDITIONS and the
   workflow completes. (Engine: `tax-legal-shared/chief-protocol.md` + `score.py`.)
4. **Contract redline with accept/deny.** Any contract reviewed (`glaw-contract-review` /
   `glaw-contract-score`) is marked up via **`bin/glaw-redline annotate <contract> <findings.json>`**
   → a HIGHLIGHTED HTML copy (each flagged clause marked, with the issue + suggested rewrite) +
   a `decisions.json`. Each change is **ACCEPT/DENY**-tracked: `glaw-redline decide <file> <id>
   accept|deny [--note]` (accepted = struck-through in the copy); `glaw-redline status` for the
   tally. The redline is a deliverable (publish it). Feeds the Chief decision in rule 3.
   **Lawyer-grade output:** `bin/glaw-redline-docx <contract.docx> <findings.json>` bridges the same
   findings into a local DOCX redline artifact plus normalized redline JSON for attorney review.

## Matter pipeline (stages)
| Stage | Skill | Produces |
|-------|-------|----------|
| Intake | `/glaw-intake` | Matter charter, conflicts clearance, engagement letter |
| Strategy | `/glaw-strategy` | Case theory (litigation) OR deal thesis (corp-build) OR theory of wrongdoing (investigation) |
| Structure | `/glaw-structure` | Entity org chart, cap table, tax election, fund tiers |
| Draft | `/glaw-draft` | The actual documents |
| Adversarial | `/glaw-adversarial` | **Aggressive** RED-team (opposing counsel / IRS / SEC / trustee / skeptical analyst) per `tax-legal-shared/adversarial.md` → BLUE rebuild → **score** via `tax-legal-shared/calculators/score.py` (hard gate: survives-adversarial<5 ⇒ no-file) |
| File | `/glaw-file` | Signature-ready filing packet + filing checklist |
| Docket | `/glaw-docket` | Deadline calendar + monitoring |
| Retro | `/glaw-matter-retro` | Matter close-out + Obsidian vault write |

---

# Divisions — every domain maps here

## Corporate & Transactional Division
Covers: **Corporate**, entity structuring, IP, contracts, employment, real estate.
| Seat | Skill |
|------|-------|
| Corporate structuring / entity architecture | `/glaw-entity-architect` |
| Formation, governance docs, compliance | `glaw-corporate-counsel` |
| M&A, secured lending, veil-piercing, FL corporate/litigation | `glaw-elite-corporate-counsel` |
| IP (trademark/patent/copyright/trade secret/assignment) | `/glaw-ip-counsel` |
| Commercial contracts (MSA/SaaS/NDA/supply/vendor) — draft/negotiate | `/glaw-commercial-contracts` |
| Inbound/third-party contract **review + redline** (CUAD 41-cat risk grading, market benchmarks, severity triage, negotiation matrix) | `glaw-contract-review` |
| ↳ *contract-review chain:* `glaw-contract-review` (markdown review w/ 🔴/🟡/🟢 tiers + redline language) → findings feed `bin/glaw-contract-score` (scorecard) **and** `bin/glaw-redline-docx` (local DOCX redline artifact + normalized redline JSON). Same 🔴 critical / 🟡 important / 🟢 acceptable severity vocabulary end-to-end. | (pipeline) |
| ↳ *one-shot orchestrator:* `bin/glaw-review-chain <contract.docx> <findings.json> --matter <slug>` runs the whole chain in one command — derives the scorecard, generates local redline artifacts, publishes review+scorecard, and drops everything into the local matter folder. | (pipeline) |
| Employment & labor | `/glaw-employment-counsel` |
| Real estate | `/glaw-real-estate-counsel` |
| §83(b) elections + founder restricted stock + IRS Form 15620 + cap table + Drive comment-review loop | `/glaw-83b-election` |

## Securities, Funds & Capital Markets Division
Covers: **VC fund**, **Private Equity**, **Fund Management**, **SEC compliance**.
| Seat | Skill |
|------|-------|
| Fund formation, LPA/PPM, Reg D/S/CF, Advisers Act, GP/LP economics | `glaw-pe-vc-counsel` |
| SEC/FINRA/state filings: Form D, Form ADV, Form PF, Blue Sky, BD/ATS, custody | `glaw-fund-regulatory-council` |
| Tokenized/digital securities, RWA, transfer agent, KYW | `glaw-tokenization-compliance` |
| Fund modeling, waterfalls, NAV, master-feeder, structured finance, M&A | `glaw-institutional-finance` |

## Tax & IRS Division
Covers: **IRS**, tax planning, tax controversy.
| Seat | Skill |
|------|-------|
| Proactive tax minimization, QSBS §1202, asset protection, wealth | `glaw-tax-strategy` |
| **Full tax-credit/incentive STRATEGY DOSSIER** (roadmap + step-by-step + deadlines + per-credit requirements: QSBS §1202, §83(b)/15620, §351, §409A, R&D §41/§174A, NOLs, §195/§248, ISOs) | `/glaw-credit-strategy` |
| **Retirement-funded business structuring** — using a Roth/IRA/401(k) to capitalize a business (ROBS C-corp QES, Self-Directed/Solo-401(k) checkbook, or build-normally-then-fund-the-Roth); §4975 prohibited-transaction screen + UBIT/UBTI exposure + Solo-401(k)/Roth contribution + optimal-salary solver (`bin/contribution_calc.py`); IRS/DOL adversarial gate | `/glaw-robs-retirement-funding` |
| **Qualified retirement plan compliance (council)** — audits a 401(k)/DB/profit-sharing/money-purchase plan against the IRS *Guide to Common Qualified Plan Requirements* (all 21 §401(a) requirements: participation §410(a), coverage §410(b), nondiscrimination §401(a)(4), ADP/ACP §401(k)/(m), limits §415/§402(g)/§401(a)(17), top-heavy §416, vesting §411, RMD §401(a)(9), J&S §417, rollover §401(a)(31), anti-alienation §401(a)(13), funding §412, exclusive-benefit trust, reporting); §4975 prohibited-transaction screen; EPCRS correction path (SCP/VCP Form 8950/Audit CAP); determination letter (5300/5307/8717) + 5500/5330/1099-R packet. Six council seats scaffolded by `bin/qp_intake.py`; zero-dep 21-point checker + limits table `bin/qp_compliance_check.py`; IRS-EP/DOL-EBSA adversarial gate | `/glaw-qualified-plan` |
| Back taxes, non-filers, penalty abatement, OIC, IRS collections defense | `glaw-tax-compliance`, `glaw-tax-relief` |
| **Back-tax & collections resolution** — file missing years from the GL + multi-year penalty/interest roll (`bin/glaw-back-filing`), SFR replacement (`bin/glaw-sfr`), offer in compromise + RCP (`bin/glaw-oic`), installment agreement (`bin/glaw-installment`), CNC/CDP (`bin/glaw-collections`), Trust Fund Recovery (`bin/glaw-tfrp`); Revenue-Officer adversarial gate | `/glaw-back-taxes` |
| **IRS audit defense (exam → Appeals → Tax Court)** — triage notice + SOL clock (`bin/glaw-sol`), transcript reconstruction (`bin/glaw-transcript`), GL-tied substantiation + Form 4549 recompute (`bin/glaw-audit-package`), penalty abatement (`bin/glaw-abatement`); IRS-examiner adversarial gate | `/glaw-irs-audit` |
| Tax-matter intake / triage | `glaw-tax-legal-intake` |
| **409A valuation architect** (end-to-end draft 409A orchestration: intake gate, DCF/comps/VC/PWERM/priced-round reconciliation, waterfall with conversion test, OPM/backsolve cross-check, DLOM, strike, audit trail, RED/BLUE residual matrix, and appraiser sign-off gate) | `/glaw-valuation-409a-architect` |
| **IP + 409A valuation engine** (audit-ready DRAFT FMV + strike via real OPM/Black-Scholes `bin/opm.py`; IP valuation; equity allocation OPM/PWERM + DLOM; risk scorecard) — fills facts #4/#8 pending appraiser sign-off | `/glaw-valuation-409a` |
| **Valuation adversary** (IRS valuation-examiner RED-team: attacks FMV/DLOM/sigma/backsolve/comps; defensibility 0-10 + sensitivity) — mandatory pass before any valuation is "ready" | `/glaw-valuation-adversary` |
| IRS-audit-shield reconstruction (forensic numbers) | `glaw-financial-forensics` |
| **Entity-specific computation** — S-corp basis Form 7203 (`bin/glaw-scorp-basis`), AAA §1368 (`bin/glaw-scorp-aaa`), partner basis §704(d) (`bin/glaw-partner-basis`), accumulated-earnings §531 + PHC §541 (`bin/glaw-penalty-taxes`), estate/trust 1041 DNI (`bin/glaw-form1041`) | `glaw-tax-strategy` |
| **State & local tax** — state income tax (`bin/glaw-state-tax`), PTET SALT-cap (`bin/glaw-ptet`), franchise/margin DE/TX/CA (`bin/glaw-franchise-tax`), combined/unitary (`bin/glaw-combined-unitary`), P.L. 86-272 nexus (`bin/glaw-income-nexus`), sourcing + throwback (`bin/glaw-sourcing`) | `glaw-tax-strategy` |
| **International** — GILTI §951A (`bin/glaw-gilti`), Subpart F (`bin/glaw-subpart-f`), FDII (`bin/glaw-fdii`), BEAT §59A (`bin/glaw-beat`), §163(j) (`bin/glaw-sec163j`), 5471/5472 (`bin/glaw-intl-forms`) | `glaw-tax-strategy`, `/glaw-international` |
| **Tax-exempt organization compliance** — §501(c) posture + Form 1023/1023-EZ/1024 recognition, annual-return gating + 990-T UBIT + §509(a) public-support test (`bin/glaw-form990`), inurement/self-dealing/excise screen; IRS-EO-examiner adversarial gate | `/glaw-exempt-org` |
| **International tax computation + information returns** — GILTI/Subpart F/FDII/BEAT/§163(j) + 5471/5472 (reuses the `bin/glaw-gilti`…`bin/glaw-intl-forms` engines), FBAR/Form 8938 thresholds + §962 election (`bin/glaw-fbar-8938`), 8865/8858, streamlined / voluntary-disclosure path; IRS-international-examiner adversarial gate | `/glaw-international-tax` |
| **U.S. Tax Court litigation** — 90-day jurisdictional clock (`bin/glaw-sol`), petition prosecution, §7463 small-case (S) election, IRS Counsel / Branerton settlement + docketed Appeals, trial; IRS-Chief-Counsel adversarial gate | `/glaw-tax-court` |
| **Estate & gift tax returns** — Form 706 estate tax (`bin/glaw-form706`) + Form 709 gift/GST (`bin/glaw-form709`) on the §2001(c) schedule, portability/DSUE + GST-allocation elections, appraisal-tied schedules; IRS-estate-&-gift-examiner adversarial gate | `/glaw-estate-gift-returns` |
| **IRS whistleblower (IRC §7623)** — Form 211 eligibility/originality screen, collected-proceeds award-range model 15–30% vs ≤15% (`bin/glaw-wbo-award`), anti-retaliation flag; Whistleblower-Office adversarial gate | `/glaw-irs-whistleblower` |
| **Structured tax-report object** (machine-validatable; sits under the prose memos) | `bin/glaw-tax-report` → schema `lib/schemas/tax-report-schema.json` |

Tax-report data object (`bin/glaw-tax-report types|validate|scaffold`): JSON Schema
vendored + extended from api-evangelist/tax-reporting-templates — report types 1040,
1120, **1120-S**, 1065, W-2, 1099-NEC/MISC, 941, 940, 720, 2290, 8849, sales-tax,
**Schedule K-1**. Tax seats emit a validated report object alongside the narrative;
clean handoff to tax software (TaxJar/Avalara/MeF per the source repo's OpenAPI).

**Compliance audit** (`bin/glaw-compliance-audit <docs-dir> --type s-corp`): data-driven
checklist runner (checklists in `lib/checklists/*.json`); reports ✅ have / 🟡 action /
❌ gap per item with the owning seat. Run `glaw-doc-extract` first for PDFs/DOCX.

**IRS e-file scaffold** (`bin/glaw-irs-file submit <payload.json>`): prepares + validates +
maps an INFORMATION return (1099-NEC/MISC/K, W-2, 941) to a transmitter (TaxBandits/IRIS)
and writes the upload file. DRY RUN by default; `--live` needs an enrolled TCC / transmitter
API key (`glaw config set irs_transmitter|irs_api_key`). Income returns (1120-S/1065) =
MeF via EFIN/approved software, NOT this tool. W-2 → SSA BSO.

**IRS PDF auto-fill** (`bin/glaw-fill-form <blank.pdf> <data.json> <out.pdf>`, `bin/glaw-inspect-fields
<pdf>`): shared AcroForm filler used by the filing seats (`/glaw-exempt-org`, `/glaw-estate-gift-returns`,
`/glaw-international-tax`, `/glaw-irs-whistleblower`). Single source of truth is the credit-strategy
filler, run under the bookkeeping local source runner (reporting-disabled PDF helper). Blank IRS PDFs are a manual drop-in per each seat's
`forms/README.md` — the seat computes the values, the filler stamps them onto the real form.

## Accounting & Finance Division → lead `/glaw-accounting`
| **Forensic reconstruction (re-runnable)** — rebuild gapless, fully-reconciled, audit-ready books from raw bank statements: month-by-month reconstruction → tamper-evident double-entry GL + chart of accounts (`bin/glaw-forensic-pipeline`) → 3-statement + SEC/IRS footnotes → credits + IRS-audit-readiness + forms package + error/resolution log + CFO/CEO reports; forensic-auditor adversarial gate | `/glaw-forensic-reconstruction` |
| **Forensic period reports + trace** — monthly/yearly P&L + full transaction trace, every posting tied to its source statement + tamper-evident hash (`bin/glaw-forensic-reports`); wires categorized by their real ORIG:/BNF: counterparty | `/glaw-forensic-reconstruction` |
| **Executable adversarial gate** — deterministic enforcement red-team (IRS Revenue Agent / forensic accountant / BSA examiner) → chief verdict; AUDIT-READY only when every critical/high finding is cleared with a source-backed resolution (`bin/glaw-forensic-adversarial`) | `/glaw-forensic-reconstruction`, `/glaw-adversarial` |
Covers: **Financial**, accounting, CFO, valuation, audit/assurance.

**The book of record + the agent loop** (the whole accounting is rebuilt, gated, and adversarially agreed here):
| Seat | Skill |
|------|-------|
| **General ledger (book of record)** — persistent double-entry GL: post balanced/non-cash journal entries, import bank as JEs, chart of accounts, as-of balances/GL, period lock, year-end close. Tools `bin/glaw-ledger` · `bin/glaw-journal` · `bin/glaw-coa`. | `/glaw-ledger` |
| **Controller (Accounting Agent)** — keeps & closes the books: posts adjustments, ties subledgers, clears the gate, prepares the draft; the BLUE preparer the panel challenges | `/glaw-controller` |
| **CFO (chief financial orchestrator)** — runs the loop: draft → adversarial panel attacks → collect comments → redirect re-writes → re-gate → **until passed & agreed** → sign-off | `/glaw-cfo` |
| **Audit Agent** — independent rebuild from source, tie-out, integrity, anomaly, **adversarial consensus loop** (CPA + IRS + financial-lawyer), audit opinion | `/glaw-audit` |
| **Reconstruction workflow** — rebuild audited books from MANY statements across MULTIPLE accounts/formats; CFO-orchestrated; continuity gate + transfer netting + per-account tie-out + adversarial loop. Engine `bin/glaw-reconstruct` (+ `bin/glaw-transfers`, `bin/glaw-continuity`) | `/glaw-reconstruct` |
| **Accounting glossary** — original bookkeeping/accounting/CPA reference; look up/search any term (`bin/glaw-glossary`) | `/glaw-glossary` |

**Bookkeeping engine + finance tools:**
| Seat | Skill |
|------|-------|
| Bookkeeping: parse bank/card statements (CSV/OFX/QFX/MT940/CAMT/PAIN/PDF) → deduped, balance-verified ledger; hledger/beancount export; account mapping. Engine vendored at `lib/bookkeeping/`, driver `bin/glaw-bank-ingest`. Feeds the seats below. | `/glaw-bookkeeping` |
| **Financial statements** — native P&L / Balance Sheet / Cash Flow / Trial Balance from the ledger (no hledger dep) | `bin/glaw-statements` |
| **Books control gate (bulletproof)** — deterministic finance doctor: TB balances, BS identity, Golden Rule, classified, cash≥0, dedup, anomaly scan, reconciled; audit/close mode requires `--rec <bank_rec.json> --require-rec` | `bin/glaw-books-doctor` |
| **Bank reconciliation** — line-match books vs bank; surfaces outstanding/unpresented + bank-only items | `bin/glaw-bank-rec` |
| **Period close** — orchestrated month-end: ingest → reconcile → adjust → books-doctor gate → statements → sign-off → lock. Cron-safe runner `bin/glaw-close-run`. | `/glaw-close` |
| **Budget vs actual** — variance cycle; flags expense over-runs / income shortfalls past threshold (`bin/glaw-budget-vs-actual`) | `/glaw-budget` |
| **AP / AR** — vendor & customer subledgers, aging buckets, 3-way match, 1099 tracking; **invoice/bill OCR → draft AP entry** (`bin/glaw-aging`, `bin/glaw-invoice`) | `/glaw-ap-ar` |
| **Payroll accounting** — register, gross-to-net, employer taxes, payroll JE, 941↔W-2 tie-out | `/glaw-payroll` |
| **Fixed assets** — asset register + depreciation (MACRS/SL, §179/bonus) (`bin/glaw-depreciate`) | `/glaw-fixed-assets` |
| **Treasury** — 13-week cash-flow forecast, runway, covenant/min-cash monitoring (`bin/glaw-cashflow-13w`) | `/glaw-treasury` |
| **Sales & use tax / VAT** — nexus, taxability, accrual, multi-jurisdiction filing calendar | `/glaw-sales-tax` |
| **Ledger monitor** — continuous transaction anomaly/fraud scan (`bin/glaw-ledger-monitor`) | `/glaw-ledger-monitor` |

**Reporting, framework & narrative (make the books legible — toward an SEC-style filing):**
| Seat | Skill |
|------|-------|
| **Conceptual Framework** — the objective, qualitative characteristics, elements, recognition & measurement underlying financial reporting | `/glaw-conceptual-framework` |
| **SEC financial reporting** — filer status, 10-K/10-Q/8-K/S-1, Regulation S-X + S-K (MD&A), Inline-XBRL; takes the audited numbers into an SEC filing (per the SEC Financial Reporting Manual) | `/glaw-sec-reporting` |
| **Financial narrative / MD&A** — SEC-filing-style report: overview, MD&A, notes (`bin/glaw-narrative`); printable HTML/PDF + Sheets export (`bin/glaw-export`) | `/glaw-narrative` |
| **Comparative reporting** — MTD / prior / YTD / budget side-by-side from the ledger | `bin/glaw-comparative` |
| **Statement of cash flows (indirect)** — tag-aware, self-reconciling to Δcash | `bin/glaw-cashflow` |
| **Tagged chart of accounts** — account type / current / cash-flow tags → exact ratios + cash flow (`glaw-coa tags`) | `bin/glaw-coa` |
| **Management dashboard** — KPI pack (margins, liquidity, DSO/DPO, leverage, burn) + period-over-period story (`bin/glaw-dashboard`) | `/glaw-dashboard` |

**Specialized accounting (Tier 3):**
| Seat | Skill |
|------|-------|
| **Revenue recognition (ASC 606)** — 5-step model, deferred revenue, contract assets/liabilities (`bin/glaw-revrec`) | `/glaw-revenue` |
| **Income tax provision (ASC 740)** — current + deferred tax, ETR reconciliation, M-1/M-3 (`bin/glaw-tax-provision`; `--book` derives pretax from the GL, `--rules` auto-derives M-1, `--post` books the JE back) | `/glaw-tax-provision` |
| **Tax engine (GL→tax→GL)** — book-to-tax M-1 from the accounts (`bin/glaw-book-to-tax`), deferred-tax basis roll-forward (`bin/glaw-deferred-tax`), and 1120/1120-S/1065/Sch-C return lines off the trial balance (`bin/glaw-return-map`) | `/glaw-tax-provision` |
| **Inventory & COGS** — perpetual/periodic, FIFO/WAC, LCNRV, cost of goods sold (`bin/glaw-inventory`) | `/glaw-inventory` |
| **FX & multi-currency** — functional/reporting currency, period-end revaluation, **per-currency GL + current-rate translation + CTA + realized-FX conversion** (`bin/glaw-fx-reval`, `bin/glaw-fx-report`, `bin/glaw-fx-convert`) | `/glaw-fx` |
| **Consolidation** — multi-entity combine + intercompany eliminations + **non-controlling interest** + **equity-method** roll-forward (`bin/glaw-consolidate`) | `/glaw-consolidation` |
| **Amortization** — loan (interest/principal split) + prepaid/deferral schedules | `bin/glaw-amortize` |
| **Cash application** — match incoming receipts to open AR invoices (closes the AR loop) | `bin/glaw-cash-apply` |
| **Recurring entries** — standard period-end JE templates, validated balanced, posted to the ledger | `bin/glaw-recurring` |
| **Subledgers (auto-post)** — fixed-asset / deferred-revenue / loan schedules that auto-post each close (`bin/glaw-subledger`) | `/glaw-fixed-assets` |
| **Audit preparation** — PBC list, workpapers, tie-outs, audit readiness → hands to `/glaw-audit` | `/glaw-audit-prep` |
| **JE forensics** — SAS-99 journal-entry tests + Benford's-law digit analysis (`bin/glaw-je-test`) | `/glaw-audit` |

**Core accounting seats:**
| Seat | Skill |
|------|-------|
| Forensic reconstruction of financials from raw records, fraud detection, QoE | `glaw-financial-forensics` |
| Audit-readiness, internal controls (COSO/SOX), GAAP/IFRS, ASC 606/842 | `/glaw-audit-assurance` |
| Institutional CFO modeling, 3-statement, LBO/waterfall, EBITDA normalization | `glaw-institutional-finance` |
| Construction/roofing CFO: job costing, WIP, % completion, Xactimate | `glaw-roofer-accounting` |
| Business valuation | `glaw-company-valuation` |
| 409A valuation orchestration, audit trail, RED/BLUE residual matrix, appraiser gate | `/glaw-valuation-409a-architect` |
| Fractional-CFO action plan / ongoing | `glaw-mc-cfo-agent` |

## Litigation & Dispute Resolution Division
Covers: **Civil** litigation, trial, disputes.
| Seat | Skill |
|------|-------|
| Commercial litigation, MCA/usury, fraud-on-court, FUFTA, civil theft, veil-piercing | `glaw-elite-corporate-counsel` |
| **Nonpayment / money recovery** — sue & collect unpaid debts (homeowner/contractor/vendor/freelancer): breach + quantum meruit + unjust enrichment + account stated + construction lien + Prompt Payment; demand → complaint → judgment → execution/garnishment/FUFTA. Helper `bin/glaw-recover` (assess/claims/deadlines) | `/glaw-recover-payment` |
| Federal litigation & trial counsel | `glaw-federal-trial-counsel` |
| Pleadings/motions/discovery drafting | `/glaw-draft` (litigation track) |
| **Quantum meruit / construction non-payment** — full FL civil case (QM + unjust-enrichment complaint, summons/service, discovery pack, MSJ + affidavit, trial brief, damages worksheet w/ §55.03 interest, proposed judgment) + 0-100 settlement-leverage score; extends to breach/account-stated/Ch.713 lien/§772.11 civil theft/FUFTA/RICO (`bin/glaw-qm`) | `/glaw-fl-quantum-meruit` |
| **Florida Title VI civil-practice library** — index DB of all 36 chapters + every cause of action with a ready-to-file complaint/enforcement/petition template, the dispositive-gate checks, discovery/intake/subpoena packs, and a damages+leverage helper + a **110-cause Florida claims library** (every cause's elements/SOL/defenses/authority + legal standards) + a **50-defense affirmative-defenses library** + answer template (`bin/glaw-fl-defense`) (`bin/glaw-fl-cause`, `bin/glaw-fl-statute`, `bin/glaw-qm`) | `/glaw-fl-quantum-meruit` |
| **Federal litigation defenses/adversary library** — the defenses + dispositive attacks a federal adversary brings (civil FRCP: Twombly/Iqbal, SMJ/standing, Daubert, Rule 56/11, qualified immunity; criminal: §3282 SOL, mens rea/Cheek, suppression, Brady, entrapment; regulatory: SEC §2462/Jarkesy, FCPA, AML, RICO) — powers the gate's **Federal Defense Counsel** + **DOJ/AUSA Prosecutor** adversaries (`bin/glaw-fed-defense`) + a **56-cause federal claims library** (elements/SOL/defenses + 22 ready-to-file complaints, a causes catalog, an answer/affirmative-defenses template, a motions pack (12(b)(6)/Rule 56/Daubert), FRCP discovery + Rule 45 subpoena + intake, and verbatim statute excerpts) (`bin/glaw-fed-cause`) | `/glaw-federal-trial-counsel`, `/glaw-investigations`, `/glaw-sec-enforcement`, `/glaw-adversarial` |
| **Florida Title XLI — Fraudulent Transfers (FUFTA Ch. 726) + Statute of Frauds (725) + ABC (727)** — verbatim statute text, FUFTA actual/constructive + ABC causes, the § 726.109 good-faith-transferee + REV + § 726.110 SOL defenses, the badges scorecard, a FUFTA complaint + civil/adversarial review workflow (verbatim statute text + `glaw-fl-cause` / `glaw-fl-defense`) | `/glaw-fl-quantum-meruit`, `/glaw-elite-corporate-counsel`, `/glaw-veil-piercing`, `receivables-assignment-counsel`, `/glaw-adversarial` |
| **Assignment & receivables transfer** — assignability (FL/DE), assignment + corporate authorization + §679.4061 notice or a true-sale Receivables Transfer Agreement, real-party-in-interest (FRCP 17 / Fla. R. Civ. P. 1.210), true-sale-vs-disguised-loan; RED-teams FUFTA / anti-assignment / champerty / non-assignable; wraps the `fl-claims-assignment` engine | `/glaw-receivables-assignment` |
| **Appellate practice** — notice-of-appeal jurisdictional clock, appealability/finality, preservation + standard-of-review map, record designation, initial/answer/reply briefs + rehearing / discretionary-review / cert petitions (FL DCAs & Supreme + federal circuits); appellate-panel adversarial gate | `/glaw-appellate` |
| **Insurance coverage & bad-faith (policyholder)** — policy parse (grant/exclusions/conditions), duty-to-defend vs -indemnify, appraisal vs suit, first-/third-party bad faith + FL §624.155 Civil Remedy Notice; pairs with `/glaw-roofer-accounting` for Xactimate/restoration claims | `/glaw-insurance-coverage` |
| **Consumer protection / debt-collection defense** — FDCPA §1692, FCRA §1681 (credit disputes), TCPA §227, FL FDUTPA + FCCPA §559; debt validation, statutory+actual damages, dispute letter / answer + counterclaim; consumer-side mirror of creditor `/glaw-recover-payment` | `/glaw-consumer-protection` |

## Public Law & Governance Branch
Covers: constitutional limits, public-law drafting, agency action, model adjudication, and government-policy review. This branch prepares attorney work-product only; it does not enact, adjudicate, enforce, file, or bind anyone.
| Seat | Skill |
|------|-------|
| **Constitutional law** — standing, justiciability, state action, scrutiny tier, federalism, separation of powers, First/Fourth/Fifth/Fourteenth Amendment frameworks, and scored risk matrix (`bin/glaw-constitution-score`) | `/glaw-constitutional` |
| **Legislative drafting** — bills, model statutes, ordinances, findings, legislative history, implementation schedule, and public-law drafting package | `/glaw-legislative` |
| **Administrative law** — APA notice-and-comment, agency authority, administrative record, Loper Bright statutory interpretation, arbitrary-and-capricious risk, exhaustion/finality, and remedies | `/glaw-admin-law` |
| **Judicial modeling** — bench memos, model opinions/orders, standards-of-review maps, findings/conclusions drafts, and adjudication simulations for review only | `/glaw-judicial` |

## Family & Domestic Relations Division
Covers: divorce/dissolution, child custody & support, marital property, marital agreements.
| Seat | Skill |
|------|-------|
| **Divorce, custody/support, alimony, property division, pre/post-nup, protective orders** — petition → temporary orders → financial disclosure → parenting plan → property division → decree; TX community-property + ch.154 child-support engine (`bin/glaw-child-support`) vs FL §61.075 equitable distribution; QDRO + tax + estate-cleanup routed out | `/glaw-family-law` |

## Litigation Support Division (the 10 named agents)
Covers: contract review, case-law research, court records, fraud detection, veil
piercing, evidence timeline, financial forensics, motion drafting, adversarial
defense, litigation strategy — each now a discrete callable agent.
| Requested agent | GLAW seat |
|-----------------|-----------|
| Contract Review | `glaw-contract-review` (CUAD 41-cat redline) + `glaw-elite-corporate-counsel` |
| Case Law Research | `/glaw-case-law-research` (find precedent; CourtListener/WebSearch) — engine: `deep-research` for multi-source, adversarially-verified citation gathering |
| PACER / CourtListener | `/glaw-court-records` (docket/opinion fetch; CourtListener API, PACER-ready) |
| Fraud Detection | `glaw-forensic-case-investigator` + `glaw-financial-forensics` via `/glaw-investigations` |
| Corporate Veil Piercing | `/glaw-veil-piercing` (factor matrix) + `glaw-elite-corporate-counsel` |
| Evidence Timeline | `/glaw-evidence-timeline` (source-cited chronology) |
| Financial Forensics | `glaw-financial-forensics` via `/glaw-accounting` |
| Motion Drafting | `/glaw-motion-drafting` + `glaw-federal-trial-counsel` |
| Adversarial Defense | `/glaw-adversarial` (RED→BLUE) |
| Litigation Strategy | `/glaw-strategy` (litigation track) + litigation seats |
Research→verify→draft chain: `/glaw-case-law-research` (+ `deep-research` engine) finds it →
`bin/glaw-cites` (stdlib citation extractor) **extracts every citation** → `/glaw-legal-research` verifies each →
`/glaw-motion-drafting` uses it → `/glaw-legal-writing` polishes it. **Full stage-by-stage map: `lib/workflow.md`.**

Free Law Project tooling (local source runner `~/.glaw/tools/flp-local source runner`, Python 3.12):
- `bin/glaw-cites <file> --json` — **stdlib citation extractor** 2.7.6: deterministic citation extractor (case/short/id/supra/statute) → feeds `/glaw-legal-research`.
- `bin/glaw-court-scrape --list|<court_id>` — **zero-dependency court handoff** 3.0.21: 319 court scrapers + PACER; covers FL Supreme + all 6 DCAs that CourtListener indexes poorly. Used by `/glaw-court-records` alongside the CourtListener API.

## Investigations & White-Collar Crime Division → lead `/glaw-investigations`
Covers: **Criminal**, fraud investigation, forensic case-building.
| Seat | Skill |
|------|-------|
| FBI/financial-crimes RED→BLUE case build, follow-the-money, RICO/wire fraud/laundering/fraudulent transfer/civil theft, build the indictment | `glaw-forensic-case-investigator` |
| Forensic accounting behind the fraud, court-ready numbers, damages | `glaw-financial-forensics` (via `/glaw-accounting`) |
| Criminal + civil exposure mapping, FUFTA, fraud on the court | `glaw-elite-corporate-counsel` |
| Federal criminal / trial posture | `glaw-federal-trial-counsel` |
| Fraudulent-transfer avoidance (§548) | `/glaw-restructuring` |
| **Due-diligence HTML report** — render a self-contained interactive DD report from a findings JSON (graceful if the dd-agents engine isn't installed) | `bin/glaw-dd-report` |

## Intelligence Super-Structure → Master Command `/glaw-command`
Four bureaus under one fusion command. **`/glaw-command` triages every case, always
returns a briefing, and escalates to a full DOSSIER only when RED FLAGS clear the
threshold.** Adversarial review + scorecards run on every issue.
| Bureau / cell | Lead | New specialist agents | Mapped to existing seats |
|---------------|------|----------------------|--------------------------|
| **FBI** (criminal / field / fraud) | `/glaw-bureau` (Case Commander) | field, cyber, osint, humint, fusion, counterfraud, prosecutor | forensic-case-investigator, financial-forensics, /glaw-adversarial |
| **FinCEN** (financial intel) | `/glaw-fincen` (CFIO) | sar, aml, ofac, crypto, tbml | financial-forensics, /glaw-accounting, /glaw-regulatory-aml |
| **CIA** (strategic intel) | `/glaw-intel` (Director) | analyst, counterintel, geopolitical, scitech | /glaw-bureau-osint/cyber/humint (collection), /glaw-adversarial |
| **SEC** (securities enforcement) | `/glaw-sec` (Chief Enforcement) | enforcement, marketabuse, insider, disclosure, adviser | financial-forensics, /glaw-audit-assurance, fund-regulatory-council, pe-vc-counsel, tokenization-compliance |
| IRS-CI (tax) | — | — | financial-forensics, tax-strategy, tax-compliance |
Scoring: `bin/glaw-bureau-score fraud|competency`. Dossier spec + FBI competency
weights: `lib/bureau-roster.md`. Investigation matter track routes here.

## Document Ingestion Layer (read any evidence file)
Before any seat reads evidence, route files through `bin/glaw-doc-extract`:
| File type | Router sends to | Output |
|-----------|-----------------|--------|
| `.pdf` | `glaw-opendataloader-pdf` (layout-faithful) | `<name>.md` |
| email `.eml/.msg/.pst`, Office, images (OCR), HTML, zip, 1000+ types | Apache Tika 3.3.1 (`~/.glaw/tools/tika-app.jar`, Java 21) | `<name>.txt` + `<name>.meta.json` |
`*.meta.json` carries forensic metadata (created/modified dates, author, software) —
used by `glaw-elite-corporate-counsel` (altered/backdated instruments) and
`/glaw-evidence-timeline` (precise event dating). Consumers: `/glaw-evidence-timeline`,
`/glaw-court-records`, `/glaw-investigations`, `glaw-contract-review`, `glaw-financial-forensics`.

## Regulatory, Licensing & Compliance Division
Covers: AML/sanctions, licensing/permits, privacy/data.
| Seat | Skill |
|------|-------|
| OFAC/sanctions, AML/KYC/BSA, FinCEN, MSB/MTL | `/glaw-regulatory-aml` |
| Business/professional/occupational licensing, permits, foreign qualification | `/glaw-licensing` |
| **Import / customs compliance** — HTS classification, duty + Section 301/232 + AD/CVD, MPF/HMF, PGA review (FDA/FCC/CPSC/EPA/USDA/DOT/ATF/OFAC), entry docs (ISF 10+2, bond, IOR), country-of-origin marking + UFLPA, landed cost; emits the Import Compliance Report; CBP/PGA adversarial gate. Routes duty->`/glaw-international-tax`, tax->`/glaw-sales-tax`, IP->`/glaw-ip-counsel`, supplier obligations->`/glaw-commercial-contracts` | `/glaw-import-customs` |
| Privacy policy, ToS, DPA, GDPR/CCPA, breach response | `/glaw-privacy-data` |

## Private Client & Cross-Border Division
Covers: estate/trusts, restructuring, immigration, international.
| Seat | Skill |
|------|-------|
| Estate planning, trusts, succession, asset protection | `/glaw-estate-trusts` |
| **Estate & gift tax RETURNS (706/709)** — prepares/computes what `/glaw-estate-trusts` designs (transfer-tax engine lives in Tax & IRS) | `/glaw-estate-gift-returns` |
| **Tax-exempt org / foundation tax COMPLIANCE** (990/990-T/UBIT, 1023/1024) — preparer counterpart to the `bin/glaw-exempt-org` diligence tool | `/glaw-exempt-org` |
| **Asset-protection STRUCTURES + trust documents + exempt-asset planning** (DAPT/third-party/DING, spendthrift, trust protector, 401k/IRA/life-ins exemptions, custodian) — fills the trust docs + runs the 5-dept compliance gate (FUFTA/solvency/IRS/FinCEN-OFAC/ethics) so nothing raises a red flag | `/glaw-asset-protection` |
| Bankruptcy, workouts, creditor rights | `/glaw-restructuring` |
| Business/founder immigration | `/glaw-immigration` |
| Cross-border / offshore structuring | `/glaw-international` |
| **Tax-exempt org / foundation diligence** (IRS BMF + 990 financials + transparent risk read) | `bin/glaw-exempt-org search\|<EIN>` |

Foundation/nonprofit tool (`bin/glaw-exempt-org`, ProPublica Nonprofit Explorer API,
no key): `search "<name>"` → EINs; `<EIN>` → 501(c)(x) status, NTEE, foundation code,
BMF assets/income, **990 revenue/expense history**, recent 990-PF PDFs, and a
transparent **financial-risk read** (operating margin, expense ratio, deficit years,
revenue trend → LOW/MODERATE/ELEVATED/HIGH, private-foundation-aware). Used by
`/glaw-estate-trusts` (charitable structuring / private foundations) and
`/glaw-investigations` (follow-the-money on a foundation).

## Anthropic Official Legal Skills (adopted as seats, 2026-06-04)
Nine official skills from `anthropics/knowledge-work-plugins` (vendored at
`~/.claude/skills-repos/knowledge-work-plugins/legal`), deployed as top-level
commands. They use connectors (email / docs / e-signature) per the plugin's
`CONNECTORS.md`. GLAW routes to them as fast-lane / workflow seats:
| Skill | Role in GLAW | Relation to existing seat |
|-------|--------------|---------------------------|
| `/triage-nda` | NDA GREEN/YELLOW/RED fast-triage from sales/BD | fast lane → escalates to `/glaw-commercial-contracts` |
| `/review-contract` | Structured inbound-contract review | complements `glaw-contract-review` + `/glaw-commercial-contracts` |
| `/brief` | Legal brief generation | feeds/complements `/glaw-motion-drafting` + `/glaw-legal-writing` |
| `/legal-response` | Draft responses to legal letters/demands | NEW — pairs with `glaw-elite-corporate-counsel` |
| `/legal-risk-assessment` | Structured legal risk analysis | complements `/glaw-adversarial` |
| `/compliance-check` | Compliance verification pass | complements `/glaw-licensing` + the Tax/IRS checklist work |
| `/vendor-check` | Vendor due-diligence / evaluation | NEW — pairs with `/glaw-regulatory-aml` (AML/KYC) |
| `/signature-request` | E-signature execution workflow | NEW — executes `/glaw-file`'s signature matrix |
| `/meeting-briefing` | Pre-meeting briefing prep | NEW — firm management |

## Legal Writing & Document Production
Covers: **Copywriter** / drafting / rendering.
| Seat | Skill |
|------|-------|
| Drafting style, brief/memo polish, persuasion, client copy, Bluebook | `/glaw-legal-writing` |
| Marketing/website copy | `glaw-copywriting`, `glaw-copy-editing` |
| Document rendering | `glaw-make-pdf`, `glaw-docx`, `glaw-document-generate` |

---

## Execution layer — `fs-*` financial-services skills (verified 2026-06-04)
GLAW's advice/drafting seats now delegate the **quantitative execution** to the
`fs-*` skills (Anthropic financial-services repo, 52 skills, symlinked under
`~/.claude/skills-repos/financial-services/`). 25 are wired in; all paths resolve.
Stages don't call `fs-*` directly — they call the seat, which hands off:
| Seat | Hands execution to |
|------|--------------------|
| `glaw-tax-compliance`, `glaw-tax-relief` (IRS) | `glaw-fs-gl-recon`, `glaw-fs-break-trace` (rebuild ledgers); `glaw-fs-xlsx-author`, `glaw-fs-audit-xls` (workpapers) |
| `glaw-tax-strategy` | `glaw-fs-dcf-model`, `glaw-fs-lbo-model`, `glaw-fs-3-statement-model`, `glaw-fs-comps-analysis`, `glaw-fs-merger-model`, `glaw-fs-tax-loss-harvesting`, `glaw-fs-xlsx-author` |
| `glaw-corporate-counsel` | `glaw-fs-3-statement-model`/`glaw-fs-dcf-model`/`glaw-fs-comps-analysis`/`glaw-fs-merger-model` (financing model); `glaw-fs-kyc-doc-parse`/`glaw-fs-kyc-rules` (investor KYC); `glaw-fs-pptx-author` (deck) |
| `glaw-elite-corporate-counsel` | `glaw-fs-gl-recon`/`glaw-fs-break-trace` (trace funds); `glaw-fs-3-statement-model`/`glaw-fs-dcf-model` (damages/lost-profits); `glaw-fs-xlsx-author`/`glaw-fs-audit-xls` (exhibits) |
| `glaw-tax-legal-intake` (router) | sequences the full `fs-*` modeling/ledger/KYC/deck execution layer (26 refs) |
So `/glaw-accounting` and `/glaw-structure` get real model/ledger/KYC/deck/workpaper
output through these seats. Advice stays in the custom suite; math/build goes to `fs-*`.

## Domain → division quick index (no gaps)
| You said... | Division / seat |
|-------------|-----------------|
| Corporate | Corporate & Transactional (`/glaw-entity-architect`, `glaw-corporate-counsel`, `glaw-elite-corporate-counsel`) |
| Financial / Accounting / CFO | Accounting & Finance (`/glaw-accounting`) |
| VC fund / Private Equity / Fund Management | Securities, Funds & Capital Markets (`glaw-pe-vc-counsel`, `glaw-institutional-finance`) |
| SEC compliance | Securities, Funds & Capital Markets (`glaw-fund-regulatory-council`) |
| IRS / Tax | Tax & IRS (`glaw-tax-strategy`, `glaw-tax-compliance`, `glaw-tax-relief`) |
| Nonprofit / foundation / Form 990 / UBIT / exemption | Tax & IRS (`/glaw-exempt-org`) |
| FBAR / Form 8938 / foreign accounts / GILTI / 5471 / §962 | Tax & IRS (`/glaw-international-tax`) + Private Client (`/glaw-international` for the structure) |
| Tax Court / notice of deficiency / 90-day letter | Tax & IRS (`/glaw-tax-court`) |
| Estate tax / gift tax / 706 / 709 / portability / GST | Private Client (`/glaw-estate-trusts` design) + Tax & IRS (`/glaw-estate-gift-returns` returns) |
| IRS whistleblower / Form 211 / §7623 award | Tax & IRS (`/glaw-irs-whistleblower`) |
| Criminal / white-collar | Investigations & White-Collar Crime (`/glaw-investigations`) |
| Civil | Litigation & Dispute Resolution (`glaw-elite-corporate-counsel`, `glaw-federal-trial-counsel`) |
| Family / divorce / custody / child support / alimony / prenup | Family & Domestic Relations (`/glaw-family-law`) |
| Assign a claim or receivable / real party in interest / true sale | Litigation (`/glaw-receivables-assignment`) |
| Appeal / notice of appeal / appellate brief / standard of review | Litigation (`/glaw-appellate`) |
| Insurance claim denial / coverage dispute / bad faith / CRN | Litigation (`/glaw-insurance-coverage`) |
| Consumer / FDCPA / FCRA / TCPA / debt-collection defense | Litigation (`/glaw-consumer-protection`) |
| Copywriter / drafting | Legal Writing & Document Production (`/glaw-legal-writing`) |
| Licensing | Regulatory, Licensing & Compliance (`/glaw-licensing`) |

## Routing rules
1. If a seat above owns the question, route there — do not freelance.
2. Tax → Tax/IRS seats. Securities/funds → Securities seats. Numbers → `/glaw-accounting`. Fraud/criminal → `/glaw-investigations`. Civil disputes → Litigation seats.
3. Every drafted legal proposition passes through `/glaw-legal-research` before `/glaw-file`.
4. No matter advances past intake until `/glaw-ethics-conflicts` clears conflicts.
5. Final wording/format polish goes through `/glaw-legal-writing` before file.
6. **Chief loop (non-blocking, every stage):** each stage's deliverable runs the advocate-vs-
   opposing debate (`tax-legal-shared/adversarial.md`) → `score.py` scorecard → the **division
   Chief** (Managing Partner overall) issues a decision card per `tax-legal-shared/chief-protocol.md`
   and **drives the stage to completion** — a weak score / kill-shot becomes conditions + an
   attorney-sign-off flag + honest downside, **never a stop**. Record the grade + decision card in
   the matter docket. (Only the conflicts/UPL and no-fabrication gates are absolute stops.)

## NOT legal advice
GLAW produces attorney work-product drafts for a licensed attorney to review, sign,
and file. It does not form an attorney-client relationship and does not substitute
for a member of the bar. The UPL guardrail lives in `/glaw-ethics-conflicts`.


## SEC Enforcement & Investigations Division

The securities-enforcement bench. Eleven requested seats, mapped to GLAW skills (★ = new 2026-06-06).

| Seat | Skill |
|---|---|
| SEC Enforcement Attorney | `/glaw-sec-enforcement` |
| SEC Investigator ★ | `/glaw-sec-investigator` |
| Forensic Accountant | `glaw-financial-forensics` + `/glaw-accounting` |
| Market Manipulation Analyst | `/glaw-sec-marketabuse` |
| Insider Trading Analyst | `/glaw-sec-insider` |
| FCPA Investigator ★ | `/glaw-sec-fcpa` |
| Whistleblower Analyst ★ | `/glaw-sec-whistleblower` |
| Litigation Support Specialist | `/glaw-evidence-timeline` + `/glaw-case-law-research` + `glaw-forensic-case-investigator` |
| Expert Witness Report Generator ★ | `/glaw-expert-witness` |
| Wells Notice Response Generator ★ | `/glaw-sec-wells-response` |
| 10-K / 10-Q Risk Analyzer ★ | `/glaw-disclosure-risk-analyzer` |

Also available: `glaw-sec-enforcement-swarm` (user-built skill) for multi-agent enforcement sweeps.
Due-diligence findings render locally through `bin/glaw-dd-report`; no external DD engine clone is
required for the supported workflow.
