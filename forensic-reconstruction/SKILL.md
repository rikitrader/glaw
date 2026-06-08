---
name: glaw-forensic-reconstruction
version: 1.0.0
description: "GLAW end-to-end forensic financial reconstruction — RE-RUNNABLE. Takes a set of bank statements (or a classified master-ledger CSV) and rebuilds a complete, gapless, fully-reconciled set of books and reports that can withstand a forensic auditor or federal investigator: month-by-month statement reconstruction, a full double-entry general ledger with a chart of accounts, the three-statement set with SEC-disclosure and IRS-audit-style footnotes, a credits advisory report, an IRS-audit-readiness report, a ready-to-file IRS forms package with checklists, an accounting error/resolution log, and CFO + CEO executive reports. Every figure ties to a real source statement; nothing is invented. Use for: 'reconstruct the books', 'forensic accounting', 'rebuild bank statements', 'audit-ready financials', 'clean up the books', 'full financial audit'."
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
  - forensic reconstruction
  - rebuild the books
  - reconstruct bank statements
  - audit-ready financials
  - full financial audit
---

## When to invoke this skill

The **forensic-reconstruction orchestrator**. Invoke it to rebuild a company's books from raw
bank statements into a bulletproof, audit-ready financial record. It is RE-RUNNABLE end to end:
point it at the statements/ledger and run the whole pipeline as many times as needed — every run
rebuilds the tamper-evident general ledger from scratch and reproduces the same audited result.

**No hallucination.** Every transaction maps to a balanced journal entry tied to its source
statement file and a tamper-evident hash. An item that cannot be classified from the source is
posted to an explicit **REVIEW** account and listed in the error log — it is never guessed.

> Attorney/CPA work-product, for a licensed CPA/attorney to review and sign. UPL footer from
> `/glaw-ethics-conflicts`.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## The pipeline (each step is re-runnable; outputs to an `--out` dir)

### 1 — Statement reconstruction (gapless)
Parse every monthly statement to transactions and classify them into a chart of accounts. Confirm
month-by-month continuity (each month's closing balance = the next month's opening); a missing
month is flagged as a gap, not papered over.

### 2 — Bookkeeping load (double-entry GL)
```bash
~/.claude/skills/glaw/bin/glaw-forensic-pipeline <master_ledger.csv> --book <co> --out <dir>
```
Posts every transaction to the GLAW tamper-evident double-entry ledger (deposit → Dr bank / Cr
income; withdrawal → Dr expense / Cr bank), builds the chart of accounts, and produces the trial
balance — trial-balance-balanced and hash-chain-intact, or it fails loudly.

### 3 — Reconciliation gate
```bash
~/.claude/skills/glaw/bin/glaw-books-doctor --book <co>      # [1..8] incl. tamper-evidence + tax tie-out
```
Own-account transfers must net to ~0 (the transfers-clearing residual surfaces any missing
statement). Every account ties; the chain proves nothing was altered.

### 4 — Three-statement set + footnotes
```bash
~/.claude/skills/glaw/bin/glaw-statements --book <co> --format text     # P&L, balance sheet, cash flow
~/.claude/skills/glaw/bin/glaw-narrative  --book <co> notes             # SEC-disclosure + IRS-audit footnotes
```

### 5 — Credits advisory report
`/glaw-credit-strategy` + `bin/glaw-credits` (R&D §41, fuel/other) → the credits identified, with
the substantiation each requires.

### 6 — IRS audit-readiness report
Flag every tax issue: deductions taken (tied to the GL via `bin/glaw-audit-package`), the M-1
book-to-tax differences (`bin/glaw-book-to-tax`), the provision tie-out (`bin/glaw-tax-tieout`),
and the legitimate minimization positions, each with its authority and substantiation — run past
the IRS-examiner adversarial pass (`/glaw-irs-audit` → `/glaw-adversarial`).

### 7 — IRS forms package (ready-to-file, each with a checklist)
`bin/glaw-return-map --book <co> --form 1120-S` (entity return) + the information returns
(`bin/glaw-1099`, payroll `bin/glaw-payroll-tax`) → `bin/glaw-irs-file` payloads, each with its
filing checklist (`bin/glaw-compliance-audit`).

### 8 — Error & resolution log + executive reports
The pipeline's `error_log.json` lists every exception (unmapped category, gap, review item); each
gets a documented corporate-level resolution so nothing stays open. Then `/glaw-cfo` (position,
ratios, risks) and a CEO summary (`/glaw-narrative`) close it out.

## ⛔ Gates (every deliverable)
Conflicts cleared · citations verified · **forensic-auditor / IRS-examiner adversarial RED→BLUE**
(`/glaw-adversarial`) · UPL footer. Nothing is "audit-ready" until the firm's own
forensic-auditor adversary has tried to break it and failed.

## Route to the bench
Numbers + statements → `/glaw-accounting`, `/glaw-cfo`; tax issues → `/glaw-irs-audit`,
`/glaw-tax-provision`; collections fallout → `/glaw-back-taxes`; fraud/criminal exposure →
`/glaw-investigations`; litigation use (e.g., a related case) → `/glaw-federal-trial-counsel`.

## Deliverables
A bulletproof, gapless, fully-reconciled reconstruction: reconstructed statements, the double-entry
GL + chart of accounts + trial balance, the three-statement set with SEC/IRS footnotes, the credits
report, the IRS audit-readiness report, the ready-to-file forms package with checklists, the
error/resolution log, and the CFO + CEO reports — every figure traced to a real source statement,
survived the forensic-auditor adversarial pass.

## Not legal, tax, or accounting advice
Forensic work-product for review and signature by a licensed CPA / attorney. UPL footer from
`/glaw-ethics-conflicts` on every external deliverable.
