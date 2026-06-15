"""Tests for Rule 11 Duty Monitor."""
import pytest
from ftc_engine.rule11_monitor import (
    check_claim_viability,
    generate_monitor_report,
    format_monitor_report,
    ViabilityCheck,
    ViabilityIssue,
    MonitorReport,
    VIABILITY_KNOWLEDGE,
    _check_built_in_viability,
    _check_exhaustion_compliance,
    _check_sol_compliance,
    _check_immunity_exposure,
)


@pytest.fixture
def bivens_case(minimal_case):
    """Case with Bivens claim for viability testing."""
    minimal_case["claims_requested"] = ["bivens_fourth_search_seizure"]
    minimal_case["parties"]["defendants"] = [
        {"name": "Agent Smith", "type": "federal", "capacity": "individual",
         "entity_type": "individual", "citizenship": "Virginia"},
    ]
    minimal_case["limitations"]["key_dates"]["injury_date"] = "2025-01-15"
    return minimal_case


@pytest.fixture
def exhaustion_case(minimal_case):
    """Case with exhaustion-sensitive claims."""
    minimal_case["claims_requested"] = ["title_vii_disparate_treatment"]
    minimal_case["exhaustion"] = {"eeoc_charge_filed": False}
    return minimal_case


class TestViabilityKnowledge:
    """Test built-in knowledge base."""

    def test_bivens_has_egbert_citation(self):
        issues = VIABILITY_KNOWLEDGE.get("bivens_fourth_search_seizure", [])
        assert any("Egbert" in i.citation for i in issues)

    def test_excessive_force_has_entries(self):
        issues = VIABILITY_KNOWLEDGE.get("1983_fourth_excessive_force", [])
        assert len(issues) > 0

    def test_apa_has_loper_bright(self):
        issues = VIABILITY_KNOWLEDGE.get("apa_arbitrary_capricious", [])
        assert any("Loper Bright" in i.citation for i in issues)

    def test_ftca_has_exhaustion(self):
        issues = VIABILITY_KNOWLEDGE.get("ftca_negligence", [])
        assert any("SF-95" in i.description or "exhaustion" in i.description.lower() for i in issues)

    def test_unknown_claim_returns_empty(self):
        issues = _check_built_in_viability("unknown_claim_xyz")
        assert issues == []


