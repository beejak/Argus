"""Driver registry and JSON parsing without invoking external binaries."""

from __future__ import annotations

import subprocess

import pytest

from model_admission.drivers import DRIVERS, get_driver
from model_admission.drivers.modelaudit import ModelAuditDriver
from model_admission.drivers.modelscan import ModelScanDriver, _MIN_PICKLESCAN_VERSION, _parse_version
from model_admission.report import Severity


def test_get_driver_known() -> None:
    assert get_driver("modelscan").name == "modelscan"
    assert get_driver("ModelAudit").name == "modelaudit"


def test_get_driver_unknown() -> None:
    with pytest.raises(KeyError, match="unknown driver"):
        get_driver("not-a-driver")


def test_drivers_registry_contains_expected_keys() -> None:
    assert set(DRIVERS) == {"modelaudit", "modelscan"}


def test_modelscan_parse_json_issues_list() -> None:
    drv = ModelScanDriver()
    sample = {
        "issues": [
            {"severity": "HIGH", "title": "Pickle risk", "description": "detail"},
        ]
    }
    findings = drv._parse_json_report(sample)
    assert len(findings) == 1
    assert findings[0].severity == Severity.HIGH
    assert findings[0].title == "Pickle risk"


def test_modelscan_parse_nested_all_issues() -> None:
    drv = ModelScanDriver()
    sample = {"issues": {"all_issues": [{"severity": "CRITICAL", "type": "X", "message": "m"}]}}
    findings = drv._parse_json_report(sample)
    assert len(findings) == 1
    assert findings[0].severity == Severity.CRITICAL


def test_modelaudit_parse_findings_list() -> None:
    drv = ModelAuditDriver()
    sample = {"findings": [{"severity": "HIGH", "title": "Leak", "message": "detail"}]}
    findings = drv._parse_json(sample)
    assert len(findings) == 1
    assert findings[0].severity == Severity.HIGH
    assert findings[0].title == "Leak"


def test_modelaudit_parse_summary_fallback() -> None:
    drv = ModelAuditDriver()
    sample = {"summary": {"critical": 1, "high": 0}}
    findings = drv._parse_json(sample)
    assert len(findings) == 1
    assert findings[0].severity == Severity.CRITICAL


# ---------------------------------------------------------------------------
# _parse_version unit tests
# ---------------------------------------------------------------------------


def test_parse_version_standard() -> None:
    assert _parse_version("modelscan, version 0.0.31") == (0, 0, 31)


def test_parse_version_bare() -> None:
    assert _parse_version("0.1.5") == (0, 1, 5)


def test_parse_version_unparseable_returns_none() -> None:
    assert _parse_version("no version here") is None


def test_parse_version_extracts_first_triple() -> None:
    assert _parse_version("foo 1.2.3 bar 4.5.6") == (1, 2, 3)


# ---------------------------------------------------------------------------
# _version_warning integration with _run
# ---------------------------------------------------------------------------


def _make_completed(stdout: str = "", returncode: int = 0) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


def test_version_warning_old_version_emits_finding(monkeypatch: pytest.MonkeyPatch) -> None:
    drv = ModelScanDriver()
    monkeypatch.setattr(drv, "_run", lambda *a, **kw: _make_completed("modelscan, version 0.0.28"))
    finding = drv._version_warning("/fake/modelscan")
    assert finding is not None
    assert finding.rule_id == "modelscan.outdated_picklescan"
    assert finding.severity == Severity.LOW
    assert "0.0.28" in finding.title
    assert "CVE-2025-10155" in finding.detail


def test_version_warning_current_version_no_finding(monkeypatch: pytest.MonkeyPatch) -> None:
    drv = ModelScanDriver()
    min_str = ".".join(str(x) for x in _MIN_PICKLESCAN_VERSION)
    monkeypatch.setattr(drv, "_run", lambda *a, **kw: _make_completed(f"modelscan, version {min_str}"))
    assert drv._version_warning("/fake/modelscan") is None


def test_version_warning_newer_version_no_finding(monkeypatch: pytest.MonkeyPatch) -> None:
    drv = ModelScanDriver()
    monkeypatch.setattr(drv, "_run", lambda *a, **kw: _make_completed("modelscan, version 1.0.0"))
    assert drv._version_warning("/fake/modelscan") is None


def test_version_warning_unparseable_output_no_finding(monkeypatch: pytest.MonkeyPatch) -> None:
    """If we can't parse the version we don't block — fail open not fail closed."""
    drv = ModelScanDriver()
    monkeypatch.setattr(drv, "_run", lambda *a, **kw: _make_completed("some unknown output"))
    assert drv._version_warning("/fake/modelscan") is None


def test_version_warning_exception_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exceptions in version check must never crash the scan."""
    drv = ModelScanDriver()

    def _raise(*a: object, **kw: object) -> None:
        raise RuntimeError("unexpected")

    monkeypatch.setattr(drv, "_run", _raise)
    assert drv._version_warning("/fake/modelscan") is None


# ---------------------------------------------------------------------------
# Version warning preserved on error return paths
# ---------------------------------------------------------------------------


def test_version_warn_preserved_on_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Version warning finding must survive a modelscan timeout (returncode -1)."""
    drv = ModelScanDriver()
    call_count = 0

    def _mock_run(argv: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        nonlocal call_count
        call_count += 1
        if "--version" in argv:
            return _make_completed("modelscan, version 0.0.28")
        return _make_completed("timed out", returncode=-1)

    monkeypatch.setattr(drv, "_run", _mock_run)
    monkeypatch.setattr(drv, "_which", lambda _: "/fake/modelscan")
    from pathlib import Path
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        art = Path(f.name)
    try:
        findings, err = drv.scan(art, timeout_sec=5)
    finally:
        os.unlink(art)
    assert any(f.rule_id == "modelscan.outdated_picklescan" for f in findings)
    assert err is not None


def test_version_warn_preserved_on_usage_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Version warning finding must survive a modelscan usage error (returncode 4)."""
    drv = ModelScanDriver()

    def _mock_run(argv: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        if "--version" in argv:
            return _make_completed("modelscan, version 0.0.28")
        return _make_completed("bad args", returncode=4)

    monkeypatch.setattr(drv, "_run", _mock_run)
    monkeypatch.setattr(drv, "_which", lambda _: "/fake/modelscan")
    from pathlib import Path
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        art = Path(f.name)
    try:
        findings, err = drv.scan(art, timeout_sec=5)
    finally:
        os.unlink(art)
    assert any(f.rule_id == "modelscan.outdated_picklescan" for f in findings)
    assert err is not None
