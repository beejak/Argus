# Graph Report - .  (2026-04-25)

## Corpus Check
- 67 files · ~45,546 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 469 nodes · 841 edges · 27 communities detected
- Extraction: 67% EXTRACTED · 33% INFERRED · 0% AMBIGUOUS · INFERRED: 277 edges (avg confidence: 0.76)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]

## God Nodes (most connected - your core abstractions)
1. `validate_job()` - 24 edges
2. `scan_bundle()` - 22 edges
3. `lint_config_file()` - 21 edges
4. `Finding` - 17 edges
5. `_cmd_scan()` - 16 edges
6. `iter_rows()` - 15 edges
7. `ModelScanDriver` - 14 edges
8. `ModelAuditDriver` - 14 edges
9. `main()` - 14 edges
10. `Severity` - 10 edges

## Surprising Connections (you probably didn't know these)
- `test_sha256_file()` --calls--> `sha256_file()`  [INFERRED]
  model-admission/tests/test_policy.py → hf_bundle_scanner/hf_bundle_scanner/snapshot.py
- `append_ledger()` --calls--> `_cmd_scan()`  [INFERRED]
  model-admission/model_admission/ledger.py → hf_bundle_scanner/hf_bundle_scanner/cli.py
- `Finding` --calls--> `_cmd_scan()`  [INFERRED]
  model-admission/model_admission/report.py → hf_bundle_scanner/hf_bundle_scanner/cli.py
- `ScanReport` --calls--> `_cmd_scan()`  [INFERRED]
  model-admission/model_admission/report.py → hf_bundle_scanner/hf_bundle_scanner/cli.py
- `_cmd_scan()` --calls--> `get_driver()`  [INFERRED]
  hf_bundle_scanner/hf_bundle_scanner/cli.py → model-admission/model_admission/drivers/__init__.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (37): ABC, finding_from_severity(), Run scan. Returns (findings, error_message_or_none)., scan(), ScanDriver, Enum, get_driver(), ModelAuditDriver (+29 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (49): build_report(), Phase-5 dynamic probe lane — machine-readable report (v1).  This is **not** a, Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable)., _catalog_rules_index(), _decision_catalog_path(), _decision_legend_rows(), _decision_support_reference_fields(), _format_reference_list() (+41 more)

