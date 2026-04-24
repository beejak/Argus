# ADR 0001 — Bundle scanner vs future orchestrator scope

- **Status:** accepted for **phase 4 design**; execution code intentionally not started in this repo until the job graph + contract below are stable.
- **Date:** 2026-04-24 (phase 4 kickoff notes: 2026-04-25)

## Context

Today, **`hf_bundle_scanner`** answers: *given a snapshot directory + policy, what do static gates say?*  
Downstream roadmap phases describe **job graphs**, sibling scanners (agents/RAG), and policy-gated dynamic probes.

## Decision (working hypothesis)

Keep **`scan-bundle`** as a **bounded, deterministic bundle admission** tool. Treat a future **orchestrator** as a separate composition layer that **calls** bundle scan (and other jobs) rather than growing infinite responsibilities inside `scan_bundle`.

## Consequences

- Bundle JSON remains the **contract** for “what this lane saw.”
- Cross-lane correlation IDs, fan-out/fan-in, and budgeted dynamic jobs live **above** bundle scan in a later component (ADR to be refined when phase 4 implementation starts).

## Phase 4 — job graph sketch (design only)

Minimal **directed acyclic** graph for the first orchestrator slice (names are logical; not code yet):

1. **`bundle_scan`** — subprocess or HTTP/MCP call to existing `scan-bundle scan` → artifact: `bundle_report.v2` JSON.
2. **`admit_model` (optional fan-out)** — one job per heavyweight file already supported by `model-admission` when policy demands it; artifacts: admit-model JSON paths referenced from bundle or orchestrator index.
3. **`aggregate`** — deterministic reducer: worst exit across children + attach `run_id`, wall-clock, and input digests in an **orchestrator envelope** (separate JSON or sidecar) so bundle schema stays backward compatible.

Edges: `admit_model*` → `aggregate`; `bundle_scan` → `aggregate`. Dynamic probes (phase 5) attach later as optional nodes with **explicit budget + secret** gates; they must not become implicit dependencies of `bundle_scan`.

## Phase 4 — correlation & provenance

- **Orchestrator-owned:** `run_id` (UUID), optional `parent_run_id`, ordered `steps[]` with `{ "name", "artifact_uri", "exit_code", "started_at", "ended_at" }`.
- **Bundle-owned (optional extension later):** mirror today’s `provenance` object; if a correlation field is added, it must be **optional** so existing consumers and fixtures keep working.

## Phase 4 — acceptance criteria (first implementation slice)

1. A single **declarative job document** (YAML or JSON) can describe the graph above and be validated without executing scans.
2. Running the orchestrator on a fixture tree produces: bundle JSON + envelope JSON + **non-zero exit** iff any child failed, preserving priority semantics already documented for bundle aggregates.
3. No new **required** fields on `hf_bundle_scanner.bundle_report.v2` until a dedicated schema bump ADR exists.

## Links

- [PRODUCTION_SCANNER_ROADMAP.md](../PRODUCTION_SCANNER_ROADMAP.md)
- Plain-language sample outputs: [../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md](../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md)
