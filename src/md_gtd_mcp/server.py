"""FastMCP server for markdown-based GTD system.

This server provides MCP (Model Context Protocol) integration for Getting Things Done
(GTD) workflows using Obsidian markdown files. The server implements a clean separation
between resources (read-only data access) and tools (write operations) following MCP
protocol best practices for semantic correctness and optimal Claude Desktop integration.

## Resource Architecture (Read-Only Operations)

### File Discovery Resources (Fast - Metadata Only)
- gtd://{vault_path}/files - List all GTD files with metadata
- gtd://{vault_path}/files/{file_type} - List filtered GTD files by type

### Single File Resources (Medium Speed - Full Content)
- gtd://{vault_path}/file/{file_path} - Read single GTD file with complete parsing

### Comprehensive Content Resources (Slower - All Content)
- gtd://{vault_path}/content - Read all GTD files with comprehensive analysis
- gtd://{vault_path}/content/{file_type} - Read filtered GTD files with content

All resources include proper MCP annotations (readOnlyHint: true, idempotentHint: true)
for optimal caching and LLM understanding.

## Tool Architecture (Write Operations)

- setup_gtd_vault - Create GTD folder structure safely (never overwrites existing files)

## Claude Desktop Integration

The server is optimized for Claude Desktop with comprehensive instructions that guide
users through GTD workflows using resource URI patterns. Instructions include:
- Daily workflow examples (inbox processing, project review, context planning)
- Weekly review patterns (complete analysis, category-specific reviews)
- Performance guidance (when to use each resource type)
- GTD phase mapping (Capture → Clarify → Organize → Reflect → Engage)

## Protocol Compliance

Follows MCP 1.0 specification with FastMCP framework for enterprise-ready automation.
"""

from typing import Any

from fastmcp import FastMCP

from md_gtd_mcp.services.resource_handler import ResourceHandler
from md_gtd_mcp.services.vault_setup import setup_gtd_vault as setup_vault_impl

mcp: FastMCP[Any] = FastMCP(
    name="Markdown GTD",
    instructions="""
This server provides AI-powered Getting Things Done (GTD) workflow automation for
Obsidian markdown files using MCP resources and tools.

## Quick Start for Claude Desktop

### Essential Resources (Read-Only Operations)
Use these URI patterns to access your GTD data:

• `gtd://vault_path/files` - List all GTD files with metadata
• `gtd://vault_path/files/inbox` - List only inbox files for processing
• `gtd://vault_path/file/gtd/inbox.md` - Read specific file with full content
• `gtd://vault_path/content` - Read all GTD files with comprehensive analysis
• `gtd://vault_path/content/projects` - Read only project files with content

### Essential Tool (Write Operations)
• `setup_gtd_vault` - Create GTD folder structure safely (never overwrites files)

## GTD Workflow Integration

### Daily Workflow Examples:
**Inbox Processing**: "Access gtd://vault_path/content/inbox and help me process
these captured items following GTD methodology"

**Project Review**: "Read gtd://vault_path/content/projects and give me a summary
of project status with next actions needed"

**Context Planning**: "Show me gtd://vault_path/files/context to see available
contexts, then gtd://vault_path/content/next-actions for today's planning"

### Weekly Review Examples:
**Complete Analysis**: "Access gtd://vault_path/content for comprehensive weekly
review - analyze all projects, stalled items, and completion patterns"

**Category Review**: "Review gtd://vault_path/content/projects,
gtd://vault_path/content/waiting-for, and gtd://vault_path/content/someday-maybe
for weekly planning"

## Resource URI Patterns

### File Discovery (Fast - Metadata Only)
- `gtd://vault_path/files` → All GTD files with task/link counts
- `gtd://vault_path/files/inbox` → Inbox files only
- `gtd://vault_path/files/projects` → Project files only
- `gtd://vault_path/files/next-actions` → Next action files only
- `gtd://vault_path/files/context` → Context files only

### Single File Analysis (Medium Speed - Full Content)
- `gtd://vault_path/file/gtd/inbox.md` → Complete inbox file analysis
- `gtd://vault_path/file/gtd/projects.md` → Full project file content
- `gtd://vault_path/file/gtd/next-actions.md` → Next actions with context

### Comprehensive Analysis (Slower - All Content)
- `gtd://vault_path/content` → Complete vault analysis for reviews
- `gtd://vault_path/content/inbox` → All inbox files with full content
- `gtd://vault_path/content/projects` → All project files with analysis

## Performance Guidelines

**Quick Checks**: Use `gtd://vault_path/files` patterns for file counts and overview
**Detailed Analysis**: Use `gtd://vault_path/file/path` for specific file review
**Weekly Reviews**: Use `gtd://vault_path/content` patterns for comprehensive analysis

## GTD Phase Mapping

**Capture Phase**: Quick file listings to understand vault structure
**Clarify Phase**: Single file analysis for detailed processing
**Organize Phase**: Content analysis for categorization and context assignment
**Reflect Phase**: Comprehensive content analysis for reviews and planning
**Engage Phase**: Context and next-action file analysis for daily execution

Replace 'vault_path' with your actual Obsidian vault path in all URIs.
""",
)


@mcp.tool()
def setup_gtd_vault(vault_path: str) -> dict[str, Any]:
    """Create GTD folder structure and template files if missing.

    This tool safely initializes a complete Getting Things Done (GTD) system in your
    Obsidian vault following David Allen's methodology. Perfect for first-time setup
    or adding GTD structure to existing vaults.

    CRITICAL SAFETY GUARANTEE: Only creates files/folders that don't exist - NEVER
    overwrites existing files. Your existing notes and structure remain untouched.

    Creates GTD folder structure:
    • GTD/inbox.md - Capture zone for quick thoughts and ideas
    • GTD/projects.md - Active projects requiring multiple steps
    • GTD/next-actions.md - Single actionable tasks organized by context
    • GTD/waiting-for.md - Items waiting for others' responses
    • GTD/someday-maybe.md - Future possibilities and ideas
    • GTD/contexts/ - Context-based action organization (@home, @computer, etc.)

    Each file includes starter templates with GTD best practices and examples.

    Args:
        vault_path: Path to your Obsidian vault directory (absolute path recommended)

    Returns:
        Dictionary with 'status', list of 'created' items, 'already_existed' items,
        and success confirmation. Use this to verify setup completion.

    Claude Desktop Usage Examples:
        "Set up GTD structure in my vault at /path/to/vault"
        "Initialize Getting Things Done system in my Obsidian vault"
        "Create GTD folders and templates in my vault safely"

    After setup, use resource URIs like:
        • gtd://vault_path/files - Overview of your new GTD system
        • gtd://vault_path/content/inbox - Start processing captured items
        • gtd://vault_path/content - Complete system review
    """
    return setup_vault_impl(vault_path)


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
