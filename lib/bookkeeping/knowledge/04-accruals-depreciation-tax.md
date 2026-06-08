# Accruals, depreciation & tax

Original notes on timing, long-lived assets, payroll, and indirect tax.

## Cash vs accrual basis
- **Cash basis** — record revenue when cash is received and expense when cash is paid. Simple;
  used by very small businesses.
- **Accrual basis** — record revenue when *earned* and expense when *incurred*, regardless of
  cash. Required by GAAP and for most businesses above a size threshold. Gives a truer picture
  because it **matches** revenue with the expenses that produced it.

## Matching principle
Recognize expenses in the same period as the revenue they helped earn. Drives most adjusting
entries (depreciation spreads an asset's cost over the periods it's used; accrued wages match
labor to the period worked).

## Accruals and deferrals (the timing entries)
- **Accrued revenue** — earned but not yet billed/received (debit AR / credit revenue).
- **Accrued expense** — incurred but not yet paid (debit expense / credit a payable). E.g.
  wages earned in the last days of the month, paid next month.
- **Prepaid expense (deferred expense)** — paid in advance for a future benefit (an asset);
  expensed over time (e.g. prepaid insurance → insurance expense each month).
- **Deferred / unearned revenue** — cash received before the work is done (a liability);
  recognized as revenue as it's earned (subscriptions, retainers).

These are **non-cash** adjusting entries — exactly the entries a bank-only model can't post,
which is why GLAW's ledger accepts arbitrary balanced journal entries.

## Depreciation & amortization
- **Depreciation** — spreading the cost of a **tangible** fixed asset (truck, equipment) over
  its useful life. The entry: debit Depreciation Expense / credit **Accumulated Depreciation**
  (a contra-asset). No cash moves.
- **Amortization** — the same idea for **intangible** assets (software, patents) or for paying
  down a loan's principal.
- **Book value** — cost minus accumulated depreciation.
- **Straight-line** — equal depreciation each year: (cost − salvage) ÷ useful life.
- **MACRS** — the U.S. tax method (IRS Pub 946): accelerated, by asset class (e.g. 5-year for
  vehicles, 7-year for equipment), half-year convention. GLAW computes both with `glaw-depreciate`.
- **Section 179 / bonus depreciation** — provisions that let you expense some or all of an
  asset's cost in year one instead of depreciating it over time.
- **Salvage (residual) value** — estimated worth at the end of useful life.

## Payroll terms
- **Gross pay** — total earned before deductions. **Net pay** — what the employee takes home.
- **Withholding** — income tax held back from pay and remitted to the government.
- **FICA** — Social Security (6.2% to a wage base) + Medicare (1.45%), withheld from the
  employee and **matched** by the employer.
- **FUTA / SUTA** — federal and state unemployment taxes (employer-side).
- **W-2 vs 1099** — W-2 = employee (withholding, employer taxes); 1099 = independent
  contractor (no withholding). Misclassification carries penalties.
- **Payroll liability** — amounts withheld/accrued but not yet remitted (a liability you hold
  in trust).

## Sales & use tax
- **Sales tax** — collected from customers on taxable sales and remitted to the state; a
  **trust-fund liability**, never the company's money.
- **Use tax** — self-assessed on taxable purchases where no sales tax was charged.
- **Nexus** — the connection (physical or economic, post-*Wayfair*) that requires you to
  collect a state's sales tax.
