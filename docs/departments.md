# GLAW Departments — full seat reference

GLAW ships as **one self-contained app**. Current doctor coverage verifies **179 source
`SKILL.md` files**, **63 vendored seats**, and top-level `/glaw-*` command parity after
`bin/glaw-setup`. The single source of truth for routing is
[`../lib/firm-roster.md`](../lib/firm-roster.md); this page is the human-readable index.
All seats listed below are bundled in this repo or implemented by repo-local `bin/glaw-*`
tools.

## The matter pipeline (8 stages)
| Stage | Skill | Produces |
|---|---|---|
| Intake | `/glaw-intake` | matter charter, track classification, routing |
| Strategy | `/glaw-strategy` | case theory · deal thesis · theory of wrongdoing |
| Structure | `/glaw-structure` | parties map · entity org chart + tax + cap table · flow-of-funds |
| Draft | `/glaw-draft` | the documents |
| Adversarial | `/glaw-adversarial` | RED→BLUE red-team + survival score (hard gate) |
| File | `/glaw-file` | signature-ready packet + filing checklist |
| Docket | `/glaw-docket` | deadline calendar |
| Close | `/glaw-matter-retro` | matter close-out + retrospective |

## Firm Management & Review Bench
| Seat | Skill |
|---|---|
| Managing Partner / orchestrator | `/glaw` |
| Review bench (strategy+structure+adversarial back-to-back) | `/glaw-autocounsel` |
| General Counsel — conflicts, engagement, UPL gate | `/glaw-ethics-conflicts` |
| Legal Research — citation verification (anti-hallucination) | `/glaw-legal-research` |
| Chief Compliance Officer — final compliance manifest + file-readiness exceptions | `/glaw-compliance` |
| Writing desk — drafting style, brief/memo polish, Bluebook | `/glaw-legal-writing` |

## Corporate & Transactional
`/glaw-entity-architect` · `/glaw-ip-counsel` · `/glaw-commercial-contracts` ·
`/glaw-employment-counsel` · `/glaw-real-estate-counsel` · `/glaw-corporate-counsel` ·
`/glaw-elite-corporate-counsel` · `/glaw-contract-review`.

## Securities, Funds & Capital Markets
`/glaw-sec` (lead) · `/glaw-sec-disclosure` · `/glaw-sec-adviser` · `/glaw-sec-insider` ·
`/glaw-sec-marketabuse` · `/glaw-sec-enforcement` · `/glaw-pe-vc-counsel` ·
`/glaw-fund-regulatory-council` · `/glaw-tokenization-compliance` ·
`/glaw-institutional-finance`.

## Accounting & Finance
`/glaw-accounting` (lead) · `/glaw-audit-assurance` · `/glaw-bookkeeping` ·
`/glaw-ledger` · `/glaw-controller` · `/glaw-cfo` · `/glaw-audit` ·
`/glaw-reconstruct` · `/glaw-financial-forensics` · `/glaw-roofer-accounting` ·
`/glaw-company-valuation` · `/glaw-mc-cfo-agent`.

## Litigation & Dispute Resolution
`/glaw-motion-drafting` · `/glaw-case-law-research` · `/glaw-evidence-timeline` ·
`/glaw-veil-piercing` · `/glaw-court-records` · `/glaw-federal-trial-counsel` ·
`/glaw-forensic-case-investigator`.

## Investigations Bureau (white-collar)
`/glaw-investigations` (lead) · `/glaw-bureau` (case commander) ·
`/glaw-bureau-counterfraud` · `/glaw-bureau-osint` · `/glaw-bureau-humint` ·
`/glaw-bureau-field` · `/glaw-bureau-cyber` · `/glaw-bureau-fusion` ·
`/glaw-bureau-prosecutor`
Charter + scoring spec: [`../lib/bureau-roster.md`](../lib/bureau-roster.md).

## Intelligence Super-Structure
**Master fusion:** `/glaw-command` (triage → briefing → red-flag gate → DOSSIER).
**FinCEN cell:** `/glaw-fincen` · `/glaw-fincen-aml` · `/glaw-fincen-sar` ·
`/glaw-fincen-ofac` · `/glaw-fincen-tbml` · `/glaw-fincen-crypto`.
**Analysis cell:** `/glaw-intel` · `/glaw-intel-analyst` · `/glaw-intel-geopolitical` ·
`/glaw-intel-scitech` · `/glaw-intel-counterintel`.

> Lawful-analysis guardrail: all bureau/intel seats are analytical/advisory work-product.
> No covert ops, surveillance, intrusion, or illegal collection — those require licensed
> investigators or law enforcement.

## Regulatory & Licensing
`/glaw-licensing` · `/glaw-regulatory-aml` · `/glaw-immigration` · `/glaw-privacy-data`

## Private Client & Restructuring
`/glaw-estate-trusts` · `/glaw-restructuring` · `/glaw-international`

## Tax & IRS
Tax work is driven by tools (`glaw-tax-report`, `glaw-irs-file`, `glaw-compliance-audit`)
plus bundled seats `/glaw-tax-strategy`, `/glaw-tax-compliance`, `/glaw-tax-relief`,
`/glaw-tax-legal-intake`, `/glaw-irs-audit`, `/glaw-back-taxes`, `/glaw-tax-court`,
`/glaw-international-tax`, `/glaw-estate-gift-returns`, `/glaw-exempt-org`, and
`/glaw-irs-whistleblower`.
See [`tools.md`](tools.md).
