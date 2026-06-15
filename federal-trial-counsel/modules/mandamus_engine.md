---
name: Federal Writ of Mandamus Engine
type: litigation-module
court: U.S. District Court / U.S. Court of Appeals
authority: 28 U.S.C. § 1361, 28 U.S.C. § 1651 (All Writs Act)
activation: "Build Mandamus Case: [case name]"
---

# FEDERAL WRIT OF MANDAMUS ENGINE

## Overview

This module builds complete, filing-ready federal mandamus actions compelling a federal officer, agency, or court to perform a clear, nondiscretionary legal duty.

**Activation Command:** `Build Mandamus Case: [case name]`

---

## WORKSPACE GENERATION

When activated, generate the following directory structure:

```
/case-files/[case-name]/mandamus/
├── MANIFEST.md
├── pleadings/
│   ├── petition_for_writ_of_mandamus.md
│   ├── memorandum_of_law_iso_mandamus.md
│   └── civil_cover_sheet.md
├── motions/
│   ├── motion_to_expedite.md
│   └── motion_for_tro.md (if emergency)
├── orders/
│   └── proposed_order_granting_writ.md
├── supporting/
│   ├── declaration_template.md
│   ├── exhibit_index.md
│   └── service_certification.md
├── analysis/
│   ├── mandamus_viability_assessment.md
│   ├── timeline_chronology.md
│   └── risk_strategy_dashboard.md
└── summons.md
```

---

## THREE-ELEMENT MANDAMUS TEST

Every mandamus petition must establish ALL THREE elements:

### Element 1: Clear Legal Duty Owed by Government

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MINISTERIAL DUTY ANALYSIS                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ SOURCE OF DUTY:                                                             │
│ [ ] Federal Statute: _________________________________________________     │
│ [ ] Federal Regulation: ______________________________________________     │
│ [ ] Constitutional Provision: ________________________________________     │
│ [ ] Court Order/Rule: ________________________________________________     │
│                                                                             │
│ DUTY LANGUAGE:                                                              │
│ "The Secretary SHALL..." / "The agency MUST..." / "Within X days..."       │
│ ________________________________________________________________________   │
│ ________________________________________________________________________   │
│                                                                             │
│ MINISTERIAL vs. DISCRETIONARY:                                              │
│ [ ] MINISTERIAL - No judgment/discretion required; duty is mandatory       │
│ [ ] DISCRETIONARY - Agency has choice/judgment (NOT mandamus-able)         │
│                                                                             │
│ KEY DISTINCTION:                                                            │
│ • "Shall" / "must" / "within X days" = Ministerial                        │
│ • "May" / "in the Secretary's discretion" = Discretionary                 │
│                                                                             │
│ SUPPORTING AUTHORITY:                                                       │
│ ________________________________________________________________________   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Element 2: Plaintiff's Clear Right to Relief

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ RIGHT TO RELIEF ANALYSIS                                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ LEGAL BASIS FOR ENTITLEMENT:                                               │
│ [ ] Statutory beneficiary of duty                                          │
│ [ ] Constitutional right                                                   │
│ [ ] Regulatory entitlement                                                 │
│ [ ] Court-ordered action                                                   │
│                                                                             │
│ SPECIFIC RIGHT CLAIMED:                                                     │
│ ________________________________________________________________________   │
│                                                                             │
│ STANDING REQUIREMENTS:                                                      │
│ [ ] Injury in fact - concrete and particularized                          │
│ [ ] Causation - traceable to defendant's inaction                         │
│ [ ] Redressability - court order would remedy injury                      │
│                                                                             │
│ PLAINTIFF'S COMPLIANCE:                                                     │
│ [ ] Application/request properly filed                                     │
│ [ ] Required documentation submitted                                       │
│ [ ] Fees paid                                                              │
│ [ ] All prerequisites satisfied                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Element 3: No Adequate Alternative Remedy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ ALTERNATIVE REMEDY ANALYSIS                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ POTENTIAL ALTERNATIVES (must show inadequacy of each):                     │
│                                                                             │
│ [ ] Administrative Appeal                                                   │
│     Inadequate because: ______________________________________________     │
│     [ ] No final decision to appeal                                        │
│     [ ] Would be futile                                                    │
│     [ ] Unreasonable delay in process                                      │
│                                                                             │
│ [ ] APA Review (5 U.S.C. § 706)                                           │
│     Inadequate because: ______________________________________________     │
│     [ ] No final agency action                                             │
│     [ ] Agency inaction unreviewable                                       │
│                                                                             │
│ [ ] Other Civil Action                                                      │
│     Inadequate because: ______________________________________________     │
│                                                                             │
│ [ ] Direct Appeal                                                           │
│     Inadequate because: ______________________________________________     │
│                                                                             │
│ EXHAUSTION ANALYSIS:                                                        │
│ [ ] Exhaustion required - has been completed                               │
│ [ ] Exhaustion required - excused because: ____________________________   │
│ [ ] Exhaustion not required                                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## TRAC FACTORS (Unreasonable Delay Analysis)

