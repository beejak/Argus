from __future__ import annotations


def test_fastmcp_import() -> None:
    from mcp.server.fastmcp import FastMCP

    assert FastMCP is not None
