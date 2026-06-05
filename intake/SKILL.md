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
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### Step 0 — Open or locate the matter
If no active matter, open one:
```bash
~/.claude/skills/glaw/bin/glaw matter new "<matter name>"
```

### Step 1 — Classify the matter (AskUserQuestion)
Ask which track this is — **litigation case (civil)** vs **corp/fund build** vs
**investigation (white-collar/criminal)** vs **both/hybrid**. This is the plan-mode
entry point; the AskUserQuestion satisfies plan mode. Write the answer into `type:`
in `~/.glaw/matters/<slug>/matter.md` (values: `litigation` | `corp-build` |
`investigation` | `hybrid`). For an investigation, hand the lead to `/glaw-investigations`.

### Step 2 — Capture the charter
Fill `matter.md` by interviewing the user. Capture, at minimum:
- **Parties** — client(s), adverse parties / counterparties, related entities, control persons.
- **Jurisdiction** — state(s) of formation + operation, federal nexus, forum.
- **Goal / relief** — what success looks like (entity stood up; offering closed; judgment; settlement).
- **Key facts + timeline** — dated events; for litigation, the operative dispute; for corp-build, the business + money flow.
- **Documents on hand** — contracts, bank records, prior filings, cap table, returns.
- **Hard dates** — anything time-sensitive (SOL, lien deadline, closing, board date). Calendar each now:
  ```bash
  ~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "<deadline>"
  ```

### Step 3 — Completeness sweep (Build-the-whole-file)
Before handoff, do the thorough thing: name every party that could be added, every
entity in the structure, every jurisdiction that could attach, every document still
missing. List the gaps explicitly rather than quietly proceeding. Cheap now, costly later.

### Step 4 — Conflicts + engagement gate (HARD GATE → hand off)
Invoke **`/glaw-ethics-conflicts`**. It runs the conflicts check against the parties
captured here, drafts the engagement letter, and stamps the UPL disclaimer. Intake
does NOT clear conflicts itself.

### Step 5 — Advance
On conflicts cleared:
```bash
~/.claude/skills/glaw/bin/glaw stage strategy
~/.claude/skills/glaw/bin/glaw timeline-log intake_done
```
Hand off to `/glaw-strategy` (or `/glaw` to drive the rest).

## Output
A complete `matter.md` charter, every known deadline docketed, a gap list, and a
clean handoff to the conflicts gate. No legal positions taken yet — that's strategy's job.
