# Long-horizon harness (Makefile, memory, graphify)

Canonical working directory: **`/root/LLM Scanner`** (WSL2).

Feedback loop: [LESSONS_LEARNED.md](LESSONS_LEARNED.md) (append mistakes and fixes). Threat model: [THREAT_MODEL_TAXONOMY.md](THREAT_MODEL_TAXONOMY.md).

## Makefile targets (repo root)

| Target | Purpose |
| ------ | -------- |
| `make help` | List harness targets |
| `make install` | Create `.venv`, install `model-admission` + `hf_bundle_scanner[dev,mcp,http]` |
| `make test` | Pytest excluding integration markers |
| `make integration` | Integration-marked tests |
| `make scan-fixture` | Minimal tree + bundle scan smoke |
| `make roadmap` | Print pointer to this roadmap doc |
| `make graphify-update` | Refresh `graphify-out/` if `graphify` CLI or Python module is available |
| `make memory-open` | Print path to session log for append-only notes |
| `make agent-verify` | Run **[`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py)** (repo `.venv` if present, else `sys.executable`); writes [`.agent/pytest-last.log`](../.agent/pytest-last.log) + `.agent/pytest-last.exit` so agents can **read** results when terminal stdout is empty |
| `make drivers-help` | Print `model-admission` scan driver names (`modelscan`, `modelaudit`) + `MODELSCAN_BIN` / `MODELAUDIT_BIN` hints (needs `make install`) |
| `make plain-english-brief` | Write `docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md` (non-technical; does not overwrite CSV/HTML/blast MD) |
| `make sample-reports-all` | `sample-action-sheets` + `plain-english-brief` |

Delegate from `hf_bundle_scanner/` with `make -C .. <target>` (see that folder’s stub Makefile).

## Session memory (“claude-mem” compatible)

At the **end of each agent session**, append to [`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md):

- Date (UTC), branch or topic
- Phase id touched (`phase0-foundations`, …)
- Commands run (`make …`, `pytest …`)
- Files changed (high level)
- Open risks / next steps

**Do not** store API keys, tokens, or customer data in the log.

If you use an external memory tool (e.g. claude-mem), treat `SESSION_LOG.md` as the **portable fallback** that stays in git.

## graphify

- If [`graphify-out/GRAPH_REPORT.md`](../graphify-out/GRAPH_REPORT.md) exists, read it before large architectural edits. If your tree includes `/root/CLAUDE.md`, follow its graphify rules for the wider workspace; otherwise use [CLAUDE.md](../CLAUDE.md) in this repo when present.
- Run **`make graphify-update`** from repo root after substantive Python changes under `model-admission/` or `hf_bundle_scanner/` when graphify is installed.

## “Superpowers” checklist (agent discipline)

- Read all touched modules before editing.
- Use a todo list for multi-step phase work.
- Run `make test` (and `make scan-fixture` when changing dispatch/admission wiring).
- One phase contract at a time; do not merge conflicting ownership (see [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md)).

## Scanner catalog pointers (non-exhaustive)

| Kind | Examples |
| ---- | -------- |
| Static artifacts | [ModelScan](https://github.com/protectai/modelscan), [ModelAudit](https://www.promptfoo.dev/docs/model-audit/), [picklescan](https://github.com/mmaitre314/picklescan) |
| Dynamic | [Garak](https://github.com/NVIDIA/garak), [PyRIT](https://github.com/Azure/PyRIT) |
| Eval / red team | [promptfoo](https://github.com/promptfoo/promptfoo), [DeepTeam](https://www.trydeepteam.com/) |
| Runtime guards | [LLM Guard](https://github.com/laiyer-ai/llm-guard), [Rebuff](https://github.com/protectai/rebuff), [Lakera](https://docs.lakera.ai/docs/red/guard-integration) |
| Enterprise | [HiddenLayer](https://www.hiddenlayer.com/solutions/model-scanning), [Prisma AIRS](https://www.paloaltonetworks.com/prisma/prisma-cloud/airs-ai-model-security) |

Map backends to phases in [PRODUCTION_SCANNER_ROADMAP.md](PRODUCTION_SCANNER_ROADMAP.md); normalize findings through **`phase0`** taxonomy when implemented.

The `help`, `roadmap`, `graphify-update`, and `memory-open` targets live in the **root** [`Makefile`](../Makefile); `make -C hf_bundle_scanner <target>` forwards to the root.
