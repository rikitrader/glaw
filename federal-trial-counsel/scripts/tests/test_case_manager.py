"""Tests for Case Manager — persistent case storage and workflow state."""
import json
import pytest
from pathlib import Path
from ftc_engine.case_manager import (
    create_case,
    open_case,
    list_cases,
    delete_case,
    save_state,
    save_case_data,
    load_case_data,
    advance_step,
    get_workflow_map,
    import_documents,
    list_intake_docs,
    get_output_path,
    list_outputs,
    CaseState,
    CaseInfo,
    WORKFLOW_STEPS,
    STEP_KEYS,
    CASES_DIR,
    _extract_case_name,
    _sanitize_case_number,
)
import ftc_engine.case_manager as cm


@pytest.fixture
def isolated_cases(tmp_path, monkeypatch):
    """Redirect CASES_DIR to a temp folder for isolation."""
    test_dir = tmp_path / "cases"
    test_dir.mkdir()
    monkeypatch.setattr(cm, "CASES_DIR", test_dir)
    return test_dir


class TestSanitize:
    """Test case number sanitization."""

    def test_colons_replaced(self):
        assert _sanitize_case_number("6:24-cv-01234") == "6-24-cv-01234"

    def test_slashes_replaced(self):
        assert _sanitize_case_number("6/24/cv") == "6-24-cv"

    def test_strips_whitespace(self):
        assert _sanitize_case_number("  case-1  ") == "case-1"


class TestExtractCaseName:
    """Test case name extraction from case data."""

    def test_both_parties(self):
        data = {
            "parties": {
                "plaintiffs": [{"name": "Smith"}],
                "defendants": [{"name": "Brown"}],
            }
        }
        assert _extract_case_name(data) == "Smith v. Brown"

    def test_missing_parties(self):
        assert _extract_case_name({}) == "Unknown v. Unknown"


class TestCreateCase:
    """Test case creation."""

    def test_creates_folder_structure(self, isolated_cases):
        state = create_case("6:24-cv-01234")
        case_path = Path(state.case_path)
        assert case_path.exists()
        assert (case_path / "intake_docs").is_dir()
        assert (case_path / "output").is_dir()
        assert (case_path / "state.json").exists()
        assert (case_path / "case.json").exists()

    def test_state_initialized(self, isolated_cases):
        state = create_case("test-001")
        assert state.case_number == "test-001"
        assert state.current_step == "court"
        assert state.completed_steps == []
        assert len(state.pending_steps) == len(WORKFLOW_STEPS)

    def test_case_data_empty_schema(self, isolated_cases):
        create_case("test-002")
        data = load_case_data("test-002")
        assert "court" in data
        assert "parties" in data
        assert data["parties"]["plaintiffs"] == []


class TestOpenCase:
    """Test opening existing cases."""

    def test_opens_existing(self, isolated_cases):
        create_case("open-001")
        state, case_data = open_case("open-001")
        assert state.case_number == "open-001"
        assert isinstance(case_data, dict)

    def test_error_on_missing(self, isolated_cases):
        with pytest.raises(FileNotFoundError):
            open_case("nonexistent-case")


class TestListCases:
    """Test listing all cases."""

    def test_empty_when_no_cases(self, isolated_cases):
        assert list_cases() == []

    def test_lists_multiple(self, isolated_cases):
        create_case("list-001")
        create_case("list-002")
        cases = list_cases()
        assert len(cases) == 2
        numbers = [c.case_number for c in cases]
        assert "list-001" in numbers
        assert "list-002" in numbers

    def test_case_info_fields(self, isolated_cases):
        create_case("info-001")
        save_case_data("info-001", {
            "parties": {
                "plaintiffs": [{"name": "Doe"}],
                "defendants": [{"name": "Corp"}],
            }
        })
        cases = list_cases()
        assert len(cases) == 1
        info = cases[0]
        assert isinstance(info, CaseInfo)
        assert info.case_name == "Doe v. Corp"
        assert info.status == "intake"


