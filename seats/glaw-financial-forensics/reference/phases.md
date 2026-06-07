# The 7-Phase Reconstruction Methodology

This is the authoritative, step-by-step procedure. Execute phases in order. Every phase has
explicit **verification gates** — do not advance until the gate passes. Cite the KB
(`scripts/search_kb.sh`) for any methodology claim.

---

## Phase 1 — Data Extraction

**Goal:** a complete, deduplicated, normalized transaction register with an audit trail.

1. **Ingest every document.** PDFs → `scripts/ingest_pdf.sh`. CSV/XLSX → read directly.
   Photos/scans → ingest, and if OCR confidence is low, flag the line as
   `[ILLEGIBLE — needs source]` rather than guessing.
2. **Extract every transaction** with: `date | description (raw) | amount | direction
   (debit/credit) | running balance (if shown) | source_file | source_page | source_line`.
3. **Identify and tag transaction types:**
   - Deposits · Withdrawals · Transfers (internal vs external) · ACH · Wire transfers ·
     Checks (capture check #) · Cash withdrawals · Merchant-processing deposits
     (Stripe/Square/etc.) · Loan proceeds · Owner contributions · Payroll runs ·
     Payroll taxes · Credit-card payments.
4. **Normalize dates** to `YYYY-MM-DD`.
5. **Normalize vendors/payees:** collapse `AMZN MKTP`, `Amazon.com`, `AMAZON` → `Amazon`.
   Keep the raw string in a `raw_description` column so nothing is lost.
6. **Detect duplicates:** same amount + same date + same normalized payee = candidate
   duplicate. List them; do NOT silently merge — a real duplicate payment is a forensic finding.
7. **Flag missing statement pages:** check page numbering ("Page 3 of 7") and beginning/
   ending balances. If statement N's ending balance ≠ statement N+1's beginning balance →
   `[GAP]`.
8. **Detect date gaps:** any period with no statement coverage → list it explicitly in the
   Missing Documents List.

**Verification gate 1:** For each account, `beginning balance + Σ(credits) − Σ(debits) =
ending balance`. If it doesn't tie, there are missing/misread transactions — resolve before
Phase 2. Record the proof.

---

## Phase 2 — Accounting Classification

Map every transaction to the chart of accounts in
[`chart-of-accounts.md`](chart-of-accounts.md). Categories:

- **Revenue:** Sales · Service · Subscription · Merchant Deposits · Other Income
- **COGS:** Materials · Inventory Purchases · Direct Labor · Subcontractors
- **Operating Expenses:** Advertising · Marketing · Payroll · Payroll Taxes · Rent ·
  Utilities · Insurance · Professional Fees · Legal Fees · Software · Telecommunications ·
  Vehicle · Fuel · Travel · Meals · Office Supplies · Repairs & Maintenance · Bank Charges ·
  Merchant Fees
- **Balance Sheet:** Cash · Accounts Receivable · Inventory · Fixed Assets · Loans ·
  Credit Cards · Accounts Payable · Owner Equity · Retained Earnings

Rules:
- **Transfers between the owner's own accounts are NOT revenue or expense** — they net to
  zero. Misclassifying transfers as income is the #1 reconstruction error and inflates both
  revenue and audit risk.
- **Loan proceeds are a liability, not revenue.** **Owner contributions are equity.**
- **Credit-card payments** from the bank are a balance-sheet movement (reduce CC liability),
  not an expense — the expense was booked when the card was charged.
- When a payee is ambiguous, classify to the most probable account and tag
  `[ASSUMPTION: <reason>]`. Never invent a category to make a number look better.

**Verification gate 2:** 100% of transactions classified; unclassifiable items sit in a
visible `Suspense / Ask-Client` bucket, never force-fit.

---

## Phase 3 — Financial Statement Generation

Build double-entry from the classified ledger, then produce **all 10 reports** in CPA
format (see [`../templates/financial-statements.md`](../templates/financial-statements.md)):

1. **Income Statement (P&L)** — Revenue → COGS → Gross Profit → OpEx → Operating Income →
   Other Income/Expense → Net Income.
2. **Balance Sheet** — Assets = Liabilities + Equity (must balance to the penny).
3. **Cash Flow Statement** — Operating / Investing / Financing; reconcile to the actual
   net change in bank cash.
4. **General Ledger Summary** — every account with its transactions.
5. **Trial Balance** — debits = credits.
6. **Revenue Analysis** — by stream, by month, by customer (if derivable).
7. **Expense Analysis** — by category, by vendor, % of revenue, trend.
8. **Monthly Profitability Report.**
9. **Year-to-Date Summary.**
10. **Executive Financial Dashboard** — KPIs + the 5 scores.

**Verification gate 3:** (a) Trial balance balances. (b) Balance Sheet balances. (c) Cash
Flow ending cash = sum of bank ending balances = Balance Sheet cash. Show all three proofs.

> **Cash-basis vs accrual:** bank statements alone yield a **cash-basis** picture. State
> this explicitly. AR/AP, inventory, and accruals can only be added if invoices/bills are
> provided; otherwise label accrual figures `[ESTIMATED]` with method. For construction
> contractors, see WIP / percentage-of-completion in the KB — cash basis materially
> misstates contractor income.

---

## Phase 4 — IRS Audit Review

Run an IRS-style review. See [`irs-audit-flags.md`](irs-audit-flags.md) for the full
catalog. Identify:

- Unreported income · Suspicious transfers · Personal expenses paid by the business ·
  Excessive deductions · Missing supporting documentation · Cash-activity risks ·
  Related-party transactions · Round-dollar transactions · **Structuring patterns**
  (multiple sub-$10,000 cash deposits) · Large/unusual transactions · Potential tax exposure
  · Payroll-compliance issues · Sales-tax issues.

Assign each finding a tier: **Low / Moderate / High / Critical.**

This phase is run **adversarially** by the Adversarial IRS Agent(s)
([`../agents/adversarial-irs-agent.md`](../agents/adversarial-irs-agent.md)) — spawn 2–3 in
parallel and keep only findings that survive their cross-examination AND carry a source
citation.

**Verification gate 4:** every finding cites the exact transaction(s) by source line and
states the IRC/issue and the evidence that would rebut it.

---

## Phase 5 — Financial Forensics

Investigate: revenue leakage · expense inflation · fraud indicators · duplicate payments ·
hidden liabilities · undisclosed loans · missing deposits · cash diversion · financial
anomalies. Use the indicators in [`forensic-ratios.md`](forensic-ratios.md).

Calculate: Gross Margin · Net Margin · EBITDA · Debt Ratio · Current Ratio · Quick Ratio ·
Cash Burn Rate · Revenue Growth · Expense Trends. Show every formula and the inputs.

**Verification gate 5:** every ratio shows its numerator/denominator sourced from the
statements; every anomaly references the transactions that triggered it.

---

## Phase 6 — Tax Reconciliation

Compare reconstructed activity against the filed/expected returns
([`tax-reconciliation.md`](tax-reconciliation.md)):

- Form 1040 · Schedule C · Form 1120 · Form 1120S · Form 1065 · Payroll filings
  (941/940/W-2/W-3) · Sales-tax filings.

Identify discrepancies (book income vs reported income, deductions claimed vs supported) and
**estimate potential audit adjustments** with a defensible range. Label estimates
`[ESTIMATED]`.

**Verification gate 6:** each discrepancy ties a reconstructed figure to a specific line of
a specific form.

---

## Phase 7 — Deliverables

Always generate, in this order:

1. Executive Summary · 2. Key Findings · 3. Financial Statements · 4. Audit Findings ·
5. Risk Assessment · 6. Missing Documents List · 7. Recommended Corrections ·
8. CPA Review Notes · 9. **IRS Audit Readiness Score (0–100)** · 10. **Estimated Tax Exposure.**

Then the **five scores** ([`scoring-rubrics.md`](scoring-rubrics.md)) and a
**CFO-level action plan** ordered highest → lowest financial risk.

**Verification gate 7:** every deliverable section is present; every number traces to a
source or is labeled `[ESTIMATED]` with method; the audit trail is complete.
