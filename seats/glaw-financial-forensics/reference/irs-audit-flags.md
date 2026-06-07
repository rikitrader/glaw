# IRS Audit Flags — Catalog, Risk Tiers & Rebuttals

The Adversarial IRS Agent works this catalog. For each flag: the **trigger**, the **risk
tier**, the **IRC/issue**, and the **evidence that rebuts it**. Ground audit technique in
`knowledge/irs-construction-industry-audit-technique-guide.md` and
`knowledge/irs-fs-2007-22-construction-tax-gap.md` (search the KB and cite).

> Tier definitions: **Low** = documentation/cleanup; **Moderate** = likely adjustment or
> questions on exam; **High** = material adjustment + penalty exposure; **Critical** =
> badge-of-fraud / criminal referral / structuring exposure.

## A. Income / Revenue
| # | Flag (trigger) | Tier | Issue | Rebuttal evidence |
|---|----------------|------|-------|-------------------|
| A1 | Bank deposits **exceed** reported gross receipts | High | Unreported income (§61). The IRS bank-deposits method is the classic contractor reconstruction. | Reconcile each deposit: loans, transfers, owner capital, refunds, customer payments. Tie remainder to 1099-K/sales journal. |
| A2 | Cash deposits with no invoice trail | High | Unreported cash receipts; common in construction tax gap. | Deposit slips, customer contracts, job files. |
| A3 | 1099-K (merchant) gross > reported revenue | Moderate | Gross-vs-net mismatch (fees/refunds/chargebacks net out). | Processor settlement reports reconciling gross → net. |
| A4 | Structuring: repeated cash deposits just under $10,000 | **Critical** | 31 USC §5324 (structuring) + Form 8300. | Legit business reason + contemporaneous records; usually indefensible if patterned. |
| A5 | Round-dollar "revenue" deposits | Moderate | Estimated/fabricated entries. | Source invoice tying to exact amount. |
| A6 | Customer 1099-NEC totals > reported income | High | Third-party matching. | Show inclusion in gross or identify duplicate/erroneous 1099. |

## B. Expenses / Deductions
| # | Flag | Tier | Issue | Rebuttal |
|---|------|------|-------|----------|
| B1 | Personal expenses run through the business | High | Non-deductible personal (§262); constructive distribution. | Reclassify to draws/distributions; produce business-purpose docs. |
| B2 | 100% of vehicle/meals/travel deducted | Moderate | §274 substantiation; meals 50%. | Mileage log, receipts, business-purpose notes. |
| B3 | Large round-dollar expenses, no invoice | Moderate | Substantiation (§6001). | Vendor invoice + proof of payment. |
| B4 | Subcontractor cash payments, no 1099-NEC | High | §6041 information-reporting penalties; possible recharacterization. | Filed 1099-NECs, W-9s, contracts. |
| B5 | Officer comp on 1120S unreasonably low | High | Reasonable-comp / payroll-tax avoidance. | Comp study; reasonable salary before distributions. |
| B6 | Deductions implausible vs revenue (margin) | Moderate | Profit-motive / overstatement. | Industry-benchmarked cost ratios (KB: roofing/CICPAC). |
| B7 | Expensing items that must be capitalized | Moderate | §263/§263A; UNICAP for contractors. | Capitalization policy + depreciation schedule. |

## C. Method / Construction-specific
| # | Flag | Tier | Issue | Rebuttal |
|---|------|------|-------|----------|
| C1 | Long-term contracts not on PCM where required | High | IRC §460 PCM (cost-to-cost); CCM misuse. | §460 exemptions (small-contractor/home-construction); method election. |
| C2 | No WIP schedule / over-under billings ignored | Moderate | Income timing misstated. | WIP schedule reconciling costs, billings, earned revenue (KB: CICPAC). |
| C3 | Switched methods without Form 3115 | Moderate | §446 method change. | Filed Form 3115 / Rev. Proc. 2016-29 automatic change. |
| C4 | Retainage mishandled | Low | Timing of income/expense on retainage. | Retainage receivable/payable tracking. |

## D. Payroll / Employment
| # | Flag | Tier | Issue | Rebuttal |
|---|------|------|-------|----------|
| D1 | Workers paid as 1099 that look like employees | High | Worker classification (§3121); SS-8. | Behavioral/financial/relationship control analysis. |
| D2 | Payroll on books but no 941/940 trail | High | Trust-fund taxes (§6672) — personal liability. | Filed 941s/940, EFTPS deposits, W-2/W-3. |
| D3 | Owner draws labeled "payroll" w/o withholding | Moderate | Mischaracterization. | Reclassify; verify reasonable comp via real payroll. |

## E. Balance Sheet / Related-Party
| # | Flag | Tier | Issue | Rebuttal |
|---|------|------|-------|----------|
| E1 | Undisclosed/related-party loans | High | Disguised income or §267 / below-market interest (§7872). | Written note, market rate, repayment record. |
| E2 | Loan proceeds booked as revenue (or vice-versa) | High | Misclassification distorts income. | Loan agreement + amortization. |
| E3 | Negative equity / draws > basis | Moderate | Distribution-in-excess-of-basis gain (§731/1368). | Basis schedule. |
| E4 | Cash diversion (deposits missing vs sales) | **Critical** | Skimming — fraud badge. | Full deposit reconciliation. |

## Badges of Fraud (any present → escalate toward Critical)
Two sets of books · destroyed/altered records · consistent cash skimming · structuring ·
fictitious vendors · personal expenses systematically disguised · backdated documents ·
large unexplained net-worth increase. (Civil fraud §6663 = 75% penalty; criminal §7201.)

## Output rule for every finding
`Finding · Tier · Transactions (source-file:line) · IRC/Issue · $ exposure (or [ESTIMATED]) ·
Rebuttal evidence needed.` No finding ships without a transaction citation.
