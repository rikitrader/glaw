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
Branched at intake into **litigation case** vs **corp/fund build**.

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
| Corporate & Transactional | `/glaw-entity-architect`, `corporate-counsel`, `elite-corporate-counsel`, `/glaw-ip-counsel`, `/glaw-commercial-contracts`, `/glaw-employment-counsel`, `/glaw-real-estate-counsel` |
| Securities, Funds & Capital Markets (VC/PE/SEC/Fund Mgmt) | `pe-vc-counsel`, `fund-regulatory-council`, `tokenization-compliance`, `institutional-finance` |
| Tax & IRS | `tax-strategy`, `tax-compliance`, `tax-relief`, `tax-legal-intake` |
| Accounting & Finance | **`/glaw-accounting`** → `financial-forensics`, `/glaw-audit-assurance`, `institutional-finance`, `roofer-accounting`, `company-valuation`, `mc-cfo-agent` |
| Litigation & Dispute Resolution (Civil) | `elite-corporate-counsel`, `federal-trial-counsel` |
| Investigations & White-Collar Crime (Criminal) | **`/glaw-investigations`** → `forensic-case-investigator`, `financial-forensics`, `federal-trial-counsel` |
| Regulatory, Licensing & Compliance | `/glaw-regulatory-aml`, `/glaw-licensing`, `/glaw-privacy-data` |
| Private Client & Cross-Border | `/glaw-estate-trusts`, `/glaw-restructuring`, `/glaw-immigration`, `/glaw-international` |
| Legal Writing & Document Production | `/glaw-legal-writing`, `copywriting`, `copy-editing`, `make-pdf`, `docx` |

The routing table (with a domain → seat quick index, no gaps) is `lib/firm-roster.md`.
The firm's principles are `ETHOS.md`.

## Hard gates (never skipped)
1. **Conflicts cleared** before strategy.
2. **Citations verified** (`/glaw-legal-research`) before file.
3. **Adversarial RED→BLUE** before file.
4. **UPL disclaimer** on every external deliverable.

## State
Lives under `~/.glaw/` (override with `$GLAW_HOME`): `config.yaml`,
`matters/<slug>/` (`matter.md`, `docket.jsonl`, `timeline.jsonl`, `.stage`),
`.active`. Driven by `bin/glaw` — run `glaw help` for the command list.
