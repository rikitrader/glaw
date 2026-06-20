# Nexus & Economic Nexus — Where You Must Collect

Nexus is the constitutional and statutory link between a seller and a state that lets the state
require the seller to **collect and remit** its sales/use tax. It is tested **per state** — a
seller can have nexus in one state and none in the neighbor. The collection duty turns on nexus;
the *taxability* of the item is a separate question (see `taxability-and-exemptions.md`).

> Every dollar/transaction threshold below defers to `tax-legal-shared/current-figures.md` and to
> the state's own current statute — thresholds **differ by state and change**. Never quote a
> nationwide number as settled.

## The constitutional floor (why nexus exists)

Two clauses constrain a state's power to impose a collection duty:

- **Due Process Clause** — requires some minimum connection / purposeful availment.
- **Commerce Clause** — under *Complete Auto Transit, Inc. v. Brady*, 430 U.S. 274 (1977), a tax
  on interstate commerce must (1) apply to an activity with **substantial nexus**, (2) be fairly
  apportioned, (3) not discriminate against interstate commerce, and (4) be fairly related to
  state services. Sales-tax nexus analysis lives mostly in prong (1).

## Physical nexus

The traditional, still-valid basis. A seller has physical nexus when it has a sufficient
in-state physical presence, commonly:

- **Employees or agents** in the state (including a single resident employee, in many states).
- **Inventory** stored in the state — including goods held in a **third-party fulfillment
  warehouse** (a major exposure for marketplace/FBA sellers; the inventory location creates nexus
  even though the seller never set foot there).
- **Owned or leased real or tangible property** (offices, equipment, a server in some states).
- **Traveling representatives** soliciting sales in the state (subject to the narrow P.L. 86-272
  protection below).

*Quill Corp. v. North Dakota*, 504 U.S. 298 (1992), once held that **physical presence was
required** for a use-tax collection duty. *Quill* was **overruled** in 2018 — see *Wayfair* below.

### P.L. 86-272 (a narrow income-tax shield, not a sales-tax shield)

Public Law 86-272 (15 U.S.C. §§ 381–384) bars a state from imposing a **net income tax** on a
seller whose only in-state activity is **soliciting orders for tangible personal property**
approved and shipped from outside the state. **It does not protect against sales/use-tax
collection duties**, and the Multistate Tax Commission has taken the position that many internet
activities exceed mere solicitation. Flag P.L. 86-272 only for the income-tax seat
(`/glaw-tax-compliance`), not as a sales-tax defense.

## Economic nexus — *South Dakota v. Wayfair* (2018)

***South Dakota v. Wayfair, Inc.***, 138 S. Ct. 2080 (2018), **overruled the *Quill* physical-
presence rule**. The Court held that a state may require a remote seller to collect tax based on
its **economic and virtual contacts** with the state — i.e., **economic nexus** — and upheld
South Dakota's threshold (sales into the state exceeding a dollar amount **or** a transaction
count in the current or prior year) as not unduly burdensome, emphasizing the law's safe-harbor
for small sellers, no retroactivity, and South Dakota's membership in the Streamlined Sales Tax
agreement.

After *Wayfair*, **essentially every state with a sales tax adopted an economic-nexus statute.**

### The common threshold pattern (VERIFY per state)

Many states followed the South Dakota model: a remote seller establishes economic nexus when, in
the current or preceding calendar year, its sales into the state exceed a **dollar threshold**
**or** a **transaction count** (the often-cited `$100,000 / 200 transactions` pattern). But the
variations are material and must be checked each time:

- Some states use **only** a dollar threshold (dropping the transaction count entirely).
- The **measurement base** differs — *gross* sales vs. *retail* sales vs. *taxable* sales.
- The **lookback period** differs (current year, prior year, trailing 12 months).
- The threshold **amount** differs by state.

→ Quote the exact figure from `tax-legal-shared/current-figures.md` or the state's current
statute. Do not state a threshold from memory.

## Marketplace-facilitator laws

After *Wayfair*, states enacted **marketplace-facilitator** statutes shifting the collection duty
to the **marketplace** (e.g., a large online platform) for sales it *facilitates* on behalf of
third-party (marketplace) sellers. Key points:

- When the marketplace is the collecting party, the **marketplace seller** generally does **not**
  separately collect on those facilitated sales — but may still have to **register and file**
  (sometimes a zero/informational return) and must keep documentation that the facilitator
  collected.
- The seller's **direct** (non-marketplace) sales — its own website, phone, retail — are still
  the seller's responsibility, and those direct sales may **independently** cross the economic-
  nexus threshold.
- Definitions of "marketplace facilitator" and "facilitated sale" are **state-specific**; confirm
  whether a given platform/payment arrangement qualifies in the state.

## Click-through and affiliate nexus (pre- and post-*Wayfair*)

Before *Wayfair*, states reached remote sellers through agency-style theories that **survive** and
can still create nexus independent of the economic threshold:

- **Click-through nexus ("Amazon laws")** — an out-of-state seller is presumed to have nexus when
  in-state residents refer customers via a link in exchange for a commission and referred sales
  exceed a small threshold. Modeled on *N.Y. Tax Law § 1101(b)(8)(vi)*, upheld in
  *Overstock.com, Inc. v. N.Y. Dep't of Taxation & Finance*, 20 N.Y.3d 586 (2013).
- **Affiliate nexus** — an in-state affiliate (common ownership, shared trademarks, in-state
  services performed for the seller) attributes nexus to the out-of-state seller.

These remain relevant where a seller is below the economic-nexus threshold but has in-state
referral or affiliate relationships.

## How this seat applies it

1. **Inventory the seller's contacts per state** — people, property, inventory (incl. 3PL/FBA),
   reps, affiliates, referral programs, and **sales volume / transaction count** by state.
2. **Run the test per state**: physical first (any in-state presence?), then economic (does the
   current/prior-year base cross the state's threshold?), then the marketplace overlay (does a
   facilitator already collect?), then click-through/affiliate.
3. **Flag back-exposure** — if nexus was triggered in a prior period but the seller never
   registered or collected, that is a live liability (collected-but-not-remitted is worse). Route
   the remediation to `voluntary disclosure` (see `audits-and-voluntary-disclosure.md`) and
   `/glaw-tax-compliance`. Do not bury it.

---

*Sales-and-use-tax work-product, not legal, tax, or accounting advice, and not a substitute for a
licensed practitioner. Prepared for review by a licensed CPA / attorney. Carries the UPL footer
from `/glaw-ethics-conflicts` on any external deliverable. Cite the state's current statute;
verify every threshold against `tax-legal-shared/current-figures.md`.*
