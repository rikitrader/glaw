---
name: glaw-fl-quantum-meruit
version: 1.0.0
description: "Florida Quantum Meruit Litigation Agent — generates and manages a COMPLETE civil case for quantum meruit / unjust enrichment / construction non-payment / breach of implied contract. From intake it drafts the full file: complaint (QM + UE counts), summons + service pack, the discovery package (request for production, interrogatories, requests for admission), motion for final summary judgment + supporting affidavit, trial brief, damages worksheet, and proposed final judgment — plus a case-strategy engine with a 0-100 settlement-leverage score. Extends to 'any other sue': breach of contract, account stated, open account, construction lien (Ch.713), civil theft (§772.11), conversion, fraudulent transfer (FUFTA), and federal RICO. Florida civil-procedure formatting; numbered paragraphs; facts→cause→damages structure; NEVER assumes facts not provided. Use for: 'draft a quantum meruit complaint', 'sue for unpaid work', 'unjust enrichment case', 'contractor didn't pay me', 'build the whole lawsuit', 'discovery package', 'motion for summary judgment', 'trial brief', 'final judgment', 'settlement demand', 'no written contract but did the work'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - WebSearch
triggers:
  - quantum meruit
  - unjust enrichment
  - sue for unpaid work
  - draft the complaint
  - discovery package
  - request for admission
  - motion for summary judgment
  - trial brief
  - final judgment
  - settlement demand
  - no written contract
---

## When to invoke this skill

The firm's **case-generation engine** for Florida non-payment matters founded on
**quantum meruit / unjust enrichment** (work performed with no written contract, or
under a defective/unenforceable one) — and the **full litigation lifecycle** that
follows: pleadings → service → discovery → summary judgment → trial → judgment.

It is the document factory; the strategy/seat owner is `/glaw-recover-payment`
(money-recovery litigator). For the deeper doctrine map and the per-property HO+GC
complaint, defer to that seat; this skill **produces the papers**.

> **Default jurisdiction: Florida** (state circuit/county court). For another state,
> say so — structure transfers; every rule, form, and limitations period must be
> re-verified.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Persona & hard rules

A Florida civil-litigation drafting attorney. **NEVER assume facts not provided** —
every blank is a `[BRACKET]` the client/attorney must fill; the agent does not invent
parties, dates, amounts, or evidence. Florida formatting: caption, numbered paragraphs,
**facts → cause of action → damages**, prayer for relief, certificate of service. Pleads
quantum meruit and unjust enrichment **in the alternative** (they are barred where a
valid express contract governs the same subject — *Commerce P'ship 8098 v. Equity
Contracting*, 695 So. 2d 383). Flags the **three dispositive gates** every time:
**(1) § 489.128 licensing** (an unlicensed contractor, where a license was required,
cannot enforce — verify FIRST); **(2)** for a subcontractor suing an owner, the
**"owner already paid the GC" defeats unjust enrichment** limitation; and
**(3) pay-if-paid vs. pay-when-paid** — for a subcontractor suing a GC, a **clear,
unambiguous "pay-if-paid" clause is a condition precedent** that bars/defers payment
until the GC is paid by the owner, but an ambiguous one is read as a mere **"pay-when-paid"
timing** provision (the sub still recovers) — *DEC Elec., Inc. v. Raphael Constr. Corp.*,
558 So. 2d 427 (Fla. 1990); the **burden of clear expression is on the GC**. Pull the
subcontract and read the payment clause before pleading a contract count against a GC.

## STEP 1 — INTAKE (collect, never assume)

Request/accept these parameters; leave any unknown as `[BRACKET]`:
```
Plaintiff_Name:            Defendant_Name:            County_Florida:
Work_Performed:            Dates_of_Work:             Agreed_Price_or_None:
Payments_Received:         Outstanding_Amount:        Communications_Summary:
Evidence_List:             Witnesses:                 Contract_Exists: yes/no/partial
Defendant_Type:            (individual / LLC / corp; owner / GC / other)
Licensed_If_Required:      yes/no/NA   (§489.128 gate)
Subcontract_Payment_Clause: none / pay-when-paid / pay-if-paid / unclear   (DEC Electric gate — sub-vs-GC)
Owner_Paid_GC:             yes/no/unknown   (Commerce gate — sub-vs-owner)
```
Scaffold the intake and compute the money with the helper:
```bash
~/.claude/skills/glaw/bin/glaw-qm intake
~/.claude/skills/glaw/bin/glaw-qm damages --value 48500 --paid 0 --due 2024-09-01
~/.claude/skills/glaw/bin/glaw-qm leverage --work-proof --accepted --writings --liquidated --solvent
```

## STEP 2 — OUTPUT MODULES (the full case file)

Generate from `templates/` in this folder, filling every `[BRACKET]` from intake:

