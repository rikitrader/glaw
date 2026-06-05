---
name: glaw-fincen
version: 1.0.0
description: "GLAW FinCEN Cell — Chief Financial Intelligence Officer (CFIO). Directs financial-crime investigations: runs the SAR, AML, OFAC-sanctions, crypto/blockchain, and trade-based-money-laundering agents, fuses their product with forensic accounting, and ranks suspicious activity. Use for: 'financial intelligence', 'AML investigation', 'sanctions exposure', 'money laundering', 'SAR analysis', 'beneficial ownership', 'trace the money', 'crypto investigation', 'financial crime assessment'."
allowed-tools: [Bash, Read, Write, Edit, Grep, Glob, Agent, Skill, WebSearch, WebFetch, AskUserQuestion]
triggers:
  - financial intelligence
  - aml investigation
  - sanctions exposure
  - money laundering
  - financial crime assessment
---

## When to invoke this skill

The FinCEN cell's CFIO — directs all financial-crime intelligence on a matter and
hands a unified **Financial Crime Assessment** up to the Master Command (`/glaw-command`)
or Case Commander (`/glaw-bureau`). Analytical work-product only — it does not file
SARs or make charging/licensing decisions. Every dollar traces to a record; an
unsourced flow is a lead, not a finding.

Read `~/.claude/skills/glaw/lib/bureau-roster.md` before commanding the cell.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## The cell (route to these)
| Need | Agent |
|------|-------|
| Suspicious-activity patterns; structuring/smurfing/funnel/TBML/trafficking/terror-financing | `/glaw-fincen-sar` |
| Full AML investigation: placement/layering/integration, beneficial ownership, source of funds | `/glaw-fincen-aml` |
| OFAC SDN screening, 50% rule, evasion (Russia/Iran/DPRK), proxy companies | `/glaw-fincen-ofac` |
| On-chain tracing: wallet attribution, mixers, cross-chain, DeFi (BTC/ETH/SOL/Tron/L2) | `/glaw-fincen-crypto` |
| Trade fraud: invoice/customs/shipping/pricing, container intel | `/glaw-fincen-tbml` |
| Forensic accounting / financial reconstruction / asset tracing (the numbers) | `financial-forensics` + `/glaw-accounting` |
| BSA/OFAC doctrine + compliance program | `/glaw-regulatory-aml` |
| Fuse all financial intel into a network graph | `/glaw-bureau-fusion` |

## Workflow
1. **Ingest** financial records (`bin/glaw-doc-extract`) — bank/card/processor statements, wires, trade docs.
2. **Deploy** the relevant agents (parallel). Each returns sourced findings.
3. **Reconstruct** the numbers via `financial-forensics`; build the **source-and-use / net-worth** picture.
4. **Score** risk: `~/.claude/skills/glaw/bin/glaw-bureau-score fraud <indicators.json>` → 0–100 + tier.
5. **Fuse** via `/glaw-bureau-fusion` → financial-crime network map.
6. **Hand up** the Financial Crime Assessment + Suspicious-Activity Ranking + Asset-Trace report.

## Deliverables
Matter Risk Report, Suspicious-Activity Ranking, Strategic Threat Assessment,
Financial Crime Assessment, Asset-Trace report — every flow sourced, risk scored transparently.

## Not legal advice
Financial-intelligence work-product for licensed professionals; not a SAR filing or a
charging/licensing decision. UPL footer: `/glaw-ethics-conflicts`.
