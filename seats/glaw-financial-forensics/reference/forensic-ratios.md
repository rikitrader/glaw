# Forensic Ratios, Anomaly Indicators & Formulas

Compute every ratio with **named inputs sourced from the reconstructed statements**. Show
numerator/denominator. For construction benchmarks, search the KB (Peterson, CICPAC, KPMG
roofing update) and cite.

## Profitability
| Metric | Formula | Read |
|--------|---------|------|
| Gross Margin % | Gross Profit ÷ Revenue | Materials/labor discipline. Contractor norm varies; benchmark vs KB. |
| Net Margin % | Net Income ÷ Revenue | Bottom-line efficiency. |
| EBITDA | Net Income + Interest + Taxes + Depreciation + Amortization | Operating cash proxy; basis for valuation (KB: roofing M&A multiples). |
| EBITDA Margin % | EBITDA ÷ Revenue | Quality of earnings. |
| Operating Margin % | Operating Income ÷ Revenue | Core ops before financing/tax. |

## Liquidity & Leverage
| Metric | Formula | Read |
|--------|---------|------|
| Current Ratio | Current Assets ÷ Current Liabilities | <1 = liquidity stress. |
| Quick Ratio | (Current Assets − Inventory) ÷ Current Liabilities | Acid test. |
| Debt Ratio | Total Liabilities ÷ Total Assets | Leverage. |
| Debt-to-Equity | Total Liabilities ÷ Equity | Solvency; negative equity = red flag. |
| Working Capital | Current Assets − Current Liabilities | Contractor bonding capacity driver. |

## Cash / Activity
| Metric | Formula | Read |
|--------|---------|------|
| Cash Burn Rate | (Beginning Cash − Ending Cash) ÷ # months (when net-negative) | Runway. |
| Months of Runway | Ending Cash ÷ monthly burn | Survival horizon. |
| Revenue Growth % | (Current − Prior) ÷ Prior | Trend; spikes invite income questions. |
| Expense Trend | Per-category % of revenue over time | Detects inflation/creep. |
| DSO (if AR known) | (AR ÷ Revenue) × days | Collection speed. |

## Construction-specific (search KB → CICPAC, Peterson)
| Metric | Formula | Read |
|--------|---------|------|
| Underbillings | Costs+Est. Earnings in excess of Billings | Asset; large = billing lag / hidden loss. |
| Overbillings | Billings in excess of Costs+Est. Earnings | Liability; large = front-loaded cash, future margin risk. |
| % Complete (cost-to-cost) | Costs incurred ÷ Total estimated costs | IRC §460 PCM driver. |
| Backlog ratio | Signed backlog ÷ annualized revenue | Forward revenue durability. |

## Fraud / Anomaly Indicators (each ⇒ a Phase-5 finding with cited transactions)
1. **Duplicate payments** — same vendor+amount+near date.
2. **Revenue leakage** — merchant gross > recorded sales; voids/refunds spike.
3. **Expense inflation** — round-dollar, ghost vendors, vendor name ≈ employee name/address.
4. **Hidden liabilities** — recurring debits matching a loan amortization not on the books.
5. **Undisclosed loans** — large lump inflow + steady outflow stream.
6. **Missing deposits / skimming** — sales records > deposits; cash sales never banked.
7. **Cash diversion** — ATM/cash withdrawals disproportionate to documented purposes.
8. **Benford's Law** — leading-digit distribution of amounts deviates from expected (1≈30.1%,
   2≈17.6%…); spikes at 4–9 or round numbers suggest fabrication. State it as a *screen*, not
   proof; confirm with transaction-level review.
9. **Period-end clustering** — entries bunched at month/quarter end (timing manipulation).
10. **Even-amount transfers** to related parties.

## Quality-of-Earnings adjustments (normalize before valuation)
Add back: one-time/non-recurring items, owner personal expenses (after reclassifying),
above-market owner comp; subtract: below-market rent/comp, unrecorded liabilities. Show a
bridge from reported Net Income → Adjusted EBITDA with each add-back sourced.
