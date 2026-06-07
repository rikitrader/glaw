---
name: glaw-asset-protection
version: 1.0.0
description: "GLAW Private Client + Asset Protection strategist — designs and papers LEGITIMATE asset-protection structures around a new corp/founder (self-settled DAPT, third-party irrevocable trust, DING/NING incomplete-gift non-grantor trust, LLC/holdco layering) WITH income-tax planning, and runs a mandatory cross-department compliance gate (Tax/IRS + Corporate + FinCEN/Investigations) so the structure survives a creditor, IRS, or fraud-examiner attack and raises NO red flags. Produces the trust documents for the agent to fill. Use for: 'asset protection', 'protect my assets', 'DAPT', 'domestic asset protection trust', 'self-settled trust', 'DING trust', 'NING', 'incomplete gift non-grantor trust', 'third-party trust', 'judgment protection', 'creditor protection', 'spendthrift trust', 'trust protector', 'shield my equity', 'protect founder stock'."
allowed-tools:
  - Skill
  - Agent
  - Bash
  - Read
  - Write
  - Edit
  - WebFetch
  - WebSearch
  - AskUserQuestion
triggers:
  - asset protection
  - protect my assets
  - dapt
  - domestic asset protection trust
  - self-settled trust
  - ding trust
  - ning trust
  - incomplete gift non-grantor trust
  - third-party trust
  - spendthrift trust
  - creditor protection
  - trust protector
  - protect founder stock
---

# GLAW — Asset Protection & Trust Planning (with a hard compliance gate)

Designs LEGITIMATE asset-protection structures and papers the trust documents — then proves they hold up
against the people who will attack them (creditors, the IRS, a fraud examiner). **Asset protection is
planning done BEFORE a claim exists, with full solvency and disclosure. Moving assets to defeat a known or
foreseeable creditor is a fraudulent transfer (a crime-adjacent civil wrong) — this skill refuses that.**

> ⚠️ Output is attorney/CPA work-product for a licensed professional to review, sign, and file. Not legal/tax
> advice. The trust documents here are TEMPLATES to be tailored to the chosen situs state's statute.

## Knowledge base (ingested sources — read before drafting)
Stored under the matter `…/drafts/` (asset-protection set) and `/private/tmp/ap/`:
- Greenleaf Trust — *Asset Protection Trusts and Income Tax Planning* (greenleaf.pdf)
- ACTEC Foundation — *DAPTs and Trust Protectors* (actec_dapt.pdf)
- SAEPC / Edmondson — *Self-Settled Trusts / DAPTs* (saepc_dapt.pdf)
- Morris Nichols — *DING Trusts* (morrisnichols_ding.pdf)
- GM Law — *Using Third-Party Trusts for Asset Protection* (gmlaw_thirdparty.pdf)
- KKWC — *Beware of the Reciprocal Trust Doctrine* (kkwc_reciprocal.pdf) — **READ**; source for U.S. v. Grace + the economic-position test + Estate of Levy/Green line (doc 26 traps).
- IRS EO CPE — *Trusts: Common Law and IRC 501(c)(3) and 4947* (eotopica03.pdf) — **READ**; this is a **CHARITABLE / split-interest-trust + §4947 reference, NOT asset-protection** — use only for private-foundation/charitable planning, never as DAPT/DING authority.

