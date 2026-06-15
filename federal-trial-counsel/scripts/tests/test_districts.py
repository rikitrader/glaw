"""Tests for District Portability Layer."""
import json
import pytest
from pathlib import Path
from ftc_engine.districts import (
    get_district,
    list_districts,
    get_active_district,
    set_active_district,
    get_sol_days_for_district,
    get_page_limits,
    get_formatting_config,
    get_district_name,
    format_district_info,
    format_district_list,
    DistrictConfig,
    DistrictContext,
    DISTRICTS,
    _CONFIG_FILE,
    _save_config,
    _load_config,
)


class TestDistrictLookup:
    """Test district lookup by code."""

    def test_known_code_returns_config(self):
        d = get_district("mdfl")
        assert d is not None
        assert d.name == "Middle District of Florida"

    def test_unknown_code_returns_none(self):
        assert get_district("zzzzz") is None

    def test_case_insensitive(self):
        d = get_district("SDFL")
        assert d is not None
        assert d.code == "sdfl"

    def test_list_all_returns_sorted(self):
        districts = list_districts()
        assert len(districts) >= 7
        codes = [d.code for d in districts]
        assert codes == sorted(codes)

    def test_all_districts_have_required_fields(self):
        for d in DISTRICTS.values():
            assert d.code
            assert d.name
            assert d.circuit
            assert d.state
            assert d.sol_personal_injury_years > 0
            assert d.motion_page_limit > 0
            assert d.font_name
            assert d.font_size_pt > 0


class TestDistrictConfig:
    """Test specific district configurations."""

    def test_mdfl_florida_reference(self):
        d = get_district("mdfl")
        assert d.circuit == "11th Circuit"
        assert d.state == "Florida"
        assert d.sol_personal_injury_years == 4.0
        assert d.mediation_required is True
        assert "Orlando" in d.divisions

    def test_sdny_three_year_sol(self):
        d = get_district("sdny")
        assert d.sol_personal_injury_years == 3.0
        assert d.state == "New York"
        assert d.circuit == "2nd Circuit"

    def test_edva_rocket_docket(self):
        d = get_district("edva")
        assert d.response_days == 11
        assert d.reply_days == 3
        assert any("Rocket Docket" in r for r in d.special_rules)

    def test_ndill_strict_page_limits(self):
        d = get_district("ndill")
        assert d.motion_page_limit == 15
        assert any("15 pages" in r for r in d.special_rules)

    def test_meet_and_confer_varies(self):
        mdfl = get_district("mdfl")
        ndcal = get_district("ndcal")
        assert mdfl.meet_and_confer_method == "phone_or_in_person"
        assert ndcal.meet_and_confer_method == "any"

    def test_ddc_generous_page_limits(self):
        d = get_district("ddc")
        assert d.motion_page_limit == 45
        assert d.state == "District of Columbia"


class TestActiveDistrict:
    """Test active district get/set with config persistence."""

    def test_default_is_mdfl(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ftc_engine.districts._CONFIG_FILE", tmp_path / "config.json")
        ctx = get_active_district()
        assert ctx.config.code == "mdfl"

    def test_set_and_get_roundtrip(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ftc_engine.districts._CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("ftc_engine.districts._CONFIG_DIR", tmp_path)
        set_active_district("sdny", "Manhattan")
        ctx = get_active_district()
        assert ctx.config.code == "sdny"
        assert ctx.division == "Manhattan"

    def test_invalid_code_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ftc_engine.districts._CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("ftc_engine.districts._CONFIG_DIR", tmp_path)
        with pytest.raises(ValueError, match="Unknown district"):
            set_active_district("zzzzz")

    def test_invalid_division_raises(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ftc_engine.districts._CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("ftc_engine.districts._CONFIG_DIR", tmp_path)
        with pytest.raises(ValueError, match="Unknown division"):
            set_active_district("mdfl", "Atlantis")

    def test_default_division_set_automatically(self, tmp_path, monkeypatch):
        monkeypatch.setattr("ftc_engine.districts._CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("ftc_engine.districts._CONFIG_DIR", tmp_path)
        ctx = set_active_district("ndcal")
        assert ctx.division == "San Francisco"


class TestSOLOverride:
    """Test state-aware SOL day calculations."""

    def test_florida_four_years(self):
        days = get_sol_days_for_district("1983_fourth_excessive_force", "mdfl")
        assert abs(days - 1461) <= 1  # ~4 years

    def test_california_two_years(self):
        days = get_sol_days_for_district("1983_fourth_excessive_force", "ndcal")
        assert abs(days - 731) <= 1  # ~2 years

    def test_new_york_three_years(self):
        days = get_sol_days_for_district("1983_fourth_excessive_force", "sdny")
        assert abs(days - 1096) <= 1  # ~3 years

    def test_non_state_sol_claim_unchanged(self):
        """Title VII 90-day SOL should NOT be affected by district."""
        days = get_sol_days_for_district("title_vii_disparate_treatment", "ndcal")
        assert days == 90

    def test_unknown_district_uses_default(self):
        days = get_sol_days_for_district("1983_fourth_excessive_force", "zzzzz")
        assert days == 1461  # Falls back to default


class TestFormattingConfig:
    """Test district-specific formatting and display."""

    def test_formatting_config_returns_dict(self):
        config = get_formatting_config("mdfl")
        assert config["font_name"] == "Times New Roman"
        assert config["font_size_pt"] == 12
        assert config["line_spacing"] == 2.0
        assert config["margin_inches"] == 1.0

    def test_page_limits_per_district(self):
        mdfl = get_page_limits("mdfl")
        ndill = get_page_limits("ndill")
        assert mdfl["motion"] == 25
        assert ndill["motion"] == 15

    def test_format_district_info_output(self):
        config = get_district("mdfl")
        output = format_district_info(config)
        assert "Middle District of Florida" in output
        assert "11th Circuit" in output
        assert "Florida" in output
        assert "25 pages" in output

    def test_format_district_list_output(self):
        output = format_district_list()
        assert "mdfl" in output
        assert "sdny" in output
        assert "ndcal" in output

    def test_district_name_helper(self):
        assert get_district_name("sdfl") == "Southern District of Florida"
        assert get_district_name("zzzzz") == "Middle District of Florida"  # fallback
