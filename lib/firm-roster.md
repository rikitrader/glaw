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
| Review bench | `/glaw-autocounsel` | Runs strategy + structure + adversarial back-to-back |
| General Counsel | `/glaw-ethics-conflicts` | Conflicts, engagement letters, RPC ethics, UPL gate |
| Legal Research | `/glaw-legal-research` | Citation verification — anti-hallucination guardrail |
| Writing desk | `/glaw-legal-writing` | Drafting style, brief/memo polish, client copy, Bluebook |

## Firm-wide output rules (STANDING — every deliverable)
1. **House style + publishing.** Every dossier, drafted `.md`, motion, memo, matrix, and
   briefing is published via **`bin/glaw-publish <matter>`** → **PDF (styled) + Google Doc
   + Google Slides** in one Google Drive folder, with an `index`. Styling = `lib/house-style.css`
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
4. **Contract redline with accept/deny.** Any contract reviewed (`contract-review` /
   `glaw-contract-score`) is marked up via **`bin/glaw-redline annotate <contract> <findings.json>`**
   → a HIGHLIGHTED HTML copy (each flagged clause marked, with the issue + suggested rewrite) +
   a `decisions.json`. Each change is **ACCEPT/DENY**-tracked: `glaw-redline decide <file> <id>
   accept|deny [--note]` (accepted = struck-through in the copy); `glaw-redline status` for the
   tally. The redline is a deliverable (publish it). Feeds the Chief decision in rule 3.
   **Lawyer-grade output:** `bin/glaw-redline-docx <contract.docx> <findings.json>` bridges the same
   findings into **real Microsoft Word tracked changes** (`w:ins`/`w:del`, accept/reject in Word) +
   full-redline PDF + schedule-of-changes PDF + internal memo, via legal-redline-tools
   (evolsb/legal-redline-tools, MIT; in `~/.glaw/tools/flp-venv`; smart/straight quotes auto-reconciled).
   `legal-redline diff a.docx b.docx` compares two versions → redline JSON.

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
| Formation, governance docs, compliance | `corporate-counsel` |
| M&A, secured lending, veil-piercing, FL corporate/litigation | `elite-corporate-counsel` |
| IP (trademark/patent/copyright/trade secret/assignment) | `/glaw-ip-counsel` |
| Commercial contracts (MSA/SaaS/NDA/supply/vendor) — draft/negotiate | `/glaw-commercial-contracts` |
| Inbound/third-party contract **review + redline** (CUAD 41-cat risk grading, market benchmarks, severity triage, negotiation matrix) | `contract-review` |
| ↳ *contract-review chain:* `contract-review` (evolsb/claude-legal-skill v3, markdown review w/ 🔴/🟡/🟢 tiers + redline language) → findings feed `bin/glaw-contract-score` (scorecard) **and** `bin/glaw-redline-docx` (real Word track-changes via legal-redline-tools). Same 🔴 critical / 🟡 important / 🟢 acceptable severity vocabulary end-to-end. | (pipeline) |
| ↳ *one-shot orchestrator:* `bin/glaw-review-chain <contract.docx> <findings.json> --matter <slug>` runs the whole chain in one command — derives the scorecard, generates the Word tracked changes + PDFs, publishes review+scorecard, and drops everything (review + scorecard ×3 formats + tracked-changes Word + redline/summary/memo PDFs) into ONE Drive folder. **"Review this Drive contract" action:** download → `contract-review` produces findings → `glaw-review-chain` does the rest. | (pipeline) |
| Employment & labor | `/glaw-employment-counsel` |
| Real estate | `/glaw-real-estate-counsel` |

## Securities, Funds & Capital Markets Division
Covers: **VC fund**, **Private Equity**, **Fund Management**, **SEC compliance**.
| Seat | Skill |
|------|-------|
| Fund formation, LPA/PPM, Reg D/S/CF, Advisers Act, GP/LP economics | `pe-vc-counsel` |
| SEC/FINRA/state filings: Form D, Form ADV, Form PF, Blue Sky, BD/ATS, custody | `fund-regulatory-council` |
| Tokenized/digital securities, RWA, transfer agent, KYW | `tokenization-compliance` |
| Fund modeling, waterfalls, NAV, master-feeder, structured finance, M&A | `institutional-finance` |

