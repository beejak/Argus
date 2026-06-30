from __future__ import annotations

from pathlib import Path

from hf_bundle_scanner.discovery import (
    DiscoveryConfig,
    discover_config_files,
    discover_scan_artifacts,
    iter_files,
)


def test_iter_files_respects_exclude(tmp_path: Path) -> None:
    (tmp_path / "ok.txt").write_text("x", encoding="utf-8")
    git = tmp_path / ".git" / "config"
    git.parent.mkdir(parents=True)
    git.write_text("git", encoding="utf-8")
    cfg = DiscoveryConfig()
    files = iter_files(tmp_path, cfg)
    assert [p.name for p in files] == ["ok.txt"]
    assert not any(".git" in p.parts for p in files)


def test_discover_scan_artifacts_by_suffix(tmp_path: Path) -> None:
    (tmp_path / "w.safetensors").write_bytes(b"x")
    (tmp_path / "readme.txt").write_text("hi", encoding="utf-8")
    arts = discover_scan_artifacts(tmp_path)
    assert len(arts) == 1
    assert arts[0].name == "w.safetensors"


def test_discover_config_files(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "tokenizer_config.json").write_text("{}", encoding="utf-8")
    (tmp_path / "other.json").write_text("{}", encoding="utf-8")
    cfgs = discover_config_files(tmp_path)
    assert {p.name for p in cfgs} == {"config.json", "tokenizer_config.json"}


def test_discover_config_files_includes_generation_config(tmp_path: Path) -> None:
    (tmp_path / "generation_config.json").write_text("{}", encoding="utf-8")
    cfgs = discover_config_files(tmp_path)
    assert any(p.name == "generation_config.json" for p in cfgs)


def test_discover_scan_artifacts_uppercase_extension(tmp_path: Path) -> None:
    (tmp_path / "model.GGUF").write_bytes(b"x")
    (tmp_path / "weights.PT").write_bytes(b"x")
    arts = discover_scan_artifacts(tmp_path)
    names = {a.name for a in arts}
    assert "model.GGUF" in names
    assert "weights.PT" in names


def test_discover_scan_artifacts_custom_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.safetensors").write_bytes(b"x")
    (tmp_path / "b.bin").write_bytes(b"x")
    cfg = DiscoveryConfig(scan_extensions=frozenset({".safetensors"}))
    arts = discover_scan_artifacts(tmp_path, cfg)
    names = {a.name for a in arts}
    assert "a.safetensors" in names
    assert "b.bin" not in names


def test_iter_files_include_globs_filters(tmp_path: Path) -> None:
    (tmp_path / "a.safetensors").write_bytes(b"x")
    (tmp_path / "b.safetensors").write_bytes(b"x")
    (tmp_path / "c.bin").write_bytes(b"x")
    cfg = DiscoveryConfig(include_globs=["*.safetensors"])
    files = iter_files(tmp_path, cfg)
    names = {f.name for f in files}
    assert "a.safetensors" in names
    assert "b.safetensors" in names
    assert "c.bin" not in names


def test_iter_files_excludes_node_modules(tmp_path: Path) -> None:
    nm = tmp_path / "node_modules" / "pkg"
    nm.mkdir(parents=True)
    (nm / "index.js").write_text("x", encoding="utf-8")
    (tmp_path / "ok.txt").write_text("x", encoding="utf-8")
    files = iter_files(tmp_path, DiscoveryConfig())
    assert not any("node_modules" in p.parts for p in files)
    assert any(f.name == "ok.txt" for f in files)


def test_discover_scan_artifacts_empty_directory(tmp_path: Path) -> None:
    arts = discover_scan_artifacts(tmp_path)
    assert arts == []
