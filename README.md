# LLM Scanner

**Production-minded scanning for Hugging Face–style model bundles** — static admission, config risk, and a path toward dynamic probes and runtime guardrails. The public mirror of this monorepo is **[Argus on GitHub](https://github.com/beejak/Argus)** ([publish notes](docs/PUBLISH_ARGUS.md)).

> **One working tree:** keep a single checkout (for example `/root/LLM Scanner` on WSL). A duplicate under Windows `\\wsl$\\…` plus a UNC workspace invites drift and confusing pytest output.

---

## What lives here

| Area | Role |
| ---- | ---- |
| [**model-admission**](model-admission/README.md) | Per-file gate: `admit-model`, policy JSON, ModelScan / ModelAudit drivers, taxonomy-aware `Finding` fields. |
| [**hf_bundle_scanner**](hf_bundle_scanner/README.md) | Bundle orchestration: manifest, discovery, `scan-bundle` CLI, configlint, aggregate JSON report (**schema v2** + **phase‑1 provenance**), optional MCP / HTTP. |
| [**llm_security_test_cases**](llm_security_test_cases/catalog.json) | Machine-readable test catalog (OWASP + risk register), consumed by pytest and [`scripts/run_tests_for_agent.py`](scripts/run_tests_for_agent.py). |
| [**Makefile**](Makefile) | `make install`, `make test`, `make agent-verify`, Docker targets, and harness helpers. |

---

## Quick start (WSL)

```bash
cd "/root/LLM Scanner"
make help
make install
make agent-verify
```

`make install` creates **`.venv/`** (PEP 668–friendly) and installs both Python packages in editable mode. Use the same interpreter for `make test`, `make scan-fixture`, and Hermes / MCP (`HF_BUNDLE_PYTHON`).

---

## Documentation hub

| Topic | Where |
| ----- | ----- |
| Agent entry + commands | [AGENTS.md](AGENTS.md) |
| Phased roadmap (0–8) | [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) |
| Threat model & OWASP mapping | [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md) |
| Pytest & test-case index | [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md) |
| Hermes / MCP boundaries | [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md) |
| Harness: Makefile, session log, graphify | [docs/LONG_HORIZON_HARNESS.md](docs/LONG_HORIZON_HARNESS.md) |
| Execution lessons | [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) |
| Append-only session memory | [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md) |
| Cursor long-horizon skill | [`.cursor/skills/llm-scanner-long-horizon/SKILL.md`](.cursor/skills/llm-scanner-long-horizon/SKILL.md) |

---

## Agents, terminals, and CI

- Prefer **Cursor Remote – WSL** (or run commands inside Linux) so paths and pytest output match the repo on disk.
- If the agent terminal shows **empty stdout** but exit `0`, use **`make agent-verify`** and read **`.agent/pytest-last.log`** (see [`.agent/README.md`](.agent/README.md)).
- **[`.github/workflows/llm-scanner.yml`](.github/workflows/llm-scanner.yml)** runs the same harness on GitHub for a second source of truth.

---

## Common Makefile targets

| Target | Purpose |
| ------ | ------- |
| `make install` | Create `.venv` and install `model-admission` + `hf_bundle_scanner[mcp,http]` |
| `make test` | Pytest for `hf_bundle_scanner` (excludes integration) |
| `make agent-verify` | Both packages; writes `.agent/pytest-last.log` |
| `make scan-fixture` | Minimal bundle scan smoke |
| `make git-doctor` | Diagnose `git commit` / trailer config issues |
| `make commit-msg MSG='…'` | Commit via `git commit -F` (safer quoting) |

You can also run `make` from **`hf_bundle_scanner/`**; that Makefile forwards to the root.

---

## `model-admission` only (from its directory)

```bash
cd "/root/LLM Scanner/model-admission"
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
docker build -t model-admission:local .
```

---

_No Tokens were harmed during making of this repo._
