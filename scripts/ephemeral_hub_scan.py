#!/usr/bin/env python3
"""Download a Hub snapshot to a temp dir, run bundle scan, write JSON, delete the tree.

This is for **manual / opt-in** demos (network + disk). It does **not** ship or execute
pickle exploits. Use ``--inject-demo-tokenizer-risk`` only to synthesize a **configlint**
signal (``trust_remote_code``) for teaching — not a supply-chain trojan.

**Interpreter:** run with the repo venv so ``huggingface_hub`` is importable, e.g.
``"/path/to/LLM Scanner/.venv/bin/python" scripts/ephemeral_hub_scan.py ...``
(plain ``python3`` on minimal systems may lack the dependency).

**Example repos (benign Hugging Face *test* weights — good for format / policy demos):**

- ``hf-internal-testing/tiny-random-BertModel`` — default; multi-format teaching snapshot.
- ``hf-internal-testing/tiny-random-GPT2Model`` — smaller alternative; still ships ``pytorch_model.bin``.
- ``hf-internal-testing/tiny-random-BartModel`` — richer ONNX surface + ``pytorch_model.bin``;
  pair with ``--inject-demo-tokenizer-risk`` to see **aggregate exit 1** from configlint
  without downloading known-malicious content.

**HTML:** after a successful scan, this script runs ``scripts/export_bundle_action_sheet.py``
with ``--bundle-json`` pointing at the written bundle JSON (unless ``--no-html``). Default
HTML path is the bundle ``--out`` path with a ``.html`` suffix.
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
        "--html-out",
        type=str,
        default=None,
        help="HTML briefing output path (default: same path as --out but with .html suffix)",
    )
    ap.add_argument(
        "--no-html",
        action="store_true",
        help="Skip HTML export after a successful scan",
    )
    ap.add_argument(
        "--inject-demo-tokenizer-risk",
        action="store_true",
        help="Write tokenizer_config.json with trust_remote_code=true to trigger configlint (demo only)",
    )
    args = ap.parse_args(argv)

    policy = Path(args.policy)
    if not policy.is_file():
        policy = root / args.policy
    if not policy.is_file():
        print(f"ERROR: policy not found: {args.policy}", file=sys.stderr)
        return 2
    policy = policy.resolve()

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
        # Run with package cwd so `python -m hf_bundle_scanner` resolves the editable install reliably.
        r = subprocess.run(cmd, cwd=str(root / "hf_bundle_scanner"), env=env, capture_output=True, text=True)
        if r.stdout:
            print(r.stdout, end="" if r.stdout.endswith("\n") else "\n")
        if r.stderr:
            print(r.stderr, file=sys.stderr, end="" if r.stderr.endswith("\n") else "\n")
        if r.returncode != 0:
            return int(r.returncode)

        if out.is_file():
            data = json.loads(out.read_text(encoding="utf-8"))
            summary = {
                "wrote": str(out),
                "aggregate_exit_code": data.get("aggregate_exit_code"),
                "schema": data.get("schema"),
            }
            if not bool(args.no_html):
                html_out = Path(args.html_out).resolve() if args.html_out else out.with_suffix(".html")
                html_out.parent.mkdir(parents=True, exist_ok=True)
                exp = [
                    str(py),
                    str(root / "scripts" / "export_bundle_action_sheet.py"),
                    "--repo-root",
                    str(root),
                    "--bundle-json",
                    str(out),
                    "--html-out",
                    str(html_out),
                ]
                r2 = subprocess.run(exp, cwd=str(root), env=env, capture_output=True, text=True)
                if r2.stdout:
                    print(r2.stdout, end="" if r2.stdout.endswith("\n") else "\n")
                if r2.stderr:
                    print(r2.stderr, file=sys.stderr, end="" if r2.stderr.endswith("\n") else "\n")
                if r2.returncode != 0:
                    return int(r2.returncode)
                summary["html"] = str(html_out)
            print(json.dumps(summary, indent=2))
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
