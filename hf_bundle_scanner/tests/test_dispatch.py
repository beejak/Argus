from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

from hf_bundle_scanner.dispatch import run_admit_scan, scan_bundle
from hf_bundle_scanner.report import BundleReport


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
    bundle = scan_bundle(
        tmp_path,
        pol,
        drivers="",
        timeout=60,
        hub_repo_id="demo/repo",
        hub_revision="abc123",
        sbom_uri="https://example.invalid/sbom.json",
    )
    assert len(bundle.file_scans) == 1
    assert bundle.file_scans[0].relpath.endswith("m.safetensors")
    assert bundle.manifest is not None
    assert bundle.manifest["file_count"] >= 2
    d = bundle.to_dict()
    assert d["schema"] == "hf_bundle_scanner.bundle_report.v2"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(d["report_generated_at_utc"]))
    assert re.search(r"\+05:30$", str(d["report_generated_at_ist"]))
    assert d["provenance"]["provenance_version"] == "phase1"
    assert d["provenance"]["hub"] == {"repo_id": "demo/repo", "revision": "abc123"}
    assert d["provenance"]["sbom"] == {"uri": "https://example.invalid/sbom.json"}
    assert "manifest_summary" in d["provenance"]


def test_scan_bundle_modelscan_missing_binary_is_driver_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Phase2 static drivers: missing ModelScan binary → admit exit 2 → bundle aggregate 2."""
    _patch_admit_env(monkeypatch)
    monkeypatch.setenv("MODELSCAN_BIN", str(tmp_path / "no-such-modelscan"))
    _write_minimal_safetensors(tmp_path / "m.safetensors")
    (tmp_path / "config.json").write_text('{"model_type": "bert"}', encoding="utf-8")
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="modelscan", timeout=60)
    assert len(bundle.file_scans) == 1
    assert bundle.file_scans[0].exit_code == 2
    assert bundle.aggregate_exit_code == 2


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


def test_run_admit_scan_timeout_returns_tooling_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A hung subprocess must not crash the scan — it must return exit_code=2 (tooling error)."""
    import hf_bundle_scanner.dispatch as dispatch_mod

    _patch_admit_env(monkeypatch)

    def _raise_timeout(*args: object, **kwargs: object) -> None:
        raise subprocess.TimeoutExpired(cmd=["admit-model"], timeout=60)

    monkeypatch.setattr(dispatch_mod.subprocess, "run", _raise_timeout)

    art = tmp_path / "f.bin"
    art.write_bytes(b"x")
    pol = _policy(tmp_path)
    code, data, err = run_admit_scan(art, pol, drivers="", timeout=60, fail_on="MEDIUM")

    assert code == 2
    assert data is None
    assert err is not None and ("timeout" in err.lower() or "timed out" in err.lower())


def test_scan_bundle_timeout_on_one_file_does_not_abort_others(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Timeout on one file must yield exit_code=2 for that record and not stop remaining files."""
    import hf_bundle_scanner.dispatch as dispatch_mod

    _patch_admit_env(monkeypatch)

    call_count = 0
    real_run = dispatch_mod.subprocess.run

    def _timeout_first_then_real(*args: object, **kwargs: object) -> object:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise subprocess.TimeoutExpired(cmd=args[0] if args else [], timeout=60)
        return real_run(*args, **kwargs)

    monkeypatch.setattr(dispatch_mod.subprocess, "run", _timeout_first_then_real)

    _write_minimal_safetensors(tmp_path / "a.safetensors")
    _write_minimal_safetensors(tmp_path / "b.safetensors")
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="", timeout=60)

    assert len(bundle.file_scans) == 2
    exit_codes = {r.relpath.split("/")[-1]: r.exit_code for r in bundle.file_scans}
    assert exit_codes["a.safetensors"] == 2
    assert exit_codes["b.safetensors"] == 0
    assert bundle.aggregate_exit_code == 2


def test_scan_bundle_script_lint_trust_remote_code_detected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Bundled .py with trust_remote_code=True must appear in config_findings and raise aggregate."""
    _patch_admit_env(monkeypatch)
    py_file = tmp_path / "train.py"
    py_file.write_text("from transformers import AutoModel\nAutoModel.from_pretrained('x', trust_remote_code=True)\n", encoding="utf-8")
    pol = _policy(tmp_path)
    bundle = scan_bundle(tmp_path, pol, drivers="", timeout=60)
    assert any(f.get("rule_id") == "trust_remote_code_in_script" for f in bundle.config_findings)
    assert bundle.aggregate_exit_code == 1


def test_bundle_report_timestamps_remain_stable_across_to_dict_calls() -> None:
    rep = BundleReport(
        root="/tmp/root",
        policy_path="/tmp/policy.json",
        drivers="",
        manifest=None,
        config_findings=[],
        file_scans=[],
        aggregate_exit_code=0,
        provenance={"provenance_version": "phase1"},
        report_generated_at_utc="2026-01-02T03:04:05Z",
        report_generated_at_ist="2026-01-02T08:34:05+05:30",
    )
    a = rep.to_dict()
    b = rep.to_dict()
    assert a["report_generated_at_utc"] == b["report_generated_at_utc"]
    assert a["report_generated_at_ist"] == b["report_generated_at_ist"]
