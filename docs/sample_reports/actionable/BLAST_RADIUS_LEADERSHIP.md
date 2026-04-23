# Blast radius & leadership brief (sample Hub demos)

This document is generated from the same three committed bundle JSON samples as [`UNIFIED_ACTION_SHEET.csv`](UNIFIED_ACTION_SHEET.csv). It answers: **if we ignored these static signals and deployed, what breaks — and who cares?**

> **Scope:** static admission + configlint only. It does **not** cover prompt abuse, toxicity, full supply-chain pen tests, or runtime guardrails. Treat as **one control column** in a broader AI governance program.

---

## Baseline — permissive policy, no injected config risk

- **Demo id:** `01_baseline`
- **Risk (bundle-level):** LOW (static admission gate)
- **Executive one-liner:** Static gate SHIP_OK_ON_STATIC_GATE for this snapshot — leadership should still budget runtime AI risk and supply-chain controls outside this JSON.

### If this snapshot reached production (ignoring the gate)

If `hf-internal-testing/tiny-random-BertModel` reached production with the same loader posture as this scan, nothing in this **static** report blocks release: policy and empty driver lane raised no finding. That does **not** prove safety—only that this gate did not fire. Residual classes of prod risk still apply: prompt injection and toxic outputs, application data exfiltration, wrong revision or mirror substitution, and higher inherent risk for pickle-era formats such as `pytorch_model.bin` if an attacker could swap weights.

### Blast radius (who / what can be touched)

**Primary:** the serving/training fleet identity (cloud IAM, k8s service accounts) and any databases or APIs the app can reach while running this model. **Secondary:** customer trust, regulatory reporting if PII is processed, and SOC workload if behavior changes. **Not modeled here:** runtime guardrails, network egress policy, or human review of Hub revision history.

### All identified signals in this demo (counts)

- **Rows in detail sheet:** 3 (0 config, 3 clean weight rows, 0 blocked/policy findings)
  - `WEIGHT_FILE`: **3**

| Kind | Subject / path | Risk | Leadership line |
| ---- | -------------- | ---- | ----------------- |
| WEIGHT_FILE | onnx/model.onnx | LOW–MEDIUM (residual supply chain) | No static blocker — confirm revision pinning and mirror policy. |
| WEIGHT_FILE | pytorch_model.bin | MEDIUM (residual format risk) | No static finding — leadership should still ask whether **.bin** is acceptable in **your** prod threat model. |
| WEIGHT_FILE | tf_model.h5 | LOW–MEDIUM (residual supply chain) | No static blocker — confirm revision pinning and mirror policy. |

---

## Same snapshot — demo tokenizer_config (trust_remote_code)

- **Demo id:** `02_demo_config_risk`
- **Risk (bundle-level):** CRITICAL (remote code execution path on load)
- **Executive one-liner:** Static gate HOLD_REVIEW_POLICY_OR_CONFIG — treat as **undeclared RCE-class supply chain** on load until explicitly waived with hardened controls and owner sign-off.

### If this snapshot reached production (ignoring the gate)

If production loaders honor `trust_remote_code`, a malicious or compromised Hub revision (or dependency confusion) can execute **Python during model/tokenizer load**, before your application logic runs its usual checks. That is comparable to shipping an unreviewed install hook on the hot path: environment secrets, cloud metadata credentials, lateral movement to batch jobs, and silent persistence become plausible incident shapes.

### Blast radius (who / what can be touched)

**Typically:** the whole namespace or VM scale set running inference, shared images and caches, CI runners that materialize tokenizer files, and any secrets mounted into those workloads. **Regulatory / comms:** expands materially if the model touches regulated data — breach timelines and customer notification may enter scope even without proven exfiltration.

### All identified signals in this demo (counts)

- **Rows in detail sheet:** 4 (1 config, 3 clean weight rows, 0 blocked/policy findings)
  - `CONFIG`: **1**
  - `WEIGHT_FILE`: **3**

| Kind | Subject / path | Risk | Leadership line |
| ---- | -------------- | ---- | ----------------- |
| CONFIG | /tmp/<ephemeral-hub-demo>/tokenizer_config.json | CRITICAL | `trust_remote_code` truthy — **stop-the-line** for prod until removed or formally accepted with compensating controls. |
| WEIGHT_FILE | onnx/model.onnx | LOW–MEDIUM (residual supply chain) | No static blocker — confirm revision pinning and mirror policy. |
| WEIGHT_FILE | pytorch_model.bin | MEDIUM (residual format risk) | No static finding — leadership should still ask whether **.bin** is acceptable in **your** prod threat model. |
| WEIGHT_FILE | tf_model.h5 | LOW–MEDIUM (residual supply chain) | No static blocker — confirm revision pinning and mirror policy. |

---

## Same snapshot — safetensors-only policy (reject .bin/.onnx/.h5)

- **Demo id:** `03_strict_safetensors_only`
- **Risk (bundle-level):** HIGH (governance / policy breach; format risk)
- **Executive one-liner:** Static gate HOLD_REVIEW_POLICY_OR_CONFIG — leadership question is: **waive with recorded risk acceptance** or **convert/remove blocked artifacts** before prod.

### If this snapshot reached production (ignoring the gate)

If teams bypass this gate and deploy anyway, production would contain **file types your org explicitly banned** (here: `.onnx`, `.bin`, `.h5`). That weakens audit answers (“safetensors-only”), increases operational surprise, and raises the likelihood of **unsafe deserialization** incidents if weights ever become attacker-controlled or accidentally swapped.

### Blast radius (who / what can be touched)

**Compliance & procurement:** SOC2 / ISO evidence gaps and vendor questionnaires. **Operations:** downstream systems that assumed “no pickle weights” may behave incorrectly or open incident bridges. **Security:** incident blast follows the inference footprint and any shared artifact store where the disallowed files land.

### All identified signals in this demo (counts)

- **Rows in detail sheet:** 3 (0 config, 0 clean weight rows, 3 blocked/policy findings)
  - `FINDING`: **3**

| Kind | Subject / path | Risk | Leadership line |
| ---- | -------------- | ---- | ----------------- |
| FINDING | onnx/model.onnx | HIGH | Blocked artifact `onnx/model.onnx` — waive only with **named executive risk acceptance**. |
| FINDING | pytorch_model.bin | HIGH | Blocked artifact `pytorch_model.bin` — waive only with **named executive risk acceptance**. |
| FINDING | tf_model.h5 | HIGH | Blocked artifact `tf_model.h5` — waive only with **named executive risk acceptance**. |

---

## Cross-demo comparison (for steering committees)

| Demo | Static gate | Main leadership story |
| ---- | ----------- | ----------------------- |
| `01_baseline` | exit **0** | Static gate SHIP_OK_ON_STATIC_GATE for this snapshot — leadership should still budget runtime AI risk and supply-chain controls outside this JSON. |
| `02_demo_config_risk` | exit **1** | Static gate HOLD_REVIEW_POLICY_OR_CONFIG — treat as **undeclared RCE-class supply chain** on load until explicitly waived with hardened controls and owner sign-off. |
| `03_strict_safetensors_only` | exit **1** | Static gate HOLD_REVIEW_POLICY_OR_CONFIG — leadership question is: **waive with recorded risk acceptance** or **convert/remove blocked artifacts** before prod. |

_Regenerate:_ `python3 scripts/export_bundle_action_sheet.py` or `make sample-action-sheets`.
