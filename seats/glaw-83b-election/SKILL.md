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

## Review loop (comments + tracked changes → AI advice)
Google Docs version: turn on **Editing ▸ Suggesting** so collaborator edits appear as
strikethrough suggestions and are recorded in version history. To let GLAW read and advise:
- `bin/review_comments.py <folderId>` lists every open **comment** on every doc in the folder
  (via the Drive API), and for each one classifies **ACCEPT** (typo/clarity/factually-correct) vs
  **CAREFUL-REWRITE** (changes legal/tax substance — escalate to the owning seat) and can post a reply.
- Note: reading **suggestion** (tracked-change) text requires a `documents`-scoped token; the
  default `~/.gcp/token.json` is `drive`+`spreadsheets`. Comments work today; add the Docs scope to
  also ingest suggestion bodies. Until then, resolve suggestions by reading version history in the UI.

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
