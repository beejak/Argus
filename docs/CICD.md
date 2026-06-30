# Argus — CI/CD Integration Guide

This document explains the existing GitHub Actions workflow, how to add Argus to any CI pipeline, policy file versioning, and three common integration patterns.

---

## How the existing GitHub Actions workflow works

The workflow is defined in [`.github/workflows/llm-scanner.yml`](../.github/workflows/llm-scanner.yml).

### Trigger conditions

```yaml
on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]
  workflow_dispatch:
```

The workflow runs on every push or pull request targeting `main`/`master`, and can also be triggered manually via the GitHub UI (`workflow_dispatch`).

### Matrix strategy

The workflow runs a single job (`test`) across a matrix of **Python 3.11 and 3.12** in parallel, with `fail-fast: false` so both versions complete even if one fails.

### Steps in order

1. **Checkout** — `actions/checkout@v4` fetches the full working tree.
2. **Setup Python** — `actions/setup-python@v5` installs the matrix Python version.
3. **Pip cache** — `actions/cache@v4` caches `~/.cache/pip` keyed on the OS + Python version + a hash of both `pyproject.toml` files. Restores partial caches via fallback restore-keys.
4. **Install (monorepo)** — Runs the same two editable installs as `make install`:
   ```bash
   python -m pip install -U pip
   cd model-admission && pip install -e ".[dev]"
   cd ../hf_bundle_scanner && pip install -e ".[dev,mcp,http]"
   ```
   `PYTHONUTF8=1` is set to avoid encoding issues on Windows-hosted runners.
5. **Verify** — Runs `python scripts/run_tests_for_agent.py`, which:
   - Runs `model-admission` pytest (all tests)
   - Runs `hf_bundle_scanner` pytest excluding the `integration` marker
   - Runs `ruff check`
   - Validates three orchestrator fixtures
   - Writes a disabled dynamic-probe stub
   - Writes `.agent/pytest-last.log` and `.agent/pytest-last.exit`
6. **Upload agent log** — `actions/upload-artifact@v4` uploads `.agent/pytest-last.log` as artifact `pytest-last-py<version>`, even on failure (`if: always()`). Download it from the Actions run page to debug failures.

### What "green" means

Both Python matrix versions exit `0` from `scripts/run_tests_for_agent.py`. The badge in the README reflects the `main` branch status of this workflow.

---

## Adding Argus to any CI pipeline

The minimal steps to gate a model bundle in any CI system:

### 1. Install dependencies

```bash
pip install -U pip
pip install -e "path/to/model-admission/[dev]"
pip install -e "path/to/hf_bundle_scanner/[dev]"
# Optional: pip install modelscan modelaudit
```

### 2. Set the Python interpreter variable (if paths contain spaces)

```bash
export HF_BUNDLE_PYTHON="$(which python)"
```

### 3. Run the scan

```bash
scan-bundle scan \
  --root "$MODEL_SNAPSHOT_DIR" \
  --policy "$POLICY_FILE" \
  --out "$REPORT_OUT" \
  --drivers "" \
  --print-summary
SCAN_EXIT=$?
```

### 4. Act on the exit code

```bash
if [ "$SCAN_EXIT" -eq 0 ]; then
  echo "PASS: scan clean"
elif [ "$SCAN_EXIT" -eq 1 ]; then
  echo "BLOCK: policy or findings — route to human review"
  exit 1
elif [ "$SCAN_EXIT" -eq 2 ]; then
  echo "ALERT: tooling error — investigate scanner/driver setup"
  exit 2
elif [ "$SCAN_EXIT" -eq 4 ]; then
  echo "CONFIG BUG: bad arguments or unknown driver — fix pipeline"
  exit 4
fi
```

---

## Exit code → CI action mapping

| Exit code | Meaning | Recommended CI action |
| --------- | ------- | --------------------- |
| **0** | Clean — no policy violations or findings at/above the severity floor | **Pass** the gate; proceed with deployment |
| **1** | Policy violation, findings, or CONFIG_RISK configlint rule fired | **Block** the pipeline; route to human security review before proceeding |
| **2** | Tooling error — a driver subprocess failed, timed out, or is missing | **Alert** the platform/SRE team; investigate scanner or driver setup; do not treat as a clean pass |
| **4** | Usage error — bad arguments, unrecognised driver, or misconfigured pipeline | **Pipeline config bug** — fix the CI configuration; do not merge until resolved |

---

## Policy file versioning strategy

Policy files are plain JSON and should be treated as code:

1. **Store policy files in version control** alongside the code that references them. Suggested path: `policy/admission-policy.json` in your repo.

2. **Name policies by profile**, not by date. Examples:
   - `policy.permissive.json` — no extension or size restrictions; policy gate only
   - `policy.safetensors-only.json` — only `.safetensors` files allowed
   - `policy.strict.json` — size limit + extension allowlist + `modelscan` driver

3. **Pin the policy path in CI** using an environment variable or a hard-coded path, not a glob. This ensures determinism — a policy change requires an explicit file edit and code review.

4. **Log the policy hash** — `admit-model scan` records `policy_hash` (SHA-256 of the policy content) in the ledger entry and in `ScanReport.policy_path`. The bundle report also records `policy_path`. Use these fields to audit which policy was active for a given scan.

