"""Tests for document exporter (.docx generation)."""
import pytest
from pathlib import Path
from ftc_engine.exporter import (
    export_draft,
    export_template,
    export_text,
    list_templates,
    _setup_document,
    _fill_placeholders,
    _extract_legal_text,
    ExportResult,
)


class TestSetupDocument:
    """Test document creation with court formatting."""

    def test_creates_document(self):
        doc = _setup_document()
        assert doc is not None

    def test_margins_set(self):
        doc = _setup_document()
        section = doc.sections[0]
        # 1 inch = 914400 EMU
        assert section.top_margin == 914400
        assert section.bottom_margin == 914400
        assert section.left_margin == 914400
        assert section.right_margin == 914400

    def test_default_font(self):
        doc = _setup_document()
        style = doc.styles["Normal"]
        assert style.font.name == "Times New Roman"
        assert style.font.size.pt == 12.0

    def test_double_spacing(self):
        doc = _setup_document()
        style = doc.styles["Normal"]
        assert style.paragraph_format.line_spacing == 2.0


class TestFillPlaceholders:
    """Test placeholder replacement in templates."""

    def test_replaces_plaintiff_name(self):
        text = "{{PLAINTIFF_NAME}} v. {{DEFENDANT_NAME}}"
        case_data = {
            "parties": {
                "plaintiffs": [{"name": "John Doe"}],
                "defendants": [{"name": "Corp Inc"}],
            }
        }
        result = _fill_placeholders(text, case_data)
        assert "JOHN DOE" in result
        assert "CORP INC" in result

    def test_replaces_case_number(self):
        text = "Case No. {{CASE_NO}}"
        case_data = {"case_number": "6:24-cv-01234", "parties": {}}
        result = _fill_placeholders(text, case_data)
        assert "6:24-cv-01234" in result

    def test_missing_data_uses_placeholder(self):
        text = "{{ATTORNEY_NAME}} - {{BAR_NO}}"
        case_data = {"parties": {}}
        result = _fill_placeholders(text, case_data)
        assert "[ATTORNEY NAME]" in result
        assert "[BAR NO.]" in result

    def test_empty_parties_handled(self):
        text = "{{PLAINTIFF_NAME}} v. {{DEFENDANT_NAME}}"
        case_data = {"parties": {"plaintiffs": [], "defendants": []}}
        result = _fill_placeholders(text, case_data)
        assert "[PLAINTIFF]" in result
        assert "[DEFENDANT]" in result


class TestExtractLegalText:
    """Test code block extraction from templates."""

    def test_extracts_from_code_blocks(self):
        template = "# Title\n\n```\nLegal text here\n```\n\nNotes."
        result = _extract_legal_text(template)
        assert result == "Legal text here\n"

    def test_returns_full_text_if_no_blocks(self):
        text = "Just plain text with no code blocks"
        result = _extract_legal_text(text)
        assert result == text


class TestListTemplates:
    """Test template listing."""

    def test_returns_list(self):
        templates = list_templates()
        assert isinstance(templates, list)

    def test_templates_have_required_keys(self):
        templates = list_templates()
        if templates:
            t = templates[0]
            assert "category" in t
            assert "name" in t
            assert "path" in t

    def test_finds_all_categories(self):
        templates = list_templates()
        categories = {t["category"] for t in templates}
        # At minimum these should exist
        assert "motions" in categories
        assert "pleadings" in categories
        assert "orders" in categories

    def test_template_count(self):
        templates = list_templates()
        assert len(templates) >= 40  # We created 42 templates


class TestExportDraft:
    """Test complaint draft export."""

    def test_produces_docx(self, sample_case, tmp_path):
        output = str(tmp_path / "complaint.docx")
        result = export_draft(sample_case, output)
        assert isinstance(result, ExportResult)
        assert result.format == "docx"
        assert Path(result.output_path).exists()
        assert Path(result.output_path).stat().st_size > 10000

    def test_result_has_sections(self, sample_case, tmp_path):
        output = str(tmp_path / "complaint.docx")
        result = export_draft(sample_case, output)
        assert result.sections >= 0


class TestExportTemplate:
    """Test template export."""

    def test_exports_motion_to_dismiss(self, sample_case, tmp_path):
        output = str(tmp_path / "mtd.docx")
        result = export_template("motions/motion_to_dismiss", sample_case, output)
        assert Path(result.output_path).exists()
        assert result.format == "docx"

    def test_exports_order_template(self, sample_case, tmp_path):
        output = str(tmp_path / "order.docx")
        result = export_template("orders/proposed_order_mtd", sample_case, output)
        assert Path(result.output_path).exists()

    def test_missing_template_raises(self, tmp_path):
        output = str(tmp_path / "missing.docx")
        with pytest.raises(FileNotFoundError):
            export_template("nonexistent/template_xyz", {}, output)

    def test_empty_case_data_uses_placeholders(self, tmp_path):
        output = str(tmp_path / "empty.docx")
        result = export_template("motions/motion_to_dismiss", {}, output)
        assert Path(result.output_path).exists()


class TestExportText:
    """Test raw text export."""

    def test_exports_plain_text(self, tmp_path):
        output = str(tmp_path / "text.docx")
        text = "UNITED STATES DISTRICT COURT\n\n     COMPLAINT\n\n     1. This is a test paragraph."
        result = export_text(text, output)
        assert Path(result.output_path).exists()
        assert result.format == "docx"
