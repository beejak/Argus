#!/usr/bin/env bash
# Thin wrapper: prefer Python runner (LF-safe). Kept for manual `bash scripts/run-tests-for-agent.sh`.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYBIN="$(command -v python3 2>/dev/null || command -v python 2>/dev/null || true)"
if [[ -z "${PYBIN}" ]]; then
  echo "python3 not found" >&2
  exit 127
fi
exec "${PYBIN}" "${ROOT}/scripts/run_tests_for_agent.py"