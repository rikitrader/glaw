# Master Case Analysis & Strategy Workflow - Federal Court

---
workflow_id: "00-master-case-analysis"
name: "Master Case Analysis & Strategic Document Generation - Federal"
purpose: "Complete federal case analysis from intake through strategic document drafting"
court: "U.S. District Court (Middle District of Florida)"
triggers: "New case, case review request, litigation strategy request"
output: "Strategic Blueprint + All Required Documents"
integration: "federal_pleading_engine, federal_litigation_engines"
---

## Integrated Engines

This workflow integrates with the following engines:

| Engine | Location | Purpose |
|--------|----------|---------|
| **FTC Python Engine** | `scripts/ftc_engine/` | Full case analysis, claims, risk, drafting (20 CLI commands) |
| **MCP Server** | `scripts/ftc_engine/mcp_server.py` | 20 MCP tools for Claude Code integration |
| **Litigation Engines (19)** | `references/federal_litigation_engines.md` | Defense matrix, jurisdiction traps, trial strategy |
| **CourtListener** | `scripts/courtlistener/` | Case law research (also integrated in Rule 11 monitor) |

### Automatic Engine Activation

When drafting complaints, the system:
1. Analyzes facts against 45 federal causes of action
2. Maps facts to required elements
3. Generates Twombly/Iqbal compliant allegations
4. Calculates MTD risk score (0-100)
5. Identifies fact gaps and recommends discovery

### Usage

**CLI (Python Engine):**
```bash
# Install the engine
pip install -e scripts/

# Auto-suggest claims from facts
ftc suggest -i case.json

# Full case analysis (jurisdiction + claims + risk + SOL + draft)
ftc analyze -i case.json -o ./output

# Interactive case wizard
ftc new

# Health check
ftc doctor
```

**MCP Server (Claude Code Integration):**
```json
{
  "mcpServers": {
    "ftc": {
      "command": "python3",
      "args": ["-m", "ftc_engine.mcp_server"],
      "cwd": "<path-to-scripts-dir>"
    }
  }
}
```

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              FEDERAL MASTER CASE ANALYSIS WORKFLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  PHASE 1: CASE INTAKE & BRAINSTORM                                          │
│  └── Gather facts, jurisdiction analysis, identify goals                    │
│                                                                             │
│  PHASE 2: CASE STATUS DETERMINATION                                         │
│  └── New case vs. Pending case vs. Post-judgment                            │
│                                                                             │
│  PHASE 3: DOCUMENT ANALYSIS (if case pending)                               │
│  └── Review all court filings via PACER/CM-ECF, identify gaps               │
│                                                                             │
│  PHASE 4: LEGAL RESEARCH & PRECEDENT ANALYSIS                               │
│  └── Find controlling 11th Circuit authority, cluster precedents            │
│                                                                             │
│  PHASE 5: STRATEGIC BLUEPRINT GENERATION                                    │
│  └── A/B/C classification, timeline, costs, game plan                       │
│                                                                             │
│  PHASE 6: DOCUMENT DRAFTING QUEUE                                           │
│  └── Generate all required filings in priority order                        │
│                                                                             │
│  PHASE 7: QUALITY CONTROL & DELIVERY                                        │
│  └── Review, cite-check, finalize for CM/ECF filing                         │
│                                                                             │
│  PHASE 8: POST-GENERATION VERIFICATION QUESTIONS                             │
│  └── Context-aware questions: pre-filing, strategic, client, procedural     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PHASE 1: CASE INTAKE & BRAINSTORM

### 1.1 Federal Case Intake Questionnaire

