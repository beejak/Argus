"""Network integration (skipped by default)."""

from __future__ import annotations

from pathlib import Path

import pytest

from hf_bundle_scanner.snapshot import snapshot_download


@pytest.mark.integration
def test_snapshot_download_smoke(tmp_path: Path) -> None:
    dest = tmp_path / "hub"
    try:
        path = snapshot_download("hf-internal-testing/tiny-random-BertModel", None, dest)
    except Exception as e:  # pragma: no cover
        pytest.skip(f"Hub unreachable: {e}")
    assert Path(path).exists()
    files = list(Path(path).rglob("*"))
    assert files
