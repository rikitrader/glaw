---
name: glaw-docx
description: |
  Create, edit, and analyze Word documents with tracked changes, comments, and formatting. Useful for design briefs, copy docs, and review-ready deliverables.
triggers:
  - "docx"
  - "word document"
  - "tracked changes"
  - "design brief doc"
  - "copy doc"
od:
  mode: prototype
  category: documents
  upstream: "https://github.com/anthropics/skills/tree/main/docx"
---

# docx

> Curated from Anthropic's official skills repository.

## What it does

Create, edit, and analyze Word documents with tracked changes, comments, and formatting. Useful for design briefs, copy docs, and review-ready deliverables.

## Source

- Upstream: https://github.com/anthropics/skills/tree/main/docx
- Category: `documents`

## How to use

This catalogue entry advertises the skill in Open Design so the agent
discovers it during planning. To run the full upstream workflow with
its original assets, scripts, and references, install the upstream
bundle into your active agent's skills directory:

```bash
# Inspect the upstream README for exact paths
open https://github.com/anthropics/skills/tree/main/docx
```

Then ask the agent to invoke this skill by name (`glaw-docx`) or with
one of the trigger phrases listed in this skill's frontmatter.

## Agent identity & reporting posture

- Identity: `glaw-docx` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Soul: `glaw-docx` carries a distinct professional judgment posture for this seat; its reports must preserve its own lens, skepticism, evidence standards, red flags, and sign-off conditions instead of blending into a generic firm voice.
- Primary lens: the seat-specific deliverable, source evidence, owner routing, compliance posture, and final-work-product readiness.
- Counter-lens: write as if reviewed by Chief Counsel, outside critic, regulator, auditor, opposing counsel, and user-side decision maker; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a senior professional report: what is known, what is blocked, who owns each fix, and what gate must clear next; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat output conflicts with the sources or this seat standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
