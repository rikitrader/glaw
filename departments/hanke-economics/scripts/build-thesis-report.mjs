import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const read = (p) => fs.readFileSync(path.join(root, p), 'utf8');
const books = JSON.parse(read('books/hanke/index.json')).books;
const flows = JSON.parse(read('books/hanke/monetary-flow-papers.json')).papers;
const courtFacts = JSON.parse(read('data/derived/court-record-balance-sheet-facts.json'));
const citgo = JSON.parse(read('data/derived/citgo-master-evidence.json'));
const variables = JSON.parse(read('datasets/venezuela-variable-inventory.json'));
const finalReport = read('reports/venezuela-final-indexed-report.md');

const line = (s = '') => s + '\n';
let out = '';
const add = (s = '') => { out += line(s); };
const page = () => { add(''); add('[[PAGEBREAK]]'); add(''); };

add('# Venezuela Dollarization: Monetary Architecture, Banking Liquidity, Fiscal Sustainability, External Financing, Legal Risk, and Institutional Readiness');
add('## A thesis-grade HAEIS research report');
add('**Edition:** Expanded preliminary research thesis — source-bound and non-decision-grade');
add('**Date:** 25 August 2026');
add('**Prepared by:** Hanke Applied Economics Intelligence System (HAEIS)');
add('**Status:** UNVERIFIED / NON-DECISION-GRADE');
add('');
add('> This document is a research and review edition, not a final policy recommendation. It preserves unresolved data, disputed records, restricted documents, and blocked analytical gates. No current Venezuela statistic is invented, silently imputed, or promoted from metadata to fact.');
page();

add('# Abstract');
add('This thesis examines whether official dollarization could improve Venezuela’s monetary stability and economic welfare, and under what conditions it could instead produce a banking liquidity crisis, credit contraction, recession, fiscal crisis, or balance-of-payments shock. The central argument is that dollarization must be analyzed as a simultaneous restructuring of the monetary system, the central bank, the commercial banking system, the sovereign balance sheet, the debt structure, the payment system, the external account, and the economic contract between the state, banks, businesses, and citizens.');
add('The report applies the Hanke Applied Economics Intelligence System (HAEIS), which distinguishes direct publication evidence, framework-based interpretation, system inference, calculation, historical evidence, external views, red-team challenges, blue-team responses, and unresolved propositions. It separates informal dollar use from partial dollarization, currency-board arrangements, official dollarization, synthetic dollar balances, stablecoin layers, and currency competition. It also distinguishes the physical-currency requirement from the monetary-base, M1, M2, and full-banking-system conversion requirements.');
add('The present edition does not issue a go/no-go decision. The evidence audit identifies material gaps in current BCV monetary aggregates, SUDEBAN banking data, liquid reserves, fiscal financing, net oil foreign-exchange inflows, current Republic and PDVSA obligations, remittances, external financing, and USD circulation. Historical and institutional evidence is therefore used for mechanism analysis and design constraints, not as a substitute for current observations.');
add('The principal research finding is conditional: dollarization could improve monetary credibility only if the conversion is supported by verified monetary statistics, solvent and liquid banks, a funded emergency-liquidity architecture, fiscal adjustment, a credible debt path, sufficient usable foreign exchange, operational payment-system readiness, and enforceable legal conversion rules. If those conditions are absent, the same reform could suppress monetary inflation while intensifying liquidity scarcity, credit compression, fiscal stress, and social dislocation.');
add('**Keywords:** Venezuela; dollarization; currency boards; monetary credibility; bank liquidity; lender of last resort; fiscal dominance; PDVSA; sovereign debt; balance of payments; Hanke; Golden Growth Rate; Credit Counterparts.');
page();

add('# Research Integrity Statement');
add('This report is deliberately conservative. A source is not treated as evidence merely because it appears in a search result, source registry, case title, book catalogue, news story, or dataset description. A material number requires a source, date, unit, series or table identifier, publication or release date where available, retrieval timestamp, transformation history, confidence status, and a reproducible locator. Court judgments and arbitration records are evidence of what a tribunal or court recorded; they are not automatically current sovereign-debt balances, current reserves, or current PDVSA liabilities.');
add('The document uses the following observation statuses: `VERIFIED`, `PROVISIONAL`, `ESTIMATED`, `MODELED`, `IMPUTED`, `DISPUTED`, `STALE`, and `UNAVAILABLE`. The current report contains no unlabelled imputation. Where evidence conflicts, the disagreement remains visible rather than being averaged away.');
add('The report may be read before the evidence universe is complete, but it must not be cited as a decision-grade estimate of the current cost or feasibility of Venezuelan dollarization.');
page();

