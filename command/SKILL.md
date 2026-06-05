---
name: glaw-command
version: 1.0.0
description: "GLAW Master Command — the top-level intelligence-fusion orchestrator. Coordinates the FBI bureau, FinCEN financial-intelligence cell, CIA strategic-intelligence cell, SEC enforcement cell, IRS-CI/forensic-accounting, the lawyer seats, and the adversarial red-team over a case. ALWAYS produces an executive briefing; escalates to a full court-ready DOSSIER only when RED FLAGS surface. Use for: 'run the command', 'full intelligence workup', 'master fusion', 'investigate and brief', 'red-flag this case', 'should this be a dossier', 'fraud + financial-crime + securities workup', 'build the case file'."
allowed-tools: [Bash, Read, Write, Edit, Grep, Glob, Agent, Skill, WebSearch, WebFetch, AskUserQuestion]
triggers:
  - run the command
  - full intelligence workup
  - master fusion
  - investigate and brief
  - red-flag this case
  - build the case file
---

## When to invoke this skill

The Master Command — the Skynet-level fusion of every GLAW investigative capability.
Invoke it to put a person/entity/transaction set through the whole intelligence
apparatus. It runs a **triage**, always returns a **briefing**, and escalates to a
**full dossier only if red flags clear the threshold** — so cheap cases stay cheap and
real cases get the full workup. It fabricates nothing; every dot traces to evidence.

Read `~/.claude/skills/glaw/lib/bureau-roster.md` (charter, dossier spec, scorecards).

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- bureaus on call ---"; echo "FBI:/glaw-bureau  FinCEN:/glaw-fincen  CIA:/glaw-intel  SEC:/glaw-sec  IRS-CI:financial-forensics  RedTeam:/glaw-adversarial"
```

## The bureaus (route by question)
| Domain | Bureau / lead |
|--------|---------------|
| Criminal / field / fraud case-building | `/glaw-bureau` (FBI Case Commander) |
| Financial crime / AML / sanctions / crypto / asset tracing | `/glaw-fincen` (CFIO) |
| Strategic / country-risk / counter-intel / tech | `/glaw-intel` (Director) |
| Securities enforcement / disclosure / market abuse / insider | `/glaw-sec` (Chief Enforcement) |
| Tax / IRS-CI forensic numbers | `financial-forensics` + `tax-strategy` + `tax-compliance` |
| Legal exposure / causes of action / motions | `/glaw-legal-research` + `/glaw-motion-drafting` + `elite-corporate-counsel` |
| Red-team everything | `/glaw-adversarial` |
| Fuse everything | `/glaw-bureau-fusion` |

## Universal engines (run as needed)
Entity Resolution · Relationship Discovery · Timeline Reconstruction (`/glaw-evidence-timeline`) ·
Fraud Detection (`glaw-bureau-score fraud`) · AML Risk · Intelligence Fusion (`/glaw-bureau-fusion`) ·
Adversarial Testing (`/glaw-adversarial`) · Predictive Risk · Evidence Validation (source every dot) ·
Executive Reporting.

## Workflow — triage, brief, and gate the dossier

### Step 0 — Scope + conflicts
Confirm the matter + target(s) + objective. Conflicts cleared (`/glaw-ethics-conflicts`).

### Step 1 — Ingest + entity resolution
`bin/glaw-doc-extract <evidence-dir>`; pull court records, exempt-org, corporate records.
Resolve entities/persons/accounts to a single roster.

### Step 2 — TRIAGE sweep (cheap, parallel)
Run a fast pass across the relevant bureaus (FBI/FinCEN/CIA/SEC/IRS) to surface
**red-flag indicators**: badges of fraud, money-flow anomalies, sanctions/SDN hits,
shell/straw entities, disclosure/securities issues, document contradictions, concealment,
timeline proximity to harm. Score them: `bin/glaw-bureau-score fraud <indicators.json>`.

### Step 3 — THE RED-FLAG GATE (the rule)
- **No red flags** (Fraud Score < 25 / tier LOW, no sanctions/securities hit): **STOP at a BRIEFING.** Produce the Executive Briefing + the cleared-issues list + scorecards. Done.
- **Red flags present** (tier MODERATE+ or any sanctions/securities/criminal hit): **ESCALATE to a full DOSSIER** — deploy the owning bureau(s) deep, then assemble the 9-part dossier.

### Step 4 — Deep deployment (only if escalated)
Task the owning bureau leads in parallel; each returns sourced product. Fuse via
`/glaw-bureau-fusion` → relationship map + unified findings.

### Step 5 — ADVERSARIAL on every issue (HARD GATE)
`/glaw-adversarial` attacks every theory, score, and red flag to destroy it; only
survivors advance. Advise adversarially on ALL issues — confidence/fraud scores are
re-rated after the red team. A theory the firm's own red team kills is struck.

### Step 6 — Score everything
- Fraud Score + AML risk (`glaw-bureau-score fraud`).
- Case readiness / each bureau's product (`glaw-bureau-score competency`).
- Evidence strength (0–5/item) + witness credibility (0–5).

### Step 7 — Deliverables
- **Always:** Executive (Intelligence) Brief + Scorecards + Adversarial Findings.
- **If escalated (red flags):** the full DOSSIER → write `<matter>/DOSSIER.md`:
  Executive Summary · Financial Crime Assessment · Asset Trace · Relationship Map ·
  Timeline · Risk Matrix · Fraud Indicators · Litigation Support Package ·
  Adversarial Findings · Strategic Recommendations. Stamp the UPL footer.
```bash
~/.claude/skills/glaw/bin/glaw timeline-log command_complete '"escalated":true_or_false,"fraud_tier":"..."'
```
Hand to `/glaw-draft` (complaint), `/glaw-file` (referral packet), or `/glaw-strategy`.

## Gates (never skip)
1. Conflicts cleared. 2. Every dot sourced (unsourced = lead, struck). 3. Adversarial RED→BLUE on every issue before the dossier. 4. Citations verified (`/glaw-legal-research`). 5. UPL footer; criminal/securities referrals go to licensed counsel. 6. No fabricated evidence, charges, or scores.

## Output
A briefing for every case; a court-ready dossier for every case with red flags — both
transparently scored, adversarially tested, and fully sourced.
