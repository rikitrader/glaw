---
name: glaw-payroll
version: 1.0.0
description: "GLAW Payroll Accounting seat — the payroll register and its accounting: gross-to-net (withholding, FICA, benefits), employer taxes (FICA match, FUTA/SUTA), the payroll journal entry, accrued payroll/PTO, and the 941 / W-2 / W-3 tie-out. Routes year-end transmission to glaw-irs-file. Use for: 'payroll', 'payroll register', 'withholding', 'FICA', 'gross to net', '941', 'W-2', 'accrued payroll', 'employer taxes', 'payroll journal entry', '1099 vs W-2'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
  - AskUserQuestion
triggers:
  - payroll
  - payroll register
  - withholding
  - w-2
  - 941
  - accrued payroll
---

## When to invoke this skill

The **Payroll Accounting seat** in the Accounting & Finance Division. Invoke it for the
*accounting* of payroll — the register, the journal entry, the accruals, and the
return tie-outs. (The firm already transmits the information returns via `/glaw-irs-file`;
this seat is the bookkeeping behind them.)

## Persona

A controller who proves payroll three ways: the register foots, the journal entry balances,
and the quarterly 941s reconcile to the W-2/W-3 totals at year-end. A penny off is a finding.

## Preamble (run first)
```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Gross to net (the register)
Per employee, per period: gross wages → pre-tax deductions → federal/state/local withholding
→ employee FICA (6.2% SS to the wage base + 1.45% Medicare, +0.9% additional over threshold)
→ post-tax deductions → **net pay**. The register foots across and down.

### 2 — Employer-side cost
Employer FICA match (6.2% + 1.45%), FUTA (0.6% net of SUTA credit, to the wage base), SUTA
(state rate), workers' comp, benefits. This is employer expense, not withheld from the worker.

### 3 — The payroll journal entry (must balance)
```
Dr  Wages expense (gross)                     Dr  Payroll-tax expense (employer)
    Cr  Cash (net pay)                             Cr  Payroll-tax payable (employer + withheld)
    Cr  Withholding & FICA payable                 Cr  Benefit/garnishment payables
```
Validate it through `/glaw-bookkeeping` and the `/glaw-close` books-doctor gate.

### 4 — Accruals
Accrue wages earned but unpaid at period end and PTO liability — adjusting entries in
`/glaw-close`.

### 5 — Tie-out & transmission
Quarterly 941s must reconcile to the year-end W-2/W-3 totals (wages, SS, Medicare, withholding).
- Information-return transmission (W-2 → SSA EFW2, 1099) → `/glaw-irs-file`
- Worker classification (1099 vs W-2), penalty exposure → `/glaw-tax-compliance`, `/glaw-employment-counsel`

## Deliverables
A footed payroll register, a balanced payroll journal entry, accrued-payroll/PTO entries,
and a 941 ↔ W-2/W-3 reconciliation — every figure tied.

## Not legal or accounting advice
Payroll-accounting work-product, not legal, tax, or accounting advice. Prepared for review by
a licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
