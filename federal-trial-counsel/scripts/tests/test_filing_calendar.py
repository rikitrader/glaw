"""Tests for Filing Calendar."""
import pytest
from datetime import date, timedelta
from ftc_engine.filing_calendar import (
    generate_filing_calendar,
    format_filing_calendar,
    FilingCalendar,
    CalendarEntry,
    _build_pre_filing_entries,
    _build_service_entries,
    _build_response_entries,
    _build_corporate_disclosure_entries,
    _build_discovery_entries,
    _build_dispositive_entries,
    _build_trial_entries,
    _build_post_trial_entries,
)


class TestCalendarGeneration:
    """Test full calendar generation."""

    def test_returns_dataclass(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        assert isinstance(cal, FilingCalendar)

    def test_has_entries(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        assert cal.total_documents > 0

    def test_entries_sorted_by_date(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        dates = [e.deadline for e in cal.entries]
        assert dates == sorted(dates)

    def test_has_critical_deadlines(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        assert cal.critical_deadlines > 0

    def test_case_name_populated(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        assert "v." in cal.case_name

    def test_defaults_to_today(self, sample_case):
        cal = generate_filing_calendar(sample_case)
        assert cal.filing_date == date.today()

    def test_filing_date_parsed(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-06-15")
        assert cal.filing_date == date(2026, 6, 15)


class TestPreFilingEntries:
    """Test pre-filing document entries."""

    def test_complaint_included(self):
        entries = _build_pre_filing_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert "Complaint" in docs

    def test_js44_included(self):
        entries = _build_pre_filing_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("JS-44" in d for d in docs)

    def test_summons_included(self):
        entries = _build_pre_filing_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("Summons" in d for d in docs)

    def test_all_on_filing_date(self):
        fd = date(2026, 3, 1)
        entries = _build_pre_filing_entries(fd)
        assert all(e.deadline == fd for e in entries)


class TestServiceEntries:
    """Test service deadline entries."""

    def test_service_per_defendant(self, sample_case):
        entries = _build_service_entries(date(2026, 3, 1), sample_case)
        defendants = sample_case.get("parties", {}).get("defendants", [])
        assert len(entries) == len(defendants)

    def test_service_deadline_90_days(self, sample_case):
        fd = date(2026, 3, 1)
        entries = _build_service_entries(fd, sample_case)
        for e in entries:
            assert e.deadline == fd + timedelta(days=90)
            assert e.relative_days == 90

    def test_federal_service_frcp_4i(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "DOJ", "type": "federal", "entity_type": "federal_agency"},
        ]
        entries = _build_service_entries(date(2026, 3, 1), minimal_case)
        assert any("4(i)" in e.rule_authority for e in entries)


class TestResponseEntries:
    """Test answer/MTD deadline entries."""

    def test_response_entry_per_defendant(self, sample_case):
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": False}
        entries = _build_response_entries(date(2026, 3, 1), sample_case, timings)
        defendants = sample_case.get("parties", {}).get("defendants", [])
        assert len(entries) == len(defendants)

    def test_federal_60_day_response(self, minimal_case):
        minimal_case["parties"]["defendants"] = [
            {"name": "VA", "type": "federal", "entity_type": "federal_agency"},
        ]
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": False}
        entries = _build_response_entries(date(2026, 3, 1), minimal_case, timings)
        assert any("60 days" in " ".join(e.notes) for e in entries)


class TestCorporateDisclosureEntries:
    """Test corporate disclosure deadline entries."""

    def test_corporate_party_gets_entry(self, minimal_case):
        entries = _build_corporate_disclosure_entries(date(2026, 3, 1), minimal_case)
        corp_parties = [
            p for p in (
                minimal_case["parties"]["plaintiffs"] +
                minimal_case["parties"]["defendants"]
            )
            if p.get("entity_type", "").lower() in ("corporation", "llc", "corporate")
        ]
        assert len(entries) == len(corp_parties)

    def test_individual_no_disclosure(self):
        case = {
            "parties": {
                "plaintiffs": [{"name": "John", "entity_type": "individual"}],
                "defendants": [{"name": "Jane", "entity_type": "individual"}],
            }
        }
        entries = _build_corporate_disclosure_entries(date(2026, 3, 1), case)
        assert len(entries) == 0


class TestDiscoveryEntries:
    """Test discovery milestone entries."""

    def test_rule_26f_included(self):
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": False}
        entries = _build_discovery_entries(date(2026, 3, 1), timings)
        docs = [e.document for e in entries]
        assert any("26(f)" in d for d in docs)

    def test_initial_disclosures_included(self):
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": False}
        entries = _build_discovery_entries(date(2026, 3, 1), timings)
        docs = [e.document for e in entries]
        assert any("Initial Disclosures" in d for d in docs)

    def test_mediation_when_required(self):
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": True}
        entries = _build_discovery_entries(date(2026, 3, 1), timings)
        docs = [e.document for e in entries]
        assert any("Mediation" in d for d in docs)

    def test_no_mediation_when_not_required(self):
        timings = {"response_days": 21, "reply_days": 7, "mediation_required": False}
        entries = _build_discovery_entries(date(2026, 3, 1), timings)
        docs = [e.document for e in entries]
        assert not any("Mediation" in d for d in docs)


class TestDispositiveMilestones:
    """Test dispositive motion entries."""

    def test_summary_judgment_deadline(self):
        entries = _build_dispositive_entries(date(2026, 3, 1))
        assert any("Dispositive" in e.document or "Summary" in e.description.lower() for e in entries)


class TestTrialEntries:
    """Test trial-related entries."""

    def test_trial_entry_exists(self):
        entries = _build_trial_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert "TRIAL" in docs

    def test_pretrial_conference(self):
        entries = _build_trial_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("Pretrial" in d for d in docs)

    def test_motions_in_limine(self):
        entries = _build_trial_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("Limine" in d for d in docs)


class TestPostTrialEntries:
    """Test post-trial entries."""

    def test_appeal_entry(self):
        entries = _build_post_trial_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("Appeal" in d for d in docs)

    def test_jmol_entry(self):
        entries = _build_post_trial_entries(date(2026, 3, 1))
        docs = [e.document for e in entries]
        assert any("JMOL" in d or "Post-Trial" in d for d in docs)


class TestFormatting:
    """Test calendar formatting."""

    def test_table_format(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        output = format_filing_calendar(cal, fmt="table")
        assert "CASE FILING CALENDAR" in output
        assert "Document" in output

    def test_detailed_format(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        output = format_filing_calendar(cal, fmt="detailed")
        assert "PRE-FILING" in output or "PLEADINGS" in output

    def test_output_contains_case_name(self, sample_case):
        cal = generate_filing_calendar(sample_case, filing_date_str="2026-03-01")
        output = format_filing_calendar(cal)
        assert cal.case_name in output
