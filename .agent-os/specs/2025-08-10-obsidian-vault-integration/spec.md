# Obsidian Vault Integration Specification

## Overview

This feature implements the foundational MCP server capability to read and parse Obsidian markdown files within a GTD workflow structure. The server will accept a vault path configuration, read markdown files from the `gtd/` folder, parse YAML frontmatter for GTD-specific properties, and process standard markdown links.

## User Stories

### Primary User Stories

**As a GTD practitioner using Obsidian**, I want the MCP server to read my vault so that AI assistants can understand my current GTD system structure.

**As a productivity optimizer**, I want the server to parse frontmatter from my GTD files so that AI can work with my project statuses, contexts, and priorities.

**As an Obsidian user**, I want the server to process markdown links in my files so that AI understands the connections between my projects, actions, and reference materials.

### Supporting User Stories

**As a project manager**, I want my GTD folder structure to be respected so that the server only processes relevant productivity files, not my entire knowledge base.

**As a configuration user**, I want to specify my vault path so that the server works with my specific Obsidian setup.

## Spec Scope

### In Scope

1. **Vault Path Configuration**: Accept vault path as a configuration parameter
2. **GTD Folder Processing**: Read markdown files specifically from `{vault_path}/gtd/` directory
3. **Frontmatter Parsing**: Parse YAML frontmatter with GTD-specific properties:
   - `status` (active, completed, someday, waiting, etc.)
   - `context` (location or tool-based contexts like @home, @computer)
   - `priority` (high, medium, low, or numeric)
   - `due_date` (ISO date format)
   - `project` (parent project reference)
   - `tags` (GTD categories and custom tags)
4. **Standard Markdown Link Processing**: Parse and extract both internal `[text](path)` and external `[text](url)` links
5. **Basic MCP Tools**: Expose fundamental file reading capabilities through MCP protocol
6. **Data Structure Optimization**: Return parsed data in an optimal structure for AI consumption

### Out of Scope

- GTD-specific workflow tools (categorization, project decomposition)
- Error handling for malformed files or permission issues
- Performance optimizations (caching, indexing)
- Multiple vault support
- Auto-discovery of vault locations
- Wikilink processing (`[[]]` format)
- Advanced search or filtering capabilities

## Expected Deliverable

A working MCP server that can:

1. Accept a vault path configuration parameter
2. Read all markdown files from the `gtd/` subfolder
3. Parse YAML frontmatter and extract GTD properties
4. Process standard markdown links within file content
5. Return structured data optimized for AI assistant consumption
6. Pass all tests demonstrating correct parsing and data structure

The deliverable enables AI assistants to understand and work with Obsidian-based GTD workflows as a foundation for future intelligent automation features.
