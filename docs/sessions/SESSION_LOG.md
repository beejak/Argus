# Session log (long-horizon memory)

Append-only notes for multi-session work. **No secrets.** Newest entries at the **bottom**.

---

## Template (copy below the line)

```
### YYYY-MM-DD (UTC) — <topic>

- **Phase:** phaseN-…
- **Commands:** `make …`
- **Changes:** …
- **Next:** …
```

### 2026-04-22 — harness docs + Hermes links

- **Phase:** harness only (no phase0–8 code yet).
- **Changes:** Added `docs/PRODUCTION_SCANNER_ROADMAP.md`, `docs/HERMES_AGENTS.md`, `docs/LONG_HORIZON_HARNESS.md`, `docs/MAKEFILE_HARNESS_APPEND.md`, `AGENTS.md`, `CLAUDE.md`, `graphify-out/README.md`; updated `README.md`, `hf_bundle_scanner/docs/hermes-mcp.md`; fixed Hermes link in `.cursor/skills/llm-scanner-long-horizon/SKILL.md`.
- **Next:** (done in follow-up) merge Makefile harness into root.

### 2026-04-22 — Makefile harness merged (agent mode)

- **Phase:** harness.
- **Commands:** `make help`, `make roadmap` (after merge, verify in WSL).
- **Changes:** Root `Makefile`: `help`, `roadmap`, `graphify-update`, `memory-open`. `hf_bundle_scanner/Makefile`: delegate all listed targets to root. README: drop “pending merge” note; LONG_HORIZON + MAKEFILE_HARNESS_APPEND header updated.

### 2026-04-22 — hf_bundle_scanner Makefile fix

- **Issue:** Blank line between `target:` and recipe + broken `.PHONY` continuation → `make: : No such file or directory`.
- **Fix:** Single delegating rule with no blank line before recipe; `.PHONY` on one line. Root `.PHONY` also one line (avoid tab-indented continuation).

### 2026-04-22 — phase0 taxonomy + lessons file

- **Phase:** `phase0-foundations` (initial slice).
- **Changes:** `model_admission.taxonomy`, `Finding.rule_id` / `category`, policy violation `rule_id`, bundle `taxonomy_version`, `docs/THREAT_MODEL_TAXONOMY.md`, `docs/LESSONS_LEARNED.md`, tests `test_taxonomy.py`, roadmap/AGENTS/README/skill links.
- **Next:** phase1 bundle provenance schema + enforcement; populate `rule_id` in drivers incrementally.

### 2026-04-22 — agent-verify + monorepo CI

- **Changes:** `scripts/run-tests-for-agent.sh`, `make agent-verify`, `.agent/README.md`, `.gitignore` for pytest capture, `.github/workflows/llm-scanner.yml`, README note on Remote WSL / CI.
- **Note:** Agent terminal → WSL may not mirror files to UNC; use Remote WSL or CI for reliable verification.

### 2026-04-23 — agent-verify Python runner + CRLF fix

- **Changes:** `scripts/run_tests_for_agent.py` is canonical; `make agent-verify` uses `$(PY)` + that script; bash wrapper delegates to Python; `.gitattributes` forces LF for `*.sh` etc.; CI runs the same script + uploads `.agent/pytest-last.log`.
- **Verified:** `.agent/pytest-last.log` readable in workspace after WSL run — **37 passed, 2 skipped** (model-admission) + **20 passed, 2 deselected** (hf_bundle), `pytest-last.exit=0`.

### 2026-04-23 — Git remote → Argus

