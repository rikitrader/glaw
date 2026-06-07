---
name: glaw-federal-trial-counsel
description: "GLAW Litigation seat — federal trial counsel. Federal civil/criminal trial strategy, pleadings, motions, and trial posture. This seat is an ENCRYPTION-GATED skill: its full engine + content are distributed separately and are NOT bundled in the public GLAW repo (they contain client/case material). Install the full skill locally to activate; GLAW routes to it when present."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
---

## When to invoke this seat

Federal trial counsel — federal civil and criminal litigation: complaints, motions,
TROs, trial blueprints, and posture. GLAW's Litigation Division routes federal trial
work here.

## Encryption-gated — installed separately

The full federal-trial-counsel engine and its content are **encryption-gated and
distributed separately** (they contain client- and case-specific material). They are
intentionally **not vendored** into the public GLAW repo. When the full skill is
installed locally (`~/.claude/skills/federal-trial-counsel/`), GLAW routes to it
automatically; this stub keeps the seat resolvable in the self-contained ecosystem
without publishing gated content.

## Not legal advice

Attorney work-product for review by a licensed attorney. Carries the UPL footer from
`/glaw-ethics-conflicts` on any external deliverable.
