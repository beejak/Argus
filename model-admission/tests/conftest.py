"""Pytest hooks and fixtures for model-admission."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HF_PKG = _REPO_ROOT / "hf_bundle_scanner"
if _HF_PKG.is_dir() and str(_HF_PKG) not in sys.path:
    sys.path.insert(0, str(_HF_PKG))

from hf_bundle_scanner.test_catalog import load_test_catalog_json  # noqa: E402


@pytest.fixture(scope="session")
def llm_security_test_catalog() -> dict:
    """Same catalog JSON as hf_bundle_scanner tests (monorepo sibling import)."""
    return load_test_catalog_json(repo_root=_REPO_ROOT)
