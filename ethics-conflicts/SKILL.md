---
name: glaw-ethics-conflicts
version: 1.0.0
description: "GLAW Firm General Counsel — the conflicts, engagement, and ethics gate. Runs a conflicts-of-interest check against all parties, drafts the engagement letter and scope, and stamps the UPL (unauthorized-practice-of-law) disclaimer that gates every external deliverable. Use before any matter advances past intake, or when asked about 'conflict of interest', 'engagement letter', 'scope of representation', 'is this legal advice', 'UPL', 'ethics wall'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - AskUserQuestion
triggers:
  - conflicts check
  - conflict of interest
  - engagement letter
  - scope of representation
  - ethics gate
  - upl
---

## When to invoke this skill

The firm's General Counsel. Nothing opens without it. Invoke it (1) as the hard gate
right after `/glaw-intake`, and (2) any time a conflict, engagement-scope, or
ethics/UPL question arises mid-matter (e.g. a new adverse party appears).

This skill is also where GLAW's single most important line lives: **GLAW produces
attorney work-product for a licensed attorney to review, sign, and file. It does not
form an attorney-client relationship and does not practice law.**

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- known matters (for cross-matter conflict scan) ---"
~/.claude/skills/glaw/bin/glaw matter list 2>/dev/null || true
```

## Workflow

### Step 1 — Build the party set
From `matter.md`, list every party and their affiliates: client(s), adverse
parties, counterparties, control persons, related entities, and known beneficial
owners. Ask the user to fill any gaps. A conflict you can't see is the one that disqualifies you.

### Step 2 — Run the conflicts check
1. **Cross-matter scan** — compare this party set against every other matter under
   `~/.glaw/matters/*/matter.md` (grep the Parties sections). Flag any party that
   appears on the opposite side of another open matter.
2. **Direct adversity** — is the firm being asked to act against a current client?
3. **Positional / issue conflict** — would a position here undercut another client?
4. **Personal-interest / business conflict** — does the user/firm have a stake adverse
   to the client?

Classify the result: **cleared**, **conflict (decline)**, or **waivable (informed consent)**.

### Step 3 — Record the outcome (AskUserQuestion if waivable)
- If **cleared**: set the charter's `Conflicts check → status: cleared`.
- If **waivable**: AskUserQuestion to confirm the user wants a written conflict
  waiver; if yes, draft the waiver and set `status: waived`.
- If **conflict**: stop. Set `status: conflict` and advise declining or building an
  ethics wall. Do not advance the matter.

```bash
# after deciding (example): record in the charter, then log
~/.claude/skills/glaw/bin/glaw timeline-log conflicts_cleared
```
Edit `~/.glaw/matters/<slug>/matter.md` so the `## Conflicts check` block reads the chosen status.

### Step 4 — Draft the engagement letter
Produce a written engagement letter capturing: parties, scope of representation
(what's in / out), fee arrangement (flat / hourly / contingency — ask), responsibilities,
termination, and the limitation that work-product requires licensed-attorney review.
Set `Engagement → engagement letter: drafted` in the charter.

### Step 5 — Stamp the UPL guardrail
Every external GLAW deliverable carries this footer (the file/draft stages pull it):

> **Attorney work-product — not legal advice.** Prepared by GLAW (an AI legal
> drafting system) for review, revision, and signature by a licensed attorney in the
> relevant jurisdiction. Use of this material does not create an attorney-client
> relationship. Verify all citations and deadlines independently before filing.

### Step 6 — Clear the gate
Only when `status: cleared` (or `waived`) AND the engagement letter is drafted, report
`CONFLICTS: cleared` and hand back to `/glaw` / `/glaw-strategy`.

## Output
A conflicts determination, a recorded status in the charter, an engagement letter
draft, and the UPL footer that gates every downstream deliverable.
