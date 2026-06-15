"""Tests for Deposition Question Generator."""
import pytest
from ftc_engine.deposition import (
    generate_deposition_outline,
    format_deposition_outline,
    DepositionOutline,
    DepositionQuestion,
    CLAIM_ELEMENTS,
    _determine_witness_role,
    _generate_foundation_questions,
    _generate_claim_element_questions,
    _generate_authentication_questions,
    _generate_impeachment_questions,
    _generate_defense_anticipation_questions,
)


@pytest.fixture
def deposition_case(sample_case):
    """Sample case enriched for deposition testing."""
    sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
    return sample_case


class TestOutlineGeneration:
    """Test deposition outline creation."""

    def test_outline_returns_dataclass(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        assert isinstance(outline, DepositionOutline)

    def test_outline_has_required_fields(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        assert outline.witness_name == "Officer James Brown"
        assert outline.exam_type == "cross"
        assert outline.total_questions > 0
        assert outline.estimated_duration_minutes > 0
        assert outline.generated_at

    def test_outline_contains_sections(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        assert "foundation" in outline.sections
        assert "claim_element" in outline.sections

    def test_cross_exam_includes_impeachment(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        assert "impeachment" in outline.sections

    def test_direct_exam_skips_impeachment(self, deposition_case):
        outline = generate_deposition_outline(
            deposition_case, "Marcus Williams", "direct",
            claim_keys=["1983_fourth_excessive_force"],
        )
        assert "impeachment" not in outline.sections

    def test_max_questions_respected(self, deposition_case):
        outline = generate_deposition_outline(
            deposition_case, "Officer James Brown", "cross", max_questions=5,
        )
        assert outline.total_questions <= 5


class TestWitnessRole:
    """Test witness role determination."""

    def test_plaintiff_detected(self, deposition_case):
        p_name = deposition_case["parties"]["plaintiffs"][0]["name"]
        role = _determine_witness_role(p_name, deposition_case)
        assert role == "plaintiff"

    def test_defendant_detected(self, deposition_case):
        d_name = deposition_case["parties"]["defendants"][0]["name"]
        role = _determine_witness_role(d_name, deposition_case)
        # Defendants may be officer type or defendant type
        assert role in ("defendant", "officer")

    def test_unknown_witness(self, deposition_case):
        role = _determine_witness_role("Jane Nobody", deposition_case)
        assert role == "witness"


class TestFoundationQuestions:
    """Test FRE 602 foundation questions."""

    def test_direct_has_identity_question(self, deposition_case):
        qs = _generate_foundation_questions("John Doe", deposition_case, "direct")
        assert any("name" in q.question_text.lower() for q in qs)

    def test_cross_has_knowledge_lock(self, deposition_case):
        qs = _generate_foundation_questions("John Doe", deposition_case, "cross")
        assert any("personal knowledge" in q.question_text.lower() for q in qs)

    def test_foundation_questions_are_deposition_questions(self, deposition_case):
        qs = _generate_foundation_questions("John Doe", deposition_case, "cross")
        for q in qs:
            assert isinstance(q, DepositionQuestion)
            assert q.category == "foundation"


class TestClaimElements:
    """Test claim element question generation."""

    def test_excessive_force_elements_exist(self):
        assert "1983_fourth_excessive_force" in CLAIM_ELEMENTS
        elements = CLAIM_ELEMENTS["1983_fourth_excessive_force"]
        assert len(elements) >= 3

    def test_element_questions_generated(self, deposition_case):
        qs = _generate_claim_element_questions(
            deposition_case, "1983_fourth_excessive_force", "Officer Brown", "cross",
        )
        assert len(qs) > 0
        assert all(q.category == "claim_element" for q in qs)

    def test_direct_vs_cross_questions_differ(self, deposition_case):
        cross = _generate_claim_element_questions(
            deposition_case, "1983_fourth_excessive_force", "Officer Brown", "cross",
        )
        direct = _generate_claim_element_questions(
            deposition_case, "1983_fourth_excessive_force", "Officer Brown", "direct",
        )
        cross_texts = {q.question_text for q in cross}
        direct_texts = {q.question_text for q in direct}
        assert cross_texts != direct_texts

    def test_unknown_claim_uses_generic(self, deposition_case):
        qs = _generate_claim_element_questions(
            deposition_case, "unknown_claim_xyz", "Witness", "cross",
        )
        assert len(qs) > 0  # Falls back to generic elements

    def test_title_vii_elements_exist(self):
        assert "title_vii_disparate_treatment" in CLAIM_ELEMENTS


class TestAuthentication:
    """Test FRE 901 authentication questions."""

    def test_documents_generate_auth_questions(self, deposition_case):
        qs = _generate_authentication_questions(deposition_case, "Officer Brown")
        if deposition_case.get("facts"):
            docs = [doc for f in deposition_case["facts"] for doc in f.get("documents", [])]
            if docs:
                assert len(qs) > 0

    def test_no_docs_gets_generic_question(self, minimal_case):
        qs = _generate_authentication_questions(minimal_case, "Witness")
        assert len(qs) > 0
        assert any("documents" in q.question_text.lower() for q in qs)


class TestImpeachment:
    """Test impeachment question generation."""

    def test_officer_gets_bias_questions(self, deposition_case):
        qs = _generate_impeachment_questions(deposition_case, "Officer Brown", "officer")
        assert any(q.subcategory == "bias" for q in qs)

    def test_defendant_gets_financial_interest(self, deposition_case):
        qs = _generate_impeachment_questions(deposition_case, "Corp", "defendant")
        assert any("financial interest" in q.question_text.lower() for q in qs)

    def test_prior_statements_always_asked(self, deposition_case):
        qs = _generate_impeachment_questions(deposition_case, "Witness", "witness")
        assert any(q.subcategory == "prior_statements" for q in qs)


class TestDefenseAnticipation:
    """Test defense anticipation questions."""

    def test_qualified_immunity_addressed(self, deposition_case):
        qs = _generate_defense_anticipation_questions(
            deposition_case, ["1983_fourth_excessive_force"], "Officer Brown",
        )
        assert any("qualified" in q.subcategory.lower() or "immunity" in q.question_text.lower() for q in qs)

    def test_exhaustion_addressed_for_title_vii(self, employment_case):
        qs = _generate_defense_anticipation_questions(
            employment_case, ["title_vii_disparate_treatment"], "HR Director",
        )
        assert any("exhaustion" in q.subcategory.lower() or "administrative" in q.question_text.lower() for q in qs)


class TestFormatting:
    """Test output formatting."""

    def test_format_returns_string(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        output = format_deposition_outline(outline)
        assert isinstance(output, str)
        assert "DEPOSITION QUESTION OUTLINE" in output

    def test_format_contains_witness_name(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        output = format_deposition_outline(outline)
        assert "Officer James Brown" in output

    def test_verbose_mode_adds_detail(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        brief = format_deposition_outline(outline, verbose=False)
        verbose = format_deposition_outline(outline, verbose=True)
        assert len(verbose) > len(brief)

    def test_warnings_displayed(self, deposition_case):
        outline = generate_deposition_outline(deposition_case, "Officer James Brown", "cross")
        if outline.warnings:
            output = format_deposition_outline(outline)
            assert "[!!]" in output
