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

---