add('# Table of Contents');
for (const item of [
  '1. Introduction and Research Question', '2. Literature Review and Hanke Framework', '3. Research Design and Evidence Architecture',
  '4. Venezuela: Structural and Historical Context', '5. Monetary Regimes and Dollarization Models', '6. Balance-Sheet and Funding Requirements',
  '7. Banking System, Credit, and Lender of Last Resort', '8. Fiscal, Oil, External, and Debt Constraints', '9. Households, Labor, and Distribution',
  '10. International Comparative Episodes', '11. Legal and Institutional Architecture', '12. Quantitative, Scenario, and Stress-Test Framework',
  '13. Economic Postures and Adversarial Review', '14. Findings, Conditions, and Decision Framework', '15. Limitations and Research Agenda',
  'References', 'Appendix A. Source and Evidence Register', 'Appendix B. Venezuela Legal and Claims Index',
  'Appendix C. Critical Variable Inventory', 'Appendix D. Formula and Indicator Register', 'Appendix E. Machine-Validated Report Index'
]) add(`- ${item}`);
page();

add('# 1. Introduction and Research Question');
add('## 1.1 Problem statement');
add('Venezuela’s monetary question cannot be reduced to whether the dollar is more credible than the bolívar. The policy choice changes the instruments available to the state, the liquidity regime of banks, the currency denomination of contracts, the distribution of adjustment costs, and the way external shocks pass through the economy. A technically feasible currency conversion can still be financially infeasible, legally incomplete, politically unstable, or socially damaging.');
add('The research question is therefore: under what monetary, fiscal, banking, reserve, external-sector, legal, institutional, political, and social conditions would official dollarization improve welfare, and under what conditions would it create a banking crisis, credit contraction, recession, fiscal crisis, or balance-of-payments shock?');
add('## 1.2 Research objectives');
for (const x of ['reconstruct the relevant Hanke and Hanke/Greenwood frameworks without impersonating Hanke;', 'separate observed facts from estimates, models, historical analogies, and unresolved claims;', 'model physical-currency, monetary-base, M1, M2, gradual, parallel, and currency-board conversion requirements separately;', 'evaluate bank liquidity, credit creation, fiscal financing, oil-linked external liquidity, sovereign and PDVSA debt, and legal implementation;', 'compare immediate dollarization with currency-board, dual-currency, managed-float, hard-peg, currency-basket, and non-dollarization reforms;', 'subject every major proposition to independent economic postures and repeated red-team review;']) add(`- ${x}`);
add('## 1.3 Contribution');
add('The contribution is institutional rather than rhetorical. HAEIS joins source provenance, economic accounting, reproducible formulas, legal-record evidence, historical comparison, scenario analysis, and adversarial review in one auditable workflow. The system is designed to reach three possible outcomes: supported, supported with conditions, or not supported in this case. It is not programmed to prove dollarization, Hanke, or the status quo correct.');
page();

add('# 2. Literature Review and Hanke Framework');
add('## 2.1 Scope of the Hanke corpus');
add('The corpus separates metadata from verified text. Commercial book metadata can establish that a title exists and identify its analytical role, but it cannot authorize a quotation, page reference, or precise attribution without the underlying text. Publicly accessible books and papers are retained with access scope, local hash, source URL, and verification status.');
add('## 2.2 Major books and analytical roles');
add('| Work | Analytical role | Evidence status |');
add('|---|---|---|');
for (const b of books) add(`| ${b.title} (${b.year}) | ${(b.analytical_role || []).join('; ')} | ${b.source_status || b.full_text_status} |`);
add('The corpus includes recent books on bank money, monetary architecture, capital theory, and public-debt sustainability, as well as the currency-board, Spanish-language currency-board, Russian transition, Cuba, and Jamaica materials. The report uses these works as a structured research map. It does not convert unacquired commercial books into direct evidence.');
add('## 2.3 Currency-board and hard-money propositions');
add('The Hanke-oriented framework emphasizes monetary credibility, convertibility, reserve backing, hard budget constraints, and the reduction of discretionary monetary financing. These propositions are analytically relevant to Venezuela because the central policy problem includes currency substitution, inflation expectations, fiscal dominance, and the credibility of the monetary authority. They do not by themselves establish that any particular conversion rate, reserve stock, banking structure, or fiscal path is feasible.');
add('## 2.4 Hanke/Greenwood monetary-flow framework');
add('The Hanke/Greenwood Golden Growth Rate and Credit Counterparts papers are treated as the basis for a monetary-flow agent. The indexed corpus contains SAE 232 for the United States, SAE 233 for the United Kingdom, and SAE 234 for the Eurozone. Their use in Venezuela is a framework transfer and must be labeled `HANKE-FRAMEWORK` or `SYSTEM-INFERENCE` unless a Venezuela-specific verified application supports the proposition.');
for (const p of flows) add(`- **${p.paper_id} — ${p.title}** (${p.authors.join(', ')}; ${p.source_locator}; status: ${p.full_text_status}).`);
add('## 2.5 Competing literature');
add('The report places the Hanke framework beside monetarist, Keynesian, New Keynesian, Austrian, supply-side, IMF-style stabilization, central-banker, banking-risk, sovereign-debt, development-economics, and political-economy perspectives. The purpose is not to produce a synthetic consensus that erases disagreement. It is to identify the assumptions that drive different conclusions and specify what evidence would falsify each position.');
page();

