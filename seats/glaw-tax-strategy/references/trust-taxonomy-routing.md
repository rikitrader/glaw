# Trust Taxonomy and Routing

This is GLAW's trust classification map. Use it to avoid the common error of treating
"trust" as one vehicle. A trust must be classified on four axes before advice or drafting:

1. Revocability and control: revocable, irrevocable, amendable by limited power, decantable.
2. Tax classification: grantor, non-grantor, simple, complex, charitable/split-interest,
   foreign, domestic, QSST, ESBT, disregarded/nominee, or business/statutory trust.
3. Planning purpose: probate, incapacity, estate freeze, GST/dynasty, creditor protection,
   income-tax planning, charity, insurance, special needs, business succession, investment.
4. Asset fit: founder stock/QSBS, S-corp stock, real estate, life insurance, retirement assets,
   private fund interests, crypto/digital assets, concentrated public stock, operating business.

## Master Trust Types

| Type | Main job | Tax posture | Key administration | GLAW routing |
|---|---|---|---|---|
| Revocable living trust | Probate avoidance, privacy, incapacity continuity. | Grantor, ignored for income tax during life. | Funding/retitling, successor trustee, pour-over will alignment. | `glaw-estate-trusts` |
| A-B / bypass / credit-shelter trust | Preserve estate/GST exemption and manage first-death planning for married couples. | Survivor's trust often revocable/grantor; bypass trust irrevocable after first death. | Formula/disclaimer review, state estate-tax fit, GST allocation, surviving-spouse access. | `glaw-estate-trusts`, `glaw-tax-strategy` |
| Testamentary trust | Created at death under will. | Estate/trust income tax after funding. | Court/probate interface, fiduciary accounting, distributions. | `glaw-estate-trusts`, `glaw-estate-gift-returns` |
| Irrevocable gift trust | Completed gift and estate exclusion. | Grantor or non-grantor. | Separate accounts, fiduciary distributions, Form 709/GST support. | `glaw-estate-trusts`, `glaw-tax-strategy` |
| Dynasty / GST trust | Multi-generation transfer and creditor/divorce protection. | Grantor or non-grantor. | GST allocation, situs, distribution standards, family governance. | `glaw-estate-trusts`, `glaw-asset-protection` |
| IDGT | Estate freeze while grantor pays income tax. | Grantor trust for income tax; estate exclusion targeted. | Seed capital, installment note, valuations, grantor-tax burn. | `glaw-tax-strategy`, `glaw-estate-trusts` |
| GRAT | Transfer appreciation above section 7520 hurdle. | Usually grantor trust. | Annuity payments, term calendar, valuation, remainder tracking. | `glaw-estate-trusts`, `glaw-tax-strategy` |
| GRUT | GRAT variant using fixed percentage of trust value. | Usually grantor trust. | Annual valuation and unitrust payment. | `glaw-estate-trusts`, `glaw-tax-strategy` |
| QPRT | Transfer personal residence at discounted gift value. | Usually grantor trust during retained term. | Residence use, expenses, insurance, term-end leaseback/transfer. | `glaw-estate-trusts` |
| SLAT | Lifetime exemption use with indirect spousal access. | Usually grantor trust. | Separate-property funding, community-property partition review, Form 709, reciprocal-trust review, spouse/death/divorce access risk, basis tradeoff, HEMS/independent-trustee limits. | `glaw-estate-trusts`, `glaw-tax-strategy` |
| ILIT | Own life insurance outside estate. | Usually grantor trust during life. | Policy ownership, premium gifts, Crummey notices, incidents of ownership, section 2035 three-year rule, IRA/RMD/tax source-of-funds screen. | `glaw-estate-trusts`, `glaw-asset-protection` |
| CRT / CRAT / CRUT / NIMCRUT | Charitable remainder, income stream, gain deferral. | Split-interest charitable trust. | Payout calculations, charitable remainder tests, tax reporting. | `glaw-tax-strategy`, `glaw-exempt-org` |
| CLT / CLAT / CLUT | Charity first, family remainder. | Split-interest charitable trust. | Lead payments, valuation, charitable reporting. | `glaw-tax-strategy`, `glaw-exempt-org` |
| Charitable trust / private foundation-adjacent trust | Charitable purpose. | Charitable or split-interest rules. | Self-dealing, expenditure responsibility, 990/990-PF/4947 issues. | `glaw-exempt-org`, `glaw-tax-strategy` |
| DAPT | Self-settled creditor protection in permitting state. | Usually grantor trust. | Solvency, seasoning, situs trustee, fraudulent-transfer screen. | `glaw-asset-protection` |
| Offshore APT | Stronger deterrence/creditor protection. | Usually grantor trust for U.S. settlor. | FBAR/FATCA, Form 3520/3520-A, foreign trustee/custody. | `glaw-asset-protection`, `glaw-international-tax` |
| DING / NING / ING | State income-tax planning and some protection. | Incomplete gift, non-grantor targeted. | Distribution committee, PLR/current-law review, state-source income. | `glaw-tax-strategy`, `glaw-asset-protection` |
| Spendthrift trust | Protect beneficiary interest from creditors. | Depends on trust design. | Distribution discretion, anti-alienation terms, beneficiary records. | `glaw-estate-trusts` |
| Discretionary trust | Give trustee flexible distribution authority for changing beneficiary facts. | Depends on design. | Trustee selection, HEMS vs broader discretion, beneficiary communication, records. | `glaw-estate-trusts`, `glaw-asset-protection` |
| Special needs trust - third-party | Preserve benefits and supplement care. | Usually non-grantor or complex trust. | SSI/Medicaid limits, distribution purpose, care plan. | `glaw-estate-trusts` |
| Special needs trust - first-party / d4A | Hold disabled beneficiary assets with payback. | Usually grantor or complex depending facts. | Medicaid payback, age/disability requirements, court/agency approval. | `glaw-estate-trusts` |
| Pooled special needs trust / d4C | Nonprofit pooled trust for disabled beneficiary. | Varies. | Joinder agreement, nonprofit trustee, Medicaid payback/retention. | `glaw-estate-trusts`, `glaw-exempt-org` |
| Medicaid income trust / Miller trust / QIT | Medicaid income eligibility in applicable states. | Usually grantor/simple administrative vehicle. | Monthly income routing, state Medicaid compliance. | `glaw-estate-trusts` |
| QSST | Eligible S-corp trust for one beneficiary. | S-corp special trust election. | Single beneficiary, income distribution rules, timely election. | `glaw-tax-strategy`, `glaw-corporate-counsel` |
| ESBT | Eligible S-corp trust for multiple beneficiaries. | S-corp special trust election. | ESBT election, separate S portion, high-rate tax, beneficiary limits. | `glaw-tax-strategy`, `glaw-corporate-counsel` |
| Voting trust | Centralize voting control. | Usually not a wealth-transfer vehicle by itself. | Voting agreement, term limits, securities/corporate law. | `glaw-corporate-counsel`, `glaw-pe-vc-counsel` |
| Land trust | Privacy/title holding for real estate in some states. | Usually grantor/nominee-like depending design. | Trustee powers, beneficiary interests, lender/title treatment. | `glaw-real-estate-counsel`, `glaw-estate-trusts` |
| Delaware statutory trust / DST | Business/statutory trust, often 1031 real estate. | Grantor trust or business entity depending structure. | 1031 limits, sponsor documents, transfer restrictions. | `glaw-real-estate-counsel`, `glaw-tax-strategy` |
| Business trust / Massachusetts trust | Business entity in trust form. | May be corporation, partnership, or trust. | Entity classification, securities, governance. | `glaw-entity-architect`, `glaw-tax-strategy` |
| Investment trust / fixed investment trust | Passive investment ownership. | Grantor trust if properly limited. | No active business powers beyond permitted limits. | `glaw-tax-strategy`, `glaw-pe-vc-counsel` |
| Rabbi trust | Nonqualified deferred compensation security. | Grantor trust, assets subject to employer creditors. | Section 409A, employer creditor access, benefit accounting. | `glaw-employment-counsel`, `glaw-tax-strategy` |
| Secular trust | Funded employee benefit/deferred compensation trust. | Employee may be taxed when vested/funded. | 409A, ERISA, payroll/reporting. | `glaw-employment-counsel`, `glaw-tax-strategy` |
| Qualified plan trust | Retirement plan trust. | Tax-exempt qualified-plan trust if compliant. | Exclusive benefit, nondiscrimination, Form 5500. | `glaw-qualified-plan` |
| IRA / custodial trust | Retirement account custodial structure. | IRA tax rules. | Prohibited transactions, UBIT, beneficiary designations. | `glaw-robs-retirement-funding`, `glaw-qualified-plan` |
| Totten / payable-on-death trust | Bank-account probate transfer. | Usually ignored during life. | Beneficiary designation and account titling. | `glaw-estate-trusts` |
| Constructive / resulting trust | Equitable remedy, not planned vehicle. | Depends on court order and property. | Litigation proof, tracing, remedies. | `glaw-litigation`, `glaw-equity/elite-corporate-counsel` |
| Blind trust | Conflict-management and discretion over assets. | Depends on assets and grantor powers. | Independence, reporting, ethics/conflicts. | `glaw-ethics-conflicts`, `glaw-tax-strategy` |
| Purpose trust / pet trust / gun trust | Special-purpose property or beneficiary management. | State-law and tax classification varies. | Purpose limits, trustee powers, state compliance. | `glaw-estate-trusts`, domain seat |

