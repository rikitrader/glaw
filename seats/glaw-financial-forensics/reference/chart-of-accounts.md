# Chart of Accounts & Classification Map

Canonical account structure for reconstruction. Use the **vendor/keyword → account** rules
to classify normalized payees. When a rule doesn't fit, tag `[ASSUMPTION]` and route doubtful
items to `9999 Suspense / Ask-Client`.

## Account Numbering

| Range | Section |
|-------|---------|
| 1000–1999 | Assets |
| 2000–2999 | Liabilities |
| 3000–3999 | Equity |
| 4000–4999 | Revenue |
| 5000–5999 | Cost of Goods Sold |
| 6000–8999 | Operating Expenses |
| 9000–9999 | Other Income/Expense, Suspense |

## Assets (1000–1999)
- 1000 Cash – Operating · 1010 Cash – Payroll · 1020 Cash – Savings/Reserve
- 1100 Accounts Receivable · 1200 Inventory · 1300 Prepaid Expenses
- 1400 Costs in Excess of Billings (Underbillings — construction WIP asset)
- 1500 Fixed Assets · 1510 Vehicles · 1520 Equipment · 1590 Accumulated Depreciation (contra)

## Liabilities (2000–2999)
- 2000 Accounts Payable · 2100 Credit Card Payable · 2200 Accrued Payroll
- 2210 Payroll Taxes Payable · 2300 Sales Tax Payable
- 2400 Billings in Excess of Costs (Overbillings — construction WIP liability)
- 2500 Line of Credit · 2600 Notes Payable / Loans · 2700 SBA/EIDL Loan

## Equity (3000–3999)
- 3000 Owner's Capital / Contributions · 3100 Owner's Draws (contra) · 3900 Retained Earnings

## Revenue (4000–4999)
- 4000 Sales Revenue · 4100 Service Revenue · 4200 Subscription Revenue
- 4300 Merchant/Processor Deposits (gross) · 4400 Contract Revenue (POC)
- 4900 Other Income

## COGS (5000–5999)
- 5000 Materials · 5100 Inventory Purchases · 5200 Direct Labor
- 5300 Subcontractors · 5400 Equipment Rental (job) · 5500 Job Permits/Fees

## Operating Expenses (6000–8999)
- 6000 Advertising · 6010 Marketing · 6100 Payroll (admin/officer) · 6110 Payroll Taxes
- 6200 Rent · 6300 Utilities · 6400 Insurance · 6500 Professional Fees · 6510 Legal Fees
- 6600 Software/SaaS · 6700 Telecommunications · 6800 Vehicle Expenses · 6810 Fuel
- 6900 Travel · 6910 Meals (50% deductible) · 7000 Office Supplies
- 7100 Repairs & Maintenance · 7200 Bank Charges · 7210 Merchant/Processor Fees
- 7300 Dues & Subscriptions · 7400 Depreciation Expense · 7500 Interest Expense

## Other / Control (9000–9999)
- 9000 Gain/Loss on Asset Sale · 9100 Interest Income
- 9900 Transfers (control — must net to $0) · 9999 Suspense / Ask-Client

---

## Vendor / Keyword → Account Rules

| If normalized payee/description contains… | Classify to |
|---|---|
| stripe, square, paypal, clover, toast, shopify payments, merchant dep | 4300 Merchant Deposits (gross inflow) |
| stripe fee, square fee, processing fee, interchange | 7210 Merchant Fees |
| home depot, lowes, ferguson, sherwin, beacon, abc supply, srs, gaf, owens corning | 5000 Materials |
| (sub) labor, crew, install, 1099 contractor names | 5300 Subcontractors |
| gusto, adp, paychex, quickbooks payroll, "payroll" | 6100 Payroll (split tax portion → 6110) |
| eftps, irs, "941", "940", state withholding | 6110 / 2210 Payroll Taxes |
| facebook ads, meta, google ads, instagram, tiktok ads | 6000 Advertising |
| rent, lease (premises), property mgmt | 6200 Rent |
| fpl, duke, electric, water, gas utility, waste mgmt | 6300 Utilities |
| geico, progressive, state farm, hiscox, liability ins, workers comp | 6400 Insurance |
| cpa, accountant, bookkeep, consultant | 6500 Professional Fees |
| law, attorney, legal, esq | 6510 Legal Fees |
| adobe, microsoft, google workspace, aws, saas, *.io, *.com subscription | 6600 Software |
| verizon, at&t, t-mobile, comcast, ringcentral | 6700 Telecommunications |
| shell, chevron, exxon, bp, wawa, fuel, gas station | 6810 Fuel |
| toll, vehicle, auto repair, tire, oil change | 6800 Vehicle |
| airline, hotel, marriott, delta, uber, lyft, airbnb | 6900 Travel |
| restaurant, doordash, ubereats, grubhub, cafe, coffee | 6910 Meals (50%) |
| staples, office depot, amazon (office) | 7000 Office Supplies |
| nsf, overdraft, "service charge", "monthly fee", wire fee | 7200 Bank Charges |
| sba, eidl, ppp, loan deposit, "loan proceeds" | 2700/2600 Loan (liability — NOT revenue) |
| transfer to/from own account, "online transfer", zelle to self | 9900 Transfers (net to $0) |
| owner name deposit, "capital", "contribution" | 3000 Owner Contributions (equity) |
| atm withdrawal, "cash" | 3100 Draw OR 9999 Suspense — flag for documentation |

## Critical Non-Revenue Inflows (never count as income)
1. **Transfers** between the entity's own accounts → 9900, net zero.
2. **Loan proceeds** → liability (2600/2700).
3. **Owner contributions** → equity (3000).
4. **Refunds/reversals** → contra to the original expense.
5. **Credit-card cash advances** → liability (2100).

Counting any of these as revenue overstates income and *creates* the unreported-income
illusion in reverse — equally wrong for court/IRS purposes. Tie every revenue dollar to a
genuine customer/sales source.
