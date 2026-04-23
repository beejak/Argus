# Agent instructions (LLM Scanner)

## Scope

This monorepo contains:

- **`model-admission/`** — `admit-model` CLI, policy JSON, ModelScan / ModelAudit drivers.
- **`hf_bundle_scanner/`** — Bundle manifest, discovery, `scan-bundle` / `hf_bundle_scanner` CLI, optional **MCP** and **HTTP**.

## Must read before large changes

- [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) — phased long-horizon plan.
- [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md) — phase 0 threat model, OWASP mapping, `rule_id` / categories.
- [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) — mistakes + fixes (feedback loop).
- [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md) — Hermes / MCP boundaries.
- [docs/LONG_HORIZON_HARNESS.md](docs/LONG_HORIZON_HARNESS.md) — Makefile, session log, graphify.
- [hf_bundle_scanner/docs/hermes-mcp.md](hf_bundle_scanner/docs/hermes-mcp.md) — MCP + HTTP + `HF_BUNDLE_PYTHON`.

## Commands

From `/root/LLM Scanner`:

```bash
make install
make test
make scan-fixture
```

## Long-horizon discipline

- Cursor skill: [`.cursor/skills/llm-scanner-long-horizon/SKILL.md`](.cursor/skills/llm-scanner-long-horizon/SKILL.md)
- End-of-session notes: [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md)

## Cursor rules

Project skills live under [`.cursor/skills/`](.cursor/skills/). Do not write into `~/.cursor/skills-cursor/` (reserved).
