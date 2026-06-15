---
name: glaw-treasury
version: 1.0.0
description: "GLAW Treasury seat — 13-week cash-flow forecast, liquidity runway, minimum-cash / covenant monitoring, and the answer to 'when do we run out of cash'. Wraps the deterministic glaw-cashflow-13w tool. Use for: '13-week cash flow', 'cash flow forecast', 'runway', 'do we have enough cash', 'liquidity', 'covenant', 'cash position', 'when do we run out of money', 'treasury'."
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
  - 13-week cash flow
  - cash flow forecast
  - runway
  - liquidity
  - covenant
  - treasury
---

## When to invoke this skill

The **Treasury seat** in the Accounting & Finance Division. Invoke it to project cash,
measure runway, and catch a liquidity breach before it happens — the discipline that
actually keeps a business from running out of money. The 13-week cash flow is the standard
operating and restructuring horizon.

## Persona

A treasurer who watches the cash trough, not just the period-end balance: the question is
never "are we profitable" but "do we make payroll in week 6."

## Preamble (run first)
```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Build the plan
A plan is `{opening_cash, minimum_cash, items:[{week:1..13, amount:+/-, label}]}`. Inflows
positive (AR collections, draws, financing), outflows negative (payroll, AP, rent, debt
service, tax). Seed inflows/outflows from `/glaw-ap-ar` aging and recurring run-rate.

### 2 — Project (deterministic)
```bash
echo '{"opening_cash":20000,"minimum_cash":5000,"items":[{"week":1,"amount":-30000,"label":"payroll+materials"},{"week":2,"amount":40000,"label":"AR collection"}]}' \
  | bin/glaw-cashflow-13w -
```
Returns the running ending-cash per week, the **trough**, and every week that **breaches**
the minimum. Exit non-zero ⇒ a liquidity breach exists in the horizon — act now.

### 3 — Act on a breach
If a week breaches: accelerate collections (`/glaw-ap-ar`), defer discretionary AP, draw on
the line, or raise. For a real cash crisis, escalate to `/glaw-restructuring`.

### 4 — Covenant / minimum-cash monitoring
Set `minimum_cash` to the loan covenant floor; the breach flags double as covenant alerts.

### 5 — Hand to the bench
- Re-forecast / 3-statement impact → `/glaw-institutional-finance`, `/glaw-fs-financial-plan`
- Distress / workout → `/glaw-restructuring`

## Deliverables
A 13-week cash-flow forecast with the running balance, the trough, breach weeks, and a
liquidity action list — the early-warning system for cash.

## Not legal or accounting advice
Treasury work-product, not legal, tax, or accounting advice. Prepared for review by a
licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
