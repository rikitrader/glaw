# The Taxpayer Bill of Rights (TBOR) — the spine of audit defense

The Taxpayer Bill of Rights groups the protections already scattered through the Internal
Revenue Code into **ten plain-English rights**. Congress codified them in **IRC §7803(a)(3)**,
directing the Commissioner to ensure IRS employees are familiar with and act in accord with
them. The IRS restates them in **Publication 1 (Your Rights as a Taxpayer)**.

In an examination these are not slogans — each right maps to a concrete procedural lever you
assert on the client's behalf. This file states each right, what the IRS must do, the
controlling authority, and **how you use it in an audit or appeal**.

> Source spine (IRS Tax Tip provenance): the 2018 TBOR series (2018-22, -26, -29, -37, -41, -50,
> -54 and the companion rights), the 2025-07 TBOR overview, and the 2026-34 / 2026-41 deep-dives.
> These Tips are plain-language summaries; the authority below is the primary law.

---

## 1. The Right to Be Informed  — *(Tax Tip 2018-22; 2026-41 deep-dive)*

**Plain statement:** Taxpayers have the right to know what they must do to comply, to clear
explanations of the laws and IRS procedures in all forms, instructions, publications, notices,
and correspondence, and to be informed of IRS decisions about their accounts with clear
explanations of the outcomes.

**What the IRS must do:**
- Certain notices must state the **amount** of tax, interest, and penalties owed and **why** tax
  is owed.
- When the IRS **disallows a refund claim**, it must explain the **specific reasons**.
- When the IRS proposes to assess tax, the **initial letter** must explain **how to appeal**, lay
  out the **entire process from audit through collection**, and explain how the **Taxpayer
  Advocate Service** can help.
- The IRS must send an **annual statement** to installment-agreement taxpayers (beginning
  balance, amount paid, ending balance).
- Forms and publications are available on IRS.gov or by calling **800-829-3676**.

**Authority:** IRC §7803(a)(3); Pub 1. (Refund-disallowance explanation duty and the
appeal/process disclosure are restated in the 2018-22 and 2026-41 Tips.)

**How you use it in an exam:** Demand the **statutory basis** for every proposed adjustment in
the Revenue Agent's Report (Form 4549 / Form 886-A). If a refund or claim is disallowed without
specific reasons, that is a defect you raise. Use the "Understand Your IRS Notice or Letter"
framework on IRS.gov to decode the notice before responding.

## 2. The Right to Quality Service  — *(Tax Tip 2018-26; 2026-34)*

**Plain statement:** Prompt, courteous, professional assistance; clear, understandable
communications; the ability to speak to a supervisor about inadequate service.

**What the IRS must do:** Provide help in dealings with the IRS, communicate clearly, and let a
taxpayer escalate poor service to a manager.

**Authority:** IRC §7803(a)(3); Pub 1.

**How you use it in an exam:** When an examiner is non-responsive, exceeds the scope, or makes
unreasonable IDR demands, **escalate to the group manager** (a recognized, low-friction lever)
before it festers. Document the request.

## 3. The Right to Pay No More Than the Correct Amount of Tax  — *(Tax Tip 2018-29)*

**Plain statement:** Pay only the amount legally due — including interest and penalties — and
have the IRS apply all payments properly.

**What the IRS must do:** Apply payments correctly; correct its own errors; accept proof that an
assessment is wrong.

**Authority:** IRC §7803(a)(3); Pub 1.

**How you use it in an exam:** This is the substantive heart of audit defense. **Recompute the
agent's adjustments** (`bin/glaw-audit-package --form4549`), find math and characterization
errors, and substantiate every legitimate deduction/credit the agent disallowed. Overstated SFR
or CP2000 assessments are the textbook violation of this right.

## 4. The Right to Challenge the IRS's Position and Be Heard

**Plain statement:** Taxpayers may raise objections and provide additional documentation in
response to formal IRS actions or proposed actions, expect the IRS to consider their timely
objections promptly and fairly, and receive a response if the IRS disagrees.

**What the IRS must do:** Consider timely objections and supporting documents promptly and fairly
and respond when it disagrees.

**Authority:** IRC §7803(a)(3); Pub 1.

**How you use it in an exam:** This powers the **IDR response**, the **CP2000 response**, and
**audit reconsideration** (asking the IRS to reopen an assessment when you have documents not
previously considered, including to replace an SFR). It is the right to put the substantiation in
front of the examiner before the case closes.

## 5. The Right to Appeal an IRS Decision in an Independent Forum  — *(Tax Tip 2018-37)*

**Plain statement:** A fair and impartial administrative appeal of most IRS decisions, including
many penalties, and a written response explaining Appeals' decision. Taxpayers generally have the
right to take their case to **court**.

**What the IRS must do:** Provide access to the **IRS Independent Office of Appeals**, separate
from the examination function.

**Authority:** IRC §7803(a)(3); IRC §7803(e) (Independent Office of Appeals); Pub 1; Pub 5
(Your Appeal Rights).

**How you use it in an exam:** The **30-day letter** is the invitation to Appeals — file a
**written protest** (formal protest if the disputed amount exceeds the small-case threshold) and
argue the **hazards of litigation** to settle. If the 30-day window lapses, the **90-day notice
of deficiency** routes you to **Tax Court** instead.

## 6. The Right to Finality  — *(Tax Tip 2018-41)*

