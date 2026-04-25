#!/usr/bin/env python3
"""Run pytest for model-admission and hf_bundle_scanner; write .agent/pytest-last.log + .agent/pytest-last.exit.

Use this from ``make agent-verify`` so we do not depend on bash scripts having LF line endings on Windows checkouts.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def _test_catalog_env(root: Path) -> dict[str, str]:
    """Resolve catalog path and export absolute ``LLM_SCANNER_TEST_CATALOG`` for child pytest."""
    hf = root / "hf_bundle_scanner"
    if hf.is_dir():
        sys.path[:0] = [str(hf)]
        try:
            from hf_bundle_scanner.test_catalog import (  # type: ignore[import-untyped]
                TEST_CATALOG_ENV_VAR,
                resolve_test_catalog_path,
            )

            cat = resolve_test_catalog_path(repo_root=root, environ=os.environ)
            return {TEST_CATALOG_ENV_VAR: str(cat.resolve())}
        finally:
            if sys.path and sys.path[0] == str(hf):
                sys.path.pop(0)
    return {}


def _pick_python(root: Path) -> Path:
    """Prefer repo-local .venv; fall back to sys.executable (e.g. GitHub Actions)."""
    candidates = [
        root / ".venv" / "bin" / "python",
        root / ".venv" / "Scripts" / "python.exe",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return Path(sys.executable)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    agent = root / ".agent"
    agent.mkdir(parents=True, exist_ok=True)
    log_path = agent / "pytest-last.log"
    exit_path = agent / "pytest-last.exit"
    py = _pick_python(root)

    buf = io.StringIO()

    def log(msg: str) -> None:
        buf.write(msg + "\n")

    log(f"=== {datetime.now(timezone.utc).isoformat()} ===")
    log(f"ROOT={root}")
    log(f"PYTHON={py}")

    catalog_env = _test_catalog_env(root)
    if catalog_env:
        k, v = next(iter(catalog_env.items()))
        log(f"{k}={v}")

    if not py.is_file():
        log(f"ERROR: missing interpreter {py} — run: make install")
        exit_path.write_text("99", encoding="utf-8")
        log_path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")
        return 99

    overall = 0

    log("=== model-admission ===")
    r1 = subprocess.run(
        [str(py), "-m", "pytest", "tests", "-v", "--tb=short"],
        cwd=str(root / "model-admission"),
        capture_output=True,
        text=True,
        env={**os.environ, **catalog_env, "PYTHONUNBUFFERED": "1"},
    )
    log(r1.stdout or "")
    log(r1.stderr or "")
    log(f"model_admission_exit={r1.returncode}")
    if r1.returncode != 0:
        overall = 1

    log("=== hf_bundle_scanner (not integration) ===")
    r2 = subprocess.run(
        [
            str(py),
            "-m",
            "pytest",
            "tests",
            "-v",
            "--tb=short",
            "-m",
            "not integration",
        ],
        cwd=str(root / "hf_bundle_scanner"),
        capture_output=True,
        text=True,
        env={**os.environ, **catalog_env, "PYTHONUNBUFFERED": "1"},
    )
    log(r2.stdout or "")
    log(r2.stderr or "")
    log(f"hf_bundle_scanner_exit={r2.returncode}")
    if r2.returncode != 0:
        overall = 1

    log("=== orchestrator job validate ===")
    job = root / "hf_bundle_scanner" / "tests" / "fixtures" / "orchestrator_job_min.json"
    r3 = subprocess.run(
        [str(py), str(root / "scripts" / "run_orchestrator_job.py"), "validate", "--job", str(job)],
        cwd=str(root),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    log(r3.stdout or "")
    log(r3.stderr or "")
    log(f"orchestrator_validate_exit={r3.returncode}")
    if r3.returncode != 0:
        overall = 1

    log("=== orchestrator job validate (with dynamic_probe fixture) ===")
    job_dyn = root / "hf_bundle_scanner" / "tests" / "fixtures" / "orchestrator_job_with_dynamic.json"
    r3b = subprocess.run(
        [str(py), str(root / "scripts" / "run_orchestrator_job.py"), "validate", "--job", str(job_dyn)],
        cwd=str(root),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    log(r3b.stdout or "")
    log(r3b.stderr or "")
    log(f"orchestrator_validate_dynamic_fixture_exit={r3b.returncode}")
    if r3b.returncode != 0:
        overall = 1

    log("=== dynamic probe stub (disabled by default) ===")
    dp_out = agent / "dynamic_probe_last.json"
    r4 = subprocess.run(
        [str(py), str(root / "scripts" / "run_dynamic_probe.py"), "--out", str(dp_out)],
        cwd=str(root),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    log(r4.stdout or "")
    log(r4.stderr or "")
    log(f"dynamic_probe_stub_exit={r4.returncode}")
    if r4.returncode != 0:
        overall = 1

    log("=== ruff (hf_bundle_scanner) ===")
    r5 = subprocess.run(
        [str(py), "-m", "ruff", "check", "hf_bundle_scanner", "tests"],
        cwd=str(root / "hf_bundle_scanner"),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    log(r5.stdout or "")
    log(r5.stderr or "")
    log(f"ruff_exit={r5.returncode}")
    if r5.returncode != 0:
        overall = 1

    log(f"overall_exit={overall}")
    exit_path.write_text(str(overall), encoding="utf-8", newline="\n")
    log_path.write_text(buf.getvalue(), encoding="utf-8", newline="\n")
    return overall


if __name__ == "__main__":
    raise SystemExit(main())
