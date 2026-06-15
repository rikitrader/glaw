# Federal Trial Counsel Skill - MANIFEST

## Skill Overview

**Name:** federal-trial-counsel
**Version:** 3.0.0
**Court:** U.S. District Court, Middle District of Florida (Orlando Division)
**Circuit:** Eleventh Circuit Court of Appeals

## File Structure

```
federal-trial-counsel/
├── SKILL.md                           # Main skill definition
├── MANIFEST.md                        # This file
├── README.md                          # Quick-start guide
├── USAGE.md                           # Detailed usage guide (3000+ words, infographics)
├── UNLOCK_INSTRUCTIONS.md             # Encrypted archive unlock guide
│
├── scripts/
│   ├── encrypt.sh                     # Encrypt TS engine into .encrypted/
│   ├── unlock.sh                      # Decrypt TS engine from archive
│   ├── pyproject.toml                 # Python package config (pip install)
│   │
│   ├── ftc_engine/                    # Python CLI engine (19 modules, 20 subcommands)
│   │   ├── __init__.py                # Package init
│   │   ├── __main__.py                # python -m ftc_engine entry point
│   │   ├── cli.py                     # CLI dispatcher (20 subcommands)
│   │   ├── claims.py                  # CLAIM_LIBRARY — 45 federal causes of action
│   │   ├── risk.py                    # MTD risk scoring (standing, SOL, exhaustion, immunity, plausibility, Monell, Rule 9(b), damages)
│   │   ├── sol.py                     # Statute of limitations calculator
│   │   ├── suggest.py                 # Claim auto-suggestion from fact patterns
│   │   ├── drafter.py                 # Complaint drafter (caption, parties, jurisdiction, counts, prayer)
│   │   ├── exporter.py                # .docx exporter (court-formatted: TNR 14pt, double-spaced, 1" margins)
│   │   ├── questions.py               # Post-generation verification questions engine (4 categories)
│   │   ├── wizard.py                  # 12-step interactive case wizard (intake, generation, output format/location)
│   │   ├── case_manager.py            # Persistent case storage, workflow state tracking, document management
│   │   ├── doc_analyzer.py            # Document analyzer: 5-layer pipeline (extract, classify, entities, analyze, route)
│   │   ├── districts.py               # Federal district court configurations (M.D. Fla., S.D.N.Y., D.D.C., etc.)
│   │   ├── deposition.py              # Deposition question outline generator (direct, cross, expert, lay)
│   │   ├── exhibits.py                # Exhibit index generator with authentication notes
│   │   ├── filing_calendar.py         # Case filing calendar and document map generator
│   │   ├── pacer_meta.py              # PACER/ECF filing package generator
│   │   ├── rule11_monitor.py          # Rule 11 duty monitor — claim viability check
│   │   └── sample_case.json           # Example case input
│   │
│   ├── tests/                         # Pytest suite (459 tests, 16 files)
│   │   ├── __init__.py
│   │   ├── conftest.py                # Shared fixtures (sample_case, minimal_case, employment_case, federal_defendant_case)
│   │   ├── test_case_manager.py       # 31 tests — case CRUD, state management, workflow advance, document intake
│   │   ├── test_claims.py             # 25 tests — claim library integrity
│   │   ├── test_deposition.py         # 28 tests — deposition outline generator
│   │   ├── test_districts.py          # 26 tests — district configurations
│   │   ├── test_doc_analyzer.py       # 45 tests — document classification, entity extraction, analysis pipeline
│   │   ├── test_drafter.py            # 23 tests — complaint drafter
│   │   ├── test_exhibits.py           # 35 tests — exhibit index generator
│   │   ├── test_exporter.py           # 21 tests — .docx export (formatting, templates, placeholders)
│   │   ├── test_filing_calendar.py    # 31 tests — filing calendar / document map
│   │   ├── test_pacer_meta.py         # 31 tests — PACER/ECF package generator
│   │   ├── test_questions.py          # 25 tests — post-generation verification questions
│   │   ├── test_risk.py               # 39 tests — MTD risk scoring engine
│   │   ├── test_rule11_monitor.py     # 29 tests — Rule 11 duty monitor
│   │   ├── test_sol.py                # 17 tests — SOL calculator
│   │   ├── test_suggest.py            # 13 tests — claim auto-suggestion
│   │   └── test_wizard.py             # 40 tests — 12-step wizard, document selection, pipeline copy
│   │
│   ├── federal_pleading_engine/       # TypeScript engine (gitignored, distributed via .encrypted/)
│   │   ├── schema.ts                  # Case input schema
│   │   ├── claim_library.ts           # TypeScript claim definitions
│   │   ├── elements.ts                # Claim element definitions
│   │   ├── mapper.ts                  # Fact-to-claim mapping
│   │   ├── risk.ts                    # MTD risk scoring
│   │   ├── drafter.ts                 # Complaint generation
│   │   ├── cli.ts                     # CLI interface
│   │   ├── package.json               # Node.js package
│   │   ├── tsconfig.json              # TypeScript config
│   │   ├── skill.json                 # Module metadata
│   │   ├── README.md                  # Module documentation
│   │   └── examples/
│   │       ├── sample_case_input.json # Example input
│   │       └── sample_output.md       # Example output
│   │
│   └── courtlistener/                 # Case law research module
│       ├── index.ts                   # Main exports
│       ├── client.ts                  # API client with retry/backoff
│       ├── types.ts                   # TypeScript type definitions
│       ├── format.ts                  # Markdown formatting
│       ├── cli.ts                     # Command-line interface
│       ├── skill.json                 # Module metadata
│       ├── README.md                  # Module documentation
│       └── examples.md                # Usage examples
│
├── .encrypted/
│   ├── federal-trial-counsel.enc      # AES-256-CBC encrypted TS engine archive
│   └── federal-trial-counsel.sha256   # SHA-256 checksum
│
├── workflows/
│   └── 00-master-case-analysis.md     # Master case analysis workflow
│
├── references/
│   ├── frcp_summary.md                # Federal Rules of Civil Procedure summary
│   ├── fre_summary.md                 # Federal Rules of Evidence summary
│   ├── mdfl_local_rules.md            # M.D. Fla. Local Rules reference
│   ├── eleventh_circuit_standards.md  # 11th Circuit standards and key cases
│   ├── case_strategy_system.md        # Case strategy framework
│   └── federal_litigation_engines.md  # Litigation engine reference
│
├── modules/
│   ├── board_risk_dashboard.md        # Executive risk briefing templates
│   ├── case_timeline_builder.md       # Litigation timeline generator
│   ├── case_analysis_engine.md        # Comprehensive case analysis (0-100 scoring)
│   ├── strategy_scoring_system.md     # Strategy scorecard with verdict probability
│   └── mandamus_engine.md             # Federal writ of mandamus litigation engine
│
└── assets/
    └── templates/
        ├── pleadings/                     # 6 templates
        │   ├── complaint_federal.md       # Federal complaint (FRCP 8)
        │   ├── amended_complaint.md       # Amended complaint (FRCP 15)
        │   ├── answer_federal.md          # Answer with affirmative defenses
        │   ├── notice_of_removal.md       # Removal to federal court (28 U.S.C. § 1446)
        │   ├── third_party_complaint.md   # Impleader (FRCP 14)
        │   └── counterclaim_crossclaim.md # Counterclaims & crossclaims (FRCP 13)
        │
        ├── motions/                       # 15 templates
        │   ├── motion_to_dismiss.md       # Rule 12(b) motion
        │   ├── opposition_to_mtd.md       # Opposition to MTD (Local Rule 3.01(b))
        │   ├── summary_judgment.md        # Rule 56 motion
        │   ├── opposition_to_sj.md        # Opposition to SJ (Local Rule 3.01(c))
        │   ├── reply_brief.md             # Reply in support (Local Rule 3.01(c))
        │   ├── motion_to_amend.md         # Leave to amend (FRCP 15(a)(2))
        │   ├── motion_for_default_judgment.md  # Default judgment (FRCP 55)
        │   ├── motion_to_remand.md        # Remand to state court (28 U.S.C. § 1447)
        │   ├── motion_for_protective_order.md  # Protective order (FRCP 26(c))
        │   ├── tro_motion.md              # TRO/emergency relief (FRCP 65(b))
        │   ├── preliminary_injunction.md  # Preliminary injunction (FRCP 65(a))
        │   ├── motion_to_compel.md        # Compel discovery (FRCP 37(a))
        │   ├── motion_for_sanctions.md    # Sanctions (Rule 11/37/§1927)
        │   ├── motions_in_limine.md       # Pre-trial evidentiary motions
        │   └── post_trial_motions.md      # JMOL, new trial, alter judgment
        │
        ├── discovery/                     # 8 templates
        │   ├── initial_disclosures.md         # Rule 26(a)(1) disclosures
        │   ├── interrogatories_first_set.md   # Rule 33 interrogatories
        │   ├── requests_for_production.md     # Rule 34 document requests
        │   ├── requests_for_admission.md      # Rule 36 RFAs
        │   ├── deposition_notice.md           # Rule 30 deposition notices
        │   ├── subpoena_third_party.md        # Rule 45 subpoenas
        │   ├── expert_disclosure.md           # Rule 26(a)(2) expert disclosures
        │   └── discovery_response_template.md # Response templates & objections
        │
        ├── orders/                        # 8 templates
        │   ├── proposed_order_mtd.md          # Order on Motion to Dismiss
        │   ├── proposed_order_sj.md           # Order on Summary Judgment
        │   ├── proposed_order_tro.md          # Temporary Restraining Order
        │   ├── proposed_order_pi.md           # Preliminary Injunction Order
        │   ├── proposed_order_compel.md       # Order on Motion to Compel
        │   ├── proposed_order_sanctions.md    # Order on Sanctions
        │   ├── proposed_order_scheduling.md   # Case Management & Scheduling Order
        │   └── proposed_order_consent.md      # Stipulated/Consent Order
        │
        ├── appellate/                     # 2 templates
        │   ├── notice_of_appeal.md            # Notice of Appeal (FRAP 3/4)
        │   └── appellate_brief.md             # 11th Circuit Appellate Brief (FRAP 28)
        │
        └── workflows/                     # 3 templates
            ├── case_intake_workflow.md        # Initial case assessment
            ├── trial_preparation_workflow.md  # 90-day trial prep checklist
            └── appeal_workflow.md             # Post-judgment appeal process
```

