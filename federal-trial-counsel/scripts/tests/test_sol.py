"""Tests for ftc_engine.sol - Statute of Limitations Calculator."""
import pytest
from datetime import date, timedelta
from ftc_engine.sol import calculate_sol, calculate_all_sol, SOL_DAYS


class TestCalculateSOL:
    def test_known_claim_returns_result(self):
        result = calculate_sol("1983_fourth_excessive_force", "2025-06-15")
        assert result.claim_key == "1983_fourth_excessive_force"
        assert result.claim_name != ""
        assert isinstance(result.deadline, date)
        assert isinstance(result.days_remaining, int)

    def test_unknown_claim_raises(self):
        with pytest.raises(ValueError, match="Unknown claim"):
            calculate_sol("nonexistent", "2025-01-01")

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError, match="Invalid date"):
            calculate_sol("1983_fourth_excessive_force", "not-a-date")

    def test_future_date_raises(self):
        future = (date.today() + timedelta(days=30)).isoformat()
        with pytest.raises(ValueError, match="in the future"):
            calculate_sol("1983_fourth_excessive_force", future)


class TestSOLStatus:
    def test_safe_status(self):
        recent = (date.today() - timedelta(days=30)).isoformat()
        result = calculate_sol("1983_fourth_excessive_force", recent)
        assert result.status == "safe"
        assert result.days_remaining > 90

    def test_expired_status(self):
        old = (date.today() - timedelta(days=2000)).isoformat()
        result = calculate_sol("1983_fourth_excessive_force", old)
        assert result.status == "expired"
        assert result.days_remaining < 0

    def test_urgent_status(self):
        # 1983 claims have 1461-day SOL (4 years)
        # Place injury date so remaining days are between 0 and 90
        almost_expired = (date.today() - timedelta(days=1400)).isoformat()
        result = calculate_sol("1983_fourth_excessive_force", almost_expired)
        assert result.status == "urgent"
        assert 0 <= result.days_remaining < 90


class TestSOLDays:
    def test_1983_claims_4_years(self):
        assert SOL_DAYS["1983_fourth_excessive_force"] == 1461

    def test_title_vii_90_days(self):
        assert SOL_DAYS["title_vii_disparate_treatment"] == 90

    def test_ftca_2_years(self):
        assert SOL_DAYS["ftca_negligence"] == 730

    def test_1986_failure_1_year(self):
        assert SOL_DAYS["1986_failure_to_prevent"] == 365

    def test_tax_wrongful_levy_9_months(self):
        assert SOL_DAYS["tax_wrongful_levy"] == 274

    def test_all_claims_have_sol_entry(self):
        from ftc_engine.claims import CLAIM_LIBRARY
        for key in CLAIM_LIBRARY:
            assert key in SOL_DAYS, f"{key} missing from SOL_DAYS"


class TestCalculateAllSOL:
    def test_multiple_claims(self):
        claims = ["1983_fourth_excessive_force", "1983_fourth_false_arrest"]
        results = calculate_all_sol(claims, "2025-06-15")
        assert len(results) == 2
        assert results[0].claim_key == claims[0]
        assert results[1].claim_key == claims[1]


class TestTollingNotes:
    def test_civil_rights_tolling(self):
        result = calculate_sol("1983_fourth_excessive_force", "2025-06-15")
        assert any("discovery" in n.lower() or "tolling" in n.lower() or "continuing" in n.lower()
                    for n in result.tolling_notes)

    def test_title_vii_90_day_note(self):
        result = calculate_sol("title_vii_disparate_treatment", "2025-06-15")
        assert any("90-day" in n or "right-to-sue" in n for n in result.tolling_notes)

    def test_ftca_admin_note(self):
        result = calculate_sol("ftca_negligence", "2025-06-15")
        assert any("SF-95" in n or "admin" in n.lower() for n in result.tolling_notes)
