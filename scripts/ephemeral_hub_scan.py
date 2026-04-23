#!/usr/bin/env python3
"""Download a Hub snapshot to a temp dir, run bundle scan, write JSON, delete the tree.

This is for **manual / opt-in** demos (network + disk). It does **not** ship or execute
pickle exploits. Use ``--inject-demo-tokenizer-risk`` only to synthesize a **configlint**
signal (``trust_remote_code``) for teaching — not a supply-chain trojan.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    root = _repo_root()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo",
        default="hf-internal-testing/tiny-random-BertModel",
        help="Hugging Face repo id to snapshot-download (default: tiny internal test model)",
    )
    ap.add_argument("--revision", default=None, help="Optional revision (branch / tag / commit)")
    ap.add_argument(
        "--policy",
        default="hf_bundle_scanner/tests/fixtures/policy.permissive.json",
        help="Policy JSON path relative to repo root unless absolute",
    )
    ap.add_argument("--out", required=True, help="Output bundle report JSON path")
    ap.add_argument(
        "--inject-demo-tokenizer-risk",
        action="store_true",
        help="Write tokenizer_config.json with trust_remote_code=true to trigger configlint (demo only)",
    )
    args = ap.parse_args(argv)

    policy = Path(args.policy)
    if not policy.is_file():
        policy = (root / args.policy).resolve()
    if not policy.is_file():
        print(f"ERROR: policy not found: {args.policy}", file=sys.stderr)
        return 2

    out = Path(args.out).resolve()
    py = os.environ.get("HF_BUNDLE_PYTHON") or sys.executable

    print(
        "Ephemeral Hub scan: snapshot will be deleted after the report is written.\n"
        "This script does not download weaponized artifacts; optional inject flag is JSON-only.",
        file=sys.stderr,
    )

    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("ERROR: install huggingface_hub (e.g. make install / hf_bundle_scanner deps)", file=sys.stderr)
        return 2

    tmp = tempfile.mkdtemp(prefix="hf-ephemeral-")
    try:
        import inspect

        kwargs: dict[str, object] = {
            "repo_id": args.repo,
            "revision": args.revision,
            "local_dir": tmp,
        }
        sig = inspect.signature(snapshot_download)
        if "local_dir_use_symlinks" in sig.parameters:
            kwargs["local_dir_use_symlinks"] = False
        snapshot_download(**kwargs)

        if args.inject_demo_tokenizer_risk:
            p = Path(tmp) / "tokenizer_config.json"
            p.write_text(
                json.dumps(
                    {
                        "trust_remote_code": True,
                        "_demo": "injected by scripts/ephemeral_hub_scan.py for configlint teaching only",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

        cmd = [
            str(py),
            "-m",
            "hf_bundle_scanner",
            "scan",
            "--root",
            tmp,
            "--policy",
            str(policy),
            "--out",
            str(out),
            "--drivers",
            "",
            "--print-summary",
            "--hub-repo",
            args.repo,
        ]
        if args.revision:
            cmd.extend(["--hub-revision", str(args.revision)])

        env = {**os.environ, "HF_BUNDLE_PYTHON": str(py)}
        r = subprocess.run(cmd, cwd=str(root), env=env, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout, end="" if r.stdout.endswith("\n") else "\n")
        if r.stderr:
            print(r.stderr, file=sys.stderr, end="" if r.stderr.endswith("\n") else "\n")
        if r.returncode != 0:
            return int(r.returncode)

        if out.is_file():
            data = json.loads(out.read_text(encoding="utf-8"))
            print(
                json.dumps(
                    {
                        "wrote": str(out),
                        "aggregate_exit_code": data.get("aggregate_exit_code"),
                        "schema": data.get("schema"),
                    },
                    indent=2,
                )
            )
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
