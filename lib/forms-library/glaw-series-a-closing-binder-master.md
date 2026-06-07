# [COMPANY], INC. — SERIES A PREFERRED STOCK FINANCING — CLOSING BINDER & SIGNING CHECKLIST

> GLAW MASTER + [Company] instance. The single index that ties the priced-round documents, corporate approvals, cap
> table, and ancillary deliverables into one closing. ATTORNEY WORK-PRODUCT; a licensed attorney runs the closing.
> Not legal advice. Filled for [Company] (Series A: $2.00/sh, $15M post — confirm against the executed term sheet).

## 0. DEAL SUMMARY
- **Company:** [Company], Inc. (Delaware) · **Round:** Series A Convertible Preferred · **Price:** $[__]/sh ·
  **Pre/Post:** $[__]/$[__] · **New money:** $[__] (target) · **Lead:** [Series A Lead] · **Pro-rata participants:** [__].
- **Closing structure:** [single close / initial + subsequent closings within [90] days].

## A. CHARTER AMENDMENT (defines the security — must be filed FIRST)
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| A1 | **Amended & Restated Certificate of Incorporation / Certificate of Designations** (Series A terms: liq pref, conversion, anti-dilution, protective provisions) | Company officer; **filed with DE Sec. of State** | ☐ draft → ☐ stockholder-approved → ☐ FILED | (attach the executed document) |

## B. THE FIVE PRICED-ROUND DOCUMENTS
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| B1 | **Series A Preferred Stock Purchase Agreement** (the buy/sell + reps & warranties + closing conditions) | Company + each Investor | ☐ **TO ADD — dedicated NVCA Series A SPA** (the M&A Share Purchase master is for acquisitions, not a financing) | — |
| B2 | **Investor Rights Agreement** (registration, info, preemptive, board, consent) | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B3 | **Right of First Refusal & Co-Sale Agreement** | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B4 | **Voting Agreement** (board election + drag-along) | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B5 | **(Cert of Designations — see A1)** | — | — | — |

## C. CORPORATE APPROVALS (sequence: Board → Stockholders → file charter → close)
| # | Document | Approves | Who signs |
|---|----------|----------|-----------|
| C1 | **Board Consent (Financing)** | the A&R charter/Cert of Designations; the 4 agreements; issuance + sale of the Series A; the new option pool (if any); the board-size change; Form D authorization | all directors |
| C2 | **Stockholder Consent** | the A&R Certificate of Incorporation (authorized-share increase + Series A terms + protective provisions); waiver of any preemptive/ROFR on this issuance | requisite Common + existing Preferred (per charter) |
| C3 | **Optional-pool top-up / 409A** | (if expanding the pool pre-money) board adopts; fresh 409A if granting | board |

## D. CAP TABLE
| # | Item | Source |
|---|------|--------|
| D1 | **Pre-money cap table** (fully diluted) | (attach the executed document) |
| D2 | **Post-money cap table** (after the Series A + any pool top-up) | Carta (run `captable_to_proof.py` to regenerate + the §368(c) check) |
| D3 | **Pro-forma / waterfall** | Carta Waterfall + Exit Scenarios tabs |

## E. ANCILLARY CLOSING DELIVERABLES
☐ E1 Legal opinion of Company counsel · ☐ E2 Secretary's Certificate (charter, bylaws, resolutions, incumbency) ·
☐ E3 Good Standing certificate (DE + foreign-qualified states) · ☐ E4 Capitalization Certificate (cap table true &
correct) · ☐ E5 **Accredited-Investor Questionnaire** + verification (506(b)/(c)) per Investor · ☐ E6 W-9 / W-8 per
Investor · ☐ E7 Management Rights Letter (for VCOC investors) · ☐ E8 Side letters (+ MFN log) · ☐ E9 Officer's
Compliance Certificate (reps bring-down) · ☐ E10 Wire instructions + receipt of funds · ☐ E11 Updated stock ledger
+ share certificates / book-entry · ☐ E12 D&O insurance bound (per IRA §4.10).

## F. SIGNING SEQUENCE (closing day)
1. Stockholders sign **C2** → Board signs **C1**.
2. File the **A&R Certificate of Incorporation / Cert of Designations (A1)** with DE; obtain file-stamped copy.
3. Parties sign **B1–B4** (Purchase Agreement + IRA + ROFR/Co-Sale + Voting).
4. Deliver **E1–E12**; Investors wire funds; Company issues the Series A (book-entry).
5. Update the cap table (D2) + stock ledger; counter-sign; release from escrow.

## G. POST-CLOSING (calendar these — `glaw docket add`)
☐ **Form D on SEC EDGAR ≤ 15 days after first sale** · ☐ **Blue Sky** notices in each Investor's state ≤ 15 days ·
☐ update minute book + cap table of record · ☐ §83(b) reminders for any new restricted stock (30-day, → /glaw-83b-election)
· ☐ board/committee organizational items · ☐ deliver executed binder to all parties.

## H. CONDITIONS TO CLOSING (from the Purchase Agreement)
Reps true & correct (bring-down); covenants performed; **charter filed**; the 4 agreements executed; required consents/
waivers; no MAE; no injunction; opinion + certificates delivered; minimum-raise threshold met (if any).

> Run the **`/glaw-consensus`** gate on the executed set before closing; **`/glaw-file`** assembles the signature
> packet; **`/glaw-docket`** calendars G. A licensed attorney must review, sign, and file.
