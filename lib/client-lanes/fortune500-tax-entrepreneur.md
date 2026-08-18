# GLAW Premium Client Lanes

This is the firm-level operating map for matters that must feel like a coordinated AmLaw,
Big Four tax, investment-bank, and family-office bench. It does not replace the stage gates or
the specialist seats. It tells `/glaw` which bench to assemble, what deliverables are expected,
and which adversaries must attack the work before it can be treated as file-ready.

Machine-readable lane data lives in `lib/client-lanes/premium-lanes.json`. Use
`bin/glaw-premium-lanes list|show|playbook|scaffold|attach|complete|render-packet|docket|check-packet|status|validate`
to generate an operator kickoff playbook, generate an operational lane packet, attach it to the
active matter as a source-backed workpaper, populate owners/reviewer outcomes/docket metadata
without hand-editing JSON, render lane-specific draft templates for the client packet, materialize
the lane's recurring obligations into `docket.jsonl`, report matter-wide readiness/action plans,
and fail closed until owners, reviewers, docket items, rendered packet templates, docket
materialization, and deliverables are ready.

Every lane starts with structured intake, conflicts/engagement, source evidence, current-figure
verification, and a jurisdiction pack. Every lane ends with a final packet, Chief decision,
UPL footer, and docketed follow-up obligations.

The machine manifest must include both `phase_playbook` and `required_lane_packet` entries for
each lane. The global packet proves the common client-facing deliverables; the lane-specific
packet proves the concrete operating surface for that client type, such as SEC disclosure for
enterprise work, book-to-tax and credit substantiation for tax work, capital-raise/QSBS/investor
disclosure for founders, and trust/LLC/estate administration for UHNW work.

Creative Planning's public service architecture is a benchmark source for the whole-client
advisory flow only. Every premium lane must classify every item in `creative_planning_required`
as complete, rejected, or not applicable with a dated source refresh before the packet says it
reflects a coordinated advisory model. The gate must route the matter through wealth management/
financial planning, tax planning and compliance, estate/trust/wealth transfer, business owner/
founder, risk/insurance/asset protection, investor/capital, family-office/UHNW, international,
specialty-practice, accounting/CFO/dashboard, integrated handoff, deliverables, and adversarial
review screens without copying Creative Planning branding, claims, client counts, awards, or
service language.

## Lane 1: Fortune 500 Enterprise Counsel

Use when the client is public, public-ready, private-equity backed, multinational, regulated,
or otherwise enterprise-scale.

| Workstream | Lead seats | Required outputs |
|---|---|---|
| Board, governance, and entity authority | `glaw-corporate-counsel`, `/glaw-entity-architect`, `glaw-elite-corporate-counsel` | authority matrix, board consent map, delegation policy, subsidiaries and signatory table |
| SEC and public-company reporting | `/glaw-sec-reporting`, `/glaw-sec-disclosure`, `/glaw-disclosure-risk-analyzer` | filer-status profile, 10-K/10-Q/8-K/S-1/proxy issue list, Form 4/Section 16 screen, MD&A/risk-factor/non-GAAP/KPI/related-party/cyber/climate/litigation disclosure controls, Reg S-K/S-X checklist, Inline XBRL/controls handoff |
| Audit, SOX, and accounting controls | `/glaw-accounting`, `/glaw-controller`, `/glaw-audit`, `/glaw-audit-assurance`, `/glaw-tax-provision` | close calendar, SOX 302/906 certifications, SOX 404 ICFR map, disclosure controls and procedures, PBC list, auditor independence, PCAOB challenge response, material-weakness remediation, ASC 740 provision bridge, auditor-ready workpapers |
| Enterprise tax | `glaw-tax-strategy`, `/glaw-international-tax`, `/glaw-sales-tax`, `/glaw-estate-gift-returns` when relevant | tax position memo, current-figures citation, SALT/international map, uncertain-tax-position register, reporting calendar |
| M&A, finance, and capital markets | `glaw-elite-corporate-counsel`, `glaw-pe-vc-counsel`, `glaw-institutional-finance`, `glaw-fs-*` modeling seats | deal thesis, diligence request list, financing/offering exemption analysis, model outputs, closing checklist |
| Commercial operations | `/glaw-commercial-contracts`, `glaw-contract-review`, `/glaw-employment-counsel`, `/glaw-privacy-data` | contract playbook, redline/scorecards, vendor-risk matrix, employment/privacy compliance map |
| Regulatory and enforcement readiness | `/glaw-compliance`, `/glaw-regulatory-aml`, `/glaw-fincen`, `/glaw-sec`, `/glaw-investigations` | regulator map, enforcement exposure matrix, remediation plan, evidence-preservation notice |
| Disputes and investigations | `glaw-elite-corporate-counsel`, `glaw-federal-trial-counsel`, `/glaw-investigations`, `/glaw-evidence-timeline` | case theory, claims/defenses, chronology, damages model, litigation-hold and docket matrix |

