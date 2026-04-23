# Threat model and taxonomy (phase 0)

This document is the **human-readable** source for normalized risk language in code: [`model_admission/taxonomy.py`](../model-admission/model_admission/taxonomy.py) and optional fields on [`Finding`](../model-admission/model_admission/report.py) (`rule_id`, `category`).

## Exit semantics (unchanged)

| Code | Meaning |
| ---- | ------- |
| 0 | Clean at configured `--fail-on` floor |
| 1 | Policy violation and/or findings at/above floor |
| 2 | Driver / tooling error |
| 4 | CLI usage error |

Severity order for `--fail-on` (lowest to highest): `INFO`, `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`. The CLI uses an explicit numeric order map, not lexicographic string order.

## Risk categories (`RiskCategory`)

| Value | Use |
| ----- | --- |
| `artifact` | Serialized weights / unsafe formats (ModelScan, ModelAudit, …) |
| `provenance` | Integrity, mirrors, revision pinning, admission policy gate |
| `config` | `config.json`, tokenizer, `trust_remote_code`, `auto_map`, … |
| `supply_chain` | Dependencies, SBOM, training-data lineage (when present) |
| `dynamic` | Runtime probes: injection, RAG weakness, agents (opt-in jobs) |
| `runtime` | Live guards, output handling, downstream sinks |
| `content_policy` | PII, harm, misinformation, org policy packs |
| `fairness` | Slice / locale behavioral eval (not static tensor “bias meters”) |
| `meta` | Cost/DoS, drift monitoring hooks, observability-only |

## Stable `rule_id` convention

Format: ``{source}.{slug}`` where `source` is slugified driver or subsystem (e.g. `modelscan`, `policy`, `configlint`) and `slug` is a short snake_case topic. Helpers: `make_rule_id()` / `slugify()` in `taxonomy.py`.

## OWASP LLM Applications (2025 framing)

Machine-readable rows: `model_admission.taxonomy.owasp_rows()` and `OWASP_LLM_2025`.

**Verify titles** against the official project: [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) and [Gen AI LLM risks](https://genai.owasp.org/llm-top-10/).

| Code | Slug (internal) | Default category |
| ---- | ---------------- | ---------------- |
| LLM01 | `prompt_injection` | `dynamic` |
| LLM02 | `sensitive_information_disclosure` | `content_policy` |
| LLM03 | `supply_chain` | `supply_chain` |
| LLM04 | `data_and_model_poisoning` | `supply_chain` |
| LLM05 | `improper_output_handling` | `runtime` |
| LLM06 | `excessive_agency` | `dynamic` |
| LLM07 | `system_prompt_leakage` | `config` |
| LLM08 | `vector_and_embedding_weaknesses` | `dynamic` |
| LLM09 | `misinformation` | `content_policy` |
| LLM10 | `unbounded_consumption` | `meta` |

## Risk register concept ids

Map free-text planning ids to categories via `category_for_register_id()` and `RISK_REGISTER` in `taxonomy.py` (includes `poison_rag_corpus`, `adapter_trojan`, `bias_fairness_slice`, …).

## Bundle JSON

[`hf_bundle_scanner` bundle reports](../hf_bundle_scanner/hf_bundle_scanner/report.py) include **`taxonomy_version": "phase0"`** alongside `schema: hf_bundle_scanner.bundle_report.v1` so consumers can gate on taxonomy-aware fields as drivers populate `rule_id` / `category`.
