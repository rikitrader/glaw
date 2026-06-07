---
name: glaw-autocounsel
version: 1.0.0
description: "GLAW review-bench orchestrator (the /autoplan analog). Runs /glaw-strategy, /glaw-structure, and /glaw-adversarial back-to-back, making reasonable decisions automatically and surfacing only genuine taste/borderline/judgment calls at a SINGLE final AskUserQuestion gate — instead of 15 intermediate prompts. Produces a fully-reviewed matter ready for /glaw-draft or /glaw-file. Use for: 'run the bench', 'autocounsel', 'review the whole matter', 'strategy + structure + adversarial in one go', 'don't ask me 15 times'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Agent
  - AskUserQuestion
  - Skill
triggers:
  - autocounsel
  - run the bench
  - review the whole matter
  - one final gate
  - review bench
---

## When to invoke this skill

The firm's review bench. Invoke it to run **strategy → structure → adversarial**
in one sitting without stopping for every micro-decision. It auto-decides
anything that has a clearly-right answer and parks only the genuine
taste/borderline/judgment calls for a single final gate. It is the GLAW analog of
gstack's `/autoplan`: maximize reviewed throughput, minimize interruptions.

Use it after conflicts clear and intake is done. For a single stage, call that
stage directly instead.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` before routing. **Refuse to run
until `CONFLICTS: cleared`** in the charter (route to `/glaw-ethics-conflicts` if not).

## Decision principles (how it auto-decides)

It applies these so it doesn't have to ask:
1. **Prefer the more protective structure.** When two structures both work, pick the one that better isolates liability, preserves elections, and survives an adversary.
2. **Plead every viable count / run every viable exemption.** Completeness is cheap (ETHOS 1). Include anything that survives adversarial; only drop what gets struck.
3. **When the adversary and the drafter disagree, surface it** — don't silently overrule either. That's a judgment call for the gate.
4. **Cite or strike.** Anything unverifiable is parked for `/glaw-legal-research`, never assumed.
5. **Irreversible / high-stakes calls go to the user** — choice of forum, entity domicile, fee posture, settlement appetite, anything one-way-door.

## Workflow

### Step 1 — Strategy (auto)
Invoke `/glaw-strategy`. Capture the case theory (litigation) or deal thesis
(corp-build). Auto-accept the dominant theory; record alternatives considered.
Park only a true fork (e.g. claim-for-damages vs equitable-relief posture) for the gate.

### Step 2 — Structure (auto)
Invoke `/glaw-structure`. Build the entity org chart / parties-and-claims map, tax
elections, cap table, fund tiers — routing to the roster seats (`glaw-corporate-counsel`,
`glaw-pe-vc-counsel`, `glaw-tax-strategy`, `glaw-fund-regulatory-council`, etc.). Apply principle
1 (more protective) and 2 (completeness). Park only domicile/forum and other
one-way-door choices.

### Step 3 — Adversarial (auto, but it owns its own loop)
Invoke `/glaw-adversarial`. Let it run its full RED→BLUE fan-out and loop to
quiescence. Auto-accept its `struck` and `needs-fix` verdicts. Where its adversary
and the drafter from Steps 1–2 genuinely disagree, capture that as a gate item
(principle 3). Collect its SURVIVABILITY REPORT.

### Step 4 — Assemble the gate list
Across all three stages, gather ONLY the genuine taste/borderline/judgment calls:
forks left open, drafter-vs-adversary disagreements, one-way-door choices, and any
position marked `needs-fix` where the cure is a business/risk choice rather than a
legal one. If there are none, skip the gate.

### Step 5 — Single final gate (AskUserQuestion)
Present the parked items as ONE AskUserQuestion with concrete options and a
recommended default per item (per the decision principles above). This is the only
interruption. Apply the answers.

### Step 6 — Verify + report
Send all survivors to `/glaw-legal-research` for citation verification (still
required before any filing). Then report a one-screen summary: theory, structure,
survivability verdict, decisions made, and what the gate resolved.

### Step 7 — Hand off
The matter is now strategized, structured, and adversaried.
```bash
~/.claude/skills/glaw/bin/glaw timeline-log autocounsel_done
```
Hand off to `/glaw-draft` (if documents aren't drafted yet) or `/glaw-file` (if
they are and survivors are verified). Do not advance past the adversarial gate
into `file` without verification.

## Output
A **fully-reviewed matter**: case theory / deal thesis, the structure, and the
SURVIVABILITY REPORT — with reasonable calls already made, the genuine judgment
calls resolved at a single gate, and a clean handoff to `/glaw-draft` or
`/glaw-file`. UPL footer (`/glaw-ethics-conflicts`) on any external deliverable.
