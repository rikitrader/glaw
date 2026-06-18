# SAR / CTR Reporting & Information Sharing

The two cornerstone BSA reports, plus the 314 information-sharing channels.

## A. Currency Transaction Report (CTR)
- **Trigger:** a transaction (or aggregated same-day transactions by/for one person) in
  **currency exceeding $10,000**. Mechanical, not discretionary.
- **Rule:** 31 CFR 1010.311; filed on **FinCEN CTR (Form 112)** within **15 days**.
- **Structuring is a crime:** breaking cash into sub-$10k pieces to dodge the CTR violates
  31 U.S.C. 5324 — itself a SAR red flag (see `/glaw-fincen-sar` typologies).
- **GTO overlay:** Geographic Targeting Orders can drop the CTR threshold far below $10,000
  for covered businesses in covered areas (Southwest Border, Minnesota) — see `gto-tracker.md`.

## B. Suspicious Activity Report (SAR)
- **Trigger:** the institution **knows, suspects, or has reason to suspect** a transaction
  involves illegal funds, is designed to evade the BSA, has no apparent lawful purpose, or
  uses the FI to facilitate a crime — at or above the applicable dollar threshold (generally
  **$5,000** for banks where a suspect is identifiable; **$2,000** for MSBs; lower/none in
  some contexts).
- **Rules:** 31 CFR **1020.320** (banks), **1022.320** (MSBs), **1023.320** (broker-dealers),
  and parallel sections; statute 31 U.S.C. 5318(g). Filed on **FinCEN SAR (Form 111)**.
- **Timing:** generally within **30 days** of initial detection (60 if no suspect identified).
- **Continuing activity:** if suspicious activity continues, file a follow-up SAR — commonly
  every **90 days** of ongoing review (this cadence is what the 2025 FAQs address).
- **Confidentiality:** the existence/contents of a SAR are confidential — **no tipping off**
  (31 CFR 1020.320(e); 31 U.S.C. 5318(g)(2)). Unlawful SAR disclosure draws penalties.

### 2025-10-09 — SAR FAQs (four), joint with FRB/FDIC/NCUA/OCC
- **Substance:** clarify SAR requirements to **stop needless resource expenditure** on
  defensive/duplicative filings and over-frequent continuing-activity reviews.
- **Compliance impact:** institutions may **right-size** their SAR programs in reliance on the
  FAQs — but **document** the FAQ basis for any reduction in filing/review cadence; an
  examiner will still test reasonableness.
- **Authority:** interpretive of the SAR rules above. Verify the FAQ text on FinCEN.gov.

> Historical context in corpus: 2021-01-19 SAR/AML FAQ (FinCEN + federal banking agencies)
> and the 2022 SAR-sharing pilot NPRM. The 2025 FAQs are the current word.

## C. 314(a) — mandatory law-enforcement information requests
- **Rule:** 31 CFR 1010.520. FinCEN relays law-enforcement queries; FIs **must** search
  records for matches to named subjects and report matches. Mandatory, confidential.

## D. 314(b) — voluntary FI-to-FI information sharing (safe harbor)
- **Rule:** 31 CFR 1010.540. Registered FIs may **voluntarily share** information with each
  other to identify/report ML or terrorist financing, with a **safe harbor** from liability.
- **2026-06-12 — Guidance to eliminate fraud through information sharing** extends the
  practical use of 314(b) to **fraud** detection, not just ML/TF.
- **2025-09-05 — Cross-border information-sharing guidance** addresses sharing across a
  financial group's borders within BSA confidentiality limits.
- **Compliance impact:** confirm **314(b) registration** and the safe-harbor conditions before
  sharing; sharing outside the safe harbor risks breaching SAR confidentiality.

## E. How GLAW uses this
- `/glaw-fincen-sar` produces a **suspicious-activity analysis with a ranked red-flag table** —
  **not a filed SAR**; the filing decision is the institution's BSA officer's alone.
- Route SAR/CTR doctrine and program-adequacy questions to `/glaw-regulatory-aml`.

---

*Not legal advice. Compliance-advisory work-product for review by a licensed professional.
Verify thresholds and FAQ text on FinCEN.gov before relying.*
