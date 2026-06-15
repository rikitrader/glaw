"""Tests for MCP Server — tool handlers only (no transport testing)."""
import pytest
import json
import ftc_engine.case_manager as cm
from ftc_engine.mcp_server import (
    TOOLS,
    TOOL_HANDLERS,
    handle_ftc_analyze,
    handle_ftc_suggest,
    handle_ftc_risk,
    handle_ftc_sol,
    handle_ftc_draft,
    handle_ftc_claims,
    handle_ftc_info,
    handle_ftc_district,
    handle_ftc_district_list,
    handle_ftc_deposition,
    handle_ftc_exhibits,
    handle_ftc_pacer,
    handle_ftc_monitor,
    handle_ftc_calendar,
    handle_ftc_questions,
    handle_ftc_cases,
    handle_ftc_doctor,
    handle_ftc_template_list,
)


class TestToolDefinitions:
    """Test MCP tool metadata."""

    def test_tool_count(self):
        assert len(TOOLS) == 20

    def test_all_tools_have_handlers(self):
        for tool in TOOLS:
            assert tool["name"] in TOOL_HANDLERS, f"No handler for {tool['name']}"

    def test_all_handlers_have_tools(self):
        tool_names = {t["name"] for t in TOOLS}
        for handler_name in TOOL_HANDLERS:
            assert handler_name in tool_names, f"Handler {handler_name} has no tool definition"

    def test_tools_have_required_fields(self):
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert tool["inputSchema"]["type"] == "object"

    def test_tool_names_prefixed(self):
        for tool in TOOLS:
            assert tool["name"].startswith("ftc_"), f"Tool {tool['name']} missing ftc_ prefix"


class TestAnalyzeHandler:
    """Test full case analysis handler."""

    def test_returns_all_sections(self, sample_case):
        result = handle_ftc_analyze({"case_data": sample_case})
        assert "jurisdiction" in result
        assert "suggestions" in result
        assert "risk_scores" in result
        assert "generated" in result

    def test_jurisdiction_has_basis(self, sample_case):
        result = handle_ftc_analyze({"case_data": sample_case})
        assert "basis" in result["jurisdiction"]

    def test_suggestions_are_list(self, sample_case):
        result = handle_ftc_analyze({"case_data": sample_case})
        assert isinstance(result["suggestions"], list)
        assert len(result["suggestions"]) > 0


class TestSuggestHandler:
    """Test claim suggestion handler."""

    def test_returns_suggestions(self, sample_case):
        result = handle_ftc_suggest({"case_data": sample_case})
        assert "suggestions" in result
        assert "count" in result
        assert result["count"] > 0

    def test_max_results_respected(self, sample_case):
        result = handle_ftc_suggest({"case_data": sample_case, "max_results": 3})
        assert result["count"] <= 3

    def test_suggestion_has_fields(self, sample_case):
        result = handle_ftc_suggest({"case_data": sample_case})
        s = result["suggestions"][0]
        assert "key" in s
        assert "name" in s
        assert "score" in s


class TestRiskHandler:
    """Test MTD risk scoring handler."""

    def test_returns_scores(self, sample_case):
        result = handle_ftc_risk({"case_data": sample_case, "claims": ["1983_fourth_excessive_force"]})
        assert "risk_scores" in result
        assert "1983_fourth_excessive_force" in result["risk_scores"]

    def test_score_has_fields(self, sample_case):
        result = handle_ftc_risk({"case_data": sample_case, "claims": ["1983_fourth_excessive_force"]})
        score = result["risk_scores"]["1983_fourth_excessive_force"]
        assert "overall_score" in score
        assert "risk_level" in score
        assert 0 <= score["overall_score"] <= 100


class TestSOLHandler:
    """Test statute of limitations handler."""

    def test_returns_results(self):
        result = handle_ftc_sol({"claims": ["1983_fourth_excessive_force"], "injury_date": "2025-06-15"})
        assert "results" in result
        assert len(result["results"]) == 1

    def test_result_has_status(self):
        result = handle_ftc_sol({"claims": ["1983_fourth_excessive_force"], "injury_date": "2025-06-15"})
        r = result["results"][0]
        assert r["status"] in ("safe", "urgent", "expired")
        assert "deadline" in r
        assert "days_remaining" in r


