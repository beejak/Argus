# Makefile harness — archive

**Status:** these targets are **merged** into the repo root [`Makefile`](../Makefile) and delegated from [`hf_bundle_scanner/Makefile`](../hf_bundle_scanner/Makefile). This file remains as a **copy/paste reference** if you need to recreate the harness on a fork.

## 1. Extend `.PHONY` and add `help`

After the existing `.PHONY` line, include the new targets and copy the blocks below.

Suggested `.PHONY` line:

```makefile
.PHONY: help install test integration scan-fixture lint fmt docker docker-bundle ruff-check \
	roadmap graphify-update memory-open
```

Insert **`help`** (and other new rules) **before** `install:` or after `PY` assignment — example:

```makefile
help:
	@echo "LLM Scanner harness"
	@echo "  make install          - venv + editable model-admission + hf_bundle_scanner[mcp,http]"
	@echo "  make test             - pytest (excludes integration)"
	@echo "  make integration      - pytest integration"
	@echo "  make scan-fixture     - minimal bundle scan smoke"
	@echo "  make roadmap          - pointer to docs/PRODUCTION_SCANNER_ROADMAP.md"
	@echo "  make graphify-update  - refresh graphify-out/ if graphify is installed"
	@echo "  make memory-open      - path to docs/sessions/SESSION_LOG.md"
	@echo "  make lint | fmt | docker | docker-bundle | ruff-check"
```

## 2. Append at end of `Makefile`

```makefile
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
```

## 3. Optional: `hf_bundle_scanner/Makefile`

Forward new targets so `make -C hf_bundle_scanner help` works:

```makefile
.PHONY: ... help roadmap graphify-update memory-open

help roadmap graphify-update memory-open:
	@$(MAKE) -C "$(ROOT)" $@
```