Enterprise matters require an adversarial panel that includes, at minimum: IRS examiner, SEC
enforcement/disclosure reviewer, auditor/PCAOB lens, plaintiff/opposing counsel, regulator, and
Chief Compliance Officer. If international operations exist, add treaty, CFC, transfer-pricing,
sanctions, and data-transfer reviewers.

Lane-specific packet items: board authority/delegation matrix, SEC disclosure tracker, 10-K/
10-Q/8-K/S-1/proxy, Form 4/Section 16, Reg S-K/S-X, MD&A, risk-factor, non-GAAP, KPI,
related-party, cyber, climate, litigation, and Inline XBRL control calendar, SOX 302/906
certification, SOX 404 ICFR, disclosure controls and procedures, audit committee, PBC evidence
bridge, auditor independence, PCAOB/auditor challenge response and material-weakness remediation
memo, ASC 740 tax provision, ETR, deferred-tax, UTP, valuation allowance, and auditor tie-out
register, enterprise regulatory exposure matrix, litigation-hold/investigation privilege-log/
custodian/evidence-timeline/document-preservation memo, and board/investor disclosure, earnings-
release, analyst-guidance, investor-relations, and Reg FD review packet. The generated packet must
classify every item in `enterprise_required` as complete, rejected, or not applicable with
rationale before board, investor, auditor, regulator, or public-company use.

## Lane 2: Tax System And IRS Engine

Use when the client wants tax planning, tax compliance, tax controversy, accounting-to-tax
conversion, credits, entity tax, or wealth transfer.

| Phase | Lead seats | Required outputs |
|---|---|---|
| Tax intake and evidence | `glaw-tax-legal-intake`, `glaw-financial-forensics`, `/glaw-bookkeeping` | taxpayer profile, source-file index, missing-information list, statute/deadline inventory |
| Current law and figures | `glaw-tax-strategy`, `tax-legal-shared/current-figures.md`, `/glaw-legal-research` | current-figures check, authority ledger, stale-law flags |
| Entity tax architecture | `glaw-tax-strategy`, `glaw-corporate-counsel`, `/glaw-entity-architect` | C/S/partnership/LLC comparison, election calendar, basis/AAA/capital-account/§704/§1368/§1202 workplan |
| Accounting to tax | `/glaw-accounting`, `/glaw-tax-provision`, `/glaw-controller`, `/glaw-audit` | trial-balance tie-out, book-to-tax M-1/M-3 bridge, return-line map, deferred-tax roll-forward, control manifest |
| Credits and incentives | `/glaw-credit-strategy`, `glaw-tax-strategy`, `/glaw-fixed-assets`, `/glaw-tax-provision`, `/glaw-audit` | credit inventory, law/form/source refresh, R&D §41/§174A and payroll-credit substantiation, IRA/energy credit substantiation, wage/capex/time-record/fixed-asset support, Form 3800/6765/3468/8974/8275 package, transferability/direct-pay/recapture screen, ASC 740/UTP/auditor tie-out, deadlines, form and return-position owner |
| State, local, and international | `glaw-tax-strategy`, `/glaw-international-tax`, `/glaw-sales-tax` | nexus matrix, apportionment/sourcing/throwback, PTET/franchise/margin/sales-use tax screen, GILTI/Subpart F/FDII/BEAT/§962/withholding/treaty/FBAR/FATCA map |
| Compliance and filings | `glaw-tax-compliance`, `/glaw-back-taxes`, `/glaw-irs-audit`, `/glaw-tax-court` | filing packet, e-file/transmitter/MeF/IRIS/SSA BSO handoff, notices matrix, transcripts, SOL/response ledger, penalty/interest computation, controversy path, docketed deadlines |
| Wealth and estate tax | `glaw-tax-strategy`, `/glaw-estate-trusts`, `/glaw-asset-protection`, `/glaw-estate-gift-returns` | trust taxonomy selection, gift/GST/estate return calendar, funding/title checklist, fraudulent-transfer screen |