```
FEDERAL CASE INTAKE QUESTIONNAIRE
═══════════════════════════════════════════════════════════════════════════════

CLIENT INFORMATION
───────────────────────────────────────────────────────────────────────────────
Client Name:           _______________________________________________
Client Type:           [ ] Individual  [ ] Corporation  [ ] LLC  [ ] Government
Citizenship:           _______________________________________________
Role:                  [ ] Plaintiff   [ ] Defendant  [ ] Third-Party
Contact:               _______________________________________________

OPPOSING PARTY
───────────────────────────────────────────────────────────────────────────────
Opposing Party Name:   _______________________________________________
Opposing Party Type:   [ ] Individual  [ ] Corporation  [ ] LLC  [ ] Government
Citizenship:           _______________________________________________
Opposing Counsel:      [ ] Represented  [ ] Pro Se  [ ] Unknown

JURISDICTIONAL BASIS
───────────────────────────────────────────────────────────────────────────────
Basis:                 [ ] Federal Question (28 U.S.C. § 1331)
                       [ ] Diversity (28 U.S.C. § 1332)
                       [ ] Supplemental (28 U.S.C. § 1367)
                       [ ] Removal (28 U.S.C. § 1441)
                       [ ] Other: _____________________________________

Federal Statute:       _______________________________________________
Amount in Controversy: $______________ (must exceed $75,000 for diversity)
Complete Diversity:    [ ] Yes  [ ] No  [ ] Analysis needed

CASE STATUS
───────────────────────────────────────────────────────────────────────────────
Case Status:           [ ] Pre-filing (new matter)
                       [ ] Recently filed (< 90 days)
                       [ ] Active litigation (discovery phase)
                       [ ] Dispositive motion stage
                       [ ] Pretrial / Trial imminent
                       [ ] Post-judgment / Appeal
                       [ ] Emergency / TRO needed
                       [ ] Removal consideration

Case Number:           _______________________________________________
Court:                 U.S. District Court, _____________ District of _______
Division:              _______________________________________________
Assigned Judge:        _______________________________________________
Magistrate Judge:      _______________________________________________

KEY DATES (Federal Deadlines)
───────────────────────────────────────────────────────────────────────────────
Filing Date:           _______________________________________________
Service Date:          _______________________________________________ (90 days limit)
Answer Due:            _______________________________________________ (21 days)
Rule 26(f) Conference: _______________________________________________
Initial Disclosures:   _______________________________________________ (14 days after 26(f))
Discovery Cutoff:      _______________________________________________
Expert Disclosure:     _______________________________________________
Dispositive Motion:    _______________________________________________
Pretrial Conference:   _______________________________________________
Trial Date:            _______________________________________________
Next Hearing:          _______________________________________________

CLAIM INFORMATION
───────────────────────────────────────────────────────────────────────────────
Claim Types:           [ ] Contract (diversity)
                       [ ] Civil Rights (42 U.S.C. § 1983)
                       [ ] Employment (Title VII / ADA / ADEA)
                       [ ] ERISA
                       [ ] Securities
                       [ ] Antitrust
                       [ ] Patent / Trademark / Copyright
                       [ ] RICO
                       [ ] Admiralty
                       [ ] Other: _____________________________________

Amount in Controversy: $_______________________________________________
Fee-Shifting Statute:  [ ] 42 U.S.C. § 1988  [ ] Other: ________________

BRIEF FACT SUMMARY
───────────────────────────────────────────────────────────────────────────────
[What happened? When? Who was involved? Key events?]




CLIENT GOALS
───────────────────────────────────────────────────────────────────────────────
Primary Goal:          [ ] Maximum recovery
                       [ ] Minimize liability
                       [ ] Injunctive relief
                       [ ] Declaratory relief
                       [ ] Quick resolution
                       [ ] Vindication / Principle

Budget Constraints:    [ ] Full litigation budget
                       [ ] Limited budget: $_________________
                       [ ] Contingency only
                       [ ] Pro se assistance

═══════════════════════════════════════════════════════════════════════════════
```

### 1.2 Federal Brainstorm Analysis

```
FEDERAL BRAINSTORM ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

1. JURISDICTION CHECK (CRITICAL)
───────────────────────────────────────────────────────────────────────────────
   Federal Question:
   □ Arising under: ________________________________________________
   □ Statute: _____________________________________________________

   Diversity Analysis:
   □ Plaintiff citizenship: ________________________________________
   □ Defendant citizenship: ________________________________________
   □ Complete diversity: [ ] Yes  [ ] No
   □ Amount > $75,000: [ ] Yes  [ ] No  [ ] Aggregation issue

   Removal Analysis (if state court filed):
   □ Federal question present: [ ] Yes  [ ] No
   □ Diversity exists: [ ] Yes  [ ] No
   □ Forum defendant rule: [ ] Applies  [ ] N/A
   □ 30-day removal deadline from: _________________________________

2. TWOMBLY/IQBAL PLAUSIBILITY CHECK
───────────────────────────────────────────────────────────────────────────────
   Each claim element:
   □ Element 1: _________________ Factual support: [ ] Strong  [ ] Weak
   □ Element 2: _________________ Factual support: [ ] Strong  [ ] Weak
   □ Element 3: _________________ Factual support: [ ] Strong  [ ] Weak
   □ Element 4: _________________ Factual support: [ ] Strong  [ ] Weak

   Plausibility Assessment: [ ] Clearly plausible  [ ] Borderline  [ ] At risk

3. SPECIAL FEDERAL DEFENSES
───────────────────────────────────────────────────────────────────────────────
   □ Qualified Immunity (§ 1983)
   □ Sovereign Immunity
   □ Preemption
   □ Arbitration (FAA)
   □ SLUSA (securities)
   □ Other: _______________________________________________________

4. STATUTE OF LIMITATIONS CHECK
───────────────────────────────────────────────────────────────────────────────
   Claim Type              SOL Period       Accrual Date      Deadline
   ____________________    ____________     ____________      ____________
   ____________________    ____________     ____________      ____________

5. INITIAL CASE CLASSIFICATION
───────────────────────────────────────────────────────────────────────────────
   Preliminary Assessment: [ ] A-System (Strong)
                          [ ] B-System (Balanced)
                          [ ] C-System (Challenging)

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 2: CASE STATUS DETERMINATION

```
FEDERAL CASE STATUS ROUTING
═══════════════════════════════════════════════════════════════════════════════

