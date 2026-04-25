"""Phase-5 dynamic probe lane — machine-readable report (v1).

This is **not** a substitute for a full Garak / PyRIT harness. It provides a **stable JSON
shape** so orchestration, CI, and future adapters can agree on fields before real probes land.
"""

from __future__ import annotations

from typing import Any

from hf_bundle_scanner.timestamps import now_report_timestamps

DYNAMIC_PROBE_SCHEMA_V1 = "llm_scanner.dynamic_probe_report.v1"


def build_report(
    *,
    status: str,
    probe_backend: str,
    message: str,
    exit_code: int,
    budget_max_probes: int | None = None,
    budget_timeout_seconds: int | None = None,
    run_id: str | None = None,
    garak_config: str | None = None,
    model_target: str | None = None,
    execution_mode: str | None = None,
    executed_argv: list[str] | None = None,
    secret_env_vars_required: list[str] | None = None,
    secret_env_vars_missing: list[str] | None = None,
    garak_cli: str | None = None,
    report_generated_at_utc: str | None = None,
    report_generated_at_ist: str | None = None,
) -> dict[str, Any]:
    """Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

    ``status`` is one of: ``disabled``, ``skipped``, ``ok``, ``error`` (lowercase).
    ``exit_code`` follows bundle-style lanes: ``0`` success, ``2`` tooling missing / misconfigured.
    """
    ts_utc, ts_ist = (
        (str(report_generated_at_utc).strip(), str(report_generated_at_ist).strip())
        if report_generated_at_utc is not None and report_generated_at_ist is not None
        else now_report_timestamps()
    )
    out: dict[str, Any] = {
        "schema": DYNAMIC_PROBE_SCHEMA_V1,
        "status": str(status).strip().lower(),
        "probe_backend": str(probe_backend).strip(),
        "message": str(message).strip(),
        "exit_code": int(exit_code),
        "report_generated_at_utc": ts_utc,
        "report_generated_at_ist": ts_ist,
    }
    if budget_max_probes is not None:
        out["budget_max_probes"] = int(budget_max_probes)
    if budget_timeout_seconds is not None:
        out["budget_timeout_seconds"] = int(budget_timeout_seconds)
    if run_id:
        out["run_id"] = str(run_id).strip()
    if garak_config:
        out["garak_config"] = str(garak_config).strip()
    if model_target:
        out["model_target"] = str(model_target).strip()
    if execution_mode:
        out["execution_mode"] = str(execution_mode).strip()
    if executed_argv:
        out["executed_argv"] = [str(x).strip() for x in executed_argv if str(x).strip()]
    if secret_env_vars_required:
        out["secret_env_vars_required"] = [str(x).strip() for x in secret_env_vars_required if str(x).strip()]
    if secret_env_vars_missing:
        out["secret_env_vars_missing"] = [str(x).strip() for x in secret_env_vars_missing if str(x).strip()]
    if garak_cli:
        out["garak_cli"] = str(garak_cli).strip()
    return out