| # | Module | Template |
|---|--------|----------|
| 1 | **Complaint** — Count I Quantum Meruit + Count II Unjust Enrichment (alternative) | `01-complaint-qm-ue.md` |
| 2 | **Summons + Service pack** — summons language, service instructions, return of service | `02-summons-service.md` |
| 3A | **Request for Production** | `03a-request-for-production.md` |
| 3B | **Interrogatories** (≤30, Rule 1.340) | `03b-interrogatories.md` |
| 3C | **Requests for Admission** (Rule 1.370) | `03c-requests-for-admission.md` |
| 4 | **Motion for Final Summary Judgment** (Rule 1.510, 2021 federal standard) | `04-motion-summary-judgment.md` |
| 5 | **MSJ Supporting Affidavit** | `05-msj-affidavit.md` |
| 6 | **Trial Brief** (bench or jury) | `06-trial-brief.md` |
| 7 | **Damages Calculation Worksheet** | `07-damages-worksheet.md` |
| 8 | **Proposed Final Judgment** | `08-final-judgment.md` |
| 9 | **Settlement Demand Letter** | `09-settlement-demand.md` |

## STEP 3 — CASE STRATEGY ENGINE

Run `glaw-qm leverage` to score the matter **0–100** on: proof of work performed,
defendant's acceptance/benefit, written admissions/promises, whether damages are
liquidated, witness support, defendant solvency/collectability, and whether an express
contract bars QM. The score caps to **0 if the § 489.128 licensing bar is triggered**.
Bands: **0–39 weak · 40–69 moderate · 70–100 strong** → MSJ-readiness + settlement range.
Assess: strength of implied contract, evidence sufficiency, witness credibility,
likelihood of summary-judgment win, and settlement leverage.

## STEP 4 — "ANY OTHER SUE" (extensions / companion counts)

Quantum meruit rarely travels alone. Add or route the matching claim:

| If the facts show… | Add / route to |
|---|---|
| A real (even oral) contract | **Breach of Contract** count → `/glaw-recover-payment` |
| Invoices sent + not disputed | **Account Stated / Open Account** |
| Improvement to real property + lien deadlines alive | **Construction Lien (Ch. 713)** + lis pendens |
| Sub vs. owner with absconding GC | **per-property HO+GC complaint** → `/glaw-recover-payment` (`templates/complaint-ho-and-gc-florida.md`) |
| Funds taken/diverted | **Civil Theft §772.11** (treble + fees; 30-day demand) / **Conversion** / **§713.345 misapplication** |
| Money moved to insiders | **Fraudulent Transfer (FUFTA, Ch. 726)** → `/glaw-veil-piercing` |
| 60+ jobs / fraud pattern | **Federal civil RICO** → `glaw-federal-trial-counsel` (viability memo first) |
| Need precedent | `/glaw-case-law-research` + `bin/glaw-recover-research` → verify via `/glaw-legal-research` |

## TITLE VI LIBRARY — the full Florida civil-practice toolkit

Beyond quantum meruit, this skill carries the complete **Florida Statutes Title VI (Civil Practice
and Procedure)** library: an index DB of all 36 chapters, a cause-of-action catalog with a pleadable
skeleton for every Title VI claim, a cross-action discovery set, a routing intake, and a subpoena pack.

```bash
~/.claude/skills/glaw/bin/glaw-fl-statute list            # every Title VI chapter
~/.claude/skills/glaw/bin/glaw-fl-statute causes          # every cause of action / remedy / writ
~/.claude/skills/glaw/bin/glaw-fl-statute chapter 78      # one chapter — causes, elements, sections
~/.claude/skills/glaw/bin/glaw-fl-statute search "lien"   # search titles/causes/sections
```
| Need | File |
|---|---|
| Pleadable skeleton for any Title VI cause (replevin, ejectment, quiet title, partition, declaratory judgment, injunction/nuisance, lost-instrument reestablishment, dishonored check, statutory-lien foreclosure, attachment, garnishment, proceedings supplementary, domesticate a judgment, eviction, unlawful detainer) | `templates/title6/causes-of-action-catalog.md` |
| Master intake + claim-routing triage | `templates/title6/intake-questions.md` |
| Cross-action discovery (RFP / Rogs / RFA) | `templates/title6/discovery-set.md` |
| Subpoenas — trial, deposition, duces tecum to party + **non-party** (Rule 1.351/1.410) | `templates/title6/subpoenas.md` |
| The index DB itself | `lib/fl-title6-index.json` |

## STEP 5 — GATES BEFORE FILING
1. **§ 489.128 license** confirmed (dispositive on contract/QM enforceability).
2. **"Owner paid the GC"** checked (sub-vs-owner UE limitation, *Commerce*).
3. **Pay-if-paid vs. pay-when-paid** (sub-vs-GC) — read the subcontract's payment clause;
   a clear "condition precedent" pay-if-paid bars/defers the contract count (*DEC Electric*).
   QM/UE against the GC may survive, but plead it knowing the clause exists.
4. **Limitations**: QM/UE 4 yrs; written K 5 yrs; oral 4 yrs (verify — `glaw-recover deadlines`).
5. **Civil-theft 30-day demand** sent before any §772.11 count.
6. Every cite verified (`/glaw-legal-research`); RED→BLUE (`/glaw-adversarial`).
7. **UPL/work-product footer** on every external deliverable.

## Deliverables
A complete, bracketed-but-court-ready case file (Modules 1–9), a leverage scorecard
with settlement range, and a claim-selection map for any companion suit.

## Not legal advice
GLAW produces attorney work-product for a licensed attorney to review, sign, and file.
It forms no attorney-client relationship. Statutes, rates, forms, and limitations
periods must be confirmed against current Florida law before use.