add('# 3. Research Design and Evidence Architecture');
add('## 3.1 Evidence hierarchy');
add('Evidence is ranked from original data and primary publications, through official institutions, peer-reviewed research, high-quality research institutions, reputable journalism, secondary commentary, and unverified sources. Discovery is not verification. A Google-dork result is an acquisition lead; it is not a fact.');
add('## 3.2 Observation contract');
add('| Required field | Purpose |');
add('|---|---|');
add('| Variable, value, unit | Prevents unlabelled numeric claims |');
add('| Observation, publication, retrieval dates | Preserves timing and vintage |');
add('| Source URL, source ID, series/table ID | Reproducibility |');
add('| Frequency and methodology | Comparability |');
add('| Transformation and confidence | Prevents silent conversion |');
add('| Verification and revision status | Keeps uncertainty visible |');
add('## 3.3 Legal-record method');
add('Court and arbitration records are read as records, not merely indexed as metadata. The evidence extraction schema captures claimants, respondents, tribunal, procedural posture, claims, counterclaims, awards or judgments, interest, enforcement, memoranda, exhibits, page or paragraph locators, local artifact hash, and overlap status. Amounts are separated into claimed amount, awarded amount, judgment amount, bond principal, payment amount, escrow amount, and enforcement exposure. These categories must not be summed without a defined accounting basis.');
add('## 3.4 Redenomination and currency normalization');
add('Historical Venezuelan monetary values cannot be compared directly across bolívar, bolívar fuerte, bolívar soberano, and bolívar digital denominations. The canonical transformation system retains the original denomination, current-equivalent denomination, USD equivalent where defensible, and real-price equivalent where appropriate.');
add('## 3.5 Reproducibility');
add('Raw documents are immutable. Transformations occur in code. Derived datasets preserve source IDs and status labels. Tests check units, duplicates, dates, redenomination errors, magnitude errors, conflicting sources, and stale observations. The report’s current production gate remains blocked where critical current data are absent or unresolved.');
page();

add('# 4. Venezuela: Structural and Historical Context');
add('## 4.1 Scope of the baseline');
add('A thesis-quality baseline must cover nominal and real GDP, GDP per capita, oil and non-oil activity, public and private sectors, productivity, capital stock, infrastructure, labor-market structure, informality, migration, and household purchasing power. The current HAEIS intake provides bounded historical context from verified World Bank and IMF artifacts, but not a complete current institutional baseline.');
add('## 4.2 Historical contraction and monetary breakdown');
add('The narrative must distinguish oil-sector disruption, nationalization and investment effects, exchange controls, fiscal financing, supply destruction, sanctions, COVID-era disruption, and later stabilization. A single-cause explanation is not accepted. The final data chapter should present a 1998–2026 real-GDP index and annotate regime changes only after the underlying series and vintage are verified.');
add('## 4.3 De facto dollar use');
add('Private use of USD prices, cash, deposits, or contracts is not equivalent to official dollarization. De facto dollarization can coexist with a domestic monetary base, domestic bank-credit creation, local tax obligations, and a central bank that retains formal powers. The distinction is central to estimating actual USD circulation and the effects of an official conversion.');
page();

