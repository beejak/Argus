"""Static checks on Hugging Face-style JSON configs (no execution).

Human-facing citations for emitted ``rule_id`` values live in
``docs/reporting/decision_support_rule_catalog.json`` (used by
``scripts/export_bundle_action_sheet.py``).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ConfigFinding:
    path: str
    rule_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "rule_id": self.rule_id, "message": self.message}


def _walk_truthy_bools(obj: Any, path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            lk = k.lower()
            if lk in ("trust_remote_code", "use_auth_token", "use_fast_tokenizer"):
                if v is True or (isinstance(v, str) and v.lower() in ("true", "1", "yes")):
                    out.append((p, str(v)))
            _walk_truthy_bools(v, p, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_truthy_bools(item, f"{path}[{i}]", out)


def lint_config_file(path: Path) -> list[ConfigFinding]:
    """Parse JSON and emit high-signal policy hints (not vulnerabilities by themselves)."""
    rel = str(path)
    findings: list[ConfigFinding] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [
            ConfigFinding(rel, "config_json_invalid", f"invalid JSON: {e}"),
        ]

    risky: list[tuple[str, str]] = []
    _walk_truthy_bools(data, "", risky)
    for key_path, val in risky:
        if "trust_remote_code" in key_path.lower():
            findings.append(
                ConfigFinding(
                    rel,
                    "trust_remote_code_enabled",
                    f"{key_path} is truthy ({val!r}); loading with trust_remote_code can execute Hub Python",
                )
            )
        elif "use_auth_token" in key_path.lower():
            findings.append(
                ConfigFinding(
                    rel,
                    "use_auth_token_present",
                    f"{key_path} is set; verify tokens are never embedded in public repos",
                )
            )
        elif "use_fast_tokenizer" in key_path.lower():
            findings.append(
                ConfigFinding(
                    rel,
                    "use_fast_tokenizer_truthy",
                    f"{key_path} is truthy ({val!r}); legacy fast tokenizer paths can complicate audits—prefer explicit tokenizer provenance",
                )
            )

    auto_map = data.get("auto_map") if isinstance(data, dict) else None
    if isinstance(auto_map, dict) and auto_map:
        findings.append(
            ConfigFinding(
                rel,
                "auto_map_custom_classes",
                "auto_map references custom class names; verify code provenance before load",
            )
        )

    return findings


def lint_tree(paths: list[Path]) -> list[ConfigFinding]:
    out: list[ConfigFinding] = []
    for p in paths:
        out.extend(lint_config_file(p))
    return out
