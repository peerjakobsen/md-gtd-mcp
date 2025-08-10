"""FastMCP server for markdown-based GTD system."""

from typing import Any

from fastmcp import FastMCP

mcp: FastMCP[Any] = FastMCP("Markdown GTD")


@mcp.tool()
def hello_world() -> str:
    """A simple hello world tool to test the MCP server."""
    return "Hello from Markdown GTD MCP Server!"


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
