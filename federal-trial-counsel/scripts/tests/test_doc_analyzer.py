"""Tests for Document Analyzer — intake, classify, extract, route."""
import pytest
from pathlib import Path
from ftc_engine.doc_analyzer import (
    read_text,
    read_document,
    classify_legal_document,
    extract_parties,
    extract_dates,
    extract_case_number,
    extract_claims,
    extract_court,
    analyze_document,
    analyze_intake_docs,
    determine_workflow,
    build_auto_populated_data,
    generate_recommendations,
    format_analysis_report,
    DocumentAnalysis,
    IntakeAnalysisReport,
    SUPPORTED_EXTENSIONS,
    LEGAL_DOCUMENT_CATEGORIES,
)
from ftc_engine.case_manager import create_case, import_documents
import ftc_engine.case_manager as cm


@pytest.fixture
def isolated_cases(tmp_path, monkeypatch):
    """Redirect CASES_DIR to temp folder."""
    test_dir = tmp_path / "cases"
    test_dir.mkdir()
    monkeypatch.setattr(cm, "CASES_DIR", test_dir)
    return test_dir


# ── Layer 1: Text Extraction ──────────────────────────────────────────────

class TestTextExtraction:
    """Test document reading functions."""

    def test_read_text_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello world")
        assert read_text(f) == "Hello world"

    def test_read_document_txt(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Document content")
        assert read_document(f) == "Document content"

    def test_read_document_md(self, tmp_path):
        f = tmp_path / "test.md"
        f.write_text("# Title\nBody text")
        result = read_document(f)
        assert "Title" in result
        assert "Body text" in result

    def test_unsupported_extension_raises(self, tmp_path):
        f = tmp_path / "test.xlsx"
        f.write_text("data")
        with pytest.raises(ValueError, match="Unsupported"):
            read_document(f)

    def test_read_missing_file_raises(self, tmp_path):
        f = tmp_path / "nonexistent.txt"
        with pytest.raises(FileNotFoundError):
            read_text(f)


# ── Layer 2: Classification ──────────────────────────────────────────────

class TestClassification:
    """Test legal document classification."""

    def test_complaint_classified(self):
        text = """CIVIL COMPLAINT
        Plaintiff comes now and files this complaint for damages.
        JURISDICTION is proper under 28 U.S.C. § 1331.
        COUNT I - Cause of Action. WHEREFORE, Plaintiff requests relief."""
        cat, conf = classify_legal_document(text)
        assert cat == "complaint"
        assert conf > 0.3

    def test_motion_dismiss_classified(self):
        text = """MOTION TO DISMISS under Rule 12(b)(6) for failure to state
        a claim. Under Iqbal and Twombly, plaintiff's complaint lacks plausibility."""
        cat, conf = classify_legal_document(text)
        assert cat == "motion_dismiss"
        assert conf > 0.3

    def test_discovery_classified(self):
        text = """PLAINTIFF'S FIRST SET OF INTERROGATORIES
        You are requested to answer the following interrogatories under
        Rule 33. Also, Request for Production under Rule 34."""
        cat, conf = classify_legal_document(text)
        assert cat == "discovery_request"

    def test_medical_records_classified(self):
        text = """DISCHARGE SUMMARY
        Patient presented to the emergency room. Doctor diagnosed a fracture.
        Treatment included radiology and MRI. Prescription for pain management."""
        cat, conf = classify_legal_document(text)
        assert cat == "medical_records"

    def test_court_order_classified(self):
        text = """IT IS ORDERED that the scheduling order is as follows.
        The Court orders the parties to comply. SO ORDERED."""
        cat, conf = classify_legal_document(text)
        assert cat == "court_order"

    def test_unknown_returns_other(self):
        text = "Random text with no legal keywords whatsoever. Just gibberish."
        cat, conf = classify_legal_document(text)
        assert cat == "other"
        assert conf == 0.0

    def test_filename_boosts_classification(self):
        text = "Some general text about a matter."
        cat1, conf1 = classify_legal_document(text, filename="complaint.pdf")
        cat2, conf2 = classify_legal_document(text, filename="random.pdf")
        assert conf1 > conf2

    def test_motion_dismiss_beats_motion_other(self):
        """Specific motion types must win over the generic motion_other catch-all."""
        text = """MOTION TO DISMISS under Rule 12(b)(6) for failure to state
        a claim. Under Iqbal and Twombly, plaintiff's complaint lacks plausibility.
        Defendant respectfully moves this Court for an order dismissing."""
        cat, conf = classify_legal_document(text)
        assert cat == "motion_dismiss"

    def test_motion_other_when_no_specific_match(self):
        """motion_other should still classify generic motions."""
        text = """MOTION FOR EXTENSION OF TIME
        Defendant respectfully moves this Court for an extension of time.
        Good cause exists for the requested extension."""
        cat, conf = classify_legal_document(text)
        assert cat == "motion_other"
        assert conf > 0.0


# ── Layer 3: Entity Extraction ───────────────────────────────────────────

class TestExtractParties:
    """Test party name extraction."""

    def test_extract_from_caption(self):
        text = "JOHN SMITH v. OFFICER BROWN, individually"
        parties = extract_parties(text)
        names = [p.value for p in parties]
        assert any("JOHN SMITH" in n for n in names)
        assert any("OFFICER BROWN" in n for n in names)

    def test_extract_labeled_parties(self):
        text = "Plaintiff: Jane Doe\nDefendant: City of Tampa"
        parties = extract_parties(text)
        p_names = [p.value for p in parties if p.entity_type == "plaintiff"]
        d_names = [p.value for p in parties if p.entity_type == "defendant"]
        assert any("Jane Doe" in n for n in p_names)
        assert any("City of Tampa" in n for n in d_names)


class TestExtractDates:
    """Test date extraction."""

    def test_extract_iso_date(self):
        text = "The incident occurred on 2025-06-15 in Tampa."
        dates = extract_dates(text)
        values = [d.value for d in dates]
        assert "2025-06-15" in values

    def test_extract_us_date(self):
        text = "Filed on 06/15/2025 in federal court."
        dates = extract_dates(text)
        values = [d.value for d in dates]
        assert "06/15/2025" in values

    def test_extract_written_date(self):
        text = "On January 15, 2024, the plaintiff was injured."
        dates = extract_dates(text)
        values = [d.value for d in dates]
        assert any("January 15, 2024" in v for v in values)

    def test_no_duplicates(self):
        text = "Date: 2025-06-15. Again: 2025-06-15."
        dates = extract_dates(text)
        assert len(dates) == 1


class TestExtractCaseNumber:
    """Test case number extraction."""

    def test_standard_case_number(self):
        text = "Case No. 6:24-cv-01234-ABC-DEF filed in M.D. Fla."
        nums = extract_case_number(text)
        values = [n.value for n in nums]
        assert any("6:24-cv-01234" in v for v in values)

    def test_standalone_case_number(self):
        text = "Reference 8:25-cv-00999 for this matter."
        nums = extract_case_number(text)
        values = [n.value for n in nums]
        assert any("8:25-cv-00999" in v for v in values)


class TestExtractClaims:
    """Test statutory reference extraction."""

    def test_section_1983(self):
        text = "This action is brought under 42 U.S.C. § 1983."
        claims = extract_claims(text)
        values = [c.value for c in claims]
        assert "42 U.S.C. § 1983" in values

    def test_title_vii(self):
        text = "Plaintiff's claims arise under Title VII of the Civil Rights Act."
        claims = extract_claims(text)
        values = [c.value for c in claims]
        assert "Title VII" in values

    def test_ftca(self):
        text = "This claim is pursuant to the Federal Tort Claims Act (FTCA)."
        claims = extract_claims(text)
        values = [c.value for c in claims]
        assert "FTCA" in values


class TestExtractCourt:
    """Test court information extraction."""

    def test_full_court_name(self):
        text = "UNITED STATES DISTRICT COURT for the MIDDLE DISTRICT OF FLORIDA"
        courts = extract_court(text)
        values = [c.value for c in courts]
        assert any("MIDDLE DISTRICT OF FLORIDA" in v for v in values)

    def test_fallback_district(self):
        text = "Filed in the Middle District of Florida, Tampa Division."
        courts = extract_court(text)
        values = [c.value for c in courts]
        assert any("Middle District of Florida" in v for v in values)


# ── Layer 4: Analysis Pipeline ───────────────────────────────────────────

class TestAnalyzeDocument:
    """Test end-to-end single document analysis."""

    def test_analyze_complaint_txt(self, tmp_path):
        f = tmp_path / "complaint.txt"
        f.write_text("""UNITED STATES DISTRICT COURT
MIDDLE DISTRICT OF FLORIDA

Case No. 6:24-cv-01234-ABC

JOHN SMITH, Plaintiff v. OFFICER BROWN, Defendant

CIVIL COMPLAINT

Plaintiff comes now and files this complaint pursuant to 42 U.S.C. § 1983.
The incident occurred on 2025-06-15.
COUNT I - Excessive Force. WHEREFORE, Plaintiff requests relief.
""")
        result = analyze_document(f)
        assert result.document_category == "complaint"
        assert result.confidence_score > 0.3
        assert result.text_length > 0
        assert len(result.parties) > 0
        assert len(result.claims) > 0
        assert len(result.courts) > 0
        assert not result.errors

    def test_analyze_bad_file(self, tmp_path):
        f = tmp_path / "bad.xlsx"
        f.write_text("not a real xlsx")
        result = analyze_document(f)
        assert len(result.errors) > 0
        assert result.document_category == "other"

    def test_error_handling_missing(self, tmp_path):
        f = tmp_path / "gone.txt"
        # Don't create the file
        result = analyze_document(f)
        assert len(result.errors) > 0


class TestAnalyzeIntakeDocs:
    """Test batch analysis of intake folder."""

    def test_analyze_intake_full(self, isolated_cases, tmp_path):
        state = create_case("analysis-001")

        # Create test documents
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "complaint.txt").write_text(
            "CIVIL COMPLAINT\nComes now plaintiff. Jurisdiction. COUNT I. WHEREFORE."
        )
        (docs_dir / "medical.txt").write_text(
            "DISCHARGE SUMMARY\nDoctor diagnosed a fracture. Hospital treatment. Emergency room."
        )

        import_documents("analysis-001", str(docs_dir))
        report = analyze_intake_docs("analysis-001")

        assert report.total_documents == 2
        assert report.successful_analyses == 2
        assert report.failed_analyses == 0
        assert len(report.documents) == 2
        assert report.suggested_workflow != ""
        assert len(report.recommendations) > 0

    def test_empty_intake(self, isolated_cases):
        create_case("empty-001")
        report = analyze_intake_docs("empty-001")
        assert report.total_documents == 0
        assert "No supported documents" in report.recommendations[0]


