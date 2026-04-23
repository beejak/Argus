"""Driver and CLI behavior for tool errors (exit 2) and timeouts — no real scanners required."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from model_admission.drivers.modelaudit import ModelAuditDriver
from model_admission.drivers.modelscan import ModelScanDriver


def _fake_modelscan_run(argv: list[str], **_kwargs):
    i = argv.index("-o")
    out = Path(argv[i + 1])
    out.write_text("{not valid json", encoding="utf-8")
    return subprocess.CompletedProcess(argv, 0, "", "")


def test_modelscan_driver_malformed_json_is_error() -> None:
    drv = ModelScanDriver()
    artifact = Path("/tmp/does-not-need-to-exist-for-mock")
    with (
        patch.object(ModelScanDriver, "_which", return_value="/fake/modelscan"),
        patch.object(ModelScanDriver, "_run", side_effect=_fake_modelscan_run),
    ):
        findings, err = drv.scan(artifact, 60)
    assert findings == []
    assert err and "JSON parse error" in err


def test_modelscan_driver_tool_exit_2() -> None:
    drv = ModelScanDriver()
    proc = subprocess.CompletedProcess(["m"], 2, "", "scan blew up")
    with (
        patch.object(ModelScanDriver, "_which", return_value="/fake/modelscan"),
        patch.object(ModelScanDriver, "_run", return_value=proc),
    ):
        findings, err = drv.scan(Path("/tmp/x"), 60)
    assert findings == []
    assert err and "exit 2" in err


def test_modelscan_driver_subprocess_timeout_returncode() -> None:
    drv = ModelScanDriver()
    proc = subprocess.CompletedProcess(["m"], -1, "", "subprocess timed out after 3s")
    with (
        patch.object(ModelScanDriver, "_which", return_value="/fake/modelscan"),
        patch.object(ModelScanDriver, "_run", return_value=proc),
    ):
        findings, err = drv.scan(Path("/tmp/x"), 3)
    assert findings == []
    assert err and "timed out" in err.lower()


def _fake_modelaudit_run(argv: list[str], **_kwargs):
    i = argv.index("--output")
    out = Path(argv[i + 1])
    out.write_text("{{{", encoding="utf-8")
    return subprocess.CompletedProcess(argv, 0, "", "")


def test_modelaudit_driver_malformed_json_is_error() -> None:
    drv = ModelAuditDriver()
    artifact = Path("/tmp/x")
    with (
        patch.object(ModelAuditDriver, "_which", return_value="/fake/modelaudit"),
        patch.object(ModelAuditDriver, "_run", side_effect=_fake_modelaudit_run),
    ):
        findings, err = drv.scan(artifact, 60)
    assert findings == []
    assert err and "JSON parse error" in err


def test_modelaudit_driver_tool_exit_2() -> None:
    drv = ModelAuditDriver()
    proc = subprocess.CompletedProcess(["m"], 2, "", "audit failed")
    with (
        patch.object(ModelAuditDriver, "_which", return_value="/fake/modelaudit"),
        patch.object(ModelAuditDriver, "_run", return_value=proc),
    ):
        findings, err = drv.scan(Path("/tmp/x"), 60)
    assert findings == []
    assert err and "exit 2" in err


def test_modelaudit_driver_subprocess_timeout_returncode() -> None:
    drv = ModelAuditDriver()
    proc = subprocess.CompletedProcess(["m"], -1, "", "subprocess timed out after 2s")
    with (
        patch.object(ModelAuditDriver, "_which", return_value="/fake/modelaudit"),
        patch.object(ModelAuditDriver, "_run", return_value=proc),
    ):
        findings, err = drv.scan(Path("/tmp/x"), 2)
    assert findings == []
    assert err and "timed out" in err.lower()


def _write_posix_executable(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable stub for PATH resolution")
def test_cli_scan_driver_error_yields_exit_2(tmp_path: Path) -> None:
    stub = tmp_path / "modelscan"
    _write_posix_executable(
        stub,
        "#!/bin/sh\nexit 2\n",
    )
    policy = tmp_path / "policy.json"
    policy.write_text("{}", encoding="utf-8")
    artifact = tmp_path / "f.bin"
    artifact.write_bytes(b"x")
    report = tmp_path / "out.json"
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ.get('PATH', '')}"}
    env.pop("MODELSCAN_BIN", None)

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "model_admission",
            "scan",
            "--artifact",
            str(artifact),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "modelscan",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert proc.returncode == 2, proc.stderr + proc.stdout
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["driver_errors"]


@pytest.mark.skipif(os.name == "nt", reason="POSIX executable stub for PATH resolution")
def test_cli_scan_driver_timeout_yields_exit_2(tmp_path: Path) -> None:
    stub = tmp_path / "modelscan"
    _write_posix_executable(
        stub,
        "#!/bin/sh\nsleep 30\n",
    )
    policy = tmp_path / "policy.json"
    policy.write_text("{}", encoding="utf-8")
    artifact = tmp_path / "f.bin"
    artifact.write_bytes(b"x")
    report = tmp_path / "out.json"
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ.get('PATH', '')}"}
    env.pop("MODELSCAN_BIN", None)

    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "model_admission",
            "scan",
            "--artifact",
            str(artifact),
            "--policy",
            str(policy),
            "--report",
            str(report),
            "--drivers",
            "modelscan",
            "--timeout",
            "1",
        ],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )
    assert proc.returncode == 2, proc.stderr + proc.stdout
    data = json.loads(report.read_text(encoding="utf-8"))
    assert any("timed out" in e.lower() for e in data["driver_errors"])
