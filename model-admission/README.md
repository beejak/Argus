# Model admission

**Canonical workspace (WSL2):** `/root/LLM Scanner/model-admission` — develop, test, and build Docker images only here.

Driver-based **model admission gate** for CI/CD: stable `admit-model` CLI, **policy** (size, extensions, SHA-256 allowlist), and pluggable scanners (**ModelScan**, **ModelAudit**). Swap drivers without changing consumer pipelines.

## Exit codes

| Code | Meaning |
|------|--------|
| 0 | Policy satisfied, no findings at or above `--fail-on` severity, no driver errors |
| 1 | Policy violation and/or findings at/above `--fail-on` |
| 2 | Driver/tooling error (missing binary, timeout, parse failure) |
| 4 | CLI usage error |

## Quick start (local)

```bash
cd model-admission
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pip install modelscan "modelaudit[all-ci]"

admit-model scan \
  --artifact /path/to/model.safetensors \
  --policy examples/policy.example.json \
  --report /tmp/report.json \
  --drivers modelscan,modelaudit
```

Environment:

- `MODELSCAN_BIN`, `MODELAUDIT_BIN` — override executables
- `MODEL_ADMISSION_LEDGER` — append-only JSONL path (also set `--ledger`)
- `PROMPTFOO_DISABLE_TELEMETRY=1`, `NO_ANALYTICS=1` — recommended for ModelAudit (set in Docker)

## Docker worker

```bash
docker build -t model-admission:local .
docker run --rm -v "$PWD:/work:ro" model-admission:local \
  scan --artifact /work/examples/policy.example.json \
  --policy /work/examples/policy.example.json \
  --report /tmp/out.json --drivers modelscan
```

Use a real model file for `--artifact`; the command above only illustrates flags (policy JSON is not a model).

## Policy JSON

- `max_bytes` — reject larger files
- `allowed_extensions` — if set, only these suffixes (lowercase) are allowed
- `forbidden_extensions` — reject matching suffixes
- `sha256_allowlist` — if non-empty, file SHA-256 must be listed

See [examples/policy.example.json](examples/policy.example.json).

## Layout

- `model_admission/cli.py` — CLI
- `model_admission/policy.py` — policy + hashing
- `model_admission/drivers/` — ModelScan / ModelAudit subprocess drivers
- `examples/github-actions.yml` — CI sketch
- `k8s/job.yaml` — Kubernetes Job sketch

## Scope

This package intentionally does **not** integrate with agent frameworks, graph pipelines, or monorepo harnesses. Keep it a small admission tool; call it from CI or a Job.

## Tests

```bash
pip install -e ".[dev]"
pytest -v
```

Integration tests (`pytest -m integration`) run when `modelscan` / `modelaudit` are on `PATH`; otherwise they skip.

**Goals vs test outcomes:** [docs/GOALS_AND_TEST_REPORT.md](docs/GOALS_AND_TEST_REPORT.md)

## Report JSON (`--report`)

Written by `admit-model scan --report /path/to/out.json`. Alongside findings and driver metadata, reports include:

- **`report_generated_at_utc`** — completion instant in UTC (RFC 3339, **`Z`**).
- **`report_generated_at_ist`** — same instant in **Asia/Kolkata** (`+05:30`).

Semantics mirror the monorepo-wide contract described in [docs/DOCUMENTATION.md](../docs/DOCUMENTATION.md) (timestamps are fixed when the scan result is assembled, not on incidental re-serialization).

## References

- [ModelScan](https://github.com/protectai/modelscan)
- [ModelAudit](https://github.com/promptfoo/modelaudit)
