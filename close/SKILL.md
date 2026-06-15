---
name: glaw-close
version: 1.0.0
description: "GLAW month-end / period close workflow — the orchestrated finance close cycle. Runs ingest → reconcile → accruals/prepaids/depreciation → adjusting entries → BOOKS-DOCTOR control gate → financial statements → review/sign-off → lock period, with hard gates like the legal pipeline. Turns ad-hoc bookkeeping into controlled, auditable, bulletproof finance. Use for: 'close the books', 'month-end close', 'period close', 'run the close', 'lock the period', 'monthly financials'."
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
  - close the books
  - month-end close
  - period close
  - run the close
  - lock the period
  - monthly financials
---

## When to invoke this skill

The **period-close orchestrator** for the Accounting & Finance Division. Invoke it to
run a controlled month-end (or quarter/year) close: raw statements in, signed-off and
locked financial statements out, with a deterministic control gate that the books must
clear before the period can close. This is what makes finance *controlled*, not ad-hoc.

It does not freelance accounting positions — it sequences the firm's bookkeeping engine,
finance tools, and the existing `fs-*` close seats, and holds the gates.

## Persona

A controller running a disciplined close calendar. Nothing locks until it ties: trial
balance balances, every account reconciled, the Golden Rule holds, no unexplained
variance. Every adjusting entry is sourced; every number traces to a document.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- accounting bench ---"
sed -n '/Accounting & Finance Division/,/^$/p' lib/firm-roster.md 2>/dev/null | head -14
```

## The close pipeline (hard gates ⛔)

```
📥 Ingest ──▶ 🔁 Reconcile ──▶ 🧾 Adjust ──▶ ⛔ BOOKS-DOCTOR ──▶ 📊 Statements ──▶ ✅ Sign-off ──▶ 🔒 Lock
   bank-ingest   bank-rec        accruals/        (gate: bulletproof   statements      chief-decision   timeline-log
                                 prepaids/         or no close)
                                 depreciation
```

### 1 — Ingest
Pull every bank/card/processor statement for the period into the ledger:
```bash
bin/glaw-bank-ingest <statements-dir> --pattern '**/*' \
  --matter <slug> --chart <fund|roofing|personal> --open <prior-close> --close <bank-close> \
  --format json > /tmp/close-ledger.json
```
Route messy/edge formats through `/glaw-bookkeeping`.

### 2 — Reconcile  ⛔ (must reconcile or explain every item)
Line-match the books against the bank statement; surface outstanding and bank-only items:
```bash
bin/glaw-bank-rec --books <books.json> --bank <bank-statement> --format json
```
Book any bank-only items (fees, interest) as adjusting entries; carry outstanding items
to next period with a note.

### 3 — Adjust (accruals, prepaids, depreciation, reclasses)
Route the period-end adjusting entries to the owning seats:
- Accruals / prepaids → `/glaw-fs-accrual-schedule`
- Balance roll-forward / continuity → `/glaw-fs-roll-forward`
- Anything the matter needs reconstructed → `/glaw-financial-forensics` via `/glaw-accounting`
Each adjusting JE is appended to the ledger with a source note.

### 4 — Control gate  ⛔ BOOKS-DOCTOR (no close without it)
The period **cannot close** until the books are bulletproof:
```bash
bin/glaw-books-doctor /tmp/close-ledger.json --rec <bank_rec.json>
```
Exit 0 = TB balances, Assets==Liab+Equity, Golden Rule holds, classified, cash≥0, dedup
intact, no anomalies, reconciled. **Any failure blocks the close** — fix and re-run.

### 5 — Statements
Render the period financials:
```bash
bin/glaw-statements /tmp/close-ledger.json --format text
```
P&L, Balance Sheet, Cash Flow, Trial Balance — every line tied.

### 6 — Review & sign-off  ⛔
Record the controller/Chief decision (PROCEED / WITH-FIXES / WITH-CONDITIONS):
```bash
bin/glaw-chief-decision ...   # the sign-off card
```

### 7 — Lock the period
```bash
bin/glaw timeline-log period_close_locked_<YYYY-MM>
```
The closing balance becomes next period's opening. The period is now read-only.

## Automated / scheduled close (cron-safe)

For a recurring close that runs without a human in the loop, `bin/glaw-close-run` executes
the whole pipeline on a book and writes a dated close package — with one hard gate:
the books-doctor must pass. **Exit code reflects the gate** (0 = bulletproof, 1 = problems),
so a cron job alerts on failure and never locks a period that didn't tie.

```bash
# run the close, write the package, lock the month if the gate passes
bin/glaw-close-run --book <book> --period 2026-06 --out ~/closes --lock

# optionally pull new statements first
bin/glaw-close-run --book <book> --ingest <statements-dir> --chart <name> --period 2026-06 --out ~/closes --lock

# schedule it — 06:00 on the 1st of each month (user installs in their own crontab):
#   0 6 1 * *  bin/glaw-close-run --book acme --out ~/closes --lock || mail -s "GLAW close FAILED" me@co
```
The package (`<book>-<period>/`) contains `statements.txt`, `comparative.txt`,
`dashboard.txt`, `narrative.md`, `books-doctor.txt`, and `summary.json`. A failed gate
leaves the period **unlocked** for the controller to fix and re-run.

## Deliverables
A signed-off close package: reconciled ledger, the four statements, the books-doctor
control report (bulletproof), the adjusting-entry list with sources, and a locked period
stamp — auditable end to end. Nothing fabricated.

## Not legal or accounting advice
Bookkeeping/close work-product, not legal, tax, or accounting advice. Prepared for review
by a licensed CPA / attorney. Carries the UPL footer from `/glaw-ethics-conflicts` on any
external deliverable.
