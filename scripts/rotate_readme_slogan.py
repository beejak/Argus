#!/usr/bin/env python3
"""Rotate the README tagline using docs/slogans.json and .github/data/slogan_state.json."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README_PATH = ROOT / "README.md"
POOL_PATH = ROOT / "docs" / "slogans.json"
STATE_PATH = ROOT / ".github" / "data" / "slogan_state.json"
MARKER_START = "<!-- SLOGAN_START -->"
MARKER_END = "<!-- SLOGAN_END -->"


def _load_pool() -> list[str]:
    data = json.loads(POOL_PATH.read_text(encoding="utf-8"))
    slogans: list[str] = list(data["slogans"])
    if len(set(slogans)) != len(slogans):
        raise SystemExit("docs/slogans.json: duplicate slogan strings are not allowed")
    if not slogans:
        raise SystemExit("docs/slogans.json: slogans[] must be non-empty")
    return slogans


def _load_state() -> dict[str, int]:
    if not STATE_PATH.is_file():
        return {"next_slogan_index": 0}
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _save_state(state: dict[str, int]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def format_block(slogan: str) -> str:
    return f"{MARKER_START}\n> *{slogan}*\n{MARKER_END}"


def replace_slogan_region(readme: str, slogan: str) -> str:
    if MARKER_START not in readme or MARKER_END not in readme:
        raise SystemExit(
            f"{README_PATH}: missing {MARKER_START} / {MARKER_END} — add markers around the tagline block"
        )
    block = format_block(slogan)
    pattern = re.escape(MARKER_START) + r"[\s\S]*?" + re.escape(MARKER_END)
    new_readme, n = re.subn(pattern, block, readme, count=1)
    if n != 1:
        raise SystemExit("failed to replace exactly one slogan region in README")
    return new_readme


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the chosen index and slogan without writing files",
    )
    args = p.parse_args(argv)

    slogans = _load_pool()
    state = _load_state()
    idx = int(state.get("next_slogan_index", 0)) % len(slogans)
    chosen = slogans[idx]
    next_idx = (idx + 1) % len(slogans)

    if args.dry_run:
        print(f"Would apply index {idx}/{len(slogans)}:\n{chosen}\nNext index after write: {next_idx}")
        return 0

    readme = README_PATH.read_text(encoding="utf-8")
    new_readme = replace_slogan_region(readme, chosen)
    README_PATH.write_text(new_readme, encoding="utf-8", newline="\n")
    _save_state({"next_slogan_index": next_idx})
    print(f"Applied slogan index {idx}; next_slogan_index={next_idx}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
