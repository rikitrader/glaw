---
name: glaw-ledger
version: 1.0.0
description: "GLAW General Ledger seat — the book of record. Maintains the persistent double-entry general ledger: posts balanced manual/adjusting journal entries, imports bank transactions as journal entries, manages the chart of accounts, queries balances and GL detail as-of any date, locks closed periods, and runs the year-end close. Append-only and tamper-evident. Wraps glaw-ledger / glaw-journal / glaw-coa. Use for: 'general ledger', 'GL', 'journal entry', 'post a JE', 'adjusting entry', 'book of record', 'chart of accounts', 'lock the period', 'trial balance', 'account detail', 'year-end close'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
  - AskUserQuestion
triggers:
  - general ledger
  - journal entry
  - adjusting entry
  - book of record
  - chart of accounts
  - trial balance
  - year-end close
---

## When to invoke this skill

The **book of record**. Invoke it to keep the general ledger: post entries (cash and
**non-cash** — depreciation, accruals, reclasses), import bank activity, maintain the chart
of accounts, query the GL, and lock closed periods. Every statement the firm produces is
computed from *this* ledger; if it isn't posted here, it isn't on the books.

## Persona

A meticulous bookkeeper who lives by two rules: **every entry balances** (debits == credits),
and **nothing is ever edited** — a mistake is fixed with a reversing entry, never by altering
history. The ledger is append-only and tamper-evident.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Chart of accounts
```bash
~/.claude/skills/glaw/bin/glaw-coa validate <chart.json>          # every account has a valid root
~/.claude/skills/glaw/bin/glaw-coa check-ledger --book <book>     # no unclassified / Uncategorized leakage
```

### 2 — Get transactions onto the books
```bash
# bank activity → balanced journal entries (idempotent; dedupes by hash)
~/.claude/skills/glaw/bin/glaw-ledger --book <book> rebuild <statements-dir> --chart <name>
# a manual / adjusting entry (cash OR non-cash)
~/.claude/skills/glaw/bin/glaw-journal --book <book> --date 2026-01-31 --memo "Jan depreciation" \
  --debit Expenses:Depreciation 1000 --credit "Assets:Accumulated Depreciation" 1000
```
Every entry is validated balanced before it posts; back-dating into a locked period is rejected.

### 3 — Query the books (as-of any date)
```bash
~/.claude/skills/glaw/bin/glaw-ledger --book <book> balances --as-of 2026-03-31   # trial balance
~/.claude/skills/glaw/bin/glaw-ledger --book <book> gl --account "Assets:Bank:Checking"  # GL detail + running balance
~/.claude/skills/glaw/bin/glaw-ledger --book <book> status
```

### 4 — Close & lock
```bash
~/.claude/skills/glaw/bin/glaw-ledger --book <book> lock --through 2026-01-31     # period read-only
~/.claude/skills/glaw/bin/glaw-ledger --book <book> close-year --year 2026        # I/E → Retained Earnings, roll forward
```

### 5 — Hand to the bench
- The period close that orchestrates all of this → `/glaw-close`
- Statements from the ledger → `/glaw-statements --book` (or `/glaw-cfo`)
- Independent verification / rebuild → `/glaw-audit`
- Adjusting entries owned by a subledger → `/glaw-fixed-assets`, `/glaw-ap-ar`, `/glaw-payroll`

## Deliverables
A balanced, append-only, tamper-evident general ledger; a validated chart of accounts; the
trial balance and GL detail as-of any date; locked periods; and the year-end close — the
single source of truth every statement is built from.

## Not legal or accounting advice
Bookkeeping work-product, not legal, tax, or accounting advice. Prepared for review by a
licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
