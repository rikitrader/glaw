---
name: glaw
version: 1.0.0
description: "GLAW — a virtual corporate law firm. Opens a matter (litigation case OR corp/fund build) and drives it through intake → strategy → structure → draft → adversarial → file → docket → retro, routing each task to a specialist seat. Use for: 'open a matter', 'build a company/corp/fund', 'start a case', 'run the firm', 'GLAW', or any multi-step legal+tax+corporate engagement."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - AskUserQuestion
  - WebSearch
triggers:
  - open a matter
  - start a case
  - build a corp
  - build a company
  - build a fund
  - run the firm
  - glaw
  - virtual law firm
---

## When to invoke this skill

GLAW is the firm's Managing Partner. Invoke it whenever the user wants to run a
**multi-step legal engagement** rather than a single question — forming and
papering a company, structuring a fund, building or defending a litigation case,
or any work that crosses corporate + tax + securities + litigation seats.

For a single narrow question ("is this clause usury?", "draft one NDA"), route
directly to the owning seat in `lib/firm-roster.md` instead — don't open a matter.

GLAW does not replace a lawyer. It produces **attorney work-product for a licensed
attorney to review, sign, and file.** The UPL guardrail lives in `/glaw-ethics-conflicts`.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- roster ---"
sed -n '/## Matter pipeline/,/## Routing rule/p' ~/.claude/skills/glaw/lib/firm-roster.md 2>/dev/null | head -40
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` in full before assigning any seat.

## The pipeline

```
intake → strategy → structure → draft → adversarial → file → docket → matter-retro
```

Branched at intake into three tracks:
- **litigation** (civil): strategy = case theory, structure = parties/claims map, draft = pleadings/motions, adversarial = opposing counsel red-team, file = court e-filing packet.
- **corp-build** (company/fund): strategy = deal thesis, structure = entity org chart + tax + cap table, draft = formation/governance/offering docs, adversarial = IRS + SEC + creditor red-team, file = EDGAR/IARD/state filing packet.
- **investigation** (white-collar/criminal): led by `/glaw-investigations`, with the **Intelligence Super-Structure** (`/glaw-command`) for deep workups — FBI bureau (`/glaw-bureau`) + FinCEN (`/glaw-fincen`) + CIA (`/glaw-intel`) + SEC (`/glaw-sec`) cells. `/glaw-command` **triages → always briefs → escalates to a full DOSSIER only when red flags clear the threshold**, with adversarial review + scorecards on every issue. strategy = theory of wrongdoing, structure = entity & flow-of-funds map, draft = exposure matrix → complaint or referral, file = complaint or referral package.

Each stage is its own skill (`/glaw-<stage>`); this orchestrator sequences them and
holds the gates. Stages route work to the **divisions** in `lib/firm-roster.md`
(Corporate, Securities/Funds, Tax/IRS, Accounting/Finance via `/glaw-accounting`,
Litigation, Investigations via `/glaw-investigations`, Regulatory/Licensing,
Private Client, Legal Writing) — every domain maps to a seat there, no gaps.

The orchestrator is the firm's Chief layer: it does not merely call the next skill. It
directs departments, requires review of reports/numbers/code/files/statements by the
owning senior agents, collects red flags, sends unresolved items back for correction,
and records the final Council decision through `glaw-chief-decision`. No matter reaches
`file` until the Chief/Council explicitly logs `chief_approved`.

## Workflow

### Step 0 — Locate or open the matter
1. Run the preamble. If `ACTIVE_MATTER: none`, ask the user what matter to open
   (name + one-line goal), then:
   ```bash
   ~/.claude/skills/glaw/bin/glaw matter new "<matter name>"
   ```
2. If a matter is active, confirm it's the one the user means. To switch:
   `glaw matter use <slug>`.

### Step 1 — Classify the matter (AskUserQuestion)
If `MATTER_TYPE: unset`, ask which track this is. Then write the answer into the
matter charter (`type:` line in `matters/<slug>/matter.md`) and set jurisdiction.

> **This is the plan-mode entry point.** The first AskUserQuestion satisfies
> plan mode; do not call ExitPlanMode here.

Options:
- **Litigation case (civil)** — assert or defend claims; produce pleadings and a trial path.
- **Corp/fund build** — form entities, structure tax, paper governance/offering.
- **Investigation (white-collar/criminal)** — uncover and prove fraud/theft; build civil + criminal exposure via `/glaw-investigations`, then feed litigation or a referral.
- **Both / hybrid** — e.g. form a holdco AND pursue a claim through it; or investigate, then sue. Sequence the tracks.

### Step 2 — Conflicts + engagement gate (HARD GATE)
Before any substantive work, invoke `/glaw-ethics-conflicts`. It runs the conflicts
check, drafts the engagement letter, and stamps the UPL disclaimer. **Do not advance
to strategy until `CONFLICTS: cleared`** (or an explicit waiver is recorded). This
mirrors a real firm: you cannot open the file until GC clears it.

The executable gate is:

```bash
~/.claude/skills/glaw/bin/glaw-ethics complete
```

That command logs `conflicts_cleared` only after conflicts, engagement, responsible reviewer, and
UPL footer state are complete.

### Step 3 — Run the pipeline
Walk the stages in order. After each stage, run `glaw stage <next>` to advance, and
`glaw timeline-log <stage>_done`. For each stage:
1. Invoke the stage skill (`/glaw-strategy`, `/glaw-structure`, ...).
2. The stage routes its sub-tasks to the seats in `lib/firm-roster.md` (delegate via
   Skill tool to existing skills, or `/glaw-*` agents).
3. Surface a one-screen summary + the open questions, then continue or stop per the user.

To run the whole review bench (strategy + structure + adversarial) without 15
intermediate prompts, offer `/glaw-autocounsel`.

### Step 4 — Adversarial gate (HARD GATE)
No matter reaches `file` until `/glaw-adversarial` has run its RED → BLUE pass and
every surviving position is verified by `/glaw-legal-research` through
`glaw-citation-gate complete`. A position that the firm's own adversary destroys, or a
position whose authority cannot be verified, does not get filed.

Record the executable adversarial gate with:

```bash
~/.claude/skills/glaw/bin/glaw-adversarial complete --profile auto
```

That command logs `adversarial_done` only after every required government/regulatory/litigation
RED-team lens for the matter profile has recorded `survive`.

Then run the Chief/Council decision. The Chief routes any red flags back to the owning
department until the agents agree on a final report/outcome:

```bash
~/.claude/skills/glaw/bin/glaw-red-flags complete
~/.claude/skills/glaw/bin/glaw-council complete --profile auto
~/.claude/skills/glaw/bin/glaw-final-packet build --profile auto
~/.claude/skills/glaw/bin/glaw-chief-decision \
  --chief "GLAW Chief Counsel" \
  --decision "PROCEED" \
  --risks "<surviving red flags or none>" \
  --conditions "<required fixes or none>" \
  --approve-final
