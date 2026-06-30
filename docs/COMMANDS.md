# Argus — Commands Reference

This document covers every CLI flag for `admit-model` and `scan-bundle`, all Makefile targets, and the key scripts in `scripts/`.

---

## admit-model

Entry-point installed by `model-admission`. Runs a per-artifact policy and driver scan.

### admit-model scan

Scan a single model artifact against a policy file.

```
admit-model scan --artifact PATH --policy PATH [options]
```

| Flag | Required | Default | Description |
| ---- | -------- | ------- | ----------- |
| `--artifact PATH` | yes | — | Path to the model file to scan |
| `--policy PATH` | yes | — | JSON policy file (size gate, extension lists, SHA-256 allowlist) |
| `--report PATH` | no | `""` (no file written) | Write the `ScanReport` JSON to this path; parent directories are created automatically |
| `--ledger PATH` | no | `""` (no ledger entry) | Append a JSONL audit line to this file. Also respected via the `MODEL_ADMISSION_LEDGER` environment variable |
| `--drivers LIST` | no | `modelscan,modelaudit` | Comma-separated driver names. Pass `""` to skip all drivers and run the policy gate only |
| `--timeout SECS` | no | `600` | Per-driver subprocess timeout in seconds |
| `--fail-on SEVERITY` | no | `MEDIUM` | Minimum finding severity that causes exit code `1`. Choices: `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |

**Exit codes:**

| Code | Meaning |
| ---- | ------- |
| `0` | No policy violations and no findings at or above `--fail-on` severity |
| `1` | At least one policy violation or finding at/above the severity floor |
| `2` | A driver subprocess failed or timed out |
| `4` | Unknown driver name or bad arguments |

**Example:**

```bash
admit-model scan \
  --artifact /path/to/model.safetensors \
  --policy policy.json \
  --report /tmp/admit.json \
  --drivers "" \
  --timeout 600 \
  --fail-on MEDIUM
```

With drivers:

```bash
admit-model scan \
  --artifact /path/to/model.bin \
  --policy policy.json \
  --report /tmp/admit.json \
  --drivers modelscan,modelaudit \
  --fail-on HIGH
```

---

## scan-bundle

Entry-point installed by `hf-bundle-scanner`. Three subcommands: `manifest`, `download`, `scan`.

### scan-bundle manifest

Compute a recursive SHA-256 manifest for a directory tree and write it to JSON.

```
scan-bundle manifest --root PATH --out PATH
```

| Flag | Required | Description |
| ---- | -------- | ----------- |
| `--root PATH` | yes | Snapshot root directory |
| `--out PATH` | yes | Output manifest JSON path |

**Example:**

```bash
scan-bundle manifest --root /path/to/snapshot --out /tmp/manifest.json
```

### scan-bundle download

Download a Hugging Face Hub snapshot to a local directory. Requires network access and `huggingface_hub` installed.

```
scan-bundle download --repo REPO_ID --dest PATH [--revision REF]
```

| Flag | Required | Default | Description |
| ---- | -------- | ------- | ----------- |
| `--repo REPO_ID` | yes | — | Hugging Face repo id, e.g. `org/name` |
| `--dest PATH` | yes | — | Destination directory for the downloaded snapshot |
| `--revision REF` | no | Hub default branch | Branch, tag, or commit hash to download |

**Example:**

```bash
scan-bundle download \
  --repo hf-internal-testing/tiny-random-BertModel \
  --dest /tmp/bert-snapshot \
  --revision main
```

### scan-bundle scan

Walk a snapshot directory: build a file manifest, run `configlint` on JSON configs, invoke `admit-model` per weight-like artifact, and write an aggregate bundle report.

```
scan-bundle scan --root PATH --policy PATH --out PATH [options]
```

| Flag | Required | Default | Description |
| ---- | -------- | ------- | ----------- |
| `--root PATH` | yes | — | Snapshot root directory |
| `--policy PATH` | yes | — | `model-admission` policy JSON |
| `--out PATH` | yes | — | Bundle report JSON output path |
| `--drivers LIST` | no | `""` (empty) | Comma-separated driver names forwarded to each `admit-model` invocation. Pass `""` for policy gate only |
| `--timeout SECS` | no | `600` | Per-file driver timeout seconds |
| `--fail-on SEVERITY` | no | `MEDIUM` | Severity floor for each `admit-model` invocation. Choices: `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `--no-manifest` | no | off | Omit the full file manifest from the bundle report (smaller output) |
| `--print-summary` | no | off | Print a small JSON summary (`aggregate_exit_code`, `file_count`, `config_finding_count`) to stdout |
| `--hub-repo REPO_ID` | no | None | Optional Hub repo id echoed into `provenance.hub_repo_id` |
| `--hub-revision REF` | no | None | Optional Hub revision echoed into `provenance.hub_revision` |
| `--mirror-allowlist HOSTS` | no | None | Comma-separated mirror hostnames merged with `HF_BUNDLE_MIRROR_ALLOWLIST` into `provenance` |
| `--sbom-uri URI` | no | None | SBOM location (URI or path) overriding `HF_BUNDLE_SBOM_URI` and echoed into `provenance.sbom_uri` |

