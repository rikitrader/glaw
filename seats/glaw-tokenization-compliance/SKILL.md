---
name: glaw-tokenization-compliance
description: "Design and launch SEC-compliant tokenized securities offerings. Covers the DTC No-Action Letter (Dec 2025), SEC five-category taxonomy (Mar 2026), OTCM/RWA Tokens Category 1 framework, Reg D/Reg S/Reg CF/Reg A exemptions, transfer agent custody, 42 Transfer Hook controls, ST22 token design on Solana, CEDEX trading, investor verification (KYC/KYB/AML/KYW), stablecoin settlement (USDC/PYUSD), fund tokenization (hedge/PE/VC/RE funds, LP interest tokenization, GP/LP economics, waterfall structures, ICA exclusions 3(c)(1)/3(c)(7)/3(c)(5)(C)), and full compliance checklists for equity, mineral/hydrocarbon, real estate, and fund tokenization. Use for: 'tokenize securities', 'SEC compliance', 'digital securities offering', 'RWA tokens', 'security token', 'transfer agent', 'Reg D tokenization', 'DTC tokenization', 'tokenized equity', 'tokenized real estate', 'tokenized fund', 'LP token', 'fund tokenization', 'CORE-CM', 'ST22', 'offering design', 'securities compliance', 'token offering', 'STO', 'security token offering', 'DSO', 'digital security offering'."
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

# Tokenization & Compliance — SEC-Compliant Digital Securities Design & Offering

End-to-end playbook for designing, structuring, and launching tokenized securities offerings that comply with the SEC's 2025-2026 regulatory framework. Built from three primary SEC sources:

1. **DTC No-Action Letter** (Dec 11, 2025) — `dtc-nal-121125.pdf`
2. **OTCM Protocol Written Input** (Jan 30, 2026) — `ctf-written-input-otcm-protocol-013026.pdf`
3. **SEC Five-Category Taxonomy** (Mar 17, 2026) — SEC Release No. 33-11412
4. **Dilendorf Fund Tokenization** (Oct 2022, updated) — `Fund-Tokenization.pdf` + practice guides
5. **Robinhood Tokenization Memo** (Jan 2025) — `tokenization_memo.pdf`
6. **IOSCO Tokenisation of Financial Assets** (Nov 2025) — `IOSCOPD809.pdf`
7. **Stanford Tech. L. Rev.** — Mendelson, "From ICOs to Security Tokens" 22 Stan. Tech. L. Rev. 52 (2019)

---

## Table of Contents

