"""Tests for PACER/ECF Meta-Generator."""
import pytest
from ftc_engine.pacer_meta import (
    generate_js44,
    generate_summons,
    generate_all_summonses,
    generate_corporate_disclosure,
    generate_all_disclosures,
    generate_notice_of_interested_parties,
    generate_filing_package,
    format_js44,
    format_summons,
    format_filing_package,
    JS44CoverSheet,
    Summons,
    CorporateDisclosure,
    PacerFilingPackage,
    CLAIM_NATURE_CODES,
    _determine_nature_of_suit,
    _is_corporate_party,
    _get_citizenship_code,
)


@pytest.fixture
def corporate_case(minimal_case):
    """Case with corporate parties for PACER testing."""
    minimal_case["parties"]["defendants"] = [
        {"name": "MegaCorp LLC", "type": "private", "capacity": "individual",
         "citizenship": "Delaware", "entity_type": "corporation",
         "principal_place_of_business": "New York"},
        {"name": "SubCorp Inc", "type": "private", "capacity": "individual",
         "citizenship": "California", "entity_type": "corporation"},
    ]
    minimal_case["claims_requested"] = ["1983_fourth_excessive_force"]
    minimal_case["relief_requested"] = ["money", "fees"]
    minimal_case["attorney"] = {
        "name": "John Lawyer",
        "bar_number": "12345",
        "address": "123 Main St",
        "phone": "555-1234",
    }
    return minimal_case


@pytest.fixture
def federal_pacer_case(minimal_case):
    """Case with federal defendant for PACER testing."""
    minimal_case["parties"]["defendants"] = [
        {"name": "Department of Veterans Affairs", "type": "federal",
         "capacity": "official", "citizenship": "Federal", "entity_type": "federal_agency"},
    ]
    minimal_case["claims_requested"] = ["ftca_negligence"]
    minimal_case["exhaustion"] = {"ftca_admin_claim_filed": True}
    return minimal_case


class TestNatureOfSuit:
    """Test nature-of-suit code determination."""

    def test_excessive_force_code(self):
        assert CLAIM_NATURE_CODES["1983_fourth_excessive_force"] == ("440", "Other Civil Rights")

    def test_title_vii_code(self):
        assert CLAIM_NATURE_CODES["title_vii_disparate_treatment"] == ("442", "Employment - Civil Rights")

    def test_ftca_code(self):
        assert CLAIM_NATURE_CODES["ftca_negligence"] == ("360", "Personal Injury - Other")

    def test_determination_from_case(self, corporate_case):
        code, text = _determine_nature_of_suit(corporate_case)
        assert code == "440"

    def test_unknown_claim_fallback(self):
        case = {"claims_requested": ["unknown_xyz"]}
        code, text = _determine_nature_of_suit(case)
        assert code  # Should return something