class TestDeleteCase:
    """Test case deletion."""

    def test_deletes_existing(self, isolated_cases):
        create_case("del-001")
        assert delete_case("del-001") is True
        assert list_cases() == []

    def test_returns_false_for_missing(self, isolated_cases):
        assert delete_case("nope") is False


class TestAdvanceStep:
    """Test workflow step advancement."""

    def test_advances_to_next(self, isolated_cases):
        state = create_case("adv-001")
        state = advance_step(state, "court")
        assert "court" in state.completed_steps
        assert state.current_step == "plaintiffs"

    def test_skips_already_completed(self, isolated_cases):
        state = create_case("adv-002")
        state = advance_step(state, "court")
        state = advance_step(state, "court")  # duplicate
        assert state.completed_steps.count("court") == 1

    def test_persists_to_disk(self, isolated_cases):
        state = create_case("adv-003")
        advance_step(state, "court")
        reloaded, _ = open_case("adv-003")
        assert "court" in reloaded.completed_steps

    def test_all_steps_leads_to_done(self, isolated_cases):
        state = create_case("adv-004")
        for key in STEP_KEYS:
            state = advance_step(state, key)
        assert state.current_step == "done"
        assert len(state.completed_steps) == len(WORKFLOW_STEPS)

    def test_invalid_step_raises(self, isolated_cases):
        state = create_case("adv-005")
        with pytest.raises(ValueError, match="Unknown step"):
            advance_step(state, "invalid_step")


class TestWorkflowMap:
    """Test workflow map formatting."""

    def test_contains_case_number(self, isolated_cases):
        state = create_case("map-001")
        output = get_workflow_map(state)
        assert "map-001" in output

    def test_shows_current_step(self, isolated_cases):
        state = create_case("map-002")
        output = get_workflow_map(state)
        assert "YOU ARE HERE" in output
        assert "[>>]" in output

    def test_shows_completed(self, isolated_cases):
        state = create_case("map-003")
        advance_step(state, "court")
        output = get_workflow_map(state)
        assert "[X]" in output

    def test_shows_progress(self, isolated_cases):
        state = create_case("map-004")
        advance_step(state, "court")
        advance_step(state, "plaintiffs")
        output = get_workflow_map(state)
        assert "2/12" in output


class TestImportDocuments:
    """Test document intake."""

    def test_import_single_file(self, isolated_cases, tmp_path):
        create_case("imp-001")
        doc = tmp_path / "complaint.txt"
        doc.write_text("This is a complaint.")
        imported = import_documents("imp-001", str(doc))
        assert imported == ["complaint.txt"]
        assert list_intake_docs("imp-001") == ["complaint.txt"]

    def test_import_directory(self, isolated_cases, tmp_path):
        create_case("imp-002")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "a.txt").write_text("Document A")
        (docs_dir / "b.txt").write_text("Document B")
        imported = import_documents("imp-002", str(docs_dir))
        assert len(imported) == 2

    def test_missing_source_raises(self, isolated_cases):
        create_case("imp-003")
        with pytest.raises(FileNotFoundError):
            import_documents("imp-003", "/nonexistent/path")


class TestOutputManagement:
    """Test output path and listing."""

    def test_output_path_simple(self, isolated_cases):
        create_case("out-001")
        p = get_output_path("out-001", "complaint_federal")
        assert "complaint_federal" in str(p)
        assert p.parent.name == "output"

    def test_output_path_with_party(self, isolated_cases):
        create_case("out-002")
        p = get_output_path("out-002", "summons", "Officer Brown")
        assert "summons_Officer_Brown" in str(p)

    def test_list_outputs_empty(self, isolated_cases):
        create_case("out-003")
        assert list_outputs("out-003") == []

    def test_list_outputs_after_write(self, isolated_cases):
        create_case("out-004")
        p = get_output_path("out-004", "calendar")
        p.with_suffix(".md").write_text("# Calendar")
        outputs = list_outputs("out-004")
        assert len(outputs) == 1