1. [SEC Regulatory Framework](#1-sec-regulatory-framework)
2. [Five-Category Taxonomy](#2-five-category-taxonomy)
3. [Tokenization Models (Category 1 vs Category 2)](#3-tokenization-models)
4. [DTC No-Action Letter Framework](#4-dtc-no-action-letter)
5. [OTCM / RWA Tokens Category 1 Framework](#5-otcm-rwa-tokens-framework)
6. [Offering Exemptions](#6-offering-exemptions)
7. [Transfer Agent & Custody](#7-transfer-agent--custody)
8. [Token Design & Smart Contract Controls](#8-token-design--smart-contract-controls)
9. [Investor Verification Stack](#9-investor-verification-stack)
10. [Settlement Infrastructure](#10-settlement-infrastructure)
11. [Trading Venue Design](#11-trading-venue-design)
12. [Asset Class Playbooks](#12-asset-class-playbooks)
13. [Fund Tokenization](#13-fund-tokenization)
14. [Robinhood Tokenization Policy Proposals](#14-robinhood-tokenization-policy-proposals)
15. [IOSCO International Standards](#15-iosco-international-standards)
16. [Howey Test Analysis & Best Practices](#16-howey-test-analysis--best-practices-for-token-offerings)
17. [Compliance Checklists](#17-compliance-checklists)
18. [Offering Design Workflow](#18-offering-design-workflow)
19. [Risk Disclosures & Disclaimers](#19-risk-disclosures--disclaimers)
20. [Reference Links](#20-reference-links)

---

## 1. SEC Regulatory Framework

### Core Principle
**"A security is a security regardless of whether it is issued, or otherwise represented, offchain or onchain."** — SEC Staff, Jan 28, 2026

Tokenization changes *how* ownership is recorded, not *what* the instrument is legally. All federal securities laws apply:

| Law | Applicability |
|-----|---------------|
| Securities Act of 1933 | Registration or exemption required for all offers/sales |
| Securities Exchange Act of 1934 | Reporting, broker-dealer registration, ATS rules, transfer agent rules |
| Investment Company Act of 1940 | Tokenized fund shares — no differentiated treatment |
| Investment Advisers Act of 1940 | Advisory on tokenized securities = advisory on securities |
| UCC Article 8 | Indirect holding system preserved; security entitlements unchanged |

### Key SEC Guidance Documents (2025-2026)

| Date | Document | What It Establishes |
|------|----------|---------------------|
| Dec 11, 2025 | DTC No-Action Letter | 3-year pilot for tokenizing DTC-custodied assets on blockchain |
| Jan 28, 2026 | Joint Staff Statement on Tokenized Securities | Three tokenization models; Category 1/2 taxonomy |
| Mar 17, 2026 | SEC Release No. 33-11412 (Five-Category Taxonomy) | Binding classification: digital commodities, collectibles, tools, stablecoins, digital securities |
| Mar 17, 2026 | Joint SEC-CFTC Interpretation | Coordinated jurisdiction over five categories |
| Apr 2026 | Staff Statement on Broker-Dealer Registration | Crypto asset securities interface requirements |

### Howey Test (Still the Gatekeeper)

A crypto asset is a security (digital security) when:
1. Investment of money
2. In a common enterprise
3. With reasonable expectation of profits
4. Derived from the essential managerial efforts of others

**2026 heightened standard**: Representations must be "explicit and unambiguous" regarding essential managerial efforts (not merely implicit).

---

## 2. Five-Category Taxonomy

SEC Release No. 33-11412 (March 17, 2026), co-signed by SEC Chairman Atkins and CFTC Chairman Selig at the DC Blockchain Summit:

| Category | Definition | Securities Law? | Examples |
|----------|-----------|----------------|----------|
| **Digital Commodities** | Integral to functional cryptosystems; value from supply/demand, no central party | NO | BTC, ETH, SOL, XRP, ADA, APT, AVAX, LINK, DOGE |
| **Digital Collectibles** | Artwork, music, trading cards, memecoins; value from sentiment | NO | NFT art, memecoins, in-game items |
| **Digital Tools** | Memberships, tickets, credentials, identity badges; functional utility | NO | Access tokens, credential badges |
| **Stablecoins** | Stable value vs reference asset; low-risk liquid reserves | NO (under GENIUS Act) | USDC, PYUSD, covered stablecoins |
| **Digital Securities** | Traditional securities tokenized on blockchain | YES — full compliance | Tokenized equity, debt, real estate, fund shares |

### Investment Contract Safe Harbor

Non-security crypto assets may separate from investment contracts when:
- Issuer fulfills all represented essential managerial efforts, OR
- Sufficiently long period passes showing issuer has abandoned efforts

### Activities Outside Securities Laws
- Protocol mining (PoW)
- Protocol staking (PoS, self-staking, custodial, liquid)
- Staking receipt tokens
- Wrapping of non-security crypto assets into redeemable wrapped tokens
- Retroactive airdrops of non-security crypto assets

### Proposed Safe Harbors (Not Yet Finalized)
- **Startup exemption**: Time-limited registration exemption, up to $5M over 4 years
- **Fundraising exemption**: New offerings up to $75M annually

---

## 3. Tokenization Models

The Jan 28, 2026 Joint Staff Statement established three models:

### Category 1: Issuer-Sponsored Tokenization

The issuer directly authorizes tokenized representations of its own securities.

**Model A — Direct Integration (DLT as Official Record)**
- Distributed ledger IS the official book-entry system
- Blockchain transfers = legally effective transfers
- Transfer agent maintains master securityholder file on-chain

**Model B — Parallel Ledger (Off-Chain Authoritative)**
- Master securityholder file remains off-chain with transfer agent
- On-chain tokens track positions but off-chain record is authoritative
- Reconciliation procedures required between on-chain/off-chain

**Key advantage**: Token holders have direct ownership claims; avoid general creditor risk.

### Category 2: Third-Party Tokenization (Custodial)

A third party creates crypto assets representing holder's interest in underlying securities held by a custodian.

- Securities remain immobilized with custodian
- Holders possess "security entitlements" not direct ownership
- **Risk**: Token holder becomes general creditor if intermediary fails

### Category 3: Third-Party Tokenization (Synthetic)

Third party issues tokens providing synthetic exposure without conferring issuer rights.

- Includes structured notes, exchangeable stock, security-based swaps
- May trigger Section 3(a)(68) classification as security-based swap
- Retail availability severely limited (must trade on national exchanges)

### Decision Matrix

| Factor | Category 1 | Category 2 | Category 3 |
|--------|-----------|-----------|-----------|
| Issuer involvement | Required | Not required | Not required |
| Holder rights | Direct ownership | Security entitlement | Contractual exposure |
| Bankruptcy risk | Protected | General creditor | General creditor |
| Regulatory complexity | Moderate | High | Highest |
| Recommended for new offerings | **YES** | Situational | Avoid for retail |

---

## 4. DTC No-Action Letter

**Issuer**: Depository Trust Company (DTCC subsidiary)
**Date**: December 11, 2025
**Relief**: SEC Division of Trading and Markets will not recommend enforcement
**Duration**: 3 years from launch (H2 2026 target)
**Program Name**: DTCC Tokenization Services (Preliminary Base Version)

### Eligible Securities

| Asset Class | Specifics |
|-------------|-----------|
| Equities | Russell 1000 Index constituents |
| ETFs | S&P 500, Nasdaq-100 tracking ETFs |
| U.S. Treasuries | Bills, notes, bonds |
| Selection criteria | Highly liquid securities only |

### Excluded Participants
- Entities with U.S. tax withholding obligations
- Treasury International Capital (TIC) reporting entities

### Operational Architecture

```
┌─────────────────────────────────────────────────────┐
│                   DTC (Cede & Co.)                   │
│            Registered Owner with Issuers             │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │   Standard   │    │  Digital Omnibus Account  │   │
│  │  Participant │    │  (Immobilized Securities) │   │
│  │   Accounts   │    └──────────┬───────────────┘   │
│  └──────────────┘               │                   │
│                          ┌──────┴──────┐            │
│                          │  Token Mint │            │
│                          └──────┬──────┘            │
└─────────────────────────────────┼───────────────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    │             │             │
              ┌─────┴─────┐ ┌────┴────┐ ┌─────┴─────┐
              │Registered │ │Registered│ │Registered │
              │ Wallet A  │ │Wallet B  │ │ Wallet C  │
              │(Participant│ │(Participant│ │(Participant│
              │    1)     │ │    2)    │ │    3)     │
              └───────────┘ └─────────┘ └───────────┘
                    ↕             ↕             ↕
              Direct peer-to-peer token transfers
              (24/7, no DTC instruction needed)
```

### Key Mechanics

**Tokenization Flow**:
1. Participant submits Tokenization Instruction to DTC
2. Securities move to Digital Omnibus Account (immobilized)
3. Corresponding tokens minted to participant's Registered Wallet
4. Peer-to-peer transfers between Registered Wallets — no DTC instruction needed

**De-tokenization**:
1. Participant submits de-tokenization instruction
2. Tokens burned
3. Securities returned to standard participant account

**Anti-Double-Spending**: Securities in Digital Omnibus Account remain immobilized on DTC's centralized systems until tokens are burned.

### LedgerScan Monitoring
- Off-chain, cloud-based monitoring system
- Tracks token movements and Registered Wallet holdings in near real-time
- Official books and records for tokenized entitlements
- Scans approved blockchains continuously

### Root Wallet
- DTC maintains root wallet with override authority
- Can mint, burn, transfer, or convert tokens without participant permission
- Keys stored in cold storage except for daily operational needs
- Used for error correction and malfeasance response

### Critical Limitations

| Constraint | Detail |
|-----------|--------|
| No collateral value | Tokens cannot serve as collateral for net debit caps |
| No settlement value | Not integrated with DTC delivery-versus-payment |
| No credit for monitoring | Cannot count toward collateral requirements |
| No default management | Cannot be used as default management resources |
| DTC-only relief | Other market participants must obtain separate approvals |

### Regulatory Relief Granted

DTC received no-action relief from:

| Rule/Section | What It Covers |
|-------------|----------------|
| Section 19(b) + Rule 19b-4 | Proposed rule change filing and public comment |
| Regulation SCI | Systems compliance and integrity |
| Rules 17Ad-22(e)(1)-(23) | Default management, systems testing, resumption |
| Rules 17Ad-25(i)-(j) | Governance controls on core service providers |

### Quarterly Reporting Obligations

DTC must report to SEC staff:
- Participant listings and wallet registrations
- Tokenization activity (share counts, valuations)
- Transfer volumes and de-tokenization data
- Root wallet usage for error correction
- System outages and durations
- Approved blockchain protocols

### Blockchain Requirements (Principles-Based)

- Tokens only transferable among known Registered Wallets
- DTC retains unilateral authority to correct erroneous transactions
- No specific blockchain mandated — any protocol meeting Technology Standards eligible
- OFAC screening before wallet registration

### Operational Resilience
- Tier 2 status: dual-site operations
- 4-hour recovery objectives
- 2-minute maximum data loss tolerance
- Annual disaster recovery testing

---

## 5. OTCM / RWA Tokens Category 1 Framework

**Entity**: Groovy Company, Inc. (Wyoming Corporation), dba RWA Tokens Corp
**OTC Ticker**: GROO
**Blockchain**: Solana Mainnet-Beta (SPL Token-2022)
**Trading Venue**: CEDEX (cedex.market)
**Transfer Agent**: Empire Stock Transfer (SEC §17A-registered)
**Model**: SEC Category 1 Model B (issuer-authorized, transfer-agent-custodied)

### Three Asset Classes

#### 1. Equities — ST22 Digital Securities

| Attribute | Detail |
|-----------|--------|
| Backing | 1:1 by Common Class B shares |
| Custodian | Empire Stock Transfer |
| CUSIP | Assigned at custody intake |
| Transfer controls | 42 Solana Transfer Hooks |
| Eligible issuers | OTC microcaps, NASDAQ/AMEX/TSX listed, global exchanges, U.S. private companies |

**Issuance Flow (5 steps)**:
1. Board authorization — Certificate of Designation for Common Class B shares
2. Custody & CUSIP — Deposit with Empire Stock Transfer; CUSIP assigned
3. Mint & deploy — ST22 tokens minted 1:1 on Solana; 42 Transfer Hooks active
4. Launch on CEDEX — Trading begins; permanent liquidity (LP tokens burned)
5. Investor access — Onboarding via Empire's compliance dashboard

#### 2. CORE-CM Tokens — Mineral & Hydrocarbon

| Attribute | Detail |
|-----------|--------|
| Structure | Zero-coupon, asset-backed, single-redemption |
| Backing | Specified mineral or hydrocarbon project cash flows |
| SPV | Delaware or Cayman holding entity + local OpCo |
| Custodian | SEC-registered institutional transfer agent |
| Coverage | 18 mineral categories + 5 hydrocarbon streams |
| Geography | 4 hemispheric subregions (Americas focus) |

**12-Step Lifecycle**:
- Phase A (1-4): SPV formation → paper bond draft → institutional custody → token mint
- Phase B (5-8): Five-check compliance → Reg D/S qualification → subscription/escrow → token delivery
- Phase C (9-12): Compliance-gated holding → maturity/trigger event → token burn → face value payment (USD)

#### 3. Real Estate — ST22 Digital Securities

| Attribute | Detail |
|-----------|--------|
| Backing | 1:1 against independent MAI appraisal NAV |
| Minimum NAV | $5M+ |
| Reappraisal | Bi-annual by independent third-party appraiser |
| Jurisdictions | Nevada (issuer) + Wyoming (digital asset law W.S. 34-29-101) + Federal (SEC) |
| Eligible assets | Commercial office, logistics, mixed-use, industrial, hospitality |

**Price Discovery**:
- CPMM (Constant Product Market Maker) on CEDEX — 24/7 continuous pricing
- NAV anchor — published on-chain via oracle network every 6 months
- TWAP (Time-Weighted Average Pricing) — dampens short-term volatility

**Real Estate-Specific Transfer Hook Controls (5 additional)**:
1. NAV deviation cap — trades exceeding % from recent NAV blocked
2. Reappraisal freshness — trading restricted if appraisal >180 days old
3. Mortgage-event halt — material mortgage changes trigger trading halt
4. Distribution-period lockup — restrictions during rental distributions
5. Concentration limits — property-specific caps beyond standard 4.99%

---

## 6. Offering Exemptions

### Exemption Matrix

| Exemption | Investor Type | Cap | Key Requirements | Timeline |
|-----------|--------------|-----|------------------|----------|
| **Reg D §506(b)** | U.S. accredited + up to 35 sophisticated | No cap | No general solicitation; Form D within 15 days | N/A |
| **Reg D §506(c)** | U.S. accredited only | No cap | General solicitation OK; must verify accreditation | N/A |
| **Reg D §501(a)** | U.S. accredited | No cap | Standard accredited investor definition | N/A |
| **Reg S** | Non-U.S. persons | No cap | Offshore transaction; no directed selling in U.S. | Category 2: 40-day distribution compliance period |
| **Reg A+ Tier 1** | All U.S. + non-U.S. | $20M/12 mo | SEC qualification required; state review | 6-12 months |
| **Reg A+ Tier 2** | All U.S. + non-U.S. | $75M/12 mo | SEC qualification; ongoing reporting; non-accredited limited to 10% income/net worth | 6-12 months |
| **Reg CF §4(a)(6)** | U.S. accredited + non-accredited retail | $5M/12 mo | Via registered funding portal; investor caps apply | 2-4 months |

### Holding Period Requirements (Rule 144)

| Exemption | Holding Period | Enforced Via |
|-----------|---------------|-------------|
| Reg D | 6 months (reporting issuers) / 12 months (non-reporting) | Transfer Hook #9-16 |
| Reg S | 40 days (Cat 1) / 6 months (Cat 2) / 12 months (Cat 3) | Transfer Hook #9-16 |
| Reg CF | 12 months | Transfer Hook #9-16 |

### Blue Sky (State Securities Laws)

- **Reg D §506**: Federal preemption of state registration (but Form D filing required in each state where securities are sold)
- **Reg A+ Tier 2**: Federal preemption of state qualification
- **Reg A+ Tier 1**: No preemption — must qualify in each state
- **Reg CF**: Federal preemption

---

## 7. Transfer Agent & Custody

### Transfer Agent Requirements (SEC Rules 17Ad-1 through 17Ad-23)

Transfer agents maintaining blockchain-based master securityholder files must:

| Requirement | Standard |
|------------|----------|
| Registration | SEC §17A registration required |
| Record integrity | Tamper-resistant records (blockchain provides) |
| Corporate actions | Automated dividend, voting, and distribution processing |
| Privacy | Personal data stored off-chain; only wallet addresses on-chain |
| Reconciliation | On-chain ↔ off-chain record reconciliation procedures |
| Reporting | SEC reporting obligations unchanged |

### Custody Models

**Category 1 (Recommended for New Offerings)**:

```
┌──────────┐    authorizes     ┌─────────────────────┐
│  Issuer  │ ───────────────→  │ SEC §17A Transfer   │
│  (Board) │                   │ Agent (e.g. Empire)  │
└──────────┘                   │                     │
                               │ • Holds paper certs │
                               │ • CUSIP assignment   │
                               │ • Master file        │
                               │ • Investor onboarding│
                               └─────────┬───────────┘
                                         │ 1:1 mint
                                         ▼
                               ┌─────────────────────┐
                               │  Solana Token-2022   │
                               │  (ST22 with 42 hooks)│
                               └─────────────────────┘
```

**DTC Model (Institutional)**:

```
┌──────────┐                   ┌─────────────────────┐
│  Issuer  │    registered     │       DTC            │
│          │ ─── to Cede & ──→ │ (CSD / Clearing     │
│          │     Co.           │  Agency)             │
│          │                   │                     │
│          │                   │ Digital Omnibus Acct │
│          │                   └─────────┬───────────┘
│          │                             │ tokenize
│          │                             ▼
│          │                   ┌─────────────────────┐
│          │                   │  Registered Wallets  │
│          │                   │  (DTC Participants)  │
│          │                   └─────────────────────┘
```

### Tripartite Custody Agreement

For Category 1 offerings, a three-party custody agreement between:
1. **Issuer** — authorizes tokenization of its shares
2. **Transfer Agent** — holds paper certificates, maintains master securityholder file
3. **Investor** — receives tokens into verified wallet

---

## 8. Token Design & Smart Contract Controls

### Solana SPL Token-2022 (ST22)

The Token-2022 standard on Solana provides native Transfer Hook extensions — custom logic that executes on EVERY token transfer at the runtime level (not bypassable by the sender).

### 42 Transfer Hook Controls

Embedded at the Solana SPL Token-2022 level, executing on every transaction:

#### Core Controls (All Asset Classes — Hooks 1-26)

| Hook # | Category | Control | Mechanism |
|--------|----------|---------|-----------|
| 1-4 | Position Limits | 4.99% maximum wallet cap | Block transfers exceeding individual position limit |
| 5-8 | Circuit Breakers | >10% price move in 5 min | Trigger 15-minute trading halt |
| 9-16 | Holding Periods | Rule 144 enforcement | 6 mo (Reg D), 12 mo (Reg S) lockup |
| 17-20 | Sanctions Screening | OFAC/SDN check | Chainalysis KYT + TRM Labs on every transfer |
| 21-26 | KYC/KYB/AML/KYW | Five-check stack | Protocol-level verification gate |

#### Asset-Specific Controls (Hooks 27-42)

| Hook # | Asset Class | Control |
|--------|------------|---------|
| 27-31 | Real Estate | NAV deviation cap, appraisal freshness, mortgage-event halt, distribution lockup, concentration |
| 32-36 | CORE-CM | Project milestone gates, maturity countdown, SPV dissolution trigger, jurisdictional transfer limits, commodity-price circuit breaker |
| 37-42 | Equity | Insider trading blackout windows, tender offer response period, proxy voting lockup, M&A event halt, delisting response, cross-listing coordination |

### Token Architecture Template

```
Token {
  standard: "SPL Token-2022",
  extensions: [
    "TransferHook",       // 42 compliance controls
    "MetadataPointer",    // Links to off-chain legal docs
    "NonTransferable",    // Optional: for restricted periods
    "InterestBearing",    // Optional: for debt instruments
    "ConfidentialTransfer" // Optional: for privacy
  ],
  backing: "1:1 with custodied security",
  mint_authority: "Transfer Agent controlled",
  freeze_authority: "Compliance officer controlled",
  supply: "Matches exact share count in custody"
}
```

### Smart Contract Security Requirements

- Mint authority restricted to transfer agent's authorized signers
- Freeze authority for compliance officer (regulatory halt, sanctions hit)
- Burn authority for de-tokenization and maturity events
- No owner-upgradeable proxy patterns — immutable after audit
- Multi-sig (2-of-3 minimum) for all administrative functions
- Time-lock on parameter changes (48-hour minimum)

---

## 9. Investor Verification Stack

### Five-Check Compliance (All Investors, All Exemptions)

| # | Check | What It Covers | Tools |
|---|-------|---------------|-------|
| 1 | **KYC** | Government ID, proof of address, biometric liveness | Jumio, Onfido, Sumsub |
| 2 | **KYB** | Entity formation docs, beneficial ownership, good standing | Manual + database verification |
| 3 | **AML** | Continuous transaction monitoring | Chainalysis KYT, TRM Labs |
| 4 | **Sanctions** | OFAC/SDN, PEP, adverse media screening | Chainalysis, ComplyAdvantage |
| 5 | **KYW** | Wallet-risk scoring; destination wallet screened for illicit exposure | Chainalysis KYT, TRM Labs |

### Verification Timing
- **Onboarding**: 1-4 business days typical
- **Re-attestation**: Every 12 months
- **Continuous monitoring**: AML + sanctions run on every transfer (hooks 17-26)

### Accredited Investor Verification (Reg D §506(c))

Must use one of:
1. Tax returns (last 2 years showing $200K+ income / $300K+ joint)
2. Bank/brokerage statements showing $1M+ net worth (excl. primary residence)
3. Written confirmation from registered broker-dealer, SEC-registered investment adviser, licensed attorney, or CPA
4. Existing certifications from recognized platforms (e.g., VerifyInvestor.com)

---

## 10. Settlement Infrastructure

### Stablecoin Settlement

| Stablecoin | Issuer | Framework | Use Case |
|-----------|--------|-----------|----------|
| USDC | Circle | GENIUS Act compliant | Primary settlement currency |
| PYUSD | PayPal | GENIUS Act compliant | Alternative settlement |

### Settlement Characteristics

| Attribute | Specification |
|-----------|--------------|
| Finality | Sub-second on Solana |
| Cost | Sub-cent transaction fees |
| Availability | 24/7/365 |
| Banking rails | Not required |
| Reconciliation | Automatic via on-chain records |

### DTC Settlement (Institutional)

- Tokenized entitlements explicitly EXCLUDED from DTC settlement (DVP)
- On-chain transfers between Registered Wallets occur 24/7
- Off-chain settlement for de-tokenized securities follows standard T+1

---

## 11. Trading Venue Design

### CEDEX (Compliant Exchange for Digital Securities)

| Feature | Specification |
|---------|--------------|
| Price discovery | CPMM (Constant Product Market Maker) |
| Availability | 24/7 (subject to compliance-gated transfer hooks) |
| Liquidity | Permanent — LP tokens burned at initialization |
| Real estate pricing | NAV-anchored with bi-annual independent appraisal |
| Volatility dampening | TWAP (Time-Weighted Average Pricing) |

### ATS Considerations

If building a trading venue for tokenized securities:
- Must register as ATS with SEC (Form ATS or Form ATS-N)
- Alternatively, operate as a national securities exchange
- Broker-dealer registration required for ATS operators
- FINRA membership required
- Reg ATS fair access rules apply above volume thresholds
- Consider: ATS exemption may apply if trading only within a single issuer's ecosystem

### Broker-Dealer Requirements

Firms facilitating tokenized security trading must determine whether:
- Broker-dealer registration with SEC required
- FINRA membership required
- State registrations needed
- Net capital requirements met
- Customer protection rules (Rule 15c3-3) satisfied
- Books and records requirements (Rules 17a-3, 17a-4) maintained

---

## 12. Asset Class Playbooks

### Playbook A: Tokenized Equity

```
Step 1: Corporate Authorization
  └─ Board resolution authorizing Common Class B shares
  └─ Certificate of Designation filed with state of incorporation
  └─ Securities counsel opinion letter

Step 2: Offering Structure
  └─ Select exemption: Reg D §506(c) (accredited, general solicitation OK)
  └─ Prepare PPM (Private Placement Memorandum)
  └─ Subscription agreement with blockchain-specific disclosures
  └─ File Form D with SEC within 15 days of first sale

Step 3: Transfer Agent Setup
  └─ Engage SEC §17A-registered transfer agent (e.g., Empire Stock Transfer)
  └─ Execute tripartite custody agreement (issuer + TA + protocol)
  └─ CUSIP assigned at custody intake

Step 4: Token Deployment
  └─ Mint ST22 tokens 1:1 on Solana
  └─ Activate 42 Transfer Hook controls
  └─ Smart contract audit (Certik, Trail of Bits, Ottersec)

Step 5: Investor Onboarding
  └─ Five-check verification (KYC/KYB/AML/Sanctions/KYW)
  └─ Accreditation verification (if Reg D §506(c))
  └─ Wallet registration and compliance gating

Step 6: Launch & Trading
  └─ List on CEDEX or compliant ATS
  └─ Initialize liquidity pool (burn LP tokens for permanence)
  └─ Begin continuous AML monitoring
```

### Playbook B: CORE-CM Mineral/Hydrocarbon Token

```
Step 1: SPV Formation
  └─ Delaware or Cayman holding entity
  └─ Local operating company in source jurisdiction
  └─ Mining/extraction rights documentation

Step 2: Bond Structuring
  └─ Paper bond certificate — zero-coupon, project-specific terms
  └─ Face value, maturity date, trigger events defined
  └─ Independent reserve certification

Step 3: Transfer Agent Custody
  └─ Engage SEC-registered institutional transfer agent
  └─ Paper bond certificates held in institutional custody
  └─ TA is definitive legal record

Step 4: Offering & Compliance
  └─ Reg D (accredited U.S.) + Reg S (non-U.S.)
  └─ PPM with mineral/hydrocarbon-specific risk disclosures
  └─ Geological survey and reserve reports appended

Step 5: Token Mint & Controls
  └─ CORE-CM tokens minted on Solana
  └─ Project-specific Transfer Hooks activated
  └─ Milestone-gated release schedule

Step 6: Lifecycle Management
  └─ Compliance-gated holding in verified wallets
  └─ Project progress reporting to token holders
  └─ Maturity/trigger event → token burn → face value paid in USD
```

### Playbook C: Tokenized Real Estate

```
Step 1: Property Qualification
  └─ Minimum NAV: $5M+
  └─ Independent MAI appraisal
  └─ Title search and insurance
  └─ Environmental assessment (Phase I minimum)

Step 2: Three-Jurisdiction Structure
  └─ Nevada: Issuer corporate structure; Certificate of Designation
  └─ Wyoming: Digital asset layer (W.S. 34-29-101 et seq.)
  └─ Federal: SEC offering under Reg D / Reg S / Reg CF

Step 3: Token Design
  └─ ST22 tokens minted 1:1 against NAV
  └─ 42 core + 5 real-estate-specific Transfer Hooks
  └─ NAV oracle integration for on-chain price anchoring

Step 4: Trading Venue
  └─ CEDEX listing with CPMM + NAV anchor
  └─ TWAP for volatility dampening
  └─ Permanent liquidity (LP burn)

Step 5: Ongoing Obligations
  └─ Bi-annual independent reappraisal
  └─ Rental income distribution via stablecoin
  └─ Property management reporting
  └─ Mortgage event monitoring and halt triggers
```

---

## 13. Fund Tokenization

*Source: Dilendorf Law Firm — Fund Tokenization whitepaper and practice guides*

### Fund Types Eligible for Tokenization

| Fund Type | Structure | Typical Strategy | Tokenization Benefit |
|-----------|----------|-----------------|---------------------|
| **Hedge Fund** | LP or LLC | Long/short, macro, event-driven | Automated distributions, 24/7 liquidity |
| **Private Equity** | LP | Buyout, growth, distressed | Fractional LP interests, secondary market |
| **Venture Capital** | LP | Early-stage, seed, Series A-C | Broader LP base, programmable carry |
| **Real Estate Fund** | LP | Core, value-add, opportunistic | NAV-anchored pricing, rental distributions |
| **Master-Feeder** | Hybrid US/Cayman | Multi-strategy | Cross-border tokenized LP interests |

### Investment Company Act Exclusions

Tokenized funds must qualify for an ICA exclusion to avoid registering as an investment company:

| Exclusion | Requirement | LP Cap | Investor Type | Best For |
|-----------|------------|--------|---------------|----------|
| **§3(c)(1)** | ≤100 beneficial owners | 100 | Any accredited | Small funds, emerging managers |
| **§3(c)(7)** | Qualified purchasers only | 2,000 | QPs ($5M+ investments) | Large institutional funds |
| **§3(c)(5)(C)** | Primarily real estate | N/A | Any accredited | RE funds (case-by-case analysis) |

**Critical tokenization warning**: Each token holder counts as a beneficial owner. If secondary market trading pushes holder count above 100 (§3(c)(1)) or 2,000 (§3(c)(7)), the fund must register or face enforcement. Transfer hooks must enforce holder count limits.

### Advisers Act Considerations

- Funds with >$100M AUM must register as investment adviser with SEC (Form ADV)
- Funds with $25M-$100M register with state(s)
- Exemptions: VC fund adviser exemption (§203(l)), private fund adviser exemption (§203(m)) for <$150M AUM
- **Tokenization impact**: Broader LP base via secondary trading may push AUM above thresholds faster

### GP/LP Economics in Tokenized Funds

#### Fee Structure

| Fee | Typical Range | Payment |
|-----|--------------|---------|
| Management Fee | 1-2% of AUM | Monthly or quarterly, automated via smart contract |
| Carried Interest | 15-20% of profits above hurdle | At distribution events |
| Acquisition Fee | 0.5-1% of asset purchase price | At close (RE funds) |
| Property Management | 3-4% of gross monthly rents | Monthly (RE funds) |
| Formation Cost Reimbursement | Actual costs | Amortized 3-5 years |

#### Distribution Waterfall (Smart Contract-Enforced)

```
Priority 1: Return of Capital
  └─ LP receives invested capital back first

Priority 2: Preferred Return
  └─ LP receives accrued preferred return (6-12% annually, varies by strategy)
  └─ NOT guaranteed — contingent on available cash flow

Priority 3: GP Catch-Up (if applicable)
  └─ GP receives 100% until they reach carried interest share

Priority 4: Residual Split
  └─ Split between LP and GP per carry agreement
  └─ Common splits: 80/20, 70/30, 60/40, 50/50 (LP/GP)
```

**Tokenization advantage**: Waterfall logic encoded in smart contracts for transparent, automated distributions. LP token holders receive distributions in stablecoin (USDC/PYUSD) directly to wallet.

### LP Interest Tokenization Structure

```
┌─────────────────────────────────────────────┐
│              Fund Entity (LP)                │
│          (Delaware or Cayman)                │
│                                             │
│  ┌───────────┐        ┌──────────────────┐  │
│  │    GP     │        │   LP Interests   │  │
│  │ (Manager) │        │  (Tokenized)     │  │
│  │           │        │                  │  │
│  │ Carry +   │        │ ST22 Tokens      │  │
│  │ Mgmt Fee  │        │ 1:1 with LP %    │  │
│  └───────────┘        └────────┬─────────┘  │
│                                │             │
└────────────────────────────────┼─────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │            │            │
              ┌─────┴─────┐ ┌───┴───┐ ┌─────┴─────┐
              │  LP Token │ │LP Token│ │  LP Token │
              │  Holder A │ │Holder B│ │  Holder C │
              │  (Reg D)  │ │(Reg S) │ │  (Reg CF) │
              └───────────┘ └───────┘ └───────────┘
```

### Fund Duration Models

| Model | Duration | Subscriptions | Redemptions | Best For |
|-------|----------|---------------|-------------|----------|
| **Closed-End** | 5-7 years | Fixed period | At liquidation | Distressed, value-add, opportunistic |
| **Open-End** | Perpetual | Quarterly | Quarterly (with notice) | Core assets, stable cash flow |
| **Semi-Open** | 7-10 years | Periodic | Limited windows | Growth equity, late-stage VC |

**Tokenization impact on closed-end funds**: LP tokens can trade on ATS during fund life, providing liquidity without fund-level redemptions. This is the primary value proposition — historically illiquid LP interests gain secondary market liquidity.

### Side Letters in Tokenized Funds

Side letters remain common — specific investors get different terms without notifying other LPs. In tokenized structures:
- Side letter terms encoded as wallet-specific Transfer Hook parameters
- Different fee structures, co-invest rights, or reporting levels per wallet class
- MFN (Most Favored Nation) provisions may require programmatic enforcement

### SEC Reporting Thresholds

| Trigger | Threshold | Consequence |
|---------|-----------|-------------|
| Total assets >$10M AND record holders ≥2,000 | Exchange Act §12(g) | Must register equity securities with SEC |
| Total assets >$10M AND non-accredited holders ≥500 | Exchange Act §12(g) | Must register equity securities with SEC |

**Transfer hooks must count unique holders and block transfers that would breach these thresholds.**

### Tokenized Fund Formation Timeline & Costs

| Phase | Traditional | Tokenized | Delta |
|-------|-----------|-----------|-------|
| Legal structuring | 3-5 weeks | 4-6 weeks | +1-2 weeks |
| Documentation (PPM, LPA, Sub Docs) | Included | Included + smart contract specs | +1 week |
| Smart contract dev + audit | N/A | 2-4 weeks | +2-4 weeks |
| ATS pre-listing coordination | N/A | 1-2 weeks | +1-2 weeks |
| **Total** | **3-5 weeks** | **6-8 weeks** | **+3-4 weeks** |
| **Formation cost** | **$35K-$60K** | **~$100K** | **+$40K-$65K** |
| Annual admin | $15K-$25K | $20K-$35K | +$5K-$10K |

### Playbook D: Tokenized Fund

```
Step 1: Fund Structure Decision
  └─ Fund type: Hedge / PE / VC / RE / Master-Feeder
  └─ ICA exclusion: §3(c)(1) (≤100 holders) or §3(c)(7) (QPs only)
  └─ Jurisdiction: Delaware LP (domestic) or Cayman (offshore feeder)
  └─ Advisers Act: Exempt or registered?

Step 2: Economics Design
  └─ Management fee: 1-2% AUM
  └─ Carry: 15-20% above hurdle (6-12% pref return)
  └─ Waterfall: American vs European
  └─ Encode waterfall in smart contract specification

Step 3: Offering Structure
  └─ Reg D §506(c) (U.S. accredited) + Reg S (non-U.S.) typical
  └─ PPM with fund-specific + blockchain-specific risk disclosures
  └─ LPA (Limited Partnership Agreement) with tokenization addendum
  └─ Subscription agreement with wallet registration

Step 4: Transfer Agent & Custody
  └─ Engage SEC §17A-registered transfer agent
  └─ LP interest certificates deposited in custody
  └─ CUSIP assigned (if applicable for ATS trading)

Step 5: Token Deployment
  └─ Mint LP tokens (ST22 on Solana or ERC-3643 on Ethereum)
  └─ Activate Transfer Hooks:
     ├─ Holder count limit (§3(c)(1): 100 / §3(c)(7): 2,000)
     ├─ Accredited investor / QP gate
     ├─ Holding period (6 mo Reg D / 12 mo Reg S)
     ├─ OFAC/sanctions screening
     └─ §12(g) threshold monitoring
  └─ Smart contract audit

Step 6: ATS Pre-Listing
  └─ Coordinate with chosen ATS (tZERO, Securitize, INX)
  └─ Ensure token compatibility with ATS platform
  └─ Test transfer restrictions and compliance hooks
  └─ Verify digital restrictive legends maintained

Step 7: Launch & Ongoing
  └─ Accept subscriptions + onboard investors (five-check KYC)
  └─ Automated distribution via smart contract (stablecoin)
  └─ Quarterly NAV reporting (RE funds)
  └─ Annual audit
  └─ Form D amendment annually
  └─ Monitor holder count vs ICA thresholds
```

### Critical Fund Tokenization Warnings

1. **Token recall is not simple**: If tokens are poorly structured or incompatible with ATS, recalling and replacing them may not be possible or may be costly and legally complicated. Get structure right before minting.

2. **Holder count is a regulatory cliff**: Exceeding §3(c)(1) or §3(c)(7) limits triggers ICA registration. Transfer hooks MUST enforce this at the protocol level.

3. **ATS compatibility is non-negotiable**: Establish contacts with the ATS before primary issuance. Ensure digital security features match platform configurations.

4. **Side letters create smart contract complexity**: Different terms per LP wallet class multiply testing surface. Budget extra audit time.

5. **$10M + 2,000 holders = Exchange Act registration**: Monitor total assets and unique holder count continuously.

---

## 14. Robinhood Tokenization Policy Proposals

*Source: Robinhood Markets, Inc. — Tokenization Memo (January 2025)*

### RWA Tokenization Categories

| Type | Description |
|------|-------------|
| Stablecoins | 1:1 pegged to fiat; reserve-backed (money market fund analogy) |
| Tokenized Securities | Stocks, bonds, securitized instruments on blockchain |
| Tokenized Bank Deposits | Savings/checking accounts converted to digital tokens |
| Tokenized Real Estate | Property or cash flows as blockchain tokens |
| NFTs | Unique-item ownership (art, video, digital content) |

### Benefits Framework

| Benefit | Mechanism |
|---------|-----------|
| Liquidity | Illiquid assets (RE, art) → tradeable digital assets on platforms |
| Efficiency | Smart contracts automate transactions, eliminate intermediaries |
| Transparency | Immutable blockchain record reduces fraud, enhances audit |
| Fractionalization | Fractional ownership democratizes access beyond institutions |
| Financial Inclusion | Previously unaffordable banking/investment services accessible |
| 24/7 Settlement | Smart contracts enable instant settlement; less capital-intensive |
| Global Reach | No geographical limitations; extended investor pool |

### U.S. Regulatory Gaps Identified

Robinhood identifies critical regulatory impediments blocking tokenization at scale:

| Impediment | Problem | Robinhood Proposal |
|-----------|---------|-------------------|
| Registration regime | Assumes centralized structures, standardized offerings, established intermediaries — incompatible with decentralized tokenized assets | Adapt Form S-1 for digital asset securities with token-specific disclosures |
| Reg D-only viable path | Limits investor pool to accredited investors; blocks retail participation | Use Reg CF and Reg A as "regulatory sandboxes" for tokenized offerings |
| SPBD limitations | Only 2 entities qualified; cannot hold securities AND non-securities (stablecoins); time-limited (expires 2026) | Permanent SPBD rulemaking allowing securities + non-securities + stablecoins |
| Safeguarding Proposal | Would prohibit transfer of digital assets from qualified custodian to exchange/trading venue | Withdraw Safeguarding Proposal; amend custody rules for banks/BDs on blockchain |
| SAB 121 | Forces banks/non-SPBD BDs to record digital assets as balance sheet liabilities | Revoke SAB 121 to encourage institutional custody participation |
| No ATS framework for tokens | ATS better suited than exchanges for tokenized assets but no streamlined path | Tailor Reg ATS to provide streamlined registration for tokenized asset ATS |
| No exchange path | Trading on national securities exchanges not yet supported | Phased approach: ATS first → expand to national exchanges after learnings |
| Clearance/settlement antiquated | Central counterparty model doesn't leverage blockchain instant settlement | SEC + DTCC comprehensive review of clearance/settlement rules for blockchain |

### Robinhood's Proposed Phased Approach

```
Phase 1: Registration Reform
  └─ Adapt Form S-1 for digital asset securities
  └─ Issue guidance on Reg CF and Reg A for tokenized offerings

Phase 2: Trading Infrastructure
  └─ Streamline ATS registration for tokenized assets
  └─ Make SPBD permanent; allow securities + non-securities + stablecoins

Phase 3: Custody & Accounting
  └─ Withdraw Safeguarding Proposal
  └─ Revoke SAB 121
  └─ Allow banks, BDs, qualified custodians to hold tokens on blockchain

Phase 4: Settlement Modernization
  └─ SEC + DTCC review of clearance/settlement rules
  └─ Accommodate blockchain post-trade processing
  └─ Eliminate need for central counterparties where smart contracts suffice

Phase 5: Exchange Listing
  └─ Expand from ATS to national securities exchanges
  └─ Full integration of tokenized securities into traditional market structure
```

### Market Context (Jan 2025)

- BlackRock launched BUIDL (tokenized U.S. Treasury fund, Mar 2024)
- Ripple tokenized hundreds of millions on XRP Ledger
- Goldman Sachs announced tokenized RE and money market funds
- McKinsey estimates tokenized fund market could reach $2T by 2030
- EU MiCA regulation already harmonizes tokenized asset framework across member states
- Hong Kong, Singapore, Abu Dhabi have comprehensive token frameworks

---

## 15. IOSCO International Standards

*Source: IOSCO Final Report on Tokenisation of Financial Assets (IOSCOPD809, November 2025)*

### Core Principle

**"Same activities, same risks, same regulatory outcomes"** — IOSCO's technology-neutral principle applied across member jurisdictions.

### Key Findings

| Finding | Status |
|---------|--------|
| Tokenized products issued in several jurisdictions | Compliant with existing regulatory frameworks |
| Adoption remains limited | New/heightened risks hinder scalability |
| Promised secondary market liquidity | Not yet fully achieved |
| Efficiency gains from DLT | Shorter settlement cycles, improved collateral mobility |
| Tokenized MMFs on public blockchains | Face trading limitations; restricted to whitelisted investors |

### Identified Risks

| Risk Category | DLT-Specific Manifestation |
|--------------|---------------------------|
| Legal uncertainty | Unclear legal status of tokenized assets across jurisdictions |
| Operational vulnerabilities | Smart contract bugs, node failures, consensus issues |
| Cyber threats | Key management, wallet compromise, bridge exploits |
| Interoperability | Fragmented blockchains prevent cross-chain settlement |
| Settlement asset quality | Lack of credible on-chain settlement assets (stablecoins not universally trusted) |

### Two Major Scalability Impediments

1. **Lack of interoperability across blockchains** — tokens on one chain cannot easily transfer/settle on another
2. **Lack of high-quality settlement assets** — no universally accepted on-chain cash equivalent for DVP

### Regulatory Approaches by Jurisdiction

| Approach | Jurisdictions | Description |
|----------|-------------|-------------|
| Apply existing frameworks | U.S., UK, most EU | Existing securities laws apply; no new regime |
| New guidance/rules | Singapore, Hong Kong, Abu Dhabi | Specific DLT/token guidance layered on existing laws |
| Sandbox programs | Multiple IOSCO members | Time-limited experimental frameworks for tokenized products |
| Comprehensive token regime | EU (MiCA) | Harmonized regulation across all member states |

### IOSCO Recommendations for Tokenization

1. Reference IOSCO's DeFi Recommendations when identifying responsible persons throughout the tokenization value chain
2. Ensure regulatory requirements are properly imposed on identifiable entities
3. Apply existing investor protection frameworks to tokenized products
4. Address interoperability and settlement asset challenges before scaling
5. Maintain market integrity standards regardless of underlying technology

---

## 16. Howey Test Analysis & Best Practices for Token Offerings

*Source: Michael Mendelson, "From Initial Coin Offerings to Security Tokens: A U.S. Federal Securities Law Analysis," 22 Stan. Tech. L. Rev. 52 (2019)*

### The Four-Factor Howey Test Applied to Digital Tokens

| Factor | Test | Application to Tokens | Weight |
|--------|------|----------------------|--------|
| 1. Investment of money | Did purchaser invest money or value? | Crypto payments (BTC, ETH) = investment of money per *Uselton v. Comm. Lovelace* | Almost always met |
| 2. Common enterprise | Is there pooling of funds toward a shared venture? | Token sale proceeds pooled for network development | Almost always met |
| 3. Expectation of profits | Do purchasers reasonably expect financial returns? | If token marketed as investment or appreciating asset → met; if purely consumptive utility → possibly not | Critical factor |
| 4. Efforts of others | Are profits derived from managerial efforts of promoters? | If team controls development, marketing, and token value → met; if fully decentralized → possibly not | Critical factor |

### Rebuttable Presumption

Per Mendelson's analysis and former SEC Chairman Clayton's position, the rebuttable presumption is that **most token offerings involve the sale of securities**. A concerted effort factoring network design, business development strategy, and legal analysis is required to overcome this presumption.

### Key Case Law Applied to Tokens

| Case | Holding | Token Relevance |
|------|---------|----------------|
| *SEC v. Howey* (1946) | Established the four-factor investment contract test | Foundation for all token analysis |
| *SEC v. Edwards* (2004) | Profits include fixed returns, not just variable | Token staking rewards = profits |
| *SEC v. Glenn W. Turner* (1973) | "Efforts of others" = essential managerial efforts affecting success/failure | Team-led token projects meet this prong |
| DAO 21A Report (2017) | SEC applied Howey directly to tokens; voting rights don't negate securities status | Even governance tokens can be securities |
| *Munchee* (2017) | Utility tokens with investment marketing = securities | Marketing matters more than token label |

### SAFT Framework (Simple Agreement for Future Tokens)

Based on Y Combinator's SAFE, the SAFT sells the right to receive tokens upon network completion:

```
SAFT Flow:
  1. Startup sells SAFT under Reg D (accredited investors)
  2. SAFT is explicitly a security (investment contract)
  3. Network development occurs with raised capital
  4. Network launches; tokens delivered to SAFT holders
  5. If tokens are functional utility → may no longer be securities
  6. Company may also sell tokens via private sale or SEC-approved exchange

Key risk: SEC has not officially endorsed SAFT structure
```

### Best Practices for U.S. Companies Planning Token Offerings

| Practice | Requirement | Rationale |
|----------|------------|-----------|
| **White Paper** | Must resemble a PPM — pro forma financials, MD&A, risk factors, sufficient information for informed decision | Post-DAO, bare marketing leaflets are unacceptable |
| **Proof of Concept** | Executable code or prototype available for review (e.g., on GitHub) | Demonstrates viability; reduces fraud risk |
| **Cybersecurity** | Robust security for ICO platform, wallets, and custody; protect both company and investors | DAO hack ($50M+ stolen) drew SEC attention |
| **Terms & Conditions** | Must address token classification, transfer restrictions, risk disclosures, regulatory compliance | Pre-DAO boilerplate is insufficient; SAFT or traditional subscription agreement recommended |
| **Legal Counsel** | Engage securities counsel before offering; not optional | SEC enforcement Cyber Unit actively pursuing violations |
| **Exemption Selection** | Choose Reg A, Reg D, Reg CF, or Reg S based on investor base and capital needs | No exemption = unregistered securities offering violation |

### Token Classification Decision Tree (Mendelson Framework)

```
Is the token sold to raise money for a project?
  ├─ YES → Strong presumption: SECURITY
  │   ├─ Is there a functioning network at time of sale?
  │   │   ├─ NO → Almost certainly a security (pre-functional token)
  │   │   └─ YES → Analyze utility vs investment characteristics
  │   │       ├─ Marketed as investment? → SECURITY
  │   │       ├─ Tradeable on secondary markets? → Leans SECURITY
  │   │       ├─ Purely consumptive use? → May not be security
  │   │       └─ Value depends on team efforts? → SECURITY
  │   └─ Consider SAFT structure for pre-functional tokens
  └─ NO (e.g., mining reward, airdrop) → Analyze independently
      ├─ Mining/staking rewards → Generally NOT securities (2026 guidance)
      └─ Airdrop of non-security asset → NOT securities (2026 guidance)
```

---

## 17. Compliance Checklists

### Pre-Offering Checklist

- [ ] **Corporate**: Board resolution, Certificate of Designation, bylaws amendment
- [ ] **Securities counsel**: Engaged, opinion letter drafted
- [ ] **Exemption selected**: Reg D / Reg S / Reg A+ / Reg CF — requirements mapped
- [ ] **Transfer agent**: SEC §17A-registered agent engaged
- [ ] **Tripartite custody agreement**: Executed (issuer + TA + protocol)
- [ ] **CUSIP assigned**: Via transfer agent
- [ ] **PPM/Offering Circular**: Drafted with blockchain-specific disclosures
- [ ] **Subscription agreement**: Includes digital asset risk disclosures
- [ ] **Smart contract**: Developed, audited by reputable firm
- [ ] **42 Transfer Hooks**: Configured and tested for asset class
- [ ] **KYC/AML provider**: Engaged (Chainalysis, TRM, Jumio, etc.)
- [ ] **Wallet infrastructure**: Registered wallet system with OFAC screening
- [ ] **Trading venue**: ATS registration or CEDEX listing arranged
- [ ] **Stablecoin settlement**: USDC/PYUSD integration tested
- [ ] **Legal opinions**: Securities law, blockchain law, state law compliance

### Post-Launch Compliance Checklist

- [ ] **Form D filing**: Within 15 days of first sale (Reg D)
- [ ] **Blue sky filings**: State notice filings where securities are sold
- [ ] **Continuous AML monitoring**: On every transfer (hooks 17-20)
- [ ] **Sanctions screening**: Real-time OFAC/SDN checks (hooks 21-26)
- [ ] **Holding period enforcement**: Rule 144 lockups active (hooks 9-16)
- [ ] **Position limit monitoring**: 4.99% cap enforced (hooks 1-4)
- [ ] **Circuit breaker testing**: >10% / 5-min halt verified (hooks 5-8)
- [ ] **Quarterly reporting**: To SEC staff (if DTC participant)
- [ ] **Investor re-attestation**: 12-month KYC refresh cycle
- [ ] **NAV reappraisal**: Bi-annual (real estate only)
- [ ] **Audit**: Annual financial audit of issuer/SPV
- [ ] **Bad actor screening**: Ongoing (Reg D §506(d) disqualification)

### Regulatory Filing Calendar

| Filing | Deadline | Exemption |
|--------|----------|-----------|
| Form D | 15 days after first sale | Reg D |
| Form D Amendment | Annually | Reg D |
| Form 1-A (Offering Circular) | Before first sale | Reg A+ |
| Form 1-K (Annual Report) | 120 days after fiscal year end | Reg A+ Tier 2 |
| Form 1-SA (Semiannual Report) | Within 90 days | Reg A+ Tier 2 |
| Form C | Before offering opens | Reg CF |
| Form C-AR (Annual Report) | 120 days after fiscal year end | Reg CF |

---

## 18. Offering Design Workflow

When the user asks to design a tokenized securities offering, follow this decision tree:

```
START
  │
  ├─ What asset class?
  │   ├─ Equity → Playbook A
  │   ├─ Mineral/Hydrocarbon → Playbook B
  │   ├─ Real Estate → Playbook C
  │   ├─ Fund (Hedge/PE/VC/RE Fund) → Playbook D (§13)
  │   └─ Other (debt, structured product) → Adapt closest playbook
  │
  ├─ What investor base?
  │   ├─ U.S. accredited only → Reg D §506(c)
  │   ├─ U.S. accredited + sophisticated → Reg D §506(b)
  │   ├─ U.S. all investors (small raise) → Reg CF ($5M cap)
  │   ├─ U.S. all investors (large raise) → Reg A+ Tier 2 ($75M cap)
  │   ├─ Non-U.S. only → Reg S
  │   └─ Mixed U.S. + international → Reg D + Reg S parallel
  │
  ├─ Tokenization model?
  │   ├─ Issuer-sponsored (recommended) → Category 1
  │   │   ├─ DLT as official record → Model A
  │   │   └─ Off-chain authoritative → Model B (recommended)
  │   ├─ Third-party custodial → Category 2 (warn about general creditor risk)
  │   └─ Synthetic exposure → Category 3 (warn: security-based swap rules)
  │
  ├─ Blockchain selection?
  │   ├─ Solana (recommended for ST22 Transfer Hook ecosystem)
  │   ├─ Ethereum (ERC-3643 / T-REX for permissioned transfers)
  │   ├─ Avalanche (Subnets for institutional isolation)
  │   ├─ Polygon (lower cost, EVM compatibility)
  │   └─ Permissioned (Hyperledger Besu, R3 Corda — for institutional-only)
  │
  ├─ Transfer agent?
  │   ├─ Empire Stock Transfer (proven ST22 integration)
  │   ├─ Securitize (SEC-registered, own ATS)
  │   ├─ tZERO (SEC-registered, own ATS)
  │   └─ Other SEC §17A-registered agent
  │
  └─ Trading venue?
      ├─ CEDEX (for RWA Tokens ecosystem)
      ├─ tZERO ATS
      ├─ Securitize Markets (ATS)
      ├─ INX (registered ATS)
      └─ Custom ATS (requires Form ATS filing)
```

### Document Generation

When asked to generate offering documents, produce:

1. **Term Sheet** — 2-3 page summary of offering terms
2. **PPM Outline** — Private Placement Memorandum structure with required sections:
   - Cover page with legends
   - Summary of Terms
   - Risk Factors (traditional + blockchain-specific)
   - Description of the Business
   - Use of Proceeds
   - Description of Securities
   - Tokenization Mechanics
   - Transfer Restrictions
   - Plan of Distribution
   - Tax Considerations
   - Subscription Procedures
3. **Subscription Agreement** — with digital asset-specific representations
4. **Investor Questionnaire** — accreditation verification + blockchain wallet info
5. **Transfer Agent Agreement** — tripartite custody terms

**Always include blockchain-specific risk disclosures**:
- Smart contract vulnerability risk
- Blockchain network congestion/failure risk
- Private key loss = permanent loss of access
- Regulatory uncertainty risk
- Liquidity risk (secondary market not guaranteed)
- Technology obsolescence risk
- Fork risk (blockchain protocol changes)
- Oracle failure risk (real estate NAV)

---

## 19. Risk Disclosures & Disclaimers

### Required Disclaimers (Include in ALL Offering Materials)

```
THESE SECURITIES HAVE NOT BEEN REGISTERED UNDER THE SECURITIES ACT OF
1933, AS AMENDED, OR THE SECURITIES LAWS OF ANY STATE OR OTHER
JURISDICTION. THEY MAY NOT BE OFFERED, SOLD, OR TRANSFERRED EXCEPT IN
COMPLIANCE WITH THE REGISTRATION REQUIREMENTS OF SAID ACT AND LAWS OR
AN EXEMPTION THEREFROM.

THE SECURITIES DESCRIBED HEREIN ARE SPECULATIVE AND INVOLVE A HIGH
DEGREE OF RISK. INVESTORS MUST BE ABLE TO AFFORD THE LOSS OF THEIR
ENTIRE INVESTMENT.

NO REGULATORY AUTHORITY HAS APPROVED OR DISAPPROVED OF THESE
SECURITIES OR PASSED UPON THE ADEQUACY OF THIS OFFERING. ANY
REPRESENTATION TO THE CONTRARY IS A CRIMINAL OFFENSE.
```

### Blockchain-Specific Risk Categories

| Risk Category | Description |
|--------------|-------------|
| Smart Contract | Code vulnerabilities may result in loss of tokens |
| Network | Blockchain congestion, forks, or failure may impair transfers |
| Key Management | Loss of private keys results in permanent, irrecoverable loss |
| Regulatory | Laws governing digital assets are evolving and may change |
| Liquidity | Secondary market trading is not guaranteed |
| Technology | Underlying blockchain technology may become obsolete |
| Oracle | Price feeds and NAV data may be delayed or inaccurate |
| Custody | Transfer agent failure or insolvency risk |
| Sanctions | Wallet may be frozen if flagged by compliance screening |

---

## 20. Reference Links

### Primary SEC Sources
- [DTC No-Action Letter (Dec 11, 2025)](https://www.sec.gov/files/tm/no-action/dtc-nal-121125.pdf)
- [OTCM Protocol Written Input (Jan 30, 2026)](https://www.sec.gov/files/ctf-written-input-otcm-protocol-013026.pdf)
- [OTCM Protocol Updated Submission (Apr 2, 2026)](https://www.sec.gov/files/ctf-written-input-goovy-company-inc-dba-otcm-protocol-040226.pdf)
- [SEC Crypto Task Force Written Input Portal](https://www.sec.gov/featured-topics/crypto-task-force/crypto-task-force-written-input)
- [Commissioner Peirce Statement on DTC NAL](https://www.sec.gov/newsroom/speeches-statements/peirce-121125-tokenization-trending-statement-division-trading-markets-no-action-letter-related-dtcs-development)
- [Chairman Atkins — Token Taxonomy Speech](https://www.sec.gov/newsroom/speeches-statements/atkins-remarks-regulation-crypto-assets-031726)

### Law Firm Analysis
- [Morgan Lewis — DTC Regulatory Pathway](https://www.morganlewis.com/pubs/2026/01/new-sec-guidance-provides-regulatory-pathway-for-dtc-securities-tokenization-services)
- [Sidley Austin — DTC Relief Analysis](https://www.sidley.com/en/insights/newsupdates/2025/12/the-depository-trust-company-gets-sec-ok-to-tokenize-securities-and-skip-key-regulations)
- [Katten — SEC Guidance on Tokenized Securities](https://katten.com/sec-issues-guidance-on-tokenized-securities)
- [Lathrop GPM — What Tokenization Doesn't Change](https://www.lathropgpm.com/insights/what-tokenization-doesnt-change-the-sec-reaffirms-the-securities-law-framework/)
- [Carlton Fields — DTC NAL Analysis](https://www.carltonfields.com/insights/publications/2025/sec-staff-no-action-letter-to-dtc-for-tokenization-services)
- [Cadwalader — DTC Tokenization Pilot](https://www.cadwalader.com/fin-news/index.php?eid=1003&nid=142)

### Industry Platforms
- [RWA Tokens Corp (OTCM Protocol)](https://rwatokens.net/)
- [CEDEX Trading Venue](https://cedex.market)
- [Empire Stock Transfer](https://www.empirestock.com)
- [Securitize](https://securitize.io)
- [tZERO](https://www.tzero.com)

### Industry Policy & Academic
- [Robinhood Tokenization Memo (Jan 2025)](https://cdn.robinhood.com/assets/robinhood/legal/tokenization_memo.pdf)
- [IOSCO Final Report on Tokenisation (Nov 2025)](https://www.iosco.org/library/pubdocs/pdf/IOSCOPD809.pdf)
- [Mendelson — From ICOs to Security Tokens, 22 Stan. Tech. L. Rev. 52 (2019)](https://law.stanford.edu/wp-content/uploads/2019/01/Mendelson_20180129.pdf)
- [EU MiCA Regulation (2023/1114)](https://eur-lex.europa.eu/eli/reg/2023/1114/oj)

### Fund Tokenization
- [Dilendorf — Tokenized Fund Formation](https://dilendorf.com/blockchain-crypto/tokenized-funds.html)
- [Dilendorf — STO Launch Process](https://dilendorf.com/blockchain-crypto/sto-launch.html)
- [Dilendorf — Real Estate Fund (Tokenized vs Traditional)](https://dilendorf.com/resources/launching-a-real-estate-fund-tokenized-or-traditional.html)
- [Dilendorf — Reg A+ Tokenized Offerings](https://dilendorf.com/blockchain-crypto/regulation-a-tokenized-offerings.html)
- [Dilendorf — Reg CF Tokenized Offerings](https://dilendorf.com/blockchain-crypto/regulation-cf-security-token-sto.html)
- [Dilendorf — Fund Tokenization PDF](https://dilendorf.com/wp-content/uploads/2022/10/Fund-Tokenization.pdf)

### Compliance Tools
- [Chainalysis KYT](https://www.chainalysis.com/kyt/)
- [TRM Labs](https://www.trmlabs.com)
- [Jumio (KYC)](https://www.jumio.com)
- [VerifyInvestor.com (Accreditation)](https://www.verifyinvestor.com)

---

## Usage Notes

This skill is for **designing and structuring** compliant tokenized securities offerings. It is NOT:
- Legal advice (always engage securities counsel)
- A substitute for SEC registration or qualification
- Investment advice
- A guarantee of regulatory approval

**Always recommend the user engage**:
1. Securities counsel (for offering structure and documentation)
2. SEC §17A-registered transfer agent (for custody and record-keeping)
3. Smart contract auditor (for token security)
4. Compliance provider (for KYC/AML/sanctions screening)

When generating code for token contracts, transfer hooks, or compliance systems, always note that the code requires professional audit before deployment with real securities.
