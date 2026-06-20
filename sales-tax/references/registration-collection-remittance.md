# Registration, Collection & Remittance — The Mechanics

Once nexus and taxability are fixed, the operational cycle is: **register** in each state where
you must collect → **collect** the correct tax at the point of sale → **accrue** it as a trust-
fund liability → **file** the return on the assigned frequency → **remit** the money. Sales tax is
**money held in trust for the state**; it is never the company's to spend.

> Quote any registration threshold, filing-frequency dollar band, fee, or discount rate from
> `tax-legal-shared/current-figures.md` or the state's current rule. They differ by state and
> change.

## 1 — Register (permit before you collect)

- A seller must obtain a **sales-tax permit / registration / seller's permit** from each state's
  Department of Revenue (DOR) / Comptroller / Tax Commission **before** collecting tax in that
  state. Collecting without a permit, or charging "tax" you are not registered to collect, is
  itself a violation in many states.
- **Register only where you have nexus** — registering everywhere needlessly creates filing
  obligations (and zero-return penalties) in states where you have no duty.
- **Order of operations matters when there is back-exposure.** If nexus was triggered in prior
  periods and tax was not collected, **registering prospectively can foreclose a Voluntary
  Disclosure Agreement** for the back period (states generally will not grant a VDA to an
  already-registered taxpayer). Resolve the back period **first** — route to
  `audits-and-voluntary-disclosure.md` and `/glaw-tax-compliance` **before** registering.

## 2 — Collect (charge the right tax)

- Collect tax at the **combined destination (or origin) rate** on each **taxable** sale, applying
  exemptions only where a **valid certificate** is on file (see `taxability-and-exemptions.md`).
- **Separately state** the tax on the invoice/receipt where the state requires it. Tax collected
  is **not revenue** — it is a liability.
- If you **over-collect** or **collect tax you were not required to collect**, most states require
  you to **remit it anyway** (you cannot keep mis-collected "tax") or refund it to the customer per
  the state's procedure.

## 3 — Accrue the trust-fund liability (the journal entry)

```
Dr  Cash / Accounts Receivable (tax collected)
        Cr  Sales-tax payable (trust-fund liability)
```

On remittance:

```
Dr  Sales-tax payable
        Cr  Cash
```

Validate the entry through `/glaw-bookkeeping`; the payable ties out in `/glaw-close`. **Never let
the sales-tax payable be spent on operations** — commingling is the fact pattern that produces
**responsible-person personal liability** (see `audits-and-voluntary-disclosure.md`).

## 4 — File on your assigned frequency

States assign a **filing frequency** based on the seller's tax liability volume — higher liability
= more frequent filing:

- **Monthly** — high-volume sellers.
- **Quarterly** — mid-volume.
- **Annual** — low-volume / small sellers.
- Some states also require **prepayments / accelerated remittance** for the largest sellers.

The DOR sets and can **change** the frequency; the assigned frequency and due date (often the
20th of the month following the period, but state-specific) drive the filing calendar. **A
"zero return" is usually still required** for an active registration with no sales — missing it
draws a late-filing penalty even with no tax due. Route every recurring due date to
`/glaw-docket`.

- Many states grant a **vendor collection allowance / timely-filing discount** (the seller keeps a
  small percentage of tax collected for filing on time); amount and caps are state-specific —
  defer to `tax-legal-shared/current-figures.md`.

## 5 — Use tax (the complement to sales tax)

Use tax is the mirror of sales tax: it applies to the **storage, use, or consumption** of taxable
property/services in a state when **sales tax was not paid** at purchase. It prevents avoidance by
buying out of state.

- **Seller's use tax** — a remote seller with nexus collects "use tax" on sales into the state
  (functionally the same collection duty, labeled differently in some states).
- **Consumer (purchaser's) use tax** — the **buyer** self-assesses and remits use tax on taxable
  goods/services bought without tax (e.g., out-of-state purchases, internet purchases from a non-
  collecting seller, items pulled from resale inventory for own use). This is a frequent audit
  finding: a business that pays no use tax on its taxable purchases is a standard auditor target.
  Self-accrue use tax on the purchase side:

```
Dr  Expense / Asset
        Cr  Use-tax payable
```

## Streamlined Sales Tax (SST)

The **Streamlined Sales and Use Tax Agreement (SSUTA)** is a multistate cooperative effort
(administered through the Streamlined Sales Tax Governing Board) to **simplify and standardize**
sales-tax administration across member states. Relevance for this seat:

- **Uniform definitions**, **uniform exemption certificate**, **simplified rate/sourcing**, and a
  **single registration (SSTRS)** covering all member states.
- **Certified Service Providers (CSPs)** — SST-certified software that calculates, files, and
  remits for the seller, often with **state-funded** compensation for **volunteer** sellers (those
  without other nexus in the state). This is a meaningful compliance-cost reducer for remote
  sellers.
- *Wayfair* expressly cited South Dakota's SST membership as reducing the burden on remote sellers
  — SST participation is part of why economic-nexus regimes are sustainable.

Not all states are SST members; confirm membership and the current CSP program before relying.

## How this seat applies it

1. Resolve any **back-exposure first** (VDA before registration).
2. **Register** only where nexus exists; capture the assigned **frequency** and **due dates**.
3. **Collect** at the correct combined rate; book the **trust-fund liability**, un-commingled.
4. **Self-accrue use tax** on the purchase side; this is the commonly missed half.
5. **File on time** (including zero returns); claim the timely-filing discount where allowed;
   route all deadlines to `/glaw-docket`. The payable ties out in `/glaw-close`.

---

*Sales-and-use-tax work-product, not legal, tax, or accounting advice, and not a substitute for a
licensed practitioner. Prepared for review by a licensed CPA / attorney. Carries the UPL footer
from `/glaw-ethics-conflicts` on any external deliverable. Cite the state's current rule; verify
every figure against `tax-legal-shared/current-figures.md`.*
