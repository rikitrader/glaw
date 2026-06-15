# Federal Trial Counsel

```
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║     ███████ ███████ ██████  ███████ ██████   █████  ██                   ║
    ║     ██      ██      ██   ██ ██      ██   ██ ██   ██ ██                   ║
    ║     █████   █████   ██   ██ █████   ██████  ███████ ██                   ║
    ║     ██      ██      ██   ██ ██      ██   ██ ██   ██ ██                   ║
    ║     ██      ███████ ██████  ███████ ██   ██ ██   ██ ███████             ║
    ║                                                                          ║
    ║     ████████ ██████  ██  █████  ██                                       ║
    ║        ██    ██   ██ ██ ██   ██ ██                                       ║
    ║        ██    ██████  ██ ███████ ██                                       ║
    ║        ██    ██   ██ ██ ██   ██ ██                                       ║
    ║        ██    ██   ██ ██ ██   ██ ███████                                  ║
    ║                                                                          ║
    ║      ██████  ██████  ██    ██ ███    ██ ███████ ███████ ██              ║
    ║     ██      ██    ██ ██    ██ ████   ██ ██      ██      ██              ║
    ║     ██      ██    ██ ██    ██ ██ ██  ██ ███████ █████   ██              ║
    ║     ██      ██    ██ ██    ██ ██  ██ ██      ██ ██      ██              ║
    ║      ██████  ██████   ██████  ██   ████ ███████ ███████ ███████         ║
    ║                                                                          ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║              U.S. DISTRICT COURT SPECIALIST  v3.0.0                      ║
    ║                                                                          ║
    ║          Middle District of Florida  *  11th Circuit  *  FRCP            ║
    ║                                                                          ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           ║
    ║    │  45 FEDERAL    │  │ 12-STEP CASE   │  │  DOCUMENT      │           ║
    ║    │    CLAIMS      │  │   WIZARD       │  │  ANALYZER      │           ║
    ║    │                │  │                │  │                │           ║
    ║    │  § 1983, FTCA  │  │  Interactive   │  │  PDF/DOCX/TXT  │           ║
    ║    │  Title VII     │  │  Case Intake   │  │  Auto-Classify │           ║
    ║    │  RICO, APA     │  │  + Generation  │  │  + Extract     │           ║
    ║    └────────────────┘  └────────────────┘  └────────────────┘           ║
    ║                                                                          ║
    ║    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           ║
    ║    │  TWOMBLY /     │  │  20 CLI        │  │ 19 LITIGATION  │           ║
    ║    │   IQBAL        │  │  COMMANDS      │  │    ENGINES     │           ║
    ║    │                │  │                │  │                │           ║
    ║    │  Plausibility  │  │  draft, risk   │  │  Full Case     │           ║
    ║    │  Compliant     │  │  suggest, new  │  │  Management    │           ║
    ║    │  Pleadings     │  │  analyze-docs  │  │  Strategies    │           ║
    ║    └────────────────┘  └────────────────┘  └────────────────┘           ║
    ║                                                                          ║
    ║       459 TESTS  *  19 MODULES  *  8,300 LOC  *  42 TEMPLATES           ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
```

**Elite AI Legal Co-Counsel for U.S. District Courts**

---

## PASSWORD PROTECTED

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   THIS REPOSITORY CONTAINS ENCRYPTED SKILL FILES                             │
│                                                                              │
│   To unlock and install:                                                     │
│                                                                              │
│       $ git clone https://github.com/rikitrader/federal-trial-counsel.git   │
│       $ cd federal-trial-counsel                                             │
│       $ ./scripts/unlock.sh                                                  │
│       Enter password: ********                                               │
│                                                                              │
│   Contact repository owner for access credentials                            │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Overview

This Claude Code skill transforms Claude into a senior federal trial attorney with deep expertise in federal civil litigation, from complaint drafting through appeal. It includes:

- **45 Federal Causes of Action** with element-by-element analysis
- **12-Step Interactive Case Wizard** for guided case intake and document generation
- **Document Analyzer** — PDF/DOCX/TXT parsing, classification, entity extraction, workflow routing
- **19 Litigation Strategy Engines** for complete case management
- **Persistent Case Management** with workflow state tracking
- **Twombly/Iqbal Compliant** pleading generation
- **MTD Risk Scoring** (0-100) with vulnerability fixes
- **Auto-Trigger Workflow** for seamless case analysis
- **20 CLI Commands** for every stage of federal litigation

## Installation

### As Claude Code Skill