> **Accuracy flags (do NOT hallucinate):**
> - **IRS PLR 202405002 is NOT asset-protection authority** — it is a §115(2) ruling on a *governmental/public
>   trust* for a US territory. Do not cite it for DAPT/DING. (The user supplied it; it's off-point.)
> - **`eotopica03.pdf` "Peek v. Commissioner, 73 T.C. 912 (1980)" is a CHARITABLE-deduction/§508 case — do NOT
>   conflate it with the well-known 2013 IRA §4975 *Peek* case.** Verify any §4975 IRA cite independently.
> - **York Howell DAPT white paper** (yorkhowell_dapt.pdf) — downloaded but text is image-light; no cites
>   extracted. **UTK law-review** — download still blocked (0 bytes); NOT ingested. Do not cite either until read.
> - The DING/NING income-tax result rests on a line of IRS private letter rulings — **verify the exact PLR
>   numbers and current IRS position with a CPA/tax attorney before citing**; PLRs bind only the taxpayer who got them.

## Structures this skill papers
| Structure | What it protects | Tax posture | Key caveat |
|-----------|------------------|-------------|------------|
| **Third-party irrevocable trust** (someone else settles it for you) | Strongest — beneficiary's creditors generally can't reach a properly drafted spendthrift third-party trust | Grantor or non-grantor | Cleanest; not self-settled, so no self-settled-trust weakness |
| **Self-settled DAPT** (you settle, you benefit) | Settlor's future creditors, in DAPT states (e.g., NV, SD, DE, AK, WY, TN…) | Usually grantor | Weak/untested against non-resident settlors & full-faith-credit; see Klabacka vs. the skeptical line |
| **DING/NING** (incomplete-gift non-grantor trust) | State income-tax savings + some protection | Non-grantor, incomplete gift | Income-tax tool first; verify PLR line + your state |
| **LLC/holdco layering** under the trust | Charging-order-only protection on the entity | Pass-through/J corp | Pairs with the trust; entity-architect designs it |

## Grounded case-law references (extracted from the ingested PDFs — VERIFY each before citing)
These case names appear in the sources above; the lawyer must pull and confirm each (use the court-research
APIs below). Citations are NOT reproduced from memory.
- *Klabacka v. Nelson* (Nevada — self-settled spendthrift DAPT upheld) — saepc_dapt.pdf
- *Rush University Medical Center v. Sessions* (Illinois — self-settled trust reached) — saepc_dapt.pdf
- *In re* / *University National Bank v. Rhoadarmer* — saepc_dapt.pdf
- *Irwin Union Bank & Trust Co. v. Long* — saepc_dapt.pdf
- *Kruse v. Repp*; *Elie v. Smith*; *Kurz v. Comm'r*; *Campbell v. Commissioner* (T.C. Memo); *People v. Waller* — saepc_dapt.pdf
- *Pitman v. Pitman* — actec_dapt.pdf
> Run each through a court-research API to get the exact reporter cite, court, year, and holding. Do not state a
> holding you have not read.

## Public court-research APIs (for verifying every case)
- **CourtListener / Free Law Project REST API** — `https://www.courtlistener.com/api/rest/v4/` (opinions, dockets, citation lookup; free, key-gated). Citation-lookup endpoint resolves "X v. Y, ___ F.3d ___".
- **Caselaw Access Project (CAP)** — `https://api.case.law/` (Harvard; bulk + case text).
- **CourtListener RECAP** — federal PACER docket mirror (free).
- **GovInfo API** — `https://api.govinfo.gov/` (USCOURTS, statutes, CFR).
- **IRS** — PLRs/written determinations at `irs.gov/pub/irs-wd/`; bulletins for Rev. Ruls./Rev. Procs.
- State court portals for situs-state DAPT statutes.
> When asked for case research, query CourtListener/CAP and return the verified cite + a one-line holding from
> the opinion text — never a remembered cite.

## MANDATORY cross-department compliance gate (so nothing raises a red flag)
Before any structure is finalized or funded, route through ALL of these and record a pass:
1. **Fraudulent-transfer / FUFTA red-team** → `glaw-elite-corporate-counsel` + `/glaw-adversarial`: test every "badge
   of fraud" (UFTA/UVTA §4: insolvency, transfer to insider, concealment, pending/threatened suit, transfer of
   substantially all assets, retained control/benefit, lack of equivalent value). **If a claim is known,
   threatened, or reasonably foreseeable → STOP; this is not asset protection.**
2. **Solvency** → require a contemporaneous **solvency affidavit** (settlor solvent before and after; transfer ≤
   what keeps them solvent). Route numbers to `/glaw-accounting` / `glaw-financial-forensics`.
3. **Tax/IRS** → `glaw-tax-strategy` + the Tax/IRS division: grantor vs non-grantor status, gift-tax/Form 709,
   income-tax (DING/NING) treatment, §2036/2038 estate inclusion, foreign-trust reporting (3520/3520-A) if any
   offshore element. No step that is tax evasion.
4. **FinCEN / AML / OFAC / FBI compliance** → `/glaw-fincen` (+ `/glaw-investigations`, `/glaw-bureau-counterfraud`):
   **FinCEN BOI** reporting for trust-owned entities; source-of-funds / AML clean; **OFAC/sanctions screening**
   (critical given any Venezuela nexus — see [[venezuela_data_sources]]); no structuring, no concealment.
5. **Ethics/UPL** → `/glaw-ethics-conflicts`: UPL disclaimer; no advice that facilitates evading a creditor.
A structure that fails ANY gate does not get drafted/funded. Log each pass in the docket.