## Statistics

| Category | Count |
|----------|-------|
| **Templates** | **42 total** |
| Pleadings | 6 |
| Motions | 15 |
| Discovery | 8 |
| Orders | 8 |
| Appellate | 2 |
| Workflows | 3 |
| **Python CLI Engine** | |
| Modules | 19 |
| CLI Subcommands | 20 |
| Lines of Code | 8,300 |
| **Engines** | **2** |
| Python CLI (ftc_engine) | 19 modules, 20 subcommands, 45 claims |
| TypeScript (federal_pleading_engine) | 12 files (encrypted) |
| **Tests** | **459** (16 test files) |
| **Litigation Intelligence Modules** | 5 |
| **Legal References** | 6 |

## Test Suite Breakdown

| File | Tests | Coverage Area |
|------|-------|---------------|
| `test_case_manager.py` | 31 | Case CRUD, state management, workflow advance, document intake |
| `test_claims.py` | 25 | Claim library integrity, categories, elements |
| `test_deposition.py` | 28 | Deposition outline generator (direct, cross, expert) |
| `test_districts.py` | 26 | District configurations, local rules |
| `test_doc_analyzer.py` | 45 | Document classification, entity extraction, analysis pipeline |
| `test_drafter.py` | 23 | Complaint drafter (caption, counts, prayer) |
| `test_exhibits.py` | 35 | Exhibit index generator, authentication |
| `test_exporter.py` | 21 | .docx export formatting, templates, placeholders |
| `test_filing_calendar.py` | 31 | Filing calendar, document map |
| `test_pacer_meta.py` | 31 | PACER/ECF package generator |
| `test_questions.py` | 25 | Post-generation verification questions |
| `test_risk.py` | 39 | MTD risk scoring (all 8 categories) |
| `test_rule11_monitor.py` | 29 | Rule 11 duty monitor, viability checks |
| `test_sol.py` | 17 | Statute of limitations calculator |
| `test_suggest.py` | 13 | Claim auto-suggestion engine |
| `test_wizard.py` | 40 | 12-step wizard, document selection, pipeline copy |
| **Total** | **459** | |

