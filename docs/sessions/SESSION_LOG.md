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

---
