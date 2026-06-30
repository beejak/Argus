# Gap Tracker

Structured register of security and coverage gaps identified during gap-analysis sessions. Update this file each session alongside `docs/sessions/SESSION_LOG.md`.

**Status values:** `OPEN` | `FIXED` | `PARTIAL` | `WONT_DO`

---

## Gap register

### GAP-001 — `subprocess.TimeoutExpired` not caught in `run_admit_scan`

| Field | Value |
|-------|-------|
| **Status** | FIXED (commit `8470112`) |
| **Module** | `hf_bundle_scanner/hf_bundle_scanner/dispatch.py` |
| **Severity** | High — a hung subprocess crashes the entire bundle scan instead of recording a tooling error |
| **CVE / Research** | Internal — identified during gap analysis 2026-06-30 |
| **Effort** | XS (already done) |

**Description:** `run_admit_scan` called `subprocess.run(..., timeout=...)` but only caught `subprocess.CalledProcessError`. A process that exceeded the timeout raised `subprocess.TimeoutExpired` uncaught, aborting the whole scan.

**Fix applied:** Added `subprocess.TimeoutExpired` to the except clause; maps to exit code 2 (tooling error) so the scan continues with remaining files.

**Tests:** `test_dispatch.py::test_timeout_returns_exit2`, `test_dispatch.py::test_timeout_on_one_file_does_not_stop_others`.

---

### GAP-002 — No AST-based scanner for `trust_remote_code=True` in bundled Python scripts

| Field | Value |
|-------|-------|
| **Status** | FIXED (commit `8470112`) |
| **Module** | `hf_bundle_scanner/hf_bundle_scanner/script_lint.py` (new) |
| **Severity** | High — models published to the Hub may bundle training/inference scripts that hard-code `trust_remote_code=True`, enabling arbitrary code execution when loaded |
| **CVE / Research** | CVE-2026-6859 class (trust_remote_code hardcoded in training scripts) |
| **Effort** | S (already done) |

**Description:** No existing check scanned `.py` files inside a model bundle for the literal `trust_remote_code=True` keyword argument pattern. A regex-based approach would produce false positives (comments, docstrings) and false negatives (multi-line calls).

**Fix applied:** `script_lint.py` uses `ast.parse` + `ast.walk` targeting `keyword` nodes where `arg == "trust_remote_code"` and the value is `Constant(True)`. Parse errors are caught and returned as warning findings. The module does not flag `trust_remote_code=False` or variable references.

**Tests:** `hf_bundle_scanner/tests/test_script_lint.py` — 12 tests covering literal true/false, variable reference, comment, string boolean, nested call, parse error, multi-file scan.

**Remaining scope (see GAP-005):** Only `trust_remote_code=True` is detected. Other dangerous patterns (`exec`, `eval`, `os.system`, `pickle.loads`) are not yet covered.

---

### GAP-003 — No GGUF metadata scan for Jinja2 SSTI in `chat_template` field

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Module** | Not yet created — would be `hf_bundle_scanner/hf_bundle_scanner/gguf_lint.py` |
| **Severity** | Critical — CVSS 9.5; Jinja2 template containing `{{ config.__class__.__init__.__globals__['os'].popen(...) }}` in the GGUF `chat_template` metadata key executes on the host when a chat application renders the template |
| **CVE / Research** | CVE-2026-5760 (CVSS 9.5); affects any consumer of llama.cpp-style GGUF files that passes `chat_template` directly to a Jinja2 renderer without sandboxing |
| **Effort** | M — needs a GGUF binary header parser (little-endian, length-prefixed key-value pairs) + Jinja2 payload heuristics or static analysis |

**Description:** GGUF is a binary format used by llama.cpp and derived runtimes. Metadata key-value pairs are stored in the file header. The `tokenizer.chat_template` key (or `chat_template`) frequently contains a Jinja2 template string. Malicious models can embed an SSTI payload here; any application that passes this string to `jinja2.Environment().from_string(...)` without `SandboxedEnvironment` is vulnerable.

**Current state:** The discovery layer finds `.gguf` files; `dispatch.py` can route them to ModelScan/ModelAudit, but neither tool checks GGUF metadata keys for template injection. No Argus module reads GGUF binary headers directly.

