"""Tests for Interactive Case Wizard."""
import pytest
from unittest.mock import patch
from pathlib import Path
from ftc_engine.wizard import (
    _prompt,
    _prompt_choice,
    _prompt_yes_no,
    _prompt_date,
    _prompt_multi_choice,
    _filter_available_docs,
    collect_court,
    collect_plaintiffs,
    collect_defendants,
    collect_facts,
    collect_claims,
    collect_relief,
    collect_exhaustion,
    collect_limitations,
    collect_goals,
    show_case_summary,
    collect_document_selection,
    execute_pipeline,
    AVAILABLE_DOCUMENTS,
    STEP_COLLECTORS,
    _generate_document,
)
from ftc_engine.case_manager import (
    create_case,
    advance_step,
    save_case_data,
    STEP_KEYS,
)
import ftc_engine.case_manager as cm


@pytest.fixture
def isolated_cases(tmp_path, monkeypatch):
    """Redirect CASES_DIR to temp folder."""
    test_dir = tmp_path / "cases"
    test_dir.mkdir()
    monkeypatch.setattr(cm, "CASES_DIR", test_dir)
    return test_dir


def _make_input_fn(responses):
    """Create a mock input() that returns responses in order."""
    it = iter(responses)
    def mock_input(prompt=""):
        return next(it)
    return mock_input


# ── Prompt helpers ──────────────────────────────────────────────────────────

class TestPrompt:
    """Test _prompt helper."""

    def test_required_retries(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["", "", "John"]))
        result = _prompt("Name", required=True)
        assert result == "John"

    def test_optional_blank(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        result = _prompt("Phone")
        assert result == ""

    def test_default_value(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        result = _prompt("State", default="Florida")
        assert result == "Florida"

    def test_returns_value(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["Tampa"]))
        result = _prompt("City")
        assert result == "Tampa"


class TestPromptChoice:
    """Test _prompt_choice helper."""

    def test_default_selection(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        result = _prompt_choice("Pick", ["A", "B", "C"])
        assert result == "A"

    def test_numeric_selection(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["2"]))
        result = _prompt_choice("Pick", ["A", "B", "C"])
        assert result == "B"

    def test_invalid_then_valid(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["99", "3"]))
        result = _prompt_choice("Pick", ["A", "B", "C"])
        assert result == "C"


class TestPromptYesNo:
    """Test _prompt_yes_no helper."""

    def test_default_no(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        assert _prompt_yes_no("Continue?") is False

    def test_default_yes(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        assert _prompt_yes_no("Continue?", default=True) is True

    def test_explicit_yes(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["y"]))
        assert _prompt_yes_no("Continue?") is True

    def test_explicit_no(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["n"]))
        assert _prompt_yes_no("Continue?", default=True) is False


class TestPromptDate:
    """Test _prompt_date helper."""

    def test_valid_date(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["2025-06-15"]))
        assert _prompt_date("Date") == "2025-06-15"

    def test_optional_blank(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn([""]))
        assert _prompt_date("Date") == ""

    def test_invalid_then_valid(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["bad", "2025-01-01"]))
        assert _prompt_date("Date") == "2025-01-01"


class TestPromptMultiChoice:
    """Test _prompt_multi_choice helper."""

    def test_select_all_then_done(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["a", "done"]))
        result = _prompt_multi_choice("Pick", ["A", "B", "C"])
        assert result == ["A", "B", "C"]

    def test_toggle_individual(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["1", "3", "done"]))
        result = _prompt_multi_choice("Pick", ["A", "B", "C"])
        assert result == ["A", "C"]

    def test_preselected(self, monkeypatch):
        monkeypatch.setattr("builtins.input", _make_input_fn(["done"]))
        result = _prompt_multi_choice("Pick", ["A", "B", "C"], preselected=[1, 2])
        assert result == ["A", "B"]


# ── Section collectors ──────────────────────────────────────────────────────

class TestCollectCourt:
    """Test court collection."""

    def test_selects_district(self, monkeypatch, isolated_cases):
        state = create_case("court-001")
        case_data = {"court": {}, "parties": {"plaintiffs": [], "defendants": []},
                     "facts": [], "claims_requested": [], "relief_requested": [],
                     "exhaustion": {}, "limitations": {"key_dates": {}}, "goals": {}}
        # Select first district, enter division
        monkeypatch.setattr("builtins.input", _make_input_fn(["1", "Tampa"]))
        result = collect_court(state, case_data)
        assert result["court"]["division"] == "Tampa"
        assert result["court"]["district"] != ""


