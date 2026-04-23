from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from hf_bundle_scanner.http_job import create_app


def test_healthz() -> None:
    c = TestClient(create_app())
    r = c.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_scan_endpoint(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("HF_BUNDLE_ADMIT_CMD", raising=False)
    monkeypatch.setenv("HF_BUNDLE_PYTHON", sys.executable)
    header = b"{}"
    (tmp_path / "x.safetensors").write_bytes(len(header).to_bytes(8, "little") + header)
    pol = tmp_path / "policy.json"
    pol.write_text(
        '{"max_bytes": 1073741824, "forbidden_extensions": null, "allowed_extensions": null, "sha256_allowlist": null}',
        encoding="utf-8",
    )
    c = TestClient(create_app())
    r = c.post(
        "/v1/scan",
        json={
            "snapshot_root": str(tmp_path),
            "policy_path": str(pol),
            "drivers": "",
            "timeout": 120,
            "fail_on": "MEDIUM",
            "include_manifest": False,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["aggregate_exit_code"] == 0
