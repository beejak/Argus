"""Tests for bundle report provenance (phase 1)."""

from __future__ import annotations

from hf_bundle_scanner.provenance import build_bundle_provenance
from hf_bundle_scanner.report import BUNDLE_REPORT_SCHEMA


def test_bundle_schema_constant() -> None:
    assert BUNDLE_REPORT_SCHEMA == "hf_bundle_scanner.bundle_report.v2"


def test_build_provenance_minimal() -> None:
    p = build_bundle_provenance(manifest=None, environ={})
    assert p["provenance_version"] == "phase1"
    assert "hub" not in p
    assert "mirror_allowlist" not in p


def test_build_provenance_hub_and_sbom() -> None:
    p = build_bundle_provenance(
        manifest=None,
        hub_repo_id="org/model",
        hub_revision="main",
        sbom_uri="file:///tmp/sbom.json",
        environ={},
    )
    assert p["hub"] == {"repo_id": "org/model", "revision": "main"}
    assert p["sbom"] == {"uri": "file:///tmp/sbom.json"}


def test_build_provenance_env_mirrors_merged() -> None:
    p = build_bundle_provenance(
        manifest=None,
        mirror_allowlist=["cdn.example.com"],
        environ={"HF_BUNDLE_MIRROR_ALLOWLIST": "huggingface.co, cdn.example.com "},
    )
    assert p["mirror_allowlist"] == ["huggingface.co", "cdn.example.com"]


def test_build_provenance_manifest_summary() -> None:
    man = {"root": "/x", "file_count": 2, "files": []}
    p = build_bundle_provenance(manifest=man, environ={})
    assert p["manifest_summary"]["file_count"] == 2
    assert len(p["manifest_summary"]["sha256"]) == 64
