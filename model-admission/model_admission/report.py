from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Finding:
    driver: str
    severity: Severity
    title: str
    detail: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    rule_id: str = ""
    category: str = ""

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "driver": self.driver,
            "severity": self.severity.value,
            "title": self.title,
            "detail": self.detail,
        }
        if self.raw:
            d["raw"] = self.raw
        if self.rule_id:
            d["rule_id"] = self.rule_id
        if self.category:
            d["category"] = self.category
        return d


@dataclass
class ScanReport:
    artifact_path: str
    artifact_sha256: str
    policy_path: str | None
    drivers_run: list[str]
    findings: list[Finding]
    driver_errors: list[str] = field(default_factory=list)

    def highest_severity(self) -> Severity | None:
        order = {
            Severity.CRITICAL: 5,
            Severity.HIGH: 4,
            Severity.MEDIUM: 3,
            Severity.LOW: 2,
            Severity.INFO: 1,
        }
        best: Finding | None = None
        for f in self.findings:
            if best is None or order[f.severity] > order[best.severity]:
                best = f
        return best.severity if best else None

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_path": self.artifact_path,
            "artifact_sha256": self.artifact_sha256,
            "policy_path": self.policy_path,
            "drivers_run": self.drivers_run,
            "driver_errors": self.driver_errors,
            "findings": [f.to_dict() for f in self.findings],
        }

    def write_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
