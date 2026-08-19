# Founder Control Stack Lane

This lane is the cross-strategy control architecture for a founder who wants durable voting and
governance control after outside investment. It combines charter-level dual/multi-class voting
with class protections and a DGCL §122(18) contractual consent overlay. It is an attorney/CPA
work-product scaffold, not a legal recommendation or filing instrument.

## Route and intersection

Attach this lane to the existing `founder-unicorn`, `tax-system`, `fortune500-enterprise`,
`founder-governance`, `uhnw-family-office`, PE/VC, and fund-regulatory lanes as facts require.
It applies to operating corporations, venture-backed companies, PE-backed platforms, GP and
management-company structures, funds with portfolio-company control rights, roll-ups, and
founder succession or trust structures.

## Control stack

1. Certificate of incorporation: Class A investor common, Class B founder common, and optional
   Class C non-voting/economic common; votes, conversion, separate-class votes, director
   designation, and adverse-change protections.
2. Bylaws: notice, quorum, meetings, record dates, voting mechanics, committees, and procedures.
3. Board and stockholder resolutions: authorization, issuance, financing, equity plan, and
   consent records.
4. Founder Rights Agreement: §122(18) reserved matters, consent, information, anti-circumvention,
   amendment/waiver locks, and sunset mechanics.
5. Voting Agreement: director elections, founder nominees, investor nominees, and agreed voting.
6. Financing and equity documents: preferred rights, protective provisions, transfer limits,
   option/RSU/SAFE/note mechanics, and disclosure interfaces.
7. Accounting and control layer: legal cap table, vote ledger, beneficial ownership, conversion,
   dilution, ASC 718, valuation/409A, tax, audit, and disclosure reconciliation.

## Required design work

The model must separately calculate economic ownership, voting power, board control, Class B
separate-vote power, contractual consent power, and sunset outcomes. It must model each financing
round, option-pool increase, SAFE/note conversion, preferred conversion, PE investment, fund or
portfolio-company transaction, and prohibited-transfer event.

Illustrative math only:

```text
Founder: 20M Class B × 20 votes = 400M votes
Investors: 80M Class A × 1 vote = 80M votes
Total: 480M votes
Founder voting power: 83.3%
Founder economic ownership: 20%
```

The ratio and thresholds are negotiated facts, not defaults. The packet must show sensitivity
cases at relevant ownership levels and identify the point where ordinary, protected,
supermajority, and separate-Class-B matters change outcome.

## 5.01% control invariant

For founder economic ownership `p` and Class B votes per share `M`, assuming all non-founder
shares carry one vote, founder voting power is:

```text
Founder voting power = pM / (pM + 100 - p)
```

At `p = 5.01`, requiring voting power greater than `50.1%` means the multiplier must exceed
approximately `19.03` votes per Class B share. A 20:1 structure is therefore a boundary case,
not a robust design margin. The lane must model at least:

| Class B ratio | Approx. founder voting power at 5.01% economics |
|---:|---:|
| 10:1 | 34.5% |
| 20:1 | 51.3% |
| 25:1 | 56.9% |
| 50:1 | 72.5% |
| 100:1 | 84.1% |

The certificate and control workpapers must define the measurement denominator, voting floor,
5.01% threshold, and treatment of options, warrants, SAFEs, convertibles, preferred stock,
acquisition shares, splits, recapitalizations, and equity plans. A variable voting formula may
be analyzed as an alternative, but it is not a default: it requires separate Delaware counsel
review under DGCL §§151, 212, and 216.

The control stack must also prevent a 5.01% → 4.99% dilution attack through defined preemptive,
participation, top-up, or equivalent contractual protections, subject to financing, employee,
acquisition, strategic, solvency, fiduciary, equal-treatment, securities, and investor-review
limitations. Falling below the threshold must have explicit conversion/sunset consequences.

## Transfer and succession

Define permitted transfers to founder-controlled entities, estate vehicles, family trusts,
foundations, and succession vehicles; define automatic conversion to Class A for prohibited
transfers or loss of required beneficial ownership. Address death, disability, incapacity,
divorce, creditor attachment, involuntary transfer, and trust/estate administration. Coordinate
corporate, tax, estate, fiduciary, securities, and solvency review.

## Control gates

Before implementation, require current Delaware authority review for DGCL §§151, 212, 216,
218, and 122(18); PE/VC and fund investor review; SEC/exchange/proxy review where relevant;
tax/QSBS/409A review; accounting/valuation/audit review; estate/trust review; and adversarial
attack on control, fiduciary, disclosure, transfer, and anti-circumvention risks.

## Current case-law and forum firewall

The lane must use `case-law-jurisdiction-index.json` as a living authority index. The
January 20, 2026 Delaware Supreme Court decision in *Moelis* reversed and vacated the
2024 Chancery judgment on laches grounds and did not decide the facial-validity merits.
The lane therefore must not encode the obsolete shortcut that "Moelis invalidated all
contractual founder vetoes." Instead, each provision requires separate analysis of:

- current mandatory-law and certificate consistency;
- §122(18) contract formation, consideration, scope, and remedies;
- facial versus as-applied challenge and limitations/laches risk;
- founder/controller status and fiduciary process;
- franchise interference, entrenchment, dilution, and fairness risk; and
- the actual court, claim, remedy, and appellate path.

The index is an internal research control. It is not a guarantee against litigation,
judicial review, statutory change, or an adverse ruling.

## Issuer precedent screen

The index also carries issuer evidence, not as legal precedent but as drafting
benchmarks:

- **Meta:** certificate-level 1-vote Class A / 10-vote Class B architecture and
  class-voting protections.
- **SpaceX:** multi-class Class A/B/C offering architecture with Class B votes,
  separate class rights, director-election rights, and specified amendment and
  combination protections.
- **Tesla:** a counterexample showing that one-vote common stock and substantial
  founder influence can still produce controller and transaction-specific
  fiduciary exposure.

The agent must label each proposition as one of: **statute**, **binding case**,
**trial-level case**, **issuer filing**, **inference**, or **drafting choice**. It
must never cite an issuer's proxy or prospectus as proof that a clause is legally
valid in another corporation.

All outputs remain subject to Delaware counsel, securities counsel, tax counsel, CPA, valuation,
estate/trust, and local-counsel review before adoption, financing, transfer, IPO, or reliance.
