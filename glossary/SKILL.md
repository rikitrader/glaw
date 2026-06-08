---
name: glaw-glossary
version: 1.0.0
description: "GLAW Accounting Glossary — the firm's original bookkeeping, accounting, and CPA reference. Look up or search any common accounting term (debit/credit, accrual, depreciation, MACRS, reconciliation, materiality, EBITDA, DSO, nexus, retained earnings…) and get a plain-English, GLAW-grounded definition tied to how the books are actually posted and proved. Backed by the glaw-glossary CLI over an originally-authored knowledge base. Use for: 'what does X mean', 'define', 'accounting term', 'bookkeeping glossary', 'what is accrual / depreciation / a journal entry', 'explain this financial term', 'CPA terminology'."
allowed-tools:
  - Bash
  - Read
  - Grep
  - Glob
  - Skill
triggers:
  - what does mean
  - accounting term
  - bookkeeping glossary
  - define
  - explain this financial term
  - cpa terminology
---

## When to invoke this skill

The firm's **accounting glossary and knowledge reference**. Invoke it to define or explain
any bookkeeping/accounting/CPA term, or to ground the finance agents in fundamentals. The
content is **GLAW's own**, written in plain English and tied to how the books are actually
posted and proved — not copied from any copyrighted dictionary or course.

## Look it up (the tool)

```bash
~/.claude/skills/glaw/bin/glaw-glossary lookup accrual        # one term → definition + source
~/.claude/skills/glaw/bin/glaw-glossary search depreciation   # keyword → matching terms
~/.claude/skills/glaw/bin/glaw-glossary list                  # every indexed term
```

## The knowledge base

Five originally-authored references under [`lib/bookkeeping/knowledge/`](../lib/bookkeeping/knowledge):
1. **Foundations** — debits/credits, the accounting equation, double-entry, accounts/journals/ledgers.
2. **The cycle & close** — transaction → JE → post → trial balance → adjust → close → lock.
3. **Statements & accounts** — the four statements, account types, the chart of accounts, subledgers.
4. **Accruals, depreciation & tax** — cash vs accrual, deferrals, depreciation methods, payroll, sales tax.
5. **Controls, reconciliation & ratios** — internal controls, bank rec, audit assertions, the key ratios.

## How the firm uses it
The finance agents consult this base for grounding: `/glaw-ledger` for what an entry is,
`/glaw-controller` for the cycle, `/glaw-cfo` for statements + ratios, `/glaw-audit` for
controls + assertions. When a definition is needed mid-work, look it up here first rather
than guessing.

## Not legal or accounting advice
A grounding reference, not legal, tax, or accounting advice. Prepared for attorney/CPA-reviewed
work-product. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
