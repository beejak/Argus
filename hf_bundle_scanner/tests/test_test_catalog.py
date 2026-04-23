"""Tests for ``hf_bundle_scanner.test_catalog`` resolution."""

from __future__ import annotations

from pathlib import Path

from hf_bundle_scanner import test_catalog as tc


def test_monorepo_root_contains_catalog():
    root = tc.monorepo_root()
    assert (root / "llm_security_test_cases" / "catalog.json").is_file()


def test_default_path_next_to_repo():
    root = tc.monorepo_root()
    p = tc.resolve_test_catalog_path(repo_root=root, environ={})
    assert p == (root / "llm_security_test_cases" / "catalog.json").resolve()


def test_env_override_absolute(tmp_path: Path):
    f = tmp_path / "custom.json"
    f.write_text("{}", encoding="utf-8")
    p = tc.resolve_test_catalog_path(
        repo_root=tmp_path,
        environ={tc.TEST_CATALOG_ENV_VAR: str(f)},
    )
    assert p == f.resolve()


def test_env_override_relative_to_repo_root(tmp_path: Path):
    sub = tmp_path / "llm_security_test_cases"
    sub.mkdir(parents=True)
    cat = sub / "catalog.json"
    cat.write_text("{}", encoding="utf-8")
    p = tc.resolve_test_catalog_path(
        repo_root=tmp_path,
        environ={tc.TEST_CATALOG_ENV_VAR: "llm_security_test_cases/catalog.json"},
    )
    assert p == cat.resolve()


def test_config_cli_wins_over_env(tmp_path: Path):
    env_file = tmp_path / "from_env.json"
    env_file.write_text("{}", encoding="utf-8")
    cli_file = tmp_path / "from_cli.json"
    cli_file.write_text("{}", encoding="utf-8")
    p = tc.resolve_test_catalog_path(
        repo_root=tmp_path,
        config_or_cli_path=cli_file,
        environ={tc.TEST_CATALOG_ENV_VAR: str(env_file)},
    )
    assert p == cli_file.resolve()


def test_config_cli_relative_to_repo_root(tmp_path: Path):
    sub = tmp_path / "alt" / "c.json"
    sub.parent.mkdir(parents=True)
    sub.write_text("{}", encoding="utf-8")
    p = tc.resolve_test_catalog_path(
        repo_root=tmp_path,
        config_or_cli_path=Path("alt/c.json"),
        environ={},
    )
    assert p == sub.resolve()


def test_llm_security_test_catalog_fixture(llm_security_test_catalog: dict) -> None:
    assert llm_security_test_catalog.get("catalog_version")
    assert isinstance(llm_security_test_catalog.get("cases"), list)


def test_load_test_catalog_json_roundtrip(tmp_path: Path):
    sub = tmp_path / "llm_security_test_cases"
    sub.mkdir()
    cat = sub / "catalog.json"
    body = '{"catalog_version":"9.9.9","cases":[]}'
    cat.write_text(body, encoding="utf-8")
    data = tc.load_test_catalog_json(
        repo_root=tmp_path,
        environ={tc.TEST_CATALOG_ENV_VAR: ""},
    )
    assert data["catalog_version"] == "9.9.9"
    assert data["cases"] == []
