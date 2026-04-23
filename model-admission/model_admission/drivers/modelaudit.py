from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from model_admission.drivers.base import ScanDriver, finding_from_severity
from model_admission.report import Finding, Severity


class ModelAuditDriver(ScanDriver):
    name = "modelaudit"

    def scan(self, artifact: Path, timeout_sec: int) -> tuple[list[Finding], str | None]:
        bin_name = os.environ.get("MODELAUDIT_BIN", "modelaudit")
        exe = self._which(bin_name)
        if not exe:
            return (
                [],
                "modelaudit executable not found (set MODELAUDIT_BIN or pip install modelaudit)",
            )
        env_extra = {
            "PROMPTFOO_DISABLE_TELEMETRY": "1",
            "NO_ANALYTICS": "1",
        }
        findings: list[Finding] = []
        with tempfile.TemporaryDirectory(prefix="modelaudit-") as td:
            out = Path(td) / "results.json"
            argv = [
                exe,
                "scan",
                str(artifact),
                "--format",
                "json",
                "--output",
                str(out),
            ]
            proc = self._run(argv, timeout_sec=timeout_sec, env_extra=env_extra)
            if proc.returncode == -1:
                return [], proc.stderr or "modelaudit subprocess timed out"
            if proc.returncode == 2:
                return (
                    [],
                    f"modelaudit scan error (exit 2): {proc.stderr or proc.stdout}",
                )
            if out.exists():
                try:
                    data = json.loads(out.read_text(encoding="utf-8"))
                    findings.extend(self._parse_json(data))
                except json.JSONDecodeError as e:
                    return [], f"modelaudit JSON parse error: {e}"
            elif proc.returncode == 1:
                findings.append(
                    finding_from_severity(
                        self.name,
                        "HIGH",
                        "modelaudit reported issues (no JSON file)",
                        (proc.stdout or proc.stderr or "")[:8000],
                    )
                )
        return findings, None

    def _parse_json(self, data: object) -> list[Finding]:
        out: list[Finding] = []
        if not isinstance(data, dict):
            return out
        issues = data.get("issues") or data.get("findings") or data.get("results") or []
        if isinstance(issues, dict):
            issues = list(issues.values())
        if not isinstance(issues, list):
            return out
        for item in issues:
            if not isinstance(item, dict):
                continue
            sev = str(
                item.get("severity")
                or item.get("level")
                or item.get("severity_level")
                or "MEDIUM"
            )
            title = str(item.get("title") or item.get("rule") or item.get("type") or "issue")
            detail = str(item.get("message") or item.get("detail") or item.get("why") or "")
            out.append(finding_from_severity(self.name, sev, title, detail))
        if not out and data.get("summary"):
            summ = data["summary"]
            if isinstance(summ, dict):
                crit = int(summ.get("critical") or 0)
                high = int(summ.get("high") or 0)
                if crit + high > 0:
                    out.append(
                        Finding(
                            driver=self.name,
                            severity=Severity.CRITICAL if crit else Severity.HIGH,
                            title="Issues reported in summary",
                            detail=json.dumps(summ)[:4000],
                        )
                    )
        return out
