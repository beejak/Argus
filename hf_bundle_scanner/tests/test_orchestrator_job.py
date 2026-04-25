from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from hf_bundle_scanner.orchestrator_job import (
    ENVELOPE_SCHEMA_V2,
    JOB_SCHEMA_V1,
    build_envelope,
    load_job,
    validate_job,
    worst_exit_code,
)


def _fixture(name: str) -> Path:
    return Path(__file__).resolve().parent / "fixtures" / name


def test_fixture_min_validates() -> None:
    p = _fixture("orchestrator_job_min.json")
    doc = load_job(p)
    assert validate_job(doc, job_path=p, strict_paths=True) == []


def test_strict_paths_fail_when_missing() -> None:
    p = _fixture("orchestrator_job_min.json")
    doc = load_job(p)
    doc["scan_bundle"]["root"] = "does-not-exist"
    assert any("scan_bundle.root" in e for e in validate_job(doc, job_path=p, strict_paths=True))


def test_cycle_detected() -> None:
    doc = {
        "schema": JOB_SCHEMA_V1,
        "steps": [
            {"id": "a", "type": "scan_bundle", "depends_on": ["b"]},
            {"id": "b", "type": "aggregate", "depends_on": ["a"]},
        ],
        "scan_bundle": {"root": "x", "policy": "y", "out": "z"},
    }
    assert any("cycle" in e.lower() for e in validate_job(doc))


def test_run_id_must_be_uuid_when_present() -> None:
    p = _fixture("orchestrator_job_min.json")
    doc = load_job(p)
    doc["run_id"] = "not-a-uuid"
    errs = validate_job(doc, job_path=p, strict_paths=False)
    assert any("run_id" in e and "UUID" in e for e in errs)


def test_parent_run_id_must_be_uuid_when_present() -> None:
    p = _fixture("orchestrator_job_min.json")
    doc = load_job(p)
    doc["parent_run_id"] = "nope"
    errs = validate_job(doc, job_path=p, strict_paths=False)
    assert any("parent_run_id" in e and "UUID" in e for e in errs)


def test_aggregate_must_depend_on_scan() -> None:
    doc = {
        "schema": JOB_SCHEMA_V1,
        "steps": [
            {"id": "bundle_scan", "type": "scan_bundle", "depends_on": []},
            {"id": "aggregate", "type": "aggregate", "depends_on": []},
        ],
        "scan_bundle": {"root": "x", "policy": "y", "out": "z"},
    }
    assert any("depends_on must include" in e for e in validate_job(doc))


