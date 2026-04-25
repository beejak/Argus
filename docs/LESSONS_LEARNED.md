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
- **Fix:** Add **`make agent-verify`** → [`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py) writes **`.agent/pytest-last.log`** + **`.agent/pytest-last.exit`** under the repo; the agent **reads those files** from the workspace after the command returns.

## 2026-04-22 — CRLF in `*.sh` breaks Git Bash / `set -u`

- **Mistake:** Checking out or editing `scripts/run-tests-for-agent.sh` with **CRLF** line endings → `set: invalid option`, `$'\r'` in paths, missing `.agent/` output.
- **Fix:** Add [`.gitattributes`](../.gitattributes) (`*.sh text eol=lf`) and move the real runner to **[`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py)**; `make agent-verify` calls **Python**, not bash logic.

## 2026-04-22 — WSL commands from the agent host may not write into the UNC workspace

- **Observation:** `wsl -e bash -lc '... > /root/LLM Scanner/.agent/...'` from the agent terminal did not create files visible to the Read tool on `\\wsl.localhost\...` in this environment (while `Write` to the same UNC path works).
- **Fix:** Prefer **Cursor Remote – WSL** (agent shell runs inside Linux) **or** rely on **GitHub Actions** (`.github/workflows/llm-scanner.yml`) for deterministic verification without depending on the agent’s local terminal bridge.

## 2026-04-23 — `git commit` and `option trailer requires a value`

- **Symptom:** `git commit -m '…'` returns **129** with **`error: option trailer requires a value`** even though you never passed **`--trailer`**.
- **Likely causes:** (1) **Shell / nested host quoting** dropped the `-m` value so a later token was parsed as **`--trailer`** with no value. (2) A broken **`trailer.*`** entry or **`alias.commit=… --trailer …`** in some Git config (`git config --list --show-origin | grep -i trailer`). (3) Rare **environment pollution**; compare against a minimal env (`env -i HOME="$HOME" XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-$HOME/.config}" PATH="/usr/bin:/bin:$PATH" git …`).
- **Fix:** Prefer **`git commit -F msg.txt`**, **`python3 scripts/git_commit_via_file.py 'subject line'`**, or **`make commit-msg MSG='subject line'`**. Inspect config with **`python3 scripts/git_doctor.py`** or **`make git-doctor`**.

## 2026-04-25 — `make commit-msg MSG='chore: …'` truncates at the colon

- **Mistake:** Passing a conventional-commit subject through **`make commit-msg MSG='chore: orchestrator hygiene'`**. **GNU Make** treats **`:`** as special (target/rule syntax), so the variable often ends at **`chore`** and the rest is lost → useless one-word commits.
- **Fix:** Use **`python3 scripts/git_commit_via_file.py "chore: full subject"`** (or **`git commit -F`** with a message file). For **`make commit-msg`**, use **`MSG=one-line-subject-without-colons`** or see the note printed by **`make commit-msg`** with an empty **`MSG`**. Root **`Makefile`** `help` documents this pitfall.

## 2026-04-25 — Multi-option “next steps” only one gets coded

- **Mistake:** Proposing two or three valid follow-ups (e.g. phase-5 depth vs phase-4 fan-out), shipping one, and letting the others live only in chat → later sessions **re-litigate** or **forget** backlog.
- **Fix:** Record non-chosen options in **[`docs/PRODUCTION_SCANNER_ROADMAP.md`](PRODUCTION_SCANNER_ROADMAP.md)** under **Choice capture** (same PR or immediate follow-up). **`AGENTS.md`** reminds agents to do this. Optional: one line in **[`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md)**.

## 2026-04-25 — Mirroring every pytest scenario in the README

- **Mistake:** Trying to keep **README** in sync with every **`pytest`** case name, marker, and edge path → duplicate maintenance, drift, and noise for humans.
- **Fix:** Treat **pytest + `hf_bundle_scanner/tests/`** and **[`docs/TEST_CASES_LLM_SECURITY_SCANNER.md`](TEST_CASES_LLM_SECURITY_SCANNER.md)** (+ **`llm_security_test_cases/catalog.json`**) as the **canonical test story**. README should **map** where verification lives (**`make test`**, **`make agent-verify`**, CI workflow), not clone the matrix. Summaries belong in roadmap / phase docs when they help prioritization.

## 2026-04-25 — Orchestrator dynamic probe: missing JSON on disk

- **Mistake:** Assuming **`run_dynamic_probe.py`** always writes **`--out`** when the subprocess exits `0` (crash, disk full, or killed mid-write).
- **Fix:** Runner treats **missing output file** like a tooling failure: merge with **`worst_exit_code(..., 2)`** so aggregate exit stays honest; same pattern when the report JSON is **unreadable**.

## 2026-04-25 — Budget fields without validation drift into runtime-only failures

- **Mistake:** Treating dynamic budget fields as “optional hints” and validating only at script runtime. Invalid job JSON (`budget_max_probes: 0`, timeout strings) then fails late and opaquely.
- **Fix:** Validate `dynamic_probe.budget_max_probes` and `dynamic_probe.budget_timeout_seconds` as positive integers in orchestrator job validation and mirror checks in the dynamic probe script for direct CLI use.

## 2026-04-25 — Correlation IDs must be pushed to leaf reports, not only envelopes

- **Mistake:** Keeping `run_id` only in the orchestrator envelope while downstream probe artifacts lack correlation fields.
- **Fix:** Forward `run_id` into `run_dynamic_probe.py` and persist it in `dynamic_probe_report.v1`, then assert in tests so cross-artifact joins are stable.

## Template (copy below)

```
### YYYY-MM-DD — <short title>

- **Mistake:** …
- **Fix:** …
```
