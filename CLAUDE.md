# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server that enables AI assistants to interact with Getting Things Done (GTD) workflows stored in Obsidian markdown files. The server bridges AI automation with personal productivity systems, providing intelligent inbox processing, project management, and review automation.

## Development Commands

### Package Management
- `uv install` - Install dependencies
- `uv add <package>` - Add new dependency
- `uv add --dev <package>` - Add development dependency
- `uv sync` - Sync dependencies with lock file

### Code Quality
- `uv run ruff check` - Run linting checks
- `uv run ruff format` - Format code
- `uv run mypy src/` - Run type checking

### Testing
- `uv run pytest` - Run all tests
- `uv run pytest <test_file>` - Run specific test file
- `uv run pytest -k <test_name>` - Run specific test by name

### Running the Server
- `uv run md-gtd-server` - Start the MCP server (defined in pyproject.toml scripts)
- `python -m md_gtd_mcp.server` - Alternative way to run the server

## Architecture

### Core Structure
- **MCP Server**: Built using FastMCP framework for handling MCP protocol communication
- **Entry Point**: `src/md_gtd_mcp/server.py` contains the main server setup and tool definitions
- **Package**: `src/md_gtd_mcp/` follows standard Python package structure

### Agent OS Integration
This project uses Agent OS for structured development:
- **Mission**: `.agent-os/product/mission.md` - Product vision and user stories
- **Tech Stack**: `.agent-os/product/tech-stack.md` - Technical architecture decisions
- **Roadmap**: `.agent-os/product/roadmap.md` - 3-phase development plan with checkboxes
- **Decisions**: `.agent-os/product/decisions.md` - Decision log for architectural choices
- **Current Spec**: `.agent-os/specs/2025-08-10-obsidian-vault-integration/` - Active specification for Obsidian vault integration feature

### Development Workflow
The project follows a 3-phase roadmap:
1. **Phase 1 (MVP)**: Core MCP server with Obsidian vault integration and basic categorization
2. **Phase 2**: Intelligent processing with project decomposition and advanced text analysis
3. **Phase 3**: Review automation and productivity analytics

### Configuration
- Uses `pyproject.toml` for project configuration with uv package management
- Ruff configured for Python 3.13 with 88 character line length
- MyPy strict type checking enabled
- FastMCP 2.11.2+ required for MCP server functionality

## Key Implementation Details

### MCP Tools
Tools are defined using the `@mcp.tool()` decorator in `server.py`. The current implementation includes a simple hello_world tool as a starting point.

### Target Integration
The server is designed to work with:
- Obsidian vaults with GTD folder structures
- Markdown files with YAML frontmatter
- GTD categories: Projects, Next Actions, Waiting For, Someday/Maybe, Reference
- Obsidian-style [[wikilinks]] and standard markdown links

## Code Quality Guidelines (Pre-commit Prevention)
- **End files with newline**: All files must end with a single newline character
- **No trailing whitespace**: Remove spaces/tabs at end of lines (most editors can show this)
- **Import sorting**: Place standard library imports first, then third-party, then local imports
- **Type hints**: Always include return type annotations for functions (`-> str`, `-> None`)
- **Docstrings**: Use triple quotes for function documentation explaining purpose
- **Line length**: Keep lines under 88 characters (ruff will auto-format longer lines)
- **File formatting**: Save files in UTF-8 without BOM, Unix line endings (LF not CRLF)
