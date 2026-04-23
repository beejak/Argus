#!/usr/bin/env python3
"""Turn bundle_report.v2 JSON into human-oriented CSV + HTML (print → PDF in browser).

Also writes a leadership-oriented blast-radius Markdown brief (prod impact, scope).

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


def _suffix(rel: str) -> str:
    return Path(rel).suffix.lower()


def _blast_for_exec_summary(demo: Demo, data: dict[str, Any]) -> dict[str, str]:
    """Whole-bundle leadership framing for this demo."""
    hub = _hub_repo(data)
    agg = data.get("aggregate_exit_code")
    verdict = _ship_verdict(agg)
    cfg = [x for x in (data.get("config_findings") or []) if isinstance(x, dict)]
    has_trc = any(str(x.get("rule_id") or "") == "trust_remote_code_enabled" for x in cfg)

    if demo.demo_id == "01_baseline":
        return {
            "risk_rating": "LOW (static admission gate)",
            "prod_impact_if_shipped": (
                f"If `{hub}` reached production with the same loader posture as this scan, nothing "
                "in this **static** report blocks release: policy and empty driver lane raised no "
                "finding. That does **not** prove safety—only that this gate did not fire. Residual "
                "classes of prod risk still apply: prompt injection and toxic outputs, application "
                "data exfiltration, wrong revision or mirror substitution, and higher inherent risk "
                "for pickle-era formats such as `pytorch_model.bin` if an attacker could swap weights."
            ),
            "blast_radius": (
                "**Primary:** the serving/training fleet identity (cloud IAM, k8s service accounts) "
                "and any databases or APIs the app can reach while running this model. "
                "**Secondary:** customer trust, regulatory reporting if PII is processed, and SOC "
                "workload if behavior changes. **Not modeled here:** runtime guardrails, network "
                "egress policy, or human review of Hub revision history."
            ),
            "exec_one_liner": (
                f"Static gate {verdict} for this snapshot — leadership should still budget runtime "
                "AI risk and supply-chain controls outside this JSON."
            ),
        }

    if demo.demo_id == "02_demo_config_risk" or has_trc:
        return {
            "risk_rating": "CRITICAL (remote code execution path on load)",
            "prod_impact_if_shipped": (
                "If production loaders honor `trust_remote_code`, a malicious or compromised Hub "
                "revision (or dependency confusion) can execute **Python during model/tokenizer "
                "load**, before your application logic runs its usual checks. That is comparable to "
                "shipping an unreviewed install hook on the hot path: environment secrets, cloud "
                "metadata credentials, lateral movement to batch jobs, and silent persistence become "
                "plausible incident shapes."
            ),
            "blast_radius": (
                "**Typically:** the whole namespace or VM scale set running inference, shared "
                "images and caches, CI runners that materialize tokenizer files, and any secrets "
                "mounted into those workloads. **Regulatory / comms:** expands materially if the "
                "model touches regulated data — breach timelines and customer notification may "
                "enter scope even without proven exfiltration."
            ),
            "exec_one_liner": (
                f"Static gate {verdict} — treat as **undeclared RCE-class supply chain** on load "
                "until explicitly waived with hardened controls and owner sign-off."
            ),
        }

    if demo.demo_id == "03_strict_safetensors_only":
        return {
            "risk_rating": "HIGH (governance / policy breach; format risk)",
            "prod_impact_if_shipped": (
                "If teams bypass this gate and deploy anyway, production would contain **file types "
                "your org explicitly banned** (here: `.onnx`, `.bin`, `.h5`). That weakens audit "
                "answers (“safetensors-only”), increases operational surprise, and raises the "
                "likelihood of **unsafe deserialization** incidents if weights ever become "
                "attacker-controlled or accidentally swapped."
            ),
            "blast_radius": (
                "**Compliance & procurement:** SOC2 / ISO evidence gaps and vendor questionnaires. "
                "**Operations:** downstream systems that assumed “no pickle weights” may behave "
                "incorrectly or open incident bridges. **Security:** incident blast follows the "
                "inference footprint and any shared artifact store where the disallowed files land."
            ),
            "exec_one_liner": (
                f"Static gate {verdict} — leadership question is: **waive with recorded risk "
                "acceptance** or **convert/remove blocked artifacts** before prod."
            ),
        }

    return {
        "risk_rating": "REVIEW",
        "prod_impact_if_shipped": "See per-row signals; aggregate gate requires human triage.",
        "blast_radius": "Scoped to the workloads and data flows that would load this snapshot.",
        "exec_one_liner": f"Static gate {verdict} — triage config then per-file findings.",
    }


def _blast_for_config(rule_id: str) -> dict[str, str]:
    rid = (rule_id or "").strip()
    if rid == "trust_remote_code_enabled":
        return {
            "risk_rating": "CRITICAL",
            "prod_impact_if_shipped": (
                "Same as exec summary: trusted Hub Python may run at load time; secrets and lateral "
                "movement are in play if an adversary influences revision content or build caches."
            ),
            "blast_radius": (
                "Inference/training hosts, mounted secrets, shared registries, CI artifact caches; "
                "customer/regulator exposure if regulated data is processed."
            ),
            "exec_one_liner": (
                "`trust_remote_code` truthy — **stop-the-line** for prod until removed or formally "
                "accepted with compensating controls."
            ),
        }
    return {
        "risk_rating": "MEDIUM",
        "prod_impact_if_shipped": (
            "A configlint finding means static posture does not match your desired prod baseline; "
            "impact depends on the specific rule—treat as a release gate until reviewed."
        ),
        "blast_radius": "Model consumers and any automation that trusts “clean config” assumptions.",
        "exec_one_liner": "Config signal requires security + ML owner review before ship.",
    }


def _blast_for_finding(rule_id: str, relpath: str) -> dict[str, str]:
    rid = (rule_id or "").strip()
    suf = _suffix(relpath)
    if rid == "policy.gate_violation":
        return {
            "risk_rating": "HIGH",
            "prod_impact_if_shipped": (
                f"If `{relpath}` ships despite policy, you are **operating outside the signed "
                f"control baseline** for file types. For `{suf}` specifically, deserialization and "
                "tooling surprises are the common technical concern; the business concern is "
                "**audit failure** and **unplanned incident response** when reality diverges from "
                "what security told auditors."
            ),
            "blast_radius": (
                "Release pipeline integrity, downstream “safetensors-only” consumers, and the "
                "security/compliance interface (evidence packs, customer DPA answers)."
            ),
            "exec_one_liner": (
                f"Blocked artifact `{relpath}` — waive only with **named executive risk acceptance**."
            ),
        }
    return {
        "risk_rating": "MEDIUM",
        "prod_impact_if_shipped": "See finding detail; map to your org risk register.",
        "blast_radius": "Workloads that load this artifact path.",
        "exec_one_liner": "Non-policy finding — route to engineering + security triage.",
    }


def _blast_for_weight_clean(relpath: str) -> dict[str, str]:
    suf = _suffix(relpath)
    if suf == ".bin":
        return {
            "risk_rating": "MEDIUM (residual format risk)",
            "prod_impact_if_shipped": (
                "`pytorch_model.bin` is a **pickle deserialization surface** in many stacks. With "
                "**benign** test weights the practical incident rate is low, but with **swapped** "
                "or **attacker-supplied** weights it becomes a classic high-impact deserialization "
                "bug class. Static scan did not prove malicious content here."
            ),
            "blast_radius": (
                "The inference/training process that deserializes this file; expands if weights "
                "live on shared storage or multi-tenant caches."
            ),
            "exec_one_liner": (
                "No static finding — leadership should still ask whether **.bin** is acceptable in "
                "**your** prod threat model."
            ),
        }
    if suf in (".onnx", ".h5", ".hdf5"):
        return {
            "risk_rating": "LOW–MEDIUM (residual supply chain)",
            "prod_impact_if_shipped": (
                f"`{relpath}` passed this static gate; prod risk is mostly **integrity and supply "
                "chain** (wrong revision, poisoned mirror) plus whatever your runtime allows the "
                "framework to do with that format."
            ),
            "blast_radius": (
                "Serving fleet and adjacent services that trust this artifact hash and revision pin."
            ),
            "exec_one_liner": "No static blocker — confirm revision pinning and mirror policy.",
        }
    return {
        "risk_rating": "LOW",
        "prod_impact_if_shipped": "No static finding on this row; residual prod risk is operational.",
        "blast_radius": "Scoped to consumers of this artifact.",
        "exec_one_liner": "No static blocker on this file for the configured policy/drivers.",
    }


def iter_rows(demo: Demo, data: dict[str, Any]) -> Iterable[dict[str, str]]:
    hub = _hub_repo(data)
    agg = data.get("aggregate_exit_code")
    policy = str(data.get("policy_path") or "")
    policy_label = _policy_label(policy)
    verdict = _ship_verdict(agg)
    blast_exec = _blast_for_exec_summary(demo, data)

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
        **blast_exec,
    }

    for cf in data.get("config_findings") or []:
        if not isinstance(cf, dict):
            continue
        path = str(cf.get("path") or "")
        rule_id = str(cf.get("rule_id") or "")
        msg = str(cf.get("message") or "")
        meaning, nxt = _meaning_for_config(rule_id, msg)
        b = _blast_for_config(rule_id)
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
            **b,
        }

    for fs in data.get("file_scans") or []:
        if not isinstance(fs, dict):
            continue
        rel = str(fs.get("relpath") or "")
        ex = fs.get("exit_code")
        rep = fs.get("report") if isinstance(fs.get("report"), dict) else {}
        findings = rep.get("findings") if isinstance(rep, dict) else []
        if not findings:
            b = _blast_for_weight_clean(rel)
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
                **b,
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
            b = _blast_for_finding(rule_id, rel)
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
                **b,
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
    "risk_rating",
    "prod_impact_if_shipped",
    "blast_radius",
    "exec_one_liner",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


# Public default for “rendered HTML” deep links (Argus mirror). Override via env for forks.
_DEFAULT_HTML_RAW_BASE = (
    "https://raw.githubusercontent.com/beejak/Argus/main/docs/sample_reports/actionable"
)


def _html_table_lines(title: str, cols: list[str], row_dicts: list[dict[str, str]]) -> list[str]:
    """Pretty-printed table as separate lines (GitHub file view stays source-only; this helps humans)."""
    t = html.escape(title)
    lines: list[str] = [
        f"  <h2>{t}</h2>",
        "  <table>",
        "    <thead>",
        "      <tr>",
    ]
    for c in cols:
        lines.append(f"        <th>{html.escape(c)}</th>")
    lines.extend(
        [
            "      </tr>",
            "    </thead>",
            "    <tbody>",
        ]
    )
    for r in row_dicts:
        lines.append("      <tr>")
        for c in cols:
            lines.append(f"        <td>{html.escape(r.get(c, ''))}</td>")
        lines.append("      </tr>")
    lines.extend(["    </tbody>", "  </table>"])
    return lines


def write_html(path: Path, demos: list[Demo], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw_url = f"{_DEFAULT_HTML_RAW_BASE}/{path.name}"
    githack_url = raw_url.replace(
        "https://raw.githubusercontent.com/",
        "https://raw.githack.com/",
    )
    readme_url = (
        "https://github.com/beejak/Argus/blob/main/docs/sample_reports/actionable/README.md"
    )

    lines: list[str] = [
        "<!DOCTYPE html>",
        "<!--",
        "  GitHub’s repository *file view* always shows HTML as source code (no execution).",
        "  To see tables: open this file from a local checkout in a browser, or use the rendered",
        "  preview URL documented next to SCAN_BRIEFING.html in docs/sample_reports/actionable/README.md.",
        "-->",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1">',
        "  <title>Bundle scan — action sheet + blast radius</title>",
        "  <style>",
        "    body { font-family: system-ui, Segoe UI, Roboto, sans-serif; margin: 24px; color: #111; }",
        "    h1 { font-size: 1.35rem; }",
        "    h2 { font-size: 1.1rem; margin-top: 1.6rem; border-bottom: 1px solid #ccc; }",
        "    table { border-collapse: collapse; width: 100%; font-size: 0.82rem; }",
        "    th, td { border: 1px solid #ddd; padding: 8px; vertical-align: top; }",
        "    th { background: #f4f4f4; text-align: left; }",
        "    .muted { color: #555; font-size: 0.85rem; margin-top: 8px; }",
        "    .lead { font-size: 0.95rem; line-height: 1.45; }",
        "    .callout { border: 1px solid #c9daf8; background: #eef5ff; padding: 12px 14px; border-radius: 6px; }",
        "    code { font-size: 0.88em; }",
        "    @media print { body { margin: 12px; } a { color: #000; text-decoration: none; } }",
        "  </style>",
        "</head>",
        "<body>",
        "  <h1>Bundle scan — human briefing + blast radius</h1>",
        "  <p class=\"callout\">",
        "    <strong>Seeing raw HTML on github.com?</strong> That is expected — GitHub does not render ",
        "    HTML inside repos. Open this file from your machine (double-click after clone) or use a ",
        "    preview host that serves <code>text/html</code> with the raw file, e.g. ",
        f"    <a href=\"{html.escape(githack_url)}\">{html.escape(githack_url)}</a>. ",
        "    More options: ",
        f"    <a href=\"{html.escape(readme_url)}\">actionable/README.md</a>.",
        "  </p>",
        "  <p class=\"muted\">Generated from committed sample bundle JSON. ",
        "  For a PDF: use your browser <strong>Print → Save as PDF</strong> on this page.</p>",
        "  <p class=\"lead\">",
        "    <strong>For leadership:</strong> use the <em>Leadership blast radius</em> ",
        "    table first (one row per demo). <strong>Blast radius</strong> means who and what could be ",
        "    affected if this snapshot were deployed with today’s signals ignored — not a prediction ",
        "    that this test model is malicious.",
        "  </p>",
    ]

    exec_rows = [r for r in rows if r.get("row_kind") == "EXEC_SUMMARY"]
    lines.extend(
        _html_table_lines(
            "Leadership — blast radius by demo",
            [
                "demo_id",
                "demo_title",
                "risk_rating",
                "exec_one_liner",
                "prod_impact_if_shipped",
                "blast_radius",
            ],
            exec_rows,
        )
    )

    detail_cols = [
        "row_kind",
        "subject",
        "path_or_artifact",
        "scanner_signal",
        "human_meaning",
        "recommended_next_step",
        "severity",
        "exit_code",
        "risk_rating",
        "prod_impact_if_shipped",
        "blast_radius",
        "exec_one_liner",
    ]

    by_demo: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        by_demo.setdefault(r["demo_id"], []).append(r)

    for demo in demos:
        lines.extend(
            _html_table_lines(
                f"Detail — {demo.title} ({demo.demo_id})",
                detail_cols,
                by_demo.get(demo.demo_id, []),
            )
        )

    lines.extend(["</body>", "</html>"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_blast_radius_md(path: Path, demos: list[Demo], rows: list[dict[str, str]]) -> None:
    """Markdown brief for executives: prod impact + blast radius per issue class."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        "# Blast radius & leadership brief (sample Hub demos)",
        "",
        "This document is generated from the same three committed bundle JSON samples as "
        "[`UNIFIED_ACTION_SHEET.csv`](UNIFIED_ACTION_SHEET.csv). It answers: **if we ignored "
        "these static signals and deployed, what breaks — and who cares?**",
        "",
        "> **Scope:** static admission + configlint only. It does **not** cover prompt abuse, "
        "toxicity, full supply-chain pen tests, or runtime guardrails. Treat as **one control "
        "column** in a broader AI governance program.",
        "",
        "---",
        "",
    ]

    exec_by_id = {r["demo_id"]: r for r in rows if r.get("row_kind") == "EXEC_SUMMARY"}
    by_demo: dict[str, list[dict[str, str]]] = {}
    for r in rows:
        if r.get("row_kind") == "EXEC_SUMMARY":
            continue
        by_demo.setdefault(r["demo_id"], []).append(r)

    for demo in demos:
        er = exec_by_id.get(demo.demo_id, {})
        lines.extend(
            [
                f"## {demo.title}",
                "",
                f"- **Demo id:** `{demo.demo_id}`",
                f"- **Risk (bundle-level):** {er.get('risk_rating', '')}",
                f"- **Executive one-liner:** {er.get('exec_one_liner', '')}",
                "",
                "### If this snapshot reached production (ignoring the gate)",
                "",
                er.get("prod_impact_if_shipped", ""),
                "",
                "### Blast radius (who / what can be touched)",
                "",
                er.get("blast_radius", ""),
                "",
                "### All identified signals in this demo (counts)",
                "",
            ]
        )
        issues = by_demo.get(demo.demo_id, [])
        kinds: dict[str, int] = {}
        for x in issues:
            kinds[x.get("row_kind", "")] = kinds.get(x.get("row_kind", ""), 0) + 1
        cfg_n = kinds.get("CONFIG", 0)
        wf_n = kinds.get("WEIGHT_FILE", 0)
        fd_n = kinds.get("FINDING", 0)
        lines.append(
            f"- **Rows in detail sheet:** {len(issues)} "
            f"({cfg_n} config, {wf_n} clean weight rows, {fd_n} blocked/policy findings)"
        )
        for k, v in sorted(kinds.items()):
            lines.append(f"  - `{k}`: **{v}**")
        lines.append("")
        lines.append("| Kind | Subject / path | Risk | Leadership line |")
        lines.append("| ---- | -------------- | ---- | ----------------- |")
        for x in issues:
            kind = x.get("row_kind", "")
            subj = (x.get("path_or_artifact") or x.get("subject") or "").replace("|", "\\|")
            lines.append(
                f"| {kind} | {subj} | {x.get('risk_rating', '')} | "
                f"{(x.get('exec_one_liner') or '').replace('|', '\\|')} |"
            )
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## Cross-demo comparison (for steering committees)",
            "",
            "| Demo | Static gate | Main leadership story |",
            "| ---- | ----------- | ----------------------- |",
        ]
    )
    for demo in demos:
        er = exec_by_id.get(demo.demo_id, {})
        agg = er.get("exit_code", "")
        story = er.get("exec_one_liner", "").replace("|", "\\|")
        lines.append(f"| `{demo.demo_id}` | exit **{agg}** | {story} |")
    lines.append("")
    lines.append(
        "_Regenerate:_ `python3 scripts/export_bundle_action_sheet.py` "
        "or `make sample-action-sheets`."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


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
    ap.add_argument(
        "--md-out",
        type=Path,
        default=None,
        help="Output Markdown blast brief (default: actionable/BLAST_RADIUS_LEADERSHIP.md)",
    )
    args = ap.parse_args()
    root: Path = args.repo_root.resolve()
    csv_out = (args.csv_out or (root / "docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv")).resolve()
    html_out = (args.html_out or (root / "docs/sample_reports/actionable/SCAN_BRIEFING.html")).resolve()
    md_out = (args.md_out or (root / "docs/sample_reports/actionable/BLAST_RADIUS_LEADERSHIP.md")).resolve()

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
    write_blast_radius_md(md_out, demos, rows)
    print(
        json.dumps(
            {"csv": str(csv_out), "html": str(html_out), "md": str(md_out), "rows": len(rows)},
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
