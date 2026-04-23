from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.snapshot import build_manifest, sha256_file, write_manifest


def test_sha256_file(tmp_path: Path) -> None:
    p = tmp_path / "a.bin"
    p.write_bytes(b"abc")
    assert len(sha256_file(p)) == 64


def test_build_manifest_sorted(tmp_path: Path) -> None:
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    d = build_manifest(tmp_path)
    rels = [f["relpath"] for f in d["files"]]
    assert rels == ["a.txt", "b.txt"]
    assert d["file_count"] == 2


def test_write_manifest_roundtrip(tmp_path: Path) -> None:
    (tmp_path / "x").write_text("x", encoding="utf-8")
    out = tmp_path / "m.json"
    write_manifest(tmp_path, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["file_count"] == 1
