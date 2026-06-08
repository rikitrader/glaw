# Foundations

Original plain-English notes on the bedrock of double-entry bookkeeping.

## The accounting equation
**Assets = Liabilities + Equity.** Everything a business owns (assets) was financed
either by what it owes (liabilities) or by the owners' stake (equity). Net income for the
period flows into equity, so the fuller form is **Assets = Liabilities + Equity + (Income − Expenses)**.
This identity must hold at all times; in GLAW it holds *by construction* because every
journal entry is balanced.

## Debits and credits
Every entry has at least one **debit** (left side) and one **credit** (right side), and the
total debits equal the total credits. Debit/credit are not "good/bad" — they are directions:
- **Debit increases** assets and expenses; **decreases** liabilities, equity, income.
- **Credit increases** liabilities, equity, income; **decreases** assets, expenses.

Each account has a **normal balance** — the side it usually carries:
| Account type | Normal balance | Increased by |
|---|---|---|
| Asset | Debit | Debit |
| Expense | Debit | Debit |
| Liability | Credit | Credit |
| Equity | Credit | Credit |
| Income / Revenue | Credit | Credit |

In GLAW's ledger a positive signed balance = a debit balance, negative = a credit balance.

## Double-entry
The system where every transaction affects at least two accounts so the books always
balance. Buying a $200 part with cash: **debit** Expenses:Materials $200, **credit**
Assets:Bank $200. The two legs are equal and opposite — that is what keeps
`Assets = Liabilities + Equity` true.

## Account, journal, ledger
- **Account** — a named bucket for one kind of item (e.g. `Assets:Bank:Checking`,
  `Expenses:Rent`). GLAW uses colon-delimited paths so accounts form a hierarchy.
- **Journal entry (JE)** — one balanced transaction: a date, a memo, and the debit/credit
  lines. The unit you *post*.
- **General ledger (GL)** — the complete, permanent record of all posted entries, by
  account. The **book of record**: if it isn't in the GL, it isn't on the books.
- **T-account** — a teaching shorthand drawing an account as a "T" with debits left, credits
  right; the balance is the difference.

## Source document
The evidence behind an entry — a bank statement line, an invoice, a receipt, a contract.
Audit-grade bookkeeping ties **every entry to a source document**. GLAW carries a source tag
and a transaction hash on each entry so the trail is traceable.

## Append-only / no erasing
A real ledger is **never edited**. A mistake is fixed by posting a **reversing entry** (and
then the correct entry), so history is preserved. GLAW's ledger is append-only and
tamper-evident (each entry is hashed) — the same discipline an auditor expects.
