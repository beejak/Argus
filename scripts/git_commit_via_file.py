#!/usr/bin/env python3
"""Run ``git commit -F`` with the message in a temp file (avoids broken ``-m`` quoting / tooling)."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "message",
        nargs="?",
        default="",
        help="Commit message body; use - to read from stdin",
    )
    parser.add_argument(
        "--amend",
        action="store_true",
        help="Pass --amend to git commit",
    )
    args, passthrough = parser.parse_known_args()

    if args.message == "-":
        body = sys.stdin.read()
    else:
        body = args.message
    if not body.strip():
        parser.error("message required (positional argument, or '-' for stdin)")

    extra: list[str] = []
    if passthrough:
        extra = passthrough[1:] if passthrough[0] == "--" else list(passthrough)

    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        suffix=".gitmsg",
        delete=False,
    ) as tmp:
        tmp.write(body.rstrip() + "\n")
        path = Path(tmp.name)

    cmd = ["git", "commit", "-F", str(path)]
    if args.amend:
        cmd.append("--amend")
    cmd.extend(extra)

    try:
        return subprocess.call(cmd)
    finally:
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
