---
name: glaw-forms
version: 1.0.0
description: GLAW forms library + fill-engine. Picks the right SEC-derived master template (stock option, equity incentive plan, RSU, SAFE, convertible note, priced-round), fills it for a specific corp from the Carta cap table, renders it in the enforced house style, and (optionally) runs the consensus/valuation gate. Use for 'draft an option grant', 'we need a SAFE', 'convertible note', 'RSU agreement', 'equity plan', 'fill the grant set', 'generate the cap-table grants', 'forms library'.
allowed-tools: Read, Bash, Glob, Grep, Agent
triggers: [forms library, draft a SAFE, convertible note, option grant, RSU agreement, equity plan, fill the grants, generate grants, cap table grants]
---

# GLAW — Forms Library & Fill-Engine

Routes any equity/financing form request to the right master, fills it for the corp, and publishes it in the
enforced house style. Every master is recreated 100% from a current SEC filing (see `forms-library/manifest.json`).

## Library (masters at `~/.claude/skills/glaw/lib/forms-library/`)
| Need | Master | Source |
|------|--------|--------|
| Grant options (ISO/NSO) | `glaw-stock-option-agreement-master.md` | Reddit 2024 |
| Omnibus equity plan | `glaw-equity-incentive-plan-master.md` | Meta 2025 |
| RSUs (double-trigger) | `glaw-rsu-award-agreement-master.md` | Heritage 2019 |
| Take a pre-priced check | `glaw-safe-master.md` (YC post-money) · `glaw-convertible-note-master.md` | YC / market |
| Priced round | (priced-round set — add per matter) | NVCA |

## Workflow
1. Emit the GLAW preamble; confirm the corp + which form.
2. **Fill** from the cap table:
   ```bash
   python3 ~/.claude/skills/glaw/bin/matter-ops/fill_from_captable.py <master.md> \
     --company "Example Holdings, Inc." --year 2024 --state Delaware --strike "[APPRAISED FMV]" --sheet <captableSheetId> --out <out.md>
   ```
   (option/RSU masters auto-append a grant schedule from the EMPLOYEE rows.)
3. **House style + publish** (always — enforced):
   ```bash
   python3 ~/.claude/skills/glaw/bin/matter-ops/publish_legal.py <out.md> --folder <driveFolderId> --name "Title"
   ```
4. **Gate (when it's an issuance/financing position):** route to `/glaw-consensus` (panel + IRS/SEC veto) and, for
   options/RSUs, `/glaw-valuation-409a` (strike ≥ appraised FMV; HELD IN ESCROW until the 409A is signed).
5. Record any new defect to `glaw-learnings`.

## Rules (enforced)
- Every output renders in the **us-law-firm house style** (`feedback_glaw_document_house_style`): full clauses,
  100% [BRACKET] template + a filled corp version, TNR/justified/0.5" indent.
- Options/RSUs: **never grant below the appraised §409A FMV**; grants HELD IN ESCROW until the 409A is signed.
- SAFE/Note: confirm the securities exemption (Reg D/§4(a)(2)) + accredited investors; usury savings on notes.
- UPL footer; a licensed attorney must review, sign, and file.

> ATTORNEY WORK-PRODUCT. Masters are recreated from public SEC filings; confirm against the current source form. Not legal advice.
