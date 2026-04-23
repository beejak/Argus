"""Unit tests for README slogan rotation (loads script from repo root)."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_rotate_module():
    root = Path(__file__).resolve().parents[2]
    path = root / "scripts" / "rotate_readme_slogan.py"
    spec = importlib.util.spec_from_file_location("rotate_readme_slogan", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_format_block_contains_markers() -> None:
    mod = _load_rotate_module()
    b = mod.format_block("Hello world")
    assert mod.MARKER_START in b
    assert mod.MARKER_END in b
    assert 'align="center"' in b
    assert "Hello world" in b


def test_replace_slogan_region_updates_text() -> None:
    mod = _load_rotate_module()
    readme = "# Title\n" + mod.format_block("OLD") + "\ntrailer"
    out = mod.replace_slogan_region(readme, "NEW")
    assert "NEW" in out
    assert "OLD" not in out
    assert "trailer" in out
