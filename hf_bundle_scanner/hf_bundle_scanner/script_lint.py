"""Detect high-risk patterns in Python scripts bundled alongside model weights.

Uses AST parsing so comments and string literals in docstrings are not flagged.
Covers .py files that configlint cannot reach (configlint only reads JSON).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


RULE_IDS_EMITTED: frozenset[str] = frozenset(
    {
        "trust_remote_code_in_script",
        "script_parse_error",
    }
)


@dataclass
class ScriptFinding:
    path: str
    rule_id: str
    message: str
    lineno: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "path": self.path,
            "rule_id": self.rule_id,
            "message": self.message,
            "lineno": self.lineno,
        }


def _is_trust_remote_code_kwarg(node: ast.keyword) -> bool:
    return (
        node.arg == "trust_remote_code"
        and isinstance(node.value, ast.Constant)
        and node.value.value is True
    )


def lint_python_file(path: Path) -> list[ScriptFinding]:
    rel = str(path)
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=rel)
    except SyntaxError as e:
        return [ScriptFinding(rel, "script_parse_error", f"syntax error: {e}", lineno=e.lineno)]

    findings: list[ScriptFinding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if _is_trust_remote_code_kwarg(kw):
                    findings.append(
                        ScriptFinding(
                            rel,
                            "trust_remote_code_in_script",
                            f"trust_remote_code=True passed to a call at line {kw.value.lineno}; "
                            "executing Hub Python is a supply-chain risk",
                            lineno=kw.value.lineno,
                        )
                    )
    return findings


def lint_python_files(paths: list[Path]) -> list[ScriptFinding]:
    out: list[ScriptFinding] = []
    for p in paths:
        out.extend(lint_python_file(p))
    return out
