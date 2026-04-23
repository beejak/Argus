from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.configlint import lint_config_file


def test_trust_remote_code_finding(tmp_path: Path) -> None:
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"trust_remote_code": True}), encoding="utf-8")
    fs = lint_config_file(p)
    assert any(f.rule_id == "trust_remote_code_enabled" for f in fs)


def test_auto_map_finding(tmp_path: Path) -> None:
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"auto_map": {"AutoModel": "custom.Module"}}), encoding="utf-8")
    fs = lint_config_file(p)
    assert any(f.rule_id == "auto_map_custom_classes" for f in fs)


def test_invalid_json(tmp_path: Path) -> None:
    p = tmp_path / "config.json"
    p.write_text("{", encoding="utf-8")
    fs = lint_config_file(p)
    assert fs and fs[0].rule_id == "config_json_invalid"


def test_use_fast_tokenizer_finding(tmp_path: Path) -> None:
    p = tmp_path / "tokenizer_config.json"
    p.write_text(json.dumps({"use_fast_tokenizer": True}), encoding="utf-8")
    fs = lint_config_file(p)
    assert any(f.rule_id == "use_fast_tokenizer_truthy" for f in fs)