When challenging agency delay, apply the six TRAC factors from *Telecommunications Research & Action Center v. FCC*, 750 F.2d 70 (D.C. Cir. 1984):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ TRAC UNREASONABLE DELAY ANALYSIS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ FACTOR 1: Rule of Reason (Congressional Timetable)                         │
│ Is there a statutory deadline?  [ ] Yes: ____________  [ ] No              │
│ Has deadline passed?            [ ] Yes  [ ] No                            │
│ If no deadline, what is reasonable? ___________________________________    │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ FACTOR 2: Congressional Priority                                            │
│ Did Congress indicate priority for this action?                            │
│ Evidence: ______________________________________________________________   │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ FACTOR 3: Prejudice to Human Health/Welfare                                │
│ Does delay prejudice health, welfare, or human life?                       │
│ [ ] Yes - Describe: ___________________________________________________   │
│ [ ] No                                                                      │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ FACTOR 4: Effect on Other Agency Actions                                   │
│ Would compelling action delay other important matters?                     │
│ [ ] Minimal impact  [ ] Moderate impact  [ ] Significant impact           │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ FACTOR 5: Nature and Extent of Interests Prejudiced                        │
│ What interests are prejudiced by delay?                                    │
│ Financial: $____________________________________________________________   │
│ Personal: ______________________________________________________________   │
│ Business: ______________________________________________________________   │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ FACTOR 6: Agency Impropriety (Bad Faith)                                   │
│ Is there evidence of agency bad faith or improper motive?                  │
│ [ ] Yes - Describe: ___________________________________________________   │
│ [ ] No                                                                      │
│ Score: [ ] Strongly favors plaintiff  [ ] Neutral  [ ] Favors agency      │
│                                                                             │
│ ═══════════════════════════════════════════════════════════════════════════│
│ TRAC OVERALL ASSESSMENT:                                                    │
│ [ ] Unreasonable delay clearly established                                 │
│ [ ] Unreasonable delay likely established                                  │
│ [ ] Unreasonable delay uncertain                                           │
│ [ ] Delay appears reasonable                                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## PETITION FOR WRIT OF MANDAMUS TEMPLATE

