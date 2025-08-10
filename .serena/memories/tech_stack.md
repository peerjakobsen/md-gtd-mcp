# Tech Stack

## Core Dependencies
- **Python**: 3.13+ (required)
- **FastMCP**: 2.11.2+ (MCP server framework)
- **Package Manager**: uv (preferred over pip)

## Development Dependencies
- **Code Quality**: ruff 0.12.8+ (linting and formatting)
- **Type Checking**: mypy 1.17.1+ (strict type checking enabled)
- **Testing**: pytest 8.4.1+ (no test files exist yet)

## Configuration
- **Build System**: hatchling
- **Entry Point**: `md-gtd-server` script points to `md_gtd_mcp.server:main`
- **Ruff**: 88 character line length, Python 3.13 target
- **MyPy**: Strict mode with additional warnings enabled

## Package Structure
- Standard Python package in `src/md_gtd_mcp/`
- MCP server implementation in `server.py`
- No additional modules or utilities yet

## Platform
- Developed on Darwin (macOS)
- Standard Unix-style commands available