The tax system never recommends secrecy, false invoices, disguised personal expenses, sham
entities, backdating, nominee owners, abusive shelters, or undisclosed offshore accounts. Borderline
positions require a business-purpose memo, disclosure analysis, privilege routing to tax counsel,
and an IRS adversary pass.

Lane-specific packet items: source-evidence index, current-figures/authority freshness ledger,
primary-law citation corpus freshness report, entity election and basis calendar, book-to-tax
M-1/M-3 bridge and return-line map, credit substantiation and return-position matrix, tax-credit
eligibility/substantiation/computation/transferability/recapture/forms packet, return-position authority,
business-purpose/economic-substance memo, Form 8275/8275-R disclosure, and penalty-defense memo, IRS notice/transcript/account-module/statute-of-
limitations/response-deadline ledger, state nexus/apportionment/sourcing/throwback/PTET/
franchise/margin/sales-use tax matrix, international information-return/FBAR/FATCA/Form
8938/5471/5472/8865/8858/GILTI/Subpart F/FDII/BEAT/§962/withholding/treaty screen, estate/
gift/GST/trust 1041/DNI/Form 706/Form 709 screen where relevant, ASC 740/ETR/deferred-tax/
UTP/auditor-PBC bridge where relevant, IRS controversy/disclosure decision memo, and
return/payment/e-file/transmitter/MeF/IRIS/SSA BSO handoff with no-live-filing authority
check. The generated packet must classify every item in `tax_engine_required` as complete,
rejected, or not applicable with rationale before any return position, filing packet,
investor tax statement, or controversy recommendation is used. It must classify every item in
`tax_credit_required` as complete, rejected, or not applicable with rationale before any credit is
claimed, sold, transferred, modeled, reported to an investor, booked under ASC 740, or defended in
an IRS/state examination. It must classify every item in `source_ingest_required` before relying on
local TAX CREDIT, LLC, SEC, irrevocable-trust, QSBS, credit, offering, or investor-publication
source material for any tax position, credit claim, source-evidence packet, investor tax
statement, or controversy recommendation.

## Lane 3: Entrepreneur, Founder, And Unicorn Advisor

Use when the client is forming a company, raising capital, issuing equity, building a fund or
SPV, claiming QSBS/tax credits, preparing for exit, or sheltering founder wealth.

