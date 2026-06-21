# Qualified Retirement Plan — Intake Form

Gather these facts, then run `bin/qp_intake.py` to scaffold the matter + the six council seat files. Anything
unknown stays on the gap list — do not guess. (Work-product for attorney/CPA/EA review; the agent never files.)

## A. Plan & sponsor
- **Matter name:** ____________________________________________
- **Plan sponsor (employer):** _________________________________  EIN: __________
- **Plan name & number (e.g., 001):** __________________________
- **Plan type:** ☐ 401(k)  ☐ profit-sharing  ☐ money-purchase  ☐ defined benefit / cash-balance  ☐ 403(b)  ☐ SEP  ☐ SIMPLE
- **Plan-year end (MM-DD):** __________
- **Recordkeeper / TPA / enrolled actuary:** ____________________
- **Document type:** ☐ IRS pre-approved (opinion letter #) ______  ☐ individually designed
- **Last restatement date (YYYY-MM-DD):** __________  **Determination letter on file?** ☐ yes ☐ no ☐ n/a

## B. Population
- **Total employees:** ______  **Eligible:** ______  **Participants (benefiting):** ______
- **HCEs (count):** ______  **NHCEs (count):** ______
- **Key employees (count):** ______  **Is the plan top-heavy (>60% to key employees)?** ☐ yes ☐ no ☐ unknown
- Any **long-term part-time** employees newly eligible? ☐ yes ☐ no

## C. Contributions & limits (current plan year)
- Plan year being audited: ______
- **ADP/ACP** testing performed & passed? ☐ pass ☐ fail ☐ safe harbor ☐ n/a
- Any participant **elective deferrals over §402(g)**? ☐ yes ☐ no
- Any **§415 excess** annual additions / benefits? ☐ yes ☐ no
- Compensation above the **§401(a)(17)** cap used anywhere? ☐ yes ☐ no
- Top-heavy **minimum contribution/benefit** provided (if top-heavy)? ☐ yes ☐ no ☐ n/a

## D. Vesting & distributions
- **Vesting schedule:** ________________________  100% at NRA & on termination? ☐ yes ☐ no
- **RMDs** for §401(a)(9)-age participants current? ☐ yes ☐ no ☐ none due
- **Involuntary cash-outs** above threshold without consent? ☐ yes ☐ no
- **QJSA/QPSA** offered (or valid profit-sharing exception)? ☐ yes ☐ no ☐ n/a
- **Direct-rollover** option + §402(f) notice given? ☐ yes ☐ no
- Any **assignment/pledge** of benefits outside loan/QDRO? ☐ yes ☐ no

## E. Coverage / nondiscrimination
- **§410(b) coverage** — NHCE benefiting __/__ ; HCE benefiting __/__ (run `qp_compliance_check.py coverage`)
- **§401(a)(4)** nondiscrimination tested? ☐ pass ☐ fail ☐ design-based safe harbor
- (DB only) **§401(a)(26)** minimum participation met? ☐ yes ☐ no ☐ n/a

## F. Funding, trust & prohibited transactions
- (DB / money-purchase) **§412 minimum funding** met (actuary certified)? ☐ yes ☐ no ☐ n/a
- Assets held **in trust**, used exclusively for participants (no diversion)? ☐ yes ☐ no
- **Disqualified persons** (sponsor, owners ≥50%, fiduciaries, family): _______________________
- Any **§4975 prohibited transaction** (sale/lease/loan/services/self-dealing with the plan)? ☐ yes ☐ no — describe: ______

## G. Reporting & known issues
- **Form 5500 / 5500-EZ** filed for all required years? ☐ yes ☐ no — gaps: ______
- **Form 1099-R** issued for all distributions? ☐ yes ☐ no
- Any **IRS/DOL notice, exam, or open correction**? ☐ yes ☐ no — describe: ______
- Hard deadlines (5500 due date, restatement deadline, RMD date, correction window): ______

## H. Authorization
- **Authorized scope:** review/analyze/draft only; no filing without named human approval.
- **Intake reviewer (named):** ____________________   **Date:** __________

---
### Scaffold command
```bash
python3 bin/qp_intake.py --matter "<A. matter name>" \
  --plan-type <401k|db|money-purchase|profit-sharing|403b|sep|simple> \
  --sponsor "<A. sponsor>" --plan-year-end <MM-DD> \
  --participants <B. participants> --last-restatement <A. YYYY-MM-DD>
```
Then fill `drafts/qualified-plan/facts.json` (true/false per requirement) and run the checker `audit`.
