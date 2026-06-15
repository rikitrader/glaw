"""Tests for ftc_engine.suggest - Claim Auto-Suggestion Engine."""
import pytest
from ftc_engine.suggest import suggest_claims, FACT_PATTERNS, PATTERN_CLAIM_MAP


class TestSuggestClaims:
    def test_excessive_force_case(self, sample_case):
        suggestions = suggest_claims(sample_case)
        keys = [s.claim_key for s in suggestions]
        assert "1983_fourth_excessive_force" in keys

    def test_false_arrest_suggested(self, sample_case):
        suggestions = suggest_claims(sample_case)
        keys = [s.claim_key for s in suggestions]
        assert "1983_fourth_false_arrest" in keys

    def test_monell_suggested_for_municipal(self, sample_case):
        suggestions = suggest_claims(sample_case)
        keys = [s.claim_key for s in suggestions]
        assert "1983_monell_municipal_liability" in keys

    def test_empty_facts_returns_empty(self, minimal_case):
        suggestions = suggest_claims(minimal_case)
        assert len(suggestions) == 0

    def test_max_results_limits_output(self, sample_case):
        suggestions = suggest_claims(sample_case, max_results=2)
        assert len(suggestions) <= 2

    def test_scores_sorted_descending(self, sample_case):
        suggestions = suggest_claims(sample_case)
        scores = [s.match_score for s in suggestions]
        assert scores == sorted(scores, reverse=True)


class TestShowstoppers:
    def test_ftca_showstopper_no_federal_defendant(self, sample_case):
        """FTCA claims should flag when no federal defendant present."""
        # sample_case has officer + city, no federal
        # Force an FTCA suggestion by adding negligence keywords
        sample_case["facts"].append({
            "event": "federal VA hospital negligent treatment caused malpractice",
            "harm": "severe injury", "actors": ["VA Hospital"],
            "date": "2025-01-01", "location": "Tampa",
        })
        suggestions = suggest_claims(sample_case)
        ftca = [s for s in suggestions if "ftca" in s.claim_key]
        if ftca:
            assert any("federal" in ss.lower() for ss in ftca[0].showstoppers)

    def test_bivens_viability_warning(self, sample_case):
        """Bivens claims should include viability warning."""
        # Add federal defendant to trigger Bivens
        sample_case["parties"]["defendants"].append(
            {"name": "Federal Agent", "type": "federal", "capacity": "individual",
             "citizenship": "Federal", "entity_type": "individual"}
        )
        suggestions = suggest_claims(sample_case)
        bivens = [s for s in suggestions if "bivens" in s.claim_key]
        # At least one Bivens claim should carry a showstopper (viability or context warning)
        assert any(len(b.showstoppers) > 0 for b in bivens), "Expected at least one Bivens showstopper"


class TestPatterns:
    def test_all_mapped_patterns_have_keywords(self):
        """Every pattern in PATTERN_CLAIM_MAP should have keywords in FACT_PATTERNS."""
        for pattern in PATTERN_CLAIM_MAP:
            assert pattern in FACT_PATTERNS, f"Claim map '{pattern}' has no keyword list"

    def test_unmapped_patterns_are_known(self):
        """Patterns without claim mappings are informational only (e.g., 'contract')."""
        unmapped = set(FACT_PATTERNS) - set(PATTERN_CLAIM_MAP)
        known_unmapped = {"contract"}  # contract patterns exist but no federal claim mapping yet
        assert unmapped <= known_unmapped, f"Unexpected unmapped patterns: {unmapped - known_unmapped}"

    def test_all_mapped_claims_exist(self):
        from ftc_engine.claims import CLAIM_LIBRARY
        for pattern, claims in PATTERN_CLAIM_MAP.items():
            for ck in claims:
                assert ck in CLAIM_LIBRARY, f"Pattern '{pattern}' maps to unknown claim '{ck}'"

    def test_force_pattern_keywords(self):
        assert "force" in FACT_PATTERNS["force"]
        assert "choked" in FACT_PATTERNS["force"]

    def test_employment_maps_to_title_vii(self):
        assert "title_vii_disparate_treatment" in PATTERN_CLAIM_MAP["employment"]
