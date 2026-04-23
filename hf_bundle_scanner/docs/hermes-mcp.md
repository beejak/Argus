# Hermes Agent and MCP

Deterministic scanning lives in Python (`hf_bundle_scanner`, `model-admission`). Hermes Agent ([NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent)) should only **orchestrate** bounded operations.

Long-horizon agent playbook (MCP boundaries, session log, phases): [../../docs/HERMES_AGENTS.md](../../docs/HERMES_AGENTS.md) and [../../docs/LONG_HORIZON_HARNESS.md](../../docs/LONG_HORIZON_HARNESS.md).

## Makefile (no MCP)

From `/root/LLM Scanner`:

```bash
make install
make test
make scan-fixture
```

If `admit-model` is not on `PATH`, set either:

- **`HF_BUNDLE_PYTHON`** — absolute path to the interpreter (may contain spaces). Optional **`HF_BUNDLE_ADMIT_MODULE`** (default `model_admission`). Example: `HF_BUNDLE_PYTHON="/root/LLM Scanner/.venv/bin/python"`.
- **`HF_BUNDLE_ADMIT_CMD`** — full prefix string parsed with **`shlex.split`**. **Do not** use this for an unquoted interpreter path that contains spaces (words split at spaces); use `HF_BUNDLE_PYTHON` instead.

## stdio MCP server

Install extras: `pip install -e "./hf_bundle_scanner[mcp]"`.

Run:

```bash
hf-bundle-mcp
```

Tools:

- `scan_path(root, policy, drivers="")` — full bundle JSON + aggregate exit semantics inside JSON (process exit is separate).
- `build_manifest_json(root)` — recursive SHA-256 manifest.

Point Hermes MCP client at this stdio server per [Hermes MCP docs](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp).

## Optional HTTP

```bash
pip install -e "./hf_bundle_scanner[http]"
HF_BUNDLE_HTTP_HOST=127.0.0.1 HF_BUNDLE_HTTP_PORT=8765 hf-bundle-http
```

- `GET /healthz`
- `POST /v1/scan` with JSON body `{ "snapshot_root": "/abs/path", "policy_path": "/abs/path", "drivers": "", "timeout": 600, "fail_on": "MEDIUM", "include_manifest": true }` (extra keys ignored).

Bind to localhost unless you add auth and TLS.
