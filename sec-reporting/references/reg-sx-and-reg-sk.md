# Regulation S-X and Regulation S-K — Form & Content

Two regulations supply the **content** of almost every SEC filing:

- **Regulation S-X (17 C.F.R. Part 210)** — the **form and content of the financial statements**:
  which statements, how many periods, the schedules, pro forma, and acquired-business statements.
- **Regulation S-K (17 C.F.R. Part 229)** — the **non-financial (narrative) disclosure**: MD&A,
  risk factors, business, legal proceedings, executive compensation, and more.

The **form's instructions** (10-K, 10-Q, S-1, etc.) tell you **which** S-X and S-K items that form
requires. SRC/EGC status **scales** several requirements down.

## Regulation S-X — the financial statements

S-X prescribes the **audited** statements for annual reports and the **condensed** statements for
interim reports:

- **Balance sheets** (statements of financial position).
- **Statements of operations** (income statements).
- **Statements of cash flows.**
- **Statements of changes in stockholders' equity.**
- **Notes / footnotes** to the financial statements.

Key S-X mechanics:

- **Number of periods.** The required number of years/periods presented depends on the form and on
  **SRC status** (an SRC presents **fewer** comparative years). Confirm the current period
  requirements per form; do not assume.
- **Article-by-article specialization.** S-X has industry/registrant-specific articles (e.g.,
  commercial/industrial companies, the Article 10 **interim** rules for 10-Q, and specialized
  articles for banks, insurance, and investment companies). Use the article that fits the
  registrant.
- **Schedules.** Certain supporting schedules are required unless the information is in the
  statements or notes.
- **Pro forma financial information** — required when a transaction (e.g., a significant
  acquisition or disposition) would materially change the registrant's financials, to show the
  effect as if it had occurred.
- **Acquired-business financial statements** — when an acquisition is **significant** under the S-X
  **significance tests** (investment, asset, and income tests), separate audited financial
  statements of the **acquired business** must be filed (commonly via an 8-K/A within the
  prescribed window). The significance level drives **how many years** of acquired-company
  statements are required.
- **Auditor independence and PCAOB standards** govern the audit underlying the S-X statements.

Source every number from the **audited general ledger**; the S-X statements must **reconcile** to
the books (route tie-out to `/glaw-audit`).

## Regulation S-K — the narrative disclosure

S-K supplies the line-item narrative. The items this seat assembles most often:

### Item 303 — Management's Discussion and Analysis (MD&A)

The centerpiece. MD&A requires a narrative of:

- **Results of operations** — material period-over-period changes and the reasons for them.
- **Liquidity and capital resources** — sources and uses of cash, material commitments, and the
  ability to meet obligations.
- **Known trends, demands, commitments, events, and uncertainties** that are **reasonably likely**
  to have a material effect — the duty to disclose a known trend or uncertainty is the most
  litigated MD&A obligation (the omitted "known trend" is a recurring enforcement theory).
- **Critical accounting estimates** — the estimates requiring the most subjective judgment.

`/glaw-narrative` drafts MD&A from the posted ledger; the **judgment** about what is a disclosable
known trend is shared with `/glaw-sec-disclosure`.

### Item 105 — Risk Factors

A discussion of the material factors that make an investment speculative or risky, organized under
relevant headings, with a concise summary if the section is long. **Boilerplate that disclaims a
risk already realized as merely "hypothetical"** is a disclosure defect (route the judgment to
`/glaw-sec-disclosure`).

### Item 103 — Legal Proceedings

Material pending legal proceedings, including specified environmental proceedings above the
disclosure threshold.

### Other recurring S-K items

- **Business** (Item 101) — description of the registrant's business.
- **Properties** (Item 102).
- **Market for the registrant's equity** (Item 201).
- **Selected/MD&A-supporting data** as the current rules require.
- **Executive compensation** (Item 402) and **corporate governance** items.
- **Controls and procedures** — disclosure controls and ICFR (paired with the § 302/§ 906
  certifications).

SRC and EGC status **reduces** several S-K items (scaled disclosure) — confirm which items the
registrant may omit or shorten.

## The non-GAAP overlay (judgment seat owns it)

Where MD&A or an exhibit presents a **non-GAAP** measure, **Regulation G** and **S-K Item 10(e)**
govern reconciliation and prominence — that **disclosure judgment** belongs to
`/glaw-sec-disclosure`; this seat ensures the **GAAP** statements themselves are S-X-compliant.

## How this seat applies it

1. **Read the form's instructions** to enumerate the required S-X articles and S-K items, then apply
   **SRC/EGC scaling**.
2. Assemble the **S-X statements** (right statements, right number of periods, schedules, pro
   forma / acquired-business where the significance tests trigger), reconciled to the audited GL.
3. Assemble the **S-K narrative** (MD&A Item 303, risk factors Item 105, business, legal
   proceedings, controls), routing the **judgment** calls (known trends, risk-factor framing,
   non-GAAP) to `/glaw-sec-disclosure`.
4. Flag any statement that does not reconcile to the books as a **red flag** to `/glaw-audit`.

---

*SEC-reporting work-product, not legal, tax, or accounting advice, and not a substitute for SEC
counsel or an auditor. Prepared for review and sign-off by a licensed CPA / securities attorney.
Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable. Confirm current
item numbers and period requirements on sec.gov.*
