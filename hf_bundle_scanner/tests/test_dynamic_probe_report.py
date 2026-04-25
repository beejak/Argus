from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from hf_bundle_scanner.dynamic_probe_report import DYNAMIC_PROBE_SCHEMA_V1, build_report


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_build_report_disabled() -> None:
    r = build_report(
        status="disabled",
        probe_backend="none",
        message="off",
        exit_code=0,
    )
    assert r["schema"] == DYNAMIC_PROBE_SCHEMA_V1
    assert r["status"] == "disabled"
    assert "budget_max_probes" not in r
    json.dumps(r)


def test_build_report_with_budget_and_cli() -> None:
    r = build_report(
        status="ok",
        probe_backend="garak",
        message="ok",
        exit_code=0,
        budget_max_probes=10,
        budget_timeout_seconds=30,
        run_id="00000000-0000-4000-8000-00000000abcd",
        garak_cli="/usr/bin/garak",
    )
    assert r["budget_max_probes"] == 10
    assert r["budget_timeout_seconds"] == 30
    assert r["run_id"] == "00000000-0000-4000-8000-00000000abcd"
    assert r["garak_cli"] == "/usr/bin/garak"


def test_run_dynamic_probe_script_disabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_SCANNER_DYNAMIC_PROBE", raising=False)
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    out = tmp_path / "dp.json"
    r = subprocess.run(
        [
            sys.executable,
            str(script),
            "--out",
            str(out),
            "--budget-max-probes",
            "8",
            "--budget-timeout-seconds",
            "33",
            "--run-id",
            "00000000-0000-4000-8000-0000000000aa",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schema"] == DYNAMIC_PROBE_SCHEMA_V1
    assert data["status"] == "disabled"
    assert data["budget_max_probes"] == 8
    assert data["budget_timeout_seconds"] == 33
    assert data["run_id"] == "00000000-0000-4000-8000-0000000000aa"


def test_run_dynamic_probe_script_rejects_invalid_budget(tmp_path: Path) -> None:
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    out = tmp_path / "dp_invalid.json"
    r = subprocess.run(
        [sys.executable, str(script), "--out", str(out), "--budget-max-probes", "0"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "error"
    assert "budget_max_probes" in data["message"]
