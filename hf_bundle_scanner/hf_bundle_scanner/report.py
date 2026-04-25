"""Aggregate per-file scan reports into a single bundle document."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hf_bundle_scanner.timestamps import now_report_timestamps


@dataclass
class FileScanRecord:
    relpath: str
    exit_code: int
    report_path: str | None
    report: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "relpath": self.relpath,
            "exit_code": self.exit_code,
            "report_path": self.report_path,
            "error": self.error,
        }
        if self.report is not None:
            d["report"] = self.report
        return d


BUNDLE_REPORT_SCHEMA = "hf_bundle_scanner.bundle_report.v2"


@dataclass
class BundleReport:
    root: str
    policy_path: str
    drivers: str
    manifest: dict[str, Any] | None
    config_findings: list[dict[str, str]]
    file_scans: list[FileScanRecord]
    aggregate_exit_code: int
    provenance: dict[str, Any]
    report_generated_at_utc: str | None = None
    report_generated_at_ist: str | None = None

    def to_dict(self) -> dict[str, Any]:
        ts_utc, ts_ist = (
            (self.report_generated_at_utc, self.report_generated_at_ist)
            if self.report_generated_at_utc is not None and self.report_generated_at_ist is not None
            else now_report_timestamps()
        )
        return {
            "schema": BUNDLE_REPORT_SCHEMA,
            "taxonomy_version": "phase0",
            "report_generated_at_utc": ts_utc,
            "report_generated_at_ist": ts_ist,
            "root": self.root,
            "policy_path": self.policy_path,
            "drivers": self.drivers,
            "manifest": self.manifest,
            "config_findings": self.config_findings,
            "file_scans": [f.to_dict() for f in self.file_scans],
            "aggregate_exit_code": self.aggregate_exit_code,
            "provenance": self.provenance,
        }

    def write_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")


def compute_aggregate_exit(file_codes: list[int]) -> int:
    """Priority: any 4 (usage) > 2 (driver) > 1 (policy/findings) > 0."""
    if any(c == 4 for c in file_codes):
        return 4
    if any(c == 2 for c in file_codes):
        return 2
    if any(c == 1 for c in file_codes):
        return 1
    return 0


def merge_aggregate_exit(bundle_exit: int, config_severity: bool) -> int:
    """If configlint reports risky settings, treat as exit 1 unless bundle already worse."""
    order = {0: 0, 1: 1, 2: 2, 4: 4}
    b = order.get(bundle_exit, 2)
    if config_severity and b < 1:
        return 1
    return bundle_exit
