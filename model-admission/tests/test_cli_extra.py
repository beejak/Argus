"""More CLI subprocess coverage."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def _run(args: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "model_admission", *args],
        capture_output=True,
        text=True,
        timeout=60,
        env={**os.environ, **(env or {})},
    )


def test_unknown_driver_exits_4(tmp_path: Path) -> None:
    policy = tmp_path / "p.json"
    policy.write_text("{}", encoding="utf-8")
    art = tmp_path / "a.txt"
    art.write_text("x", encoding="utf-8")
    proc = _run(
        [
            "scan",
            "--artifact",
            str(art),
            "--policy",
            str(policy),
            "--drivers",
            "notreal",
        ]
    )
    assert proc.returncode == 4


def test_ledger_via_env_without_flag(tmp_path: Path) -> None:
    policy = tmp_path / "p.json"
    policy.write_text("{}", encoding="utf-8")
    art = tmp_path / "a.txt"
    art.write_text("x", encoding="utf-8")
    led = tmp_path / "from-env.jsonl"
    proc = _run(
        [
            "scan",
            "--artifact",
            str(art),
            "--policy",
            str(policy),
            "--drivers",
            "",
        ],
        env={"MODEL_ADMISSION_LEDGER": str(led)},
    )
    assert proc.returncode == 0
    assert led.exists()
    line = led.read_text(encoding="utf-8").strip().splitlines()[-1]
    assert json.loads(line)["exit_code"] == 0
