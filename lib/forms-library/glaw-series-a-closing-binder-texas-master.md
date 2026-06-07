# SERIES A PREFERRED STOCK FINANCING — CLOSING BINDER & SIGNING CHECKLIST (TEXAS)

> GLAW MASTER + [Company] instance, for a Series A priced round in a **Texas for-profit corporation** governed by the
> **Texas Business Organizations Code (TBOC)**. The single index that ties the priced-round documents, corporate
> approvals, cap table, and ancillary deliverables into one closing. ATTORNEY WORK-PRODUCT; a licensed Texas attorney
> runs the closing. Not legal advice. Filled for [Company] (Series A: $[__]/sh, $[__] post — confirm against the
> executed term sheet).

## 0. DEAL SUMMARY
- **Company:** [Company], Inc. (**Texas**) · **Round:** Series A Convertible Preferred · **Price:** $[__]/sh ·
  **Pre/Post:** $[__]/$[__] · **New money:** $[__] (target) · **Lead:** [Series A Lead] · **Pro-rata participants:** [__].
- **Closing structure:** [single close / initial + subsequent closings within [90] days].

## A. CHARTER AMENDMENT (defines the security — must be filed FIRST)
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| A1 | **Amended & Restated Certificate of Formation** with a **Statement of Designation establishing the Series A Preferred series** (liq pref, conversion, anti-dilution, protective provisions), authorized under **TBOC §21.155** (board authority to establish and designate a series of shares within the limits of the certificate of formation), filed with the **Texas Secretary of State** under TBOC Chapter 3 (Form 424 / certificate of amendment, or Form 425 statement of operating provisions as applicable) | Company officer; **filed with TX Sec. of State** | ☐ draft → ☐ shareholder-approved → ☐ FILED | (attach the executed document) |

## B. THE FIVE PRICED-ROUND DOCUMENTS
| # | Document | Who signs | Status | Drive |
|---|----------|-----------|--------|-------|
| B1 | **Series A Preferred Stock Purchase Agreement** (the buy/sell + reps & warranties + closing conditions; Texas-governing-law NVCA-style SPA — the M&A Share Purchase master is for acquisitions, not a financing) | Company + each Investor | ☐ | (attach the executed document) |
| B2 | **Investor Rights Agreement** (registration, info, preemptive, board, consent) | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B3 | **Right of First Refusal & Co-Sale Agreement** | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B4 | **Voting Agreement** (board election + drag-along) | Company + Investors + Key Holders | ☐ | (attach the executed document) |
| B5 | **(Statement of Designation — see A1)** | — | — | — |

## C. CORPORATE APPROVALS (sequence: Board → Shareholders → file charter → close)
| # | Document | Approves | Who signs |
|---|----------|----------|-----------|
| C1 | **Board Consent (Financing)** — unanimous written consent in lieu of a meeting under **TBOC §6.201** (directors may act by written consent without a meeting; effective when signed by all directors unless a later date is specified) | the A&R certificate of formation / Statement of Designation; the 4 agreements; issuance + sale of the Series A; the new option pool (if any); the board-size change; Form D authorization | all directors |
| C2 | **Shareholder Consent** — written consent of shareholders under **TBOC §6.202**. **FLAG:** Texas DEFAULTS to **unanimous** written consent (§6.202(a)); a Texas corporation may permit LESS-THAN-UNANIMOUS written consent ONLY if its **certificate of formation expressly so provides** (§6.202(b)–(c)). Confirm the certificate of formation contains a less-than-unanimous-consent provision before relying on a majority/requisite written consent; otherwise convene a meeting or obtain all shareholder signatures | the A&R Certificate of Formation (authorized-share increase + Series A terms + protective provisions); waiver of any preemptive/ROFR on this issuance | requisite Common + existing Preferred (per certificate of formation) |
| C3 | **Optional-pool top-up / 409A** | (if expanding the pool pre-money) board adopts; fresh 409A if granting | board |

## D. CAP TABLE
| # | Item | Source |
|---|------|--------|
| D1 | **Pre-money cap table** (fully diluted) | (attach the executed document) |
| D2 | **Post-money cap table** (after the Series A + any pool top-up) | Carta (run `captable_to_proof.py` to regenerate + the §368(c) check) |
| D3 | **Pro-forma / waterfall** | Carta Waterfall + Exit Scenarios tabs |