IF case_status == "Pre-filing (new matter)":
    → Jurisdiction memo required
    → Removal analysis (if considering federal forum)
    → SKIP Phase 3
    → Focus: Complaint drafting (Twombly/Iqbal compliant)

ELIF case_status == "Recently filed (< 90 days)":
    → Check: Service deadline (90 days - FRCP 4(m))
    → Check: Answer deadline (21 days - FRCP 12(a))
    → Check: Rule 26(f) conference scheduling
    → Focus: Responsive pleading, Rule 12 motions

ELIF case_status == "Active litigation (discovery)":
    → FULL document analysis via PACER
    → Check: Discovery limits (25 interrogatories, 10 depositions)
    → Check: Scheduling order deadlines
    → Focus: Discovery strategy, MSJ preparation

ELIF case_status == "Dispositive motion stage":
    → Check: Local Rule page limits
    → Check: Statement of material facts requirements
    → Focus: Rule 56 motion practice

ELIF case_status == "Post-judgment / Appeal":
    → Check: FRAP 4(a) appeal deadline (30/60 days)
    → Check: Post-trial motion deadlines (28 days)
    → Focus: 11th Circuit appeal or enforcement

ELIF case_status == "Emergency / TRO needed":
    → FRCP 65 analysis
    → Focus: TRO motion, preliminary injunction

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 3: DOCUMENT ANALYSIS (Pending Cases)

### 3.1 Federal Court Filing Inventory (PACER/CM-ECF Review)

```
FEDERAL FILING ANALYSIS CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

PLEADINGS
───────────────────────────────────────────────────────────────────────────────
□ Complaint
  └── Docket Entry #: _____________
  └── Jurisdictional Allegations: [ ] Adequate  [ ] Deficient
  └── Twombly/Iqbal Plausibility: [ ] Met  [ ] At risk
  └── FRCP 9(b) Compliance (fraud): [ ] N/A  [ ] Met  [ ] Deficient

□ Answer
  └── Docket Entry #: _____________
  └── Rule 12(b) Defenses Preserved: _______________________________
  └── Affirmative Defenses: ________________________________________
  └── Counterclaims: [ ] Compulsory  [ ] Permissive  [ ] None

□ Corporate Disclosure Statement (FRCP 7.1)
  └── Filed: [ ] Yes  [ ] No  [ ] Required

RULE 12 MOTIONS
───────────────────────────────────────────────────────────────────────────────
□ Motion to Dismiss (12(b)(6))
  └── Status: [ ] Pending  [ ] Granted  [ ] Denied  [ ] Partial

□ Motion for More Definite Statement (12(e))
  └── Status: [ ] Pending  [ ] Granted  [ ] Denied

□ Motion to Strike (12(f))
  └── Status: [ ] Pending  [ ] Granted  [ ] Denied

DISCOVERY STATUS
───────────────────────────────────────────────────────────────────────────────
□ Rule 26(f) Conference
  └── Held: [ ] Yes  [ ] No  Date: _____________
  └── Report Filed: [ ] Yes  [ ] No

□ Rule 26(a)(1) Initial Disclosures
  └── Ours: [ ] Served  [ ] Deficient  Date: _____________
  └── Theirs: [ ] Received  [ ] Deficient  Date: _____________

□ Scheduling Order (FRCP 16(b))
  └── Entered: [ ] Yes  [ ] No  Docket #: _____________
  └── Discovery Cutoff: _____________
  └── Expert Disclosure: _____________
  └── Dispositive Motions: _____________
  └── Pretrial Conference: _____________
  └── Trial Date: _____________

□ Interrogatories (25 limit)
  └── Ours Served: _______/25  Responses: [ ] Complete  [ ] Pending
  └── Theirs Received: _______/25  Responses: [ ] Complete  [ ] Pending

□ Depositions (10 per side limit)
  └── Taken: _______/10
  └── Scheduled: _____________
  └── Remaining: _______/10

EXPERT DISCOVERY
───────────────────────────────────────────────────────────────────────────────
□ Rule 26(a)(2) Expert Disclosures
  └── Our Deadline: _____________
  └── Their Deadline: _____________
  └── Reports Exchanged: [ ] Yes  [ ] No

□ Daubert Challenges
  └── Filed: [ ] By us  [ ] By them  [ ] Pending

DISPOSITIVE MOTIONS
───────────────────────────────────────────────────────────────────────────────
□ Motion for Summary Judgment (FRCP 56)
  └── Filed By: _____________  Date: _____________
  └── Response Due: _____________
  └── Status: [ ] Pending  [ ] Granted  [ ] Denied

□ Statement of Material Facts (Local Rule 3.01)
  └── Filed: [ ] Yes  [ ] No
  └── Response: [ ] Yes  [ ] No

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 4: LEGAL RESEARCH (11th Circuit Focus)

```
FEDERAL LEGAL RESEARCH PROTOCOL
═══════════════════════════════════════════════════════════════════════════════

