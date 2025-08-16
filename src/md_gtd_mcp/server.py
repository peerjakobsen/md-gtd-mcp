"""FastMCP server for markdown-based GTD system."""

from pathlib import Path
from typing import Any

from fastmcp import FastMCP

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.services.resource_handler import ResourceHandler
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
            "frontmatter": gtd_file.frontmatter.model_dump()
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


def list_gtd_files_impl(
    vault_path: str, file_type: str | None = None
) -> dict[str, Any]:
    """Implementation for listing all GTD files in the vault.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_type: Optional filter by file type (inbox, projects, context, etc.)

    Returns:
        Dictionary with status, files list, summary stats, and vault path
    """
    try:
        # Validate inputs
        if not vault_path or not vault_path.strip():
            return {
                "status": "error",
                "error": "Invalid vault path: path cannot be empty",
                "vault_path": vault_path,
            }

        # Convert to Path object
        vault_path_obj = Path(vault_path)

        # Check if vault exists, create if needed for suggestion logic
        vault_exists = vault_path_obj.exists()
        gtd_path = vault_path_obj / "gtd"
        gtd_exists = gtd_path.exists() if vault_exists else False

        # Initialize vault configuration and reader
        vault_config = VaultConfig(vault_path_obj)
        vault_reader = VaultReader(vault_config)

        # Get all GTD files
        try:
            if gtd_exists:
                gtd_files = vault_reader.list_gtd_files(file_type=file_type)
            else:
                gtd_files = []
        except Exception:
            # If there's an error reading files, return empty list
            gtd_files = []

        # Convert GTD files to metadata-only format (no full content)
        files_data = []
        for gtd_file in gtd_files:
            file_data = {
                "file_path": str(gtd_file.path),
                "file_type": gtd_file.file_type,
                "task_count": len(gtd_file.tasks),
                "link_count": len(gtd_file.links),
            }
            files_data.append(file_data)

        # Generate summary statistics
        try:
            if gtd_files:
                vault_summary = vault_reader.get_vault_summary()
            else:
                vault_summary = {
                    "total_files": 0,
                    "total_tasks": 0,
                    "total_links": 0,
                    "files_by_type": {},
                    "tasks_by_type": {},
                }
        except Exception:
            # Fallback summary if vault_reader fails
            total_tasks = 0
            total_links = 0
            for file_data in files_data:
                task_count = file_data["task_count"]
                link_count = file_data["link_count"]
                assert isinstance(task_count, int)
                assert isinstance(link_count, int)
                total_tasks += task_count
                total_links += link_count

            vault_summary = {
                "total_files": len(files_data),
                "total_tasks": total_tasks,
                "total_links": total_links,
                "files_by_type": {},
                "tasks_by_type": {},
            }

        # Prepare response
        response = {
            "status": "success",
            "files": files_data,
            "summary": vault_summary,
            "vault_path": vault_path,
        }

        # Add suggestion if no GTD structure exists
        if not gtd_exists or len(files_data) == 0:
            if not vault_exists:
                response["suggestion"] = (
                    "No vault found at the specified path. "
                    "Use the setup_gtd_vault tool to create a new GTD structure: "
                    "setup_gtd_vault(vault_path)"
                )
            elif not gtd_exists:
                response["suggestion"] = (
                    "No GTD structure found in this vault. "
                    "Use the setup_gtd_vault tool to create the GTD folder structure: "
                    "setup_gtd_vault(vault_path)"
                )

        return response

    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error listing GTD files: {e}",
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


@mcp.tool()
def list_gtd_files(vault_path: str, file_type: str | None = None) -> dict[str, Any]:
    """List GTD files with metadata only (no content) and optional filtering.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_type: Optional filter by file type (inbox, projects, next-actions,
                  waiting-for, someday-maybe, context)

    Returns:
        Dictionary with status, lightweight file metadata (paths, types, counts),
        summary statistics, and vault path. Does NOT include file content, tasks
        details, or links details. Includes suggestion to run setup_gtd_vault if
        no GTD structure exists. Use for quick overviews and file discovery.
    """
    return list_gtd_files_impl(vault_path, file_type)


