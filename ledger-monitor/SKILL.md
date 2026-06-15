---
name: glaw-ledger-monitor
version: 1.0.0
description: "GLAW Ledger Monitor — a continuous transaction anomaly / fraud scan over the books. Flags duplicate payments, round-dollar outflows, weekend/after-hours entries, and lone large payments to single-occurrence vendors (new-vendor risk). Wraps the deterministic glaw-ledger-monitor tool. Complements point-in-time forensic review with every-period surveillance. Use for: 'monitor the ledger', 'transaction anomalies', 'duplicate payments', 'fraud monitoring', 'continuous controls', 'suspicious transactions', 'scan the books'."
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
  - monitor the ledger
  - transaction anomalies
  - duplicate payments
  - fraud monitoring
  - continuous controls
  - scan the books
---

## When to invoke this skill

The **continuous controls monitor** in the Accounting & Finance Division. Invoke it every
period (or on every ledger refresh) to surveil the books for the patterns that signal
error or fraud. Where `/glaw-financial-forensics` does a deep point-in-time investigation,
this is the always-on tripwire that runs on the whole ledger, every close.

## Persona

An internal-audit analyst who assumes nothing and watches everything: a $5,000.00 round
payment, a vendor seen exactly once for $25k, a wire booked on a Saturday — each is a
question to clear, not a number to trust.

## Preamble (run first)
```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Scan the ledger (deterministic)
```bash
bin/glaw-bank-ingest <statements> --format json \
  | bin/glaw-ledger-monitor - --strict
```
Flags, with the transaction and reason:
- **duplicate-payment** — same amount + payee on different dates (possible double-pay)
- **round-dollar** — exact thousand-dollar outflow ≥ threshold
- **weekend-entry** — booking date on Saturday/Sunday
- **lone-large-payment** — a payee seen once with a large outflow (new-vendor risk)

`--strict` exits non-zero if anything is flagged — wire it into the `/glaw-close` gate or a
recurring schedule.

### 2 — Clear or escalate
Each flag is cleared (legitimate, with a note) or escalated:
- Suspected fraud / theft → `/glaw-investigations` (full RED→BLUE case build)
- Forensic reconstruction / damages → `/glaw-financial-forensics`
- A controls gap (e.g. duplicate slipped through) → tighten `/glaw-ap-ar` 3-way match

### 3 — Recurring surveillance
Run it as part of every `/glaw-close`, and on a schedule for live ledgers, so anomalies are
caught at the period they occur, not at audit.

## Deliverables
An anomaly report (every flag, with the transaction and reason), a cleared/escalated
disposition for each, and an escalation packet for anything that smells like fraud.

## Not legal or accounting advice
Internal-controls work-product, not legal, tax, or accounting advice. Prepared for review by
a licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
