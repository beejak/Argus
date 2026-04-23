# Human-readable scan outputs (start here)

The raw bundle reports are JSON (`hf_bundle_scanner.bundle_report.v2`). If you want **actionable intelligence** in formats you can skim in a minute, use these instead:

| File | What it is | Best for |
| ---- | ---------- | -------- |
| [`UNIFIED_ACTION_SHEET.csv`](UNIFIED_ACTION_SHEET.csv) | One spreadsheet: **three demos** side-by-side (baseline, injected config risk, strict policy). | Excel / Sheets: filter by `demo_id`, sort by `severity`. |
| [`SCAN_BRIEFING.html`](SCAN_BRIEFING.html) | Same content as **tables** in a browser. | Reading on a screen; **Print → Save as PDF** for a fixed artifact to attach to a ticket. |

## How to read a row

- **`demo_id` / `demo_title`**: which teaching scenario this row belongs to (same Hub test snapshot; different policy or injected config).
- **`row_kind`**: `EXEC_SUMMARY` = whole-bundle rollup; `CONFIG` = configlint; `WEIGHT_FILE` = scanned weight-like file with no driver/policy finding; `FINDING` = a concrete violation to fix or waive.
- **`scanner_signal`**: short echo of what the machine saw (exit codes, rule ids, messages).
- **`human_meaning`**: plain-language interpretation (not legal advice; not proof of exploitation).
- **`recommended_next_step`**: what a security or ML engineer typically does next in a review workflow.

## Regenerate (maintainers)

From repo root:

```bash
python3 scripts/export_bundle_action_sheet.py
```

Optional paths:

```bash
python3 scripts/export_bundle_action_sheet.py --csv-out /tmp/out.csv --html-out /tmp/brief.html
```
