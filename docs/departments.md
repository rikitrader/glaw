# GLAW Departments — full seat reference

GLAW ships **59 native skills**, deployed by `bin/glaw-setup` as top-level `/glaw-*`
commands. The single source of truth for routing is [`../lib/firm-roster.md`](../lib/firm-roster.md);
this page is the human-readable index. Seats marked *(external)* are optional companion
skills GLAW routes to if installed — they are **not** bundled.

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
| Writing desk — drafting style, brief/memo polish, Bluebook | `/glaw-legal-writing` |

## Corporate & Transactional
`/glaw-entity-architect` · `/glaw-ip-counsel` · `/glaw-commercial-contracts` ·
`/glaw-employment-counsel` · `/glaw-real-estate-counsel`
*External companions:* `corporate-counsel`, `elite-corporate-counsel`, `contract-review`.

## Securities, Funds & Capital Markets
`/glaw-sec` (lead) · `/glaw-sec-disclosure` · `/glaw-sec-adviser` · `/glaw-sec-insider` ·
`/glaw-sec-marketabuse` · `/glaw-sec-enforcement`
*External companions:* `pe-vc-counsel`, `fund-regulatory-council`, `tokenization-compliance`, `institutional-finance`.

## Accounting & Finance
`/glaw-accounting` (lead) · `/glaw-audit-assurance`
*External companions:* `financial-forensics`, `roofer-accounting`, `company-valuation`, `mc-cfo-agent`.

## Litigation & Dispute Resolution
`/glaw-motion-drafting` · `/glaw-case-law-research` · `/glaw-evidence-timeline` ·
`/glaw-veil-piercing` · `/glaw-court-records`
*External companions:* `federal-trial-counsel`, `forensic-case-investigator`.

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
plus external companions `tax-strategy`, `tax-compliance`, `tax-relief`, `tax-legal-intake`.
See [`tools.md`](tools.md).
