from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _run_admit(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "model_admission", *args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_cli_scan_no_drivers_passes(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text('{"max_bytes": 1000000}', encoding="utf-8")
    artifact = tmp_path / "note.txt"
    artifact.write_text("hello", encoding="utf-8")
    report = tmp_path / "out.json"

    proc = _run_admit(
        [
            "scan",
            "--artifact",
            str(artifact),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "",
        ]
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["artifact_sha256"]
    assert data["drivers_run"] == []
    assert data["findings"] == []


def test_cli_scan_policy_forbidden_extension_fails(tmp_path: Path) -> None:
    policy = tmp_path / "policy.json"
    policy.write_text(
        json.dumps(
            {
                "max_bytes": 1000000,
                "forbidden_extensions": [".pkl"],
            }
        ),
        encoding="utf-8",
    )
    bad = tmp_path / "evil.pkl"
    bad.write_bytes(b"not-really-pickle")
    report = tmp_path / "out.json"

    proc = _run_admit(
        [
            "scan",
            "--artifact",
            str(bad),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "",
        ]
    )
    assert proc.returncode == 1
    data = json.loads(report.read_text(encoding="utf-8"))
    assert any(f.get("driver") == "policy" for f in data["findings"])


def test_cli_version() -> None:
    from importlib.metadata import version as pkg_version

    proc = subprocess.run(
        [sys.executable, "-m", "model_admission", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0
    assert pkg_version("model-admission") in (proc.stdout + proc.stderr)
