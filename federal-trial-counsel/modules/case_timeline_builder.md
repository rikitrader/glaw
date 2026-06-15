---
name: Automatic Case Timeline Builder
type: litigation-intelligence
output: chronology
---

# Automatic Case Timeline Builder

## Overview

This module generates comprehensive case timelines for federal litigation, tracking key dates, deadlines, and events for trial preparation and case management.

## Timeline Template

```
═══════════════════════════════════════════════════════════════════════════════
                         CASE TIMELINE AND CHRONOLOGY
═══════════════════════════════════════════════════════════════════════════════
CASE:          {{CASE_NAME}}
CASE NUMBER:   {{CASE_NO}}
COURT:         U.S. District Court, Middle District of Florida
JUDGE:         {{JUDGE_NAME}}
PREPARED:      {{DATE}}
═══════════════════════════════════════════════════════════════════════════════

                         LITIGATION PHASE OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ CURRENT PHASE: [ ] Pleading  [X] Discovery  [ ] Dispositive  [ ] Trial     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   FILED ──► ANSWER ──► DISCOVERY ──► MOTIONS ──► PRETRIAL ──► TRIAL       │
│     │         │           ▲            │           │          │            │
│     ✓         ✓           █            ○           ○          ○            │
│                                                                             │
│   Legend: ✓ Complete  █ Current  ○ Pending                                 │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                          CRITICAL DEADLINES
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│  ⚠️  NEXT 30 DAYS                                                           │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ EVENT                                        │ STATUS        │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ {{EVENT}}                                    │ {{STATUS}}    │
│ {{DATE}}     │ {{EVENT}}                                    │ {{STATUS}}    │
│ {{DATE}}     │ {{EVENT}}                                    │ {{STATUS}}    │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  📅 KEY COURT DEADLINES                                                     │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ EVENT                                        │ SOURCE        │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ Initial Disclosures Due                      │ Rule 26(a)    │
│ {{DATE}}     │ Discovery Cutoff                             │ CMO           │
│ {{DATE}}     │ Expert Designation - Plaintiff               │ CMO           │
│ {{DATE}}     │ Expert Designation - Defendant               │ CMO           │
│ {{DATE}}     │ Rebuttal Expert Designation                  │ CMO           │
│ {{DATE}}     │ Expert Discovery Cutoff                      │ CMO           │
│ {{DATE}}     │ Dispositive Motions Deadline                 │ CMO           │
│ {{DATE}}     │ Mediation Deadline                           │ CMO           │
│ {{DATE}}     │ Pretrial Conference                          │ Court Order   │
│ {{DATE}}     │ Trial                                        │ Court Order   │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        FACTUAL CHRONOLOGY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ PRE-LITIGATION EVENTS                                                       │
├──────────────┬──────────────────────────────────────────────────────────────┤
│ DATE         │ EVENT                                                        │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ {{DESCRIPTION}}                                              │
│              │ Source: {{SOURCE_DOCUMENT}}                                  │
│              │ Witnesses: {{WITNESSES}}                                     │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ {{DESCRIPTION}}                                              │
│              │ Source: {{SOURCE_DOCUMENT}}                                  │
│              │ Witnesses: {{WITNESSES}}                                     │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ {{DESCRIPTION}}                                              │
│              │ Source: {{SOURCE_DOCUMENT}}                                  │
│              │ Witnesses: {{WITNESSES}}                                     │
└──────────────┴──────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ KEY DISPUTED EVENTS                                                         │
├──────────────┬──────────────────────────────────────────────────────────────┤
│ DATE         │ EVENT                                                        │
├──────────────┼──────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ {{DESCRIPTION}}                                              │
│              │ Plaintiff's Version: {{PLAINTIFF_VERSION}}                   │
│              │ Defendant's Version: {{DEFENDANT_VERSION}}                   │
│              │ Key Documents: {{DOCUMENTS}}                                 │
└──────────────┴──────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        PROCEDURAL CHRONOLOGY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ PLEADINGS PHASE                                                             │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ FILING                                       │ DOC #         │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ Complaint Filed                              │ Doc. 1        │
│ {{DATE}}     │ Summons Issued                               │ Doc. 2        │
│ {{DATE}}     │ Service Executed                             │ Doc. 3        │
│ {{DATE}}     │ Answer/Motion to Dismiss Filed               │ Doc. {{X}}    │
│ {{DATE}}     │ {{FILING}}                                   │ Doc. {{X}}    │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ DISCOVERY PHASE                                                             │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ EVENT                                        │ DOC #/STATUS  │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ Rule 26(f) Conference                        │ Completed     │
│ {{DATE}}     │ Case Management Order Entered                │ Doc. {{X}}    │
│ {{DATE}}     │ Initial Disclosures Served                   │ N/A           │
│ {{DATE}}     │ Plaintiff's First Interrogatories            │ Served        │
│ {{DATE}}     │ Plaintiff's First RFPs                       │ Served        │
│ {{DATE}}     │ Defendant's Discovery Responses Due          │ Pending       │
│ {{DATE}}     │ Deposition of {{WITNESS}}                    │ Scheduled     │
│ {{DATE}}     │ {{EVENT}}                                    │ {{STATUS}}    │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ MOTION PRACTICE                                                             │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ MOTION                                       │ STATUS        │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ Motion to Dismiss (Doc. {{X}})               │ {{STATUS}}    │
│ {{DATE}}     │ Response to MTD (Doc. {{X}})                 │ {{STATUS}}    │
│ {{DATE}}     │ Reply (Doc. {{X}})                           │ {{STATUS}}    │
│ {{DATE}}     │ Order on MTD (Doc. {{X}})                    │ {{RULING}}    │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        DEADLINE CALCULATIONS
═══════════════════════════════════════════════════════════════════════════════

Rule 6(a) - Computing Time:

┌─────────────────────────────────────────────────────────────────────────────┐
│ TRIGGERED DEADLINES                                                         │
├─────────────────────────────┬───────────────┬───────────────────────────────┤
│ TRIGGERING EVENT            │ PERIOD        │ DEADLINE                      │
├─────────────────────────────┼───────────────┼───────────────────────────────┤
│ Service of Complaint        │ 21 days       │ Answer due: {{DATE}}          │
│ Service of Discovery        │ 30 days       │ Response due: {{DATE}}        │
│ Filing of Motion            │ 21 days       │ Response due: {{DATE}}        │
│ Service of Response         │ 7 days        │ Reply due: {{DATE}}           │
│ Entry of Judgment           │ 28 days       │ Rule 59 motion: {{DATE}}      │
│ Entry of Judgment           │ 30 days       │ Notice of Appeal: {{DATE}}    │
└─────────────────────────────┴───────────────┴───────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                          WITNESS TIMELINE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ WITNESS               │ DEPOSITION    │ AVAILABILITY     │ KEY FACTS        │
├───────────────────────┼───────────────┼──────────────────┼──────────────────┤
│ {{WITNESS_NAME}}      │ {{DATE}}      │ {{AVAILABILITY}} │ {{FACTS}}        │
│ {{WITNESS_NAME}}      │ {{DATE}}      │ {{AVAILABILITY}} │ {{FACTS}}        │
│ {{WITNESS_NAME}}      │ {{DATE}}      │ {{AVAILABILITY}} │ {{FACTS}}        │
└───────────────────────┴───────────────┴──────────────────┴──────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                        DOCUMENT TIMELINE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│ KEY DOCUMENTS BY DATE                                                       │
├──────────────┬──────────────────────────────────────────────┬───────────────┤
│ DATE         │ DOCUMENT                                     │ EXHIBIT #     │
├──────────────┼──────────────────────────────────────────────┼───────────────┤
│ {{DATE}}     │ {{DOCUMENT_DESCRIPTION}}                     │ Ex. {{X}}     │
│ {{DATE}}     │ {{DOCUMENT_DESCRIPTION}}                     │ Ex. {{X}}     │
│ {{DATE}}     │ {{DOCUMENT_DESCRIPTION}}                     │ Ex. {{X}}     │
└──────────────┴──────────────────────────────────────────────┴───────────────┘

═══════════════════════════════════════════════════════════════════════════════
```

