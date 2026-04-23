from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _write_minimal_safetensors(path: Path) -> None:
    header = b"{}"
    n = len(header)
    path.write_bytes(n.to_bytes(8, "little") + header)


def test_cli_manifest_subcommand(tmp_path: Path) -> None:
    (tmp_path / "a").write_text("x", encoding="utf-8")
    out = tmp_path / "m.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "hf_bundle_scanner",
            "manifest",
            "--root",
            str(tmp_path),
            "--out",
            str(out),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["file_count"] >= 1


def test_cli_scan_subcommand(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_BUNDLE_ADMIT_CMD", raising=False)
    monkeypatch.setenv("HF_BUNDLE_PYTHON", sys.executable)
    _write_minimal_safetensors(tmp_path / "w.safetensors")
    pol = tmp_path / "policy.json"
    pol.write_text(
        '{"max_bytes": 1073741824, "forbidden_extensions": null, "allowed_extensions": null, "sha256_allowlist": null}',
        encoding="utf-8",
    )
    out = tmp_path / "bundle.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "hf_bundle_scanner",
            "scan",
            "--root",
            str(tmp_path),
            "--policy",
            str(pol),
            "--out",
            str(out),
            "--drivers",
            "",
            "--no-manifest",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == "hf_bundle_scanner.bundle_report.v2"
    assert data["provenance"]["provenance_version"] == "phase1"
