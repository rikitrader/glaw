# GLAW Investigations Bureau — charter, roster, dossier spec

An FBI-style investigative department inside GLAW. The **Case Commander**
(`/glaw-bureau`) runs the bureau, fuses every agent's product, and ships a
court-ready **dossier**. Plugs into the **investigation** matter track and feeds
litigation (`/glaw-strategy` → `/glaw-draft`/`/glaw-motion-drafting` → `/glaw-file`).

> Investigative work-product, not legal advice and not a charging decision.
> Criminal referrals are for a licensed prosecutor. UPL guardrail: `/glaw-ethics-conflicts`.

## Roster — 14 roles → seats (new bureau seats + mapped existing seats)
| Role | Seat | Status |
|------|------|--------|
| FBI Director (Strategic Command) | `/glaw-bureau` (Case Commander assumes this) | orchestrator |
| Supervisory Special Agent (SSA) | `/glaw-bureau` (supervisory layer) | orchestrator |
| Master AI Agent (Case Commander) | `/glaw-bureau` | orchestrator |
| Special Agent (Field Investigator) | `/glaw-bureau-field` | NEW |
| Cyber Intelligence Agent | `/glaw-bureau-cyber` | NEW |
| Open-Source Intelligence (OSINT) Agent | `/glaw-bureau-osint` | NEW |
| Human Intelligence (HUMINT) Agent | `/glaw-bureau-humint` | NEW |
| Intelligence Fusion Agent | `/glaw-bureau-fusion` | NEW |
| Counter-Fraud Agent | `/glaw-bureau-counterfraud` | NEW |
| Prosecutor Agent | `/glaw-bureau-prosecutor` | NEW |
| Financial Crimes Agent (Forensic Accountant) | `financial-forensics` + `/glaw-accounting` | mapped |
| Legal Intelligence Agent | `/glaw-legal-research` + `/glaw-case-law-research` + `/glaw-motion-drafting` | mapped |
| Adversarial Agent (Red Team) | `/glaw-adversarial` (+ `/glaw-bureau-field` cross-exam sim) | mapped |
| (forensic case build) | `forensic-case-investigator`, `/glaw-investigations` | mapped |

## Bureau tooling (already built — the agents use these)
- Ingest any evidence: `bin/glaw-doc-extract` (Tika/opendataloader + OCR + metadata)
- Court records: `bin/glaw-court-scrape` (zero-dependency court handoff) + `/glaw-court-records` (CourtListener)
- Citations: `bin/glaw-cites` (stdlib citation extractor)
- Exempt-org/foundation diligence: `bin/glaw-exempt-org`
- Chronology: `/glaw-evidence-timeline`
- Competency/score: `bin/glaw-bureau-score`

## Dossier — the 9 outputs (Case Commander assembles)
1. **Executive Summary** — what happened, who, the ask, the bottom line.
2. **Investigation Report** — narrative + methodology + sources.
3. **Fraud Score** — 0–100 (see scoring below) + driver flags.
4. **Evidence Matrix** — each fact → source doc → strength (0–5) → what it proves.
5. **Timeline** — source-cited chronology (`/glaw-evidence-timeline`).
6. **Relationship Map** — entities/persons/accounts + edges (control, money, comms).
7. **Litigation Strategy** — causes of action (civil + criminal), elements, exposure matrix.
8. **Red-Team Assessment** — `/glaw-adversarial` attacks every theory → survivors only.
9. **Recommended Actions** — next steps, evidence still needed, referral vs file.

## Scoring (transparent, documented — never a black box)
- **Fraud Score (0–100):** weighted indicators — badges of fraud present, money-flow anomalies, shell/straw entities, document contradictions, concealment, timeline proximity to harm. Each scored 0–5, normalized, weighted. Show the components.
- **Evidence strength (0–5 per item):** 5 = authenticated primary doc; 3 = corroborated secondary; 1 = uncorroborated assertion/lead. A 0–1 item is a lead, not a fact.
- **Witness credibility (0–5):** consistency, corroboration, bias, deception indicators (`/glaw-bureau-humint`).

## FBI Core Competencies Scorecard (weights — sum 100%)
Applied by the Case Commander to score case readiness / each agent's product.
| Competency | Weight |
|-----------|--------|
| Communication | 15% |
| Leadership | 15% |
| Organizing & Planning | 15% |
| Problem Solving / Judgment | 15% |
| Collaboration | 10% |
| Flexibility / Adaptability | 10% |
| Initiative | 10% |
| Interpersonal Ability | 10% |
Compute with `bin/glaw-bureau-score competency <scores.json>` → weighted total + tier
(0–59 NOT READY · 60–74 DEVELOPING · 75–89 READY · 90–100 EXEMPLARY).

## Hard rules
- Every dot traces to evidence. A claim with no source is a lead, struck from the dossier.
- Every cited statute/case verified via `/glaw-legal-research` before the dossier ships.
- Red-Team (`/glaw-adversarial`) runs before any theory enters Litigation Strategy.
- No fabricated evidence, charges, or scores. Ever.
