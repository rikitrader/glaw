---
name: glaw-tax-legal-intake
description: >
  Front-door router for the tax/legal/corporate suite — decomposes a messy, multi-issue situation
  and SEQUENCES the right specialist skills in the correct order. Use when a request spans more
  than one of: forming/governing a company, back/unfiled taxes, owing the IRS and can't pay,
  proactive tax planning / asset protection, or a dispute/lawsuit — or when the user says "where do
  I start", "help me with my whole situation", "I have a tax and business mess", "owe taxes and want
  to start a company", "sort out my taxes and my LLC", "I don't know which of these I need". Routes
  to tax-compliance, tax-relief, tax-strategy, corporate-counsel, elite-corporate-counsel. For a
  single clearly-scoped task, invoke that specialist directly instead.
---

# Tax / Legal / Corporate Intake Router

Real situations rarely fit one skill. Your job: **take a tangled situation, break it into the
underlying issues, order them correctly, and hand each to the right specialist** — so nothing is
done out of sequence (e.g., never plan an exit before the entity exists, never negotiate IRS debt
before returns are filed).

**Read `tax-legal-shared/guardrails.md`** — the shared ethical floor governs every hand-off.

## The five specialists
| Skill | Owns |
|---|---|
| **`glaw-corporate-counsel`** | Form entities; draft bylaws/operating/shareholder/voting agreements; founder control/dual-class; securities-for-equity; ongoing compliance (annual report, franchise tax, CTA/BOI). |
| **`glaw-tax-compliance`** | Unfiled/back/late returns; penalties; IRS notices; the **criminal-exposure gate**. |
| **`glaw-tax-relief`** | Owe and **can't pay**: IA / OIC / CNC / Fresh Start; stop levies/liens. |
| **`glaw-tax-strategy`** | Proactive **minimization**, QSBS, trusts, **asset protection**, residency. |
| **`glaw-elite-corporate-counsel`** | Disputes, litigation, FUFTA/veil-piercing, fraud-on-court, forensics. |
| **`glaw-contract-review`** | Review/redline an inbound third-party contract (NDA/SaaS/MSA/employment/M&A) — CUAD risk grading + market benchmarks. |

## Financial-modeling execution layer (`fs-*` — Anthropic "Claude for Financial Services")
When a matter needs the **numbers/models/decks built** (not just advised), route to the installed
`fs-*` skills (52 of them, from anthropics/financial-services):
- **Valuation/modeling:** `glaw-fs-dcf-model` (+ validator), `glaw-fs-lbo-model`, `glaw-fs-3-statement-model`,
  `glaw-fs-comps-analysis`, `glaw-fs-merger-model`.
- **Accounting close / reconciliation:** `glaw-fs-gl-recon`, `glaw-fs-break-trace`, `glaw-fs-nav-tieout`,
  `glaw-fs-accrual-schedule`, `glaw-fs-roll-forward`, `glaw-fs-variance-commentary` (pair with `glaw-financial-forensics`).
- **Equity research / IB / PE / WM:** `glaw-fs-earnings-analysis`, `glaw-fs-morning-note`, `glaw-fs-cim-builder`,
  `glaw-fs-teaser`, `glaw-fs-deal-screening`, `glaw-fs-dd-checklist`, `glaw-fs-financial-plan`, `glaw-fs-tax-loss-harvesting`, etc.
- **Output:** `glaw-fs-xlsx-author`, `glaw-fs-audit-xls`, `glaw-fs-pptx-author`, `glaw-fs-clean-data-xls`.
- **KYC:** `glaw-fs-kyc-doc-parse`, `glaw-fs-kyc-rules`.
Hand-off pattern: `glaw-tax-strategy`/`glaw-corporate-counsel`/`glaw-institutional-finance` design the structure →
an `fs-*` skill **builds the model/deck** → `glaw-financial-forensics` reconciles. (Note: LSEG/S&P Global
partner skills were NOT installed — they need paid data connectors.)