1. Copy this directory to `~/.claude/skills/federal-trial-counsel/`
2. The skill auto-activates when federal litigation topics are detected

### Python CLI Engine (Primary)

```bash
cd scripts
pip install -e .
ftc doctor    # Verify installation
ftc setup     # Auto-install all dependencies
```

### TypeScript Pleading Engine (Optional)

```bash
cd scripts/federal_pleading_engine
npm install
npm run build
```

## Features

### Interactive Case Wizard (NEW in v3.0.0)

The 12-step wizard guides you through complete case intake and document generation:

```
    ┌─────────────────────────────────────────────────────────────┐
    │                    12-STEP CASE WIZARD                       │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │   1. Court & Jurisdiction                                   │
    │   2. Plaintiff Information                                  │
    │   3. Defendant Information                                  │
    │   4. Factual Allegations                                    │
    │   5. Claims Selection                                       │
    │   6. Relief Requested                                       │
    │   7. Administrative Exhaustion                              │
    │   8. Statute of Limitations                                 │
    │   9. Case Goals                                             │
    │  10. Case Summary Review                                    │
    │  11. Document Selection + Output Format + Save Location     │
    │  12. Generate Documents                                     │
    │                                                             │
    │   Features:                                                 │
    │   * Save/resume at any step                                │
    │   * Auto-populates from imported documents                 │
    │   * Outputs: Markdown, Word (.docx), or both               │
    │   * Saves to Desktop, Documents, or custom path            │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

```bash
ftc new           # Start new case wizard
ftc open CASE-ID  # Resume existing case
ftc cases         # List all saved cases
```

### Document Analyzer (NEW in v3.0.0)

Analyze intake documents automatically:

```
    ┌─────────────────────────────────────────────────────────────┐
    │                 DOCUMENT ANALYZER PIPELINE                   │
    ├─────────────────────────────────────────────────────────────┤
    │                                                             │
    │   Layer 1: TEXT EXTRACTION                                  │
    │   PDF (PyPDF2) | DOCX (python-docx) | TXT | MD             │
    │                         |                                   │
    │   Layer 2: CLASSIFICATION                                   │
    │   18 legal document categories + keyword scoring            │
    │                         |                                   │
    │   Layer 3: ENTITY EXTRACTION                                │
    │   Parties | Dates | Case Numbers | Claims | Courts          │
    │                         |                                   │
    │   Layer 4: ANALYSIS                                         │
    │   Per-document report + batch aggregation                   │
    │                         |                                   │
    │   Layer 5: WORKFLOW ROUTING                                  │
    │   complaint_defense | motion_response | discovery_response  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

```bash
ftc analyze-docs CASE-ID   # Analyze all intake documents
```

### Federal Pleading Engine

Location: `scripts/federal_pleading_engine/`

The engine generates Rule 12(b)(6)-resilient federal complaints with:

| Feature | Description |
|---------|-------------|
| **Elements Analysis** | Maps facts to required legal elements for each claim |
| **Plausibility Hardening** | Ensures Twombly/Iqbal compliance |
| **Rule 9(b) Detection** | Heightened pleading for fraud-based claims |
| **MTD Risk Scoring** | 0-100 vulnerability assessment with fixes |
| **Defense Anticipation** | Immunity, exhaustion, SOL analysis |
| **Fact Gap Detection** | Missing allegations identified |
| **Auto-Suggest** | Recommends claims based on facts |

#### Supported Claims (45)

**Constitutional / Civil Rights (§ 1983)**
- `1983_first_amendment_retaliation`
- `1983_first_amendment_speech_restriction`
- `1983_fourth_false_arrest`
- `1983_fourth_unlawful_search_seizure`
- `1983_fourth_excessive_force`
- `1983_fourteenth_procedural_due_process`
- `1983_fourteenth_substantive_due_process`
- `1983_fourteenth_equal_protection`
- `1983_monell_municipal_liability`
- `1985_conspiracy`
- `1986_failure_to_prevent`

**Bivens Claims (Federal Actors)**
- `bivens_fourth_search_seizure`
- `bivens_fifth_due_process`
- `bivens_eighth_deliberate_indifference`

**Administrative / APA**
- `apa_arbitrary_capricious`
- `apa_unlawful_withholding_unreasonable_delay`
- `mandamus_compel_ministerial_duty`
- `habeas_detention_challenge`

