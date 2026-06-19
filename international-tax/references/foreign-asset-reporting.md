# Foreign-Asset Reporting — FBAR, FATCA (8938), 5471/5472/8865/8858, §962

The **information regime** is where the penalty risk concentrates: these filings are due
**regardless of whether any tax is owed**, and the penalties are fixed and large. Treat disclosure
as mandatory, never discretionary. **All dollar thresholds defer to
`tax-legal-shared/current-figures.md`** (verify current).

## FBAR — FinCEN Form 114 (Report of Foreign Bank and Financial Accounts)

- **Authority:** 31 U.S.C. §5314; 31 C.F.R. §1010.350 (Bank Secrecy Act — **not** the Internal
  Revenue Code; filed with **FinCEN**, separately from the tax return).
- **Who:** a U.S. person with a financial **interest in or signature authority over** foreign
  financial accounts whose **aggregate maximum value exceeds $10,000** at any point in the year.
- **What counts:** bank, brokerage, certain insurance/annuity, and some foreign-held crypto-asset
  accounts (the reporting reach over digital assets has been expanding — verify current rule).
- **Deadline:** **April 15**, with an **automatic extension to October 15** (no form required).
- **Penalties (defer exact figures to current-figures.md):** non-willful — up to a per-*report*
  cap (*Bittner v. United States*, 143 S. Ct. 713 (2023): non-willful penalty is **per report, not
  per account**); willful — the **greater of ~$100k (indexed) or 50% of the balance**, per year,
  plus criminal exposure (31 U.S.C. §5322). Willfulness is the line that changes everything.

```bash
bin/glaw-fbar-8938 --max-aggregate <amt> --year-end-aggregate <amt> \
  --status single|mfj --residence us|abroad --cfc-inclusion <GILTI/SubF inclusion>
```

## Form 8938 — Statement of Specified Foreign Financial Assets (FATCA, §6038D)

- **Authority:** IRC §6038D (FATCA); filed **with the income-tax return** (Title 26 — distinct from
  the FBAR's Title 31).
- **Who:** specified persons holding **specified foreign financial assets** above thresholds that
  **vary by filing status and U.S.-vs-abroad residence** (higher thresholds for those living
  abroad). Defer the exact thresholds to current-figures.md.
- **Overlap, not substitution:** Form 8938 and the FBAR cover overlapping but not identical assets
  — an asset can be reportable on **both**. File both where both apply.
- **Penalty:** $10,000 base, escalating up to $50,000 for continued failure after notice, plus a
  40% accuracy-related penalty on related underpayments (§6662(j)) and an extended statute of
  limitations (§6501(c)(8)) for the whole return until the form is filed.

## Forms 5471 / 5472 / 8865 / 8858 — entity information returns

| Form | Filer | Trigger | Penalty (defer exact to current-figures.md) |
|---|---|---|---|
| **5471** | U.S. person who is an officer/director/10% shareholder of a foreign corp / CFC | §6038 / §6046 | **$10,000 per form per year** base; +continuation; SOL stays open (§6501(c)(8)) |
| **5472** | 25%-foreign-owned U.S. corp, or foreign corp engaged in U.S. trade/business, with reportable transactions | §6038A / §6038C | **$25,000 per form per year** base |
| **8865** | U.S. person with an interest in a controlled foreign **partnership** | §6038 / §6046A | $10,000-tier, mirroring 5471 |
| **8858** | U.S. person owning a foreign **disregarded entity** / foreign branch | Reg. §1.367 / §6038 | $10,000-tier |

These penalties apply **even with zero tax due** — the single biggest source of foreign-filing
exposure. Fill staged PDFs from computed values:

```bash
bin/glaw-fill-form forms/f8938.pdf forms/f8938.data.json out/f8938-filled.pdf
```

## The §962 election (§962) — individual shareholder relief on GILTI/Subpart F

An **individual** U.S. shareholder bearing GILTI/NCTI or Subpart F at individual ordinary rates may
elect under **§962** to be taxed **as if a domestic C-corporation** on that income: the **21%**
corporate rate, the **§250 deduction**, and the **§960 indirect FTC** become available — at the cost
of a **second layer of tax on actual distribution** (the previously-included amount is taxed again,
less the §962(d) basis adjustment, when distributed as a dividend).

- **When it helps:** high-foreign-tax CFCs (the indirect FTC washes out U.S. tax) and shareholders
  who will not repatriate soon.
- **When it hurts:** low-foreign-tax CFCs with near-term distributions (the second layer dominates).
- It is an **annual** election and **consequential** — `bin/glaw-fbar-8938` gives the rough year-1
  comparison; route the full multi-year model to `/glaw-tax-strategy`. **AskUserQuestion before
  electing.**

## The delinquency cure paths (when prior years were missed)

| Path | For whom | Mechanism | Key risk |
|---|---|---|---|
| **Streamlined Domestic Offshore (SDO)** | U.S.-resident, **non-willful** | 3 years amended returns + 6 years FBARs + 5% Title-26 miscellaneous offshore penalty + non-willful certification | False non-willful cert = fraud |
| **Streamlined Foreign Offshore (SFO)** | Non-resident, **non-willful** | Same filings, **penalty waived** + non-willful certification | Same |
| **Delinquent FBAR / information-return procedures** | No unreported income, reasonable cause | File late with a reasonable-cause statement | Only if income was reported |
| **IRS Voluntary Disclosure Practice (VDP)** | **Willful** exposure | Through Criminal Investigation; pre-clearance; civil penalty framework; avoids referral | Must go through an attorney |

**The fork is willfulness.** A Streamlined non-willful certification is signed **under penalty of
perjury** — if the facts show willfulness, certifying non-willful is itself a crime. Screen for
willfulness first; route any willful/criminal-exposure case to `/glaw-investigations` and a tax
attorney **before anything is filed**. See `persona-and-guardrails.md`.

> Quote every threshold and penalty figure from `tax-legal-shared/current-figures.md`; re-verify on
> irs.gov / fincen.gov — FBAR penalty indexing and the digital-asset reporting reach change.