5. **Review policy changes in the same PR as code changes** they affect. If you relax `allowed_extensions`, that change should be reviewed alongside the model artifact change that requires it.

6. **Document escalation rules** — The `configlint_rule_defaults.json` in `docs/policy/` describes which configlint rule IDs escalate the aggregate exit code to `1`. Fork this file for your org and reference it from your policy documentation.

---

## Three integration patterns

### Pattern 1: Pre-merge gate

Block pull requests that introduce new or changed model artifacts. Scan runs on every PR; exit `1` or `2` fails the required check.

```yaml
# GitHub Actions example
- name: Scan model bundle
  env:
    HF_BUNDLE_PYTHON: ${{ env.pythonLocation }}/bin/python
  run: |
    scan-bundle scan \
      --root models/ \
      --policy policy/admission-policy.json \
      --out /tmp/bundle-report.json \
      --drivers "" \
      --print-summary
```

Mark this step as a **required status check** in your branch protection rules. Upload the report as an artifact for reviewers:

```yaml
- uses: actions/upload-artifact@v4
  if: always()
  with:
    name: bundle-report
    path: /tmp/bundle-report.json
```

### Pattern 2: Scheduled scan

Re-scan committed model artifacts on a schedule (e.g. nightly) to catch policy drift as your policy evolves, even when no PR was opened.

```yaml
on:
  schedule:
    - cron: '0 2 * * *'   # 02:00 UTC daily
  workflow_dispatch:

jobs:
  scheduled-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e "model-admission/[dev]" -e "hf_bundle_scanner/[dev]"
      - name: Scan
        run: |
          scan-bundle scan \
            --root models/ \
            --policy policy/admission-policy.json \
            --out /tmp/bundle-report.json \
            --drivers modelscan \
            --print-summary
        env:
          MODELSCAN_BIN: modelscan
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: scheduled-scan-${{ github.run_id }}
          path: /tmp/bundle-report.json
```

A non-zero exit on scheduled scans should trigger an alert (Slack notification, PagerDuty, etc.) even if no code changed.

### Pattern 3: Download-then-scan

Download a Hugging Face snapshot, scan it, then optionally delete the local copy. Suitable for admission workflows that pull from the Hub before serving.

```bash
# Step 1: Download
scan-bundle download \
  --repo org/model-name \
  --revision main \
  --dest /tmp/model-snapshot

# Step 2: Scan
scan-bundle scan \
  --root /tmp/model-snapshot \
  --policy policy/admission-policy.json \
  --out /tmp/bundle-report.json \
  --hub-repo org/model-name \
  --hub-revision main \
  --sbom-uri "file:///path/to/sbom.json" \
  --drivers "" \
  --print-summary

SCAN_EXIT=$?

# Step 3: Gate
if [ "$SCAN_EXIT" -ne 0 ]; then
  rm -rf /tmp/model-snapshot
  echo "Scan failed with exit $SCAN_EXIT — snapshot deleted"
  exit "$SCAN_EXIT"
fi

# Step 4: Proceed with admitted snapshot
echo "Snapshot admitted — proceeding"
```

The `--hub-repo`, `--hub-revision`, and `--sbom-uri` flags are echoed into the bundle report's `provenance` field so downstream SIEMs and auditors can tie the report to exactly what was scanned and from where.

Use `scripts/ephemeral_hub_scan.py` as a higher-level wrapper for pattern 3 in ad-hoc or demo contexts (`make ephemeral-hub-scan OUT=/tmp/report.json`).

---

## Environment variable configuration in CI secrets

Never hard-code tokens, mirror credentials, or SBOM URIs in workflow YAML. Use CI secrets:

| Variable | Recommended secret name | Notes |
| -------- | ----------------------- | ----- |
| `HF_TOKEN` | `HF_TOKEN` | Hugging Face API token for private repos; passed to `huggingface_hub` automatically when set in environment |
| `HF_BUNDLE_MIRROR_ALLOWLIST` | `HF_BUNDLE_MIRROR_ALLOWLIST` | Comma-separated mirror hostnames; safe to store as a variable (not a secret) unless hostnames are sensitive |
| `HF_BUNDLE_SBOM_URI` | `HF_BUNDLE_SBOM_URI` | SBOM storage URI; may be a secret if it contains auth tokens |
| `MODELSCAN_BIN` | — | Usually a path, not a secret; set as an env var in the workflow step |
| `MODELAUDIT_BIN` | — | Same as above |

In GitHub Actions:

```yaml
env:
  HF_TOKEN: ${{ secrets.HF_TOKEN }}
  HF_BUNDLE_MIRROR_ALLOWLIST: ${{ vars.HF_BUNDLE_MIRROR_ALLOWLIST }}
  HF_BUNDLE_SBOM_URI: ${{ secrets.HF_BUNDLE_SBOM_URI }}
```

The `LLM_SCANNER_DYNAMIC_PROBE` variable should **not** be set in default CI. Only enable it in dedicated dynamic-probe workflow jobs that have access to a Garak environment (`.venv-garak/`).
