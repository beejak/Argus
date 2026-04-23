"""Ledger append-only JSONL."""

from __future__ import annotations

import json
from pathlib import Path

from model_admission.ledger import append_ledger


def test_append_ledger_writes_one_json_line(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    append_ledger(path, {"event": "test", "ok": True})
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    obj = json.loads(lines[0])
    assert obj["event"] == "test"
    assert obj["ok"] is True
    assert "ts" in obj


def test_append_ledger_appends_second_line(tmp_path: Path) -> None:
    path = tmp_path / "l.jsonl"
    append_ledger(path, {"n": 1})
    append_ledger(path, {"n": 2})
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["n"] == 2
