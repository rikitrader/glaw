# Financial statements & accounts

Original notes on the four statements and the accounts behind them.

## The four statements
- **Income statement (P&L / profit and loss)** — revenue minus expenses over a *period* =
  net income. Shows performance.
- **Balance sheet (statement of financial position)** — assets, liabilities, and equity at a
  *point in time*. Always balances: Assets = Liabilities + Equity. Shows what is owned/owed.
- **Statement of cash flows** — the change in cash over a period, split into **operating**
  (running the business), **investing** (buying/selling assets), and **financing** (debt and
  equity). Reconciles why cash moved even when profit didn't.
- **Statement of changes in equity** — how equity moved (contributions, distributions, and
  net income flowing into retained earnings).

In GLAW, `glaw-statements` / `/glaw-cfo` produce all four from the posted ledger, and they
tie by construction.

## Account types (the five roots)
| Root | Statement | Examples |
|---|---|---|
| **Assets** | Balance sheet | cash, AR, inventory, prepaid, equipment, accumulated depreciation (contra) |
| **Liabilities** | Balance sheet | AP, accrued expenses, payroll/sales-tax payable, loans |
| **Equity** | Balance sheet | contributed capital, retained earnings, distributions |
| **Income / Revenue** | Income statement | sales, service revenue, interest income |
| **Expenses** | Income statement | wages, rent, materials, depreciation, professional fees |

- **Current vs non-current** — current = within one year (cash, AR, AP); non-current =
  longer (equipment, long-term debt).
- **Contra account** — an account that offsets another (e.g. **Accumulated Depreciation**
  reduces a fixed asset; **Allowance for Doubtful Accounts** reduces AR).

## Common accounts & terms
- **Accounts receivable (AR)** — money customers owe you (an asset). Tracked in the AR
  subledger and **aged** (`/glaw-ap-ar`).
- **Accounts payable (AP)** — money you owe vendors (a liability). Aged the same way.
- **Inventory** — goods held for sale (asset); becomes **COGS** (cost of goods sold, an
  expense) when sold.
- **Retained earnings** — cumulative net income not distributed; the link between the
  income statement and the balance sheet.
- **Working capital** — current assets minus current liabilities; short-term liquidity.

## Subledgers
Detailed books that support a single GL **control account**: AP, AR, fixed assets, payroll,
inventory. Each subledger total must **reconcile to its GL control account** every period —
a core control. GLAW: `/glaw-ap-ar`, `/glaw-fixed-assets`, `/glaw-payroll`.

## Chart of accounts (COA)
The organized list of every account a business uses, with its type. A good COA has no
catch-all leakage (transactions shouldn't pile up in `Uncategorized`). GLAW validates it with
`glaw-coa` and ships starter charts (`fund`, `roofing`, `personal`).
