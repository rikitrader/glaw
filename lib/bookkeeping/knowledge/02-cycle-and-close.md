# The accounting cycle & close

Original notes on the repeating process that turns raw transactions into statements.

## The cycle (per period)
1. **Transaction** happens (a sale, a payment, a wire).
2. **Journalize** — record it as a balanced journal entry.
3. **Post** — write the entry's lines into the general ledger accounts.
4. **Trial balance** — list every account's balance; total debits must equal total credits.
   A trial balance that doesn't balance means a posting error.
5. **Adjusting entries** — period-end entries for things not triggered by a cash event:
   accruals, deferrals, depreciation, prepaids (see file 4).
6. **Adjusted trial balance** — re-run after adjustments; still balanced.
7. **Financial statements** — P&L, balance sheet, cash flow, prepared from the adjusted GL.
8. **Closing entries** (period/year end) — zero the income & expense accounts into retained
   earnings, so the next period starts fresh.
9. **Lock** the period — make it read-only so prior numbers can't change.

GLAW runs this as `/glaw-close`: ingest → reconcile → adjust → **books-doctor gate** →
statements → sign-off → lock.

## Key terms
- **Posting** — moving a journalized entry into the ledger accounts. Until posted, it isn't
  on the books.
- **Trial balance (TB)** — proof that debits == credits across all accounts. The first gate.
- **Adjusting entry** — a JE recorded at period end to put income and expense in the right
  period (matching). Most have **no cash leg** (e.g. depreciation), which is why a real
  ledger must accept non-cash entries.
- **Reclassification (reclass)** — an entry that moves an amount from one account to a more
  correct account, without changing net income.
- **Closing entries** — year-end JEs that transfer the income-statement balances to
  **Retained Earnings**; afterward Income and Expense start the new year at zero.
- **Cut-off** — the discipline of recording a transaction in the period it actually belongs
  to (a December sale is December revenue, even if cash arrives in January).
- **Period lock / hard close** — once reviewed and signed, the period is frozen; later
  corrections go to an **open** period as adjusting/reversing entries.
- **Roll-forward** — carrying each balance-sheet account's ending balance into the next
  period as its opening balance.

## What "the books are closed" means
Every account is reconciled, the trial balance balances, the statements tie, adjustments are
posted, and the period is locked. In GLAW, "closed" = the `glaw-books-doctor` gate is green
and `glaw-ledger lock` has been run.