**Suggested next steps:**
1. Add a pure-Python GGUF header reader (`gguf_lint.py`) that parses the binary format up to the metadata key-value section (no dependency on llama.cpp).
2. Check for keys `tokenizer.chat_template` and `chat_template`; flag any value that contains Jinja2 expression markers (`{{`, `{%`) or known RCE gadgets.
3. Return a `Finding` with `rule_id="gguf.chat_template_ssti"`, severity HIGH/CRITICAL.
4. Wire into `dispatch.py` alongside the existing per-file routing.
5. Add test fixtures: a benign `.gguf` stub, a `.gguf` stub with a safe template, and one with an SSTI payload marker.

**Reference:** [CVE-2026-5760](https://nvd.nist.gov/vuln/detail/CVE-2026-5760) — Jinja2 SSTI via GGUF chat_template metadata.

---

### GAP-004 — No picklescan version enforcement; three zero-days affect < 0.0.31

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Module** | `hf_bundle_scanner/hf_bundle_scanner/dispatch.py` or a new `driver_version_check.py` |
| **Severity** | High — using picklescan < 0.0.31 means three known bypass techniques silently pass malicious pickle files as clean |
| **CVE / Research** | CVE-2025-10155 (`.bin`/`.pt` rename bypass), CVE-2025-10156 (CRC-zeroed ZIP), CVE-2025-10157 (subclassed module path bypass); fixed in picklescan 0.0.31 |
| **Effort** | S — importlib.metadata version check + CI pin |

**Description:** Three zero-days were disclosed in 2025 against picklescan < 0.0.31:
- **CVE-2025-10155:** Renaming a malicious pickle to `.bin` or `.pt` (common PyTorch checkpoint extensions) causes picklescan to skip the file entirely.
- **CVE-2025-10156:** A ZIP archive with zeroed CRC fields bypasses the ZIP-archive scan path.
- **CVE-2025-10157:** Subclassed module paths (e.g., `builtins.exec` spelled via `__class__` chain) evade the class/function blocklist.

All three are fixed in picklescan 0.0.31. Argus currently invokes picklescan as a subprocess driver but does not check which version is installed. A CI environment with picklescan 0.0.29 installed will report "clean" for payloads that exploit any of these three bypasses.

**Suggested next steps:**
1. In `dispatch.py` (or a new `driver_version_check.py` called during dispatch init), use `importlib.metadata.version("picklescan")` to read the installed version.
2. Compare against the minimum safe version `0.0.31` using `packaging.version.Version`.
3. If below minimum, emit a `Finding` with `rule_id="tooling.picklescan_version_too_old"`, severity HIGH, and exit code 2 (tooling error) to prevent a false-clean result.
4. Add a check to CI (`requirements-dev.txt` or `pyproject.toml`) pinning `picklescan >= 0.0.31`.
5. Add a unit test that mocks `importlib.metadata.version` to return `"0.0.29"` and asserts the finding is emitted.

**Reference:** NVD entries for CVE-2025-10155, CVE-2025-10156, CVE-2025-10157.

---

### GAP-005 — `script_lint.py` covers only `trust_remote_code=True`; other dangerous Python patterns undetected

| Field | Value |
|-------|-------|
| **Status** | PARTIAL (trust_remote_code covered; other patterns open) |
| **Module** | `hf_bundle_scanner/hf_bundle_scanner/script_lint.py` |
| **Severity** | Medium — missing coverage for `exec`/`eval` of remote strings, `os.system`, `subprocess.run` with shell=True, `pickle.loads` on untrusted data, and `__import__` calls |
| **CVE / Research** | CVE-2026-6859 class; general ML supply-chain script injection patterns (NullifAI research Feb 2025) |
| **Effort** | S–M depending on desired pattern set and false-positive tolerance |

**Description:** `script_lint.py` currently uses AST analysis to detect exactly one pattern: `trust_remote_code=True` as a literal keyword argument. The CVE-2026-6859 class of vulnerabilities includes a broader set of dangerous patterns that can appear in bundled training/inference scripts:

- `exec(...)` or `eval(...)` called with a non-literal argument (potential remote code execution).
- `os.system(...)` or `subprocess.run(..., shell=True)` with a non-literal argument.
- `pickle.loads(...)` called on a variable (untrusted deserialization).
- `__import__(...)` called with a variable argument (dynamic import from untrusted source).
- `urllib.request.urlopen` / `requests.get` writing to disk without integrity check (download + execute pattern).

**Suggested next steps:**
1. Extend `script_lint.py` with additional AST visitor methods, each emitting a distinct `rule_id` (e.g., `script.exec_non_literal`, `script.pickle_loads`, `script.shell_true`).
2. Gate new rule IDs behind the existing policy JSON (`docs/policy/configlint_rule_defaults.json`) so operators can suppress individual rules.
3. Keep false-positive rate low: flag `exec(some_var)` but not `exec("literal string")`.
4. Add corresponding test fixtures and entries in `docs/reporting/decision_support_rule_catalog.json`.

---

### GAP-006 — 7z-compressed PyTorch archives evade all current scanners

| Field | Value |
|-------|-------|
| **Status** | OPEN |
| **Module** | `hf_bundle_scanner/hf_bundle_scanner/dispatch.py` or a new `archive_probe.py` |
| **Severity** | High — a `.pt` / `.bin` file compressed with 7z instead of ZIP is structurally valid to Python's `torch.load` but is not recognized as a ZIP by picklescan or ModelScan, producing a silent false-clean |
| **CVE / Research** | NullifAI research (February 2025): demonstrated that PyTorch checkpoint files re-compressed with 7z pass all current OSS scanners without detection |
| **Effort** | M — magic-byte detection of 7z headers in files with `.pt`/`.bin`/`.pth` extensions; optionally decompress and re-scan |

**Description:** PyTorch `.pt` / `.pth` / `.bin` files are ZIP archives internally. Picklescan and ModelScan detect malicious opcodes by unzipping the archive and inspecting the contained pickle stream. NullifAI (Feb 2025) showed that re-compressing the same file with 7z produces a file that `torch.load` can still open (because PyTorch's ZIP reader falls back to other decompressors), but that picklescan and ModelScan reject silently as "not a ZIP" — returning no findings rather than an error.

**Suggested next steps:**
1. After dispatch calls picklescan/ModelScan on a `.pt`/`.bin`/`.pth` file, check the first 6 bytes for the 7z magic (`37 7A BC AF 27 1C`).
2. If 7z magic is detected, emit a `Finding` with `rule_id="archive.7z_disguised_as_pytorch"`, severity HIGH, and exit code 1 (suspicious), regardless of what picklescan reported.
3. Optionally: attempt to decompress with `py7zr` and re-run picklescan on the decompressed stream.
4. Add a test fixture: a minimal 7z file with a `.pt` extension.

**Reference:** NullifAI blog post, February 2025 — "PyTorch models compressed with 7z evade ML security scanners."

---

## Summary table

| Gap ID | Title | Status | Severity | Effort | Commit / Reference |
|--------|-------|--------|----------|--------|--------------------|
| GAP-001 | TimeoutExpired not caught in dispatch | FIXED | High | XS | `8470112` |
| GAP-002 | No AST scan for trust_remote_code=True in scripts | FIXED | High | S | `8470112` |
| GAP-003 | No GGUF metadata scan for Jinja2 SSTI | OPEN | Critical | M | CVE-2026-5760 |
| GAP-004 | No picklescan version enforcement | OPEN | High | S | CVE-2025-10155/10156/10157 |
| GAP-005 | script_lint covers only trust_remote_code | PARTIAL | Medium | S–M | CVE-2026-6859 class |
| GAP-006 | 7z-compressed PyTorch files evade all scanners | OPEN | High | M | NullifAI Feb 2025 |

---

## Recommended implementation order (open gaps)

1. **GAP-004** (picklescan version guard) — smallest effort, highest confidence payoff. Prevents silent false-clean results without any new parsing code.
2. **GAP-003** (GGUF SSTI) — highest severity (CVSS 9.5). GGUF usage is growing; implement the header parser before the format becomes dominant in internal model libraries.
3. **GAP-006** (7z magic byte check) — straightforward magic-byte probe; does not require decompression for initial coverage.
4. **GAP-005** (script_lint expansion) — incremental; tackle one pattern at a time starting with `exec`/`eval` of non-literal arguments.

---

*Last updated: 2026-06-30. Session commit: `8470112`.*
