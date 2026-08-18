#!/usr/bin/env bash
# premium_lane_cli_test.sh - premium lane command emits actionable lane packets.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$HERE/.."
TMP="$(mktemp -d)"
source "$HERE/premium_source_fixture.sh"
setup_premium_source_fixture "$TMP"
pass=0; fail=0
ok(){ if [ "$1" = 1 ]; then pass=$((pass+1)); echo "  ✓ $2"; else fail=$((fail+1)); echo "  ✗ FAIL: $2"; fi; }

CMD="$ROOT/bin/glaw-premium-lanes"

"$CMD" validate --json > "$TMP/validate.json"; rc=$?
python3 - "$TMP/validate.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ok=(data.get("status") == "pass" and data.get("lane_count") == 7 and "work-product" in data.get("authority", ""))
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane manifest validates"

"$CMD" audit-objective --json > "$TMP/objective-audit.json"; rc=$?
python3 - "$TMP/objective-audit.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
rows={row.get("id"): row for row in data.get("requirements", [])}
tools={row.get("path"): row.get("status") for row in data.get("tools", [])}
taxonomy=data.get("trust_taxonomy_summary", {})
carveouts="\n".join(taxonomy.get("direct_ownership_carveouts", []))
blueprint=data.get("founder_blueprint_summary", {})
phases="\n".join(blueprint.get("phase_names", []))
commands="\n".join(blueprint.get("kickoff_commands", []))
tax_blueprint=data.get("tax_engine_blueprint_summary", {})
tax_phases="\n".join(tax_blueprint.get("phase_names", []))
tax_commands="\n".join(tax_blueprint.get("kickoff_commands", []))
enterprise_blueprint=data.get("enterprise_blueprint_summary", {})
enterprise_phases="\n".join(enterprise_blueprint.get("phase_names", []))
enterprise_commands="\n".join(enterprise_blueprint.get("kickoff_commands", []))
firm_blueprint=data.get("firm_blueprint_summary", {})
firm_phases="\n".join(firm_blueprint.get("phase_names", []))
firm_commands="\n".join(firm_blueprint.get("kickoff_commands", []))
source_ingest=data.get("local_source_ingest_summary", {})
source_rows=source_ingest.get("sources", [])
source_paths="\n".join(str(row.get("path", "")) for row in source_rows if isinstance(row, dict))
ok=(
    data.get("status") == "pass"
    and data.get("manifest_status") == "pass"
    and data.get("trust_taxonomy_status") == "pass"
    and data.get("founder_blueprint_status") == "pass"
    and data.get("tax_engine_blueprint_status") == "pass"
    and data.get("enterprise_blueprint_status") == "pass"
    and data.get("firm_blueprint_status") == "pass"
    and data.get("local_source_ingest_status") == "pass"
    and taxonomy.get("trust_type_count") == 38
    and taxonomy.get("required_type_count") == 38
    and taxonomy.get("direct_ownership_carveout_count", 0) >= 6
    and "QSBS" in carveouts
    and "S-corp" in carveouts
    and "retirement" in carveouts.lower()
    and "Schwab" in str(taxonomy.get("schwab_benchmark", {}))
    and blueprint.get("phase_count") == 6
    and blueprint.get("trust_type_count") == 38
    and blueprint.get("direct_ownership_carveout_count", 0) >= 6
    and "founder-unicorn" in blueprint.get("lanes", [])
    and "tax-system" in blueprint.get("lanes", [])
    and "uhnw-family-office" in blueprint.get("lanes", [])
    and "Raise money legally" in phases
    and "Investor tax and onboarding package" in phases
    and "Shelter and family-office topology" in phases
    and "bin/glaw-premium-lanes attach founder-unicorn" in commands
    and tax_blueprint.get("phase_count") == 7
    and tax_blueprint.get("tax_engine_item_count") >= 15
    and tax_blueprint.get("tax_credit_item_count") >= 14
    and tax_blueprint.get("source_ingest_item_count") >= 12
    and "tax-system" in tax_blueprint.get("lanes", [])
    and "Accounting-to-tax bridge" in tax_phases
    and "Credits, incentives, substantiation, transferability, and recapture" in tax_phases
    and "SALT, international, information returns, and withholding" in tax_phases
    and "Compliance, controversy, filing handoff, and no-live-filing authority" in tax_phases
    and "bin/glaw-premium-lanes attach tax-system" in tax_commands
    and enterprise_blueprint.get("phase_count") == 8
    and enterprise_blueprint.get("enterprise_item_count") >= 14
    and enterprise_blueprint.get("creative_planning_item_count") >= 15
    and "fortune500-enterprise" in enterprise_blueprint.get("lanes", [])
    and "tax-system" in enterprise_blueprint.get("lanes", [])
    and "SEC disclosure, capital markets, investor relations, and Reg FD" in enterprise_phases
    and "Audit, SOX, ICFR, PCAOB, close, and accounting controls" in enterprise_phases
    and "Enterprise tax, ASC 740, SALT, international, and tax provision" in enterprise_phases
    and "Regulatory, enforcement, investigations, litigation hold, and evidence timeline" in enterprise_phases
    and "bin/glaw-premium-lanes attach fortune500-enterprise" in enterprise_commands
    and firm_blueprint.get("phase_count") == 10
    and firm_blueprint.get("source_count") == 6
    and firm_blueprint.get("trust_type_count") == 38
    and "fortune500-enterprise" in firm_blueprint.get("lanes", [])
    and "tax-system" in firm_blueprint.get("lanes", [])
    and "founder-unicorn" in firm_blueprint.get("lanes", [])
    and "uhnw-family-office" in firm_blueprint.get("lanes", [])
    and "Fortune 500 enterprise bench" in firm_phases
    and "Tax system and IRS engine" in firm_phases
    and "Entrepreneur, founder, QSBS, and capital raise" in firm_phases
    and "Investor tax, onboarding, and reporting promises" in firm_phases
    and "Trust, investment LLC, asset shelter, and direct ownership carve-outs" in firm_phases
    and "RED to BLUE adversarial review and Chief decision" in firm_phases
    and "bin/glaw-premium-lanes materialize-source-ingest --json" in firm_commands
    and "bin/glaw-premium-lanes attach uhnw-family-office" in firm_commands
    and source_ingest.get("source_count") == 6
    and source_ingest.get("required_source_count") == 6
    and source_ingest.get("extracted_char_count", 0) > 1000
    and source_ingest.get("extractor") == "pdftotext"
    and all(isinstance(row.get("sha256"), str) and len(row.get("sha256")) == 64 for row in source_rows if isinstance(row, dict))
    and all(row.get("extraction_status") == "pass" for row in source_rows if isinstance(row, dict))
    and all(isinstance(row.get("extracted_sha256"), str) and len(row.get("extracted_sha256")) == 64 for row in source_rows if isinstance(row, dict))
    and "TAX CREDIT/F_PUB_550.pdf" in source_paths
    and "LLC/FormCandOS.pdf" in source_paths
    and "SEC/id257bpm.pdf" in source_paths
    and isinstance(data.get("manifest_sha256"), str)
    and len(data.get("manifest_sha256", "")) == 64
    and rows.get("fortune500_lawyer", {}).get("status") == "pass"
    and rows.get("tax_system", {}).get("status") == "pass"
    and rows.get("entrepreneur_founder_unicorn", {}).get("status") == "pass"
    and rows.get("investor_raise", {}).get("status") == "pass"
    and rows.get("trust_asset_shelter", {}).get("status") == "pass"
    and "fortune500-tax-entrepreneur.md" in "\n".join(rows.get("fortune500_lawyer", {}).get("evidence", []))
    and "source-ingest-tax-credit-llc-sec.md" in "\n".join(rows.get("tax_system", {}).get("evidence", []))
    and "founder-unicorn-tax-capital-playbook.md" in "\n".join(rows.get("entrepreneur_founder_unicorn", {}).get("evidence", []))
    and "glaw-pe-vc-counsel/SKILL.md" in "\n".join(rows.get("investor_raise", {}).get("evidence", []))
    and "schwab-trusts-benchmark.md" in "\n".join(rows.get("trust_asset_shelter", {}).get("evidence", []))
    and tools.get("bin/glaw-intake") == "pass"
    and tools.get("bin/glaw-final-packet") == "pass"
    and tools.get("lib/glaw_premium_scope.py") == "pass"
    and not data.get("failures")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane objective audit proves Fortune 500, tax, founder, investor, QSBS, and trust surfaces"

"$CMD" trust-taxonomy --json > "$TMP/trust-taxonomy.json"; rc=$?
python3 - "$TMP/trust-taxonomy.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
types={row.get("type"): row for row in data.get("trust_types", [])}
carveouts="\n".join(data.get("direct_ownership_carveouts", []))
topics="\n".join(data.get("schwab_benchmark", {}).get("required_topics", []))
ok=(
    data.get("status") == "pass"
    and data.get("trust_type_count") == 38
    and data.get("required_type_count") == 38
    and data.get("source") == "seats/glaw-tax-strategy/references/trust-taxonomy-routing.md"
    and "Revocable living trust" in types
    and "Irrevocable gift trust" in types
    and "Dynasty / GST trust" in types
    and "IDGT" in types
    and "GRAT" in types
    and "GRUT" in types
    and "QPRT" in types
    and "SLAT" in types
    and "ILIT" in types
    and "CRT / CRAT / CRUT / NIMCRUT" in types
    and "CLT / CLAT / CLUT" in types
    and "Charitable trust / private foundation-adjacent trust" in types
    and "DAPT" in types
    and "Offshore APT" in types
    and "DING / NING / ING" in types
    and "Spendthrift trust" in types
    and "Discretionary trust" in types
    and "Special needs trust - first-party / d4A" in types
    and "Pooled special needs trust / d4C" in types
    and "Medicaid income trust / Miller trust / QIT" in types
    and "QSST" in types
    and "ESBT" in types
    and "Voting trust" in types
    and "Delaware statutory trust / DST" in types
    and "Business trust / Massachusetts trust" in types
    and "Investment trust / fixed investment trust" in types
    and "Rabbi trust" in types
    and "Secular trust" in types
    and "Qualified plan trust" in types
    and "IRA / custodial trust" in types
    and "Totten / payable-on-death trust" in types
    and "Constructive / resulting trust" in types
    and "Blind trust" in types
    and "Purpose trust / pet trust / gun trust" in types
    and "Grantor, ignored for income tax during life." == types["Revocable living trust"].get("tax_posture")
    and "glaw-tax-strategy" in types["QSST"].get("routing", [])
    and "glaw-qualified-plan" in types["Qualified plan trust"].get("routing", [])
    and "irrevocable dynasty or investment trust owns an investment LLC" in data.get("default_topology", {}).get("chassis", "")
    and "QSBS section 1202 carve-out" in carveouts
    and "S-corp stock carve-out" in carveouts
    and "retirement-asset carve-out" in carveouts
    and "issuer-restricted private securities carve-out" in carveouts
    and "Schwab 2026 topic-index capture" in topics
    and "page-level source drift control" in topics
    and not data.get("failures")
    and "licensed counsel" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane trust-taxonomy exposes all trust types, topology, Schwab benchmark, and carve-outs"

"$CMD" source-ingest-audit --json > "$TMP/source-ingest-audit.json"; rc=$?
python3 - "$TMP/source-ingest-audit.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
rows=data.get("sources", [])
by_id={row.get("id"): row for row in rows if isinstance(row, dict)}
ok=(
    data.get("status") == "pass"
    and data.get("source_count") == 6
    and data.get("required_source_count") == 6
    and data.get("extractor") == "pdftotext"
    and data.get("extracted_char_count", 0) > 1000
    and set(by_id) == {
        "tax-base-options",
        "irrevocable-trust-types",
        "fy2026-tax-expenditures",
        "pub-550-investment-income",
        "llc-form-c-offering",
        "sec-delinquent-reporting",
    }
    and all(row.get("exists") is True for row in rows)
    and all(row.get("source_ingest_term_present") is True for row in rows)
    and all(isinstance(row.get("sha256"), str) and len(row.get("sha256")) == 64 for row in rows)
    and all(row.get("size_bytes", 0) > 0 for row in rows)
    and all(row.get("extraction_status") == "pass" for row in rows)
    and all(row.get("extracted_chars", 0) > 0 for row in rows)
    and all(isinstance(row.get("extracted_sha256"), str) and len(row.get("extracted_sha256")) == 64 for row in rows)
    and by_id["tax-base-options"].get("lane") == "tax-system"
    and by_id["llc-form-c-offering"].get("lane") == "founder-unicorn"
    and by_id["sec-delinquent-reporting"].get("lane") == "fortune500-enterprise"
    and not data.get("failures")
    and "file presence" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "source-ingest audit proves local TAX CREDIT, LLC, and SEC files with source and extracted-text hashes"

"$CMD" source-ingest-audit > "$TMP/source-ingest-audit.txt"; rc=$?
grep -q "LOCAL SOURCE INGEST: pass" "$TMP/source-ingest-audit.txt"; rc2=$?
grep -q "tax-base-options" "$TMP/source-ingest-audit.txt"; rc3=$?
grep -q "sec-delinquent-reporting" "$TMP/source-ingest-audit.txt"; rc4=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && echo 1 || echo 0)" "source-ingest audit renders readable operator summary"

mkdir -p "$TMP/glaw/matters/source-ledger-matter"
printf 'source-ledger-matter\n' > "$TMP/glaw/.active"
GLAW_HOME="$TMP/glaw" "$CMD" materialize-source-ingest --json > "$TMP/materialize-source-ingest.json"; rc=$?
python3 - "$TMP/materialize-source-ingest.json" "$TMP/glaw/matters/source-ledger-matter" <<'PY'
import hashlib, json, pathlib, sys
data=json.load(open(sys.argv[1]))
matter=pathlib.Path(sys.argv[2])
json_path=matter/"sources/local-source-ingest-ledger.json"
md_path=matter/"sources/local-source-ingest-ledger.md"
ledger=json.load(open(json_path)) if json_path.is_file() else {}
rows=ledger.get("sources", [])
ok=(
    data.get("status") == "pass"
    and data.get("matter_slug") == "source-ledger-matter"
    and json_path.is_file()
    and md_path.is_file()
    and data.get("json_sha256") == hashlib.sha256(json_path.read_bytes()).hexdigest()
    and data.get("markdown_sha256") == hashlib.sha256(md_path.read_bytes()).hexdigest()
    and ledger.get("source_count") == 6
    and ledger.get("required_source_count") == 6
    and ledger.get("extracted_char_count", 0) > 1000
    and len(rows) == 6
    and all(str(row.get("source_row_id", "")).startswith("LSI-") for row in rows)
    and all(row.get("extraction_status") == "pass" for row in rows)
    and "tax-base-options" in md_path.read_text()
    and "sec-delinquent-reporting" in md_path.read_text()
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "materialize-source-ingest writes hashed matter source ledger artifacts"

"$CMD" list > "$TMP/list.txt"; rc=$?
grep -q $'fortune500-enterprise\tFortune 500 Enterprise Counsel' "$TMP/list.txt"; rc2=$?
grep -q $'founder-unicorn\tEntrepreneur, Founder, And Unicorn Advisor' "$TMP/list.txt"; rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "premium lane list includes enterprise and founder lanes"

"$CMD" show tax-system --json > "$TMP/tax.json"; rc=$?
python3 - "$TMP/tax.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
packet=set(data.get("required_lane_packet", []))
tax_engine=set(data.get("tax_engine_required", []))
tax_credit=set(data.get("tax_credit_required", []))
source_ingest=set(data.get("source_ingest_required", []))
creative=set(data.get("creative_planning_required", []))
ok=(
    data.get("lane_id") == "tax-system"
    and "glaw-tax-strategy" in data.get("lead_seats", [])
    and "/glaw-tax-court" in data.get("lead_seats", [])
    and "Accounting to tax" in data.get("workstreams", [])
    and "primary-law citation corpus freshness report" in packet
    and "return-position authority, Form 8275/8275-R disclosure, and penalty-defense memo" in packet
    and "IRS notice, transcript, statute-of-limitations, and response-deadline ledger" in packet
    and "tax-credit eligibility, substantiation, computation, transferability, recapture, and forms packet" in packet
    and "source evidence intake: taxpayer profile, entity chart, source-file index, missing-information list, and document hashes" in tax_engine
    and "GL trial-balance tie-out, book-to-tax M-1/M-3 bridge, return-line map, and control manifest" in tax_engine
    and "international information-return, FBAR/FATCA, Form 8938, 5471, 5472, 8865, 8858, GILTI, Subpart F, FDII, BEAT, 962, withholding, and treaty screen" in tax_engine
    and "return/payment/e-file/transmitter/MeF/IRIS/SSA BSO handoff and no-live-filing authority check" in tax_engine
    and "tax-credit source refresh: IRC sections, Treasury/IRS notices, forms, instructions, current-year inflation figures, state credit guidance, and expiration/phaseout/effective-date ledger" in tax_credit
    and "R&D substantiation: business component, permitted purpose, technological uncertainty, process of experimentation, qualified research expenses, wage/supply/contract allocation, section 174/174A capitalization, and payroll-credit election support" in tax_credit
    and "energy and IRA credit substantiation: prevailing wage/apprenticeship, domestic content, energy community, low-income community, beginning-of-construction, placed-in-service, transfer election, direct pay, registration number, and recapture monitoring" in tax_credit
    and "forms and filing package: Form 3800, 6765, 3468, 8835, 8911, 8933, 8974, 8994/8995 where relevant, Form 8275/8275-R disclosure, state credit forms, and e-file/transmitter/MeF handoff owner" in tax_credit
    and "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/Options to Broaden the US Tax Base (May 2024 Update).pdf mapped to QSBS, trusts, grantor trusts, multiple-trust stacking, partnership/entity basis, PPLI/PPA, trust reporting proposals, and IRS anti-abuse review" in source_ingest
    and "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/what-are-the-different-types-of-irrevocable-trusts.pdf mapped to irrevocable trust administration, grantor-trust income-tax posture, GRAT, QPRT, irrevocable gift trust, ILIT, and trustee focus" in source_ingest
    and "local source inventory: /Users/ricardoprieto/Desktop/SEC/id257bpm.pdf mapped to SEC delinquent-reporting enforcement, investor-protection rationale, public-reporting consequences, adversarial SEC lens, and investor communications controls" in source_ingest
    and "output traceability: every QSBS certificate, tax-credit claim, investor tax statement, offering disclosure, trust/LLC topology memo, and tax-return position cites the source-ingest row or marks the source not applicable with rationale" in source_ingest
    and "Creative Planning public-site benchmark source refresh: https://creativeplanning.com/sitemap/, family office, wealth management, tax planning, business services, M&A/exit, risk/insurance, international, and specialty-service pages dated before use" in creative
    and "whole-client inventory: household, income, balance sheet, investments, trusts, business entities, real estate, retirement assets, insurance, debt, private fund interests, crypto/digital assets, advisors, goals, and jurisdiction facts" in creative
    and "tax-planning and compliance lane: current figures, return posture, entity tax, credits, SALT, international, estimated tax, controversy, authority freshness, and CPA/preparer handoff" in creative
    and "integrated deliverables: source/evidence binder, lane map, seat ownership table, entity/trust/org chart, tax roadmap, investor/board packet, estate/trust plan, asset-protection plan, compliance calendar, dashboard, and recurring review schedule" in creative
    and "benchmark boundary: Creative Planning materials are used only as a public-market service taxonomy and intake-flow benchmark; GLAW must not copy branding, claims, client counts, awards, product language, or substitute benchmark pages for licensed legal/tax/investment advice" in creative
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "tax-system lane show exposes tax bench and return-position controls"

"$CMD" playbook founder-unicorn --matter "Acme Founder Raise" --json > "$TMP/playbook-founder.json"; rc=$?
python3 - "$TMP/playbook-founder.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
commands="\n".join(data.get("kickoff_commands", []))
required={row.get("item") for row in data.get("required_packet", [])}
capital_raise={row.get("item") for row in data.get("capital_raise_required", [])}
investor_required={row.get("item") for row in data.get("investor_required", [])}
qsbs_required={row.get("item") for row in data.get("qsbs_required", [])}
source_ingest={row.get("item") for row in data.get("source_ingest_required", [])}
creative={row.get("item") for row in data.get("creative_planning_required", [])}
reviewers={row.get("reviewer") for row in data.get("adversarial_reviewers", [])}
ok=(
    data.get("lane_id") == "founder-unicorn"
    and data.get("matter") == "Acme Founder Raise"
    and "bin/glaw-premium-lanes attach founder-unicorn" in commands
    and "bin/glaw-premium-lanes complete --lane founder-unicorn" in commands
    and "bin/glaw-premium-lanes render-packet --lane founder-unicorn" in commands
    and "bin/glaw-premium-lanes check-packet --lane founder-unicorn" in commands
    and "bin/glaw-premium-lanes docket --lane founder-unicorn" in commands
    and "workpapers/premium-lane-founder-unicorn.json" not in commands
    and "<YYYY-MM-DD>" not in commands
    and "<basis>" not in commands
    and "--due YYYY-MM-DD" in commands
    and "--source \"SRC-0001 basis\"" in commands
    and "investor tax disclosure, withholding, K-1/1099/1042-S/FATCA/CRS, and no-guarantee QSBS statement" in required
    and "capital raise exemption, Form D, Blue Sky, KYC, and investor-suitability plan" in required
    and "exemption selection: Reg D 506(b), Reg D 506(c), Reg CF, Reg A, Reg S, intrastate, or registered offering" in capital_raise
    and "investor KYC/AML/OFAC/source-of-funds review" in capital_raise
    and "broker-dealer, finder, referral-fee, and transaction-compensation analysis" in capital_raise
    and "tax-exempt/foreign investor blocker, withholding, UBIT/ECI, and K-1/1099/shareholder-reporting screen" in capital_raise
    and "investor persona and capacity map: individual, entity, trust, IRA/qualified plan, family office, fund, strategic, tax-exempt, foreign, and nominee/beneficial-owner screen" in investor_required
    and "subscription agreement, investor questionnaire, W-9/W-8, entity authority, trust/IRA custodian authority, and signature authority package" in investor_required
    and "tax reporting profile: K-1/1099/1042-S/1099-B/Form 3921/3922/shareholder statement, withholding, FATCA/CRS, UBIT, ECI, PFIC/CFC, and state tax screen" in investor_required
    and "communications controls: investor updates, projections, performance claims, testimonials, selective disclosure, Reg FD where relevant, marketing archive, and version control" in investor_required
    and "QSBS source refresh: IRC section 1202, section 1045, Treasury/IRS current guidance, and 2023 CLA Proposed Revenue Procedure to Standardize the Information Corporations Give Shareholders to Show That Stock is QSBS" in qsbs_required
    and "qualified-small-business gross-assets test: cash, adjusted basis, contributed-property FMV, immediate pre/post-issuance aggregate gross assets, $50 million threshold, and supporting balance-sheet/valuation workpapers" in qsbs_required
    and "QSBS corporation certificate: officer-signed factual certificate, counsel-reviewed legal issue list, record-retention covenant, statement of unsupported assertions, negative/qualified responses, and notice if records cannot support a favorable answer" in qsbs_required
    and "local source inventory: /Users/ricardoprieto/Desktop/LLC/FormCandOS.pdf mapped to Reg CF offering statement, LLC agreement, risk factors, investor acknowledgments, subscription mechanics, transfer restrictions, series LLC governance, beneficial ownership, and issuer/investor tax disclaimers" in source_ingest
    and "source-backed no-go screen: tax shelters, reportable transactions, promoted credit claims, PPLI/PPA, multiple-trust stacking, grantor-trust freezes, backdating, sham entities, and guaranteed QSBS/credit claims receive IRS/SEC/adversarial review before use" in source_ingest
    and "business-owner and founder lane: entity/org chart, governance, cap table, QSBS, 83(b), 409A, tax credits, capital raise, M&A/exit, succession, payroll, accounting, insurance, and technology/legal operations" in creative
    and "investor and capital lane: securities exemption, investor eligibility, KYC/AML/OFAC/source-of-funds, subscription documents, risk factors, tax statements, data room, communications controls, and post-close reporting" in creative
    and "integrated handoff rules: founder stock/QSBS, trusts plus concentrated stock, business exit/succession, credits in investor materials, UHNW multi-entity families, and international facts each trigger the required secondary lanes" in creative
    and "adversarial benchmark review: IRS, SEC, creditor/fraudulent-transfer counsel, fiduciary/trustee reviewer, valuation/appraiser, auditor/PCAOB where relevant, investor counsel, privacy/security, and Chief Compliance Officer pass before release" in creative
    and "IRS QSBS examiner" in reviewers
    and "SEC offering reviewer" in reviewers
    and "unregistered securities offerings" in "\n".join(data.get("hard_no_go", []))
    and "does not give legal" in data.get("authority", "")
    and "Chief/Council approved" in data.get("gate_sequence", [])
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "founder playbook exposes kickoff commands, investor/QSBS packet, reviewers, and no-go controls"

"$CMD" founder-blueprint --matter "Acme Founder Raise" --json > "$TMP/founder-blueprint.json"; rc=$?
python3 - "$TMP/founder-blueprint.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
commands="\n".join(data.get("kickoff_commands", []))
phases={row.get("phase"): row for row in data.get("sequence", [])}
raise_required="\n".join(phases.get("3. Raise money legally", {}).get("required", []))
investor_required="\n".join(phases.get("4. Investor tax and onboarding package", {}).get("required", []))
qsbs_required="\n".join(phases.get("2. Formation, founder stock, and QSBS", {}).get("required", []))
shelter_required="\n".join(phases.get("5. Shelter and family-office topology", {}).get("required", []))
carveouts="\n".join(data.get("trust_taxonomy", {}).get("direct_ownership_carveouts", []))
reviewers="\n".join(data.get("adversarial_reviewers", []))
source_ingest="\n".join(data.get("source_ingest_required", []))
ok=(
    data.get("status") == "pass"
    and data.get("matter") == "Acme Founder Raise"
    and data.get("lanes") == ["founder-unicorn", "tax-system", "uhnw-family-office"]
    and "bin/glaw-intake premium founder-unicorn tax-system uhnw-family-office" in commands
    and "bin/glaw-premium-lanes attach founder-unicorn" in commands
    and "bin/glaw-final-packet build --profile auto" in commands
    and "exemption selection: Reg D 506(b), Reg D 506(c), Reg CF, Reg A, Reg S, intrastate, or registered offering" in raise_required
    and "broker-dealer, finder, referral-fee, and transaction-compensation analysis" in raise_required
    and "PPM/OM/Form C/Form 1-A disclosure stack" in raise_required
    and "investor persona and capacity map" in investor_required
    and "KYC, AML, OFAC, sanctions" in investor_required
    and "tax reporting profile: K-1/1099/1042-S" in investor_required
    and "QSBS source refresh: IRC section 1202" in qsbs_required
    and "QSBS corporation certificate" in qsbs_required
    and "direct trust-owned asset lane" in shelter_required
    and "investment LLC governance" in shelter_required
    and data.get("trust_taxonomy", {}).get("trust_type_count") == 38
    and data.get("trust_taxonomy", {}).get("required_type_count") == 38
    and "QSBS section 1202 carve-out" in carveouts
    and "founder restricted stock and 83(b) carve-out" in carveouts
    and "S-corp stock carve-out" in carveouts
    and "life-insurance carve-out" in carveouts
    and "retirement-asset carve-out" in carveouts
    and "issuer-restricted private securities carve-out" in carveouts
    and "SEC offering reviewer" in reviewers
    and "IRS QSBS examiner" in reviewers
    and "trustee fiduciary reviewer" in reviewers
    and "local source inventory: /Users/ricardoprieto/Desktop/LLC/FormCandOS.pdf" in source_ingest
    and "source-backed no-go screen" in source_ingest
    and any("unregistered securities offerings" in item for item in data.get("hard_no_go", []))
    and "does not offer securities" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "founder blueprint gives one operator flow for raise, investor package, QSBS, and sheltering"

"$CMD" founder-blueprint --matter "Acme Founder Raise" > "$TMP/founder-blueprint.md"; rc=$?
grep -q "# Founder Capital, Investor, QSBS, and Shelter Blueprint" "$TMP/founder-blueprint.md"; rc2=$?
grep -q "## 3. Raise money legally" "$TMP/founder-blueprint.md"; rc3=$?
grep -q "Direct Ownership Carve-Outs" "$TMP/founder-blueprint.md"; rc4=$?
grep -q "Authority Boundary" "$TMP/founder-blueprint.md"; rc5=$?
grep -q "bin/glaw-premium-lanes attach founder-unicorn" "$TMP/founder-blueprint.md"; rc6=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && [ "$rc5" = 0 ] && [ "$rc6" = 0 ] && echo 1 || echo 0)" "founder blueprint renders Markdown for operator use"

"$CMD" tax-engine-blueprint --matter "Acme Tax Engine" --json > "$TMP/tax-engine-blueprint.json"; rc=$?
python3 - "$TMP/tax-engine-blueprint.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
commands="\n".join(data.get("kickoff_commands", []))
phases={row.get("phase"): row for row in data.get("sequence", [])}
intake_required="\n".join(phases.get("1. Intake, source evidence, current law, and current figures", {}).get("required", []))
entity_required="\n".join(phases.get("2. Entity classification, elections, basis, QSBS, and ownership", {}).get("required", []))
bridge_required="\n".join(phases.get("3. Accounting-to-tax bridge", {}).get("required", []))
credits_required="\n".join(phases.get("4. Credits, incentives, substantiation, transferability, and recapture", {}).get("required", []))
salt_required="\n".join(phases.get("5. SALT, international, information returns, and withholding", {}).get("required", []))
compliance_required="\n".join(phases.get("6. Compliance, controversy, filing handoff, and no-live-filing authority", {}).get("required", []))
wealth_required="\n".join(phases.get("7. Wealth, estate, trust, gift, GST, 1041/DNI, and investor tax overlay", {}).get("required", []))
reviewers="\n".join(data.get("adversarial_reviewers", []))
source_ingest="\n".join(data.get("source_ingest_required", []))
ok=(
    data.get("status") == "pass"
    and data.get("matter") == "Acme Tax Engine"
    and data.get("lanes") == ["tax-system", "founder-unicorn", "uhnw-family-office"]
    and len(data.get("sequence", [])) == 7
    and "bin/glaw-intake premium tax-system" in commands
    and "bin/glaw-premium-lanes attach tax-system" in commands
    and "bin/glaw-premium-lanes complete --lane tax-system" in commands
    and "bin/glaw-premium-lanes render-packet --lane tax-system" in commands
    and "bin/glaw-premium-lanes docket --lane tax-system" in commands
    and "bin/glaw-final-packet build --profile auto" in commands
    and "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/Options to Broaden the US Tax Base" in source_ingest
    and "local source inventory: /Users/ricardoprieto/Desktop/SEC/id257bpm.pdf" in intake_required
    and "section 1202" in entity_required
    and "section 704" in entity_required
    and "section 1368" in entity_required
    and "GL trial-balance tie-out, book-to-tax M-1/M-3 bridge, return-line map" in bridge_required
    and "ASC 740" in bridge_required
    and "Form 3800, 6765" in credits_required
    and "Form 8275/8275-R disclosure" in credits_required
    and "section 6418 transfer" in credits_required
    and "section 6417 direct pay" in credits_required
    and "recapture" in credits_required
    and "SALT nexus" in salt_required
    and "Form 8938, 5471, 5472" in salt_required
    and "GILTI" in salt_required
    and "return-position authority level" in compliance_required
    and "IRS notice, transcript, account module" in compliance_required
    and "no-live-filing authority check" in compliance_required
    and "trust 1041/DNI" in wealth_required
    and "direct trust-owned asset lane" in wealth_required
    and "IRS credit examiner" in reviewers
    and "state credit authority" in reviewers
    and "IRS international examiner" in reviewers
    and "forensic accountant" in reviewers
    and "auditor/PCAOB lens" in reviewers
    and "investor tax counsel" in reviewers
    and any("tax positions with no business purpose or economic substance" in item for item in data.get("hard_no_go", []))
    and "does not give legal, tax, accounting" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "tax-engine blueprint gives one operator flow for GL-to-tax, credits, SALT/international, controversy, and filing handoff"

"$CMD" tax-engine-blueprint --matter "Acme Tax Engine" > "$TMP/tax-engine-blueprint.md"; rc=$?
grep -q "# Tax System, Credits, Compliance, And Controversy Blueprint" "$TMP/tax-engine-blueprint.md"; rc2=$?
grep -q "## 3. Accounting-to-tax bridge" "$TMP/tax-engine-blueprint.md"; rc3=$?
grep -q "Tax Credit Required" "$TMP/tax-engine-blueprint.md"; rc4=$?
grep -q "no-live-filing authority" "$TMP/tax-engine-blueprint.md"; rc5=$?
grep -q "bin/glaw-premium-lanes attach tax-system" "$TMP/tax-engine-blueprint.md"; rc6=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && [ "$rc5" = 0 ] && [ "$rc6" = 0 ] && echo 1 || echo 0)" "tax-engine blueprint renders Markdown for operator use"

"$CMD" enterprise-blueprint --matter "Acme Enterprise" --json > "$TMP/enterprise-blueprint.json"; rc=$?
python3 - "$TMP/enterprise-blueprint.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
commands="\n".join(data.get("kickoff_commands", []))
phases={row.get("phase"): row for row in data.get("sequence", [])}
intake_required="\n".join(phases.get("1. Intake, conflicts, jurisdiction, authority, and enterprise triage", {}).get("required", []))
governance_required="\n".join(phases.get("2. Board governance, subsidiaries, approvals, and entity authority", {}).get("required", []))
sec_required="\n".join(phases.get("3. SEC disclosure, capital markets, investor relations, and Reg FD", {}).get("required", []))
audit_required="\n".join(phases.get("4. Audit, SOX, ICFR, PCAOB, close, and accounting controls", {}).get("required", []))
tax_required="\n".join(phases.get("5. Enterprise tax, ASC 740, SALT, international, and tax provision", {}).get("required", []))
ops_required="\n".join(phases.get("6. M&A, financing, capital markets, contracts, privacy, employment, and operations", {}).get("required", []))
reg_required="\n".join(phases.get("7. Regulatory, enforcement, investigations, litigation hold, and evidence timeline", {}).get("required", []))
signoff_required="\n".join(phases.get("8. Board, auditor, investor, regulator, and Chief sign-off packet", {}).get("required", []))
reviewers="\n".join(data.get("adversarial_reviewers", []))
docket="\n".join(data.get("docket_items", []))
ok=(
    data.get("status") == "pass"
    and data.get("matter") == "Acme Enterprise"
    and data.get("lanes") == ["fortune500-enterprise", "tax-system"]
    and len(data.get("sequence", [])) == 8
    and "bin/glaw-intake premium fortune500-enterprise tax-system" in commands
    and "bin/glaw-premium-lanes attach fortune500-enterprise" in commands
    and "bin/glaw-premium-lanes complete --lane fortune500-enterprise" in commands
    and "bin/glaw-premium-lanes render-packet --lane fortune500-enterprise" in commands
    and "bin/glaw-premium-lanes docket --lane fortune500-enterprise" in commands
    and "board authority" in intake_required
    and "foreign-qualification" in intake_required
    and "board authority" in governance_required
    and "public-company reporting profile" in sec_required
    and "MD&A" in sec_required
    and "Reg FD" in sec_required
    and "SOX 302/906 certification" in audit_required
    and "PCAOB inspection/challenge response" in audit_required
    and "ASC 740 current/deferred tax" in tax_required
    and "GL trial-balance" in tax_required
    and "M&A/capital markets financing/offering exemption" in ops_required
    and "privacy/data" in ops_required
    and "FCPA/anti-corruption" in ops_required
    and "enterprise regulatory map: SEC, DOJ, FTC, CFPB, FinCEN/BSA/AML, OFAC" in reg_required
    and "litigation hold, document preservation" in reg_required
    and "chief compliance" in reg_required
    and "board authority and delegation matrix" in signoff_required
    and "board/investor disclosure" in signoff_required
    and "SEC enforcement/disclosure reviewer" in reviewers
    and "auditor/PCAOB lens" in reviewers
    and "plaintiff/opposing counsel" in reviewers
    and "treaty/CFC/transfer-pricing reviewer" in reviewers
    and "sanctions reviewer" in reviewers
    and "data-transfer reviewer" in reviewers
    and "10-K/10-Q/8-K/S-1/proxy" in docket
    and "SOX certification" in docket
    and any("without human authority" in item for item in data.get("hard_no_go", []))
    and "does not give legal, tax, accounting" in data.get("authority", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "enterprise blueprint gives one operator flow for Fortune 500 governance, SEC, SOX, tax, and enforcement readiness"

"$CMD" enterprise-blueprint --matter "Acme Enterprise" > "$TMP/enterprise-blueprint.md"; rc=$?
grep -q "# Fortune 500 Enterprise Counsel Blueprint" "$TMP/enterprise-blueprint.md"; rc2=$?
grep -q "## 3. SEC disclosure, capital markets, investor relations, and Reg FD" "$TMP/enterprise-blueprint.md"; rc3=$?
grep -q "## 4. Audit, SOX, ICFR, PCAOB, close, and accounting controls" "$TMP/enterprise-blueprint.md"; rc4=$?
grep -q "Enterprise Required" "$TMP/enterprise-blueprint.md"; rc5=$?
grep -q "bin/glaw-premium-lanes attach fortune500-enterprise" "$TMP/enterprise-blueprint.md"; rc6=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && [ "$rc5" = 0 ] && [ "$rc6" = 0 ] && echo 1 || echo 0)" "enterprise blueprint renders Markdown for operator use"

"$CMD" firm-blueprint --matter "Integrated Premium Firm" --json > "$TMP/firm-blueprint.json"; rc=$?
python3 - "$TMP/firm-blueprint.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
phases="\n".join(row.get("phase", "") for row in data.get("sequence", []))
commands="\n".join(data.get("kickoff_commands", []))
components=data.get("component_statuses", {})
ok=(
    data.get("status") == "pass"
    and data.get("matter") == "Integrated Premium Firm"
    and len(data.get("lanes", [])) == 4
    and data.get("source_ingest", {}).get("source_count") == 6
    and data.get("trust_taxonomy", {}).get("trust_type_count") == 38
    and all(value == "pass" for value in components.values())
    and "Fortune 500 enterprise bench" in phases
    and "Tax system and IRS engine" in phases
    and "Entrepreneur, founder, QSBS, and capital raise" in phases
    and "Investor tax, onboarding, and reporting promises" in phases
    and "Trust, investment LLC, asset shelter, and direct ownership carve-outs" in phases
    and "CFO, accounting, dashboard, and investor/board numbers" in phases
    and "RED to BLUE adversarial review and Chief decision" in phases
    and "bin/glaw-premium-lanes attach fortune500-enterprise" in commands
    and "bin/glaw-premium-lanes attach tax-system" in commands
    and "bin/glaw-premium-lanes attach founder-unicorn" in commands
    and "bin/glaw-premium-lanes attach uhnw-family-office" in commands
    and not data.get("failures")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "firm blueprint gives one integrated Fortune 500, tax, founder, investor, and trust operating model"

"$CMD" firm-blueprint --matter "Integrated Premium Firm" > "$TMP/firm-blueprint.md"; rc=$?
grep -q "# Integrated GLAW Fortune 500, Tax System, Founder, Investor, and Trust Blueprint" "$TMP/firm-blueprint.md"; rc2=$?
grep -q "## 2. Fortune 500 enterprise bench" "$TMP/firm-blueprint.md"; rc3=$?
grep -q "## 6. Trust, investment LLC, asset shelter, and direct ownership carve-outs" "$TMP/firm-blueprint.md"; rc4=$?
grep -q "Authority Boundary" "$TMP/firm-blueprint.md"; rc5=$?
grep -q "bin/glaw-premium-lanes materialize-source-ingest --json" "$TMP/firm-blueprint.md"; rc6=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && [ "$rc5" = 0 ] && [ "$rc6" = 0 ] && echo 1 || echo 0)" "firm blueprint renders Markdown for operator use"

"$CMD" playbook tax-system --matter "Tax Engine" > "$TMP/playbook-tax.md"; rc=$?
grep -q "# Tax System And IRS Engine Kickoff Playbook" "$TMP/playbook-tax.md"; rc2=$?
grep -q "bin/glaw-premium-lanes attach tax-system" "$TMP/playbook-tax.md"; rc3=$?
grep -q "IRS examiner" "$TMP/playbook-tax.md"; rc4=$?
grep -q "Authority Boundary" "$TMP/playbook-tax.md"; rc5=$?
grep -q "<YYYY-MM-DD>" "$TMP/playbook-tax.md"; rc6=$?
grep -q "<basis>" "$TMP/playbook-tax.md"; rc7=$?
grep -q "Tax Engine Required" "$TMP/playbook-tax.md"; rc8=$?
grep -q "return-line map" "$TMP/playbook-tax.md"; rc9=$?
grep -q "Creative Planning Required" "$TMP/playbook-tax.md"; rc10=$?
grep -q "whole-client inventory" "$TMP/playbook-tax.md"; rc11=$?
grep -q "Tax Credit Required" "$TMP/playbook-tax.md"; rc12=$?
grep -q "Form 3800" "$TMP/playbook-tax.md"; rc13=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && [ "$rc4" = 0 ] && [ "$rc5" = 0 ] && [ "$rc6" != 0 ] && [ "$rc7" != 0 ] && [ "$rc8" = 0 ] && [ "$rc9" = 0 ] && [ "$rc10" = 0 ] && [ "$rc11" = 0 ] && [ "$rc12" = 0 ] && [ "$rc13" = 0 ] && echo 1 || echo 0)" "tax-system playbook renders readable Markdown with copy-safe placeholders"

"$CMD" scaffold founder-unicorn --matter "Acme Founder Raise" --json > "$TMP/founder.json"; rc=$?
python3 - "$TMP/founder.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
packet={row.get("item") for row in data.get("required_packet", [])}
lane_packet={row.get("item") for row in data.get("required_lane_packet", [])}
capital_raise={row.get("item") for row in data.get("capital_raise_required", [])}
investor_required={row.get("item") for row in data.get("investor_required", [])}
qsbs_required={row.get("item") for row in data.get("qsbs_required", [])}
entity_topology={row.get("item") for row in data.get("entity_topology_required", [])}
source_ingest={row.get("item") for row in data.get("source_ingest_required", [])}
phases={row.get("phase") for row in data.get("phase_playbook", [])}
docket={row.get("item") for row in data.get("docket_items", [])}
reviewers={row.get("reviewer") for row in data.get("adversarial_reviewers", [])}
ok=(
    data.get("matter") == "Acme Founder Raise"
    and data.get("lane_id") == "founder-unicorn"
    and "glaw-pe-vc-counsel" in data.get("lead_seats", [])
    and "tax strategy and compliance calendar" in packet
    and "capital raise exemption, Form D, Blue Sky, KYC, and investor-suitability plan" in lane_packet
    and "broker-dealer/finder and transaction-compensation memo" in lane_packet
    and "investor risk-factor bank and data-room disclosure archive" in lane_packet
    and "use-of-proceeds, funds-flow, cap-table dilution, and post-raise reporting calendar" in lane_packet
    and "QSBS source-refresh and proposed revenue procedure certificate memo" in lane_packet
    and "QSBS annual checklist, officer certificate, counsel issue list, record-retention covenant, and shareholder information statement" in lane_packet
    and "investor persona, eligibility, suitability, authority, and beneficial-owner onboarding packet" in lane_packet
    and "investor tax disclosure, withholding, K-1/1099/1042-S/FATCA/CRS, and no-guarantee QSBS statement" in lane_packet
    and "side-letter, MFN, information-rights, pro-rata, ROFR/co-sale, transfer-restriction, and confidentiality matrix" in lane_packet
    and "investor communications, marketing-claim, performance/projection, complaint, privacy, and retention-control memo" in lane_packet
    and "exemption selection: Reg D 506(b), Reg D 506(c), Reg CF, Reg A, Reg S, intrastate, or registered offering" in capital_raise
    and "solicitation and integration memo" in capital_raise
    and "bad-actor disqualification screen" in capital_raise
    and "investor KYC/AML/OFAC/source-of-funds review" in capital_raise
    and "PPM/OM/Form C/Form 1-A disclosure stack" in capital_raise
    and "QSBS issuer and shareholder information statement" in capital_raise
    and "issuer status: domestic C corporation at issuance and during substantially all tested years; not DISC/former DISC, RIC, REIT, REMIC, cooperative, or section 936 corporation" in qsbs_required
    and "original-issue acquisition: issuance date, shareholder name, certificate/ledger entry, consideration paid, services/property detail, underwriter status, 83(b)/restricted-stock status, SAFE/note/option conversion path, and no acquisition for stock unless section 1202(f)/(h) exception applies" in qsbs_required
    and "active-business requirement: 80 percent active qualified trade or business assets, excluded service/investment/farming/hotel/restaurant/mining/finance businesses, startup/R&E/section 41/software royalty safe harbors, working-capital limits, real-property cap, and stock/securities cap" in qsbs_required
    and "redemption taint screen: related-party redemptions two years before/after issuance, significant redemptions one year before/after issuance, de minimis/service/death/disability/divorce exceptions, value calculations, and related-party attribution map" in qsbs_required
    and "shareholder-side facts: acquisition chain, pass-through/gift/death/reorganization/section 351 history, holding period, sale or exchange, offsetting short position, replacement QSBS purchase within 60 days for section 1045, and shareholder-specific limitation tracking" in qsbs_required
    and "exit and M&A preservation: merger/reorganization section 1202(h), stock-for-stock exchange limits, built-in gain tracking, rollover/secondary/tender planning, escrows/holdbacks, and buyer diligence response" in qsbs_required
    and "investor eligibility and suitability: accredited investor, qualified purchaser, qualified client, sophistication, investment limits, bad-actor and disqualification status" in investor_required
    and "KYC, AML, OFAC, sanctions, politically exposed person, source-of-funds, source-of-wealth, and beneficial-ownership verification" in investor_required
    and "QSBS and tax-credit investor statement: no guarantee, issuer evidence, shareholder holding-period tracking, section 1045 rollover, section 1202 limitations, and reporting owner" in investor_required
    and "post-close reporting calendar: capital account, cap table, investor ledger, annual tax package, financial statements, notices, consents, amendments, and board/investor approvals" in investor_required
    and "investor complaint, rescission, fraud, misstatement, blue-sky, SEC/state examiner, IRS investor-tax, and plaintiff counsel adversarial review pass" in investor_required
    and "default chassis: irrevocable dynasty or investment trust owns an investment LLC for diversified brokerage assets, alternatives, private fund interests, real estate interests, crypto custody vehicles, and family investment administration" in entity_topology
    and "direct trust-owned asset lane: assets bypass the investment LLC when tax, issuer, transfer, securities, ERISA, insurance, or fiduciary rules make direct ownership preferable" in entity_topology
    and "founder restricted stock and 83(b) carve-out: transfer timing, service-provider status, vesting, valuation, and 30-day election proof reviewed before any trust or LLC funding" in entity_topology
    and "QSBS section 1202 carve-out: original issue holder, qualified shareholder, holding period, transfer history, section 1202(g), section 1045, gross-assets, active-business, redemption, and shareholder-level limits reviewed before transfer" in entity_topology
    and "S-corp stock carve-out: QSST, ESBT, grantor trust, eligible shareholder, single-class-stock, election, consent, and termination-risk screen before trust or LLC ownership" in entity_topology
    and "life-insurance carve-out: ILIT ownership, incidents of ownership, new-policy versus transferred-policy, section 2035, premium gifts, Crummey notices, underwriting, and policy-economics screen" in entity_topology
    and "retirement-asset carve-out: beneficiary designation, prohibited transaction, RMD, inherited-IRA, UBIT/UBTI, custodial agreement, and qualified-plan rules reviewed before any trust or LLC routing" in entity_topology
    and "issuer-restricted private securities carve-out: issuer consent, transfer restrictions, subscription terms, KYC/AML/OFAC, tax forms, ERISA, custody, valuation, and securities-law limits reviewed before transfer" in entity_topology
    and "investment LLC governance: manager/trustee authority, operating agreement, capital-call and distribution controls, investment policy statement, fiduciary accounting, charging-order law, books, K-1/reporting, custody, and valuation cadence" in entity_topology
    and "adversarial topology review: IRS estate/gift/QSBS examiner, SEC or issuer transfer reviewer, creditor/fraudulent-transfer counsel, trustee fiduciary reviewer, valuation/appraiser, and investor tax counsel pass before funding" in entity_topology
    and "local source inventory: /Users/ricardoprieto/Desktop/TAX CREDIT/fy2026h1_tab8.pdf mapped to tax expenditure and credit inventory, QSBS, R&E/R&D, state credits, investment credits, brownfields, LIHTC, historic, climatetech, qualified conversion, internship, transferability, and refundability concepts" in source_ingest
    and "external authority refresh: IRS Instructions for Schedule D (Form 1120-S), current 26 U.S.C. section 1202 text, section 1045, Treasury/IRS guidance, and CLA QSBS proposed revenue procedure source are dated and reconciled against local source conclusions" in source_ingest
    and "source routing: every local and external source is assigned to tax qualification, capital-raising disclosure, investor reporting, wealth/asset sheltering, SEC/investor communications, or adversarial review owner" in source_ingest
    and "investor tax disclosure, withholding, K-1/1099/1042-S/FATCA/CRS, and no-guarantee QSBS statement" in packet
    and "dynasty trust, investment LLC, and direct-ownership carve-out memo" in packet
    and "QSBS issuer and shareholder evidence file" in phases
    and "QSBS source refresh and proposed revenue procedure certificate plan" in phases
    and "annual QSBS checklist, gross-assets, controlled-group, active-business, and redemption screen" in phases
    and "KYC/AML, OFAC, source-of-funds, source-of-wealth, and funds-flow controls" in phases
    and "side-letter, information-rights, transfer-restriction, and data-room archive" in phases
    and "investor persona, eligibility, suitability, and authority screen" in phases
    and "investor communications, marketing archive, complaint, privacy, and retention controls" in phases
    and "83(b)/Form 15620 30-day deadline" in docket
    and "QSBS annual certificate, record-retention, and shareholder information refresh" in docket
    and "section 1045 60-day rollover deadline where relevant" in docket
    and "post-raise investor update and reporting cadence" in docket
    and "investor KYC refresh, tax-document collection, consent, complaint, privacy-retention, and transfer-review deadlines" in docket
    and "IRS QSBS examiner" in reviewers
    and any("without human authority" in item for item in data.get("hard_no_go", []))
    and "Chief/Council approved" in data.get("gates", [])
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "founder scaffold includes investor tax, QSBS, docket, and gate controls"

"$CMD" scaffold fortune500-enterprise --json > "$TMP/enterprise.json"; rc=$?
python3 - "$TMP/enterprise.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane_packet={row.get("item") for row in data.get("required_lane_packet", [])}
enterprise_required={row.get("item") for row in data.get("enterprise_required", [])}
phases={row.get("phase") for row in data.get("phase_playbook", [])}
ok=(
    "SEC disclosure and public-company reporting" not in data.get("workstreams", [])
    and "SEC and public-company reporting" in {row.get("name") for row in data.get("workstreams", [])}
    and "10-K/10-Q/8-K/S-1/proxy, Reg S-K/S-X, MD&A, risk-factor, Form 4/Section 16, and Inline XBRL control calendar" in lane_packet
    and "SOX 302/906 certification, SOX 404 ICFR, disclosure controls, audit committee, and PBC evidence bridge" in lane_packet
    and "PCAOB/auditor independence challenge response and material-weakness remediation memo" in lane_packet
    and "ASC 740 tax provision, ETR, deferred-tax, UTP, valuation allowance, and auditor tie-out register" in lane_packet
    and "litigation hold, investigations, privilege log, custodians, evidence timeline, and document-preservation memo" in lane_packet
    and "board/investor disclosure, earnings-release, analyst-guidance, investor-relations, and Reg FD review packet" in lane_packet
    and "public-company reporting profile: filer status, 10-K, 10-Q, 8-K, S-1, proxy, Form 4/Section 16, Reg S-K, Reg S-X, and Inline XBRL screen" in enterprise_required
    and "SOX 302/906 certification, SOX 404 ICFR, disclosure controls and procedures, control-owner evidence, and deficiency/material-weakness remediation" in enterprise_required
    and "audit committee, PBC list, auditor independence, PCAOB inspection/challenge response, management representation, and audit-adjustment log" in enterprise_required
    and "board/investor disclosure packet, investor-relations controls, analyst guidance, earnings release, and selective-disclosure/Reg FD review" in enterprise_required
    and "litigation-hold, preservation, privilege, custodians, and investigation-readiness sweep" in phases
    and "/glaw-sec-reporting" in data.get("lead_seats", [])
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "enterprise scaffold includes SEC/SOX/PCAOB/ASC740 controls"

"$CMD" scaffold tax-system --json > "$TMP/tax-scaffold.json"; rc=$?
python3 - "$TMP/tax-scaffold.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane_packet={row.get("item") for row in data.get("required_lane_packet", [])}
tax_engine={row.get("item") for row in data.get("tax_engine_required", [])}
tax_credit={row.get("item") for row in data.get("tax_credit_required", [])}
phases={row.get("phase") for row in data.get("phase_playbook", [])}
docket={row.get("item") for row in data.get("docket_items", [])}
ok=(
    "primary-law citation corpus freshness report" in lane_packet
    and "book-to-tax M-1/M-3 bridge and return-line map" in lane_packet
    and "return-position authority, Form 8275/8275-R disclosure, and penalty-defense memo" in lane_packet
    and "tax-credit eligibility, substantiation, computation, transferability, recapture, and forms packet" in lane_packet
    and "IRS notice, transcript, statute-of-limitations, and response-deadline ledger" in lane_packet
    and "state nexus/apportionment/PTET/franchise-tax matrix" in lane_packet
    and "international information-return and FBAR/FATCA screen" in lane_packet
    and "ASC 740, ETR, deferred-tax, UTP, and auditor/PBC bridge where relevant" in lane_packet
    and "source evidence intake: taxpayer profile, entity chart, source-file index, missing-information list, and document hashes" in tax_engine
    and "credit and incentive eligibility, substantiation, wage/capex/time-record support, recapture, transferability, and return-position owner" in tax_engine
    and "SALT nexus, apportionment, sourcing, throwback, PTET, franchise/margin, sales/use tax, and state-credit matrix" in tax_engine
    and "estate, gift, GST, trust 1041/DNI, Form 706, Form 709, DSUE/portability, and appraisal tie-out where relevant" in tax_engine
    and "recurring docket: returns, extensions, estimated taxes, notices, elections, credit certifications, information returns, and trust administration" in tax_engine
    and "credit inventory and routing: R&D section 41/174A, payroll credit, section 45X/45Y/48/48E/30C/45V/45Q/45L/179D, LIHTC, NMTC, WOTC, ERC/historic claims, disaster, foreign tax credit, AMT, state and local credits, and industry-specific incentives" in tax_credit
    and "credit computation workpaper: base amount, incremental or percentage calculation, limitation ordering, carryforward/carryback, basis reduction, passive activity, at-risk, AMT, section 38 general business credit, and book-to-tax tie-out" in tax_credit
    and "transferability, monetization, and investor reporting: section 6418 transfer, section 6417 direct pay, tax-credit purchase agreement, indemnity/insurance, buyer diligence file, investor K-1/1099/shareholder statement, and no-guarantee disclosure" in tax_credit
    and "recapture and compliance calendar: placed-in-service, annual certification, wage/apprenticeship cure, basis/event changes, disposition, casualty, production/measurement period, carryforward expiry, amended return, and statute-of-limitations docket" in tax_credit
    and "adversarial review: IRS credit examiner, state credit authority, forensic accountant, auditor/PCAOB where relevant, investor/buyer counsel, and Chief Compliance Officer pass before claiming, selling, transferring, or reporting any credit" in tax_credit
    and "return-position authority, disclosure, and penalty-defense review" in phases
    and "credit and incentive eligibility inventory" in phases
    and "credit substantiation, computation, form, recapture, and transferability build" in phases
    and "ASC 740, UTP, auditor PBC, and credit control tie-out" in phases
    and "return/payment/e-file/transmitter/MeF/IRIS/SSA BSO handoff" in phases
    and "international information-return and FBAR/FATCA due dates" in docket
    and "credit certification, registration, substantiation, recapture, transferability, and carryforward deadlines" in docket
    and "/glaw-tax-provision" in data.get("lead_seats", [])
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "tax scaffold includes source-fresh return-position and controversy controls"

python3 - "$ROOT/docs/tools.md" <<'PY'
import sys
text=open(sys.argv[1], encoding="utf-8").read()
row=next((line for line in text.splitlines() if line.startswith("| `glaw-premium-lanes` |")), "")
ok=(
    "complete --lane LANE" in row
    and "render-packet --lane LANE" in row
    and "check-packet --lane LANE" in row
    and "docket --lane LANE" in row
    and "<YYYY-MM-DD>" not in row
    and "<basis>" not in row
    and "<lead>" not in row
    and "packet.json" not in row
    and "copy-safe kickoff commands" in row
    and "active-matter packet by `--lane`" in row
)
sys.exit(0 if ok else 1)
PY
rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "premium lane docs teach active-matter copy-safe command flow"

"$CMD" scaffold uhnw-family-office --json > "$TMP/uhnw.json"; rc=$?
python3 - "$TMP/uhnw.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
workstreams={row.get("name") for row in data.get("workstreams", [])}
lane_packet={row.get("item") for row in data.get("required_lane_packet", [])}
trust_taxonomy={row.get("type") for row in data.get("trust_taxonomy_required", [])}
schwab_topics={row.get("topic") for row in data.get("schwab_trust_topic_required", [])}
entity_topology={row.get("item") for row in data.get("entity_topology_required", [])}
docket={row.get("item") for row in data.get("docket_items", [])}
ok=(
    "Estate and trust design" in workstreams
    and "Asset protection" in workstreams
    and "Fiduciary administration" in workstreams
    and "Family governance and special situations" in workstreams
    and "revocable, A-B/bypass, testamentary, irrevocable gift, dynasty/GST, IDGT, GRAT/GRUT, QPRT, SLAT, ILIT, CRT/CLT, DAPT/offshore APT, DING/NING/ING, special-needs, QSST/ESBT, land/DST, business/statutory, rabbi/secular, qualified-plan/IRA, purpose, and constructive/resulting trust classification memo" in lane_packet
    and "revocable living trust" in trust_taxonomy
    and "A-B / bypass / credit-shelter trust" in trust_taxonomy
    and "testamentary trust" in trust_taxonomy
    and "IDGT" in trust_taxonomy
    and "GRAT / GRUT" in trust_taxonomy
    and "SLAT" in trust_taxonomy
    and "CRT / CRAT / CRUT / NIMCRUT" in trust_taxonomy
    and "DING / NING / ING" in trust_taxonomy
    and "QSST / ESBT" in trust_taxonomy
    and "Delaware statutory trust / DST" in trust_taxonomy
    and "business/statutory trust" in trust_taxonomy
    and "rabbi / secular trust" in trust_taxonomy
    and "qualified plan / IRA custodial trust" in trust_taxonomy
    and "constructive / resulting trust" in trust_taxonomy
    and "investment LLC governance and IPS packet" in lane_packet
    and "trustee/executor fiduciary-risk workpaper" in lane_packet
    and "special-needs, conservatorship, and incapacity planning branch memo" in lane_packet
    and "family governance, mission statement, equal/equitable distribution, and beneficiary-readiness memo" in lane_packet
    and "current Schwab Learn trusts topic source update note from https://www.schwab.com/learn/topic/trusts" in lane_packet
    and "Schwab trusts topic source update note: https://www.schwab.com/learn/topic/trusts dated source refresh and visible topic-index capture" in schwab_topics
    and any("How to Plan Around Estate Tax Uncertainties (Aug. 11, 2026)" in topic and "Avoiding Restrictions With a Discretionary Trust (Nov. 14, 2025)" in topic for topic in schwab_topics)
    and "estate-tax uncertainty: A-B/bypass, GRAT, CRT, federal/state estate-tax uncertainty, and old formula-clause review" in schwab_topics
    and "SLAT planning: separate-property funding, community-property partition, reciprocal-trust doctrine, HEMS/independent trustee, access risk, basis tradeoff, and optional dynasty/GST design" in schwab_topics
    and "dynasty trust planning: GST allocation, situs, trustee location, duration/perpetuities law, distribution standards, creditor/divorce protection, and income-tax posture" in schwab_topics
    and "ILIT and IRA funding: RMD/income-tax modeling, underwriting, Form 709, Crummey notices, policy economics, incidents of ownership, and section 2035 three-year-rule screen" in schwab_topics
    and "QPRT planning: retained term, section 7520 valuation, survival risk, post-term leaseback, basis tradeoff, property tax, title, and insurance review" in schwab_topics
    and "discretionary trust planning: trustee discretion, HEMS or incentive standards, beneficiary conflict, oversight cost, and professional co-trustee option" in schwab_topics
    and "equal-versus-equitable distributions: family governance, beneficiary fairness, difficult-to-divide assets, advance gifts, special assets, and communication memo" in schwab_topics
    and "charitable trust routing: CRT/CRAT/CRUT/NIMCRUT/CLT comparison, payout/reporting tests, gain deferral, income stream, deduction, and philanthropic intent" in schwab_topics
    and "page-level source drift control: pages 1 through 4 of the Schwab trusts topic index are captured with title, date, URL, and routing note before relying on the benchmark" in schwab_topics
    and "founder and business-owner succession crosswalk: IP protection, assignment, governance, and estate-transfer issues from the Schwab trust index are routed to corporate/IP/tax seats where relevant" in schwab_topics
    and "default chassis: irrevocable dynasty or investment trust owns an investment LLC for diversified brokerage assets, alternatives, private fund interests, real estate interests, crypto custody vehicles, and family investment administration" in entity_topology
    and "direct trust-owned asset lane: assets bypass the investment LLC when tax, issuer, transfer, securities, ERISA, insurance, or fiduciary rules make direct ownership preferable" in entity_topology
    and "QSBS section 1202 carve-out: original issue holder, qualified shareholder, holding period, transfer history, section 1202(g), section 1045, gross-assets, active-business, redemption, and shareholder-level limits reviewed before transfer" in entity_topology
    and "retirement-asset carve-out: beneficiary designation, prohibited transaction, RMD, inherited-IRA, UBIT/UBTI, custodial agreement, and qualified-plan rules reviewed before any trust or LLC routing" in entity_topology
    and "trust administration and funding: completed gift, GST allocation, grantor/non-grantor classification, situs, trustee powers, solvency certificate, fraudulent-transfer screen, title assignment, beneficiary designations, and periodic review" in entity_topology
    and "tax and compliance model: income-tax owner, estate/gift/GST effect, basis and section 1014 tradeoff, section 704 partnership reporting where relevant, state tax, SEC/private-offering transfer, BOI/beneficial ownership, and Form 709/1041/K-1 calendar" in entity_topology
    and "Form 709 and GST allocation calendar" in docket
    and "/glaw-estate-trusts" in data.get("lead_seats", [])
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "UHNW scaffold includes trust, asset-protection, and transfer-tax operations"

"$CMD" show missing-lane >/tmp/glaw-premium-missing.out 2>&1; rc=$?
grep -q "unknown lane" /tmp/glaw-premium-missing.out; rc2=$?
ok "$([ "$rc" != 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane command fails closed on unknown lane"

export GLAW_HOME="$TMP/glaw-home"
"$ROOT/bin/glaw" matter new "Premium Lane Active Matter" >/dev/null; rc=$?
"$CMD" attach fortune500-enterprise --json > "$TMP/attach.json"; rc2=$?
python3 - "$TMP/attach.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
root=Path(__file__).resolve()
artifact=Path(report.get("artifact", ""))
source=Path(report.get("source", ""))
timeline=home/"matters"/report.get("matter_slug", "")/"timeline.jsonl"
intake=home/"matters"/report.get("matter_slug", "")/"intake.json"
packet=json.load(open(artifact)) if artifact.is_file() else {}
intake_data=json.load(open(intake)) if intake.is_file() else {}
timeline_text=timeline.read_text(encoding="utf-8") if timeline.is_file() else ""
source_text=source.read_text(encoding="utf-8") if source.is_file() else ""
intake_lanes=intake_data.get("universal", {}).get("premium_lanes", [])
ok=(
    report.get("status") == "attached"
    and report.get("timeline_event") == "premium_lane_attached"
    and report.get("intake_premium_lanes") == ["fortune500-enterprise"]
    and packet.get("lane_id") == "fortune500-enterprise"
    and intake_lanes == ["fortune500-enterprise"]
    and packet.get("manifest_source") == "lib/client-lanes/premium-lanes.json"
    and isinstance(packet.get("manifest_version"), int)
    and isinstance(packet.get("manifest_sha256"), str)
    and len(packet.get("manifest_sha256", "")) == 64
    and "manifest_sha256:" in source_text
    and "SEC enforcement/disclosure reviewer" in {row.get("reviewer") for row in packet.get("adversarial_reviewers", [])}
    and "premium_lane_attached" in timeline_text
    and "manifest: lib/client-lanes/premium-lanes.json" in source_text
)
sys.exit(0 if ok else 1)
PY
rc3=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && [ "$rc3" = 0 ] && echo 1 || echo 0)" "premium lane attach writes active-matter artifact, source note, and timeline event"

"$CMD" status --json > "$TMP/status-after-attach.json"; rc=$?
python3 - "$TMP/status-after-attach.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane=data.get("lanes", [{}])[0]
ids={row.get("id") for row in lane.get("failures", [])}
ok=(
    data.get("status") == "fail"
    and data.get("matter_slug") == "premium-lane-active-matter"
    and lane.get("lane_id") == "fortune500-enterprise"
    and "workstream_owner" in ids
    and "complete --lane fortune500-enterprise" in lane.get("next_command", "")
    and data.get("action_plan", [{}])[0].get("next_command") == lane.get("next_command")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane status summarizes incomplete active-matter packet and next command"

ARTIFACT="$(python3 - "$TMP/attach.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
python3 - "$ARTIFACT" <<'PY'
import json, sys
from pathlib import Path
path=Path(sys.argv[1])
packet=json.load(open(path))
packet["manifest_sha256"]="0"*64
path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
PY
"$CMD" check-packet "$ARTIFACT" --json > "$TMP/check-stale.json"; rc=$?
python3 - "$TMP/check-stale.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "manifest_stale" in ids
sys.exit(0 if ok else 1)
PY
rc2=$?
"$CMD" docket "$ARTIFACT" --json > "$TMP/docket-stale.json"; rc3=$?
python3 - "$TMP/docket-stale.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "manifest_stale" in ids and not data.get("docketed")
sys.exit(0 if ok else 1)
PY
rc4=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && [ "$rc3" = 1 ] && [ "$rc4" = 0 ] && echo 1 || echo 0)" "premium lane packet freshness blocks stale manifest artifacts"

"$CMD" attach fortune500-enterprise --json > "$TMP/attach-refresh.json"; rc=$?
ARTIFACT="$(python3 - "$TMP/attach-refresh.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
"$CMD" complete --lane fortune500-enterprise --owner "Playbook lead" --docket-owner "Playbook docket" --due 2026-12-01 --source "SRC-0001 premium lane source" --json > "$TMP/complete-by-lane.json"; rc=$?
python3 - "$TMP/complete-by-lane.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
artifact=home/"matters"/"premium-lane-active-matter"/"workpapers"/"premium-lane-fortune500-enterprise.json"
packet=json.load(open(artifact))
ok=(
    report.get("timeline_event") == "premium_lane_packet_completed"
    and report.get("lane_id") == "fortune500-enterprise"
    and packet.get("completed_by") == "Playbook lead"
    and all(row.get("owner") for row in packet.get("workstreams", []))
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane playbook --lane complete resolves active-matter workpaper from repo root"

"$CMD" attach fortune500-enterprise --json > "$TMP/attach-reset.json"; rc=$?
ARTIFACT="$(python3 - "$TMP/attach-reset.json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1]))["artifact"])
PY
)"
ok "$([ "$rc" = 0 ] && [ -s "$ARTIFACT" ] && echo 1 || echo 0)" "premium lane fixture reset after playbook --lane smoke"

"$CMD" check-packet "$ARTIFACT" --json > "$TMP/check-incomplete.json"; rc=$?
python3 - "$TMP/check-incomplete.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and {"workstream_owner", "phase_owner", "required_packet_owner", "reviewer_status", "docket_due"} <= ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane packet check fails closed while scaffold is incomplete"

"$CMD" docket "$ARTIFACT" --json > "$TMP/docket-incomplete.json"; rc=$?
python3 - "$TMP/docket-incomplete.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "workstream_owner" in ids and not data.get("docketed")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane docket refuses incomplete packet"

"$CMD" complete "$ARTIFACT" --owner "Lead partner" --docket-owner "Docketing" --due 2026-12-01 --source "SRC-0001 premium lane source" --json > "$TMP/complete.json"; rc=$?
python3 - "$TMP/complete.json" "$ARTIFACT" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
packet=json.load(open(sys.argv[2]))
home=Path(sys.argv[3])
timeline=home/"matters"/report.get("packet", "").split("/matters/", 1)[1].split("/", 1)[0]/"timeline.jsonl"
timeline_text=timeline.read_text(encoding="utf-8") if timeline.is_file() else ""
ok=(
    report.get("status") == "fail"
    and report.get("timeline_event") == "premium_lane_packet_completed"
    and packet.get("completed_by") == "Lead partner"
    and all(row.get("status") == "complete" and row.get("owner") for row in packet.get("workstreams", []))
    and all(row.get("status") == "complete" and row.get("owner") for row in packet.get("phase_playbook", []))
    and all(row.get("status") == "complete" and row.get("owner") for row in packet.get("required_packet", []))
    and all(row.get("status") == "complete" and row.get("owner") for row in packet.get("required_lane_packet", []))
    and all(row.get("status") == "survived" for row in packet.get("adversarial_reviewers", []))
    and all(row.get("owner") == "Docketing" and row.get("due") == "2026-12-01" and "SRC-" in row.get("source", "") for row in packet.get("docket_items", []))
    and "premium_lane_packet_completed" in timeline_text
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane complete populates owners, reviewers, docket metadata, and timeline while templates remain pending"

"$CMD" check-packet "$ARTIFACT" --json > "$TMP/check-complete-no-render.json"; rc=$?
python3 - "$TMP/check-complete-no-render.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "rendered_template_missing" in ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane packet check still fails until rendered templates exist"

"$CMD" docket "$ARTIFACT" --json > "$TMP/docket-before-render.json"; rc=$?
python3 - "$TMP/docket-before-render.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "rendered_template_missing" in ids and not data.get("docketed")
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane docket refuses metadata-complete packet before templates render"

"$CMD" render-packet "$ARTIFACT" --owner "Lead partner" --source "SRC-0001 premium lane source" --json > "$TMP/render.json"; rc=$?
python3 - "$TMP/render.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
matter=home/"matters"/"premium-lane-active-matter"
rendered=report.get("rendered", [])
paths=[matter/row.get("path", "") for row in rendered]
texts=[path.read_text(encoding="utf-8") for path in paths if path.is_file()]
timeline=(matter/"timeline.jsonl").read_text(encoding="utf-8")
required=("Owner:", "Report voice:", "Findings:", "Evidence:", "Red flags:", "Sign-off conditions:", "## UPL / Human Authority Footer")
ok=(
    report.get("status") == "pass"
    and report.get("timeline_event") == "premium_lane_templates_rendered"
    and len(rendered) == 19
    and all(path.is_file() for path in paths)
    and any("executive decision memo" in text for text in texts)
    and any("investor or board disclosure packet" in text for text in texts)
    and any("SEC disclosure issue tracker" in text for text in texts)
    and any("## Phase Playbook" in text for text in texts)
    and any("## Lane-Specific Packet Items" in text for text in texts)
    and all("DRAFT CONTENT TO BE COMPLETED" not in text and "REVIEW:" not in text for text in texts)
    and all(all(term in text for term in required) for text in texts)
    and all("Premium lane fortune500-enterprise" in text or "Lane ID: fortune500-enterprise" in text for text in texts)
    and "premium_lane_templates_rendered" in timeline
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane render-packet creates lane-specific report-ready draft templates"

python3 - "$TMP/render.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
matter=home/"matters"/"premium-lane-active-matter"
target=matter/report["rendered"][0]["path"]
target.write_text(target.read_text(encoding="utf-8") + "\nREVIEW: unresolved premium lane issue.\n", encoding="utf-8")
PY
"$CMD" check-packet "$ARTIFACT" --json > "$TMP/check-render-marker.json"; rc=$?
python3 - "$TMP/check-render-marker.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
ids={row.get("id") for row in data.get("failures", [])}
ok=data.get("status") == "fail" and "rendered_template_review_marker" in ids
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane packet check blocks unresolved rendered-template review markers"

"$CMD" render-packet "$ARTIFACT" --owner "Lead partner" --source "SRC-0001 premium lane source" --json > "$TMP/render-restored.json"; rc=$?
ok "$([ "$rc" = 0 ] && echo 1 || echo 0)" "premium lane render-packet restores clean templates"

"$CMD" check-packet "$ARTIFACT" --json > "$TMP/check-complete.json"; rc=$?
python3 - "$TMP/check-complete.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
data=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
matter=home/"matters"/"premium-lane-active-matter"
rendered=data.get("rendered_templates", [])
ok=(
    data.get("status") == "pass"
    and data.get("lane_id") == "fortune500-enterprise"
    and not data.get("failures")
    and len(rendered) == 19
    and all(row.get("path", "").startswith("drafts/premium-lane-fortune500-enterprise/") for row in rendered)
    and all(row.get("item") and row.get("sha256") and len(row.get("sha256")) == 64 for row in rendered)
    and all((matter/row.get("path", "")).is_file() for row in rendered)
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane packet check passes with rendered-template hash manifest"

"$CMD" status --json > "$TMP/status-before-docket.json"; rc=$?
python3 - "$TMP/status-before-docket.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane=data.get("lanes", [{}])[0]
ids={row.get("id") for row in lane.get("failures", [])}
ok=(
    data.get("status") == "fail"
    and lane.get("check_packet_status") == "pass"
    and lane.get("docketed") is False
    and "docket_materialized" in ids
    and "docket --lane fortune500-enterprise" in lane.get("next_command", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 1 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane status blocks packet-ready lane until docket materialization"

"$CMD" docket "$ARTIFACT" --json > "$TMP/docket.json"; rc=$?
python3 - "$TMP/docket.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
matter=home/"matters"/"premium-lane-active-matter"
docket=(matter/"docket.jsonl").read_text(encoding="utf-8").splitlines()
timeline=(matter/"timeline.jsonl").read_text(encoding="utf-8")
rows=[json.loads(line) for line in docket if line.strip()]
ok=(
    report.get("status") == "pass"
    and report.get("timeline_event") == "premium_lane_docketed"
    and len(report.get("docketed", [])) == 6
    and not report.get("skipped")
    and len(rows) == 6
    and all(row.get("lane_id") == "fortune500-enterprise" for row in rows)
    and all(row.get("owner") == "Docketing" for row in rows)
    and all(row.get("source") == "SRC-0001" for row in rows)
    and all(row.get("premium_lane_artifact") == "workpapers/premium-lane-fortune500-enterprise.json" for row in rows)
    and "premium_lane_docketed" in timeline
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane docket writes source-backed matter docket rows"

"$CMD" status --json > "$TMP/status-after-docket.json"; rc=$?
python3 - "$TMP/status-after-docket.json" <<'PY'
import json, sys
data=json.load(open(sys.argv[1]))
lane=data.get("lanes", [{}])[0]
ok=(
    data.get("status") == "pass"
    and data.get("lane_count") == 1
    and not data.get("failures")
    and not data.get("action_plan")
    and lane.get("status") == "pass"
    and lane.get("check_packet_status") == "pass"
    and lane.get("docketed") is True
    and lane.get("rendered_template_count") == 19
    and "glaw-final-packet build --profile auto" in lane.get("next_command", "")
)
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane status passes after packet check and docket materialization"

"$CMD" docket "$ARTIFACT" --json > "$TMP/docket-again.json"; rc=$?
python3 - "$TMP/docket-again.json" "$GLAW_HOME" <<'PY'
import json, sys
from pathlib import Path
report=json.load(open(sys.argv[1]))
home=Path(sys.argv[2])
docket=(home/"matters"/"premium-lane-active-matter"/"docket.jsonl").read_text(encoding="utf-8").splitlines()
ok=report.get("status") == "pass" and not report.get("docketed") and len(report.get("skipped", [])) == 6 and len(docket) == 6
sys.exit(0 if ok else 1)
PY
rc2=$?
ok "$([ "$rc" = 0 ] && [ "$rc2" = 0 ] && echo 1 || echo 0)" "premium lane docket is idempotent on rerun"

rm -rf "$TMP" /tmp/glaw-premium-missing.out
echo
echo "0 failures — $pass passed, $fail failed"
[ "$fail" = 0 ] && { echo "ALL PASS"; exit 0; } || { echo "FAILURES"; exit 1; }