```
UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA
ORLANDO DIVISION

{{PETITIONER_NAME}},
                                    Petitioner,

v.                                              Case No. ____________

{{RESPONDENT_NAME}}, in [his/her]
official capacity as {{TITLE}},
                                    Respondent.
_______________________________________/

              PETITION FOR WRIT OF MANDAMUS

     Petitioner {{PETITIONER_NAME}} respectfully petitions this Court for
a writ of mandamus pursuant to 28 U.S.C. § 1361 [and/or the All Writs Act,
28 U.S.C. § 1651] compelling Respondent to [describe specific action].

                             JURISDICTION

     1.   This Court has jurisdiction under 28 U.S.C. § 1361, which
provides that "[t]he district courts shall have original jurisdiction of
any action in the nature of mandamus to compel an officer or employee of
the United States or any agency thereof to perform a duty owed to the
plaintiff."

     2.   [If invoking All Writs Act:] This Court also has jurisdiction
under 28 U.S.C. § 1651(a), the All Writs Act, which authorizes federal
courts to "issue all writs necessary or appropriate in aid of their
respective jurisdictions."

                               VENUE

     3.   Venue is proper in this district under 28 U.S.C. § 1391(e)(1)
because [Respondent resides in this district / a substantial part of the
events giving rise to the claim occurred here / Petitioner resides here
and no real property is involved].

                              PARTIES

     4.   Petitioner {{PETITIONER_NAME}} is [describe - individual,
corporation, etc.] who [describe connection to the claim].

     5.   Respondent {{RESPONDENT_NAME}} is [title], an officer of the
United States [or agency of the United States], sued in [his/her] official
capacity. Respondent is responsible for [describe relevant duties].

                         STATEMENT OF FACTS

     6.   [Chronological statement of facts - use timeline format]

     7.   On {{DATE}}, Petitioner [filed application / submitted request /
took required action].

     8.   Under {{STATUTE/REGULATION}}, Respondent was required to
[describe mandatory action] within [timeframe / upon occurrence of X].

     9.   [Continue factual narrative with specific dates and actions]

     10.  As of the date of this Petition, [X days/months/years] have
passed since [triggering event], and Respondent has failed to [perform
required duty].

     11.  Petitioner has made the following efforts to obtain action:
          a. [Date] - [Action taken]
          b. [Date] - [Action taken]
          c. [Date] - [Action taken]

     12.  Respondent has [refused to act / failed to respond / provided
inadequate response].

            IDENTIFICATION OF CLEAR, NONDISCRETIONARY DUTY

     13.  {{STATUTE/REGULATION}} imposes a clear, nondiscretionary duty
on Respondent to [describe duty].

     14.  The statutory language is mandatory: "[Quote relevant language
showing 'shall,' 'must,' or mandatory timeframe]."

     15.  This duty is ministerial, not discretionary, because [explain
why no judgment or discretion is involved].

                    UNREASONABLE DELAY OR REFUSAL

     16.  Respondent has unreasonably delayed [or refused] to perform the
mandatory duty by [describe the delay/refusal].

     17.  [If delay case:] Applying the TRAC factors:
          a. [Factor 1 analysis]
          b. [Factor 2 analysis]
          c. [Factor 3 analysis]
          d. [Factor 4 analysis]
          e. [Factor 5 analysis]
          f. [Factor 6 analysis]

                      HARM FROM INACTION

     18.  Petitioner has suffered and continues to suffer harm as a direct
result of Respondent's failure to act, including:
          a. [Specific harm 1]
          b. [Specific harm 2]
          c. [Specific harm 3]

     19.  [Describe irreparable nature of harm if applicable]

                   NO ADEQUATE ALTERNATIVE REMEDY

     20.  Petitioner has no adequate remedy at law or through
administrative channels because:
          a. [Explain why administrative appeal is inadequate]
          b. [Explain why APA review is inadequate]
          c. [Explain why other civil action is inadequate]

     21.  [If exhaustion issue:] Exhaustion of administrative remedies
is [complete / not required / excused] because [explain].

                    CAUSE OF ACTION — MANDAMUS

     22.  Petitioner incorporates all preceding paragraphs.

     23.  Respondent owes Petitioner a clear, nondiscretionary duty under
{{STATUTE/REGULATION}} to [describe duty].

     24.  Petitioner has a clear right to the performance of this duty
because [explain legal entitlement].

     25.  Petitioner has no adequate alternative remedy.

     26.  Respondent has unreasonably delayed [or refused] to perform
this duty.

     27.  Petitioner is entitled to a writ of mandamus compelling
Respondent to [specific action requested].

                        PRAYER FOR RELIEF

     WHEREFORE, Petitioner respectfully requests that this Court:

     a.   Issue a writ of mandamus compelling Respondent to [specific
action] within [timeframe];

     b.   [If applicable:] Declare that Respondent has violated
{{STATUTE/REGULATION}} by failing to [perform duty];

     c.   Order Respondent to file status reports every [30 days] until
compliance is achieved;

     d.   Award Petitioner costs and attorneys' fees under the Equal
Access to Justice Act, 28 U.S.C. § 2412, if applicable;

     e.   Grant such other relief as the Court deems just and proper.

          REQUEST FOR EXPEDITED CONSIDERATION

     28.  Petitioner respectfully requests expedited consideration of
this Petition because [explain urgency - ongoing harm, statutory deadline,
emergency circumstances].

                                        Respectfully submitted,

                                        /s/ {{ATTORNEY_NAME}}
                                        {{ATTORNEY_NAME}}
                                        Florida Bar No. {{BAR_NO}}
                                        {{FIRM_NAME}}
                                        {{ADDRESS}}
                                        Telephone: {{PHONE}}
                                        Email: {{EMAIL}}

                                        Counsel for Petitioner

                         CERTIFICATE OF SERVICE

     I HEREBY CERTIFY that on {{DATE}}, a true and correct copy of the
foregoing was served upon:

     [Respondent's counsel / U.S. Attorney's Office]
     [Address]

via [CM/ECF / certified mail / personal service].

                                        /s/ {{ATTORNEY_NAME}}
                                        {{ATTORNEY_NAME}}
```

