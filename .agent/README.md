# Agent-readable test artifacts

## `make agent-verify`

From a **real Linux shell** in this repo (WSL, container, or CI):

```bash
cd "/root/LLM Scanner"
make install   # once
make agent-verify
```

This runs **[`scripts/run_tests_for_agent.py`](../scripts/run_tests_for_agent.py)** (via the repo `.venv` Python) so results do not depend on bash CRLF on Windows checkouts. The shell file [`run-tests-for-agent.sh`](../scripts/run-tests-for-agent.sh) is a thin `exec python3 …run_tests_for_agent.py` wrapper.

Writes:

| File | Meaning |
| ---- | ------- |
| `pytest-last.log` | Full pytest output (both packages) |
| `pytest-last.exit` | `0` = all passed, `1` = a suite failed, `99` = missing `.venv` |

**Cursor caveat:** some Cursor + Windows setups run agent terminal commands in an environment where **WSL side effects do not land** in the workspace the Read tool sees, and stdout is empty. In that case:

1. **Use Cursor “Remote - WSL”** (or open the folder **inside** WSL so the default terminal is Linux) — then `make test` / `make agent-verify` behave normally for the agent.
2. Rely on **GitHub Actions**: [`.github/workflows/llm-scanner.yml`](../.github/workflows/llm-scanner.yml) runs the same installs + pytest on `ubuntu-latest` for every push/PR.

**Do not commit secrets here.** `pytest-last.*` is gitignored.