STATUTORY AUTHORITY
───────────────────────────────────────────────────────────────────────────────
Federal Statutes:
□ ___ U.S.C. § _____________ : _____________________________________
□ ___ U.S.C. § _____________ : _____________________________________

Federal Rules:
□ FRCP _____________ : _____________________________________
□ FRE _____________ : _____________________________________

CASE LAW RESEARCH
───────────────────────────────────────────────────────────────────────────────
U.S. Supreme Court:
□ _________________________________, ___ U.S. ___ (_____)
  └── Holding: ________________________________________________

Eleventh Circuit:
□ _________________________________, ___ F.4th ___ (11th Cir. _____)
  └── Holding: ________________________________________________
□ _________________________________, ___ F.4th ___ (11th Cir. _____)
  └── Holding: ________________________________________________

M.D. Florida District Court:
□ _________________________________, ___ F. Supp. 3d ___ (M.D. Fla. _____)
  └── Holding: ________________________________________________

KEY STANDARDS
───────────────────────────────────────────────────────────────────────────────
□ Twombly/Iqbal (pleading): Bell Atlantic v. Twombly, 550 U.S. 544 (2007)
□ Summary Judgment: Celotex Corp. v. Catrett, 477 U.S. 317 (1986)
□ Qualified Immunity: Saucier v. Katz, 533 U.S. 194 (2001)
□ Daubert: Daubert v. Merrell Dow, 509 U.S. 579 (1993)

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 5: STRATEGIC BLUEPRINT GENERATION

**Generate complete Federal Strategic Blueprint per `references/case_strategy_system.md`**

Include:
1. Executive Summary with jurisdictional basis
2. Timeline per FRCP and Local Rules
3. Cost Estimate (Attorney vs. Pro Se)
4. A/B/C System Classification
5. Judge + Magistrate Analysis
6. Complete Game Plan (Rule 26(f), etc.)
7. Key Strategic Decisions
8. Critical Filings with FRCP citations
9. Risk Assessment (including jurisdictional risks)
10. Settlement Analysis with fee-shifting

---

## PHASE 6: DOCUMENT DRAFTING QUEUE

### Federal Document Generation by Status

```
NEW CASE (Pre-Filing) - Plaintiff:
├── [ ] Jurisdictional Analysis Memo
├── [ ] Complaint (Twombly/Iqbal compliant)
├── [ ] Civil Cover Sheet (JS-44)
├── [ ] Corporate Disclosure Statement (FRCP 7.1)
├── [ ] Summons
└── [ ] Initial Disclosures preparation

NEW CASE - Defendant:
├── [ ] Answer (21 days)
├── [ ] Rule 12 Motion (if appropriate)
├── [ ] Corporate Disclosure Statement
├── [ ] Removal Analysis (if state court)
└── [ ] Initial Disclosures preparation

ACTIVE CASE - Discovery Phase:
├── [ ] Rule 26(f) Report
├── [ ] Proposed Scheduling Order
├── [ ] Interrogatories (max 25)
├── [ ] Requests for Production
├── [ ] Requests for Admission
├── [ ] Deposition Notices
└── [ ] Expert Disclosure preparation

DISPOSITIVE MOTION STAGE:
├── [ ] Motion for Summary Judgment
├── [ ] Statement of Undisputed Material Facts (Local Rule 3.01)
├── [ ] Supporting Declarations
├── [ ] Memorandum of Law (page limits per Local Rule)
└── [ ] Response/Reply briefs

PRETRIAL/TRIAL:
├── [ ] Motions in Limine
├── [ ] Pretrial Statement
├── [ ] Proposed Jury Instructions
├── [ ] Witness List
├── [ ] Exhibit List
├── [ ] Trial Brief
└── [ ] Proposed Findings (bench trial)

POST-JUDGMENT:
├── [ ] Rule 50(b) Renewed JMOL (28 days)
├── [ ] Rule 59 Motion for New Trial (28 days)
├── [ ] Rule 54(d)(2) Attorney's Fees Motion (14 days)
├── [ ] Bill of Costs (14 days)
├── [ ] Notice of Appeal (30/60 days)
└── [ ] 11th Circuit briefing

EMERGENCY:
├── [ ] Motion for TRO (FRCP 65)
├── [ ] Verified Complaint
├── [ ] Declarations
├── [ ] Proposed TRO
└── [ ] Motion for Preliminary Injunction
```

