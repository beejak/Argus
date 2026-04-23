# Production LLM integration scanner — in-repo roadmap

This file is the **working copy** of the long-horizon plan: phases, YAML-style todos, and pointers to standards. The canonical detailed narrative may also live in a Cursor plan file on your machine; keep this document **updated when phases complete** so WSL/CI/agents do not depend on IDE-local paths.

## Goal

One orchestrated scanner answering: *What can go wrong if we ship this LLM integration to production?* — weights, Hub config, optional dynamic probes, optional runtime guards — with **OSS-by-default** and **optional commercial** backends behind explicit policy (air-gapped CI stays deterministic).

### Phase 0 status (implemented in repo)

- **Code:** [`model_admission/taxonomy.py`](../model-admission/model_admission/taxonomy.py) — `RiskCategory`, OWASP rows, risk-register map, `make_rule_id` / `slugify`.
- **Findings:** [`Finding`](../model-admission/model_admission/report.py) optional `rule_id`, `category`; policy violations emit `policy.gate_violation` + `provenance`.
- **Bundle JSON:** `taxonomy_version: "phase0"` on bundle reports ([`hf_bundle_scanner/report.py`](../hf_bundle_scanner/hf_bundle_scanner/report.py)); schema is **`hf_bundle_scanner.bundle_report.v2`** once phase 1 landed (see below).
- **Docs:** [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md), [LESSONS_LEARNED.md](LESSONS_LEARNED.md).

### Phase 1 status (`phase1-bundle-provenance`, implemented in repo)

- **Schema:** bundle reports use **`schema: hf_bundle_scanner.bundle_report.v2`** with a top-level **`provenance`** object ([`hf_bundle_scanner/provenance.py`](../hf_bundle_scanner/hf_bundle_scanner/provenance.py), [`hf_bundle_scanner/report.py`](../hf_bundle_scanner/hf_bundle_scanner/report.py)).
- **Fields:** `provenance_version: "phase1"`; optional **`hub`** (`repo_id`, `revision`); **`mirror_allowlist`** (env `HF_BUNDLE_MIRROR_ALLOWLIST` and/or CLI / HTTP / MCP); **`sbom`** `{ "uri": … }` (env `HF_BUNDLE_SBOM_URI` or flags); **`manifest_summary`** (`sha256` of canonical manifest JSON + `file_count`) when a manifest is included.
- **Surfaces:** `scan-bundle scan …` ([`cli.py`](../hf_bundle_scanner/hf_bundle_scanner/cli.py)), `POST /v1/scan` ([`http_job.py`](../hf_bundle_scanner/hf_bundle_scanner/http_job.py)), MCP `scan_path` ([`mcp_server.py`](../hf_bundle_scanner/hf_bundle_scanner/mcp_server.py)).
- **Next (later phases):** enforce mirror policy against actual download URLs, attach real SBOM artifacts from CI, and widen bundle provenance with SBOM hashes once `phase6-supplychain-extras` matures.

### Phase 2 status (`phase2-static-drivers`, starter slice in repo)

