"""Snapshot directory manifest and optional Hugging Face Hub download."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


def sha256_file(path: Path, chunk: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


@dataclass
class FileEntry:
    relpath: str
    size_bytes: int
    sha256: str


def build_manifest(root: Path) -> dict[str, Any]:
    """Walk regular files under root, return stable JSON-serializable manifest."""
    root = root.resolve()
    entries: list[FileEntry] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(root).as_posix()
        except ValueError:
            continue
        entries.append(
            FileEntry(
                relpath=rel,
                size_bytes=p.stat().st_size,
                sha256=sha256_file(p),
            )
        )
    return {
        "root": str(root),
        "file_count": len(entries),
        "files": [asdict(e) for e in entries],
    }


def write_manifest(root: Path, out: Path) -> dict[str, Any]:
    data = build_manifest(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def snapshot_download(repo_id: str, revision: str | None, dest: Path) -> Path:
    """Download Hub snapshot into dest (creates directory). Requires huggingface_hub."""
    import inspect

    from huggingface_hub import snapshot_download

    dest.mkdir(parents=True, exist_ok=True)
    kwargs: dict[str, object] = {
        "repo_id": repo_id,
        "revision": revision,
        "local_dir": str(dest),
    }
    sig = inspect.signature(snapshot_download)
    if "local_dir_use_symlinks" in sig.parameters:
        kwargs["local_dir_use_symlinks"] = False
    path = snapshot_download(**kwargs)
    return Path(path)
