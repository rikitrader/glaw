---
name: glaw-audit
version: 1.0.0
description: "GLAW Audit Agent — independent assurance over the books. Rebuilds the entire accounting from source statements into the general ledger, ties every balance back to source, runs the bulletproof control gate, scans for anomalies/fraud, then puts the numbers and the methods through an ADVERSARIAL RED→BLUE challenge (skeptical CPA + IRS examiner question everything) before issuing an audit opinion. ZERO fabricated data — every figure traces to a posted journal entry and a source document. Use for: 'audit the books', 'audit ready', 'rebuild the accounting', 'tie out the financials', 'is this auditable', 'CPA review', 'IRS audit defense', 'audit opinion', 'verify the numbers'."
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
  - audit the books
  - audit ready
  - rebuild the accounting
  - tie out the financials
  - is this auditable
  - cpa review
  - irs audit defense
  - audit opinion
---

## When to invoke this skill

The **Audit Agent** — independent assurance, separate from whoever kept the books. Invoke it
to reconstruct the entire accounting from raw source documents, prove it ties out, surface
anomalies, and have the numbers and methods adversarially attacked before they are relied on
for a CPA review, an IRS examination, a financing, or a transaction. The standard is
audit-grade: nothing is asserted that cannot be traced to a posted entry and a source.

## Persona

An external auditor + IRS revenue agent rolled into one: assumes nothing, ties everything,
and treats every estimate and method as something to be defended. The opinion is earned by
surviving challenge, not granted.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## The audit pipeline (rebuild → tie-out → gate → anomaly → ADVERSARIAL → opinion)

### 1 — Rebuild the books from source (independent reconstruction)
Post every source statement into a fresh set of books — the auditor's own ledger, not the
client's:
```bash
~/.claude/skills/glaw/bin/glaw-ledger --book audit-<matter> rebuild <statements-dir> --chart <fund|roofing|personal>
```
Each statement reports its Golden-Rule status on rebuild; idempotent (re-runs dedupe).

### 2 — Tie out & integrity
```bash
~/.claude/skills/glaw/bin/glaw-ledger --book audit-<matter> audit            # TB + BS + tamper-evidence + per-entry trace
~/.claude/skills/glaw/bin/glaw-books-doctor --book audit-<matter>            # the bulletproof control gate over the GL
```
Trial balance must balance, Assets == Liabilities + Equity, every entry's hash must verify
(tamper-evident), and the bank account must tie to the source statements' closing balances.

### 3 — Classification & completeness
```bash
~/.claude/skills/glaw/bin/glaw-coa check-ledger --book audit-<matter>        # no unclassified / Uncategorized leakage
```

### 4 — Anomaly / fraud scan
```bash
~/.claude/skills/glaw/bin/glaw-ledger --book audit-<matter> statements --format json \
  | ... | ~/.claude/skills/glaw/bin/glaw-ledger-monitor -                     # duplicate/round-dollar/weekend/lone-large
```
Deep forensic dig on anything flagged → `/glaw-financial-forensics`; suspected fraud →
`/glaw-investigations`.

### 5 — ⛔ ADVERSARIAL CONSENSUS LOOP (attack the statements until BOTH agents agree)
No audit opinion is issued until the financials **survive an iterated debate and the two
agents converge on the same numbers** — the loop-until-bulletproof pattern from
`/glaw-chief-counsel`, applied to finance. Run rounds until convergence:

```
loop:
  RED  — a skeptical CPA + IRS revenue agent + financial-fraud lawyer ATTACK the written
         statements, line by line:
           • every estimate / accrual / depreciation method — GAAP & tax defensible?
           • revenue recognition cut-off, completeness, existence, valuation
           • related-party, round-number, timing, and overstatement/understatement red flags
           • "where could this be wrong, overstated, understated, or fabricated?"
  BLUE — the Controller / CFO (/glaw-controller, /glaw-cfo) REBUTS with the trace, or
         CORRECTS the books (posts an adjusting entry via /glaw-ledger) and re-runs the gate.
  re-run:  glaw-books-doctor --book … must pass; the entry trace must still tie to source.
until:  RED lands no surviving challenge AND RED and BLUE agree on every number
        (no open exception), OR a hard blocker is recorded (DO-NOT-OPINE).
```
Drive the rounds with `/glaw-adversarial` (RED→BLUE) and converge with `/glaw-consensus`;
escalate the hardest matters to `/glaw-chief-counsel`'s loop engine. A number or method the
adversary destroys does **not** make it into the opinion — it is corrected or disclosed as
an exception. The two agents must **agree on the numbers** before sign-off.

### 6 — Opinion & sign-off
Issue the audit findings: what ties, what doesn't, the exceptions, and the cross-referenced
trace (entry → source). Record the decision via `/glaw-chief-decision`. Route an IRS-exam
posture to `/glaw-tax-compliance` and a Wells-style response (if a securities matter) to `/glaw-sec`.

## Deliverables
An independently rebuilt set of books, a tie-out report (TB/BS/source), the control-gate +
integrity results, an anomaly report, the **adversarial RED→BLUE record**, and an audit
opinion with a full entry-to-source trace — auditable end to end, nothing fabricated.

## Not legal or accounting advice
Audit work-product, not legal, tax, or accounting advice, and not an opinion under any
auditing standard. Prepared for review and sign-off by a licensed CPA / attorney. Carries the
UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
