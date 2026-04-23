# LLM Scanner

<!-- SLOGAN_START -->
> *Because “we downloaded it from Hugging Face” is not a threat model — it’s a release note written in advance.*
<!-- SLOGAN_END -->

*Rotating taglines live in [`docs/slogans.json`](docs/slogans.json); a bot advances them on a schedule ([`docs/SLOGANS.md`](docs/SLOGANS.md), [`.github/workflows/rotate-slogan.yml`](.github/workflows/rotate-slogan.yml)).*

**Production-minded scanning for Hugging Face–style model bundles** — static admission, config risk, and a staged path toward dynamic probes and runtime guardrails. The public mirror of this monorepo is **[Argus on GitHub](https://github.com/beejak/Argus)** ([publish notes](docs/PUBLISH_ARGUS.md)).

> **One working tree:** use a single checkout (for example `/root/LLM Scanner` on WSL). A duplicate under Windows `\\wsl$\\…` plus a UNC workspace invites drift and confusing pytest output.

---

## What this repository does

| Capability | Where | In plain language |
| ---------- | ----- | ----------------- |
| **Per-file admission** | [`model-admission/`](model-admission/README.md) | Runs **`admit-model`** with a **policy JSON** file: size/extension gates, optional **ModelScan / ModelAudit** drivers, stable **exit codes**. |
| **Bundle orchestration** | [`hf_bundle_scanner/`](hf_bundle_scanner/README.md) | Walks a snapshot tree: **manifest** (hashes), **discovery**, **configlint** (static JSON hints), **dispatch** to model-admission per weight-like file, **aggregate JSON** report (**`hf_bundle_scanner.bundle_report.v2`** + **provenance**). |
| **Taxonomy & findings** | [`model_admission/taxonomy.py`](model-admission/model_admission/taxonomy.py) | Normalized **`RiskCategory`**, OWASP LLM01–10 mapping, **risk register** ids, optional **`rule_id` / `category`** on findings. |
| **Test catalog** | [`llm_security_test_cases/catalog.json`](llm_security_test_cases/catalog.json) | Machine-readable catalog (pytest fixture + CI harness); see [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md). |
| **Agent / CI harness** | [`Makefile`](Makefile), [`scripts/run_tests_for_agent.py`](scripts/run_tests_for_agent.py), [`.github/workflows/llm-scanner.yml`](.github/workflows/llm-scanner.yml) | One command runs both packages and writes **`.agent/pytest-last.log`**; GitHub Actions runs the same script. |
| **Optional surfaces** | MCP + HTTP | Bounded tools for agents; see [hf_bundle_scanner/docs/hermes-mcp.md](hf_bundle_scanner/docs/hermes-mcp.md). |

---

## What this repository does **not** do

- **It is not a full application or RAG pentest.** Phase 8 and the roadmap describe broader evals; today the default path is **artifact + config static** analysis inside a bundle directory.
- **It does not run Garak-class dynamic red teaming in default CI.** Dynamic probes stay **opt-in** (markers, env gates) so air-gapped CI stays deterministic.
- **It does not replace legal, compliance, or vendor attestation.** Findings are **technical signals**; severity and policy live in **your** policy JSON and process.
- **It is not a hosted scanner SaaS.** You run CLI, Makefile, MCP, or HTTP **on your infrastructure**.
- **It does not silently “fix” models.** The gate **reports** and exits; it does not rewrite weights or auto-remediate Hub repos.

---

## Philosophy

1. **Explicit over magical** — Policy JSON, driver lists, and exit codes are visible and versionable. Surprise behavior belongs in documentation, not in defaults.
2. **Deterministic CI first** — Default tests avoid network and multi‑GiB downloads. Anything slow or flaky is **marked** and **env-gated**.
3. **OSS-by-default, commercial optional** — Static lanes prefer open tooling; commercial adapters stay behind explicit configuration (roadmap).
4. **Agents orchestrate, they do not replace judgment** — Hermes / MCP should call **bounded** tools; humans (or your org) own severity floors and ship decisions. See [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md).
5. **Phased honesty** — [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) names what exists today vs **phase 5–8** backlog (dynamic probes, runtime guards, observability).
6. **Provenance as a first-class column** — Bundle JSON **v2** carries **`provenance`** (Hub hints, mirror allowlist, SBOM pointer, manifest digest summary) so downstream SIEMs and auditors can tie a report to **what** was scanned and **from where** ([`provenance.py`](hf_bundle_scanner/hf_bundle_scanner/provenance.py)).

---

## Phase 2 snapshot (`phase2-static-drivers`)

**Theme:** widen **Lane A** static coverage (more drivers / adapters) while keeping default CI honest.

**In this repo today (starter slice):**

- **Ephemeral Hub demo** — [`scripts/ephemeral_hub_scan.py`](scripts/ephemeral_hub_scan.py) downloads a **small** public snapshot (default `hf-internal-testing/tiny-random-BertModel`), runs **`scan-bundle scan`**, writes your **`--out`** JSON, then **deletes** the tree. Optional **`--inject-demo-tokenizer-risk`** adds a **JSON-only** `tokenizer_config.json` flag so **configlint** fires on `trust_remote_code` for teaching — it is **not** a pickle exploit or a “trojan weight”.
- **More configlint** — extra high-signal tokenizer / loader hints land here before heavier driver work (see roadmap).

Full checklist: [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) (`phase2-static-drivers`).

---

## How to run a scan

### A. Fast path (fixture smoke, no Hub download)

From the repo root after **`make install`**:

```bash
cd "/root/LLM Scanner"
make scan-fixture
```

This builds a tiny **`safetensors`** stub under `hf_bundle_scanner/tests/fixtures/minimal_tree/`, runs **`scan-bundle scan`** with a **permissive** policy fixture, and prints a JSON summary. The full bundle report path is printed by the Makefile target (under `/tmp/` by default).

### B. Full `scan-bundle` CLI (your tree + your policy)

Use the same interpreter for **`transformers`-style** stacks and for **`admit-model`** (paths with spaces → set **`HF_BUNDLE_PYTHON`**):

```bash
cd "/root/LLM Scanner"
export HF_BUNDLE_PYTHON="$(pwd)/.venv/bin/python"

scan-bundle scan \
  --root /path/to/snapshot \
  --policy /path/to/policy.json \
  --out /tmp/bundle-report.json \
  --drivers "" \
  --print-summary
```

**Optional provenance** (merged with env `HF_BUNDLE_MIRROR_ALLOWLIST`, `HF_BUNDLE_SBOM_URI`):

```bash
scan-bundle scan \
  --root "$SNAPSHOT" \
  --policy "$POLICY" \
  --out /tmp/bundle-report.json \
  --drivers "" \
  --hub-repo org/model --hub-revision main \
  --mirror-allowlist huggingface.co,cdn-lfs.huggingface.co \
  --sbom-uri file:///path/to/sbom.json
```

**Per-file gate only** (single artifact):

```bash
admit-model scan --artifact /path/to/file.safetensors --policy policy.json --report /tmp/admit.json --drivers "" --timeout 600 --fail-on MEDIUM
```

Policy shape and driver strings are documented in [`model-admission/README.md`](model-admission/README.md).

### C. HTTP / MCP

See [hf_bundle_scanner/docs/hermes-mcp.md](hf_bundle_scanner/docs/hermes-mcp.md) for **`POST /v1/scan`** JSON and MCP **`scan_path`** parameters.

### D. Ephemeral Hub scan (network, then delete)

Use this when you want a **real download** and a **bundle JSON** on disk, but **no** long-lived snapshot directory. Requires **`make install`**, **`HF_BUNDLE_PYTHON`**, and outbound Hub access.

```bash
cd "/root/LLM Scanner"
export HF_BUNDLE_PYTHON="$(pwd)/.venv/bin/python"

# Tiny public test model → /tmp/ephemeral-bundle.json, tree removed afterward
make ephemeral-hub-scan OUT=/tmp/ephemeral-bundle.json

# Same, but force a configlint “trust_remote_code” hit for demos (JSON-only; not malware)
make ephemeral-hub-scan OUT=/tmp/ephemeral-risk.json INJECT=1
```

Advanced flags are passed through **`EPHEMERAL_FLAGS`** (see **`make help`**). **Do not** use this path to fetch or execute known-offensive artifacts; for red-team payloads use an **org-approved** lab and separate policy.

---

## Reporting mechanism

| Output | What it is | Where / how |
| ------ | ---------- | ------------- |
| **Bundle report JSON** | Single document: per-file admission results, **configlint** findings, optional **file manifest**, **`aggregate_exit_code`**, **`provenance`**. | Written by **`scan-bundle scan --out …`**, returned by HTTP/MCP. Schema: **`hf_bundle_scanner.bundle_report.v2`**; taxonomy tag: **`taxonomy_version`: `"phase0"`**. |
| **Admit-model JSON** | One artifact’s scan: findings, severity, driver output references. | `--report` path on `admit-model scan`. |
| **Pytest harness log** | Full stdout/stderr from **both** packages’ pytest runs + exit summary. | **`make agent-verify`** → **`.agent/pytest-last.log`** and **`.agent/pytest-last.exit`** ([`.agent/README.md`](.agent/README.md)). |
| **GitHub Actions** | Same harness as local agent-verify; uploads the log artifact. | [`.github/workflows/llm-scanner.yml`](.github/workflows/llm-scanner.yml) — open the latest run for your branch. |

**Exit semantics (bundle aggregate):** worst child wins by priority — code **`4`** (usage), then **`2`** (driver/tooling), then **`1`** (policy / findings / certain configlint escalations), else **`0`** (`compute_aggregate_exit` in [`report.py`](hf_bundle_scanner/hf_bundle_scanner/report.py)). Config risk from **`trust_remote_code`**, **`auto_map`** custom classes, or **invalid `config.json`** can raise the aggregate to **`1`** when the file lane was clean. See [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md).

---

## Tests in this repository

| Suite | Path | What it covers |
| ----- | ---- | -------------- |
| **model-admission** | [`model-admission/tests/`](model-admission/tests/) | CLI, policy gates, drivers (incl. fault injection), taxonomy, **`Finding`** JSON, **catalog ↔ taxonomy** alignment. |
| **hf_bundle_scanner (default)** | [`hf_bundle_scanner/tests/`](hf_bundle_scanner/tests/) | Manifest, discovery, dispatch, **configlint**, report math, **provenance**, CLI, HTTP (needs **`[http]`** deps), MCP import smoke. **`integration`** and **`chwoo`** markers excluded from `make test`. |
| **Integration** | `pytest -m integration` | Network / Hub smoke (skipped unless opted in). |
| **Agent verify** | `make agent-verify` | Runs **`scripts/run_tests_for_agent.py`**: model-admission **all** tests + hf_bundle_scanner **excluding** `integration`. |

Canonical index: [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md).

---

## Help & troubleshooting

| Symptom | Try |
| ------- | --- |
| **Agent terminal shows no pytest output** | Run **`make agent-verify`**, then open **`.agent/pytest-last.log`**. Prefer **Cursor Remote – WSL**. |
| **`admit-model` / bundle scan fails with argv / path errors** | Set **`HF_BUNDLE_PYTHON`** to your venv’s **`python`** (paths with spaces break unquoted **`HF_BUNDLE_ADMIT_CMD`** — see [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)). |
| **`git commit` fails with `option trailer requires a value`** | Run **`make git-doctor`**, then commit with **`make commit-msg MSG='…'`** or **`python3 scripts/git_commit_via_file.py`**. |
| **“Is CI green?”** | Open the latest **GitHub Actions** run for **`llm-scanner`** on [Argus](https://github.com/beejak/Argus/actions). |

Deeper narrative: [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md). Agent entry: [AGENTS.md](AGENTS.md).

---

## Quick start (WSL)

```bash
cd "/root/LLM Scanner"
make help
make install
make agent-verify
```

`make install` creates **`.venv/`** (PEP 668–friendly) and installs both Python packages in editable mode.

---

## Keeping this README honest

After you change behavior, contracts, or defaults: run **`make agent-verify`**, push, and append a line to [**`docs/sessions/SESSION_LOG.md`**](docs/sessions/SESSION_LOG.md) (**no secrets**). If the README drifts from code, treat that as a bug—**fix the doc in the same change** when you can.

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
| Append-only session memory | [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md) |
| Cursor long-horizon skill | [`.cursor/skills/llm-scanner-long-horizon/SKILL.md`](.cursor/skills/llm-scanner-long-horizon/SKILL.md) |

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
