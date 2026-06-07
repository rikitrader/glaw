# Penalty Relief: FTA → Reasonable Cause → Statutory

Verify current penalty rates and dollar thresholds per SKILL.md Step 1a. Authority: **IRM
20.1.1 (Penalty Handbook)**, IRC §6651 (FTF/FTP), §6662 (accuracy), §6654/§6655 (estimated tax).

## The penalties you're fighting

| Penalty | Rate | Cap | Notes |
|---|---|---|---|
| **Failure to File (FTF)** | ~5% of unpaid tax per month (or part) | 25% | IRC §6651(a)(1). Minimum penalty for >60 days late applies if return is very late. |
| **Failure to Pay (FTP)** | ~0.5% per month | 25% | IRC §6651(a)(2). Drops to 0.25%/month while an IA is in effect — **but only if the return was timely filed** (with extensions). §6651(h). |
| **FTF + FTP same month** | FTF reduced by FTP → net ~4.5%/mo | — | They don't simply stack; §6651(c)(1) offsets. |
| **Accuracy-related** | 20% of underpayment | — | IRC §6662 (negligence, substantial understatement). |
| **Estimated tax** | varies w/ interest rate | — | IRC §6654 (individuals). Generally **not** abatable for reasonable cause. |
| **Interest** | federal short-term + 3% | — | IRC §6601. **Rarely** abatable — only if tied to IRS error/delay (§6404(e)). |

If penalties are abated, the **interest on those penalties** is abated with them. Interest on
the underlying *tax* generally is not.

## Decision tree — pick the channel in this order

```
START
 │
 ├─ Is there a clean compliance history? (no FTF/FTP/accuracy penalty in prior 3 yrs,
 │  all required returns filed, balance paid or under arrangement)
 │      └─ YES → FIRST-TIME ABATEMENT (FTA). Fastest. Apply to the EARLIEST eligible year.
 │
 ├─ Do real facts explain the failure? (illness/death, disaster, records destroyed,
 │  reliance on a professional, etc. — NOT "forgot" or "couldn't afford")
 │      └─ YES → REASONABLE CAUSE. Draft the narrative (letter-templates.md).
 │
 ├─ Did the IRS give incorrect WRITTEN advice, or err/delay?
 │      └─ YES → STATUTORY EXCEPTION (Form 843 + the written advice / §6404(e)).
 │
 └─ None apply → no abatement; focus on collection resolution (Installment Agreement / OIC)
    and accept the penalties, or revisit FTA after a year of clean compliance.
```

## 1. First-Time Abatement (FTA) — check FIRST

Administrative waiver under **IRM 20.1.1.3.3.2.1** (the IRS operationalizes the determination
through the Reasonable Cause Assistant, IRM 20.1.1.3.6 / 20.1.1.3.6.1). Applies to **FTF, FTP,
and failure-to-deposit** penalties (not accuracy or estimated-tax). FTA relief is limited to a
**single tax period**. Three requirements:

1. **Clean compliance history** — no penalties (other than an estimated-tax penalty) in the
   **3 tax years** preceding the year at issue.
2. **Filing compliance** — all currently required returns filed (or a valid extension).
3. **Payment compliance** — paid, or in an active payment arrangement, for any tax due.

How to request:
- **Phone** — call the IRS and ask for "first-time abate / first-time penalty abatement." Often
  granted on the spot for one year. Get the agent's ID and a confirmation.
- **Letter** or **Form 843** — if the balance is large or you want a paper trail.

Strategy notes:
- **Apply FTA to the EARLIEST year** that has the largest penalty *and* meets the look-back,
  so later years can still use reasonable cause. FTA is a once-per-clean-streak resource.
- If a year qualifies for **both** FTA and reasonable cause, use **reasonable cause** for that
  year and **save FTA** for a year that has no reasonable-cause story. (The IRS will often
  apply FTA first by default — explicitly request reasonable cause where you have it.)

## 2. Reasonable Cause — fact-based

The taxpayer exercised ordinary business care and prudence but still couldn't comply. IRM
20.1.1.3.2. The IRS weighs: what happened, when, how it prevented compliance, and what the
taxpayer did to fix it once able.

**Generally QUALIFIES (with documentation):**
- Serious illness, incapacity, or death of the taxpayer or immediate family.
- Natural disaster, fire, casualty (FEMA-declared zones get automatic relief).
- Records unobtainable through no fault of the taxpayer.
- Reliance on a tax professional **for a matter of professional judgment** (not for a
  mechanical filing deadline — *United States v. Boyle*).
- Unavoidable absence, postal/IRS error.

**Generally does NOT qualify (be honest with the user):**
- "I forgot" / oversight / ignorance of the deadline.
- "I couldn't afford to pay." (Inability to pay can support **FTP** relief in narrow cases but
  rarely **FTF** — you still must *file*.)
- Reliance on an agent to **file on time** (Boyle: that duty is non-delegable).
- Relying on the skill or another AI as the reason. Don't suggest it.

Documentation to attach: medical records, death certificate, FEMA declaration, insurance/fire
report, correspondence showing records were requested, etc.

## 3. Statutory / IRS-error exceptions

- **Incorrect written advice from the IRS** — IRC §6404(f). Attach the written advice and your
  written request that prompted it. Use **Form 843**.
- **IRS error or unreasonable delay** — §6404(e) can abate interest attributable to an IRS
  ministerial/managerial delay.
- **Disaster/combat-zone postponements** — automatic; verify the year/zone.

## Form 843 vs. letter vs. phone

| Method | Use when |
|---|---|
| **Phone** | Single year, FTA, want a fast yes. |
| **Signed letter / written statement** | Reasonable cause, multiple facts, want a record. Attach to the return or send to the notice address. |
| **Form 843** (Claim for Refund and Request for Abatement) | Penalty already **paid** (claiming a refund of it), statutory/written-advice claims, or when a formal claim is needed. Not used for income-tax itself. |

## After a denial

- Request **Appeals** review (the denial letter explains the window).
- Penalty Appeals via the IRS Independent Office of Appeals; or pay and file **Form 843** to
  preserve a refund claim, then litigate if warranted.
- Escalate genuine hardship to the **Taxpayer Advocate Service** (Form 911).
