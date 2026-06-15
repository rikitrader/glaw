"""Tests for post-generation verification questions engine."""
import pytest
from ftc_engine.questions import (
    generate_questions,
    format_questions,
    Question,
    QuestionSet,
)


class TestGenerateQuestions:
    """Test context-aware question generation."""

    def test_returns_question_set(self, sample_case):
        qs = generate_questions(sample_case)
        assert isinstance(qs, QuestionSet)
        assert qs.document_type == "analyze"
        assert len(qs.questions) > 0

    def test_all_questions_have_required_fields(self, sample_case):
        qs = generate_questions(sample_case)
        for q in qs.questions:
            assert q.category in ("prefiling", "strategic", "client", "procedural")
            assert q.priority in ("critical", "high", "medium")
            assert len(q.text) > 10

    def test_critical_questions_always_present(self, sample_case):
        qs = generate_questions(sample_case)
        critical = qs.critical
        assert len(critical) >= 2  # attorney review + facts verified are always critical

    def test_by_category_groups_correctly(self, sample_case):
        qs = generate_questions(sample_case)
        cats = qs.by_category
        assert "prefiling" in cats
        assert "client" in cats
        assert all(q.category == "prefiling" for q in cats["prefiling"])

    def test_sorted_by_priority(self, sample_case):
        qs = generate_questions(sample_case)
        priority_order = {"critical": 0, "high": 1, "medium": 2}
        scores = [priority_order[q.priority] for q in qs.questions]
        assert scores == sorted(scores)

    def test_corporate_party_triggers_disclosure_question(self, minimal_case):
        """Corporation defendants should trigger FRCP 7.1 disclosure question."""
        qs = generate_questions(minimal_case)
        texts = [q.text for q in qs.questions]
        assert any("Corporate Disclosure" in t for t in texts)

    def test_individual_only_no_disclosure_question(self, minimal_case):
        """All-individual parties should NOT trigger the FRCP 7.1 disclosure question."""
        minimal_case["parties"]["defendants"] = [
            {"name": "John Smith", "type": "individual", "capacity": "individual",
             "citizenship": "Georgia", "entity_type": "individual"}
        ]
        qs = generate_questions(minimal_case)
        # Check specifically for the FRCP 7.1 question (not the calendaring one)
        prefiling_texts = [q.text for q in qs.questions if q.category == "prefiling"]
        assert not any("FRCP 7.1" in t for t in prefiling_texts)

    def test_injunction_relief_triggers_tro_question(self, sample_case):
        """Requesting injunctive relief should ask about TRO urgency."""
        sample_case["relief_requested"] = ["injunction"]
        qs = generate_questions(sample_case, doc_type="analyze")
        texts = [q.text for q in qs.questions]
        assert any("TRO" in t for t in texts)

    def test_multi_defendant_triggers_strategy_question(self, sample_case):
        """Multiple defendants should trigger joint-and-several liability question."""
        qs = generate_questions(sample_case, doc_type="analyze")
        texts = [q.text for q in qs.questions]
        has_multi_def = any("defendants" in t.lower() and ("crossclaim" in t.lower() or "joint" in t.lower()) for t in texts)
        if len(sample_case.get("parties", {}).get("defendants", [])) > 1:
            assert has_multi_def

    def test_high_risk_scores_trigger_warning(self, sample_case):
        """High MTD risk scores should trigger critical warning."""
        risk_scores = {"1983_fourth_excessive_force": {"score": 75, "level": "high"}}
        qs = generate_questions(sample_case, risk_scores=risk_scores)
        texts = [q.text for q in qs.questions]
        assert any("HIGH MTD risk" in t for t in texts)

    def test_no_risk_warning_for_low_scores(self, sample_case):
        """Low risk scores should NOT trigger risk warning."""
        risk_scores = {"1983_fourth_excessive_force": {"score": 30, "level": "low"}}
        qs = generate_questions(sample_case, risk_scores=risk_scores)
        texts = [q.text for q in qs.questions]
        assert not any("HIGH MTD risk" in t for t in texts)

    def test_expired_sol_triggers_critical(self, sample_case):
        """Expired SOL should trigger critical procedural question."""
        sol_results = [{"claim_key": "test_claim", "status": "expired", "days_remaining": -30}]
        qs = generate_questions(sample_case, sol_results=sol_results)
        expired_qs = [q for q in qs.questions if "EXPIRED" in q.text]
        assert len(expired_qs) >= 1
        assert expired_qs[0].priority == "critical"

    def test_urgent_sol_triggers_critical(self, sample_case):
        """Urgent SOL should trigger critical deadline question."""
        sol_results = [{"claim_key": "test_claim", "status": "urgent", "days_remaining": 15}]
        qs = generate_questions(sample_case, sol_results=sol_results)
        urgent_qs = [q for q in qs.questions if "URGENT" in q.text]
        assert len(urgent_qs) >= 1
        assert urgent_qs[0].priority == "critical"

    def test_safe_sol_no_urgency(self, sample_case):
        """Safe SOL should NOT trigger urgent questions."""
        sol_results = [{"claim_key": "test_claim", "status": "safe", "days_remaining": 500}]
        qs = generate_questions(sample_case, sol_results=sol_results)
        texts = [q.text for q in qs.questions]
        assert not any("URGENT" in t or "EXPIRED" in t for t in texts)

    def test_doc_type_draft_includes_strategic(self, sample_case):
        """Draft doc type should include strategic questions."""
        qs = generate_questions(sample_case, doc_type="draft")
        cats = qs.by_category
        assert "strategic" in cats

    def test_doc_type_export_excludes_strategic(self, sample_case):
        """Export doc type should NOT include strategic questions."""
        qs = generate_questions(sample_case, doc_type="export")
        cats = qs.by_category
        assert "strategic" not in cats

    def test_pro_se_triggers_extra_questions(self, minimal_case):
        """Pro se cases should get additional guidance questions."""
        minimal_case["pro_se"] = True
        qs = generate_questions(minimal_case)
        texts = [q.text for q in qs.questions]
        assert any("pro se" in t.lower() for t in texts)

    def test_new_case_triggers_post_filing_deadlines(self, minimal_case):
        """New/pre-filing cases should ask about calendaring post-filing deadlines."""
        qs = generate_questions(minimal_case)
        texts = [q.text for q in qs.questions]
        assert any("90-day service deadline" in t for t in texts)


