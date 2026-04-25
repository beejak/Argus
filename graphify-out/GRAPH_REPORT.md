# Graph Report - .  (2026-04-25)

## Corpus Check
- 71 files · ~48,248 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 509 nodes · 920 edges · 41 communities detected
- Extraction: 65% EXTRACTED · 35% INFERRED · 0% AMBIGUOUS · INFERRED: 320 edges (avg confidence: 0.76)
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
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]

## God Nodes (most connected - your core abstractions)
1. `validate_job()` - 27 edges
2. `scan_bundle()` - 23 edges
3. `lint_config_file()` - 21 edges
4. `Finding` - 18 edges
5. `_cmd_scan()` - 17 edges
6. `iter_rows()` - 15 edges
7. `ModelScanDriver` - 14 edges
8. `ModelAuditDriver` - 14 edges
9. `main()` - 14 edges
10. `BundleReport` - 13 edges

## Surprising Connections (you probably didn't know these)
- `test_sha256_file()` --calls--> `sha256_file()`  [INFERRED]
  model-admission/tests/test_policy.py → hf_bundle_scanner/hf_bundle_scanner/snapshot.py
- `test_policy_sha256_allowlist()` --calls--> `sha256_file()`  [INFERRED]
  model-admission/tests/test_policy.py → hf_bundle_scanner/hf_bundle_scanner/snapshot.py
- `append_ledger()` --calls--> `_cmd_scan()`  [INFERRED]
  model-admission/model_admission/ledger.py → hf_bundle_scanner/hf_bundle_scanner/cli.py
- `_cmd_scan()` --calls--> `get_driver()`  [INFERRED]
  hf_bundle_scanner/hf_bundle_scanner/cli.py → model-admission/model_admission/drivers/__init__.py
- `_cmd_scan()` --calls--> `scan()`  [INFERRED]
  hf_bundle_scanner/hf_bundle_scanner/cli.py → model-admission/model_admission/drivers/base.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (61): _blast_for_config(), _blast_for_exec_summary(), _blast_for_finding(), _blast_for_weight_clean(), _catalog_rules_index(), _decision_catalog_path(), _decision_english(), _decision_legend_rows() (+53 more)