def test_build_envelope_roundtrip_json(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text("{}", encoding="utf-8")
    envelope = tmp_path / "envelope.json"
    env = build_envelope(
        run_id="00000000-0000-4000-8000-000000000002",
        parent_run_id=None,
        scan_step_id="bundle_scan",
        aggregate_step_id="aggregate",
        bundle_path=bundle,
        envelope_path=envelope,
        scan_exit=0,
        aggregate_exit=0,
        scan_started_at="2026-01-01T00:00:00Z",
        scan_ended_at="2026-01-01T00:00:01Z",
        aggregate_started_at="2026-01-01T00:00:01Z",
        aggregate_ended_at="2026-01-01T00:00:02Z",
    )
    assert env["schema"] == ENVELOPE_SCHEMA_V2
    assert env["run_id"] == "00000000-0000-4000-8000-000000000002"
    assert "parent_run_id" not in env
    assert len(env["steps"]) == 2
    assert env["steps"][0]["name"] == "scan_bundle"
    assert env["steps"][0]["artifact_uri"].startswith("file:")
    assert env["steps"][1]["name"] == "aggregate"
    json.dumps(env)


def test_worst_exit_code_priority() -> None:
    assert worst_exit_code(0, 1, 0) == 1
    assert worst_exit_code(0, 2) == 2
    assert worst_exit_code(1, 2) == 2
    assert worst_exit_code(2, 4) == 4


def test_fixture_with_dynamic_validates() -> None:
    p = _fixture("orchestrator_job_with_dynamic.json")
    doc = load_job(p)
    assert validate_job(doc, job_path=p, strict_paths=True) == []


def test_aggregate_must_depend_on_dynamic_when_present() -> None:
    doc = {
        "schema": JOB_SCHEMA_V1,
        "steps": [
            {"id": "bundle_scan", "type": "scan_bundle", "depends_on": []},
            {"id": "dyn", "type": "dynamic_probe", "depends_on": ["bundle_scan"]},
            {"id": "aggregate", "type": "aggregate", "depends_on": ["bundle_scan"]},
        ],
        "scan_bundle": {"root": "x", "policy": "y", "out": "z"},
        "dynamic_probe": {"out": "dyn.json"},
    }
    assert any("dynamic_probe step id" in e for e in validate_job(doc))


def test_dynamic_probe_depends_on_must_be_scan_only() -> None:
    doc = {
        "schema": JOB_SCHEMA_V1,
        "steps": [
            {"id": "bundle_scan", "type": "scan_bundle", "depends_on": []},
            {"id": "dyn", "type": "dynamic_probe", "depends_on": []},
            {"id": "aggregate", "type": "aggregate", "depends_on": ["bundle_scan", "dyn"]},
        ],
        "scan_bundle": {"root": "x", "policy": "y", "out": "z"},
        "dynamic_probe": {"out": "dyn.json"},
    }
    assert any("depends_on must be exactly" in e for e in validate_job(doc))


def test_dynamic_probe_settings_without_step() -> None:
    doc = {
        "schema": JOB_SCHEMA_V1,
        "steps": [
            {"id": "bundle_scan", "type": "scan_bundle", "depends_on": []},
            {"id": "aggregate", "type": "aggregate", "depends_on": ["bundle_scan"]},
        ],
        "scan_bundle": {"root": "x", "policy": "y", "out": "z"},
        "dynamic_probe": {"out": "dyn.json"},
    }
    assert any("no dynamic_probe step" in e for e in validate_job(doc))


def test_build_envelope_three_steps(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle.json"
    bundle.write_text("{}", encoding="utf-8")
    envelope = tmp_path / "envelope.json"
    dp_row = {
        "id": "dyn",
        "name": "dynamic_probe",
        "type": "dynamic_probe",
        "exit_code": 0,
        "artifact_uri": (tmp_path / "dyn.json").resolve().as_uri(),
        "started_at": "2026-01-01T00:00:01Z",
        "ended_at": "2026-01-01T00:00:02Z",
    }
    env = build_envelope(
        run_id="00000000-0000-4000-8000-000000000004",
        parent_run_id=None,
        scan_step_id="bundle_scan",
        aggregate_step_id="aggregate",
        bundle_path=bundle,
        envelope_path=envelope,
        scan_exit=0,
        aggregate_exit=0,
        scan_started_at="2026-01-01T00:00:00Z",
        scan_ended_at="2026-01-01T00:00:01Z",
        aggregate_started_at="2026-01-01T00:00:02Z",
        aggregate_ended_at="2026-01-01T00:00:03Z",
        dynamic_probe_step=dp_row,
    )
    assert env["schema"] == ENVELOPE_SCHEMA_V2
    assert len(env["steps"]) == 3
    assert env["steps"][1]["type"] == "dynamic_probe"
    assert env["steps"][1]["id"] == "dyn"
    json.dumps(env)


def test_run_orchestrator_job_with_dynamic_writes_envelope(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("LLM_SCANNER_DYNAMIC_PROBE", raising=False)
    repo = Path(__file__).resolve().parents[2]
    bundle_out = tmp_path / "bundle_report.json"
    dp_out = tmp_path / "dynamic_report.json"
    env_out = tmp_path / "envelope.json"
    job = {
        "schema": JOB_SCHEMA_V1,
        "run_id": "00000000-0000-4000-8000-000000000020",
        "steps": [
            {"id": "bundle_scan", "type": "scan_bundle", "depends_on": []},
            {"id": "dyn", "type": "dynamic_probe", "depends_on": ["bundle_scan"]},
            {"id": "aggregate", "type": "aggregate", "depends_on": ["bundle_scan", "dyn"]},
        ],
        "scan_bundle": {
            "root": str(repo / "hf_bundle_scanner/tests/fixtures/minimal_tree"),
            "policy": str(repo / "hf_bundle_scanner/tests/fixtures/policy.permissive.json"),
            "out": str(bundle_out),
            "drivers": "",
            "timeout": 600,
            "fail_on": "MEDIUM",
        },
        "dynamic_probe": {"out": str(dp_out)},
    }
    job_path = tmp_path / "job.json"
    job_path.write_text(json.dumps(job), encoding="utf-8")
    script = repo / "scripts" / "run_orchestrator_job.py"
    r = subprocess.run(
        [sys.executable, str(script), "run", "--job", str(job_path), "--envelope-out", str(env_out)],
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, (r.stdout, r.stderr)
    env = json.loads(env_out.read_text(encoding="utf-8"))
    assert env["schema"] == ENVELOPE_SCHEMA_V2
    assert len(env["steps"]) == 3
    assert env["steps"][1]["type"] == "dynamic_probe"
    assert env["steps"][1]["exit_code"] == 0
    assert dp_out.is_file()


def test_build_envelope_parent_run_id(tmp_path: Path) -> None:
    bundle = tmp_path / "b.json"
    bundle.write_text("{}", encoding="utf-8")
    env = build_envelope(
        run_id="00000000-0000-4000-8000-000000000003",
        parent_run_id="00000000-0000-4000-8000-000000000099",
        scan_step_id="s",
        aggregate_step_id="a",
        bundle_path=bundle,
        envelope_path=None,
        scan_exit=1,
        aggregate_exit=1,
        scan_started_at="2026-01-01T00:00:00Z",
        scan_ended_at="2026-01-01T00:00:01Z",
        aggregate_started_at="2026-01-01T00:00:01Z",
        aggregate_ended_at="2026-01-01T00:00:02Z",
    )
    assert env["parent_run_id"] == "00000000-0000-4000-8000-000000000099"
