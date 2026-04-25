# Hermes agents — playbook for this repo

[Hermes Agent](https://github.com/nousresearch/hermes-agent) should **orchestrate** bounded work. **Deterministic scanning** stays in Python: [`model-admission`](../model-admission/README.md) and [`hf_bundle_scanner`](../hf_bundle_scanner/README.md).

## What Hermes may call

1. **stdio MCP — `hf-bundle-mcp`** (after `make install` from repo root)  
   - Tools: `scan_path`, `build_manifest_json` — see [`hf_bundle_scanner/docs/hermes-mcp.md`](../hf_bundle_scanner/docs/hermes-mcp.md).

2. **Optional HTTP — `hf-bundle-http`**  
   - `GET /healthz`, `POST /v1/scan` — same doc; bind localhost unless TLS + auth exist.

3. **Makefile harness (subprocess)**  
   - From `/root/LLM Scanner`: `make test`, `make scan-fixture`, `make integration` (when intended), `make orchestrator-validate`, `make agent-verify` (writes `.agent/pytest-last.log`).  
   - See [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md).

## Where test scenarios live (do not duplicate in README)

- **Canonical matrix:** `hf_bundle_scanner/tests/` (pytest), `model-admission/tests/`, plus [TEST_CASES_LLM_SECURITY_SCANNER.md](TEST_CASES_LLM_SECURITY_SCANNER.md) and `llm_security_test_cases/catalog.json`.  
- **README** should **point** here, not enumerate every case (avoids drift).  
- **Feedback loop:** append reusable mistakes to [LESSONS_LEARNED.md](LESSONS_LEARNED.md); mirror **short** discipline into the long-horizon skill + harness per [LONG_HORIZON_HARNESS.md — Propagating sanitized lessons](LONG_HORIZON_HARNESS.md#propagating-sanitized-lessons-skills-makefile-hermes).

## What Hermes must not do

- Replace `admit-model` / policy JSON with “vibes-based” approval.
- Run **dynamic red-team** (phase 5) in default CI without explicit env/policy (cost, egress, nondeterminism).
- Exfiltrate customer snapshots or keys into external services unless **hybrid tier** is explicitly enabled.

## Environment reminders

- Prefer **`HF_BUNDLE_PYTHON`** when the interpreter path contains spaces (see hermes-mcp doc).
- For ModelAudit telemetry: `PROMPTFOO_DISABLE_TELEMETRY=1`, `NO_ANALYTICS=1` (see model-admission README).

## Long horizon

When a task spans multiple sessions, follow [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md) and append checkpoints to [`docs/sessions/SESSION_LOG.md`](sessions/SESSION_LOG.md).

When a session surfaces a **repeatable** pitfall, add it to [LESSONS_LEARNED.md](LESSONS_LEARNED.md) and, if it affects how agents invoke tools, add a **one-line** reminder here or in the harness doc (see **Propagating sanitized lessons** in [LONG_HORIZON_HARNESS.md](LONG_HORIZON_HARNESS.md)).