**Employment**
- `title_vii_disparate_treatment`
- `title_vii_hostile_work_environment`
- `title_vii_retaliation`
- `adea_age_discrimination`
- `ada_title_i_employment_disability`
- `fmla_interference`
- `fmla_retaliation`
- `flsa_unpaid_wages_overtime`

**FTCA (Federal Tort Claims)**
- `ftca_negligence`
- `ftca_medical_malpractice`
- `ftca_wrongful_death`

**Financial / Consumer**
- `fcra_inaccurate_reporting`
- `fdcpa_prohibited_practices`
- `tila_disclosure_violations`

**Commercial / RICO / Antitrust / IP**
- `false_claims_act_qui_tam`
- `rico_1962c`
- `rico_1962d_conspiracy`
- `antitrust_sherman_section_1`
- `antitrust_sherman_section_2`
- `lanham_trademark_infringement`
- `copyright_infringement`
- `patent_infringement`

**ERISA**
- `erisa_502a1b_benefits`
- `erisa_502a3_equitable_relief`

**Tax**
- `tax_refund_suit`
- `tax_wrongful_levy`

### Python CLI — 20 Commands

```bash
# Case Management
ftc new                              # Interactive 12-step case wizard
ftc open CASE-ID                     # Resume existing case
ftc cases                            # List all saved cases

# Analysis & Research
ftc analyze --case case.json         # Full case analysis with scoring
ftc suggest --case case.json         # Auto-suggest claims from facts
ftc risk --case case.json --claim X  # MTD risk scoring for specific claim
ftc sol --claim X --date 2025-06-15  # Statute of limitations calculator
ftc analyze-docs CASE-ID             # Analyze intake documents

# Document Generation
ftc draft --case case.json --out .   # Generate complaint draft
ftc export --input doc.md --out .    # Export to .docx (court-formatted)

# Reference & Info
ftc claims                           # Browse 45 federal causes of action
ftc info CLAIM_KEY                   # Claim details with elements/defenses
ftc district                         # Manage district configuration
ftc deposition WITNESS_TYPE          # Generate deposition question outline
ftc exhibits --case case.json        # Generate exhibit index
ftc pacer --case case.json           # Generate PACER/ECF filing package
ftc monitor --case case.json         # Rule 11 duty monitor
ftc calendar --case case.json        # Generate case filing calendar

# System
ftc setup                            # Auto-install dependencies
ftc doctor                           # Diagnostic health check
```

### 19 Litigation Strategy Engines

Location: `references/federal_litigation_engines.md`

| # | Engine | Purpose |
|---|--------|---------|
| 1 | **Defense Matrix** | Identify all Rule 12(b) and substantive defenses with counter-strategies |
| 2 | **Jurisdictional Trap Detector** | Standing, exhaustion, abstention, removal defects |
| 3 | **Complaint Structure Generator** | Rule 8 compliant pleading templates |
| 4 | **MTD Counter-Strike** | Strategies to defeat motions to dismiss |
| 5 | **Case Survival Probability** | Weighted outcome modeling (MTD/SJ/Trial %) |
| 6 | **Judge Risk Model** | Judicial tendencies and strategy adaptation |
| 7 | **Discovery Strategy** | Phase planning, ESI, depositions, expert strategy |
| 8 | **Summary Judgment Builder** | SUMF, element analysis, burden shifting |
| 9 | **Trial Strategy** | Theme, witnesses, exhibits, jury psychology |
| 10 | **Appellate Strategy** | Preservation audit, standards of review, brief structure |
| 11 | **Settlement Optimization** | Case valuation, timing, negotiation psychology |
| 12 | **Jury Persuasion** | Narrative framing, cognitive bias leverage |
| 13 | **Damages Modeling** | Economic/non-economic quantification |
| 14 | **Evidence Credibility** | Admissibility, authentication, Daubert analysis |
| 15 | **Pretrial Motions** | MIL, Daubert, procedural motion strategy |
| 16 | **Sanctions Analyzer** | Spoliation exposure, Rule 37(e), ethical issues |
| 17 | **Jury Instruction Builder** | Elements instructions, verdict forms |
| 18 | **Judge Behavior Profiler** | Detailed judicial tendency profiles |
| 19 | **Voir Dire Strategy** | Jury selection, bias detection, strike strategy |

### 8-Phase Master Workflow

