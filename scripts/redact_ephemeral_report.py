#!/usr/bin/env python3
"""Copy a bundle report JSON, redacting ephemeral /tmp/hf-ephemeral-* paths for docs."""
from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: redact_ephemeral_report.py <in.json> <out.json>", file=sys.stderr)
        return 2
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    t = src.read_text(encoding="utf-8")
    t = re.sub(r"/tmp/hf-ephemeral-[A-Za-z0-9_-]+", "/tmp/<ephemeral-hub-demo>", t)
    dst.write_text(t, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
