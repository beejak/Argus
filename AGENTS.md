# Agent instructions (LLM Scanner)

## Scope

This monorepo contains:

- **`model-admission/`** — `admit-model` CLI, policy JSON, ModelScan / ModelAudit drivers.
- **`hf_bundle_scanner/`** — Bundle manifest, discovery, `scan-bundle` / `hf_bundle_scanner` CLI, optional **MCP** and **HTTP**.

## Must read before large changes

- [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) — phased long-horizon plan.
- [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md) — phase 0 threat model, OWASP mapping, `rule_id` / categories.
- [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md) — index of LLM security test cases and where they live.
- [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) — mistakes + fixes (feedback loop). After a durable lesson, consider mirroring a **short** hint into [LONG_HORIZON_HARNESS.md](docs/LONG_HORIZON_HARNESS.md) (propagation table), [HERMES_AGENTS.md](docs/HERMES_AGENTS.md), or the long-horizon Cursor skill — not a full README rewrite.
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

If **`git commit -m …`** fails with **`option trailer requires a value`**, run **`make git-doctor`**, then commit with **`make commit-msg MSG='…'`** or **`python3 scripts/git_commit_via_file.py '…'`** (see [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)).

**README tagline:** pool in [`docs/slogans.json`](docs/slogans.json); dry-run with **`make slogan-dry-run`**. **Ephemeral Hub demo:** **`OUT=/tmp/x.json make ephemeral-hub-scan`** (see root [`README.md`](README.md)) — network; tree deleted after scan.


## Long-horizon discipline

- Cursor skill: [`.cursor/skills/llm-scanner-long-horizon/SKILL.md`](.cursor/skills/llm-scanner-long-horizon/SKILL.md)
- End-of-session notes: [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md)
- **Multi-option handoffs:** if several next steps were discussed and only one was built, record the **rest** in [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) under **Choice capture** (same PR or immediate follow-up) so backlog stays explicit.

## Cursor rules

Project skills live under [`.cursor/skills/`](.cursor/skills/). Do not write into `~/.cursor/skills-cursor/` (reserved).

_No Tokens were harmed during making of this repo._
