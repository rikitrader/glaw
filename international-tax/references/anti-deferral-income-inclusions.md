# Anti-Deferral Income Inclusions — Subpart F, GILTI/NCTI, FDII, BEAT, §163(j)

The U.S. taxes its persons on worldwide income but historically let foreign-corporation earnings
defer until repatriated. The anti-deferral regimes claw that back. This file is the income-tax
("what's taxable") half of the seat; the information-return half is in
`foreign-asset-reporting.md`. **All effective rates and dollar thresholds defer to
`tax-legal-shared/current-figures.md`** (verify current — OBBBA 2025 changed several).

## Controlled foreign corporation (CFC) — the gateway concept

- A **CFC** is a foreign corporation more than **50%** owned (vote or value) by **U.S.
  shareholders** (§957). A **U.S. shareholder** is a U.S. person owning **10%** or more (vote or
  value) (§951(b)). Attribution rules (§958) pull in indirect and constructive ownership — and the
  2017 repeal of §958(b)(4) sweeps in many foreign-parented structures ("downward attribution").
- CFC status is the gate: it triggers Subpart F, GILTI, and the Form 5471 filing.

## Subpart F income (§951–965) — current inclusion of mobile income

U.S. shareholders of a CFC include their pro rata share of **Subpart F income** currently, even
without a distribution. The core categories:

- **Foreign base company income (§954):** foreign personal holding company income (passive —
  dividends, interest, rents, royalties), foreign base company sales income, and services income.
- **Insurance income (§953)** and certain international-boycott / illegal-payment income (§952).

Key reliefs and limits: the **high-tax exception** (§954(b)(4)), the **de minimis / full-inclusion**
thresholds, the **same-country exceptions**, and the **§954(c)(6) look-through** for CFC-to-CFC
payments. Previously taxed E&P (§959) is not taxed again on distribution.

## GILTI → NCTI (§951A) — the residual current inclusion

**Global Intangible Low-Taxed Income** sweeps in a CFC's active earnings above a routine return.
OBBBA 2025 renamed it **Net CFC Tested Income (NCTI)** and **removed the QBAI (tangible-return)
offset**, so the inclusion is broader. A C-corporation U.S. shareholder gets a **§250 deduction**
(reduced under OBBBA) and an **indirect foreign tax credit (§960)** subject to a haircut — yielding
an effective rate around the mid-teens (**defer the exact rate to current-figures.md**). Individual
U.S. shareholders bear NCTI at individual rates **unless they make the §962 election** (see below).

## FDII → FDDEI (§250) — the export incentive

**Foreign-Derived Intangible Income** (renamed **Foreign-Derived Deduction Eligible Income,
FDDEI**, under OBBBA) gives a domestic C-corporation a **§250 deduction** on income from serving
foreign markets, producing a reduced effective rate (defer the rate to current-figures.md). It is
the carrot paired with the GILTI/NCTI stick.

## BEAT (§59A) — base-erosion minimum tax

The **Base Erosion and Anti-Abuse Tax** applies to large corporations (gross-receipts and
base-erosion-percentage thresholds) that make deductible payments to foreign related parties. It
recomputes tax adding back those base-erosion payments and imposes a minimum. Threshold-gated —
most closely held cross-border businesses are below it, but **test it**, do not assume.

## §163(j) — business interest limitation (cross-border edge)

Business interest deduction is capped (broadly 30% of adjusted taxable income, with carryforward of
disallowed interest). It interacts with cross-border financing and with the anti-deferral regimes;
compute it before finalizing the inclusions.

## Foreign tax credit (§901 / §904 / §960)

Foreign income tax can be credited against U.S. tax, **limited by basket** (§904: GILTI/NCTI
basket, foreign-branch basket, passive, general) so credits in one basket cannot shelter income in
another. The **§960 deemed-paid credit** flows GILTI/Subpart F foreign taxes to the U.S.
shareholder, subject to the GILTI-basket haircut. Excess credits do not refund; they carry.

## Pillar Two (OECD GloBE) — the overlay to flag

For MNE groups above the OECD revenue threshold, the **15% global minimum tax** (GloBE / Pillar
Two) may apply through other countries' IIR/UTPR even where the U.S. regimes do not reach. Flag it
and route the multinational-group modeling to `/glaw-tax-strategy`.

## Order of operations (compute, then reconcile)

1. Identify CFCs and U.S. shareholders (§957/§951(b)/§958 attribution).
2. Compute Subpart F (§954) → GILTI/NCTI (§951A) on the residual.
3. Apply §250 (NCTI deduction and FDDEI), §960 FTC, and §904 basket limits.
4. Test BEAT (§59A) and §163(j); flag Pillar Two.
5. Decide §962 (individual shareholders) — see `foreign-asset-reporting.md` and `/glaw-tax-strategy`.
6. Tie every inclusion to the foreign entity's E&P/FBCI via `/glaw-accounting`; deferred tax to
   `/glaw-tax-provision`.

> Reuse the engines: `bin/glaw-gilti`, `bin/glaw-subpart-f`, `bin/glaw-fdii`, `bin/glaw-beat`,
> `bin/glaw-sec163j`, `bin/glaw-intl-forms`. Quote every effective rate / threshold from
> `tax-legal-shared/current-figures.md` and re-verify on irs.gov / law.cornell.edu — OBBBA 2025
> changed the NCTI/FDDEI mechanics.
