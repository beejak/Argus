# LLM Scanner — documentation hub

This page is the **canonical map** of project documentation: who should read what, which **contracts** are stable, and how we keep prose aligned with code.

**Repository layout:** monorepo with [`model-admission/`](../model-admission/README.md) (per-artifact gate), [`hf_bundle_scanner/`](../hf_bundle_scanner/README.md) (bundle scan + orchestrator primitives), root [`Makefile`](../Makefile), and [`scripts/`](../scripts/) (orchestrator runner, dynamic probe, Hub helpers, exports).

---

## How to use this hub

| If you are… | Start here | Then |
| ----------- | ---------- | ---- |
| **New to the repo** | [README.md](../README.md) (overview + quick start) | [PROGRAM_STATUS_SNAPSHOT.md](PROGRAM_STATUS_SNAPSHOT.md), [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) |
| **Implementing or reviewing code** | [AGENTS.md](../AGENTS.md) | [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md), package READMEs, [adr/0001-bundle-scanner-vs-orchestrator-scope.md](adr/0001-bundle-scanner-vs-orchestrator-scope.md) |
| **Running CI / agents** | [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md), [`.agent/README.md`](../.agent/README.md) | `make agent-verify` → `.agent/pytest-last.log` |
| **Risk / leadership / procurement** | [sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md](sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md) | [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md), actionable CSV/HTML in [sample_reports/actionable/](sample_reports/actionable/) |
| **Operating Hermes / MCP** | [HERMES_AGENTS.md](HERMES_AGENTS.md) | [hf_bundle_scanner/docs/hermes-mcp.md](../hf_bundle_scanner/docs/hermes-mcp.md) |
| **Dynamic / Garak lane (phase 5)** | [PHASE5_DYNAMIC_PROBES.md](PHASE5_DYNAMIC_PROBES.md) | [scripts/run_dynamic_probe.py](../scripts/run_dynamic_probe.py), [hf_bundle_scanner/dynamic_probe_report.py](../hf_bundle_scanner/hf_bundle_scanner/dynamic_probe_report.py) |

---

## Stable machine-readable contracts

These are the **schemas and fields** downstream tools (CI, SIEM, orchestrators) should key off. When any of them change, treat it as a **versioned contract** change: update tests, this table, and the root README in the same change when possible.

| Artifact | Schema id / location | Purpose |
| -------- | --------------------- | -------- |
| **Bundle report** | `hf_bundle_scanner.bundle_report.v2` — emitted by `scan-bundle scan --out` | Per-file admission, configlint, manifest, aggregate exit, **provenance**. |
| **Admit-model report** | JSON from `admit-model scan --report` (shape documented in model-admission README) | Single-artifact findings + driver errors. |
| **Dynamic probe report** | `llm_scanner.dynamic_probe_report.v1` — [dynamic_probe_report.py](../hf_bundle_scanner/hf_bundle_scanner/dynamic_probe_report.py) | Opt-in Garak lane: status, exit_code, execution metadata, **no secret values**. |
| **Orchestrator job** | `llm_scanner.orchestrator_job.v1` — [orchestrator_job.py](../hf_bundle_scanner/hf_bundle_scanner/orchestrator_job.py) | Declarative DAG: `scan_bundle`, optional `admit_model` fan-out, optional `dynamic_probe`, `aggregate`. |
| **Orchestrator envelope** | `llm_scanner.orchestrator_envelope.v2` — written by `run_orchestrator_job.py run` | Per-step exit codes, UTC **Z** timestamps, `artifact_uri` for bundle / admit / dynamic outputs. |

### Report generation timestamps (JSON)

Bundle, admit-model, and dynamic-probe JSON reports include:

- **`report_generated_at_utc`** — RFC 3339 UTC with **`Z`** suffix (second precision).
- **`report_generated_at_ist`** — same instant in **Asia/Kolkata** (`+05:30`), for human parity with sample HTML headers.

**Semantics:** timestamps are set when the scan **finishes producing** that report object (bundle dispatch completion, admit CLI assembly, dynamic probe emission), not on incidental re-reads of the dataclass. Orchestrator post-processing that rewrites bundle JSON (e.g. provenance echo) does **not** roll the report clock forward.

**HTML / CSV / leadership MD:** [`scripts/export_bundle_action_sheet.py`](../scripts/export_bundle_action_sheet.py) prefers **`report_generated_at_ist`** from the bundle JSON when present (so re-exporting a committed bundle aligns the briefing header with the scan). If those fields are absent (older samples), the exporter falls back to **export-time** IST. Reopening a previously written HTML file still shows whatever stamp was baked in at generation.

Helpers live in:

- [`hf_bundle_scanner/timestamps.py`](../hf_bundle_scanner/hf_bundle_scanner/timestamps.py)
- [`model-admission/model_admission/timestamps.py`](../model-admission/model_admission/timestamps.py)

---

## Phase map (where to read detail)

| Phase | Topic | Primary doc |
| ----- | ----- | ----------- |
| 0 | Taxonomy, OWASP mapping, `rule_id` | [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md) |
| 1 | Provenance on bundle v2 | [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md), [hf_bundle_scanner/README.md](../hf_bundle_scanner/README.md) |
| 2 | Static drivers, configlint, samples | README, [hf_bundle_scanner/README.md](../hf_bundle_scanner/README.md), [policy/](policy/) |
| 3 | Org policy templates | [policy/README.md](policy/README.md), roadmap |
| 4 | Orchestrator job + envelope | [adr/0001-bundle-scanner-vs-orchestrator-scope.md](adr/0001-bundle-scanner-vs-orchestrator-scope.md), [scripts/run_orchestrator_job.py](../scripts/run_orchestrator_job.py) |
| 5 | Dynamic probe (opt-in Garak) | [PHASE5_DYNAMIC_PROBES.md](PHASE5_DYNAMIC_PROBES.md) |
| 6–8 | Supply chain, runtime guards, observability | [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) |

