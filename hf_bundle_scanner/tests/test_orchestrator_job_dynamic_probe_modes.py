from __future__ import annotations

import copy
import json
from pathlib import Path

from hf_bundle_scanner.orchestrator_job import JOB_SCHEMA_V1, validate_job


def _load_dynamic_fixture() -> dict:
    root = Path(__file__).resolve().parents[1]
    p = root / "tests" / "fixtures" / "orchestrator_job_with_dynamic.json"
    return json.loads(p.read_text(encoding="utf-8"))


def test_orchestrator_job_accepts_dynamic_probe_selfcheck_mode() -> None:
    doc = _load_dynamic_fixture()
    assert doc["schema"] == JOB_SCHEMA_V1
    doc = copy.deepcopy(doc)
    doc["dynamic_probe"]["execution_mode"] = "selfcheck"
    doc["dynamic_probe"].pop("execute_args", None)
    errs = validate_job(doc, job_path=None, strict_paths=False)
    assert errs == []


def test_orchestrator_job_rejects_execute_once_without_execute_args() -> None:
    doc = _load_dynamic_fixture()
    doc = copy.deepcopy(doc)
    doc["dynamic_probe"]["execution_mode"] = "execute_once"
    doc["dynamic_probe"].pop("execute_args", None)
    errs = validate_job(doc, job_path=None, strict_paths=False)
    assert any("execute_args" in e for e in errs)
