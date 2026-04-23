from __future__ import annotations

from pathlib import Path

import pytest

from hf_bundle_scanner.test_catalog import load_test_catalog_json


@pytest.fixture(scope="session")
def llm_security_test_catalog() -> dict:
    """Machine-readable LLM security test catalog for the monorepo (see docs/TEST_CASES_*)."""
    return load_test_catalog_json()


def write_minimal_safetensors(path: Path) -> None:
    header = b"{}"
    n = len(header)
    path.write_bytes(n.to_bytes(8, "little") + header)
