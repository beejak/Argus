# Production LLM integration scanner — in-repo roadmap

This file is the **working copy** of the long-horizon plan: phases, YAML-style todos, and pointers to standards. The canonical detailed narrative may also live in a Cursor plan file on your machine; keep this document **updated when phases complete** so WSL/CI/agents do not depend on IDE-local paths.

## Goal

One orchestrated scanner answering: *What can go wrong if we ship this LLM integration to production?* — weights, Hub config, optional dynamic probes, optional runtime guards — with **OSS-by-default** and **optional commercial** backends behind explicit policy (air-gapped CI stays deterministic).

### Phase 0 status (implemented in repo)

- **Code:** [`model_admission/taxonomy.py`](../model-admission/model_admission/taxonomy.py) — `RiskCategory`, OWASP rows, risk-register map, `make_rule_id` / `slugify`.
- **Findings:** [`Finding`](../model-admission/model_admission/report.py) optional `rule_id`, `category`; policy violations emit `policy.gate_violation` + `provenance`.
- **Bundle JSON:** `taxonomy_version: "phase0"` on bundle reports ([`hf_bundle_scanner/report.py`](../hf_bundle_scanner/hf_bundle_scanner/report.py)).
- **Docs:** [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md), [LESSONS_LEARNED.md](LESSONS_LEARNED.md).

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
