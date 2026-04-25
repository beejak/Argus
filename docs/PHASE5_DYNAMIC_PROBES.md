# Phase 5 — dynamic probes (design + v1 stub)

## Scope

**Phase 5** adds an **opt-in** lane for **behavioral** probing (Garak-class tools, budgets, secrets) that is **not** part of default static bundle CI. Static admission (`scan-bundle`) stays deterministic; dynamic work is **policy- and env-gated**.

## v1 stub (shipped)

- **Report schema:** `llm_scanner.dynamic_probe_report.v1` — see [`hf_bundle_scanner/dynamic_probe_report.py`](../hf_bundle_scanner/hf_bundle_scanner/dynamic_probe_report.py).
- **CLI:** [`scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py) writes JSON to **`--out`**.
  - Default: `LLM_SCANNER_DYNAMIC_PROBE` unset or not `1` → `status: disabled`, exit `0`.
  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` missing** on `PATH` → `status: skipped`, exit `2` (tooling lane).
  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` present** → runs `garak --help` (120s cap); on success → `status: ok`, exit `0`; on failure → `status: error`, exit `2`.

This proves wiring, CI safety, and **absent-tool** semantics before any real probe configuration or model calls.

## Next (not in the stub)

- Real Garak / PyRIT **job configs**, model targets, rate limits, and artifact correlation with orchestrator `run_id`.
- Orchestrator **job graph** nodes for `dynamic_probe` with explicit **budget** and **secret** inputs (see [ADR 0001](adr/0001-bundle-scanner-vs-orchestrator-scope.md)).

## References

- [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) — phase table and pillar 7.
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — dynamic findings map to app-layer controls, not bundle file hashes.
