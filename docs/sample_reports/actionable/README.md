# Human-readable scan outputs (start here)

The raw bundle reports are JSON (`hf_bundle_scanner.bundle_report.v2`). If you want **actionable intelligence** in formats you can skim in a minute, use these instead:

| File | What it is | Best for |
| ---- | ---------- | -------- |
| [`BLAST_RADIUS_LEADERSHIP.md`](BLAST_RADIUS_LEADERSHIP.md) | **Leadership / steering:** prod impact, **blast radius**, and a roll-up of **every** signal per demo (generated from the same JSON as the CSV). | Exec readout, risk committee appendix, Confluence paste. |
| [`UNIFIED_ACTION_SHEET.csv`](UNIFIED_ACTION_SHEET.csv) | One spreadsheet: **three demos** + columns **`risk_rating`**, **`prod_impact_if_shipped`**, **`blast_radius`**, **`exec_one_liner`**. | Excel / Sheets: filter by `demo_id`, sort by `risk_rating`. |
| [`SCAN_BRIEFING.html`](SCAN_BRIEFING.html) | Tables: **leadership blast-radius** section first, then full detail. | Screen readout; **Print → Save as PDF** for a fixed artifact. |

## Why `SCAN_BRIEFING.html` looks “broken” on GitHub

**GitHub’s file viewer never runs HTML** in the browser for repos (you always see tags). That is normal security behavior — the file is still valid.

**Ways to see the real page (tables + styling):**

1. **Local checkout:** open `docs/sample_reports/actionable/SCAN_BRIEFING.html` in Chrome/Edge/Firefox (double-click or drag into a tab).
2. **Rendered preview (public `main`):** [raw.githack.com mirror of this HTML](https://raw.githack.com/beejak/Argus/main/docs/sample_reports/actionable/SCAN_BRIEFING.html) — serves `Content-Type: text/html` so the page renders.
3. **Raw file then “Open with…”** does *not* apply on github.com; use (1) or (2).

If `raw.githack.com` is slow or blocked, use (1) or print the Markdown brief [`BLAST_RADIUS_LEADERSHIP.md`](BLAST_RADIUS_LEADERSHIP.md) instead.

## How to read a row

- **`demo_id` / `demo_title`**: which teaching scenario this row belongs to (same Hub test snapshot; different policy or injected config).
- **`row_kind`**: `EXEC_SUMMARY` = whole-bundle rollup; `CONFIG` = configlint; `WEIGHT_FILE` = scanned weight-like file with no driver/policy finding; `FINDING` = a concrete violation to fix or waive.
- **`scanner_signal`**: short echo of what the machine saw (exit codes, rule ids, messages).
- **`human_meaning`**: plain-language interpretation (not legal advice; not proof of exploitation).
- **`recommended_next_step`**: what a security or ML engineer typically does next in a review workflow.
- **`risk_rating`**: coarse leadership tier (not CVSS): **LOW / MEDIUM / HIGH / CRITICAL** with short context in parentheses where needed.
- **`prod_impact_if_shipped`**: what could go wrong if this snapshot were deployed **while ignoring** the static gate for that row.
- **`blast_radius`**: who and what could be touched (fleet IAM, secrets, compliance, customers) — **scenario text**, not incident forensics.
- **`exec_one_liner`**: one sentence suitable for a steering slide or Jira summary.
- **`signal_light`**: **GREEN / AMBER / RED** traffic light for this row (static gate lens only).
- **`exec_risk_score_1_to_5`**: coarse leadership severity (not CVSS); see the score rubric in [`BLAST_RADIUS_LEADERSHIP.md`](BLAST_RADIUS_LEADERSHIP.md).
- **`recommended_decision` / `recommended_decision_explained`**: machine token + one-line board call.
- **`owasp_llm_primary` / `owasp_llm_secondary` / `owasp_touchpoints`**: mapping to **OWASP Top 10 for LLM Applications (2025 framing)** as summarized in-repo.
- **`risk_taxonomy_category`**: phase0 `RiskCategory` bucket (`config`, `provenance`, `artifact`, `supply_chain`, …).
- **`taxonomy_version`**, **`threat_model_doc`**, **`owasp_project_url`**: pointers to [`docs/THREAT_MODEL_TAXONOMY.md`](../../THREAT_MODEL_TAXONOMY.md) and the official OWASP project.
- **`default_ci_blocks_release`**: **YES / NO / N_A** — whether this signal **flips the bundle aggregate exit code in default CI today** (mirrors `hf_bundle_scanner.dispatch.scan_bundle` for configlint; separate logic for failed artifact rows).
- **`compared_to_worst_case_loader_risk`**: plain-language comparison to **`trust_remote_code`** as the reference “worst static loader” story (e.g. `use_fast_tokenizer_truthy` vs `trust_remote_code_enabled`).
- **`decision_support_expert`**: concise **what leadership should do next** for that row (not legal advice).
- **`reference_citations`**: authoritative **title + URL** strings pulled from [`docs/reporting/decision_support_rule_catalog.json`](../../reporting/decision_support_rule_catalog.json) when the row’s `rule_id` is catalogued (exec summary rows also include the catalog’s global bibliography).
- **`owasp_genai_catalog_hint`**: optional **OWASP GenAI / LLM Top 10** crosswalk notes from the same catalog (supplements `owasp_touchpoints`; numbering may differ from older slide decks — verify against [genai.owasp.org](https://genai.owasp.org/llm-top-10/)).
- **`decision_catalog_version`**: catalog snapshot id (`catalog_version` field) for audit trails.

The **HTML** and **`BLAST_RADIUS_LEADERSHIP.md`** files include a **legend table** built from that catalog when present (fallback text if the JSON is missing), including the `use_fast_tokenizer` vs `trust_remote_code` contrast plus **citations**.

Dynamic/runtime risks (e.g. **LLM01** prompt injection) are **out of scope** for these static sample exports; see roadmap for later phases.

## Regenerate (maintainers)

From repo root:

```bash
python3 scripts/export_bundle_action_sheet.py
```

Optional paths:

```bash
python3 scripts/export_bundle_action_sheet.py --csv-out /tmp/out.csv --html-out /tmp/brief.html
```
