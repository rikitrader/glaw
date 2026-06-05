---
name: glaw-adversarial
version: 1.0.0
description: "GLAW pipeline stage 5 and the HARD GATE before filing. RED team destroys every position; BLUE team rebuilds only the survivors. Fans out one adversary per lens — opposing counsel, IRS examiner, SEC/securities reviewer, bankruptcy trustee / FUFTA creditor, and a skeptical judge — each trying its hardest to defeat the position, then keeps only what survives by majority. Use for: 'red team my case', 'attack this position', 'destroy and rebuild', 'will this survive', 'adversarial review', 'stress test the structure', or before any GLAW matter advances to file."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Agent
  - WebSearch
  - Skill
triggers:
  - red team
  - adversarial review
  - attack this position
  - destroy and rebuild
  - will this survive
  - stress test
---

## When to invoke this skill

Stage 5 of the GLAW pipeline and a **hard gate** before `/glaw-file`. This is
ETHOS principle 2 made operational: the adversary is always in the room. Every
position the firm intends to file — every cause of action, every tax election,
every securities exemption, every entity in the structure — gets attacked here
before it leaves the building. A claim the firm's own adversary destroys does
not get filed.

RED destroys. BLUE rebuilds only survivors. Nothing reaches `file` until this
pass produces no new fatal attack and `/glaw-legal-research` has verified the
survivors.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` before routing.

## Workflow

### Step 1 — Inventory the positions to attack
From the strategy, structure, and draft work-product, list every discrete
position the matter rests on. Number them. A position is anything an adversary
could defeat in isolation:
- **Litigation**: each cause of action, each element, standing, jurisdiction, SOL, damages theory.
- **Corp-build**: each entity's separateness, each tax election (S-corp, 83(b), QSBS), each securities exemption (Reg D 506(b)/(c), Reg S, ICA 3(c)(1)/3(c)(7)), each transfer of value, each fiduciary structure.

### Step 2 — RED team: fan out one adversary per lens (Agent tool)
Spawn adversaries in parallel via the Agent tool, one per relevant lens. Each is
instructed to try its **hardest to defeat** the matter, not to be fair:
- **Opposing counsel** — motion to dismiss, affirmative defenses, factual holes, every count attacked element-by-element. Route depth to `forensic-case-investigator` (its own RED/BLUE case-builder) and `elite-corporate-counsel` (adversarial panel mode).
- **IRS examiner** — recharacterization, sham/substance-over-form, disallowed deductions, blown elections, reasonable-comp, accuracy penalties. Route to `financial-forensics` (IRS-audit-shield) and `tax-strategy`/`tax-compliance`.
- **SEC / securities reviewer** — integration, general-solicitation defects, bad-actor disqualification, accredited-verification gaps, ICA/Advisers Act traps, disclosure inadequacy. Route to `fund-regulatory-council`, `tokenization-compliance`, `pe-vc-counsel`.
- **Bankruptcy trustee / creditor (FUFTA)** — fraudulent transfer (Ch. 726 / §548), badges of fraud, reasonably-equivalent-value, preference, veil-pierce / alter-ego, successor liability. Route to `elite-corporate-counsel` and `/glaw-restructuring`.
- **Skeptical judge** — does this persuade a tired, hostile bench? Weakest link, credibility, equities, the question you don't want asked.

Use WebSearch only to surface adverse authority and recent rule changes — never
to manufacture a cite; verification is `/glaw-legal-research`'s job.

### Step 3 — Score each position (majority-survives)
For every position, collect the strongest attack from each lens. A position
**survives** only if it withstands the majority of adversaries that have standing
to attack it. Classify each:
- **survives** — withstood every serious attack as drafted.
- **needs-fix** — survivable but only with a specific change (added element, restructured transfer, swapped exemption, better record).
- **struck** — no rebuild leaves it standing; do not file it.

### Step 4 — BLUE team: rebuild only survivors
For each `needs-fix`, draft the specific cure and re-attack it. For each `struck`,
remove it or replace it with a position that can survive. BLUE never rehabilitates
by softening language — it rebuilds the substance or drops the claim. Re-run the
relevant RED lens against every rebuild.

### Step 5 — Loop until quiescent
Repeat Steps 2–4 until a full RED pass surfaces **no new fatal attack**. Only a
clean pass closes the gate. Log each round:
```bash
~/.claude/skills/glaw/bin/glaw timeline-log adversarial_round
```

### Step 6 — Verify survivors (HARD requirement before file)
Hand the surviving positions and every authority they rely on to
**`/glaw-legal-research`** for citation verification. An unverifiable survivor is
struck, not filed (ETHOS principle 3).

### Step 7 — Advance
Only when no new fatal attack surfaces AND survivors are verified:
```bash
~/.claude/skills/glaw/bin/glaw stage file
~/.claude/skills/glaw/bin/glaw timeline-log adversarial_done
```
Hand off to `/glaw-file`.

## Output
A **SURVIVABILITY REPORT** — a table of every position → its strongest attack
(per lens) → `survives` / `struck` / `needs-fix` → the cure applied. The report
names what was dropped and why. Carry the UPL footer from `/glaw-ethics-conflicts`
on the report. Only verified survivors pass to `file`.
