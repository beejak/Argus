"""Run model-admission per artifact and collect results."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from hf_bundle_scanner.configlint import lint_tree
from hf_bundle_scanner.discovery import DiscoveryConfig, discover_config_files, discover_scan_artifacts
from hf_bundle_scanner.provenance import build_bundle_provenance
from hf_bundle_scanner.report import BundleReport, FileScanRecord, compute_aggregate_exit, merge_aggregate_exit
from hf_bundle_scanner.snapshot import build_manifest
from hf_bundle_scanner.timestamps import now_report_timestamps


# Configlint rule_ids that flip ``config_risk`` → bundle aggregate exit 1 when file scans are clean.
# Keep aligned with ``docs/policy/configlint_rule_defaults.json`` (see tests) and reporting exports.
CONFIG_RISK_RULE_IDS: frozenset[str] = frozenset(
    {
        "trust_remote_code_enabled",
        "auto_map_custom_classes",
        "config_json_invalid",
    }
)


def admit_argv() -> list[str]:
    """Command prefix to invoke model-admission (``python -m model_admission`` or ``admit-model``).

    Prefer **HF_BUNDLE_PYTHON** when the interpreter path contains spaces: ``shlex.split`` treats
    spaces inside an *unquoted* ``HF_BUNDLE_ADMIT_CMD`` string as word breaks, which breaks paths
    like ``/root/LLM Scanner/.venv/bin/python``.
    """
    py = os.environ.get("HF_BUNDLE_PYTHON")
    if py:
        mod = os.environ.get("HF_BUNDLE_ADMIT_MODULE", "model_admission")
        return [py, "-m", mod]
    override = os.environ.get("HF_BUNDLE_ADMIT_CMD")
    if override:
        # OK for simple paths; for spaces in the executable, set HF_BUNDLE_PYTHON instead.
        return shlex.split(override.strip(), posix=os.name != "nt")
    exe = shutil.which("admit-model")
    if exe:
        return [exe]
    return [sys.executable, "-m", "model_admission"]


def run_admit_scan(
    artifact: Path,
    policy: Path,
    *,
    drivers: str,
    timeout: int,
    fail_on: str,
) -> tuple[int, dict[str, Any] | None, str | None]:
    """Run admit-model scan; return (exit_code, report_dict_or_none, stderr_snippet)."""
    with tempfile.NamedTemporaryFile(
        suffix=".json", delete=False, prefix="admit-"
    ) as tmp:
        report_path = Path(tmp.name)
    try:
        argv = [
            *admit_argv(),
            "scan",
            "--artifact",
            str(artifact.resolve()),
            "--policy",
            str(policy.resolve()),
            "--report",
            str(report_path),
            "--drivers",
            drivers,
            "--timeout",
            str(timeout),
            "--fail-on",
            fail_on,
        ]
        proc = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout + 120,
            check=False,
            env=os.environ.copy(),
        )
        data: dict[str, Any] | None = None
        err = (proc.stderr or "") + (proc.stdout or "")
        if report_path.exists():
            try:
                data = json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                err += "; report JSON parse failed"
        return proc.returncode, data, err[:8000] if err else None
    finally:
        report_path.unlink(missing_ok=True)


def scan_bundle(
    root: Path,
    policy: Path,
    *,
    drivers: str = "",
    timeout: int = 600,
    fail_on: str = "MEDIUM",
    include_manifest: bool = True,
    discovery: DiscoveryConfig | None = None,
    hub_repo_id: str | None = None,
    hub_revision: str | None = None,
    mirror_allowlist: list[str] | None = None,
    sbom_uri: str | None = None,
) -> BundleReport:
    """Discover artifacts, lint configs, run admit-model per file, aggregate."""
    root = root.resolve()
    policy = policy.resolve()
    discovery = discovery or DiscoveryConfig()
    manifest: dict[str, Any] | None = build_manifest(root) if include_manifest else None

    cfg_paths = discover_config_files(root, discovery)
    cfg_findings = [f.to_dict() for f in lint_tree(cfg_paths)]
    config_risk = any(f["rule_id"] in CONFIG_RISK_RULE_IDS for f in cfg_findings)

    targets = discover_scan_artifacts(root, discovery)
    records: list[FileScanRecord] = []
    codes: list[int] = []

    for art in targets:
        rel = art.relative_to(root).as_posix()
        code, data, err = run_admit_scan(
            art,
            policy,
            drivers=drivers,
            timeout=timeout,
            fail_on=fail_on,
        )
        if data is not None:
            records.append(
                FileScanRecord(
                    relpath=rel,
                    exit_code=code,
                    report_path=None,
                    report=data,
                    error=err,
                )
            )
        else:
            records.append(
                FileScanRecord(
                    relpath=rel,
                    exit_code=code if code != 0 else 2,
                    report_path=None,
                    report=None,
                    error=err or "no report",
                )
            )
        codes.append(records[-1].exit_code)

    agg = compute_aggregate_exit(codes)
    agg = merge_aggregate_exit(agg, config_risk)

    provenance = build_bundle_provenance(
        manifest=manifest,
        hub_repo_id=hub_repo_id,
        hub_revision=hub_revision,
        mirror_allowlist=mirror_allowlist,
        sbom_uri=sbom_uri,
    )

    report_generated_at_utc, report_generated_at_ist = now_report_timestamps()
    return BundleReport(
        root=str(root),
        policy_path=str(policy),
        drivers=drivers,
        manifest=manifest,
        config_findings=cfg_findings,
        file_scans=records,
        aggregate_exit_code=agg,
        provenance=provenance,
        report_generated_at_utc=report_generated_at_utc,
        report_generated_at_ist=report_generated_at_ist,
    )
