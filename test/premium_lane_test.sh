#!/usr/bin/env bash
# premium_lane_test.sh - enterprise/tax/founder/UHNW lanes must stay complete and routed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

python3 - "$ROOT" <<'PY'
from __future__ import annotations

import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
lane = root / "lib" / "client-lanes" / "fortune500-tax-entrepreneur.md"
text = lane.read_text(encoding="utf-8")

checks = 0


def fail(message: str) -> None:
    raise SystemExit(f"FAIL: {message}")


def require(label: str, haystack: str, needles: list[str]) -> None:
    global checks
    missing = [needle for needle in needles if needle not in haystack]
    if missing:
        fail(f"{label} missing: {', '.join(missing)}")
    checks += 1


def section(title: str) -> str:
    pattern = rf"^## {re.escape(title)}\n(?P<body>.*?)(?=^## |\Z)"
    match = re.search(pattern, text, re.M | re.S)
    if not match:
        fail(f"missing section: {title}")
    return match.group("body")


require("lane headings", text, [
    "## Lane 1: Fortune 500 Enterprise Counsel",
    "## Lane 2: Tax System And IRS Engine",
    "## Lane 3: Entrepreneur, Founder, And Unicorn Advisor",
    "## Lane 4: UHNW And Family Office Overlay",
    "## Firm-Level Flow",
    "## Required Client-Facing Packet",
    "## Hard No-Go Items",
])
require("Creative Planning integrated advisory gate", text, [
    "`creative_planning_required`",
    "wealth management/",
    "tax planning and compliance",
    "estate/trust/wealth transfer",
    "business owner/",
    "investor/capital",
    "family-office/UHNW",
    "specialty-practice",
    "accounting/CFO/dashboard",
    "without copying Creative Planning branding",
])

enterprise = section("Lane 1: Fortune 500 Enterprise Counsel")
require("enterprise workstreams", enterprise, [
    "Board, governance, and entity authority",
    "SEC and public-company reporting",
    "Audit, SOX, and accounting controls",
    "Enterprise tax",
    "M&A, finance, and capital markets",
    "Commercial operations",
    "Regulatory and enforcement readiness",
    "Disputes and investigations",
])
require("enterprise bench", enterprise, [
    "glaw-corporate-counsel",
    "/glaw-sec-reporting",
    "/glaw-sec-disclosure",
    "/glaw-accounting",
    "/glaw-tax-provision",
    "glaw-tax-strategy",
    "glaw-pe-vc-counsel",
    "/glaw-compliance",
    "/glaw-investigations",
])
require("enterprise adversaries", enterprise, [
    "IRS examiner",
    "enforcement/disclosure reviewer",
    "auditor/PCAOB lens",
    "plaintiff/opposing counsel",
    "Chief Compliance Officer",
])
require("enterprise Fortune 500 packet depth", enterprise, [
    "10-Q/8-K",
    "S-1/proxy",
    "Form 4/Section 16",
    "Reg S-K/S-X",
    "Inline XBRL control calendar",
    "SOX 302/906",
    "SOX 404 ICFR",
    "ICFR",
    "auditor independence",
    "PCAOB/auditor challenge response",
    "ASC 740 tax provision",
    "Reg FD review packet",
    "`enterprise_required`",
    "litigation-hold/investigation privilege-log/",
])

tax = section("Lane 2: Tax System And IRS Engine")
require("tax phases", tax, [
    "Tax intake and evidence",
    "Current law and figures",
    "Entity tax architecture",
    "Accounting to tax",
    "Credits and incentives",
    "State, local, and international",
    "Compliance and filings",
    "Wealth and estate tax",
])
require("tax bench", tax, [
    "glaw-tax-legal-intake",
    "glaw-financial-forensics",
    "glaw-tax-strategy",
    "/glaw-credit-strategy",
    "/glaw-international-tax",
    "glaw-tax-compliance",
    "/glaw-irs-audit",
    "/glaw-tax-court",
    "/glaw-estate-trusts",
])
require("tax guardrails", tax, [
    "secrecy",
    "sham",
    "undisclosed offshore accounts",
    "business-purpose memo",
    "IRS adversary pass",
])
require("tax-system packet depth", tax, [
    "primary-law citation corpus freshness report",
    "return-position authority",
    "return-line map",
    "tax-credit",
    "Form 3800/6765/3468/8974/8275",
    "transferability/direct-pay/recapture",
    "`tax_credit_required`",
    "`source_ingest_required`",
    "local TAX CREDIT, LLC, SEC, irrevocable-trust, QSBS, credit, offering, or investor-publication",
    "business-purpose/economic-substance memo",
    "Form 8275/8275-R",
    "penalty-defense memo",
    "IRS notice/transcript/account-module/statute-of-",
    "state nexus/apportionment/sourcing/throwback/PTET/",
    "FBAR/FATCA/Form",
    "ASC 740/ETR/deferred-tax",
    "MeF/IRIS/SSA BSO handoff",
    "`tax_engine_required`",
    "international information-return/FBAR/FATCA",
])

