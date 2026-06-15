---
name: glaw-strategy
version: 1.0.0
description: "GLAW pipeline stage 2 — the strategy memo. Litigation: theory of the case, the elements of every viable claim and defense, the full set of causes of action to plead, the damages theory, and settlement posture. Corp-build: the deal thesis — objective, candidate entity strategies with tradeoffs, high-level tax posture, capital plan, and exit. Routes each piece to a specialist seat and gates direction with the client before structure. Use after intake clears conflicts, or when asked for 'case theory', 'theory of the case', 'deal thesis', 'litigation strategy', 'what claims do I have', 'how should I structure this'."
allowed-tools:
  - Skill
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
  - WebSearch
triggers:
  - case theory
  - theory of the case
  - deal thesis
  - litigation strategy
  - what claims do I have
  - strategy memo
---

## When to invoke this skill

Second stage of the GLAW pipeline. Runs once `/glaw-ethics-conflicts` reports
`CONFLICTS: cleared`. Strategy turns the intake charter into a **committed
direction**: for a case, the theory and the complete claim set; for a build, the
deal thesis and the entity path. It decides *what we are doing and why* — structure
(stage 3) decides *how*, and draft (stage 4) produces the paper.

Strategy takes positions but does not verify citations — that is
`/glaw-legal-research` at the file gate. It states the law it relies on plainly and
flags every proposition that needs authority.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `lib/firm-roster.md` before routing any sub-task.
If the preamble shows conflicts are not cleared, stop and return to `/glaw-ethics-conflicts`.

## Workflow

Branch on `MATTER_TYPE` from `matter.md`.

### Litigation case — Theory of the Case

1. **State the theory.** One paragraph: who did what to whom, why it is wrong in
   law, and what relief follows. The theory is the spine every claim hangs on.
2. **Plead every viable count (Build-the-whole-file).** Route claim development to
   **`glaw-elite-corporate-counsel`** (fraud-on-court, FUFTA, veil-piercing, civil theft,
   MCA/usury) and **`glaw-federal-trial-counsel`** (federal claims, RICO, removal/venue).
   For each candidate cause of action, write:
   - the **elements** the plaintiff must prove,
   - the **facts** from the charter that satisfy each element,
   - the **gaps** (elements with no supporting fact yet → fact-development item).
   Enumerate every count that is colorable, not just the obvious one. A skipped
   count is a waived count.
3. **Map defenses + counterclaims.** For a defense posture, list affirmative
   defenses and any counterclaims by the same elements-and-facts method.
4. **Develop the facts.** Where elements lack proof, route to
   **`glaw-forensic-case-investigator`** (connect the dots, follow the money, who controls
   the entities) and **`glaw-financial-forensics`** (reconstruct the numbers from records).
   Capture each open fact as a discovery target for stage 4.
5. **Damages theory.** Quantify each measure: actual/compensatory, statutory (note
   trebling where pleaded — e.g. civil theft), punitive exposure, attorney's-fee
   hooks, pre/post-judgment interest. Route quantification to **`glaw-financial-forensics`**
   or **`glaw-company-valuation`** where a number must be modeled.
6. **Settlement posture.** Best/worst/likely outcome, leverage points, and a
   pre-suit demand path vs. file-first path.

### Corp/fund build — Deal Thesis

1. **Objective.** One paragraph: what is being built (operating company / fund /
   token offering / roll-up), the money flow, and what success looks like (entity
   live, offering closed, exit achieved).
2. **Candidate entity strategies (with tradeoffs).** Route to
   **`glaw-institutional-finance`** and **`glaw-pe-vc-counsel`**. Lay out 2–3 viable paths,
   each with its tradeoffs — e.g. single C-corp vs. holdco/opco; LLC vs. C-corp for
   QSBS; for a fund, GP + management co + LP (+ feeder/blocker) tiers. Do not pick
   silently — present the options.
3. **Tax posture (high level).** Route to **`glaw-tax-strategy`**: pass-through vs.
   C-corp, QSBS §1202 eligibility, check-the-box, carried-interest treatment,
   blocker need for tax-exempt/foreign LPs. Detail belongs to stage 3 — here, state
   the posture and its driver.
4. **Capital plan.** How it gets funded: founder/bootstrapped, SAFE/priced round,
   Reg D 506(b)/506(c), Reg S, Reg CF/A+, or fund capital calls. Route securities
   framing to **`glaw-pe-vc-counsel`** / **`glaw-institutional-finance`**.
5. **Exit.** Acquisition, IPO, secondary, fund wind-down/distribution waterfall.
   Route a valuation anchor to **`glaw-company-valuation`** where the thesis turns on a number.

### Direction gate (AskUserQuestion — HARD)

Before structure, confirm direction with the client. Use **AskUserQuestion**:
- Litigation: which counts to carry forward, pre-suit demand vs. file-first,
  settlement appetite.
- Corp-build: which entity strategy to pursue, risk/control/tax priority ordering.

Do not advance to structure on a silently chosen path. Record the decision in
`matter.md` (append a `## Strategy decision` block).

## Output

Write the **strategy memo** to `~/.glaw/matters/<slug>/strategy-memo.md`:
- litigation → theory, the full claim/defense set (each with elements · facts · gaps),
  damages theory, settlement posture, fact-development targets;
- corp-build → objective, candidate entity strategies with tradeoffs, tax posture,
  capital plan, exit, the chosen direction.

Then advance:

```bash
bin/glaw stage structure
bin/glaw timeline-log strategy_done
```

Hand off to `/glaw-structure`. No citations are blessed here — every legal
proposition is flagged for `/glaw-legal-research` at the file gate.

**Adversarial gate (downstream, hard):** the strategy is not relied on for filing until it
survives the firm's `/glaw-adversarial` RED→BLUE pass — opposing counsel / IRS / SEC attack
every theory and only the survivors stand. Write the strategy to *invite* that attack
(name the weakest link in each theory), since the orchestrator runs that gate before `file`.

> **Attorney work-product — not legal advice.** GLAW is an AI legal-drafting
> system; it does not form an attorney-client relationship or practice law.
