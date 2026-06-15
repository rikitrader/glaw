# estate-gift-returns — IRS PDF auto-fill

This seat computes the figures; the shared filler stamps them onto the real IRS PDF.

**Forms in scope:** 706 (estate, incl. Schedules A–U), 709 (gift + GST), 4768 (706 extension),
8971 (basis-consistency, where applicable).

## One-time prerequisite (manual)
Blank IRS AcroForm PDFs are **not** vendored. Download the filing-year blank from irs.gov and drop
it here, e.g. `f706.pdf`, `f709.pdf`.

## Workflow
1. Dump the exact AcroForm field names:
   ```bash
   bin/glaw-inspect-fields forms/f706.pdf forms/f706.fields.json
   ```
2. Build `forms/f706.data.json` — `{ "exact field name": "value" }` — from the computed values
   (`glaw-form706 --format json` / `glaw-form709 --format json`) and the appraisal-backed schedule
   detail. The portability and GST-allocation election boxes use the on-states from step 1.
3. Fill:
   ```bash
   bin/glaw-fill-form forms/f706.pdf forms/f706.data.json out/f706-filled.pdf
   ```

Every schedule value must trace to an appraisal or source document. Filled PDFs are DRAFTS for a
licensed attorney/CPA to review and sign.
