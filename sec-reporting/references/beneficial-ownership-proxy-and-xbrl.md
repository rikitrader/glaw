# Beneficial Ownership (§16, 13D/G), Proxy (Reg 14A) & Inline XBRL

Beyond the registrant's periodic reports, the reporting ecosystem includes **insider and large-
holder** beneficial-ownership filings, the **proxy** disclosure regime for shareholder votes, and
the **Inline XBRL** structured-data requirement that overlays the financial statements. This file
maps each.

> Forms, deadlines, and thresholds change — confirm on sec.gov and quote any figure from
> `tax-legal-shared/current-figures.md`.

## Section 16 — insider beneficial-ownership reports (Forms 3, 4, 5)

**Exchange Act § 16** (15 U.S.C. § 78p) covers **insiders** of a § 12-registered company —
directors, officers, and beneficial owners of more than **10%** of a class of registered equity:

- **Form 3** — *initial* statement of beneficial ownership, filed when a person first becomes an
  insider.
- **Form 4** — *changes* in beneficial ownership (most insider trades), filed on a **short clock**
  (generally within two business days of the transaction — confirm the current period).
- **Form 5** — *annual* statement reporting transactions exempt from or not previously reported on
  Form 4.
- **§ 16(b) short-swing profit** — profits from a purchase and sale (or sale and purchase) within
  **six months** are recoverable **by the issuer**, regardless of intent — a strict-liability
  disgorgement rule distinct from insider-trading liability.
- **§ 16(a)** late-filing delinquencies must be disclosed in the proxy/10-K.

Forms 3/4/5 are filed via EDGAR by or on behalf of the **insider** (not the issuer), though issuers
commonly facilitate them.

## Schedules 13D and 13G — large beneficial owners

**Exchange Act § 13(d) and § 13(g)** require a person (or group) acquiring beneficial ownership of
more than **5%** of a class of registered voting equity to report:

- **Schedule 13D** — the **long-form** report (identity, source of funds, **purpose** of the
  acquisition, and plans/proposals) for active investors. Filed within the prescribed window after
  crossing 5%; **amendments** required on material changes.
- **Schedule 13G** — the **short-form** report available to **passive investors**, certain
  **qualified institutional investors**, and **exempt investors**, with less detail and different
  deadlines.

The SEC has **amended the 13D/13G filing deadlines** (shortening them) and addressed group/cash-
settled-derivative treatment — **verify the current deadlines and rules on sec.gov.**

## Proxy disclosure — Regulation 14A

When a company solicits shareholder **votes** (annual meeting, mergers, director elections),
**Exchange Act § 14(a) and Regulation 14A** govern the proxy statement:

- **Schedule 14A** — the content of the proxy statement (director nominees, executive compensation
  per S-K Item 402, governance, auditor ratification, and any extraordinary matters).
- **Rule 14a-8** — the shareholder-proposal process (when a company must include a shareholder
  proposal and the bases for exclusion).
- **Rule 14a-9** — the **anti-fraud** rule: a proxy solicitation may not contain false or misleading
  statements of material fact or omit a material fact. This makes proxy disclosure a live
  **enforcement and private-litigation** exposure (route the judgment to `/glaw-sec-disclosure`).
- **DEF 14A / PRE 14A** — the definitive and preliminary proxy filings on EDGAR.

## Inline XBRL — the structured-data layer

The SEC requires registrants to tag their financial statements (and certain other disclosures such
as cover-page data and parts of risk/management disclosures as the rules expand) in **Inline XBRL**
(iXBRL) — machine-readable tags embedded in the human-readable HTML:

- The financial statements and footnotes are tagged to the appropriate **US-GAAP taxonomy**
  elements; **cover pages** of 10-K/10-Q/8-K and certain other items are also tagged.
- **Tagging accuracy is part of the filing's quality** — mis-tagging is a deficiency the staff can
  flag. The tagged data must **match** the rendered financial statements (which tie to the audited
  GL).
- SRCs and certain smaller filers were **phased in**; confirm the current scope and any
  accommodations on sec.gov.

## How this seat applies it

1. Identify whether the matter implicates **insider** (§16 Forms 3/4/5) or **large-holder**
   (13D/13G) reporting — and the **deadlines** that run on each.
2. For a vote, build the **Schedule 14A** content (S-K Item 402 comp, governance, Rule 14a-8
   proposals) and test it against the **Rule 14a-9** anti-fraud standard (judgment →
   `/glaw-sec-disclosure`).
3. Plan **Inline XBRL** tagging so the tagged data **reconciles** to the S-X statements and the
   audited GL.
4. Flag **§ 16(a) delinquencies** and **§ 16(b) short-swing** exposure; route enforcement-grade
   issues to `/glaw-sec-enforcement`.

---

*SEC-reporting work-product, not legal, tax, or accounting advice, and not a substitute for SEC
counsel or an auditor. Prepared for review and sign-off by a licensed CPA / securities attorney.
Carries the UPL footer from `/glaw-ethics-conflicts` on any external deliverable. Confirm current
forms, deadlines, and thresholds on sec.gov.*
