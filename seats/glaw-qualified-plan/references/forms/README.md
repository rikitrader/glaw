# Qualified Plan IRS Forms Library

Official IRS PDFs for the qualified-plan compliance workflow, downloaded from irs.gov on 2026-06-21. These are
**blank official forms + Pub 560** — the seat drafts/maps them for a licensed ERISA attorney + CPA / enrolled
actuary to review, sign, and file. **The agent never transmits anything to the IRS or DOL.** Re-pull annually
(forms are revised yearly): `curl -sL -o <file> https://www.irs.gov/pub/irs-pdf/<file>`.

| File | Form | Role in the qualified-plan lifecycle | Filed where |
|------|------|--------------------------------------|-------------|
| `f5500.pdf` | Form 5500 | Annual return/report for a plan with employees / ≥ filing tier (req. #21) | **DOL EFAST2** (+ IRS) |
| `f5500ez.pdf` | Form 5500-EZ | Annual return for a **one-participant** plan (small-plan <$250k exception; **not** for ROBS) | IRS |
| `f1099r.pdf` | Form 1099-R | Reports **distributions** and rollovers (reqs. #11, #14, #21) | IRS + recipient |
| `f5300.pdf` | Form 5300 | **Determination letter** application — individually-designed plan | IRS |
| `f5307.pdf` | Form 5307 | Determination letter — **adopter of a pre-approved** plan | IRS |
| `f5310.pdf` | Form 5310 | Determination on **plan termination** (wind-down) | IRS |
| `f8717.pdf` | Form 8717 | **User-fee** transmittal for the determination application | IRS |
| `f8950.pdf` | Form 8950 | **EPCRS VCP** application — voluntary correction of a plan failure | IRS via pay.gov |
| `f5330.pdf` | Form 5330 | **Excise taxes** — §4975 prohibited transaction, §4971 funding, §4972 nondeductible, §4979 excess | IRS |
| `p560.pdf` | Pub. 560 | *Retirement Plans for Small Business* — SEP, SIMPLE, and qualified-plan limits reference | n/a (reference) |

## Note on Form 5500-SF
Form **5500-SF** (short form for small plans) is filed **only electronically through DOL EFAST2** — there is no
fillable IRS PDF at `irs.gov/pub/irs-pdf/`. Prepare it in the EFAST2 system (IFILE) or approved software.

## Lifecycle order (typical qualified plan)
1. **Adopt / restate:** pre-approved document (vendor opinion letter) **or** individually-designed + **Form 5300/5307
   + 8717** determination letter.
2. **Operate:** annual **Form 5500 / 5500-EZ** (req. #21) + **Form 1099-R** on distributions; run the 21-requirement
   audit (`bin/qp_compliance_check.py`).
3. **Correct (if a defect is found):** SCP (no filing) → **VCP (Form 8950)** → Audit CAP; prohibited transactions →
   **Form 5330**. See `../correction-and-determination.md`.
4. **Terminate:** **Form 5310** determination on termination + final **Form 5500** + final distributions/1099-R.

> The matching legal analysis lives in `../qualified-plan-requirements.md` (the 21 requirements) and
> `../correction-and-determination.md` (EPCRS + determination + §4975/5330). Attorney/CPA work-product — not
> legal/tax advice; the agent never files.
