# Phase 5 — dynamic probes (design + v1 stub)

## Scope

**Phase 5** adds an **opt-in** lane for **behavioral** probing (Garak-class tools, budgets, secrets) that is **not** part of default static bundle CI. Static admission (`scan-bundle`) stays deterministic; dynamic work is **policy- and env-gated**.

## v1 stub (shipped)

- **Report schema:** `llm_scanner.dynamic_probe_report.v1` — see [`hf_bundle_scanner/dynamic_probe_report.py`](../hf_bundle_scanner/hf_bundle_scanner/dynamic_probe_report.py).
- **CLI:** [`scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py) writes JSON to **`--out`**.
  - Optional flags: **`--run-id`**, **`--budget-max-probes`**, **`--budget-timeout-seconds`**, **`--garak-config`**, **`--model-target`**, **`--secret-env-vars`**.
  - Secret handling: `--secret-env-vars` records only **names**, never values; missing required env vars fail with `status: error` and exit `2`.
  - Budget guardrails: invalid non-positive budgets return `status: error`, exit `2`.
  - Default: `LLM_SCANNER_DYNAMIC_PROBE` unset or not `1` → `status: disabled`, exit `0`.
  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` missing** on `PATH` → `status: skipped`, exit `2` (tooling lane).
  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` present** → runs `garak --help` (timeout from `--budget-timeout-seconds`, default `120`); on success → `status: ok`, exit `0`; on failure → `status: error`, exit `2`.

This proves wiring, CI safety, and **absent-tool** semantics before any real probe configuration or model calls.

## Orchestrator composition (v1 slice, shipped)

Jobs may include **at most one** `dynamic_probe` step **after** `scan_bundle` and **before** `aggregate`:

- **`steps`:** `dynamic_probe` → `depends_on` must be exactly `[<scan_bundle step id>]`; `aggregate` → `depends_on` must include both `scan_bundle` and `dynamic_probe` ids when a dynamic step exists.
- **Top-level `dynamic_probe` object:** non-empty **`out`** path for `llm_scanner.dynamic_probe_report.v1` JSON (written by [`scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py)); optional **`budget_max_probes`** and **`budget_timeout_seconds`** are validated as positive integers; optional **`garak_config`**, **`model_target`**, **`secret_env_vars`** (array of names) are accepted and validated.
- **Runner:** [`scripts/run_orchestrator_job.py`](../scripts/run_orchestrator_job.py) `run` invokes the probe script after a successful job validation, forwards `run_id` + dynamic settings, merges **`aggregate_exit_code`** with the probe report’s **`exit_code`** via the same **worst-of** priority as bundle aggregates (`4 > 2 > 1 > 0`), and inserts a **middle** row in envelope **`llm_scanner.orchestrator_envelope.v2`** `steps[]`.
- **Fixture:** [`hf_bundle_scanner/tests/fixtures/orchestrator_job_with_dynamic.json`](../hf_bundle_scanner/tests/fixtures/orchestrator_job_with_dynamic.json).

## Next (beyond this slice)

- Real Garak / PyRIT **probe execution** beyond the current metadata + `garak --help` preflight.
- Explicit **secret** inputs and richer budget policy semantics on the job document (see [ADR 0001](adr/0001-bundle-scanner-vs-orchestrator-scope.md)).

## References

- [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) — phase table, pillar 7, and **Choice capture** (backlog for Garak config / budgets vs phase-4 fan-out).
- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — dynamic findings map to app-layer controls, not bundle file hashes.
