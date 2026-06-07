# Choosing the Resolution Path (decision tree + RCP estimator)

Match the taxpayer to the right program **honestly**. Verify thresholds per Step 1a.

## Decision tree

```
START — all required returns filed? ── NO ──► route to tax-compliance (file first), then return
   │ YES
   ▼
Active levy / Final Notice (LT11/CP90/1058)? ── YES ──► triage first (CDP Form 12153 / release);
   │ NO                                                 lien-levy-and-hardship.md
   ▼
Can you pay in full within ~180 days? ── YES ──► short-term payment plan (no fee)
   │ NO
   ▼
Owe ≤ $50k AND can clear in ≤ 72 months? ── YES ──► STREAMLINED INSTALLMENT AGREEMENT
   │ NO
   ▼
Compute RCP (below). Is RCP < total debt?
   ├─ NO (you can pay it) ──► full IA, or PPIA if monthly ability < required IA payment
   └─ YES ──► can you pay anything monthly?
              ├─ YES, some ──► PARTIAL PAYMENT IA (PPIA)  or  OFFER IN COMPROMISE (if RCP ≪ debt)
              └─ NO (hardship) ──► CURRENTLY NOT COLLECTIBLE (CNC)
ALWAYS in parallel ──► penalty abatement (FTA → reasonable cause); innocent spouse if joint debt
                       is really the other spouse's.
```

## RCP estimator (pre-qualify the OIC before anyone pays a fee)

```
RCP  =  Net realizable equity in ASSETS  +  Future INCOME component

  Net realizable equity = Σ (quick-sale value of each asset − loans against it − exemptions)
        assets: home equity, vehicles (minus allowance), bank/investment, cash value, business assets

  Future income = (gross monthly income − allowable monthly expenses) × multiplier
        allowable expenses = IRS Collection Financial Standards (housing, food, transport,
                             health, taxes) — NOT actual spending if higher
        multiplier = 12  (lump-sum offer, paid in ≤5 installments)
                   = 24  (periodic-payment offer)

  The IRS accepts an OIC offered amount ≥ RCP.
```
- **RCP < debt** → an OIC can work; offer ≈ RCP. **RCP ≥ debt** → OIC will be **rejected**; use IA/
  PPIA/CNC instead. *This is the honest pre-screen "pennies on the dollar" ads skip.*
- Low monthly disposable income + few assets → low RCP → best OIC candidates (and best CNC cases).

## Quick chooser

| Profile | Best path |
|---|---|
| Steady income, owe ≤ $50k | Streamlined IA |
| Income but RCP ≥ debt, can't full-pay before CSED | PPIA |
| Low assets + low disposable income | OIC (if RCP < debt) or CNC |
| Unemployed / illness / true hardship | CNC (+ penalty abatement) |
| Big penalty component, otherwise compliant history | FTA / reasonable cause first |
| Debt is spouse's | Innocent spouse (Form 8857) |

Then build the application in Step 5 with `tax-compliance/references/collection-resolution.md`
+ `letter-templates.md`.
