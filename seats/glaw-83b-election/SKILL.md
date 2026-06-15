---
name: glaw-83b-election
version: 1.0.0
description: "GLAW corporate sub-skill — §83(b) election & founder restricted-stock workflow for C-corp formations. Generates IRS Form 15620 from a transferor questionnaire (fill-library), produces a visual workflow + entrepreneur checklist, the restricted-stock purchase agreement, the board resolution, and the cap table; computes the 30-day deadline; and pushes everything to Google Drive as Helvetica/single-spaced Docs ready for comments + Suggesting-mode tracked changes, then runs a comment-review loop that advises accept-vs-rewrite. Use for: '83(b) election', 'Form 15620', 'restricted stock', 'founder vesting', 'section 83b', '30-day deadline', 'should I file 83(b)', 'fill out 83b', 'QSBS holding period', 'early exercise tax'."
allowed-tools:
  - Skill
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
  - AskUserQuestion
triggers:
  - 83(b) election
  - section 83b
  - form 15620
  - restricted stock
  - founder vesting
  - 30-day deadline
  - qsbs holding period
  - early exercise tax
---

# GLAW — §83(b) Election & Founder Restricted-Stock Workflow

A corporate sub-skill of GLAW (Corporate & Transactional Division). It papers and FILES the
single most deadline-sensitive event in startup formation: the IRS §83(b) election on founder
restricted stock. Feeds `/glaw-draft` in a corp-build matter. Carries the UPL footer; all
citations defer to `/glaw-legal-research`.

## The one rule that governs everything
**File within 30 days of the stock transfer. No extensions. No late relief. No cure.**
Day 0 (transfer day) doesn't count; 30 calendar days; weekend/holiday rolls to next business day (IRC §7503).

## What this skill produces
1. **IRS Form 15620** filled from the transferor questionnaire (see `assets/form15620-library.json`).
2. **Visual workflow + entrepreneur checklist** (Helvetica, single-spaced .docx with images).
3. **Restricted Stock Purchase Agreement** (4-yr vest / 1-yr cliff) + the §83(b) statement.
4. **Board Resolution** authorizing the issuance + 83(b) acknowledgment.
5. **Cap table** (Google Sheet).
6. **WIKI/dossier** reference + **S-corp/LLC compliance** comparison (why C-corp for QSBS).

## Workflow
1. **Intake the transferor** — run the questionnaire in `assets/form15620-library.json`
   (name/TIN/address → Box 1; shares+class+company → Box 2; transfer date → Box 3; tax year →
   Box 4; restrictions → Box 5; FMV/share → Box 6; price paid → Box 7; Box 8 = 6c−7c; company → Box 9).
2. **Compute the deadline** — `bin/deadline.py <YYYY-MM-DD>` prints the 30-day due date with rollover.
3. **Decide file/no-file** — file when FMV≈price-paid (founders) so Box 8≈$0; counsel-review for high-FMV/forfeiture-risk grants. RSUs do NOT qualify.
4. **Generate docs** and **upload to Drive** — `bin/upload_to_drive.py` converts the markdown drafts to
   Helvetica/single-spaced Google Docs (+ raw .md + .docx), and a cap-table Sheet, into one folder.
5. **Set the docs to comment/Suggesting mode** — see "Review loop" below.
6. **File** — electronic via IRS portal (ID.me; allow 1–2 days) OR paper Certified Mail to the filer's
   IRS service center. Post-2025-12-24 USPS rule: get a same-day retail-counter postmark; no collection boxes.
   Pick ONE method, never both. Deliver a copy to the company; keep proof indefinitely.
7. **Docket** — `glaw docket add <due-date> "83(b) deadline — <founder>"`.

## Review loop (comments + tracked changes -> AI advice)
Keep the draft, comment log, and resolution log in the local matter packet. For each open comment
or proposed edit, classify **ACCEPT** (typo/clarity/factually-correct) vs **CAREFUL-REWRITE**
(changes legal/tax substance, so escalate to the owning seat). Do not depend on Google Drive,
Docs API scopes, or token files for the core workflow.

## Tie-in to GLAW
- Division: Corporate & Transactional (see `glaw/lib/firm-roster.md`).
- Invoked by `/glaw-draft` during a **corp-build** matter, after `/glaw-structure` sets the cap table.
- Hard gates still apply: conflicts cleared, citations verified (`/glaw-legal-research`), adversarial
  RED→BLUE (`/glaw-adversarial`) before any external/filed deliverable.

## Tax context (verify with CPA — post-OBBBA 2025)
83(b) starts the **QSBS §1202** 5-year clock at grant (vs restarting each vest). Post-OBBBA stock
(after 7/4/2025): per-issuer cap ~$15M (or 10× basis), gross-asset ceiling ~$75M, tiered 50/75/100%
at 3/4/5 yrs. Missing 83(b) can forfeit QSBS even if the company qualifies.

> ATTORNEY/CPA WORK-PRODUCT — drafts for a licensed attorney + CPA to review, sign, and file. Not legal/tax advice.

## Agent identity & reporting posture

- Identity: `glaw-83b-election` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Soul: `glaw-83b-election` carries a distinct professional judgment posture for this seat; its reports must preserve its own lens, skepticism, evidence standards, red flags, and sign-off conditions instead of blending into a generic firm voice.
- Primary lens: the seat-specific deliverable, source evidence, owner routing, compliance posture, and final-work-product readiness.
- Counter-lens: write as if reviewed by Chief Counsel, outside critic, regulator, auditor, opposing counsel, and user-side decision maker; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a senior professional report: what is known, what is blocked, who owns each fix, and what gate must clear next; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat output conflicts with the sources or this seat standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