**Exit codes:** same semantics as `admit-model` — worst child wins: `4` (usage) > `2` (tooling) > `1` (policy/findings/configlint CONFIG_RISK) > `0` (clean).

**Example (policy gate only, with provenance):**

```bash
export HF_BUNDLE_PYTHON="$(pwd)/.venv/bin/python"
scan-bundle scan \
  --root /path/to/snapshot \
  --policy /path/to/policy.json \
  --out /tmp/bundle-report.json \
  --drivers "" \
  --print-summary \
  --hub-repo org/model \
  --hub-revision main \
  --mirror-allowlist huggingface.co,cdn-lfs.huggingface.co \
  --sbom-uri file:///path/to/sbom.json
```

**Example (with drivers):**

```bash
scan-bundle scan \
  --root /path/to/snapshot \
  --policy policy.json \
  --out /tmp/bundle-report.json \
  --drivers modelscan,modelaudit \
  --fail-on HIGH \
  --print-summary
```

---

## Makefile targets

Run `make help` from the repo root to see the current list. All targets use the repo-local `.venv/` interpreter.

| Target | Description |
| ------ | ----------- |
| `make install` | Create `.venv/` and install `model-admission[dev]` + `hf_bundle_scanner[dev,mcp,http]` in editable mode |
| `make test` | Run `hf_bundle_scanner` pytest, excluding `integration` and `chwoo` markers |
| `make integration` | Run `hf_bundle_scanner` pytest with the `integration` marker (requires network / Hub) |
| `make scan-fixture` | Smoke scan of a minimal `safetensors` stub with the permissive policy fixture |
| `make agent-verify` | Full verify: both packages' pytest + ruff + orchestrator `validate` + dynamic-probe stub; writes `.agent/pytest-last.log` and `.agent/pytest-last.exit` |
| `make lint` | Run `ruff check` over `hf_bundle_scanner/` source and tests |
| `make fmt` | Run `ruff format` over `hf_bundle_scanner/` source and tests |
| `make ruff-check` | Alias for `make lint` |
| `make docker` | Build `model-admission:local` Docker image |
| `make docker-bundle` | Build `hf-bundle-scanner:local` Docker image |
| `make roadmap` | Print pointer to `docs/PRODUCTION_SCANNER_ROADMAP.md` |
| `make docs-map` | Print pointer to `docs/DOCUMENTATION.md` (canonical documentation hub) |
| `make graphify-update` | Refresh `graphify-out/` code graph if `graphify` is installed |
| `make memory-open` | Print path to `docs/sessions/SESSION_LOG.md` |
| `make git-doctor` | Diagnose `git commit` / trailer config issues |
| `make commit-msg MSG='…'` | Commit via `git commit -F` (safer quoting than `-m` for conventional prefixes) |
| `make slogan-dry-run` | Print the next README slogan without writing any files |
| `make ephemeral-hub-scan OUT=/path.json` | Download a Hub snapshot, run `scan-bundle scan`, delete the tree. Optional: `INJECT=1` adds a demo `trust_remote_code` tokenizer JSON; `EPHEMERAL_FLAGS="--repo org/name"` targets a different repo |
| `make sample-action-sheets` | Regenerate `docs/sample_reports/actionable/` (CSV, HTML, leadership MD) from committed sample JSON |
| `make plain-english-brief` | Write `PLAIN_ENGLISH_BRIEF.md` only (does not overwrite CSV/HTML/blast MD) |
| `make sample-reports-all` | Run `sample-action-sheets` then `plain-english-brief` |
| `make drivers-help` | Print known `admit-model` driver names and `MODELSCAN_BIN` / `MODELAUDIT_BIN` hints |
| `make hub-find-models-under-size` | Hub metadata search for repos whose total file size is under `--max-mb` (default 200 MiB). Pass flags via `HF_HUB_FIND_FLAGS`. Requires network. |
| `make orchestrator-validate` | Validate three orchestrator job fixtures (min, dynamic_probe, admit_model) — no subprocess scans |
| `make dynamic-probe-stub` | Write `.agent/dynamic_probe_last.json` with a disabled probe (unless `LLM_SCANNER_DYNAMIC_PROBE=1`) |
| `make dynamic-probe-live-preflight` | Run `garak --help` via isolated `.venv-garak` (requires `LLM_SCANNER_DYNAMIC_PROBE=1` is not needed — Makefile sets it) |
| `make dynamic-probe-live-selfcheck` | Run `garak --version` via isolated `.venv-garak` |
| `make dynamic-probe-live-exec EXECUTE_ARGS='…'` | Run `execute_once` with explicit Garak argv |
| `make live-e2e-compare` | Multi-lane end-to-end harness (dynamic + gate + assessment + strict); optional `LIVE_E2E_FLAGS` |

