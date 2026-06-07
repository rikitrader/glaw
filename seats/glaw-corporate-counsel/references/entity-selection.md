# Entity Selection & State of Formation

State law forms the entity; **federal tax law taxes it** (IRS FS-2008-22). Pick the entity for
liability + governance + investor fit, then coordinate the *tax* election with `tax-strategy`.
Verify current fees/rules per SKILL.md Step 1a.

## Entity matrix

| Entity | Liability | Default tax | Owners | Best for | Notes |
|---|---|---|---|---|---|
| **Sole proprietorship** | None (personal) | Schedule C | 1 | Tiny/test | No formation; full personal liability |
| **General partnership** | None (joint & several) | 1065 passthrough | 2+ | Informal co-ownership | Avoid for liability reasons |
| **LP / LLP** | Limited (LPs/partners) | Passthrough | 2+ | Real estate, professional firms | GP liable in LP unless GP is an entity |
| **LLC** | Limited | Passthrough by default; **can elect S or C** | 1+ | Closely held, real estate, holding co | Most flexible; single-member = "disregarded" (FS-2008-22); operating agreement governs |
| **C-corporation** | Limited | Entity 21% + dividend double-tax | unlimited | VC-backed, **QSBS**, going public | Investor standard; supports dual-class & options |
| **S-corporation** *(election, not an entity)* | Limited (corp/LLC) | Passthrough + payroll-tax split | ≤100, **US persons only**, one class | Profitable owner-operated SMB | No foreign/entity owners; one class of stock — *incompatible with dual-class* |
| **PBC (public benefit corp)** | Limited | Like a C-corp | unlimited | Mission + profit | Directors weigh a stated public benefit |
| **Nonprofit (501(c)(3))** | Limited | Tax-exempt if approved | members/none | Charitable/educational | Needs IRS Form 1023; no private inurement |

## State of formation

| Choice | Why | Watch |
|---|---|---|
| **Home/operating state** | Simplest, cheapest if single-state | Default for local LLCs/SMBs |
| **Delaware** | DGCL + Court of Chancery; investor/VC expectation; flexible | Franchise tax; foreign-qualify where you operate |
| **Texas** | TBOC (eff. Sept 2025), business courts, controller-friendly; **Tesla/SpaceX redomiciled** | Margin tax; newer case law |
| **Nevada / Wyoming** | No state income tax; privacy; statutory business-judgment protection | Still taxed where you operate; substance matters |

> **Formation ≠ tax home.** You owe tax and must **foreign-qualify** wherever you have employees,
> property, or sales — regardless of the state on the certificate.

## Foreign owners (trade.gov)
A foreign person/entity can form and own a US entity with **no citizenship/residency/visa**
requirement; can sit on the board. Common choices: a **US C-corp** (clean for US investors,
avoids passthrough filing complexity for foreign owners, and isolates US tax) or an **LLC** (but
a foreign-owned single-member LLC has special IRS reporting — Form 5472). **S-corp is off the
table** (US-person shareholders only). Ownership doesn't grant work authorization (immigration is
separate), and foreign-owned entities may trigger CTA/BOI + withholding — coordinate with
`tax-strategy` + immigration counsel.

## Family business / farm & ranch (CFRA themes)
For farms/ranches and family operations, the same menu applies, with emphasis on **succession +
liability + keeping the asset in the family**: an **LLC** (or multiple LLCs separating land from
operations) for liability isolation and easy fractional gifting to the next generation; **family
LP** for centralized control + valuation discounts on gifts; and coordination with **trusts**
(`tax-strategy`) for estate/succession. Lease land from a land-holding entity to the operating
entity at arm's length.

## How to recommend
1. Liability shield needed → at least an LLC or corp (never sole prop/GP for real operations).
2. Raising venture capital / want QSBS / going public → **Delaware C-corp**.
3. Closely held, passthrough, flexible → **LLC** (elect S if owner-operated and eligible).
4. Founder must keep voting control through financing/sale → C-corp with **dual-class** (Step 5).
5. Always: confirm the *tax* election with `tax-strategy` and foreign-qualify where you operate.
