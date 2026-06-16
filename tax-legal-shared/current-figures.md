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

No reusable numeric figure is currently approved in this source index. Workflows
that require a current tax/legal number must add a sourced `FIG-YYYY-####` entry
first, then cite that figure ID in the workpaper or report.
