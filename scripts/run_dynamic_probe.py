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


def _csv_names(raw: str) -> list[str]:
    return [x.strip() for x in str(raw).split(",") if x.strip()]


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
        help="Optional max probes budget (validated + recorded in the report)",
    )
    ap.add_argument(
        "--budget-timeout-seconds",
        type=int,
        default=120,
        help="Timeout budget for the garak --help probe (default: 120)",
    )
    ap.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Optional orchestrator run_id to record for report correlation",
    )
    ap.add_argument(
        "--garak-config",
        type=Path,
        default=None,
        help="Optional Garak config path (recorded + validated when provided)",
    )
    ap.add_argument(
        "--model-target",
        type=str,
        default=None,
        help="Optional model target label recorded in report metadata",
    )
    ap.add_argument(
        "--secret-env-vars",
        type=str,
        default="",
        help="Comma-separated required secret env-var names (values are never recorded)",
    )
    args = ap.parse_args(argv)
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    garak_config = None
    if args.garak_config is not None:
        garak_config = Path(args.garak_config).resolve()
        if not garak_config.is_file():
            doc = build_report(
                status="error",
                probe_backend="none",
                message=f"garak_config not a file: {garak_config}",
                exit_code=2,
                budget_max_probes=args.budget_max_probes,
                budget_timeout_seconds=args.budget_timeout_seconds,
                run_id=args.run_id,
                garak_config=str(garak_config),
                model_target=args.model_target,
            )
            out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
            return 2
    required_secret_vars = _csv_names(args.secret_env_vars)

    if args.budget_max_probes is not None and int(args.budget_max_probes) <= 0:
        doc = build_report(
            status="error",
            probe_backend="none",
            message="budget_max_probes must be >= 1 when provided.",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2
    if int(args.budget_timeout_seconds) <= 0:
        doc = build_report(
            status="error",
            probe_backend="none",
            message="budget_timeout_seconds must be >= 1.",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    enabled = os.environ.get("LLM_SCANNER_DYNAMIC_PROBE", "").strip() == "1"
    if not enabled:
        doc = build_report(
            status="disabled",
            probe_backend="none",
            message="Set LLM_SCANNER_DYNAMIC_PROBE=1 to run the garak presence check.",
            exit_code=0,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 0
    missing_secret_vars = [name for name in required_secret_vars if not os.environ.get(name, "").strip()]
    if missing_secret_vars:
        doc = build_report(
            status="error",
            probe_backend="garak",
            message=f"required secret env vars are missing: {', '.join(missing_secret_vars)}",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
            secret_env_vars_missing=missing_secret_vars,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    garak = shutil.which("garak")
    if not garak:
        doc = build_report(
            status="skipped",
            probe_backend="garak",
            message="LLM_SCANNER_DYNAMIC_PROBE=1 but `garak` not found on PATH.",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
        )
        out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
        return 2

    try:
        p = subprocess.run(
            [garak, "--help"] if garak_config is None else [garak, "--config", str(garak_config), "--help"],
            capture_output=True,
            text=True,
            timeout=int(args.budget_timeout_seconds),
            check=False,
        )
    except subprocess.TimeoutExpired:
        doc = build_report(
            status="error",
            probe_backend="garak",
            message=f"garak --help timed out after {int(args.budget_timeout_seconds)}s",
            exit_code=2,
            budget_max_probes=args.budget_max_probes,
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
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
            budget_timeout_seconds=args.budget_timeout_seconds,
            run_id=args.run_id,
            garak_config=str(garak_config) if garak_config is not None else None,
            model_target=args.model_target,
            secret_env_vars_required=required_secret_vars,
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
        budget_timeout_seconds=args.budget_timeout_seconds,
        run_id=args.run_id,
        garak_config=str(garak_config) if garak_config is not None else None,
        model_target=args.model_target,
        secret_env_vars_required=required_secret_vars,
        garak_cli=garak,
    )
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