## Tax & IRS Division
Covers: **IRS**, tax planning, tax controversy.
| Seat | Skill |
|------|-------|
| Proactive tax minimization, QSBS §1202, asset protection, wealth | `tax-strategy` |
| Back taxes, non-filers, penalty abatement, OIC, IRS collections defense | `tax-compliance`, `tax-relief` |
| Tax-matter intake / triage | `tax-legal-intake` |
| IRS-audit-shield reconstruction (forensic numbers) | `financial-forensics` |
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

## Accounting & Finance Division → lead `/glaw-accounting`
Covers: **Financial**, accounting, CFO, valuation, audit/assurance.
| Seat | Skill |
|------|-------|
| Forensic reconstruction of financials from raw records, fraud detection, QoE | `financial-forensics` |
| Audit-readiness, internal controls (COSO/SOX), GAAP/IFRS, ASC 606/842 | `/glaw-audit-assurance` |
| Institutional CFO modeling, 3-statement, LBO/waterfall, EBITDA normalization | `institutional-finance` |
| Construction/roofing CFO: job costing, WIP, % completion, Xactimate | `roofer-accounting` |
| Business valuation | `company-valuation` |
| Fractional-CFO action plan / ongoing | `mc-cfo-agent` |

## Litigation & Dispute Resolution Division
Covers: **Civil** litigation, trial, disputes.
| Seat | Skill |
|------|-------|
| Commercial litigation, MCA/usury, fraud-on-court, FUFTA, civil theft, veil-piercing | `elite-corporate-counsel` |
| Federal litigation & trial counsel | `federal-trial-counsel` |
| Pleadings/motions/discovery drafting | `/glaw-draft` (litigation track) |

## Litigation Support Division (the 10 named agents)
Covers: contract review, case-law research, court records, fraud detection, veil
piercing, evidence timeline, financial forensics, motion drafting, adversarial
defense, litigation strategy — each now a discrete callable agent.
| Requested agent | GLAW seat |
|-----------------|-----------|
| Contract Review | `contract-review` (CUAD 41-cat redline) + `elite-corporate-counsel` |
| Case Law Research | `/glaw-case-law-research` (find precedent; CourtListener/WebSearch) — engine: `deep-research` for multi-source, adversarially-verified citation gathering |
| PACER / CourtListener | `/glaw-court-records` (docket/opinion fetch; CourtListener API, PACER-ready) |
| Fraud Detection | `forensic-case-investigator` + `financial-forensics` via `/glaw-investigations` |
| Corporate Veil Piercing | `/glaw-veil-piercing` (factor matrix) + `elite-corporate-counsel` |
| Evidence Timeline | `/glaw-evidence-timeline` (source-cited chronology) |
| Financial Forensics | `financial-forensics` via `/glaw-accounting` |
| Motion Drafting | `/glaw-motion-drafting` + `federal-trial-counsel` |
| Adversarial Defense | `/glaw-adversarial` (RED→BLUE) |
| Litigation Strategy | `/glaw-strategy` (litigation track) + litigation seats |
Research→verify→draft chain: `/glaw-case-law-research` (+ `deep-research` engine) finds it →
`bin/glaw-cites` (eyecite) **extracts every citation** → `/glaw-legal-research` verifies each →
`/glaw-motion-drafting` uses it → `/glaw-legal-writing` polishes it. **Full stage-by-stage map: `lib/workflow.md`.**

Free Law Project tooling (venv `~/.glaw/tools/flp-venv`, Python 3.12):
- `bin/glaw-cites <file> --json` — **eyecite** 2.7.6: deterministic citation extractor (case/short/id/supra/statute) → feeds `/glaw-legal-research`.
- `bin/glaw-court-scrape --list|<court_id>` — **juriscraper** 3.0.21: 319 court scrapers + PACER; covers FL Supreme + all 6 DCAs that CourtListener indexes poorly. Used by `/glaw-court-records` alongside the CourtListener API.

## Investigations & White-Collar Crime Division → lead `/glaw-investigations`
Covers: **Criminal**, fraud investigation, forensic case-building.
| Seat | Skill |
|------|-------|
| FBI/financial-crimes RED→BLUE case build, follow-the-money, RICO/wire fraud/laundering/fraudulent transfer/civil theft, build the indictment | `forensic-case-investigator` |
| Forensic accounting behind the fraud, court-ready numbers, damages | `financial-forensics` (via `/glaw-accounting`) |
| Criminal + civil exposure mapping, FUFTA, fraud on the court | `elite-corporate-counsel` |
| Federal criminal / trial posture | `federal-trial-counsel` |
| Fraudulent-transfer avoidance (§548) | `/glaw-restructuring` |

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
| `.pdf` | `opendataloader-pdf` (layout-faithful) | `<name>.md` |
| email `.eml/.msg/.pst`, Office, images (OCR), HTML, zip, 1000+ types | Apache Tika 3.3.1 (`~/.glaw/tools/tika-app.jar`, Java 21) | `<name>.txt` + `<name>.meta.json` |
`*.meta.json` carries forensic metadata (created/modified dates, author, software) —
used by `elite-corporate-counsel` (altered/backdated instruments) and
`/glaw-evidence-timeline` (precise event dating). Consumers: `/glaw-evidence-timeline`,
`/glaw-court-records`, `/glaw-investigations`, `contract-review`, `financial-forensics`.

