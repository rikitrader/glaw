# Transcripts & Account Reconstruction

You cannot defend an exam from memory. Before responding, pull what the **IRS actually has on
record** and reconcile the return to it. This is the evidentiary foundation of every position the
seat takes — and the **W&I transcript gate** is non-negotiable.

> Source spine: Tax Tips 2018-43 (get prior-year tax info), 2018-30 (IRS can help get a Form
> W-2), 2018-121 (monitor IRS information online), 2023-25 (missing/incorrect W-2 or 1099),
> 2026-33 (check refund status). Authority: IRC §6103(e) (taxpayer access), Form 4506-T, the IRS
> Transcript Delivery System (TDS), and the Cohan doctrine.

---

## The four transcript types — what each tells you

| Transcript | What it shows | Use in the exam |
|---|---|---|
| **Wage & Income (W&I)** | Third-party data the IRS received — **W-2, 1099 (NEC/MISC/INT/DIV/B/K), 1098, K-1, SSA-1099** | The **backbone**. This is the data the **CP2000 / AUR** matched against. Reconcile the return to it. |
| **Account** | Posted transactions: assessments, payments, penalties, interest, **SFR** flag, **assessment date** | Drives the **CSED** (assessment date + 10 yr) and shows whether an **SFR** was filed by the IRS. |
| **Return** | Line items **as the taxpayer originally filed** | Confirms what was reported; baseline for amendments / audit reconsideration. |
| **Record of Account** | **Return + Account** combined | One-stop view of filed figures plus subsequent IRS activity. |

## How to pull them

```bash
bin/glaw-transcript --account <account.json> --wage-income <wi.json>
```

For the taxpayer/representative directly:

1. **IRS Online Account / Get Transcript** (IRS.gov) — fastest; W&I, Account, Return, Record of
   Account, and a Verification of Non-Filing letter (Tax Tip 2018-121: taxpayers can monitor IRS
   information online).
2. **Form 4506-T** (Request for Transcript of Tax Return) — mail/fax; free; or **Form 4506**
   (full copy of the return, fee, for older years).
3. **Tax professional via e-Services / Transcript Delivery System (TDS)** — with a **Form 2848**
   (POA) or **Form 8821** (info authorization) on file.

**Missing or wrong W-2 / 1099 (Tax Tip 2023-25 / 2018-30):** if the taxpayer never received a W-2
or it's incorrect, the **W&I transcript** usually still has the IRS's copy; the IRS can also help
obtain a W-2 from the employer, and **Form 4852** substitutes for a missing W-2 when reconstructing
the return.

## The reconciliation discipline

For each year under exam, build a tie-out:

```
W&I transcript income  →  vs.  →  return as filed  →  vs.  →  the posted ledger
```

- **Income side:** every W&I line should appear on the return (or be explained — e.g., a 1099-K
  for gross sales that nets to the Schedule C gross receipts). An item on the W&I transcript that
  is **missing** from the return is exactly what the CP2000 flags — get ahead of it.
- **Deduction/expense side:** the W&I transcript won't show these — they come from the **posted
  general ledger**, bank/credit-card records, invoices, and receipts (`bin/glaw-audit-package`).
- **Payments/credits:** confirm the Account transcript reflects all payments and withholding the
  taxpayer is entitled to.

### ⛔ The W&I transcript gate

**Do not assert an income figure, and do not sign off on a response, until the income picture
reconciles to the Wage & Income transcript — or you have documented, in the file, exactly why it
differs** (e.g., nominee income, a duplicate 1099, basis on a 1099-B the broker didn't report).
An unreconciled gap is a red flag, not a rounding difference — surface it.

## Reconstructing lost records — the Cohan rule

When records are **genuinely lost** (fire, flood, defunct bank, a prior preparer who won't
release files), the **Cohan rule** (*Cohan v. Commissioner*, 39 F.2d 540 (2d Cir. 1930)) lets a
court/examiner **estimate** a deductible expense where it's clear the taxpayer incurred *some*
expense — bearing heavily against the taxpayer, who created the gap.

Discipline when you invoke it:

- **Label every Cohan figure an ESTIMATE.** Never present a reconstructed number as a
  substantiated one (zero-fabrication rule, `persona-and-guardrails.md`).
- **Document the basis** for the estimate — industry ratios, prior-year actuals, bank-deposit
  analysis, mileage from a reconstructed calendar, vendor statements re-obtained.
- **Cohan does NOT apply where the IRC imposes strict substantiation:** **§274(d)** items —
  **travel, meals, gifts, and listed property (incl. vehicles)** — require contemporaneous records
  (amount, time, place, business purpose). A Cohan estimate **cannot** rescue an undocumented
  §274(d) deduction. Concede these honestly if the records don't exist.
- Hand heavy reconstruction (bank-statement → P&L) to `/glaw-financial-forensics`; tie the numbers
  out with `/glaw-accounting` and `/glaw-tax-provision`.

## Output of this step

A reconstruction package: the Account transcript (with assessment date → CSED), the W&I transcript
tie-out (income reconciled or the difference documented), the GL-tied substantiation index for
disputed deductions, and a flagged list of any Cohan estimates with their bases. This feeds the
IDR response, the CP2000 rebuttal, the 30-day protest, and the Form 4549 recompute.

All figures are facts traced to a source — none are quoted as rates/thresholds here; where a
threshold matters (e.g., reporting floors), defer to `tax-legal-shared/current-figures.md`.
