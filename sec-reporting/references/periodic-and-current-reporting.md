# Periodic & Current Reporting — Forms, Filer Status & Deadlines

The Exchange Act §13(a) imposes the ongoing reporting duty on issuers with registered securities.
This file maps the **filer categories**, the **periodic and current forms**, the **registration
statements**, and how **deadlines** flow from filer status and period-end.

> Every filer-status threshold, day count, and fee defers to `tax-legal-shared/current-figures.md`
> or the current SEC rule — they change. Name the rule; quote the figure from the spine.

## The reporting duty

- **Securities Exchange Act of 1934 § 13(a)** (15 U.S.C. § 78m) — issuers with securities
  registered under § 12 must file periodic and current reports.
- **§ 15(d)** — a parallel reporting obligation for issuers that registered an offering under the
  **Securities Act of 1933** (S-1 etc.).
- **Exchange Act Rules 13a-1 (10-K), 13a-13 (10-Q), and 13a-11 (8-K)** — prescribe the periodic and
  current reports.

## Filer status (drives deadlines and scaled disclosure)

Filer status is set by **public float** (the aggregate market value of voting/non-voting common
equity held by non-affiliates) measured at prescribed dates, and — for the smaller categories — by
**annual revenue**. The four categories:

| Category | Set by | Effect |
|---|---|---|
| **Large Accelerated Filer** | Highest public-float band | Shortest 10-K / 10-Q deadlines; full disclosure; ICFR auditor attestation |
| **Accelerated Filer** | Middle public-float band | Mid deadlines; ICFR auditor attestation |
| **Smaller Reporting Company (SRC)** | Below the public-float / revenue thresholds | **Scaled** disclosure — fewer financial-statement years, reduced S-K items |
| **Non-accelerated Filer** | Not accelerated | Longest deadlines; no ICFR auditor attestation |

- A company can be **both** an SRC **and** a non-accelerated or accelerated filer — the two tests
  are related but distinct. **Emerging Growth Companies (EGCs)** under the JOBS Act get additional
  accommodations (e.g., reduced years, deferred ICFR attestation).
- The SEC has **amended/proposed streamlining** of how filer status is determined — **verify the
  current thresholds and any adopted changes on sec.gov before relying** on a category.

## The forms

### 10-K — annual report (Exchange Act Rule 13a-1)

Audited financial statements (Reg S-X), full MD&A (Item 303), risk factors (Item 105), business
description, legal proceedings (Item 103), management/governance, **internal control over financial
reporting** (and, for accelerated/large accelerated filers, the auditor's ICFR attestation), and the
officer **§ 302 / § 906** certifications.

### 10-Q — quarterly report (Rule 13a-13)

Unaudited, **condensed** interim financial statements (S-X Article 10), an MD&A update, and the
officer certifications. Filed for the first three fiscal quarters; the fourth quarter is covered by
the 10-K.

### 8-K — current report (Rule 13a-11)

A report of **specified material events** on a **short clock** (generally within four business days
of the triggering event — confirm the current period and the event-specific timing). Item examples:
material agreements, acquisitions/dispositions, results of operations and financial condition (Item
2.02 earnings releases), departures of directors/officers, changes in auditor, bankruptcy, and Reg
FD disclosures (Item 7.01). A **late or missing 8-K** measured against its triggering event is a
classic reporting defect.

### S-1 / S-3 — registration statements (Securities Act)

- **S-1** — the general registration statement for an offering (full prospectus, S-X financials,
  S-K disclosures).
- **S-3** — the **short-form / shelf** registration available to seasoned issuers meeting the
  eligibility requirements (incorporates Exchange Act reports by reference). Confirm S-3 eligibility
  before relying.

## Deadlines

10-K and 10-Q due dates run from **fiscal period-end** and **depend on filer status** — shorter for
larger filers. **Do not state the day counts from memory** — confirm the current deadlines (by
filer category) on sec.gov and quote them from `tax-legal-shared/current-figures.md`. A deadline
falling on a weekend/holiday rolls to the next business day per SEC rules. The **8-K** clock runs
from the **event**, not period-end.

## Officer certifications

- **SOX § 302** (Exchange Act Rules 13a-14 / 15d-14) — CEO/CFO certify the report's accuracy, the
  disclosure controls, and material changes; filed as an exhibit with each 10-K/10-Q.
- **SOX § 906** (18 U.S.C. § 1350) — CEO/CFO certify that the report fully complies and fairly
  presents; carries **criminal** exposure for a knowing false certification.

## EDGAR

All filings are submitted electronically through **EDGAR** (Electronic Data Gathering, Analysis,
and Retrieval). GLAW **prepares** the submission package (assembled document set, exhibits,
certifications, Inline-XBRL data); an **authorized filer agent transmits** it. Filer credentials
(CIK, CCC, filer codes) are obtained through EDGAR onboarding.

## How this seat applies it

1. **Determine filer status** (public float ± revenue at the prescribed dates) and SRC/EGC scaling.
2. **Pick the form** and **compute its deadline** from period-end (or, for 8-K, the event).
3. Assemble the **S-X financials** and **S-K disclosures** (see the companion files).
4. **Tag in Inline XBRL**, obtain the **§ 302 / § 906** certifications, and assemble the **EDGAR**
   package — every figure tied to the audited GL, then hand to the authorized filer agent.

---

*SEC-reporting work-product, not legal, tax, or accounting advice, and not a substitute for SEC
counsel or an auditor. Prepared for review and sign-off by a licensed CPA / securities attorney.
Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable. Verify all
thresholds/deadlines on sec.gov and in `tax-legal-shared/current-figures.md`.*
