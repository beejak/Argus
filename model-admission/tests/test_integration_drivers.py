"""Optional: run when modelscan / modelaudit are on PATH."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def _minimal_safetensors(path: Path) -> None:
    """Tiny valid safetensors payload (empty tensor map)."""
    header = b"{}"
    n = len(header)
    path.write_bytes(n.to_bytes(8, "little") + header)


@pytest.mark.integration
def test_modelscan_on_minimal_safetensors(tmp_path: Path) -> None:
    if not shutil.which("modelscan"):
        pytest.skip("modelscan not installed")
    _minimal_safetensors(tmp_path / "m.safetensors")
    policy = tmp_path / "policy.json"
    policy.write_text("{}", encoding="utf-8")
    report = tmp_path / "rep.json"

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "model_admission",
            "scan",
            "--artifact",
            str(tmp_path / "m.safetensors"),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "modelscan",
            "--timeout",
            "120",
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert proc.returncode in (0, 1, 2), proc.stderr + proc.stdout
    assert report.exists()


@pytest.mark.integration
def test_modelaudit_on_minimal_safetensors(tmp_path: Path) -> None:
    if not shutil.which("modelaudit"):
        pytest.skip("modelaudit not installed")
    _minimal_safetensors(tmp_path / "m.safetensors")
    policy = tmp_path / "policy.json"
    policy.write_text("{}", encoding="utf-8")
    report = tmp_path / "rep.json"

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "model_admission",
            "scan",
            "--artifact",
            str(tmp_path / "m.safetensors"),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "modelaudit",
            "--timeout",
            "120",
        ],
        capture_output=True,
        text=True,
        timeout=180,
        env={
            **os.environ,
            "PROMPTFOO_DISABLE_TELEMETRY": "1",
            "NO_ANALYTICS": "1",
        },
    )
    assert proc.returncode in (0, 1, 2), proc.stderr + proc.stdout
    assert report.exists()