## E. ANCILLARY CLOSING DELIVERABLES
☐ E1 Legal opinion of Company counsel · ☐ E2 Secretary's Certificate (certificate of formation, bylaws, resolutions,
incumbency) · ☐ E3 Certificate of fact / good standing (Texas Sec. of State) + certificate of account status (Texas
Comptroller) + foreign-qualified states · ☐ E4 Capitalization Certificate (cap table true & correct) · ☐ E5
**Accredited-Investor Questionnaire** + verification (506(b)/(c)) per Investor · ☐ E6 W-9 / W-8 per Investor · ☐ E7
Management Rights Letter (for VCOC investors) · ☐ E8 Side letters (+ MFN log) · ☐ E9 Officer's Compliance Certificate
(reps bring-down) · ☐ E10 Wire instructions + receipt of funds · ☐ E11 Updated stock ledger + share certificates /
book-entry (per TBOC §3.151 records requirement) · ☐ E12 D&O insurance bound (per IRA §4.10).

## F. SIGNING SEQUENCE (closing day)
1. Shareholders sign **C2** (confirm unanimity OR a §6.202 less-than-unanimous-consent provision in the certificate
   of formation) → Board signs **C1** (§6.201).
2. File the **A&R Certificate of Formation / Statement of Designation (A1)** with the Texas Secretary of State; obtain
   the file-stamped acknowledgment of filing.
3. Parties sign **B1–B4** (Purchase Agreement + IRA + ROFR/Co-Sale + Voting).
4. Deliver **E1–E12**; Investors wire funds; Company issues the Series A (book-entry).
5. Update the cap table (D2) + stock ledger; counter-sign; release from escrow.

## G. POST-CLOSING (calendar these — `glaw docket add`)
☐ **Form D on SEC EDGAR ≤ 15 days after first sale** · ☐ **Blue Sky / Texas State Securities Board notice** in each
Investor's state ≤ 15 days · ☐ update minute book + cap table of record · ☐ §83(b) reminders for any new restricted
stock (30-day, → /glaw-83b-election) · ☐ board/committee organizational items · ☐ deliver executed binder to all
parties.

## H. CONDITIONS TO CLOSING (from the Purchase Agreement)
Reps true & correct (bring-down); covenants performed; **certificate of formation / Statement of Designation filed**;
the 4 agreements executed; required consents/waivers; no MAE; no injunction; opinion + certificates delivered;
minimum-raise threshold met (if any).

## TEXAS STATUTORY MAPPING (replaces the Delaware DGCL references)
- **Series establishment ("blank-check" preferred):** TBOC **§21.155** — the board may establish and designate one or
  more series of shares and fix their preferences, limitations, and relative rights within the limits set by the
  certificate of formation (the Texas analog to DGCL §151). Effected by a **Statement of Designation** filed under
  TBOC Chapter 3.
- **Board action by written consent:** TBOC **§6.201** — directors may act without a meeting by written consent
  signed by all directors (analog to DGCL §141(f)).
- **Shareholder action by written consent:** TBOC **§6.202** — DEFAULTS to **unanimous** written consent; a
  less-than-unanimous written consent is available **only if the certificate of formation expressly authorizes it**
  (contrast DGCL §228, which permits majority written consent by default). **This is the single most important Texas
  divergence for a priced round — verify the certificate of formation before assuming majority consent works.**
- **Records:** TBOC **§3.151** — books, records, and shareholder list maintenance.

> Run the **`/glaw-consensus`** gate on the executed set before closing; **`/glaw-file`** assembles the signature
> packet; **`/glaw-docket`** calendars G. A licensed Texas attorney must review, sign, and file.

---

> ATTORNEY WORK-PRODUCT — GLAW master form. Not legal advice; no attorney-client relationship is formed by use of
> this template. A licensed Texas attorney must review, adapt, and execute every provision and schedule.

> **Attorney work-product — not legal advice.** Texas variant genericized to `[BRACKETS]`; a licensed Texas attorney must adapt and sign it. GLAW does not form an attorney-client relationship or practice law.