---

## MEMORANDUM OF LAW IN SUPPORT OF MANDAMUS

```
UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA
ORLANDO DIVISION

{{PETITIONER_NAME}},
                                    Petitioner,

v.                                              Case No. {{CASE_NO}}

{{RESPONDENT_NAME}},
                                    Respondent.
_______________________________________/

          MEMORANDUM OF LAW IN SUPPORT OF
           PETITION FOR WRIT OF MANDAMUS

                         INTRODUCTION

     [1-2 paragraph summary of case and why mandamus is appropriate]

                      STATEMENT OF FACTS

     [Detailed factual background with record citations]

                           ARGUMENT

I. THIS COURT HAS JURISDICTION TO ISSUE A WRIT OF MANDAMUS

     A. Jurisdiction Under 28 U.S.C. § 1361

     Section 1361 grants district courts "original jurisdiction of any
action in the nature of mandamus to compel an officer or employee of the
United States or any agency thereof to perform a duty owed to the
plaintiff." 28 U.S.C. § 1361.

     [Apply to facts]

     B. Jurisdiction Under the All Writs Act (If Applicable)

     [Analysis under 28 U.S.C. § 1651]

II. PETITIONER SATISFIES ALL REQUIREMENTS FOR MANDAMUS RELIEF

     The Supreme Court has established that mandamus relief requires three
elements: "(1) a clear right in the plaintiff to the relief sought; (2) a
clear duty on the part of the defendant to do the act in question; and
(3) no other adequate remedy available." Cash v. Barnhart, 327 F.3d 1252,
1258 (11th Cir. 2003).

     A. Respondent Owes Petitioner a Clear, Nondiscretionary Duty

     [Identify statute/regulation creating mandatory duty]

     "A duty is ministerial only when it is 'a positive command [that]
... require[s] the performance of a specified act.'" Pittston Coal Grp.
v. Sebben, 488 U.S. 105, 121 (1988).

     [Apply to facts showing duty is mandatory, not discretionary]

     B. Petitioner Has a Clear Right to Relief

     [Establish legal entitlement and standing]

     C. Petitioner Has No Adequate Alternative Remedy

     [Analyze and reject each potential alternative]

III. RESPONDENT HAS UNREASONABLY DELAYED PERFORMING ITS DUTY

     [Apply TRAC factors if delay case]

     [Or explain outright refusal]

IV. THE BALANCE OF EQUITIES FAVORS MANDAMUS

     [Discuss harm to petitioner vs. burden on agency]

V. SEPARATION OF POWERS CONCERNS DO NOT BAR RELIEF

     "Mandamus does not infringe on executive discretion when directed
at ministerial acts." [cite authority]

     [Address any separation of powers concerns]

                         CONCLUSION

     For the foregoing reasons, Petitioner respectfully requests that
this Court grant the Petition for Writ of Mandamus.

                                        Respectfully submitted,

                                        /s/ {{ATTORNEY_NAME}}
                                        {{ATTORNEY_NAME}}
                                        Counsel for Petitioner
```