---

## Timeline Categories

### 1. Factual Events
- Pre-litigation conduct
- Contract formation/breach
- Injury-causing events
- Communications between parties
- Third-party involvement

### 2. Procedural Events
- Filings (complaints, answers, motions)
- Court orders
- Discovery events
- Hearings
- Deadlines

### 3. Discovery Events
- Written discovery served/responses
- Depositions
- Document productions
- Expert disclosures

### 4. Deadlines
- Court-ordered deadlines (CMO)
- Rule-based deadlines
- Contractual deadlines
- Statutory deadlines

---

## Automatic Deadline Calculation

### FRCP Deadlines:

| Event | Deadline | Rule |
|-------|----------|------|
| Answer to Complaint | 21 days from service | Rule 12(a)(1)(A) |
| Answer after MTD denied | 14 days from order | Rule 12(a)(4) |
| Discovery responses | 30 days from service | Rules 33, 34, 36 |
| Motion response | 21 days from service | Local Rule |
| Reply brief | 7 days from response | Local Rule |
| Rule 59 motion | 28 days from judgment | Rule 59(b) |
| Notice of Appeal | 30 days from judgment | FRAP 4(a)(1) |

### M.D. Fla. Local Rule Deadlines:

| Event | Deadline | Local Rule |
|-------|----------|------------|
| Motion response | 21 days | LR 3.01(b) |
| Reply | 7 days | LR 3.01(b) |
| Discovery certification | Before filing | LR 3.01(g) |

---

## Usage

### Input Required:
1. Case caption and number
2. Judge assignment
3. Case Management Order dates
4. Key factual events with dates
5. Document list with dates

### Output Generated:
1. Comprehensive timeline (Markdown/PDF)
2. Deadline calendar (ICS export)
3. Trial preparation checklist
4. Witness availability chart
