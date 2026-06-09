<!-- FUFTA REVIEW + CIVIL/ADVERSARIAL WORKFLOW (Florida Title XLI / Ch. 726). The methodology a GLAW
     seat runs to (a) screen a transfer, (b) build the avoidance claim [CIVIL agent], and (c) red-team
     it [ADVERSARIAL agent]. Pair with: causes `glaw-fl-cause show "fraudulent transfer"`; defenses
     `glaw-fl-defense for "fraudulent transfer"`; verbatim text `lib/statute-text/title-xli-fufta-
     excerpts.md`; complaint `complaint-fufta.md`; assignment/true-sale → receivables-assignment-counsel
     / /fl-claims-assignment. NOT legal advice. -->

# FUFTA Review & Workflow — Ch. 726 (+ Ch. 725 statute of frauds, Ch. 727 ABC)

## A. THE THRESHOLD REVIEW (run on any challenged transfer)
1. **Is the plaintiff a "creditor" with a "claim"?** (§ 726.102) — a right to payment, matured or not,
   arising **before or after** the transfer (actual-intent reaches future creditors; § 726.106 protects
   only present creditors).
2. **Is there a "transfer" of an "asset"?** (§ 726.102) — exempt/encumbered property to the extent of a
   valid lien or homestead is generally NOT an "asset."
3. **Which theory fits?** Actual intent (§ 726.105(1)(a)) and/or constructive (§ 726.105(1)(b) /
   § 726.106). Constructive needs **no intent** — just no reasonably equivalent value + insolvency/
   undercapitalization.
4. **SOL (§ 726.110) — calendar it first:** actual-intent = **4 yr** OR **1 yr from discovery**;
   constructive = **4 yr** (§ 726.106(2) insider = **1 yr**). Extinguishment, not mere limitation.

## B. THE BADGES OF FRAUD SCORECARD (§ 726.105(2)) — actual intent
Score each badge the facts support; more badges = stronger actual-intent inference (no single badge is
dispositive; insolvency + insider + no-value + retained-control is the classic strong cluster):
| # | Badge | Present? | Fact |
|---|-------|----------|------|
| a | transfer to an **insider** | ☐ | |
| b | debtor **retained possession/control** | ☐ | |
| c | transfer **concealed / not recorded** | ☐ | |
| d | **suit pending/threatened** before transfer | ☐ | |
| e | **substantially all** assets transferred | ☐ | |
| f | debtor **absconded** | ☐ | |
| g | assets **removed/concealed** | ☐ | |
| h | **not reasonably equivalent value** | ☐ | |
| i | debtor **insolvent** at/around transfer | ☐ | |
| j | timing vs. **substantial debt** incurred | ☐ | |
| k | essential assets to a **lienor → insider** | ☐ | |

## C. CIVIL AGENT — build the avoidance claim (creditor side)
1. Confirm the creditor/claim, the transfer, and the theory (§ A).
2. Plead the badges with **facts** (§ B → `complaint-fufta.md`, Count I) + the constructive count
   (Count II). Insolvency: use § 726.103 balance-sheet **or** equitable (cash-flow) insolvency; tie to
   the forensic reconstruction (`/glaw-financial-forensics`, the GL).
3. Pick the **§ 726.108 remedy**: avoidance, attachment, injunction, receiver, levy, money judgment vs.
   the transferee (§ 726.109(2), capped at asset value or the claim).
4. **Veil/insider overlay:** if the transferee is an alter-ego or insider, pair with `/glaw-veil-piercing`
   (alter-ego factor matrix) + civil theft (§ 772.11) where felonious intent is supportable.
5. **Assignment/receivable?** If the "transfer" is an assignment of a claim/receivable, route the
   **true-sale vs. disguised-loan / real-party-in-interest** analysis to **receivables-assignment-counsel**
   / **/fl-claims-assignment** before drafting.

## D. ADVERSARIAL AGENT — red-team the claim (transferee/debtor side)
Run BEFORE filing (this is the FL Defense Counsel pass for a FUFTA claim). The transferee's killers:
1. **§ 726.109(1) GOOD-FAITH TRANSFEREE FOR REASONABLY EQUIVALENT VALUE** — the single biggest defense:
   if the transferee took in good faith and gave REV, the actual-intent count fails and recovery is
   limited to a residual (transferee keeps a lien to the extent of value given, § 726.109(4)). *608
   Hoffner: a sale at ~appraised value = REV → FUFTA MSJ denied.*
2. **Reasonably equivalent value** rebuts the constructive count (§ 726.105(1)(b)/§ 726.106(1)) and
   badge (h) — show dollar-for-dollar, a genuine arms-length sale, or satisfaction of an antecedent debt.
3. **Solvency** — the debtor was solvent and not rendered insolvent (defeats § 726.106(1) + badge (i)).
4. **SOL / extinguishment (§ 726.110)** — the claim is time-barred (run the dates).
5. **Not a creditor / no claim / asset exempt** — standing + "asset" attacks (§ 726.102).
6. **Badges rebutted** — no insider, recorded openly, no retained control, no insolvency.
→ Enumerate with `glaw-fl-defense for "fraudulent transfer"`; the Chief produces the resolution.

## E. ADJACENT CHAPTERS
- **Ch. 725 (Statute of Frauds, § 725.01):** a guaranty / land-sale / not-within-1-year agreement must be
  **written and signed** — both a sword (enforce a written guaranty) and a shield (defense "Statute of
  Frauds"). Cross-ref `glaw-fl-defense show "statute of frauds"`.
- **Ch. 727 (ABC):** a debtor's assignment for the benefit of creditors is a non-bankruptcy liquidation;
  if it is a **sham to defeat one creditor**, attack it as a fraudulent transfer (§ A-D). The § 727.105
  exclusive-forum bar otherwise channels creditor claims to the assignee.

<!-- Gate: confirm SOL (§ 726.110), run the badges scorecard, ALWAYS anticipate the § 726.109 good-faith
     defense, route assignments to receivables-assignment-counsel, then the FL Defense Counsel adversarial
     pass + Chief resolution. UPL/work-product — not legal advice; verify every § and cite. -->
