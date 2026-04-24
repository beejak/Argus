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
- **Configlint expansion (phase 2 starter):** tokenizer / loader hints — see [`hf_bundle_scanner/configlint.py`](../hf_bundle_scanner/hf_bundle_scanner/configlint.py); full **`rule_id`** set and policy alignment are tracked under **phase 3** above.
- **ModelScan / ModelAudit (shipped in `model-admission`):** subprocess drivers **`modelscan`**, **`modelaudit`** registered in [`model_admission/drivers/`](../model-admission/model_admission/drivers/); integration tests skip when binaries are absent. **`scan-bundle scan --drivers modelscan,modelaudit`** is supported; **`make drivers-help`** lists driver names + env overrides; bundle aggregate treats missing tooling as **exit 2** (see `hf_bundle_scanner` README + `tests/test_dispatch.py`).
- **Next (still phase 2 lane):** optional commercial static adapters behind explicit policy; richer driver output mapping (`rule_id` / taxonomy on every finding row).

### Phase 3 status (`phase3-configlint-oss`, OSS starter **shipped**)

- **Widen OSS signals:** tokenizer / loader heuristics in [`configlint.py`](../hf_bundle_scanner/hf_bundle_scanner/configlint.py) — including **`trust_remote_code`**, **`auto_map`**, **`use_auth_token`**, **`use_fast_tokenizer`**, **`use_safetensors_disabled`**, **`local_files_only_false`**, **`remote_pretrained_identifier_url`**, **`tokenizer_subfolder_path_traversal`**, **`http_proxies_configured`**, **`torchscript_truthy`**, invalid JSON. Only **`CONFIG_RISK_RULE_IDS`** in [`dispatch.py`](../hf_bundle_scanner/hf_bundle_scanner/dispatch.py) escalates the bundle aggregate today (mirrored in policy JSON below).
- **Org policy template:** [`docs/policy/configlint_rule_defaults.json`](policy/configlint_rule_defaults.json) lists every emitted **`rule_id`** with **`default_aggregate_escalates`** aligned to **`CONFIG_RISK_RULE_IDS`**; drift-tested in **`hf_bundle_scanner/tests/test_configlint_policy_template.py`**. Narrative + citations in [`docs/reporting/decision_support_rule_catalog.json`](reporting/decision_support_rule_catalog.json); exports + plain-English brief stay aligned.
- **Hub discovery:** [`scripts/hub_find_models_under_size.py`](../scripts/hub_find_models_under_size.py) optional **`--probe-configlint`** (metadata search → tiny JSON download → `lint_config_file`).
- **Next (still phase-3 lane / backlog):** optional org overrides consumed by CI; graduate additional `rule_id`s to **`CONFIG_RISK_RULE_IDS`** only with measured false-positive budget; keep widening OSS signals behind the same policy + catalog discipline.

### Phase 4 status (`phase4-orchestrator-scope`, **current**)

- **Goal:** define the **composition layer above** `scan-bundle` — job graph, fan-out/fan-in, budgets, correlation — without turning `hf_bundle_scanner` into an orchestrator (see ADR).
- **Working artifacts:** [`docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md`](adr/0001-bundle-scanner-vs-orchestrator-scope.md) (scope + job-graph sketch + acceptance criteria for the first orchestrator slice).
- **Next:** refine ADR into implementation tickets; add **`run_id` / correlation** story (orchestrator envelope vs optional bundle `provenance` field); stub or reference external job-runner repo only when execution shape is agreed.

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

Starter ADR (bundle vs orchestrator): [`docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md`](adr/0001-bundle-scanner-vs-orchestrator-scope.md).

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

**Dependency order:** 0 → (1 ∥ 2 ∥ 3) → **4 (current)** → (5 / 6 / 7 as policy-gated) → 8.

## External references (issues)

- [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [OWASP Gen AI — LLM risks](https://genai.owasp.org/llm-top-10/)

## Scanner catalog (representative)

See [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md#scanner-catalog-pointers) for OSS/commercial pointers and how they map to pillars.

## Repo implementation today

- **Shipped:** [`model-admission`](../model-admission/README.md), [`hf_bundle_scanner`](../hf_bundle_scanner/README.md), root [`Makefile`](../Makefile), MCP/HTTP per [`hf_bundle_scanner/docs/hermes-mcp.md`](../hf_bundle_scanner/docs/hermes-mcp.md).
- **Planned:** phases above; track progress in [`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md).
- **Test catalog (LLM Scanner root):** default `llm_security_test_cases/catalog.json` (phase0-aligned, pytest guard); resolution order in [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md#next-run-consumption) (config/CLI → `LLM_SCANNER_TEST_CATALOG` → default). **`add-catalog`** / **`wire-loader`** checklist: [TEST_CASES — todos](TEST_CASES_LLM_SECURITY_SCANNER.md#todos-under-llm-scanner).
