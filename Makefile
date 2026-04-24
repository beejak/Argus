# LLM Scanner — root harness (WSL2). Paths are relative to this Makefile directory.
# Debian/Ubuntu ship PEP 668 ("externally managed"); use a repo-local venv for pip.
VENVDIR ?= .venv
PY := $(abspath $(VENVDIR))/bin/python

.PHONY: help install test integration scan-fixture lint fmt docker docker-bundle ruff-check roadmap graphify-update memory-open agent-verify git-doctor commit-msg slogan-dry-run ephemeral-hub-scan sample-action-sheets sample-reports-all plain-english-brief drivers-help

help:
	@echo "LLM Scanner harness"
	@echo "  make install          - venv + editable model-admission + hf_bundle_scanner[mcp,http]"
	@echo "  make test             - pytest (excludes integration)"
	@echo "  make integration      - pytest integration"
	@echo "  make scan-fixture     - minimal bundle scan smoke"
	@echo "  make roadmap          - pointer to docs/PRODUCTION_SCANNER_ROADMAP.md"
	@echo "  make graphify-update  - refresh graphify-out/ if graphify is installed"
	@echo "  make memory-open      - path to docs/sessions/SESSION_LOG.md"
	@echo "  make agent-verify     - run both pytest suites; write .agent/pytest-last.log"
	@echo "  make git-doctor       - print trailer-related git config + env hints"
	@echo "  make commit-msg       - git commit via -F (usage: make commit-msg MSG='subject')"
	@echo "  make slogan-dry-run   - print next README slogan (no file writes)"
	@echo "  make ephemeral-hub-scan - Hub download → scan → delete (needs OUT=/path.json; optional INJECT=1)"
	@echo "  make sample-action-sheets - regenerate docs/sample_reports/actionable/* from sample JSON"
	@echo "  make plain-english-brief  - non-technical PLAIN_ENGLISH_BRIEF.md (same samples; does not touch CSV/HTML/blast MD)"
	@echo "  make sample-reports-all - action sheets + plain-English brief"
	@echo "  make drivers-help       - list model-admission scan drivers + env overrides"
	@echo "  make lint | fmt | docker | docker-bundle | ruff-check"

install:
	@if [ ! -x "$(PY)" ]; then python3 -m venv "$(VENVDIR)"; fi
	"$(PY)" -m pip install -U pip
	cd model-admission && "$(PY)" -m pip install -e ".[dev]"
	cd hf_bundle_scanner && "$(PY)" -m pip install -e ".[dev,mcp,http]"

test:
	cd hf_bundle_scanner && "$(PY)" -m pytest tests -v --tb=short -m "not integration"

integration:
	cd hf_bundle_scanner && "$(PY)" -m pytest tests -v --tb=short -m integration

scan-fixture:
	@"$(PY)" -c "from pathlib import Path; p=Path('hf_bundle_scanner/tests/fixtures/minimal_tree/weights.safetensors'); h=b'{}'; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(len(h).to_bytes(8,'little')+h)"
	cd hf_bundle_scanner && HF_BUNDLE_PYTHON='$(PY)' "$(PY)" -m hf_bundle_scanner scan \
		--root tests/fixtures/minimal_tree \
		--policy tests/fixtures/policy.permissive.json \
		--out /tmp/hf-bundle-fixture-report.json \
		--drivers "" \
		--print-summary

lint:
	cd hf_bundle_scanner && "$(PY)" -m ruff check hf_bundle_scanner tests

fmt:
	cd hf_bundle_scanner && "$(PY)" -m ruff format hf_bundle_scanner tests

docker:
	docker build -f model-admission/Dockerfile -t model-admission:local model-admission

docker-bundle:
	docker build -f hf_bundle_scanner/Dockerfile -t hf-bundle-scanner:local .

ruff-check: lint

roadmap:
	@echo "Long-horizon roadmap: docs/PRODUCTION_SCANNER_ROADMAP.md"
	@test -f docs/PRODUCTION_SCANNER_ROADMAP.md

graphify-update:
	@if command -v graphify >/dev/null 2>&1; then \
		graphify update .; \
	elif "$(PY)" -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('graphify') else 1)" >/dev/null 2>&1; then \
		"$(PY)" -m graphify update .; \
	else \
		echo "graphify not installed; pip install graphify (see upstream docs) then retry"; \
	fi

memory-open:
	@echo "Append session notes to: $$(pwd)/docs/sessions/SESSION_LOG.md"

agent-verify:
	@"$(PY)" "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/run_tests_for_agent.py"

git-doctor:
	@python3 "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/git_doctor.py"

commit-msg:
	@test -n "$(MSG)" || (echo 'Usage: make commit-msg MSG="commit subject"' >&2 && exit 1)
	@python3 "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/git_commit_via_file.py" "$(MSG)"

slogan-dry-run:
	@"$(PY)" "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/rotate_readme_slogan.py" --dry-run

# OUT=/tmp/b.json [INJECT=1] [EPHEMERAL_FLAGS="--repo org/name --revision main"]
ephemeral-hub-scan:
	@test -n "$(OUT)" || (echo 'Usage: OUT=/tmp/bundle.json make ephemeral-hub-scan [INJECT=1] [EPHEMERAL_FLAGS="--repo ..."]' >&2 && exit 1)
	@"$(PY)" "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/ephemeral_hub_scan.py" --out "$(OUT)" $(if $(filter 1,$(INJECT)),--inject-demo-tokenizer-risk,) $(EPHEMERAL_FLAGS)

sample-action-sheets:
	@python3 "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/export_bundle_action_sheet.py"

plain-english-brief:
	@python3 "$(abspath $(dir $(lastword $(MAKEFILE_LIST))))/scripts/export_plain_english_brief.py"

sample-reports-all: sample-action-sheets plain-english-brief

drivers-help:
	@"$(PY)" -c "from model_admission.drivers import DRIVERS; \
print('Known admit-model drivers:', ', '.join(sorted(DRIVERS))); \
print('Env overrides: MODELSCAN_BIN, MODELAUDIT_BIN'); \
print('Bundle scan: scan-bundle scan ... --drivers modelscan,modelaudit')"
