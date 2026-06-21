# Correction (EPCRS), Determination Letters, Fix-It Guides & the §4975 / Form 5330 map

Companion to `qualified-plan-requirements.md`. When the 21-requirement audit finds a ❌, this is how it gets fixed,
confirmed, or penalized. Ingested 2026-06-21; **VERIFY** procedure numbers and dollar thresholds against the current
Revenue Procedure / IRS notice before reliance.

---

## 1. EPCRS — Employee Plans Compliance Resolution System
The IRS program for correcting plan failures so the plan keeps its qualified status. Governed by the current EPCRS
**Revenue Procedure** (Rev. Proc. 2021-30 and its SECURE 2.0 expansions — **VERIFY** the live Rev. Proc.). Three
programs:

| Program | When | How | Cost |
|---------|------|-----|------|
| **SCP — Self-Correction Program** | Eligible operational failures (and certain document failures); insignificant failures anytime; significant failures within the correction window | Self-correct, **no IRS filing, no fee**; keep documentation | $0 (internal cost) |
| **VCP — Voluntary Correction Program** | Failures not eligible for SCP, or where the sponsor wants IRS sign-off; **must not be under exam** | Submit **Form 8950** (+ correction description) via **pay.gov**; IRS issues a compliance statement | IRS **user fee** (asset-based — VERIFY) |
| **Audit CAP — Closing Agreement Program** | Failure found **on IRS examination** | Negotiated **closing agreement** + sanction | Negotiated sanction (much higher) |

**Correction principles (EPCRS §6):** put the plan and participants in the position they would have been in had the
failure not occurred (full correction, all affected participants/years, reasonable and consistent method, restore
earnings). The four failure types: **plan-document**, **operational**, **demographic** (e.g., coverage/§410(b)),
and **employer-eligibility**.

**Form 8950** (`forms/f8950.pdf`) = the VCP application. Submitted electronically via pay.gov with the user fee.

## 2. Determination Letter program (confirm the document in advance)
The IRS will rule on whether the plan **document** meets §401(a). The program is now limited (the IRS curtailed
ongoing individually-designed determination letters — **VERIFY** current open windows / cycles):

| Form | Use | Notes |
|------|-----|-------|
| **Form 5300** (`forms/f5300.pdf`) | Determination for an **individually-designed plan** (initial qualification, certain terminations, limited cycles) | Most detailed application |
| **Form 5307** (`forms/f5307.pdf`) | Determination for an **adopter of a pre-approved (volume submitter)** plan, in limited cases | For modified pre-approved plans |
| **Form 5310** (`forms/f5310.pdf`) | Determination on **plan termination** | Used at wind-down |
| **Form 8717** (`forms/f8717.pdf`) | **User fee** transmittal for the determination application | Pay the fee with the app |

Most employers now use IRS **pre-approved plans** (the document vendor's IRS opinion letter covers form qualification),
which is why ongoing 5300 filings are limited.

## 3. IRS Fix-It Guides (plan-type-specific find/fix/avoid)
Referenced from the qualified-plan page — practical "mistake → find it → fix it → avoid it" tables:
- **401(k) Plan Fix-It Guide** — the master for the §401(k) requirements above.
- **403(b) Plan Fix-It Guide** — for §403(b) tax-sheltered annuities.
- **SEP Plan Fix-It Guide** — simplified employee pensions (Form 5305-SEP).
- **SIMPLE IRA Plan Fix-It Guide** — SIMPLE IRAs (Form 5304/5305-SIMPLE).
- **SARSEP Plan Fix-It Guide** — grandfathered salary-reduction SEPs.
Pull the current online guide for the plan type before drafting a correction; they cross-reference the EPCRS method
and the COLA limits.

## 4. §4975 prohibited transactions → Form 5330 excise map
A **disqualified person** (employer/sponsor, fiduciaries, ≥50% owners, family members, and entities they control)
may not engage in any of the **six prohibited acts** with the plan: (1) sale/exchange/lease of property;
(2) lending/extension of credit; (3) furnishing goods, services, or facilities; (4) transfer/use of plan assets;
(5) fiduciary self-dealing; (6) receipt of consideration by a fiduciary. A QDRO and a compliant participant loan
are statutory exceptions.

**Excise tax tiers (§4975):** an initial tax on the **amount involved** (the first-tier rate — VERIFY current %),
escalating to **100%** if not corrected within the taxable period. Reported and paid on **Form 5330**
(`forms/f5330.pdf`). The same Form 5330 also reports **§4971** (funding deficiency), **§4972** (nondeductible
contributions), and **§4979** (excess ADP/ACP contributions).

> Prohibited transactions also threaten the **exclusive-benefit rule (#20)** and therefore qualification itself —
> screen them first. Deeper §4975 analysis for retirement-capital deals lives in `/glaw-robs-retirement-funding`.

## 5. Late / missing Form 5500 relief — DFVCP
A late or missing **Form 5500** is corrected through the **DOL Delinquent Filer Voluntary Compliance Program
(DFVCP)** — file the delinquent return through **EFAST2** and pay the reduced DFVCP penalty (capped per plan).
One-participant (5500-EZ) late filers use the **IRS** penalty-relief program for non-Title-I plans, not DFVCP.

## 6. The correction decision tree (how this seat routes a ❌)
1. **Document failure** (missed restatement / off-document operation) → amend; if outside SCP, **VCP (Form 8950)**;
   confirm form via the **Determination** program if individually designed.
2. **Operational failure** (ADP/ACP, §415 excess, late RMD, late deposits, coverage operation) → SCP if eligible &
   timely; else VCP.
3. **Demographic failure** (§410(b) coverage, §401(a)(4), §401(a)(26)) → corrective **(a)(4)-11(g) amendment** +
   contributions; VCP if needed.
4. **Prohibited transaction (§4975)** → unwind + **Form 5330** excise + (if it tainted exclusive benefit) EPCRS.
5. **Late Form 5500** → **DFVCP** (Title I) or IRS 5500-EZ penalty relief (non-Title-I).

Every chosen path ships with: the corrective action, the form, the deadline (docket it), and the cost — then through
the `/glaw-adversarial` EPCRS-specialist lens before sign-off.
