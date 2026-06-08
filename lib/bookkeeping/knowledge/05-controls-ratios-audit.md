# Controls, reconciliation & ratios

Original notes on keeping the books trustworthy and reading them.

## Internal controls
The policies that keep errors and fraud out of the books.
- **Segregation of duties** — no one person both approves and pays, or both records and
  custodies cash. Splitting duties means fraud needs collusion.
- **Authorization** — transactions are approved before they happen (a PO before a purchase).
- **Three-way match** — pay a vendor only when the **purchase order**, the **goods receipt**,
  and the **invoice** agree on quantity and price.
- **Reconciliation** — independently comparing the books to an outside record (the bank).
- **Audit trail** — the documented chain from each number back to its source, so any entry
  can be re-traced. GLAW hashes every entry and tags its source for this reason.

## Reconciliation
- **Bank reconciliation** — matching the cash ledger to the bank statement, explaining every
  difference: **deposits in transit** (recorded, not yet on the bank), **outstanding checks**
  (written, not yet cleared), and **bank-only items** (fees, interest) to record. The book and
  bank balances must reconcile to the same adjusted figure. GLAW: `glaw-bank-rec`.
- **Account reconciliation** — proving every balance-sheet account's balance to supporting
  detail each period (not just cash). A reconciled account is one you can defend.

## Audit terms
- **Audit** — an independent examination that the financial statements are fairly stated.
- **Tie-out** — proving a statement figure back to the GL and the GL back to source.
- **Materiality** — the size of a misstatement that would change a reader's decision; below it,
  small errors are not worth chasing.
- **Assertions** — what the statements implicitly claim: **existence**, **completeness**,
  **valuation**, **rights/obligations**, **cut-off**, **classification**. Auditors test each.
- **Substantive testing** — checking actual balances and transactions for misstatement.
- **Working papers** — the documented evidence supporting the audit conclusion.
- In GLAW, `/glaw-audit` rebuilds the books from source, ties out, runs the control gate, and
  puts the numbers through an adversarial CPA/IRS challenge before issuing an opinion.

## Quality of earnings & adjustments
- **EBITDA** — earnings before interest, tax, depreciation, amortization; a proxy for operating
  cash generation.
- **Normalization / add-backs** — adjusting reported earnings for one-time or owner-specific
  items to show sustainable performance (used in valuation and M&A diligence).

## Key ratios (reading the statements)
| Ratio | Formula | Tells you |
|---|---|---|
| **Current ratio** | current assets ÷ current liabilities | short-term liquidity |
| **Quick (acid-test)** | (current assets − inventory) ÷ current liabilities | liquidity without selling inventory |
| **Gross margin** | gross profit ÷ revenue | pricing/production efficiency |
| **Net margin** | net income ÷ revenue | overall profitability |
| **DSO** | AR ÷ revenue × days | how long to collect receivables |
| **DPO** | AP ÷ COGS × days | how long you take to pay |
| **Debt-to-equity** | total liabilities ÷ equity | leverage |
| **Working capital** | current assets − current liabilities | short-term cushion |
| **Burn / runway** | monthly net cash outflow; cash ÷ burn | how long until out of cash |

## Trust-fund liabilities (handle with care)
Amounts collected/withheld on someone else's behalf — **payroll withholding** and **sales tax**.
They are not the company's money; spending them carries personal-liability exposure for the
responsible person.
