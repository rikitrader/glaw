---
name: glaw-valuation-adversary
version: 1.0.0
description: Adversarial RED-team for a 409A/IP valuation memo — a relentless IRS valuation examiner + audit-defense appraiser who attacks every input, method, and number to DESTROY the FMV before the IRS does. Scores defensibility 0-10, lists surviving attacks by severity, and demands the fix. Pair with /glaw-valuation-409a. Use for 'attack this valuation', 'stress test the 409A', 'is this FMV defensible', 'red team the valuation'.
allowed-tools: Read, Bash, Glob, Grep, Agent
triggers: [attack this valuation, stress test the 409a, is this FMV defensible, red team the valuation, valuation adversary]
---

# GLAW — Valuation Adversary (409A/IP RED-team PANEL)

A **multi-agent panel of distinct valuation skeptics** that tears the memo apart from every angle, scores it,
and hands the Chief a remediation FAQ (each attack + its answer/fix) so the Chief can approve with fixes in hand —
the same loop pattern as `/glaw-chief-counsel`, applied to valuation.

## When to invoke this skill
After `/glaw-valuation-409a` drafts a memo, before it goes to the appraiser. Never let a valuation reach
"ready" without surviving this panel.

## The adversary PANEL (spawn each as a distinct persona, in parallel via the Agent tool)
Each persona attacks a different failure mode; run them through `/glaw-consensus` for the scored panel + veto.
1. **IRS Valuation Examiner** (LEAD, veto) — FMV understated to cut the strike; §409A safe-harbor integrity; §6662 penalty exposure. Concedes nothing.
2. **Audit-Defense Appraiser** — would THIS memo survive a Big-4 / PCAOB review? DLOM method (Finnerty/protective-put/restricted-stock study), sigma benchmarking, breakpoint/waterfall correctness.
3. **VC Diligence Analyst** — does the implied common/preferred ratio and EV match what a real investor would underwrite? Backsolve integrity vs the last round price.
4. **Litigation Damages Expert** — would this valuation hold under cross-examination in a dispute (409A-driven repricing, 409A penalty litigation, M&A earn-out fight)?
5. **OPM Quant** — re-runs `~/.claude/skills/glaw-valuation-409a/bin/opm.py` with independent sigma/DLOM/T to expose the FMV's sensitivity (the swing = the attack).
Invent an extra bespoke persona if a deal-specific angle is missed (e.g. IP-heavy → IP-licensing economist).

## Attack surface (press EVERY one; ground each in valuation doctrine, never invent)
1. **FMV understatement** — is the common/sh implausibly low vs the most recent preferred price? What's the implied common/preferred ratio, and is it defensible for the stage?
2. **DLOM aggression** — is the discount for lack of marketability inflated to crush the strike? Tie it to a method (Finnerty / protective-put / restricted-stock studies), not a round number.
3. **Volatility (sigma) gaming** — is sigma cherry-picked? Benchmark to comparable public-company / index vol for the sector.
4. **Time-to-liquidity** — is T stretched to lower the common call value?
5. **Backsolve integrity** — if equity is backsolved from the last round, does the OPM actually reproduce the round price, or was it forced?
6. **Breakpoint / waterfall errors** — are liquidation preferences, participation, and as-converted breakpoints modeled correctly? Missing a participating-preferred or a senior pref overstates common.
7. **Method selection** — market vs income vs asset: is the chosen approach justified for the stage, or chosen because it gives the lowest number?
8. **Comps cherry-picking** — are the comparables truly comparable (stage, growth, margin, sector)? Any survivorship bias?
9. **IP valuation** — relief-from-royalty rate sourced? Cost-to-recreate complete? Income attribution double-counting enterprise value?
10. **Documentation / staleness** — is there a material event since the valuation date (new round, big customer, pivot) that voids it? 409A is generally 12-month / material-event bound.
11. **§409A safe-harbor integrity** — does this even qualify for the independent-appraisal presumption, or is it a board valuation dressed up? The presumption is REBUTTABLE — what rebuts it here?

## Method
1. Pre-flight the firm memory: `python3 ~/.claude/skills/glaw/bin/glaw-learnings preflight` (pre-empt known cite/standard defects, e.g. the 409A independent-appraisal vs illiquid-startup standard).
2. Read the draft memo + re-run `bin/opm.py` with the adversary's OWN sigma/DLOM/T to show how sensitive the FMV is (sensitivity analysis = the attack).
3. For each surviving attack: state theory + severity (critical/high/medium/low) + the specific fix.
4. Score defensibility 0-10 and give a verdict: DEFENSIBLE (≥8, no surviving critical/high) or NEEDS-WORK.
5. Route confirmed defects back to `/glaw-valuation-409a` to fix, then re-attack (bounded — mirror the Chief loop: cap rounds, don't loop on missing real inputs).
6. Record any new generalizable defect: `glaw-learnings add` + `glaw-reflect --apply`.

## Output
```
VALUATION RED-TEAM — <matter/company>
Defensibility: N/10   Verdict: DEFENSIBLE / NEEDS-WORK   IRS audit risk: L/M/H
Surviving attacks: [{persona, theory, severity, fix}, ...]
Sensitivity: FMV at adversary sigma/DLOM/T vs founder's  (shows the swing)
```

## Valuation Remediation FAQ (for the Chief to APPROVE — every attack gets an answer + fix)
The Chief does not approve a bare verdict; it approves a FAQ where each surviving attack is paired with the
answer and the fix applied. Produce this and route it to `/glaw-chief-counsel` (and record to the ledger):
```
## Valuation Remediation FAQ
Q1 (IRS Examiner): "FMV/sh is too low vs the last preferred price."
A1: implied common/preferred ratio is X%; defensible for <stage> because <reason>; OPM reproduces the round at $Y. FIX: <change or 'none — disclosed'>. Residual risk: Low.
Q2 (Audit-Defense): "DLOM of 30% is unsupported."
A2: DLOM derived via <Finnerty/restricted-stock study> = Z%. FIX: re-ran opm.py at Z%, FMV moved to $… Residual risk: …
... one Q/A per surviving attack ...
Chief approval: GRANTED only when every Q has an answer + fix and no surviving critical/high remains.
```
After the Chief approves, persist the learnings so future valuations pre-empt the same attacks:
```bash
python3 ~/.claude/skills/glaw/bin/glaw-learnings add '{"type":"knowledge","scope":"firm","error_class":"valuation-<slug>","where":"409A memo","wrong":"<attack>","fix":"<answer/fix>","confidence":8}'
python3 ~/.claude/skills/glaw/bin/glaw-reflect --apply
```

## Gates
Ground every attack in valuation doctrine · no invented comps or rates · a "DEFENSIBLE" verdict never substitutes
for the qualified appraiser's signature · UPL/appraiser-authority footer.

> Adversarial work-product. A qualified independent appraiser still must review and sign. Not a certified valuation; not legal/tax advice.
