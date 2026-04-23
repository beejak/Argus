"""ScanReport / Finding serialization and severity aggregation."""

from __future__ import annotations

import json
from pathlib import Path

from model_admission.report import Finding, ScanReport, Severity


def test_finding_to_dict_severity_is_string() -> None:
    f = Finding(driver="x", severity=Severity.HIGH, title="t", detail="d")
    d = f.to_dict()
    assert d["severity"] == "high"
    assert d["driver"] == "x"
    assert "rule_id" not in d
    assert "category" not in d


def test_finding_to_dict_includes_rule_id_when_set() -> None:
    f = Finding(
        driver="x",
        severity=Severity.MEDIUM,
        title="t",
        rule_id="modelscan.foo",
        category="artifact",
    )
    d = f.to_dict()
    assert d["rule_id"] == "modelscan.foo"
    assert d["category"] == "artifact"


def test_scan_report_highest_severity() -> None:
    rep = ScanReport(
        artifact_path="/a",
        artifact_sha256="0" * 64,
        policy_path="/p",
        drivers_run=["modelscan"],
        findings=[
            Finding("m", Severity.LOW, "l"),
            Finding("m", Severity.CRITICAL, "c"),
            Finding("m", Severity.MEDIUM, "m"),
        ],
    )
    assert rep.highest_severity() == Severity.CRITICAL


def test_scan_report_highest_none_when_empty() -> None:
    rep = ScanReport(
        artifact_path="/a",
        artifact_sha256="",
        policy_path=None,
        drivers_run=[],
        findings=[],
    )
    assert rep.highest_severity() is None


def test_scan_report_write_json_roundtrip(tmp_path: Path) -> None:
    rep = ScanReport(
        artifact_path=str(tmp_path / "m.bin"),
        artifact_sha256="ab" * 32,
        policy_path=str(tmp_path / "pol.json"),
        drivers_run=["modelscan"],
        findings=[Finding("modelscan", Severity.MEDIUM, "x", "y")],
    )
    out = tmp_path / "r.json"
    rep.write_json(out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["artifact_sha256"] == "ab" * 32
    assert len(data["findings"]) == 1
    assert data["findings"][0]["severity"] == "medium"
