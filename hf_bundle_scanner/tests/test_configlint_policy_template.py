"""Org policy template stays aligned with configlint + dispatch."""

from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.configlint import RULE_IDS_EMITTED
from hf_bundle_scanner.dispatch import CONFIG_RISK_RULE_IDS


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_configlint_policy_template_matches_dispatch() -> None:
    path = _repo_root() / "docs" / "policy" / "configlint_rule_defaults.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    rules = data.get("rules")
    assert isinstance(rules, list) and rules
    escalating = {r["rule_id"] for r in rules if r.get("default_aggregate_escalates") is True}
    assert escalating == set(CONFIG_RISK_RULE_IDS)
    all_ids = {r["rule_id"] for r in rules}
    assert all_ids == RULE_IDS_EMITTED
