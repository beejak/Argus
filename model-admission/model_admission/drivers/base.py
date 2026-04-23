from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from pathlib import Path

from model_admission.report import Finding, Severity


class ScanDriver(ABC):
    name: str

    @abstractmethod
    def scan(self, artifact: Path, timeout_sec: int) -> tuple[list[Finding], str | None]:
        """Run scan. Returns (findings, error_message_or_none)."""

    def _which(self, binary: str) -> str | None:
        return shutil.which(binary)

    def _run(
        self,
        argv: list[str],
        *,
        timeout_sec: int,
        env_extra: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        if env_extra:
            env.update(env_extra)
        # Strip inherited secrets from subprocess where practical
        for k in list(env.keys()):
            if any(
                x in k.upper()
                for x in ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL")
            ):
                if k not in env_extra:  # allow explicit scan-time vars if ever needed
                    env.pop(k, None)
        try:
            return subprocess.run(
                argv,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                env=env,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(
                argv,
                -1,
                "",
                f"subprocess timed out after {timeout_sec}s",
            )


def finding_from_severity(
    driver: str,
    severity: str,
    title: str,
    detail: str = "",
    *,
    rule_id: str = "",
    category: str = "",
) -> Finding:
    sev = severity.upper()
    mapping = {
        "CRITICAL": Severity.CRITICAL,
        "HIGH": Severity.HIGH,
        "MEDIUM": Severity.MEDIUM,
        "LOW": Severity.LOW,
        "INFO": Severity.INFO,
        "WARNING": Severity.MEDIUM,
        "WARN": Severity.MEDIUM,
    }
    return Finding(
        driver=driver,
        severity=mapping.get(sev, Severity.MEDIUM),
        title=title,
        detail=detail,
        rule_id=rule_id,
        category=category,
    )