- **Remote:** `origin` → `https://github.com/beejak/Argus.git` ([Argus](https://github.com/beejak/Argus)).
- **Commits:** initial monorepo import + `docs: Argus publish guide; expand .gitignore`.
- **Next:** `git push -u origin main` from WSL with GitHub auth (see `docs/PUBLISH_ARGUS.md`).

### 2026-04-23 — README refresh + phase1 bundle provenance

- **Phase:** `phase1-bundle-provenance` (initial slice).
- **Changes:** `hf_bundle_scanner.bundle_report.v2` + `provenance` block (`provenance.py`, CLI / HTTP / MCP), docs (roadmap, threat model, Hermes), beautified root `README.md`.
- **Commands:** `make agent-verify` (or `pytest` under `hf_bundle_scanner` with `.venv`).

### 2026-04-23 — add-catalog (phase0) + taxonomy CI guard

- **Phase:** test catalog / phase0 alignment.
- **Changes:** `llm_security_test_cases/catalog.json` v0.2.0 (`taxonomy_version: phase0`, OWASP LLM01–LLM10 + `RISK_REGISTER` rows), stricter `catalog.schema.json`, `model-admission/tests/test_catalog_taxonomy_alignment.py`, `docs/TEST_CASES_LLM_SECURITY_SCANNER.md` + `PRODUCTION_SCANNER_ROADMAP.md` (add-catalog done).
- **Commands:** `python scripts/run_tests_for_agent.py`; `pytest model-admission/tests/test_catalog_taxonomy_alignment.py`.
- **Next:** `phase1-bundle-provenance` (roadmap).

### 2026-04-22 — actionable exports: decision support vs trust_remote_code + default CI facts

- **Changes:** `export_bundle_action_sheet.py` adds `default_ci_blocks_release`, comparison + expert columns; HTML/MD legend table; `actionable/README.md` + root README pointer.
- **Commands:** `make sample-action-sheets`, `make agent-verify`.

### 2026-04-22 — README roadmap + CLI/scripts tables; roadmap phase 2/3 handoff

- **Changes:** root `README.md` (where we are, doc hub rows, Makefile targets, CLI/env/scripts, outputs); `docs/PRODUCTION_SCANNER_ROADMAP.md` phase 2 bullets + phase 3 next.
- **Commands:** `make agent-verify`. **Git:** `origin/main` already synced before commit.

### 2026-04-22 — leadership exports: OWASP mapping, 1–5 score, traffic light, tighter HTML

- **Changes:** `export_bundle_action_sheet.py` adds taxonomy columns + executive-first HTML (`<details>` for long tables); `BLAST_RADIUS_LEADERSHIP.md` dashboard; README column help.
- **Commands:** `make sample-action-sheets`, `make agent-verify`.

### 2026-04-22 — HTML briefing: pretty-print + GitHub “no render” note + raw.githack preview

- **Changes:** `export_bundle_action_sheet.py` multiline HTML + in-page callout; `actionable/README.md` explains GitHub behavior + preview URL.
- **Commands:** `make sample-action-sheets`.

### 2026-04-22 — leadership blast-radius (prod impact) in CSV/HTML/MD

- **Changes:** `export_bundle_action_sheet.py` adds risk/prod/blast/exec columns + `BLAST_RADIUS_LEADERSHIP.md`; HTML leadership table; README pointers.
- **Commands:** `make sample-action-sheets`, `make agent-verify`.

### 2026-04-22 — actionable sample exports (CSV + HTML briefing)

- **Changes:** `docs/sample_reports/actionable/*`, `scripts/export_bundle_action_sheet.py`, `make sample-action-sheets`, README pointers.
- **Commands:** `make sample-action-sheets`, `make agent-verify`.

### 2026-04-22 — README: human-readable test summary, strict-policy Hub sample, redact helper

- **Changes:** README “What green looks like” table; Live Hub third JSON (safetensors-only policy); `scripts/redact_ephemeral_report.py`; `hf_bundle_scanner/tests/fixtures/policy.safetensors-only.json`; `docs/sample_reports/README.md`.
- **Commands:** `make agent-verify`.

### 2026-04-23 — committed live Hub bundle sample reports + README interpretation

- **Changes:** `docs/sample_reports/*.json` + `docs/sample_reports/README.md`; README section explaining fields + baseline vs demo-risk; `scripts/ephemeral_hub_scan.py` resolves policy paths against repo root (works with scan `cwd`).
- **Commands:** `scripts/ephemeral_hub_scan.py`, `make agent-verify`.

### 2026-04-23 — dedupe GitHub Actions (Docker-only hf-bundle workflow)

- **Changes:** `.github/workflows/hf-bundle-scanner.yml` no longer runs a second pytest matrix; **`llm-scanner.yml`** remains the canonical test workflow. **`hf-bundle-scanner`** workflow keeps **Docker build + CLI smoke** only.

### 2026-04-23 — README hero (minimal pop) + CI pip cache

- **Changes:** Centered README hero (badges, HTML slogan block), note that GitHub ignores custom README fonts; `scripts/rotate_readme_slogan.py` emits centered `<p><i>…</i></p>`; `actions/cache` + `PYTHONUTF8` on CI install step.
- **Commands:** `make agent-verify`.

### 2026-04-23 — slogan pool + rotation workflow + ephemeral Hub scan

- **Phase:** `phase2-static-drivers` starter + harness docs.
- **Changes:** `docs/slogans.json`, `.github/data/slogan_state.json`, `docs/SLOGANS.md`, `scripts/rotate_readme_slogan.py`, `.github/workflows/rotate-slogan.yml`, `scripts/ephemeral_hub_scan.py`, `Makefile`, README (markers + Hub demo + phase2 blurb), roadmap Phase 2 section, `hf_bundle_scanner/tests/test_rotate_readme_slogan.py`.
- **Commands:** `make slogan-dry-run`, `make agent-verify`, optional `OUT=/tmp/x.json make ephemeral-hub-scan` (network).

### 2026-04-23 — README scope/philosophy/reporting + configlint `use_fast_tokenizer`

- **Phase:** docs + small `phase3-configlint-oss` slice.
- **Changes:** Root `README.md` expanded (what repo does / does not, philosophy, how to scan, reporting, tests, help, “keeping README honest”); `configlint` finding `use_fast_tokenizer_truthy`; `tests/test_configlint.py`.
- **Commands:** `make agent-verify`.

### 2026-04-23 — decision-support rule catalog + exporter wiring

- **Phase:** reporting / human decision support.
- **Changes:** `docs/reporting/decision_support_rule_catalog.json` (versioned `rule_id` rows with OWASP GenAI / NIST / HF citations), `docs/reporting/README.md`; `scripts/export_bundle_action_sheet.py` loads catalog for legend + `compared_to_worst_case_loader_risk` / `decision_support_expert` text; CSV columns `reference_citations`, `owasp_genai_catalog_hint`, `decision_catalog_version`; `configlint` module doc points to catalog; `docs/sample_reports/actionable/README.md` documents new columns; regenerated actionable CSV/HTML/MD.
- **Commands:** `python3 scripts/export_bundle_action_sheet.py`, `make agent-verify`.

### 2026-04-24 — phase3 configlint: `use_safetensors_disabled`

- **Phase:** `phase3-configlint-oss` (incremental).
- **Changes:** `configlint` emits `use_safetensors_disabled` when `use_safetensors` is explicitly false in HF-style JSON; catalog row + legend order + exporter validation tuple; `tests/test_configlint.py`; roadmap note; `python3 scripts/export_bundle_action_sheet.py` to refresh actionable outputs.
- **Commands:** `make agent-verify`, `python3 scripts/export_bundle_action_sheet.py`.

### 2026-04-24 — phase3 org policy template + phase2 driver discoverability

- **Phase:** `phase3-configlint-oss` + `phase2-static-drivers`.
- **Changes:** `CONFIG_RISK_RULE_IDS` + `RULE_IDS_EMITTED`; `docs/policy/configlint_rule_defaults.json` + `docs/policy/README.md`; `test_configlint_policy_template.py`; exporter tries `CONFIG_RISK_RULE_IDS` import; `make drivers-help`; `hf_bundle_scanner/README.md` bundle drivers section; `test_dispatch.py` driver exit 2 path; ModelAudit JSON parse unit tests; roadmap + reporting README cross-links.
- **Commands:** `make agent-verify`, `make drivers-help` (after `make install`).

### 2026-04-24 — root README sync (reports + policy + drivers)

- **Changes:** Root `README.md` — reporting / CLI / doc hub / Makefile table aligned with **`CONFIG_RISK_RULE_IDS`**, **`docs/policy/`**, **`docs/reporting/`**, new actionable CSV columns, **`make drivers-help`**, **`MODELSCAN_BIN` / `MODELAUDIT_BIN`**, export **`--repo-root`** note.

### 2026-04-24 — plain-English approver brief + README blurb + phase4 ADR stub

- **Phase:** reporting UX + `phase4-orchestrator-scope` (ADR only).
- **Changes:** Root `README.md` “plain English” section + maintenance note; **`scripts/export_plain_english_brief.py`** → **`docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md`** (does not modify CSV/HTML/`BLAST_RADIUS_LEADERSHIP.md`); **`make plain-english-brief`**, **`make sample-reports-all`**; actionable README + harness + roadmap link; **`docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md`**.
- **Commands:** `make plain-english-brief` or `make sample-reports-all`.

### 2026-04-24 — ephemeral Hub drills (GPT2 + Bart internal test weights)

- **Phase:** harness / ops validation (network).
- **Commands (WSL, venv python):** ephemeral download → `scan-bundle` → delete tree for **`hf-internal-testing/tiny-random-GPT2Model`** (aggregate **0**, includes `pytorch_model.bin`) and **`hf-internal-testing/tiny-random-BartModel`** with **`--inject-demo-tokenizer-risk`** (aggregate **1**, `trust_remote_code_enabled`). Summarized with **`scripts/summarize_bundle_json.py`**.
- **Changes:** **`scripts/summarize_bundle_json.py`**; **`ephemeral_hub_scan.py`** docstring (example repos + venv note); README ephemeral section + helper-scripts table.

### 2026-04-24 — Hub metadata search under 200 MiB

- **Phase:** harness / discovery (network).
- **Changes:** **`scripts/hub_find_models_under_size.py`** (default **`--max-mb 200`**, broad query set, optional **`--probe-trust-remote-code`**); **`make hub-find-models-under-size`** + **`HF_HUB_FIND_FLAGS`**; README + LONG_HORIZON harness + delegating **`hf_bundle_scanner/Makefile`**.
- **Commands:** `make hub-find-models-under-size` or `.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 12`.

### 2026-04-25 — configlint breadth + Hub probe

- **Phase:** configlint / reporting / harness (network optional).
- **Changes:** **`hf_bundle_scanner/configlint.py`** (non-blocking signals: `local_files_only_false`, `remote_pretrained_identifier_url`, `tokenizer_subfolder_path_traversal`, `http_proxies_configured`, `torchscript_truthy`); tests; **`docs/policy/configlint_rule_defaults.json`** + **`docs/reporting/decision_support_rule_catalog.json`**; **`scripts/export_bundle_action_sheet.py`** (catalog drift tuple + legend order); **`scripts/export_plain_english_brief.py`**; **`scripts/hub_find_models_under_size.py`** (**`--probe-configlint`**, **`--probe-trust-remote-code`** as alias); README + LONG_HORIZON harness.
- **Commands:** `make agent-verify`; bounded Hub: `.venv/bin/python scripts/hub_find_models_under_size.py --queries tiny,distil --per-query 4 --max-mb 200 --probe-configlint --max-probes 2`.

### 2026-04-25 — `git commit` / “trailer requires a value” (WSL + PowerShell)

- **Phase:** harness / developer ergonomics.
- **Finding:** Not a stray `trailer.*` line in `~/.gitconfig` / repo config. With `set -x`, PowerShell-sourced `wsl -d Ubuntu -- bash -lc "… git commit --allow-empty …"` can arrive in bash as `git commit --trailer` (mangled argv), which triggers `error: option 'trailer' requires a value`.
- **Mitigation:** From PowerShell, prefer `wsl --% …`, single-quote the whole `bash -lc '…'` script, or run commits inside an interactive WSL shell. **`scripts/git_doctor.py`** documents the pitfall.

### 2026-04-25 — Phase 3 OSS slice closed; Phase 4 orchestrator scope opened

- **Phase:** roadmap / ADR (`phase3-configlint-oss` → **`phase4-orchestrator-scope`**).
- **Gate:** `make agent-verify` green (`.agent/pytest-last.exit` **0**).
- **Changes:** **`docs/PRODUCTION_SCANNER_ROADMAP.md`** — phase 3 marked **shipped** (configlint + policy + catalog + Hub probe); **phase 4** marked **current** with pointers. **`docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md`** — status **accepted for design**; added job-graph sketch, correlation split (orchestrator envelope vs optional bundle provenance), acceptance criteria for first orchestrator slice.

### 2026-04-25 — Orchestrator job v1 (validate + run)

- **Phase:** `phase4-orchestrator-scope` (code slice).
- **Changes:** **`hf_bundle_scanner/hf_bundle_scanner/orchestrator_job.py`**; **`hf_bundle_scanner/tests/test_orchestrator_job.py`** + fixture **`hf_bundle_scanner/tests/fixtures/orchestrator_job_min.json`**; **`scripts/run_orchestrator_job.py`**; **`make orchestrator-validate`**; roadmap line under phase 4.

### 2026-04-25 — Phase 4 envelope tighten + Phase 5 stub + CI harness

- **Phase:** `phase4-orchestrator-scope` (tighten) → **`phase5-dynamic-staging`** (v1 stub).
- **Changes:** UUID **`run_id` / `parent_run_id`** validation; envelope **`llm_scanner.orchestrator_envelope.v2`** (two steps, `artifact_uri`, monotonic UTC timestamps); ADR + roadmap updates; **`hf_bundle_scanner/dynamic_probe_report.py`**, **`scripts/run_dynamic_probe.py`**, **`docs/PHASE5_DYNAMIC_PROBES.md`**; **`scripts/run_tests_for_agent.py`** now runs **orchestrator validate**, **dynamic probe stub**, and **ruff**; **`make dynamic-probe-stub`**; README / hf_bundle_scanner README / `.gitignore` for `.agent/dynamic_probe_last.json`.
- **Commands:** `make test`; `make lint`; `python3 scripts/run_tests_for_agent.py`; `make orchestrator-validate`; `make dynamic-probe-stub`.

### 2026-04-25 — Orchestrator sanity, tests, choice-capture docs

- **Phase:** `phase4-orchestrator-scope` / `phase5-dynamic-staging` (hygiene + process).
- **Changes:** `run_orchestrator_job.py` defensive checks (missing probe report → tooling-style merge), `Makefile` + `run_tests_for_agent.py` validate **both** orchestrator fixtures; extra pytest (`at most one` dynamic step, envelope aggregate exit); roadmap **Choice capture** + recommended next slice **`phase5-garak-config-budgets`**; AGENTS + README + PHASE5 links.
- **Commands:** `make test`, `make lint`, `python3 scripts/run_tests_for_agent.py`.
- **Next:** implement `phase5-garak-config-budgets` or schedule `phase4-admit-model-fanout` per roadmap table.

### 2026-04-25 — Lessons propagation + README vs test matrix

- **Phase:** harness / docs only.
- **Changes:** **`docs/LESSONS_LEARNED.md`** (2026-04-25 lessons: Make colon + commit-msg, choice capture, README vs pytest matrix, missing probe JSON); **`docs/LONG_HORIZON_HARNESS.md`** Makefile rows + **Propagating sanitized lessons** section; **`docs/HERMES_AGENTS.md`** test-inventory + lessons pointer; **`.cursor/skills/llm-scanner-long-horizon/SKILL.md`** checklist; **`README.md`** test row clarifies README is not the full scenario list; **`AGENTS.md`** cross-link for mirroring hints.

### 2026-04-25 — Phase 5 budget + run_id correlation pass

- **Phase:** `phase5-dynamic-staging` (`phase5-garak-config-budgets`, first implementation slice).
- **Changes:** `dynamic_probe_report.v1` now includes optional `budget_timeout_seconds` + `run_id`; `run_dynamic_probe.py` accepts `--run-id`, `--budget-max-probes`, `--budget-timeout-seconds`, enforces positive budget values, and uses timeout budget for `garak --help`; orchestrator job validation enforces positive integer budget fields; orchestrator runner forwards run_id + budget flags; dynamic fixture updated with budget fields; tests expanded (`test_dynamic_probe_report.py`, `test_orchestrator_job.py`); phase-5 and roadmap docs updated.
- **Commands:** `pytest tests/test_dynamic_probe_report.py tests/test_orchestrator_job.py -q`; `make test`; `make lint`; `python3 scripts/run_tests_for_agent.py`.
- **Next:** define real Garak config surface (beyond `--help`) and secret-handling fields while keeping default CI opt-in.

---