---

## PHASE 7: QUALITY CONTROL

```
FEDERAL DOCUMENT CHECKLIST
═══════════════════════════════════════════════════════════════════════════════

□ CM/ECF formatting compliant
□ Caption correct (U.S. District Court format)
□ Case number in proper format
□ All FRCP citations verified
□ All FRE citations verified
□ 11th Circuit precedent current
□ Local Rule compliance (page limits, fonts, margins)
□ Certificate of Service (CM/ECF)
□ Signature block with Bar admission
□ Corporate Disclosure Statement filed (if required)
□ Privacy redactions (FRCP 5.2)

═══════════════════════════════════════════════════════════════════════════════
```

---

## PHASE 8: POST-GENERATION VERIFICATION QUESTIONS

After every document generation, the system produces context-aware verification questions organized into four categories. Questions adapt based on claim types, risk scores, SOL status, jurisdiction basis, and document type.

```
POST-GENERATION VERIFICATION QUESTIONS
═══════════════════════════════════════════════════════════════════════════════

CATEGORY 1: PRE-FILING VERIFICATION
───────────────────────────────────────────────────────────────────────────────
□ Has the document been reviewed by a licensed attorney?
□ Have all facts been verified with client and supporting documents?
□ Corporate Disclosure Statement (FRCP 7.1) prepared?
□ Civil Cover Sheet (JS-44) completed?
□ Service of process plan within 90-day deadline (FRCP 4(m))?
□ M.D. Fla. Local Rule formatting compliance?
□ [Risk-based] High-risk claims strengthened or dropped?

CATEGORY 2: STRATEGIC FOLLOW-UPS
───────────────────────────────────────────────────────────────────────────────
□ Alternative viable claims considered?
□ Top 3 likely defenses preemptively addressed?
□ Discovery plan for undocumented facts?
□ Settlement demand range calculated?
□ Emergency TRO needed before standard PI timeline?
□ Multi-defendant strategy (crossclaim/third-party)?

CATEGORY 3: CLIENT COMMUNICATION
───────────────────────────────────────────────────────────────────────────────
□ Client informed of timeline and costs?
□ Client advised of adverse outcome risks and fee-shifting?
□ Document preservation instruction given?
□ Counterclaim risk discussed?
□ [Pro se] Federal court procedures explained?

CATEGORY 4: PROCEDURAL NEXT STEPS
───────────────────────────────────────────────────────────────────────────────
□ [SOL-based] Urgent/expired claims addressed with tolling analysis?
□ Post-filing deadlines calendared (service, 26(f), disclosures)?
□ Meet-and-confer satisfied for discovery motions?
□ Document exported to .docx for CM/ECF filing?

═══════════════════════════════════════════════════════════════════════════════
```

### Usage

```bash
# Add -q flag to any command to generate questions
ftc analyze -i case.json -q              # Questions after full analysis
ftc draft -i case.json -q                # Questions after complaint draft
ftc export --draft -i case.json -o out.docx -q  # Questions after export

# Add -v for detailed context on each question
ftc analyze -i case.json -q -v
```

### Question Priority Levels

| Icon | Priority | Meaning |
|------|----------|---------|
| `!!` | CRITICAL | Must address before filing — risk of sanctions, dismissal, or malpractice |
| `>>` | HIGH | Should address — significantly affects case outcome |
| `..` | MEDIUM | Good practice — improves filing quality |

---

## Output Location

```
/cases/{case_no}/
├── analysis/
│   ├── intake_questionnaire.md
│   ├── jurisdiction_memo.md
│   ├── brainstorm_analysis.md
│   └── legal_research_memo.md
├── strategy/
│   ├── strategic_blueprint.bd
│   ├── system_classification.md
│   └── judge_profile.md
├── drafts/
│   └── [priority-ordered documents]
└── final/
    └── [CM/ECF ready documents]
```
