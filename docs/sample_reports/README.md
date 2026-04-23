# Sample bundle reports (real Hub downloads)

**Prefer a human briefing?** Start at **[`actionable/`](actionable/)** — committed **CSV** (Excel-friendly), **HTML** (print → PDF), and **[`BLAST_RADIUS_LEADERSHIP.md`](actionable/BLAST_RADIUS_LEADERSHIP.md)** (exec prod impact + blast radius) derived from the JSON below.

These JSON files were produced by [`scripts/ephemeral_hub_scan.py`](../../scripts/ephemeral_hub_scan.py) against **`hf-internal-testing/tiny-random-BertModel`** (small public snapshot used by Hugging Face for tests).

| File | What it demonstrates |
| ---- | -------------------- |
| [`live_hub_tiny_bert_bundle_report.json`](live_hub_tiny_bert_bundle_report.json) | **Clean lane:** permissive policy, no injected tokenizer risk, aggregate exit **`0`**. |
| [`live_hub_tiny_bert_bundle_report_with_demo_risk.json`](live_hub_tiny_bert_bundle_report_with_demo_risk.json) | **Config risk lane:** same snapshot + **synthetic** `tokenizer_config.json` with `trust_remote_code: true` (demo-only) → **`trust_remote_code_enabled`** → aggregate exit **`1`**. |
| [`live_hub_tiny_bert_bundle_report_strict_safetensors_policy.json`](live_hub_tiny_bert_bundle_report_strict_safetensors_policy.json) | **Strict policy lane:** same snapshot + [`policy.safetensors-only.json`](../../hf_bundle_scanner/tests/fixtures/policy.safetensors-only.json) → `.onnx` / `.bin` / `.h5` fail the extension allow-list → aggregate exit **`1`**. |

Snapshot directory paths inside JSON are redacted to **`/tmp/<ephemeral-hub-demo>`** for readability; your local runs will show a unique temp folder name.
