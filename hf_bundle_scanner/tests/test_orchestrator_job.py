from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.orchestrator_job import (
    ENVELOPE_SCHEMA_V2,
    JOB_SCHEMA_V1,
    build_envelope,
    load_job,
    validate_job,
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