| Stage | Lead seats | Required outputs |
|---|---|---|
| Formation and IP lock-in | `glaw-corporate-counsel`, `/glaw-ip-counsel`, `/glaw-83b-election` | entity choice, charter/bylaws/OA, founder stock, IP assignment, 83(b)/Form 15620 deadline |
| QSBS and tax-credit posture | `glaw-tax-strategy`, `/glaw-credit-strategy`, `/glaw-valuation-409a-architect` | QSBS source refresh, issuer/shareholder evidence file, proposed-revenue-procedure certificate memo, original-issue and C-corp proof, gross-assets and controlled-group support, annual active-business checklist, redemption-taint screen, 409A/valuation plan, credit substantiation plan |
| Founder control and governance | `glaw-corporate-counsel`, `glaw-elite-corporate-counsel` | dual-class/voting/protective provisions, board composition, transfer restrictions, control-risk memo |
| Capital raise | `glaw-pe-vc-counsel`, `/glaw-fund-regulatory-council`, `glaw-fs-kyc-*`, `glaw-pitch-deck` | exemption choice, solicitation/integration memo, Form D/Blue Sky/Reg CF/Reg A calendar, investor eligibility/KYC/AML/OFAC/source-of-funds, subscription docs, risk factors, data room, deck/CIM |
| Investor tax/disclosure package | `glaw-tax-strategy`, `glaw-pe-vc-counsel`, `/glaw-legal-research`, `glaw-fs-kyc-*`, `/glaw-regulatory-aml` | investor persona/capacity map, eligibility/suitability and authority screen, no-guarantee QSBS statement, tax-attribute package, credit-risk disclosure, KYC/AML/OFAC/source-of-funds/source-of-wealth/beneficial-owner verification, tax-exempt/foreign investor blocker/withholding/UBIT/ECI/FATCA/CRS screen, annual K-1/1099/1042-S/shareholder reporting promises |
| Family-office sheltering | `glaw-tax-strategy`, `/glaw-estate-trusts`, `/glaw-asset-protection` | dynasty/investment trust plan, investment LLC operating rules, direct-ownership carve-out for QSBS/83(b)/S-corp/insurance/retirement |
| Exit and liquidity | `glaw-institutional-finance`, `glaw-company-valuation`, `glaw-tax-strategy`, `glaw-elite-corporate-counsel` | exit waterfall, tax estimate, purchase agreement issue list, rollover/1045/1202 analysis, post-exit investment policy |
| Ongoing compliance | `glaw-corporate-counsel`, `glaw-tax-compliance`, `/glaw-docket`, `/glaw-accounting` | annual report/franchise tax, cap-table hygiene, books close, tax filing calendar, securities reporting promises |

The default founder topology is: operating company selected for business and investor fit,
founder shares held directly when 83(b), QSBS, issuer transfer limits, or tax rules require;
family wealth moves into irrevocable dynasty/investment trust structures only when transfer,
tax, securities, solvency, and fraudulent-transfer gates clear. The default wealth chassis is
an irrevocable dynasty/investment trust owning an investment LLC for diversified investments,
with a direct trust-owned asset lane where tax, issuer, transfer, securities, ERISA, insurance,
or fiduciary rules make direct ownership preferable.

Lane-specific packet items: formation/IP checklist, 83(b)/Form 15620 proof, QSBS source-refresh
and proposed revenue procedure certificate memo, QSBS issuer/shareholder evidence, QSBS annual
checklist, officer certificate, counsel issue list, record-retention covenant, shareholder
information statement, 409A/equity-comp readiness, capital raise exemption/Form D/Blue Sky/Reg
CF/Reg A/KYC/AML/OFAC/source-of-funds/investor-suitability plan, solicitation and integration
memo, bad-actor screen, broker-dealer/finder and transaction-compensation memo, subscription
agreement and investor questionnaire, investor persona/capacity/authority/beneficial-owner
onboarding packet, PPM/OM/Form C/Form 1-A disclosure stack, investor risk-factor bank and
version-controlled data-room archive, use-of-proceeds/funds-flow/cap-table dilution/post-raise
reporting calendar, side-letter/MFN/pro-rata/information-rights/ROFR/co-sale/transfer-restriction/
confidentiality matrix, investor communications and marketing-claim archive, complaint/rescission/
misstatement control memo, data-privacy and retention-control memo, tax-exempt/foreign investor
blocker/withholding/UBIT/ECI/K-1/1099/1042-S/FATCA/CRS/shareholder-reporting screen, investor
no-guarantee QSBS/credit disclosure, secondary-transfer/tender/lock-up/1045/1202 exit screen,
dynasty trust/investment LLC/direct-ownership carve-out memo, and exit/1045/1202 liquidity memo.
The QSBS source-refresh item must capture IRC §§ 1202 and 1045, current Treasury/IRS guidance,
and the 2023 California Lawyers Association Taxation Section paper, "Proposed Revenue Procedure
to Standardize the Information Corporations Give Shareholders to Show That Stock is QSBS." The
certificate workpaper must address issuer status, original issue, gross assets, controlled-group/
subsidiary look-through, active-business use, redemption taint, shareholder-side facts, §1045
rollover timing, §1202 limits, direct versus trust/pass-through/IRA ownership, M&A preservation,
officer records, counsel review, negative or qualified answers, and penalty/reasonable-cause
posture.
The generated packet must classify every item in `capital_raise_required` as complete,
rejected, or not applicable with rationale before investor-facing use, and every item in
`investor_required` as complete, rejected, or not applicable with rationale before any investor
onboarding, subscription, tax reporting promise, side letter, update, secondary transfer, or
complaint response is used. It must classify every item in `qsbs_required` as complete, rejected,
or not applicable with rationale before any QSBS certificate, investor tax statement, §1045
rollover recommendation, §1202 exclusion analysis, founder trust/direct-ownership memo, or exit
tax estimate is used. It must classify every item in `entity_topology_required` as complete,
rejected, or not applicable with rationale before funding a dynasty/investment trust, investment
LLC, direct trust-owned asset lane, founder/QSBS stock transfer, 83(b) share transfer, S-corp
share transfer, insurance transfer, retirement-asset routing, or issuer-restricted private
security transfer. It must classify every item in `source_ingest_required` before using local TAX
CREDIT, LLC, SEC, irrevocable-trust, QSBS, credit, offering, or investor-publication source
material in any QSBS certificate, capital-raise disclosure, investor tax statement, trust/LLC
topology memo, tax-credit model, or founder sheltering recommendation.

