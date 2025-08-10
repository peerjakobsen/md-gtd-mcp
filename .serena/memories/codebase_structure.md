# Codebase Structure

## Root Directory
```
/Users/peerjakobsen/projects/md-gtd-mcp/
├── .gitignore              # Git ignore rules
├── .python-version         # Python version specification
├── CLAUDE.md              # Development documentation for Claude Code
├── README.md              # Project readme
├── pyproject.toml         # Project configuration and dependencies
├── uv.lock               # Dependency lock file
└── src/                  # Source code directory
    └── md_gtd_mcp/       # Main package
        ├── __init__.py   # Package initialization (empty)
        └── server.py     # MCP server implementation
```

## Package Structure
- **Single Package**: `md_gtd_mcp` in `src/` directory
- **Entry Point**: `server.py` contains main MCP server logic
- **No Modules**: No additional utility modules or subdirectories yet

## Key Files
- **`server.py`**: Contains FastMCP server instance, tool definitions, and main() function
- **`pyproject.toml`**: All project configuration including dependencies, scripts, and tool settings
- **`CLAUDE.md`**: Comprehensive development documentation with commands and architecture

## Missing Structure
- **No `tests/` directory**: Tests should be added
- **No configuration files**: Config system not implemented yet
- **No utility modules**: Core GTD functionality not built yet
- **No data models**: Markdown parsing and GTD structures not defined

## Future Structure (Planned)
Based on roadmap, will likely need:
- Configuration management module
- Markdown parsing utilities
- GTD categorization logic
- File system navigation tools
- Test suite directory
