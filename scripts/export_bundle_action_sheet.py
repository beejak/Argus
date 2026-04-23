#!/usr/bin/env python3
"""Turn bundle_report.v2 JSON into human-oriented CSV + HTML (print → PDF in browser).

No third-party deps. Intended for committed samples under docs/sample_reports/actionable/.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Demo:
    demo_id: str
    title: str
    json_path: Path


def _hub_repo(data: dict[str, Any]) -> str:
    prov = data.get("provenance") or {}
    hub = prov.get("hub") or {}
    return str(hub.get("repo_id") or "(unknown hub)")


def _meaning_for_finding(rule_id: str | None, detail: str, title: str) -> tuple[str, str]:
    rid = (rule_id or "").strip()
    if rid == "policy.gate_violation":
        return (
            "Your admission policy rejected this file (extension, size, or hash allow-list).",
            "If this format is intentional, update policy with an explicit exception and record "
            "why the risk is accepted; otherwise convert weights (e.g. safetensors) or drop the file.",
        )
    if rid == "trust_remote_code_enabled":
        return (
            "Tokenizer / loader config enables remote code execution paths in typical HF stacks.",
            "Remove trust_remote_code, pin a forked tokenizer, or gate loading behind manual review "
            "and sandboxed CI — do not enable silently in production.",
        )
    if "auto_map" in rid.lower():
        return (
            "Custom class auto-mapping can deserialize into user-controlled Python types.",
            "Replace with explicit trusted classes or disable auto_map; review model card + code.",
        )
    return (
        f"Scanner reported: {title or rid or 'finding'}",
        "Open the linked bundle JSON for raw fields; map severity to your org's risk register.",
    )


def _meaning_for_config(rule_id: str | None, message: str) -> tuple[str, str]:
    rid = (rule_id or "").strip()
    if rid == "trust_remote_code_enabled":
        return (
            "Configlint: trust_remote_code is set truthy — loading may execute Hub-supplied Python.",
            "Treat like a code dependency change: review, pin revision, and require explicit approval.",
        )
    return (
        f"Configlint rule {rid or 'unknown'} fired.",
        message or "See bundle JSON config_findings for the exact path and text.",
    )


def _ship_verdict(agg: Any) -> str:
    try:
        code = int(agg)
    except (TypeError, ValueError):
        return "REVIEW"
    if code == 0:
        return "SHIP_OK_ON_STATIC_GATE"
    if code == 1:
        return "HOLD_REVIEW_POLICY_OR_CONFIG"
    if code == 2:
        return "HOLD_TOOLING_DRIVER"
    if code == 4:
        return "HOLD_USAGE_CLI"
    return "REVIEW"


def _policy_label(policy_path: str) -> str:
    p = policy_path.strip()
    if not p:
        return "(no policy_path in report)"
    name = Path(p).name
    if name == p:
        return name
    return f"{name} (fixture in repo)"


def iter_rows(demo: Demo, data: dict[str, Any]) -> Iterable[dict[str, str]]:
    hub = _hub_repo(data)
    agg = data.get("aggregate_exit_code")
    policy = str(data.get("policy_path") or "")
    policy_label = _policy_label(policy)
    verdict = _ship_verdict(agg)

    yield {
        "demo_id": demo.demo_id,
        "demo_title": demo.title,
        "row_kind": "EXEC_SUMMARY",
        "subject": "(entire bundle)",
        "path_or_artifact": "",
        "scanner_signal": f"aggregate_exit_code={agg}; schema={data.get('schema')}",
        "human_meaning": (
            f"Hub snapshot {hub} scanned with policy {policy_label}. "
            f"Verdict for CI-style static gate: {verdict}."
        ),
        "recommended_next_step": (
            "If HOLD: triage config_findings first, then per-file findings. "
            "If SHIP: still verify provenance, revision pin, and runtime controls outside this scanner."
        ),
        "severity": "",
        "exit_code": str(agg) if agg is not None else "",
    }

    for cf in data.get("config_findings") or []:
        if not isinstance(cf, dict):
            continue
        path = str(cf.get("path") or "")
        rule_id = str(cf.get("rule_id") or "")
        msg = str(cf.get("message") or "")
        meaning, nxt = _meaning_for_config(rule_id, msg)
        yield {
            "demo_id": demo.demo_id,
            "demo_title": demo.title,
            "row_kind": "CONFIG",
            "subject": "tokenizer / loader config",
            "path_or_artifact": path,
            "scanner_signal": f"{rule_id}: {msg}",
            "human_meaning": meaning,
            "recommended_next_step": nxt,
            "severity": "HIGH" if "trust_remote" in rule_id else "MEDIUM",
            "exit_code": str(agg) if agg is not None else "",
        }

    for fs in data.get("file_scans") or []:
        if not isinstance(fs, dict):
            continue
        rel = str(fs.get("relpath") or "")
        ex = fs.get("exit_code")
        rep = fs.get("report") if isinstance(fs.get("report"), dict) else {}
        findings = rep.get("findings") if isinstance(rep, dict) else []
        if not findings:
            yield {
                "demo_id": demo.demo_id,
                "demo_title": demo.title,
                "row_kind": "WEIGHT_FILE",
                "subject": "weight-like artifact gate",
                "path_or_artifact": rel,
                "scanner_signal": f"exit_code={ex}; findings=0",
                "human_meaning": (
                    "This file was scanned; policy + configured drivers did not raise a finding "
                    "(for this demo, drivers are empty)."
                ),
                "recommended_next_step": (
                    "Still treat formats like .bin as higher deserialization risk in real threat models."
                ),
                "severity": "OK",
                "exit_code": str(ex) if ex is not None else "",
            }
            continue
        for f in findings:
            if not isinstance(f, dict):
                continue
            title = str(f.get("title") or "")
            detail = str(f.get("detail") or "")
            sev = str(f.get("severity") or "").strip().upper()
            rule_id = str(f.get("rule_id") or "")
            meaning, nxt = _meaning_for_finding(rule_id, detail, title)
            yield {
                "demo_id": demo.demo_id,
                "demo_title": demo.title,
                "row_kind": "FINDING",
                "subject": "weight-like artifact gate",
                "path_or_artifact": rel,
                "scanner_signal": f"{title} — {detail}".strip(" —"),
                "human_meaning": meaning,
                "recommended_next_step": nxt,
                "severity": sev,
                "exit_code": str(ex) if ex is not None else "",
            }


FIELDNAMES = [
    "demo_id",
    "demo_title",
    "row_kind",
    "subject",
    "path_or_artifact",
    "scanner_signal",
    "human_meaning",
    "recommended_next_step",
    "severity",
    "exit_code",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def write_html(path: Path, demos: list[Demo], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    parts: list[str] = []
    parts.append("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'>")
    parts.append(
        "<title>Bundle scan — action sheet</title>"
        "<style>"
        "body{font-family:system-ui,Segoe UI,Roboto,sans-serif;margin:24px;color:#111;}"
        "h1{font-size:1.35rem;} h2{font-size:1.1rem;margin-top:1.6rem;border-bottom:1px solid #ccc;}"
        "table{border-collapse:collapse;width:100%;font-size:0.88rem;}"
        "th,td{border:1px solid #ddd;padding:8px;vertical-align:top;}"
        "th{background:#f4f4f4;text-align:left;}"
        ".muted{color:#555;font-size:0.85rem;margin-top:8px;}"
        "@media print{body{margin:12px;} a{color:#000;text-decoration:none;}}"
        "</style></head><body>"
    )
    parts.append("<h1>Bundle scan — human briefing</h1>")
    parts.append(
        "<p class='muted'>Generated from committed sample bundle JSON. "
        "For a PDF: use your browser <strong>Print → Save as PDF</strong> on this page.</p>"
    )
    parts.append("<p><strong>How to read this:</strong> each <em>demo</em> is the same tiny Hub test "
                 "snapshot with a different policy or a small injected config flag. "
                 "Rows are ordered: executive summary → config issues → per-file gate.</p>")

    by_demo: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by_demo.setdefault(r["demo_id"], []).append(r)

    for demo in demos:
        parts.append(f"<h2>{html.escape(demo.title)} <span class='muted'>({html.escape(demo.demo_id)})</span></h2>")
        parts.append("<table><thead><tr>")
        for col in [
            "row_kind",
            "subject",
            "path_or_artifact",
            "scanner_signal",
            "human_meaning",
            "recommended_next_step",
            "severity",
            "exit_code",
        ]:
            parts.append(f"<th>{html.escape(col)}</th>")
        parts.append("</tr></thead><tbody>")
        for r in by_demo.get(demo.demo_id, []):
            parts.append("<tr>")
            for col in [
                "row_kind",
                "subject",
                "path_or_artifact",
                "scanner_signal",
                "human_meaning",
                "recommended_next_step",
                "severity",
                "exit_code",
            ]:
                parts.append(f"<td>{html.escape(r.get(col, ''))}</td>")
            parts.append("</tr>")
        parts.append("</tbody></table>")

    parts.append("</body></html>")
    path.write_text("".join(parts), encoding="utf-8", newline="\n")


def default_demos(root: Path) -> list[Demo]:
    base = root / "docs" / "sample_reports"
    return [
        Demo(
            "01_baseline",
            "Baseline — permissive policy, no injected config risk",
            base / "live_hub_tiny_bert_bundle_report.json",
        ),
        Demo(
            "02_demo_config_risk",
            "Same snapshot — demo tokenizer_config (trust_remote_code)",
            base / "live_hub_tiny_bert_bundle_report_with_demo_risk.json",
        ),
        Demo(
            "03_strict_safetensors_only",
            "Same snapshot — safetensors-only policy (reject .bin/.onnx/.h5)",
            base / "live_hub_tiny_bert_bundle_report_strict_safetensors_policy.json",
        ),
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root (default: parent of scripts/)",
    )
    ap.add_argument(
        "--csv-out",
        type=Path,
        default=None,
        help="Output CSV path (default: docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv)",
    )
    ap.add_argument(
        "--html-out",
        type=Path,
        default=None,
        help="Output HTML path (default: docs/sample_reports/actionable/SCAN_BRIEFING.html)",
    )
    args = ap.parse_args()
    root: Path = args.repo_root.resolve()
    csv_out = (args.csv_out or (root / "docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv")).resolve()
    html_out = (args.html_out or (root / "docs/sample_reports/actionable/SCAN_BRIEFING.html")).resolve()

    demos = default_demos(root)
    rows: list[dict[str, str]] = []
    for d in demos:
        if not d.json_path.is_file():
            print(f"ERROR: missing {d.json_path}", file=sys.stderr)
            return 2
        data = json.loads(d.json_path.read_text(encoding="utf-8"))
        rows.extend(iter_rows(d, data))

    write_csv(csv_out, rows)
    write_html(html_out, demos, rows)
    print(json.dumps({"csv": str(csv_out), "html": str(html_out), "rows": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
