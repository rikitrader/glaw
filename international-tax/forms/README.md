# international-tax — IRS PDF auto-fill

This seat computes the figures; the shared filler stamps them onto the real IRS PDF.

**Forms in scope:** 8938 (FATCA), FinCEN 114 (FBAR — filed via BSA E-Filing, not a fillable
return), 5471 / 5472, 8865, 8858, 8992 (GILTI), 8993 (FDII/§250).

## One-time prerequisite (manual)
Blank IRS AcroForm PDFs are **not** vendored. Download the filing-year blank from irs.gov and drop
it here, e.g. `f8938.pdf`, `f5471.pdf`, `f8992.pdf`.

## Workflow
1. Dump the exact AcroForm field names:
   ```bash
   ~/.claude/skills/glaw/bin/glaw-inspect-fields forms/f8938.pdf forms/f8938.fields.json
   ```
2. Build `forms/f8938.data.json` — `{ "exact field name": "value" }` — from the computed values
   (`glaw-fbar-8938 --format json`, `glaw-gilti`, `glaw-intl-forms`, …).
3. Fill:
   ```bash
   ~/.claude/skills/glaw/bin/glaw-fill-form forms/f8938.pdf forms/f8938.data.json out/f8938-filled.pdf
   ```

FBAR is filed through the FinCEN BSA E-Filing system, not by stamping a return PDF — prepare the
values, then transcribe into BSA E-Filing. Filled PDFs are DRAFTS for a licensed CPA/attorney.
