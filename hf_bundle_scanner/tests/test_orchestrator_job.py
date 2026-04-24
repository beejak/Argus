from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.orchestrator_job import (
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


def test_build_envelope_roundtrip_json() -> None:
    env = build_envelope(
        run_id="r1",
        scan_step_id="bundle_scan",
        bundle_path=Path("/tmp/b.json"),
        scan_exit=0,
        aggregate_exit=0,
    )
    json.dumps(env)
