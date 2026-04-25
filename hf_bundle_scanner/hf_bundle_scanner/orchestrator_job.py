"""Orchestrator job document v1 — structure + DAG validation (no scan execution)."""

from __future__ import annotations

import json
import uuid
from collections import deque
from pathlib import Path
from typing import Any


JOB_SCHEMA_V1 = "llm_scanner.orchestrator_job.v1"
# v2: per ADR 0001 — steps include name/type, artifact_uri, started_at/ended_at; aggregate step row.
ENVELOPE_SCHEMA_V2 = "llm_scanner.orchestrator_envelope.v2"


def worst_exit_code(*codes: int) -> int:
    """Same priority family as bundle aggregates: 4 > 2 > 1 > 0."""
    xs = [int(x) for x in codes]
    if any(x == 4 for x in xs):
        return 4
    if any(x == 2 for x in xs):
        return 2
    if any(x == 1 for x in xs):
        return 1
    return 0


def _is_non_empty_str(v: Any) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _validate_uuid_field(label: str, value: Any, errs: list[str]) -> None:
    """If ``value`` is non-empty after strip, it must be a RFC 4122 UUID string."""
    if value is None:
        return
    if not isinstance(value, str):
        errs.append(f"{label} must be a string when present")
        return
    s = value.strip()
    if not s:
        return
    try:
        uuid.UUID(s)
    except ValueError:
        errs.append(f"{label} must be an RFC 4122 UUID string (got {value!r})")


def validate_job(doc: Any, *, job_path: Path | None = None, strict_paths: bool = False) -> list[str]:
    """Return a list of human-readable errors; empty means valid."""
    errs: list[str] = []
    if not isinstance(doc, dict):
        return ["document must be a JSON object"]
    if doc.get("schema") != JOB_SCHEMA_V1:
        errs.append(f'schema must be "{JOB_SCHEMA_V1}"')

    _validate_uuid_field("run_id", doc.get("run_id"), errs)
    _validate_uuid_field("parent_run_id", doc.get("parent_run_id"), errs)

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
        if typ not in ("scan_bundle", "dynamic_probe", "aggregate"):
            errs.append(
                f"steps[{i}].type must be 'scan_bundle', 'dynamic_probe', or 'aggregate' (got {typ!r})"
            )
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
    dp_ids = [s for s, v in by_id.items() if v.get("type") == "dynamic_probe"]
    agg_ids = [s for s, v in by_id.items() if v.get("type") == "aggregate"]
    if len(scan_ids) != 1:
        errs.append("v1 requires exactly one step with type 'scan_bundle'")
    if len(agg_ids) != 1:
        errs.append("v1 requires exactly one step with type 'aggregate'")
    if len(dp_ids) > 1:
        errs.append("v1 allows at most one step with type 'dynamic_probe'")

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
    dp_id = dp_ids[0] if dp_ids else None
    agg_deps = list(by_id[agg_id].get("depends_on", []) or [])
    agg_dep_set = {str(x) for x in agg_deps}
    if scan_id not in agg_dep_set:
        errs.append("aggregate step depends_on must include the scan_bundle step id")
    if dp_id is not None:
        dp_raw = by_id[dp_id]
        dp_dep = [str(x) for x in (dp_raw.get("depends_on") or [])]
        if dp_dep != [scan_id]:
            errs.append(
                "dynamic_probe step depends_on must be exactly [scan_bundle step id] "
                f"(expected [{scan_id!r}], got {dp_dep!r})"
            )
        if dp_id not in agg_dep_set:
            errs.append("aggregate step depends_on must include the dynamic_probe step id")
        dp_obj = doc.get("dynamic_probe")
        if not isinstance(dp_obj, dict):
            errs.append("dynamic_probe must be an object when a dynamic_probe step is present")
        else:
            if not _is_non_empty_str(dp_obj.get("out")):
                errs.append("dynamic_probe.out must be a non-empty string")
            if "budget_max_probes" in dp_obj and dp_obj.get("budget_max_probes") is not None:
                try:
                    if int(dp_obj["budget_max_probes"]) <= 0:
                        errs.append("dynamic_probe.budget_max_probes must be >= 1 when provided")
                except (TypeError, ValueError):
                    errs.append("dynamic_probe.budget_max_probes must be an integer when provided")
            if "budget_timeout_seconds" in dp_obj and dp_obj.get("budget_timeout_seconds") is not None:
                try:
                    if int(dp_obj["budget_timeout_seconds"]) <= 0:
                        errs.append("dynamic_probe.budget_timeout_seconds must be >= 1 when provided")
                except (TypeError, ValueError):
                    errs.append("dynamic_probe.budget_timeout_seconds must be an integer when provided")

    dpr = doc.get("dynamic_probe")
    if isinstance(dpr, dict) and bool(dpr) and dp_id is None:
        errs.append("dynamic_probe settings are present but no dynamic_probe step was defined")

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

        if dp_id is not None and isinstance(doc.get("dynamic_probe"), dict):
            dpo = doc["dynamic_probe"]
            if _is_non_empty_str(dpo.get("out")):
                outp = _rp(str(dpo.get("out", "")))
                outp.parent.mkdir(parents=True, exist_ok=True)

    return errs


def load_job(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_envelope(
    *,
    run_id: str,
    parent_run_id: str | None,
    scan_step_id: str,
    aggregate_step_id: str,
    bundle_path: Path,
    envelope_path: Path | None,
    scan_exit: int,
    aggregate_exit: int,
    scan_started_at: str,
    scan_ended_at: str,
    aggregate_started_at: str,
    aggregate_ended_at: str,
    dynamic_probe_step: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build orchestrator envelope JSON (v2).

    ``steps`` follow ADR 0001: ``id``, ``name``, ``type``, ``exit_code``,
    ``artifact_uri`` (file URI when possible), ``started_at`` / ``ended_at``
    (RFC 3339 UTC with ``Z`` suffix, caller-supplied).

    When ``dynamic_probe_step`` is set, it is inserted **between** the scan row and the
    aggregate row (same envelope schema).
    """
    bundle_uri = bundle_path.expanduser().resolve().as_uri()
    env_uri = ""
    if envelope_path is not None:
        env_uri = envelope_path.expanduser().resolve().as_uri()

    scan_row: dict[str, Any] = {
        "id": scan_step_id,
        "name": "scan_bundle",
        "type": "scan_bundle",
        "exit_code": int(scan_exit),
        "artifact_uri": bundle_uri,
        "started_at": scan_started_at,
        "ended_at": scan_ended_at,
    }
    agg_row: dict[str, Any] = {
        "id": aggregate_step_id,
        "name": "aggregate",
        "type": "aggregate",
        "exit_code": int(aggregate_exit),
        "artifact_uri": env_uri,
        "started_at": aggregate_started_at,
        "ended_at": aggregate_ended_at,
    }
    steps: list[dict[str, Any]] = [scan_row]
    if dynamic_probe_step is not None:
        steps.append(dict(dynamic_probe_step))
    steps.append(agg_row)
    out: dict[str, Any] = {
        "schema": ENVELOPE_SCHEMA_V2,
        "run_id": run_id,
        "aggregate_exit_code": int(aggregate_exit),
        "steps": steps,
    }
    if _is_non_empty_str(parent_run_id):
        out["parent_run_id"] = str(parent_run_id).strip()
    return out
