# Org policy templates (LLM Scanner)

Machine-readable defaults you can **copy into your org** and extend (do not treat these files as executable policy engines by themselves).

| File | Purpose |
| ---- | ------- |
| [`configlint_rule_defaults.json`](configlint_rule_defaults.json) | Every **`rule_id`** emitted by `hf_bundle_scanner.configlint`, with **`default_aggregate_escalates`** matching **`hf_bundle_scanner.dispatch.CONFIG_RISK_RULE_IDS`** today. |

**How to use:** fork the JSON, add columns (`owner`, `severity_override`, `ticket_template_url`, …), and wire your CI/reporting to your fork. When upstream adds a `rule_id`, `pytest` drift tests will fail until you merge the new row.

See also: [decision support catalog](../reporting/decision_support_rule_catalog.json) (narrative + citations for exports).
