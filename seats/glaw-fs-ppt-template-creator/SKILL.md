---
name: glaw-fs-ppt-template-creator
description: Create a reusable firm PowerPoint .pptx template using only stdlib OOXML, for decks, exhibits, financial teasers, board packs, and forensic presentations.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
---

# ppt-template-creator

Use this seat when a GLAW workflow needs a reusable `.pptx` template before
`/glaw-fs-pptx-author` builds the actual deck.

## Output contract

- Write to `./templates/firm-template.pptx` unless the user gives another path.
- Create `./templates/` if it does not exist.
- Use only source-controlled instructions and Python standard-library OOXML packaging.
- Return the relative template path and the slide-layout inventory.

## Required layouts

1. Title / matter overview.
2. Executive summary.
3. Financial table with source-note footer.
4. Timeline / litigation path.
5. Evidence / exhibit board.
6. Risk matrix with red/yellow/green status.
7. Appendix / source trace.

## Firm rules

- No third-party package imports.
- No remote template downloads.
- Every financial number shown in a deck built from the template must trace to a model,
  ledger, statement, or source file.
- Every legal claim or citation shown in a deck must pass the citation gate before final
  packet approval.
- External decks keep the attorney-review / not-legal-advice footer unless a licensed
  reviewer removes it.

## Implementation pattern

Run:

```bash
bin/glaw-pptx-template --out templates/firm-template.pptx
```

The tool builds the `.pptx` as an OOXML zip package with `zipfile`. It includes
`[Content_Types].xml`, root relationships, `ppt/presentation.xml`, presentation
relationships, one slide master, the required slide layouts, a theme, and layout
inventory slides. The generated template is then consumed by `/glaw-fs-pptx-author`.
