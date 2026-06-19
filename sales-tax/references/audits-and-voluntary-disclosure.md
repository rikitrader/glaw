# Sales-Tax Audits, Liability & Voluntary Disclosure

A state DOR sales-tax audit tests two things: did you **collect** the right tax on your sales, and
did you **pay** use tax on your taxable purchases. Because sales tax is **trust money**, the
exposure reaches **individuals** personally and follows the business into the hands of **buyers
and successors**. This file covers the audit mechanics, the personal/successor liability traps,
and the two principal cleanup paths — **Voluntary Disclosure Agreements** and **amnesty**.

> Quote any look-back period, penalty rate, or threshold from the state's current rule or
> `tax-legal-shared/current-figures.md` — these are state-specific and change.

## The DOR sales-tax audit

- **Scope & period.** The auditor reviews an **audit period** (typically the open years under the
  state's statute of limitations — often three to four years, **longer or unlimited** for
  unfiled/unregistered periods or fraud). They examine sales records, exemption certificates,
  purchase invoices (for use tax), fixed-asset additions, and the general ledger.
- **The two findings that dominate.** (1) **Unsupported exemptions** — exempt/resale sales with no
  valid certificate on file are reclassified as taxable and assessed to the **seller**. (2)
  **Unaccrued use tax** — taxable purchases (supplies, equipment, software, items pulled from
  resale inventory) on which no tax was paid and no use tax self-assessed.

### Sampling

Sales-tax audits rarely examine every transaction. Auditors use **statistical or block sampling**:
they test a sample period or a stratified sample, compute an **error rate**, and **project** it
across the full audit period. Discipline for this seat:

- **Scrutinize the sample design** — a sample that is unrepresentative (e.g., a peak month, or a
  period before a process fix) over-projects the liability. A defensible **alternative sample** or
  a **detailed (actual) review** of a contested category can beat the projection.
- **Cure exemption certificates.** Many states allow a **post-audit period** to obtain missing
  exemption/resale certificates from customers; a cured certificate removes that transaction from
  the assessment. This is often the single largest reduction available.
- **Reconcile to the GL.** Tie the auditor's numbers to the posted ledger; an assessment that does
  not reconcile to the books is a red flag to raise, not accept.

## Successor / bulk-sale liability

When a business is **sold** (or its assets are), the **buyer can inherit the seller's unpaid
sales-tax liability** unless the state's **bulk-sale** procedure is followed:

- Most states require the **purchaser** to notify the DOR of a bulk sale and **withhold** enough of
  the purchase price to cover the seller's outstanding sales tax until the DOR issues a **tax
  clearance / certificate of no liability**.
- A buyer who skips this can be held liable for the seller's back tax up to the purchase price.
  In any acquisition, obtaining the **clearance certificate** is the standard protection — flag
  this to `/glaw-corporate-counsel` / M&A diligence whenever a deal touches a business with a
  sales-tax footprint.

## Responsible-person (personal) liability

Because collected sales tax is **trust-fund money**, states impose **personal liability** on the
**"responsible persons"** of the business — officers, directors, members, or employees who have
the **duty to collect/remit** and **control over** the funds — when the tax is collected but not
remitted. Key points:

- The liability **pierces the entity**: an LLC or corporation does **not** shield a responsible
  person from trust-fund sales-tax liability.
- The classic trigger is **commingling** — using collected tax for operations/payroll instead of
  remitting it. This is why the trust-fund liability must be kept un-commingled (see
  `registration-collection-remittance.md`).
- Treat responsible-person exposure as a **live risk** in any matter where collected tax was not
  timely remitted; route controls/governance to `/glaw-compliance` and surface it plainly.

## Voluntary Disclosure Agreements (VDAs)

A **VDA** is a state program that lets a taxpayer with **undisclosed back-liability** (e.g., nexus
triggered but never registered) come forward **voluntarily** in exchange for:

- A **limited look-back period** (commonly three to four years instead of the unlimited period that
  applies to a non-filer) — capping the historical tax.
- **Penalty waiver** (interest usually still applies).
- **Anonymity during negotiation** — the taxpayer (often through a representative) can negotiate
  the terms **before** identifying itself.

**Critical eligibility rule:** a VDA is generally available **only to taxpayers not yet
registered and not already contacted by the state.** Therefore:

- **Resolve the VDA before registering** prospectively (registration can disqualify the back
  period — see `registration-collection-remittance.md`).
- A VDA is **off the table** once the DOR has initiated contact (nexus questionnaire, audit notice,
  inquiry). **Timing is everything** — surface back-exposure early and move before the state does.
- Route execution to `/glaw-tax-compliance`.

## Amnesty

Periodically, states offer a **tax amnesty** — a defined window in which taxpayers can pay back
tax with **reduced or waived penalties (and sometimes interest)**, often **without** the
prospective-registration and not-yet-contacted constraints of a VDA. Amnesty terms are
**program-specific** and **time-limited**; when one is open it can be a better deal than a VDA for
an already-on-the-radar taxpayer. Track announced amnesty windows for states where back-exposure
exists.

## How this seat applies it

1. On audit: **scrutinize the sample**, **cure certificates**, **reconcile to the GL**, and contest
   over-projection — do not accept a projected assessment uncritically.
2. In any acquisition: insist on the **bulk-sale clearance certificate**; flag successor liability.
3. Wherever collected tax was not remitted: treat **responsible-person** exposure as live; fix
   controls and the commingling.
4. For undisclosed back-exposure: evaluate **VDA vs. amnesty**, **resolve before registering**, and
   move **before** the state makes contact. Route execution to `/glaw-tax-compliance`.

---

*Sales-and-use-tax work-product, not legal, tax, or accounting advice, and not a substitute for a
licensed practitioner. Prepared for review by a licensed CPA / attorney. Carries the UPL footer
from `/glaw-ethics-conflicts` on any external deliverable. Cite the state's current rule; verify
every figure against `tax-legal-shared/current-figures.md`.*
