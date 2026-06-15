"""Tests for ftc_engine.risk - MTD Risk Scoring Engine."""
import pytest
from ftc_engine.risk import calculate_mtd_risk, _assess_standing, _assess_plausibility, RISK_WEIGHTS


class TestCalculateMTDRisk:
    def test_sample_case_returns_result(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        assert 0 <= result.overall_score <= 100
        assert result.risk_level in ("low", "medium", "high", "critical")
        assert len(result.factors) > 0

    def test_unknown_claim_returns_medium(self, sample_case):
        result = calculate_mtd_risk(sample_case, "nonexistent")
        assert result.overall_score == 50
        assert result.risk_level == "medium"

    def test_risk_levels(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        if result.overall_score < 25:
            assert result.risk_level == "low"
        elif result.overall_score < 50:
            assert result.risk_level == "medium"
        elif result.overall_score < 75:
            assert result.risk_level == "high"
        else:
            assert result.risk_level == "critical"


class TestStandingAssessment:
    def test_no_injury_scores_high(self):
        factor = _assess_standing(
            [{"event": "something happened"}],
            {"defendants": [{"name": "Doe"}]},
            [],
        )
        assert factor.score >= 40

    def test_complete_standing_scores_low(self):
        factor = _assess_standing(
            [{"event": "assault", "harm": "broken arm", "actors": ["Officer Smith"]}],
            {"defendants": [{"name": "Officer Smith"}]},
            ["money"],
        )
        assert factor.score == 0

    def test_no_relief_adds_risk(self):
        factor = _assess_standing(
            [{"event": "assault", "harm": "injury", "actors": ["Doe"]}],
            {"defendants": [{"name": "Doe"}]},
            [],
        )
        assert factor.score >= 20


class TestSOLAssessment:
    def test_expired_sol_scores_critical(self, sample_case):
        sample_case["limitations"]["key_dates"]["injury_date"] = "2018-01-01"
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        assert sol_factor.score >= 90

    def test_safe_sol_scores_zero(self, sample_case):
        sample_case["limitations"]["key_dates"]["injury_date"] = "2025-12-01"
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        assert sol_factor.score == 0

    def test_analogous_sol_flags_for_review(self, sample_case):
        """Claims with 'Analogous state SOL' should score 30 (flag for verification)."""
        result = calculate_mtd_risk(sample_case, "lanham_trademark_infringement")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        assert sol_factor.score == 30
        assert "varies" in sol_factor.issue.lower() or "analogous" in sol_factor.issue.lower()

    def test_missing_injury_date_scores_moderate(self, minimal_case):
        result = calculate_mtd_risk(minimal_case, "1983_fourth_excessive_force")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        assert sol_factor.score == 30


class TestExhaustionAssessment:
    def test_no_exhaustion_required_scores_zero(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 0

    def test_eeoc_not_filed_scores_critical(self, employment_case):
        employment_case["exhaustion"]["eeoc_charge_filed"] = False
        result = calculate_mtd_risk(employment_case, "title_vii_disparate_treatment")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 90

    def test_eeoc_unknown_scores_moderate(self, employment_case):
        employment_case["exhaustion"]["eeoc_charge_filed"] = "unknown"
        result = calculate_mtd_risk(employment_case, "title_vii_disparate_treatment")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 50

    def test_ftca_not_filed_scores_critical(self, federal_defendant_case):
        federal_defendant_case["exhaustion"]["ftca_admin_claim_filed"] = False
        result = calculate_mtd_risk(federal_defendant_case, "ftca_negligence")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 90

    def test_ftca_unknown_scores_moderate(self, federal_defendant_case):
        federal_defendant_case["exhaustion"]["ftca_admin_claim_filed"] = "unknown"
        result = calculate_mtd_risk(federal_defendant_case, "ftca_negligence")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 50

    def test_erisa_not_completed(self, minimal_case):
        minimal_case["exhaustion"]["erisa_appeal_done"] = False
        result = calculate_mtd_risk(minimal_case, "erisa_502a1b_benefits")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 70

    def test_apa_no_final_action(self, minimal_case):
        minimal_case["exhaustion"]["agency_final_action"] = False
        result = calculate_mtd_risk(minimal_case, "apa_arbitrary_capricious")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 80

    def test_plra_not_completed(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "Warden", "type": "officer", "capacity": "individual", "citizenship": "FL"}
        ]
        minimal_case["exhaustion"]["plra_exhaustion_done"] = False
        result = calculate_mtd_risk(minimal_case, "1983_eighth_deliberate_indifference")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 90

    def test_plra_unknown_scores_moderate(self, minimal_case):
        minimal_case["exhaustion"]["plra_exhaustion_done"] = "unknown"
        result = calculate_mtd_risk(minimal_case, "1983_eighth_deliberate_indifference")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 50

    def test_administrative_not_done(self, minimal_case):
        minimal_case["exhaustion"]["administrative_exhaustion_done"] = False
        result = calculate_mtd_risk(minimal_case, "habeas_detention_challenge")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 70

    def test_administrative_unknown(self, minimal_case):
        minimal_case["exhaustion"]["administrative_exhaustion_done"] = "unknown"
        result = calculate_mtd_risk(minimal_case, "habeas_detention_challenge")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 40

    def test_irs_not_filed(self, minimal_case):
        minimal_case["exhaustion"]["irs_claim_filed"] = False
        result = calculate_mtd_risk(minimal_case, "tax_refund_suit")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score >= 90

    def test_irs_unknown(self, minimal_case):
        minimal_case["exhaustion"]["irs_claim_filed"] = "unknown"
        result = calculate_mtd_risk(minimal_case, "tax_refund_suit")
        ex_factor = next(f for f in result.factors if f.category == "exhaustion")
        assert ex_factor.score == 50


class TestImmunityAssessment:
    def test_qualified_immunity_risk(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        imm_factor = next(f for f in result.factors if f.category == "immunity")
        assert imm_factor.score >= 0

    def test_eleventh_amendment_for_state(self, sample_case):
        sample_case["parties"]["defendants"] = [
            {"name": "State Agency", "type": "state", "capacity": "official", "citizenship": "FL"}
        ]
        result = calculate_mtd_risk(sample_case, "copyright_infringement")
        imm_factor = next(f for f in result.factors if f.category == "immunity")
        assert imm_factor.score >= 50


class TestMonellAssessment:
    def test_monell_triggered_for_municipal(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_monell_municipal_liability")
        monell_factor = next((f for f in result.factors if f.category == "monell"), None)
        assert monell_factor is not None

    def test_no_monell_for_private_defendant(self, minimal_case):
        result = calculate_mtd_risk(minimal_case, "fcra_inaccurate_reporting")
        monell_factor = next((f for f in result.factors if f.category == "monell"), None)
        # After the Monell-visibility fix, the factor is always present; for
        # non-applicable claims it scores 0 with an explicit "Not applicable" note
        # so users can see that Monell was considered and ruled out.
        assert monell_factor is not None
        assert monell_factor.score == 0
        assert "Not applicable" in monell_factor.issue


class TestPlausibilityAssessment:
    def test_detailed_facts_low_risk(self):
        facts = [
            {"event": "assault", "date": "2025-01-01", "actors": ["Doe"],
             "documents": ["video"], "harm": "broken arm"},
        ]
        factor = _assess_plausibility(facts, "test")
        assert factor.score <= 70

    def test_empty_facts_max_risk(self):
        factor = _assess_plausibility([], "test")
        assert factor.score == 100


class TestRule9bAssessment:
    def test_rule_9b_triggered_for_rico(self, sample_case):
        result = calculate_mtd_risk(sample_case, "rico_1962c")
        r9b = next((f for f in result.factors if f.category == "rule_9b"), None)
        assert r9b is not None

    def test_rule_9b_not_triggered_for_1983(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        r9b = next((f for f in result.factors if f.category == "rule_9b"), None)
        assert r9b is None

    def test_rule_9b_scores_high_without_details(self, minimal_case):
        minimal_case["facts"] = [{"event": "fraud scheme"}]
        result = calculate_mtd_risk(minimal_case, "rico_1962c")
        r9b = next((f for f in result.factors if f.category == "rule_9b"), None)
        assert r9b is not None
        assert r9b.score >= 30


class TestDamagesAssessment:
    def test_no_harm_scores_high(self, minimal_case):
        result = calculate_mtd_risk(minimal_case, "fcra_inaccurate_reporting")
        dmg = next(f for f in result.factors if f.category == "damages")
        assert dmg.score >= 40

    def test_documented_harm_scores_lower(self, sample_case):
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        dmg = next(f for f in result.factors if f.category == "damages")
        assert dmg.score < 60


class TestSOLEdgeCases:
    def test_invalid_date_format(self, sample_case):
        sample_case["limitations"]["key_dates"]["injury_date"] = "June 2025"
        result = calculate_mtd_risk(sample_case, "1983_fourth_excessive_force")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        assert sol_factor.score == 30  # Invalid format → moderate

    def test_90_day_sol_parsing(self, employment_case):
        """Title VII has 90-day SOL — should be parsed correctly."""
        employment_case["limitations"]["key_dates"]["injury_date"] = "2025-03-01"
        result = calculate_mtd_risk(employment_case, "title_vii_disparate_treatment")
        sol_factor = next(f for f in result.factors if f.category == "sol")
        # 90-day SOL from March 2025 is long expired by now
        assert sol_factor.score >= 40

    def test_sovereign_immunity_for_federal(self, federal_defendant_case):
        result = calculate_mtd_risk(federal_defendant_case, "ftca_negligence")
        imm = next(f for f in result.factors if f.category == "immunity")
        assert imm.score >= 40


class TestRiskWeights:
    def test_weights_sum_reasonable(self):
        total = sum(RISK_WEIGHTS.values())
        assert 90 <= total <= 120

    def test_plausibility_highest_weight(self):
        assert RISK_WEIGHTS["plausibility"] >= 15
        assert RISK_WEIGHTS["immunity"] >= 15