add('# 5. Monetary Regimes and Dollarization Models');
add('## 5.1 Definitions');
add('| Regime | Core feature | Main constraint |');
add('|---|---|---|');
add('| Informal dollarization | Private USD use; local currency remains legal tender | Fragmented monetary and payment system |');
add('| Partial dollarization | USD and bolívar coexist legally | Conversion and settlement complexity |');
add('| Currency board | Fixed parity with defined reserve and legal rules | Reserve and fiscal discipline |');
add('| Official dollarization | USD becomes the monetary unit and legal tender | Loss of domestic monetary issuance |');
add('| Synthetic dollarization | USD-denominated digital balances without equivalent cash | Settlement and backing risk |');
add('| Stablecoin layer | Tokenized dollar claims | Regulatory, reserve, and run risk |');
add('## 5.2 Six mandatory conversion models');
for (const x of ['Model A — physical currency replacement;', 'Model B — monetary-base conversion;', 'Model C — full banking-system conversion;', 'Model D — gradual dollarization;', 'Model E — parallel currency regime;', 'Model F — currency-board transition;']) add(`- ${x}`);
add('The models cannot be collapsed into a single “dollar requirement.” M2 is a stock of deposits and other monetary liabilities, not a quantity of physical notes that must be purchased one-for-one. The banking model requires a separate treatment of deposits, reserves, loans, foreign assets, and emergency liquidity.');
add('## 5.3 Conversion-rate alternatives');
add('Candidate rates must be modeled through monetary-base, M1, M2, purchasing-power-parity, real-effective-exchange-rate, market-FX, parallel-market, external-balance, reserve-backed, and fiscal-consistency approaches. The output should be a low/base/high range with distributional and banking effects, not a falsely precise point estimate.');
page();

add('# 6. Balance-Sheet and Funding Requirements');
add('## 6.1 Accounting identities');
add('The basic physical-currency requirement is `USD required = VES currency in circulation / conversion rate`. The monetary-base requirement is `VES monetary base / conversion rate`. For M1, `M1 = currency + demand deposits`. For M2, `M2 = M1 + savings + time deposits`. These identities do not determine whether the conversion is financially feasible; they define the objects that must be measured.');
add('## 6.2 Funding package');
add('A complete transition-financing package includes physical cash, bank reserves, a liquidity stabilization fund, deposit insurance, bank recapitalization, a government operating buffer, payment-system conversion, and contingency financing. The funding gap is `dollarization requirement − available liquid reserves`, but the requirement must be defined before the gap is calculated.');
add('## 6.3 Reserves');
add('Gross international reserves, liquid foreign exchange, gold, SDRs, foreign securities, deposits abroad, pledged assets, sanctions constraints, and litigation exposure must be separated. Gold can be valuable without being immediately deployable as settlement liquidity. Reserve coverage is therefore calculated against the relevant dollarization object and not against an undifferentiated reserve headline.');
add('## 6.4 Current finding');
add('The current evidence bundle does not support a decision-grade value for BCV monetary base, M1, M2, liquid reserves, or USD circulation. The correct status is `UNAVAILABLE`, not a fabricated funding estimate.');
page();

add('# 7. Banking System, Credit, and Lender of Last Resort');
add('## 7.1 Banking balance sheet');
add('The aggregate and bank-level models separate loans, securities, reserves, FX assets, deposits, wholesale funding, central-bank funding, other liabilities, and equity. Where bank-level evidence is unavailable, the report remains at system level and does not accuse a specific bank of insolvency.');
add('## 7.2 Conversion risk');
add('Dollarization can convert liabilities and assets at different effective rates, creating a conversion gap. A bank can be solvent under one conversion and undercapitalized under another. Liquidity and solvency are not synonyms. A bank can hold positive capital but still fail a deposit run if liquid assets are insufficient.');
add('## 7.3 Credit contraction');
add('The causal chain tested is: deposits → bank liquidity → loanable funds → credit → investment → employment → GDP. Stress cases include no contraction, 10%, 20%, 30%, 40%, and 50% reductions in credit. These are modeled scenarios, not forecasts.');
add('## 7.4 Lender of last resort');
add('A dollarized system cannot rely on unlimited domestic base-money creation. Alternatives include a fiscal liquidity fund, multilateral facilities, foreign credit lines, private interbank liquidity, deposit insurance, reserve requirements, and oil-linked stabilization mechanisms. Each alternative has funding, collateral, governance, and political constraints.');
add('## 7.5 Bank-run stress grid');
add('| Withdrawal | Required analysis |');
add('|---:|---|');
for (const x of [5,10,15,20,25,30,40,50]) add(`| ${x}% | Liquid assets exhausted; emergency liquidity; credit contraction; GDP sensitivity |`);
page();

