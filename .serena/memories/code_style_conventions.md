# Code Style and Conventions

## General Style
- **Line Length**: 88 characters (ruff configured)
- **Python Version**: 3.13+ features allowed
- **Type Hints**: Strict typing enforced by mypy
- **Docstrings**: Triple-quoted docstrings for functions (seen in hello_world example)

## Naming Conventions
- **Functions**: snake_case (e.g., `hello_world`)
- **Variables**: snake_case (e.g., `mcp`)
- **Constants**: Not yet established in codebase

## Code Quality Standards
- **Linting**: Ruff with rules E, F, I, N, UP, B, C4, PIE, T20
- **Type Checking**: MyPy strict mode with return type warnings
- **Imports**: Sorted by ruff (I rule enabled)

## MCP-Specific Patterns
- Tools defined with `@mcp.tool()` decorator
- Type hints required for tool functions
- Docstrings explain tool purpose
- Return type annotations mandatory

## Current Code Examples
```python
@mcp.tool()
def hello_world() -> str:
    \"\"\"A simple hello world tool to test the MCP server.\"\"\"
    return "Hello from Markdown GTD MCP Server!"
```

## Documentation Standards
- Comprehensive CLAUDE.md with development commands
- Type hints serve as inline documentation
- Docstrings explain business purpose, not implementation