class TestFormatQuestions:
    """Test CLI output formatting."""

    def test_format_returns_string(self, sample_case):
        qs = generate_questions(sample_case)
        output = format_questions(qs)
        assert isinstance(output, str)
        assert "POST-GENERATION VERIFICATION QUESTIONS" in output

    def test_format_shows_category_headers(self, sample_case):
        qs = generate_questions(sample_case, doc_type="analyze")
        output = format_questions(qs)
        assert "PRE-FILING VERIFICATION" in output
        assert "CLIENT COMMUNICATION" in output

    def test_format_shows_priority_icons(self, sample_case):
        qs = generate_questions(sample_case)
        output = format_questions(qs)
        assert "[!!]" in output  # critical
        assert "[>>]" in output or "[..]" in output  # high or medium

    def test_format_verbose_shows_context(self, sample_case):
        qs = generate_questions(sample_case)
        verbose_output = format_questions(qs, verbose=True)
        assert "->" in verbose_output  # context lines

    def test_format_non_verbose_hides_context(self, sample_case):
        qs = generate_questions(sample_case)
        output = format_questions(qs, verbose=False)
        assert "->" not in output

    def test_format_shows_question_count(self, sample_case):
        qs = generate_questions(sample_case)
        output = format_questions(qs)
        assert f"{len(qs.questions)} questions" in output
        assert f"{len(qs.critical)} CRITICAL" in output

    def test_format_shows_tip(self, sample_case):
        qs = generate_questions(sample_case)
        output = format_questions(qs)
        assert "--questions --verbose" in output
