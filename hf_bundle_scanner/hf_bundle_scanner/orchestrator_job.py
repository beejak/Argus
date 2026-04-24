"""Orchestrator job document v1 — structure + DAG validation (no scan execution)."""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path
from typing import Any


JOB_SCHEMA_V1 = "llm_scanner.orchestrator_job.v1"
ENVELOPE_SCHEMA_V1 = "llm_scanner.orchestrator_envelope.v1"


def _is_non_empty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def validate_job(doc: Any, *, job_path: Path | None = None, strict_paths: bool = False) -> list[str]:
    """Return a list of human-readable errors; empty means valid."""
    errs: list[str] = []
    if not isinstance(doc, dict):
        return ["document must be a JSON object"]
    if doc.get("schema") != JOB_SCHEMA_V1:
        errs.append(f'schema must be "{JOB_SCHEMA_V1}"')

    steps = doc.get("steps")
    if not isinstance(steps, list) or len(steps) < 2:
        errs.append("steps must be a non-empty array with at least two entries")
        return errs

    by_id: dict[str, dict[str, Any]] = {}
    for i, raw in enumerate(steps):
        if not isinstance(raw, dict):
            errs.append(f"steps[{i}] must be an object")
            continue
        sid = raw.get("id")
        if not _is_non_empty_str(sid):
            errs.append(f"steps[{i}].id must be a non-empty string")
            continue
        if sid in by_id:
            errs.append(f"duplicate step id: {sid!r}")
        typ = raw.get("type")
        if typ not in ("scan_bundle", "aggregate"):
            errs.append(f"steps[{i}].type must be 'scan_bundle' or 'aggregate' (got {typ!r})")
        dep = raw.get("depends_on", [])
        if dep is None:
            dep = []
        if not isinstance(dep, list) or not all(_is_non_empty_str(x) for x in dep):
            errs.append(f"steps[{i}].depends_on must be an array of strings")
            continue
        by_id[str(sid)] = raw

    if errs:
        return errs

    scan_ids = [s for s, v in by_id.items() if v.get("type") == "scan_bundle"]
    agg_ids = [s for s, v in by_id.items() if v.get("type") == "aggregate"]
    if len(scan_ids) != 1:
        errs.append("v1 requires exactly one step with type 'scan_bundle'")
    if len(agg_ids) != 1:
        errs.append("v1 requires exactly one step with type 'aggregate'")

    # edges: dep -> step (dep must finish before step)
    outgoing: dict[str, set[str]] = {sid: set() for sid in by_id}
    indeg: dict[str, int] = {sid: 0 for sid in by_id}
    for sid, raw in by_id.items():
        for d in raw.get("depends_on", []) or []:
            ds = str(d)
            if ds not in by_id:
                errs.append(f"step {sid!r} depends_on unknown id {ds!r}")
                continue
            outgoing[ds].add(sid)
            indeg[sid] += 1

    if errs:
        return errs

    q: deque[str] = deque([sid for sid, k in indeg.items() if k == 0])
    seen = 0
    while q:
        n = q.popleft()
        seen += 1
        for m in sorted(outgoing[n]):
            indeg[m] -= 1
            if indeg[m] == 0:
                q.append(m)
    if seen != len(by_id):
        errs.append("steps contain a cycle or unreachable nodes (invalid DAG)")
        return errs

    scan_id = scan_ids[0]
    agg_id = agg_ids[0]
    agg_deps = list(by_id[agg_id].get("depends_on", []) or [])
    if scan_id not in set(str(x) for x in agg_deps):
        errs.append("aggregate step depends_on must include the scan_bundle step id")

    sb = doc.get("scan_bundle")
    if not isinstance(sb, dict):
        errs.append("scan_bundle must be an object")
        return errs
    for key in ("root", "policy", "out"):
        if not _is_non_empty_str(sb.get(key)):
            errs.append(f"scan_bundle.{key} must be a non-empty string")

    if strict_paths and job_path is not None:
        base = job_path.resolve().parent

        def _rp(p: str) -> Path:
            pp = Path(p)
            return pp if pp.is_absolute() else (base / pp).resolve()

        r = _rp(str(sb.get("root", "")))
        pol = _rp(str(sb.get("policy", "")))
        if not r.is_dir():
            errs.append(f"scan_bundle.root not a directory: {r}")
        if not pol.is_file():
            errs.append(f"scan_bundle.policy not a file: {pol}")

    return errs


def load_job(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_envelope(
    *,
    run_id: str,
    scan_step_id: str,
    bundle_path: Path,
    scan_exit: int,
    aggregate_exit: int,
) -> dict[str, Any]:
    return {
        "schema": ENVELOPE_SCHEMA_V1,
        "run_id": run_id,
        "aggregate_exit_code": int(aggregate_exit),
        "steps": [
            {
                "id": scan_step_id,
                "exit_code": int(scan_exit),
                "artifact": str(bundle_path),
            },
        ],
    }
