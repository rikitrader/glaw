# Federal Trial Counsel — Complete Usage Guide

```
    ╔══════════════════════════════════════════════════════════════════════════╗
    ║                                                                          ║
    ║                    FEDERAL TRIAL COUNSEL v3.0.0                          ║
    ║                    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                          ║
    ║                    Complete Usage Guide (3000+ words)                     ║
    ║                                                                          ║
    ╠══════════════════════════════════════════════════════════════════════════╣
    ║                                                                          ║
    ║    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              ║
    ║    │ 19       │  │ 20       │  │ 459      │  │ 45       │              ║
    ║    │ MODULES  │  │ CLI CMDS │  │ TESTS    │  │ CLAIMS   │              ║
    ║    └──────────┘  └──────────┘  └──────────┘  └──────────┘              ║
    ║                                                                          ║
    ║    ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              ║
    ║    │ 11,910   │  │ 42       │  │ 81%+     │  │ 12-STEP  │              ║
    ║    │ LOC      │  │ TEMPLATES│  │ COVERAGE │  │ WIZARD   │              ║
    ║    └──────────┘  └──────────┘  └──────────┘  └──────────┘              ║
    ║                                                                          ║
    ╚══════════════════════════════════════════════════════════════════════════╝
```

---

## Table of Contents

1. [Quick Start](#1-quick-start)
2. [Installation](#2-installation)
3. [The Interactive Wizard](#3-the-interactive-wizard)
4. [CLI Commands Reference](#4-cli-commands-reference)
5. [Document Analyzer](#5-document-analyzer)
6. [Case Management](#6-case-management)
7. [Pleading Engine](#7-pleading-engine)
8. [Litigation Engines](#8-litigation-engines)
9. [CourtListener Research](#9-courtlistener-research)
10. [Output Formats & Locations](#10-output-formats--locations)
11. [Templates Library](#11-templates-library)
12. [Architecture Overview](#12-architecture-overview)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Quick Start

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FASTEST PATH TO A CASE                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Step 1: Install                                                   │
│   $ cd ~/.claude/skills/federal-trial-counsel/scripts               │
│   $ pip3 install -e .                                               │
│                                                                     │
│   Step 2: Launch Wizard                                             │
│   $ ftc new                                                         │
│                                                                     │
│   Step 3: Follow the 12-step prompts                                │
│   court → plaintiffs → defendants → facts → claims → relief →      │
│   exhaustion → SOL → goals → review → documents → generate         │
│                                                                     │
│   Step 4: Find your files                                           │
│   ~/.ftc/cases/<case-number>/output/                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**One-liner to generate a complaint from a JSON case file:**

```bash
ftc draft --case sample_case.json --out complaint.md
```

**One-liner to analyze documents you already have:**

```bash
ftc analyze-docs my-case-001
```

---

## 2. Installation

### Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| Python | 3.10+ | 3.11+ |
| pip | 21.0+ | Latest |
| Node.js (TS engine only) | 18+ | 20+ |

### Install the Python CLI Engine

```bash
cd ~/.claude/skills/federal-trial-counsel/scripts

# Install in development mode (editable)
pip3 install -e .

# Verify installation
ftc setup
ftc info 1983_fourth_excessive_force
```

### Install Dependencies Manually (if needed)

```bash
pip3 install python-docx PyPDF2
```

### Verify Everything Works

```bash
# Run the full test suite
python3 -m pytest -v --tb=short

# Expected output: 459 passed in ~0.6s
```

### Install the TypeScript Engine (Optional)

```bash
cd scripts/federal_pleading_engine
npm install && npm run build
```

### Install CourtListener Module (Optional)

```bash
# No npm install needed — uses native fetch (Node 18+)
export COURTLISTENER_API_TOKEN="your-token"  # optional, for higher rate limits
```

---

## 3. The Interactive Wizard

The wizard is the primary way to create new cases. It guides you through 12 structured steps, auto-suggesting claims, calculating deadlines, and generating court-ready documents.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    12-STEP CASE WIZARD FLOW                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐         │
│    │ 1.COURT │──>│2.PLNTFS │──>│3.DEFNDS │──>│ 4.FACTS │         │
│    └─────────┘   └─────────┘   └─────────┘   └─────────┘         │
│         │                                          │               │
│         v                                          v               │
│    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐         │
│    │5.CLAIMS │──>│6.RELIEF │──>│7.EXHSTN │──>│ 8.SOL   │         │
│    └─────────┘   └─────────┘   └─────────┘   └─────────┘         │
│         │                                          │               │
│         v                                          v               │
│    ┌─────────┐   ┌──────────┐  ┌──────────┐  ┌─────────┐         │
│    │ 9.GOALS │──>│10.REVIEW │──>│11.DOCS  │──>│12.GEN   │         │
│    └─────────┘   └──────────┘  └──────────┘  └─────────┘         │
│                                                    │               │
│                                                    v               │
│                                         ┌──────────────────┐       │
│                                         │  OUTPUT FILES:   │       │
│                                         │  .md / .docx     │       │
│                                         │  Desktop/Docs/   │       │
│                                         │  Custom path     │       │
│                                         └──────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Launch the Wizard

```bash
# New case from scratch
ftc new

# Resume an existing case
ftc open 6:24-cv-01234

# List all saved cases
ftc cases
```

### Step-by-Step Walkthrough

**Step 1 — Court & Jurisdiction**: Select from 94 federal districts or enter manually. Specify the division (Orlando, Tampa, Jacksonville, etc.).

**Step 2 — Plaintiffs**: Enter one or more plaintiffs. For each: name, entity type (individual, corporation, LLC, partnership, municipality), citizenship/domicile, and contact information. Corporate parties get additional fields for state of incorporation and principal place of business (for diversity jurisdiction analysis).

**Step 3 — Defendants**: Enter one or more defendants. Additional fields include: defendant type (officer, local, federal, state, private), capacity sued in (individual, official, or both), and role/title. This directly feeds into Monell analysis and immunity screening.

**Step 4 — Factual Allegations**: Enter each factual event: date, location, what happened, who was involved, harm caused, supporting documents, witnesses, evidence, and damages estimate. You can enter as many facts as needed. These facts feed directly into the claim auto-suggestion engine.

**Step 5 — Claims Selection**: The engine auto-suggests claims based on your facts using pattern matching against 45 federal causes of action across 9 categories. You can accept the suggestions, browse categories manually, or combine both. Each suggestion shows a confidence score.

**Step 6 — Relief Requested**: Multi-select from: compensatory/punitive damages, injunctive relief, declaratory judgment, attorney fees/costs, and restoration/reinstatement.

**Step 7 — Administrative Exhaustion**: The system automatically checks which of your selected claims require exhaustion (EEOC for Title VII/ADA/ADEA, SF-95 for FTCA, internal appeal for ERISA, final agency action for APA) and asks the relevant questions.

**Step 8 — Statute of Limitations**: Enter the injury/incident date. The system calculates SOL deadlines for each selected claim and flags any that are close to expiring.

**Step 9 — Case Goals**: Capture the client's primary and secondary goals (e.g., "Obtain $500,000 compensation" and "Policy change to prevent future incidents").

**Step 10 — Case Summary Review**: Full summary displayed. You can go back to any previous step to make corrections before proceeding.

**Step 11 — Document Selection & Output**: Select which documents to generate (complaint, analysis report, JS-44, summons, corporate disclosure, filing calendar, Rule 11 monitor, MTD risk scores, SOL report, exhibit index, deposition outlines, verification questions). Choose your **output format** (terminal, markdown, docx, or both md+docx) and **save location** (Desktop, Documents, case folder, or custom path).

**Step 12 — Generation**: The pipeline generates all selected documents, saves them to disk, and copies them to your chosen location.

### Document Import & Analysis

At the start of both new and existing case flows, the wizard asks if you have documents to provide. If yes:

1. Point to a folder or file path
2. Documents are copied to `intake_docs/`
3. The Document Analyzer runs automatically (see Section 5)
4. Extracted data (parties, dates, case numbers, claims, court) is offered for auto-population
5. A workflow suggestion is provided (complaint defense, motion response, etc.)

---

## 4. CLI Commands Reference

```
┌─────────────────────────────────────────────────────────────────────┐
│                     20 CLI COMMANDS                                  │
├──────────────┬──────────────────────────────────────────────────────┤
│ COMMAND      │ DESCRIPTION                                          │
├──────────────┼──────────────────────────────────────────────────────┤
│ ftc new      │ Launch 12-step wizard for a new case                 │
│ ftc open     │ Resume an existing case                              │
│ ftc cases    │ List all saved cases                                 │
│ ftc delete   │ Delete a case                                        │
│ ftc import   │ Import documents into a case                         │
│ ftc analyze-docs │ Analyze documents in a case's intake folder      │
│ ftc suggest  │ Auto-suggest claims from case facts                  │
│ ftc risk     │ Calculate MTD risk score for a claim                 │
│ ftc sol      │ Statute of limitations calculator                    │
│ ftc draft    │ Generate complaint draft                             │
│ ftc export   │ Export document to .docx format                      │
│ ftc claims   │ Browse all 45 federal causes of action               │
│ ftc info     │ Show claim details (elements, defenses, SOL)         │
│ ftc generate │ Generate specific document for a case                │
│ ftc outputs  │ List generated files for a case                      │
│ ftc status   │ Show case workflow progress                          │
│ ftc districts│ List all 94 federal districts                        │
│ ftc questions│ Generate verification questions                      │
│ ftc calendar │ Generate filing calendar                             │
│ ftc setup    │ Install dependencies and verify setup                │
├──────────────┴──────────────────────────────────────────────────────┤
│ Usage: ftc <command> [arguments]                                     │
│ Help:  ftc --help                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Examples

```bash
# Create a new case interactively
ftc new

# Auto-suggest claims from a JSON case file
ftc suggest --case my_case.json

# Calculate MTD risk for excessive force claim
ftc risk --case my_case.json --claim 1983_fourth_excessive_force

# Check statute of limitations
ftc sol --claim title_vii_disparate_treatment --date 2024-03-15

# Generate complaint from case data
ftc draft --case my_case.json --out complaint.md

# Export to Word format
ftc export complaint.md --out complaint.docx

# Browse claims by category
ftc claims --category constitutional

# Show full claim details
ftc info 1983_monell_municipal_liability

# Analyze documents in a case
ftc analyze-docs 6:24-cv-01234

# List all cases
ftc cases

# Check case workflow status
ftc status 6:24-cv-01234
```

---

## 5. Document Analyzer

The Document Analyzer is a 5-layer intake pipeline that reads, classifies, and extracts entities from legal documents.

```
┌─────────────────────────────────────────────────────────────────────┐
│                   DOCUMENT ANALYZER PIPELINE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│   │  LAYER 1 │  │  LAYER 2 │  │  LAYER 3 │  │  LAYER 4 │         │
│   │  READ    │─>│ CLASSIFY │─>│ EXTRACT  │─>│ ANALYZE  │         │
│   │          │  │          │  │          │  │          │         │
│   │ PDF      │  │complaint │  │ parties  │  │ combine  │         │
│   │ DOCX     │  │motion    │  │ dates    │  │ score    │         │
│   │ TXT      │  │discovery │  │ case #   │  │ report   │         │
│   │ MD       │  │evidence  │  │ claims   │  │          │         │
│   │          │  │18 types  │  │ court    │  │          │         │
│   └──────────┘  └──────────┘  └──────────┘  └──────────┘         │
│                                                    │               │
│                                                    v               │
│                                         ┌──────────────────┐       │
│                                         │    LAYER 5       │       │
│                                         │    ROUTE         │       │
│                                         │                  │       │
│                                         │ complaint_defense│       │
│                                         │ motion_response  │       │
│                                         │ discovery_resp   │       │
│                                         │ compliance       │       │
│                                         │ new_case         │       │
│                                         └──────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Supported File Types

| Extension | Reader | Library |
|-----------|--------|---------|
| `.pdf` | PyPDF2 page extraction | PyPDF2 |
| `.docx` / `.doc` | Paragraph text extraction | python-docx |
| `.txt` | Plain text UTF-8 read | stdlib |
| `.md` | Plain text UTF-8 read | stdlib |

### 18 Document Categories

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT CLASSIFICATION                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   PROCEDURAL (7)              │  EVIDENCE (11)                      │
│   ─────────────────           │  ─────────────────                  │
│   complaint                   │  medical_records                    │
│   answer                      │  police_report                     │
│   motion_dismiss              │  financial                         │
│   motion_summary_judgment     │  correspondence                    │
│   motion_other                │  photograph                        │
│   discovery_request           │  employment                        │
│   court_order                 │  government_record                 │
│   subpoena                    │  contract                          │
│   notice                      │  deposition_transcript             │
│   deposition_transcript       │                                     │
│                               │                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Entity Extraction (Regex-Based)

| Entity | Pattern | Example Match |
|--------|---------|---------------|
| Parties | `Name v. Name`, `Plaintiff: Name` | JOHN SMITH v. OFFICER BROWN |
| Dates | ISO, US, written formats | 2025-06-15, 06/15/2025, January 15, 2024 |
| Case Numbers | Federal court patterns | 6:24-cv-01234-ABC-DEF |
| Statutory Claims | 15+ patterns | 42 U.S.C. Section 1983, Title VII, FTCA |
| Court Info | District court patterns | MIDDLE DISTRICT OF FLORIDA |

### Workflow Routing Priority

When multiple document types are detected, routing follows this priority:

```
complaint > motion_dismiss > motion_summary_judgment > motion_other >
discovery_request > court_order > subpoena > notice > answer >
deposition_transcript > evidence types (all route to new_case)
```

### Standalone Usage

```bash
# Analyze all documents in a case
ftc analyze-docs my-case-001

# Output: classification table, extracted entities, workflow suggestion
```

---

## 6. Case Management

All cases are stored at `~/.ftc/cases/<case_number>/` with this structure:

```
~/.ftc/cases/6:24-cv-01234/
├── state.json          # Wizard progress, selected docs, format, location
├── case.json           # All case data (parties, facts, claims, court, etc.)
├── intake_docs/        # Imported documents (originals preserved)
├── output/             # Generated documents (.md, .docx)
├── work_product/       # Strategic documents, blueprints, memos
│   ├── pleadings/
│   ├── strategy/
│   ├── motions/
│   ├── discovery/
│   ├── evidence/
│   ├── research/
│   └── trial/
└── exhibits/           # Exhibit management
```

### Case Lifecycle

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  CREATE  │──>│  INTAKE  │──>│ GENERATE │──>│  FILED   │
│  ftc new │   │  wizard  │   │ docs     │   │  manage  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Key Commands

```bash
ftc cases                    # List all cases with status
ftc open <case_number>       # Resume wizard for a case
ftc status <case_number>     # Show workflow progress map
ftc import <case> <path>     # Import documents into a case
ftc delete <case_number>     # Delete a case (asks confirmation)
ftc outputs <case_number>    # List all generated files
```

---

## 7. Pleading Engine

The Pleading Engine generates Twombly/Iqbal-compliant federal complaints with element-by-element analysis.

### 45 Federal Causes of Action

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CLAIM CATEGORIES (9)                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  A. Constitutional / 1983 .... 11 claims                            │
│  B. Bivens (Federal) ......... 3 claims                             │
│  C. Administrative / APA ..... 4 claims                             │
│  D. Employment ............... 8 claims                             │
│  E. FTCA (Federal Tort) ..... 3 claims                             │
│  F. Financial / Consumer ..... 3 claims                             │
│  G. Commercial / RICO / IP .. 8 claims                             │
│  H. ERISA ................... 2 claims                             │
│  I. Tax ..................... 2 claims                             │
│                               ─────────                             │
│                         TOTAL: 45 claims                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Auto-Suggestion

The suggest engine pattern-matches facts to claims using keyword scoring. It checks for:

- Constitutional violation indicators (force, arrest, search, speech)
- Employment discrimination signals (termination, harassment, retaliation)
- Government actor detection (officer, agency, federal employee)
- Exhaustion requirement detection (EEOC, FTCA, ERISA)
- Statutory reference recognition (42 U.S.C. Section 1983, Title VII, etc.)

### MTD Risk Scoring (0-100)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MTD RISK CATEGORIES                              │
├──────────────┬────────┬─────────────────────────────────────────────┤
│ Category     │ Weight │ Factors                                      │
├──────────────┼────────┼─────────────────────────────────────────────┤
│ Standing     │   15%  │ Injury, causation, redressability            │
│ Immunity     │   20%  │ Qualified, sovereign, Eleventh Amendment     │
│ Exhaustion   │   15%  │ EEOC, FTCA SF-95, ERISA, APA                │
│ SOL          │   15%  │ Statute of limitations compliance            │
│ Rule 9(b)    │   10%  │ Fraud pleading particularity                 │
│ Monell       │   10%  │ Municipal liability sufficiency              │
│ Causation    │   10%  │ Direct and proximate cause                   │
│ Damages      │    5%  │ Quantification and proof                     │
├──────────────┼────────┼─────────────────────────────────────────────┤
│ TOTAL        │  100%  │ Score 0-100 (lower = higher risk)           │
└──────────────┴────────┴─────────────────────────────────────────────┘
```

---

## 8. Litigation Engines

19 specialized analysis engines for complete case management:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    19 LITIGATION ENGINES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   OFFENSIVE                    │  DEFENSIVE                         │
│   ──────────                   │  ──────────                        │
│   1. Complaint Structure       │  2. Defense Matrix                 │
│   3. Discovery Strategy        │  4. MTD Counter-Strike             │
│   8. Summary Judgment Builder  │  5. Case Survival Probability      │
│   12. Jury Persuasion          │  16. Sanctions Analyzer            │
│                                │                                     │
│   INTELLIGENCE                 │  TRIAL                             │
│   ──────────────               │  ──────                            │
│   6. Judge Risk Model          │  9. Trial Strategy                 │
│   14. Evidence Credibility     │  15. Pretrial Motions              │
│   18. Judge Behavior Profiler  │  17. Jury Instructions             │
│                                │  19. Voir Dire Strategy            │
│                                │                                     │
│   FINANCIAL                    │  APPELLATE                         │
│   ──────────                   │  ──────────                        │
│   11. Settlement Optimization  │  10. Appellate Strategy            │
│   13. Damages Modeling         │                                     │
│                                │                                     │
│   JURISDICTIONAL               │                                     │
│   ──────────────               │                                     │
│   7. Jurisdictional Traps      │                                     │
│                                │                                     │
└─────────────────────────────────────────────────────────────────────┘
```

These engines are activated through the skill's AI analysis workflow. Each generates structured output with risk assessments, recommendations, and action items.

---

## 9. CourtListener Research

Search federal case law directly from the CLI:

```bash
# Search Middle District of Florida
npx ts-node scripts/courtlistener/cli.ts \
  --q "qualified immunity excessive force" \
  --court flmd --after 2023-01-01 --sort newest

# Search Eleventh Circuit
npx ts-node scripts/courtlistener/cli.ts \
  --q "motion to dismiss plausibility" \
  --court ca11 --limit 20

# Search multiple courts
npx ts-node scripts/courtlistener/cli.ts \
  --q "Monell failure to train" \
  --court flmd,ca11,scotus
```

### Supported Courts

| Code | Court |
|------|-------|
| `flmd` | Middle District of Florida |
| `flnd` | Northern District of Florida |
| `flsd` | Southern District of Florida |
| `ca11` | Eleventh Circuit |
| `scotus` | Supreme Court |
| `ca1`-`ca11` | All Circuit Courts |

---

## 10. Output Formats & Locations

### Format Options (Step 11)

| Format | Extension | Description |
|--------|-----------|-------------|
| `terminal` | (none) | Display output in terminal only |
| `markdown` | `.md` | Save as Markdown files |
| `docx` | `.docx` | Court-formatted Word (TNR 14pt, double-spaced, 1" margins) |
| `both` | `.md` + `.docx` | Save both formats |

### Save Location Options (Step 11)

| Location | Path | Use Case |
|----------|------|----------|
| `desktop` | `~/Desktop/<case>/` | Quick access for review |
| `documents` | `~/Documents/<case>/` | Long-term storage |
| `case-folder` | `~/.ftc/cases/<case>/output/` | Default (internal) |
| `custom` | Any path you enter | Shared drives, cloud sync, etc. |

Files are always saved to the internal case folder AND copied to your chosen location.

---

## 11. Templates Library

42 court-ready templates organized by category:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    42 TEMPLATES                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   PLEADINGS (6)          │  MOTIONS (15)        │  DISCOVERY (8)   │
│   ────────────           │  ────────────        │  ────────────    │
│   Complaint              │  MTD (12b)           │  Initial Discl.  │
│   Amended Complaint      │  Opposition to MTD   │  Interrogatories │
│   Answer                 │  Summary Judgment    │  RFPs            │
│   Notice of Removal      │  Opposition to SJ    │  RFAs            │
│   Third-Party Complaint  │  Reply Brief         │  Depo Notice     │
│   Counterclaim           │  Amend               │  Subpoena        │
│                          │  Default Judgment    │  Expert Discl.   │
│                          │  Remand              │  Response Tmpl.  │
│                          │  Protective Order    │                  │
│                          │  TRO                 │                  │
│                          │  Preliminary Inj.    │                  │
│                          │  Compel              │                  │
│                          │  Sanctions           │                  │
│                          │  MIL                 │                  │
│                          │  Post-Trial          │                  │
│                                                                     │
│   ORDERS (8)             │  APPELLATE (2)       │  WORKFLOWS (3)   │
│   ──────────             │  ────────────        │  ────────────    │
│   MTD Order              │  Notice of Appeal    │  Case Intake     │
│   SJ Order               │  Appellate Brief     │  Trial Prep      │
│   TRO Order              │                      │  Appeal Process  │
│   PI Order               │                      │                  │
│   Compel Order           │                      │                  │
│   Sanctions Order        │                      │                  │
│   Scheduling Order       │                      │                  │
│   Consent Order          │                      │                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Templates are located at `assets/templates/` and follow M.D. Fla. Local Rules formatting. Adapt for other districts as needed.

---

## 12. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   USER INPUT                                                        │
│   ──────────                                                        │
│      │                                                              │
│      ├── ftc new ──────────> WIZARD (12 steps)                      │
│      │                         │                                    │
│      ├── ftc draft ─────────> DRAFTER (complaint gen)               │
│      │                         │                                    │
│      ├── ftc suggest ───────> SUGGEST (claim matching)              │
│      │                         │                                    │
│      ├── ftc risk ──────────> RISK ENGINE (MTD scoring)             │
│      │                         │                                    │
│      ├── ftc analyze-docs ──> DOC ANALYZER (5-layer pipeline)       │
│      │                         │                                    │
│      └── ftc sol ───────────> SOL CALCULATOR                        │
│                                │                                    │
│                                v                                    │
│   STORAGE                                                           │
│   ───────                                                           │
│   ~/.ftc/cases/<case>/                                              │
│      ├── state.json    (wizard progress)                            │
│      ├── case.json     (structured case data)                       │
│      ├── intake_docs/  (imported documents)                         │
│      ├── output/       (generated .md / .docx)                      │
│      └── work_product/ (strategy, memos)                            │
│                                                                     │
│   PYTHON MODULES (19)                                               │
│   ──────────────────                                                │
│   cli.py ─── claims.py ─── risk.py ─── sol.py ─── suggest.py       │
│   drafter.py ─── exporter.py ─── questions.py ─── wizard.py        │
│   case_manager.py ─── doc_analyzer.py ─── districts.py             │
│   exhibits.py ─── deposition.py ─── filing_calendar.py             │
│   pacer_meta.py ─── rule11_monitor.py ─── sample_case.json         │
│   __init__.py ─── __main__.py                                       │
│                                                                     │
│   TEST SUITE (459 tests, 81%+ coverage)                             │
│   ─────────────────────────────────────                             │
│   18 test files, pytest + pytest-cov                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Dependency Map

```
cli.py (entry point)
  ├── wizard.py (12-step interactive flow)
  │     ├── case_manager.py (CRUD, state, persistence)
  │     ├── doc_analyzer.py (intake pipeline)
  │     ├── districts.py (94 federal districts)
  │     └── [all generation modules below]
  │
  ├── claims.py (45 causes of action)
  ├── suggest.py (auto-suggestion from facts)
  ├── risk.py (MTD risk scoring)
  ├── sol.py (statute of limitations)
  ├── drafter.py (complaint generation)
  ├── exporter.py (.docx formatting)
  ├── questions.py (verification questions)
  ├── filing_calendar.py (deadline tracking)
  ├── pacer_meta.py (JS-44, summons, disclosure)
  ├── rule11_monitor.py (compliance checks)
  ├── exhibits.py (exhibit management)
  └── deposition.py (outline generation)
```

---

## 13. Troubleshooting

### Common Issues

**`ftc: command not found`**
```bash
cd ~/.claude/skills/federal-trial-counsel/scripts
pip3 install -e .
```

**`ModuleNotFoundError: No module named 'docx'`**
```bash
pip3 install python-docx
```

**`ModuleNotFoundError: No module named 'PyPDF2'`**
```bash
pip3 install PyPDF2
```

**Tests failing after update**
```bash
cd ~/.claude/skills/federal-trial-counsel/scripts
pip3 install -e .
python3 -m pytest -v --tb=short
```

**Case folder not found**
Cases are stored at `~/.ftc/cases/`. Check with:
```bash
ls ~/.ftc/cases/
```

**Document analysis finds no documents**
Only `.pdf`, `.docx`, `.doc`, `.txt`, and `.md` files in `intake_docs/` are analyzed. Check:
```bash
ls ~/.ftc/cases/<case>/intake_docs/
```

### Getting Help

```bash
ftc --help           # General help
ftc <command> --help # Command-specific help
```

### Running Tests

```bash
cd ~/.claude/skills/federal-trial-counsel/scripts

# Full suite
python3 -m pytest -v

# Specific module
python3 -m pytest tests/test_doc_analyzer.py -v

# With coverage
python3 -m pytest --cov --cov-report=term-missing
```

---

## Version History

| Version | Date | Tests | Changes |
|---------|------|-------|---------|
| 1.0.0 | 2025 | — | Initial release: 40+ claims, 19 litigation engines |
| 1.1.0 | 2026-01 | — | Complete template library, case analysis engine |
| 1.2.0 | 2026-01 | — | Mandamus engine |
| 2.0.0 | 2026-02 | 117 | Python CLI (45 claims), 42 templates, pytest suite |
| 2.1.0 | 2026-02 | 163 | .docx export, verification questions |
| 2.2.0 | 2026-02 | 290 | Districts, deposition, exhibits, PACER, Rule 11, calendar |
| 2.3.0 | 2026-02 | 409 | 12-step interactive wizard, case manager |
| 2.4.0 | 2026-02 | 452 | Document analyzer (5-layer intake pipeline) |
| **3.0.0** | **2026-02** | **459** | **Output format/location, classifier hardening, regex fixes** |

---

*This guide covers Federal Trial Counsel v3.0.0. All output should be reviewed by a licensed attorney before filing with any court.*