The skill automatically executes this workflow when federal cases are detected:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FEDERAL MASTER CASE WORKFLOW                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  PHASE 1: INTAKE & CLASSIFICATION                                   │
│  ├── Federal case questionnaire / Interactive wizard               │
│  ├── A/B/C System classification                                    │
│  ├── Jurisdiction analysis (diversity/federal question)            │
│  └── Document Analyzer: Auto-classify intake docs                  │
│                                                                     │
│  PHASE 2: STATUS DETERMINATION                                      │
│  ├── FRCP timeline analysis                                         │
│  ├── Deadline calculation (21-day answer, 90-day service)          │
│  └── Rule 26(f) conference scheduling                              │
│                                                                     │
│  PHASE 3: DOCUMENT ANALYSIS (existing cases)                        │
│  ├── Pleadings review (Twombly/Iqbal compliance)                   │
│  ├── Discovery status (Rule 26 disclosures)                        │
│  └── Federal Pleading Engine: MTD risk assessment                  │
│                                                                     │
│  PHASE 4: LEGAL RESEARCH                                            │
│  ├── 11th Circuit precedent research                               │
│  ├── Supreme Court controlling authority                           │
│  └── CourtListener integration                                      │
│                                                                     │
│  PHASE 5: STRATEGIC BLUEPRINT GENERATION (.bd)                      │
│  ├── Litigation Engines: Full case analysis                        │
│  ├── Timeline & cost estimates                                     │
│  ├── Judge profile and risk adjustments                            │
│  └── Settlement valuation                                           │
│                                                                     │
│  PHASE 6: DOCUMENT DRAFTING QUEUE                                   │
│  ├── Federal Pleading Engine: Generate complaints                  │
│  ├── Priority-ranked document generation                           │
│  └── Element-by-element drafting                                   │
│                                                                     │
│  PHASE 7: QUALITY CONTROL & FILING                                  │
│  ├── FRCP/FRE citation verification                                │
│  ├── M.D. Fla. Local Rules compliance                              │
│  └── CM/ECF formatting check                                        │
│                                                                     │
│  PHASE 8: POST-GENERATION VERIFICATION                              │
│  ├── Pre-filing verification (Rule 11, formatting)                 │
│  ├── Strategic follow-ups (alternative claims, defenses)           │
│  ├── Client communication (timeline, risks)                        │
│  └── Procedural next steps (deadlines, CM/ECF export)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
federal-trial-counsel/
├── SKILL.md                          # Main skill definition
├── README.md                         # This documentation
├── MANIFEST.md                       # File index
├── USAGE.md                          # Detailed usage guide (3000+ words)
│
├── scripts/
│   ├── pyproject.toml                # Python package config
│   │
│   ├── ftc_engine/                   # Python CLI engine (19 modules, 20 commands)
│   │   ├── __init__.py               # Package init
│   │   ├── __main__.py               # python -m ftc_engine entry point
│   │   ├── cli.py                    # CLI dispatcher (20 subcommands)
│   │   ├── claims.py                 # CLAIM_LIBRARY — 45 federal causes of action
│   │   ├── risk.py                   # MTD risk scoring engine
│   │   ├── sol.py                    # Statute of limitations calculator
│   │   ├── suggest.py                # Claim auto-suggestion from fact patterns
│   │   ├── drafter.py                # Complaint drafter (caption, parties, counts, prayer)
│   │   ├── exporter.py               # .docx exporter (court-formatted: TNR 14pt)
│   │   ├── questions.py              # Post-generation verification questions
│   │   ├── wizard.py                 # 12-step interactive case wizard
│   │   ├── case_manager.py           # Persistent case storage & workflow state
│   │   ├── doc_analyzer.py           # Document analyzer (5-layer pipeline)
│   │   ├── districts.py              # Federal district court configurations
│   │   ├── deposition.py             # Deposition question outline generator
│   │   ├── exhibits.py               # Exhibit index generator
│   │   ├── filing_calendar.py        # Case filing calendar / document map
│   │   ├── pacer_meta.py             # PACER/ECF filing package generator
│   │   ├── rule11_monitor.py         # Rule 11 duty monitor
│   │   └── sample_case.json          # Example case input
│   │
│   ├── tests/                        # Pytest suite (459 tests, 16 files)
│   │   ├── conftest.py               # Shared fixtures
│   │   ├── test_case_manager.py      # 31 tests
│   │   ├── test_claims.py            # 25 tests
│   │   ├── test_deposition.py        # 28 tests
│   │   ├── test_districts.py         # 26 tests
│   │   ├── test_doc_analyzer.py      # 45 tests
│   │   ├── test_drafter.py           # 23 tests
│   │   ├── test_exhibits.py          # 35 tests
│   │   ├── test_exporter.py          # 21 tests
│   │   ├── test_filing_calendar.py   # 31 tests
│   │   ├── test_pacer_meta.py        # 31 tests
│   │   ├── test_questions.py         # 25 tests
│   │   ├── test_risk.py              # 39 tests
│   │   ├── test_rule11_monitor.py    # 29 tests
│   │   ├── test_sol.py               # 17 tests
│   │   ├── test_suggest.py           # 13 tests
│   │   └── test_wizard.py            # 40 tests
│   │
│   ├── federal_pleading_engine/      # TypeScript engine (encrypted)
│   │   └── ...
│   │
│   └── courtlistener/                # Case law research module
│       └── ...
│
├── references/                       # 6 legal reference files
│   ├── federal_litigation_engines.md
│   ├── case_strategy_system.md
│   ├── frcp_summary.md
│   ├── fre_summary.md
│   ├── mdfl_local_rules.md
│   └── eleventh_circuit_standards.md
│
├── workflows/
│   └── 00-master-case-analysis.md
│
├── modules/                          # 5 litigation intelligence modules
│   ├── case_analysis_engine.md
│   ├── strategy_scoring_system.md
│   ├── board_risk_dashboard.md
│   ├── case_timeline_builder.md
│   └── mandamus_engine.md
│
└── assets/templates/                 # 42 court document templates
    ├── pleadings/        (6)
    ├── motions/          (15)
    ├── discovery/        (8)
    ├── orders/           (8)
    ├── appellate/        (2)
    └── workflows/        (3)
