---
name: Strategy Scoring System
type: litigation-intelligence
output: strategy-scorecard
---

# LITIGATION STRATEGY SCORING SYSTEM

## Overview

This module provides a comprehensive scoring methodology for evaluating case strength, strategy effectiveness, and outcome probability.

---

## MASTER SCORECARD TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                       LITIGATION STRATEGY SCORECARD
═══════════════════════════════════════════════════════════════════════════════

CASE:          {{CASE_NAME}}
CASE NO:       {{CASE_NO}}
DATE:          {{DATE}}
PHASE:         {{CURRENT_PHASE}}

═══════════════════════════════════════════════════════════════════════════════
                         OVERALL CASE SCORE
═══════════════════════════════════════════════════════════════════════════════

                    ┌────────────────────────────┐
                    │                            │
                    │     CASE STRENGTH: {{X}}   │
                    │        /100                │
                    │                            │
                    │  ████████████░░░░░░░░░░░   │
                    │                            │
                    │   RATING: {{RATING}}       │
                    │                            │
                    └────────────────────────────┘

RATING SCALE:
  90-100: EXCELLENT - Highly likely to prevail
  75-89:  STRONG    - Favorable position
  60-74:  GOOD      - Better than even odds
  45-59:  NEUTRAL   - Outcome uncertain
  30-44:  WEAK      - Significant challenges
  0-29:   POOR      - Unlikely to prevail

═══════════════════════════════════════════════════════════════════════════════
                         COMPONENT SCORES
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  LIABILITY                                                                  │
│  ████████████████░░░░   {{LIABILITY_SCORE}}/100                            │
│                                                                             │
│  DAMAGES                                                                    │
│  ██████████████████░░   {{DAMAGES_SCORE}}/100                              │
│                                                                             │
│  EVIDENCE                                                                   │
│  ████████████████████   {{EVIDENCE_SCORE}}/100                             │
│                                                                             │
│  LEGAL AUTHORITY                                                            │
│  ██████████████░░░░░░   {{AUTHORITY_SCORE}}/100                            │
│                                                                             │
│  PROCEDURAL POSITION                                                        │
│  ████████████████████   {{PROCEDURAL_SCORE}}/100                           │
│                                                                             │
│  OPPOSING COUNSEL                                                           │
│  ████████████░░░░░░░░   {{OPPOSING_SCORE}}/100 (higher = weaker opponent)  │
│                                                                             │
│  JUDGE FAVORABILITY                                                         │
│  ██████████████████░░   {{JUDGE_SCORE}}/100                                │
│                                                                             │
│  JURY APPEAL                                                                │
│  ████████████████░░░░   {{JURY_SCORE}}/100                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                         LIABILITY ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

CLAIM-BY-CLAIM ELEMENT SCORING:

┌─────────────────────────────────────────────────────────────────────────────┐
│ CLAIM 1: {{CLAIM_NAME}}                                                     │
│ Legal Basis: {{STATUTE/RULE}}                                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Element 1: {{ELEMENT_NAME}}                                                 │
│ Score: {{X}}/10  █████████░  {{STATUS}}                                    │
│ Evidence: {{EVIDENCE_SUMMARY}}                                              │
│ Weakness: {{WEAKNESS}}                                                      │
│                                                                             │
│ Element 2: {{ELEMENT_NAME}}                                                 │
│ Score: {{X}}/10  ████████░░  {{STATUS}}                                    │
│ Evidence: {{EVIDENCE_SUMMARY}}                                              │
│ Weakness: {{WEAKNESS}}                                                      │
│                                                                             │
│ Element 3: {{ELEMENT_NAME}}                                                 │
│ Score: {{X}}/10  ██████░░░░  {{STATUS}}                                    │
│ Evidence: {{EVIDENCE_SUMMARY}}                                              │
│ Weakness: {{WEAKNESS}}                                                      │
│                                                                             │
│ Element 4: {{ELEMENT_NAME}}                                                 │
│ Score: {{X}}/10  █████████░  {{STATUS}}                                    │
│ Evidence: {{EVIDENCE_SUMMARY}}                                              │
│ Weakness: {{WEAKNESS}}                                                      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ CLAIM 1 TOTAL: {{X}}/40 = {{X}}%                                            │
│ Liability Probability: {{X}}%                                               │
│ Verdict Range: ${{LOW}} - ${{HIGH}}                                         │
└─────────────────────────────────────────────────────────────────────────────┘

[Repeat for each claim]

═══════════════════════════════════════════════════════════════════════════════
                         DEFENSE VULNERABILITY
═══════════════════════════════════════════════════════════════════════════════

AFFIRMATIVE DEFENSE ASSESSMENT:

┌─────────────────────────────┬────────┬────────┬─────────────────────────────┐
│ Defense                     │ Threat │ Our    │ Net                         │
│                             │ Level  │ Counter│ Position                    │
├─────────────────────────────┼────────┼────────┼─────────────────────────────┤
│ Statute of Limitations      │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ Failure to Mitigate         │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ Comparative Fault           │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ Assumption of Risk          │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ Waiver/Estoppel             │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ Qualified Immunity          │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
│ {{OTHER_DEFENSE}}           │ {{X}}/10│{{X}}/10│ {{FAVORABLE/NEUTRAL/RISK}} │
└─────────────────────────────┴────────┴────────┴─────────────────────────────┘