---

## PROPOSED ORDER GRANTING WRIT

```
UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA
ORLANDO DIVISION

{{PETITIONER_NAME}},
                                    Petitioner,
v.                                              Case No. {{CASE_NO}}

{{RESPONDENT_NAME}},
                                    Respondent.
_______________________________________/

              ORDER GRANTING WRIT OF MANDAMUS

     THIS CAUSE is before the Court on Petitioner's Petition for Writ of
Mandamus (Doc. __). Having considered the Petition, Respondent's response,
and the applicable law, and being otherwise fully advised, it is hereby

     ORDERED AND ADJUDGED:

     1.   The Petition for Writ of Mandamus is GRANTED.

     2.   A peremptory writ of mandamus is hereby ISSUED commanding
Respondent {{RESPONDENT_NAME}}, in [his/her] official capacity as
{{TITLE}}, to [describe specific action required] within [X] days of
the date of this Order.

     3.   Respondent shall file a status report with this Court within
[X] days of the date of this Order, and every [30] days thereafter,
confirming compliance with this Order.

     4.   The Court retains jurisdiction to enforce this Order and to
address any issues arising from Respondent's compliance.

     5.   [If fees awarded:] Petitioner is awarded reasonable attorneys'
fees and costs under [28 U.S.C. § 2412 / other authority], in an amount
to be determined upon proper application.

     DONE AND ORDERED in Chambers at Orlando, Florida, this ____ day of
_____________, 20___.


                                        _______________________________
                                        UNITED STATES DISTRICT JUDGE
```

---

## MOTION TO EXPEDITE

```
UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA
ORLANDO DIVISION

{{PETITIONER_NAME}},
                                    Petitioner,

v.                                              Case No. {{CASE_NO}}

{{RESPONDENT_NAME}},
                                    Respondent.
_______________________________________/

                    MOTION TO EXPEDITE

     Petitioner {{PETITIONER_NAME}} respectfully moves this Court for
expedited consideration of the Petition for Writ of Mandamus and states:

I. INTRODUCTION

     This case involves [describe urgency]. Petitioner seeks expedited
briefing and decision because [explain why normal schedule is inadequate].

II. GOOD CAUSE FOR EXPEDITED CONSIDERATION

     Expedited consideration is warranted because:

     1.   [Ongoing irreparable harm]
     2.   [Statutory deadline at issue]
     3.   [Time-sensitive circumstances]
     4.   [Other urgency factors]

III. PROPOSED SCHEDULE

     Petitioner respectfully proposes the following expedited schedule:

     Response deadline:    [X] days from date of this motion
     Reply deadline:       [X] days from response
     Hearing:              At the Court's earliest convenience

IV. CONCLUSION

     For these reasons, Petitioner respectfully requests that the Court
grant this Motion and set an expedited briefing schedule.

                                        Respectfully submitted,

                                        /s/ {{ATTORNEY_NAME}}
                                        {{ATTORNEY_NAME}}
                                        Counsel for Petitioner
```

---

## EXHIBIT INDEX TEMPLATE

