"""Optional: download a single <1GiB artifact from a repo listed in the chwoo collection, then bundle-scan.

Collection (curated list, not an endorsement): https://huggingface.co/collections/chwoo/uncensored-models

We use ``mradermacher/gemma3-4b-it-abliterated-GGUF`` because the smallest *weight-like* file in that repo
under 1GiB is the vision projector ``mmproj`` GGUF (~561MiB). Full chat GGUF shards there are >1.6GiB.

Run::

    HF_BUNDLE_CHWOO_SCAN=1 HF_BUNDLE_PYTHON=/path/to/.venv/bin/python \\
      python -m pytest tests/test_integration_chwoo_collection.py -v --tb=short
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO_ID = "mradermacher/gemma3-4b-it-abliterated-GGUF"
FILENAME = "gemma3-4b-it-abliterated.mmproj-Q8_0.gguf"
MAX_BYTES = 600 * 1024 * 1024  # 600 MiB ceiling sanity check


@pytest.mark.integration
@pytest.mark.chwoo
@pytest.mark.skipif(
    not os.environ.get("HF_BUNDLE_CHWOO_SCAN"),
    reason="set HF_BUNDLE_CHWOO_SCAN=1 to download ~561MiB and scan (network)",
)
def test_chwoo_collection_small_mmproj_download_and_scan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from huggingface_hub import hf_hub_download

    monkeypatch.delenv("HF_BUNDLE_ADMIT_CMD", raising=False)
    monkeypatch.setenv("HF_BUNDLE_PYTHON", sys.executable)

    dest = tmp_path / "snap"
    dest.mkdir(parents=True, exist_ok=True)
    p = hf_hub_download(repo_id=REPO_ID, filename=FILENAME, local_dir=str(dest))
    path = Path(p).resolve()
    assert path.is_file()
    assert path.stat().st_size <= MAX_BYTES, f"unexpected size {path.stat().st_size}"

    from hf_bundle_scanner.dispatch import scan_bundle

    policy = Path(__file__).resolve().parent / "fixtures" / "policy.permissive.json"
    bundle = scan_bundle(dest, policy, drivers="", timeout=600, include_manifest=True)
    assert bundle.manifest is not None
    assert bundle.manifest["file_count"] >= 1
    assert len(bundle.file_scans) >= 1
    assert bundle.file_scans[0].relpath.endswith(".gguf")
    assert bundle.aggregate_exit_code in (0, 1, 2)