## File Descriptions

### Core Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Main skill definition with FRCP/FRE expertise, jurisdiction analysis, and procedural guidance |
| `MANIFEST.md` | Index of all files and their procedural purposes |
| `README.md` | Quick-start guide with feature overview |
| `USAGE.md` | Detailed usage guide (3000+ words) with ASCII infographics |
| `UNLOCK_INSTRUCTIONS.md` | How to decrypt the TypeScript engine |

### Python CLI Engine (ftc_engine/) — 19 Modules

| File | Purpose |
|------|---------|
| `cli.py` | CLI dispatcher — 20 subcommands: analyze, suggest, risk, sol, draft, claims, export, info, district, deposition, exhibits, pacer, monitor, calendar, new, open, cases, analyze-docs, setup, doctor |
| `claims.py` | CLAIM_LIBRARY — 45 federal causes of action across 9 categories with elements, defenses, SOL, exhaustion |
| `risk.py` | MTD risk scoring — standing, SOL, exhaustion, immunity, plausibility, Monell, Rule 9(b), damages |
| `sol.py` | Statute of limitations calculator with tolling notes and status tracking |
| `suggest.py` | Claim auto-suggestion engine — pattern-matches facts to federal claims |
| `drafter.py` | Complaint drafter — generates caption, parties, jurisdiction, venue, factual allegations, counts, prayer |
| `exporter.py` | .docx exporter — court-formatted (Times New Roman 14pt, double-spaced, 1" margins) |
| `questions.py` | Post-generation verification questions engine (pre-filing, strategic, client, procedural) |
| `wizard.py` | 12-step interactive case wizard — guided intake, document selection, output format/location |
| `case_manager.py` | Persistent case storage at ~/.ftc/cases/ — workflow state, document intake, output management |
| `doc_analyzer.py` | Document analyzer — 5-layer pipeline: text extraction, classification, entity extraction, analysis, workflow routing |
| `districts.py` | Federal district court configurations (M.D. Fla., S.D.N.Y., D.D.C., E.D. Va., N.D. Ill.) |
| `deposition.py` | Deposition question outline generator — direct, cross, expert, and lay witness |
| `exhibits.py` | Exhibit index generator with authentication notes and document type classification |
| `filing_calendar.py` | Case filing calendar and document map generator with FRCP deadlines |
| `pacer_meta.py` | PACER/ECF filing package generator with CM/ECF compliance |
| `rule11_monitor.py` | Rule 11 duty monitor — ongoing claim viability assessment |
| `sample_case.json` | Example case input for testing and demonstration |

### Test Suite (tests/) — 459 Tests

| File | Tests | Coverage |
|------|-------|----------|
| `test_case_manager.py` | 31 | case_manager.py |
| `test_claims.py` | 25 | claims.py: 100% |
| `test_deposition.py` | 28 | deposition.py |
| `test_districts.py` | 26 | districts.py |
| `test_doc_analyzer.py` | 45 | doc_analyzer.py |
| `test_drafter.py` | 23 | drafter.py |
| `test_exhibits.py` | 35 | exhibits.py |
| `test_exporter.py` | 21 | exporter.py |
| `test_filing_calendar.py` | 31 | filing_calendar.py |
| `test_pacer_meta.py` | 31 | pacer_meta.py |
| `test_questions.py` | 25 | questions.py |
| `test_risk.py` | 39 | risk.py |
| `test_rule11_monitor.py` | 29 | rule11_monitor.py |
| `test_sol.py` | 17 | sol.py |
| `test_suggest.py` | 13 | suggest.py |
| `test_wizard.py` | 40 | wizard.py |
| **Total** | **459** | |

### TypeScript Engine (federal_pleading_engine/)

Distributed via encrypted archive (`.encrypted/federal-trial-counsel.enc`). Decrypt with `scripts/unlock.sh`.

| File | Purpose |
|------|---------|
| `schema.ts` | Case input schema with TypeScript types |
| `claim_library.ts` | 45 federal claim definitions |
| `elements.ts` | Claim element definitions for Twombly/Iqbal analysis |
| `mapper.ts` | Fact pattern to claim mapping |
| `risk.ts` | MTD risk scoring engine |
| `drafter.ts` | Full complaint generation |
| `cli.ts` | Command-line interface |

### CourtListener Research Module

| File | Purpose |
|------|---------|
| `scripts/courtlistener/index.ts` | Main entry point — `searchCourtListener()` function |
| `scripts/courtlistener/client.ts` | HTTP client with authentication, retry/backoff, pagination |
| `scripts/courtlistener/types.ts` | TypeScript interfaces for input/output |
| `scripts/courtlistener/format.ts` | Markdown formatting for search results |
| `scripts/courtlistener/cli.ts` | Command-line interface for manual searches |
| `scripts/courtlistener/skill.json` | Module metadata and configuration |
| `scripts/courtlistener/README.md` | Module documentation |
| `scripts/courtlistener/examples.md` | Research scenario examples |

### References

| File | Purpose |
|------|---------|
| `references/frcp_summary.md` | Federal Rules of Civil Procedure reference |
| `references/fre_summary.md` | Federal Rules of Evidence reference |
| `references/mdfl_local_rules.md` | M.D. Fla. Local Rules reference |
| `references/eleventh_circuit_standards.md` | 11th Circuit standards and key cases |
| `references/case_strategy_system.md` | Case strategy framework |
| `references/federal_litigation_engines.md` | Litigation engine reference |

### Litigation Intelligence Modules

| File | Purpose | Output |
|------|---------|--------|
| `modules/board_risk_dashboard.md` | Executive-level legal risk assessment | Board briefing (.md) |
| `modules/case_timeline_builder.md` | Automatic case chronology and deadline tracking | Timeline (.md) |
| `modules/case_analysis_engine.md` | Comprehensive case strength analysis with 0-100 scoring | Full analysis report (.md) |
| `modules/strategy_scoring_system.md` | Litigation strategy scorecard with verdict probability | Strategy scorecard (.md) |
| `modules/mandamus_engine.md` | Federal writ of mandamus litigation builder (28 U.S.C. § 1361) | Complete mandamus case workspace |

### Pleading Templates

| File | Rule | Purpose |
|------|------|---------|
| `complaint_federal.md` | FRCP 8 | Federal civil complaint with Twombly/Iqbal guidance |
| `amended_complaint.md` | FRCP 15 | Amended complaint (as of right or by leave) |
| `answer_federal.md` | FRCP 8(b), 12 | Answer with affirmative defenses and counterclaims |
| `notice_of_removal.md` | 28 U.S.C. § 1446 | Removal from state to federal court |
| `third_party_complaint.md` | FRCP 14 | Third-party complaint (impleader) |
| `counterclaim_crossclaim.md` | FRCP 13 | Compulsory/permissive counterclaims and crossclaims |

### Motion Templates

| File | Rule | Purpose |
|------|------|---------|
| `motion_to_dismiss.md` | FRCP 12(b) | Motion to dismiss (12(b)(1), 12(b)(6)) |
| `opposition_to_mtd.md` | Local Rule 3.01(b) | Response in opposition to motion to dismiss |
| `summary_judgment.md` | FRCP 56 | Summary judgment with Local Rule 3.01(c) |
| `opposition_to_sj.md` | Local Rule 3.01(c) | Response in opposition to summary judgment |
| `reply_brief.md` | Local Rule 3.01(c) | Reply brief in support of any motion |
| `motion_to_amend.md` | FRCP 15(a)(2) | Motion for leave to file amended complaint |
| `motion_for_default_judgment.md` | FRCP 55 | Default judgment after clerk's entry of default |
| `motion_to_remand.md` | 28 U.S.C. § 1447 | Remand improperly removed case to state court |
| `motion_for_protective_order.md` | FRCP 26(c) | Protective order for discovery disputes |
| `tro_motion.md` | FRCP 65(b) | Emergency TRO with Winter factors |
| `preliminary_injunction.md` | FRCP 65(a) | Preliminary injunction with evidentiary hearing |
| `motion_to_compel.md` | FRCP 37(a) | Compel discovery with meet-and-confer |
| `motion_for_sanctions.md` | Rule 11/37/§1927 | Sanctions for misconduct |
| `motions_in_limine.md` | FRE 104, 401-403 | Pre-trial evidentiary exclusions |
| `post_trial_motions.md` | FRCP 50, 59 | JMOL, new trial, alter judgment |

### Discovery Templates

| File | Rule | Purpose |
|------|------|---------|
| `initial_disclosures.md` | FRCP 26(a)(1) | Mandatory initial disclosures |
| `interrogatories_first_set.md` | FRCP 33 | 25 interrogatories with verification |
| `requests_for_production.md` | FRCP 34 | 30 RFPs with ESI protocol |
| `requests_for_admission.md` | FRCP 36 | 30 RFAs with strategic guidance |
| `deposition_notice.md` | FRCP 30 | Individual and 30(b)(6) corporate notices |
| `subpoena_third_party.md` | FRCP 45 | Third-party subpoenas (banks, carriers, social media) |
| `expert_disclosure.md` | FRCP 26(a)(2) | Retained and non-retained expert disclosures |
| `discovery_response_template.md` | FRCP 33, 34, 36 | Response templates with common objections |

### Order Templates

| File | Motion | Purpose |
|------|--------|---------|
| `proposed_order_mtd.md` | Rule 12(b) | Proposed order on motion to dismiss |
| `proposed_order_sj.md` | Rule 56 | Proposed order on summary judgment |
| `proposed_order_tro.md` | Rule 65(b) | Temporary restraining order |
| `proposed_order_pi.md` | Rule 65(a) | Preliminary injunction order |
| `proposed_order_compel.md` | Rule 37(a) | Order on motion to compel discovery |
| `proposed_order_sanctions.md` | Rule 11/37/§1927 | Order on motion for sanctions |
| `proposed_order_scheduling.md` | Rule 16(b) | Case management and scheduling order |
| `proposed_order_consent.md` | Rule 29 | Stipulated/consent order |

### Appellate Templates

| File | Rule | Purpose |
|------|------|---------|
| `notice_of_appeal.md` | FRAP 3, 4 | Notice of appeal (30/60-day deadline) |
| `appellate_brief.md` | FRAP 28, 32 | Full appellate brief for 11th Circuit |

### Workflow Templates

| File | Phase | Purpose |
|------|-------|---------|
| `case_intake_workflow.md` | Pre-litigation | 7-phase intake with jurisdiction analysis |
| `trial_preparation_workflow.md` | Pre-trial | 90-day trial prep with trial notebook |
| `appeal_workflow.md` | Post-judgment | 11th Circuit appeal process |

## Capabilities

### Case Management (NEW in v3.0.0)
- 12-step interactive case wizard (new/open/resume)
- Persistent case storage at `~/.ftc/cases/`
- Workflow state tracking with progress visualization
- Document intake and import
- Output format selection (Markdown, Word .docx)
- Save location selection (Desktop, Documents, custom path)
- Auto-copy generated files to chosen location

### Document Analysis (NEW in v3.0.0)
- PDF text extraction (PyPDF2)
- DOCX text extraction (python-docx)
- TXT/MD text extraction
- 18-category legal document classification
- Entity extraction: parties, dates, case numbers, claims, courts
- Workflow routing based on document types
- Auto-populate case data from analyzed documents

### Document Generation
- Federal complaints (diversity, federal question, CAFA)
- Amended complaints with relation back analysis
- Answers with affirmative defenses
- Counterclaims and crossclaims
- Third-party complaints (impleader)
- Removal notices with jurisdiction analysis
- Remand motions
- TRO/preliminary injunction motions (Winter factors)
- Motions to dismiss (12(b)(1), 12(b)(6))
- Opposition briefs to MTD and SJ
- Reply briefs
- Summary judgment motions
- Motion to amend / leave to amend
- Default judgment motions
- Motions to compel discovery
- Protective orders
- Sanctions motions (Rule 11, 37, § 1927)
- Motions in limine (7 categories)
- Post-trial motions (JMOL, new trial)
- Complete discovery packages
- Proposed orders for all motions
- Case management and scheduling orders
- Stipulated/consent orders
- Notice of appeal
- Appellate briefs (11th Circuit)

### Legal Research
- CourtListener API integration for case law
- Middle District of Florida precedent
- Eleventh Circuit controlling authority
- Supreme Court foundational cases

### Case Analysis & Strategy
- **Case Analysis Engine**: Comprehensive 0-100 scoring
  - Jurisdiction strength (10%)
  - Claims/defenses viability (25%)
  - Evidence quality (20%)
  - Damages/exposure (15%)
  - Procedural posture (10%)
  - Settlement factors (10%)
  - Trial factors (10%)
- **Strategy Scoring System**: Verdict probability modeling
- **Risk Dashboard**: Board-level risk assessment
- **Timeline Builder**: Automatic chronology generation
- **Mandamus Engine**: Complete mandamus case builder
  - Three-element test analysis
  - TRAC factors for unreasonable delay
  - Viability scoring (0-100)
  - Defense preemption analysis
  - Full pleading generation

### Python CLI Engine — 20 Commands
- `ftc analyze` — Full case analysis with scoring
- `ftc suggest` — Auto-suggest claims from facts
- `ftc risk` — MTD risk scoring for specific claims
- `ftc sol` — Statute of limitations calculations
- `ftc draft` — Generate complaint draft
- `ftc claims` — Browse 45 federal causes of action
- `ftc export` — Export to .docx (court-formatted)
- `ftc info` — Claim details with elements and defenses
- `ftc district` — Manage district configuration
- `ftc deposition` — Generate deposition question outline
- `ftc exhibits` — Generate exhibit index
- `ftc pacer` — Generate PACER/ECF filing package
- `ftc monitor` — Rule 11 duty monitor
- `ftc calendar` — Generate case filing calendar
- `ftc new` — Interactive 12-step case wizard
- `ftc open` — Open/resume existing case
- `ftc cases` — List all saved cases
- `ftc analyze-docs` — Analyze intake documents
- `ftc setup` — Auto-install dependencies
- `ftc doctor` — Diagnostic health check

### Expertise Areas
- Federal jurisdiction (diversity, federal question, supplemental)
- Removal and remand
- Emergency injunction practice (TRO, PI)
- **Mandamus practice (28 U.S.C. § 1361, All Writs Act)**
- Discovery procedure and disputes
- Expert witness practice (Daubert)
- Motions practice (offensive and defensive)
- Default judgment practice
- Amendment practice (Rule 15)
- Protective orders
- Class action defense
- White-collar defense
- Regulatory enforcement
- Administrative law and agency inaction
- Appeals (11th Circuit)

## Usage

### Invoke the Skill

```
/federal-trial-counsel
```

### Python CLI

```bash
cd scripts
pip install -e .
ftc new                                    # Interactive case wizard
ftc suggest --case sample_case.json        # Auto-suggest claims
ftc risk --case sample_case.json --claim 1983_fourth_excessive_force
ftc sol --claim 1983_fourth_excessive_force --date 2025-06-15
ftc draft --case sample_case.json --out complaint.md
ftc analyze-docs CASE-ID                   # Analyze intake documents
```

### Run Tests

```bash
cd scripts
pip install pytest pytest-cov
pytest                           # 459 tests
pytest --cov --cov-report=term   # with coverage
pytest -v --tb=short             # verbose mode
```

### CourtListener Search (CLI)

```bash
cd scripts/courtlistener
npx ts-node cli.ts --q "preliminary injunction" --court flmd --after 2023-01-01
```

### Example Commands

```
"Draft a TRO motion to stop defendant from [conduct]"
"Analyze whether this case can be removed to federal court"
"Search for qualified immunity cases in the Middle District of Florida"
"Generate a board-level risk assessment for this matter"
"Create a case timeline from these documents"
"Analyze my case and provide a full strategy report"
"Draft interrogatories for a breach of contract case"
"Prepare a motion for sanctions under Rule 11"
"Build Mandamus Case: [case name]"
"Draft an opposition to defendant's motion to dismiss"
"File an amended complaint adding new claims"
"Draft a motion to remand to state court"
"Prepare a notice of appeal"
```

## Dependencies

| Component | Requirements |
|-----------|-------------|
| Python CLI (ftc_engine) | Python 3.10+ |
| TypeScript Engine | Node.js 18+, TypeScript |
| CourtListener Module | Node.js 18+ (native fetch) |
| Tests | pytest, pytest-cov |
| PDF Analysis | PyPDF2 >= 3.0.0 |
| DOCX Export | python-docx >= 1.0.0 |

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `COURTLISTENER_API_TOKEN` | API token for higher rate limits | Optional |

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025 | Initial release |
| 1.1.0 | 2026 | Complete template library, case analysis engine, strategy scoring |
| 1.2.0 | 2026 | Federal Writ of Mandamus Engine (28 U.S.C. § 1361, All Writs Act) |
| 2.0.0 | 2026 | Python CLI engine (45 claims, 8 modules), 42 templates, 117 tests (95% coverage), appellate templates, proposed orders, opposition briefs |
| 3.0.0 | 2026 | Interactive wizard, document analyzer, case management, 19 modules, 20 CLI commands, 459 tests, output format/location selection, USAGE.md |

---

*This skill is designed for the U.S. District Court, Middle District of Florida. Adapt templates for other districts as needed.*
