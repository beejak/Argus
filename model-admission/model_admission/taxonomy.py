"""Phase-0 risk taxonomy: categories, OWASP LLM mapping, stable rule_id prefixes.

Authoritative human narrative: ``docs/THREAT_MODEL_TAXONOMY.md`` in the LLM Scanner repo.
"""

from __future__ import annotations

import re
from enum import Enum
from typing import Final


class RiskCategory(str, Enum):
    """Normalized category for findings and future policy packs."""

    ARTIFACT = "artifact"
    PROVENANCE = "provenance"
    CONFIG = "config"
    SUPPLY_CHAIN = "supply_chain"
    DYNAMIC = "dynamic"
    RUNTIME = "runtime"
    CONTENT_POLICY = "content_policy"
    FAIRNESS = "fairness"
    META = "meta"


# OWASP Top 10 for LLM Applications (2025 framing) — titles paraphrased; verify against
# https://owasp.org/www-project-top-10-for-large-language-model-applications/
OWASP_LLM_2025: Final[tuple[tuple[str, str, RiskCategory], ...]] = (
    ("LLM01", "prompt_injection", RiskCategory.DYNAMIC),
    ("LLM02", "sensitive_information_disclosure", RiskCategory.CONTENT_POLICY),
    ("LLM03", "supply_chain", RiskCategory.SUPPLY_CHAIN),
    ("LLM04", "data_and_model_poisoning", RiskCategory.SUPPLY_CHAIN),
    ("LLM05", "improper_output_handling", RiskCategory.RUNTIME),
    ("LLM06", "excessive_agency", RiskCategory.DYNAMIC),
    ("LLM07", "system_prompt_leakage", RiskCategory.CONFIG),
    ("LLM08", "vector_and_embedding_weaknesses", RiskCategory.DYNAMIC),
    ("LLM09", "misinformation", RiskCategory.CONTENT_POLICY),
    ("LLM10", "unbounded_consumption", RiskCategory.META),
)

# In-repo risk register concept ids (see docs/PRODUCTION_SCANNER_ROADMAP.md)
RISK_REGISTER: Final[dict[str, RiskCategory]] = {
    "poison_rag_corpus": RiskCategory.DYNAMIC,
    "poison_system_template": RiskCategory.CONFIG,
    "poison_train_data": RiskCategory.SUPPLY_CHAIN,
    "reputational_policy": RiskCategory.CONTENT_POLICY,
    "memorization_pii": RiskCategory.CONTENT_POLICY,
    "safety_harm": RiskCategory.CONTENT_POLICY,
    "bias_fairness_slice": RiskCategory.FAIRNESS,
    "multimodal_abuse": RiskCategory.DYNAMIC,
    "adapter_trojan": RiskCategory.ARTIFACT,
    "tool_exfil": RiskCategory.DYNAMIC,
    "model_steal": RiskCategory.DYNAMIC,
    "drift_post_deploy": RiskCategory.META,
    "prompt_injection": RiskCategory.DYNAMIC,
    "sensitive_disclosure": RiskCategory.CONTENT_POLICY,
    "improper_output_handling": RiskCategory.RUNTIME,
    "excessive_agency": RiskCategory.DYNAMIC,
    "system_prompt_leak": RiskCategory.CONFIG,
    "vector_embedding_weakness": RiskCategory.DYNAMIC,
    "misinformation": RiskCategory.CONTENT_POLICY,
    "unbounded_consumption": RiskCategory.META,
}

_SLUG = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    s = text.strip().lower()
    s = _SLUG.sub("_", s).strip("_")
    return s or "unknown"


def make_rule_id(prefix: str, slug: str) -> str:
    """Stable ``rule_id`` like ``modelscan.unsafe_pickle``."""
    p = slugify(prefix)
    s = slugify(slug)
    return f"{p}.{s}"


def category_for_register_id(concept_id: str) -> RiskCategory | None:
    return RISK_REGISTER.get(concept_id)


def owasp_rows() -> list[dict[str, str]]:
    """Serializable rows for bundle docs / tooling."""
    out: list[dict[str, str]] = []
    for code, slug, cat in OWASP_LLM_2025:
        out.append(
            {
                "owasp_code": code,
                "slug": slug,
                "category": cat.value,
            }
        )
    return out