## Trust Tax Classification Rules of Thumb

- Grantor trust: income taxed to grantor or deemed owner; useful for estate freezes and
  administrative simplicity, but not a separate income taxpayer for the grantor-owned portion.
- Non-grantor trust: separate taxpayer; can support state planning and QSBS stacking in some
  cases, but compressed brackets, fiduciary income-tax rules, DNI, and state-source income matter.
- Simple trust: generally must distribute all income currently and has limited charitable/corpus
  distribution behavior.
- Complex trust: anything not simple; can accumulate income, distribute corpus, or make charitable
  distributions depending the instrument.
- Domestic vs foreign trust: apply the court test and control test; foreign classification can
  trigger Form 3520/3520-A, FBAR/FATCA, throwback rules, and international-tax routing.
- Business/statutory trust: do not assume Subchapter J trust treatment; classify under entity-tax
  rules and the governing instrument.

## Founder / Investor Asset Fit

| Asset or situation | Trust routing |
|---|---|
| QSBS founder shares | Direct trust/non-corporate holder analysis; use QSBS packet and shareholder statement. |
| Restricted stock / 83(b) | Route before issuance or immediately at transfer; 30-day deadline controls. |
| S-corp shares | QSST/ESBT/grantor trust screen before transfer. |
| Concentrated public stock | Consider CRT, exchange fund, collar/hedge, borrowing, charitable, and estate-transfer options. |
| Operating company equity | Buy-sell, voting/control, transfer restrictions, valuation, and creditor screen. |
| Real estate | LLC/SPE, land trust, QPRT, 1031/DST, insurance, and lender/title review. |
| Life insurance | ILIT if estate liquidity or estate exclusion is the goal; check policy ownership, premium gifts, Crummey notices, incidents of ownership, and section 2035. |
| Retirement assets | Beneficiary designation and qualified-plan/IRA rules usually control; do not fund trusts/LLCs with IRA assets without prohibited-transaction, RMD, income-tax, and inherited-IRA review. |
| Private fund interests | Subscription, transfer, KYC, ERISA, tax form, and securities-law review. |

