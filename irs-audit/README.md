# irs-audit

The GLAW **IRS audit-defense seat** — a tax-controversy attorney + EA/CPA examiner-adversary +
forensic accountant in one. It drives an IRS examination (or a parallel state DOR audit) from the
first notice to resolution, with **every figure tied to the posted general ledger** so nothing is
fabricated, and every position run past an IRS-examiner adversarial pass before it leaves the firm.

This seat is **self-contained**: its `references/` knowledge base is grounded in the IRS Tax Tip
corpus (topic spine + provenance) and in primary authority (IRC, IRM, Pubs, Forms), and it defers
all volatile figures to `tax-legal-shared/current-figures.md`.

## What it does

Walks an exam through the correct order of operations (the SKILL.md workflow):

1. **Triage the notice + fix the SOL clock** — identify the notice, compute ASED/CSED/RSED, decide
   if the year is even open. An expired ASED is a complete defense.
2. **Reconstruct the IRS's account** — pull Account + Wage & Income transcripts; reconcile.
3. **Substantiate from the ledger** — tie every challenged item to a posted GL entry; recompute the
   agent's Form 4549 adjustments.
4. **Penalty abatement** — First-Time Abatement, then reasonable cause, then statutory (Form 843).
5. **Build the response** — IDR response / 30-day protest to Appeals / 90-day Tax Court petition /
   Form 2848 POA, via `/glaw-draft`.
6. **Adversarial gate** — IRS Revenue Agent / Appeals / Chief Counsel RED→BLUE before anything ships.
7. **Docket every deadline** — especially the **jurisdictional** 90-day and CDP clocks.

## Files

- `SKILL.md` — the workflow, routing, deliverables, firm-memory, and agent-identity sections.
- `references/persona-and-guardrails.md` — tone, UPL/"not advice" rule, the eggshell-audit &
  criminal-exposure gate (IRS-CI / §7525 limits / voluntary disclosure / Kovel), and the
  zero-fabrication / tie-to-the-ledger rule. **Read first.**
- `references/taxpayer-bill-of-rights.md` — all 10 rights (IRC §7803(a)(3)), each mapped to a
  concrete audit/appeals lever. The spine of the seat.
- `references/notices-and-letters.md` — CP2000, 30-day letter (525/692/950), 90-day notice of
  deficiency (§6212/§6213), IDR (Form 4564), Form 4549/886-A, and the CP14→CP504→1058 collection
  track. What each is, the clock it starts, the right response, and whether the deadline is
  jurisdictional.
- `references/examination-workflow.md` — exam types, the SOL clocks, IDR discipline, the
  audit→30-day→Appeals→90-day→Tax Court ladder, audit reconsideration, and the RED→BLUE gate.
- `references/penalty-relief.md` — FTA → reasonable cause → statutory, penalty mechanics
  (§6651/§6662/§6663/§6699/§6698/§6672), order of operations, Form 843. Rates defer to current-figures.
- `references/scams-and-data-security.md` — letter ≠ phone call authentication, ERC promoter
  schemes (withdrawal/VDP), IP PIN, Form 14039, and the preparer WISP / data-theft response steps.
- `references/transcripts-and-reconstruction.md` — W&I vs. Account vs. Return vs. Record-of-Account
  transcripts, how to pull them, the W&I reconciliation gate, and the Cohan rule (with §274(d) limits).
- `references/sources-corpus-index.md` — provenance ledger: Tax Tip issue → topic → KB file, plus
  the primary-authority map (IRC/IRM/Pub/Form/case law) the KB rests on.

## Source grounding

The KB's topic spine comes from the **IRS Tax Tip** corpus (irs@service.govdelivery.com, 2018–2026):
the Taxpayer Bill of Rights series (2018-22/-26/-29/-37/-41/-50/-54, 2025-07, 2026-34/-41), the
notice/deadline series (2018-101, 2026-30/-31/-32/-33/-35/-36), penalty/OIC context (2026-40), the
scam & data-security series (2018-44/-32/-92, 2023-44, 2021-07, 2026-37/-44, preparer
2018-23/-137/-151/-160), and the transcript series (2018-43/-30/-121, 2023-25). Tax Tips are
plain-language summaries; the operative rules are grounded in primary authority — see
`references/sources-corpus-index.md`.

## Scope & limits

IRS-controversy **work-product, not legal or tax advice**, and not a substitute for an enrolled
practitioner. Prepared for review and signature by a licensed attorney / CPA / EA; the UPL footer
from `/glaw-ethics-conflicts` rides on every external deliverable. The seat **drafts and
prepares** — it does **not** e-file or transmit to the IRS. It flags eggshell/criminal exposure and
routes to a tax attorney (privilege + voluntary disclosure) before any substantive IRS response.
Penalty rates and thresholds change yearly — figures defer to `tax-legal-shared/current-figures.md`;
verify current on IRS.gov.
