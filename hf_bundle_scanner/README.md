# hf-bundle-scanner

Modular HF-oriented bundle scanner: **manifest** (hashes), **discovery**, **dispatch** to [`model-admission`](../model-admission/README.md) per file, **configlint** (e.g. `trust_remote_code`, `auto_map`, `use_auth_token`, `use_fast_tokenizer`, invalid JSON), **aggregate report**.

Install from repo root (WSL):

```bash
pip install -e "./model-admission"
pip install -e "./hf_bundle_scanner[dev]"
```

Use the Makefile in the parent `LLM Scanner/` directory (`make test`, `make scan-fixture`).

## CLI

```bash
scan-bundle manifest --root /path/to/snapshot --out /tmp/manifest.json
scan-bundle download --repo org/name --revision main --dest /tmp/snap
scan-bundle scan --root /path/to/snapshot --policy policy.json --out /tmp/bundle.json --drivers ""
# Optional provenance (bundle JSON schema v2, top-level `provenance`):
scan-bundle scan --root "$D" --policy policy.json --out /tmp/bundle.json --drivers "" \
  --hub-repo org/name --hub-revision main \
  --mirror-allowlist huggingface.co,cdn-lfs.huggingface.co \
  --sbom-uri file:///tmp/sbom.json
python -m hf_bundle_scanner manifest --root /path --out /tmp/m.json
```

Environment mirrors / SBOM merge with CLI flags: **`HF_BUNDLE_MIRROR_ALLOWLIST`** (comma-separated hosts), **`HF_BUNDLE_SBOM_URI`**.

See [docs/hermes-mcp.md](docs/hermes-mcp.md) for MCP and optional HTTP.

### Optional: scan a small file from the “uncensored-models” collection

The curated list [uncensored-models](https://huggingface.co/collections/chwoo/uncensored-models) mostly hosts **multi‑GiB** full weights. One repo in that list has a **under 1 GiB** weight-like artifact we can use for a real download + scan check: **`mradermacher/gemma3-4b-it-abliterated-GGUF`** file **`gemma3-4b-it-abliterated.mmproj-Q8_0.gguf`** (~561 MiB, vision projector tensors—not the full chat stack).

Opt-in pytest (network, large download):

```bash
cd "/root/LLM Scanner/hf_bundle_scanner"
export HF_BUNDLE_PYTHON="/root/LLM Scanner/.venv/bin/python"
HF_BUNDLE_CHWOO_SCAN=1 python -m pytest tests/test_integration_chwoo_collection.py -v --tb=short
```

Manual equivalent (download one file, then scan):

```bash
export HF_BUNDLE_PYTHON="/root/LLM Scanner/.venv/bin/python"
D=$(mktemp -d)
python3 -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='mradermacher/gemma3-4b-it-abliterated-GGUF', filename='gemma3-4b-it-abliterated.mmproj-Q8_0.gguf', local_dir='$D')"
cd "/root/LLM Scanner/hf_bundle_scanner"
scan-bundle scan --root "$D" --policy tests/fixtures/policy.permissive.json --out /tmp/chwoo-scan.json --drivers "" --print-summary
```