## Administration Gate

Every estate/trust matter must check these before drafting is called complete:

- Beneficiary designations: retirement plans, IRAs, life insurance, annuities, TOD/POD accounts,
  and transfer-on-death deeds. These can override the will/trust plan.
- Title and funding: every real estate parcel, brokerage account, business interest, bank account,
  vehicle, digital asset, and valuable personal item is either funded, assigned, excluded with a
  reason, or handled by beneficiary designation.
- Situs and trustee: state income tax, state estate/inheritance tax, dynasty/perpetuities rules,
  asset-protection law, trustee residency, corporate trustee capacity, and court jurisdiction.
- SLAT controls: separate-property proof, community-property partition if needed, Form 709/GST,
  reciprocal-trust doctrine, spouse/death/divorce access risk, basis tradeoff, and HEMS vs
  independent-trustee discretion.
- ILIT controls: policy ownership, new-policy vs existing-policy transfer, section 2035,
  premium gifts, Crummey notices, IRA/RMD/tax source of premium funding, underwriting,
  insurance economics, and estate liquidity need.
- Distribution design: equal vs equitable, HEMS, discretionary standards, special-needs terms,
  substance-use/creditor/divorce provisions, education incentives, and personal-property memo.
- Review cadence: annual beneficiary/title review, law-change review, trustee report, tax return,
  Crummey notices, GRAT annuity, ILIT premiums, QPRT term, and Form 709/GST reporting.
- Public benchmark refresh: record whether Schwab Learn trust topic coverage or another approved
  public-trust education benchmark was checked for current trust-administration issues before the
  client packet is marked fresh.

## Required Output

Every trust memo should include:

- Classification table: revocable/irrevocable, grantor/non-grantor, domestic/foreign, simple/complex.
- Purpose and asset-fit table.
- Trustee administration checklist.
- Beneficiary-designation and title/funding checklist.
- Trust situs/trustee selection analysis.
- Distribution-design memo, including equal vs equitable and special-needs considerations.
- Tax filings and reporting calendar.
- Funding/titling/beneficiary-designation checklist.
- Fraudulent-transfer and creditor screen.
- Direct-ownership carve-out analysis for founder stock, QSBS, S-corp shares, insurance, and retirement assets.
