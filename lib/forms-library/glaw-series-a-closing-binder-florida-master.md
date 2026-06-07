# SERIES A PREFERRED STOCK FINANCING — CLOSING BINDER & SIGNING CHECKLIST (FLORIDA)

> GLAW MASTER FORM — a standalone Florida-law closing binder for a Series A Convertible Preferred Stock financing
> of a corporation organized under the **Florida Business Corporation Act, Chapter 607, Florida Statutes**. The
> single index that ties the priced-round documents, corporate approvals, cap table, and ancillary deliverables
> into one closing. ATTORNEY WORK-PRODUCT; a licensed Florida attorney runs the closing. Not legal advice.

## 0. DEAL SUMMARY
- **Company:** [COMPANY], Inc., a Florida corporation · **Round:** Series A Convertible Preferred · **Price:**
  $[__]/sh · **Pre/Post:** $[__]/$[__] · **New money:** $[__] (target) · **Lead:** [SERIES A LEAD] · **Pro-rata
  participants:** [__].
- **Closing structure:** [single close / initial + subsequent closings within [90] days].

## A. ARTICLES OF AMENDMENT (defines the security — must be filed FIRST)
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| A1 | **Amended & Restated Articles of Incorporation / Articles of Amendment designating the Series A Preferred** (Series A terms: liquidation preference, conversion, anti-dilution, protective provisions), authorized under §607.0602 (board authority to fix terms of a class/series) and effected by §607.1002–607.1006 (amendment + filing) | Company officer; **filed with the Florida Department of State, Division of Corporations** | ☐ draft → ☐ shareholder-approved → ☐ FILED | (attach the executed document) |

## B. THE FOUR PRICED-ROUND AGREEMENTS (Florida-variant constituent docs)
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| B1 | **Series A Preferred Stock Purchase Agreement (Florida)** (the buy/sell + reps & warranties + closing conditions; governing law Florida; forum Circuit Court in and for [COUNTY] County, Florida) | Company + each Investor | ☐ | (attach the executed document) |
| B2 | **Investor Rights Agreement (Florida)** (registration, information, preemptive, board, consent rights) | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B3 | **Right of First Refusal & Co-Sale Agreement (Florida)** | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B4 | **Voting Agreement (Florida)** (board election + drag-along; shareholders' agreement enforceable under §607.0731) | Company + Investors + Key Holders | ☐ | (attach the executed document) |

## C. CORPORATE APPROVALS (sequence: Board → Shareholders → file articles → close)
| # | Document | Approves | Who signs / authority |
|---|----------|----------|-----------|
| C1 | **Board Consent (Financing)** — by unanimous written consent under **§607.0821, Fla. Stat.** | the A&R articles / Articles of Amendment designating the Series A; the four agreements (B1–B4); issuance + sale of the Series A; the new option pool (if any); the board-size change; Form D authorization | all directors |
| C2 | **Shareholder Consent** — by written consent under **§607.0704, Fla. Stat.** (action without a meeting) | the A&R Articles of Incorporation (authorized-share increase + Series A terms + protective provisions) per §§607.1002–607.1006; waiver of any preemptive (§607.0630) / ROFR rights on this issuance | requisite Common + existing Preferred (per the articles) |
| C3 | **Option-pool top-up / 409A** | (if expanding the pool pre-money) board adopts; fresh 409A valuation if granting | board |

## D. CAP TABLE
| # | Item | Source |
|---|------|--------|
| D1 | **Pre-money cap table** (fully diluted) | (attach the executed document) |
| D2 | **Post-money cap table** (after the Series A + any pool top-up) | Carta (run `captable_to_proof.py` to regenerate + the §368(c) check) |
| D3 | **Pro-forma / waterfall** | Carta Waterfall + Exit Scenarios tabs |

## E. ANCILLARY CLOSING DELIVERABLES
☐ E1 Legal opinion of Company counsel · ☐ E2 Secretary's Certificate (articles, bylaws, resolutions, incumbency) ·
☐ E3 **Certificate of Active Status** from the Florida Department of State (+ certificates of authority in each
foreign-qualified state) · ☐ E4 Capitalization Certificate (cap table true & correct) · ☐ E5 **Accredited-Investor
Questionnaire** + verification (506(b)/(c)) per Investor · ☐ E6 W-9 / W-8 per Investor · ☐ E7 Management Rights
Letter (for VCOC investors) · ☐ E8 Side letters (+ MFN log) · ☐ E9 Officer's Compliance Certificate (reps
bring-down) · ☐ E10 Wire instructions + receipt of funds · ☐ E11 Updated stock ledger + share certificates /
book-entry (§607.0626; corporate records §607.1601) · ☐ E12 D&O insurance bound (per IRA).

## F. SIGNING SEQUENCE (closing day)
1. Shareholders sign **C2** (§607.0704) → Board signs **C1** (§607.0821).
2. File the **A&R Articles of Incorporation / Articles of Amendment (A1)** with the Florida Department of State;
   obtain the file-stamped copy.
3. Parties sign **B1–B4** (Purchase Agreement + IRA + ROFR/Co-Sale + Voting).
4. Deliver **E1–E12**; Investors wire funds; Company issues the Series A (book-entry).
5. Update the cap table (D2) + stock ledger; counter-sign; release from escrow.

## G. POST-CLOSING (calendar these — `glaw docket add`)
☐ **Form D on SEC EDGAR ≤ 15 days after first sale** · ☐ **Florida securities (Blue Sky) notice filing** under
Ch. 517, Fla. Stat. (Florida Office of Financial Regulation), plus notices in each other Investor's state ≤ 15 days
· ☐ update minute book + cap table of record (§607.1601) · ☐ §83(b) reminders for any new restricted stock
(30-day, → /glaw-83b-election) · ☐ board/committee organizational items · ☐ deliver executed binder to all parties.

## H. CONDITIONS TO CLOSING (from the Purchase Agreement)
Reps true & correct (bring-down); covenants performed; **articles filed**; the four agreements executed; required
consents/waivers; no MAE; no injunction; opinion + certificates delivered (incl. Certificate of Active Status);
minimum-raise threshold met (if any).

> Run the **`/glaw-consensus`** gate on the executed set before closing; **`/glaw-file`** assembles the signature
> packet; **`/glaw-docket`** calendars G. A licensed Florida attorney must review, sign, and file.

> **Attorney work-product — not legal advice.** Florida form genericized to `[BRACKETS]`; a licensed Florida
> attorney must adapt and sign it. GLAW does not form an attorney-client relationship or practice law.
