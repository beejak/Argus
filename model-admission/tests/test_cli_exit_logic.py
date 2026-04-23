"""Exit logic for --fail-on (imports private helpers — stable contract tests)."""

from __future__ import annotations

import argparse

import pytest

from model_admission.cli import _any_finding_at_or_above, _min_severity
from model_admission.report import Finding, Severity


def test_min_severity_parsing() -> None:
    assert _min_severity("medium") == Severity.MEDIUM
    assert _min_severity("HIGH") == Severity.HIGH
    with pytest.raises(argparse.ArgumentTypeError):
        _min_severity("nope")


def test_any_finding_at_or_above_respects_floor() -> None:
    low = Finding("d", Severity.LOW, "a")
    assert not _any_finding_at_or_above([low], Severity.MEDIUM)
    assert _any_finding_at_or_above([low], Severity.LOW)
    med = Finding("d", Severity.MEDIUM, "b")
    assert _any_finding_at_or_above([low, med], Severity.MEDIUM)
    assert not _any_finding_at_or_above([low], Severity.HIGH)
