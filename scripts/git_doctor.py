#!/usr/bin/env python3
"""Print Git trailer-related config and env hints for `commit` failures."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys


def main() -> int:
    print("git:", shutil.which("git") or "(not found)")
    try:
        ver = subprocess.run(
            ["git", "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        print(ver)
    except (OSError, subprocess.CalledProcessError) as e:
        print("Could not run git --version:", e, file=sys.stderr)
        return 1

    print("\n--- env (names matching TRAILER / GIT_COMMIT) ---")
    for k, v in sorted(os.environ.items()):
        if re.search(r"TRAILER|GIT_COMMIT", k, re.I):
            print(f"{k}={v!r}")

    print("\n--- `git config --list --show-origin` lines matching trailer ---")
    r = subprocess.run(
        ["git", "config", "--list", "--show-origin"],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        print(r.stderr or r.stdout or "(git config failed)", file=sys.stderr)
        return r.returncode
    hits = [ln for ln in r.stdout.splitlines() if re.search(r"trailer", ln, re.I)]
    if not hits:
        print("(none)")
    else:
        for ln in hits:
            print(ln)

    print("\n--- `git config --global --get-regexp '^alias\\.'` ---")
    a = subprocess.run(
        ["git", "config", "--global", "--get-regexp", r"^alias\."],
        capture_output=True,
        text=True,
    )
    if a.returncode == 0 and a.stdout.strip():
        print(a.stdout.rstrip())
    else:
        print("(none or not readable)")

    print("\nTip: if `git commit -m ...` fails with `option trailer requires a value`,")
    print("use `git commit -F FILE`, `make commit-msg MSG=...`, or `python3 scripts/git_commit_via_file.py`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