class TestDraftHandler:
    """Test complaint draft handler."""

    def test_returns_complaint(self, sample_case):
        result = handle_ftc_draft({"case_data": sample_case})
        assert "complaint" in result
        assert len(result["complaint"]) > 100

    def test_returns_length(self, sample_case):
        result = handle_ftc_draft({"case_data": sample_case})
        assert result["length"] > 0


class TestClaimsHandler:
    """Test claims listing handler."""

    def test_returns_categories(self):
        result = handle_ftc_claims({})
        assert "categories" in result
        assert result["total"] == 45

    def test_categories_not_empty(self):
        result = handle_ftc_claims({})
        for cat, claims in result["categories"].items():
            assert len(claims) > 0, f"Empty category: {cat}"


class TestInfoHandler:
    """Test claim info handler."""

    def test_known_claim(self):
        result = handle_ftc_info({"claim_key": "1983_fourth_excessive_force"})
        assert "name" in result
        assert "category" in result
        assert result["name"] != ""

    def test_unknown_claim(self):
        result = handle_ftc_info({"claim_key": "nonexistent_xyz"})
        assert "error" in result


class TestDistrictHandler:
    """Test district info handler."""

    def test_known_district(self):
        result = handle_ftc_district({"code": "mdfl"})
        assert "info" in result
        assert "code" in result

    def test_unknown_district(self):
        result = handle_ftc_district({"code": "zzzzz"})
        assert "error" in result

    def test_district_list(self):
        result = handle_ftc_district_list({})
        assert "districts" in result
        assert result["total"] >= 5


class TestDepositionHandler:
    """Test deposition outline handler."""

    def test_returns_outline(self, sample_case):
        result = handle_ftc_deposition({
            "case_data": sample_case,
            "witness_name": "Officer Brown",
            "exam_type": "cross",
        })
        assert "outline" in result


class TestExhibitsHandler:
    """Test exhibit index handler."""

    def test_returns_index(self, exhibit_case):
        result = handle_ftc_exhibits({"case_data": exhibit_case})
        assert "index" in result


class TestPacerHandler:
    """Test PACER filing package handler."""

    def test_full_package(self, corporate_case):
        result = handle_ftc_pacer({"case_data": corporate_case, "component": "all"})
        assert "package" in result

    def test_js44_only(self, corporate_case):
        result = handle_ftc_pacer({"case_data": corporate_case, "component": "js44"})
        assert "js44" in result

    def test_disclosure(self, corporate_case):
        result = handle_ftc_pacer({"case_data": corporate_case, "component": "disclosure"})
        assert "disclosures" in result


class TestMonitorHandler:
    """Test Rule 11 monitor handler."""

    def test_returns_report(self, sample_case):
        sample_case["claims_requested"] = ["1983_fourth_excessive_force"]
        result = handle_ftc_monitor({"case_data": sample_case})
        assert "compliance" in result
        assert "claims_checked" in result
        assert result["claims_checked"] >= 1


class TestCalendarHandler:
    """Test filing calendar handler."""

    def test_returns_calendar(self, sample_case):
        result = handle_ftc_calendar({"case_data": sample_case})
        assert "calendar" in result
        assert "total_documents" in result


class TestQuestionsHandler:
    """Test verification questions handler."""

    def test_returns_questions(self, sample_case):
        result = handle_ftc_questions({"case_data": sample_case})
        assert "questions" in result


class TestCasesHandler:
    """Test cases listing handler."""

    def test_returns_list(self, tmp_path, monkeypatch):
        import ftc_engine.case_manager as cm
        test_dir = tmp_path / "cases"
        test_dir.mkdir()
        monkeypatch.setattr(cm, "CASES_DIR", test_dir)
        result = handle_ftc_cases({})
        assert "cases" in result
        assert isinstance(result["cases"], list)


class TestDoctorHandler:
    """Test diagnostics handler."""

    def test_returns_checks(self):
        result = handle_ftc_doctor({})
        assert "checks" in result
        assert result["total"] > 0
        assert result["passed"] > 0

    def test_checks_have_fields(self):
        result = handle_ftc_doctor({})
        for check in result["checks"]:
            assert "name" in check
            assert "ok" in check
            assert "value" in check


class TestTemplateListHandler:
    """Test template listing handler."""

    def test_returns_templates(self):
        result = handle_ftc_template_list({})
        assert "templates" in result
        assert result["total"] > 0
