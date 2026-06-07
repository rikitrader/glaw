# Scoring Rubrics — the Five 0–100 Scores

Every engagement closes with these five scores. Each must be **defensible and reproducible**:
show the components, the points, and the transactions/ratios that drove deductions. Never
output a bare number for court without the breakdown.

General method: start at 100, subtract weighted deductions, floor at 0. Show the arithmetic.

---

## 1. Financial Health Score (0–100)
Weighted blend of solvency, liquidity, profitability, trend.
| Component | Weight | Full marks when… |
|-----------|--------|------------------|
| Profitability (net & gross margin vs industry) | 30 | At/above KB benchmark |
| Liquidity (current/quick ratio) | 20 | Current ≥ 1.5, quick ≥ 1.0 |
| Leverage (debt ratio, equity positive) | 20 | Debt ratio < 0.5, equity > 0 |
| Cash trend / runway | 15 | Positive operating cash, ≥ 6 mo runway |
| Revenue trend | 15 | Stable/growing, no unexplained swings |

## 2. IRS Audit Readiness Score (0–100)
Starts at 100; subtract by highest open finding tier in `irs-audit-flags.md`.
| Deduction | Each |
|-----------|------|
| Critical finding (fraud badge / structuring / skimming) | −40 |
| High finding | −20 |
| Moderate finding | −8 |
| Low finding | −3 |
| Missing required doc (per Missing-Docs list) | −2 |
Cap total deduction per category sensibly; a single Critical alone caps the score ≤ 50.
State: "Score X/100 — driven by N findings (list)."

## 3. Bookkeeping Accuracy Score (0–100)
| Component | Weight | Full marks when… |
|-----------|--------|------------------|
| Reconciliation (gate-1 ties on every account) | 30 | All statements tie to the penny |
| Classification completeness | 25 | 0 items in Suspense; transfers/loans/equity correct |
| Trial balance / BS balances (gate-3) | 20 | Both balance exactly |
| Duplicate/error rate | 15 | No unresolved duplicates |
| Documentation coverage | 10 | Source for each material line |

## 4. Fraud Risk Score (0–100, HIGHER = MORE risk)
Inverse of the others — start at 0, **add** points for indicators (`forensic-ratios.md`).
| Indicator present | Add |
|-------------------|-----|
| Cash skimming / missing deposits | +30 |
| Structuring pattern | +30 |
| Duplicate payments / ghost vendor | +15 each (cap +30) |
| Undisclosed/related-party loan | +15 |
| Benford / period-end clustering anomaly | +10 |
| Personal expenses systematically disguised | +15 |
0–20 Low · 21–45 Moderate · 46–70 High · 71–100 Critical. List the driving transactions.

## 5. Cash Flow Stability Score (0–100)
| Component | Weight | Full marks when… |
|-----------|--------|------------------|
| Operating cash flow positivity | 35 | Positive across periods |
| Volatility (month-to-month swing) | 25 | Low variance |
| Runway / cushion | 20 | ≥ 6 months |
| Dependence on financing inflows | 20 | Ops self-funding, not loan-propped |

---

## Closing: CFO Action Plan
After the five scores, output a prioritized action plan, **highest financial risk → lowest**.
Each item: `Priority · Issue · Financial/legal exposure · Specific corrective action ·
Owner · Suggested deadline.` Tie each back to a finding and its source. This is the
deliverable the user acts on — make it concrete, not generic.
