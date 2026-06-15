"""Tests for ftc_engine.drafter - Complaint Drafter."""
import pytest
from ftc_engine.drafter import (
    analyze_jurisdiction, generate_caption, generate_parties_section,
    generate_factual_allegations, generate_count, generate_prayer,
    generate_complaint,
)


class TestAnalyzeJurisdiction:
    def test_federal_question(self, sample_case):
        jx = analyze_jurisdiction(sample_case)
        assert jx.basis == "federal_question"
        assert jx.satisfied is True
        assert "28 U.S.C. 1331" in jx.citations

    def test_diversity_jurisdiction(self, minimal_case):
        minimal_case["parties"]["plaintiffs"][0]["citizenship"] = "Florida"
        minimal_case["parties"]["defendants"][0]["citizenship"] = "Delaware"
        minimal_case["claims_requested"] = ["fcra_inaccurate_reporting"]
        jx = analyze_jurisdiction(minimal_case)
        # FCRA is federal_question, so it should still be federal_question
        assert jx.satisfied is True

    def test_standing_injury(self, sample_case):
        jx = analyze_jurisdiction(sample_case)
        assert jx.standing_injury is True

    def test_standing_no_injury(self, minimal_case):
        minimal_case["claims_requested"] = ["1983_fourth_excessive_force"]
        jx = analyze_jurisdiction(minimal_case)
        assert jx.standing_injury is False

    def test_venue_analysis(self, sample_case):
        jx = analyze_jurisdiction(sample_case)
        assert jx.venue_proper is True


class TestGenerateCaption:
    def test_caption_format(self, sample_case):
        caption = generate_caption(sample_case)
        assert "UNITED STATES DISTRICT COURT" in caption
        assert "MIDDLE DISTRICT OF FLORIDA" in caption
        assert "JOHN SMITH" in caption
        assert "OFFICER JAMES BROWN" in caption
        assert "Case No." in caption

    def test_missing_parties_placeholder(self):
        caption = generate_caption({"court": {}, "parties": {}})
        assert "[PLAINTIFF]" in caption
        assert "[DEFENDANT]" in caption


class TestGeneratePartiesSection:
    def test_parties_section(self, sample_case):
        section = generate_parties_section(sample_case)
        assert "PARTIES" in section
        assert "John Smith" in section
        assert "Officer James Brown" in section
        assert "City of Tampa" in section

    def test_individual_plaintiff(self, sample_case):
        section = generate_parties_section(sample_case)
        assert "citizen of the State of Florida" in section

    def test_officer_defendant(self, sample_case):
        section = generate_parties_section(sample_case)
        assert "police officer" in section

    def test_municipal_defendant(self, sample_case):
        section = generate_parties_section(sample_case)
        assert "municipal corporation" in section


class TestGenerateFactualAllegations:
    def test_allegations_from_facts(self, sample_case):
        lines = generate_factual_allegations(sample_case)
        assert lines[0] == "FACTUAL ALLEGATIONS\n"
        assert len(lines) > 1

    def test_dates_included(self, sample_case):
        lines = generate_factual_allegations(sample_case)
        text = "\n".join(lines)
        assert "2025-06-15" in text or "On or about" in text

    def test_empty_facts(self, minimal_case):
        lines = generate_factual_allegations(minimal_case)
        assert len(lines) == 1  # Just the header


class TestGenerateCount:
    def test_known_claim(self, sample_case):
        count = generate_count(sample_case, "1983_fourth_excessive_force", 1)
        assert "COUNT 1" in count
        assert "EXCESSIVE FORCE" in count.upper()
        assert "42 U.S.C. 1983" in count

    def test_unknown_claim(self, sample_case):
        count = generate_count(sample_case, "nonexistent", 1)
        assert "UNKNOWN CLAIM" in count

    def test_count_2_incorporates(self, sample_case):
        count = generate_count(sample_case, "1983_fourth_false_arrest", 2)
        assert "re-alleges" in count.lower()


class TestGeneratePrayer:
    def test_money_relief(self):
        prayer = generate_prayer({"relief_requested": ["money"]})
        assert "Compensatory damages" in prayer
        assert "Punitive damages" in prayer

    def test_injunction_relief(self):
        prayer = generate_prayer({"relief_requested": ["injunction"]})
        assert "injunctive relief" in prayer

    def test_fees_relief(self):
        prayer = generate_prayer({"relief_requested": ["fees"]})
        assert "attorneys' fees" in prayer

    def test_always_includes_other_relief(self):
        prayer = generate_prayer({"relief_requested": []})
        assert "just and proper" in prayer


class TestGenerateComplaint:
    def test_complete_complaint(self, sample_case):
        complaint = generate_complaint(sample_case)
        assert "UNITED STATES DISTRICT COURT" in complaint
        assert "COMPLAINT" in complaint
        assert "PARTIES" in complaint
        assert "JURISDICTION" in complaint
        assert "VENUE" in complaint
        assert "FACTUAL ALLEGATIONS" in complaint
        assert "CAUSES OF ACTION" in complaint
        assert "PRAYER FOR RELIEF" in complaint
        assert "JURY DEMAND" in complaint
        assert "Respectfully submitted" in complaint

    def test_auto_suggest_populates_counts(self, sample_case):
        sample_case["claims_requested"] = ["auto_suggest"]
        complaint = generate_complaint(sample_case)
        assert "COUNT 1" in complaint