```
═══════════════════════════════════════════════════════════════════════════════
                    EXHIBIT INDEX — MANDAMUS PETITION
═══════════════════════════════════════════════════════════════════════════════

CATEGORY A — STATUTES / REGULATIONS IMPOSING DUTY

Exhibit A-1:  {{Statute citation}} (imposing duty to [action])
Exhibit A-2:  {{Regulation citation}} (implementing [statute])
Exhibit A-3:  [Additional authority]

CATEGORY B — CORRESPONDENCE WITH AGENCY

Exhibit B-1:  Letter from Petitioner to [Agency] dated {{DATE}}
              (initial request for [action])
Exhibit B-2:  [Agency] acknowledgment letter dated {{DATE}}
Exhibit B-3:  Follow-up letter from Petitioner dated {{DATE}}
Exhibit B-4:  [Additional correspondence]

CATEGORY C — PROOF OF SUBMISSION / APPLICATION

Exhibit C-1:  Application form submitted {{DATE}}
Exhibit C-2:  Receipt confirmation
Exhibit C-3:  Payment confirmation / fee receipt
Exhibit C-4:  [Additional submission documentation]

CATEGORY D — DELAY EVIDENCE

Exhibit D-1:  Timeline showing [X] days elapsed since [triggering event]
Exhibit D-2:  [Agency] processing statistics showing average time
Exhibit D-3:  Comparative data showing Petitioner's delay exceeds norm
Exhibit D-4:  [Additional delay evidence]

CATEGORY E — HARM DOCUMENTATION

Exhibit E-1:  Declaration of {{NAME}} regarding harm suffered
Exhibit E-2:  Financial records showing [economic harm]
Exhibit E-3:  [Medical records / business records / other harm evidence]
Exhibit E-4:  [Additional harm documentation]

CATEGORY F — ADMINISTRATIVE RECORD (if applicable)

Exhibit F-1:  Agency decision / letter
Exhibit F-2:  Administrative appeal (if filed)
Exhibit F-3:  [Additional administrative record documents]
```

---

## CHRONOLOGICAL TIMELINE ENGINE

```
═══════════════════════════════════════════════════════════════════════════════
                    MANDAMUS CASE TIMELINE
═══════════════════════════════════════════════════════════════════════════════

MATTER:         {{PETITIONER}} v. {{RESPONDENT}}
PREPARED:       {{DATE}}

┌──────────────┬───────────────────────────────────────────────────────────────┐
│ DATE         │ EVENT                                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ TRIGGERING EVENT: [Application filed / Request made]         │
│              │ Document: Exhibit C-1                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ STATUTORY DEADLINE: [X days from application per § ___]      │
│              │ *** DEADLINE PASSED ***                                       │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ Petitioner sent follow-up inquiry                            │
│              │ Document: Exhibit B-3                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ Agency response: [Describe response or non-response]         │
│              │ Document: Exhibit B-4                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ HARM EVENT: [Describe specific harm that occurred]           │
│              │ Document: Exhibit E-1                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ Demand letter sent to agency                                 │
│              │ Document: Exhibit B-5                                         │
├──────────────┼───────────────────────────────────────────────────────────────┤
│ {{DATE}}     │ PETITION FILED                                               │
│              │ Days elapsed since application: [___]                        │
│              │ Days past statutory deadline: [___]                          │
└──────────────┴───────────────────────────────────────────────────────────────┘

DELAY SUMMARY:
• Total days since initial request: [___]
• Days past statutory deadline (if any): [___]
• Number of follow-up attempts: [___]
• Agency responses received: [___]
```

---

## MANDAMUS VIABILITY ASSESSMENT