DEFENSE VULNERABILITY SCORE: {{X}}/100
(Higher = defenses are weaker, favors plaintiff)

═══════════════════════════════════════════════════════════════════════════════
                         DAMAGES SCORING
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                        DAMAGES PROBABILITY MATRIX                            │
├─────────────────────────────┬────────────┬────────────┬─────────────────────┤
│ Outcome                     │ Amount     │ Probability│ Expected Value      │
├─────────────────────────────┼────────────┼────────────┼─────────────────────┤
│ Defense Verdict             │ $0         │ {{X}}%     │ $0                  │
│ Nominal Damages             │ ${{X}}     │ {{X}}%     │ ${{X}}              │
│ Low-Range Verdict           │ ${{X}}     │ {{X}}%     │ ${{X}}              │
│ Mid-Range Verdict           │ ${{X}}     │ {{X}}%     │ ${{X}}              │
│ High-Range Verdict          │ ${{X}}     │ {{X}}%     │ ${{X}}              │
│ Maximum Damages             │ ${{X}}     │ {{X}}%     │ ${{X}}              │
├─────────────────────────────┼────────────┼────────────┼─────────────────────┤
│ EXPECTED VALUE              │            │ 100%       │ ${{TOTAL_EV}}       │
└─────────────────────────────┴────────────┴────────────┴─────────────────────┘

DAMAGES PROVABILITY SCORE: {{X}}/100

═══════════════════════════════════════════════════════════════════════════════
                         EVIDENCE QUALITY SCORE
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                        EVIDENCE ASSESSMENT MATRIX                            │
├─────────────────────────────┬────────────┬────────────┬─────────────────────┤
│ Evidence Category           │ Quality    │ Availability│ Authentication     │
├─────────────────────────────┼────────────┼────────────┼─────────────────────┤
│ Documentary Evidence        │ {{X}}/10   │ {{X}}/10   │ {{X}}/10           │
│ Witness Testimony           │ {{X}}/10   │ {{X}}/10   │ N/A                │
│ Expert Evidence             │ {{X}}/10   │ {{X}}/10   │ {{X}}/10 (Daubert) │
│ Physical Evidence           │ {{X}}/10   │ {{X}}/10   │ {{X}}/10           │
│ Electronic/Digital Evidence │ {{X}}/10   │ {{X}}/10   │ {{X}}/10           │
│ Admissions/Stipulations     │ {{X}}/10   │ {{X}}/10   │ N/A                │
├─────────────────────────────┼────────────┼────────────┼─────────────────────┤
│ AVERAGE SCORE               │ {{X}}/10   │ {{X}}/10   │ {{X}}/10           │
└─────────────────────────────┴────────────┴────────────┴─────────────────────┘

EVIDENCE QUALITY SCORE: {{X}}/100

KEY EVIDENCE GAPS:
1. {{GAP}} - Impact: {{HIGH/MED/LOW}} - Remediation: {{STRATEGY}}
2. {{GAP}} - Impact: {{HIGH/MED/LOW}} - Remediation: {{STRATEGY}}
3. {{GAP}} - Impact: {{HIGH/MED/LOW}} - Remediation: {{STRATEGY}}

═══════════════════════════════════════════════════════════════════════════════
                         MOTION SUCCESS PROBABILITY
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                        MOTION OUTCOME PREDICTIONS                            │
├─────────────────────────────┬────────────┬────────────┬─────────────────────┤
│ Motion                      │ Success %  │ Impact     │ Recommendation      │
├─────────────────────────────┼────────────┼────────────┼─────────────────────┤
│ Motion to Dismiss (12b6)    │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Motion to Dismiss (12b1)    │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Motion for Summary Judgment │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Motion to Compel Discovery  │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Motion in Limine            │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Motion for Sanctions        │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ TRO/Preliminary Injunction  │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
│ Daubert Motion              │ {{X}}%     │ {{X}}/10   │ {{FILE/SKIP}}       │
└─────────────────────────────┴────────────┴────────────┴─────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
                         SETTLEMENT ANALYSIS
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                      SETTLEMENT VALUE CALCULATION                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ INPUTS:                                                                     │
│   Expected Verdict Value:        ${{VERDICT}}                               │
│   Liability Probability:         {{X}}%                                     │
│   Litigation Costs to Trial:     ${{COSTS}}                                 │
│   Time to Resolution:            {{X}} months                               │
│   Discount Rate:                 {{X}}%                                     │
│   Appeal Risk:                   {{X}}%                                     │
│                                                                             │
│ CALCULATION:                                                                │
│   Expected Recovery:             ${{VERDICT}} × {{X}}% = ${{ER}}            │
│   Less Litigation Costs:         ${{ER}} - ${{COSTS}} = ${{NET1}}           │
│   Less Time Value:               ${{NET1}} × (1-{{X}}%) = ${{NET2}}         │
│   Less Appeal Risk:              ${{NET2}} × (1-{{X}}%) = ${{NET3}}         │
│                                                                             │
│ SETTLEMENT VALUE:                ${{SETTLEMENT_VALUE}}                      │
│                                                                             │
│ RECOMMENDED RANGE:               ${{LOW}} - ${{HIGH}}                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

