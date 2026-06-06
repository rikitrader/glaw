---
name: glaw-structure
version: 1.0.0
description: "GLAW pipeline stage 3 — the structure memo. Corp-build: the entity org chart, jurisdiction and entity-type choice with tradeoffs, cap table, tax elections (check-the-box, S-election, QSBS §1202, 83(b)), fund tiers (GP / management co / LP / SPV / feeder / blocker), holdco/opco split, and asset-protection layering. Litigation: the parties-to-claims matrix — each claim mapped to its elements and supporting facts — plus venue, jurisdiction, standing, and joinder. Routes each piece to a specialist seat. Use after the strategy memo, or when asked for 'entity structure', 'org chart', 'cap table', 'tax election', 'fund tiers', 'holdco opco', 'parties to claims', 'venue and standing'."
allowed-tools:
  - Skill
  - Bash
  - Read
  - Write
  - Edit
  - AskUserQuestion
triggers:
  - structure memo
  - entity structure
  - org chart
  - cap table
  - fund tiers
  - parties to claims
  - venue and standing
---

## When to invoke this skill

Third stage of the GLAW pipeline. Strategy decided *what and why*; structure
decides *how*. For a build, it lays out the entity machine — who owns what, formed
where, taxed how. For a case, it locks the architecture of the lawsuit — who sues
whom on which claim, where, and with what standing — so the pleadings draft
themselves at stage 4.

Structure commits an architecture; it does not draft the documents (stage 4) and
does not verify citations (`/glaw-legal-research` at the file gate).

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` before routing. Read
`~/.glaw/matters/<slug>/strategy-memo.md` — structure executes the chosen direction.

## Workflow

Branch on `MATTER_TYPE` from `matter.md`.

### Corp/fund build — Structure Memo + Org Chart

1. **Entity org chart.** Draw the full topology (ASCII tree): every entity, its
   owners, and the ownership percentages. Route to **`corporate-counsel`** and
   **`institutional-finance`**. Build the whole structure — name every entity that
   should exist, not just the obvious operating company.
2. **Jurisdiction choice.** **Delaware by default** for the C-corp / fund vehicles;
   note alternatives (Wyoming/Nevada for privacy/cost, home-state for a single-member
   LLC, Cayman for offshore feeders) with the tradeoff for each. Route to
   **`corporate-counsel`** / **`pe-vc-counsel`**.
3. **Entity type with tradeoffs.** C-corp (QSBS, institutional capital, double tax)
   vs. S-corp (pass-through, ownership limits) vs. LLC (flexibility, SE tax) vs. LP
   (fund vehicle). Lay out the tradeoffs; route the call to **`corporate-counsel`** +
   **`tax-strategy`**.
4. **Cap table.** Founders, option pool, SAFE/note conversions, priced-round
   preferred — fully diluted. Route modeling to **`institutional-finance`** and a
   valuation anchor (409A / preferred price) to **`company-valuation`**.
5. **Tax elections.** Route all to **`tax-strategy`**: check-the-box (Form 8832),
   S-election (Form 2553), **QSBS §1202** qualification (C-corp, ≤$50M gross assets,
   active-business, 5-yr hold), **83(b)** for founder restricted stock, entity
   classification for any blocker. Name each election, its deadline, and its driver.
6. **Fund tiers (if a fund).** Route to **`pe-vc-counsel`**,
   **`fund-regulatory-council`**, **`institutional-finance`**: GP entity, management
   company, fund LP, parallel/feeder funds, **SPV** for single deals, **blocker**
   corp for tax-exempt/foreign LPs, AIV. Map the carry, management fee, and waterfall
   to the tiers. For tokenized LP interests, route to **`tokenization-compliance`**.
7. **Holdco/opco split.** Where it applies, separate the IP/asset-holding entity
   from the operating entity; show the intercompany license/lease flow.
8. **Asset-protection layering.** Route to **`tax-strategy`** and, for trust/estate
   layers, **`/glaw-estate-trusts`**: which assets sit behind which entity, charging-order
   protection (LLC/LP), and any trust ownership above the holdco.

### Litigation case — Parties-to-Claims Matrix

1. **Parties-to-claims matrix.** A grid: rows = claims from the strategy memo,
   columns = each plaintiff and defendant. Mark who asserts each claim against whom.
   Route to **`elite-corporate-counsel`** / **`federal-trial-counsel`**.
2. **Elements + facts per claim.** For every cell that fires, restate the claim's
   **elements** and the **specific facts** that satisfy each — this is the skeleton
   the complaint draft fills. Carry forward the gaps from strategy as discovery items.
3. **Venue, jurisdiction, standing.** Route to **`federal-trial-counsel`**:
   subject-matter jurisdiction (diversity/amount-in-controversy or federal question),
   personal jurisdiction over each defendant, proper venue and forum, and **standing**
   for each plaintiff on each claim.
4. **Joinder.** Identify every party that must or may be joined (Rule 19/20) and
   every claim that should be joined or pleaded in the alternative. Build the whole
   file — name the party you could add, not just the one in front of you.

## Output

Write the **structure memo** to `~/.glaw/matters/<slug>/structure-memo.md`:
- corp-build → org-chart (ASCII), jurisdiction + entity-type rationale, cap table,
  the named tax elections with deadlines, fund tiers, holdco/opco, asset-protection layering;
- litigation → the parties-to-claims matrix, elements+facts per claim, venue/jurisdiction/
  standing analysis, joinder plan.

Then advance:

```bash
~/.claude/skills/glaw/bin/glaw stage draft
~/.claude/skills/glaw/bin/glaw timeline-log structure_done
```

Hand off to `/glaw-draft`. Every legal proposition here is flagged for
`/glaw-legal-research` at the file gate — no citation is blessed at this stage.

> **Attorney work-product — not legal advice.** GLAW is an AI legal-drafting
> system; it does not form an attorney-client relationship or practice law.
