---
name: glaw-docket
version: 1.0.0
description: "GLAW pipeline stage 7 — calendars and MONITORS every deadline via the glaw docket CLI. Corp-build recurring: Form D anniversary amendment, FinCEN BOI updates, annual report / franchise tax, blue-sky renewals, the 83(b) 30-day window. Litigation: statute of limitations, responsive-pleading deadlines, discovery cutoffs, motion deadlines, appeal windows. Surfaces what's due in 30/60/90 days and can hand ongoing monitoring to /schedule or /loop. Use for: 'calendar the deadlines', 'what's coming up', 'docket', 'set up deadline monitoring', 'when is X due'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Skill
triggers:
  - calendar deadlines
  - docket
  - whats coming up
  - deadline monitoring
  - when is it due
---

## When to invoke this skill

Stage 7 of the GLAW pipeline. It is the firm's calendar clerk: every deadline the
matter generates gets calendared and then **monitored**, so a blown statute of
limitations or a missed Form D anniversary never happens by neglect. This is
ETHOS principle 1 — completeness is cheap, a blown deadline is not.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- current docket ---"
~/.claude/skills/glaw/bin/glaw docket upcoming 90 2>/dev/null || true
```

## Workflow

### Step 1 — Pull every deadline from the file
Sweep `matter.md`, the filing checklist (`/glaw-file`), and the timeline for every
date that matters. Confirm each against current rule — do not state a deadline
from memory.

### Step 2 — Calendar by track

**Corp-build — recurring obligations (the ones firms forget):**
| Obligation | Cadence |
|------------|---------|
| Form D amendment | annually on the anniversary while offering open; on material change |
| FinCEN BOI update | within the CTA window after any beneficial-owner change — verify current timing |
| Annual report / franchise tax | per state, annually |
| Blue Sky renewals | per state, typically annual |
| 83(b) election | **one-shot, 30 days from grant** — calendar the day it's grantable |
| Form ADV annual updating amendment | within 90 days of fiscal year end (if RIA/ERA) |

**Litigation — case deadlines:**
- Statute of limitations (the master deadline — calendar with a buffer).
- Responsive-pleading deadlines (answer / motion to dismiss windows).
- Discovery cutoffs, expert disclosures, dispositive-motion deadlines.
- Trial date, pretrial filings, and **appeal windows** (jurisdictional — calendar the instant judgment enters).

Add each:
```bash
~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "<deadline> — <consequence if missed>"
```

### Step 3 — Show the horizon
```bash
~/.claude/skills/glaw/bin/glaw docket upcoming 30
~/.claude/skills/glaw/bin/glaw docket upcoming 60
~/.claude/skills/glaw/bin/glaw docket upcoming 90
```
Flag anything jurisdictional or one-shot (SOL, appeal window, 83(b)) at the top —
those have no second chance.

### Step 4 — Set up ongoing monitoring
A static calendar is not monitoring. Offer to stand up a recurring check that
re-runs `glaw docket upcoming` and surfaces what's due:
- **`/schedule`** — a cron routine (e.g. weekly) that reports the upcoming docket.
- **`/loop`** — a self-paced recurring check while a matter is hot.
Ask the user which they want before creating anything.

### Step 5 — Advance
```bash
~/.claude/skills/glaw/bin/glaw stage matter-retro
~/.claude/skills/glaw/bin/glaw timeline-log docket_done
```
Hand off to `/glaw-matter-retro` for close-out.

## Output
A fully calendared matter: every deadline docketed with its consequence, the
30/60/90-day horizon shown, jurisdictional/one-shot deadlines flagged, and an
ongoing-monitoring routine offered via `/schedule` or `/loop`.

> **Attorney work-product — not legal advice.** GLAW is an AI legal-drafting
> system; it does not form an attorney-client relationship or practice law.