add('# 8. Fiscal, Oil, External, and Debt Constraints');
add('## 8.1 Fiscal dominance');
add('Dollarization removes or sharply limits domestic monetary financing. It does not remove the fiscal deficit. Revenue, spending, primary balance, interest burden, arrears, contingent liabilities, and debt rollover must be modeled in a common unit and time period.');
add('## 8.2 Seigniorage');
add('The report estimates historical monetary-creation revenue only where the monetary base and price-level inputs are verified. Foregone seigniorage under dollarization must be replaced by taxes, spending restraint, external financing, asset sales, or higher growth.');
add('## 8.3 Oil and usable sovereign FX');
add('Gross oil revenue is not equal to government FX. The net-flow model subtracts lifting costs, transport, discounts, joint-venture shares, royalties, taxes, domestic consumption, debt payments, and operating obligations. Oil price and production grids are stress inputs, not predictions.');
add('## 8.4 Debt and PDVSA');
add('Court and arbitration records can establish awards, judgments, defaults, security interests, payment events, and enforcement exposure. They do not by themselves establish the current consolidated debt stock. Debt analysis therefore keeps Republic debt, PDVSA debt, bilateral obligations, arbitration awards, commercial claims, arrears, and enforcement claims in separate ledgers.');
add('## 8.5 Balance of payments');
add('Under a dollarized regime, external deficits can tighten domestic liquidity directly. The dollar-flow waterfall tracks oil exports, non-oil exports, remittances, FDI, tourism, borrowing, imports, debt service, profit repatriation, capital flight, travel, and services.');
page();

add('# 9. Households, Labor, and Distribution');
add('Dollarization redistributes wealth through the conversion rate, contract rules, wage formation, debt conversion, deposit conversion, and access to bank liquidity. Potential beneficiaries include existing USD earners, exporters, savers, and importers. Potentially exposed groups include bolívar-income households, public employees, pensioners, debtors, SMEs dependent on domestic credit, and people outside the formal banking system.');
add('Pension scenarios use monthly benefits of $30, $50, $70, $100, $150, and $200, but the fiscal cost cannot be calculated without a verified beneficiary count and budget coverage. Public-wage scenarios must separate teachers, health workers, police, military, civil servants, and SOE employees where reliable payroll data exist.');
add('Distributional analysis must be stratified by income decile, USD exposure, remittance receipt, formal or informal employment, region, and bank access. A nominal conversion that stabilizes prices can still reduce real activity if credit and public wages adjust abruptly.');
page();

add('# 10. International Comparative Episodes');
add('## 10.1 Comparative method');
add('Comparisons are used to test mechanisms, not to claim that Venezuela will repeat another country. Each case must record pre-reform inflation, monetary regime, banking conditions, reserves, fiscal balance, debt, external accounts, legal structure, transition sequence, and five- and ten-year outcomes. Before-and-after comparisons do not establish causality by themselves.');
add('| Case | Main analytical use | Caution |');
add('|---|---|---|');
for (const [a,b,c] of [
  ['Ecuador','Banking crisis followed by official dollarization','Different size, institutions, and external financing'],
  ['Panama','Dollarized banking and payment architecture','Long institutional history; not a direct transition analogue'],
  ['El Salvador','Dollarization, remittances, and fiscal constraints','Remittance and institutional differences'],
  ['Zimbabwe','Currency collapse and multicurrency stabilization','Extreme supply and political conditions'],
  ['Argentina 1989–90','Hyperinflation and currency credibility','Convertibility was not full dollarization'],
  ['Argentina 2001–02','Debt, banking freeze, and regime collapse','Important warning against treating pegs as dollarization'],
  ['Montenegro and Kosovo','Unilateral currency adoption','Small open economies and distinct legal settings']
]) add(`| ${a} | ${b} | ${c} |`);
add('## 10.2 Historical evidence rule');
add('The historical case universe remains a staged intake. A case is not “verified” merely because an index lists it. Full verification requires the underlying judgment, award, official report, or primary dataset to be acquired and read with locators.');
page();

add('# 11. Legal and Institutional Architecture');
add('The legal workstream examines the Venezuelan Constitution, Article 318, BCV law, banking law, tax law, labor law, contract law, public-debt law, foreign-exchange rules, sanctions constraints, and payment-system authority. Every conclusion must distinguish fact, interpretation, and unresolved legal question.');
add('A transition statute would need rules for wages, deposits, loans, mortgages, pensions, taxes, government bonds, commercial contracts, accounting, payment systems, and disputes. The future BCV role could include banking supervision, reserve management, payments oversight, statistics, macroprudential regulation, financial stability, and resolution support, while monetary issuance and conventional lender-of-last-resort power would be constrained or removed.');
add('Legal readiness is not an administrative detail. If contract conversion, bank resolution, reserve ownership, or payment settlement is unclear, a technically sound balance-sheet conversion can still fail operationally.');
page();

