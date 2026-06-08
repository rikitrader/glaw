---
name: glaw-irs-audit
version: 1.0.0
description: "GLAW IRS audit-defense seat — drive an IRS examination (or a state DOR audit) from the first notice to resolution: triage the notice, fix the statute-of-limitations clock, reconstruct the account from transcripts, substantiate every challenged item from the general ledger, recompute the agent's Form 4549 adjustments, and assemble the response / Appeals protest / Tax Court petition with a penalty-abatement request — every figure tied to the books, run past an IRS-examiner adversarial pass, for a licensed attorney/CPA to sign. Use for: 'IRS audit', 'examination', 'IDR', 'Form 4549', '30-day letter', '90-day letter / notice of deficiency', 'CP2000', 'respond to the IRS', 'penalty abatement', 'audit defense', 'state DOR audit'."
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
  - irs audit
  - examination
  - notice of deficiency
  - form 4549
  - penalty abatement
  - audit defense
---

## When to invoke this skill

The **IRS audit-defense seat**. Invoke it the moment a client receives an exam notice, IDR,
CP2000, Form 4549, a 30-day letter, or a 90-day statutory notice of deficiency — or for a parallel
state Department-of-Revenue audit. It is the controversy counterpart to the tax-computation
engines: it defends the numbers those engines produced, with every assertion **tied to the posted
general ledger** so nothing is fabricated.

> Attorney/CPA work-product, not advice. Carries the UPL footer from `/glaw-ethics-conflicts`.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Triage the notice + fix the statute-of-limitations clock (FIRST)
Identify the notice type and the deadline it starts (IDR response, 30-day protest, 90-day Tax
Court petition). Compute the assessment + refund statutes so you know whether the year is even open:
```bash
~/.claude/skills/glaw/bin/glaw-sol --due-date <YYYY-04-15> --filed-date <YYYY-MM-DD> --as-of <today>
```
A closed assessment year (`EXPIRED`) is a complete defense — raise it first. Fraud or a non-filed
year is open indefinitely; flag the criminal-exposure question for `/glaw-investigations` (eggshell).

### 2 — Reconstruct the IRS's account picture from transcripts
Pull what the IRS actually has on record before responding — assessed tax, withholding, payments,
penalties, interest, and the third-party income reported to it:
```bash
~/.claude/skills/glaw/bin/glaw-transcript --account <account.json> --wage-income <wi.json>
```

### 3 — Substantiate every challenged item from the general ledger
For each account under exam, produce the supporting posted entries — each carrying its
tamper-evident hash, so the substantiation ties to the books and not to a story:
```bash
~/.claude/skills/glaw/bin/glaw-audit-package --book <book> --accounts Expenses:Meals,Expenses:Travel \
  --form4549 <4549.json>     # recompute the agent's proposed adjustments
```
Hand the forensic-reconstruction edge cases to `/glaw-financial-forensics`; route the underlying
numbers to `/glaw-accounting` and tie the provision out with `/glaw-tax-provision` + books-doctor `[8/8]`.

### 4 — Penalty abatement
Test First-Time Abatement, then reasonable cause, and quantify the abatable penalty (Form 843):
```bash
~/.claude/skills/glaw/bin/glaw-abatement --penalty <amt> [--factors death_or_serious_illness,reliance_on_tax_professional]
```

### 5 — Build the response package (lawyer)
Route the assembled facts to `/glaw-draft` to produce the deliverable for the stage reached:
IDR response · audit-protest letter (30-day → IRS Appeals, with hazards-of-litigation) · **Tax
Court petition** on a 90-day notice (with `/glaw-federal-trial-counsel`) · Form 2848 POA.

### 6 — ⛔ Adversarial gate (IRS-examiner RED→BLUE) before anything is sent
No response leaves the firm until `/glaw-adversarial` runs the **IRS Revenue Agent / Appeals /
Chief Counsel** red-team against it — attacking the substantiation, the methods, the SOL position,
and the penalty defense. A position the firm's own examiner-adversary destroys is reworked, not
filed. Record the sign-off with `/glaw-chief-decision`.

### 7 — Docket every deadline
```bash
~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "IDR response due"
~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "30-day protest deadline"
~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "90-day Tax Court petition (jurisdictional)"
```

## Route to the bench
- Statute / clock → `glaw-sol`; transcripts → `glaw-transcript`; substantiation → `glaw-audit-package`;
  abatement → `glaw-abatement`.
- Numbers + tie-out → `/glaw-accounting`, `/glaw-tax-provision`, `/glaw-financial-forensics`.
- Tax Court / litigation posture → `/glaw-federal-trial-counsel`.
- Criminal / eggshell exposure → `/glaw-investigations`.
- Collections that follow an assessment → `/glaw-tax-relief`.

## Deliverables
A complete, signature-ready audit-response file: the SOL position, the transcript reconstruction,
a GL-tied substantiation index, the Form 4549 recompute, the penalty-abatement request, the
response/protest/petition, a docket of jurisdictional deadlines — every figure traced to the
posted ledger, survived the IRS-examiner adversarial pass.

## Not legal or tax advice
IRS-controversy work-product, not legal or tax advice, and not a substitute for an enrolled
practitioner. Prepared for review and signature by a licensed attorney / CPA / EA. UPL footer from
`/glaw-ethics-conflicts` on every external deliverable.
