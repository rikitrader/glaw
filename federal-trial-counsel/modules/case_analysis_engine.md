---
name: Comprehensive Case Analysis Engine
type: litigation-intelligence
output: detailed-analysis-report
---

# COMPREHENSIVE CASE ANALYSIS ENGINE

## Overview

This module generates detailed case analysis reports when drafting motions, pleadings, or discovery responses. It provides a complete strategic assessment with scoring metrics.

---

## MASTER CASE ANALYSIS TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                    COMPREHENSIVE CASE ANALYSIS REPORT
═══════════════════════════════════════════════════════════════════════════════

CASE:              {{CASE_NAME}}
CASE NUMBER:       {{CASE_NO}}
COURT:             {{COURT}}
JUDGE:             {{JUDGE_NAME}}
ANALYSIS DATE:     {{DATE}}
ANALYST:           {{ATTORNEY_NAME}}
CLASSIFICATION:    PRIVILEGED AND CONFIDENTIAL - ATTORNEY WORK PRODUCT

═══════════════════════════════════════════════════════════════════════════════
                         EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                         CASE VIABILITY SCORE                                │
│                                                                             │
│         ████████████████████░░░░░░░░░░   {{SCORE}}/100                     │
│                                                                             │
│    RECOMMENDATION:  [ ] STRONG  [ ] FAVORABLE  [ ] NEUTRAL  [ ] WEAK       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│    Primary Claim Strength:        {{CLAIM_SCORE}}/100                       │
│    Defense Vulnerability:         {{DEFENSE_SCORE}}/100                     │
│    Evidence Quality:              {{EVIDENCE_SCORE}}/100                    │
│    Damages Potential:             {{DAMAGES_SCORE}}/100                     │
│    Settlement Likelihood:         {{SETTLEMENT_SCORE}}/100                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

SUMMARY:
{{EXECUTIVE_SUMMARY_PARAGRAPH}}

═══════════════════════════════════════════════════════════════════════════════
                      SECTION 1: CASE OVERVIEW
═══════════════════════════════════════════════════════════════════════════════

1.1 PARTIES
───────────────────────────────────────────────────────────────────────────────
PLAINTIFF(S):
│ Name:           {{PLAINTIFF_NAME}}
│ Type:           [ ] Individual  [ ] Corporation  [ ] Government  [ ] Other
│ Citizenship:    {{CITIZENSHIP}}
│ Representation: {{COUNSEL_NAME}} ({{FIRM}})
│ Resources:      [ ] Limited  [ ] Moderate  [ ] Substantial
│ Motivation:     {{MOTIVATION_ASSESSMENT}}
│
DEFENDANT(S):
│ Name:           {{DEFENDANT_NAME}}
│ Type:           [ ] Individual  [ ] Corporation  [ ] Government  [ ] Other
│ Citizenship:    {{CITIZENSHIP}}
│ Representation: {{COUNSEL_NAME}} ({{FIRM}})
│ Resources:      [ ] Limited  [ ] Moderate  [ ] Substantial
│ Exposure Risk:  {{EXPOSURE_ASSESSMENT}}

1.2 CASE TYPE AND CLAIMS
───────────────────────────────────────────────────────────────────────────────
Case Type:        [ ] Contract  [ ] Tort  [ ] Civil Rights  [ ] Employment
                  [ ] IP  [ ] Securities  [ ] Antitrust  [ ] Other: _______

Claims Asserted:
┌──────┬────────────────────────────────┬──────────────┬────────────────────┐
│ # │ Claim                          │ Strength     │ Damages Potential  │
├──────┼────────────────────────────────┼──────────────┼────────────────────┤
│ 1    │ {{CLAIM_1}}                    │ {{SCORE}}/10 │ ${{RANGE}}         │
│ 2    │ {{CLAIM_2}}                    │ {{SCORE}}/10 │ ${{RANGE}}         │
│ 3    │ {{CLAIM_3}}                    │ {{SCORE}}/10 │ ${{RANGE}}         │
│ 4    │ {{CLAIM_4}}                    │ {{SCORE}}/10 │ ${{RANGE}}         │
└──────┴────────────────────────────────┴──────────────┴────────────────────┘

