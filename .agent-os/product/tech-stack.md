# Tech Stack

## Context

Technical architecture for the MD-GTD-MCP server, based on global Agent OS standards with MCP-specific adaptations.

## Core Framework & Language
- **MCP Server Framework**: FastMCP 0.2+
- **Language**: Python 3.13+
- **Package Manager**: uv (preferred) / pip
- **Virtual Environment**: uv / venv

## Development & Code Quality
- **Testing Framework**: pytest
- **Code Quality**: ruff + mypy
- **Code Linting**: ruff check
- **Code Formatting**: ruff format
- **Type Checking**: mypy

## File Processing & Data
- **Markdown Processing**: python-frontmatter + markdown libraries
- **File System Operations**: pathlib + os
- **Text Processing**: Regular expressions + NLP libraries (if needed)
- **Configuration**: pydantic for settings validation

## MCP Integration
- **Protocol Version**: MCP 1.0
- **Server Type**: FastMCP server
- **Communication**: JSON-RPC over stdio/SSE
- **Tools**: File operations, text analysis, markdown parsing
- **Resources**: Obsidian vault access, GTD templates

## MCP Implementation Details
- **Tool Descriptions**: Enhanced descriptions with GTD context and usage examples for optimal LLM understanding
- **Tool Annotations**: Behavioral hints (readOnlyHint, destructiveHint, idempotentHint, openWorldHint) to guide LLM tool selection
- **Tool Meta Information**: GTD phase indicators (capture/clarify/organize/reflect/engage), usage frequency, and categorization
- **Tool Tags**: Organized by GTD workflow, frequency, and functionality for filtering and discovery
- **Prompt Templates**: Pre-configured @mcp.prompt decorators for common GTD workflows (weekly_review, inbox_processing, project_planning, daily_planning)
- **Tool Transformation**: Tool.from_tool() patterns for context-specific tool adaptations (meeting notes vs email processing)
- **Interactive Features**: ctx.elicit() with structured dataclasses for comprehensive data gathering during GTD processes
- **LLM Sampling**: ctx.sample() integration for complex GTD decision-making and analysis
- **Server Instructions**: Comprehensive FastMCP server instructions explaining GTD methodology and workflow integration

## Obsidian Integration
- **File Format**: Markdown with YAML frontmatter
- **Vault Structure**: Flexible folder organization
- **Link Support**: Obsidian-style [[wikilinks]] and standard markdown links
- **Tag Support**: Obsidian hashtag format
- **Template Support**: Obsidian template syntax

## GTD Workflow Support
- **Categories**: Projects, Next Actions, Waiting For, Someday/Maybe, Reference
- **Contexts**: Location-based and tool-based contexts
- **Reviews**: Daily, weekly, monthly review templates
- **Capture**: Inbox processing and quick capture

## Development Environment
- **Python Version**: 3.13+
- **Dependency Management**: pyproject.toml with uv
- **Environment**: Local development with file system access
- **Configuration**: Environment variables + config files

## Deployment & Distribution
- **Distribution**: PyPI package for easy installation
- **Installation**: pip/uv installable MCP server
- **Configuration**: JSON config file for vault paths and preferences
- **Client Integration**: Compatible with Claude Code, Claude Desktop, and other MCP clients

## Security & Access
- **File Access**: Read/write access to specified Obsidian vault directories
- **Permissions**: User-controlled access to vault contents
- **Data Privacy**: Local processing, no external data transmission
- **Validation**: Input sanitization for file operations
