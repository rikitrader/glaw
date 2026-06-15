# tax-compliance

Senior tax-compliance specialist persona — a tax attorney + EA-level preparer + CPA in one —
that brings non-filers and late filers back into compliance the right way, then minimizes or
eliminates penalties through every legitimate relief channel.

## What it does

Walks a back-tax case through the correct order of operations:

1. **Diagnose** — intake (jurisdiction, years, owe/refund, collection status, why late, ability to pay).
2. **Scope years** — 6-year rule, RSED refund clock, SFR years.
3. **Reconstruct** — pull IRS Wage & Income / Account transcripts, fill the gaps.
4. **File** — oldest required year forward; replace SFRs.
5. **Resolve the balance** — Installment Agreement / OIC / Currently Not Collectible / Fresh Start.
6. **Penalty relief** — First-Time Abatement first, then reasonable cause, then statutory.
7. **Statutes & rights** — ASED/CSED, liens vs. levies, CDP deadlines, Taxpayer Advocate.
8. **Draft** — ready-to-send abatement letters, Form 843, IA/OIC narratives, CDP requests.
9. **Respond** — structured output: bottom line → year table → sequence → relief plan → citations → disclaimer.

## Files

- `SKILL.md` — the 9-step workflow.
- `references/persona-and-guardrails.md` — tone, ethics, criminal-exposure escalation. **Read first.**
- `references/filing-rules.md` — which years, RSED/ASED/CSED, SFR replacement.
- `references/record-reconstruction.md` — transcripts, Cohan rule, reconciliation.
- `references/penalty-relief.md` — FTA → reasonable cause → statutory decision tree + penalty math.
- `references/collection-resolution.md` — IA, OIC + RCP formula, CNC, Fresh Start, liens/levies.
- `references/statutes-and-rights.md` — clocks, CP-notice escalation, CDP, TAS, representation.
- `references/state-and-international.md` — state VDAs/amnesty, Streamlined (14653/14654), FBAR/FATCA.
- `references/letter-templates.md` — copy-ready documents.
- `references/worked-examples.md` — three end-to-end cases (non-filer, SFR+levy, non-willful expat).
- `references/intake-questions.md` — `AskUserQuestion` spec for structured intake (4 categorical Qs).
- `references/business-payroll-track.md` — entity + payroll non-filer track (§6699/§6698/§6672/§6721/§6722).
- `references/other-levers-and-flags.md` — §7345 passport, bankruptcy tax discharge, innocent/injured spouse.
- `references/forms-catalog.md` — verified IRS form-download URLs + auto-fill scope + mailing-address sourcing.
- `references/filing-packet.md` — download → inspect → fill → assemble pipeline + guardrails.
- `scripts/` — `download_forms.py`, `inspect_fields.py`, `fill_form.py`, `assemble_dossier.py` (reporting-disabled PDF helper + text checklist renderer).

## Filing-packet capability

Downloads current IRS forms + prior-year returns live, auto-fills the **simple** forms (843, 9465,
12153, 911, 2848, 8821, 4506-T, 8379) from the user's facts (field names inspected at runtime, not
hardcoded), and assembles a cover-sheet + TOC + checklist dossier PDF. **It never e-files or
transmits to the IRS** — the taxpayer signs and submits. Returns/OIC financials get identifying
fields only; substance is left to a preparer. Pipeline tested end-to-end (download→fill→assemble).
- `references/state-and-international.md` also carries a **state quick-reference table** (9 no-income-tax states + major income-tax states' agencies/VDAs).

## Verified citations

Core IRC sections checked against the U.S. Code / IRM (June 2026): §6501 (assessment 3/6/∞),
§6502 (collection 10 yrs), §6511 (refund 3-yr/2-yr + §6513 deemed-paid), §6651 incl. (h) 0.25%
IA reduction (timely-filed only), FTA at IRM 20.1.1.3.3.2.1, reasonable cause at IRM 20.1.1.3.2,
six-year rule at IRM 1.2.1.6.18 / Policy Statement 5-133, SDOP 5% penalty + Forms 14653/14654.
Business/levers additions verified: §6698/§6699 ($255/owner/month), §6672 TFRP (100% trust-fund),
§6721/§6722 info-return penalties, §7345 passport threshold (>$66k, 2026 indexed), bankruptcy
3-yr/2-yr/240-day discharge rules (11 USC §507(a)(8)/§523(a)(1)), innocent/injured spouse (§6015).

## Scope & limits

Informational and drafting only — not a substitute for a licensed CPA, enrolled agent, or tax
attorney admitted in the relevant jurisdiction. Helps people **come into compliance, never
evade**. Flags potential willful non-filing / fraud / criminal exposure and routes to a tax
attorney for voluntary-disclosure and privilege reasons before any return is filed. Penalty
rates and thresholds change yearly — verify current figures on IRS.gov.
