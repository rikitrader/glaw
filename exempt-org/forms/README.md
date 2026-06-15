# exempt-org — IRS PDF auto-fill

This seat computes the figures; the shared filler stamps them onto the real IRS PDF.

**Forms in scope:** 990, 990-EZ, 990-T (UBIT), 1023 / 1023-EZ / 1024.

## One-time prerequisite (manual)
Blank IRS AcroForm PDFs are **not** vendored (they change yearly and are large). Download the
filing-year blank from irs.gov and drop it here, e.g. `f990.pdf`, `f990t.pdf`, `f1023.pdf`.

## Workflow
1. Dump the exact AcroForm field names:
   ```bash
   bin/glaw-inspect-fields forms/f990.pdf forms/f990.fields.json
   ```
2. Build `forms/f990.data.json` — a `{ "exact field name": "value" }` map — from the computed
   values (`glaw-form990 --format json`). Checkboxes use the on-state from step 1 (e.g. `/Yes`).
3. Fill:
   ```bash
   bin/glaw-fill-form forms/f990.pdf forms/f990.data.json out/f990-filled.pdf
   ```

The filler reports any data keys that did not match a real field (typos) — fix and re-run.
The filled PDF is a DRAFT for a licensed CPA/attorney to review and sign.
