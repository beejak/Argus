# Program Status Snapshot

Last updated: 2026-04-26

This document is the high-level operational view for the LLM Scanner program:
- what exists now,
- what is stable for CI/CD,
- what is still controlled/experimental,
- and what comes next.

## Architecture (current)

```text
                  +-----------------------------------+
                  | orchestrator runner               |
                  | scripts/run_orchestrator_job.py   |
                  +----------------+------------------+
                                   |
      +----------------------------+-----------------------------+
      |                                                          |
+-----v----------------+                              +----------v------------+
| scan_bundle          |                              | dynamic_probe         |
| python -m hf_bundle..|                              | scripts/run_dynamic.. |
| static bundle lane   |                              | opt-in dynamic lane   |
+-----+----------------+                              +----------+------------+
      |                                                          |
      | optional fan-out                                          |
+-----v----------------+                                          |
| admit_model*         |                                          |
| python -m model_adm..|                                          |
| per-artifact checks  |                                          |
+----------+-----------+                                          |
           +------------------------+-----------------------------+
                                    |
                           +--------v---------+
                           | aggregate         |
                           | envelope v2 + rc  |
                           +--------+---------+
                                    |
                           +--------v---------+
                           | JSON artifacts    |
                           | bundle/admit/dyn  |
                           +-------------------+
```

## Module responsibilities

| Module | Responsibility | Maturity |
| --- | --- | --- |
| `model-admission/` | Per-artifact policy gate + optional driver scans | Stable |
| `hf_bundle_scanner/` | Snapshot-level scan, configlint, aggregation, bundle report v2 | Stable |
| `orchestrator_job` + `run_orchestrator_job.py` | Job graph validation/execution + envelope | Stable baseline, expanding |
| `run_dynamic_probe.py` + `dynamic_probe_report.py` | Opt-in dynamic contract and controls | Controlled, still evolving |
| `Makefile` + `run_tests_for_agent.py` | Deterministic local/CI verification harness | Stable |

## Phase matrix

| Phase | Status | Delivered so far |
| --- | --- | --- |
| 0 Foundations | Done | taxonomy + OWASP mapping + `rule_id` structure |
| 1 Provenance | Done | `bundle_report.v2` provenance fields |
| 2 Static drivers | Done (starter) | ModelScan/ModelAudit integration path + sample report flow |
| 3 Configlint OSS | Done | expanded high-signal config/loader checks |
| 4 Orchestrator scope | In progress (strong) | envelope v2, UUIDs, `admit_model` fan-out, optional provenance echo |
| 5 Dynamic staging | In progress | dynamic report contract, budgets, secrets names, controlled execution modes |
| 6 Supply-chain extras | Planned | deeper license/secrets/dependency/SBOM appendices |
| 7 Runtime guards | Planned | guard adapter integration guidance/workflow |
| 8 Observability | Planned | scanner version/correlation/event normalization for audit pipelines |

## Production-ready now vs controlled/experimental

### Production-ready now (practical CI lane)
- Static admission + bundle gating
- Deterministic tests/lint/agent-verify harness
- Orchestrator JSON jobs with reproducible envelopes
- Optional `admit_model` fan-out with explicit job mapping

### Controlled/experimental (opt-in lane)
- Dynamic probe depth beyond CLI self-checks is intentionally constrained
- Dynamic lane requires explicit enablement (`LLM_SCANNER_DYNAMIC_PROBE=1`) and budget/secret controls
- Optional **`.venv-garak/`** is used for live Makefile targets so the main CI venv stays lean (not committed)
- YAML orchestrator job format not shipped yet

## Current capabilities vs planned

| Area | Current | Planned next |
| --- | --- | --- |
| Dynamic execution | `preflight`, `selfcheck`, and controlled `execute_once` (bounded subprocess) | richer probe profiles, policy-governed execution depth |
| Job format | JSON schema v1 | YAML surface (with same strict validation intent) |
| Correlation | envelope + optional bundle provenance echo + **paired UTC/IST report timestamps** on JSON artifacts | stronger event lineage for SIEM/audit |
| Pillar 8/9 readiness | taxonomy + roadmap + placeholders | concrete app-eval and runtime-guard adapters/workflows |

## Practical posture (kept intentionally)

Two-lane model:
1. **Gate lane (default CI):** deterministic, fast, release-focused.
2. **Assessment lane (opt-in):** dynamic/heavier analysis, policy-gated.

This prevents overengineering while preserving a path to deeper enterprise coverage.

## Near-term next actions

1. Phase 5 depth: expand controlled real probe execution profiles.
2. Phase 4 format: YAML job surface (if needed) without weakening validation.
3. Phase 8 prep: normalized observability/audit event schema.
