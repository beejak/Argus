#!/usr/bin/env python3
"""Print a short human summary of a bundle_report.v2 JSON path (argv[1])."""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: summarize_bundle_json.py <bundle.json>", file=sys.stderr)
        return 2
    p = Path(sys.argv[1])
    d = json.loads(p.read_text(encoding="utf-8"))
    print("path:", p)
    print("aggregate_exit_code:", d.get("aggregate_exit_code"))
    print("schema:", d.get("schema"))
    print("policy_path:", d.get("policy_path"))
    print("drivers:", repr(d.get("drivers")))
    prov = d.get("provenance") or {}
    print("hub:", prov.get("hub"))
    cfs = d.get("config_findings") or []
    print("config_findings_count:", len(cfs))
    for c in cfs[:8]:
        print("  -", c.get("rule_id"), ":", (c.get("message") or "")[:120])
    fss = d.get("file_scans") or []
    print("file_scans_count:", len(fss))
    for fs in fss:
        rel = fs.get("relpath")
        code = fs.get("exit_code")
        rep = fs.get("report") if isinstance(fs.get("report"), dict) else {}
        n = len(rep.get("findings") or []) if isinstance(rep, dict) else 0
        print(f"  - {rel!r} exit={code} findings={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
