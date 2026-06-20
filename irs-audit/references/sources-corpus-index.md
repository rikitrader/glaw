# Sources & Corpus Provenance Index

This knowledge base uses the **IRS Tax Tip** email corpus (irs@service.govdelivery.com, ~700
issues 2018–2026, mirroring public IRS.gov pages) as its **topic spine and provenance**, but
rests on **primary authority** — the Internal Revenue Code, the Internal Revenue Manual (IRM),
IRS Publications, and IRS Forms.

> **Important:** IRS Tax Tips are **plain-language summaries**, not law. They tell us *what the
> IRS says publicly and which topics matter*; they do **not** establish a rule. Every operative
> statement in this KB is grounded in the primary authority cited in the right-hand columns below.
> When a figure or program window is in play, **defer to `tax-legal-shared/current-figures.md`**
> and verify on the primary source.

---

## Corpus → KB consumption ledger

Issue numbers confirmed in the corpus (subject lines verified via the mailbox). "Consumed by"
shows which KB file used the Tip as its topic anchor.

### Taxpayer Bill of Rights series (the spine of `taxpayer-bill-of-rights.md`)

| Issue | Topic | Consumed by |
|---|---|---|
| 2018-22 | Right to Be Informed (TBOR #1) — verbatim body ingested | taxpayer-bill-of-rights.md (Right 1) |
| 2018-26 | Right to Quality Service (TBOR #2) | taxpayer-bill-of-rights.md (Right 2) |
| 2018-29 | Right to Pay No More Than the Correct Amount (TBOR #3) | taxpayer-bill-of-rights.md (Right 3) |
| 2018-37 | Right to Appeal in an Independent Forum (TBOR #5) | taxpayer-bill-of-rights.md (Right 5) |
| 2018-41 | Right to Finality (TBOR #6) | taxpayer-bill-of-rights.md (Right 6) |
| 2018-50 | Right to Privacy (TBOR #7) | taxpayer-bill-of-rights.md (Right 7) |
| 2018-54 | Right to Confidentiality (TBOR #8) | taxpayer-bill-of-rights.md (Right 8) |
| (companion) | Right to Retain Representation; Right to Challenge & Be Heard; Right to a Fair & Just System | taxpayer-bill-of-rights.md (Rights 4, 9, 10) |
| 2025-07 | TBOR overview — "fundamental protection for all taxpayers" | taxpayer-bill-of-rights.md (intro) |
| 2026-34 | Right to Quality Service (deep-dive) | taxpayer-bill-of-rights.md (Right 2) |
| 2026-41 | Right to Be Informed (detailed) | taxpayer-bill-of-rights.md (Right 1) |

### Notices, examination & deadlines (`notices-and-letters.md`, `examination-workflow.md`)

| Issue | Topic | Consumed by |
|---|---|---|
| 2018-101 | What taxpayers can do when a letter arrives | notices-and-letters.md (triage; authentication) |
| 2026-32 | Actions if you missed the April filing/payment deadline | notices-and-letters.md (collection track) |
| 2026-31 | Options for taxpayers who need help paying a tax bill | notices-and-letters.md; penalty-relief.md |
| 2026-33 | Ways to check refund status | transcripts-and-reconstruction.md |
| 2026-35 | When and how to amend a return | examination-workflow.md (audit reconsideration / amendments) |
| 2026-30 | Need more time? Request an extension | examination-workflow.md (context) |
| 2026-36 | Check withholding now | (context — withholding/estimated-tax penalty) |

### Penalty relief / collections (`penalty-relief.md`)

| Issue | Topic | Consumed by |
|---|---|---|
| 2026-40 | Resolve tax debt through an Offer in Compromise | penalty-relief.md (post-assessment context; routes to /glaw-tax-relief) |

### Scams & data security (`scams-and-data-security.md`)

| Issue | Topic | Consumed by |
|---|---|---|
| 2018-44 | IRS phone scam intensifies during filing season | scams-and-data-security.md (letter ≠ phone call) |
| 2018-32 | IRS alerts taxpayers about refund scam | scams-and-data-security.md (refund scams) |
| 2018-92 | Disaster scams during hurricane season | scams-and-data-security.md (disaster scams) |
| 2023-44 | Employers: watch out for Employee Retention Credit schemes | scams-and-data-security.md (ERC withdrawal/VDP) |
| 2021-07 | All taxpayers now eligible for Identity Protection PINs | scams-and-data-security.md (IP PIN) |
| 2026-44 | IRS-verified is the way to go for social media / e-News | scams-and-data-security.md (authenticate the IRS) |
| 2026-37 | National Small Business Week: avoid the scam | scams-and-data-security.md (small-business scams) |
| 2018-23 / 2018-137 / 2018-151 / 2018-160 | Preparer data-security plan / spearphishing / data-theft response steps | scams-and-data-security.md (WISP, Pub 4557, Form 14039, Stakeholder Liaison) |

### Transcripts & reconstruction (`transcripts-and-reconstruction.md`)

| Issue | Topic | Consumed by |
|---|---|---|
| 2018-43 | Get prior-year tax information | transcripts-and-reconstruction.md (how to pull) |
| 2018-30 | IRS can help get a Form W-2 | transcripts-and-reconstruction.md (missing W-2; Form 4852) |
| 2018-121 | Taxpayers can monitor their IRS information online | transcripts-and-reconstruction.md (online account) |
| 2023-25 | What to do when a W-2 or 1099 is missing or incorrect | transcripts-and-reconstruction.md (W&I gate) |

### Filing-basics Tips (background context, not operative rules)

2018-19 (six reasons to e-file), 2018-31 (return-prep options), 2018-28 (itemize vs. standard),
2018-24 (EITC), 2018-20 (exemptions and dependents), plus the 2019/2020/2024 filing-basics and
tax-pro-tool Tips. These inform the seat's general literacy but are not relied on for audit-defense
rules.

> **Corpus completeness note:** the mailbox returns 200+ matching threads in a single query
> (estimate of the full subscription is ~700 issues 2018–2026). The issues above are the
> **confirmed, topic-relevant** spine ingested for this seat. The KB intentionally indexes the
> exam/rights/scam/transcript clusters and treats the remaining filing-season Tips as background.

---

## Primary-authority map (what the KB actually rests on)

### Internal Revenue Code
| § | Subject | KB file |
|---|---|---|
| **§6212** | Notice of deficiency | notices-and-letters.md |
| **§6213(a)** | 90-day petition period; assessment barred while pending | notices-and-letters.md; examination-workflow.md |
| **§6501** | ASED — assessment statute (3/6/∞) | examination-workflow.md; taxpayer-bill-of-rights.md |
| **§6502** | CSED — collection statute (10 yr) | examination-workflow.md |
| **§6511** | RSED — refund statute (3 yr / 2 yr) | examination-workflow.md |
| **§6320 / §6330** | CDP — lien / levy hearing rights | notices-and-letters.md; taxpayer-bill-of-rights.md |
| **§6651(a)/(c)/(h)** | FTF / FTP penalties; offset; IA reduction | penalty-relief.md |
| **§6662 / §6663** | Accuracy-related (20%) / civil fraud (75%) | penalty-relief.md |
| **§6654 / §6655** | Estimated-tax penalties | penalty-relief.md |
| **§6698 / §6699** | Partnership / S-corp late-filing penalties | penalty-relief.md |
| **§6672** | Trust Fund Recovery Penalty | penalty-relief.md |
| **§6721 / §6722** | Information-return penalties | penalty-relief.md |
| **§6404(e)/(f)** | Interest abatement (IRS delay) / incorrect written advice | penalty-relief.md |
| **§7803(a)(3)** | Taxpayer Bill of Rights mandate | taxpayer-bill-of-rights.md |
| **§7803(e)** | Independent Office of Appeals | taxpayer-bill-of-rights.md |
| **§7521(b)(2)/(c)** | Right to suspend interview / not be compelled to attend | taxpayer-bill-of-rights.md |
| **§7525** | Limited practitioner privilege (non-criminal only) | persona-and-guardrails.md; taxpayer-bill-of-rights.md |
| **§6103** | Confidentiality of return information | taxpayer-bill-of-rights.md |
| **§7811** | Taxpayer Assistance Orders (TAS) | taxpayer-bill-of-rights.md |
| **§274(d)** | Strict substantiation (travel/meals/gifts/listed property) | transcripts-and-reconstruction.md |
| **§6713 / §7216** | Unauthorized disclosure of return info (preparers) | scams-and-data-security.md |

### IRM, Publications, Forms, and case law
- **IRM 20.1.1** (Penalty Handbook); **IRM 20.1.1.3.3.2.1** (First-Time Abatement);
  **IRM 20.1.1.3.2** (reasonable cause).
- **Pub 1** (Your Rights as a Taxpayer); **Pub 5** (Your Appeal Rights); **Pub 947**
  (representation); **Pub 556** (examination of returns / appeal rights); **Pub 4557 / Pub 5293**
  (safeguarding taxpayer data).
- **Forms:** 4549 + 886-A (RAR), 4564 (IDR), 2848 (POA), 8821 (info auth), 872 (consent to extend
  ASED), 12153 (CDP request), 843 (abatement/refund claim), 911 (TAS), 14039 (ID-theft affidavit),
  4506-T / 4506 (transcript / copy of return), 4852 (substitute W-2), 8275 / 8275-R (disclosure),
  656 / 433-A(OIC) / 433-B(OIC) (OIC — via /glaw-tax-relief).
- **Case law:** *United States v. Boyle*, 469 U.S. 241 (1985) (reliance on agent to file ≠
  reasonable cause); *Cohan v. Commissioner*, 39 F.2d 540 (2d Cir. 1930) (estimate where records
  lost, subject to §274(d)).

### Shared canon (the firm's single sources of truth)
- `tax-legal-shared/current-figures.md` — **all** dollar thresholds and rates (dated + cited).
- `tax-legal-shared/guardrails.md` — the suite-wide ethics floor (zero fabrication; criminal-
  exposure/privilege gate; drafts-not-files).

**Verification posture:** figures verified as of the dates in `current-figures.md` (suite
verification 2026-06-04); always re-confirm the specific number in play on IRS.gov / law.cornell.edu
when web tools are available.
