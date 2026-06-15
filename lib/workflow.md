# GLAW End-to-End Workflow — the connected firm

How a **matter** flows through the firm, and exactly which skills fire at each stage. The
orchestrator (`/glaw`) holds the gates; each stage routes work to the seats in `firm-roster.md`,
which delegate to the connected skills below. **Advice/drafting stays in the legal seats; numbers/
models go to `fs-*`; research goes through `deep-research`→verify; figures come from
`tax-legal-shared/current-figures.md`; ethics floor is `tax-legal-shared/guardrails.md`.**

## The pipeline (every stage, every connected skill)

```
INTAKE  /glaw-intake
  └─ form: `intake.json` via `bin/glaw-intake` (required before strategy)
  └─ GATE: /glaw-ethics-conflicts → `glaw-ethics complete`
     (conflicts + engagement letter + UPL state)                           ← hard gate #1
  └─ tax/legal triage → tax-legal-intake (sequences tax/corp/relief work)

STRATEGY  /glaw-strategy
  ├─ litigation track → elite-corporate-counsel · federal-trial-counsel
  ├─ corp/fund build → corporate-counsel · pe-vc-counsel · institutional-finance
  ├─ tax angle → tax-strategy (QSBS/asset-protection) · tax-compliance/tax-relief (controversy)
  └─ research → /glaw-case-law-research + deep-research engine

STRUCTURE  /glaw-structure
  ├─ entity/cap table/elections → /glaw-entity-architect · corporate-counsel
  ├─ fund tiers/waterfall → pe-vc-counsel · institutional-finance · tokenization-compliance
  ├─ tax election/QSBS → tax-strategy  (math → fs-3-statement-model / fs-dcf-model / fs-lbo-model / fs-comps-analysis / fs-merger-model)
  └─ numbers/forensics → /glaw-accounting → financial-forensics · roofer-accounting · company-valuation
        └─ execution: fs-gl-recon · fs-break-trace · fs-nav-tieout · fs-xlsx-author · fs-audit-xls

DRAFT  /glaw-draft
  ├─ formation/governance docs → corporate-counsel (bylaws/OA/voting/dual-class templates)
  ├─ fund docs → pe-vc-counsel · fund-regulatory-council
  ├─ inbound contract review/redline → contract-review (CUAD)        ← NEW seat
  ├─ commercial contract drafting → /glaw-commercial-contracts
  ├─ tax letters/packets → tax-compliance · tax-relief (+ tax-compliance form-fill scripts)
  ├─ pleadings/motions → /glaw-motion-drafting · federal-trial-counsel
  └─ decks/exhibits → glaw-fs-pptx-author · glaw-fs-ppt-template-creator · glaw-make-pdf · glaw-docx

ADVERSARIAL  /glaw-adversarial  (RED-team → BLUE-team rebuild)        ← hard gate #2
  └─ fraud/criminal lens → /glaw-investigations · forensic-case-investigator
  └─ evidence → /glaw-evidence-timeline · /glaw-veil-piercing
  └─ executable gate → `glaw-adversarial complete --profile auto` logs `adversarial_done`
     only after every required government/regulatory/litigation RED lens survives

  GATE: /glaw-legal-research verifies every cited proposition via
        `glaw-citation-gate complete`                                  ← hard gate #3

FILE  /glaw-file  (signature-ready packet + checklist; UPL disclaimer on every deliverable)
  └─ GATE: `glaw-red-flags status` must show no blocking critical/high findings
  └─ GATE: `glaw-red-flags complete` logs the explicit clear event
  └─ GATE: `glaw-upl-check <matter>` must show all external text deliverables carry the footer
  └─ GATE: external reports must include Owner / Report voice / Findings / Evidence / Red flags / Sign-off conditions
  └─ GATE: report Evidence must cite a hashed source ID (SRC-0001...) from evidence/, sources/, or source_documents/
  └─ GATE: `glaw-final-packet build` writes final_packet.json/md and logs readiness
  └─ GATE: `glaw-chief-decision --approve-final` logs Chief/Council approval
  └─ court records → /glaw-court-records (CourtListener/PACER)
  └─ final polish → /glaw-legal-writing  (Bluebook)

DOCKET  /glaw-docket  (deadline calendar + monitoring)
  └─ GATE: `glaw-docket-gate complete` before matter-retro

RETRO  /glaw-matter-retro  (close-out + Obsidian vault write)
```

## The three cross-cutting chains (what "connected" means)

1. **Research → verify → draft → polish:** `/glaw-case-law-research` (+`deep-research`) →
   `/glaw-legal-research` (citation gate) → `/glaw-motion-drafting`/`/glaw-draft` →
   `/glaw-legal-writing`.
2. **Advise → model → reconcile:** a legal/tax seat designs it → a `/glaw-fs-*` skill builds the
   model/ledger/KYC/deck → `/glaw-financial-forensics` reconciles. (See the Execution-layer table in
   `firm-roster.md`.)
3. **Tax cleanup → resolve → plan forward:** `/glaw-tax-compliance` (file) →
   `/glaw-tax-relief` (resolve can't-pay) → `/glaw-tax-strategy` (optimize) —
   sequenced by `/glaw-tax-legal-intake`.

## Hard gates (orchestrator-enforced)
1. Structured intake complete (`bin/glaw-intake complete`) before strategy.
2. Conflicts cleared (`glaw-ethics complete`) before strategy.
3. Adversarial RED→BLUE (`/glaw-adversarial`) before file.
4. Citations verified (`glaw-citation-gate complete`) before file.
5. Chief/Council approval (`glaw-chief-decision --approve-final`) before file.
6. UPL disclaimer on every external deliverable (`glaw-upl-check`).
7. Figures quoted from `tax-legal-shared/current-figures.md` ("as of [date], verify").

## Connected skill inventory (by layer)
- **In-house seats:** all `glaw-*` (pipeline + 20+ practice/litigation-support seats).
- **Custom legal/tax suite:** corporate-counsel · elite-corporate-counsel · tax-strategy ·
  tax-compliance · tax-relief · tax-legal-intake · pe-vc-counsel · fund-regulatory-council ·
  tokenization-compliance · institutional-finance · financial-forensics · forensic-case-investigator ·
  federal-trial-counsel · roofer-accounting · company-valuation · mc-cfo-agent.
- **Contract review:** contract-review (CUAD).
- **Execution (fs-*):** 52 financial-services skills (modeling/ledger/KYC/deck/output).
- **Research:** deep-research.
- **Shared spine:** tax-legal-shared/{current-figures, guardrails, calculators, evals, REVERIFY}.
- **Render:** make-pdf · docx · document-generate · fs-pptx-author.
