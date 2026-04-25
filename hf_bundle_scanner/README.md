# hf-bundle-scanner

Modular HF-oriented bundle scanner: **manifest** (hashes), **discovery**, **dispatch** to [`model-admission`](../model-admission/README.md) per file, **configlint** (e.g. `trust_remote_code`, `auto_map`, `use_auth_token`, `use_fast_tokenizer`, invalid JSON), **aggregate report**.

Install from repo root (WSL):

```bash
pip install -e "./model-admission"
pip install -e "./hf_bundle_scanner[dev]"
```

Use the Makefile in the parent `LLM Scanner/` directory (`make test`, `make scan-fixture`).

## CLI

```bash
scan-bundle manifest --root /path/to/snapshot --out /tmp/manifest.json
scan-bundle download --repo org/name --revision main --dest /tmp/snap
scan-bundle scan --root /path/to/snapshot --policy policy.json --out /tmp/bundle.json --drivers ""
# Optional provenance (bundle JSON schema v2, top-level `provenance`):
scan-bundle scan --root "$D" --policy policy.json --out /tmp/bundle.json --drivers "" \
  --hub-repo org/name --hub-revision main \
  --mirror-allowlist huggingface.co,cdn-lfs.huggingface.co \
  --sbom-uri file:///tmp/sbom.json
python -m hf_bundle_scanner manifest --root /path --out /tmp/m.json
```

Environment mirrors / SBOM merge with CLI flags: **`HF_BUNDLE_MIRROR_ALLOWLIST`** (comma-separated hosts), **`HF_BUNDLE_SBOM_URI`**.

### Optional static drivers (ModelScan / ModelAudit)

`scan-bundle scan` forwards **`--drivers`** to [`model-admission`](../model-admission/README.md) (`admit-model scan`). Built-in driver names today: **`modelscan`**, **`modelaudit`** (comma-separated).

```bash
scan-bundle scan --root "$D" --policy policy.json --out /tmp/bundle.json \
  --drivers modelscan,modelaudit --fail-on MEDIUM
```

If the external CLI is missing, per-file **`exit_code`** is **`2`** (tooling/driver lane) and the bundle aggregate follows the usual priority rules. Override binaries with **`MODELSCAN_BIN`** / **`MODELAUDIT_BIN`** (see model-admission README). From repo root: **`make drivers-help`**.

Org-level defaults for **configlint** severities vs CI escalation live in [`docs/policy/configlint_rule_defaults.json`](../docs/policy/configlint_rule_defaults.json).

See [docs/hermes-mcp.md](docs/hermes-mcp.md) for MCP and optional HTTP.

## Phase-4 orchestrator (composition above `scan-bundle`)

- **ADR:** [../docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md](../docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md)
- **Python API:** `hf_bundle_scanner.orchestrator_job` — `validate_job`, `load_job`, `build_envelope`
- **CLI:** from repo root, `python3 scripts/run_orchestrator_job.py validate|run --job …` (see script docstring). **`make orchestrator-validate`** runs `validate` on the committed fixture.

Job documents use schema **`llm_scanner.orchestrator_job.v1`**; envelopes written by `run` use **`llm_scanner.orchestrator_envelope.v2`** (`run_id`, optional `parent_run_id`, per-step timestamps and `artifact_uri` values). Jobs may declare **one** optional **`dynamic_probe`** step between **`scan_bundle`** and **`aggregate`** (see [PHASE5 doc](../docs/PHASE5_DYNAMIC_PROBES.md)); `run` invokes [`run_dynamic_probe.py`](../scripts/run_dynamic_probe.py), forwards `run_id` + optional dynamic budgets (`budget_max_probes`, `budget_timeout_seconds`), and merges exits into **`aggregate_exit_code`**.

## Phase-5 dynamic probes (stub)

- **Doc:** [../docs/PHASE5_DYNAMIC_PROBES.md](../docs/PHASE5_DYNAMIC_PROBES.md)
- **Report builder:** `hf_bundle_scanner.dynamic_probe_report`
- **CLI:** [`../scripts/run_dynamic_probe.py`](../scripts/run_dynamic_probe.py) — supports `--run-id`, `--budget-max-probes`, and `--budget-timeout-seconds`; from repo root, **`make dynamic-probe-stub`** writes `.agent/dynamic_probe_last.json` (disabled unless **`LLM_SCANNER_DYNAMIC_PROBE=1`**).

### Optional: scan a small file from the “uncensored-models” collection

The curated list [uncensored-models](https://huggingface.co/collections/chwoo/uncensored-models) mostly hosts **multi‑GiB** full weights. One repo in that list has a **under 1 GiB** weight-like artifact we can use for a real download + scan check: **`mradermacher/gemma3-4b-it-abliterated-GGUF`** file **`gemma3-4b-it-abliterated.mmproj-Q8_0.gguf`** (~561 MiB, vision projector tensors—not the full chat stack).

Opt-in pytest (network, large download):

```bash
cd "/root/LLM Scanner/hf_bundle_scanner"
export HF_BUNDLE_PYTHON="/root/LLM Scanner/.venv/bin/python"
HF_BUNDLE_CHWOO_SCAN=1 python -m pytest tests/test_integration_chwoo_collection.py -v --tb=short
```

Manual equivalent (download one file, then scan):

```bash
export HF_BUNDLE_PYTHON="/root/LLM Scanner/.venv/bin/python"
D=$(mktemp -d)
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='mradermacher/gemma3-4b-it-abliterated-GGUF', filename='gemma3-4b-it-abliterated.mmproj-Q8_0.gguf', local_dir='$D')"
cd "/root/LLM Scanner/hf_bundle_scanner"
scan-bundle scan --root "$D" --policy tests/fixtures/policy.permissive.json --out /tmp/chwoo-scan.json --drivers "" --print-summary
```
