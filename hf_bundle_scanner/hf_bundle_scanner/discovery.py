"""Discover scan targets under a snapshot root."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

# Extensions sent to model-admission (single-file scan).
DEFAULT_SCAN_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".safetensors",
        ".bin",
        ".pt",
        ".pth",
        ".ckpt",
        ".pkl",
        ".pickle",
        ".gguf",
        ".onnx",
        ".h5",
        ".hdf5",
        ".npz",
        ".msgpack",
    }
)

DEFAULT_CONFIG_NAMES: frozenset[str] = frozenset(
    {
        "config.json",
        "tokenizer_config.json",
        "generation_config.json",
    }
)


@dataclass
class DiscoveryConfig:
    """include_globs empty means all files (subject to excludes)."""

    include_globs: list[str] = field(default_factory=list)
    exclude_globs: list[str] = field(
        default_factory=lambda: [
            "**/.git/**",
            "**/__pycache__/**",
            "**/.venv/**",
        ]
    )
    scan_extensions: frozenset[str] | None = None  # None => DEFAULT_SCAN_EXTENSIONS


def _builtin_excluded(rel_posix: str) -> bool:
    parts = rel_posix.split("/")
    return any(
        x in parts
        for x in (
            ".git",
            "__pycache__",
            ".venv",
            "node_modules",
        )
    )


def _matches_any(rel_posix: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(rel_posix, pat):
            return True
    return False


def _included(rel_posix: str, cfg: DiscoveryConfig) -> bool:
    if not cfg.include_globs:
        return True
    return any(fnmatch.fnmatch(rel_posix, g) for g in cfg.include_globs)


def iter_files(root: Path, cfg: DiscoveryConfig) -> list[Path]:
    root = root.resolve()
    out: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if _builtin_excluded(rel):
            continue
        if not _included(rel, cfg):
            continue
        if _matches_any(rel, cfg.exclude_globs):
            continue
        out.append(p)
    out.sort(key=lambda x: x.relative_to(root).as_posix())
    return out


def discover_scan_artifacts(root: Path, cfg: DiscoveryConfig | None = None) -> list[Path]:
    """Regular files whose suffix is a candidate for weight/serialization scanning."""
    cfg = cfg or DiscoveryConfig()
    exts = cfg.scan_extensions if cfg.scan_extensions is not None else DEFAULT_SCAN_EXTENSIONS
    return [p for p in iter_files(root, cfg) if p.suffix.lower() in exts]


def discover_config_files(root: Path, cfg: DiscoveryConfig | None = None) -> list[Path]:
    """JSON config files checked by configlint."""
    cfg = cfg or DiscoveryConfig()
    names = DEFAULT_CONFIG_NAMES
    return [p for p in iter_files(root, cfg) if p.name in names]
