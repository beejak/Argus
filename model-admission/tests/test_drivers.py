"""Driver registry and JSON parsing without invoking external binaries."""

from __future__ import annotations

import pytest

from model_admission.drivers import DRIVERS, get_driver
from model_admission.drivers.modelscan import ModelScanDriver
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
