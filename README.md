<div align="center">

# LLM Scanner

<!-- SLOGAN_START -->
<p align="center"><i>Because “we downloaded it from Hugging Face” is not a threat model — it’s a release note written in advance.</i></p>
<!-- SLOGAN_END -->

<sub>Rotating tagline pool: <code>docs/slogans.json</code> · <a href="docs/SLOGANS.md">how it rotates</a> · <a href=".github/workflows/rotate-slogan.yml">workflow</a></sub>

<br/>

[![LLM Scanner CI](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml/badge.svg?branch=main)](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml?query=branch%3Amain)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-101624?logo=python&logoColor=white)

**Production-minded scanning** for Hugging Face–style model bundles — static admission, config risk, and a staged path toward dynamic probes and runtime guardrails.

[**Argus** (GitHub mirror)](https://github.com/beejak/Argus) · [Publish notes](docs/PUBLISH_ARGUS.md)

<sub><b>Fonts:</b> <code>github.com</code> ignores custom web fonts in READMEs. This layout uses <b>spacing, centering, and badges</b> instead. For a bespoke typeface, ship docs via <a href="https://pages.github.com/">GitHub Pages</a> (or any static site) with your own CSS.</sub>

</div>

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

## Live Hub sample reports (real download)

These are **committed outputs** from a **live** Hugging Face snapshot download (**`hf-internal-testing/tiny-random-BertModel`**), then the working tree was deleted. Among common `hf-internal-testing/tiny-random-*` snapshots, this repo is **one of the smallest** full multi-format fixtures we measured (~**1.3 MB** over the wire vs ~**2.1 MB** for `tiny-random-GPT2Model`), which keeps demos fast.

**About “small but vulnerable”:** this repository does **not** ship or recommend downloading known-malicious weights. In practice, “risky” Hub content usually means **(a)** policy-relevant formats (for example **pickle-capable** `pytorch_model.bin`), **(b)** **config** flags like `trust_remote_code`, or **(c)** your org’s **stricter policy** rejecting formats you do not want in production. The samples below illustrate **(b)** with a JSON-only demo file and **(c)** with a **safetensors-only** policy on the same benign test snapshot.

Snapshot paths are **redacted** to `/tmp/<ephemeral-hub-demo>` for readability. Index + context: [`docs/sample_reports/README.md`](docs/sample_reports/README.md).

### Start here (actionable formats — not JSON)

If the JSON feels opaque, open the **human briefing pack** first:

- **[`docs/sample_reports/actionable/README.md`](docs/sample_reports/actionable/README.md)** — how to read the columns.
- **[`docs/sample_reports/actionable/BLAST_RADIUS_LEADERSHIP.md`](docs/sample_reports/actionable/BLAST_RADIUS_LEADERSHIP.md)** — **leadership blast-radius brief**: prod impact + who is affected + roll-up of **every** identified signal per demo.
- **[`docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv`](docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv)** — one spreadsheet with **all three demos** (filter on `demo_id`) including **`risk_rating`**, **`prod_impact_if_shipped`**, **`blast_radius`**, **`exec_one_liner`**.
- **[`docs/sample_reports/actionable/SCAN_BRIEFING.html`](docs/sample_reports/actionable/SCAN_BRIEFING.html)** — the same story as tables in a browser (leadership section first).

**PDF (no extra tooling):** open `SCAN_BRIEFING.html` → **Print** → **Save as PDF**.

Regenerate after changing sample JSON: `python3 scripts/export_bundle_action_sheet.py` (also `make sample-action-sheets`).

| Artifact | One-line meaning |
| -------- | ---------------- |
| [`docs/sample_reports/live_hub_tiny_bert_bundle_report.json`](docs/sample_reports/live_hub_tiny_bert_bundle_report.json) | **Baseline:** three weight-like artifacts (`.onnx`, `.bin`, `.h5`) scanned; **no** configlint hits; **`aggregate_exit_code`: `0`**. |
| [`docs/sample_reports/live_hub_tiny_bert_bundle_report_with_demo_risk.json`](docs/sample_reports/live_hub_tiny_bert_bundle_report_with_demo_risk.json) | **Same snapshot + demo JSON risk:** a synthetic `tokenizer_config.json` enables **`trust_remote_code_enabled`** → aggregate bumped to **`1`** even if per-file scans are clean. |
| [`docs/sample_reports/live_hub_tiny_bert_bundle_report_strict_safetensors_policy.json`](docs/sample_reports/live_hub_tiny_bert_bundle_report_strict_safetensors_policy.json) | **Same snapshot + strict policy:** only **`.safetensors`** allowed ([`policy.safetensors-only.json`](hf_bundle_scanner/tests/fixtures/policy.safetensors-only.json)); `.onnx`, `.bin`, `.h5` each get a **policy** finding → **`aggregate_exit_code`: `1`**. |

### Trimmed excerpt (strict policy sample)

This is what a **policy-gated** failure looks like in the bundle JSON (one of three similar rows); the full file is linked above.

```json
{
  "relpath": "pytorch_model.bin",
  "exit_code": 1,
  "report": {
    "findings": [
      {
        "driver": "policy",
        "severity": "high",
        "title": "Policy violation",
        "detail": "extension '.bin' not in allowed_extensions",
        "rule_id": "policy.gate_violation"
      }
    ]
  }
}
```

### How to read the JSON (top-level)

| Field | What it tells you |
| ----- | ----------------- |
| **`schema`** | Report format version (`hf_bundle_scanner.bundle_report.v2`). |
| **`taxonomy_version`** | Phase‑0 risk language revision (`phase0`) for `rule_id` / categories. |
| **`root`** | Snapshot root that was scanned (redacted here). |
| **`policy_path`** | The admission policy JSON used for every `admit-model` invocation. |
| **`drivers`** | Comma-separated static driver list forwarded to `admit-model` (empty here = policy gate only). |
| **`manifest`** | Recursive file hashes for integrity / drift (includes Hub cache files under `.cache/` in this sample). |
| **`config_findings`** | **configlint** hits on JSON configs (`tokenizer_config.json`, etc.) — empty in the baseline file; populated in the demo-risk file. |
| **`file_scans[]`** | One row per discovered artifact: `relpath`, `exit_code`, embedded **`report`** (admit-model JSON) or `error` text. |
| **`aggregate_exit_code`** | Single “ship / no-ship style” rollup for CI gates (`0` clean, `1` policy/config/findings floor, `2` tooling, `4` usage). |
| **`provenance`** | Phase‑1 metadata: Hub repo/revision echo, mirror/SBOM env hints if set, **`manifest_summary`** digest. |

### Why the “demo risk” file exits `1`

`merge_aggregate_exit` intentionally escalates **0 → 1** when configlint sees high-risk loader posture (`trust_remote_code_enabled`, `auto_map_custom_classes`, or invalid JSON). That is **not** proof of exploitation — it is a **policy signal** that your integration is asking for a sharper review before production.

---

## Tests in this repository

| Suite | Path | What it covers |
| ----- | ---- | -------------- |
| **model-admission** | [`model-admission/tests/`](model-admission/tests/) | CLI, policy gates, drivers (incl. fault injection), taxonomy, **`Finding`** JSON, **catalog ↔ taxonomy** alignment. |
| **hf_bundle_scanner (default)** | [`hf_bundle_scanner/tests/`](hf_bundle_scanner/tests/) | Manifest, discovery, dispatch, **configlint**, report math, **provenance**, CLI, HTTP (needs **`[http]`** deps), MCP import smoke. **`integration`** and **`chwoo`** markers excluded from `make test`. |
| **Integration** | `pytest -m integration` | Network / Hub smoke (skipped unless opted in). |
| **Agent verify** | `make agent-verify` | Runs **`scripts/run_tests_for_agent.py`**: model-admission **all** tests + hf_bundle_scanner **excluding** `integration`. |

Canonical index: [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md).

### What “green” looks like (human-readable)

`make agent-verify` runs **two** pytest invocations and writes **`.agent/pytest-last.log`** plus **`.agent/pytest-last.exit`** (`0` = both suites passed). A typical green log ends like this:

| Step | Result | Meaning |
| ---- | ------ | ------- |
| **model-admission** | **42 passed**, **2 skipped** | Skips are integration-style driver checks that need optional external tools; they are not failures. |
| **hf_bundle_scanner** | **36 passed**, **2 deselected** | Deselected = tests marked **`integration`** excluded on purpose for speed and determinism. |
| **Overall** | **`overall_exit=0`** | Both subprocess exit codes were `0`. |

The [![LLM Scanner CI](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml/badge.svg?branch=main)](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml?query=branch%3Amain) badge reflects the same harness in GitHub Actions (open the workflow run to download the uploaded log if you need it).

> **Plain language:** If someone mentions an “optional third sample” or “pasting an excerpt into the README,” they are talking about **documentation choices**, not a product fork. A **stricter policy** sample means “same harmless Hub test weights, but your policy rejects `.bin` / `.onnx` / `.h5`.” A **trimmed excerpt** means “show a short JSON fragment inline so readers see shape without opening a large file.” Neither option changes how the scanner runs.

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
| Live Hub sample bundle JSON | [docs/sample_reports/](docs/sample_reports/) |
| Human briefing + blast radius (CSV / HTML / MD) | [docs/sample_reports/actionable/](docs/sample_reports/actionable/) |
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
