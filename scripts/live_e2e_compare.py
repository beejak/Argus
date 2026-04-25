#!/usr/bin/env python3
"""Run a single-command live E2E comparison across scanner lanes.

Sequence:
1) Dynamic probe preflight + execute_once (via isolated garak PATH)
2) Gate lane ephemeral Hub scan
3) Assessment lane (drivers enabled)
4) Strict lane (drivers + safetensors-only policy)
5) Print compact summary table and write JSON summary
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from hf_bundle_scanner.timestamps import ist_now_iso, utc_now_iso_z


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run(cmd: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> int:
    p = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, check=False)
    if p.stdout:
        print(p.stdout, end="" if p.stdout.endswith("\n") else "\n")
    if p.stderr:
        print(p.stderr, file=sys.stderr, end="" if p.stderr.endswith("\n") else "\n")
    return int(p.returncode)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_stats(path: Path) -> dict[str, int]:
    d = _load_json(path)
    fs = d.get("file_scans", [])
    findings = sum(len((x.get("report") or {}).get("findings", [])) for x in fs)
    return {
        "aggregate_exit_code": int(d.get("aggregate_exit_code", 4)),
        "config_findings": len(d.get("config_findings", [])),
        "file_findings": findings,
        "files": len(fs),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default="hf-internal-testing/tiny-random-BertModel")
    ap.add_argument("--summary-out", default=".agent/live_e2e_compare_summary.json")
    ap.add_argument("--baseline-out", default="/tmp/live_e2e_baseline.json")
    ap.add_argument("--assessment-out", default="/tmp/live_e2e_assessment.json")
    ap.add_argument("--strict-out", default="/tmp/live_e2e_assessment_strict.json")
    ap.add_argument("--target-dir", default="/tmp/live_e2e_target")
    args = ap.parse_args(argv)

    root = _repo_root()
    py = root / ".venv" / "bin" / "python"
    garak_bin = root / ".venv-garak" / "bin"
    dynamic_probe_out = root / ".agent" / "dynamic_probe_last.json"

    if not py.is_file():
        print(f"ERROR: missing scanner python: {py}", file=sys.stderr)
        return 2
    if not (garak_bin / "garak").is_file():
        print(f"ERROR: missing isolated garak binary: {garak_bin / 'garak'}", file=sys.stderr)
        return 2

    env_with_garak = {**os.environ, "PATH": f"{garak_bin}:{os.environ.get('PATH', '')}"}

    rc = _run(
        ["make", "dynamic-probe-live-preflight"],
        cwd=root,
        env=env_with_garak,
    )
    if rc != 0:
        return rc
    rc = _run(
        ["make", "dynamic-probe-live-exec", "EXECUTE_ARGS=--version"],
        cwd=root,
        env=env_with_garak,
    )
    if rc != 0:
        return rc

    rc = _run(
        ["make", f"OUT={args.baseline_out}", f"EPHEMERAL_FLAGS=--repo {args.repo}", "ephemeral-hub-scan"],
        cwd=root,
    )
    if rc != 0:
        return rc

    rc = _run(
        [str(py), "-c", f"from huggingface_hub import snapshot_download; snapshot_download(repo_id='{args.repo}', local_dir='{args.target_dir}')"],
        cwd=root,
    )
    if rc != 0:
        return rc

    bundle_pkg = root / "hf_bundle_scanner"
    driver_env = {**os.environ, "PATH": f"{root / '.venv' / 'bin'}:{os.environ.get('PATH', '')}", "HF_BUNDLE_PYTHON": str(py)}

    rc = _run(
        [
            str(py),
            "-m",
            "hf_bundle_scanner",
            "scan",
            "--root",
            args.target_dir,
            "--policy",
            "tests/fixtures/policy.permissive.json",
            "--out",
            args.assessment_out,
            "--drivers",
            "modelscan,modelaudit",
            "--print-summary",
            "--hub-repo",
            args.repo,
        ],
        cwd=bundle_pkg,
        env=driver_env,
    )
    # Keep running strict lane even if permissive lane returns 1 due findings.
    if rc not in (0, 1):
        return rc

    rc_strict = _run(
        [
            str(py),
            "-m",
            "hf_bundle_scanner",
            "scan",
            "--root",
            args.target_dir,
            "--policy",
            "tests/fixtures/policy.safetensors-only.json",
            "--out",
            args.strict_out,
            "--drivers",
            "modelscan,modelaudit",
            "--print-summary",
            "--hub-repo",
            args.repo,
        ],
        cwd=bundle_pkg,
        env=driver_env,
    )
    if rc_strict not in (0, 1):
        return rc_strict

    dyn = _load_json(dynamic_probe_out)
    gate = _bundle_stats(Path(args.baseline_out))
    assess = _bundle_stats(Path(args.assessment_out))
    strict = _bundle_stats(Path(args.strict_out))

    summary = {
        "repo": args.repo,
        "report_generated_at_utc": utc_now_iso_z(),
        "report_generated_at_ist": ist_now_iso(),
        "dynamic_probe": {
            "status": dyn.get("status"),
            "exit_code": dyn.get("exit_code"),
            "execution_mode": dyn.get("execution_mode"),
            "executed_argv": dyn.get("executed_argv"),
        },
        "gate_lane": gate,
        "assessment_lane": assess,
        "strict_lane": strict,
        "artifacts": {
            "dynamic_probe": str(dynamic_probe_out),
            "baseline_bundle": args.baseline_out,
            "assessment_bundle": args.assessment_out,
            "strict_bundle": args.strict_out,
            "target_dir": args.target_dir,
        },
    }

    summary_path = (root / args.summary_out).resolve()
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print("\nLive E2E Compare")
    print(f"- dynamic_probe: status={summary['dynamic_probe']['status']} exit={summary['dynamic_probe']['exit_code']} mode={summary['dynamic_probe']['execution_mode']}")
    print(
        f"- gate_lane: agg={gate['aggregate_exit_code']} config={gate['config_findings']} findings={gate['file_findings']} files={gate['files']}"
    )
    print(
        f"- assessment_lane: agg={assess['aggregate_exit_code']} config={assess['config_findings']} findings={assess['file_findings']} files={assess['files']}"
    )
    print(
        f"- strict_lane: agg={strict['aggregate_exit_code']} config={strict['config_findings']} findings={strict['file_findings']} files={strict['files']}"
    )
    print(f"- summary_json: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
