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
