# ADR 0001 — Bundle scanner vs future orchestrator scope

- **Status:** accepted. **Implemented (repo, 2026-04-25):** job document `llm_scanner.orchestrator_job.v1` validation + `run` / `validate` in [`scripts/run_orchestrator_job.py`](../scripts/run_orchestrator_job.py); envelope `llm_scanner.orchestrator_envelope.v2` with UUID `run_id` / optional `parent_run_id` and per-step wall times; **optional** `admit_model` fan-out nodes (subprocess `python -m model_admission scan`), plus optional `dynamic_probe` step (at most one) after `scan_bundle` — all merged in `aggregate`. See [`docs/PHASE5_DYNAMIC_PROBES.md`](../PHASE5_DYNAMIC_PROBES.md). **Not implemented yet:** YAML job format, non-subprocess backends.
- **Date:** 2026-04-24 (phase 4 kickoff notes: 2026-04-25)

## Context

Today, **`hf_bundle_scanner`** answers: *given a snapshot directory + policy, what do static gates say?*  
Downstream roadmap phases describe **job graphs**, sibling scanners (agents/RAG), and policy-gated dynamic probes.

## Decision (working hypothesis)

Keep **`scan-bundle`** as a **bounded, deterministic bundle admission** tool. Treat a future **orchestrator** as a separate composition layer that **calls** bundle scan (and other jobs) rather than growing infinite responsibilities inside `scan_bundle`.

## Consequences

- Bundle JSON remains the **contract** for “what this lane saw.”
- Cross-lane correlation IDs, fan-out/fan-in, and budgeted dynamic jobs live **above** bundle scan in a later component (ADR to be refined when phase 4 implementation starts).

## Phase 4 — job graph sketch (v1 shipped subset)

Minimal **directed acyclic** graph for the **first shipped** orchestrator slice (validator + runner):

1. **`bundle_scan`** — subprocess or HTTP/MCP call to existing `scan-bundle scan` → artifact: `bundle_report.v2` JSON.
2. **`admit_model` (optional fan-out)** — one job per heavyweight file already supported by `model-admission` when policy demands it; artifacts: admit-model JSON paths referenced from bundle or orchestrator index.
3. **`aggregate`** — deterministic reducer: worst exit across children + attach `run_id`, wall-clock, and input digests in an **orchestrator envelope** (separate JSON or sidecar) so bundle schema stays backward compatible.

Edges: `admit_model*` → `aggregate`; `bundle_scan` → `aggregate`. **Shipped subset:** optional `admit_model` fan-out (`bundle_scan` → each `admit_model` → `aggregate`) and optional `dynamic_probe` (`bundle_scan` → `dynamic_probe` → `aggregate`) with validator-enforced DAG / `depends_on`.

## Phase 4 — correlation & provenance

- **Orchestrator-owned (envelope v2):** `run_id` (RFC 4122 UUID string; optional in job doc — runner generates one if absent), optional `parent_run_id` (UUID when present). `steps[]` entries include **`id`** and **`type`** (mirror job document) plus **`name`**, **`artifact_uri`** (`file:` URI for bundle output and envelope path), **`exit_code`**, **`started_at` / `ended_at`** (RFC 3339 UTC with `Z`). Job documents must use UUID `run_id` / `parent_run_id` when those keys are non-empty.
- **Bundle-owned (optional extension later):** mirror today’s `provenance` object; if a correlation field is added, it must be **optional** so existing consumers and fixtures keep working.

## Phase 4 — acceptance criteria (first implementation slice)

1. **Done (JSON):** a declarative **JSON** job document describes the **scan_bundle → aggregate** graph and validates without executing scans (`validate` subcommand).
2. **Done:** running `run` on the fixture tree produces bundle JSON + envelope JSON; process exit follows bundle **`aggregate_exit_code`** when readable (else tooling-style failure).
3. **Done:** no new **required** fields on `hf_bundle_scanner.bundle_report.v2`.

**Still open (later slices):** YAML jobs; broader multi-scan graph composition beyond current `scan_bundle` + `admit_model*` + optional `dynamic_probe`; optional echo of `run_id` into bundle `provenance` (separate ADR if pursued); HTTP/MCP job backends.

## Links

- [PRODUCTION_SCANNER_ROADMAP.md](../PRODUCTION_SCANNER_ROADMAP.md)
- Plain-language sample outputs: [../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md](../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md)
- Runner + validator entrypoint: [`../scripts/run_orchestrator_job.py`](../scripts/run_orchestrator_job.py)
