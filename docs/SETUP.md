# Argus — Setup Guide

This document covers everything needed to go from a fresh checkout to a working scan environment.

---

## Python version requirement

Both packages require **Python 3.11 or 3.12** (declared in `pyproject.toml` as `requires-python = ">=3.11"`). Python 3.10 and earlier are not supported.

---

## Install both packages in dev mode

The recommended path creates a repo-local virtual environment so pip does not conflict with PEP 668 system-managed interpreters.

```bash
# From the repo root
make install
```

This is equivalent to:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
cd model-admission && pip install -e ".[dev]"
cd ../hf_bundle_scanner && pip install -e ".[dev,mcp,http]"
```

After installation the following entry-points are on your `PATH` (inside the venv):

| Entry-point | Package | Purpose |
| ----------- | ------- | ------- |
| `admit-model` | `model-admission` | Per-artifact policy gate |
| `scan-bundle` | `hf-bundle-scanner` | Bundle orchestration (manifest, download, scan) |
| `hf-bundle-mcp` | `hf-bundle-scanner` | MCP server (requires `[mcp]` extras) |
| `hf-bundle-http` | `hf-bundle-scanner` | HTTP server (requires `[http]` extras) |

---

## Optional external tools

Three external tools are used by the `--drivers` flag on `admit-model scan` and `scan-bundle scan`. All three are **optional** — if they are absent the policy gate still runs, and you can pass `--drivers ""` to skip driver invocations entirely.

| Tool | Purpose | What happens if absent |
| ---- | ------- | ---------------------- |
| **modelscan** | Deep deserialization and pickle safety scanning of weight files | If requested via `--drivers modelscan` and the binary cannot be found, `admit-model` exits `2` (tooling error). The bundle aggregate also receives exit `2`. |
| **modelaudit** | Additional static audit of model file formats | Same as modelscan — exit `2` if binary missing and driver is requested. |
| **garak** | Dynamic LLM probe harness (phase-5 opt-in) | If `LLM_SCANNER_DYNAMIC_PROBE=1` is set and `garak` is absent, the dynamic probe script exits `2`. Default CI does **not** set this variable, so garak's absence never breaks `make test` or `make agent-verify`. |

Install modelscan and modelaudit into the same venv when you want driver-based scanning:

```bash
.venv/bin/pip install modelscan modelaudit
```

For garak, use the **isolated** `.venv-garak/` environment the Makefile expects:

```bash
python3 -m venv .venv-garak
.venv-garak/bin/pip install garak
```

Override the binary locations with environment variables if needed (see the Environment Variables section below).

---

## Environment variables

| Variable | Purpose | Default |
| -------- | ------- | ------- |
| `HF_BUNDLE_PYTHON` | Interpreter used to spawn `admit-model` / `python -m model_admission`. **Set this when the repo path contains spaces** (e.g. `/root/LLM Scanner/.venv/bin/python`) to avoid `shlex.split` word-break bugs. | None — falls back to `HF_BUNDLE_ADMIT_CMD`, then `shutil.which("admit-model")`, then `sys.executable -m model_admission` |
| `HF_BUNDLE_ADMIT_CMD` | Full command prefix for admit invocations (advanced override). Quoting pitfalls apply for paths with spaces — prefer `HF_BUNDLE_PYTHON` instead. | None |
| `HF_BUNDLE_MIRROR_ALLOWLIST` | Comma-separated mirror hostnames merged into the bundle report's `provenance.mirror_allowlist` field (e.g. `huggingface.co,cdn-lfs.huggingface.co`). Also mergeable via `--mirror-allowlist` CLI flag. | None |
| `HF_BUNDLE_SBOM_URI` | SBOM location (URI or file path) merged into `provenance.sbom_uri`. Overridable per-run via `--sbom-uri`. | None |
| `LLM_SCANNER_DYNAMIC_PROBE` | Set to `1` to enable the Garak lane in `scripts/run_dynamic_probe.py`. Default CI leaves this unset, which causes the probe script to write a `status: disabled` report and exit `0`. | Unset |
| `MODELSCAN_BIN` | Override the `modelscan` executable path (default: `shutil.which("modelscan")`). | None |
| `MODELAUDIT_BIN` | Override the `modelaudit` executable path (default: `shutil.which("modelaudit")`). | None |
| `LLM_SCANNER_TEST_CATALOG` | Absolute path to `llm_security_test_cases/catalog.json` for pytest harnesses. Set automatically by `scripts/run_tests_for_agent.py`. | None |

---

## Policy JSON format

Every `admit-model scan` and `scan-bundle scan` invocation requires a `--policy` JSON file. The policy controls size gates, extension allowlists/denylists, and SHA-256-based bypass lists.

### Fields

| Field | Type | Purpose |
| ----- | ---- | ------- |
| `max_bytes` | integer | Maximum file size in bytes. Files larger than this receive a `policy.gate_violation` finding. Omit or set to `null` / `0` for no size limit. |
| `allowed_extensions` | list of strings | If non-empty, only files whose extension is in this list are admitted. Files with other extensions get a `policy.gate_violation` finding. |
| `forbidden_extensions` | list of strings | Files whose extension appears here are always rejected regardless of `allowed_extensions`. |
| `sha256_allowlist` | list of strings | SHA-256 hex digests that bypass all other policy checks. Useful for pinning known-good artifacts. |

### Example: permissive (policy gate only, no size/extension restrictions)

```json
{
  "max_bytes": 0,
  "allowed_extensions": [],
  "forbidden_extensions": [],
  "sha256_allowlist": []
}
```

### Example: safetensors-only policy

```json
{
  "max_bytes": 5368709120,
  "allowed_extensions": [".safetensors"],
  "forbidden_extensions": [".bin", ".pt", ".pkl", ".pickle", ".onnx", ".h5"],
  "sha256_allowlist": []
}
```

Fixture policies live under [`hf_bundle_scanner/tests/fixtures/`](../hf_bundle_scanner/tests/fixtures/) and [`model-admission/tests/fixtures/`](../model-admission/tests/fixtures/).

---

## Verify your setup

Run the fixture smoke scan — no network, no external tools required:

```bash
make scan-fixture
```

This builds a tiny `safetensors` stub under `hf_bundle_scanner/tests/fixtures/minimal_tree/`, runs `scan-bundle scan` with the permissive policy fixture, and prints a JSON summary to stdout. Expected output:

```json
{
  "aggregate_exit_code": 0,
  "file_count": 1,
  "config_finding_count": 0
}
```

Then run the full test suite:

```bash
make agent-verify
```

A green run ends with `overall_exit=0` and writes `.agent/pytest-last.log`.

---

## Isolated Garak environment (optional)

Live dynamic-probe Makefile targets expect `garak` under `.venv-garak/bin/garak`. That tree is gitignored. Keep the main `.venv/` lean:

```bash
python3 -m venv .venv-garak
.venv-garak/bin/pip install garak
# Then:
make dynamic-probe-live-preflight   # garak --help
make dynamic-probe-live-selfcheck   # garak --version
```

See [docs/PHASE5_DYNAMIC_PROBES.md](PHASE5_DYNAMIC_PROBES.md) for the full dynamic-probe contract.
