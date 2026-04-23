# Lessons learned (planning + execution)

Append **newest lessons at the bottom** under a dated heading. This file is the feedback loop for agents and humans so we do not repeat the same mistakes.

---

## 2026-04-22 — Makefile delegation in `hf_bundle_scanner/`

- **Mistake:** Blank line between a rule’s `target:` line and its tabbed recipe in GNU make. The recipe detached from the rule; `make` then tried to interpret the next tab line oddly → **`: No such file or directory`**.
- **Fix:** Put the recipe **immediately** under the rule header (no empty lines).
- **Mistake:** `.PHONY: foo \` continued on a line that **started with a tab** (`\troadmap`). Tabs start recipes; continuations should use **spaces** only, or put `.PHONY` on **one line**.
- **Fix:** Single-line `.PHONY` in root and subdir Makefiles.

## 2026-04-22 — Plan-only vs agent mode

- **Mistake:** Assuming all harness files can be edited in one mode. **Plan-only** flows blocked **non-markdown** edits (e.g. root `Makefile`), so work split across a bridge doc and real Makefile merge later.
- **Fix:** When you need `Makefile`, scripts, or binaries, run in **Agent mode** (or equivalent) or merge manually from [`MAKEFILE_HARNESS_APPEND.md`](MAKEFILE_HARNESS_APPEND.md).

## 2026-04-22 — Paths and spaces (WSL)

- **Mistake:** `HF_BUNDLE_ADMIT_CMD` with an **unquoted** interpreter path containing spaces → `shlex.split` breaks argv (`PermissionError` on bogus paths).
- **Fix:** Prefer **`HF_BUNDLE_PYTHON`** (absolute path to `.venv/bin/python`) and optional **`HF_BUNDLE_ADMIT_MODULE`**; document in Hermes / bundle docs.

## 2026-04-22 — Cursor skill relative links

- **Mistake:** Linking `hf_bundle_scanner/docs/...` from `.cursor/skills/.../SKILL.md` with only `../..` (lands in `.cursor/`, not repo root).
- **Fix:** From `.cursor/skills/<skill>/SKILL.md`, use **`../../../`** to reach repo root.

## 2026-04-22 — “All scanners” wording

- **Mistake:** Implying an exhaustive global vendor list. The market moves weekly; lists go stale and create false completeness.
- **Fix:** Publish a **representative catalog** + explicit **non-exhaustive** disclaimer; link OWASP / official docs for issue taxonomies.

## 2026-04-22 — Phase 0 scope creep

- **Mistake:** Implementing dynamic red-team (Garak) in default CI “because security.” It is slow, flaky, and needs secrets.
- **Fix:** **Phase 5** stays **opt-in** (env / policy / staging); phase 0 is **taxonomy + docs + optional JSON fields**, not new subprocess scanners unless explicitly scheduled.

## 2026-04-22 — `Finding.to_dict` and `asdict`

- **Mistake:** Using `dataclasses.asdict()` for `Finding` while adding optional JSON fields (`rule_id`, `category`) would either omit control over omission or dump large nested defaults awkwardly.
- **Fix:** Build `to_dict()` explicitly: always emit core fields; emit `raw`, `rule_id`, `category` only when non-empty so existing JSON consumers stay lean.

---

## 2026-04-22 — Agent cannot see pytest stdout

- **Mistake:** Assuming `run_terminal_cmd` always returns streamed pytest output to the agent; in some Cursor setups stdout is empty while exit code is `0`.
- **Fix:** Add **`make agent-verify`** → [`scripts/run-tests-for-agent.sh`](../scripts/run-tests-for-agent.sh) writes **`.agent/pytest-last.log`** + **`.agent/pytest-last.exit`** under the repo; the agent **reads those files** from the workspace after the command returns.

## 2026-04-22 — CRLF in `*.sh` breaks Git Bash / `set -u`

- **Mistake:** Checking out or editing `scripts/run-tests-for-agent.sh` with **CRLF** line endings → `set: invalid option`, `$'\r'` in paths, missing `.agent/` output.
- **Fix:** Add [`.gitattributes`](../.gitattributes) (`*.sh text eol=lf`) and move the real runner to **[`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py)**; `make agent-verify` calls **Python**, not bash logic.

## 2026-04-22 — WSL commands from the agent host may not write into the UNC workspace

- **Observation:** `wsl -e bash -lc '... > /root/LLM Scanner/.agent/...'` from the agent terminal did not create files visible to the Read tool on `\\wsl.localhost\...` in this environment (while `Write` to the same UNC path works).
- **Fix:** Prefer **Cursor Remote – WSL** (agent shell runs inside Linux) **or** rely on **GitHub Actions** (`.github/workflows/llm-scanner.yml`) for deterministic verification without depending on the agent’s local terminal bridge.

## Template (copy below)

```
### YYYY-MM-DD — <short title>

- **Mistake:** …
- **Fix:** …
```