class TestViabilityCheck:
    """Test individual claim viability checks."""

    def test_check_returns_dataclass(self, bivens_case):
        check = check_claim_viability(bivens_case, "bivens_fourth_search_seizure")
        assert isinstance(check, ViabilityCheck)

    def test_bivens_flagged_questionable(self, bivens_case):
        check = check_claim_viability(bivens_case, "bivens_fourth_search_seizure")
        assert check.status in ("questionable", "non_viable")

    def test_viable_claim_detected(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        sample_case["limitations"] = {"key_dates": {"injury_date": "2025-06-15"}}
        check = check_claim_viability(sample_case, "1983_fourth_excessive_force")
        assert check.status in ("viable", "warning")

    def test_confidence_range(self, bivens_case):
        check = check_claim_viability(bivens_case, "bivens_fourth_search_seizure")
        assert 0.0 <= check.confidence <= 1.0

    def test_data_source_default_offline(self, bivens_case):
        check = check_claim_viability(bivens_case, "bivens_fourth_search_seizure")
        assert check.data_source == "built_in"

    def test_unknown_claim_still_checks(self, minimal_case):
        check = check_claim_viability(minimal_case, "unknown_claim_xyz")
        assert isinstance(check, ViabilityCheck)


class TestExhaustionCompliance:
    """Test exhaustion checking."""

    def test_eeoc_not_filed_critical(self, exhaustion_case):
        issues = _check_exhaustion_compliance(exhaustion_case, "title_vii_disparate_treatment")
        assert any(i.severity == "critical" for i in issues)

    def test_eeoc_filed_no_issue(self, exhaustion_case):
        exhaustion_case["exhaustion"]["eeoc_charge_filed"] = True
        issues = _check_exhaustion_compliance(exhaustion_case, "title_vii_disparate_treatment")
        assert not any(i.severity == "critical" for i in issues)

    def test_ftca_not_filed_critical(self, minimal_case):
        minimal_case["exhaustion"] = {"ftca_admin_claim_filed": False}
        issues = _check_exhaustion_compliance(minimal_case, "ftca_negligence")
        assert any(i.severity == "critical" for i in issues)

    def test_no_exhaustion_required(self, minimal_case):
        issues = _check_exhaustion_compliance(minimal_case, "1983_fourth_excessive_force")
        assert issues == []


class TestSOLCompliance:
    """Test SOL cross-checking."""

    def test_no_injury_date_no_issues(self, minimal_case):
        issues = _check_sol_compliance(minimal_case, "1983_fourth_excessive_force")
        assert issues == []

    def test_recent_injury_no_sol_issue(self, minimal_case):
        minimal_case["limitations"]["key_dates"]["injury_date"] = "2025-06-15"
        issues = _check_sol_compliance(minimal_case, "1983_fourth_excessive_force")
        # Should not flag critical if within SOL
        assert not any(i.severity == "critical" and "EXPIRED" in i.description for i in issues)


class TestImmunityExposure:
    """Test immunity risk detection."""

    def test_qualified_immunity_flagged(self, sample_case):
        sample_case["parties"]["defendants"] = [
            {"name": "Officer Brown", "type": "officer", "capacity": "individual"},
        ]
        issues = _check_immunity_exposure(sample_case, "1983_fourth_excessive_force")
        assert any("qualified" in i.description.lower() or "immunity" in i.description.lower() for i in issues)

    def test_sovereign_immunity_flagged(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "USA", "type": "federal", "capacity": "official"},
        ]
        issues = _check_immunity_exposure(minimal_case, "ftca_negligence")
        assert any("sovereign" in i.description.lower() for i in issues)

    def test_no_immunity_for_private_defendant(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "Corp Inc", "type": "private", "entity_type": "corporation"},
        ]
        issues = _check_immunity_exposure(minimal_case, "1983_fourth_excessive_force")
        # Private parties don't get qualified/sovereign immunity
        assert not any("qualified" in i.description.lower() for i in issues)


class TestMonitorReport:
    """Test full monitor report generation."""

    def test_report_returns_dataclass(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        report = generate_monitor_report(sample_case)
        assert isinstance(report, MonitorReport)

    def test_report_checks_all_claims(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force", "1983_fourth_false_arrest"]
        report = generate_monitor_report(sample_case)
        assert report.claims_checked == 2

    def test_bivens_report_non_compliant(self, bivens_case):
        report = generate_monitor_report(bivens_case)
        assert report.overall_compliance in ("review_needed", "non_compliant")

    def test_critical_flags_populated(self, bivens_case):
        report = generate_monitor_report(bivens_case)
        assert len(report.critical_flags) > 0

    def test_case_name_in_report(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        report = generate_monitor_report(sample_case)
        assert "v." in report.case_name

    def test_next_review_recommended(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        report = generate_monitor_report(sample_case)
        assert report.next_review_recommended


class TestFormatting:
    """Test report formatting."""

    def test_format_returns_string(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        report = generate_monitor_report(sample_case)
        output = format_monitor_report(report)
        assert isinstance(output, str)
        assert "RULE 11 DUTY MONITOR" in output

    def test_verbose_mode(self, bivens_case):
        report = generate_monitor_report(bivens_case)
        brief = format_monitor_report(report, verbose=False)
        verbose = format_monitor_report(report, verbose=True)
        assert len(verbose) >= len(brief)

    def test_format_contains_claim_keys(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        report = generate_monitor_report(sample_case)
        output = format_monitor_report(report)
        assert "1983_fourth_excessive_force" in output