founder = section("Lane 3: Entrepreneur, Founder, And Unicorn Advisor")
require("founder stages", founder, [
    "Formation and IP lock-in",
    "QSBS and tax-credit posture",
    "Founder control and governance",
    "Capital raise",
    "Investor tax/disclosure package",
    "Family-office sheltering",
    "Exit and liquidity",
    "Ongoing compliance",
])
require("founder bench", founder, [
    "glaw-corporate-counsel",
    "/glaw-ip-counsel",
    "/glaw-83b-election",
    "glaw-tax-strategy",
    "/glaw-credit-strategy",
    "/glaw-valuation-409a-architect",
    "glaw-pe-vc-counsel",
    "/glaw-fund-regulatory-council",
    "/glaw-estate-trusts",
    "/glaw-asset-protection",
])
require("founder tax and sheltering details", founder, [
    "issuer/shareholder evidence file",
    "QSBS source refresh",
    "proposed-revenue-procedure certificate memo",
    "original-issue and C-corp proof",
    "controlled-group support",
    "redemption-taint screen",
    "83(b)/Form 15620 deadline",
    "solicitation/integration memo",
    "KYC/AML/OFAC/source-of-funds",
    "source-of-wealth",
    "beneficial-owner verification",
    "broker-dealer/finder and transaction-compensation memo",
    "tax-exempt/foreign investor blocker/withholding/UBIT",
    "FATCA/CRS",
    "1042-S",
    "no-guarantee QSBS statement",
    "investor communications and marketing-claim archive",
    "complaint/rescission/",
    "`investor_required`",
    "`qsbs_required`",
    "dynasty/investment trust plan",
    "investment LLC operating rules",
    "direct-ownership carve-out",
    "S-corp/insurance/retirement",
    "`capital_raise_required`",
    "`entity_topology_required`",
    "`source_ingest_required`",
    "default wealth chassis",
    "direct trust-owned asset lane",
    "complete,",
])