# ── Layer 5: Workflow Routing ────────────────────────────────────────────

class TestWorkflowRouting:
    """Test workflow determination from document classifications."""

    def _make_analysis(self, category: str) -> DocumentAnalysis:
        return DocumentAnalysis(
            filename="test.txt",
            file_path="/test.txt",
            document_category=category,
            confidence_score=0.8,
            extracted_text="",
            text_length=100,
        )

    def test_complaint_triggers_defense(self):
        analyses = [self._make_analysis("complaint")]
        assert determine_workflow(analyses) == "complaint_defense"

    def test_motion_triggers_response(self):
        analyses = [self._make_analysis("motion_dismiss")]
        assert determine_workflow(analyses) == "motion_response"

    def test_discovery_triggers_response(self):
        analyses = [self._make_analysis("discovery_request")]
        assert determine_workflow(analyses) == "discovery_response"

    def test_evidence_triggers_new_case(self):
        analyses = [self._make_analysis("medical_records")]
        assert determine_workflow(analyses) == "new_case"

    def test_empty_analyses_default(self):
        assert determine_workflow([]) == "new_case"

    def test_complaint_priority_over_evidence(self):
        analyses = [
            self._make_analysis("medical_records"),
            self._make_analysis("complaint"),
        ]
        assert determine_workflow(analyses) == "complaint_defense"


