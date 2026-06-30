"""Tests for script_lint — AST-based detection of risky patterns in bundled .py files."""

from __future__ import annotations

from pathlib import Path

from hf_bundle_scanner.script_lint import lint_python_file, lint_python_files


# ---------------------------------------------------------------------------
# trust_remote_code_in_script — positive cases
# ---------------------------------------------------------------------------


def test_trust_remote_code_kwarg_flagged(tmp_path: Path) -> None:
    p = tmp_path / "train.py"
    p.write_text('model = AutoModel.from_pretrained("x", trust_remote_code=True)\n')
    fs = lint_python_file(p)
    assert any(f.rule_id == "trust_remote_code_in_script" for f in fs)


def test_trust_remote_code_lineno_reported(tmp_path: Path) -> None:
    p = tmp_path / "train.py"
    p.write_text("import transformers\nmodel = transformers.AutoModel.from_pretrained(\n    'x', trust_remote_code=True\n)\n")
    fs = lint_python_file(p)
    hit = next(f for f in fs if f.rule_id == "trust_remote_code_in_script")
    assert hit.lineno is not None and hit.lineno >= 3


def test_trust_remote_code_in_function_flagged(tmp_path: Path) -> None:
    p = tmp_path / "loader.py"
    p.write_text(
        "def load():\n    return AutoTokenizer.from_pretrained('m', trust_remote_code=True)\n"
    )
    fs = lint_python_file(p)
    assert any(f.rule_id == "trust_remote_code_in_script" for f in fs)


def test_multiple_calls_all_flagged(tmp_path: Path) -> None:
    p = tmp_path / "multi.py"
    p.write_text(
        "AutoModel.from_pretrained('a', trust_remote_code=True)\n"
        "AutoTokenizer.from_pretrained('b', trust_remote_code=True)\n"
    )
    fs = lint_python_file(p)
    hits = [f for f in fs if f.rule_id == "trust_remote_code_in_script"]
    assert len(hits) == 2


# ---------------------------------------------------------------------------
# trust_remote_code_in_script — negative cases (must NOT fire)
# ---------------------------------------------------------------------------


def test_trust_remote_code_commented_out_not_flagged(tmp_path: Path) -> None:
    p = tmp_path / "train.py"
    p.write_text("# model = AutoModel.from_pretrained('x', trust_remote_code=True)\n")
    fs = lint_python_file(p)
    assert not any(f.rule_id == "trust_remote_code_in_script" for f in fs)


def test_trust_remote_code_in_docstring_not_flagged(tmp_path: Path) -> None:
    p = tmp_path / "docs.py"
    p.write_text(
        '"""\nExample: AutoModel.from_pretrained("x", trust_remote_code=True)\n"""\n'
    )
    fs = lint_python_file(p)
    assert not any(f.rule_id == "trust_remote_code_in_script" for f in fs)


def test_trust_remote_code_false_not_flagged(tmp_path: Path) -> None:
    p = tmp_path / "safe.py"
    p.write_text('model = AutoModel.from_pretrained("x", trust_remote_code=False)\n')
    fs = lint_python_file(p)
    assert not any(f.rule_id == "trust_remote_code_in_script" for f in fs)


def test_trust_remote_code_absent_not_flagged(tmp_path: Path) -> None:
    p = tmp_path / "clean.py"
    p.write_text('model = AutoModel.from_pretrained("x")\n')
    fs = lint_python_file(p)
    assert not any(f for f in fs)


def test_trust_remote_code_string_variable_not_flagged(tmp_path: Path) -> None:
    """trust_remote_code=some_var is not flagged — we only flag literal True."""
    p = tmp_path / "var.py"
    p.write_text(
        "trc = True\nmodel = AutoModel.from_pretrained('x', trust_remote_code=trc)\n"
    )
    fs = lint_python_file(p)
    assert not any(f.rule_id == "trust_remote_code_in_script" for f in fs)


# ---------------------------------------------------------------------------
# script_parse_error
# ---------------------------------------------------------------------------


def test_syntax_error_emits_parse_error_finding(tmp_path: Path) -> None:
    p = tmp_path / "broken.py"
    p.write_text("def foo(\n")
    fs = lint_python_file(p)
    assert any(f.rule_id == "script_parse_error" for f in fs)


def test_empty_file_clean(tmp_path: Path) -> None:
    p = tmp_path / "empty.py"
    p.write_text("")
    fs = lint_python_file(p)
    assert fs == []


# ---------------------------------------------------------------------------
# lint_python_files batch helper
# ---------------------------------------------------------------------------


def test_lint_python_files_aggregates_across_files(tmp_path: Path) -> None:
    clean = tmp_path / "clean.py"
    clean.write_text('model = AutoModel.from_pretrained("x")\n')
    risky = tmp_path / "risky.py"
    risky.write_text('model = AutoModel.from_pretrained("x", trust_remote_code=True)\n')

    all_findings = lint_python_files([clean, risky])
    assert not any(f.path == str(clean) and f.rule_id == "trust_remote_code_in_script" for f in all_findings)
    assert any(f.path == str(risky) and f.rule_id == "trust_remote_code_in_script" for f in all_findings)


def test_lint_python_files_empty_list(tmp_path: Path) -> None:
    assert lint_python_files([]) == []
