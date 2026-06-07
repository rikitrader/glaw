---
name: glaw-fund-regulatory-council
description: "Multi-agent regulatory council that drafts, fills, and generates all SEC/FINRA/state filings and compliance documents for tokenized fund offerings. Covers Form D (EDGAR), Form ADV (IARD), Blue Sky state notice filings, Form PF, auditor engagement letters, qualified custodian agreements, entity org charts, BD/ATS analysis, ERISA disclosures, Persona KYC configuration, PPM supplements, and subscription agreement addenda. Use for: 'regulatory filings', 'Form D', 'Form ADV', 'Blue Sky', 'fund compliance documents', 'auditor engagement', 'custodian agreement', 'entity structure', 'BD registration', 'state filings', 'fund formation documents', 'compliance council', 'regulatory council'."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - WebFetch
  - WebSearch
  - Grep
  - Glob
  - Agent
compatibility: claude-code-only
---

# Fund Regulatory Council

Multi-agent council skill that drafts, fills, and generates all SEC/FINRA/state regulatory filings and compliance documents required to take a tokenized fund from demo to live capital acceptance. Built from the 4-agent compliance audit of fund.roof10x.com and the `/tokenization-compliance` skill framework.

**This skill is NOT legal advice.** All generated documents are drafts requiring review and filing by licensed securities counsel. The skill produces complete, form-ready drafts that minimize counsel's billable hours.

---

## Council Agents

When invoked, the skill spawns up to 5 parallel council agents, each responsible for a regulatory domain:

| Agent | Domain | Outputs |
|-------|--------|---------|
| **SEC Filings Agent** | Form D, Form ADV, Form PF | Pre-filled XML/EDGAR drafts, filing checklists, fee calculations |
| **State Filings Agent** | Blue Sky notice filings, state-specific legends | Per-state filing matrix, Form D state copies, fee schedule |
| **Fund Documents Agent** | Auditor engagement, custodian agreement, entity org chart, PPM supplement | Draft letters, agreement templates, corporate structure diagrams |
| **BD/ATS Analysis Agent** | Broker-dealer analysis, ATS determination, secondary market characterization | Legal memo, no-action letter analysis, structural recommendations |
| **Ops Config Agent** | Persona KYC prod config, NAV calculation fix, ERISA wiring verification | Technical implementation specs, API configuration, code patches |

---

## BLOCKER-2: Engage Independent Auditor

### Auditor Engagement Letter Template

When generating an auditor engagement letter, include these sections:

```
ENGAGEMENT LETTER — ANNUAL AUDIT OF FINANCIAL STATEMENTS

TO: [Fund Name], LP
    [GP Entity Name], LLC (as General Partner)

FROM: [Audit Firm Name]
      [Address]

DATE: [Date]

1. SCOPE OF ENGAGEMENT

We are pleased to confirm our understanding of the terms and objectives
of our engagement to audit the financial statements of [Fund Name], LP
(the "Fund") and to express an opinion on the financial statements.

We will audit the following financial statements of the Fund as of and
for the fiscal year ending [Date]:

  (a) Statement of Assets, Liabilities, and Partners' Capital
  (b) Statement of Operations
  (c) Statement of Changes in Net Assets (Partners' Capital)
  (d) Statement of Cash Flows (if applicable)
  (e) Schedule of Investments
  (f) Financial Highlights (Per-Unit Data)
  (g) Notes to Financial Statements

The financial statements will be prepared in conformity with accounting
principles generally accepted in the United States of America (U.S. GAAP),
specifically:

  - ASC 946 (Financial Services — Investment Companies), OR
  - ASC 970 (Real Estate — General) if the Fund does not qualify as an
    investment company under ASC 946-10-15

[NOTE: The applicability of ASC 946 vs ASC 970 must be determined as part
of this engagement. The Fund holds operating real estate assets (roofing
operations, insurance restoration) that generate operating income, which
may disqualify ASC 946 treatment. The auditor should opine on the
appropriate reporting framework as a pre-engagement deliverable.]

2. FAIR VALUE MEASUREMENTS (ASC 820)

We will evaluate the Fund's fair value measurements under ASC 820,
including:

  - Level 1/2/3 hierarchy classification of all investments
  - Beginning-to-ending balance reconciliation for Level 3 measurements
  - Sensitivity analysis for significant unobservable inputs
  - Valuation methodology documentation and consistency

3. MANAGEMENT'S RESPONSIBILITIES

Management is responsible for:

  (a) Preparation and fair presentation of financial statements
  (b) Design, implementation, and maintenance of internal controls
  (c) Prevention and detection of fraud
  (d) Compliance with applicable laws and regulations
  (e) Making all financial records and related information available
  (f) Providing written representations at conclusion of audit
  (g) Adjusting financial statements for material misstatements

4. AUDITOR'S RESPONSIBILITIES

Our audit will be conducted in accordance with auditing standards
generally accepted in the United States of America (GAAS). We will:

  (a) Plan and perform the audit to obtain reasonable assurance
  (b) Consider internal controls relevant to financial statement preparation
  (c) Evaluate the appropriateness of accounting policies
  (d) Evaluate the overall presentation of financial statements
  (e) Communicate significant matters to management and those charged
      with governance

5. CUSTODY RULE COMPLIANCE (Rule 206(4)-2)

If the Fund's investment adviser is registered or required to register
under the Investment Advisers Act of 1940, we will perform either:

  (a) An annual surprise examination of client assets, OR
  (b) Verification that the Fund's financial statements are audited
      annually by an independent public accountant registered with the
      PCAOB, delivered to investors within 120 days of fiscal year end

[SELECT ONE AND DELETE THE OTHER]

6. DELIVERABLES

  (a) Audited financial statements with auditor's report
  (b) Management letter (if control deficiencies identified)
  (c) ASC 946 vs ASC 970 applicability opinion (pre-engagement)
  (d) ASC 820 Level 3 fair value inputs review
  (e) Tax return review (Form 1065 and Schedule K-1s)

7. FEES AND TIMING

  Estimated fee: $[___] for the initial audit
  Subsequent years: $[___] annually
  K-1 preparation: $[___] per partner
  Timing: Fieldwork [month], draft report [month], final [month]
  K-1 delivery to partners: March 15 of the following year

8. ENGAGEMENT TEAM

  Engagement Partner: [Name], CPA
  Senior Manager: [Name], CPA
  PCAOB Registration: [Yes/No — required for Custody Rule compliance]

9. TERMS AND CONDITIONS

[Standard engagement terms including limitation of liability,
indemnification, dispute resolution, termination provisions]
```

