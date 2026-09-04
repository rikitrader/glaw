# Venezuela Dollarization and Monetary Reform

## Preliminary Reading Report — UNVERIFIED / NON-DECISION-GRADE

**Prepared for research review**  
**Status:** Preliminary, incomplete, and not suitable for policy execution  
**Purpose:** Provide a readable analytical draft while the 80-case primary-evidence universe and current Venezuela data are still being ingested.

## Important limitation

This report is not the final HAEIS report. It does not claim that Venezuela currently has enough dollars, reserves, banking liquidity, fiscal capacity, or legal readiness for official dollarization. Current BCV, SUDEBAN, fiscal, reserve, oil, debt, FX, wage, pension, and household observations remain incomplete or disputed.

The report therefore separates:

- **VERIFIED LEGAL FACT:** read from a local judgment, award, or official record.
- **UNVERIFIED ECONOMIC CLAIM:** requires current data or an additional primary source.
- **MODELED SCENARIO:** an analytical assumption, not an observed fact.
- **UNAVAILABLE:** no defensible source-bound observation currently ingested.

## Executive summary

Official dollarization would not be a banknote exchange alone. It would simultaneously change Venezuela’s monetary system, central-bank role, commercial-bank liquidity, government financing, sovereign debt service, payment infrastructure, contract denomination, wage payments, pensions, and external adjustment mechanism.

The potential benefit is straightforward: replacing or legally subordinating the bolívar could reduce the government’s ability to finance deficits through domestic money creation and could improve the credibility of the unit of account. The potential cost is equally important: a dollarized system would have less domestic emergency liquidity and would depend more directly on fiscal discipline, bank capitalization, external dollar inflows, and the ability to restructure obligations.

The central question is not whether dollars circulate in Venezuela. The relevant question is whether the country could support a legally dollarized banking and fiscal system through adverse conditions: deposit withdrawals, oil-price declines, capital flight, sanctions-related payment restrictions, debt service, and weak domestic credit creation.

**Preliminary assessment:** dollarization should be treated as a conditional regime-conversion hypothesis. The available evidence in this draft is insufficient to determine whether it is financially feasible today.

## 1. What dollarization could mean

### Informal dollarization

U.S. dollars may be used for pricing, savings, remittances, or private transactions while the bolívar remains legal tender. This does not establish that the banking system is fully dollar-funded.

### Partial or dual-currency regime

The bolívar and dollar coexist legally. This can preserve some domestic flexibility, but it can also create conversion disputes, exchange-rate segmentation, and balance-sheet mismatches.

### Currency board

A domestic currency remains in circulation but is subject to a fixed parity and reserve rules. The design must specify eligible reserves, monetary liabilities, convertibility, fiscal financing restrictions, and emergency liquidity arrangements.

### Full official dollarization

The dollar becomes the legal monetary anchor and the bolívar ceases to be the principal monetary-policy instrument. This removes domestic currency issuance but does not automatically solve fiscal deficits, bank insolvency, external arrears, or low productivity.

## 2. Evidence currently available

### CITGO, PDVH, PDVSA, and creditor enforcement

The verified appellate record describes the corporate chain from PDVSA through PDV Holding, Inc. (PDVH), CITGO Holding, Inc., and CITGO Petroleum Corporation. The Crystallex litigation concerned attachment and execution against PDVH shares in an effort to satisfy a judgment against Venezuela. The record also discusses a 50.1% security interest in PDVH shares used as collateral for PDVSA debt.

These are important sovereign-balance-sheet and asset-encumbrance facts. They do not, by themselves, establish current CITGO value, current PDVSA debt, current lien priority, or available reserves.