class TestBuildAutoPopulated:
    """Test auto-population of case data from extracted entities."""

    def test_builds_parties(self):
        a = DocumentAnalysis(
            filename="test.txt", file_path="/test.txt",
            document_category="complaint", confidence_score=0.8,
            extracted_text="", text_length=100,
        )
        from ftc_engine.doc_analyzer import ExtractedEntity
        a.parties = [
            ExtractedEntity("plaintiff", "John Smith", 0.8, "context"),
            ExtractedEntity("defendant", "Officer Brown", 0.8, "context"),
        ]
        result = build_auto_populated_data([a])
        assert "parties" in result
        assert len(result["parties"]["plaintiffs"]) == 1
        assert result["parties"]["plaintiffs"][0]["name"] == "John Smith"

    def test_builds_court(self):
        a = DocumentAnalysis(
            filename="test.txt", file_path="/test.txt",
            document_category="complaint", confidence_score=0.8,
            extracted_text="", text_length=100,
        )
        from ftc_engine.doc_analyzer import ExtractedEntity
        a.courts = [ExtractedEntity("court", "Middle District of Florida", 0.9, "context")]
        result = build_auto_populated_data([a])
        assert "court" in result
        assert "Middle District of Florida" in result["court"]["district"]


class TestGenerateRecommendations:
    """Test recommendation generation."""

    def _make_analysis(self, category: str) -> DocumentAnalysis:
        return DocumentAnalysis(
            filename="test.txt", file_path="/test.txt",
            document_category=category, confidence_score=0.8,
            extracted_text="", text_length=100,
        )

    def test_complaint_recommendation(self):
        recs = generate_recommendations([self._make_analysis("complaint")])
        assert any("Answer or MTD" in r for r in recs)

    def test_discovery_recommendation(self):
        recs = generate_recommendations([self._make_analysis("discovery_request")])
        assert any("30 days" in r for r in recs)

    def test_evidence_recommendation(self):
        recs = generate_recommendations([self._make_analysis("photograph")])
        assert any("standard case intake" in r for r in recs)


# ── Formatting ───────────────────────────────────────────────────────────

class TestFormatReport:
    """Test report formatting."""

    def test_format_contains_header(self):
        report = IntakeAnalysisReport(
            case_number="fmt-001",
            analyzed_at="2025-06-15 10:00",
            total_documents=0,
            successful_analyses=0,
            failed_analyses=0,
        )
        output = format_analysis_report(report)
        assert "DOCUMENT ANALYSIS REPORT" in output
        assert "fmt-001" in output

    def test_format_shows_classifications(self):
        a = DocumentAnalysis(
            filename="complaint.txt", file_path="/complaint.txt",
            document_category="complaint", confidence_score=0.8,
            extracted_text="", text_length=100,
        )
        report = IntakeAnalysisReport(
            case_number="fmt-002",
            analyzed_at="2025-06-15 10:00",
            total_documents=1,
            successful_analyses=1,
            failed_analyses=0,
            documents=[a],
            suggested_workflow="complaint_defense",
        )
        output = format_analysis_report(report)
        assert "complaint.txt" in output
        assert "complaint" in output.lower()
        assert "Complaint Defense" in output