class TestCollectPlaintiffs:
    """Test plaintiff collection."""

    def test_single_individual(self, monkeypatch, isolated_cases):
        state = create_case("plt-001")
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        # name, entity (1=individual), citizenship, address, phone, email, add another=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "John Smith", "1", "Florida", "", "", "", "n",
        ]))
        result = collect_plaintiffs(state, case_data)
        assert len(result["parties"]["plaintiffs"]) == 1
        assert result["parties"]["plaintiffs"][0]["name"] == "John Smith"
        assert result["parties"]["plaintiffs"][0]["entity_type"] == "individual"

    def test_corporation_extra_fields(self, monkeypatch, isolated_cases):
        state = create_case("plt-002")
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        # name, entity (2=corporation), citizenship, incorp state, ppb, address, phone, email, add=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "MegaCorp LLC", "2", "Delaware", "Delaware", "New York",
            "123 Main St", "555-1234", "mega@corp.com", "n",
        ]))
        result = collect_plaintiffs(state, case_data)
        p = result["parties"]["plaintiffs"][0]
        assert p["entity_type"] == "corporation"
        assert p["state_of_incorporation"] == "Delaware"

    def test_multiple_plaintiffs(self, monkeypatch, isolated_cases):
        state = create_case("plt-003")
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "Jane Doe", "1", "Florida", "", "", "", "y",
            "John Doe", "1", "Florida", "", "", "", "n",
        ]))
        result = collect_plaintiffs(state, case_data)
        assert len(result["parties"]["plaintiffs"]) == 2


class TestCollectDefendants:
    """Test defendant collection."""

    def test_officer_defendant(self, monkeypatch, isolated_cases):
        state = create_case("def-001")
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        # name, entity(1=individual), type(1=officer), capacity(3=both), citizenship,
        # role, add=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "Officer Brown", "1", "1", "3", "Florida", "police officer", "n",
        ]))
        result = collect_defendants(state, case_data)
        d = result["parties"]["defendants"][0]
        assert d["type"] == "officer"
        assert d["capacity"] == "both"

    def test_federal_agency(self, monkeypatch, isolated_cases):
        state = create_case("def-002")
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        # name, entity(5=federal_agency), type(3=federal), capacity(2=official), citizenship, role, add=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "DOJ", "5", "3", "2", "Federal", "agency", "n",
        ]))
        result = collect_defendants(state, case_data)
        d = result["parties"]["defendants"][0]
        assert d["entity_type"] == "federal_agency"
        assert d["type"] == "federal"


class TestCollectFacts:
    """Test fact collection."""

    def test_full_fact(self, monkeypatch, isolated_cases):
        state = create_case("fact-001")
        case_data = {"facts": []}
        # date, location, event, actors, harm, docs, witnesses, evidence, damages, add=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "2025-06-15", "Tampa, FL", "Officer used excessive force",
            "Officer Brown, John Smith", "Broken arm",
            "Body camera footage", "Jane Doe", "Video, Photos", "$150000",
            "n",
        ]))
        result = collect_facts(state, case_data)
        f = result["facts"][0]
        assert f["event"] == "Officer used excessive force"
        assert len(f["actors"]) == 2
        assert f["actors"][0] == "Officer Brown"

    def test_minimal_fact(self, monkeypatch, isolated_cases):
        state = create_case("fact-002")
        case_data = {"facts": []}
        # date=blank, location=blank, event(required), actors=blank, harm=blank,
        # docs=blank, witnesses=blank, evidence=blank, damages=blank, add=n
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "", "", "Something happened", "", "", "", "", "", "", "n",
        ]))
        result = collect_facts(state, case_data)
        assert result["facts"][0]["event"] == "Something happened"
        assert result["facts"][0]["actors"] == []


class TestCollectExhaustion:
    """Test exhaustion collection."""

    def test_no_exhaustion_needed(self, monkeypatch, isolated_cases):
        state = create_case("exh-001")
        case_data = {"claims_requested": ["1983_fourth_excessive_force"]}
        monkeypatch.setattr("builtins.input", _make_input_fn([]))
        result = collect_exhaustion(state, case_data)
        assert result["exhaustion"] == {}

    def test_title_vii_asks_eeoc(self, monkeypatch, isolated_cases):
        state = create_case("exh-002")
        case_data = {"claims_requested": ["title_vii_disparate_treatment"]}
        # eeoc filed=y, right to sue=y
        monkeypatch.setattr("builtins.input", _make_input_fn(["y", "y"]))
        result = collect_exhaustion(state, case_data)
        assert result["exhaustion"]["eeoc_charge_filed"] is True


class TestCollectGoals:
    """Test goals collection."""

    def test_collects_goals(self, monkeypatch, isolated_cases):
        state = create_case("goal-001")
        case_data = {"goals": {}}
        monkeypatch.setattr("builtins.input", _make_input_fn([
            "Compensation", "Policy change",
        ]))
        result = collect_goals(state, case_data)
        assert result["goals"]["primary"] == "Compensation"
        assert result["goals"]["secondary"] == "Policy change"


# ── Document filtering ──────────────────────────────────────────────────────

class TestFilterAvailableDocs:
    """Test document availability filtering."""

    def test_no_corp_removes_disclosure(self):
        case_data = {
            "parties": {
                "plaintiffs": [{"name": "John", "entity_type": "individual"}],
                "defendants": [{"name": "Officer", "entity_type": "individual"}],
            }
        }
        docs = _filter_available_docs(case_data)
        keys = [d["key"] for d in docs]
        assert "disclosure" not in keys

    def test_corp_includes_disclosure(self):
        case_data = {
            "parties": {
                "plaintiffs": [],
                "defendants": [{"name": "Corp", "entity_type": "corporation"}],
            }
        }
        docs = _filter_available_docs(case_data)
        keys = [d["key"] for d in docs]
        assert "disclosure" in keys

    def test_no_defendants_removes_deposition(self):
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        docs = _filter_available_docs(case_data)
        keys = [d["key"] for d in docs]
        assert "deposition" not in keys


