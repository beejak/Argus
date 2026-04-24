# Plain-language brief (for approvers)

This page is **not** a replacement for legal, compliance, or security sign-off. It translates the same three **sample** bundle scans into **everyday language** so you can decide **who to pull into the room** and **what question to ask next**.

> **What this is:** a **static** check of files and config in a model folder — think “airport metal detector,” not a full background investigation. It does **not** test whether the model will behave badly in chat, whether your app is secure, or whether someone poisoned weights in a clever way the scanner did not model.

---

## How to use this in a meeting

1. Read **Your bottom line** for each scenario below.
2. If it says **stop / fail**, do not debate the math — assign **security + ML** to either **fix** or **waive with a written risk note**.
3. If it says **pass for this check**, still ask whether **your** production rules need more than static files (runtime monitoring, access control, etc.).

---

## Baseline — permissive policy, no injected config risk

**Teaching label:** `01_baseline` · **Model source (sample):** hf-internal-testing/tiny-random-BertModel

### Your bottom line

- **This automated static gate did not raise a stop signal on the files we checked.**
- **What to do next:** You may treat this as okay for this specific check only. It does not mean the product is “safe” overall — ask your team about real-world risks (data leaks, prompt abuse, wrong model version, etc.).

### What the checks noticed

On this sample, the automated config hints and policy gates we show here did **not** add extra **stop** reasons beyond the overall headline above.

### If you only remember one thing

- Ask: **“Did we run the right policy for how we sell this product?”**
- Ask: **“Who owns the waiver if we ship anyway?”**

---

## Same snapshot — demo tokenizer_config (trust_remote_code)

**Teaching label:** `02_demo_config_risk` · **Model source (sample):** hf-internal-testing/tiny-random-BertModel

### Your bottom line

- **This snapshot would fail a typical release gate until someone fixes the issue or formally accepts the risk.**
- **What to do next:** Do not ship to customers on this signal alone. Pick an owner (security + ML), decide fix vs waive, and record the decision.

### What the config check noticed (plain words)

These are **automatic hints** from JSON settings — not proof someone attacked you:

- A tokenizer/loader setting is on that can let **supplier-provided code run when the model loads** (same risk family as running an installer you did not separately vet).

### If you only remember one thing

- Ask: **“Did we run the right policy for how we sell this product?”**
- Ask: **“Who owns the waiver if we ship anyway?”**

---

## Same snapshot — safetensors-only policy (reject .bin/.onnx/.h5)

**Teaching label:** `03_strict_safetensors_only` · **Model source (sample):** hf-internal-testing/tiny-random-BertModel

### Your bottom line

- **This snapshot would fail a typical release gate until someone fixes the issue or formally accepts the risk.**
- **What to do next:** Do not ship to customers on this signal alone. Pick an owner (security + ML), decide fix vs waive, and record the decision.

### What the file rules noticed

Your **policy** for this demo rejected at least one file path or type:

- **onnx/model.onnx:** Policy violation — extension '.onnx' not in allowed_extensions
- **pytorch_model.bin:** Policy violation — extension '.bin' not in allowed_extensions
- **tf_model.h5:** Policy violation — extension '.h5' not in allowed_extensions

### If you only remember one thing

- Ask: **“Did we run the right policy for how we sell this product?”**
- Ask: **“Who owns the waiver if we ship anyway?”**

---

## Where the technical detail lives

- **Spreadsheet + tables:** [`UNIFIED_ACTION_SHEET.csv`](UNIFIED_ACTION_SHEET.csv), [`SCAN_BRIEFING.html`](SCAN_BRIEFING.html), [`BLAST_RADIUS_LEADERSHIP.md`](BLAST_RADIUS_LEADERSHIP.md) — for engineers and auditors.
- **Raw machine output:** the `docs/sample_reports/*.json` bundle files — for forensics and CI.

_Regenerate this plain brief:_ `python3 scripts/export_plain_english_brief.py` or `make plain-english-brief`.