## Lane 3A: Founder Governance And Consent Rights

Use this lane when the founder wants a Delaware control architecture built around contractual
consent rights over extraordinary corporate actions. It is a governance implementation lane,
not a blanket claim that the founder controls ordinary operations or can replace the board's
fiduciary judgment.

| Workstream | Lead seats | Required outputs |
|---|---|---|
| Authority refresh | `glaw-legal-research`, `glaw-corporate-counsel` | current-law ledger for DGCL §§141(a), 122(18), and 218; Moelis decision/post-enactment treatment; certificate/bylaws consistency review |
| Control-stack architecture | `glaw-corporate-counsel`, `glaw-elite-corporate-counsel` | certificate + bylaws + Founder Rights Agreement + Voting Agreement responsibility map |
| Reserved matters | `glaw-corporate-counsel`, `glaw-pe-vc-counsel` | board/committee/founder consent matrix with thresholds, direct/indirect coverage, notice, response, and evidence fields |
| Board and committees | `glaw-corporate-counsel`, `glaw-sec-disclosure` | nomination, replacement, board-size, removal, committee, independence, and exchange-compatibility schedule |
| Adversarial and implementation gate | `glaw-adversarial`, `glaw-tax-strategy` | control-risk, fiduciary-duty, investor, disclosure, tax, valuation, anti-circumvention, sunset, and Delaware-counsel review |

The lane must expressly separate: (1) board authority and director fiduciary duties; (2) the
founder's capacity as stockholder or beneficial owner; and (3) the corporation's contractual
promise not to take listed actions without the required consent. The reserved-matters schedule
should cover corporate structure, equity, extraordinary transactions, debt/financing, board
composition, material IP/subsidiary actions, bankruptcy, amendment/waiver/termination, and
anti-circumvention. Thresholds, aggregation, ownership-based sunset tiers, change-of-control
treatment, emergency mechanics, and record retention must be explicit.

Lane-specific packet items: authority ledger; control-stack diagram; Founder Rights Agreement
issue list; reserved-matters matrix; board/committee rights schedule; transaction, financing,
equity, IP, subsidiary, litigation, and bankruptcy controls; anti-circumvention and sunset
schedule; consent notice/response protocol; control-risk memo; implementation checklist; and
governance docket. Every legal conclusion remains subject to current-source verification and
Delaware counsel review before adoption, enforcement, financing, IPO, or reliance.

