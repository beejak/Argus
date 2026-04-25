from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from model_admission.drivers.base import ScanDriver, finding_from_severity
from model_admission.report import Finding, Severity


class ModelScanDriver(ScanDriver):
    name = "modelscan"

    def scan(self, artifact: Path, timeout_sec: int) -> tuple[list[Finding], str | None]:
        bin_name = os.environ.get("MODELSCAN_BIN", "modelscan")
        exe = self._which(bin_name)
        if not exe:
            return (
                [],
                "modelscan executable not found (set MODELSCAN_BIN or install modelscan)",
            )
        findings: list[Finding] = []
        with tempfile.TemporaryDirectory(prefix="modelscan-") as td:
            out = Path(td) / "report.json"
            argv = [exe, "-p", str(artifact), "-r", "json", "-o", str(out)]
            proc = self._run(argv, timeout_sec=timeout_sec)
            if proc.returncode == -1:
                return [], proc.stderr or "modelscan subprocess timed out"
            if proc.returncode == 4:
                return [], f"modelscan usage error: {proc.stderr or proc.stdout}"
            if proc.returncode == 3:
                findings.append(
                    Finding(
                        driver=self.name,
                        severity=Severity.MEDIUM,
                        title="No supported files",
                        detail="modelscan returned exit 3 (unsupported or empty scan set)",
                    )
                )
                return findings, None
            if proc.returncode == 2:
                return (
                    [],
                    f"modelscan scan failed (exit 2): {proc.stderr or proc.stdout}",
                )
            if out.exists():
                try:
                    data = json.loads(out.read_text(encoding="utf-8"))
                    findings.extend(self._parse_json_report(data))
                except json.JSONDecodeError as e:
                    return [], f"modelscan JSON parse error: {e}"
            elif proc.returncode == 1:
                # vulnerabilities but no output file?
                findings.append(
                    finding_from_severity(
                        self.name,
                        "HIGH",
                        "modelscan reported issues",
                        proc.stdout or proc.stderr or "",
                    )
                )
            if proc.returncode == 1 and not findings:
                findings.append(
                    finding_from_severity(
                        self.name,
                        "HIGH",
                        "modelscan exit 1 (issues found)",
                        (proc.stdout or "")[:8000],
                    )
                )
        return findings, None

    def _parse_json_report(self, data: object) -> list[Finding]:
        out: list[Finding] = []
        if not isinstance(data, dict):
            return out
        issues = data.get("issues") or data.get("scan_results") or []
        if isinstance(issues, dict):
            issues = issues.get("all_issues") or issues.get("issues") or []
        if not isinstance(issues, list):
            return out
        for item in issues:
            if not isinstance(item, dict):
                continue
            sev = str(item.get("severity") or item.get("level") or "MEDIUM")
            title = str(item.get("title") or item.get("name") or item.get("type") or "issue")
            detail = str(item.get("description") or item.get("details") or item.get("message") or "")
            out.append(finding_from_severity(self.name, sev, title, detail))
        return out