## Regulatory, Licensing & Compliance Division
Covers: AML/sanctions, licensing/permits, privacy/data.
| Seat | Skill |
|------|-------|
| OFAC/sanctions, AML/KYC/BSA, FinCEN, MSB/MTL | `/glaw-regulatory-aml` |
| Business/professional/occupational licensing, permits, foreign qualification | `/glaw-licensing` |
| Privacy policy, ToS, DPA, GDPR/CCPA, breach response | `/glaw-privacy-data` |

## Private Client & Cross-Border Division
Covers: estate/trusts, restructuring, immigration, international.
| Seat | Skill |
|------|-------|
| Estate planning, trusts, succession, asset protection | `/glaw-estate-trusts` |
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
| `/review-contract` | Structured inbound-contract review | complements `contract-review` + `/glaw-commercial-contracts` |
| `/brief` | Legal brief generation | feeds/complements `/glaw-motion-drafting` + `/glaw-legal-writing` |
| `/legal-response` | Draft responses to legal letters/demands | NEW — pairs with `elite-corporate-counsel` |
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
| Marketing/website copy | `copywriting`, `copy-editing` |
| Document rendering | `make-pdf`, `docx`, `document-generate` |

---

## Execution layer — `fs-*` financial-services skills (verified 2026-06-04)
GLAW's advice/drafting seats now delegate the **quantitative execution** to the
`fs-*` skills (Anthropic financial-services repo, 52 skills, symlinked under
`~/.claude/skills-repos/financial-services/`). 25 are wired in; all paths resolve.
Stages don't call `fs-*` directly — they call the seat, which hands off:
| Seat | Hands execution to |
|------|--------------------|
| `tax-compliance`, `tax-relief` (IRS) | `fs-gl-recon`, `fs-break-trace` (rebuild ledgers); `fs-xlsx-author`, `fs-audit-xls` (workpapers) |
| `tax-strategy` | `fs-dcf-model`, `fs-lbo-model`, `fs-3-statement-model`, `fs-comps-analysis`, `fs-merger-model`, `fs-tax-loss-harvesting`, `fs-xlsx-author` |
| `corporate-counsel` | `fs-3-statement-model`/`fs-dcf-model`/`fs-comps-analysis`/`fs-merger-model` (financing model); `fs-kyc-doc-parse`/`fs-kyc-rules` (investor KYC); `fs-pptx-author` (deck) |
| `elite-corporate-counsel` | `fs-gl-recon`/`fs-break-trace` (trace funds); `fs-3-statement-model`/`fs-dcf-model` (damages/lost-profits); `fs-xlsx-author`/`fs-audit-xls` (exhibits) |
| `tax-legal-intake` (router) | sequences the full `fs-*` modeling/ledger/KYC/deck execution layer (26 refs) |
So `/glaw-accounting` and `/glaw-structure` get real model/ledger/KYC/deck/workpaper
output through these seats. Advice stays in the custom suite; math/build goes to `fs-*`.

## Domain → division quick index (no gaps)
| You said... | Division / seat |
|-------------|-----------------|
| Corporate | Corporate & Transactional (`/glaw-entity-architect`, `corporate-counsel`, `elite-corporate-counsel`) |
| Financial / Accounting / CFO | Accounting & Finance (`/glaw-accounting`) |
| VC fund / Private Equity / Fund Management | Securities, Funds & Capital Markets (`pe-vc-counsel`, `institutional-finance`) |
| SEC compliance | Securities, Funds & Capital Markets (`fund-regulatory-council`) |
| IRS / Tax | Tax & IRS (`tax-strategy`, `tax-compliance`, `tax-relief`) |
| Criminal / white-collar | Investigations & White-Collar Crime (`/glaw-investigations`) |
| Civil | Litigation & Dispute Resolution (`elite-corporate-counsel`, `federal-trial-counsel`) |
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
