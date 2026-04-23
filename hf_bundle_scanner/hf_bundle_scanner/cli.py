"""CLI: manifest, download, scan (bundle)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from hf_bundle_scanner import __version__
from hf_bundle_scanner.dispatch import scan_bundle
from hf_bundle_scanner.snapshot import build_manifest, snapshot_download, write_manifest


def _cmd_manifest(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    out = Path(args.out).resolve()
    write_manifest(root, out)
    return 0


def _cmd_download(args: argparse.Namespace) -> int:
    dest = Path(args.dest).resolve()
    snapshot_download(args.repo, args.revision, dest)
    return 0


def _cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    policy = Path(args.policy).resolve()
    out = Path(args.out).resolve()
    bundle = scan_bundle(
        root,
        policy,
        drivers=args.drivers,
        timeout=args.timeout,
        fail_on=args.fail_on,
        include_manifest=not args.no_manifest,
    )
    bundle.write_json(out)
    if args.print_summary:
        print(
            json.dumps(
                {
                    "aggregate_exit_code": bundle.aggregate_exit_code,
                    "file_count": len(bundle.file_scans),
                    "config_finding_count": len(bundle.config_findings),
                },
                indent=2,
            )
        )
    return int(bundle.aggregate_exit_code)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="scan-bundle",
        description="HF snapshot manifest, Hub download, bundle scan via model-admission.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    pm = sub.add_parser("manifest", help="Write SHA-256 manifest for a directory tree")
    pm.add_argument("--root", required=True, help="Snapshot root directory")
    pm.add_argument("--out", required=True, help="Output manifest JSON path")
    pm.set_defaults(func=_cmd_manifest)

    pd = sub.add_parser("download", help="Download a Hub snapshot (requires network)")
    pd.add_argument("--repo", required=True, help="Hugging Face repo id, e.g. org/name")
    pd.add_argument("--revision", default=None, help="Branch, tag, or commit hash")
    pd.add_argument("--dest", required=True, help="Destination directory")
    pd.set_defaults(func=_cmd_download)

    ps = sub.add_parser("scan", help="Run bundle scan (discovery + configlint + admit-model per file)")
    ps.add_argument("--root", required=True, help="Snapshot root directory")
    ps.add_argument("--policy", required=True, help="model-admission policy JSON")
    ps.add_argument("--out", required=True, help="Bundle report JSON path")
    ps.add_argument(
        "--drivers",
        default="",
        help="Comma-separated drivers for admit-model (default empty)",
    )
    ps.add_argument("--timeout", type=int, default=600, help="Per-file driver timeout seconds")
    ps.add_argument(
        "--fail-on",
        default="MEDIUM",
        help="Severity floor for admit-model (INFO, LOW, MEDIUM, HIGH, CRITICAL)",
    )
    ps.add_argument(
        "--no-manifest",
        action="store_true",
        help="Omit full file manifest from bundle report",
    )
    ps.add_argument(
        "--print-summary",
        action="store_true",
        help="Print a small JSON summary to stdout",
    )
    ps.set_defaults(func=_cmd_scan)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
