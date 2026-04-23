"""catalog.json must stay aligned with model_admission.taxonomy (phase0)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from model_admission.taxonomy import OWASP_LLM_2025, RISK_REGISTER, RiskCategory

_REPO_ROOT = Path(__file__).resolve().parents[2]
_CATALOG_PATH = _REPO_ROOT / "llm_security_test_cases" / "catalog.json"


@pytest.fixture(scope="module")
def catalog_obj() -> dict:
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def _owasp_slug_to_default_category() -> dict[str, str]:
    return {slug: cat.value for _, slug, cat in OWASP_LLM_2025}


def _owasp_pairs() -> set[tuple[str, str]]:
    return {(code, slug) for code, slug, _ in OWASP_LLM_2025}


def test_catalog_file_exists() -> None:
    assert _CATALOG_PATH.is_file(), f"missing {_CATALOG_PATH}"


def test_catalog_taxonomy_version_matches_phase0(catalog_obj: dict) -> None:
    assert catalog_obj.get("taxonomy_version") == "phase0"


def test_catalog_cases_unique_ids(catalog_obj: dict) -> None:
    ids = [c["id"] for c in catalog_obj["cases"]]
    assert len(ids) == len(set(ids)), f"duplicate ids: {ids}"


def test_catalog_cases_align_taxonomy(catalog_obj: dict) -> None:
    allowed_cat = {e.value for e in RiskCategory}
    owasp_default = _owasp_slug_to_default_category()
    owasp_pairs = _owasp_pairs()
    for case in catalog_obj["cases"]:
        cid = case["id"]
        cat = case["category"]
        assert cat in allowed_cat, f"{cid}: invalid category {cat!r}"
        rid = case.get("risk_register_id")
        oslug = case.get("owasp_slug")
        ocode = case.get("owasp_code")
        if rid is not None:
            assert rid in RISK_REGISTER, f"{cid}: unknown risk_register_id {rid!r}"
            assert cat == RISK_REGISTER[rid].value, (
                f"{cid}: category {cat!r} != RISK_REGISTER[{rid!r}]"
            )
        if oslug is not None:
            assert oslug in owasp_default, f"{cid}: unknown owasp_slug {oslug!r}"
            if rid is None:
                assert cat == owasp_default[oslug], (
                    f"{cid}: category {cat!r} != OWASP default for {oslug!r}"
                )
        if ocode is not None or oslug is not None:
            assert ocode is not None and oslug is not None, (
                f"{cid}: owasp_code and owasp_slug must both be set if either is set"
            )
            assert (ocode, oslug) in owasp_pairs, f"{cid}: unknown OWASP pair {(ocode, oslug)!r}"
