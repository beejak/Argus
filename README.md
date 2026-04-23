# LLM Scanner (WSL2 workspace)

**Upstream GitHub:** [beejak/Argus](https://github.com/beejak/Argus) — first push instructions: [docs/PUBLISH_ARGUS.md](docs/PUBLISH_ARGUS.md).

**Single working directory for this effort:** `/root/LLM Scanner`

- **Per-file admission gate:** [`model-admission/`](model-admission/README.md) — `admit-model`, ModelScan/ModelAudit drivers, policy JSON.
- **HF bundle orchestration:** [`hf_bundle_scanner/`](hf_bundle_scanner/README.md) — manifest, discovery, `scan-bundle` CLI, optional MCP/HTTP.

Do not maintain a second copy under Windows for this project; it causes drift.

**Agents / pytest visibility:** run tests in WSL (or use **Cursor Remote – WSL** so the agent’s shell is Linux). If terminal output is not captured, use **`make agent-verify`** → read **`.agent/pytest-last.log`**, and/or rely on **[`.github/workflows/llm-scanner.yml`](.github/workflows/llm-scanner.yml)** on GitHub.

## Long-horizon harness (agents)

- [AGENTS.md](AGENTS.md) — entry for coding agents.
- [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) — phased roadmap (sync with your Cursor plan as needed).
- [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md) — Hermes / MCP playbook.
- [docs/LONG_HORIZON_HARNESS.md](docs/LONG_HORIZON_HARNESS.md) — session log, graphify, Makefile target list.
- [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md) — phase 0 taxonomy and OWASP mapping.
- [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) — planning/execution lessons (append over time).
- [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md) — append-only session memory (**no secrets**).
- Cursor skill: [`.cursor/skills/llm-scanner-long-horizon/SKILL.md`](.cursor/skills/llm-scanner-long-horizon/SKILL.md)
- Makefile merge notes (historical): [docs/MAKEFILE_HARNESS_APPEND.md](docs/MAKEFILE_HARNESS_APPEND.md)

## Quick commands (root Makefile)

`make install` creates **`./.venv`** (PEP 668–safe on Debian/Ubuntu) and installs `model-admission` + `hf_bundle_scanner` into it. Use the same venv for `make test` / `make scan-fixture`.

Targets like **`scan-fixture`** are defined in the **repo root** [`Makefile`](Makefile). Run `make` from `/root/LLM Scanner`, or from `hf_bundle_scanner/` (that folder has a tiny Makefile that forwards to the root).

```bash
cd "/root/LLM Scanner"
make help
make install
make test
make scan-fixture
make roadmap
make graphify-update
make memory-open
make docker
make docker-bundle
```

## model-admission only

```bash
cd "/root/LLM Scanner/model-admission"
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
docker build -t model-admission:local .
```