```

## Auto-Trigger Conditions

The skill activates automatically when detecting:

| Trigger | Example |
|---------|---------|
| Federal case description | "I have a diversity case in the Middle District..." |
| Case number reference | "Case 6:24-cv-01234-ABC-DEF..." |
| Federal document drafting | "Draft a motion to dismiss under Rule 12(b)(6)..." |
| Jurisdiction analysis | "Can we remove this case to federal court..." |
| FRCP/FRE reference | Mentions of federal rules or procedures |
| 11th Circuit appeal | "We need to appeal to the Eleventh Circuit..." |

## Pleading Standards Applied

### FRCP Rule 8(a)
- Short and plain statement of jurisdiction
- Short and plain statement of claim
- Demand for judgment

### Twombly/Iqbal Plausibility
- Each element supported by factual allegations
- "Who, what, when, where, how" for material facts
- Legal conclusions disregarded
- Plausibility = more than possible, less than probable

### Rule 9(b) Heightened Pleading (Fraud)
- Specific identification of false statements
- Who made them, when, where, how
- Why statements were false
- Reliance and causation

### Immunity Considerations
- **Qualified Immunity**: Clearly established law analysis
- **Sovereign Immunity**: Waiver identification
- **Eleventh Amendment**: State agency protection

## MTD Risk Scoring Categories

| Category | Weight | Factors |
|----------|--------|---------|
| Standing | 15% | Injury, causation, redressability |
| Immunity | 20% | Qualified, sovereign, Eleventh Amendment |
| Exhaustion | 15% | EEOC, FTCA SF-95, ERISA, APA |
| SOL | 15% | Statute of limitations compliance |
| Rule 9(b) | 10% | Fraud pleading particularity |
| Monell | 10% | Municipal liability sufficiency |
| Causation | 10% | Direct and proximate cause |
| Damages | 5% | Quantification and proof |

## Running Tests

```bash
cd scripts
pip install pytest pytest-cov
pytest                            # 459 tests
pytest --cov --cov-report=term    # with coverage
pytest -v --tb=short              # verbose with short tracebacks
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

## Legal Disclaimer

This tool assists with legal drafting but does not constitute legal advice. All output should be reviewed by a licensed attorney before filing. The engine does NOT fabricate facts - it only uses facts provided in the input.

## License

Private - For use with Claude Code skills system.

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025 | Initial release — 40+ claims, 19 litigation engines |
| 1.1.0 | 2026 | Complete template library, case analysis engine, strategy scoring |
| 1.2.0 | 2026 | Federal Writ of Mandamus Engine (28 U.S.C. § 1361) |
| 2.0.0 | 2026 | Python CLI engine (45 claims, 8 modules), 42 templates, 117 tests |
| 3.0.0 | 2026 | Interactive wizard, document analyzer, case management, 19 modules, 20 CLI commands, 459 tests |

See [USAGE.md](USAGE.md) for detailed usage instructions with infographics.