## Lane 3B: Founder Control Stack — Dual-Class, Charter, Contract, And Capital Math

Attach this cross-strategy lane when the objective is durable founder control after outside
investment. It intersects corp-build, VC/PE, fund, tax, accounting, enterprise/SEC, and UHNW
work; it does not replace those lanes.

| Control surface | Primary document/workpaper | Required review |
|---|---|---|
| Class A/B/C powers, votes, conversion, separate-class protections | Certificate of incorporation | Delaware corporate, securities, tax, and investor counsel |
| Meetings, notice, quorum, committees, and procedures | Bylaws | Corporate counsel and governance reviewer |
| Issuance, financing, equity plan, and consent record | Board/stockholder resolutions | Corporate, PE/VC, fund, and capitalization reviewers |
| Reserved matters, founder consent, information, anti-circumvention | §122(18) Founder Rights Agreement | Delaware counsel, investor counsel, adversarial reviewer |
| Director elections and nominee obligations | §218 Voting Agreement | Corporate, investor, fiduciary, and disclosure reviewers |
| Transfers, automatic conversion, succession, trusts, and estate vehicles | Charter schedules and transfer/succession workpapers | Corporate, tax, estate/trust, and securities counsel |
| Votes, dilution, conversion, ASC 718, valuation, and beneficial ownership | Cap table, vote ledger, accounting-control packet | CPA, auditor, valuation, tax, and SEC reviewers |

The lane must model economic ownership separately from voting power for each financing round,
option-pool increase, SAFE/note conversion, preferred conversion, PE investment, and prohibited
transfer. It must distinguish super-voting stock, supermajority thresholds, Class B separate
votes, board designation, and §122(18) consent rights. Any ratio such as 10:1 or 20:1 is an
illustrative sensitivity case, not a default recommendation.

## Lane 4: UHNW And Family Office Overlay

Apply this overlay to any enterprise owner, founder, investor, or executive with estate,
asset-protection, philanthropic, or succession goals.

| Workstream | Lead seats | Required outputs |
|---|---|---|
| Estate and trust design | `/glaw-estate-trusts`, `glaw-tax-strategy` | trust taxonomy table, revocable/irrevocable distinction, grantor/non-grantor/simple/complex/domestic/foreign status, trustee and situs memo |
| Asset protection | `/glaw-asset-protection`, `glaw-elite-corporate-counsel` | solvency certificate, creditor/fraudulent-transfer screen, insurance/exempt-asset inventory |
| Gift, GST, and estate tax | `/glaw-estate-gift-returns`, `glaw-tax-strategy` | 709/706/GST allocation calendar, valuation/appraisal tie-out, DSUE/portability analysis |
| Investment governance | `glaw-tax-strategy`, `glaw-institutional-finance`, `/glaw-accounting` | investment LLC governance, IPS, capital-call and distribution controls, K-1/reporting calendar |
| Philanthropy | `/glaw-exempt-org`, `glaw-tax-strategy` | DAF/foundation/CRT/CLT comparison, private-foundation excise-tax screen, charitable substantiation |
| Fiduciary administration | `/glaw-estate-trusts`, `/glaw-accounting`, `glaw-tax-strategy` | trustee/executor fiduciary-risk workpaper, tax/payment order, recordkeeping cadence, co-trustee deadlock plan |
| Family governance and special situations | `/glaw-estate-trusts`, `/glaw-asset-protection`, `glaw-tax-strategy` | family mission/equal-equitable memo, special-needs/conservatorship branch, beneficiary-readiness and difficult-asset plan |

