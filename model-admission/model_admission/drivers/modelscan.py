from __future__ import annotations

import json
import os
import re
import tempfile
from pathlib import Path

from model_admission.drivers.base import ScanDriver, finding_from_severity
from model_admission.report import Finding, Severity

# CVE-2025-10155 / CVE-2025-10156 / CVE-2025-10157 were patched in 0.0.31.
# Running an older version means .bin/.pt rename bypass, CRC-zeroed ZIP bypass,
# and subclassed module path bypass are all undetected.
_MIN_PICKLESCAN_VERSION = (0, 0, 31)
_VERSION_RULE_ID = "modelscan.outdated_picklescan"


def _parse_version(text: str) -> tuple[int, ...] | None:
    """Extract the first X.Y.Z triple from a version string."""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    return None


class ModelScanDriver(ScanDriver):
    name = "modelscan"

    def _version_warning(self, exe: str) -> Finding | None:
        """Return a LOW finding if picklescan is below the minimum safe version."""
        try:
            proc = self._run([exe, "--version"], timeout_sec=15)
            output = (proc.stdout or "") + (proc.stderr or "")
            version = _parse_version(output)
            if version is None:
                return None  # can't parse — don't block
            if version < _MIN_PICKLESCAN_VERSION:
                min_str = ".".join(str(x) for x in _MIN_PICKLESCAN_VERSION)
                found_str = ".".join(str(x) for x in version)
                return finding_from_severity(
                    self.name,
                    "LOW",
                    f"modelscan {found_str} is below minimum safe version {min_str}",
                    f"CVE-2025-10155/10156/10157 allow .bin/.pt rename bypass, "
                    f"CRC-zeroed ZIP bypass, and subclassed module path bypass in "
                    f"picklescan < {min_str}. Update with: pip install 'modelscan>={min_str}'",
                    rule_id=_VERSION_RULE_ID,
                    category="supply_chain",
                )
        except Exception:
            pass
        return None

    def scan(self, artifact: Path, timeout_sec: int) -> tuple[list[Finding], str | None]:
        bin_name = os.environ.get("MODELSCAN_BIN", "modelscan")
        exe = self._which(bin_name)
        if not exe:
            return (
                [],
                "modelscan executable not found (set MODELSCAN_BIN or install modelscan)",
            )
        findings: list[Finding] = []
        version_warn = self._version_warning(exe)
        if version_warn:
            findings.append(version_warn)
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
