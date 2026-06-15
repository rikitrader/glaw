# Building the Filing Packet (download → fill → assemble)

This is the pipeline that turns the plan into a **ready-to-sign dossier**. It downloads current
forms, pre-populates the simple ones from the user's facts, and merges everything (with a cover
sheet, table of contents, and filing checklist) into one PDF.

> **The skill assembles; the human signs and submits.** It NEVER e-files or transmits anything to
> the IRS — that requires the taxpayer's signature and identity verification. Every output is a
> draft for review.

## Step 0 — detect tooling

| Need | Check | If missing |
|---|---|---|
| Download | `curl` or Python `urllib` (always present) | n/a |
| Fill / merge | `python3 -c "import reporting-disabled PDF helper"` | `zero-dependency mode: do not install packages
| Cover sheet | `python3 -c "import text checklist renderer"` | `zero-dependency mode: do not install packages

If PDF tooling can't be installed, fall back to: give the user the **download URLs**
(`forms-catalog.md`) + the filled **letters/narratives** as markdown + a **line-by-line fill
guide**, and skip auto-assembly.

## Step 1 — download (current versions, live)

```bash
# relief/collection forms (current) + a personal + business return range (prior-year)
python3 scripts/download_forms.py ./packet \
  f843 f9465 i9465 \
  1040:2021-2025 1040sc:2021-2025 \
  1120s:2021-2025 f1120ssk:2021-2025 1065:2021-2025 f1065sk1:2021-2025 1120:2021-2025
```
Validates each file is a real PDF. The `name:YYYY-YYYY` **range token** pulls one return per year.
Cover **both tracks** when the taxpayer has personal *and* entity exposure — file entity returns +
K-1s before the owners' 1040s (`business-payroll-track.md`). See `forms-catalog.md` for the token
map.

## Step 2 — inspect field names (never hardcode them)

Field names are revision-specific, so read them from the *downloaded* form:
```bash
python3 scripts/inspect_fields.py ./packet/f843.pdf > fields_843.json
```
Output lists each field's `name`, `type`, and (for checkboxes) the valid `states`.

## Step 3 — build the fill map and fill

From the inspected names, write a `{field_name: value}` JSON using the taxpayer's facts (text →
strings; checkboxes → one of the `states`, e.g. `"/1"`). Then:
```bash
python3 scripts/fill_form.py ./packet/f843.pdf map_843.json ./packet/843_filled.pdf
```
It reports how many mapped fields matched and warns on any name that isn't on the form. Output is
**not flattened and not signed** — values remain editable for the taxpayer's review.

**Auto-fill only the simple, stable forms** (843, 9465, 12153, 911, 2848, 8821, 4506-T, 8379).
For **returns (1040/1120/1065)** and **OIC financials (433-x, 656)**, pre-populate identifying
fields only; the calculations and substance must be prepared/verified by the taxpayer or a
preparer. Never enter a number you can't substantiate (no fabrication — see
`persona-and-guardrails.md`).

## Step 4 — render the letters/narratives as PDF

Turn the templates in `letter-templates.md` (reasonable-cause letter, Form 843 narrative,
IA/OIC narratives) into PDFs via the `make-pdf` / `docx` skills, into `./packet/`.

## Step 5 — assemble the dossier

Write a manifest (schema in `scripts/assemble_dossier.py`) listing every item in **IRS filing
order**, each with a `mail_to` source and any signing `notes`, plus a `checklist` and `mailing`
note. Then:
```bash
python3 scripts/assemble_dossier.py manifest.json ./packet/DOSSIER.pdf
```
Produces a single packet: **cover sheet → table of contents → filing checklist → each document**.

## Step 6 — hand off

Tell the user exactly: (1) what to **sign and date** (per `notes`), (2) what **supporting docs**
to attach, (3) the **address to verify** for each form (per `forms-catalog.md` — never a guessed
address), and (4) to send **certified mail, return receipt requested**, keeping a full copy.
Where e-filing is appropriate (current-year returns, FBARs via BSA E-Filing), say so — this skill
prepares the paper packet, it does not transmit.

## Guardrails recap

- Download **current** forms every run; never reuse stale PDFs.
- Auto-fill **simple** forms only; identifying fields on returns/financials; **never fabricate**.
- Output is a **draft for signature** — the skill does not file, e-file, or transmit to the IRS.
- Verify mailing addresses per form/state/year; recommend certified mail.
- If the Step 1d criminal-exposure gate fired, **do not build a filing packet** — the attorney
  decides the disclosure route first.
