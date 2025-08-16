"""FastMCP server for markdown-based GTD system."""

import dataclasses
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.services.vault_reader import VaultReader
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


def read_gtd_file_impl(vault_path: str, file_path: str) -> dict[str, Any]:
    """Implementation for reading and parsing a single GTD file from the vault.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_path: Path to the GTD file to read (can be absolute or relative to vault)

    Returns:
        Dictionary with status, file data, and vault path
    """
    try:
        # Validate inputs
        if not vault_path or not vault_path.strip():
            return {
                "status": "error",
                "error": "Invalid vault path: path cannot be empty",
                "vault_path": vault_path,
            }

        if not file_path or not file_path.strip():
            return {
                "status": "error",
                "error": "Invalid file path: path cannot be empty",
                "vault_path": vault_path,
            }

        # Convert to Path objects
        vault_path_obj = Path(vault_path)

        # Handle both absolute and relative file paths
        if Path(file_path).is_absolute():
            file_path_obj = Path(file_path)
        else:
            file_path_obj = vault_path_obj / file_path

        # Check if vault exists
        if not vault_path_obj.exists():
            return {
                "status": "error",
                "error": f"Vault directory not found: {vault_path}",
                "vault_path": vault_path,
            }

        # Initialize vault configuration and reader
        vault_config = VaultConfig(vault_path_obj)
        vault_reader = VaultReader(vault_config)

        # Read the GTD file
        gtd_file = vault_reader.read_gtd_file(file_path_obj)

        # Convert GTD file to dictionary format
        file_data = {
            "file_path": gtd_file.path,
            "file_type": gtd_file.file_type,
            "content": gtd_file.content,
            "frontmatter": dataclasses.asdict(gtd_file.frontmatter)
            if gtd_file.frontmatter
            else {},
            "tasks": [
                {
                    "description": task.text,
                    "completed": task.is_completed,
                    "completion_date": task.done_date.isoformat()
                    if task.done_date
                    else None,
                    "context": task.context,
                    "project": task.project,
                    "energy": task.energy,
                    "time_estimate": task.time_estimate,
                    "delegated_to": task.delegated_to,
                    "tags": task.tags,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "scheduled_date": task.scheduled_date.isoformat()
                    if task.scheduled_date
                    else None,
                    "start_date": task.start_date.isoformat()
                    if task.start_date
                    else None,
                    "raw_text": task.raw_text,
                    "line_number": task.line_number,
                }
                for task in gtd_file.tasks
            ],
            "links": [
                {
                    "type": "external" if link.is_external else "wikilink",
                    "text": link.text,
                    "target": link.target,
                    "is_external": link.is_external,
                    "line_number": link.line_number,
                }
                for link in gtd_file.links
            ],
        }

        return {
            "status": "success",
            "file": file_data,
            "vault_path": vault_path,
        }

    except FileNotFoundError as e:
        return {
            "status": "error",
            "error": f"GTD file not found: {e}",
            "vault_path": vault_path,
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": f"Invalid GTD file: {e}",
            "vault_path": vault_path,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error reading GTD file: {e}",
            "vault_path": vault_path,
        }


@mcp.tool()
def read_gtd_file(vault_path: str, file_path: str) -> dict[str, Any]:
    """Read and parse a single GTD file from the vault.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_path: Path to the GTD file to read (can be absolute or relative to vault)

    Returns:
        Dictionary with status, file data, and vault path
    """
    return read_gtd_file_impl(vault_path, file_path)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