OPTIMAL SETTLEMENT WINDOWS:
1. Pre-discovery: ${{AMOUNT}} - Leverage: {{DESCRIPTION}}
2. Post-discovery: ${{AMOUNT}} - Leverage: {{DESCRIPTION}}
3. Pre-trial: ${{AMOUNT}} - Leverage: {{DESCRIPTION}}

═══════════════════════════════════════════════════════════════════════════════
                         TRIAL OUTCOME PREDICTION
═══════════════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRIAL OUTCOME PROBABILITY                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                         JURY TRIAL                                          │
│                                                                             │
│  Plaintiff Verdict    ████████████████████░░░░░░░░░░   {{X}}%              │
│                                                                             │
│  Defense Verdict      ████████████░░░░░░░░░░░░░░░░░░   {{X}}%              │
│                                                                             │
│  Mistrial/Hung        ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░   {{X}}%              │
│                                                                             │
│                                                                             │
│                         BENCH TRIAL                                         │
│                                                                             │
│  Plaintiff Verdict    ██████████████████░░░░░░░░░░░░   {{X}}%              │
│                                                                             │
│  Defense Verdict      ████████████████░░░░░░░░░░░░░░   {{X}}%              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

TRIAL FACTORS:
• Jury Appeal:      {{FAVORABLE/NEUTRAL/UNFAVORABLE}}
• Complexity:       {{LOW/MEDIUM/HIGH}}
• Witness Quality:  {{STRONG/AVERAGE/WEAK}}
• Document Case:    {{YES/NO}}
• Sympathy Factor:  {{PLAINTIFF/NEUTRAL/DEFENDANT}}

═══════════════════════════════════════════════════════════════════════════════
                         STRATEGY RECOMMENDATIONS
═══════════════════════════════════════════════════════════════════════════════

PRIORITY ACTIONS:

┌────┬────────────────────────────────────────┬──────────┬───────────────────┐
│ #  │ Action                                 │ Priority │ Deadline          │
├────┼────────────────────────────────────────┼──────────┼───────────────────┤
│ 1  │ {{ACTION}}                             │ CRITICAL │ {{DATE}}          │
│ 2  │ {{ACTION}}                             │ HIGH     │ {{DATE}}          │
│ 3  │ {{ACTION}}                             │ HIGH     │ {{DATE}}          │
│ 4  │ {{ACTION}}                             │ MEDIUM   │ {{DATE}}          │
│ 5  │ {{ACTION}}                             │ MEDIUM   │ {{DATE}}          │
└────┴────────────────────────────────────────┴──────────┴───────────────────┘

STRATEGIC RECOMMENDATIONS:

1. {{RECOMMENDATION}}
2. {{RECOMMENDATION}}
3. {{RECOMMENDATION}}

═══════════════════════════════════════════════════════════════════════════════
              PRIVILEGED AND CONFIDENTIAL - ATTORNEY WORK PRODUCT
═══════════════════════════════════════════════════════════════════════════════
```

---

## SCORING RUBRICS

### Element Scoring (0-10)

| Score | Status | Evidence Level | Outcome |
|-------|--------|----------------|---------|
| 10 | Conclusive | Direct, uncontroverted proof | Directed verdict |
| 9 | Overwhelming | Multiple strong sources | Near-certain |
| 8 | Strong | Clear evidence, minor gaps | Likely to prevail |
| 7 | Good | Solid evidence, some dispute | Favorable |
| 6 | Above Average | Preponderance likely | Better than even |
| 5 | Even | Evidence balanced | Toss-up |
| 4 | Below Average | Burden is challenge | Uphill battle |
| 3 | Weak | Significant gaps | Unlikely |
| 2 | Very Weak | Minimal support | Remote chance |
| 1 | Minimal | Bare allegations | Near-impossible |
| 0 | None | Cannot establish | Dismissal likely |

### Motion Success Probability

| Probability | Assessment |
|-------------|------------|
| 80-100% | Highly likely to succeed; controlling authority supports |
| 60-79% | Good chance; strong arguments, favorable law |
| 40-59% | Uncertain; arguments on both sides |
| 20-39% | Unlikely; opposing arguments stronger |
| 0-19% | Very unlikely; file only to preserve issues |

### Settlement Calculation Formula

```
Settlement Value = (EV × LP) - LC - TVD - ARD

Where:
  EV  = Expected Verdict Value
  LP  = Liability Probability
  LC  = Litigation Costs
  TVD = Time Value Discount
  ARD = Appeal Risk Discount
```

---

## USAGE

Generate this scorecard:
- At case intake
- Before major motions
- Pre-mediation
- Quarterly review
- Pre-trial

Output formats:
- Full scorecard (.md)
- Summary (1 page)
- Visual dashboard
- Action checklist
