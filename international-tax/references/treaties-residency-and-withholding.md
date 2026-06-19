# Treaties, Residency & Cross-Border Withholding

The seat computes inclusions and prepares filings; this file is the framework for **who is taxed as
what** and **what must be withheld**. Broad treaty/withholding *planning* belongs to
`/glaw-tax-strategy`; this file is the working reference so the computation rests on the right status.

## U.S. tax residency (the threshold question)

- **Citizens and lawful permanent residents (green-card holders)** are taxed on **worldwide
  income** wherever resident.
- **Substantial Presence Test (§7701(b)):** a non-immigrant is a U.S. resident for tax if present
  **≥ 31 days** in the current year and **≥ 183 weighted days** over a 3-year look-back (current
  year ×1 + prior ×1/3 + second-prior ×1/6). Exceptions: the **closer-connection** exception (Form
  8840) and exempt individuals (students/teachers, Form 8843).
- **Dual-status and treaty tie-breakers:** where two countries both claim residence, an income-tax
  treaty's **residence tie-breaker** (permanent home → center of vital interests → habitual abode →
  nationality) controls; claim it on **Form 8833** (treaty-based return position disclosure).
- **Expatriation (§877A):** the **exit tax** on covered expatriates (net-worth / tax-liability /
  certification thresholds) — flag and route to `/glaw-tax-strategy`.

## Sourcing of income (determines U.S. taxing right over non-residents)

Source rules (§861–865) decide whether income is U.S.-source: services where **performed**;
interest by the **payer's** residence; dividends by the **payer corporation's** residence; rents/
royalties by **where the property is used**; sale of inventory and personal property by special
rules. Source drives both the U.S. tax on a nonresident and the FTC limitation basket for a
U.S. person.

## Non-resident taxation — two regimes

1. **FDAP** (Fixed, Determinable, Annual, Periodical — passive U.S.-source income): a flat **30%
   gross** withholding tax (§871(a) / §881), **reduced or eliminated by treaty**.
2. **ECI** (income **effectively connected** with a U.S. trade or business): taxed on a **net**
   basis at graduated rates (§871(b) / §882), return required.

## Withholding regimes (Chapters 3, 4, and FIRPTA)

| Regime | Statute | What it withholds | Documentation |
|---|---|---|---|
| **Chapter 3 (NRA withholding)** | §1441 / §1442 | 30% on FDAP to non-residents (treaty-reduced) | W-8BEN / W-8BEN-E / W-8ECI; report on 1042 / 1042-S |
| **Chapter 4 (FATCA)** | §1471–1474 | 30% on withholdable payments to non-compliant foreign financial institutions / NFFEs | W-8BEN-E; FFI agreement / IGA |
| **FIRPTA** | §1445 / §897 | 15% on the **gross** sale price of a U.S. real property interest by a foreign person | Form 8288 / 8288-A; withholding certificate to reduce |
| **Partnership §1446** | §1446(a)/(f) | On ECI allocable to foreign partners; §1446(f) on transfer of a partnership interest | — |

**Forms W-8** (foreign payee) and **W-9** (U.S. payee) establish status and treaty eligibility;
the wrong or missing form defaults to 30% backup/NRA withholding.

## Treaty benefits (claim them correctly)

- Treaties **reduce withholding rates** (dividends, interest, royalties), allocate taxing rights,
  provide the **residence tie-breaker**, and contain a **Limitation on Benefits (LOB)** article to
  deny treaty-shopping. A treaty does **not** override the **saving clause** for U.S. citizens
  (the U.S. still taxes its citizens as if no treaty, subject to enumerated exceptions).
- A treaty-based return position is disclosed on **Form 8833** (penalty under §6712 for failure).
- The U.S. does **not** have an income-tax treaty with every country — confirm one exists before
  claiming a benefit.

## FATCA / CRS reality (why "no one will know" is dead)

**FATCA** (Chapter 4) makes foreign financial institutions report U.S. account holders to the IRS;
the **OECD Common Reporting Standard (CRS)** does the reciprocal among ~100+ jurisdictions. Foreign
accounts and entities are reported automatically. Any position that assumes non-detection is
unsound — see `persona-and-guardrails.md`.

## Sales / VAT abroad (flag, don't compute here)

Cross-border sales of goods/services can trigger **foreign VAT/GST** registration and the U.S.
**state** sales/use-tax nexus rules. Route VAT to `/glaw-international` / local counsel and the U.S.
state side to `/glaw-sales-tax`.

> Quote withholding rates and residency day-counts from the treaty in play and from
> `tax-legal-shared/current-figures.md`; verify the specific treaty article on irs.gov / the
> Treasury treaty list before relying.
