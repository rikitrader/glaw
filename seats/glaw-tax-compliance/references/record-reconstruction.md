# Record Reconstruction

You cannot prepare an accurate delinquent return from memory. Build the numbers from data the
IRS already has, then fill the gaps.

## IRS transcripts — the backbone

| Transcript | What it shows | Why it matters |
|---|---|---|
| **Wage & Income** | Third-party reported data: W-2, 1099-NEC/MISC/INT/DIV/B/R, 1098, K-1, SSA-1099, 1095-A | The income skeleton. Matches what IRS will expect. Generally available ~10 years back. |
| **Account** | Assessments, SFRs, payments, penalties, the **CSED** date, liens/levies posted | Shows where you stand on the clocks and whether an SFR exists. |
| **Return** | Line items of a filed return | Confirms what was (or wasn't) filed. |
| **Record of Account** | Combines Return + Account | One-stop for filed years. |
| **Wage & Income (full / unmasked)** | Full payer info | Needed when the masked version hides what you need to reconstruct. |

### How to pull them
1. **IRS Individual Online Account** (IRS.gov) — fastest; instant PDF.
2. **Form 4506-T** (Request for Transcript) — mailed/faxed; free.
3. **Tax professional** with e-Services / Transcript Delivery System (TDS) and a signed
   **Form 2848** (Power of Attorney) or **Form 8821** (Tax Information Authorization).
4. **Get Transcript by Mail** for prior-year account/return transcripts.

> The Wage & Income transcript is the single most valuable document. Pull it for **every**
> unfiled year before doing anything else.

## What transcripts WON'T show — fill the gaps

The Wage & Income transcript captures *reported income*, not deductions or unreported items.
Reconstruct these from the taxpayer's own records:

- **Schedule C / business expenses** — bank & credit-card statements, accounting exports,
  vendor invoices, receipts, mileage logs. (This is where SFRs most overstate the bill.)
- **Cost basis** — for stock/crypto/property sales (a 1099-B may show proceeds only).
- **Cash income** not on any 1099 — must be included; reconstruct from deposits/records.
- **Itemized deductions** — mortgage interest (1098 *is* on the transcript), property tax,
  charitable, medical.
- **Credits** — dependents, education (1098-T), EITC, child tax credit.

## The Cohan rule (estimating lost records)

When records are genuinely destroyed or unavailable, *Cohan v. Commissioner* permits a
**reasonable estimate** of deductible expenses — but:
- It does **not** apply to expenses with strict substantiation rules (IRC §274: travel, meals,
  entertainment, listed property — those need actual records).
- Document **how** you estimated (industry ratios, bank-deposit analysis, partial records).
- The IRS resolves uncertainty against the taxpayer, so estimate conservatively and keep the
  workpapers.

## Reconciliation gate

Before finalizing a return, reconcile reported income to the Wage & Income transcript:
- Income on the return **≥** income on the transcript, **or**
- A documented explanation for any difference (e.g., a 1099 that double-counts, nominee income,
  a corrected 1099).

If you have the `financial-forensics` skill available and the user has raw bank statements, it
can reconstruct a full P&L / Schedule C from statements — hand off for the heavy lifting, then
return here for filing and relief.

## Business-entity reconstruction

- **S-corp / partnership** — need the entity return (1120-S / 1065) *and* K-1s before the
  owner's 1040 can be finished; sequence entity first.
- **Payroll** — unfiled 941/940 and W-2/W-3 have their own penalties and the **Trust Fund
  Recovery Penalty** (IRC §6672) exposure for responsible persons. Flag this; it's personal.
