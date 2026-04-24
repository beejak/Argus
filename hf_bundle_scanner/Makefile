# Delegate to LLM Scanner repo root (same targets as ../Makefile).
ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST)))/..)

.PHONY: help scan-fixture install test integration lint fmt docker docker-bundle ruff-check roadmap graphify-update memory-open agent-verify sample-action-sheets plain-english-brief sample-reports-all drivers-help hub-find-models-under-size

help scan-fixture install test integration lint fmt docker docker-bundle ruff-check roadmap graphify-update memory-open agent-verify sample-action-sheets plain-english-brief sample-reports-all drivers-help hub-find-models-under-size:
	@$(MAKE) -C "$(ROOT)" $@