add('# 12. Quantitative, Scenario, and Stress-Test Framework');
add('## 12.1 Deterministic formulas');
for (const x of ['inflation and compound inflation;', 'monetary growth and velocity;', 'parallel-market premium;', 'reserve coverage;', 'monetary-base, M1, and M2 conversion;', 'money multiplier and credit growth;', 'debt-to-GDP and interest-to-revenue;', 'fiscal deficit-to-GDP;', 'real interest and real credit growth;', 'deposit dollarization and bank-capital ratios;', 'stress losses and liquidity gaps;']) add(`- ${x}`);
add('## 12.2 Scenario library');
for (const x of ['baseline', 'successful dollarization', 'failed dollarization', 'banking crisis', 'credit crunch', 'oil collapse', 'high oil revenue', 'massive FDI', 'capital return', 'capital flight', 'debt restructuring', 'sanctions relief', 'sanctions tightening', 'dual-currency transition', 'currency board', 'monetary reform without dollarization']) add(`- ${x}`);
add('Each scenario carries explicit assumptions and year-1, year-3, year-5, and year-10 outputs for GDP, inflation, credit, employment, reserves, debt, fiscal deficit, poverty, and investment only where inputs support those outputs. Modeled probabilities are labeled model-implied probabilities under specified assumptions, not objective truth.');
add('## 12.3 Advanced models');
add('The architecture includes a Venezuela-specific DSGE design, VAR/SVAR feasibility checks, Monte Carlo engine, system-dynamics loops, and an agent-based transition model. These are prototypes until calibrated to verified data. The architecture does not permit a model to override a missing-data gate.');
page();

add('# 13. Economic Postures and Adversarial Review');
add('| Posture | Primary question |');
add('|---|---|');
for (const [a,b] of [['Hanke / hard money','What does the documented framework imply?'],['Monetarist','What does money growth and expectations imply?'],['Keynesian','What are the demand, employment, and multiplier effects?'],['New Keynesian','How do credibility, nominal rigidity, and expectations interact?'],['Austrian','What are the credit, capital-structure, and intervention distortions?'],['IMF-style','Are reserves, fiscal sustainability, banks, and debt viable?'],['Central banker','What happens when conventional liquidity tools disappear?'],['Banking-risk','What happens to deposits, capital, reserves, and credit?'],['Citizen','What happens to wages, pensions, savings, and access?'],['Business','What happens to working capital, imports, investment, and contracts?'],['Investor','What happens to sovereign, FX, capital-control, and repatriation risk?']]) add(`| ${a} | ${b} |`);
add('The Red Team must steelman the strongest Hanke argument before attacking it. The Blue Team must steelman the strongest opposing argument before defending a modified proposal. A second Red Team pass tests whether the defense resolved the risk or merely restated the claim.');
add('Current status: the evidence gates remain unresolved for a production policy conclusion. The proper result is an evidence and readiness assessment, not a recommendation disguised as certainty.');
page();

add('# 14. Findings, Conditions, and Decision Framework');
add('## 14.1 Findings supported by the present architecture');
for (const x of ['Dollarization is an institutional and balance-sheet reform, not a banknote exchange.', 'M2 cannot be equated with physical USD required.', 'Banking liquidity and solvency must be analyzed separately.', 'Dollarization does not remove the fiscal deficit or debt burden.', 'Oil gross revenue is not the same as usable sovereign FX.', 'Legal-record amounts must not be double-counted or treated as current debt without accounting treatment.', 'Historical analogies require comparable reserves, banking depth, fiscal structure, external financing, and institutions.', 'The current report cannot issue a decision-grade Venezuela recommendation while critical current data remain unavailable or unresolved.']) add(`- ${x}`);
add('## 14.2 Minimum conditions');
for (const x of ['independently verified monetary aggregates and redenomination history;', 'audited BCV balance sheet and reserve classification;', 'commercial-bank asset-quality, liquidity, capital, and FX-mismatch review;', 'funded emergency liquidity and deposit-protection architecture;', 'fiscal adjustment and a credible replacement for monetary financing;', 'debt and PDVSA restructuring path with enforcement exposure modeled;', 'legal conversion rules and tested payment-system operations;', 'protection for pensioners, public employees, low-income households, and unbanked citizens;']) add(`- ${x}`);
add('## 14.3 Decision tree');
add('If monetary statistics are not independently verified, stop. If liquid reserves are insufficient, secure financing or choose another regime. If banks are insolvent, recapitalize before conversion. If fiscal financing is unsustainable without monetary issuance, stabilize the fiscal position first. If emergency liquidity is unfunded, establish the facility. If the debt path is unmanageable, resolve it before conversion. If the legal framework is incomplete, complete the legislative phase. Only then may operational conversion proceed.');
add('## 14.4 Conditional conclusion');
add('The evidence supports a conditional research conclusion, not a policy verdict: official dollarization could become feasible only after the monetary, banking, fiscal, reserve, debt, legal, payment-system, and social prerequisites are independently verified and funded. If those prerequisites remain unresolved, the transition risk is not acceptable for a decision-grade recommendation.');
page();

