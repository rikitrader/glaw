# irs-whistleblower — IRS PDF auto-fill

This seat builds the claim; the shared filler stamps the computed/narrative values onto the real
IRS PDF.

**Form in scope:** Form 211 (Application for Award for Original Information).

## One-time prerequisite (manual)
The blank Form 211 PDF is **not** vendored. Download the current blank from irs.gov and drop it
here as `f211.pdf`.

## Workflow
1. Dump the exact AcroForm field names:
   ```bash
   bin/glaw-inspect-fields forms/f211.pdf forms/f211.fields.json
   ```
2. Build `forms/f211.data.json` — `{ "exact field name": "value" }` — from the claim narrative, the
   taxpayer/years identifiers, and the proceeds/award model (`glaw-wbo-award --format json`).
3. Fill:
   ```bash
   bin/glaw-fill-form forms/f211.pdf forms/f211.data.json out/f211-filled.pdf
   ```

File through counsel to preserve anonymity. Nothing on the form may be fabricated — every figure
and assertion traces to the lawfully obtained record. The filled PDF is a DRAFT for a licensed
attorney to review and sign.