### Recommended Audit Firms (Tokenized Fund Specialization)

| Firm | Specialty | Typical Fee Range | Notes |
|------|----------|------------------|-------|
| Eisner Advisory Group | Crypto/digital assets + RE funds | $40K-$80K | Strong ASC 946/820 practice |
| Cohen & Company | Digital asset funds, tokenized securities | $35K-$70K | SOC 1 reports for fund admin |
| Withum | Blockchain/crypto + PE/RE funds | $40K-$75K | AICPA digital assets task force |
| Armanino | Crypto audit + fund audit | $45K-$90K | Real-time audit dashboard |
| Marcum | PE/RE funds + digital assets | $35K-$65K | Mid-market focus |
| KPMG/PwC/EY/Deloitte | Full-service (if AUM justifies) | $150K+ | Institutional credibility |

---

## BLOCKER-3: Establish Qualified Custodian

### Custodian Analysis for Tokenized Fund Assets

The fund holds two categories of assets requiring custody:

| Asset Type | Current State | Required Custodian |
|-----------|--------------|-------------------|
| Fiat/USD (investor subscriptions) | Crossmint → GP wallet (USDC on Base) | Qualified custodian per Rule 206(4)-2 |
| Tokenized LP interests (R10X ERC-721) | GP-controlled wallet `0xc20e...` | SEC §17A transfer agent OR qualified custodian |
| Real property interests (SPVs) | Held via SPV LLCs | Title company / county recorder (traditional) |

### Qualified Custodian Options

| Provider | Type | Digital Asset Custody | Fiat Custody | Transfer Agent | Fee Range |
|----------|------|----------------------|-------------|----------------|-----------|
| **Anchorage Digital** | OCC-chartered bank | Yes (institutional) | Yes | No | 25-50 bps AUM |
| **Coinbase Prime** | NY-chartered trust | Yes | Yes (via Circle) | No | 20-40 bps AUM |
| **BitGo Trust** | SD-chartered trust | Yes | Yes | No | 15-35 bps AUM |
| **Fireblocks** | Technology + custody network | Yes (MPC wallets) | Via banking partners | No | Platform fee |
| **Empire Stock Transfer** | SEC §17A transfer agent | Token custody via TA model | No | Yes | Per-transaction |
| **Securitize** | SEC §17A TA + ATS | Yes (own platform) | Via banking partner | Yes | Platform + per-tx |

### Qualified Custodian Agreement Template (Key Terms)

