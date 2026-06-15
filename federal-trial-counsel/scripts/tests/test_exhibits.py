"""Tests for Exhibit Metadata Extractor."""
import pytest
from pathlib import Path
from ftc_engine.exhibits import (
    generate_exhibit_index,
    format_exhibit_index,
    ExhibitIndex,
    ExhibitEntry,
    DOCUMENT_TYPES,
    AUTHENTICATION_METHODS,
    _classify_document_type,
    _suggest_authentication,
    _anticipate_objections,
    _extract_date_from_text,
    _number_exhibit,
    _map_to_claims,
)


@pytest.fixture
def exhibit_case(sample_case):
    """Sample case with rich document references."""
    sample_case["facts"] = [
        {"date": "2025-06-15", "event": "Use of force incident",
         "actors": ["Officer Brown"], "harm": "Broken arm",
         "documents": ["Body camera footage", "Medical records from Tampa General Hospital"],
         "location": "Tampa, FL"},
        {"date": "2025-06-15", "event": "Arrest and booking",
         "actors": ["Officer Brown"], "harm": "False imprisonment",
         "documents": ["Arrest report", "Booking records"],
         "location": "Tampa, FL"},
        {"date": "2025-07-01", "event": "Email from police chief",
         "actors": ["Chief Rivera"], "harm": "",
         "documents": ["Email correspondence from Chief Rivera"],
         "location": "Tampa, FL"},
    ]
    sample_case["claims_requested"] = [
        "1983_fourth_excessive_force", "1983_fourth_false_arrest",
    ]
    return sample_case


class TestDocumentClassification:
    """Test document type classification."""

    def test_medical_records_classified(self):
        assert _classify_document_type("Medical records from Tampa General Hospital") == "medical_records"

    def test_police_report_classified(self):
        assert _classify_document_type("Arrest report by Officer Brown") == "police_report"

    def test_correspondence_classified(self):
        assert _classify_document_type("Email correspondence from CEO") == "correspondence"

    def test_financial_classified(self):
        assert _classify_document_type("Bank statement and invoice records") == "financial"

    def test_photograph_classified(self):
        assert _classify_document_type("Photograph of injury scene") == "photograph"

    def test_unknown_returns_other(self):
        assert _classify_document_type("random thing") == "other"

    def test_all_types_have_keywords(self):
        for dtype, keywords in DOCUMENT_TYPES.items():
            assert len(keywords) > 0, f"No keywords for {dtype}"


class TestAuthentication:
    """Test authentication method suggestions."""

    def test_medical_records_auth(self):
        rule, method, witness = _suggest_authentication("medical_records")
        assert "803(6)" in rule or "902(11)" in rule
        assert "Business Records" in method

    def test_police_report_auth(self):
        rule, method, witness = _suggest_authentication("police_report")
        assert "Public Records" in method

    def test_unknown_type_fallback(self):
        rule, method, witness = _suggest_authentication("xyzzy")
        assert "901(b)(1)" in rule

    def test_all_known_types_have_auth(self):
        for dtype in DOCUMENT_TYPES:
            result = _suggest_authentication(dtype)
            assert len(result) == 3


class TestObjections:
    """Test anticipated objection generation."""

    def test_medical_records_objection(self):
        objs = _anticipate_objections("medical_records")
        assert any("Hearsay" in o for o in objs)

    def test_photograph_objection(self):
        objs = _anticipate_objections("photograph")
        assert any("Authentication" in o or "Prejudice" in o for o in objs)

    def test_unknown_gets_generic(self):
        objs = _anticipate_objections("xyzzy")
        assert len(objs) > 0


class TestNumbering:
    """Test exhibit numbering schemes."""

    def test_alpha_numbering(self):
        assert _number_exhibit(0, "alpha") == "A"
        assert _number_exhibit(25, "alpha") == "Z"
        assert _number_exhibit(26, "alpha") == "AA"

    def test_numeric_numbering(self):
        assert _number_exhibit(0, "numeric") == "1"
        assert _number_exhibit(9, "numeric") == "10"

    def test_bates_numbering_with_prefix(self):
        result = _number_exhibit(0, "bates", "SMITH")
        assert result == "SMITH-000001"

    def test_bates_numbering_without_prefix(self):
        result = _number_exhibit(0, "bates")
        assert result == "EX-000001"


class TestDateExtraction:
    """Test date extraction from text."""

    def test_iso_date(self):
        assert _extract_date_from_text("Report 2025-06-15 version") == "2025-06-15"

    def test_us_date(self):
        assert _extract_date_from_text("Filed 06/15/2025") == "06/15/2025"

    def test_no_date(self):
        assert _extract_date_from_text("No date here") == ""


class TestClaimMapping:
    """Test exhibit-to-claim mapping."""

    def test_force_maps_to_excessive_force(self):
        case = {"claims_requested": ["1983_fourth_excessive_force"]}
        claims = _map_to_claims("Body camera footage of use of force", case)
        assert "1983_fourth_excessive_force" in claims

    def test_medical_maps_to_force(self):
        case = {"claims_requested": ["1983_fourth_excessive_force"]}
        claims = _map_to_claims("Medical records from hospital", case)
        assert "1983_fourth_excessive_force" in claims

    def test_empty_claims_returns_empty(self):
        case = {"claims_requested": []}
        claims = _map_to_claims("Any document", case)
        assert claims == []


class TestIndexGeneration:
    """Test full exhibit index generation."""

    def test_index_from_case_facts(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        assert isinstance(index, ExhibitIndex)
        assert index.total_exhibits > 0

    def test_index_entries_have_auth(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        for entry in index.entries:
            assert entry.authentication_method
            assert entry.authentication_witness

    def test_index_has_checklist(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        assert len(index.authentication_checklist) == len(index.entries)

    def test_self_authenticating_detected(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        police_entries = [e for e in index.entries if e.document_type == "police_report"]
        for pe in police_entries:
            assert pe.status == "self_authenticating"

    def test_numbering_alpha(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case, numbering="alpha")
        first = index.entries[0].exhibit_number
        assert first == "A"

    def test_numbering_bates(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case, numbering="bates", prefix="SMITH")
        first = index.entries[0].exhibit_number
        assert "SMITH" in first

    def test_manifest_overrides_facts(self, exhibit_case):
        manifest = [
            {"description": "Custom Document One", "type": "contract"},
            {"description": "Custom Document Two", "type": "photograph"},
        ]
        index = generate_exhibit_index(exhibit_case, document_manifest=manifest)
        assert index.total_exhibits == 2
        assert index.entries[0].description == "Custom Document One"

    def test_deduplication(self, exhibit_case):
        """Same document referenced in two facts should appear once."""
        exhibit_case["facts"].append({
            "date": "2025-06-16", "event": "Follow-up",
            "documents": ["Medical records from Tampa General Hospital"],
        })
        index = generate_exhibit_index(exhibit_case)
        descs = [e.description for e in index.entries]
        assert descs.count("Medical records from Tampa General Hospital") == 1


class TestFormatting:
    """Test exhibit index formatting."""

    def test_table_format(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        output = format_exhibit_index(index, fmt="table")
        assert "EXHIBIT INDEX" in output
        assert index.case_name in output

    def test_detailed_format(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        output = format_exhibit_index(index, fmt="detailed")
        assert "Authentication:" in output

    def test_missing_auth_warning(self, exhibit_case):
        index = generate_exhibit_index(exhibit_case)
        if index.missing_authentication:
            output = format_exhibit_index(index)
            assert "AUTHENTICATION NEEDED" in output