### Community 2 - "Community 2"
Cohesion: 0.06
Nodes (40): _any_finding_at_or_above(), build_parser(), _cmd_download(), _cmd_manifest(), _cmd_scan(), main(), _min_severity(), CLI: manifest, download, scan (bundle). (+32 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (41): _builtin_excluded(), discover_config_files(), discover_scan_artifacts(), DiscoveryConfig, _included(), iter_files(), _matches_any(), Discover scan targets under a snapshot root. (+33 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (38): _blast_for_config(), _blast_for_exec_summary(), _blast_for_finding(), _blast_for_weight_clean(), _decision_english(), default_demos(), Demo, _html_report_scope_block() (+30 more)

### Community 5 - "Community 5"
Cohesion: 0.12
Nodes (34): build_envelope(), _is_non_empty_str(), load_job(), Orchestrator job document v1 — structure + DAG validation (no scan execution)., Same priority family as bundle aggregates: 4 > 2 > 1 > 0., If ``value`` is non-empty after strip, it must be a RFC 4122 UUID string., Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `, Return a list of human-readable errors; empty means valid. (+26 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (24): llm_security_test_catalog(), Pytest hooks and fixtures for model-admission., Machine-readable LLM security test catalog for the monorepo (see docs/TEST_CASES, Same catalog JSON as hf_bundle_scanner tests (monorepo sibling import)., main(), _pick_python(), Resolve catalog path and export absolute ``LLM_SCANNER_TEST_CATALOG`` for child, Prefer repo-local .venv; fall back to sys.executable (e.g. GitHub Actions). (+16 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (27): ConfigFinding, _is_explicitly_false(), lint_config_file(), lint_tree(), Static checks on Hugging Face-style JSON configs (no execution).  Human-facing, Emit paths where ``use_safetensors`` is explicitly false (pickle-era weight path, Parse JSON and emit high-signal policy hints (not vulnerabilities by themselves), JSON configs sometimes store booleans as strings; treat explicit false only. (+19 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (18): category_for_register_id(), make_rule_id(), owasp_rows(), Phase-0 risk taxonomy: categories, OWASP LLM mapping, stable rule_id prefixes., Normalized category for findings and future policy packs., Stable ``rule_id`` like ``modelscan.unsafe_pickle``., Serializable rows for bundle docs / tooling., RiskCategory (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.27
Nodes (11): format_block(), _load_pool(), _load_state(), main(), GitHub strips most inline CSS; centered HTML still renders cleanly., replace_slogan_region(), _save_state(), _load_rotate_module() (+3 more)

### Community 10 - "Community 10"
Cohesion: 0.22
Nodes (10): build_bundle_provenance(), _manifest_summary(), _parse_csv_hosts(), Phase-1 bundle report provenance (Hub revision, mirror allowlist, SBOM pointer,, Assemble the ``provenance`` object for a bundle report.      Environment (opti, Tests for bundle report provenance (phase 1)., test_build_provenance_env_mirrors_merged(), test_build_provenance_hub_and_sbom() (+2 more)

### Community 11 - "Community 11"
Cohesion: 0.29
Nodes (11): build_markdown(), _config_plain_lines(), default_demos(), Demo, _exit_story(), _hub_label(), main(), _plain_config_message() (+3 more)

### Community 12 - "Community 12"
Cohesion: 0.42
Nodes (9): _admit_argv(), _is_non_empty_str(), main(), _pick_python(), _repo_root(), _resolve(), _scan_argv(), _utc_iso_z() (+1 more)

### Community 13 - "Community 13"
Cohesion: 0.24
Nodes (8): BaseModel, create_app(), Optional thin HTTP API for bundle scan (bind localhost in production)., Request body for POST /v1/scan (module-level model for reliable OpenAPI / valida, run_uvicorn(), ScanBody, test_healthz(), test_scan_endpoint()

### Community 14 - "Community 14"
Cohesion: 0.4
Nodes (4): append_ledger(), Ledger append-only JSONL., test_append_ledger_appends_second_line(), test_append_ledger_writes_one_json_line()

### Community 15 - "Community 15"
Cohesion: 0.67
Nodes (3): Org policy template stays aligned with configlint + dispatch., _repo_root(), test_configlint_policy_template_matches_dispatch()

### Community 16 - "Community 16"
Cohesion: 0.67
Nodes (1): Ensure the shared LLM security test catalog loads in this package's pytest sessi

### Community 17 - "Community 17"
Cohesion: 0.67
Nodes (1): HF bundle scanner: snapshot manifest, discovery, dispatch to model-admission, co

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (0): 

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

### Community 21 - "Community 21"
Cohesion: 1.0
Nodes (0): 

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (1): Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

## Knowledge Gaps
- **80 isolated node(s):** `Pytest hooks and fixtures for model-admission.`, `Same catalog JSON as hf_bundle_scanner tests (monorepo sibling import).`, `Optional: run when modelscan / modelaudit are on PATH.`, `Tiny valid safetensors payload (empty tensor map).`, `More CLI subprocess coverage.` (+75 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 18`** (2 nodes): `main()`, `redact_ephemeral_report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (2 nodes): `summarize_bundle_json.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (2 nodes): `main()`, `git_doctor.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 21`** (2 nodes): `test_mcp_import.py`, `test_fastmcp_import()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 22`** (1 nodes): `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (1 nodes): `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `_cmd_scan()` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 8`, `Community 14`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `scan_bundle()` connect `Community 3` to `Community 0`, `Community 1`, `Community 2`, `Community 7`, `Community 10`?**
  _High betweenness centrality (0.170) - this node is a cross-community bridge._
- **Why does `lint_config_file()` connect `Community 7` to `Community 1`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._
- **Are the 67 inferred relationships involving `str` (e.g. with `test_cli_scan_driver_error_yields_exit_2()` and `test_cli_scan_driver_timeout_yields_exit_2()`) actually correct?**
  _`str` has 67 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `validate_job()` (e.g. with `main()` and `test_fixture_min_validates()`) actually correct?**
  _`validate_job()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `scan_bundle()` (e.g. with `test_scan_bundle_empty_tree()` and `test_scan_bundle_with_weight()`) actually correct?**
  _`scan_bundle()` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `lint_config_file()` (e.g. with `test_trust_remote_code_finding()` and `test_auto_map_finding()`) actually correct?**
  _`lint_config_file()` has 12 INFERRED edges - model-reasoned connections that need verification._