Lane-specific packet items: trust taxonomy and administration matrix; a classification memo
covering revocable living, A-B/bypass/credit-shelter, testamentary, irrevocable gift,
dynasty/GST, IDGT, GRAT/GRUT, QPRT, SLAT, ILIT, CRT/CRAT/CRUT/NIMCRUT, CLT/CLAT/CLUT,
DAPT, offshore APT, DING/NING/ING, discretionary/spendthrift, special-needs, QSST/ESBT,
land trust, Delaware statutory trust/DST, business/statutory trust, investment/fixed
investment trust, rabbi/secular, qualified-plan/IRA custodial, purpose, blind, and
constructive/resulting trust categories; situs/trustee/beneficiary/distribution memo;
Form 709/706/GST calendar; investment LLC governance and IPS; solvency/fraudulent-transfer
screen; direct-ownership carve-out analysis for founder restricted stock/83(b), QSBS/§1202,
S-corp stock, life insurance, retirement assets, and issuer-restricted private securities; and
charitable substantiation plan. Schwab Learn trust topic coverage is a benchmark refresh item:
the packet must record a dated source update note from
`https://www.schwab.com/learn/topic/trusts`, capture the current topic-index coverage for
estate-tax uncertainty, SLAT, dynasty trust, ILIT/IRA funding, equal-versus-equitable
distributions, discretionary trust planning, state tax, trust-fit, loss-driven administration,
and trust account setup, and address trustee/executor fiduciary risk, special-needs/
conservatorship/incapacity planning, family mission statements, equal-versus-equitable
distributions, and beneficiary readiness where facts trigger those lanes. The Schwab benchmark
workpaper must classify every item in `schwab_trust_topic_required` as complete, rejected, or not
applicable with the source date before GLAW says the trust lane reflects current public-market
trust-planning questions. The generated packet must classify every trust type in
`trust_taxonomy_required` as selected, rejected, or not applicable with rationale before the UHNW
lane can be marked complete. It must classify every item in `entity_topology_required` before any trust-owned investment LLC,
direct trust-owned asset lane, founder stock, QSBS, S-corp stock, insurance, retirement asset,
issuer-restricted security, diversified investment pool, or family investment governance plan is
treated as implementation-ready.

## Firm-Level Flow

1. Classify the matter by lane and track: enterprise, tax, entrepreneur/founder,
   founder-governance/consent-rights, UHNW overlay,
   litigation, investigation, or hybrid.
2. Open the matter and clear conflicts before any substantive recommendation.
3. Build a source evidence manifest: documents, websites, statutes, figures, financial data,
   cap table, accounting records, and client-provided assumptions.
4. Classify the integrated advisory benchmark: whole-client inventory, lane routing, source
   refresh, handoff triggers, deliverables, accounting/CFO dashboard, recurring review, and
   IRS/SEC/creditor/fiduciary/valuation/investor/adversarial review.
5. Assign one lead seat and named reviewers from tax, corporate, finance/accounting, securities,
   litigation, and private-client as needed.
6. Produce a lane-specific deliverables index before drafting the documents.
7. Run RED to BLUE review from all regulators or opponents who can break the plan.
8. Record Chief/Council approval only after current artifacts, citations, figures, source evidence,
   UPL footer, report quality, reviewer identity, and docket gates are fresh.
9. Docket every recurring obligation: filing deadlines, annual reports, Form D amendments, Blue Sky,
   83(b), 409A refresh, tax payments, return due dates, trust administration, and board approvals.

## Required Client-Facing Packet

Every premium-lane matter should produce, at minimum:

- executive decision memo;
- lane map and seat ownership table;
- entity/trust/org chart where relevant;
- tax strategy and compliance calendar;
- investor or board disclosure packet where relevant;
- financial model or accounting tie-out when numbers drive the answer;
- risk matrix with regulator/opponent attack lines;
- implementation checklist with signer, filing, advisor, and deadline owner;
- docket export; and
- explicit attorney/CPA/local-counsel review conditions.

## Hard No-Go Items

Do not recommend or paper:

- hiding beneficial ownership, income, investors, or assets;
- backdating or fabricating board minutes, invoices, assignments, valuations, or elections;
- issuer promises that QSBS, credits, or deductions are guaranteed to any investor;
- transfers made to defeat an existing or foreseeable creditor without solvency and counsel review;
- unregistered securities offerings without a valid exemption and filing plan;
- tax positions with no business purpose or economic substance; or
- any filing, signature, service, live transmission, payment, or binding act without human authority.
