# Skadden / Practical Law 409A Equity Pitfalls Map

Source: Skadden-hosted Practical Law checklist, *Equity Pitfalls under Section
409A Checklist* (2014), by Regina Olshan, Daniel Hogans, and Russell E. Hall:
https://www.skadden.com/-/media/files/publications/2015/02/equity-pitfalls-under-section-409a-checklist.pdf

Use this file as the legal-audit overlay for 409A valuation matters. It is not a
substitute for counsel review; it is the checklist the seat must surface before a
draft valuation is relied on for grants.

## Controls to Map Into `review_controls`

| Control | Why it matters | Intake key |
|---|---|---|
| Private-company FMV method is reasonable. | The checklist flags that private-company option exercise price work must rest on a reasonable valuation method. | `valuation_method_reasonable` |
| Valuation is fresh and reflects material information. | The checklist notes that a valuation generally should be no more than 12 months old and should refresh for material information. | `valuation_freshness_confirmed`, `material_events_reviewed` |
| Exercise price is at least FMV on grant date. | Options intended to be excluded from 409A need an exercise price no less than grant-date FMV. | `option_exercise_price_fmv_on_grant_date`, `option_grant_dates_confirmed` |
| Public-company average-price method controls are satisfied or N/A. | Average trading price methods require tight recipient, share-count, timing, and irrevocability controls. | `average_price_period_controls` |
| Option modifications are reviewed. | Repricing, term extension, deferred option gains, and certain in-the-money modifications can create 409A exposure. | `option_modification_reviewed` |
| Dividend-equivalent rights are reviewed. | Dividend equivalents that terminate on exercise can be treated as an indirect exercise-price reduction. | `dividend_equivalent_rights_reviewed` |
| RSU documents outside the plan are reviewed. | Employment, severance, and change-in-control agreements can change RSU 409A status. | `rsu_documents_reviewed` |
| RSU short-term deferral position is tested. | Retirement, good-reason, and post-termination non-compete vesting can undermine short-term deferral treatment. | `rsu_short_term_deferral_checked` |
| RSU payment schedules and event definitions are 409A-compliant. | RSUs subject to 409A require compliant payment timing, event definitions, and specified-employee delay where applicable. | `rsu_payment_schedule_409a_compliant` |
| Release timing cannot let the employee choose the payment year. | Release execution/revocation conditions can create impermissible payment timing control. | `release_timing_reviewed` |

## Required Reviewer Posture

- **Equity-awards counsel** owns RSU, option, release, modification, dividend-equivalent, and public-company average-price controls.
- **Appraiser** owns valuation-method reasonableness, valuation freshness, material-event refresh, DLOM, OPM, backsolve, PWERM, and waterfall assumptions.
- **Auditor/tax reviewer** owns ASC 718/820 consistency, cheap-stock exposure, grant-date evidence, board approvals, and audit-trail sufficiency.

Every open control remains visible in `results.json.legal_audit`, the memo's
Legal/Appraiser Audit Gate, and the RED/BLUE residual matrix.
