#!/usr/bin/env python3
"""Validate or run a phase-4 orchestrator job document (v1).

``scan_bundle`` execution delegates to ``python -m hf_bundle_scanner scan`` (same CLI as ``scan-bundle``).

``run`` writes an orchestrator envelope JSON (schema ``llm_scanner.orchestrator_envelope.v2``): UUID
``run_id`` (from the job or generated), optional ``parent_run_id``, and ``steps`` for ``scan_bundle``,
optional ``dynamic_probe`` (see job schema in ``hf_bundle_scanner.orchestrator_job``), and ``aggregate``
with RFC 3339 UTC timestamps and ``file:`` artifact URIs. When present, ``dynamic_probe`` receives
``run_id`` and optional budget flags from the job document.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _pick_python() -> Path:
    env = os.environ.get("HF_BUNDLE_PYTHON")
    if env:
        return Path(env)
    root = _repo_root()
    for p in (root / ".venv" / "bin" / "python", root / ".venv" / "Scripts" / "python.exe"):
        if p.is_file():
            return p
    return Path(sys.executable)


def _resolve(job_dir: Path, p: str) -> Path:
    pp = Path(p)
    return pp if pp.is_absolute() else (job_dir / pp).resolve()


def _scan_argv(*, py: Path, sb: dict[str, object], root: Path, policy: Path, out: Path) -> list[str]:
    cmd: list[str] = [str(py), "-m", "hf_bundle_scanner", "scan", "--root", str(root), "--policy", str(policy), "--out", str(out)]
    drivers = sb.get("drivers", "")
    if drivers is not None and str(drivers).strip() != "":
        cmd.extend(["--drivers", str(drivers)])
    if "timeout" in sb and sb["timeout"] is not None:
        cmd.extend(["--timeout", str(int(sb["timeout"]))])  # type: ignore[arg-type]
    if _is_non_empty_str(sb.get("fail_on")):
        cmd.extend(["--fail-on", str(sb["fail_on"]).strip()])
    if sb.get("no_manifest") is True:
        cmd.append("--no-manifest")
    if _is_non_empty_str(sb.get("hub_repo")):
        cmd.extend(["--hub-repo", str(sb["hub_repo"]).strip()])
    if _is_non_empty_str(sb.get("hub_revision")):
        cmd.extend(["--hub-revision", str(sb["hub_revision"]).strip()])
    if _is_non_empty_str(sb.get("mirror_allowlist")):
        cmd.extend(["--mirror-allowlist", str(sb["mirror_allowlist"]).strip()])
    if _is_non_empty_str(sb.get("sbom_uri")):
        cmd.extend(["--sbom-uri", str(sb["sbom_uri"]).strip()])
    return cmd


def _is_non_empty_str(v: object) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _utc_iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    sys.path.insert(0, str(root / "hf_bundle_scanner"))
    from hf_bundle_scanner.orchestrator_job import (  # noqa: PLC0415
        build_envelope,
        load_job,
        validate_job,
        worst_exit_code,
    )

    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pv = sub.add_parser("validate", help="Validate job JSON (no subprocess)")
    pv.add_argument("--job", type=Path, required=True)
    pv.add_argument("--no-strict", action="store_true", help="Skip on-disk path checks")

    pr = sub.add_parser(
        "run",
        help="Validate, run scan_bundle (and optional dynamic_probe), write envelope JSON",
    )
    pr.add_argument("--job", type=Path, required=True)
    pr.add_argument("--envelope-out", type=Path, required=True)
    pr.add_argument("--python", type=Path, default=None, help="Override interpreter (default HF_BUNDLE_PYTHON or .venv)")

    args = ap.parse_args(argv)
    job_path: Path = args.job.resolve()
    doc = load_job(job_path)
    strict = not bool(getattr(args, "no_strict", False))

    if args.cmd == "validate":
        errs = validate_job(doc, job_path=job_path, strict_paths=strict)
        if errs:
            print(json.dumps({"errors": errs}, indent=2))
            return 2
        print(json.dumps({"ok": True}, indent=2))
        return 0

    if args.cmd == "run":
        errs = validate_job(doc, job_path=job_path, strict_paths=True)
        if errs:
            print(json.dumps({"errors": errs}, indent=2))
            return 2
        sb = doc.get("scan_bundle")
        if not isinstance(sb, dict):
            print(json.dumps({"errors": ["scan_bundle must be an object"]}, indent=2))
            return 2
        job_dir = job_path.parent
        r = _resolve(job_dir, str(sb["root"]))
        pol = _resolve(job_dir, str(sb["policy"]))
        out = _resolve(job_dir, str(sb["out"]))
        out.parent.mkdir(parents=True, exist_ok=True)
        py = Path(args.python) if args.python is not None else _pick_python()
        cmd = _scan_argv(py=py, sb=sb, root=r, policy=pol, out=out)
        scan_id = next(str(s["id"]) for s in doc["steps"] if s.get("type") == "scan_bundle")
        agg_id = next(str(s["id"]) for s in doc["steps"] if s.get("type") == "aggregate")
        run_id = str(doc.get("run_id") or "").strip() or str(uuid.uuid4())
        parent_raw = doc.get("parent_run_id")
        parent_run_id = str(parent_raw).strip() if _is_non_empty_str(parent_raw) else None
        dp_ids = [str(s["id"]) for s in doc["steps"] if s.get("type") == "dynamic_probe"]
        dp_id = dp_ids[0] if dp_ids else None

        t_scan_start = _utc_now()
        # Match Makefile harness: run the module with CWD at the Python project root.
        p = subprocess.run(cmd, cwd=str(root / "hf_bundle_scanner"))
        t_scan_end = _utc_now()
        if t_scan_end < t_scan_start:
            t_scan_end = t_scan_start
        scan_exit = int(p.returncode)
        bundle_agg = scan_exit
        if out.is_file():
            try:
                rep = json.loads(out.read_text(encoding="utf-8"))
                if isinstance(rep, dict) and rep.get("aggregate_exit_code") is not None:
                    bundle_agg = int(rep["aggregate_exit_code"])
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                bundle_agg = 2

        dynamic_probe_step: dict[str, object] | None = None
        probe_exit = 0
        t_after_scan = t_scan_end
        if dp_id is not None:
            dpo = doc.get("dynamic_probe")
            if not isinstance(dpo, dict) or not _is_non_empty_str(dpo.get("out")):
                print(
                    json.dumps(
                        {"errors": ["dynamic_probe step present but dynamic_probe.out is invalid"]},
                        indent=2,
                    )
                )
                return 2
            dp_out = _resolve(job_dir, str(dpo["out"]))
            dp_out.parent.mkdir(parents=True, exist_ok=True)
            probe_script = root / "scripts" / "run_dynamic_probe.py"
            probe_cmd: list[str] = [str(py), str(probe_script), "--out", str(dp_out), "--run-id", run_id]
            if dpo.get("budget_max_probes") is not None:
                probe_cmd.extend(["--budget-max-probes", str(int(dpo["budget_max_probes"]))])
            if dpo.get("budget_timeout_seconds") is not None:
                probe_cmd.extend(["--budget-timeout-seconds", str(int(dpo["budget_timeout_seconds"]))])
            t_dp_start = _utc_now()
            probe = subprocess.run(
                probe_cmd,
                cwd=str(root),
                env=os.environ,
                capture_output=True,
                text=True,
            )
            t_dp_end = _utc_now()
            if t_dp_end < t_dp_start:
                t_dp_end = t_dp_start
            probe_exit = int(probe.returncode)
            if not dp_out.is_file():
                probe_exit = worst_exit_code(probe_exit, 2)
            else:
                try:
                    drep = json.loads(dp_out.read_text(encoding="utf-8"))
                    if isinstance(drep, dict) and drep.get("exit_code") is not None:
                        probe_exit = int(drep["exit_code"])
                except (OSError, json.JSONDecodeError, TypeError, ValueError):
                    probe_exit = worst_exit_code(probe_exit, 2)
            dp_uri = dp_out.expanduser().resolve().as_uri()
            dynamic_probe_step = {
                "id": dp_id,
                "name": "dynamic_probe",
                "type": "dynamic_probe",
                "exit_code": int(probe_exit),
                "artifact_uri": dp_uri,
                "started_at": _utc_iso_z(t_dp_start),
                "ended_at": _utc_iso_z(t_dp_end),
            }
            t_after_scan = t_dp_end if t_dp_end > t_scan_end else t_scan_end

        agg = worst_exit_code(bundle_agg, probe_exit) if dp_id is not None else bundle_agg

        t_agg_start = t_after_scan
        t_agg_end = _utc_now()
        if t_agg_end < t_agg_start:
            t_agg_end = t_agg_start
        env = build_envelope(
            run_id=run_id,
            parent_run_id=parent_run_id,
            scan_step_id=scan_id,
            aggregate_step_id=agg_id,
            bundle_path=out.resolve(),
            envelope_path=args.envelope_out.resolve(),
            scan_exit=scan_exit,
            aggregate_exit=agg,
            scan_started_at=_utc_iso_z(t_scan_start),
            scan_ended_at=_utc_iso_z(t_scan_end),
            aggregate_started_at=_utc_iso_z(t_agg_start),
            aggregate_ended_at=_utc_iso_z(t_agg_end),
            dynamic_probe_step=dynamic_probe_step,
        )
        args.envelope_out.parent.mkdir(parents=True, exist_ok=True)
        args.envelope_out.write_text(json.dumps(env, indent=2), encoding="utf-8")
        return int(agg)

    return 4


if __name__ == "__main__":
    raise SystemExit(main())
