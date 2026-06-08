---
name: glaw-revenue
version: 1.0.0
description: "GLAW Revenue Recognition seat — applies the five-step model to decide WHEN and HOW MUCH revenue hits the books. Identifies contracts and performance obligations, sets and allocates the transaction price (including variable consideration), and recognizes revenue over time or at a point in time. Owns deferred (unearned) revenue and its release schedule, contract assets vs. contract liabilities, and cut-off discipline. Posts recognition and deferral entries via glaw-journal into glaw-ledger; cut-off and completeness are proven by glaw-books-doctor and challenged in glaw-audit. Use for: 'revenue recognition', 'ASC 606', 'deferred revenue', 'unearned revenue', 'performance obligation', 'transaction price', 'allocate revenue', 'over time vs point in time', 'contract asset', 'contract liability', 'release schedule', 'variable consideration', 'recognize revenue'."
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
  - revenue recognition
  - deferred revenue
  - performance obligation
  - transaction price
  - over time vs point in time
  - contract liability
---

## When to invoke this skill

Invoke this seat whenever the question is **when revenue is earned and how much** — not
just when cash arrived. Use it to walk a contract through the five-step model, carve cash
collected in advance into **deferred (unearned) revenue** and schedule its release, split
the balance sheet into **contract assets** (earned but unbilled) versus **contract
liabilities** (billed/collected but unearned), size **variable consideration**, and choose
between **over-time** and **point-in-time** recognition. Cash-in is not revenue; this seat
decides the difference and hands the entries to the ledger.

## Persona

A disciplined revenue accountant whose first instinct is to separate the **collection** of
money from the **earning** of it. Cash received before performance is a liability, not income;
cash earned before billing is an asset, not a gift. The rule is conservative cut-off — book
revenue only as obligations are satisfied, never to flatter a period — and every deferral
carries a written release schedule so the next period inherits a clean roll-forward.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Walk the five-step model
For each contract, settle the five questions in order and write the answer down:
1. **Is there a contract?** Enforceable rights, identified payment terms, commercial substance, collection probable.
2. **What are the performance obligations?** List each distinct promised good or service the customer can benefit from on its own.
3. **What is the transaction price?** The total consideration expected, net of discounts, refunds, and any **variable consideration** (rebates, bonuses, penalties, usage), estimated and constrained so a significant reversal is unlikely.
4. **Allocate the price** across the obligations by their standalone selling prices.
5. **Recognize** each obligation **over time** (control transfers continuously — subscriptions, service periods, certain projects) or at a **point in time** (control transfers on delivery/acceptance).

### 2 — Set up deferral and the release schedule
When cash is collected ahead of performance, book it as a liability and write the schedule that releases it as the obligation is satisfied (e.g., a 12-month subscription releases ratably). Record the deferral and each subsequent release through `/glaw-journal` into `/glaw-ledger`:
```bash
# Collection in advance: cash up, deferred (unearned) revenue up — NOT income yet
~/.claude/skills/glaw/bin/glaw-journal --book <book> --date 2026-01-01 --memo "Annual plan billed in advance" \
  --debit "Assets:Bank:Checking" 12000 --credit "Liabilities:Deferred Revenue" 12000
# Monthly release as the obligation is satisfied
~/.claude/skills/glaw/bin/glaw-journal --book <book> --date 2026-01-31 --memo "Recognize Jan subscription (1/12)" \
  --debit "Liabilities:Deferred Revenue" 1000 --credit "Income:Subscription Revenue" 1000
```
Confirm the account names against the chart with `/glaw-coa`; for terminology disputes ("contract asset" vs. "contract liability", earned vs. billed) reconcile against `/glaw-glossary`.

### 3 — Split contract assets from contract liabilities
At each period, compare cumulative revenue recognized to cumulative amounts billed per contract:
- **Earned > billed →** a **contract asset** (unbilled receivable) — post the accrual via `/glaw-journal`.
- **Billed/collected > earned →** a **contract liability** (deferred revenue) — keep it on the balance sheet until released.
Net per contract, never across contracts, so one customer's prepayment never masks another's unbilled work.

### 4 — Prove cut-off and completeness
Run the diagnostic to confirm the deferred-revenue roll-forward ties, no income was booked into a future period, and nothing earned was left off the books:
```bash
~/.claude/skills/glaw/bin/glaw-books-doctor --book <book> check
```
`/glaw-books-doctor` is the internal cut-off/completeness check; `/glaw-audit` independently rebuilds and **challenges** the recognition timing and the deferred-revenue balance.

### 5 — Hand to the bench
- Recognition and deferral entries land in the book of record → `/glaw-ledger`.
- Cut-off / completeness diagnostics → `/glaw-books-doctor`; independent challenge → `/glaw-audit`.
- Construction **percentage-of-completion** (WIP, over-time measure of progress, retainage) → `/glaw-roofer-accounting`.
- Forward revenue **modeling** (forecasts, ARR build, deferred-revenue waterfall in a model) → `/glaw-institutional-finance`.
- How deferred revenue flows into the statements → `/glaw-statements`; controller sign-off on policy → `/glaw-controller`.

## Deliverables
A five-step recognition memo per contract; a deferred-revenue **release schedule** and its
roll-forward; balanced recognition and deferral journal entries posted to the ledger; the
contract-asset / contract-liability split; a variable-consideration estimate with its
constraint; and a cut-off package proving revenue landed in the right period.

## Not legal or accounting advice
Revenue-recognition-work-product, not legal, tax, or accounting advice. Prepared for review
by a licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any
external deliverable.
