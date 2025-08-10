# Obsidian Vault Integration (Lite)

**Purpose**: Foundation MCP server capability to read/parse Obsidian GTD markdown files

**Key Requirements**:
- Accept vault path as config parameter
- Read markdown files from `{vault_path}/gtd/` folder only
- Parse GTD frontmatter: status, context, priority, due_date, project, tags
- Process standard markdown links `[text](path/url)`
- Return optimally structured data for AI consumption

**Success Criteria**:
- MCP server reads GTD folder files
- Frontmatter parsed correctly with GTD properties
- Markdown links extracted and structured
- All tests pass for parsing functionality

**Foundation for**: Future GTD workflow automation and intelligent processing features
