#!/usr/bin/env python3
"""
Known-answer tests for the 409A valuation engine. Stdlib only — run directly:

    python3 scripts/test_valuation_engine.py        # -> "ALL PASSED" or a failure

Also pytest-compatible (`pytest scripts/test_valuation_engine.py`) since every
check is a `test_*` function using bare asserts. Hand-computed expected values
lock the math so a regression in any module is caught.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import valuation_engine as E  # noqa: E402
import reviewer_check as R  # noqa: E402


def approx(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


class A:  # minimal audit stub
    def record(self, *a, **k): pass
    def warn(self, *a, **k): pass


# --------------------------------------------------------------------------- #
def test_percentile():
    xs = [1, 2, 3, 4]
    assert approx(E.percentile(xs, 50), 2.5)
    assert approx(E.percentile(xs, 25), 1.75)
    assert E.percentile([], 50) is None
    assert E.percentile([7], 90) == 7


def test_bs_call_intrinsic_floor():
    # Deep in the money, no time -> intrinsic value.
    assert approx(E.bs_call(100, 40, 0, 0.04, 0.6), 60)
    # Zero strike -> equals S.
    assert E.bs_call(100, 0, 4, 0.04, 0.6) == 100
    # Known Black-Scholes value: S=K=100, T=1, r=0, sigma=0.2 -> ~7.9656
    assert approx(E.bs_call(100, 100, 1, 0.0, 0.2), 7.9655, tol=1e-3)


def test_dcf():
    intake = {
        "financials": {"tax_rate": 0.0},
        "forecasts": {
            "revenue": [1000, 1000], "opex_pct": 0.0,
            "capex": [0, 0], "depreciation": [0, 0], "working_capital_change": [0, 0],
            "discount_rate": 0.10, "terminal_growth": 0.0,
        },
    }
    r = E.dcf(intake, A())
    # FCF each year = revenue*(1-0)=1000 (no tax/capex/dep/nwc). EBIT=1000, NOPAT=1000.
    # PV1 = 1000/1.1 = 909.0909; PV2 = 1000/1.21 = 826.4463
    assert approx(r["years"][0]["pv"], 909.09, tol=1e-3)
    assert approx(r["years"][1]["pv"], 826.45, tol=1e-3)
    # TV = 1000*(1+0)/(0.10-0) = 10000; PV(TV) = 10000/1.21 = 8264.46
    assert approx(r["terminal_value"], 10000.0, tol=1e-2)
    assert approx(r["pv_terminal_value"], 8264.46, tol=1e-2)
    # EV = 909.09 + 826.45 + 8264.46
    assert approx(r["enterprise_value"], 9999.99, tol=1e-1)


def test_dcf_terminal_guard():
    intake = {"forecasts": {"revenue": [100], "discount_rate": 0.02, "terminal_growth": 0.05}}
    r = E.dcf(intake, A())
    assert r["terminal_value"] == 0.0  # r <= g -> TV zeroed


def test_comps():
    intake = {
        "comparables": {"peers": [
            {"name": "a", "ev": 100, "revenue": 10, "ebitda": 5},   # 10x, 20x
            {"name": "b", "ev": 200, "revenue": 10, "ebitda": 5},   # 20x, 40x
        ]},
        "forecasts": {"revenue": [10], "ebitda": [5]},
    }
    r = E.comps(intake, A())
    # median EV/Rev = 15 -> implied 150; median EV/EBITDA = 30 -> implied 150; mean = 150
    assert approx(r["enterprise_value"], 150.0)
    assert approx(r["ev_revenue"]["median"], 15.0)


def test_vc_method():
    intake = {"vc_method": {"exit_year_revenue": 1000, "exit_multiple": 5,
                            "target_return": 10, "investment": 100}}
    r = E.vc_method(intake, A())
    assert approx(r["exit_value"], 5000)
    assert approx(r["post_money"], 500)
    assert approx(r["pre_money"], 400)


def test_pwerm_normalizes():
    intake = {"forecasts": {"discount_rate": 0.0},
              "pwerm": {"scenarios": [
                  {"name": "up", "probability": 1, "exit_value": 100, "time_to_exit": 0},
                  {"name": "down", "probability": 1, "exit_value": 0, "time_to_exit": 0},
              ]}}
    r = E.pwerm(intake, A())
    # probs normalize to 0.5/0.5; r=0 so no discount -> 0.5*100 + 0.5*0 = 50
    assert approx(r["probability_weighted_equity_value"], 50.0)


def test_priced_round_basis_uses_post_money():
    cap = {"fully_diluted": 10000}
    intake = {"financing_rounds": [
        {"round": "Seed", "price_per_share": 1.00, "post_money": 10000},
        {"round": "Series A", "price_per_share": 2.50, "post_money": 25000},
    ]}
    r = E.priced_round_basis(intake, cap, A())
    assert r["round"] == "Series A"
    assert r["basis"] == "post_money"
    assert approx(r["equity_value"], 25000)


def test_priced_round_basis_infers_from_price():
    cap = {"fully_diluted": 10000}
    intake = {"financing_rounds": [{"round": "Seed", "price_per_share": 1.50}]}
    r = E.priced_round_basis(intake, cap, A())
    assert r["basis"] == "price_per_share * fully_diluted_shares"
    assert approx(r["equity_value"], 15000)


def test_round_only_path_produces_value():
    intake = {
        "shares": {"common": 8000, "preferred": [
            {"name": "Series A", "shares": 2000, "invested": 5000,
             "liquidation_multiple": 1.0, "participating": False}
        ]},
        "financials": {"cash": 0, "debt": 0},
        "financing_rounds": [{"round": "Series A", "price_per_share": 2.50,
                              "amount": 5000, "post_money": 25000}],
    }
    errors, _ = E.validate(intake)
    assert errors == []
    r = E.run_value(intake, A())
    assert approx(r["priced_round"]["equity_value"], 25000)
    assert approx(r["reconciliation"]["equity_value"], 25000)
    assert r["headline"]["recommended_409a_strike"] is not None


def test_waterfall_conversion():
    # Non-participating preferred should CONVERT when as-converted beats preference.
    cap = {"common": 1000, "options": 0, "warrants": 0, "fully_diluted": 2000}
    intake = {"shares": {"preferred": [
        {"name": "P", "shares": 1000, "invested": 100, "liquidation_multiple": 1.0,
         "participating": False}
    ]}}
    # Equity 10,000. If P takes pref (100), common pool=1000 -> per share=9.9 ->
    # P as-converted = 1000*~5 ... it converts. After conversion pool=2000.
    wf = E.waterfall(intake, 10000.0, cap, A())
    assert wf["converted_to_common"] == ["P"]
    # pool=2000, per_share=5.0; common(1000)=5000
    assert approx(wf["common_per_share"], 5.0)
    assert approx(wf["value_to_common"], 5000.0)


def test_waterfall_keeps_preference():
    # Low exit: preference beats conversion, so P stays on its preference.
    cap = {"common": 1000, "options": 0, "warrants": 0, "fully_diluted": 2000}
    intake = {"shares": {"preferred": [
        {"name": "P", "shares": 1000, "invested": 900, "liquidation_multiple": 1.0,
         "participating": False}
    ]}}
    wf = E.waterfall(intake, 1000.0, cap, A())
    # pref=900; residual=100; common per share=0.1; P as-conv=1000*0.1=100 < 900 -> stays.
    assert wf["converted_to_common"] == []
    assert approx(wf["preferred_preferences_paid"], 900.0)
    assert approx(wf["value_to_common"], 100.0)


def test_participation_cap_excess_to_common():
    cap = {"common": 1000, "options": 0, "warrants": 0, "fully_diluted": 2000}
    intake = {"shares": {"preferred": [
        {"name": "P", "shares": 1000, "invested": 100, "liquidation_multiple": 1.0,
         "participating": True, "participation_cap": 2}  # total cap = 200
    ]}}
    wf = E.waterfall(intake, 10000.0, cap, A())
    # pref=100; residual=9900; pool=2000; per_share=4.95; P participation gross=4950
    # capped to (200-100)=100 -> excess 4850 redistributes to common.
    assert approx(wf["participation_paid"], 100.0)
    # common = 1000*4.95 + 4850 = 4950 + 4850 = 9800
    assert approx(wf["value_to_common"], 9800.0, tol=1e-3)


def test_strike():
    r = E.strike(2.00, 0.30, A())
    assert approx(r["strike_price"], 1.40)


def test_sensitivity_analysis():
    r = E.sensitivity_analysis(2.00, 0.30, A())
    assert len(r["rows"]) == 9
    base = [x for x in r["rows"] if x["equity_case"] == "base" and x["dlom_case"] == "base_dlom"][0]
    assert approx(base["strike"], 1.40)


def test_valuation_support():
    intake = {"comparables": {"peers": [{"name": "a"}, {"name": "b"}]}}
    results = {
        "comps": {"ev_revenue": {"low": 2, "median": 4, "high": 6}},
        "reconciliation": {"approach_evs": {"dcf": 100, "comps": 200},
                           "blended_enterprise_value": 150},
        "pwerm": {"probability_weighted_equity_value": 120},
        "dlom": {"recommended_dlom": 0.30},
        "opm": {"sigma": 0.60},
        "opm_backsolve": {"round": "A", "implied_post_money": 100,
                          "backsolved_equity_value": 90},
    }
    r = E.valuation_support(intake, results, A())
    assert approx(r["approach_dispersion"], 2 / 3, tol=1e-3)
    assert r["volatility_benchmark"]["review_band"] == "NORMAL"
    assert r["dlom_support"]["review_band"] == "SUPPORTED_RANGE"
    assert len(r["pwerm_sensitivity"]) == 3


def test_legal_audit_flags_missing_controls():
    r = E.legal_audit({"review_controls": {
        "appraiser_engaged": False,
        "valuation_method_reasonable": True,
        "valuation_freshness_confirmed": True,
        "cap_table_source_attached": True,
        "board_approval_planned": True,
        "option_grant_dates_confirmed": False,
        "option_exercise_price_fmv_on_grant_date": True,
        "average_price_period_controls": True,
        "option_modification_reviewed": True,
        "dividend_equivalent_rights_reviewed": True,
        "rsu_documents_reviewed": True,
        "rsu_short_term_deferral_checked": True,
        "rsu_payment_schedule_409a_compliant": True,
        "release_timing_reviewed": True,
        "material_events_reviewed": True,
        "legal_counsel_review_required": True,
        "auditor_review_required": True,
    }}, A())
    assert r["status"] == "REVIEW ITEMS OPEN"
    assert len(r["missing_controls"]) == 2


def test_legal_audit_ready():
    r = E.legal_audit({"review_controls": {
        "appraiser_engaged": True,
        "valuation_method_reasonable": True,
        "valuation_freshness_confirmed": True,
        "cap_table_source_attached": True,
        "board_approval_planned": True,
        "option_grant_dates_confirmed": True,
        "option_exercise_price_fmv_on_grant_date": True,
        "average_price_period_controls": True,
        "option_modification_reviewed": True,
        "dividend_equivalent_rights_reviewed": True,
        "rsu_documents_reviewed": True,
        "rsu_short_term_deferral_checked": True,
        "rsu_payment_schedule_409a_compliant": True,
        "release_timing_reviewed": True,
        "material_events_reviewed": True,
        "legal_counsel_review_required": True,
        "auditor_review_required": True,
    }}, A())
    assert r["status"] == "READY FOR APPRAISER/COUNSEL REVIEW"
    assert r["missing_controls"] == []


def test_reviewer_check_verdicts():
    legal = E.legal_audit({"review_controls": {
        "appraiser_engaged": False,
        "valuation_method_reasonable": True,
        "valuation_freshness_confirmed": True,
        "cap_table_source_attached": True,
        "board_approval_planned": True,
        "option_grant_dates_confirmed": False,
        "option_exercise_price_fmv_on_grant_date": True,
        "average_price_period_controls": True,
        "option_modification_reviewed": True,
        "dividend_equivalent_rights_reviewed": True,
        "rsu_documents_reviewed": True,
        "rsu_short_term_deferral_checked": True,
        "rsu_payment_schedule_409a_compliant": True,
        "release_timing_reviewed": True,
        "material_events_reviewed": True,
        "legal_counsel_review_required": True,
        "auditor_review_required": True,
    }}, A())
    out = R.evaluate("all", {"legal_audit": legal}, {"warnings": []})
    assert out["appraiser"]["verdict"] == "CLEAR WITH CONDITIONS"
    assert out["equity-awards-lawyer"]["verdict"] == "CLEAR WITH CONDITIONS"
    assert out["auditor-tax"]["verdict"] == "CLEAR"


def test_dlom_band():
    early = E.dlom({"dlom_profile": {"stage": "seed", "annual_revenue": 0,
                                     "recently_funded": False, "liquidity_horizon_years": 6,
                                     "exit_probability": 0.1}}, A())
    late = E.dlom({"dlom_profile": {"stage": "late", "annual_revenue": 100e6,
                                    "recently_funded": True, "liquidity_horizon_years": 1,
                                    "exit_probability": 0.9}}, A())
    assert 0.30 <= early["recommended_dlom"] <= 0.35
    assert 0.10 <= late["recommended_dlom"] <= 0.15
    assert early["recommended_dlom"] > late["recommended_dlom"]


def test_compliance_triggers():
    valid = E.compliance({"compliance": {"last_valuation_date": "2026-01-01"},
                          "entity": {"valuation_date": "2026-06-01"},
                          "material_events": {}}, A())
    assert valid["status"] == "VALID"
    stale = E.compliance({"compliance": {"last_valuation_date": "2024-01-01"},
                          "entity": {"valuation_date": "2026-06-01"},
                          "material_events": {"new_financing": True}}, A())
    assert stale["status"] == "REVALUATION REQUIRED"
    assert len(stale["triggers"]) == 2  # stale + new financing


def test_validate_gate():
    errors, _ = E.validate({})  # no basis at all
    assert any("No valuation basis" in e for e in errors)
    errors2, _ = E.validate({"forecasts": {"revenue": [1]}, "shares": {"common": 1}})
    assert errors2 == []


def test_opm_backsolve_recovers_invested():
    # The backsolved equity, fed back through OPM, allocates ~invested to the series.
    cap = {"common": 8000, "options": 0, "warrants": 0, "fully_diluted": 10000}
    intake = {
        "shares": {"preferred": [
            {"name": "A", "shares": 2000, "invested": 5000, "liquidation_multiple": 1.0}]},
        "financing_rounds": [{"round": "A", "price_per_share": 2.5, "amount": 5000,
                              "post_money": 25000}],
        "opm": {"sigma": 0.6, "years": 4, "rate": 0.04},
    }
    bs = E.opm_backsolve(intake, cap, A())
    E_val = bs["backsolved_equity_value"]
    # re-derive series value at E_val
    L = 5000
    up = E.bs_call(E_val, L, 4, 0.04, 0.6)
    series_val = (E_val - up) * (5000 / L) + up * (2000 / 10000)
    assert approx(series_val, 5000, tol=1e-2)


# --------------------------------------------------------------------------- #
def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith("test_") and callable(v)]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"  ERROR {t.__name__}: {type(e).__name__}: {e}")
    print("-" * 50)
    print(f"{len(tests) - failed}/{len(tests)} passed")
    if failed:
        sys.exit(1)
    print("ALL PASSED")


if __name__ == "__main__":
    _run()