- **Ephemeral Hub demo:** [`scripts/ephemeral_hub_scan.py`](../scripts/ephemeral_hub_scan.py) + **`make ephemeral-hub-scan`** — download a **small** public Hub snapshot, run **`scan-bundle scan`**, write bundle JSON, **delete** the working tree (opt-in / manual; network).
- **Committed sample reports:** [`docs/sample_reports/`](../docs/sample_reports/) (raw bundle JSON) + **[`docs/sample_reports/actionable/`](../docs/sample_reports/actionable/)** — CSV / HTML / leadership Markdown with **traffic-light**, **1–5 score**, **OWASP LLM touchpoints**, and links to [`THREAT_MODEL_TAXONOMY.md`](THREAT_MODEL_TAXONOMY.md); regenerate via **`make sample-action-sheets`** ([`scripts/export_bundle_action_sheet.py`](../scripts/export_bundle_action_sheet.py)).
- **Configlint expansion:** tokenizer / loader hints including **`use_fast_tokenizer_truthy`**, **`use_auth_token_present`**, **`trust_remote_code`**, **`auto_map`**, invalid JSON — see [`hf_bundle_scanner/configlint.py`](../hf_bundle_scanner/hf_bundle_scanner/configlint.py). Only a **subset** currently escalates **`aggregate_exit_code`** via [`dispatch.py`](../hf_bundle_scanner/hf_bundle_scanner/dispatch.py) (`trust_remote_code_enabled`, `auto_map_custom_classes`, `config_json_invalid`).
- **Next (still phase 2 lane):** optional **ModelScan / ModelAudit** wiring in policy + CI; optional commercial static adapters behind explicit policy.
- **Next phase (phase 3):** **`phase3-configlint-oss`** — widen OSS loader / tokenizer patterns, tighten which configlint **`rule_id`** values are **release-blocking** vs informational, and document severities per org policy pack. *(In progress: e.g. `use_safetensors_disabled` — explicit `use_safetensors: false` in JSON configs; informational in default CI today — see `configlint.py` + `docs/reporting/decision_support_rule_catalog.json`.)*

## Ten capability pillars (summary)

| # | Pillar |
|---|--------|
| 1 | Artifact static scan (ModelScan, ModelAudit, …) |
| 2 | Integrity + provenance (manifest, revision, mirrors) |
| 3 | Config + loader risk (`trust_remote_code`, tokenizer, …) |
| 4 | License / compliance metadata |
| 5 | Secrets + repo hygiene |
| 6 | Dependency / SBOM |
| 7 | Dynamic model probing (Garak-class, opt-in) |
| 8 | App / RAG / agent eval |
| 9 | Runtime guardrails (LLM Guard–class, optional APIs) |
| 10 | Observability + audit |

## Phases (non-overlapping todos)

| Phase | Todo id | Role |
| ----- | ------- | ---- |
| 0 | `phase0-foundations` | Threat model, `rule_id` taxonomy, OWASP mapping, severity→exit contract |
| 1 | `phase1-bundle-provenance` | Bundle JSON vNext + provenance (revision, mirror allowlist, SBOM pointer) |
| 2 | `phase2-static-drivers` | Extra Lane A drivers + optional commercial static adapters |
| 3 | `phase3-configlint-oss` | Configlint + high-risk OSS loader patterns |
| 4 | `phase4-orchestrator-scope` | Job graph + ADR: bundle vs sibling agent/RAG scanner |
| 5 | `phase5-dynamic-staging` | Opt-in Garak/PyRIT-class jobs, budgets, secrets |
| 6 | `phase6-supplychain-extras` | License, secrets scan, deps / SBOM appendices |
| 7 | `phase7-runtime-guards` | Integration guides + optional guard adapters |
| 8 | `phase8-observability` | `scanner_versions`, correlation IDs, ledger/SIEM shape |

**Dependency order:** 0 → (1 ∥ 2 ∥ 3) → 4 → (5 / 6 / 7 as policy-gated) → 8.

## External references (issues)

- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Gen AI — LLM risks](https://genai.owasp.org/llm-top-10/)

## Scanner catalog (representative)

See [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md#scanner-catalog-pointers) for OSS/commercial pointers and how they map to pillars.

## Repo implementation today

- **Shipped:** [`model-admission`](../model-admission/README.md), [`hf_bundle_scanner`](../hf_bundle_scanner/README.md), root [`Makefile`](../Makefile), MCP/HTTP per [`hf_bundle_scanner/docs/hermes-mcp.md`](../hf_bundle_scanner/docs/hermes-mcp.md).
- **Planned:** phases above; track progress in [`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md).
- **Test catalog (LLM Scanner root):** default `llm_security_test_cases/catalog.json` (phase0-aligned, pytest guard); resolution order in [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md#next-run-consumption) (config/CLI → `LLM_SCANNER_TEST_CATALOG` → default). **`add-catalog`** / **`wire-loader`** checklist: [TEST_CASES — todos](TEST_CASES_LLM_SECURITY_SCANNER.md#todos-under-llm-scanner).
