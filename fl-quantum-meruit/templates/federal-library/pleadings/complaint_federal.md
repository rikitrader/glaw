---
name: Federal Civil Complaint
court: U.S. District Court, Middle District of Florida
rule: FRCP Rule 8
integration: federal_pleading_engine
---

# FEDERAL CIVIL COMPLAINT TEMPLATE

## Integration with Federal Pleading Engine

This template integrates with the Federal Pleading Engine for elements-based drafting:

**Location:** `scripts/federal_pleading_engine/`

**Process:**
1. Create `CASE_INPUT` JSON with facts, parties, and claims
2. Run `node dist/cli.js --input case.json --suggest` to identify viable claims
3. Run `node dist/cli.js --input case.json --out ./output` to generate draft
4. Review MTD Risk Score and address fact gaps
5. Customize generated counts with case-specific details
6. Verify Twombly/Iqbal plausibility for each element

**Supported Claims:** 40+ federal causes of action with elements definitions

---

```
UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA
ORLANDO DIVISION

{{PLAINTIFF_NAME}},
                                    Plaintiff,

v.                                              Case No. {{CASE_NO}}

{{DEFENDANT_NAME}},
                                    Defendant.
_______________________________________/

                              COMPLAINT

     Plaintiff, {{PLAINTIFF_NAME}}, by and through undersigned counsel, hereby
sues Defendant, {{DEFENDANT_NAME}}, and alleges as follows:

                         NATURE OF THE ACTION

     1. This is an action for [describe nature - e.g., breach of contract,
civil rights violations under 42 U.S.C. § 1983, federal statutory claims].

     2. Plaintiff seeks [monetary damages / injunctive relief / declaratory
judgment] arising from Defendant's [brief description of wrongful conduct].

                              PARTIES

     3. Plaintiff {{PLAINTIFF_NAME}} is [a citizen of the State of _________ /
a corporation organized under the laws of _________ with its principal place of
business in _________], residing at [address].

     4. Defendant {{DEFENDANT_NAME}} is [a citizen of the State of _________ /
a corporation organized under the laws of _________ with its principal place of
business in _________], with an address at [address].

                            JURISDICTION

     5. This Court has subject matter jurisdiction pursuant to:

        [ ] 28 U.S.C. § 1331 (federal question) because this action arises
            under the Constitution and laws of the United States, specifically
            [cite federal statute or constitutional provision].

        [ ] 28 U.S.C. § 1332 (diversity of citizenship) because:
            (a) Plaintiff is a citizen of [State] and Defendant is a citizen
                of [different State]; and
            (b) The amount in controversy exceeds $75,000, exclusive of
                interest and costs.

        [ ] 28 U.S.C. § 1332(d) (CAFA) because:
            (a) This is a class action with at least 100 class members;
            (b) Minimal diversity exists; and
            (c) The aggregate amount in controversy exceeds $5,000,000.

     6. This Court has supplemental jurisdiction over Plaintiff's state law
claims pursuant to 28 U.S.C. § 1367 because they arise from the same case or
controversy as the federal claims.

                               VENUE

     7. Venue is proper in this District pursuant to 28 U.S.C. § 1391(b)
because:

        [ ] A substantial part of the events or omissions giving rise to the
            claims occurred in this District;

        [ ] Defendant resides in this District; and/or

        [ ] Defendant is subject to personal jurisdiction in this District
            and there is no other district in which the action may be brought.

                        FACTUAL ALLEGATIONS

                          A. Background

     8. [Describe relevant background facts]

     9. [Continue with chronological facts]

                       B. Defendant's Conduct

     10. On or about [date], Defendant [describe wrongful conduct].

     11. [Continue with specific factual allegations]

     12. As a direct and proximate result of Defendant's conduct, Plaintiff
has suffered [describe injuries/damages].

                       CAUSES OF ACTION

                              COUNT I
                    [TITLE OF FIRST CLAIM]
                   [e.g., Violation of 42 U.S.C. § 1983]

     13. Plaintiff re-alleges and incorporates by reference paragraphs 1
through 12 as if fully set forth herein.

     14. [State elements of the claim]

     15. [Allege facts satisfying each element]

     16. As a direct and proximate result of Defendant's [conduct],
Plaintiff has suffered damages including [specify].

                             COUNT II
                    [TITLE OF SECOND CLAIM]

     17. Plaintiff re-alleges and incorporates by reference paragraphs 1
through 16 as if fully set forth herein.

     18. [State elements and supporting facts]

                             COUNT III
                    [TITLE OF THIRD CLAIM]

     19. Plaintiff re-alleges and incorporates by reference paragraphs 1
through 18 as if fully set forth herein.

     20. [State elements and supporting facts]

                          PRAYER FOR RELIEF

     WHEREFORE, Plaintiff respectfully requests that this Court enter
judgment in Plaintiff's favor and against Defendant as follows:

     a. Compensatory damages in an amount to be determined at trial;

     b. Punitive damages in an amount to be determined at trial;

     c. Pre-judgment and post-judgment interest;

     d. Costs of suit and reasonable attorneys' fees;

     e. [Injunctive relief if sought];

     f. [Declaratory relief if sought]; and

     g. Such other and further relief as this Court deems just and proper.

                           JURY DEMAND

     Plaintiff demands a trial by jury on all issues so triable.

                                        Respectfully submitted,

                                        /s/ {{ATTORNEY_NAME}}
                                        {{ATTORNEY_NAME}}
                                        Florida Bar No. {{BAR_NO}}
                                        {{FIRM_NAME}}
                                        {{ADDRESS}}
                                        {{CITY}}, {{STATE}} {{ZIP}}
                                        Telephone: {{PHONE}}
                                        Email: {{EMAIL}}

                                        Counsel for Plaintiff
```

## Drafting Notes

### Pleading Standard (Twombly/Iqbal)

To survive a motion to dismiss:
- Facts must state a **plausible** claim for relief
- Legal conclusions are not accepted as true
- Factual allegations must be **specific** enough to raise a right to relief above the speculative level

### Required Elements

1. **Short and plain statement of jurisdiction** (Rule 8(a)(1))
2. **Short and plain statement of the claim** (Rule 8(a)(2))
3. **Demand for relief** (Rule 8(a)(3))

### M.D. Fla. Local Requirements

- Civil Cover Sheet (JS-44)
- Corporate Disclosure Statement (if applicable)
- Summons for each defendant
- Filing fee or IFP application

### Verification

Required for:
- TRO/PI motions
- Certain statutory claims
- Claims requiring verification by rule or statute

Add verification block:

```
VERIFICATION

     I, {{PLAINTIFF_NAME}}, declare under penalty of perjury that the
foregoing is true and correct to the best of my knowledge.

     Executed on {{DATE}}.

                                        _______________________________
                                        {{PLAINTIFF_NAME}}
```