add('# 15. Limitations and Research Agenda');
add('The principal limitation is not theoretical. It is the incomplete and disputed current data environment. The next research sequence is to acquire and reconcile BCV and SUDEBAN series, classify reserves, construct a current fiscal and oil-flow statement, read all primary legal records in the 80-case universe, verify debt and PDVSA obligations, and calibrate the banking and external-liquidity models.');
add('The report also has legal-access limits. Some commercial books and case documents are metadata-only, restricted, or not locally acquired. Such sources remain in a controlled queue and are not treated as text evidence. The existence of a source gap is itself a finding and is recorded in the source-gap register.');
add('A future edition can become decision-grade only when the critical-data gates are closed, calculations reproduce independently, citations pass audit, the Red-Team/Blue-Team/second-Red-Team loop is complete, and the chief-economist gate authorizes a conclusion.');
page();

add('# References');
add('## Hanke corpus and methodological anchors');
for (const b of books) add(`- ${b.authors.join(', ')}. *${b.title}*. ${b.publisher || 'Publisher not recorded'}, ${b.year}. Metadata source: ${b.metadata_source_url}. Text status: ${b.full_text_status}.`);
for (const p of flows) add(`- ${p.authors.join(', ')}. “${p.title}.” *Studies in Applied Economics* ${p.paper_id.replace('SAE-','No. ')}, ${p.year}. Source locator: ${p.source_locator}. Text status: ${p.full_text_status}.`);
add('## Institutional and legal sources');
for (const [name,url] of [['UNCTAD ISDS Navigator','https://investmentpolicy.unctad.org/investment-dispute-settlement'],['ICSID Case Database','https://icsid.worldbank.org/cases/case-database'],['U.S. Department of Justice','https://www.justice.gov/'],['ICC Venezuela I','https://www.icc-cpi.int/venezuela-i'],['ICJ Guyana v. Venezuela','https://www.icj-cij.org/case/171'],['U.S. District Court, District of Delaware','https://www.ded.uscourts.gov/'],['CourtListener','https://www.courtlistener.com/']]) add(`- ${name}. ${url}. Access and verification status recorded in the HAEIS source registry.`);
add('## Data and comparative sources');
add('- International Monetary Fund historical monetary and financial-statistics artifacts acquired by HAEIS; World Bank historical macroeconomic artifacts acquired by HAEIS; OPEC and other institutional sources where individually verified. Each observation retains source ID, unit, date, and transformation status.');
add('- No restricted or metadata-only record is represented as a verified full-text source.');
page();

add('# Appendix A. Source and Evidence Register');
add('The following register summarizes the evidence architecture used in this edition. It is not a substitute for the machine-readable source registry.');
add('| Evidence class | Current status | Permitted use |');
add('|---|---|---|');
add('| Verified full text | Locally acquired, hashed, read with locator | Direct factual propositions within scope |');
add('| Verified institutional dataset | Source-bound observations with units and dates | Historical or current analysis within coverage |');
add('| Metadata verified | Existence/title/authors confirmed | Bibliography and retrieval planning only |');
add('| Restricted/unread | Lead or record not fully inspected | Gap disclosure; no substantive attribution |');
add('| Modeled | Deterministic or probabilistic output | Scenario analysis only |');
add('| Disputed | Conflicting source or unresolved interpretation | Preserve disagreement; no silent averaging |');
add('## Evidence-handling rules');
for (const x of ['Every material number requires a locator and unit.', 'Every source retains its original URL and retrieval metadata.', 'A newer vintage does not erase an older vintage.', 'Court claims, awards, judgments, payments, and enforcement are separate accounting objects.', 'No primary source is replaced silently by a secondary summary.', 'Missing evidence is reported as `UNAVAILABLE`, not filled by prose.']) add(`- ${x}`);
page();

