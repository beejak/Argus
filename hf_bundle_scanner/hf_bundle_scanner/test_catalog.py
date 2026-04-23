"""Resolve the LLM security test catalog path for the next run (CI + local)."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

TEST_CATALOG_ENV_VAR = "LLM_SCANNER_TEST_CATALOG"
_REL_CATALOG = Path("llm_security_test_cases") / "catalog.json"


def monorepo_root() -> Path:
    """Return the LLM Scanner repo root (parent of ``hf_bundle_scanner/``)."""
    # hf_bundle_scanner/hf_bundle_scanner/test_catalog.py -> parents[2] == repo root
    return Path(__file__).resolve().parents[2]


def resolve_test_catalog_path(
    *,
    repo_root: Path | None = None,
    config_or_cli_path: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> Path:
    """
    Resolution order: **config/CLI** (``config_or_cli_path``) → **env**
    ``LLM_SCANNER_TEST_CATALOG`` (see ``TEST_CATALOG_ENV_VAR``) → default ``<repo>/llm_security_test_cases/catalog.json``.
    """
    if config_or_cli_path is not None:
        p = Path(config_or_cli_path).expanduser()
        return p if p.is_absolute() else (repo_root or monorepo_root()) / p

    envmap = environ if environ is not None else os.environ
    raw = envmap.get(TEST_CATALOG_ENV_VAR, "").strip()
    if raw:
        p = Path(raw).expanduser()
        return p if p.is_absolute() else (repo_root or monorepo_root()) / p

    root = repo_root or monorepo_root()
    return (root / _REL_CATALOG).resolve()


def load_test_catalog_json(
    *,
    repo_root: Path | None = None,
    config_or_cli_path: str | Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Load ``catalog.json`` using the same resolution as :func:`resolve_test_catalog_path`."""
    path = resolve_test_catalog_path(
        repo_root=repo_root,
        config_or_cli_path=config_or_cli_path,
        environ=environ,
    )
    return json.loads(path.read_text(encoding="utf-8"))
