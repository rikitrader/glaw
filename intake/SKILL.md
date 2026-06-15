---
name: glaw-intake
version: 1.0.0
description: "GLAW pipeline stage 1 — matter intake. Captures facts, parties, jurisdiction, and goal; classifies the matter (litigation vs corp-build); and hands off to the conflicts/engagement gate. Use at the start of any GLAW matter, or when asked to 'open a matter', 'take on a case', 'start intake'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - Skill
triggers:
  - matter intake
  - open a matter
  - start intake
  - take on a case
---

## When to invoke this skill

First stage of the GLAW pipeline. Run it to turn a loose request ("help me set up
my company", "I want to sue X") into a structured matter the rest of the firm can
work. It does NOT give legal advice — it gathers, classifies, and routes.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### Step 0 — Open or locate the matter
If no active matter, open one:
```bash
bin/glaw matter new "<matter name>"
```
This creates both `matter.md` and the required structured intake form `intake.json`.

### Step 1 — Classify the matter (AskUserQuestion)
Ask which track this is — **litigation case (civil)** vs **corp/fund build** vs
**investigation (white-collar/criminal)** vs **accounting/tax/bookkeeping** vs
**contract review** vs **both/hybrid**. This is the plan-mode
entry point; the AskUserQuestion satisfies plan mode. Write the answer into `type:`
in `~/.glaw/matters/<slug>/matter.md` (values: `litigation` | `corp-build` |
`investigation` | `accounting-tax` | `contract-review` | `hybrid`). For an investigation,
hand the lead to `/glaw-investigations`.

Also set the structured form track:
```bash
bin/glaw-intake set workflow_track <track>
```

### Step 2 — Capture the charter
Fill `matter.md` by interviewing the user. Capture, at minimum:
- **Parties** — client(s), adverse parties / counterparties, related entities, control persons.
- **Jurisdiction** — state(s) of formation + operation, federal nexus, forum.
- **Goal / relief** — what success looks like (entity stood up; offering closed; judgment; settlement).
- **Key facts + timeline** — dated events; for litigation, the operative dispute; for corp-build, the business + money flow.
- **Documents on hand** — contracts, bank records, prior filings, cap table, returns.
- **Hard dates** — anything time-sensitive (SOL, lien deadline, closing, board date). Calendar each now:
  ```bash
  bin/glaw docket add <YYYY-MM-DD> "<deadline>"
  ```

Fill the matching machine-readable fields at the same time:
```bash
bin/glaw-intake set client_names 'Client A; Client B'
bin/glaw-intake set parties 'Client A; Counterparty X; Related Entity Y'
bin/glaw-intake set jurisdiction 'Delaware; Florida; federal'
bin/glaw-intake set goal '<what success looks like>'
bin/glaw-intake set source_documents 'bank statement; contract; tax return'
bin/glaw-intake set deadlines '2026-07-01 closing; 2026-08-15 filing'
bin/glaw-intake set facts_timeline '2026-01-01 event...'
bin/glaw-intake set open_questions 'missing statement; confirm ownership'
bin/glaw-intake set conflicts_parties 'all clients, adverse parties, owners, affiliates'
bin/glaw-intake set authorized_scope 'review/analyze/draft only; no filing without human approval'
```

For accounting/tax/bookkeeping workflows, also fill:
```bash
bin/glaw-intake set track_specific.bank_statement_sources '<files, folders, or Google Sheets URLs>'
bin/glaw-intake set track_specific.tax_years '<years in scope>'
bin/glaw-intake set track_specific.entity_tax_type '<C-corp/S-corp/partnership/individual/etc.>'
bin/glaw-intake set track_specific.books_status '<unknown/reconstructed/closed/etc.>'
bin/glaw-intake set track_specific.irs_forms_needed '<1120/1065/1040/941/1099/etc.>'
```

### Step 3 — Completeness sweep (Build-the-whole-file)
Before handoff, do the thorough thing: name every party that could be added, every
entity in the structure, every jurisdiction that could attach, every document still
missing. List the gaps explicitly rather than quietly proceeding. Cheap now, costly later.

Run:
```bash
bin/glaw-intake status
```
If it reports missing fields, do not advance. Missing facts stay in the intake gap list.

### Step 4 — Conflicts + engagement gate (HARD GATE → hand off)
Invoke **`/glaw-ethics-conflicts`**. It runs the conflicts check against the parties
captured here, drafts the engagement letter, and stamps the UPL disclaimer. Intake
does NOT clear conflicts itself.

### Step 5 — Advance
On conflicts cleared:
```bash
bin/glaw-intake complete
bin/glaw stage strategy
bin/glaw timeline-log intake_done
```
`glaw stage strategy` is code-gated: it refuses to advance until both `intake_complete`
and `conflicts_cleared` are present in the matter timeline. Hand off to `/glaw-strategy`
(or `/glaw` to drive the rest).

## Output
A complete `matter.md` charter, a complete `intake.json`, every known deadline docketed,
a gap list, and a clean handoff to the conflicts gate. No legal positions taken yet —
that's strategy's job.


## Firm memory

Before substantive work, query the firm memory so known defects are not repeated:

```bash
python3 bin/glaw-learnings preflight [matter-slug]
```

During review, preserve new reusable defects as firm knowledge:

```bash
python3 bin/glaw-learnings add '{"error_class":"<slug>","scope":"firm","where":"<seat/file>","wrong":"<defect>","fix":"<correction>","authority":"<source if any>","confidence":8}'
python3 bin/glaw-reflect --apply
```

Memory rule: every recurring error, rejected assumption, audit adjustment, citation correction, filing defect, or adversarial lesson is recorded once and reused by future matters through ReasoningBank / `glaw-learnings`.

## Agent identity & reporting posture

- Identity: `glaw-intake` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Primary lens: claims, defenses, elements, jurisdiction, evidence admissibility, deadlines, and litigation leverage.
- Counter-lens: write as if reviewed by opposing counsel, trial judge, appellate panel, clerk, and sanctions reviewer; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a litigation partner report: procedural posture, dispositive risks, evidence table, authorities, and filing-ready action list; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat's output conflicts with the sources or this seat's standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
