# Taxability, Exemptions & Sourcing — What Is Taxed, and at Whose Rate

Once nexus exists (`nexus-and-economic-nexus.md`), the next questions are **what** is taxable,
**who** is exempt, and **whose rate** applies (sourcing). Each is decided **per state, per
product/service** — there is no single national answer. Build a **taxability matrix** and ground
every cell in the state's statute, regulation, or ruling.

> No fabricated taxability conclusions. If a product/service's status in a state is uncertain,
> say so and name the controlling statute/ruling to verify — never assert "taxable" or "exempt"
> without grounding.

## What is taxable: the three buckets

### 1 — Tangible personal property (TPP) — the default base

Most states tax **retail sales of tangible personal property** as the default, then carve out
exemptions. TPP is property that can be seen, weighed, measured, felt, or touched. The sale must
be a **retail sale** (sale to the end user / final consumer) — a sale **for resale** is not a
retail sale and is exempt with a valid certificate (below).

### 2 — Services — usually NOT taxed, but the trend is expanding

Historically most states taxed goods and **exempted services** unless specifically enumerated.
Many states now tax **specified** services — common taxed categories include certain
**fabrication/repair, installation, telecommunications, lodging, admissions, and personal
services** — but the enumerated list is **state-specific**. A handful of states (e.g.,
broad-base states) tax services much more widely. **Never assume a service is exempt**; check the
state's enumerated-services list.

- **Mixed/bundled transactions** (taxable TPP + nontaxable service for one price) are resolved by
  state-specific **bundling** and **true-object/dominant-purpose** rules. The bundling rule can
  make the **entire** charge taxable if a taxable item is included and the price is not separately
  stated.

### 3 — Digital goods & SaaS — the fastest-changing area

Digital products (downloaded software, e-books, streamed music/video) and **Software-as-a-Service
(SaaS)** are treated **very differently** across states:

- Some tax **digital equivalents** of taxable TPP (e.g., a downloaded book taxed like a printed
  book); others exempt digital goods absent a specific statute.
- **SaaS** in particular is a patchwork — taxed in some states (sometimes as a taxable "data
  processing" or "computer service," sometimes as the lease/use of prewritten software), exempt in
  others. The classification (sale of software vs. service vs. data processing) drives the answer.

→ This is the single most error-prone area. Always cite the state's specific statute/ruling on
digital goods or SaaS; quote any rate/threshold from `tax-legal-shared/current-figures.md`.

## Common exemptions

Even where an item is in the taxable base, the **transaction** may be exempt. Exemptions are
**entity-based** (who buys), **use-based** (how it's used), or **product-based** (what it is):

- **Resale** — purchase of goods (or taxable services) for **resale** in the ordinary course; the
  tax is collected later from the final consumer. Requires a valid **resale certificate**.
- **Manufacturing / production** — machinery, equipment, and sometimes consumables **used directly**
  in manufacturing or production for sale (the "integrated plant" / "direct use" tests vary by
  state). A common and valuable exemption; the scope (what counts as "used in manufacturing") is
  heavily litigated and state-specific.
- **Agricultural** — farm equipment, feed, seed, and supplies used in commercial agriculture.
- **Nonprofit / governmental** — sales **to** qualifying exempt organizations (§501(c)(3) status
  is a *federal income-tax* concept and does **not** automatically confer state sales-tax
  exemption — the state grants its own exemption and usually issues an **exemption certificate**).
- **Sale-for-resale of services**, **occasional/casual sale**, **interstate commerce**, and
  product-specific exemptions (groceries, prescription drugs, medical devices) — all state-specific.

## Exemption & resale certificates (the documentation rule)

An exemption claim is only as good as the **valid certificate on file**. The discipline:

- The **seller** must obtain a **properly completed** exemption/resale certificate from the buyer
  **at or near the time of sale** and retain it. Absent a valid certificate, the sale is
  **presumptively taxable** and the seller — not the buyer — bears the assessment on audit.
- A certificate accepted **in good faith** generally shifts liability to the buyer for misuse; a
  certificate that is **incomplete, expired, or facially defective** does not protect the seller.
- The **Streamlined Sales Tax** member states accept a uniform **Streamlined exemption
  certificate**; the **Multistate Tax Commission** offers a **Uniform Sales & Use Tax Exemption
  Certificate** accepted by many states — but **acceptance and conditions vary**; some states
  require their **own** form.
- **No invented certificate validity.** Do not treat a sale as exempt on the assumption a
  certificate exists — confirm the document and its completeness.

## Sourcing — origin vs. destination

Sourcing decides **which jurisdiction's rate** applies (state + county + city + special district).
Two regimes:

- **Destination-based** (the majority and the Streamlined default) — the sale is sourced to where
  the buyer **receives** the goods/service (the ship-to / delivery location). The seller applies
  the rate of the destination jurisdiction.
- **Origin-based** — the sale is sourced to the **seller's** location (the ship-from). A minority
  of states use origin sourcing for **intrastate** sales.
- **Interstate** sales into a state where the seller has nexus are virtually always **destination**-
  sourced. The combined rate is the **state + local** stack at the destination — a single state
  can have hundreds of rate combinations, which is why rate determination defers to the state's
  current rate table or a sourcing engine, not memory.

## How this seat applies it

1. **Classify each product/service** into TPP / service / digital-or-SaaS, per state.
2. **Test taxability** against the state's statute and enumerated lists; resolve bundling.
3. **Identify exemptions** and confirm a **valid certificate** is on file for each exempt sale.
4. **Source** each sale (destination vs. origin) and apply the combined state+local rate.
5. Record uncertainties as **red flags** with the controlling authority to verify — never paper
   over an unknown with an assumed answer.

---

*Sales-and-use-tax work-product, not legal, tax, or accounting advice, and not a substitute for a
licensed practitioner. Prepared for review by a licensed CPA / attorney. Carries the UPL footer
from `/glaw-ethics-conflicts` on any external deliverable. Cite the state's current statute;
verify every rate/threshold against `tax-legal-shared/current-figures.md`.*