add('# Appendix B. Venezuela Legal and Claims Index');
add(`The current legal evidence artifact contains ${courtFacts.facts?.length || courtFacts.length || 'a controlled set of'} separately typed facts. The complete 80-case universe remains an intake and verification program; only records with acquired and read primary evidence may be promoted to verified case findings.`);
add('| Evidence ID | Matter | Classification | Amount / fact basis | Locator status |');
add('|---|---|---|---|---|');
const facts = courtFacts.facts || courtFacts;
for (const f of facts.slice(0, 25)) {
  const id = f.fact_id || f.id || 'FACT';
  const matter = f.matter || f.case_name || f.title || 'Matter not stated';
  const cls = f.classification || f.fact_type || 'Legal-record fact';
  const amount = f.amount_usd != null ? `$${f.amount_usd}` : (f.amount_basis || f.statement || 'Not a quantified amount');
  const loc = f.locator || f.page_locator || f.verification_status || 'See source record';
  add(`| ${id} | ${matter} | ${cls} | ${amount} | ${loc} |`);
}
add('## CITGO and PDVH evidence boundary');
add(`The CITGO master evidence artifact records ${citgo.facts?.length || citgo.evidence_items?.length || 'multiple'} source-bound corporate-chain and enforcement facts. Those records support analysis of attachment, collateral, and enforcement exposure. They do not, without a consolidated accounting statement, establish Venezuela’s current debt stock, current reserve position, or the amount available for dollarization.`);
page();

add('# Appendix C. Critical Variable Inventory');
add('The variable inventory is intentionally exhaustive. A listed variable is not an observed value. Variables without source-bound observations remain unavailable.');
add('| Domain | Required variables |');
add('|---|---|');
const inv = variables.variables || variables;
if (Array.isArray(inv)) {
  for (const row of inv) add(`| ${row.domain || 'Domain'} | ${(row.variables || row.required_variables || []).join('; ')} |`);
} else {
  for (const [domain, vals] of Object.entries(inv)) add(`| ${domain} | ${Array.isArray(vals) ? vals.join('; ') : JSON.stringify(vals)} |`);
}
add('## Data quality labels');
for (const x of ['GREEN — strong coverage and source agreement;', 'YELLOW — usable with limitations;', 'ORANGE — weak coverage or material conflict;', 'RED — unavailable, unreconciled, or not decision-grade;']) add(`- ${x}`);
page();

add('# Appendix D. Formula and Indicator Register');
add('| Indicator | Formula or definition | Status rule |');
add('|---|---|---|');
for (const [a,b,c] of [
  ['Inflation','CPI_t / CPI_(t-1) − 1','Requires comparable CPI vintage'],['Parallel premium','Parallel FX / Official FX − 1','Same date and quotation convention'],['Reserve coverage','Liquid FX reserves / defined dollarization requirement','Requirement must be defined'],['Debt/GDP','Debt stock / GDP','Same currency and period basis'],['Interest/revenue','Interest expenditure / government revenue','Accrual/cash basis disclosed'],['Capital adequacy','Regulatory capital / risk-weighted assets','Banking methodology verified'],['Loan/deposit','Loans / deposits','Aggregate or bank-level scope stated'],['Pension cost','Pensioners × monthly benefit × 12','Beneficiary count verified'],['Net oil FX','Gross oil revenue − costs − obligations','Government take and obligations sourced'],['Funding gap','Dollarization requirement − available liquid reserves','Liquid reserves classified']
]) add(`| ${a} | ${b} | ${c} |`);
page();

add('# Appendix E. Machine-Validated Report Index');
add('The following appendix preserves the full machine-generated indexed report, including section-level status, missing-data declarations, chart specifications, formula slots, completeness rows, source conflicts, scenario gates, and policy stop conditions. Its repetition is intentional: it is the audit trail, not narrative filler.');
add('[[BEGIN MACHINE-VALIDATED INDEX]]');
out += finalReport.trim() + '\n';
add('[[END MACHINE-VALIDATED INDEX]]');

fs.writeFileSync(path.join(root, 'reports/venezuela-dollarization-thesis.md'), out);
console.log(`wrote reports/venezuela-dollarization-thesis.md (${out.split(/\s+/).length} words)`);
