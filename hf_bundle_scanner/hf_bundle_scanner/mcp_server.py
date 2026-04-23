"""stdio MCP server exposing bounded scan tools (optional dependency: mcp)."""

from __future__ import annotations

import json
from pathlib import Path

from hf_bundle_scanner.dispatch import scan_bundle
from hf_bundle_scanner.snapshot import build_manifest


def _scan_path_tool(
    root: str,
    policy: str,
    drivers: str = "",
    hub_repo: str = "",
    hub_revision: str = "",
    mirror_allowlist: str = "",
    sbom_uri: str = "",
) -> str:
    mirrors = (
        [x.strip() for x in mirror_allowlist.split(",") if x.strip()] if mirror_allowlist else None
    )
    bundle = scan_bundle(
        Path(root),
        Path(policy),
        drivers=drivers,
        hub_repo_id=hub_repo or None,
        hub_revision=hub_revision or None,
        mirror_allowlist=mirrors,
        sbom_uri=sbom_uri or None,
    )
    return json.dumps(bundle.to_dict(), indent=2)


def _manifest_tool(root: str) -> str:
    data = build_manifest(Path(root))
    return json.dumps(data, indent=2)


def main() -> None:
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as e:  # pragma: no cover
        raise SystemExit(
            "Install optional dependency: pip install 'hf-bundle-scanner[mcp]'"
        ) from e

    mcp = FastMCP("hf_bundle_scanner")

    @mcp.tool()
    def scan_path(
        root: str,
        policy: str,
        drivers: str = "",
        hub_repo: str = "",
        hub_revision: str = "",
        mirror_allowlist: str = "",
        sbom_uri: str = "",
    ) -> str:
        """Run full bundle scan (discovery, configlint, admit-model per file). Deterministic verdict in JSON."""
        return _scan_path_tool(
            root,
            policy,
            drivers,
            hub_repo,
            hub_revision,
            mirror_allowlist,
            sbom_uri,
        )

    @mcp.tool()
    def build_manifest_json(root: str) -> str:
        """Compute recursive SHA-256 manifest for a local directory tree."""
        return _manifest_tool(root)

    try:
        mcp.run(transport="stdio")
    except TypeError:
        mcp.run()


if __name__ == "__main__":
    main()
