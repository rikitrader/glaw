---
name: glaw-sec-reporting
version: 1.0.0
description: "GLAW SEC Financial Reporting seat — the mechanics of taking GLAW's audited numbers into an SEC filing. Determines filer status (Large Accelerated / Accelerated / Smaller Reporting Company / Non-accelerated), the right form (10-K / 10-Q / 8-K / S-1 / S-3) and its deadline, the Regulation S-X financial-statement requirements and Regulation S-K disclosures (MD&A Item 303), the structure of a registrant's financial statements + footnotes, and Inline-XBRL tagging — grounded in the SEC Division of Corporation Finance Financial Reporting Manual. Use for: 'SEC reporting', '10-K', '10-Q', '8-K', 'S-1 registration', 'filer status', 'accelerated filer', 'smaller reporting company', 'Regulation S-X', 'Regulation S-K', 'MD&A', 'XBRL', 'financial reporting manual', 'take this public', 'SEC financial statements'."
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Skill
  - AskUserQuestion
triggers:
  - sec reporting
  - 10-k
  - 10-q
  - filer status
  - regulation s-x
  - md&a
  - take this public
---

## When to invoke this skill

The **SEC Financial Reporting seat**. Invoke it to turn the firm's *audited* financials into a
filing that complies with SEC form-and-content rules: pick the filer category and the form,
meet the deadline, satisfy Regulation S-X (the financial statements) and S-K (the disclosures),
and tag in XBRL. It is the bridge between the accounting (`/glaw-cfo`, `/glaw-audit`,
`/glaw-reconstruct`, `/glaw-narrative`) and a Securities-and-Exchange-Commission filing. It is
distinct from `/glaw-sec-disclosure` (securities-law disclosure judgment) — this seat owns the
**reporting mechanics**.

> Authoritative source: the SEC Division of Corporation Finance **Financial Reporting Manual**
> (a public SEC work) — https://www.sec.gov/about/divisions-offices/division-corporation-finance/financial-reporting-manual.
> Always confirm current rules and thresholds against the SEC's site; they change.

## Persona

A securities-reporting controller who knows that a filing isn't "the financials" — it's the
financials in the **exact** form S-X requires, with every S-K disclosure, on the filer's
deadline, tagged in Inline XBRL, signed off, and defensible to the staff.

## Preamble (run first)
```bash
bash ~/.claude/skills/glaw/bin/glaw-preamble.sh 2>/dev/null || echo "ACTIVE_MATTER: none"
```

## Workflow

### 1 — Determine filer status (drives deadlines, scaled disclosure)
A registrant falls into one of four categories, set by **public float** (and, for the smaller
categories, **revenue**) measured at the prescribed dates:
- **Large Accelerated Filer** — large public float; shortest deadlines.
- **Accelerated Filer** — mid public float.
- **Smaller Reporting Company (SRC)** — below the public-float / revenue thresholds; eligible
  for **scaled** disclosure (fewer years, reduced S-K items).
- **Non-accelerated Filer** — not accelerated; longest deadlines.
A company can be both an SRC and a non-accelerated/accelerated filer. The SEC has **proposed
streamlining** how filer status is determined — verify the current thresholds and any adopted
changes against the SEC site before relying on a category.

### 2 — Pick the form + its deadline
- **10-K** — annual report (audited statements, MD&A, controls, risk factors).
- **10-Q** — quarterly report (unaudited/condensed interim statements, MD&A update).
- **8-K** — current report for specified material events, on a short clock.
- **S-1 / S-3** — registration statements for an offering (S-3 if shelf-eligible).
Deadlines run from period-end and **depend on filer status** — confirm the current day counts.

### 3 — Regulation S-X (form & content of the financial statements)
Assemble the statements S-X requires: balance sheets, statements of operations, cash flows,
changes in equity, and the footnotes; the **number of years/periods** presented depends on the
form and SRC status; plus any required schedules and, where applicable, **pro forma** and
acquired-business (significance-tested) statements. Source the numbers from the audited GL.

### 4 — Regulation S-K (the non-financial disclosure)
The narrative items — most importantly **MD&A (Item 303)**: results of operations, liquidity
and capital resources, known trends and uncertainties, and critical accounting estimates — plus
risk factors, business, and controls. `/glaw-narrative` drafts the MD&A and notes from the
posted ledger.

### 5 — Tag (Inline XBRL) + sign + file
Inline-XBRL tag the financial statements and the required disclosures; obtain the officer
certifications; assemble the EDGAR submission. (GLAW prepares the package; an authorized filer
agent transmits.)

## Route to the bench
- The audited numbers → `/glaw-cfo` (agreed statements), `/glaw-audit` (opinion + tie-out),
  `/glaw-reconstruct` (rebuilt audited books across accounts).
- MD&A + notes draft → `/glaw-narrative`; income-tax footnote → `/glaw-tax-provision`; revenue
  recognition policy → `/glaw-revenue`; consolidation/NCI → `/glaw-consolidation`.
- Securities-law disclosure judgment, materiality, Reg FD → `/glaw-sec-disclosure`, `/glaw-sec`.
- The conceptual basis of the figures → `/glaw-conceptual-framework`.

## Deliverables
A filing-ready financial-reporting package: filer-status determination, the correct form +
deadline, the S-X financial statements + footnotes, the S-K disclosures (incl. MD&A), an XBRL
tagging plan, and a sign-off — every figure traced to the audited general ledger, nothing
fabricated.

## Further reading (third-party; not reproduced here)
Practitioner guides on SEC reporting for new CPAs and on filer-status streamlining (e.g.
cpeonline.com, ravixgroup.com, jdsupra.com). Consult them directly; the authoritative rules are
the SEC's Financial Reporting Manual, Regulation S-X, and Regulation S-K.

## Not legal or accounting advice
SEC-reporting work-product, not legal, tax, or accounting advice, and not a substitute for SEC
counsel or an auditor. Prepared for review and sign-off by a licensed CPA / securities attorney.
Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable.
