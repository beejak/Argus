from __future__ import annotations

import sys
from pathlib import Path

import pytest

from hf_bundle_scanner.dispatch import run_admit_scan, scan_bundle


def _write_minimal_safetensors(path: Path) -> None:
    header = b"{}"
    n = len(header)
    path.write_bytes(n.to_bytes(8, "little") + header)


def _policy(tmp_path: Path) -> Path:
    p = tmp_path / "policy.json"
    p.write_text(
        '{"max_bytes": 1073741824, "allowed_extensions": null, "forbidden_extensions": null, "sha256_allowlist": null}',
        encoding="utf-8",
    )
    return p


def _patch_admit_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_BUNDLE_ADMIT_CMD", raising=False)
    monkeypatch.setenv("HF_BUNDLE_PYTHON", sys.executable)


def test_run_admit_scan_no_drivers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_admit_env(monkeypatch)
    art = tmp_path / "f.bin"
    art.write_bytes(b"x")
    pol = _policy(tmp_path)
    code, data, err = run_admit_scan(art, pol, drivers="", timeout=60, fail_on="MEDIUM")
    assert code == 0
    assert data is not None
    assert data.get("findings") == []


def test_scan_bundle_empty_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_admit_env(monkeypatch)
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="", timeout=60)
    assert bundle.file_scans == []
    assert bundle.aggregate_exit_code == 0


def test_scan_bundle_with_weight(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_admit_env(monkeypatch)
    _write_minimal_safetensors(tmp_path / "m.safetensors")
    (tmp_path / "config.json").write_text('{"model_type": "llama"}', encoding="utf-8")
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="", timeout=60)
    assert len(bundle.file_scans) == 1
    assert bundle.file_scans[0].relpath.endswith("m.safetensors")
    assert bundle.manifest is not None
    assert bundle.manifest["file_count"] >= 2


def test_scan_bundle_trust_remote_raises_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _patch_admit_env(monkeypatch)
    _write_minimal_safetensors(tmp_path / "m.safetensors")
    (tmp_path / "tokenizer_config.json").write_text(
        '{"trust_remote_code": true}', encoding="utf-8"
    )
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="", timeout=60)
    assert bundle.aggregate_exit_code == 1
    assert any(f["rule_id"] == "trust_remote_code_enabled" for f in bundle.config_findings)
