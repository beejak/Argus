---
name: llm-hf-scanner
description: HF snapshot manifest, bundle discovery, model-admission dispatch, configlint, aggregate report, Makefile harness, optional Hermes MCP/HTTP.
---

# LLM HF bundle scanner

## Layout (LLM Scanner repo)

| Area | Path | Owns |
|------|------|------|
| Per-file gate | `model-admission/model_admission/` | Policy, ModelScan/ModelAudit drivers, `admit-model` |
| Bundle orchestration | `hf_bundle_scanner/hf_bundle_scanner/` | `snapshot`, `discovery`, `dispatch`, `configlint`, `report`, `cli`, optional `mcp_server`, `http_job` |
| Harness | `/root/LLM Scanner/Makefile` | `install`, `test`, `scan-fixture`, `docker`, `docker-bundle` |

## Contracts

- **Manifest JSON** (`scan-bundle manifest`): `{ root, file_count, files: [{ relpath, size_bytes, sha256 }] }`.
- **Bundle report** (`scan-bundle scan`): `{ schema: hf_bundle_scanner.bundle_report.v1, aggregate_exit_code, file_scans[], config_findings[], manifest? }`.
- **Exit codes** (aggregate): `4` usage from child, `2` driver errors, `1` policy/findings/config risk, `0` pass.

## Commands

```bash
cd "/root/LLM Scanner"
make install && make test
make scan-fixture
```

CLI module: `python -m hf_bundle_scanner` with subcommands `manifest`, `download`, `scan`. For interpreters whose path contains spaces, set **`HF_BUNDLE_PYTHON`** (see `dispatch.admit_argv` and `docs/hermes-mcp.md`).

Hermes / other agents: see [hf_bundle_scanner/docs/hermes-mcp.md](../../../hf_bundle_scanner/docs/hermes-mcp.md).

## Agent handoffs (Cursor)

| Focus | Module files | Input | Output |
|-------|----------------|--------|--------|
| Snapshot | `snapshot.py` | directory or Hub repo | manifest dict / downloaded tree |
| Discovery | `discovery.py` | root path | lists of scan artifacts vs config files |
| Dispatch | `dispatch.py` | root + policy | `BundleReport` |
| Configlint | `configlint.py` | config JSON paths | `ConfigFinding` list |
| Report | `report.py` | per-file admit JSONs | aggregate exit + bundle dict |

Do not move verdict logic into LLM prompts; use `aggregate_exit_code` from JSON.