```
QUALIFIED CUSTODIAN AGREEMENT

PARTIES:
  Custodian: [Name], a [charter type] chartered under [jurisdiction]
  Fund: [Fund Name], LP
  Adviser: [GP Entity], LLC (as investment adviser to the Fund)

1. APPOINTMENT
   The Fund hereby appoints Custodian as qualified custodian of Fund
   assets pursuant to Rule 206(4)-2 under the Investment Advisers Act
   of 1940 (the "Custody Rule").

2. ASSETS UNDER CUSTODY
   (a) Digital assets: R10X tokens (ERC-721) on Base blockchain
   (b) Stablecoin holdings: USDC on Base blockchain
   (c) Fiat currency: USD held in omnibus account at [Bank Name]

3. CUSTODY STANDARDS
   (a) Digital assets held in segregated, multi-signature wallets
   (b) Private keys stored in HSM (Hardware Security Module) with
       geographic redundancy
   (c) Insurance coverage: $[___] per-occurrence / $[___] aggregate
   (d) SOC 2 Type II certification maintained annually

4. ACCOUNT STATEMENTS
   Custodian will deliver quarterly account statements directly to
   each Fund investor showing:
   (a) All assets held
   (b) All transactions during the period
   (c) Ending balances

5. INDEPENDENT VERIFICATION
   [OPTION A — if adviser has custody]:
   Custodian will facilitate annual surprise examination by [Audit Firm]
   pursuant to Rule 206(4)-2(a)(4).

   [OPTION B — if relying on audit exception]:
   Fund financial statements will be audited annually and delivered to
   investors within 120 days of fiscal year end per Rule 206(4)-2(b)(4).

6. DIGITAL ASSET SPECIFIC PROVISIONS
   (a) Blockchain reconciliation: Custodian will reconcile on-chain
       balances with internal records daily
   (b) Fork/airdrop policy: Custodian will hold forked assets pending
       Fund instruction; airdrops credited to Fund account
   (c) Smart contract interaction: Custodian will execute on-chain
       transactions only upon authorized instruction from Adviser
   (d) Key ceremony: Initial key generation conducted with dual control
       and split knowledge; documented and witnessed

7. FEES
   [Standard custodian fee schedule — basis points on AUM, per-transaction
   fees for on-chain operations, minimum monthly fee]

8. TERMINATION
   Either party may terminate upon [90] days written notice.
   Upon termination, Custodian will transfer all assets to successor
   custodian within [30] days.
```

---

## BLOCKER-4: Fix NAV Calculation

### Technical Specification for NAV Fix

The current NAV calculation in `functions/api/me/statements.js` is:

```javascript
// CURRENT (materially incomplete):
totalNAV = SUM(properties.current_nav_cents)
totalDebt = SUM(debt_tranches.balance_cents)
netAssets = totalNAV - totalDebt
navPerUnit = netAssets / 10_000_000  // HARDCODED
```

### Required Fix:

```javascript
// CORRECTED:
const totalInvestments = SUM(properties.current_nav_cents)
const cash = SUM(bank_accounts.balance_cents)  // new table needed
const receivables = SUM(receivables.amount_cents)  // mgmt fees, rent
const totalAssets = totalInvestments + cash + receivables

const totalDebt = SUM(debt_tranches.balance_cents)
const payables = SUM(payables.amount_cents)  // accrued expenses
const mgmtFeePayable = computeAccruedMgmtFee(fund, period)
const distPayable = SUM(distributions.amount_cents WHERE status='scheduled')
const totalLiabilities = totalDebt + payables + mgmtFeePayable + distPayable

const netAssets = totalAssets - totalLiabilities

// DYNAMIC units from DB, not hardcoded:
const unitsOutstanding = await env.DB.prepare(
  `SELECT SUM(units) FROM subscriptions
   WHERE offering_id = ? AND status IN ('active','signed')`
).bind(offeringId).first()

const navPerUnit = netAssets / unitsOutstanding.sum_units
```

### New Tables Required

```sql
CREATE TABLE IF NOT EXISTS fund_cash_accounts (
  id TEXT PRIMARY KEY,
  fund_id TEXT NOT NULL,
  account_name TEXT NOT NULL,
  institution TEXT NOT NULL,
  account_type TEXT DEFAULT 'operating',  -- operating, reserve, escrow
  balance_cents INTEGER DEFAULT 0,
  as_of_date TEXT NOT NULL,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fund_receivables (
  id TEXT PRIMARY KEY,
  fund_id TEXT NOT NULL,
  description TEXT NOT NULL,
  counterparty TEXT,
  amount_cents INTEGER NOT NULL,
  due_date TEXT,
  status TEXT DEFAULT 'outstanding',  -- outstanding, collected, written_off
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fund_payables (
  id TEXT PRIMARY KEY,
  fund_id TEXT NOT NULL,
  description TEXT NOT NULL,
  vendor TEXT,
  amount_cents INTEGER NOT NULL,
  due_date TEXT,
  status TEXT DEFAULT 'outstanding',  -- outstanding, paid, disputed
  created_at TEXT DEFAULT (datetime('now'))
);
```

---

## BLOCKER-5: File Form D + Form ADV

### Form D (Notice of Exempt Offering of Securities)

