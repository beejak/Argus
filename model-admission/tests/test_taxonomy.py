"""Phase-0 taxonomy: OWASP mapping, risk register, rule_id helpers."""

from __future__ import annotations

from model_admission.taxonomy import (
    OWASP_LLM_2025,
    RISK_REGISTER,
    RiskCategory,
    category_for_register_id,
    make_rule_id,
    owasp_rows,
    slugify,
)


def test_risk_category_values() -> None:
    assert RiskCategory.ARTIFACT.value == "artifact"


def test_make_rule_id() -> None:
    assert make_rule_id("ModelScan", "Unsafe Pickle") == "modelscan.unsafe_pickle"


def test_slugify() -> None:
    assert slugify("  Foo-Bar  ") == "foo_bar"


def test_owasp_row_count() -> None:
    assert len(OWASP_LLM_2025) == 10
    rows = owasp_rows()
    assert rows[0]["owasp_code"] == "LLM01"
    assert rows[0]["category"] == "dynamic"


def test_risk_register_covers_register_ids() -> None:
    assert category_for_register_id("poison_rag_corpus") == RiskCategory.DYNAMIC
    assert category_for_register_id("adapter_trojan") == RiskCategory.ARTIFACT
    assert "prompt_injection" in RISK_REGISTER
