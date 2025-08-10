"""FastMCP server for markdown-based GTD system."""

from typing import Any

from fastmcp import FastMCP

from md_gtd_mcp.services.vault_setup import setup_gtd_vault as setup_vault_impl

mcp: FastMCP[Any] = FastMCP("Markdown GTD")


@mcp.tool()
def hello_world() -> str:
    """A simple hello world tool to test the MCP server."""
    return "Hello from Markdown GTD MCP Server!"


@mcp.tool()
def setup_gtd_vault(vault_path: str) -> dict[str, Any]:
    """Create GTD folder structure if missing.

    CRITICAL SAFETY: Only creates files/folders that don't exist - NEVER overwrites
    existing files.

    Args:
        vault_path: Path to the Obsidian vault directory

    Returns:
        Dictionary with status, created items, and already existed items
    """
    return setup_vault_impl(vault_path)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
