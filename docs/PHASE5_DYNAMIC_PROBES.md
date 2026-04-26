# Phase 5 — dynamic probes (design + v1 stub)



## Scope



**Phase 5** adds an **opt-in** lane for **behavioral** probing (Garak-class tools, budgets, secrets) that is **not** part of default static bundle CI. Static admission (`scan-bundle`) stays deterministic; dynamic work is **policy- and env-gated**.



## v1 stub (shipped)



- **Report schema:** `llm_scanner.dynamic_probe_report.v1` — see [`hf_bundle_scanner/dynamic_probe_report.py`](../hf_bundle_scanner/hf_bundle_scanner/dynamic_probe_report.py).

- **CLI:** [`scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py) writes JSON to **`--out`**.

  - Optional flags: **`--run-id`**, **`--budget-max-probes`**, **`--budget-timeout-seconds`**, **`--garak-config`**, **`--garak-config-inline`**, **`--model-target`**, **`--secret-env-vars`**, **`--execution-mode`**, **`--execute-args`**.
  - Config source:
    - **`--garak-config`** = path to config file.
    - **`--garak-config-inline`** = inline config text (orchestrator/job-JSON friendly).
    - These two inputs are **mutually exclusive**.

  - **Execution modes** (bounded subprocess, no shell injection):

    - **`preflight`** (default): `garak --help` availability check (with optional `--config` when either config source is set).

    - **`selfcheck`**: `garak --version` CLI self-check (still bounded by **`--budget-timeout-seconds`**).

    - **`execute_once`**: one explicit argv tail from **`--execute-args`** (must be non-empty); use the Makefile form `EXECUTE_ARGS='…'` to avoid the shell eating leading `--`.

  - **Timestamps:** every emitted report includes **`report_generated_at_utc`** and **`report_generated_at_ist`** (same clock instant, UTC `Z` + IST `+05:30`). They are fixed at **report write time**, not recomputed on every dict serialization.

  - Secret handling: `--secret-env-vars` records only **names**, never values; missing required env vars fail with `status: error` and exit `2`.

  - Budget guardrails: invalid non-positive budgets return `status: error`, exit `2`.

  - Default: `LLM_SCANNER_DYNAMIC_PROBE` unset or not `1` → `status: disabled`, exit `0`.

  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` missing** on `PATH` → `status: skipped`, exit `2` (tooling lane).

  - `LLM_SCANNER_DYNAMIC_PROBE=1` and **`garak` present**:

    - success → `status: ok`, exit `0`; subprocess failure / timeout → `status: error`, exit `2`.



This proves wiring, CI safety, and **absent-tool** semantics before any real probe configuration or model calls.



### Isolated Garak venv (repo root)



Garak pulls a large dependency graph. This repo keeps an **optional** interpreter tree at **`.venv-garak/`** (ignored by git) and Makefile targets that prepend **`GARAK_BIN`** (`.venv-garak/bin`) to `PATH` for live checks. The main **`.venv/`** used by `make install` / `make agent-verify` stays suitable for CI.



| Makefile target | What it runs |

| --------------- | ------------- |

| **`make dynamic-probe-stub`** | `run_dynamic_probe.py` → `.agent/dynamic_probe_last.json` (disabled unless env). |

| **`make dynamic-probe-live-preflight`** | `LLM_SCANNER_DYNAMIC_PROBE=1`, `execution_mode=preflight`. |

| **`make dynamic-probe-live-selfcheck`** | `LLM_SCANNER_DYNAMIC_PROBE=1`, `execution_mode=selfcheck` (`garak --version`). |

| **`make dynamic-probe-live-exec`** | `execution_mode=execute_once` — requires **`EXECUTE_ARGS='…'`**. |



## Orchestrator composition (v1 slice, shipped)



Jobs may include **at most one** `dynamic_probe` step **after** `scan_bundle` and **before** `aggregate`:



- **`steps`:** `dynamic_probe` → `depends_on` must be exactly `[<scan_bundle step id>]`; `aggregate` → `depends_on` must include both `scan_bundle` and `dynamic_probe` ids when a dynamic step exists.

- **Top-level `dynamic_probe` object:** non-empty **`out`** path for `llm_scanner.dynamic_probe_report.v1` JSON (written by [`scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py)); optional **`budget_max_probes`** and **`budget_timeout_seconds`** are validated as positive integers; optional **`garak_config`** (file path) **or** **`garak_config_inline`** (inline text; mutually exclusive), **`model_target`**, **`secret_env_vars`** (array of names), and execution controls (`execution_mode`, `execute_args`) are accepted and validated.

  - **`execution_mode`** must be one of: **`preflight`**, **`selfcheck`**, **`execute_once`**.

  - When **`execution_mode`** is **`execute_once`**, **`execute_args`** must be a non-empty string.

- **Runner:** [`scripts/run_orchestrator_job.py`](../scripts/run_orchestrator_job.py) `run` invokes the probe script after a successful job validation, forwards `run_id` + dynamic settings, merges **`aggregate_exit_code`** with the probe report’s **`exit_code`** via the same **worst-of** priority as bundle aggregates (`4 > 2 > 1 > 0`), and inserts a **middle** row in envelope **`llm_scanner.orchestrator_envelope.v2`** `steps[]`.

- **Fixture:** [`hf_bundle_scanner/tests/fixtures/orchestrator_job_with_dynamic.json`](../hf_bundle_scanner/tests/fixtures/orchestrator_job_with_dynamic.json).



## Live multi-lane harness (optional)



[`scripts/live_e2e_compare.py`](../scripts/live_e2e_compare.py) ( **`make live-e2e-compare`** ) runs a scripted comparison across lanes (dynamic preflight + selfcheck, ephemeral Hub baseline, driver-on assessment, strict policy). It writes a small summary JSON (with the same UTC/IST timestamp pair). Intended for **manual or lab** verification when `.venv` and `.venv-garak` are present — not a substitute for **`make agent-verify`** in default CI.



## Next (beyond this slice)



- Real Garak / PyRIT **probe execution breadth** beyond help/version/execute-once controls.

- Explicit **secret** inputs and richer budget policy semantics on the job document (see [ADR 0001](adr/0001-bundle-scanner-vs-orchestrator-scope.md)).



## References



- [DOCUMENTATION.md](DOCUMENTATION.md) — hub: contracts, timestamps, Makefile map.

- [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) — phase table, pillar 7, and **Choice capture** (backlog for Garak config / budgets vs phase-4 fan-out).

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — dynamic findings map to app-layer controls, not bundle file hashes.


