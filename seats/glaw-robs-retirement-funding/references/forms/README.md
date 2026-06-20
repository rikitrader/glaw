# ROBS IRS Forms Library

Official IRS PDFs for the ROBS workflow, downloaded from irs.gov on 2026-06-20. These are **blank official
forms + the governing IRS memorandum** — the seat drafts/maps them for a licensed ERISA attorney + CPA to
review, sign, and file. The agent never transmits anything to the IRS or DOL. Re-pull annually (forms are
revised yearly): `curl -sL -o <file> https://www.irs.gov/pub/irs-pdf/<file>`.

| File | Form | Role in the ROBS workflow | Filed where |
|------|------|---------------------------|-------------|
| `robs_guidelines_2008_memo.pdf` | EP ROBS Guidelines (Julianelle memo, 10/1/2008) | **The governing IRS authority** on how examiners view ROBS — read first | n/a (authority) |
| `f5500.pdf` | Form 5500 | Annual plan return for a ROBS plan with employees / ≥ filing tier | **DOL EFAST2** (+ IRS) |
| `f5500ez.pdf` | Form 5500-EZ | One-participant annual return — **but the <$250k exception does NOT apply to ROBS**, so a ROBS plan files anyway | IRS |
| `f1120.pdf` | Form 1120 | The C-corporation's annual income tax return (the operating-company tax) | IRS |
| `f1099r.pdf` | Form 1099-R | Reports the **rollover** into the ROBS plan — IRS flags "failure to issue" as a defect | IRS + recipient |
| `f5300.pdf` | Form 5300 | Application for a **determination letter** on the new plan's qualified status | IRS |
| `f5310.pdf` | Form 5310 | Application for a determination on **plan termination** — used on ROBS **wind-down / exit** after QES redemption | IRS |

## Workflow order (typical ROBS lifecycle)
1. **Set-up:** form C-corp → adopt plan (optionally **Form 5300** determination letter) → roll funds (**Form
   1099-R** issued for the rollover) → plan buys QES.
2. **Operate:** annually file **Form 5500 / 5500-EZ** (plan) + **Form 1120** (C-corp) + keep the independent
   stock valuation current.
3. **Exit / convert:** redeem QES from the plan at current FMV (see `../robs-qes-redemption.md`) → only then
   convert out of C-corp → terminate the plan (**Form 5310**).

> The matching legal analysis lives in `../robs-irs-compliance-project.md` (IRS position + findings) and the
> seat's `SKILL.md` knowledge base. Attorney/CPA work-product — not legal/tax advice; the agent never files.
