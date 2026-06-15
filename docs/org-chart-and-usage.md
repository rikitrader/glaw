# GLAW — a virtual corporate law firm

GLAW is [gstack](https://github.com/garrytan/gstack)'s skill-orchestration
methodology applied to law. gstack builds software; GLAW builds **matters** — a
litigation case or a corporate/fund structure — carrying each from intake to
filing through a bench of specialist agents, with the adversary in the room the
whole time.

It does **not** replace a lawyer. GLAW produces **attorney work-product for a
licensed attorney to review, sign, and file.** No attorney-client relationship,
no practice of law. (`/glaw-ethics-conflicts` owns that guardrail.)

## Quick start
```bash
# open a matter (the orchestrator does this for you, or run it directly)
~/.claude/skills/glaw/bin/glaw matter new "Acme Holdings Formation"
```
Then invoke `/glaw` and it drives the pipeline.

## The pipeline
```
intake → strategy → structure → draft → adversarial → file → docket → matter-retro
```
Branched at intake into **litigation**, **corp/fund build**, **investigation**,
**accounting/tax**, **contract-review**, **SEC-reporting**, or **hybrid** tracks.

| Stage | Skill |
|-------|-------|
| Matter intake | `/glaw-intake` |
| Strategy (case theory / deal thesis) | `/glaw-strategy` |
| Structure (entity + tax + cap table) | `/glaw-structure` |
| Draft (the documents) | `/glaw-draft` |
| Adversarial (RED → BLUE) | `/glaw-adversarial` |
| File (signature-ready packet) | `/glaw-file` |
| Docket (deadline calendar) | `/glaw-docket` |
| Close-out + vault | `/glaw-matter-retro` |
| Run the whole review bench | `/glaw-autocounsel` |

## The firm (org chart)
**Management:** `/glaw` (Managing Partner) · `/glaw-autocounsel` (review bench) ·
`/glaw-ethics-conflicts` (GC + UPL gate) · `/glaw-legal-research` (citation verifier) ·
`/glaw-legal-writing` (writing desk)

**Divisions** (each maps a domain to seats — see `lib/firm-roster.md` for the full table)

| Division | Lead / key seats |
|----------|------------------|
| Corporate & Transactional | `/glaw-entity-architect`, `/glaw-corporate-counsel`, `/glaw-elite-corporate-counsel`, `/glaw-ip-counsel`, `/glaw-commercial-contracts`, `/glaw-employment-counsel`, `/glaw-real-estate-counsel`, `/glaw-contract-review` |
| Securities, Funds & Capital Markets (VC/PE/SEC/Fund Mgmt) | `/glaw-pe-vc-counsel`, `/glaw-fund-regulatory-council`, `/glaw-tokenization-compliance`, `/glaw-institutional-finance`, `/glaw-sec`, `/glaw-sec-reporting` |
| Tax & IRS | `/glaw-tax-strategy`, `/glaw-tax-compliance`, `/glaw-tax-relief`, `/glaw-tax-legal-intake`, `/glaw-irs-audit`, `/glaw-tax-court`, `/glaw-back-taxes` |
| Accounting & Finance | **`/glaw-accounting`** → `/glaw-bookkeeping`, `/glaw-ledger`, `/glaw-controller`, `/glaw-cfo`, `/glaw-audit`, `/glaw-financial-forensics`, `/glaw-reconstruct`, `/glaw-roofer-accounting`, `/glaw-company-valuation`, `/glaw-mc-cfo-agent` |
| Litigation & Dispute Resolution (Civil) | `/glaw-elite-corporate-counsel`, `/glaw-federal-trial-counsel`, `/glaw-motion-drafting`, `/glaw-appellate`, `/glaw-court-records` |
| Investigations & White-Collar Crime (Criminal) | **`/glaw-investigations`** → `/glaw-forensic-case-investigator`, `/glaw-financial-forensics`, `/glaw-federal-trial-counsel`, `/glaw-bureau`, `/glaw-fincen`, `/glaw-intel` |
| Regulatory, Licensing & Compliance | `/glaw-regulatory-aml`, `/glaw-licensing`, `/glaw-privacy-data` |
| Private Client & Cross-Border | `/glaw-estate-trusts`, `/glaw-restructuring`, `/glaw-immigration`, `/glaw-international` |
| Legal Writing & Document Production | `/glaw-legal-writing`, `/glaw-copywriting`, `/glaw-copy-editing`, `/glaw-document-generate`, `/glaw-make-pdf`, `/glaw-docx`, `/glaw-fs-pptx-author`, `/glaw-fs-ppt-template-creator` |

The routing table (with a domain → seat quick index, no gaps) is `lib/firm-roster.md`.
The firm's principles are `ETHOS.md`.

## Hard gates (never skipped)
1. **Structured intake + conflicts/engagement** before strategy.
2. **Citations verified** (`glaw-citation-gate complete`) before file.
3. **Adversarial RED→BLUE** (`glaw-adversarial complete --profile auto`) before file.
4. **Red flags clear** before file.
5. **Final packet ready** before file.
6. **Chief/Council approval** before file.
7. **UPL disclaimer** on every external deliverable.
8. **Docket gate complete** before matter-retro.

## State
Lives under `~/.glaw/` (override with `$GLAW_HOME`): `config.yaml`,
`matters/<slug>/` (`matter.md`, `docket.jsonl`, `timeline.jsonl`, `.stage`),
`.active`. Driven by `bin/glaw` — run `glaw help` for the command list.
