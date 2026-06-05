---
name: glaw-file
version: 1.0.0
description: "GLAW pipeline stage 6 — assembles the signature-ready FILING PACKET and a filing checklist. Corp-build: Secretary-of-State formation, EIN/SS-4, EDGAR Form D, IARD Form ADV, Blue Sky state notices, FinCEN BOI, 83(b) elections. Litigation: court e-filing packet (complaint, civil cover sheet, summons, service list, exhibits index). For each filing it states where, how, the fee, and the deadline. Use for: 'assemble the filing', 'prepare the packet', 'what do I file and where', 'filing checklist', 'ready to file', after adversarial review passes."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Skill
triggers:
  - assemble the filing
  - filing packet
  - filing checklist
  - ready to file
  - what do I file
---

## When to invoke this skill

Stage 6 of the GLAW pipeline. It turns approved work-product into a
**signature-ready packet** a licensed attorney can review, sign, and file — plus
the checklist that says exactly where each piece goes, how it's submitted, what
it costs, and when it's due. File does not draft new legal positions; it
assembles and routes the ones that already cleared the gates.

## Preamble (run first)

```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || bash .claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

Read `~/.claude/skills/glaw/lib/firm-roster.md` before routing.

## Workflow

### Step 0 — HARD PRE-CHECK (refuse otherwise)
Do not assemble until both are true in the matter timeline/charter:
1. Every citation verified by **`/glaw-legal-research`**.
2. **`/glaw-adversarial`** ran a clean RED→BLUE pass (no surviving fatal attack).

If either is missing, stop and route back. The firm does not file unverified or
un-adversaried work-product.

### Step 1 — Build the filing manifest by track

**Corp-build** — assemble each applicable filing as its own line item:
| Filing | Where | How | Fee (verify) | Deadline |
|--------|-------|-----|--------------|----------|
| Formation (Articles/Cert.) | State Secretary of State | SOS portal / registered agent | state-specific | at formation |
| EIN (SS-4) | IRS | online EIN / fax SS-4 | $0 | before banking/payroll |
| Form D | SEC EDGAR | EDGAR filer (needs CIK/CCC) | $0 | 15 days after first sale |
| Form ADV | IARD | IARD portal | IARD fee | before holding out as adviser |
| Blue Sky notices | each investor's home state | state notice + fee | per state | per state (often w/ Form D) |
| FinCEN BOI | FinCEN BOIR | BOI e-filing | $0 | per current CTA timing — verify |
| 83(b) election | IRS service center | mail, certified | $0 | **30 days** from grant (hard) |

Route the securities/fund filings to **`fund-regulatory-council`** for the actual
form fill (Form D, ADV, Blue Sky, custodian/auditor letters). Confirm each fee and
deadline against current rule before stating it — do not rely on memory.

**Litigation** — assemble the court e-filing packet:
- Complaint (final, post-adversarial), **civil cover sheet**, **summons** per defendant, **service list**, **exhibits index** + exhibits, proposed order(s), any required certificates (e.g. interested-parties, pre-suit notice).
- For each: court (which division/county/federal district), e-filing system (e.g. state e-portal / PACER-CM/ECF), filing fee, and the controlling deadline (SOL, response window).

### Step 2 — Docket every deadline now
For each filing line, calendar it immediately so nothing relies on memory:
```bash
~/.claude/skills/glaw/bin/glaw docket add <YYYY-MM-DD> "<filing> due — <where>"
```

### Step 3 — Render the packet
Route document production to **`make-pdf`** (and `docx`/`document-generate` as
needed) to produce clean, signature-ready PDFs with signature blocks, exhibit
tabs, and a cover checklist. Every external doc carries the UPL footer from
`/glaw-ethics-conflicts`.

### Step 4 — Filing checklist (the cover page)
Produce a one-page checklist: each filing, where it's filed, how, the fee, the
deadline, who signs, and what must be attached. This is what the signing attorney
works from.

### Step 5 — Advance
```bash
~/.claude/skills/glaw/bin/glaw stage docket
~/.claude/skills/glaw/bin/glaw timeline-log file_done
```
Hand off to `/glaw-docket` for ongoing calendaring/monitoring.

## Output
A **FILING PACKET** (signature-ready PDFs, UPL-footed) plus a **filing checklist**
naming for each filing: where, how, fee, deadline, signer, and attachments. All
deadlines docketed. No new legal positions introduced — only assembly of cleared
work-product.
