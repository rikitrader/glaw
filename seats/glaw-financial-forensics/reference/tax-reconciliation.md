# Tax Reconciliation — Books ↔ Returns

Map reconstructed activity to the filed/expected returns, find discrepancies, and estimate
audit adjustments with a defensible range. Label every estimate `[ESTIMATED]` with method.
Search the KB for method rules (`tax-accounting-methods-construction-contractors.md`,
`irs-rev-proc-16-29-accounting-method-changes.md`) and cite.

## Entity → Return map
| Entity | Income return | Where business income lands |
|--------|---------------|------------------------------|
| Sole prop / SMLLC | Form 1040 + **Schedule C** | Sch C Part I (gross) / Part II (expenses) → 1040; SE tax on Sch SE. |
| C-Corp | **Form 1120** | Corp pays tax; owner taxed on wages (W-2) + dividends. |
| S-Corp | **Form 1120S** + K-1 | Pass-through to shareholder 1040; **reasonable W-2 comp required**. |
| Partnership / multi-LLC | **Form 1065** + K-1 | Pass-through to partners; guaranteed payments. |
| Payroll | 941 (qtrly), 940 (FUTA), W-2/W-3 | Wages, withholding, trust-fund taxes. |
| Sales tax | State returns | Taxable sales vs collected/remitted. |

## Reconciliation procedure
1. **Gross receipts test (the core IRS move):**
   `Total bank deposits − non-income deposits (loans, transfers, owner capital, refunds) =
   reconstructed gross receipts.` Compare to Sch C line 1 / 1120 line 1a / 1120S line 1a /
   1065 line 1a. Any positive delta = **potential unreported income** → quantify.
2. **Expense tie-out:** reconstructed deductible expenses by category vs the return's
   deduction lines. Flag claimed-but-unsupported (no invoice) and supported-but-unclaimed.
3. **Schedule C line map (sole prop):** Advertising L8 · Car/truck L9 · Commissions L10 ·
   Contract labor L11 · Depreciation L13 · Insurance L15 · Interest L16 · Legal/prof L17 ·
   Office L18 · Rent L20 · Repairs L21 · Supplies L22 · Taxes/licenses L23 · Travel L24a ·
   Meals L24b (50%) · Utilities L25 · Wages L26 · Other L27a · COGS Part III.
4. **Officer comp check (1120S/1120):** distributions without reasonable W-2 salary →
   payroll-tax adjustment (see `irs-audit-flags.md` B5/D3).
5. **Payroll tie-out:** book wages = Σ W-2 Box 1 ≈ 941 lines; deposits via EFTPS match.
   Mismatch → trust-fund exposure (§6672).
6. **Sales-tax tie-out:** taxable sales × rate vs remitted; under-remittance = liability +
   penalty.
7. **Method check:** is the entity on a permissible method (cash/accrual/CCM/PCM §460)? Any
   method change needs **Form 3115** (Rev. Proc. 2016-29 automatic list — search KB).

## Discrepancy output (one row each)
`Return line · Reported $ · Reconstructed $ · Δ · Direction (under/over) · Likely adjustment ·
Penalty/interest exposure [ESTIMATED] · Supporting source-line.`

## Estimated Tax Exposure (deliverable #10)
For each adjustment: `Δ taxable income × marginal rate (+ SE 15.3% if Sch C) + accuracy
penalty (20% §6662, or 75% §6663 if fraud) + interest [ESTIMATED]`. Present a **range**
(conservative ↔ aggressive) and state every assumption. Never present a single false-precise
number for court.