manifest = (root / "lib/client-lanes/premium-lanes.json").read_text(encoding="utf-8")
require("premium manifest Creative Planning integrated advisory benchmark", manifest, [
    "creative_planning_required",
    "Creative Planning public-site benchmark source refresh: https://creativeplanning.com/sitemap/",
    "whole-client inventory: household, income, balance sheet, investments, trusts, business entities, real estate, retirement assets, insurance, debt, private fund interests, crypto/digital assets, advisors, goals, and jurisdiction facts",
    "wealth-management and financial-planning lane: goals, cash flow, investment policy, asset allocation, concentration risk, liquidity, debt, retirement, tax-aware portfolio overlay, and recurring review cadence",
    "tax-planning and compliance lane: current figures, return posture, entity tax, credits, SALT, international, estimated tax, controversy, authority freshness, and CPA/preparer handoff",
    "estate, trust, and wealth-transfer lane: trust taxonomy, fiduciary map, situs, beneficiary designations, title/funding, gift/GST/estate tax, philanthropy, and administration cadence",
    "business-owner and founder lane: entity/org chart, governance, cap table, QSBS, 83(b), 409A, tax credits, capital raise, M&A/exit, succession, payroll, accounting, insurance, and technology/legal operations",
    "investor and capital lane: securities exemption, investor eligibility, KYC/AML/OFAC/source-of-funds, subscription documents, risk factors, tax statements, data room, communications controls, and post-close reporting",
    "family-office and UHNW lane: coordinated entities, trusts, investment governance, family governance, philanthropy, bill pay/accounting dashboard, reporting cadence, privacy, and next-generation readiness",
    "integrated handoff rules: founder stock/QSBS, trusts plus concentrated stock, business exit/succession, credits in investor materials, UHNW multi-entity families, and international facts each trigger the required secondary lanes",
    "integrated deliverables: source/evidence binder, lane map, seat ownership table, entity/trust/org chart, tax roadmap, investor/board packet, estate/trust plan, asset-protection plan, compliance calendar, dashboard, and recurring review schedule",
    "adversarial benchmark review: IRS, SEC, creditor/fraudulent-transfer counsel, fiduciary/trustee reviewer, valuation/appraiser, auditor/PCAOB where relevant, investor counsel, privacy/security, and Chief Compliance Officer pass before release",
    "benchmark boundary: Creative Planning materials are used only as a public-market service taxonomy and intake-flow benchmark",
])
require("premium manifest lane-specific founder packet", manifest, [
    "phase_playbook",
    "required_lane_packet",
    "capital raise exemption, Form D, Blue Sky, KYC, and investor-suitability plan",
    "capital_raise_required",
    "exemption selection: Reg D 506(b), Reg D 506(c), Reg CF, Reg A, Reg S, intrastate, or registered offering",
    "investor class map: accredited, qualified purchaser, qualified client, retail crowdfunding, non-U.S., tax-exempt, foreign, and strategic investors",
    "solicitation and integration memo",
    "bad-actor disqualification screen",
    "broker-dealer, finder, referral-fee, and transaction-compensation analysis",
    "investor KYC/AML/OFAC/source-of-funds review",
    "PPM/OM/Form C/Form 1-A disclosure stack",
    "risk-factor bank: tax, securities, dilution, liquidity, valuation, conflicts, related-party, regulatory, transfer, custody, and reporting",
    "Form D, Blue Sky, Reg CF/Form C amendments, Reg A updates, and state notice calendar",
    "tax-exempt/foreign investor blocker, withholding, UBIT/ECI, and K-1/1099/shareholder-reporting screen",
    "side-letter, MFN, information-rights, pro-rata, ROFR/co-sale, and transfer-restriction matrix",
    "post-raise investor update, annual tax statement, and reporting calendar",
    "investor tax disclosure, withholding, K-1/1099/1042-S/FATCA/CRS, and no-guarantee QSBS statement",
    "broker-dealer/finder and transaction-compensation memo",
    "investor risk-factor bank and data-room disclosure archive",
    "use-of-proceeds, funds-flow, cap-table dilution, and post-raise reporting calendar",
    "QSBS source-refresh and proposed revenue procedure certificate memo",
    "QSBS annual checklist, officer certificate, counsel issue list, record-retention covenant, and shareholder information statement",
    "investor persona, eligibility, suitability, authority, and beneficial-owner onboarding packet",
    "investor tax disclosure, withholding, K-1/1099/1042-S/FATCA/CRS, and no-guarantee QSBS statement",
    "side-letter, MFN, information-rights, pro-rata, ROFR/co-sale, transfer-restriction, and confidentiality matrix",
    "investor communications, marketing-claim, performance/projection, complaint, privacy, and retention-control memo",
    "dynasty trust, investment LLC, and direct-ownership carve-out memo",
    "exit waterfall, secondary transfer, and section 1045/1202 liquidity memo",
    "investor_required",
    "qsbs_required",
    "entity_topology_required",
    "source_ingest_required",
    "default chassis: irrevocable dynasty or investment trust owns an investment LLC for diversified brokerage assets, alternatives, private fund interests, real estate interests, crypto custody vehicles, and family investment administration",
    "direct trust-owned asset lane: assets bypass the investment LLC when tax, issuer, transfer, securities, ERISA, insurance, or fiduciary rules make direct ownership preferable",
    "founder restricted stock and 83(b) carve-out: transfer timing, service-provider status, vesting, valuation, and 30-day election proof reviewed before any trust or LLC funding",
    "QSBS section 1202 carve-out: original issue holder, qualified shareholder, holding period, transfer history, section 1202(g), section 1045, gross-assets, active-business, redemption, and shareholder-level limits reviewed before transfer",
    "S-corp stock carve-out: QSST, ESBT, grantor trust, eligible shareholder, single-class-stock, election, consent, and termination-risk screen before trust or LLC ownership",
    "life-insurance carve-out: ILIT ownership, incidents of ownership, new-policy versus transferred-policy, section 2035, premium gifts, Crummey notices, underwriting, and policy-economics screen",
    "retirement-asset carve-out: beneficiary designation, prohibited transaction, RMD, inherited-IRA, UBIT/UBTI, custodial agreement, and qualified-plan rules reviewed before any trust or LLC routing",
    "issuer-restricted private securities carve-out: issuer consent, transfer restrictions, subscription terms, KYC/AML/OFAC, tax forms, ERISA, custody, valuation, and securities-law limits reviewed before transfer",
    "investment LLC governance: manager/trustee authority, operating agreement, capital-call and distribution controls, investment policy statement, fiduciary accounting, charging-order law, books, K-1/reporting, custody, and valuation cadence",
    "adversarial topology review: IRS estate/gift/QSBS examiner, SEC or issuer transfer reviewer, creditor/fraudulent-transfer counsel, trustee fiduciary reviewer, valuation/appraiser, and investor tax counsel pass before funding",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/Options to Broaden the US Tax Base (May 2024 Update).pdf mapped to QSBS, trusts, grantor trusts, multiple-trust stacking, partnership/entity basis, PPLI/PPA, trust reporting proposals, and IRS anti-abuse review",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/what-are-the-different-types-of-irrevocable-trusts.pdf mapped to irrevocable trust administration, grantor-trust income-tax posture, GRAT, QPRT, irrevocable gift trust, ILIT, and trustee focus",
    "local source inventory: /Users/ricardoprieto/Desktop/LLC/FormCandOS.pdf mapped to Reg CF offering statement, LLC agreement, risk factors, investor acknowledgments, subscription mechanics, transfer restrictions, series LLC governance, beneficial ownership, and issuer/investor tax disclaimers",
    "output traceability: every QSBS certificate, tax-credit claim, investor tax statement, offering disclosure, trust/LLC topology memo, and tax-return position cites the source-ingest row or marks the source not applicable with rationale",
    "QSBS source refresh: IRC section 1202, section 1045, Treasury/IRS current guidance, and 2023 CLA Proposed Revenue Procedure to Standardize the Information Corporations Give Shareholders to Show That Stock is QSBS",
    "issuer status: domestic C corporation at issuance and during substantially all tested years",
    "original-issue acquisition: issuance date, shareholder name, certificate/ledger entry, consideration paid",
    "qualified-small-business gross-assets test: cash, adjusted basis, contributed-property FMV, immediate pre/post-issuance aggregate gross assets, $50 million threshold",
    "controlled-group and subsidiary look-through: 50 percent parent-child controlled-group members",
    "active-business requirement: 80 percent active qualified trade or business assets",
    "annual QSBS checklist: each tested year C-corp status, controlled group, subsidiaries, asset categories",
    "redemption taint screen: related-party redemptions two years before/after issuance",
    "shareholder-side facts: acquisition chain, pass-through/gift/death/reorganization/section 351 history",
    "QSBS corporation certificate: officer-signed factual certificate, counsel-reviewed legal issue list",
    "shareholder information package: issuer evidence, shareholder evidence, no-guarantee statement",
    "investor and transfer structuring: direct ownership versus trust/partnership/LLC/IRA ownership",
    "exit and M&A preservation: merger/reorganization section 1202(h)",
    "adversarial review: IRS QSBS examiner, shareholder tax advisor, company counsel",
    "investor persona and capacity map: individual, entity, trust, IRA/qualified plan, family office, fund, strategic, tax-exempt, foreign, and nominee/beneficial-owner screen",
    "investor eligibility and suitability: accredited investor, qualified purchaser, qualified client, sophistication, investment limits, bad-actor and disqualification status",
    "KYC, AML, OFAC, sanctions, politically exposed person, source-of-funds, source-of-wealth, and beneficial-ownership verification",
    "subscription agreement, investor questionnaire, W-9/W-8, entity authority, trust/IRA custodian authority, and signature authority package",
    "tax reporting profile: K-1/1099/1042-S/1099-B/Form 3921/3922/shareholder statement, withholding, FATCA/CRS, UBIT, ECI, PFIC/CFC, and state tax screen",
    "QSBS and tax-credit investor statement: no guarantee, issuer evidence, shareholder holding-period tracking, section 1045 rollover, section 1202 limitations, and reporting owner",
    "communications controls: investor updates, projections, performance claims, testimonials, selective disclosure, Reg FD where relevant, marketing archive, and version control",
    "investor complaint, rescission, fraud, misstatement, blue-sky, SEC/state examiner, IRS investor-tax, and plaintiff counsel adversarial review pass",
    "data privacy and retention: investor PII, tax IDs, bank details, secure storage, retention, access logs, deletion limits, and breach-response owner",
    "QSBS annual certificate, record-retention, and shareholder information refresh",
    "section 1045 60-day rollover deadline where relevant",
])
creative = (root / "seats/glaw-tax-strategy/references/creative-planning-benchmark-lanes.md").read_text(encoding="utf-8")
require("Creative Planning benchmark memo current source refresh", creative, [
    "Current public-site snapshot reviewed on 2026-08-13",
    "https://creativeplanning.com/sitemap/",
    "Family Office",
    "Wealth Strategies",
    "Business\n  Solutions",
    "professional athletes, dental professionals, law enforcement, aviation, and special",
    "founders, C-suite executives, entrepreneurs, professional athletes, venture capitalists, and",
    "entities, trusts, business interests, administrative support, privacy, control, diversification",
    "audit and attest, business tax, outsourced accounting and bill pay, payroll",
    "## Machine-Enforced Checklist",
    "`creative_planning_required`",
    "whole-client inventory",
    "adversarial review by IRS, SEC, creditor/fraudulent-transfer counsel",
])
require("premium manifest Fortune 500 packet depth", manifest, [
    "enterprise_required",
    "10-K/10-Q/8-K/S-1/proxy, Reg S-K/S-X, MD&A, risk-factor, Form 4/Section 16, and Inline XBRL control calendar",
    "SOX 302/906 certification, SOX 404 ICFR, disclosure controls, audit committee, and PBC evidence bridge",
    "PCAOB/auditor independence challenge response and material-weakness remediation memo",
    "ASC 740 tax provision, ETR, deferred-tax, UTP, valuation allowance, and auditor tie-out register",
    "litigation hold, investigations, privilege log, custodians, evidence timeline, and document-preservation memo",
    "public-company reporting profile: filer status, 10-K, 10-Q, 8-K, S-1, proxy, Form 4/Section 16, Reg S-K, Reg S-X, and Inline XBRL screen",
    "SOX 302/906 certification, SOX 404 ICFR, disclosure controls and procedures, control-owner evidence, and deficiency/material-weakness remediation",
    "audit committee, PBC list, auditor independence, PCAOB inspection/challenge response, management representation, and audit-adjustment log",
    "enterprise regulatory map: SEC, DOJ, FTC, CFPB, FinCEN/BSA/AML, OFAC, state AG, licensing, privacy, employment, and industry regulator exposure",
    "board/investor disclosure packet, investor-relations controls, analyst guidance, earnings release, and selective-disclosure/Reg FD review",
    "recurring docket: SEC reports, board/audit committee meetings, close calendar, certifications, annual reports, franchise tax, litigation holds, and regulator response deadlines",
])
require("premium manifest tax-system packet depth", manifest, [
    "primary-law citation corpus freshness report",
    "tax_engine_required",
    "tax_credit_required",
    "source_ingest_required",
    "source evidence intake: taxpayer profile, entity chart, source-file index, missing-information list, and document hashes",
    "current-law and current-figures freshness ledger",
    "primary-law citation corpus and authority hierarchy",
    "entity classification, tax election, basis, AAA, capital account, and section 704/1368/1202 screen",
    "GL trial-balance tie-out, book-to-tax M-1/M-3 bridge, return-line map, and control manifest",
    "credit and incentive eligibility, substantiation, wage/capex/time-record support, recapture, transferability, and return-position owner",
    "return-position authority level, business-purpose/economic-substance memo, Form 8275/8275-R disclosure, and penalty-defense analysis",
    "IRS notice, transcript, account module, statute-of-limitations, response-deadline, Appeals, and Tax Court docket ledger",
    "SALT nexus, apportionment, sourcing, throwback, PTET, franchise/margin, sales/use tax, and state-credit matrix",
    "international information-return, FBAR/FATCA, Form 8938, 5471, 5472, 8865, 8858, GILTI, Subpart F, FDII, BEAT, 962, withholding, and treaty screen",
    "tax provision ASC 740, current/deferred tax, ETR, uncertain-tax-position register, and auditor/PBC bridge where relevant",
    "return/payment/e-file/transmitter/MeF/IRIS/SSA BSO handoff and no-live-filing authority check",
    "recurring docket: returns, extensions, estimated taxes, notices, elections, credit certifications, information returns, and trust administration",
    "tax-credit source refresh: IRC sections, Treasury/IRS notices, forms, instructions, current-year inflation figures, state credit guidance, and expiration/phaseout/effective-date ledger",
    "credit inventory and routing: R&D section 41/174A, payroll credit, section 45X/45Y/48/48E/30C/45V/45Q/45L/179D, LIHTC, NMTC, WOTC, ERC/historic claims, disaster, foreign tax credit, AMT, state and local credits, and industry-specific incentives",
    "eligibility screen: taxpayer/entity type, activity, location, placed-in-service or wage period, ownership, related-party, aggregation, controlled-group, tax-exempt/government/foreign investor, and anti-abuse limits",
    "source evidence index: contracts, invoices, payroll, time records, GL accounts, fixed-asset register, engineering records, location data, certification letters, permits, interconnection/utility documents, and document hashes",
    "R&D substantiation: business component, permitted purpose, technological uncertainty, process of experimentation, qualified research expenses, wage/supply/contract allocation, section 174/174A capitalization, and payroll-credit election support",
    "energy and IRA credit substantiation: prevailing wage/apprenticeship, domestic content, energy community, low-income community, beginning-of-construction, placed-in-service, transfer election, direct pay, registration number, and recapture monitoring",
    "credit computation workpaper: base amount, incremental or percentage calculation, limitation ordering, carryforward/carryback, basis reduction, passive activity, at-risk, AMT, section 38 general business credit, and book-to-tax tie-out",
    "forms and filing package: Form 3800, 6765, 3468, 8835, 8911, 8933, 8974, 8994/8995 where relevant, Form 8275/8275-R disclosure, state credit forms, and e-file/transmitter/MeF handoff owner",
    "transferability, monetization, and investor reporting: section 6418 transfer, section 6417 direct pay, tax-credit purchase agreement, indemnity/insurance, buyer diligence file, investor K-1/1099/shareholder statement, and no-guarantee disclosure",
    "financial-statement and audit tie-out: ASC 740, uncertain tax position, ETR, deferred tax, grant accounting, capitalization, auditor PBC bridge, control-owner evidence, and management representation",
    "adversarial review: IRS credit examiner, state credit authority, forensic accountant, auditor/PCAOB where relevant, investor/buyer counsel, and Chief Compliance Officer pass before claiming, selling, transferring, or reporting any credit",
    "tax-credit eligibility, substantiation, computation, transferability, recapture, and forms packet",
    "credit certification, registration, substantiation, recapture, transferability, and carryforward deadlines",
    "return-position authority, Form 8275/8275-R disclosure, and penalty-defense memo",
    "IRS notice, transcript, statute-of-limitations, and response-deadline ledger",
    "state nexus/apportionment/PTET/franchise-tax matrix",
    "international information-return and FBAR/FATCA screen",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/Options to Broaden the US Tax Base (May 2024 Update).pdf mapped to QSBS, trusts, grantor trusts, multiple-trust stacking, partnership/entity basis, PPLI/PPA, trust reporting proposals, and IRS anti-abuse review",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/what-are-the-different-types-of-irrevocable-trusts.pdf mapped to irrevocable trust administration, grantor-trust income-tax posture, GRAT, QPRT, irrevocable gift trust, ILIT, and trustee focus",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/fy2026h1_tab8.pdf mapped to tax expenditure and credit inventory, QSBS, R&E/R&D, state credits, investment credits, brownfields, LIHTC, historic, climatetech, qualified conversion, internship, transferability, and refundability concepts",
    "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/F_PUB_550.pdf mapped to investment income, capital gain/loss, basis, holding periods, investment interest, tax shelters/reportable transactions, and Pub. 550 small-business-stock reporting context",
    "local source inventory: /Users/ricardoprieto/Desktop/LLC/FormCandOS.pdf mapped to Reg CF offering statement, LLC agreement, risk factors, investor acknowledgments, subscription mechanics, transfer restrictions, series LLC governance, beneficial ownership, and issuer/investor tax disclaimers",
    "local source inventory: /Users/ricardoprieto/Desktop/SEC/id257bpm.pdf mapped to SEC delinquent-reporting enforcement, investor-protection rationale, public-reporting consequences, adversarial SEC lens, and investor communications controls",
    "external authority refresh: IRS Instructions for Schedule D (Form 1120-S), current 26 U.S.C. section 1202 text, section 1045, Treasury/IRS guidance, and CLA QSBS proposed revenue procedure source are dated and reconciled against local source conclusions",
    "source-backed no-go screen: tax shelters, reportable transactions, promoted credit claims, PPLI/PPA, multiple-trust stacking, grantor-trust freezes, backdating, sham entities, and guaranteed QSBS/credit claims receive IRS/SEC/adversarial review before use",
    "output traceability: every QSBS certificate, tax-credit claim, investor tax statement, offering disclosure, trust/LLC topology memo, and tax-return position cites the source-ingest row or marks the source not applicable with rationale",
])
require("premium manifest UHNW trust packet", manifest, [
    "trust taxonomy and administration matrix",
    "revocable, A-B/bypass, testamentary, irrevocable gift, dynasty/GST, IDGT, GRAT/GRUT, QPRT, SLAT, ILIT, CRT/CLT, DAPT/offshore APT, DING/NING/ING, special-needs, QSST/ESBT, land/DST, business/statutory, rabbi/secular, qualified-plan/IRA, purpose, and constructive/resulting trust classification memo",
    "trust_taxonomy_required",
    "revocable living trust",
    "A-B / bypass / credit-shelter trust",
    "testamentary trust",
    "IDGT",
    "GRAT / GRUT",
    "SLAT",
    "CRT / CRAT / CRUT / NIMCRUT",
    "CLT / CLAT / CLUT",
    "DAPT",
    "offshore APT",
    "DING / NING / ING",
    "QSST / ESBT",
    "Delaware statutory trust / DST",
    "business/statutory trust",
    "rabbi / secular trust",
    "qualified plan / IRA custodial trust",
    "constructive / resulting trust",
    "situs, trustee, beneficiary, and distribution-design memo",
    "investment LLC governance and IPS packet",
    "asset-protection solvency and fraudulent-transfer screen",
    "entity_topology_required",
    "trustee/executor fiduciary-risk workpaper",
    "special-needs, conservatorship, and incapacity planning branch memo",
    "family governance, mission statement, equal/equitable distribution, and beneficiary-readiness memo",
    "current Schwab Learn trusts topic source update note from https://www.schwab.com/learn/topic/trusts",
    "schwab_trust_topic_required",
    "Schwab trusts topic source update note: https://www.schwab.com/learn/topic/trusts dated source refresh and visible topic-index capture",
    "Schwab 2026 topic-index capture: How to Plan Around Estate Tax Uncertainties (Aug. 11, 2026)",
    "Avoiding Restrictions With a Discretionary Trust (Nov. 14, 2025)",
    "estate-tax uncertainty: A-B/bypass, GRAT, CRT, federal/state estate-tax uncertainty, and old formula-clause review",
    "SLAT planning: separate-property funding, community-property partition, reciprocal-trust doctrine, HEMS/independent trustee, access risk, basis tradeoff, and optional dynasty/GST design",
    "dynasty trust planning: GST allocation, situs, trustee location, duration/perpetuities law, distribution standards, creditor/divorce protection, and income-tax posture",
    "ILIT and IRA funding: RMD/income-tax modeling, underwriting, Form 709, Crummey notices, policy economics, incidents of ownership, and section 2035 three-year-rule screen",
    "QPRT planning: retained term, section 7520 valuation, survival risk, post-term leaseback, basis tradeoff, property tax, title, and insurance review",
    "discretionary trust planning: trustee discretion, HEMS or incentive standards, beneficiary conflict, oversight cost, and professional co-trustee option",
    "equal-versus-equitable distributions: family governance, beneficiary fairness, difficult-to-divide assets, advance gifts, special assets, and communication memo",
    "special-needs, conservatorship, and incapacity planning: benefits preservation, care plan, POA, healthcare directive, successor fiduciary, and administrative powers",
    "charitable trust routing: CRT/CRAT/CRUT/NIMCRUT/CLT comparison, payout/reporting tests, gain deferral, income stream, deduction, and philanthropic intent",
    "page-level source drift control: pages 1 through 4 of the Schwab trusts topic index are captured with title, date, URL, and routing note before relying on the benchmark",
    "founder and business-owner succession crosswalk: IP protection, assignment, governance, and estate-transfer issues from the Schwab trust index are routed to corporate/IP/tax seats where relevant",
])

