from __future__ import annotations

import json
import re
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
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(r["report_generated_at_utc"]))
    assert re.search(r"\+05:30$", str(r["report_generated_at_ist"]))
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
        garak_config="/tmp/garak.yaml",
        model_target="openai:gpt-4.1-mini",
        execution_mode="preflight",
        executed_argv=["/usr/bin/garak", "--help"],
        secret_env_vars_required=["OPENAI_API_KEY"],
        secret_env_vars_missing=["OPENAI_API_KEY"],
        garak_cli="/usr/bin/garak",
    )
    assert r["budget_max_probes"] == 10
    assert r["budget_timeout_seconds"] == 30
    assert r["run_id"] == "00000000-0000-4000-8000-00000000abcd"
    assert r["garak_config"] == "/tmp/garak.yaml"
    assert r["model_target"] == "openai:gpt-4.1-mini"
    assert r["execution_mode"] == "preflight"
    assert r["executed_argv"] == ["/usr/bin/garak", "--help"]
    assert r["secret_env_vars_required"] == ["OPENAI_API_KEY"]
    assert r["secret_env_vars_missing"] == ["OPENAI_API_KEY"]
    assert r["garak_cli"] == "/usr/bin/garak"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(r["report_generated_at_utc"]))
    assert re.search(r"\+05:30$", str(r["report_generated_at_ist"]))


def test_build_report_honors_explicit_timestamps() -> None:
    r = build_report(
        status="ok",
        probe_backend="garak",
        message="ok",
        exit_code=0,
        report_generated_at_utc="2026-01-02T03:04:05Z",
        report_generated_at_ist="2026-01-02T08:34:05+05:30",
    )
    assert r["report_generated_at_utc"] == "2026-01-02T03:04:05Z"
    assert r["report_generated_at_ist"] == "2026-01-02T08:34:05+05:30"


def test_run_dynamic_probe_script_disabled(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LLM_SCANNER_DYNAMIC_PROBE", raising=False)
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    gcfg = tmp_path / "garak.yaml"
    gcfg.write_text("plugins: {}\n", encoding="utf-8")
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
            "--garak-config",
            str(gcfg),
            "--model-target",
            "fixture://model",
            "--secret-env-vars",
            "OPENAI_API_KEY,ANTHROPIC_API_KEY",
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
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(data["report_generated_at_utc"]))
    assert re.search(r"\+05:30$", str(data["report_generated_at_ist"]))
    assert data["budget_max_probes"] == 8
    assert data["budget_timeout_seconds"] == 33
    assert data["run_id"] == "00000000-0000-4000-8000-0000000000aa"
    assert data["garak_config"] == str(gcfg.resolve())
    assert data["model_target"] == "fixture://model"
    assert data["secret_env_vars_required"] == ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]
    assert data["execution_mode"] == "preflight"


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


def test_run_dynamic_probe_script_rejects_missing_secret_env_vars(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LLM_SCANNER_DYNAMIC_PROBE", "1")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    out = tmp_path / "dp_missing_secret.json"
    r = subprocess.run(
        [sys.executable, str(script), "--out", str(out), "--secret-env-vars", "OPENAI_API_KEY"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "error"
    assert data["secret_env_vars_missing"] == ["OPENAI_API_KEY"]


def test_run_dynamic_probe_script_rejects_execute_once_without_args(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("LLM_SCANNER_DYNAMIC_PROBE", "1")
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    out = tmp_path / "dp_exec_missing_args.json"
    r = subprocess.run(
        [sys.executable, str(script), "--out", str(out), "--execution-mode", "execute_once"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "error"
    assert "execute_once" in data["message"]


def test_run_dynamic_probe_script_accepts_inline_config_metadata_when_disabled(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("LLM_SCANNER_DYNAMIC_PROBE", raising=False)
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    out = tmp_path / "dp_inline_disabled.json"
    r = subprocess.run(
        [
            sys.executable,
            str(script),
            "--out",
            str(out),
            "--garak-config-inline",
            "plugins: {}\n",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "disabled"
    assert data["garak_config"] == "inline://dynamic_probe.garak_config_inline"


def test_run_dynamic_probe_script_rejects_both_config_sources(
    tmp_path: Path,
) -> None:
    root = _repo_root()
    script = root / "scripts" / "run_dynamic_probe.py"
    if not script.is_file():
        pytest.skip("monorepo scripts/ not present")
    cfg = tmp_path / "garak.yaml"
    cfg.write_text("plugins: {}\n", encoding="utf-8")
    out = tmp_path / "dp_both_configs.json"
    r = subprocess.run(
        [
            sys.executable,
            str(script),
            "--out",
            str(out),
            "--garak-config",
            str(cfg),
            "--garak-config-inline",
            "plugins: {}\n",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 2, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "error"
    assert "mutually exclusive" in data["message"]