## Step 1: Decompose
List the distinct issues in the request and tag each to a specialist. Identify **dependencies**
(what must happen before what) and **hard gates / deadlines**.

## Step 2: Apply the ordering rules (dependencies & gates)
1. **Stop active bleeding first.** A levy/garnishment or a CDP/lien deadline (LT11/CP90/Letter 1058,
   30 days) or a litigation deadline outranks everything → `glaw-tax-relief` (levy) / `glaw-elite-corporate-counsel` (suit).
2. **Criminal-exposure gate.** Willful non-filing, hidden/offshore income, fraud → **tax attorney
   first** (privilege) before any filing or disclosure (`glaw-tax-compliance` 1d).
3. **File before you resolve.** No IA/OIC/CNC until all required returns are filed →
   `glaw-tax-compliance` **before** `glaw-tax-relief`.
4. **Entity before entity-level planning.** Form/fix the entity (`glaw-corporate-counsel`) **before**
   structuring its tax (`glaw-tax-strategy`) or issuing equity.
5. **Resolve the past before optimizing the future.** Clean up back taxes/debt
   (`glaw-tax-compliance`/`glaw-tax-relief`) **before** proactive planning (`glaw-tax-strategy`).
6. **Asset protection only before a claim.** `glaw-tax-strategy`/`glaw-corporate-counsel` for protection is
   valid only with no pending/known claim; if a creditor/suit exists → `glaw-elite-corporate-counsel`
   (fraudulent-transfer line).

## Step 3: Sequence & hand off
Produce an ordered plan: **[step → specialist skill → why → gate/deadline]**. Then **invoke the
first specialist** (or, if the user wants the whole map first, present the sequence and ask which
to start). Carry facts forward between skills; re-confirm before any irreversible step.

## Step 3.5: Chief loop — debate, score, decide, COMPLETE (non-blocking)
Run the **Chief Protocol** (`tax-legal-shared/chief-protocol.md`): advocate vs opposing agent
debate (`adversarial.md` panels — IRS/SEC/opposing counsel/trustee/analyst) → Debate Report →
`calculators/score.py` scorecard → the **Intake Chief** (or the assigned workflow Chief) issues a
decision card (PROCEED / WITH FIXES / WITH CONDITIONS) and **drives the plan to completion**. The
adversarial pass **informs, never halts** — weak score ⇒ conditions + attorney-sign-off flag +
honest downside, deliverable still produced. Report the grade + Chief decision.

## Step 4: Respond
1. **Issues found** (decomposition) and which specialist owns each.
2. **The ordered plan** (numbered, with the gate/deadline on each step).
3. **Start here** — the single first action and the skill handling it.
4. **Shared disclaimer** (`tax-legal-shared/guardrails.md`): informational, not a substitute for
   licensed counsel; figures per `tax-legal-shared/current-figures.md`.

### Example
> *"I haven't filed in 3 years, I owe about $60k I can't pay, and I want to put my rental
> properties in an LLC so I can't be sued."*
1. **Screen criminal exposure** (`glaw-tax-compliance` 1d) — if clean, proceed; if willful/hidden income → tax attorney first.
2. **File the back returns** (`glaw-tax-compliance`) — required before any debt deal; may shrink the $60k (SFR replacement).
3. **Resolve the $60k** (`glaw-tax-relief`) — pre-qualify RCP → streamlined IA vs OIC vs CNC; stop any levy first.
4. **Form the rental LLC(s)** (`glaw-corporate-counsel`) — liability isolation, one entity per property.
5. **Asset protection layer** (`glaw-tax-strategy`) — *only* since no lawsuit is pending; if a creditor already exists, that's `glaw-elite-corporate-counsel` (fraudulent-transfer analysis), not protection.
> **Start:** the criminal-exposure screen + pulling transcripts in `glaw-tax-compliance`.

## Reference
- `tax-legal-shared/guardrails.md` — shared ethics floor. `tax-legal-shared/current-figures.md` — figures. `tax-legal-shared/evals.md` — behavior checks.
