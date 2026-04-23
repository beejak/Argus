from __future__ import annotations

import argparse
import sys
from pathlib import Path

from model_admission import __version__
from model_admission.drivers import get_driver
from model_admission.ledger import append_ledger
from model_admission.policy import PolicyConfig, evaluate_policy, sha256_file
from model_admission.report import Finding, ScanReport, Severity
from model_admission.taxonomy import RiskCategory, make_rule_id


SEVERITY_ORDER = {
    Severity.INFO: 1,
    Severity.LOW: 2,
    Severity.MEDIUM: 3,
    Severity.HIGH: 4,
    Severity.CRITICAL: 5,
}


def _min_severity(name: str) -> Severity:
    key = name.strip().upper()
    for s in Severity:
        if s.value.upper() == key or s.name == key:
            return s
    raise argparse.ArgumentTypeError(f"unknown severity {name!r}")


def _any_finding_at_or_above(findings: list[Finding], minimum: Severity) -> bool:
    floor = SEVERITY_ORDER[minimum]
    for f in findings:
        if SEVERITY_ORDER.get(f.severity, 0) >= floor:
            return True
    return False


def cmd_scan(args: argparse.Namespace) -> int:
    artifact = Path(args.artifact).resolve()
    policy = PolicyConfig.load(Path(args.policy).resolve())
    policy_path = str(Path(args.policy).resolve())
    policy_hash = policy.content_hash()

    violations = evaluate_policy(artifact, policy)
    digest = sha256_file(artifact) if artifact.is_file() else ""

    driver_names = [d.strip().lower() for d in args.drivers.split(",") if d.strip()]
    all_findings: list[Finding] = []
    driver_errors: list[str] = []
    drivers_run: list[str] = []

    for dname in driver_names:
        try:
            driver = get_driver(dname)
        except KeyError as e:
            print(e, file=sys.stderr)
            return 4
        drivers_run.append(driver.name)
        findings, err = driver.scan(artifact, timeout_sec=args.timeout)
        if err:
            driver_errors.append(f"{driver.name}: {err}")
        all_findings.extend(findings)

    if violations:
        for v in reversed(violations):
            all_findings.insert(
                0,
                Finding(
                    driver="policy",
                    severity=Severity.HIGH,
                    title="Policy violation",
                    detail=v,
                    rule_id=make_rule_id("policy", "gate_violation"),
                    category=RiskCategory.PROVENANCE.value,
                ),
            )

    report = ScanReport(
        artifact_path=str(artifact),
        artifact_sha256=digest,
        policy_path=policy_path,
        drivers_run=drivers_run,
        findings=all_findings,
        driver_errors=driver_errors,
    )

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        report.write_json(Path(args.report))

    min_sev: Severity = args.fail_on

    if driver_errors:
        exit_code = 2
    elif violations or _any_finding_at_or_above(all_findings, min_sev):
        exit_code = 1
    else:
        exit_code = 0

    append_ledger(
        Path(args.ledger).resolve() if args.ledger else None,
        {
            "event": "model_admission_scan",
            "version": __version__,
            "artifact": str(artifact),
            "sha256": digest,
            "policy_hash": policy_hash,
            "drivers": drivers_run,
            "exit_code": exit_code,
            "violations": violations,
            "driver_errors": driver_errors,
            "findings_count": len(all_findings),
        },
    )

    return exit_code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="admit-model",
        description="Model admission gate: policy + ModelScan/ModelAudit drivers.",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("scan", help="Scan a single artifact")
    sp.add_argument("--artifact", required=True, help="Path to model file")
    sp.add_argument("--policy", required=True, help="JSON policy file")
    sp.add_argument("--report", default="", help="Write ScanReport JSON to this path")
    sp.add_argument(
        "--ledger",
        default="",
        help="Append JSONL audit line (or set MODEL_ADMISSION_LEDGER env)",
    )
    sp.add_argument(
        "--drivers",
        default="modelscan,modelaudit",
        help="Comma-separated drivers (default: modelscan,modelaudit)",
    )
    sp.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Per-driver subprocess timeout in seconds",
    )
    sp.add_argument(
        "--fail-on",
        default="MEDIUM",
        type=_min_severity,
        help="Minimum finding severity to fail (INFO, LOW, MEDIUM, HIGH, CRITICAL)",
    )
    sp.set_defaults(func=cmd_scan)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "scan":
        return int(args.func(args))
    parser.print_help()
    return 4
