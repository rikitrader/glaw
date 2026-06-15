---
name: glaw-fs-xlsx-author
description: Produce a .xlsx file on disk (headless) instead of driving a live Excel workbook — for managed-agent sessions with no open Office app.
---

# xlsx-author

Use this skill when running **headless** (managed-agent / CMA mode) and you need to deliver an Excel workbook as a **file artifact** rather than editing a live workbook via `mcp__office__excel_*`.

## Output contract

- Write to `./out/<name>.xlsx`. Create `./out/` if it does not exist.
- Return the relative path in your final message so the orchestration layer can collect it.

## How to build the workbook

Write a short Python script and run it with Bash. Use only the Python standard
library (`zipfile` plus XML strings), or use a live Office/Excel tool if one is
available:

```python
import zipfile

# Build a minimal OOXML .xlsx package with formula cells.
# Use shared strings or inline strings; formulas go inside <f>...</f>.
sheet_xml = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1"><c r="A1" t="inlineStr"><is><t>Revenue</t></is></c><c r="B1"><v>1250000000</v></c></row>
    <row r="2"><c r="A2" t="inlineStr"><is><t>Growth</t></is></c><c r="B2"><v>0.08</v></c></row>
    <row r="3"><c r="A3" t="inlineStr"><is><t>Next Revenue</t></is></c><c r="B3"><f>B1*(1+B2)</f></c></row>
  </sheetData>
</worksheet>"""
```

## Conventions (mirror `audit-xls`)

- **Blue / black / green.** Blue = hardcoded input, black = formula, green = link to another sheet/file.
- **No hardcodes in calc cells.** Every calculation cell is a formula; every input lives on an Inputs tab.
- **Named ranges** for any value referenced from a deck or memo.
- **Balance checks.** Include a Checks tab that ties (BS balances, CF ties to cash, etc.) and surfaces TRUE/FALSE.
- **One model per file.** Do not append to an existing workbook unless explicitly asked.

## When NOT to use

If `mcp__office__excel_*` tools are available (Cowork plugin mode), use those instead — they drive the user's live workbook with review checkpoints. This skill is the file-producing fallback for headless runs.