class TestJS44:
    """Test JS-44 Civil Cover Sheet generation."""

    def test_js44_returns_dataclass(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert isinstance(sheet, JS44CoverSheet)

    def test_js44_has_party_names(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert sheet.plaintiff_name == "Jane Doe"
        assert sheet.defendant_name == "MegaCorp LLC"

    def test_js44_nature_of_suit(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert sheet.nature_of_suit_code

    def test_js44_cause_of_action(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert sheet.cause_of_action  # Should have statutory citation

    def test_js44_jury_demand(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert sheet.jury_demand == "Yes"  # Has "money" in relief

    def test_js44_no_money_no_jury(self, minimal_case):
        minimal_case["claims_requested"] = ["1983_fourth_excessive_force"]
        minimal_case["relief_requested"] = ["injunction"]
        sheet = generate_js44(minimal_case)
        assert sheet.jury_demand == "No"

    def test_js44_attorney_info(self, corporate_case):
        sheet = generate_js44(corporate_case)
        assert sheet.plaintiff_attorney == "John Lawyer"
        assert sheet.plaintiff_attorney_bar == "12345"


class TestSummons:
    """Test summons generation."""

    def test_summons_for_single_defendant(self, corporate_case):
        summons = generate_summons(corporate_case, 0)
        assert isinstance(summons, Summons)
        assert summons.defendant_name == "MegaCorp LLC"

    def test_summons_response_days_default(self, corporate_case):
        summons = generate_summons(corporate_case, 0)
        assert summons.response_days == 21

    def test_summons_response_days_federal(self, federal_pacer_case):
        summons = generate_summons(federal_pacer_case, 0)
        assert summons.response_days == 60

    def test_summons_invalid_index_raises(self, corporate_case):
        with pytest.raises(IndexError):
            generate_summons(corporate_case, 99)

    def test_all_summonses_count(self, corporate_case):
        summonses = generate_all_summonses(corporate_case)
        assert len(summonses) == 2  # Two defendants

    def test_summons_has_court_name(self, corporate_case):
        summons = generate_summons(corporate_case, 0)
        assert "United States District Court" in summons.court_name


class TestCorporateDisclosure:
    """Test FRCP 7.1 corporate disclosure."""

    def test_corporate_party_detected(self):
        assert _is_corporate_party({"entity_type": "corporation"}) is True
        assert _is_corporate_party({"entity_type": "llc"}) is True
        assert _is_corporate_party({"entity_type": "individual"}) is False

    def test_disclosure_generated(self, corporate_case):
        party = corporate_case["parties"]["defendants"][0]
        disc = generate_corporate_disclosure(corporate_case, party)
        assert isinstance(disc, CorporateDisclosure)
        assert disc.party_name == "MegaCorp LLC"

    def test_all_disclosures_for_corporate_parties(self, corporate_case):
        discs = generate_all_disclosures(corporate_case)
        # Both defendants are corporate + plaintiff is corporate in minimal_case
        corp_parties = sum(
            1 for p in (corporate_case["parties"]["plaintiffs"] + corporate_case["parties"]["defendants"])
            if _is_corporate_party(p)
        )
        assert len(discs) == corp_parties

    def test_no_disclosure_for_individuals(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "John Smith", "type": "individual", "entity_type": "individual"},
        ]
        discs = generate_all_disclosures(minimal_case)
        individual_discs = [d for d in discs if d.party_name == "John Smith"]
        assert len(individual_discs) == 0


class TestCitizenship:
    """Test citizenship code generation."""

    def test_individual_citizen(self):
        code = _get_citizenship_code({"entity_type": "individual", "citizenship": "Florida"})
        assert "Florida" in code

    def test_corporation_with_ppb(self):
        code = _get_citizenship_code({
            "entity_type": "corporation",
            "citizenship": "Delaware",
            "principal_place_of_business": "New York",
        })
        assert "Delaware" in code
        assert "New York" in code

    def test_federal_agency(self):
        code = _get_citizenship_code({"entity_type": "federal_agency"})
        assert "Government" in code


class TestFilingPackage:
    """Test complete filing package generation."""

    def test_package_has_all_components(self, corporate_case):
        pkg = generate_filing_package(corporate_case)
        assert isinstance(pkg, PacerFilingPackage)
        assert pkg.js44 is not None
        assert len(pkg.summonses) >= 1
        assert pkg.generated_at

    def test_package_warnings_for_missing_attorney(self, minimal_case):
        minimal_case["claims_requested"] = ["1983_fourth_excessive_force"]
        pkg = generate_filing_package(minimal_case)
        assert any("attorney" in w.lower() for w in pkg.warnings)

    def test_notice_of_interested_parties(self, corporate_case):
        notice = generate_notice_of_interested_parties(corporate_case)
        assert "NOTICE OF INTERESTED PARTIES" in notice
        assert "Jane Doe" in notice
        assert "MegaCorp LLC" in notice


class TestFormatting:
    """Test output formatting."""

    def test_format_js44(self, corporate_case):
        sheet = generate_js44(corporate_case)
        output = format_js44(sheet)
        assert "JS-44 CIVIL COVER SHEET" in output
        assert sheet.plaintiff_name in output

    def test_format_summons(self, corporate_case):
        summons = generate_summons(corporate_case, 0)
        output = format_summons(summons)
        assert "SUMMONS" in output
        assert summons.defendant_name in output

    def test_format_filing_package(self, corporate_case):
        pkg = generate_filing_package(corporate_case)
        output = format_filing_package(pkg)
        assert "PACER/ECF FILING PACKAGE" in output
        assert "Documents generated:" in output
