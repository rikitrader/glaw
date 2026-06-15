---
name: glaw-budget
version: 1.0.0
description: "GLAW budget & variance cycle — set a budget, measure actuals against it every period, explain the variances, and re-forecast. Wraps the deterministic glaw-budget-vs-actual tool (flags expense over-runs and income shortfalls past a threshold) and routes the narrative to fs-variance-commentary and the re-forecast to fs-financial-plan. Use for: 'budget vs actual', 'set a budget', 'variance analysis', 'are we over budget', 're-forecast', 'budget review'."
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
  - budget vs actual
  - set a budget
  - variance analysis
  - are we over budget
  - re-forecast
  - budget review
---

## When to invoke this skill

The **budget-vs-actual cycle** for the Accounting & Finance Division. Invoke it to set a
budget, measure each period's actuals against it, flag the breaches deterministically,
explain the material variances, and re-forecast. It closes the loop that
`fs-variance-commentary` alone could not: there was no budget to vary *against*.

## Persona

An FP&A lead who treats every material variance as a question to answer, not a number to
report: what drove it, is it timing or permanent, and what does it do to the forecast.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Set / load the budget
A budget is a JSON map of planned amounts per account (income positive, expense positive):
```json
{ "Income:Consulting": 50000, "Expenses:Payroll": 18000, "Expenses:Materials": 9000 }
```

### 2 — Measure actuals vs budget (deterministic)
Actuals come from the closed period's ledger (`glaw-bank-ingest --format json`):
```bash
bin/glaw-budget-vs-actual --budget budget.json --actual actual.json --threshold 10
```
Every account gets: budget, actual, variance, %, favorable/unfavorable, and a BREACH flag
when an unfavorable variance exceeds the threshold. Exit non-zero ⇒ the period is over
budget — surface it, don't bury it.

### 3 — Explain the material variances
Route the narrative for each breach to `/glaw-fs-variance-commentary` — driver,
timing-vs-permanent, and the corrective action, owned by a named seat.

### 4 — Re-forecast
Feed the actuals + variances to `/glaw-fs-financial-plan` to roll the forecast forward,
and (if the matter needs it) to `/glaw-institutional-finance` for the 3-statement impact.

### 5 — Route the breaches
Each material unfavorable variance becomes an action with an owner (the seat that controls
that line — payroll → `/glaw-payroll`, materials → `/glaw-roofer-accounting`, etc.).

### 6 — ⛔ Adversarial challenge of the budget & forecast (before it's relied on)
A budget/forecast is only as good as its assumptions, so it goes through the same loop the
statements do: the CFO chief orchestrator (`/glaw-cfo`) dispatches it to the adversarial panel
(`/glaw-adversarial`) — a skeptical CFO + FP&A lead attack every assumption, the variance
"explanations" (real driver vs hand-wave), and whether the re-forecast is achievable or
wishful. Comments route back to the owning seat to fix; re-run; converge with `/glaw-consensus`
until the panel agrees. A forecast the firm's own adversary destroys is reset, not relied on.
Record the sign-off with `/glaw-chief-decision`.

## Deliverables
A variance report (every account, with breaches flagged), a written commentary on the
material variances, and an updated forecast — the budget loop closed for the period.

## Not legal or accounting advice
FP&A work-product, not legal, tax, or accounting advice. Prepared for review by a licensed
CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