1.3 PROCEDURAL POSTURE
───────────────────────────────────────────────────────────────────────────────
Current Phase:     [ ] Pleading  [ ] Discovery  [ ] Dispositive  [ ] Trial
Case Age:          {{MONTHS}} months
Next Key Deadline: {{DEADLINE}} - {{DESCRIPTION}}
Trial Date:        {{TRIAL_DATE}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 2: JURISDICTIONAL ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

2.1 SUBJECT MATTER JURISDICTION
───────────────────────────────────────────────────────────────────────────────
Basis:  [ ] Federal Question (28 U.S.C. § 1331)
        [ ] Diversity (28 U.S.C. § 1332)
        [ ] Supplemental (28 U.S.C. § 1367)
        [ ] CAFA (28 U.S.C. § 1332(d))
        [ ] Other: _______________________

Assessment:
┌─────────────────────────────────────────────────────────────────────────────┐
│ JURISDICTIONAL STRENGTH:  {{SCORE}}/10                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ Analysis:                                                                   │
│ {{JURISDICTION_ANALYSIS}}                                                   │
│                                                                             │
│ Risks:                                                                      │
│ • {{RISK_1}}                                                                │
│ • {{RISK_2}}                                                                │
│                                                                             │
│ Recommendation: {{RECOMMENDATION}}                                          │
└─────────────────────────────────────────────────────────────────────────────┘

2.2 PERSONAL JURISDICTION
───────────────────────────────────────────────────────────────────────────────
Basis:  [ ] Consent  [ ] General (domicile)  [ ] Specific (minimum contacts)

Analysis: {{PERSONAL_JURISDICTION_ANALYSIS}}

2.3 VENUE
───────────────────────────────────────────────────────────────────────────────
Proper Venue:  [ ] Yes  [ ] Challenged  [ ] Transfer likely

Analysis: {{VENUE_ANALYSIS}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 3: CLAIMS ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

3.1 CLAIM-BY-CLAIM BREAKDOWN

┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLAIM 1: {{CLAIM_NAME}}                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ Legal Basis: {{STATUTE/COMMON_LAW}}                                         │
│ Limitations: {{SOL_DATE}} ({{TIME_REMAINING}})                              │
├─────────────────────────────────────────────────────────────────────────────┤
│ ELEMENTS:                                                                   │
│                                                                             │
│ Element 1: {{ELEMENT}}                                                      │
│   Status:     [ ] Established  [ ] Likely  [ ] Disputed  [ ] Weak          │
│   Evidence:   {{SUPPORTING_EVIDENCE}}                                       │
│   Gaps:       {{EVIDENCE_GAPS}}                                             │
│   Score:      {{SCORE}}/10                                                  │
│                                                                             │
│ Element 2: {{ELEMENT}}                                                      │
│   Status:     [ ] Established  [ ] Likely  [ ] Disputed  [ ] Weak          │
│   Evidence:   {{SUPPORTING_EVIDENCE}}                                       │
│   Gaps:       {{EVIDENCE_GAPS}}                                             │
│   Score:      {{SCORE}}/10                                                  │
│                                                                             │
│ Element 3: {{ELEMENT}}                                                      │
│   Status:     [ ] Established  [ ] Likely  [ ] Disputed  [ ] Weak          │
│   Evidence:   {{SUPPORTING_EVIDENCE}}                                       │
│   Gaps:       {{EVIDENCE_GAPS}}                                             │
│   Score:      {{SCORE}}/10                                                  │
│                                                                             │
│ Element 4: {{ELEMENT}}                                                      │
│   Status:     [ ] Established  [ ] Likely  [ ] Disputed  [ ] Weak          │
│   Evidence:   {{SUPPORTING_EVIDENCE}}                                       │
│   Gaps:       {{EVIDENCE_GAPS}}                                             │
│   Score:      {{SCORE}}/10                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ OVERALL CLAIM SCORE: {{TOTAL}}/40 = {{PERCENTAGE}}%                         │
│                                                                             │
│ VERDICT PROBABILITY:                                                        │
│   • Directed Verdict (D): {{X}}%                                            │
│   • Jury Verdict (D):     {{X}}%                                            │
│   • Jury Verdict (P):     {{X}}%                                            │
│   • Directed Verdict (P): {{X}}%                                            │
│                                                                             │
│ KEY RISKS: {{RISKS}}                                                        │
│ KEY STRENGTHS: {{STRENGTHS}}                                                │
└─────────────────────────────────────────────────────────────────────────────┘

[Repeat for each claim]

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 4: DEFENSE ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

4.1 AFFIRMATIVE DEFENSES ASSESSMENT

┌──────┬─────────────────────────────┬────────────┬───────────────────────────┐
│ #    │ Defense                     │ Viability  │ Impact if Successful      │
├──────┼─────────────────────────────┼────────────┼───────────────────────────┤
│ 1    │ Statute of Limitations      │ {{X}}/10   │ Complete bar              │
│ 2    │ Failure to Mitigate         │ {{X}}/10   │ Damages reduction         │
│ 3    │ Comparative Fault           │ {{X}}/10   │ Damages reduction         │
│ 4    │ Waiver/Estoppel             │ {{X}}/10   │ Complete/partial bar      │
│ 5    │ {{DEFENSE}}                 │ {{X}}/10   │ {{IMPACT}}                │
└──────┴─────────────────────────────┴────────────┴───────────────────────────┘

4.2 ANTICIPATED DEFENSE ARGUMENTS

For each defense:
• Legal basis
• Factual support
• Counter-arguments
• Evidence needed to defeat

{{DETAILED_DEFENSE_ANALYSIS}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 5: EVIDENCE ASSESSMENT
═══════════════════════════════════════════════════════════════════════════════

5.1 EVIDENCE INVENTORY

┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVIDENCE QUALITY MATRIX                              │
├────────────────────────┬────────────┬─────────────┬────────────────────────┤
│ Evidence Type          │ Available  │ Quality     │ Authentication         │
├────────────────────────┼────────────┼─────────────┼────────────────────────┤
│ Documentary            │ {{STATUS}} │ {{SCORE}}   │ {{STATUS}}             │
│ Testimonial            │ {{STATUS}} │ {{SCORE}}   │ N/A                    │
│ Expert                 │ {{STATUS}} │ {{SCORE}}   │ {{DAUBERT_STATUS}}     │
│ Physical               │ {{STATUS}} │ {{SCORE}}   │ {{STATUS}}             │
│ Electronic/Digital     │ {{STATUS}} │ {{SCORE}}   │ {{STATUS}}             │
└────────────────────────┴────────────┴─────────────┴────────────────────────┘

5.2 KEY DOCUMENTS

┌──────┬─────────────────────────────────┬────────────────┬───────────────────┐
│ #    │ Document                        │ Proves         │ Issues            │
├──────┼─────────────────────────────────┼────────────────┼───────────────────┤
│ 1    │ {{DOCUMENT}}                    │ {{ELEMENT}}    │ {{ISSUES}}        │
│ 2    │ {{DOCUMENT}}                    │ {{ELEMENT}}    │ {{ISSUES}}        │
│ 3    │ {{DOCUMENT}}                    │ {{ELEMENT}}    │ {{ISSUES}}        │
└──────┴─────────────────────────────────┴────────────────┴───────────────────┘

5.3 WITNESS ASSESSMENT

┌─────────────────────────────────────────────────────────────────────────────┐
│ WITNESS: {{NAME}}                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│ Role:              {{ROLE}}                                                 │
│ Knowledge:         {{KNOWLEDGE_SUMMARY}}                                    │
│ Credibility:       {{SCORE}}/10                                             │
│ Demeanor:          [ ] Excellent  [ ] Good  [ ] Fair  [ ] Poor  [ ] Unknown│
│ Cross-Exam Risk:   [ ] Low  [ ] Medium  [ ] High                            │
│ Bias/Interest:     {{BIAS_ASSESSMENT}}                                      │
│ Availability:      [ ] Cooperative  [ ] Reluctant  [ ] Hostile  [ ] Unknown│
└─────────────────────────────────────────────────────────────────────────────┘

[Repeat for each key witness]

5.4 EVIDENCE GAPS

Critical missing evidence:
1. {{GAP_1}} - Impact: {{IMPACT}} - Strategy to obtain: {{STRATEGY}}
2. {{GAP_2}} - Impact: {{IMPACT}} - Strategy to obtain: {{STRATEGY}}
3. {{GAP_3}} - Impact: {{IMPACT}} - Strategy to obtain: {{STRATEGY}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 6: DAMAGES ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

6.1 DAMAGES BREAKDOWN

┌─────────────────────────────────────────────────────────────────────────────┐
│                        DAMAGES CALCULATION                                   │
├─────────────────────────────────┬───────────────┬───────────────────────────┤
│ Category                        │ Amount        │ Confidence               │
├─────────────────────────────────┼───────────────┼───────────────────────────┤
│ ECONOMIC DAMAGES                │               │                          │
│   Direct/Actual                 │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Consequential                 │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Lost Profits                  │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Future Economic Loss          │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
├─────────────────────────────────┼───────────────┼───────────────────────────┤
│ NON-ECONOMIC DAMAGES            │               │                          │
│   Pain and Suffering            │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Emotional Distress            │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Loss of Consortium            │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Reputational Harm             │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
├─────────────────────────────────┼───────────────┼───────────────────────────┤
│ PUNITIVE DAMAGES                │               │                          │
│   Eligible?                     │ [ ] Yes [ ] No│                          │
│   Estimated Range               │ ${{RANGE}}    │ {{HIGH/MED/LOW}}         │
├─────────────────────────────────┼───────────────┼───────────────────────────┤
│ STATUTORY DAMAGES               │               │                          │
│   Attorneys' Fees               │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
│   Statutory Multiplier          │ ${{AMOUNT}}   │ {{HIGH/MED/LOW}}         │
├─────────────────────────────────┼───────────────┼───────────────────────────┤
│ TOTAL RANGE                     │               │                          │
│   Low Estimate                  │ ${{LOW}}      │                          │
│   Most Likely                   │ ${{LIKELY}}   │                          │
│   High Estimate                 │ ${{HIGH}}     │                          │
└─────────────────────────────────┴───────────────┴───────────────────────────┘

6.2 COMPARABLE VERDICTS

┌──────┬─────────────────────────────────┬─────────────┬───────────────────────┐
│ #    │ Case                            │ Verdict     │ Key Similarities      │
├──────┼─────────────────────────────────┼─────────────┼───────────────────────┤
│ 1    │ {{CASE_NAME}} ({{YEAR}})        │ ${{AMOUNT}} │ {{SIMILARITIES}}      │
│ 2    │ {{CASE_NAME}} ({{YEAR}})        │ ${{AMOUNT}} │ {{SIMILARITIES}}      │
│ 3    │ {{CASE_NAME}} ({{YEAR}})        │ ${{AMOUNT}} │ {{SIMILARITIES}}      │
└──────┴─────────────────────────────────┴─────────────┴───────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 7: STRATEGIC ASSESSMENT
═══════════════════════════════════════════════════════════════════════════════

7.1 STRENGTHS

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. {{STRENGTH}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    How to leverage: {{STRATEGY}}                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. {{STRENGTH}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    How to leverage: {{STRATEGY}}                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. {{STRENGTH}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    How to leverage: {{STRATEGY}}                                            │
└─────────────────────────────────────────────────────────────────────────────┘

7.2 WEAKNESSES

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. {{WEAKNESS}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    Mitigation strategy: {{STRATEGY}}                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. {{WEAKNESS}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    Mitigation strategy: {{STRATEGY}}                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. {{WEAKNESS}}                                                             │
│    Impact: {{HIGH/MEDIUM/LOW}}                                              │
│    Mitigation strategy: {{STRATEGY}}                                        │
└─────────────────────────────────────────────────────────────────────────────┘

7.3 OPPORTUNITIES

{{OPPORTUNITY_ANALYSIS}}

7.4 THREATS

{{THREAT_ANALYSIS}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 8: MOTION STRATEGY
═══════════════════════════════════════════════════════════════════════════════

8.1 RECOMMENDED MOTIONS

┌──────┬─────────────────────────────────┬────────────┬───────────────────────┐
│ Priority │ Motion                      │ Success %  │ Timing                │
├──────┼─────────────────────────────────┼────────────┼───────────────────────┤
│ 1    │ {{MOTION}}                      │ {{X}}%     │ {{TIMING}}            │
│ 2    │ {{MOTION}}                      │ {{X}}%     │ {{TIMING}}            │
│ 3    │ {{MOTION}}                      │ {{X}}%     │ {{TIMING}}            │
└──────┴─────────────────────────────────┴────────────┴───────────────────────┘

8.2 MOTION ANALYSIS

For each recommended motion:
• Legal standard
• Key arguments
• Supporting evidence
• Anticipated opposition
• Reply strategy
• Success probability

{{DETAILED_MOTION_ANALYSIS}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 9: DISCOVERY STRATEGY
═══════════════════════════════════════════════════════════════════════════════

9.1 DISCOVERY PRIORITIES

┌──────┬─────────────────────────────────┬────────────┬───────────────────────┐
│ Priority │ Discovery Need              │ Method     │ Target                │
├──────┼─────────────────────────────────┼────────────┼───────────────────────┤
│ 1    │ {{NEED}}                        │ {{METHOD}} │ {{TARGET}}            │
│ 2    │ {{NEED}}                        │ {{METHOD}} │ {{TARGET}}            │
│ 3    │ {{NEED}}                        │ {{METHOD}} │ {{TARGET}}            │
└──────┴─────────────────────────────────┴────────────┴───────────────────────┘

9.2 DEPOSITION STRATEGY

Recommended depositions in order:
1. {{WITNESS}} - Objectives: {{OBJECTIVES}}
2. {{WITNESS}} - Objectives: {{OBJECTIVES}}
3. {{WITNESS}} - Objectives: {{OBJECTIVES}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 10: SETTLEMENT ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

10.1 SETTLEMENT VALUATION

┌─────────────────────────────────────────────────────────────────────────────┐
│                      SETTLEMENT VALUE CALCULATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Expected Verdict Value:           ${{VERDICT_VALUE}}                        │
│ × Probability of Verdict:         {{X}}%                                    │
│ = Expected Recovery:              ${{EXPECTED}}                             │
│                                                                             │
│ - Litigation Costs to Trial:      ${{COSTS}}                                │
│ - Time Value Discount:            ${{DISCOUNT}}                             │
│ - Appeal Risk Adjustment:         ${{ADJUSTMENT}}                           │
│                                                                             │
│ = NET SETTLEMENT VALUE:           ${{NET_VALUE}}                            │
│                                                                             │
│ RECOMMENDED SETTLEMENT RANGE:     ${{LOW}} - ${{HIGH}}                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

10.2 SETTLEMENT LEVERAGE POINTS

Best times to settle:
1. {{LEVERAGE_POINT}} - Reason: {{REASON}}
2. {{LEVERAGE_POINT}} - Reason: {{REASON}}
3. {{LEVERAGE_POINT}} - Reason: {{REASON}}

═══════════════════════════════════════════════════════════════════════════════
                    SECTION 11: RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════════════════

11.1 IMMEDIATE ACTIONS (0-30 Days)

┌─────────────────────────────────────────────────────────────────────────────┐
│ [ ] {{ACTION_1}}                                                            │
│     Deadline: {{DATE}}                                                      │
│     Responsible: {{PERSON}}                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] {{ACTION_2}}                                                            │
│     Deadline: {{DATE}}                                                      │
│     Responsible: {{PERSON}}                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ [ ] {{ACTION_3}}                                                            │
│     Deadline: {{DATE}}                                                      │
│     Responsible: {{PERSON}}                                                 │
└─────────────────────────────────────────────────────────────────────────────┘

11.2 SHORT-TERM STRATEGY (30-90 Days)

{{SHORT_TERM_STRATEGY}}

11.3 LONG-TERM STRATEGY (90+ Days)

{{LONG_TERM_STRATEGY}}

11.4 FINAL RECOMMENDATION

{{FINAL_RECOMMENDATION}}

═══════════════════════════════════════════════════════════════════════════════
                              APPENDICES
═══════════════════════════════════════════════════════════════════════════════

APPENDIX A: Detailed Legal Research
APPENDIX B: Evidence Index
APPENDIX C: Witness Summaries
APPENDIX D: Damages Calculation Methodology
APPENDIX E: Comparable Cases Analysis
APPENDIX F: Timeline of Events
APPENDIX G: Document Index

═══════════════════════════════════════════════════════════════════════════════
              PRIVILEGED AND CONFIDENTIAL - ATTORNEY WORK PRODUCT
═══════════════════════════════════════════════════════════════════════════════

Prepared by: {{ATTORNEY_NAME}}
Date: {{DATE}}
Version: {{VERSION}}
```

---

## SCORING METHODOLOGY

### Case Viability Score (0-100)

| Component | Weight | Factors |
|-----------|--------|---------|
| **Claim Strength** | 30% | Elements satisfaction, legal authority, jury appeal |
| **Evidence Quality** | 25% | Authentication, credibility, completeness |
| **Defense Vulnerability** | 20% | Weakness of defenses, counterarguments |
| **Damages Potential** | 15% | Quantifiability, jury appeal, caps |
| **Procedural Position** | 10% | Jurisdiction, venue, limitations |

### Individual Element Scoring (0-10)

| Score | Meaning |
|-------|---------|
| 9-10 | Conclusively established |
| 7-8 | Strong evidence, likely to prove |
| 5-6 | Disputed, outcome uncertain |
| 3-4 | Weak evidence, uphill battle |
| 1-2 | Serious deficiency, unlikely to prove |
| 0 | Cannot establish element |

### Verdict Probability Assessment

| Factor | Impact |
|--------|--------|
| Strength of evidence | +/- 20% |
| Credibility of witnesses | +/- 15% |
| Complexity of issues | +/- 10% |
| Jury appeal | +/- 15% |
| Judge tendencies | +/- 10% |
| Defense resources | +/- 10% |

---

## USAGE INSTRUCTIONS

### When to Generate Analysis:

1. **New case intake** - Initial assessment
2. **Pre-motion filing** - Support motion strategy
3. **Pre-discovery** - Prioritize discovery needs
4. **Pre-mediation** - Settlement valuation
5. **Pre-trial** - Trial strategy refinement
6. **Periodic review** - Case status update

### Output Formats:

- Full analysis report (.md)
- Executive summary (1-2 pages)
- Risk matrix (visual)
- Action item checklist
- Timeline chart
