---
name: glaw-consensus
version: 1.0.0
description: Reusable scored consensus gate — distinct-identity adversaries score a position 0-10 per lens; the government/IRS persona holds a veto; converges to BULLETPROOF / DRAFTING-CLEAN / NEEDS-WORK. The firm-wide primitive extracted from the Chief-Counsel loop.
allowed-tools: Read, Bash, Glob, Grep, Agent
triggers: [consensus, score this, panel review, is this defensible, adversarial gate]
---

# GLAW — Consensus Gate (scored, vetoed, bounded)

A reusable gate ANY matter or seat can call to get a defensibility verdict on a single position
or document — without re-implementing the Chief-Counsel loop. Same scoring contract the
`/glaw-chief-counsel` engine uses, so verdicts are comparable across the firm.

## When to invoke this skill
When you need a defensibility verdict on ONE position/document ("score this §351 memo",
"is this clause bulletproof?", "run the panel on doc 17") — not a full matter pipeline. For a
whole matter, use `/glaw-chief-counsel`.

## The contract (identical to the engine)
1. **Panel.** Assemble distinct-identity adversaries, each with a named lens. The **IRS/government
   persona is the most aggressive and holds a veto** — it concedes nothing until there is genuinely
   no issue. Add 1 invented persona for an angle the standard panel misses.
2. **Score.** Each adversary scores 0-10 how DEFENSIBLE the position is and lists only attacks that
   still SURVIVE, with severity (critical/high/medium/low). Ground every attack in real law; never
   invent authority.
3. **Classify (the convergence key).** Split surviving attacks into:
   - **fact-gaps** — a real fact is missing ([VERIFY], no issuance date / gross-assets / cap table /
     valuation / EIN). These are recorded as "facts needed", NOT fixable defects.
   - **drafting defects** — fixable now.
4. **Verdict.**
   - **BULLETPROOF** — no surviving critical/high drafting defects, IRS clear on drafting, min-score ≥ 8, and zero fact-gaps.
   - **DRAFTING-CLEAN — pending facts** — no fixable critical/high left and IRS clear on drafting, but fact-gaps remain. Terminal; can't be hardened away.
   - **NEEDS-WORK** — fixable critical/high drafting defects survive.
5. **Budget.** Hard cap on adversary count per call (mirror `MAX_DEBATE_AGENTS=48`). Never loop on fact-gaps.

## Pre-flight (read the firm's memory first)
Always inject prior defects so the panel pre-empts known errors:
```bash
python3 bin/glaw-learnings preflight
```

## Workflow
1. Emit the GLAW preamble; confirm the position + the document path.
2. Run `glaw-learnings preflight` and give every adversary the KNOWN-DEFECTS digest.
3. Spawn the panel (Agent tool, parallel). Each returns {adversary, score, verdict, surviving[]}.
4. Apply the classify + verdict contract above. Report the verdict, min-score, surviving drafting
   defects, and the facts-needed list.
5. Write back any NEW distinct defect: `glaw-learnings add '<json>'`; then `glaw-reflect --apply`.

## Verify against the canonical implementation
The pure logic (`classify`, `govDraftingClear`, budget cap, convergence) is unit-tested in
`seats/glaw-chief-counsel/test/loop-selftest.mjs` (zero-spend). Keep this gate's
verdict semantics in sync with that test.

## Gates
Citations verified before any "BULLETPROOF" stamp · UPL disclaimer on external deliverables ·
never declare BULLETPROOF while fact-gaps remain (that's DRAFTING-CLEAN).

> ATTORNEY/CPA WORK-PRODUCT — a licensed professional must review, sign, and file. Not legal/tax advice.
