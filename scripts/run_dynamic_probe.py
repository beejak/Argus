#!/usr/bin/env python3
"""Phase-5 dynamic probe stub (v1): opt-in Garak presence check + JSON report.

Default (no env): writes ``llm_scanner.dynamic_probe_report.v1`` with ``status: disabled`` and
exits ``0`` so CI can call this script without enabling probes.

Set ``LLM_SCANNER_DYNAMIC_PROBE=1`` to attempt a trivial ``garak`` CLI check (``--help``,
timeout-bounded). If ``garak`` is missing, exits ``2`` and writes ``status: skipped`` with a
clear message (tooling lane, aligned with absent ModelScan/ModelAudit semantics).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    sys.path.insert(0, str(root / "hf_bundle_scanner"))
    from hf_bundle_scanner.dynamic_probe_report import (  # noqa: PLC0415
        build_report,
    )

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True, help="Output dynamic_probe_report.v1 JSON path")
    ap.add_argument(
        "--budget-max-probes",
        type=int,
        default=None,
        help="Optional budget hint recorded in the report (not enforced in this stub)",
    )
    args = ap.parse_args(argv)
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    enabled = os.environ.get("LLM_SCANNER_DYNAMIC_PROBE", "").strip() == "1"
    if not enabled:
        doc = build_report(
            status="disabled",
            probe_backend="none",
            message="Set LLM_SCANNER_DYNAMIC_PROBE=1 to run the garak presence check.",
            exit_code=0,
            budget_max_probes=args.budget_max_probes,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 0

    garak = shutil.which("garak")
    if not garak:
        doc = build_report(
            status="skipped",
            probe_backend="garak",
            message="LLM_SCANNER_DYNAMIC_PROBE=1 but `garak` not found on PATH.",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    try:
        p = subprocess.run(
            [garak, "--help"],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except subprocess.TimeoutExpired:
        doc = build_report(
            status="error",
            probe_backend="garak",
            message="garak --help timed out after 120s",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            garak_cli=garak,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    if p.returncode != 0:
        tail = (p.stderr or p.stdout or "").strip()[-2000:]
        doc = build_report(
            status="error",
            probe_backend="garak",
            message=f"garak --help failed (exit {p.returncode}). stderr/stdout tail: {tail!r}",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            garak_cli=garak,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    doc = build_report(
        status="ok",
        probe_backend="garak",
        message="garak CLI responds to --help (probe harness not run in this stub).",
        exit_code=0,
        budget_max_probes=args.budget_max_probes,
        garak_cli=garak,
    )
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