```
═══════════════════════════════════════════════════════════════════════════════
              MANDAMUS VIABILITY ASSESSMENT & RISK DASHBOARD
═══════════════════════════════════════════════════════════════════════════════

MATTER:         {{PETITIONER}} v. {{RESPONDENT}}
ASSESSED BY:    {{ATTORNEY}}
DATE:           {{DATE}}

┌─────────────────────────────────────────────────────────────────────────────┐
│ ELEMENT SCORING                                                             │
├─────────────────────────────────────┬──────────────────┬────────────────────┤
│ Element                             │ Score (0-100)    │ Assessment         │
├─────────────────────────────────────┼──────────────────┼────────────────────┤
│ 1. Clear Ministerial Duty           │ {{X}}/100        │ [Strong/Mod/Weak]  │
│    • Statute uses mandatory language│                  │                    │
│    • No discretion involved         │                  │                    │
│    • Duty is specific and defined   │                  │                    │
├─────────────────────────────────────┼──────────────────┼────────────────────┤
│ 2. Clear Right to Relief            │ {{X}}/100        │ [Strong/Mod/Weak]  │
│    • Standing established           │                  │                    │
│    • Legal entitlement clear        │                  │                    │
│    • All prerequisites met          │                  │                    │
├─────────────────────────────────────┼──────────────────┼────────────────────┤
│ 3. No Adequate Alternative Remedy   │ {{X}}/100        │ [Strong/Mod/Weak]  │
│    • Admin appeal inadequate        │                  │                    │
│    • APA review unavailable         │                  │                    │
│    • Other remedies insufficient    │                  │                    │
├─────────────────────────────────────┼──────────────────┼────────────────────┤
│ 4. Unreasonable Delay/Refusal       │ {{X}}/100        │ [Strong/Mod/Weak]  │
│    • TRAC factors favor petitioner  │                  │                    │
│    • Delay is documented            │                  │                    │
│    • No legitimate justification    │                  │                    │
├─────────────────────────────────────┼──────────────────┼────────────────────┤
│ OVERALL VIABILITY SCORE             │ {{X}}/100        │                    │
└─────────────────────────────────────┴──────────────────┴────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ RISK ASSESSMENT                                                             │
├─────────────────────────────────────┬───────────────────────────────────────┤
│ Risk Factor                         │ Assessment                            │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Jurisdiction Challenge Risk         │ [ ] High  [ ] Medium  [ ] Low        │
│ (12(b)(1) dismissal probability)    │ Notes: _____________________________ │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Failure to State Claim Risk         │ [ ] High  [ ] Medium  [ ] Low        │
│ (12(b)(6) dismissal probability)    │ Notes: _____________________________ │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Discretionary Function Defense      │ [ ] High  [ ] Medium  [ ] Low        │
│ (Agency argues discretion)          │ Notes: _____________________________ │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Exhaustion Defense Risk             │ [ ] High  [ ] Medium  [ ] Low        │
│ (Admin remedies not exhausted)      │ Notes: _____________________________ │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Sovereign Immunity Risk             │ [ ] High  [ ] Medium  [ ] Low        │
│ (Immunity bars suit)                │ Notes: _____________________________ │
├─────────────────────────────────────┼───────────────────────────────────────┤
│ Separation of Powers Concern        │ [ ] High  [ ] Medium  [ ] Low        │
│ (Court reluctant to order agency)   │ Notes: _____________________________ │
└─────────────────────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ JUDICIAL PERSPECTIVE ASSESSMENT                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ How will the court likely view this petition?                              │
│                                                                             │
│ Duty Analysis:        [ ] Clearly ministerial  [ ] Arguably ministerial    │
│                       [ ] Likely discretionary                             │
│                                                                             │
│ Delay Assessment:     [ ] Egregious delay  [ ] Significant delay          │
│                       [ ] Moderate delay   [ ] Arguably reasonable        │
│                                                                             │
│ Harm Assessment:      [ ] Severe/irreparable  [ ] Significant             │
│                       [ ] Moderate            [ ] Minimal                 │
│                                                                             │
│ Government Defense:   [ ] Weak defenses likely  [ ] Moderate defenses     │
│                       [ ] Strong defenses likely                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STRATEGIC RECOMMENDATIONS                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ PROCEED WITH MANDAMUS?                                                      │
│ [ ] YES - Strong case, recommend immediate filing                          │
│ [ ] YES - With modifications: ___________________________________________ │
│ [ ] CONDITIONAL - Address issues first: _________________________________ │
│ [ ] NO - Alternative approach recommended: ______________________________ │
│                                                                             │
│ RECOMMENDED ACTIONS:                                                        │
│ 1. ___________________________________________________________________     │
│ 2. ___________________________________________________________________     │
│ 3. ___________________________________________________________________     │
│                                                                             │
│ ESTIMATED TIMELINE TO RULING: ________________________________________     │
│                                                                             │
│ APPEAL LIKELIHOOD (if denied): [ ] High  [ ] Medium  [ ] Low              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## JURISDICTION DEFENSE SHIELD

### Preemptive Analysis of Government Defenses

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DEFENSE PREEMPTION ANALYSIS                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ SOVEREIGN IMMUNITY DEFENSE                                                  │
│ Expected argument: United States cannot be sued without consent            │
│ Counter: Mandamus under § 1361 is an established waiver for ministerial   │
│          duties; suit is against officer in official capacity              │
│ Supporting authority: _________________________________________________   │
│                                                                             │
│ DISCRETIONARY FUNCTION DEFENSE                                              │
│ Expected argument: Action requested involves agency discretion             │
│ Counter: [Quote mandatory statutory language; distinguish from             │
│          discretionary decisions]                                          │
│ Supporting authority: _________________________________________________   │
│                                                                             │
│ EXHAUSTION DEFENSE                                                          │
│ Expected argument: Petitioner failed to exhaust administrative remedies   │
│ Counter: [Exhaustion complete / not required / excused because ___]       │
│ Supporting authority: _________________________________________________   │
│                                                                             │
│ ADEQUATE ALTERNATIVE REMEDY DEFENSE                                         │
│ Expected argument: APA review / admin appeal is adequate alternative      │
│ Counter: [Explain why alternatives are inadequate]                        │
│ Supporting authority: _________________________________________________   │
│                                                                             │
│ MOOTNESS DEFENSE                                                            │
│ Expected argument: Agency took action, case is moot                       │
│ Counter: [Action incomplete / capable of repetition yet evading review]   │
│ Supporting authority: _________________________________________________   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## KEY MANDAMUS AUTHORITY

### Controlling Cases

| Case | Holding | Use For |
|------|---------|---------|
| *Heckler v. Ringer*, 466 U.S. 602 (1984) | Three-element mandamus test | Establishing standard |
| *Cash v. Barnhart*, 327 F.3d 1252 (11th Cir. 2003) | 11th Circuit mandamus standard | Circuit authority |
| *TRAC v. FCC*, 750 F.2d 70 (D.C. Cir. 1984) | Six-factor delay test | Unreasonable delay |
| *Norton v. S. Utah Wilderness Alliance*, 542 U.S. 55 (2004) | Discrete vs. programmatic duty | Defining actionable duty |
| *Pittston Coal Grp. v. Sebben*, 488 U.S. 105 (1988) | Ministerial duty definition | Distinguishing discretion |

### Statutory Authority

| Statute | Purpose |
|---------|---------|
| 28 U.S.C. § 1361 | District court mandamus jurisdiction |
| 28 U.S.C. § 1651 | All Writs Act (supplemental authority) |
| 28 U.S.C. § 2412 | Equal Access to Justice Act (fees) |
| 5 U.S.C. § 706(1) | APA - compel agency action unlawfully withheld |

---

## OUTPUT CHECKLIST

When `Build Mandamus Case: [case name]` is activated, generate:

```
[ ] MANIFEST.md - File index
[ ] petition_for_writ_of_mandamus.md - Main petition
[ ] memorandum_of_law_iso_mandamus.md - Legal brief
[ ] proposed_order_granting_writ.md - Draft order
[ ] civil_cover_sheet.md - JS-44 information
[ ] summons.md - Service documents
[ ] exhibit_index.md - Categorized exhibits (A-F)
[ ] declaration_template.md - Supporting declaration
[ ] service_certification.md - Proof of service
[ ] timeline_chronology.md - Dated event log
[ ] mandamus_viability_assessment.md - Risk/strategy dashboard
[ ] motion_to_expedite.md - If urgency exists
[ ] motion_for_tro.md - If immediate harm (emergency only)
```