uhnw = section("Lane 4: UHNW And Family Office Overlay")
require("uhnw workstreams", uhnw, [
    "Estate and trust design",
    "Asset protection",
    "Gift, GST, and estate tax",
    "Investment governance",
    "Philanthropy",
    "Fiduciary administration",
    "Family governance and special situations",
])
require("uhnw bench", uhnw, [
    "/glaw-estate-trusts",
    "glaw-tax-strategy",
    "/glaw-asset-protection",
    "/glaw-estate-gift-returns",
    "/glaw-exempt-org",
    "glaw-institutional-finance",
])
require("uhnw full trust taxonomy prose", uhnw, [
    "classification memo",
    "revocable living",
    "A-B/bypass/credit-shelter",
    "testamentary",
    "dynasty/GST",
    "GRAT/GRUT",
    "CRT/CRAT/CRUT/NIMCRUT",
    "DAPT",
    "offshore APT",
    "QSST/ESBT",
    "Delaware statutory trust/DST",
    "business/statutory trust",
    "qualified-plan/IRA custodial",
    "blind",
    "constructive/resulting trust",
    "`trust_taxonomy_required`",
    "https://www.schwab.com/learn/topic/trusts",
    "estate-tax uncertainty",
    "SLAT",
    "dynasty trust",
    "ILIT/IRA funding",
    "equal-versus-equitable",
    "discretionary trust planning",
    "loss-driven administration",
    "trust account setup",
    "`schwab_trust_topic_required`",
    "source date before GLAW says the trust lane reflects current public-market",
    "`entity_topology_required`",
    "direct-ownership carve-out analysis for founder restricted stock/83(b), QSBS/§1202",
    "before any trust-owned investment LLC",
    "selected, rejected, or not applicable with rationale",
])