```

Use `--deny-final` instead when the Council refuses the final entry. `--approve-final` refuses to
log `chief_approved` until the verified final packet is ready. Guarded stage transitions are
code-gated and cannot be forced; `glaw stage strategy`, `glaw stage file`, and
`glaw stage matter-retro` advance only after their owning gate commands produce the required
events and backing artifacts.

### Step 5 — File + docket
`/glaw-file` assembles the signature-ready packet and the filing checklist.
`/glaw-docket` calendars every deadline (`glaw docket add <date> <desc>`): statutes
of limitation, lien deadlines, Form D anniversaries, BOI, annual reports.

### Step 6 — Close
Before close-out, `/glaw-docket` must run `glaw-docket-gate complete` so deadlines are either
docketed or explicitly marked no-deadlines with a rationale. Then `/glaw-matter-retro` writes the
matter's Obsidian vault (per the user's universal workflow rule), logs decisions + followups, and
marks the matter status.

## Gates summary (never skip)
1. **Conflicts cleared** before strategy.
2. **Citations verified** (`glaw-citation-gate complete`) before file.
3. **Adversarial RED→BLUE** before file.
4. **Chief/Council approval** before file.
5. **UPL disclaimer** on every external deliverable (`glaw-upl-check`).
6. **Docket gate complete** before matter-retro.

## State commands
| Need | Command |
|------|---------|
| Open matter | `glaw matter new "<name>"` |
| List / switch | `glaw matter list` · `glaw matter use <slug>` |
| Advance stage | `glaw stage <stage>` |
| Add deadline | `glaw docket add <YYYY-MM-DD> "<desc>"` |
| Upcoming deadlines | `glaw docket upcoming [days]` |
| Log event | `glaw timeline-log <event>` |
