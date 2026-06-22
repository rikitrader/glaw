# Seats & Adversarial RED/BLUE Matrix (409A)

The defensibility record. After the math and the RED-team panel, every seat's
attack must resolve to **HOLDS**, **HOLDS-CONDITIONED** (condition named +
verified), or **MATERIAL** (disclosed). A draft is **exam-ready for appraiser
review** when no attack is left hidden — not when no attack exists.

> Fill this matrix from *this matter's* numbers. The text below is the template
> and the doctrine each seat presses; replace the RED/BLUE cells with the actual
> findings against `results.json` + `audit_log.json` + the OPM run.

```
┌──────────────────────────┬─────────────────────────────────┬────────────────────────────────────────────────────────────┬──────────────────┐
│           Lens           │            RED attack           │              BLUE response / fix folded in                 │     Residual     │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ IRS §409A examiner       │ "Common FMV set artificially    │ DLOM rubric-scored from stage/revenue/funding/horizon/exit │ HOLDS-COND       │
│ (FMV understatement,     │ low to cut strike prices;       │ within 10–35% band; strike = FMV×(1−DLOM); every input in   │ (DLOM inputs     │
│ §6662 penalty)           │ DLOM inflated."                 │ audit_log. HOLDS if DLOM inputs are real & contemporaneous. │  must be real)   │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ IRS — safe-harbor        │ "No qualified independent       │ Memo states plainly: DRAFT; independent-appraisal /         │ MATERIAL         │
│ reliance integrity       │ appraiser → the rebuttable      │ illiquid-startup presumption requires a signed appraiser.   │ (disclosure —    │
│                          │ presumption never attaches."    │ Recommend appraiser before any grant relies on safe harbor. │  not a fix)      │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ Audit-Defense Appraiser  │ "Backsolve doesn't reproduce    │ OPM (bin/opm.py + engine backsolve) reproduces the last     │ HOLDS-COND       │
│ (PCAOB / Big-4)          │ the last round; breakpoints     │ round amount; waterfall breakpoints tie to the cap table;   │ (OPM must tie to │
│                          │ wrong; sigma cherry-picked."    │ sigma/T benchmarked to sector comps. HOLDS if OPM ties.     │  the round)      │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ Cheap-stock reviewer     │ "Strikes in 12–18 mo pre-IPO    │ Preferred/common spread justified by liquidation prefs +    │ HOLDS-COND       │
│ (IPO / SEC)              │ sit below fair value →          │ stage; strike trend tied to dated valuations; waterfall     │ (spread must be  │
│                          │ restatement / cheap stock."     │ + conversion test explain the gap. HOLDS if spread economic.│  economic)       │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ FS auditor (ASC 718/820) │ "Level-3 inputs unsupported;    │ Method follows AICPA practice aid; every input+formula+     │ HOLDS-COND       │
│                          │ DLOM unsupported."              │ intermediate in audit_log; DLOM method documented.          │ (contemporaneous │
│                          │                                 │ HOLDS conditioned on contemporaneous data.                 │  data)           │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ Independent valuation    │ "Terminal value is most of EV;  │ Report flags PV(TV) % of EV; comps use median not mean;     │ HOLDS-COND       │
│ analyst                  │ comps span 4×–13×; PWERM is     │ widen comparability narrative; cross-check vs PWERM, OPM,   │ (divergence      │
│                          │ wishful."                       │ last round. HOLDS if approach divergence < 40%.            │  < 40%)          │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ Board / fiduciary        │ "Options granted without a      │ compliance verdict gates grants; revaluation triggers       │ HOLDS            │
│                          │ current valuation in hand."     │ enforced; board minutes reference the dated DRAFT.          │                  │
├──────────────────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────────┼──────────────────┤
│ Skeptical client CFO     │ "Hockey-stick forecast; the     │ Forecast realism challenged; downside weighted in PWERM;    │ MATERIAL         │
│                          │ next round marks us down."      │ sensitivity shown. Client chooses with eyes open.          │ (disclosure)     │
└──────────────────────────┴─────────────────────────────────┴────────────────────────────────────────────────────────────┴──────────────────┘
```

## Residual ratings (definition)

| Rating | Meaning | Required action |
|---|---|---|
| **HOLDS** | Attack defeated by design/data already in the record. | None. |
| **HOLDS-CONDITIONED** | Holds only if a named condition is true. | Verify + document the condition before relying. |
| **MATERIAL** | A live risk that cannot be engineered away. | Surface in the memo Executive Summary + Risk Flags; client/board accepts with eyes open. |

## Exam-ready draft gate
The memo may ship as a DRAFT when **every** lens above is HOLDS, HOLDS-CONDITIONED
(condition verified), or MATERIAL (disclosed). The single failure mode is a hidden
MATERIAL finding. The safe-harbor-reliance lens is **always MATERIAL** until a
qualified independent appraiser has reviewed and signed — never imply the
presumption or safe-harbor status without one.

## Doctrine each seat presses (for grounding the RED cells)
- **FMV understatement** — implied common/preferred ratio plausible for the stage?
- **DLOM aggression** — tied to a method (Finnerty / protective-put / restricted-stock studies), not a round number?
- **Sigma / time-to-liquidity gaming** — benchmarked, not stretched to lower the common call value?
- **Backsolve integrity** — does the OPM actually reproduce the last round amount? (engine `opm_backsolve` does this by construction.)
- **Breakpoint / waterfall** — senior prefs, participation, conversion, as-converted breakpoints modeled correctly? (engine waterfall runs the conversion test.)
- **Method selection** — income vs market vs asset justified for the stage, not chosen for the lowest number?
- **Comps cherry-picking** — peers truly comparable (stage, growth, margin, sector); survivorship bias?
- **Staleness** — any material event since the valuation date that voids it (12-month / material-event rule)?
- **Safe-harbor integrity** — does this qualify for the independent-appraisal presumption, or is it a board valuation dressed up? The presumption is **rebuttable**.
