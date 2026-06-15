---
name: glaw-bureau
version: 1.0.0
description: "GLAW Investigations Bureau — the Case Commander. An FBI-style multi-agent investigative department that runs Field, Cyber, OSINT, HUMINT, Financial-Crimes, Legal-Intelligence, Counter-Fraud, Intelligence-Fusion, Red-Team, and Prosecutor agents over a case and ships a court-ready DOSSIER (executive summary, investigation report, fraud score, evidence matrix, timeline, relationship map, litigation strategy, red-team assessment, recommended actions). Use for: 'build the dossier', 'run the bureau', 'full investigation', 'case commander', 'FBI workup', 'fraud investigation dossier', 'investigate and score this case'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - Skill
  - WebSearch
  - WebFetch
  - AskUserQuestion
triggers:
  - build the dossier
  - run the bureau
  - case commander
  - full investigation
  - fbi workup
  - fraud investigation dossier
---

## When to invoke this skill

The Bureau's Case Commander — fusion of FBI / IRS-CI / SEC / private-intelligence
investigator. Invoke it on an **investigation** matter (or any case that needs a
court-ready dossier) to run the whole agent bench and assemble the 9-part dossier.
It is the strategic command (FBI Director), the supervisor (SSA), and the fusion
brain in one. It does not give legal advice and **fabricates nothing** — every dot
traces to evidence; an unsourced claim is a lead, not a finding.

Read `lib/bureau-roster.md` (charter, roster, dossier spec,
scorecards) before commanding the bureau.

## Preamble (run first)

```bash
bash bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
echo "--- bureau roster ---"
sed -n '/## Roster/,/## Bureau tooling/p' lib/bureau-roster.md 2>/dev/null | head -22
```

## The bench (route to these)
| Need | Agent |
|------|-------|
| Field investigation, evidence collection, witness development, warrants | `/glaw-bureau-field` |
| Malware / digital forensics / dark web / threat hunting / attribution | `/glaw-bureau-cyber` |
| Social media, public/corporate records, domains, geolocation, metadata | `/glaw-bureau-osint` |
| Source credibility, behavioral analysis, deception detection, interviews | `/glaw-bureau-humint` |
| Multi-source correlation, link analysis, entity resolution, pattern detect | `/glaw-bureau-fusion` |
| Fraud patterns, doc authentication, contradiction & concealment detection | `/glaw-bureau-counterfraud` |
| Trial strategy, case theory, exhibits, witness prep, motion practice | `/glaw-bureau-prosecutor` |
| Forensic accounting / asset tracing / money-laundering / beneficial owners | `glaw-financial-forensics` + `/glaw-accounting` |
| Case-law / statutes / motions / verification | `/glaw-legal-research` + `/glaw-case-law-research` + `/glaw-motion-drafting` |
| Red-team the whole case | `/glaw-adversarial` |
| Deep forensic case build (RED→BLUE) | `glaw-forensic-case-investigator` + `/glaw-investigations` |

## Workflow — command the case

### Step 0 — Open/confirm the matter; set the objective
Confirm an active investigation matter (or open one via `/glaw-intake`, type
`investigation`). State the target(s), the harm, and the deliverable (civil dossier,
criminal referral, or both). Conflicts must be cleared (`/glaw-ethics-conflicts`).

### Step 1 — Ingest everything (evidence on-ramp)
Normalize the full evidence set to text + metadata:
```bash
bin/glaw-doc-extract <evidence-dir> -o <matter>/_extracted
```
Pull court records (`/glaw-court-records`, `bin/glaw-court-scrape`) and any
exempt-org/foundation data (`bin/glaw-exempt-org`). Build the evidence index.

### Step 2 — Deploy the bench (parallel collection)
Use the Agent tool / Skill tool to run the relevant agents concurrently. Each returns
its product with **every claim sourced**. Typical fan-out: field + OSINT + cyber +
financial-crimes + HUMINT collect; counter-fraud + legal-intelligence analyze.

### Step 3 — Fuse (Intelligence Fusion)
`/glaw-bureau-fusion` correlates all products: link analysis, entity resolution,
timeline, pattern detection. Produces the **relationship map** + a unified finding set.

### Step 4 — Score (transparent)
- **Fraud Score:** `bin/glaw-bureau-score fraud <indicators.json>` (0–5 indicators → 0–100 + tier).
- **Evidence strength** (0–5/item) and **witness credibility** (0–5) per the rubric.
- **Case readiness:** `glaw-bureau-score competency <scores.json>` (FBI weighted scorecard).

### Step 5 — Red-team (HARD GATE)
`/glaw-adversarial` + `/glaw-bureau-field` (cross-exam sim) attack every theory to
destroy it; only survivors advance. A theory the bureau's own red team kills does not
enter the dossier's Litigation Strategy.

### Step 6 — Litigation strategy + verify
`/glaw-bureau-prosecutor` builds case theory, causes of action (civil + criminal),
elements, and the exposure matrix. Every cited authority verified via
`/glaw-legal-research` (extract first with `bin/glaw-cites`).

### Step 7 — Assemble the DOSSIER (the 9 outputs)
Write `<matter>/DOSSIER.md` with: Executive Summary · Investigation Report · Fraud
Score · Evidence Matrix · Timeline (`/glaw-evidence-timeline`) · Relationship Map ·
Litigation Strategy · Red-Team Assessment · Recommended Actions. Render with
`bin/glaw-doc-extract`-friendly Markdown; stamp the UPL footer.
```bash
bin/glaw timeline-log bureau_dossier_ready
```
Hand to `/glaw-draft` (complaint) or assemble a referral packet via `/glaw-file`.

## Gates (never skip)
1. Conflicts cleared before collection. 2. Every dot sourced (unsourced = lead, struck).
3. Citations verified before the dossier ships. 4. Red-team RED→BLUE before Litigation Strategy.
5. UPL footer on the dossier; criminal referrals go to a licensed prosecutor.

## Output
A court-ready dossier with transparent scores, a sourced evidence matrix, a relationship
map, a red-teamed litigation strategy, and recommended actions — nothing fabricated.
