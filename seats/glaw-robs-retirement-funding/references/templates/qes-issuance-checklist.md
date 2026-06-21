# QES Issuance Checklist — Private C-Corporation ROBS

> Canonical template for the seat's QES-issuance deliverable (Qualifying Employer Securities issued to a
> 401(k) plan in a Rollover-as-Business-Startup). Render to a Google-Doc-ready HTML with
> `bin/make_qes_checklist.py`; the agent then imports it to Google Docs via `~/.gcp/token.json`.
>
> **ATTORNEY/CPA WORK-PRODUCT — not legal/tax/investment advice.** A licensed ERISA attorney + CPA review,
> complete, sign, and file. The agent never opens accounts, rolls funds, issues stock, values securities, or
> transmits to the IRS/DOL. Figures + form revisions are **VERIFY**. Authorities: IRC §4975(d)(13), §4975(e)(8);
> ERISA §407(d)(5), §408(e), §409(l), §3(18); IRC §401(a), §410(b).

## 0. Threshold (all must be true before issuing QES)
- ☐ Entity is a **newly formed C-corporation** (not S-corp / LLC / partnership) — ROBS / §409(l)
- ☐ Corporation has adopted a qualified **401(k)/profit-sharing plan whose document expressly permits
  participants to invest in employer stock (QES)** — §401(a)
- ☐ A **TPA fluent in ROBS** is engaged
- ☐ Funds **directly rolled** into the plan trust (no participant receipt); **Form 1099-R** to be issued
- ☐ Plan trust holds **cash sufficient** to buy the QES at FMV — §408(e)

## A. Charter & capital structure (the stock must itself qualify)
- ☐ Certificate of Incorporation authorizes enough **common stock** for the issuance
- ☐ Class issued to the plan is **common stock with voting + dividend rights at least equal to the class with
  the greatest voting power and the greatest dividend rights** (the §409(l) test when no stock is readily
  tradable; auto-satisfied if a single class of common)
- ☐ No charter / shareholder agreement / buy-sell strips the plan's shares of voting or dividend rights
- ☐ Authorized-but-unissued share count adequate; par value recorded
- ☐ Cap table prepared (pre- vs post-issuance: plan % vs founder %)

## B. Independent valuation (private stock — load-bearing)
- ☐ Engage an **independent qualified appraiser / CPA** (not founder, TPA, or any disqualified person)
- ☐ FMV determined **as of a date contemporaneous with issuance** (good-faith FMV, ERISA §3(18), for a
  security with no generally recognized market)
- ☐ Valuation report **in hand and dated BEFORE** the plan pays (not back-filled)
- ☐ **Plan pays appraised FMV per share = adequate consideration**; founder may NOT take identical stock at a
  sweetheart/par price while the plan pays FMV
- ☐ Workpapers retained; methodology documented
- ☐ Calendar **annual re-valuation** + re-valuation at each significant event (subsequent investment,
  redemption, dividend)

## C. Issuance transaction (corporate mechanics)
- ☐ **Board resolution** authorizing issuance + sale of [#] shares to the Plan as QES at FMV/share
- ☐ **Stock Purchase / Subscription Agreement** with the Plan trustee (the Plan — not the individual — is the
  purchaser/record holder)
- ☐ **Payment flows from the Plan trust to the corporation** (shares × FMV) — the QES transaction
- ☐ **Stock certificate(s) issued in the name of the Plan / trustee**, held by the Plan
- ☐ **Stock ledger / cap table updated** to show the Plan as shareholder of record
- ☐ Cash used for **bona fide business purposes** (equipment, lease, franchise fee, working capital, reasonable
  W-2 payroll) — not personal use

## D. §4975 prohibited-transaction clearance (the three QES conditions)
- ☐ **Adequate consideration** — every leg at FMV; proportional; no sweetheart founder price
- ☐ **No commission / kickback / finder's fee** to the Plan (directly or indirectly); founder does not
  personally benefit off the rollover or issuance
- ☐ **QES-only** — the Plan's rolled funds buy only Qualifying Employer Securities (no real estate / unrelated
  assets)
- ☐ No prohibited furnishing of services / self-dealing / personal use by any disqualified person (founder,
  spouse, ascendants/descendants + their spouses, ≥50%-owned entities)

## E. Plan qualification & coverage
- ☐ Plan offered to **all eligible employees — current AND future** (no lock-out amendment) — §410(b)
- ☐ **Form 5300** determination-letter application considered/filed
- ☐ Owner's **W-2 compensation reasonable** for services rendered
- ☐ TPA engaged for ongoing testing + filings

## F. Filings & ongoing compliance calendar
| Obligation | Form | Cadence / note |
|---|---|---|
| Report the rollover | **1099-R** | At rollover — "failure to issue" is an IRS-flagged defect |
| Annual plan return — **from day one** | **5500 / 5500-EZ** | The <$250k one-participant exception does **NOT** apply to ROBS |
| C-corp income tax return | **1120** | Annual |
| Independent stock re-valuation | (report) | Annual + each significant event |
| **Stay a C-corp** | — | Do NOT elect S-corp / convert to LLC until **all QES is redeemed at current FMV** |
| Plan termination (on exit) | **5310** | After QES redemption, on wind-down |

## G. Audit / evidence binder (what the IRS will demand)
- ☐ Certificate of Incorporation + bylaws + authorized-share record ☐ Plan document + employer-stock language
- ☐ Determination letter (if obtained) ☐ Rollover paperwork + Form 1099-R ☐ Valuation report (dated
  pre-issuance) ☐ Board resolution ☐ Stock Purchase/Subscription Agreement ☐ Proof of payment plan→corp
- ☐ Stock certificate in the Plan's name ☐ Updated stock ledger / cap table ☐ Evidence of bona-fide business
  use ☐ Filed 5500/5500-EZ + 1120 ☐ Annual re-valuations

## H. Adversarial gate (mandatory before sign-off — survives-adversarial < 5 ⇒ no-file)
- ☐ **IRS EP examiner** — §4975 PT, QES adequate-consideration, amount-and-timing, plan language
- ☐ **DOL / EBSA** — fiduciary self-dealing, ERISA §407/§408(e)
- ☐ **Valuation examiner** — thin/stale/back-dated valuation; price ≠ FMV
- ☐ **Qualification reviewer** — §410(b) coverage, day-one 5500, C-corp-stays-C-corp, reasonable comp
- ☐ **Skeptical client CPA** — is ROBS worth it vs build-normally-then-fund-the-Roth? (most ROBS businesses fail)
- ☐ Surviving positions authority-verified; defects rebuilt (BLUE) and re-scored

## Sign-off
- ERISA attorney — reviewed & approved: ____________________  Date ______
- CPA — reviewed & approved: ____________________  Date ______