# ── Document generation ─────────────────────────────────────────────────────

class TestGenerateDocument:
    """Test individual document generation."""

    def test_complaint_generates(self, isolated_cases, sample_case):
        state = create_case("gen-001")
        text = _generate_document("complaint", sample_case, state)
        assert text is not None
        assert len(text) > 0

    def test_calendar_generates(self, isolated_cases, sample_case):
        state = create_case("gen-002")
        text = _generate_document("calendar", sample_case, state)
        assert "FILING CALENDAR" in text or "Document" in text

    def test_unknown_key_returns_empty(self, isolated_cases, sample_case):
        state = create_case("gen-003")
        text = _generate_document("nonexistent", sample_case, state)
        assert text == ""


# ── Document selection: format + location ──────────────────────────────────

class TestCollectDocumentSelection:
    """Test output format and save location prompts in Step 11."""

    def test_selects_format_and_location(self, isolated_cases, monkeypatch):
        state = create_case("sel-001")
        case_data = {"parties": {"plaintiffs": [], "defendants": [{"name": "X", "entity_type": "individual"}]}}
        # Simulate: "done" (accept all docs), "2" (markdown), "3" (case-folder)
        monkeypatch.setattr("builtins.input", _make_input_fn(["done", "2", "3"]))
        collect_document_selection(state, case_data)
        assert state.output_format == "markdown"
        assert state.output_location == ""  # case-folder = empty string

    def test_desktop_location(self, isolated_cases, monkeypatch):
        state = create_case("sel-002")
        case_data = {"parties": {"plaintiffs": [], "defendants": [{"name": "X", "entity_type": "individual"}]}}
        # "done" (docs), "3" (docx), "1" (desktop)
        monkeypatch.setattr("builtins.input", _make_input_fn(["done", "3", "1"]))
        collect_document_selection(state, case_data)
        assert state.output_format == "docx"
        assert "Desktop" in state.output_location
        assert "sel-002" in state.output_location

    def test_custom_location(self, isolated_cases, tmp_path, monkeypatch):
        state = create_case("sel-003")
        case_data = {"parties": {"plaintiffs": [], "defendants": [{"name": "X", "entity_type": "individual"}]}}
        custom = str(tmp_path / "my_cases")
        # "done" (docs), "1" (terminal), "4" (custom), path
        monkeypatch.setattr("builtins.input", _make_input_fn(["done", "1", "4", custom]))
        collect_document_selection(state, case_data)
        assert state.output_location == custom


class TestExecutePipelineCopy:
    """Test that execute_pipeline copies files to output_location."""

    def test_copies_to_output_location(self, isolated_cases, tmp_path, monkeypatch):
        from ftc_engine.case_manager import load_case_data
        state = create_case("pipe-001")
        case_data = load_case_data("pipe-001")
        # Minimal case data to generate calendar
        case_data["claims_requested"] = []
        case_data["parties"] = {"plaintiffs": [{"name": "A"}], "defendants": [{"name": "B"}]}
        save_case_data("pipe-001", case_data)

        state.documents_selected = ["calendar"]
        state.output_format = "markdown"
        dest = tmp_path / "my_output"
        state.output_location = str(dest)

        # Advance to generate step
        for step in STEP_KEYS[:-1]:
            advance_step(state, step)

        generated = execute_pipeline(state, case_data)
        assert len(generated) >= 1

        # Files should exist in both the case output dir and the custom location
        dest_files = list(dest.iterdir())
        assert len(dest_files) >= 1
        assert any(f.suffix == ".md" for f in dest_files)

    def test_no_copy_when_location_empty(self, isolated_cases, tmp_path, monkeypatch):
        from ftc_engine.case_manager import load_case_data
        state = create_case("pipe-002")
        case_data = load_case_data("pipe-002")
        case_data["claims_requested"] = []
        case_data["parties"] = {"plaintiffs": [{"name": "A"}], "defendants": [{"name": "B"}]}
        save_case_data("pipe-002", case_data)

        state.documents_selected = ["calendar"]
        state.output_format = "markdown"
        state.output_location = ""  # no custom location

        for step in STEP_KEYS[:-1]:
            advance_step(state, step)

        generated = execute_pipeline(state, case_data)
        assert len(generated) >= 1
        # All files should be in case folder only
        for g in generated:
            assert "pipe-002" in g


# ── Step collectors map ─────────────────────────────────────────────────────

class TestStepCollectors:
    """Test that all workflow steps have collectors."""

    def test_all_steps_covered(self):
        for key in STEP_KEYS:
            assert key in STEP_COLLECTORS, f"Missing collector for step: {key}"