**Plain statement:** Taxpayers have the right to know the **maximum time** they have to challenge
the IRS's position, the **maximum time** the IRS has to **audit** a particular year or **collect**
a debt, and when the IRS has **finished** an audit.

**What the IRS must do:** Tell the taxpayer when an audit is complete; observe the assessment and
collection statutes.

**Authority:** IRC §7803(a)(3); the underlying statutes are **§6501 (ASED)**, **§6502 (CSED)**,
**§6511 (RSED)**. Pub 1.

**How you use it in an exam:** **The single most powerful defense.** Compute the **ASED**
(`bin/glaw-sol`): a year whose assessment statute has **expired** is a complete bar to additional
tax — raise it first. Watch for and **scrutinize any Form 872** request to **extend** the ASED;
do not consent without analysis. (Figures defer to `current-figures.md`.)

## 7. The Right to Privacy  — *(Tax Tip 2018-50)*

**Plain statement:** IRS inquiry, examination, or enforcement will comply with the law and be no
more intrusive than necessary, respecting due-process rights including search-and-seizure
protections and a **collection due process** hearing where applicable.

**What the IRS must do:** Keep enforcement proportionate; e.g., it generally will not seek
intrusive financial information when ability to pay is plausibly demonstrable, and must follow
CDP procedures before levying.

**Authority:** IRC §7803(a)(3); CDP statutes §6320 (lien) / §6330 (levy); Pub 1.

**How you use it in an exam:** Push back on **overbroad IDRs** ("no more intrusive than
necessary"). If the exam transitions to collection, preserve **CDP** rights (Form 12153,
30-day clock) — route to `/glaw-tax-relief`.

## 8. The Right to Confidentiality  — *(Tax Tip 2018-54)*

**Plain statement:** Information provided to the IRS will not be disclosed unless authorized by
the taxpayer or by law; the IRS will take action against employees, preparers, and others who
wrongfully use or disclose return information.

**What the IRS must do:** Protect return information under **§6103**; penalize unauthorized
disclosure.

**Authority:** IRC §7803(a)(3); **§6103** (confidentiality of returns and return information);
§7525 (limited practitioner privilege, non-criminal). Pub 1.

**How you use it in an exam:** Frame the **privilege analysis** — note that §7525 does **not**
cover criminal matters or return preparation (see `persona-and-guardrails.md` eggshell gate), and
control what is volunteered to third parties or summoned.

## 9. The Right to Retain Representation

**Plain statement:** Taxpayers have the right to retain an authorized representative of their
choice to represent them in dealings with the IRS, and the right to seek **Low Income Taxpayer
Clinic** assistance if they cannot afford representation.

**What the IRS must do:** Recognize a valid power of attorney; if a taxpayer in an interview
clearly states a wish to consult a representative, the IRS interviewer must **suspend the
interview**.

**Authority:** IRC §7803(a)(3); **IRC §7521(b)(2)** (right to suspend an interview to consult a
representative) and **§7521(c)** (a represented taxpayer generally cannot be required to attend);
representation perfected on **Form 2848 (Power of Attorney)**, info-only via **Form 8821**. Pub 1;
Pub 947.

**How you use it in an exam:** **File Form 2848 immediately** so the firm speaks for the client
and the client does not face the Revenue Agent alone. Invoke **§7521(b)(2)** to stop any interview
where the client begins to volunteer harmful information — critical in an eggshell audit.

## 10. The Right to a Fair and Just Tax System

**Plain statement:** The system should consider facts and circumstances that might affect a
taxpayer's underlying liabilities, ability to pay, or ability to provide information timely; and
taxpayers have the right to receive **Taxpayer Advocate Service** assistance if facing financial
difficulty or if the IRS has not resolved issues properly through normal channels.

**What the IRS must do:** Weigh the taxpayer's facts and circumstances; provide access to the
**TAS**.

**Authority:** IRC §7803(a)(3); **§7811** (Taxpayer Assistance Orders / TAS); Pub 1.

**How you use it in an exam:** Where the exam stalls, causes economic harm, or breaks down, file
**Form 911** to bring in the **Taxpayer Advocate Service**, which can issue a Taxpayer Assistance
Order. Raise reasonable-cause and ability-to-pay facts that the mechanical assessment ignored.

---

## Quick map — right → audit/appeals lever

| Right | Primary lever you pull |
|---|---|
| Be Informed | Demand statutory basis for each adjustment; decode the notice |
| Quality Service | Escalate to the group manager |
| Pay No More | Recompute the RAR; substantiate disallowed items |
| Challenge & Be Heard | IDR / CP2000 response; **audit reconsideration** |
| Appeal | 30-day **protest → IRS Appeals**; hazards-of-litigation settlement |
| Finality | **SOL/ASED defense** (`bin/glaw-sol`); scrutinize **Form 872** |
| Privacy | Narrow overbroad IDRs; preserve **CDP** (§6320/§6330) |
| Confidentiality | §6103; privilege scoping (§7525 limits) |
| Retain Representation | **Form 2848**; **§7521(b)(2)** suspend-the-interview |
| Fair & Just System | **Form 911 / TAS** (§7811); facts-and-circumstances |

All ten rest on **IRC §7803(a)(3)** and are restated in **Publication 1**. Dollar thresholds
(e.g., the formal-protest small-case ceiling) defer to `tax-legal-shared/current-figures.md` —
verify current on IRS.gov.
