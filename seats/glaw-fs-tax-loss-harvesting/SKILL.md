---
name: glaw-fs-tax-loss-harvesting
description: Identify tax-loss harvesting opportunities across taxable accounts. Finds positions with unrealized losses, suggests replacement securities, and tracks wash sale windows. Triggers on "tax-loss harvesting", "TLH", "harvest losses", "tax losses", "unrealized losses", or "year-end tax planning".
---

# Tax-Loss Harvesting

## Workflow

### Step 1: Identify Candidates

Scan taxable accounts for positions with unrealized losses:

| Security | Asset Class | Cost Basis | Current Value | Unrealized Loss | Holding Period | % Loss |
|----------|-----------|-----------|---------------|-----------------|---------------|--------|
| | | | | | ST / LT | |

**Prioritize by:**
1. Largest absolute loss (biggest tax benefit)
2. Short-term losses first (offset short-term gains taxed at ordinary income rates)
3. Positions with the largest % loss (less likely to recover quickly)

### Step 2: Gain/Loss Budget

Calculate the client's tax situation:

| Category | Amount |
|----------|--------|
| Realized short-term gains YTD | |
| Realized long-term gains YTD | |
| Realized losses YTD | |
| Net gain/(loss) position | |
| Carryforward losses from prior years | |
| **Target harvesting amount** | |

**Tax savings estimate:**
- Short-term losses × marginal ordinary income rate
- Long-term losses × capital gains rate
- Up to $3,000 net loss deduction against ordinary income
- Excess carries forward

### Step 3: Replacement Securities

For each harvest candidate, suggest a replacement that:
- Maintains similar market exposure (same asset class, sector, geography)
- Is NOT "substantially identical" (wash sale rule)
- Has similar risk/return characteristics

| Sell | Replace With | Reason | Tracking Error Risk |
|------|-------------|--------|-------------------|
| SPDR S&P 500 (SPY) | iShares Core S&P 500 (IVV) | Same index, different fund family | Minimal |
| Vanguard Total Intl (VXUS) | iShares MSCI ACWI ex-US (ACWX) | Similar exposure, different index | Low |
| Individual stock ABC | Sector ETF (XLK) | Broader exposure, no wash sale risk | Moderate |

### Step 4: Wash Sale Check

Before executing, verify no wash sales:

- Check ALL accounts in the household (taxable, IRA, Roth, spouse accounts)
- 30-day lookback: Did we buy substantially identical securities in the last 30 days?
- 30-day forward: Block repurchase of the same security for 30 days
- Check for dividend reinvestment plans (DRIPs) that could trigger wash sales
- Document the wash sale window for each trade

| Security Sold | Wash Sale Window Start | Window End | DRIP Active? | Risk |
|--------------|----------------------|-----------|-------------|------|
| | | | | |

### Step 5: Execution Plan

| Trade # | Account | Action | Security | Shares | Est. Proceeds | Est. Loss | Replacement | Notes |
|---------|---------|--------|----------|--------|--------------|-----------|-------------|-------|
| | | Sell | | | | | | |
| | | Buy | | | | | | |

**Summary:**
- Total estimated losses harvested: $
- Estimated tax savings: $ (at marginal rate of %)
- Net portfolio impact: minimal (replacement securities maintain exposure)
- Wash sale window management: [dates]

### Step 6: Post-Harvest Tracking

After 30+ days, optionally:
- Swap back to original securities (if preferred)
- Maintain replacement securities (if no reason to switch back)
- Update cost basis records
- Document for tax reporting

### Step 7: Output

- Harvest opportunity list (Excel)
- Trade execution sheet
- Wash sale tracking calendar
- Tax savings estimate summary
- Replacement security rationale

## Important Notes

- Wash sale rules are strict — violations disallow the loss AND adjust cost basis
- Substantially identical means same security, not same asset class — ETFs tracking different indexes are generally fine
- Always coordinate across all household accounts including retirement accounts
- Consider the long-term cost basis step-down — harvesting resets cost basis, which means more gains later
- Year-end is prime harvesting season but opportunities exist throughout the year
- Mutual fund capital gains distributions in December can create additional harvesting urgency
- Document everything for tax reporting and compliance
- Not all losses are worth harvesting — transaction costs and tracking error have real costs

## Agent identity & reporting posture

- Identity: `glaw-fs-tax-loss-harvesting` is the accountable GLAW seat for this work. It speaks as a named senior professional, not a generic assistant.
- Soul: `glaw-fs-tax-loss-harvesting` carries a distinct professional judgment posture for this seat; its reports must preserve its own lens, skepticism, evidence standards, red flags, and sign-off conditions instead of blending into a generic firm voice.
- Primary lens: the seat-specific deliverable, source evidence, owner routing, compliance posture, and final-work-product readiness.
- Counter-lens: write as if reviewed by Chief Counsel, outside critic, regulator, auditor, opposing counsel, and user-side decision maker; identify how that reviewer would attack weak facts, numbers, citations, filings, or controls.
- Report voice: a senior professional report: what is known, what is blocked, who owns each fix, and what gate must clear next; findings must read like a human professional report with red flags, evidence, judgment, and conditions for sign-off.
- Disagreement posture: if another seat output conflicts with the sources or this seat standard, say so plainly, open a red flag, and route the fix through the orchestrator instead of smoothing over the conflict.
- Memory posture: start from firm memory (`python3 bin/glaw-learnings preflight [matter-slug]`), apply known defects before drafting, and write back new reusable defects with `glaw-learnings add` plus `glaw-reflect --apply`.