**Filing destination:** SEC EDGAR (https://www.sec.gov/cgi-bin/browse-edgar)
**Filing method:** Online via EDGAR Filing System
**Deadline:** Within 15 days of first sale of securities
**Fee:** None
**Amendment:** Annual amendment required; also amend for material changes

#### Form D Pre-Fill Data

```
FORM D — NOTICE OF EXEMPT OFFERING OF SECURITIES

ITEM 1. ISSUER'S IDENTITY
  Name of Issuer: Roof10x Florida Roofing Fund III, LP
  CIK Number: [TO BE OBTAINED — file EDGAR access request first]
  Jurisdiction of Organization: Delaware
  Year of Organization: [Year]
  IRS Employer ID Number (EIN): [EIN]

  Address:
    Street: [Address]
    City: [City]
    State: Florida
    ZIP: [ZIP]
    Phone: [Phone]

ITEM 2. PRINCIPAL PLACE OF BUSINESS
  [Same or different from Item 1]

ITEM 3. RELATED PERSONS
  [List all executive officers, directors, and promoters]
  
  Person 1:
    Last Name: [___]
    First Name: [___]
    Title: General Partner / Managing Member
    Relationship: Executive Officer, Director, Promoter
    Street: [Address]
    CRD Number: [if applicable]

  [Repeat for each related person — include all persons who would be
   "covered persons" under Rule 506(d) bad actor provisions]

ITEM 4. INDUSTRY GROUP
  ☐ Banking & Financial Services
  ☐ Real Estate
  ☒ Pooled Investment Fund
    Type: ☒ Other (Tokenized Real Estate Private Equity Fund)
    Is this an investment company under the ICA 1940? ☐ Yes ☒ No
    ICA exemption claimed: ☒ Section 3(c)(7)

ITEM 5. ISSUER SIZE
  Revenue Range: [Select]
  Aggregate Net Asset Value Range: [Select — if >$25M, triggers IA considerations]

ITEM 6. FEDERAL EXEMPTION(S) AND EXCLUSION(S) CLAIMED
  ☒ Rule 506(c)
  ☐ Rule 506(b)
  ☐ Rule 504
  ☐ Regulation S
  ☐ Section 4(a)(5)

ITEM 7. TYPE OF FILING
  ☒ New Notice
  ☐ Amendment
  Date of First Sale: [Date — if not yet sold, enter "Yet to occur"]

ITEM 8. DURATION OF OFFERING
  Does the issuer intend this to be a continuous offering? ☐ Yes ☒ No

ITEM 9. TYPE(S) OF SECURITIES OFFERED
  ☒ Equity — Limited Partnership Interests
  ☐ Debt
  ☐ Option/Warrant
  ☐ Security to be acquired upon exercise of option/warrant
  ☐ Pooled investment fund interests
  ☒ Other: Tokenized LP Interests (ERC-721 on Base blockchain)

ITEM 10. BUSINESS COMBINATION TRANSACTION
  Is this offering made in connection with a business combination? ☐ Yes ☒ No

ITEM 11. MINIMUM INVESTMENT ACCEPTED FROM ANY OUTSIDE INVESTOR
  $[Minimum commitment amount]

ITEM 12. SALES COMPENSATION
  Recipient Name: [If using BD — name of BD; if none, state "None"]
  CRD Number: [BD CRD#]
  Associated BD: [BD name]
  Compensation: [Description — flat fee, % of raise, etc.]
  State(s) of Solicitation: [List all states]

  [If no BD used, state: "No person has been or will be paid directly
   or indirectly any commission or similar compensation for solicitation
   of purchasers in connection with this offering."]

ITEM 13. OFFERING AND SALES AMOUNTS
  Total Offering Amount: $[___]
  Total Amount Sold: $[___]
  Total Remaining to be Sold: $[___]

  ☐ Indefinite offering amount
  ☐ Clarification of Response (if needed): [___]

ITEM 14. INVESTORS
  Number of accredited investors who have already invested: [___]
  Number of non-accredited investors who have already invested: 0
  (506(c) permits ONLY verified accredited investors / qualified purchasers)

ITEM 15. SALES COMMISSIONS & FINDERS' FEES
  Sales Commissions: $[___] (estimate if not yet determined)
  Finders' Fees: $[___]
  ☐ Clarification: [___]

ITEM 16. USE OF PROCEEDS
  Provide the amount of the gross proceeds used for:
  Estimated amount for payments to officers/directors: $[___]
  Estimated amount for payments to promoters: $[___]
  Estimated amount for investment: $[___]
  Estimated amount for other expenses: $[___]

SIGNATURE
  Issuer: Roof10x Florida Roofing Fund III, LP
  By: [GP Entity Name], LLC, its General Partner
  By: [Name], [Title]
  Date: [Date]
```

### Form ADV Parts 1 & 2A

**Filing destination:** IARD (Investment Adviser Registration Depository)
**Filing method:** Online via IARD system (https://www.iard.com)
**Fee:** SEC registration fee (~$300) + state notice filing fees ($50-$400/state)

#### Form ADV Part 1A — Key Items to Complete

```
FORM ADV PART 1A — UNIFORM APPLICATION FOR INVESTMENT ADVISER REGISTRATION

ITEM 1: IDENTIFYING INFORMATION
  A. Name: Example Holdings Holdings LLC
  B. SEC File Number: [To be assigned]
  C. CRD Number: [To be assigned via IARD]
  D. Principal Office:
     Address: [___]
     City/State/ZIP: [___]
     Phone: [___]
     Website: roof10x.com
  E. Mailing Address: [if different]
  F. Organization:
     Type: ☒ Limited Liability Company
     State of Organization: [State]
     Date of Organization: [Date]

ITEM 2: SEC REGISTRATION
  A. Are you registered with the SEC as an investment adviser?
     ☐ Yes ☒ No (applying)
  B. Are you applying for SEC registration? ☒ Yes
  C. Basis for SEC registration (check all that apply):
     ☐ Assets under management of $100M+ (Section 203A(a)(2))
     ☒ Adviser to private fund(s) with $150M+ AUM (Section 203(m))
     ☐ Multi-state adviser
     ☐ Other: [___]

ITEM 5: INFORMATION ABOUT YOUR ADVISORY BUSINESS
  C. Approximate AUM:
     Discretionary: $[___]
     Non-Discretionary: $[___]
     Total: $[___]
     Date of Calculation: [___]
  
  D. Types of advisory services:
     ☒ Financial planning services
     ☒ Portfolio management for pooled investment vehicles
     ☐ Portfolio management for individuals
     ☐ Pension consulting
     ☐ Selection of other advisers
     ☐ Publication of periodicals
     ☐ Other: [___]
  
  F. Types of clients:
     ☒ Pooled investment vehicles (private funds)
     ☐ Individuals (other than high net worth)
     ☐ High net worth individuals
     ☐ Banking/thrift institutions
     ☐ Other: [___]

ITEM 6: OTHER BUSINESS ACTIVITIES
  A. Broker-dealer:
     ☐ Registered broker-dealer ☐ Registered representative
  B. Other financial industry activities:
     [Disclose relationship between Example Holdings Holdings LLC (adviser),
      Example Holdings Inc. (SaaS operating company), ROOF_OS Inc. (technology
      platform), and Roof10x Florida Roofing Fund III LP (fund)]

ITEM 7: FINANCIAL INDUSTRY AFFILIATIONS
  [List all related entities and their registration status]

  Entity 1: Example Holdings Inc.
    Relationship: Under common control
    Type: Operating company (SaaS)
    Registered: ☐ BD ☐ IA ☐ Other ☒ None

  Entity 2: ROOF_OS Inc.
    Relationship: Under common control
    Type: Technology platform provider
    Registered: ☐ BD ☐ IA ☐ Other ☒ None

  Entity 3: Roof10x Florida Roofing Fund III, LP
    Relationship: Fund managed by applicant
    Type: Private fund
    Registered: ☐ BD ☐ IA ☐ Other ☒ None (relies on 3(c)(7))

ITEM 7.B: PRIVATE FUND REPORTING (FORM ADV-exempt or full registration)
  
  Private Fund 1:
    Name: Roof10x Florida Roofing Fund III, LP
    State: Delaware
    Type: Real Estate Fund
    Gross AUM: $[___]
    Net AUM: $[___]
    Number of Beneficial Owners: [___]
    Minimum Investment: $[___]
    Auditor: [Name — TBD per BLOCKER-2]
    Custodian: [Name — TBD per BLOCKER-3]
    Administrator: [Name or self-administered]

ITEM 11: DISCLOSURE INFORMATION
  [Bad actor disqualification events — Rule 506(d) check]
  Has any supervised person been subject to:
  ☐ Criminal charges (felony or investment-related misdemeanor)
  ☐ SEC, CFTC, state, or foreign regulatory proceedings
  ☐ Self-regulatory organization proceedings
  ☐ Civil proceedings (investment-related)
  [If yes to any, provide DRP (Disclosure Reporting Page)]
```

#### Form ADV Part 2A — Brochure (Outline)

```
FORM ADV PART 2A — FIRM BROCHURE

1. COVER PAGE
   Example Holdings Holdings LLC
   [Address]
   [Phone]
   [Website]
   [Date of Brochure]
   "This brochure provides information about the qualifications and
    business practices of Example Holdings Holdings LLC..."

2. MATERIAL CHANGES
   [Summary of material changes since last annual update]

3. TABLE OF CONTENTS

4. ADVISORY BUSINESS
   - Description of advisory services
   - Types of clients (private funds only)
   - AUM (discretionary and non-discretionary)
   - Wrap fee programs: N/A

5. FEES AND COMPENSATION
   - Management Fee: 2% of AUM [committed/invested/NAV — specify]
   - Carried Interest: 20% above 8% preferred return
   - Technology Platform Fee: $240K/quarter (related-party — see Item 10)
   - Other Fund Expenses: legal, audit, admin, blockchain, insurance

6. PERFORMANCE-BASED FEES AND SIDE-BY-SIDE MANAGEMENT
   - Carried interest is a performance-based fee
   - Conflicts arising from performance-based compensation

7. TYPES OF CLIENTS
   - Qualified purchasers under ICA §2(a)(51)
   - Minimum investment: $[___]
   - Other conditions: KYC/AML/OFAC/accreditation verification

8. METHODS OF ANALYSIS, INVESTMENT STRATEGIES, AND RISK OF LOSS
   - Real estate acquisition strategy (Florida roofing/insurance restoration)
   - Tokenization strategy (ERC-721 on Base blockchain)
   - Risk factors: real estate, leverage, illiquidity, blockchain, key person

9. DISCIPLINARY INFORMATION
   [Disclose any material legal or disciplinary events]

10. OTHER FINANCIAL INDUSTRY ACTIVITIES AND AFFILIATIONS
    - Example Holdings Inc. (SaaS operating company) — common ownership
    - ROOF_OS Inc. (technology platform) — common ownership, related-party fee
    - Conflict: GP charges fund $240K/quarter for platform license TO ITSELF

11. CODE OF ETHICS, PARTICIPATION IN CLIENT TRANSACTIONS
    - Personal trading policy
    - GP co-investment in fund
    - Side letter policies

12. BROKERAGE PRACTICES
    - No brokerage used (direct investment in real property via SPVs)
    - Secondary market: [describe if applicable]

13. REVIEW OF ACCOUNTS
    - Quarterly review of fund investments by GP
    - Annual audit by independent auditor
    - Quarterly investor reports

14. CLIENT REFERRALS AND OTHER COMPENSATION
    - [Disclose any referral arrangements]

15. CUSTODY
    - Adviser deemed to have custody (GP controls fund assets)
    - Qualified custodian: [Name — per BLOCKER-3]
    - Annual audit delivery within 120 days of FYE
    - [Or: surprise examination arrangement]

16. INVESTMENT DISCRETION
    - Full discretionary authority per LPA
    - Investment committee approval for acquisitions > $[threshold]

17. VOTING CLIENT SECURITIES
    - LP voting rights per LPA
    - Governance proposals via fund.roof10x.com portal

18. FINANCIAL INFORMATION
    - Balance sheet (if >$500K prepaid fees or financial condition issue)
```

---

## BLOCKER-6: Configure Persona Production

### Persona KYC Configuration Checklist

```
1. ENVIRONMENT UPGRADE
   Current: PERSONA_ENV = "sandbox"
   Target:  PERSONA_ENV = "production"

2. TEMPLATE CREATION
   Current: PERSONA_TEMPLATE_ID = "" (empty)
   Required: Create inquiry template in Persona dashboard with:
   
   Step 1: Government ID Verification
     - Document types: passport, driver's license, national ID
     - Both sides required for DL
     - Barcode/MRZ extraction enabled
   
   Step 2: Selfie Liveness Check
     - Active liveness (not passive)
     - Photo comparison to ID document
   
   Step 3: Database Verification
     - OFAC/SDN screening
     - PEP (Politically Exposed Persons) check
     - Adverse media screening
     - Watchlist screening (FBI, Interpol, EU sanctions)
   
   Step 4: Accredited Investor Verification (506(c))
     - Income verification: connect to payroll/tax data
     - Net worth verification: connect to financial accounts
     - Professional certification: Series 7/65/82 license check
     - Third-party letter upload + admin review workflow
   
   Step 5: Qualified Purchaser Verification (3(c)(7))
     - Investment portfolio verification ($5M+ in investments)
     - Exclude primary residence from net worth
     - Entity QP: $25M+ in investments

3. WEBHOOK CONFIGURATION
   Endpoint: https://fund.roof10x.com/api/persona-webhook
   Events: inquiry.completed, inquiry.failed, inquiry.expired
   Signing secret: [generate and store in Cloudflare secret]

4. WRANGLER.TOML UPDATES
   [vars]
   PERSONA_ENV = "production"
   
   [secrets]
   PERSONA_API_KEY = "[production API key]"
   PERSONA_TEMPLATE_ID = "[production template ID]"
   PERSONA_WEBHOOK_SECRET = "[webhook signing secret]"
```

---

## CRITICAL-8: Entity Structure / Org Chart

### Entity Org Chart Template

```
                    ┌─────────────────────────┐
                    │   [Principal Name(s)]    │
                    │   Individual Owner(s)    │
                    └────────────┬────────────┘
                                 │ 100%
                    ┌────────────▼────────────┐
                    │   Example Holdings Holdings LLC   │
                    │   (Holding Company)      │
                    │   [State] LLC            │
                    └──┬──────────┬──────────┬─┘
                       │          │          │
            ┌──────────▼──┐  ┌───▼───────┐  ┌▼──────────────┐
            │ Example Holdings Inc │  │ ROOF_OS   │  │ GP Entity     │
            │ (OpCo/SaaS) │  │ Inc.      │  │ (TBD Name)    │
            │ [State] Corp│  │ Tech      │  │ [State] LLC   │
            │             │  │ Platform  │  │               │
            │ • SaaS rev  │  │           │  │ • Fund mgmt   │
            │ • Roofing   │  │ • $240K/q │  │ • 2% mgmt fee │
            │   operations│  │   license │  │ • 20% carry   │
            └─────────────┘  │   to Fund │  └───────┬───────┘
                             └───────────┘          │ General Partner
                                           ┌───────▼───────────┐
                                           │ Roof10x Florida   │
                                           │ Roofing Fund III  │
                                           │ LP                │
                                           │ Delaware LP       │
                                           │                   │
                                           │ • $[__]M target   │
                                           │ • 3(c)(7) exempt  │
                                           │ • Reg D 506(c)    │
                                           └───────┬───────────┘
                                                   │ Holds
                                    ┌──────────────┼──────────────┐
                                    │              │              │
                              ┌─────▼─────┐  ┌────▼────┐  ┌─────▼─────┐
                              │  SPV 1    │  │  SPV 2  │  │  SPV N    │
                              │  LLC      │  │  LLC    │  │  LLC      │
                              │ Property A│  │ Prop B  │  │ Prop N    │
                              └───────────┘  └─────────┘  └───────────┘
```

### Required Entity Disclosures

For each entity, document:

| Entity | Role | State | Registration | Relationship to Fund |
|--------|------|-------|-------------|---------------------|
| Example Holdings Holdings LLC | Holding company | [State] | LLC | Parent of GP |
| Example Holdings Inc. | Operating company (SaaS + roofing) | [State] | Corp | Affiliated; common ownership |
| ROOF_OS Inc. | Technology platform | [State] | Corp | Affiliated; $240K/q license to Fund (related-party) |
| [GP Entity Name] LLC | General Partner | [State] | LLC | GP of the Fund; receives mgmt fee + carry |
| Roof10x Florida Roofing Fund III LP | The Fund | Delaware | LP | Issuer of LP interests |
| SPV 1-N LLC | Property holding | [State] | LLC | Wholly-owned by Fund |

---

## CRITICAL-9: Blue Sky State Notice Filings

### State Filing Matrix

| State | Filing Required | Form | Fee | Deadline | Online Filing |
|-------|----------------|------|-----|----------|---------------|
| **Florida** | Yes — issuer's home state | Form D copy | $0 | 15 days after first FL sale | FLOFR |
| **Texas** | Yes | Form D copy + Form 133.28 | $500 | 15 days after first TX sale | TX SOS |
| **California** | Yes | Form D copy + Form 25102(f) | $300 + $25/investor | 15 days after first CA sale | CalBRE |
| **New York** | Yes (Martin Act) | Form D copy + Form 99 | $1,200 | 15 days after first NY sale | NY AG |
| **Delaware** | Exempt (issuer domicile) | N/A | N/A | N/A | N/A |
| **All other states** | Yes if investors solicited there | Form D copy | $150-$600 avg | 15 days after first sale in state | Varies |

### State Filing Checklist

For each state where securities are offered or sold:

- [ ] File copy of Form D with state securities regulator
- [ ] Pay state filing fee
- [ ] Include state-specific consent to service of process (Form U-2)
- [ ] Provide state-specific legends (if required by state)
- [ ] Calendar annual renewal date
- [ ] Designate state agent for service of process

### Estimated Total Blue Sky Budget

| Scenario | States | Estimated Cost |
|----------|--------|---------------|
| Florida only | 1 | $0 |
| FL + TX + CA + NY | 4 | ~$2,500 |
| 10 major states | 10 | ~$5,000-$7,000 |
| All 50 states + DC | 51 | ~$15,000-$25,000 |

---

## CRITICAL-11: Broker-Dealer / ATS Analysis

### Decision Framework

```
Does the platform facilitate securities transactions?
  │
  ├─ Does it match buyers and sellers? (secondary market)
  │   ├─ YES → Likely ATS under Rule 300(a) of Reg ATS
  │   │   ├─ Register as ATS (Form ATS) + register as BD
  │   │   ├─ OR: Use a registered ATS (tZERO, Securitize, INX)
  │   │   └─ OR: Remove secondary market feature entirely
  │   └─ NO (only primary issuance by issuer) → Continue analysis
  │
  ├─ Does anyone receive transaction-based compensation?
  │   ├─ YES → BD registration likely required
  │   └─ NO → Continue analysis
  │
  ├─ Is the platform "effecting transactions" in securities?
  │   ├─ Accepts orders → YES
  │   ├─ Handles investor funds (Crossmint) → YES
  │   ├─ Provides investment recommendations → MAYBE
  │   └─ Purely informational → NO
  │
  └─ RECOMMENDATION for fund.roof10x.com:
      │
      ├─ OPTION A: Engage a registered BD for the offering
      │   • BD conducts all sales, handles subscriptions
      │   • Platform becomes information-only LP portal
      │   • Cost: 1-3% of raise as placement fee
      │
      ├─ OPTION B: Rely on issuer exemption (§3(a)(9))
      │   • Issuer selling its own securities
      │   • No transaction-based compensation to anyone
      │   • Secondary market must be REMOVED or restructured
      │   • Risk: aggressive regulators may still challenge
      │
      └─ OPTION C: Register as BD + ATS (most expensive)
          • Full FINRA membership application ($5K-$15K filing)
          • Net capital requirement ($250K minimum for ATS)
          • Annual FINRA fees + examination costs
          • Timeline: 6-12 months for approval
          • Only justified if operating ongoing marketplace
```

### Secondary Market Restructuring Options

| Option | Description | Regulatory Risk | Cost |
|--------|------------|----------------|------|
| **Remove entirely** | Delete secondary transfer feature | Zero | $0 |
| **GP bulletin board** | GP posts transfer requests; matches manually; no automated execution | Low | $0 |
| **Use registered ATS** | Route secondary trades through tZERO/Securitize/INX | Very low | Per-transaction fee |
| **Register own ATS** | File Form ATS, register as BD, join FINRA | Very low | $50K-$250K+ setup |

---

## Workflow: Invoking the Council

When the user invokes `/fund-regulatory-council`, spawn agents as follows:

```
User: /fund-regulatory-council [fund-name or URL]

1. Read the fund's current state (fetch URL or read project files)
2. Identify which blockers/criticals remain open
3. For each open item, spawn the appropriate council agent:

   BLOCKER-2 → Fund Documents Agent (auditor engagement letter)
   BLOCKER-3 → Fund Documents Agent (custodian agreement)
   BLOCKER-4 → Ops Config Agent (NAV calculation fix)
   BLOCKER-5 → SEC Filings Agent (Form D + Form ADV pre-fill)
   BLOCKER-6 → Ops Config Agent (Persona production config)
   CRITICAL-8 → Fund Documents Agent (entity org chart)
   CRITICAL-9 → State Filings Agent (Blue Sky matrix + forms)
   CRITICAL-11 → BD/ATS Analysis Agent (legal memo + recommendation)

4. Each agent produces:
   - Draft document / pre-filled form
   - Filing checklist with deadlines
   - Fee estimate
   - Counsel action items (what requires a licensed attorney)

5. Compile all outputs into a master regulatory package
```

### Output Directory Structure

```
docs/regulatory/
├── forms/
│   ├── form-d-draft.md              # Pre-filled Form D
│   ├── form-adv-part1-draft.md      # Pre-filled Form ADV Part 1A
│   ├── form-adv-part2a-draft.md     # Form ADV Part 2A Brochure
│   └── blue-sky-matrix.md           # State-by-state filing tracker
├── agreements/
│   ├── auditor-engagement-letter.md # Draft engagement letter
│   ├── custodian-agreement.md       # Draft QC agreement
│   └── transfer-agent-agreement.md  # Draft TA agreement
├── corporate/
│   ├── entity-org-chart.md          # Entity structure diagram
│   ├── entity-registry.md           # All entities + registrations
│   └── bad-actor-506d-cert.md       # 506(d) certification
├── disclosures/
│   ├── ppm-supplement.md            # PPM blockchain/token addendum
│   ├── subscription-addendum.md     # Sub agreement digital asset terms
│   └── risk-factors-blockchain.md   # Blockchain-specific risk factors
├── ops/
│   ├── persona-prod-config.md       # KYC production configuration
│   ├── nav-calculation-spec.md      # NAV fix technical specification
│   └── erisa-wiring-verification.md # ERISA compliance verification
└── memos/
    ├── bd-ats-analysis.md           # BD/ATS legal analysis memo
    ├── ica-exemption-analysis.md    # 3(c)(7) vs 3(c)(1) analysis
    └── asc946-vs-asc970.md          # Accounting framework determination
```

---

## Filing Timeline (60-90 Day Sprint)

| Week | Action | Owner | Deliverable |
|------|--------|-------|-------------|
| 1 | Entity structure finalization | Counsel | Org chart + entity registry |
| 1 | Auditor selection + engagement | GP + Counsel | Signed engagement letter |
| 1 | Custodian selection + outreach | GP + Counsel | Term sheet from custodian |
| 2 | EDGAR access request (CIK) | Counsel | CIK number assigned |
| 2 | Form D preparation | Counsel (using draft) | Final Form D |
| 2 | Persona production configuration | Ops | Production KYC live |
| 3 | Form D filing (EDGAR) | Counsel | Filed; SEC file number |
| 3 | Blue Sky filings (priority states) | Counsel | FL, TX, CA, NY filed |
| 3 | NAV calculation fix deployed | Engineering | Code deployed + tested |
| 4 | IARD registration | Counsel | IARD CRD number |
| 4 | Form ADV Part 1A filing | Counsel (using draft) | Filed on IARD |
| 4 | Form ADV Part 2A (Brochure) | Counsel (using draft) | Posted on IARD + website |
| 4 | Custodian agreement executed | Counsel | Signed agreement |
| 5-6 | Blue Sky filings (remaining states) | Counsel | All target states filed |
| 5-6 | 506(d) bad actor certifications | Counsel | All covered persons certified |
| 6-8 | PPM supplement (blockchain addendum) | Counsel (using draft) | Final PPM supplement |
| 6-8 | Subscription agreement addendum | Counsel (using draft) | Final sub agreement |
| 8-12 | Initial audit fieldwork | Auditor | Draft financial statements |
| 12 | Audit complete | Auditor | Audited financials delivered |

---

## Disclaimer

This skill generates **draft documents for counsel review**. It is NOT:
- Legal advice
- A substitute for licensed securities counsel
- A guarantee of regulatory approval
- An offer to practice law

All forms, filings, and agreements require review, completion, and filing by:
1. Securities counsel (admitted in relevant jurisdictions)
2. CPA / audit firm (for financial statements)
3. Transfer agent (for custody arrangements)

The skill minimizes counsel's billable hours by producing complete first drafts — but the final versions must be counsel-reviewed and counsel-filed.
