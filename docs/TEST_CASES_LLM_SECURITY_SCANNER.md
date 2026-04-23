# Test cases for LLM security scanner

This file is the **in-repo home** for the test-case and risk coverage you asked for under that title in chat. It **indexes** pytest suites, taxonomy, and standards—so you are not dependent on a single Cursor thread.

## File layout (LLM Scanner workspace root)

Treat the **LLM Scanner monorepo root** (the folder that contains `model-admission/`, `hf_bundle_scanner/`, and `Makefile`) as the workspace anchor. Paths below are written that way: **full paths** for the schema (so editors and CI can paste them), **relative paths** for code (portable in git).

| Kind | Path |
| ---- | ---- |
| Workspace root | e.g. WSL `/root/LLM Scanner` or Windows `\\wsl.localhost\Ubuntu\root\LLM Scanner` |
| Catalog (default) | `<workspace>/llm_security_test_cases/catalog.json` |
| JSON Schema (canonical) | `<workspace>/llm_security_test_cases/catalog.schema.json` — full example on WSL: `/root/LLM Scanner/llm_security_test_cases/catalog.schema.json` |
| Resolver (code) | [`hf_bundle_scanner/hf_bundle_scanner/test_catalog.py`](../hf_bundle_scanner/hf_bundle_scanner/test_catalog.py) |
| Resolver tests | [`hf_bundle_scanner/tests/test_test_catalog.py`](../hf_bundle_scanner/tests/test_test_catalog.py) |
| Catalog ↔ taxonomy guard | [`model-admission/tests/test_catalog_taxonomy_alignment.py`](../model-admission/tests/test_catalog_taxonomy_alignment.py) |

## Next-run consumption

The **next test run** (local `make agent-verify` / CI) should resolve the machine-readable catalog in this order:

1. **Config or CLI** — explicit path passed by the harness or CLI (highest precedence; not all entrypoints expose this yet).
2. **Environment override** — `LLM_SCANNER_TEST_CATALOG`: absolute path, or path relative to the **repo root**.
3. **Default** — `llm_security_test_cases/catalog.json` **next to the repo root**, so CI clones and local checkouts pick it up without extra wiring.

Implementation today: [`resolve_test_catalog_path()`](../hf_bundle_scanner/hf_bundle_scanner/test_catalog.py) and [`load_test_catalog_json()`](../hf_bundle_scanner/hf_bundle_scanner/test_catalog.py); session fixture **`llm_security_test_catalog`** in [`hf_bundle_scanner/tests/conftest.py`](../hf_bundle_scanner/tests/conftest.py) and [`model-admission/tests/conftest.py`](../model-admission/tests/conftest.py); [`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py) logs and sets absolute **`LLM_SCANNER_TEST_CATALOG`** for each pytest subprocess so CI and `make agent-verify` share one resolution.

## Automated tests (today)

| Area | Location | What it proves |
| ---- | -------- | -------------- |
| Admission gate | [`model-admission/tests/`](../model-admission/tests/) | Policy, CLI exits, drivers (incl. fault injection), ledger, **taxonomy** (`test_taxonomy.py`), `Finding` JSON |
| Bundle orchestration | [`hf_bundle_scanner/tests/`](../hf_bundle_scanner/tests/) | Manifest, discovery, dispatch, configlint, HTTP, MCP import, aggregate exits |
| Optional Hub smoke | [`hf_bundle_scanner/tests/test_integration_chwoo_collection.py`](../hf_bundle_scanner/tests/test_integration_chwoo_collection.py) | Real HF download + bundle scan when `HF_BUNDLE_CHWOO_SCAN=1` |
| Full matrix (local) | `make agent-verify` → [`.agent/pytest-last.log`](../.agent/README.md) | Both packages in one log |

## Risk / “test case” catalog (normative docs)

| Topic | Doc |
| ----- | --- |
| Pillars, phases, OWASP mapping, risk register | [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md) |
| Severity, categories, `rule_id`, OWASP table | [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md) |
| Prompt poisoning, bias, political/reputational policy | Same roadmap + threat model sections |
| Scanner market / backends (representative) | Roadmap “scanner catalog” + [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md) |

## Standards to align new **manual** or **dynamic** test packs

- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Gen AI — LLM risks](https://genai.owasp.org/llm-top-10/)

## Planned (not default CI yet)

- **Phase 5 — dynamic probes** (Garak-class): jailbreak, injection, leakage, toxicity; **opt-in** only (`phase5-dynamic-staging` in roadmap).
- **Phase 8 — observability**: which pack ran, correlation IDs in bundle JSON.

### Todos (under LLM Scanner)

- [x] **add-catalog** — Default **`llm_security_test_cases/catalog.json`** (v0.2.0, **`taxonomy_version`: phase0**) lists OWASP LLM01–LLM10 rows plus **RISK_REGISTER**-tagged packs; **[`catalog.schema.json`](../llm_security_test_cases/catalog.schema.json)** constrains `category` to `RiskCategory`. CI enforces alignment via **`test_catalog_taxonomy_alignment.py`**. The **next run** still honors **env / harness** overrides.
- [x] **wire-loader** — Pytest + [`run_tests_for_agent.py`](../scripts/run_tests_for_agent.py) use **`resolve_test_catalog_path()`** / **`load_test_catalog_json()`** with **config/CLI → `LLM_SCANNER_TEST_CATALOG` → default catalog** (harness exports the resolved absolute path for subprocesses). Optional follow-up: expose catalog path on other CLIs (e.g. `scan-bundle`).

## How to extend

1. Add a **pytest** under the right package if the behavior is deterministic and fast.  
2. Add a **row** to the risk register / OWASP mapping in code ([`model_admission/taxonomy.py`](../model-admission/model_admission/taxonomy.py)) and narrative in [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md).  
3. For slow/network tests: **marker + env gate** (see chwoo test pattern).

When you add substantial new cases, append a line to [`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md) and run **`make agent-verify`** before push.
