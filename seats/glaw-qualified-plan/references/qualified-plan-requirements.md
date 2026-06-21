# A Guide to Common Qualified Plan Requirements — ingested

Source: IRS, *A Guide to Common Qualified Plan Requirements*
(https://www.irs.gov/retirement-plans/a-guide-to-common-qualified-plan-requirements), ingested 2026-06-21.

A qualified plan must satisfy the Internal Revenue Code **in form and in operation**. The 21 common requirements
below each map to a Code section, a test, a failure mode, and a correction path. Failing any one risks
**disqualification**: the trust loses its **§501(a)** tax exemption, the employer loses deductions, and vested
participants may be taxed currently. All dollar figures are inflation-indexed — treat every figure as **VERIFY**
against the current IRS COLA notice (`bin/qp_compliance_check.py limits`).

> Owning seat is shown in brackets — these are the council seats scaffolded by `bin/qp_intake.py`.

---

## 1. Minimum participation requirements — §410(a)  [Coverage & Nondiscrimination]
An employee must be allowed to participate by the **later of age 21 or one year of service** (a year = a 12-month
period with ≥1,000 hours). Entry dates must be **no later than the earlier of** (a) the first day of the plan year
after the requirements are met, or (b) **6 months after** they are met. *Long-term part-time* employees have
reduced service rules (SECURE / SECURE 2.0 — VERIFY current consecutive-year threshold).
**Failure:** excluding eligible employees or late entry dates. **Fix:** retroactive inclusion + corrective
contribution (EPCRS).

## 2. Operate in accordance with the plan document  [Plan Document & Qualification]
The plan must **cover all employees the document describes** and provide **exactly the benefits** the document
states. Operating off-document (paying benefits not in the document, or not following its terms) is an operational
failure. **Fix:** conform operations or amend (watch §411(d)(6), #3); EPCRS for past operation.

## 3. No cutback of accrued benefits — §411(d)(6)  [Plan Document & Qualification]
A plan amendment may **not** decrease any participant's **accrued benefit**, nor eliminate or reduce a **§411(d)(6)
protected benefit** — early-retirement benefits, retirement-type subsidies, or **optional forms of distribution** —
with respect to benefits already accrued. **Failure:** retroactive reduction. **Fix:** restore the protected
benefit; the amendment is void to the extent it cuts back.

## 4. 401(k) Actual Deferral Percentage (ADP) test — §401(k)  [Coverage & Nondiscrimination]
A cash-or-deferred arrangement must pass the **ADP test**: the average deferral percentage of **HCEs** may exceed
that of **NHCEs** only within the §401(k)(3) limits (1.25× or the lesser of 2× / +2 points). **Safe harbor**
designs (§401(k)(12)/(13)) are deemed to pass. **Failure:** excess contributions to HCEs. **Fix:** corrective
distribution / recharacterization of excess by the deadline, or QNEC; otherwise EPCRS.

## 5. Matching/employee contribution ACP test — §401(m)  [Coverage & Nondiscrimination]
Plans with **matching** or **after-tax employee** contributions must pass the **ACP test** (same structure as ADP,
applied to match + employee contributions). Safe-harbor match designs are deemed to pass. **Fix:** distribute/forfeit
excess aggregate contributions by the deadline, or EPCRS.

## 6. Elective deferral limit — §402(g)  [Limits & Top-Heavy]
A participant's **elective deferrals** across all plans are capped per calendar year, with an **age-50 catch-up**
and a **SECURE 2.0 super catch-up for ages 60–63**. Excess deferrals must be returned by April 15 of the next year.
**VERIFY** the year's figures (see limits table). Coordinated with §401(a)(30).

## 7. Section 415 contribution/benefit limits — §415  [Limits & Top-Heavy]
- **DC plans (§415(c)):** total **annual additions** (employer + employee + forfeitures) per participant are capped
  at the lesser of the dollar limit or 100% of compensation.
- **DB plans (§415(b)):** the **annual benefit** is capped at the lesser of the dollar limit or 100% of average
  high-3 compensation.
**VERIFY** both dollar figures. **Failure:** excess annual additions / excess benefit. **Fix:** correct under
EPCRS; §4972/§4979 excise via Form 5330 may apply.

## 8. Section 401(a)(17) compensation limit — §401(a)(17)  [Limits & Top-Heavy]
Only **compensation up to the annual limit** may be used to compute contributions and benefits. Using comp above
the cap inflates allocations/benefits and breaks nondiscrimination. **VERIFY** the year's figure.

## 9. Top-heavy requirements — §416  [Limits & Top-Heavy]
A plan is **top-heavy** if **>60%** of accrued benefits/account balances belong to **key employees** (an officer
above the indexed compensation threshold, a >5% owner, or a >1% owner with comp above $150,000). A top-heavy plan
must provide **minimum vesting** (3-year cliff / 6-year graded) and a **minimum contribution** (3% of comp for
non-keys) or minimum DB accrual (2%/yr up to 20%). **VERIFY** the key-employee threshold.

## 10. Minimum vesting requirements — §411  [Vesting & Distributions]
Employees must vest in employer contributions at least as fast as a permitted schedule (e.g., 3-year cliff or
6-year graded for defined contribution; **employee deferrals are always 100% vested**). Participants must be
**100% vested at normal retirement age** and on **plan termination / partial termination**. **Failure:** forfeiting
vested amounts; not 100%-vesting on termination. **Fix:** restore + EPCRS.

## 11. Required minimum distributions — §401(a)(9)  [Vesting & Distributions]
Distributions must begin by the **required beginning date** — April 1 of the year after the participant reaches the
**§401(a)(9) applicable age** (SECURE 2.0 moved it to 73, rising to 75 — **VERIFY** the participant's age band) or
retires (whichever the plan/ownership allows). **Failure:** missed/late RMD. **Fix:** make up the RMD; the
participant's excise tax (Form 5329) is reduced/waivable; plan corrects under EPCRS (a common VCP item).

## 12. Consent for distributions — §411(a)(11)  [Vesting & Distributions]
A plan may **not force a distribution** before normal retirement age (or 62, if later) **without the participant's
consent** if the vested benefit **exceeds the cash-out threshold** (indexed; SECURE 2.0 raised it — **VERIFY**).
Mandatory distributions above the lower threshold must default to an **automatic IRA rollover** (see #14).

## 13. Joint and survivor annuity — §401(a)(11) / §417  [Vesting & Distributions]
Benefits subject to the annuity rules must be paid as a **qualified joint & survivor annuity (QJSA)** with a
**qualified preretirement survivor annuity (QPSA)**, unless the participant elects out **with notarized spousal
consent**. A **profit-sharing/401(k) plan** can be exempt if it pays the full balance to the spouse on death and
offers no life annuity. **Failure:** paying a non-QJSA form without valid spousal consent.

## 14. Direct rollover requirements — §401(a)(31)  [Vesting & Distributions]
The plan must let a participant elect a **direct trustee-to-trustee rollover** of any **eligible rollover
distribution**, and must give the **§402(f) notice**. **Mandatory distributions** above the automatic-rollover
threshold (and not directly elected) must default to an **IRA rollover** for the participant. **Failure:** paying
cash without the direct-rollover option / §402(f) notice.

## 15. Assignment and alienation prohibition — §401(a)(13)  [Vesting & Distributions]
Benefits **cannot be assigned, pledged, or used as collateral**, except a **participant loan** that meets §72(p) and
a **Qualified Domestic Relations Order (QDRO)**. **Failure:** garnishment/assignment outside those exceptions.

## 16. Nondiscrimination requirements — §401(a)(4)  [Coverage & Nondiscrimination]
Contributions **or** benefits must **not discriminate in favor of HCEs**. Tested via design-based safe harbors,
the general test (rate-group testing), or cross-testing for DC plans. Also covers nondiscriminatory availability of
benefits, rights, and features. **Failure:** HCE-tilted allocations/benefits. **Fix:** corrective amendment
(§401(a)(4)) / additional NHCE contributions; EPCRS.

## 17. Coverage requirements — §410(b)  [Coverage & Nondiscrimination]
The plan must pass **one of**: (a) **ratio-percentage test** — the percentage of NHCEs benefiting is ≥ **70%** of
the percentage of HCEs benefiting; or (b) the **average benefit test** (nondiscriminatory classification + average
benefit percentage ≥ 70%). **Failure:** coverage below the line. **Fix:** expand coverage retroactively / corrective
amendment (§1.401(a)(4)-11(g)); EPCRS. (See `bin/qp_compliance_check.py coverage`.)

## 18. Defined benefit minimum participation — §401(a)(26)  [Coverage & Nondiscrimination]
A **DB plan** must benefit the **lesser of 50 employees or the greater of 40% of all employees or 2 employees**, on
each day of the plan year. Applies to DB plans only (not DC). **Failure:** too few benefiting. **Fix:** amend to
cover enough employees.

## 19. Minimum funding requirements — §412  [Funding, Trust & Fiduciary]
**DB and money-purchase pension plans** must make the **required minimum contribution** determined by an **enrolled
actuary** (§430 for single-employer DB) or by the plan's formula (money purchase). **Failure:** funding deficiency.
**Fix/penalty:** **§4971 excise tax** via **Form 5330**; correct the shortfall.

## 20. Exclusive benefit requirement — §401(a)  [Funding, Trust & Fiduciary]
All plan assets must be held **in trust** and used **exclusively for the benefit of employees and their
beneficiaries** (and defraying reasonable plan expenses); **no diversion** to the employer or insiders before all
liabilities are satisfied. This is the spine: any diversion is both a **§4975 prohibited transaction** and a
qualification failure. **Fix:** undo the diversion + §4975 excise (Form 5330) + EPCRS.

## 21. Reporting and disclosure requirements  [Reporting & Correction]
- **Form 5500 / 5500-EZ / 5500-SF** annually (one-participant plans use 5500-EZ; the **<$250k exception** exempts
  small one-participant plans — **but a ROBS plan files anyway**, see `/glaw-robs-retirement-funding`). Large plans
  (generally ≥100 participants) require an **independent audit** (Schedule H + accountant's opinion).
- **Form 1099-R** for distributions; **§402(f)** rollover notice; **SPD / SMM**; periodic **participant statements**;
  for DB, the **annual funding notice**.
**Failure:** late/incomplete 5500 (DOL **DFVCP** for relief), missed 1099-R, missing notices. **Fix:** file late via
DFVCP; issue corrected forms.

---

## Cross-cutting consequences of disqualification
- **Trust:** loses §501(a) exemption → trust earnings become taxable.
- **Employer:** loses the deduction for contributions (timing/limits).
- **Employees:** **vested** amounts can become **currently taxable**; rollovers from a disqualified plan are
  jeopardized.
- **Excise taxes:** §4971 (funding), §4972 (nondeductible contributions), §4975 (prohibited transactions),
  §4979 (excess contributions) — all via **Form 5330**.

## Where each fix lives
Operational and document failures are corrected through **EPCRS** (Self-Correction Program, Voluntary Correction
Program via **Form 8950**, or Audit Closing Agreement Program) — see `correction-and-determination.md`. Plan-document
qualification can be confirmed in advance through the **Determination Letter** program (Form 5300 / 5307 + 8717 user
fee). The IRS **Fix-It Guides** (401(k), 403(b), SEP, SIMPLE, SARSEP) give plan-type-specific find/fix/avoid tables.
