"""Tests for ftc_engine.claims - Claim Library."""
import pytest
from ftc_engine.claims import (
    CLAIM_LIBRARY, get_claim, get_claims_by_category,
    get_exhaustion_required, get_heightened_pleading, list_categories,
)

EXPECTED_CATEGORIES = [
    "administrative", "bivens", "commercial", "constitutional_civil_rights",
    "employment", "erisa", "financial_consumer", "tax", "tort_government",
]


class TestClaimLibrary:
    def test_total_claims(self):
        assert len(CLAIM_LIBRARY) >= 44

    def test_all_claims_have_required_fields(self):
        for key, meta in CLAIM_LIBRARY.items():
            assert meta.name, f"{key} missing name"
            assert meta.category, f"{key} missing category"
            assert meta.source, f"{key} missing source"
            assert meta.statute_of_limitations, f"{key} missing SOL"

    def test_categories_complete(self):
        assert sorted(list_categories()) == EXPECTED_CATEGORIES

    @pytest.mark.parametrize("cat", EXPECTED_CATEGORIES)
    def test_category_has_claims(self, cat):
        claims = get_claims_by_category(cat)
        assert len(claims) > 0, f"Category {cat} is empty"


class TestGetClaim:
    def test_known_claim(self):
        meta = get_claim("1983_fourth_excessive_force")
        assert meta is not None
        assert "Excessive Force" in meta.name
        assert meta.category == "constitutional_civil_rights"

    def test_unknown_claim_returns_none(self):
        assert get_claim("nonexistent_claim") is None

    def test_immunities_present(self):
        meta = get_claim("1983_fourth_excessive_force")
        assert "qualified" in meta.immunities

    def test_monell_no_qualified_immunity(self):
        meta = get_claim("1983_monell_municipal_liability")
        assert meta.immunities == []


class TestExhaustion:
    def test_exhaustion_claims_exist(self):
        exhaustion_claims = get_exhaustion_required()
        assert len(exhaustion_claims) >= 10

    def test_title_vii_requires_eeoc(self):
        meta = get_claim("title_vii_disparate_treatment")
        assert meta.exhaustion_required is True
        assert meta.exhaustion_type == "eeoc"

    def test_ftca_requires_sf95(self):
        meta = get_claim("ftca_negligence")
        assert meta.exhaustion_required is True
        assert meta.exhaustion_type == "ftca_sf95"

    def test_erisa_requires_internal(self):
        meta = get_claim("erisa_502a1b_benefits")
        assert meta.exhaustion_required is True
        assert meta.exhaustion_type == "erisa_internal"

    def test_eighth_amendment_requires_plra(self):
        meta = get_claim("1983_eighth_deliberate_indifference")
        assert meta.exhaustion_required is True
        assert meta.exhaustion_type == "plra"


class TestHeightenedPleading:
    def test_rico_requires_9b(self):
        meta = get_claim("rico_1962c")
        assert meta.heightened_pleading is True

    def test_false_claims_requires_9b(self):
        meta = get_claim("false_claims_act_qui_tam")
        assert meta.heightened_pleading is True

    def test_excessive_force_no_9b(self):
        meta = get_claim("1983_fourth_excessive_force")
        assert meta.heightened_pleading is False

    def test_heightened_count(self):
        assert len(get_heightened_pleading()) >= 3
