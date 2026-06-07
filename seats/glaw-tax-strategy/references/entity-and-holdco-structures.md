# Entity & Holding-Company Structures

The chassis everything bolts onto. Verify current rates/limits per SKILL.md Step 1a.

## Entity choice (model both — post-OBBBA the math shifted)

| Entity | Taxed | Best for | Key levers / traps |
|---|---|---|---|
| **Sole prop / SMLLC** | Schedule C, full SE tax | Tiny/new | Simplest; no SE-tax split; QBI eligible |
| **S-corp** (or LLC w/ S-election) | Passthrough; salary + distribution | Profitable owner-operated SMB | Pay **reasonable salary**, take rest as distribution → saves the 15.3% SE/payroll on the distribution; QBI §199A 20% (SSTB phase-out for service pros) |
| **Partnership / multi-LLC** | Passthrough, flexible allocations | Multi-owner, real estate | Special allocations, basis planning, §754 step-up |
| **C-corp** | 21% entity rate, dividends double-taxed | Startups seeking QSBS, retained-earnings reinvestment, fringe benefits | **QSBS §1202**; accumulate at 21% vs top individual rates; watch accumulated-earnings & PHC traps |

**Reasonable compensation** is the S-corp's pressure point — set it defensibly (comp studies);
too-low salary is the #1 S-corp audit issue.

## Holdco / Opco architecture

```
        Holding Co (holds IP, cash, ownership)
        /            |               \
     Opco 1        Opco 2        Real-estate LLC (leases to Opcos)
```
- **Liability isolation** — each operating business in its own entity; valuable assets (IP, real
  estate, cash) in separate holding entities a lawsuit can't reach.
- **Tax-free intercompany dividends** — dividends from a subsidiary to a corporate parent get the
  **dividends-received deduction** (often 100% in a consolidated/≥80% group).
- **Clean exit** — sell an Opco without disturbing the rest; QSBS can apply at the Opco level.
- **Real-estate LLC** owns the building and **leases to the Opco** at market rent — shifts profit
  to a lower-taxed/depreciation-sheltered entity (must be arm's-length, §482).

## Management company

A central **management/services company** that provides real services (admin, IP, executive,
back-office) to the operating entities for an **arm's-length fee**. Legitimately centralizes
costs, concentrates retirement-plan funding, and can shift income — **but only for real services
at a defensible price**; a hollow management fee with no functions is the classic §482 / economic-
substance loss. Document the services, the people, and the pricing.

## QSBS — §1202 (the founder crown jewel)

- **C-corp** stock, original issuance, ≤ **$75M** aggregate gross assets at/after issuance
  (post-7/4/2025 stock; was $50M), held by a non-corporate holder.
- **Exclusion** (stock acquired after 7/4/2025): **50% at 3 yrs, 75% at 4 yrs, 100% at 5 yrs**;
  cap = greater of **$15M** (inflation-indexed after 2026) **or 10× basis** *per issuer*. Pre-
  7/4/2025 stock keeps the old **$10M / 5-yr / 100%** rule. Unexcluded gain at 3–4 yrs is taxed
  at **28%**.
- **Stacking** — gift shares to multiple non-grantor trusts / family members so each gets its own
  per-issuer cap (multiplies the exclusion). Real gifts, real trusts.
- Excludes most service businesses (SSTBs) — it's aimed at operating/tech/product companies.

## State of formation

- **Delaware** — default for venture-backed C-corps (case law, investor expectation).
- **Wyoming / Nevada** — privacy + no state income tax for the holding entity (but you're taxed
  where you operate/reside, not where you form — formation state ≠ tax home).
- Don't confuse **formation** with **nexus**: you owe tax where you have employees, property, or
  sales, regardless of the state on the certificate.
