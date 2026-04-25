"""Phase-5 dynamic probe lane — machine-readable report (v1).

This is **not** a substitute for a full Garak / PyRIT harness. It provides a **stable JSON
shape** so orchestration, CI, and future adapters can agree on fields before real probes land.
"""

from __future__ import annotations

from typing import Any

DYNAMIC_PROBE_SCHEMA_V1 = "llm_scanner.dynamic_probe_report.v1"


def build_report(
    *,
    status: str,
    probe_backend: str,
    message: str,
    exit_code: int,
    budget_max_probes: int | None = None,
    garak_cli: str | None = None,
) -> dict[str, Any]:
    """Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

    ``status`` is one of: ``disabled``, ``skipped``, ``ok``, ``error`` (lowercase).
    ``exit_code`` follows bundle-style lanes: ``0`` success, ``2`` tooling missing / misconfigured.
    """
    out: dict[str, Any] = {
        "schema": DYNAMIC_PROBE_SCHEMA_V1,
        "status": str(status).strip().lower(),
        "probe_backend": str(probe_backend).strip(),
        "message": str(message).strip(),
        "exit_code": int(exit_code),
    }
    if budget_max_probes is not None:
        out["budget_max_probes"] = int(budget_max_probes)
    if garak_cli:
        out["garak_cli"] = str(garak_cli).strip()
    return out
