# Reporting — decision support rule catalog

This folder holds **human-decision** material that is safe to version in git (no secrets).

## Files

| File | Purpose |
| ---- | ------- |
| [`decision_support_rule_catalog.json`](decision_support_rule_catalog.json) | Machine-readable **rule_id → references + guidance** used by [`scripts/export_bundle_action_sheet.py`](../../scripts/export_bundle_action_sheet.py) for CSV / HTML / `BLAST_RADIUS_LEADERSHIP.md`. |

## When to edit

- **`configlint.py` emits a new `rule_id`** → add a catalog row and decide **`blocks_default_ci`** (must match [`hf_bundle_scanner/dispatch.py`](../../hf_bundle_scanner/hf_bundle_scanner/dispatch.py) unless you change dispatch in the same PR). Current informational examples include `use_fast_tokenizer_truthy`, `use_auth_token_present`, `use_safetensors_disabled`.
- **`dispatch.py` changes which rules escalate** → update `blocks_default_ci` + `maintainer_note` in the JSON.
- **You want clearer leadership language** → edit `legend_takeaway` / `expert_guidance` / `vs_trust_remote_code` (keep claims honest: static signals, not exploit proof).

## `blocks_default_ci` meaning

- **`true`**: this `rule_id` participates in **`config_risk`** aggregation that can raise **`aggregate_exit_code`** to **`1`** when file scans are clean (today: `trust_remote_code_enabled`, `auto_map_custom_classes`, `config_json_invalid`).
- **`false`**: emitted for awareness; leadership may still care, but **default CI** does not treat it as the same gate failure class.

## References

Prefer **primary** sources (OWASP GenAI, NIST, vendor security docs) and the in-repo [`THREAT_MODEL_TAXONOMY.md`](../THREAT_MODEL_TAXONOMY.md). The catalog’s `global_references` array is copied into exports as a bibliography-style anchor.
