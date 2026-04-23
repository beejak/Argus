"""Phase-1 bundle report provenance (Hub revision, mirror allowlist, SBOM pointer, manifest digest)."""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Mapping
from typing import Any

ENV_MIRROR_ALLOWLIST = "HF_BUNDLE_MIRROR_ALLOWLIST"
ENV_SBOM_URI = "HF_BUNDLE_SBOM_URI"


def _parse_csv_hosts(raw: str | None) -> list[str]:
    if not raw or not str(raw).strip():
        return []
    return [x.strip() for x in str(raw).split(",") if x.strip()]


def _manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return {
        "sha256": digest,
        "file_count": int(manifest.get("file_count", 0)),
    }


def build_bundle_provenance(
    *,
    manifest: dict[str, Any] | None,
    hub_repo_id: str | None = None,
    hub_revision: str | None = None,
    mirror_allowlist: list[str] | None = None,
    sbom_uri: str | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """
    Assemble the ``provenance`` object for a bundle report.

    Environment (optional, merged with explicit args; explicit lists/URI win for SBOM,
    mirrors are merged + de-duplicated in order: env first, then explicit).
    """
    envmap = environ if environ is not None else os.environ

    mirrors = _parse_csv_hosts(envmap.get(ENV_MIRROR_ALLOWLIST))
    if mirror_allowlist:
        for h in mirror_allowlist:
            if h and h not in mirrors:
                mirrors.append(h)

    sbom = (sbom_uri or envmap.get(ENV_SBOM_URI) or "").strip() or None

    hub: dict[str, str] = {}
    if hub_repo_id:
        hub["repo_id"] = hub_repo_id
    if hub_revision:
        hub["revision"] = hub_revision

    out: dict[str, Any] = {"provenance_version": "phase1"}
    if hub:
        out["hub"] = hub
    if mirrors:
        out["mirror_allowlist"] = mirrors
    if sbom:
        out["sbom"] = {"uri": sbom}
    if manifest is not None:
        out["manifest_summary"] = _manifest_summary(manifest)
    return out
