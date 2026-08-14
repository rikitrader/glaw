---
updated_as_of: 2026-06-16
max_age_days: 120
owner: GLAW Tax Compliance
status: source-index
---

# Current Figures Source Index

This file is the shared source-of-truth index for rates, thresholds, penalties,
filing limits, contribution limits, mileage rates, inflation adjustments, and
other numeric tax/legal figures used by GLAW tax, accounting, corporate, and IRS
workflows.

The index is deliberately fail-closed:

- Do not quote a figure from memory.
- Do not invent a missing amount.
- Do not rely on a stale number when a live source is required.
- If a figure is not listed below with an `as_of`, `source_url`, and
  `verified_by`, keep it in review and cite the missing figure as a red flag.

## Required Entry Shape

Every numeric figure used in a client-facing tax/legal deliverable must be added
in this shape before final packet approval:

```text
figure_id: FIG-YYYY-####
label:
jurisdiction:
tax_year_or_period:
value:
as_of:
source_url:
source_owner:
verified_by:
notes:
```

## Official Source Families

Use primary-source URLs wherever possible:

- IRS forms and instructions: `https://www.irs.gov/forms-instructions`
- IRS publications: `https://www.irs.gov/publications`
- IRS news releases and tax inflation adjustments: `https://www.irs.gov/newsroom`
- Internal Revenue Bulletin: `https://www.irs.gov/irb`
- Treasury regulations / CFR: `https://www.ecfr.gov/current/title-26`
- United States Code: `https://uscode.house.gov/`
- SEC rules and forms: `https://www.sec.gov/rules-regulations`
- FinCEN BOI and BSA guidance: `https://www.fincen.gov/boi`

## Active Figure Entries

figure_id: FIG-2026-QSBS-0001
label: QSBS aggregate gross asset threshold for stock issued after July 4, 2025
jurisdiction: US federal
tax_year_or_period: stock issued after 2025-07-04
value: $75,000,000, indexed for taxable years beginning after 2026
as_of: 2026-08-13
source_url: https://uscode.house.gov/view.xhtml?edition=prelim&path=%2Fprelim%40title26%2FsubtitleA%2Fchapter1%2FsubchapterP
source_owner: U.S. Code, 26 U.S.C. section 1202
verified_by: GLAW Tax Strategy
notes: IRS 2025 Schedule D (Form 1120-S) instructions also state the $75M threshold and the $50M rule for stock issued on or before July 4, 2025.

figure_id: FIG-2026-QSBS-0002
label: QSBS aggregate gross asset threshold for stock issued on or before July 4, 2025
jurisdiction: US federal
tax_year_or_period: stock issued on or before 2025-07-04
value: $50,000,000
as_of: 2026-08-13
source_url: https://www.irs.gov/instructions/i1120ssd
source_owner: IRS Instructions for Schedule D (Form 1120-S), 2025
verified_by: GLAW Tax Strategy
notes: Verify against issuer-specific acquisition/issuance date and all predecessor/controlled-group assets.

figure_id: FIG-2026-QSBS-0003
label: QSBS post-July 4, 2025 per-issuer dollar cap
jurisdiction: US federal
tax_year_or_period: stock issued after 2025-07-04
value: $15,000,000 or 10 times basis, subject to current-law holder-specific rules
as_of: 2026-08-13
source_url: https://uscode.house.gov/view.xhtml?edition=prelim&path=%2Fprelim%40title26%2FsubtitleA%2Fchapter1%2FsubchapterP
source_owner: U.S. Code, 26 U.S.C. section 1202
verified_by: GLAW Tax Strategy
notes: Confirm married filing allocation, prior exclusions, holder transfers, and state conformity before use.

figure_id: FIG-2026-QSBS-0004
label: QSBS post-July 4, 2025 holding-period tiers
jurisdiction: US federal
tax_year_or_period: stock issued after 2025-07-04
value: 50% exclusion after at least 3 years; 75% after at least 4 years; 100% after at least 5 years
as_of: 2026-08-13
source_url: https://uscode.house.gov/view.xhtml?edition=prelim&path=%2Fprelim%40title26%2FsubtitleA%2Fchapter1%2FsubchapterP
source_owner: U.S. Code, 26 U.S.C. section 1202
verified_by: GLAW Tax Strategy
notes: Stock acquired on or before July 4, 2025 remains subject to the prior more-than-5-year framework.