Sources: [Crystallex appellate opinion](https://www.courtlistener.com/opinion/4643670/crystallex-intl-corp-v-bolivarian-republic-de-venezuela-in-re-de/), [OI European Group appellate opinion](https://www.courtlistener.com/opinion/9412117/oi-european-group-bv-v-bolivarian-republic-of-venezuela/).

### Verified commercial-arbitration record

The locally ingested ConocoPhillips/Phillips Petroleum final award concerns Petrozuata and Hamaca project agreements and PDVSA guarantees. The award states a USD 66,876,773.81 payment obligation to one claimant, rejects a separate USD 102,910,000 claim, and fixes arbitration costs at USD 820,000. These amounts are case-specific legal obligations and must not be added to separate ICSID awards or later enforcement records.

Source artifact: `data/derived/venezuela-batch1-case-evidence.json`.

### International investment-dispute context

UNCTAD’s Venezuela case records identify investor claims, sectors, claimed amounts, awarded amounts, breaches alleged/found, and follow-on proceedings. For example, the UNCTAD record for Crystallex identifies a USD 3.160 billion claimed amount and a USD 1.202 billion awarded amount, while the Gold Reserve record identifies a USD 1.735 billion claim and a USD 713 million award. These figures require reconciliation with the actual awards, interest, enforcement, settlements, and payment records before they can enter a sovereign-debt model.

Sources: [UNCTAD Crystallex record](https://investmentpolicy.unctad.org/investment-dispute-settlement/cases/403/crystallex-v-venezuela), [UNCTAD Gold Reserve record](https://investmentpolicy.unctad.org/investment-dispute-settlement/cases/333/gold-reserve-v-venezuela).

## 3. Balance-sheet questions that must be answered

The following variables are currently **UNAVAILABLE or insufficiently reconciled** for a decision-grade conclusion:

- BCV monetary base, M1, M2, currency in circulation, and reserves.
- Gross, liquid, encumbered, and unencumbered international reserves.
- VES and foreign-currency bank deposits.
- Bank loans, capital, NPLs, liquidity, government exposure, and FX mismatch.
- Republic and PDVSA debt by instrument, creditor, maturity, arrears, and currency.
- CITGO/PDVH debt, liens, cash, dividends, restricted cash, and valuation.
- Fiscal revenue, expenditure, primary balance, overall balance, and monetary financing.
- Oil production, realized prices, net government FX, operating costs, partner payments, and debt service.
- Remittances, capital flight, FDI, imports, and external financing.

Without these observations, a dollar-conversion requirement cannot be responsibly calculated.

## 4. Dollarization funding models

The correct calculation depends on what is being converted:

```text
Physical-currency requirement = VES currency in circulation / conversion rate

Monetary-base requirement = VES monetary base / conversion rate

M1 requirement = VES M1 / conversion rate

M2 requirement = VES M2 / conversion rate
```

These are not interchangeable. Replacing physical currency is a narrower operation than converting transactional deposits, and converting M2 is not equivalent to supplying physical dollars for every deposit.

The final model must also add separate amounts for bank recapitalization, deposit insurance, emergency liquidity, government operating cash, payment-system conversion, and debt restructuring.

## 5. Banking risk

The main preliminary banking risk is not simply “lack of dollars.” It is a mismatch between:

- dollar liabilities and dollar assets;
- short-term withdrawals and liquid assets;
- converted loan values and converted deposits;
- bank capital and post-conversion losses;
- private credit demand and available external liquidity.

A dollarized banking system may still create bank deposits and credit, but it cannot rely on unlimited domestic currency creation by the central bank. Emergency liquidity would therefore need to come from fiscal reserves, external credit lines, a funded stability facility, private interbank markets, or other legally enforceable mechanisms.

## 6. Fiscal risk

Dollarization would not remove the fiscal deficit. It would change how the deficit can be financed. The government would have less access to domestic monetary financing and would need a credible combination of taxation, spending control, debt restructuring, oil revenue, external financing, or asset monetization.

The fiscal model must separately measure:

```text
Revenue - expenditure = fiscal balance

Revenue - non-interest expenditure = primary balance

Interest expenditure / government revenue = interest burden
```

Pensions, wages, subsidies, health, education, security, and SOE obligations must be modeled in dollars under multiple coverage assumptions. No current dollar wage or pension conclusion is issued in this preliminary report.

## 7. Oil and external liquidity

Oil may generate dollars, but gross exports are not the same as dollars available to the government or banking system. The usable flow must subtract operating costs, imports, partner shares, royalties, taxes, debt service, blocked funds, and other obligations.

```text
Usable sovereign oil FX = gross oil revenue
                         - operating costs
                         - imports
                         - partner payments
                         - debt service
                         - other committed outflows
```

Under dollarization, external deficits can tighten domestic liquidity more directly because the government cannot restore liquidity by issuing a freely depreciating domestic currency.

## 8. Competing regime scenarios

The final analysis must compare at least:

1. Current monetary arrangement.
2. Immediate full dollarization.
3. Gradual dollarization.
4. Currency board.
5. Dual-currency regime.
6. Managed float.
7. Inflation-targeting bolívar.
8. Currency basket or other hard-peg design.

Each scenario requires the same stress tests:

- 5%, 10%, 20%, 30%, 40%, and 50% deposit withdrawal.
- 20%, 40%, and 60% oil-revenue shock.
- Capital flight and sanctions-related payment restrictions.
- Debt restructuring and external financing loss.
- Credit contraction of 10%, 20%, 30%, 40%, and 50%.

## 9. Preliminary conclusion

This preliminary report supports only the following limited conclusion:

**Official dollarization is a complex sovereign, banking, fiscal, legal, and external-sector restructuring. The evidence currently ingested is sufficient to establish the existence of major legal claims, PDVSA/CITGO asset-enforcement exposure, and historical arbitration obligations. It is not sufficient to determine whether Venezuela currently possesses the liquid dollar reserves, bank capital, fiscal capacity, external income, and institutional readiness required for safe official dollarization.**

## 10. What would change this report

The report can move from preliminary to decision-grade only after:

- the complete 80-case primary-evidence audit;
- verified current BCV and SUDEBAN data;
- audited reserve composition;
- bank asset-quality and capital review;
- fiscal and PDVSA debt reconciliation;
- CITGO/PDVH financial and lien documentation;
- oil net-FX-flow reconstruction;
- legal conversion and contract framework;
- full red-team, blue-team, second-red-team, math, data, and citation audits.

**Current decision status: DATA INSUFFICIENT — NO POLICY RECOMMENDATION.**
