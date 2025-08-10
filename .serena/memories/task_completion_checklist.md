# Task Completion Checklist

## Before Committing Code

### 1. Code Quality Checks (REQUIRED)
```bash
uv run ruff check    # Must pass with no errors
uv run ruff format   # Auto-format code
uv run mypy src/     # Must pass type checking
```

### 2. Testing (when tests exist)
```bash
uv run pytest       # All tests must pass
```

### 3. Functional Testing
```bash
uv run md-gtd-server # Verify MCP server starts without errors
```

## Development Workflow Standards

### After Adding New Dependencies
```bash
uv sync             # Update lock file
```

### After Adding New MCP Tools
- Verify tool has proper type hints
- Include descriptive docstring
- Test tool manually with MCP client
- Consider adding unit tests

### After Making Major Changes
- Update CLAUDE.md if commands change
- Update roadmap.md if features completed
- Consider updating documentation

## Quality Gates
- **No lint errors**: Ruff must pass cleanly
- **Type safety**: MyPy must pass in strict mode
- **Functionality**: MCP server must start successfully
- **Tests**: All tests must pass (when they exist)

## Notes
- Tests directory doesn't exist yet - should be created for new features
- Consider TDD approach: write tests first, then implement
- MCP tools should be testable in isolation
- Use Agent OS structured development approach
