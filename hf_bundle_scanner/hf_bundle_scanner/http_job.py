"""Optional thin HTTP API for bundle scan (bind localhost in production)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from hf_bundle_scanner.dispatch import scan_bundle


class ScanBody(BaseModel):
    """Request body for POST /v1/scan (module-level model for reliable OpenAPI / validation)."""

    model_config = ConfigDict(extra="ignore")

    # Avoid JSON field name "root" (Pydantic model internals / tooling edge cases).
    snapshot_root: str = Field(..., description="Absolute path to snapshot root")
    policy_path: str = Field(..., description="Absolute path to model-admission policy JSON")
    drivers: str = Field(default="", description="Comma-separated admit-model drivers")
    timeout: int = Field(default=600, ge=1, le=86_400)
    fail_on: str = Field(default="MEDIUM")
    include_manifest: bool = Field(default=True)


def create_app():
    from fastapi import FastAPI, HTTPException

    app = FastAPI(title="hf-bundle-scanner", version="0.1.0")

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/v1/scan")
    def scan(scan_in: ScanBody) -> dict[str, Any]:
        root = Path(scan_in.snapshot_root)
        policy = Path(scan_in.policy_path)
        if not root.is_dir():
            raise HTTPException(status_code=400, detail="snapshot_root must be a directory")
        if not policy.is_file():
            raise HTTPException(status_code=400, detail="policy_path must be a file")
        bundle = scan_bundle(
            root,
            policy,
            drivers=scan_in.drivers,
            timeout=scan_in.timeout,
            fail_on=scan_in.fail_on,
            include_manifest=scan_in.include_manifest,
        )
        return bundle.to_dict()

    return app


def run_uvicorn() -> None:
    import uvicorn

    host = os.environ.get("HF_BUNDLE_HTTP_HOST", "127.0.0.1")
    port = int(os.environ.get("HF_BUNDLE_HTTP_PORT", "8765"))
    app = create_app()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_uvicorn()
