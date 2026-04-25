<div align="center">

# LLM Scanner

<!-- SLOGAN_START -->
<p align="center"><i>Because “we downloaded it from Hugging Face” is not a threat model — it’s a release note written in advance.</i></p>
<!-- SLOGAN_END -->

<sub>Rotating tagline pool: <code>docs/slogans.json</code> · <a href="docs/SLOGANS.md">how it rotates</a> · <a href=".github/workflows/rotate-slogan.yml">workflow</a></sub>

<br/>

[![LLM Scanner CI](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml/badge.svg?branch=main)](https://github.com/beejak/Argus/actions/workflows/llm-scanner.yml?query=branch%3Amain)
![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-101624?logo=python&logoColor=white)

**Production-minded scanning** for Hugging Face–style model bundles — static admission, config risk, a **phase-4 orchestrator** (job JSON + envelope), and a **phase-5 opt-in dynamic probe stub** (contract + `garak --help` check when enabled).

[**Argus** (GitHub mirror)](https://github.com/beejak/Argus) · [Publish notes](docs/PUBLISH_ARGUS.md)

<sub><b>Fonts:</b> <code>github.com</code> ignores custom web fonts in READMEs. This layout uses <b>spacing, centering, and badges</b> instead. For a bespoke typeface, ship docs via <a href="https://pages.github.com/">GitHub Pages</a> (or any static site) with your own CSS.</sub>

</div>

> **One working tree:** use a single checkout (for example `/root/LLM Scanner` on WSL). A duplicate under Windows `\\wsl$\\…` plus a UNC workspace invites drift and confusing pytest output.

---

## What this repo does (plain English)

**Who this is for:** engineering leads, security / risk partners, and executives who need a **yes/no/hold** story without reading JSON or spreadsheets first.

**What we actually do:** we take a **folder of model-related files** (weights, configs, and similar artifacts) and run **automated, offline-friendly checks** on them. Think “a release gate for the **files you are about to trust**,” not “we proved your chatbot will behave.”

**What you get out of it:**

- A **traffic-light style signal** for “did our default static gate object?” — useful in CI and procurement conversations.
- **Separate outputs:** engineers can use the detailed tables/CSV; approvers can start with a **plain-language brief** of the same sample scans ([`docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md`](docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md)).

**What we do *not* do (yet):** we do **not** replace human judgment, legal review, or full red-teaming. **Phase 5** ships a **stub + JSON report only** (no default Garak runs); phases **6–8** add supply-chain appendices, runtime guardrails, and observability — see [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) and [docs/PHASE5_DYNAMIC_PROBES.md](docs/PHASE5_DYNAMIC_PROBES.md).

**Keeping this section honest:** when a roadmap **phase** lands user-visible behavior, update **this blurb** in the same change when you can, and regenerate **`PLAIN_ENGLISH_BRIEF.md`** with **`make plain-english-brief`** (or **`make sample-reports-all`** after changing sample JSON).

---

## What this repository does

| Capability | Where | In plain language |
| ---------- | ----- | ----------------- |
| **Per-file admission** | [`model-admission/`](model-admission/README.md) | Runs **`admit-model`** with a **policy JSON** file: size/extension gates, optional **ModelScan / ModelAudit** drivers, stable **exit codes**. |
| **Bundle orchestration** | [`hf_bundle_scanner/`](hf_bundle_scanner/README.md) | Walks a snapshot tree: **manifest** (hashes), **discovery**, **configlint** (static JSON hints), **dispatch** to model-admission per weight-like file, **aggregate JSON** report (**`hf_bundle_scanner.bundle_report.v2`** + **provenance**). |
| **Taxonomy & findings** | [`model_admission/taxonomy.py`](model-admission/model_admission/taxonomy.py) | Normalized **`RiskCategory`**, OWASP LLM01–10 mapping, **risk register** ids, optional **`rule_id` / `category`** on findings. |
| **Test catalog & scenarios** | [`llm_security_test_cases/catalog.json`](llm_security_test_cases/catalog.json), [`hf_bundle_scanner/tests/`](hf_bundle_scanner/tests/), **`make test`** | Canonical matrix lives in **pytest + catalog +** [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md). **README does not list every test case** (would duplicate CI and drift); this row is the pointer. |
| **Agent / CI harness** | [`Makefile`](Makefile), [`scripts/run_tests_for_agent.py`](scripts/run_tests_for_agent.py), [`.github/workflows/llm-scanner.yml`](.github/workflows/llm-scanner.yml) | One command runs both packages, **ruff**, orchestrator **validate**, dynamic-probe **stub**, and writes **`.agent/pytest-last.log`**; GitHub Actions runs the same script. |
| **Orchestrator (phase 4)** | [`scripts/run_orchestrator_job.py`](scripts/run_orchestrator_job.py), [`docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md`](docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md) | Declarative job JSON → `scan-bundle` + optional **`admit_model` fan-out** + optional **`dynamic_probe`** + **envelope v2** (`run_id`, per-step timestamps). **`make orchestrator-validate`**. |
| **Dynamic probe stub (phase 5)** | [`scripts/run_dynamic_probe.py`](scripts/run_dynamic_probe.py), [`docs/PHASE5_DYNAMIC_PROBES.md`](docs/PHASE5_DYNAMIC_PROBES.md) | Opt-in via **`LLM_SCANNER_DYNAMIC_PROBE=1`**; writes **`llm_scanner.dynamic_probe_report.v1`**. Supports controlled modes (`execution_mode=preflight|execute_once`) with bounded command execution. Orchestrator **`run`** forwards `run_id`, budgets, and config metadata. **`make dynamic-probe-stub`**. |
| **Optional surfaces** | MCP + HTTP | Bounded tools for agents; see [hf_bundle_scanner/docs/hermes-mcp.md](hf_bundle_scanner/docs/hermes-mcp.md). |

---

## What this repository does **not** do

- **It is not a full application or RAG pentest.** Phase 8 and the roadmap describe broader evals; today the default path is **artifact + config static** analysis inside a bundle directory.
- **It does not run real Garak harnesses in default CI.** The phase-5 entrypoint defaults to **`status: disabled`**; set **`LLM_SCANNER_DYNAMIC_PROBE=1`** only when you intend to check tooling (`garak --help` today, real probes later).
- **It does not replace legal, compliance, or vendor attestation.** Findings are **technical signals**; severity and policy live in **your** policy JSON and process.
- **It is not a hosted scanner SaaS.** You run CLI, Makefile, MCP, or HTTP **on your infrastructure**.
- **It does not silently “fix” models.** The gate **reports** and exits; it does not rewrite weights or auto-remediate Hub repos.

---

## Philosophy

1. **Explicit over magical** — Policy JSON, driver lists, and exit codes are visible and versionable. Surprise behavior belongs in documentation, not in defaults.
2. **Deterministic CI first** — Default tests avoid network and multi‑GiB downloads. Anything slow or flaky is **marked** and **env-gated**.
3. **OSS-by-default, commercial optional** — Static lanes prefer open tooling; commercial adapters stay behind explicit configuration (roadmap).
4. **Agents orchestrate, they do not replace judgment** — Hermes / MCP should call **bounded** tools; humans (or your org) own severity floors and ship decisions. See [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md).
5. **Phased honesty** — [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) names what exists today vs **phase 6–8** backlog (supply extras, runtime guards, observability); **phase 5** is the dynamic lane (stub now, real probes next). **Choice capture:** when multiple next steps are proposed and one ships first, the roadmap **Choice capture** table holds the others until they ship, are re-prioritized, or are explicitly declined.
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

# Another *benign* internal test snapshot (still has pickle-era ``pytorch_model.bin`` on disk):
make ephemeral-hub-scan OUT=/tmp/ephemeral-gpt2.json EPHEMERAL_FLAGS="--repo hf-internal-testing/tiny-random-GPT2Model"

# Richer multi-format Bart test weights + injected tokenizer risk → aggregate exit 1:
make ephemeral-hub-scan OUT=/tmp/ephemeral-bart-risk.json INJECT=1 EPHEMERAL_FLAGS="--repo hf-internal-testing/tiny-random-BartModel"
```

Use the venv interpreter for the helper itself when system Python lacks **`huggingface_hub`**:

```bash
"$(pwd)/.venv/bin/python" scripts/ephemeral_hub_scan.py --out /tmp/x.json --repo hf-internal-testing/tiny-random-GPT2Model
```

After a successful scan, the helper also writes an **HTML briefing** next to the bundle JSON (same path with a ``.html`` suffix) via ``scripts/export_bundle_action_sheet.py``, unless you pass ``--no-html``. Override the HTML path with ``--html-out PATH``.

Summarize any written bundle JSON: **`python3 scripts/summarize_bundle_json.py /tmp/ephemeral-gpt2.json`**.

**Broaden candidate discovery (metadata, ≤200 MiB default):** search the Hub for small model repos before you download anything heavy::

```bash
"$(pwd)/.venv/bin/python" scripts/hub_find_models_under_size.py --max-mb 200 --per-query 15
# Optional: probe a few hits with configlint on tokenizer_config.json / config.json (extra downloads)
"$(pwd)/.venv/bin/python" scripts/hub_find_models_under_size.py --max-mb 200 --per-query 10 --probe-configlint --max-probes 5
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

**Exit semantics (bundle aggregate):** worst child wins by priority — code **`4`** (usage), then **`2`** (driver/tooling), then **`1`** (policy / findings / certain configlint escalations), else **`0`** (`compute_aggregate_exit` in [`report.py`](hf_bundle_scanner/hf_bundle_scanner/report.py)). Config risk from **`CONFIG_RISK_RULE_IDS`** in [`dispatch.py`](hf_bundle_scanner/hf_bundle_scanner/dispatch.py) (mirrored in [`docs/policy/configlint_rule_defaults.json`](docs/policy/configlint_rule_defaults.json)) can raise the aggregate to **`1`** when the file lane was clean. See [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md).

---

## Live Hub sample reports (real download)

These are **committed outputs** from a **live** Hugging Face snapshot download (**`hf-internal-testing/tiny-random-BertModel`**), then the working tree was deleted. Among common `hf-internal-testing/tiny-random-*` snapshots, this repo is **one of the smallest** full multi-format fixtures we measured (~**1.3 MB** over the wire vs ~**2.1 MB** for `tiny-random-GPT2Model`), which keeps demos fast.

**About “small but vulnerable”:** this repository does **not** ship or recommend downloading known-malicious weights. In practice, “risky” Hub content usually means **(a)** policy-relevant formats (for example **pickle-capable** `pytorch_model.bin`), **(b)** **config** flags like `trust_remote_code`, or **(c)** your org’s **stricter policy** rejecting formats you do not want in production. The samples below illustrate **(b)** with a JSON-only demo file and **(c)** with a **safetensors-only** policy on the same benign test snapshot.

Snapshot paths are **redacted** to `/tmp/<ephemeral-hub-demo>` for readability. Index + context: [`docs/sample_reports/README.md`](docs/sample_reports/README.md).

### Start here (actionable formats — not JSON)

If the JSON feels opaque, open the **human briefing pack** first:

- **[`docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md`](docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md)** — **non-technical** “what should we do?” narrative for the same three demos (regenerate: **`make plain-english-brief`**).
- **[`docs/sample_reports/actionable/README.md`](docs/sample_reports/actionable/README.md)** — how to read the **technical** columns.
- **[`docs/sample_reports/actionable/BLAST_RADIUS_LEADERSHIP.md`](docs/sample_reports/actionable/BLAST_RADIUS_LEADERSHIP.md)** — **leadership brief**: executive **dashboard** (signal + 1–5 score + **OWASP LLM** touchpoints + board decision), then blast-radius narrative and issue roll-up.
- **[`docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv`](docs/sample_reports/actionable/UNIFIED_ACTION_SHEET.csv)** — one spreadsheet with **all three demos** (filter on `demo_id`) including **`risk_rating`**, **`prod_impact_if_shipped`**, **`blast_radius`**, **`exec_one_liner`**, plus **decision-support** columns (**`reference_citations`**, **`owasp_genai_catalog_hint`**, **`decision_catalog_version`**) sourced from [`docs/reporting/decision_support_rule_catalog.json`](docs/reporting/decision_support_rule_catalog.json).
- **[`docs/sample_reports/actionable/SCAN_BRIEFING.html`](docs/sample_reports/actionable/SCAN_BRIEFING.html)** — the same story as tables in a browser (leadership section first). **GitHub’s repo file view shows HTML as source only** — open locally or use the rendered preview link in [`actionable/README.md`](docs/sample_reports/actionable/README.md).

**PDF (no extra tooling):** open `SCAN_BRIEFING.html` in a real browser → **Print** → **Save as PDF**.

Regenerate after changing sample JSON: `make sample-reports-all` (technical sheets + plain brief), or separately `make sample-action-sheets` / `make plain-english-brief`. The bundle exporter also accepts optional `--repo-root` if not run from the repo root.

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

`merge_aggregate_exit` intentionally escalates **0 → 1** when configlint emits a **`rule_id`** in **`CONFIG_RISK_RULE_IDS`** (see [`dispatch.py`](hf_bundle_scanner/hf_bundle_scanner/dispatch.py)). That is **not** proof of exploitation — it is a **policy signal** that your integration is asking for a sharper review before production.

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

## Where we are (roadmap)

| Phase | Status (high level) | What to read next |
| ----- | -------------------- | ----------------- |
| **0–1** | **Shipped** — taxonomy, bundle **`hf_bundle_scanner.bundle_report.v2`**, **`provenance`** | [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md), [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) |
| **2** | **In progress** — Lane A static demos (**ModelScan** / **ModelAudit** via `--drivers`; `make drivers-help`), **configlint** tokens, **human/actionable** sample exports | This README (Hub + reports below), [`hf_bundle_scanner/README.md`](hf_bundle_scanner/README.md), [`hf_bundle_scanner/hf_bundle_scanner/configlint.py`](hf_bundle_scanner/hf_bundle_scanner/configlint.py) |
| **3+** | **In progress (OSS slice)** — org **configlint** policy template ([`docs/policy/`](docs/policy/)); wider loader heuristics + orchestrator scope + opt-in dynamic probes on the roadmap | [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md#phases-non-overlapping-todos) |

---

## Documentation hub

| Topic | Where |
| ----- | ----- |
| Agent entry + commands | [AGENTS.md](AGENTS.md) |
| Phased roadmap (0–8) | [docs/PRODUCTION_SCANNER_ROADMAP.md](docs/PRODUCTION_SCANNER_ROADMAP.md) |
| ADR starter (bundle vs orchestrator, phase 4) | [docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md](docs/adr/0001-bundle-scanner-vs-orchestrator-scope.md) |
| Threat model & OWASP mapping | [docs/THREAT_MODEL_TAXONOMY.md](docs/THREAT_MODEL_TAXONOMY.md) |
| Pytest & test-case index | [docs/TEST_CASES_LLM_SECURITY_SCANNER.md](docs/TEST_CASES_LLM_SECURITY_SCANNER.md) |
| Hermes / MCP boundaries | [docs/HERMES_AGENTS.md](docs/HERMES_AGENTS.md) |
| Harness: Makefile, session log, graphify | [docs/LONG_HORIZON_HARNESS.md](docs/LONG_HORIZON_HARNESS.md) |
| Append-only session memory | [docs/sessions/SESSION_LOG.md](docs/sessions/SESSION_LOG.md) |
| Publish / mirror notes | [docs/PUBLISH_ARGUS.md](docs/PUBLISH_ARGUS.md) |
| Lessons learned (paths, git, CI) | [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md) |
| Agent pytest artifacts (local) | [`.agent/README.md`](.agent/README.md) |
| Live Hub sample bundle JSON | [docs/sample_reports/](docs/sample_reports/) |
| Human briefing + blast radius (CSV / HTML / MD) | [docs/sample_reports/actionable/](docs/sample_reports/actionable/) |
| Plain-language approver brief (same samples) | [docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md](docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md) |
| Decision-support rule catalog (exports + citations) | [docs/reporting/](docs/reporting/) |
| Org **configlint** escalation template (fork for CI/policy) | [docs/policy/](docs/policy/) |
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
| `make ephemeral-hub-scan` | `OUT=/tmp/report.json` — live Hub download → scan → delete tree ([`scripts/ephemeral_hub_scan.py`](scripts/ephemeral_hub_scan.py); optional `INJECT=1`) |
| `make sample-action-sheets` | Regenerate [`docs/sample_reports/actionable/`](docs/sample_reports/actionable/) (CSV, HTML, leadership MD) from committed sample JSON |
| `make plain-english-brief` | Write [`PLAIN_ENGLISH_BRIEF.md`](docs/sample_reports/actionable/PLAIN_ENGLISH_BRIEF.md) only (does not overwrite CSV/HTML/blast MD) |
| `make sample-reports-all` | Runs **`sample-action-sheets`** then **`plain-english-brief`** |
| `make drivers-help` | Print **`model-admission`** scan driver names (`modelscan`, `modelaudit`) and **`MODELSCAN_BIN` / `MODELAUDIT_BIN`** hints (after `make install`) |

You can also run `make` from **`hf_bundle_scanner/`**; that Makefile forwards to the root.

---

## CLI syntax (minimal)

Full flags for **`scan-bundle`** / **`download`** / **`manifest`** live in [`hf_bundle_scanner/README.md`](hf_bundle_scanner/README.md). Common **`scan-bundle scan`** shape from repo root:

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

**Per-file gate** (single artifact): `admit-model scan --artifact … --policy … --report … --drivers "" --timeout 600 --fail-on MEDIUM` — policy JSON shape: [`model-admission/README.md`](model-admission/README.md).

**Configlint rules** that can bump **`aggregate_exit_code`** to **`1`** when the file lane is otherwise clean: **`CONFIG_RISK_RULE_IDS`** in [`dispatch.py`](hf_bundle_scanner/hf_bundle_scanner/dispatch.py) (also in [`docs/policy/configlint_rule_defaults.json`](docs/policy/configlint_rule_defaults.json)). Other configlint signals (e.g. `use_fast_tokenizer_truthy`, `use_safetensors_disabled`) appear in **`config_findings`** but do not currently force that escalation — the **actionable** exports spell out that contrast for leadership ([`docs/sample_reports/actionable/`](docs/sample_reports/actionable/), columns **`default_ci_blocks_release`** + narrative fields + **`reference_citations`**).

---

## Environment variables (bundle / admit)

| Variable | Purpose |
| -------- | ------- |
| **`HF_BUNDLE_PYTHON`** | Interpreter used to spawn **`admit-model`** / **`python -m model_admission`** (set when paths contain spaces). |
| **`HF_BUNDLE_ADMIT_CMD`** | Optional override for admit argv (advanced; quoting pitfalls — see [docs/LESSONS_LEARNED.md](docs/LESSONS_LEARNED.md)). |
| **`HF_BUNDLE_MIRROR_ALLOWLIST`** | Comma-separated mirror hosts merged into **`provenance`**. |
| **`HF_BUNDLE_SBOM_URI`** | SBOM pointer merged into **`provenance`**. |
| **`LLM_SCANNER_TEST_CATALOG`** | Absolute path to [`llm_security_test_cases/catalog.json`](llm_security_test_cases/catalog.json) for pytest harnesses ([`scripts/run_tests_for_agent.py`](scripts/run_tests_for_agent.py)). |
| **`MODELSCAN_BIN`**, **`MODELAUDIT_BIN`** | Override **`modelscan`** / **`modelaudit`** executables when using **`--drivers`** on **`admit-model`** or **`scan-bundle scan`** (see [`model-admission/README.md`](model-admission/README.md)). |

---

## Root helper scripts (syntax)

| Script | Purpose | Example |
| ------ | ------- | ------- |
| [`scripts/ephemeral_hub_scan.py`](scripts/ephemeral_hub_scan.py) | Hub **`snapshot_download`** → **`scan-bundle`** → delete temp tree | `HF_BUNDLE_PYTHON="$(pwd)/.venv/bin/python" python3 scripts/ephemeral_hub_scan.py --out /tmp/r.json` · optional `--inject-demo-tokenizer-risk` · `--policy` path |
| [`scripts/export_bundle_action_sheet.py`](scripts/export_bundle_action_sheet.py) | Bundle JSON → **CSV + HTML +** `BLAST_RADIUS_LEADERSHIP.md` (OWASP + board call + catalog citations) | `python3 scripts/export_bundle_action_sheet.py` · optional `--repo-root` / `--csv-out` / `--html-out` / `--md-out` |
| [`scripts/export_plain_english_brief.py`](scripts/export_plain_english_brief.py) | Same sample JSON → **`PLAIN_ENGLISH_BRIEF.md`** (non-technical approver narrative) | `python3 scripts/export_plain_english_brief.py` · optional `--out` / `--repo-root` |
| [`scripts/redact_ephemeral_report.py`](scripts/redact_ephemeral_report.py) | Strip ephemeral `/tmp/hf-ephemeral-*` paths before committing a sample | `python3 scripts/redact_ephemeral_report.py /tmp/in.json docs/sample_reports/out.json` |
| [`scripts/summarize_bundle_json.py`](scripts/summarize_bundle_json.py) | Short stdout summary of a bundle JSON (paths, exits, configlint hits) | `python3 scripts/summarize_bundle_json.py /tmp/ephemeral-gpt2.json` |
| [`scripts/hub_find_models_under_size.py`](scripts/hub_find_models_under_size.py) | Hub **metadata** search: repos whose summed file sizes are under **`--max-mb`** (default **200**); optional **`--probe-configlint`** | `.venv/bin/python scripts/hub_find_models_under_size.py --max-mb 200 --per-query 12` |
| [`scripts/run_tests_for_agent.py`](scripts/run_tests_for_agent.py) | **`make agent-verify`** backend; writes **`.agent/pytest-last.log`** | `make agent-verify` |
| [`scripts/git_commit_via_file.py`](scripts/git_commit_via_file.py) | Commit when `git commit -m` / trailers misbehave | `python3 scripts/git_commit_via_file.py 'subject line'` |
| [`scripts/git_doctor.py`](scripts/git_doctor.py) | Diagnose trailer / identity issues | `make git-doctor` |

---

## Outputs & reports (what to attach where)

| Output | Produced by | Attach to |
| ------ | ----------- | --------- |
| **`.agent/pytest-last.log`** | `make agent-verify` | CI debugging, agent session |
| **`docs/sample_reports/*.json`** | `scripts/ephemeral_hub_scan.py` (then redact paths) | Engineering evidence of bundle schema |
| **`docs/sample_reports/actionable/*`** | `make sample-reports-all` (or `make sample-action-sheets` + `make plain-english-brief`) | **Leadership / risk**: CSV, HTML, `BLAST_RADIUS_LEADERSHIP.md` + **`PLAIN_ENGLISH_BRIEF.md`** ([index](docs/sample_reports/actionable/README.md)) |

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