---

## Operational commands (summary)

Full tables: [README.md § Common Makefile targets](../README.md#common-makefile-targets), [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md).

| Command | Use when |
| ------- | -------- |
| `make install` | First-time or fresh clone (creates `.venv/`, editable installs). |
| `make docs-map` | Print path to this file (`docs/DOCUMENTATION.md`). |
| `make agent-verify` | **Authoritative** local/CI parity: both packages’ pytest, ruff, orchestrator `validate`, dynamic probe stub. |
| `make orchestrator-validate` | Job JSON only (no subprocess scans). |
| `make dynamic-probe-stub` | Write `.agent/dynamic_probe_last.json` with default **disabled** probe (no `LLM_SCANNER_DYNAMIC_PROBE`). |
| `make dynamic-probe-live-preflight` | Requires `.venv-garak` + `garak` on PATH via Makefile; `garak --help` preflight. |
| `make dynamic-probe-live-selfcheck` | Same; `garak --version` self-check. |
| `make dynamic-probe-live-exec` | Controlled `execute_once` (requires `EXECUTE_ARGS='…'`). |
| `make live-e2e-compare` | Multi-lane harness script (dynamic + Hub + assessment + strict); see [scripts/live_e2e_compare.py](../scripts/live_e2e_compare.py). |

**Isolated Garak environment:** heavy optional deps live under **`.venv-garak/`** (see root `.gitignore`). Main **`.venv/`** stays lean for CI; Makefile live targets prepend `GARAK_BIN` to `PATH`.

---

## Full documentation inventory

| Document | Role |
| -------- | ---- |
| [README.md](../README.md) | Project front door: philosophy, quick start, samples, Makefile, env vars. |
| [AGENTS.md](../AGENTS.md) | AI/agent discipline: must-read list, commands, session memory. |
| [PROGRAM_STATUS_SNAPSHOT.md](PROGRAM_STATUS_SNAPSHOT.md) | Operational snapshot: what is production-ready vs experimental. |
| [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) | Long-horizon phases 0–8, choice capture, pillars. |
| [PHASE5_DYNAMIC_PROBES.md](PHASE5_DYNAMIC_PROBES.md) | Dynamic lane design + shipped stub behavior. |
| [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md) | Threat model, severity, OWASP mapping. |
| [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md) | Test catalog index. |
| [LESSONS_LEARNED.md](LESSONS_LEARNED.md) | Pitfalls (paths, git, CI) — append when you learn something durable. |
| [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md) | Makefile, session log, graphify, propagation rules. |
| [HERMES_AGENTS.md](HERMES_AGENTS.md) | MCP/HTTP boundaries for agents. |
| [PUBLISH_ARGUS.md](PUBLISH_ARGUS.md) | GitHub mirror / publish notes. |
| [adr/0001-bundle-scanner-vs-orchestrator-scope.md](adr/0001-bundle-scanner-vs-orchestrator-scope.md) | ADR: bundle scanner vs orchestrator scope. |
| [sample_reports/README.md](sample_reports/README.md) | Committed live Hub sample JSON index. |
| [sample_reports/actionable/README.md](sample_reports/actionable/README.md) | Leadership / CSV / HTML briefing pack. |
| [sessions/SESSION_LOG.md](sessions/SESSION_LOG.md) | Append-only session notes (**no secrets**). |
| [graphify-out/README.md](../graphify-out/README.md) | Code graph artifact (optional). |
| [hf_bundle_scanner/README.md](../hf_bundle_scanner/README.md) | Bundle CLI, orchestrator pointers, phase 5 pointers. |
| [hf_bundle_scanner/docs/hermes-mcp.md](../hf_bundle_scanner/docs/hermes-mcp.md) | MCP + HTTP API. |
| [model-admission/README.md](../model-admission/README.md) | Admit-model CLI, policy, drivers, exit codes. |

---

## Documentation quality bar (maintainers)

1. **Same change as code** — When you change a default, schema field, or Makefile target, update **README** and/or this hub and the **phase doc** (e.g. PHASE5) in the same PR when practical.
2. **No secret values** — Never paste API keys, tokens, or customer paths into docs or [SESSION_LOG](sessions/SESSION_LOG.md).
3. **Do not mirror the full pytest matrix in README** — Link to [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md) and rely on **`make agent-verify`** + `.agent/pytest-last.log` (see [LESSONS_LEARNED.md](LESSONS_LEARNED.md)).
4. **Regenerate human samples when JSON changes** — `make sample-reports-all` / `make plain-english-brief` as appropriate (README § “Keeping this README honest”).
5. **Graphify** — After substantive Python edits under `hf_bundle_scanner/` or `model-admission/`, run **`make graphify-update`** when graphify is installed ([CLAUDE.md](../CLAUDE.md) / workspace rules).

---

_Last updated: 2026-04-26 — documentation hub introduced; aligns README, phase 5 doc, harness tables, and timestamp contract._
