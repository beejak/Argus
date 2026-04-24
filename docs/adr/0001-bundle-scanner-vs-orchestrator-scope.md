# ADR 0001 — Bundle scanner vs future orchestrator scope

- **Status:** proposed (phase **`phase4-orchestrator-scope`**)
- **Date:** 2026-04-24

## Context

Today, **`hf_bundle_scanner`** answers: *given a snapshot directory + policy, what do static gates say?*  
Downstream roadmap phases describe **job graphs**, sibling scanners (agents/RAG), and policy-gated dynamic probes.

## Decision (working hypothesis)

Keep **`scan-bundle`** as a **bounded, deterministic bundle admission** tool. Treat a future **orchestrator** as a separate composition layer that **calls** bundle scan (and other jobs) rather than growing infinite responsibilities inside `scan_bundle`.

## Consequences

- Bundle JSON remains the **contract** for “what this lane saw.”
- Cross-lane correlation IDs, fan-out/fan-in, and budgeted dynamic jobs live **above** bundle scan in a later component (ADR to be refined when phase 4 implementation starts).

## Links

- [PRODUCTION_SCANNER_ROADMAP.md](../PRODUCTION_SCANNER_ROADMAP.md)
- Plain-language sample outputs: [../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md](../sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md)