def read_gtd_files_impl(
    vault_path: str, file_type: str | None = None
) -> dict[str, Any]:
    """Implementation for reading GTD files with comprehensive content.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_type: Optional filter by file type (inbox, projects, context, etc.)

    Returns:
        Dictionary with status, files with complete content, summary stats, and
        vault path
    """
    try:
        # Validate inputs
        if not vault_path or not vault_path.strip():
            return {
                "status": "error",
                "error": "Invalid vault path: path cannot be empty",
                "vault_path": vault_path,
            }

        # Convert to Path object
        vault_path_obj = Path(vault_path)

        # Check if vault exists, create if needed for suggestion logic
        vault_exists = vault_path_obj.exists()
        gtd_path = vault_path_obj / "gtd"
        gtd_exists = gtd_path.exists() if vault_exists else False

        # Initialize vault configuration and reader
        vault_config = VaultConfig(vault_path_obj)
        vault_reader = VaultReader(vault_config)

        # Get all GTD files with optional filtering
        try:
            if gtd_exists:
                gtd_files = vault_reader.list_gtd_files(file_type=file_type)
            else:
                gtd_files = []
        except Exception:
            # If there's an error reading files, return empty list
            gtd_files = []

        # Convert GTD files to complete format with full content
        files_data = []
        for gtd_file in gtd_files:
            file_data = {
                "file_path": str(gtd_file.path),
                "file_type": gtd_file.file_type,
                "content": gtd_file.content,
                "frontmatter": gtd_file.frontmatter.model_dump()
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
                        "due_date": task.due_date.isoformat()
                        if task.due_date
                        else None,
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
                "task_count": len(gtd_file.tasks),
                "link_count": len(gtd_file.links),
            }
            files_data.append(file_data)

        # Generate comprehensive summary statistics
        try:
            if gtd_files:
                vault_summary = vault_reader.get_vault_summary()
            else:
                vault_summary = {
                    "total_files": 0,
                    "total_tasks": 0,
                    "total_links": 0,
                    "files_by_type": {},
                    "tasks_by_type": {},
                }
        except Exception:
            # Fallback summary if vault_reader fails
            total_tasks = 0
            total_links = 0
            for file_data in files_data:
                task_count = file_data["task_count"]
                link_count = file_data["link_count"]
                assert isinstance(task_count, int)
                assert isinstance(link_count, int)
                total_tasks += task_count
                total_links += link_count

            vault_summary = {
                "total_files": len(files_data),
                "total_tasks": total_tasks,
                "total_links": total_links,
                "files_by_type": {},
                "tasks_by_type": {},
            }

        # Prepare comprehensive response
        response = {
            "status": "success",
            "files": files_data,
            "summary": vault_summary,
            "vault_path": vault_path,
        }

        # Add suggestion if no GTD structure exists
        if not gtd_exists or len(files_data) == 0:
            if not vault_exists:
                response["suggestion"] = (
                    "No vault found at the specified path. "
                    "Use the setup_gtd_vault tool to create a new GTD structure: "
                    "setup_gtd_vault(vault_path)"
                )
            elif not gtd_exists:
                response["suggestion"] = (
                    "No GTD structure found in this vault. "
                    "Use the setup_gtd_vault tool to create the GTD folder structure: "
                    "setup_gtd_vault(vault_path)"
                )

        return response

    except Exception as e:
        return {
            "status": "error",
            "error": f"Unexpected error reading GTD files: {e}",
            "vault_path": vault_path,
        }


@mcp.tool()
def read_gtd_files(vault_path: str, file_type: str | None = None) -> dict[str, Any]:
    """Read GTD files with comprehensive content and optional filtering.

    Args:
        vault_path: Path to the Obsidian vault directory
        file_type: Optional filter by file type (inbox, projects, next-actions,
                  waiting-for, someday-maybe, context)

    Returns:
        Dictionary with status, files with complete content (markdown, tasks, links,
        frontmatter), comprehensive summary statistics, and vault path. Includes
        suggestion to run setup_gtd_vault if no GTD structure exists. This tool
        provides full content access for comprehensive analysis, weekly reviews,
        and detailed GTD workflow processing.
    """
    return read_gtd_files_impl(vault_path, file_type)


