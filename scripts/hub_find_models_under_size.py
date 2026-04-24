#!/usr/bin/env python3
"""Search Hugging Face Hub for **model** repos whose **committed file sizes** sum under a limit.

Uses ``HfApi.list_models`` (text search) + ``HfApi.model_info(..., files_metadata=True)`` to sum
``sibling.size`` bytes. This is a **heuristic** for “small enough to download for a lab drill” —
LFS pointer quirks and omitted metadata can make totals wrong; always verify before large pulls.

Network required. Be polite: small sleeps between ``model_info`` calls.

Example::

    ./.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 12

Optional: probe a few repos with **configlint** (downloads small JSON only)::

    ./.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 8 \\
        --probe-configlint --max-probes 5
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Callable

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

_LINT_CONFIG_FILE: Callable[[Path], list[Any]] | None = None


def _lint_config_file() -> Callable[[Path], list[Any]]:
    """Resolve hf_bundle_scanner.configlint without requiring cwd; prefers editable install."""
    global _LINT_CONFIG_FILE
    if _LINT_CONFIG_FILE is not None:
        return _LINT_CONFIG_FILE
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "hf_bundle_scanner"
    sp = str(src)
    if sp not in sys.path:
        sys.path.insert(0, sp)
    from hf_bundle_scanner.configlint import lint_config_file as fn  # noqa: PLC0415

    _LINT_CONFIG_FILE = fn
    return _LINT_CONFIG_FILE


def _finding_to_dict(f: Any) -> dict[str, str]:
    to_dict = getattr(f, "to_dict", None)
    if callable(to_dict):
        d = to_dict()
        if isinstance(d, dict):
            return {str(k): str(v) for k, v in d.items()}
    rid = str(getattr(f, "rule_id", "") or "")
    msg = str(getattr(f, "message", "") or "")
    rel = str(getattr(f, "path", "") or "")
    return {"path": rel, "rule_id": rid, "message": msg}


def _probe_configlint(repo_id: str) -> tuple[bool, str, list[dict[str, str]], bool, str]:
    """Return (any_hit, detail, findings_json, trc_hit, trc_detail)."""
    findings_out: list[dict[str, str]] = []
    lint = _lint_config_file()
    with tempfile.TemporaryDirectory(prefix="hf-probe-") as td:
        root = Path(td)
        for fname in ("tokenizer_config.json", "config.json"):
            try:
                p = hf_hub_download(
                    repo_id,
                    filename=fname,
                    local_dir=str(root),
                )
                for f in lint(Path(p)):
                    d = _finding_to_dict(f)
                    d["file"] = fname
                    findings_out.append(d)
            except Exception:
                continue
    if not findings_out:
        return False, "", [], False, ""

    parts: list[str] = []
    for d in findings_out:
        rid = d.get("rule_id", "")
        parts.append(f"{d.get('file')}: {rid}")
    detail = "; ".join(parts[:12])
    if len(parts) > 12:
        detail += f" … (+{len(parts) - 12} more)"

    trc_msgs: list[str] = []
    for d in findings_out:
        if d.get("rule_id") == "trust_remote_code_enabled":
            trc_msgs.append(f"{d.get('file')}: {d.get('message', '')}".strip())
    trc_hit = bool(trc_msgs)
    trc_detail = "; ".join(trc_msgs[:4])
    if len(trc_msgs) > 4:
        trc_detail += f" … (+{len(trc_msgs) - 4} more)"

    return True, detail, findings_out, trc_hit, trc_detail


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
        "--probe-configlint",
        action="store_true",
        help=(
            "For the first N qualifying repos, download tokenizer_config.json/config.json and run "
            "hf_bundle_scanner.configlint (RCE-adjacent + supply-chain + hygiene signals)"
        ),
    )
    ap.add_argument(
        "--probe-trust-remote-code",
        action="store_true",
        help="Deprecated alias for --probe-configlint (same downloads; broader rule coverage)",
    )
    ap.add_argument(
        "--max-probes",
        type=int,
        default=5,
        help="Cap configlint probes when --probe-configlint is set (default: 5)",
    )
    ap.add_argument(
        "--json-lines-out",
        type=Path,
        default=None,
        help="Append one JSON object per matching repo (newline-delimited)",
    )
    args = ap.parse_args(argv)
    if bool(getattr(args, "probe_trust_remote_code", False)):
        args.probe_configlint = True

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
            cl_hit = False
            cl_detail = ""
            cl_findings: list[dict[str, str]] = []
            trc_hit = False
            trc_detail = ""
            if args.probe_configlint and probes_done < int(args.max_probes):
                probes_done += 1
                time.sleep(float(args.sleep_seconds) * 2)
                cl_hit, cl_detail, cl_findings, trc_hit, trc_detail = _probe_configlint(rid)

            row = {
                "repo_id": rid,
                "total_bytes": total,
                "total_mb": round(mb, 3),
                "files_counted": len(sibs),
                "files_unknown_size": unknown,
                "query": q,
                "configlint_probe_hit": cl_hit,
                "configlint_probe_detail": cl_detail,
                "configlint_probe_findings": cl_findings,
                "trust_remote_code_probe_hit": trc_hit,
                "trust_remote_code_probe_detail": trc_detail,
            }
            rows.append(row)

            extra = ""
            if cl_hit:
                extra = f" **CONFIGLINT** {cl_detail}"
            print(f"{rid}\t{mb:.3f} MiB summed\tfiles={len(sibs)}\tunknown_sizes={unknown}\tfrom_query={q!r}{extra}")

            if args.json_lines_out is not None:
                args.json_lines_out.parent.mkdir(parents=True, exist_ok=True)
                with args.json_lines_out.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(json.dumps({"matches": len(rows), "unique_seen": len(seen)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
