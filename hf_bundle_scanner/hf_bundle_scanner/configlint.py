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


# Stable ``rule_id`` strings emitted by this module (for org policy templates + drift tests).
RULE_IDS_EMITTED: frozenset[str] = frozenset(
    {
        "config_json_invalid",
        "trust_remote_code_enabled",
        "use_auth_token_present",
        "use_fast_tokenizer_truthy",
        "auto_map_custom_classes",
        "use_safetensors_disabled",
        "local_files_only_false",
        "remote_pretrained_identifier_url",
        "tokenizer_subfolder_path_traversal",
        "http_proxies_configured",
        "torchscript_truthy",
    }
)


@dataclass
class ConfigFinding:
    path: str
    rule_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"path": self.path, "rule_id": self.rule_id, "message": self.message}


def _is_explicitly_false(v: Any) -> bool:
    """JSON configs sometimes store booleans as strings; treat explicit false only."""
    if v is False:
        return True
    if isinstance(v, str) and v.strip().lower() in ("false", "0", "no"):
        return True
    return False


def _walk_local_files_only_false(obj: Any, path: str, out: list[str]) -> None:
    """Emit paths where ``local_files_only`` is explicitly false (may fetch remote Hub files at load)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k.lower() == "local_files_only" and _is_explicitly_false(v):
                out.append(p)
            else:
                _walk_local_files_only_false(v, p, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_local_files_only_false(item, f"{path}[{i}]", out)


REMOTE_PRETRAINED_KEYS: frozenset[str] = frozenset(
    {
        "pretrained_model_name_or_path",
        "name_or_path",
        "_name_or_path",
    }
)


def _walk_remote_pretrained_url(obj: Any, path: str, out: list[tuple[str, str]]) -> None:
    """Emit (json_path, url_prefix) when a pretrained pointer is an http(s) URL (unexpected supply-chain path)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            lk = k.lower()
            if lk in {x.lower() for x in REMOTE_PRETRAINED_KEYS} and isinstance(v, str):
                s = v.strip()
                low = s.lower()
                if low.startswith("http://") or low.startswith("https://"):
                    out.append((p, s[:240]))
            _walk_remote_pretrained_url(v, p, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_remote_pretrained_url(item, f"{path}[{i}]", out)


def _walk_subfolder_path_traversal(obj: Any, path: str, out: list[str]) -> None:
    """Emit paths where ``subfolder`` looks like a traversal / absolute escape (integrity / path confusion)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k.lower() == "subfolder" and isinstance(v, str):
                if ".." in v or v.startswith(("/", "\\")):
                    out.append(p)
            else:
                _walk_subfolder_path_traversal(v, p, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_subfolder_path_traversal(item, f"{path}[{i}]", out)


def _walk_use_safetensors_disabled(obj: Any, path: str, out: list[str]) -> None:
    """Emit paths where ``use_safetensors`` is explicitly false (pickle-era weight paths more likely)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if k.lower() == "use_safetensors" and _is_explicitly_false(v):
                out.append(p)
            else:
                _walk_use_safetensors_disabled(v, p, out)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk_use_safetensors_disabled(item, f"{path}[{i}]", out)


def _walk_truthy_bools(obj: Any, path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            lk = k.lower()
            if lk in ("trust_remote_code", "use_auth_token", "use_fast_tokenizer", "torchscript"):
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
        elif "torchscript" in key_path.lower():
            findings.append(
                ConfigFinding(
                    rel,
                    "torchscript_truthy",
                    f"{key_path} is truthy ({val!r}); TorchScript / tracing paths can complicate audits and supply-chain review",
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

    safetensors_off: list[str] = []
    _walk_use_safetensors_disabled(data, "", safetensors_off)
    for key_path in safetensors_off:
        findings.append(
            ConfigFinding(
                rel,
                "use_safetensors_disabled",
                f"{key_path} is false; loaders may prefer pickle-era weight paths—prefer safetensors "
                "when your threat model cares about deserialization integrity",
            )
        )

    lfo: list[str] = []
    _walk_local_files_only_false(data, "", lfo)
    for key_path in lfo:
        findings.append(
            ConfigFinding(
                rel,
                "local_files_only_false",
                f"{key_path} is false; loaders may fetch remote Hub files at load time—confirm mirror "
                "policy and revision pinning",
            )
        )

    remote_urls: list[tuple[str, str]] = []
    _walk_remote_pretrained_url(data, "", remote_urls)
    for key_path, url in remote_urls:
        findings.append(
            ConfigFinding(
                rel,
                "remote_pretrained_identifier_url",
                f"{key_path} points to a URL ({url!r}); treat like a remote dependency with its own "
                "supply-chain and integrity story",
            )
        )

    bad_sub: list[str] = []
    _walk_subfolder_path_traversal(data, "", bad_sub)
    for key_path in bad_sub:
        findings.append(
            ConfigFinding(
                rel,
                "tokenizer_subfolder_path_traversal",
                f"{key_path} looks like a path escape (`..` or absolute prefix); verify tokenizer "
                "packaging and extraction controls",
            )
        )

    if isinstance(data, dict):
        proxies = data.get("proxies")
        if isinstance(proxies, dict) and proxies:
            findings.append(
                ConfigFinding(
                    rel,
                    "http_proxies_configured",
                    "top-level `proxies` is non-empty; verify secrets / egress policy and that this "
                    "config is not published with live corporate proxy credentials",
                )
            )

    return findings


def lint_tree(paths: list[Path]) -> list[ConfigFinding]:
    out: list[ConfigFinding] = []
    for p in paths:
        out.extend(lint_config_file(p))
    return out
