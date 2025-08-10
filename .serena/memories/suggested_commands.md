# Suggested Commands

## Package Management
```bash
uv install          # Install dependencies
uv add <package>    # Add new dependency
uv add --dev <package>  # Add development dependency
uv sync            # Sync dependencies with lock file
```

## Pre-commit Setup (One-time)
```bash
uv sync                    # Install pre-commit dependency
uv run pre-commit install  # Install git hooks
```

## Code Quality (Automated via pre-commit)
```bash
# Manual checks (pre-commit runs these automatically on commit)
uv run ruff check          # Run linting checks
uv run ruff format         # Format code
uv run mypy src/           # Run type checking

# Run all pre-commit hooks manually
uv run pre-commit run --all-files
```

## Testing
```bash
uv run pytest                # Run all tests
uv run pytest <test_file>    # Run specific test file
uv run pytest -k <test_name> # Run specific test by name
```

## Running the Server
```bash
uv run md-gtd-server        # Start MCP server (preferred)
python -m md_gtd_mcp.server # Alternative way to run
```

## System Commands (Darwin/macOS)
```bash
ls          # List files
find        # Find files
grep        # Search in files
git         # Version control
cd          # Change directory
```

## Development Workflow
1. Make changes to code
2. Git commit (pre-commit hooks run automatically)
3. If pre-commit fails, fix issues and commit again
4. Run tests when they exist: `uv run pytest`
5. Test MCP server: `uv run md-gtd-server`

## Pre-commit Features
- Automatically runs on git commit
- Includes ruff linting with auto-fix
- Includes ruff formatting
- Includes mypy type checking
- Includes basic file quality checks (YAML, TOML, whitespace)
- Prevents commits with quality issues

## Important Notes
- Pre-commit hooks enforce code quality automatically
- No test files exist yet - should be created
- Use uv over pip for package management
- MCP server runs on local machine for development