flow = section("Firm-Level Flow")
require("firm flow gates", flow, [
    "Classify the matter by lane and track",
    "clear conflicts",
    "source evidence manifest",
    "Assign one lead seat",
    "lane-specific deliverables index",
    "Run RED to BLUE review",
    "Chief/Council approval",
    "Docket every recurring obligation",
])

packet = section("Required Client-Facing Packet")
require("client packet", packet, [
    "executive decision memo",
    "lane map and seat ownership table",
    "entity/trust/org chart",
    "tax strategy and compliance calendar",
    "investor or board disclosure packet",
    "financial model or accounting tie-out",
    "risk matrix",
    "implementation checklist",
    "docket export",
    "attorney/CPA/local-counsel review conditions",
])

nogo = section("Hard No-Go Items")
require("hard no-go controls", nogo, [
    "hiding beneficial ownership",
    "backdating",
    "QSBS, credits, or deductions are guaranteed",
    "defeat an existing or foreseeable creditor",
    "unregistered securities offerings",
    "no business purpose or economic substance",
    "without human authority",
])

for rel in [
    "SKILL.md",
    "lib/firm-roster.md",
    "docs/org-chart-and-usage.md",
    "docs/MODULES.md",
]:
    require(f"{rel} routes premium lanes", (root / rel).read_text(encoding="utf-8"), [
        "lib/client-lanes/fortune500-tax-entrepreneur.md",
    ])

