# Penalty Relief in an Audit — FTA → Reasonable Cause → Statutory

When an exam produces an assessment, penalties ride on top of it. Attack them **after** the tax
issue is resolved, in a fixed order. Authority: **IRM 20.1.1 (Penalty Handbook)**. **Verify every
rate and dollar threshold against `tax-legal-shared/current-figures.md`** — they change yearly.

> Source spine: Tax Tip 2026-40 (Offer in Compromise / can't-pay context) and the abatement
> threads; primary authority is the IRC and IRM 20.1.1.

---

## The penalties you fight in an exam

| Penalty | What triggers it | Cite | Rate/cap (defer to current-figures.md) |
|---|---|---|---|
| **Failure to File (FTF)** | Return filed late | §6651(a)(1) | ~5%/mo of unpaid tax, max 25%; minimum penalty if >60 days late |
| **Failure to Pay (FTP)** | Tax not paid by due date | §6651(a)(2) | ~0.5%/mo, max 25%; drops to 0.25%/mo under an IA **only if return timely filed** (§6651(h)) |
| **FTF + FTP same month** | Both apply | §6651(c)(1) | FTF reduced by FTP — they don't simply stack |
| **Accuracy-related** | Negligence or **substantial understatement** | **§6662** | 20% of the underpayment |
| **Civil fraud** | Underpayment due to fraud | **§6663** | **75%** of the fraud portion (IRS bears burden, clear and convincing) |
| **Estimated-tax** | Underpaid estimates | §6654 (indiv.) / §6655 (corp.) | varies with the interest rate; generally **not** abatable for reasonable cause |
| **S-corp / partnership late filing** | Entity return late | **§6699 / §6698** | per-owner, per-month (even with no tax due) |
| **Trust Fund Recovery Penalty (TFRP)** | Unremitted withheld trust-fund taxes | **§6672** | 100% of the trust-fund portion; **personal**; not dischargeable |
| **Information-return penalties** | Late/incorrect 1099/W-2, etc. | **§6721 / §6722** | per-form, tiered, indexed; higher if intentional |
| **Interest** | On tax and on penalties | §6601 | fed short-term + 3%; rarely abatable (only IRS error/delay, §6404(e)) |

If a penalty is **abated**, the **interest on that penalty** is abated with it. Interest on the
underlying **tax** generally is not. The §6663 **civil-fraud** penalty is the bridge to the
**eggshell** analysis — if the examiner is "developing fraud," route to `/glaw-investigations`.

## Order of operations — pick the channel in this order

```
START
 │
 ├─ Clean compliance history? (no FTF/FTP/accuracy penalty in the prior 3 years,
 │  all required returns filed, balance paid or under an arrangement)
 │      └─ YES → FIRST-TIME ABATEMENT (FTA). Fastest. Apply to the EARLIEST eligible year.
 │
 ├─ Do real, documented facts explain the failure? (illness/death, disaster, records
 │  destroyed, reliance on a professional for judgment — NOT "forgot" / "couldn't afford")
 │      └─ YES → REASONABLE CAUSE. Draft the narrative; attach proof.
 │
 ├─ Incorrect WRITTEN IRS advice, or IRS error/delay?
 │      └─ YES → STATUTORY EXCEPTION (Form 843 + the written advice / §6404(e)/(f)).
 │
 └─ None apply → concede the penalty; resolve the balance via /glaw-tax-relief; revisit FTA
    after a year of clean compliance.
```

## 1. First-Time Abatement (FTA) — check FIRST

Administrative waiver under **IRM 20.1.1.3.3.2.1**. Applies to **FTF, FTP, and
failure-to-deposit** penalties (**not** accuracy or estimated-tax). Limited to a **single tax
period**. Three requirements:

1. **Clean compliance history** — no penalties (other than an estimated-tax penalty) in the
   **3 tax years** preceding the year at issue.
2. **Filing compliance** — all currently required returns filed (or valid extension).
3. **Payment compliance** — paid, or in an active arrangement, for any tax due.

How to request: by **phone** (often granted on the spot — get the agent ID and confirmation), by
**letter**, or on **Form 843** for a paper trail / when the penalty is already paid.

**Strategy:** apply FTA to the **earliest** qualifying year with the largest abatable penalty, and
**save reasonable cause** for years that have a genuine story. If a year qualifies for **both**,
use **reasonable cause** there and preserve FTA for a year with no reasonable-cause facts (the IRS
defaults to FTA first — request reasonable cause explicitly where you have it).

## 2. Reasonable cause — fact-based

The taxpayer exercised **ordinary business care and prudence** but still couldn't comply. **IRM
20.1.1.3.2.** The IRS weighs: what happened, when, how it prevented compliance, and what the
taxpayer did to fix it once able.

**Generally QUALIFIES (with documentation):**
- Serious illness, incapacity, or death of the taxpayer or immediate family.
- Natural disaster, fire, casualty (FEMA-declared zones get automatic relief).
- Records unobtainable through no fault of the taxpayer.
- **Reliance on a tax professional for a matter of professional judgment** — *not* for a
  mechanical filing deadline (**United States v. Boyle**, 469 U.S. 241 (1985): the duty to file
  on time is non-delegable).
- Unavoidable absence; postal or IRS error.

**Generally does NOT qualify (be honest with the client):**
- "I forgot" / oversight / ignorance of the deadline.
- "I couldn't afford to pay" — inability to pay rarely supports **FTF** relief (you still must
  *file*); it can support **FTP** relief in narrow cases.
- Reliance on an agent to **file on time** (Boyle).
- **Never** offer "I relied on the software / an AI" as a reason, and never invent a qualifying
  fact (see `persona-and-guardrails.md` — zero fabrication).

**Documentation to attach:** medical records, death certificate, FEMA declaration, fire/insurance
report, correspondence showing records were requested.

## 3. Statutory / IRS-error exceptions

- **Incorrect written advice from the IRS** — **§6404(f)**. Attach the written advice and your
  written request that prompted it. Use **Form 843**.
- **IRS error or unreasonable delay** — **§6404(e)** can abate interest attributable to a
  ministerial/managerial delay.
- **Disaster / combat-zone postponements** — automatic; verify the year and zone.
- **Reasonable-basis / adequate-disclosure** defenses to the **§6662** accuracy penalty —
  substantial authority (§6662(d)(2)(B)) or disclosure on **Form 8275 / 8275-R**.

## Form 843 vs. letter vs. phone

| Method | Use when |
|---|---|
| **Phone** | Single year, FTA, want a fast yes. |
| **Signed letter / written statement** | Reasonable cause, multiple facts, want a record. |
| **Form 843** (Claim for Refund and Request for Abatement) | Penalty already **paid** (claiming it back), statutory/written-advice claims, or when a formal claim is needed. **Not** used for the income tax itself. |

## After a denial

- Request **Appeals** review (the denial letter states the window) — the **Right to Appeal**.
- Penalty Appeals via the **IRS Independent Office of Appeals**; or pay and file **Form 843** to
  preserve a refund claim, then litigate if warranted.
- Escalate genuine hardship to the **Taxpayer Advocate Service** (Form 911) — the **Right to a
  Fair and Just Tax System**.

## Quantify before you ask

Run `bin/glaw-abatement --penalty <amt> [--factors ...]` so the request states the **exact
abatable amount** and the channel. Never claim relief the facts don't support — concede the
penalty honestly and pivot to collection resolution (`/glaw-tax-relief`).