### Community 1 - "Community 1"
Cohesion: 0.08
Nodes (44): _builtin_excluded(), discover_config_files(), discover_scan_artifacts(), DiscoveryConfig, _included(), iter_files(), _matches_any(), Discover scan targets under a snapshot root. (+36 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (37): Run scan. Returns (findings, error_message_or_none)., Run scan. Returns (findings, error_message_or_none)., _any_finding_at_or_above(), build_parser(), _cmd_manifest(), _cmd_scan(), main(), _min_severity() (+29 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (40): build_envelope(), _is_non_empty_str(), load_job(), Orchestrator job document v1 — structure + DAG validation (no scan execution)., Same priority family as bundle aggregates: 4 > 2 > 1 > 0., If ``value`` is non-empty after strip, it must be a RFC 4122 UUID string., Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `, Return a list of human-readable errors; empty means valid. (+32 more)

### Community 4 - "Community 4"
Cohesion: 0.1
Nodes (25): ABC, finding_from_severity(), scan(), ScanDriver, get_driver(), ModelAuditDriver, ModelScanDriver, ScanDriver (+17 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (28): build_report(), Phase-5 dynamic probe lane — machine-readable report (v1).  This is **not** a, Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable)., _bundle_stats(), _load_json(), main(), _repo_root(), _run() (+20 more)

### Community 6 - "Community 6"
Cohesion: 0.09
Nodes (24): llm_security_test_catalog(), Pytest hooks and fixtures for model-admission., Machine-readable LLM security test catalog for the monorepo (see docs/TEST_CASES, Same catalog JSON as hf_bundle_scanner tests (monorepo sibling import)., main(), _pick_python(), Resolve catalog path and export absolute ``LLM_SCANNER_TEST_CATALOG`` for child, Prefer repo-local .venv; fall back to sys.executable (e.g. GitHub Actions). (+16 more)

### Community 7 - "Community 7"
Cohesion: 0.12
Nodes (26): _is_explicitly_false(), lint_config_file(), lint_tree(), Static checks on Hugging Face-style JSON configs (no execution).  Human-facing, Emit paths where ``use_safetensors`` is explicitly false (pickle-era weight path, Parse JSON and emit high-signal policy hints (not vulnerabilities by themselves), JSON configs sometimes store booleans as strings; treat explicit false only., Emit paths where ``local_files_only`` is explicitly false (may fetch remote Hub (+18 more)

### Community 8 - "Community 8"
Cohesion: 0.1
Nodes (18): category_for_register_id(), make_rule_id(), owasp_rows(), Phase-0 risk taxonomy: categories, OWASP LLM mapping, stable rule_id prefixes., Normalized category for findings and future policy packs., Stable ``rule_id`` like ``modelscan.unsafe_pickle``., Serializable rows for bundle docs / tooling., RiskCategory (+10 more)

### Community 9 - "Community 9"
Cohesion: 0.1
Nodes (19): _cmd_download(), main(), _repo_root(), _manifest_tool(), stdio MCP server exposing bounded scan tools (optional dependency: mcp)., _scan_path_tool(), build_manifest(), FileEntry (+11 more)

### Community 10 - "Community 10"
Cohesion: 0.27
Nodes (11): format_block(), _load_pool(), _load_state(), main(), GitHub strips most inline CSS; centered HTML still renders cleanly., replace_slogan_region(), _save_state(), _load_rotate_module() (+3 more)

### Community 11 - "Community 11"
Cohesion: 0.22
Nodes (10): build_bundle_provenance(), _manifest_summary(), _parse_csv_hosts(), Phase-1 bundle report provenance (Hub revision, mirror allowlist, SBOM pointer,, Assemble the ``provenance`` object for a bundle report.      Environment (opti, Tests for bundle report provenance (phase 1)., test_build_provenance_env_mirrors_merged(), test_build_provenance_hub_and_sbom() (+2 more)

### Community 12 - "Community 12"
Cohesion: 0.29
Nodes (11): build_markdown(), _config_plain_lines(), default_demos(), Demo, _exit_story(), _hub_label(), main(), _plain_config_message() (+3 more)

### Community 13 - "Community 13"
Cohesion: 0.42
Nodes (9): _admit_argv(), _is_non_empty_str(), main(), _pick_python(), _repo_root(), _resolve(), _scan_argv(), _utc_iso_z() (+1 more)

### Community 14 - "Community 14"
Cohesion: 0.24
Nodes (8): BaseModel, create_app(), Optional thin HTTP API for bundle scan (bind localhost in production)., Request body for POST /v1/scan (module-level model for reliable OpenAPI / valida, run_uvicorn(), ScanBody, test_healthz(), test_scan_endpoint()

### Community 15 - "Community 15"
Cohesion: 0.47
Nodes (5): _minimal_safetensors(), Optional: run when modelscan / modelaudit are on PATH., Tiny valid safetensors payload (empty tensor map)., test_modelaudit_on_minimal_safetensors(), test_modelscan_on_minimal_safetensors()

### Community 16 - "Community 16"
Cohesion: 0.4
Nodes (4): append_ledger(), Ledger append-only JSONL., test_append_ledger_appends_second_line(), test_append_ledger_writes_one_json_line()

### Community 17 - "Community 17"
Cohesion: 0.6
Nodes (3): _run_admit(), test_cli_scan_no_drivers_passes(), test_cli_scan_policy_forbidden_extension_fails()

### Community 18 - "Community 18"
Cohesion: 0.6
Nodes (4): More CLI subprocess coverage., _run(), test_ledger_via_env_without_flag(), test_unknown_driver_exits_4()

### Community 19 - "Community 19"
Cohesion: 0.67
Nodes (3): Org policy template stays aligned with configlint + dispatch., _repo_root(), test_configlint_policy_template_matches_dispatch()

### Community 20 - "Community 20"
Cohesion: 0.67
Nodes (1): Ensure the shared LLM security test catalog loads in this package's pytest sessi

### Community 21 - "Community 21"
Cohesion: 0.67
Nodes (1): HF bundle scanner: snapshot manifest, discovery, dispatch to model-admission, co

### Community 22 - "Community 22"
Cohesion: 1.0
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 1.0
Nodes (0): 

### Community 24 - "Community 24"
Cohesion: 1.0
Nodes (0): 

### Community 25 - "Community 25"
Cohesion: 1.0
Nodes (0): 

### Community 26 - "Community 26"
Cohesion: 1.0
Nodes (0): 

### Community 27 - "Community 27"
Cohesion: 1.0
Nodes (0): 

### Community 28 - "Community 28"
Cohesion: 1.0
Nodes (1): Phase2 static drivers: missing ModelScan binary → admit exit 2 → bundle aggregat

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Priority: any 4 (usage) > 2 (driver) > 1 (policy/findings) > 0.

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (1): If configlint reports risky settings, treat as exit 1 unless bundle already wors

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (1): Phase2 static drivers: missing ModelScan binary → admit exit 2 → bundle aggregat

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (1): Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (1): Priority: any 4 (usage) > 2 (driver) > 1 (policy/findings) > 0.

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, `

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).

## Knowledge Gaps
- **93 isolated node(s):** `Pytest hooks and fixtures for model-admission.`, `Same catalog JSON as hf_bundle_scanner tests (monorepo sibling import).`, `Optional: run when modelscan / modelaudit are on PATH.`, `Tiny valid safetensors payload (empty tensor map).`, `More CLI subprocess coverage.` (+88 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 22`** (2 nodes): `main()`, `redact_ephemeral_report.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 23`** (2 nodes): `summarize_bundle_json.py`, `main()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 24`** (2 nodes): `main()`, `git_doctor.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 25`** (2 nodes): `test_mcp_import.py`, `test_fastmcp_import()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 26`** (1 nodes): `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 27`** (1 nodes): `__main__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 28`** (1 nodes): `Phase2 static drivers: missing ModelScan binary → admit exit 2 → bundle aggregat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 29`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (1 nodes): `Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (1 nodes): `Priority: any 4 (usage) > 2 (driver) > 1 (policy/findings) > 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `If configlint reports risky settings, treat as exit 1 unless bundle already wors`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `Phase2 static drivers: missing ModelScan binary → admit exit 2 → bundle aggregat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `Priority: any 4 (usage) > 2 (driver) > 1 (policy/findings) > 0.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Build orchestrator envelope JSON (v2).      ``steps`` follow ADR 0001: ``id``, ``
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Return a ``dynamic_probe_report.v1`` object (plain dict, JSON-serializable).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `scan_bundle()` connect `Community 1` to `Community 0`, `Community 2`, `Community 5`, `Community 7`, `Community 9`, `Community 11`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Why does `_cmd_scan()` connect `Community 2` to `Community 0`, `Community 1`, `Community 4`, `Community 5`, `Community 8`, `Community 9`, `Community 16`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `validate_job()` connect `Community 3` to `Community 0`, `Community 13`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 73 inferred relationships involving `str` (e.g. with `test_cli_scan_driver_error_yields_exit_2()` and `test_cli_scan_driver_timeout_yields_exit_2()`) actually correct?**
  _`str` has 73 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `validate_job()` (e.g. with `main()` and `test_fixture_min_validates()`) actually correct?**
  _`validate_job()` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Are the 20 inferred relationships involving `scan_bundle()` (e.g. with `test_scan_bundle_empty_tree()` and `test_scan_bundle_with_weight()`) actually correct?**
  _`scan_bundle()` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `lint_config_file()` (e.g. with `test_trust_remote_code_finding()` and `test_auto_map_finding()`) actually correct?**
  _`lint_config_file()` has 12 INFERRED edges - model-reasoned connections that need verification._