## Workflow
1. GLAW preamble; confirm/open the matter (`/glaw`).
2. **Intake** (AskUserQuestion): goal; are there ANY known/threatened/foreseeable claims (gate 1 — if yes, stop);
   net worth + solvency; what assets (founder stock, cash, real estate); residency/situs; married/heirs; foreign nexus.
3. **Design** the structure (table above), with `/glaw-entity-architect` for the LLC/holdco layer and the
   `roofai_holdings` holdco if relevant.
4. **Run the compliance gate** (all 5). Record passes.
5. **Draft the trust documents** (templates in the matter's asset-protection drafts; fill via
   `~/.claude/skills/glaw-credit-strategy/bin/fill_form.py` for any fillable PDFs, or as text instruments).
6. **Tax wrap** (`glaw-tax-strategy`): grantor/non-grantor memo, Form 709 if a completed gift, situs-state analysis.
7. **Verify case law** via the court-research APIs; attach a verified authority table.
8. **Deliver** + offer Drive publish (`glaw-83b-election/bin/upload_to_drive.py`) + docket the deadlines.

## Documents this skill produces (templates for the agent to fill)
Trust agreement (third-party irrevocable / DAPT / DING variants) · Certification of Trust · Schedule A (assets) ·
Assignment/Transfer of membership interests & stock into trust · Spendthrift + Trust Protector provisions ·
Trust Protector appointment & acceptance · Solvency Affidavit · Gift memo/Form 709 cover · Trustee acceptance ·
Funding letter. (See the matter's asset-protection document set.)

## How this wires into the whole GLAW pipeline (every stage + agent + checklist)
The asset-protection engagement threads the standard GLAW pipeline; each stage fires specific seats, checklists,
adversarial agents, and the LLM review loop:

| Stage | What fires | Seats / agents | Checklist / artifact |
|-------|-----------|----------------|----------------------|
| **intake** | open/confirm matter; the **claim-foreseeability gate** (if any claim known/threatened/foreseeable → STOP) | `/glaw-intake`, `/glaw-ethics-conflicts` (UPL + conflicts) | intake Q's in Workflow §2 |
| **strategy** | pick structure (third-party / DAPT / DING / LLC layer) + income-tax thesis | this skill + `glaw-tax-strategy` + `glaw-pe-vc-counsel` (founder-stock) | structure table above |
| **structure** | entity + situs + holdco design | `/glaw-entity-architect`, `/glaw-structure` | org chart; situs-state pick |
| **draft** | fill the trust documents (doc 26) + exempt-asset plan (doc 27) | `/glaw-draft`, fill via `glaw-credit-strategy/bin/fill_form.py` | doc 26 instruments + Schedule A |
| **adversarial** (HARD GATE) | RED-team to DESTROY the structure, then BLUE rebuild | `/glaw-adversarial` + `glaw-elite-corporate-counsel` (FUFTA badges) + `glaw-forensic-case-investigator` (follow-the-money) + `/glaw-veil-piercing` | "survives-adversarial ≥5" or NO-FILE |
| **compliance** (HARD GATE) | 5-department clearance (below) | `glaw-tax-strategy` · `/glaw-accounting`/`glaw-financial-forensics` · `/glaw-fincen`(+`-ofac`,`-aml`) · `/glaw-investigations`/`/glaw-bureau-counterfraud` | the 5-gate log |
| **file** | signature-ready packet; trust funding; BOI | `/glaw-file` | funding letter, certification of trust |
| **docket** | calendar 709, BOI, situs-renewal, annual trustee review | `/glaw-docket` (`glaw docket add`) | deadline calendar |
| **retro** | Obsidian vault write-up | `/glaw-matter-retro` | matter vault |

**Adversarial + LLM verification loop (so it's bullet-proof):**
- Every drafted clause is published to Drive **comment-ready** (Helvetica, single-spaced). The LLM review loop
  `~/.claude/skills/glaw-83b-election/bin/review_comments.py <folderId>` reads comments **and** tracked-change
  suggestions (Docs scope is ON) and triages each **ACCEPT vs CAREFUL-REWRITE** (substance → escalate to the
  owning seat). Run it after every review round.
- Every case/PLR/statute cited is re-verified through the **court-research APIs** before it appears in a
  deliverable (CourtListener/CAP/GovInfo). No remembered cites.
- `/glaw-autocounsel` can run strategy+structure+adversarial back-to-back.

## Gates summary
Compliance gate (5 depts) before funding · citations verified via court APIs before citing · adversarial
RED→BLUE before file · UPL + "not legal/tax advice" on every deliverable · **refuse fraudulent transfers.**