# Initialize resource handler for MCP resource templates
resource_handler = ResourceHandler()


@mcp.resource(
    "gtd://{vault_path}/files",
    name="GTD File Listings",
    description="List GTD files in vault with metadata for file system navigation and "
    "discovery",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def list_files_resource(vault_path: str) -> str:
    """List all GTD files in vault with metadata for file system navigation.

    This resource provides lightweight file listings with metadata only (no content)
    for quick overviews and file discovery. Equivalent to list_gtd_files tool but
    following proper MCP resource semantics for read-only data access.

    URI Pattern: gtd://{vault_path}/files

    Args:
        vault_path: Path to the Obsidian vault directory extracted from URI

    Returns:
        JSON string with status, lightweight file metadata (paths, types, counts),
        summary statistics, and vault path. Does NOT include file content, task
        details, or link details. Includes suggestion to run setup_gtd_vault if
        no GTD structure exists.

    Example Usage:
        Resource URI: gtd://path/to/vault/files
        Claude Desktop: "List all GTD files in my vault"
        Response: File listings with task/link counts for quick overview

    GTD Context:
        - Use during Reflect phase for vault overview and file discovery
        - Supports weekly review preparation by showing all available files
        - Ideal for understanding vault structure before detailed analysis
    """
    import json

    result = resource_handler.get_files(vault_path)
    return json.dumps(result, indent=2)


@mcp.resource(
    "gtd://{vault_path}/files/{file_type}",
    name="GTD Filtered File Listings",
    description="List GTD files filtered by type (inbox, projects, next-actions, etc.) "
    "for targeted workflows",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def list_files_filtered_resource(vault_path: str, file_type: str) -> str:
    """List GTD files filtered by type (inbox, projects, next-actions, etc.).

    This resource provides filtered file listings for specific GTD categories,
    supporting focused workflows and phase-specific operations. Maintains
    lightweight metadata format while enabling targeted file discovery.

    URI Pattern: gtd://{vault_path}/files/{file_type}

    Args:
        vault_path: Path to the Obsidian vault directory extracted from URI
        file_type: GTD file type filter (inbox, projects, next-actions,
                  waiting-for, someday-maybe, context, reference)

    Returns:
        JSON string with status, filtered file metadata matching the specified
        type, summary statistics, and vault path. Only includes files of the
        requested type for focused GTD workflows.

    Example Usage:
        Resource URI: gtd://path/to/vault/files/inbox
        Claude Desktop: "Show me all inbox files"
        Resource URI: gtd://path/to/vault/files/projects
        Claude Desktop: "List project files for review"

    GTD Context:
        - Use during Clarify phase to focus on inbox items specifically
        - Supports context-specific reviews (projects, next-actions, etc.)
        - Enables targeted processing during GTD phase transitions
        - Weekly review optimization by reviewing specific file categories
    """
    import json

    result = resource_handler.get_files(vault_path, file_type)
    return json.dumps(result, indent=2)


@mcp.resource(
    "gtd://{vault_path}/file/{file_path}",
    name="GTD Single File Reader",
    description="Read single GTD file with complete content, tasks, and links for "
    "detailed analysis",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def read_file_resource(vault_path: str, file_path: str) -> str:
    """Read single GTD file with full content parsing and analysis.

    This resource provides comprehensive access to individual GTD files including
    content, frontmatter, tasks, and links. Equivalent to read_gtd_file tool but
    following proper MCP resource semantics for read-only data access.

    URI Pattern: gtd://{vault_path}/file/{file_path}

    Args:
        vault_path: Path to the Obsidian vault directory extracted from URI
        file_path: Path to the GTD file (relative to vault or absolute)

    Returns:
        JSON string with status, complete file data including content, frontmatter,
        parsed tasks with all properties, links with metadata, and vault path.
        Provides full context needed for detailed GTD analysis and processing.

    Example Usage:
        Resource URI: gtd://path/to/vault/file/GTD/inbox.md
        Claude Desktop: "Read my inbox file and analyze items"
        Resource URI: gtd://path/to/vault/file/GTD/projects.md
        Claude Desktop: "Show me the contents of my projects file"

    GTD Context:
        - Use during Clarify phase for detailed inbox item analysis
        - Supports project review with full context and task details
        - Enables deep analysis of specific GTD files during reviews
        - Provides complete data for AI-assisted GTD processing
    """
    import json

    result = resource_handler.get_file(vault_path, file_path)
    return json.dumps(result, indent=2)


@mcp.resource(
    "gtd://{vault_path}/content",
    name="GTD Complete Content Reader",
    description="Read all GTD files with comprehensive content for complete vault "
    "analysis and reviews",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def read_content_resource(vault_path: str) -> str:
    """Read all GTD files with comprehensive content extraction and analysis.

    This resource provides complete vault content access with full file parsing
    for comprehensive GTD analysis, weekly reviews, and detailed workflow
    processing. Equivalent to read_gtd_files tool but following proper MCP
    resource semantics for read-only data access.

    URI Pattern: gtd://{vault_path}/content

    Args:
        vault_path: Path to the Obsidian vault directory extracted from URI

    Returns:
        JSON string with status, complete files data including content, frontmatter,
        detailed tasks with all properties, links with metadata, task/link counts,
        comprehensive summary statistics, and vault path. Provides complete GTD
        system state for comprehensive analysis and review automation.

    Example Usage:
        Resource URI: gtd://path/to/vault/content
        Claude Desktop: "Analyze my complete GTD system"
        Use Case: "Prepare comprehensive weekly review summary"

    GTD Context:
        - Use during Reflect phase for comprehensive weekly reviews
        - Supports complete GTD system analysis and pattern recognition
        - Enables AI-assisted productivity insights across entire vault
        - Provides full context for automated review generation
        - Weekly review automation and stalled project detection
    """
    import json

    result = resource_handler.get_content(vault_path)
    return json.dumps(result, indent=2)


@mcp.resource(
    "gtd://{vault_path}/content/{file_type}",
    name="GTD Filtered Content Reader",
    description="Read GTD files filtered by type with comprehensive content for "
    "focused analysis",
    annotations={"readOnlyHint": True, "idempotentHint": True},
)
async def read_content_filtered_resource(vault_path: str, file_type: str) -> str:
    """Read GTD files filtered by type with comprehensive content extraction.

    This resource provides filtered comprehensive content access for specific GTD
    categories, supporting focused analysis while maintaining complete file parsing.
    Combines filtering capabilities with full content access for targeted workflows.

    URI Pattern: gtd://{vault_path}/content/{file_type}

    Args:
        vault_path: Path to the Obsidian vault directory extracted from URI
        file_type: GTD file type filter (inbox, projects, next-actions,
                  waiting-for, someday-maybe, context, reference)

    Returns:
        JSON string with status, complete files data for matching file type,
        including content, frontmatter, detailed tasks, links, counts, summary
        statistics, and vault path. Provides focused yet comprehensive analysis
        for specific GTD categories.

    Example Usage:
        Resource URI: gtd://path/to/vault/content/projects
        Claude Desktop: "Analyze all project files with full details"
        Resource URI: gtd://path/to/vault/content/inbox
        Claude Desktop: "Process inbox with complete context"

    GTD Context:
        - Use during Clarify phase for comprehensive inbox processing
        - Supports detailed project review with complete task context
        - Enables focused analysis while maintaining full data access
        - Phase-specific review automation (projects review, inbox processing)
        - Context-aware AI assistance for specific GTD categories
    """
    import json

    result = resource_handler.get_content(vault_path, file_type)
    return json.dumps(result, indent=2)


def main() -> None:
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
