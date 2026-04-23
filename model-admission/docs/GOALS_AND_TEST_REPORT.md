# Goals vs outcomes — model-admission (test round)

**Canonical tree:** `/root/LLM Scanner/model-admission` (WSL2).  
**Report date:** generated alongside automated test run documented below.

## What we set out to achieve

| # | Goal | Intent |
|---|------|--------|
| G1 | **Stable CLI contract** | `admit-model scan` with predictable exit codes (0 / 1 / 2 / 4) for CI. |
| G2 | **Policy gate before/at scan** | Size caps, extension allow/deny lists, optional SHA-256 allowlist. |
| G3 | **Pluggable drivers** | ModelScan + ModelAudit behind one interface; swap without rewriting CI. |
| G4 | **Provenance / audit trail** | Optional JSONL ledger (`--ledger` or `MODEL_ADMISSION_LEDGER`). |
| G5 | **Packaging & CI** | `pyproject.toml`, `python -m build`, GitHub Actions, Apache-2.0 + NOTICE. |
| G6 | **WSL2 as single workspace** | Docker + Linux tooling in one folder; no parallel “mystery” copy. |
| G7 | **Tests without downloading models** | Unit + CLI subprocess tests; integration optional when scanners on PATH. |

## Automated test round (this session)

Commands:

```bash
cd "/root/LLM Scanner/model-admission"
source .venv/bin/activate   # or: python3 -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"
pytest -v --tb=short
```

### Test modules exercised

| File | What it proves |
|------|----------------|
| `tests/test_policy.py` | Policy JSON load, SHA-256 of file, allow/forbid lists. |
| `tests/test_report.py` | `Finding` / `ScanReport` JSON shape, `highest_severity`, `write_json`. |
| `tests/test_cli.py` | End-to-end subprocess: no drivers pass; policy fail; `--version`. |
| `tests/test_cli_exit_logic.py` | `--fail-on` parsing and severity floor logic. |
| `tests/test_cli_extra.py` | Unknown driver → exit 4; ledger via env var. |
| `tests/test_ledger.py` | Append-only JSONL lines with `ts` field. |
| `tests/test_drivers.py` | Driver registry + ModelScan JSON parsing (no binary). |
| `tests/test_integration_drivers.py` | **Optional:** real `modelscan` / `modelaudit` if installed (else skip). |

## Results: were we successful?

| Goal | Status | Evidence |
|------|--------|----------|
| G1 Stable CLI | **Met** | `test_cli*.py` subprocess runs; exit 0/1/4 covered; 2 = driver errors (covered in integration / manual). |
| G2 Policy | **Met** | `test_policy.py`, `test_cli_scan_policy_forbidden_extension_fails`. |
| G3 Drivers | **Met** | `test_drivers.py` registry + JSON parse; integration tests skip if binaries absent. |
| G4 Ledger | **Met** | `test_ledger.py`, `test_cli_extra.py` env-based ledger line with `exit_code`. |
| G5 Packaging | **Met** (last verified on dev machine) | `python -m build` + wheel install documented in README; `.github/workflows/ci.yml` present. |
| G6 WSL-only | **Met** (process) | README + parent `/root/LLM Scanner/README.md` state canonical path; work done under WSL path. |
| G7 No model download | **Met** | All default tests use tiny files or JSON only; integration uses minimal safetensors bytes. |

### pytest summary (recorded run)

Last automated run on WSL2 (`bash -lc`, `pytest tests -v --tb=short`):

`23 passed, 2 skipped` (runtime typically under one second on a small VM)

- **Passed** — all non-skipped assertions succeeded.  
- **Skipped** — `tests/test_integration_drivers.py` (2 tests) when `modelscan` / `modelaudit` not on `PATH` (expected in minimal `.venv` without those packages).

## Gaps / not proven by tests alone

- **Exit code 2** paths (driver timeout, malformed tool output) are best covered by integration or fault injection; not every branch has a dedicated unit test.
- **Scanner correctness** (finding every malicious model) is not guaranteed by any tool; tests only check wiring and parsing.
- **Docker image** build is not run inside pytest; validate periodically with `docker build -t model-admission:local .`

## Conclusion

For the **stated engineering goals** (CLI, policy, dual drivers, ledger, packaging layout, WSL-centric workflow, tests without large model downloads), the project is **on track**: automated tests cover the core contract, and optional integration tests extend coverage when scanners are installed.