---

## Key scripts in scripts/

| Script | Purpose | Example invocation |
| ------ | ------- | ------------------ |
| `scripts/run_tests_for_agent.py` | Backend for `make agent-verify`; runs both packages' pytest and writes `.agent/pytest-last.log` and `.agent/pytest-last.exit` | `make agent-verify` |
| `scripts/ephemeral_hub_scan.py` | Hub `snapshot_download` → `scan-bundle scan` → delete temp tree; optionally writes HTML briefing alongside the bundle JSON | `python3 scripts/ephemeral_hub_scan.py --out /tmp/r.json --inject-demo-tokenizer-risk` |
| `scripts/run_orchestrator_job.py` | Phase-4 orchestrator runner: declarative job JSON → `scan_bundle` + optional `admit_model` fan-out + optional `dynamic_probe` + envelope v2 | `python3 scripts/run_orchestrator_job.py validate --job hf_bundle_scanner/tests/fixtures/orchestrator_job_min.json` |
| `scripts/run_dynamic_probe.py` | Phase-5 dynamic probe CLI; writes `llm_scanner.dynamic_probe_report.v1` JSON | `LLM_SCANNER_DYNAMIC_PROBE=1 python3 scripts/run_dynamic_probe.py --out .agent/probe.json --execution-mode preflight` |
| `scripts/export_bundle_action_sheet.py` | Bundle JSON → CSV + HTML + `BLAST_RADIUS_LEADERSHIP.md` with OWASP tags and decision-support columns | `python3 scripts/export_bundle_action_sheet.py` |
| `scripts/export_plain_english_brief.py` | Sample bundle JSONs → `PLAIN_ENGLISH_BRIEF.md` (non-technical approver narrative) | `python3 scripts/export_plain_english_brief.py` |
| `scripts/redact_ephemeral_report.py` | Strip ephemeral `/tmp/hf-ephemeral-*` paths from a bundle JSON before committing as a sample | `python3 scripts/redact_ephemeral_report.py /tmp/in.json docs/sample_reports/out.json` |
| `scripts/summarize_bundle_json.py` | Short stdout summary of a bundle JSON (paths, exits, configlint hits) | `python3 scripts/summarize_bundle_json.py /tmp/bundle.json` |
| `scripts/hub_find_models_under_size.py` | Hub metadata search: repos whose summed file sizes are under `--max-mb` (default 200); optional `--probe-configlint` | `.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 12` |
| `scripts/live_e2e_compare.py` | Multi-lane end-to-end comparison harness (network + drivers + strict policy) | `make live-e2e-compare` |
| `scripts/git_commit_via_file.py` | Commit via `git commit -F` when `git commit -m` / trailers misbehave | `python3 scripts/git_commit_via_file.py 'type: subject'` |
| `scripts/git_doctor.py` | Diagnose trailer and identity issues in git config | `make git-doctor` |
| `scripts/rotate_readme_slogan.py` | Rotate the README tagline from `docs/slogans.json` | `make slogan-dry-run` |
| `scripts/run-tests-for-agent.sh` | Shell wrapper around `run_tests_for_agent.py` (alternative entry-point) | `bash scripts/run-tests-for-agent.sh` |
