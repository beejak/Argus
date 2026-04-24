#!/usr/bin/env python3
"""Search Hugging Face Hub for **model** repos whose **committed file sizes** sum under a limit.

Uses ``HfApi.list_models`` (text search) + ``HfApi.model_info(..., files_metadata=True)`` to sum
``sibling.size`` bytes. This is a **heuristic** for “small enough to download for a lab drill” —
LFS pointer quirks and omitted metadata can make totals wrong; always verify before large pulls.

Network required. Be polite: small sleeps between ``model_info`` calls.

Example::

    ./.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 12

Optional: probe a few repos for ``trust_remote_code`` in ``tokenizer_config.json`` / ``config.json``::

    ./.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 8 \\
        --probe-trust-remote-code --max-probes 5
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import tempfile
import time
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download


DEFAULT_QUERIES: tuple[str, ...] = (
    "tiny",
    "small",
    "mini",
    "distil",
    "compact",
    "bert-tiny",
    "gpt2 small",
)


def _truthy_remote_code(text: str) -> bool:
    if "trust_remote_code" not in text.lower():
        return False
    # crude: "trust_remote_code": true or : true
    return bool(re.search(r"trust_remote_code\"?\s*:\s*true\b", text, flags=re.I))


def _probe_remote_code(repo_id: str) -> tuple[bool, str]:
    """Return (hit, detail) after trying tiny JSON files only."""
    hits: list[str] = []
    with tempfile.TemporaryDirectory(prefix="hf-probe-") as td:
        root = Path(td)
        for fname in ("tokenizer_config.json", "config.json"):
            try:
                p = hf_hub_download(
                    repo_id,
                    filename=fname,
                    local_dir=str(root),
                    local_dir_use_symlinks=False,
                )
                body = Path(p).read_text(encoding="utf-8", errors="replace")
                if _truthy_remote_code(body):
                    hits.append(f"{fname}: trust_remote_code truthy")
            except Exception:
                continue
    if not hits:
        return False, ""
    return True, "; ".join(hits)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-mb", type=float, default=200.0, help="Max total sibling bytes (default: 200)")
    ap.add_argument(
        "--queries",
        default=",".join(DEFAULT_QUERIES),
        help="Comma-separated list_models search strings (default: built-in broad set)",
    )
    ap.add_argument(
        "--per-query",
        type=int,
        default=12,
        help="Max model cards to inspect per search query (default: 12)",
    )
    ap.add_argument(
        "--sleep-seconds",
        type=float,
        default=0.25,
        help="Pause between model_info calls to reduce Hub pressure (default: 0.25)",
    )
    ap.add_argument(
        "--probe-trust-remote-code",
        action="store_true",
        help="For the first N qualifying repos, try to download tokenizer_config.json/config.json and detect truthy trust_remote_code",
    )
    ap.add_argument(
        "--max-probes",
        type=int,
        default=5,
        help="Cap trust_remote_code probes when --probe-trust-remote-code is set (default: 5)",
    )
    ap.add_argument(
        "--json-lines-out",
        type=Path,
        default=None,
        help="Append one JSON object per matching repo (newline-delimited)",
    )
    args = ap.parse_args(argv)

    max_bytes = int(args.max_mb * 1024 * 1024)
    queries = [q.strip() for q in str(args.queries).split(",") if q.strip()]
    if not queries:
        print("ERROR: no queries", file=sys.stderr)
        return 2

    api = HfApi()
    seen: set[str] = set()
    rows: list[dict[str, object]] = []
    probes_done = 0

    est = len(queries) * int(args.per_query)
    print(
        f"Searching Hub (metadata only) — queries={queries!r}, per_query={args.per_query}, "
        f"max_total_mb={args.max_mb:g} (~{est} list_models cards, then up to that many model_info calls; "
        f"can take several minutes).",
        file=sys.stderr,
    )

    for q in queries:
        try:
            it = api.list_models(search=q, limit=int(args.per_query))
        except Exception as e:
            print(f"WARNING: list_models({q!r}) failed: {e}", file=sys.stderr)
            continue
        for card in it:
            rid = str(getattr(card, "modelId", "") or "").strip()
            if not rid or rid in seen:
                continue
            seen.add(rid)
            time.sleep(float(args.sleep_seconds) * (0.5 + random.random()))
            try:
                info = api.model_info(rid, files_metadata=True)
            except Exception as e:
                print(f"SKIP model_info {rid!r}: {e}", file=sys.stderr)
                continue
            sibs = getattr(info, "siblings", None) or []
            total = 0
            unknown = 0
            for s in sibs:
                sz = getattr(s, "size", None)
                if sz is None:
                    unknown += 1
                    continue
                total += int(sz)
            if total <= 0:
                continue
            if total > max_bytes:
                continue
            mb = total / (1024 * 1024)
            trc_hit = False
            trc_detail = ""
            if args.probe_trust_remote_code and probes_done < int(args.max_probes):
                probes_done += 1
                time.sleep(float(args.sleep_seconds) * 2)
                trc_hit, trc_detail = _probe_remote_code(rid)

            row = {
                "repo_id": rid,
                "total_bytes": total,
                "total_mb": round(mb, 3),
                "files_counted": len(sibs),
                "files_unknown_size": unknown,
                "query": q,
                "trust_remote_code_probe_hit": trc_hit,
                "trust_remote_code_probe_detail": trc_detail,
            }
            rows.append(row)

            trc = f" **TRC?** {trc_detail}" if trc_hit else ""
            print(f"{rid}\t{mb:.3f} MiB summed\tfiles={len(sibs)}\tunknown_sizes={unknown}\tfrom_query={q!r}{trc}")

            if args.json_lines_out is not None:
                args.json_lines_out.parent.mkdir(parents=True, exist_ok=True)
                with args.json_lines_out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"matches": len(rows), "unique_seen": len(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
