---
name: llm-scanner-long-horizon
description: Long-horizon execution for the LLM Scanner monorepo (model-admission + hf_bundle_scanner)—phased roadmap, Hermes MCP boundaries, graphify refresh, session memory hooks, and harness Makefile targets.
---

# LLM Scanner — long-horizon execution

Use this skill when work spans **multiple sessions**, **phase 0–8** of the production-scanner roadmap, or **Hermes / MCP orchestration** around deterministic scans.

## Canonical repo layout (WSL2)

- **Root harness:** `/root/LLM Scanner` — root [`Makefile`](Makefile), [`.venv`](.venv).
- **Admission gate:** [`model-admission/`](../../../model-admission/README.md) — `admit-model`, ModelScan / ModelAudit drivers.
- **Bundle orchestration:** [`hf_bundle_scanner/`](../../../hf_bundle_scanner/README.md) — `scan-bundle`, manifest, MCP / HTTP.
- **Roadmap (in-repo):** [`docs/PRODUCTION_SCANNER_ROADMAP.md`](../../../docs/PRODUCTION_SCANNER_ROADMAP.md).
- **Hermes playbook:** [`docs/HERMES_AGENTS.md`](../../../docs/HERMES_AGENTS.md).
- **Harness + memory:** [`docs/LONG_HORIZON_HARNESS.md`](../../../docs/LONG_HORIZON_HARNESS.md).
- **Threat model / taxonomy:** [`docs/THREAT_MODEL_TAXONOMY.md`](../../../docs/THREAT_MODEL_TAXONOMY.md).
- **Lessons learned:** [`docs/LESSONS_LEARNED.md`](../../../docs/LESSONS_LEARNED.md).

Always run **`make`** from the **repo root** unless delegating via `hf_bundle_scanner/Makefile`.

## Phases (do not collapse)

Execute **one phase todo at a time** (see roadmap YAML mirror in `docs/PRODUCTION_SCANNER_ROADMAP.md`): `phase0-foundations` → parallel `phase1` / `phase2` / `phase3` → `phase4` → gated `phase5` / `phase6` / `phase7` → `phase8`. After each phase: **`make test`** (and `make integration` only when network / tools are intended).

## graphify (judgement: use for architecture + doc drift)

If [`graphify-out/GRAPH_REPORT.md`](../../../graphify-out/GRAPH_REPORT.md) exists, **read it before large refactors**. After substantive edits to Python under `model-admission/` or `hf_bundle_scanner/`, run **`make graphify-update`** from repo root (no-op if graphify is not installed). Follow the workspace graphify rule in [`CLAUDE.md`](../../../../CLAUDE.md) under `/root` when present.

For **plan-only** iterations stored outside the repo (Cursor `*.plan.md`), optionally run graphify on `docs/` after syncing roadmap text into `docs/PRODUCTION_SCANNER_ROADMAP.md`.

## claude-mem (judgement: lightweight session log in-repo)

At **end of each agent session**, append a short entry to [`docs/sessions/SESSION_LOG.md`](../../../docs/sessions/SESSION_LOG.md): date, phase touched, commands run (`make …`), files changed, open risks. This file acts as a **portable memory** when external memory plugins are unavailable. Do not put secrets in the log.

## superpowers (judgement: agent discipline)

- Batch **read_file** on all touched modules before editing.
- Use **todo_write** for multi-step phase work; mark completed when done.
- Prefer **deterministic** checks: `make test`, `make scan-fixture`, targeted `pytest`.
- Keep **Hermes** to orchestration; **no** “creative” skipping of `admit-model` / policy JSON.

## Hermes reminder

MCP tools expose **bounded** scan operations — see [`hf_bundle_scanner/docs/hermes-mcp.md`](../../../hf_bundle_scanner/docs/hermes-mcp.md). Long-horizon dynamic red-team (Garak-class) belongs in **phase 5** and must stay **opt-in** (env / policy), not default CI.
