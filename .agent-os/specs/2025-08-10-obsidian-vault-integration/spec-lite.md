# Obsidian Vault Integration (Lite)

**Purpose**: MCP server to read/parse Obsidian GTD workflows using Tasks plugin format

**Key Requirements**:
- Accept vault path as config parameter
- Read from GTD folder structure (inbox, projects, next-actions, waiting-for, contexts/)
- Parse Obsidian Tasks: checkboxes with GTD metadata (contexts, projects, delegation)
- Extract project frontmatter (outcomes, status, review dates)
- Process markdown links and wikilinks for relationships
- Return GTD-aligned structured data for AI consumption

**Success Criteria**:
- Correctly identifies GTD file types (inbox, projects, contexts, etc.)
- Parses Obsidian Tasks with all GTD metadata
- Extracts project outcomes and relationships
- All tests pass for GTD workflow parsing

**Foundation for**: Future GTD workflow automation and intelligent processing features