index = (root / "app/public/index.html").read_text(encoding="utf-8")
require("public premium lane landing page", index, [
    "id=\"premium-lanes\"",
    "infers these premium lanes server-side",
    "returns a source-only handoff package with lane attach commands",
    "active-matter handoff does not depend on browser-only routing",
    "intake id plus handoff package",
    "Fortune 500 Enterprise Counsel",
    "10-K/10-Q/8-K",
    "S-1/proxy",
    "Section 16",
    "Inline XBRL",
    "SOX 302/404",
    "ICFR",
    "PCAOB",
    "Reg FD",
    "Tax System And IRS Engine",
    "return-line maps",
    "R&amp;D §41/§174A",
    "IRA energy credits",
    "3800/6765/3468/8974",
    "transferability",
    "recapture",
    "8275",
    "FBAR/FATCA",
    "ASC 740",
    "e-file handoff",
    "Founder And Unicorn Advisor",
    "QSBS certificate",
    "§1202",
    "§1045",
    "Reg D/CF/A/S raise",
    "investor suitability",
    "KYC/AML/OFAC",
    "W-9/W-8",
    "K-1/1099/1042-S",
    "side letters",
    "transfer controls",
    "UHNW Family Office Overlay",
    "Full trust taxonomy",
    "CRT/CLT",
    "DAPT/offshore",
    "QSST/ESBT",
    "fortune500-enterprise",
    "tax-system",
    "founder-unicorn",
    "uhnw-family-office",
])

print(f"{checks} passed")
PY
