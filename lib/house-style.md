# GLAW House Style & Publishing Rule (STANDING — applies to every document)

**RULE:** Every GLAW deliverable — every dossier, every drafted `.md`, every motion,
memo, matrix, briefing, and packet — is published in the firm house style as **three
formats in one Google Drive folder, with an index**:
- **PDF** (styled), **Google Doc**, **Google Slides**.

Run it with one command at the end of any matter or deliverable:
```bash
~/.claude/skills/glaw/bin/glaw-publish <matter-slug-or-dir> [--folder "<Drive folder name>"]
```
It renders every `.md` deliverable (skipping ingested evidence, extractions, and state
files), uploads PDF + Doc + Slides to a new Drive folder, and writes `index.md` (local
+ as a Google Doc). Add `--local-only` to render without uploading.

The styling lives in **`lib/house-style.css`** (applied to the PDF via pandoc + weasyprint;
the Google Doc/Slides inherit the same structure). The spec it encodes:

## Typeface
- Body + headings: **Helvetica** (fallback: Helvetica Neue, Arial, sans-serif).
- Black text `#000000` on pure white `#FFFFFF`.

## Body text
- Helvetica Regular, ~12pt, **JUSTIFIED** (flush left and right), line-height ~1.5.
- Inline labels in **bold**: `Matter:`, `Cause No.:`, `Court:`, `Draft prepared:`.
- Case names / party captions in *italic*.
- Single spacing within paragraphs; ~1 blank line (16–20px) between blocks.

## Titles / headings
- Main title: Helvetica **Bold ~20pt, CENTERED, ALL CAPS**, line-height 1.3.
- Subtitle: Bold ~17pt, CENTERED, ALL CAPS (em-dash variant tag, e.g. `— V3 BULLETPROOF DRAFT`).
- Section headers: Bold ~14pt, **LEFT-ALIGNED**.
- Extra space above each section header.

## Spacing & rules
- Wide margins (~1 inch / 2.5cm all sides).
- Thin gray horizontal divider rules (`---`) between major sections.

## Callout / directive block
- Blockquotes (`> ...`) render as an indented light-blue block: background `#D6E4FF`,
  text `#1A3FA0`, **bold + italic**. Use for the `DRAFTING DIRECTIVE` governing
  instruction and the UPL banner.
- **[Bold-bracketed placeholders]** stay bold to flag fields the pleader must fill —
  `glaw-publish` auto-bolds `[like this]` (links `[text](url)` are left alone).

## Preserve
- All bold/italic emphasis exactly as written.
- Bracketed placeholders `[like this]`.
- File-path references (e.g. `07-Strategy/2026-05-20-...md`) in regular weight.

> To change the firm's look, edit `lib/house-style.css` once — every future deliverable
> inherits it. This is attorney work-product formatting, not legal advice.
