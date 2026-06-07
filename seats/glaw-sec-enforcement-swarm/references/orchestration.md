# Orchestration — Swarm Recipes & Spawn Patterns

How to route a matter to seats, run them in parallel, and reconcile. The SKILL.md Step 3
gives the generic loop; this file gives the **named recipes** and the **spawn mechanics**.

## Spawn mechanics

- Spawn each seat with the **Agent tool**, `general-purpose` type, instructing it to read its
  definition file (`~/.claude/skills/sec-enforcement-swarm/agents/NN-*.md`) and the relevant
  `references/` files, then return a structured findings block with **every line cited**.
- Put **all independent seats in ONE message** with `run_in_background: true`. Wait for all
  to return before reconciling. Do **not** poll status.
- Sequential dependencies (intake → fan-out → synthesis) are barriers; only the middle
  fan-out is parallel.

## Named recipes

| Matter type | Seats (in order) | Notes |
|---|---|---|
| **Accounting-fraud case** | 2 intake → (3 forensic ∥ 11 filing-risk) → 1 attorney → 9 expert → 8 lit-support | Revenue-rec / restatement core; expert does loss-causation/damages |
| **Insider-trading case** | 2 intake → (5 insider ∥ 4 market) → 1 attorney → 8 lit-support | Market analyst corroborates suspicious timing with the tape |
| **Manipulation case** | 2 intake → 4 market → 3 forensic (if P&L tracing) → 1 attorney → 9 expert | Expert often required to prove artificial price impact |
| **FCPA matter** | 2 intake → (6 fcpa ∥ 3 forensic) → 1 attorney → 8 lit-support | Forensic traces the off-books payments / slush accounts |
| **Whistleblower triage** | 7 whistleblower → 2 investigator (if credible) → 1 attorney | Score the tip first; only build if it survives credibility |
| **Defense engagement** (client got a Wells) | 2 intake → 1 attorney (theory) → relevant substantive seat(s) for rebuttal → 10 wells-response → 8 lit-support | RED team plays SEC staff |
| **Filing diligence** | 11 filing-risk → 3 forensic (deep-dive any flag) | Fast screen; escalate flags only |
| **Expert-only ask** | 9 expert (+ pull facts from 3/4/5 as needed) | Standalone Rule 26 report |

## Reconciliation rules (after fan-out)

1. **Merge** all seat findings into one fact base keyed by entity/transaction/date.
2. **Dedupe** — same fact from two seats = one row, both cites retained.
3. **Conflict** — if two seats disagree, surface it explicitly; do not silently pick one.
4. **Cite gate** — a finding advances to the Proof Matrix **only with a source cite**; an
   uncited assertion is downgraded to a *lead* (goes in Gaps & Next Steps, not Findings).
5. **Hand off** survivors to Step 4 (RED → BLUE) before anything reaches the deliverable.

## Scaling the swarm to the ask

- "Quick read / is this insider trading?" → single seat inline, light RED pass.
- "Build the case" / "respond to this Wells Notice" → full recipe, parallel fan-out, full
  RED→BLUE, complete deliverable with audit trail.
- "Be exhaustive / litigation-grade" → add a second independent RED team per claim and a
  completeness critic that asks *what evidence or theory did we not run?*
