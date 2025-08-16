# Obsidian Vault Integration Specification

## Overview

This feature implements the foundational MCP server capability to read and parse Obsidian markdown files organized according to the Getting Things Done (GTD) methodology. The server will accept a vault path configuration, read markdown files from the standardized `gtd/` folder structure, parse tasks using the Obsidian Tasks plugin format with GTD-specific metadata, extract project frontmatter, and process both standard markdown links and wikilinks to understand the relationships between projects, actions, and contexts.

## User Stories

### Primary User Stories

**As a GTD practitioner starting with Obsidian**, I want the MCP server to set up my GTD vault structure so that I have the proper folders and files to begin implementing GTD methodology.

**As a GTD practitioner using Obsidian**, I want the MCP server to read my vault so that AI assistants can understand my current GTD system structure.

**As a productivity optimizer**, I want the server to parse frontmatter from my GTD files so that AI can work with my project statuses, contexts, and priorities.

**As an Obsidian user**, I want the server to process markdown links in my files so that AI understands the connections between my projects, actions, and reference materials.

### Supporting User Stories

**As a project manager**, I want my GTD folder structure to be respected so that the server only processes relevant productivity files, not my entire knowledge base.

**As a configuration user**, I want to specify my vault path so that the server works with my specific Obsidian setup.

## Spec Scope

### In Scope

1. **Vault Path Configuration**: Accept vault path as a configuration parameter
2. **GTD Vault Setup**: Create standardized GTD folder structure if missing
3. **GTD Folder Structure**: Read from standardized GTD organization:
   - `inbox.md` - Capture area for new items
   - `projects.md` - Active projects with outcomes
   - `next-actions.md` - Context-organized actionable tasks
   - `waiting-for.md` - Delegated items
   - `someday-maybe.md` - Future possibilities
   - `contexts/` - Context-specific files (@calls, @computer, @errands)
3. **Obsidian Tasks Plugin Support**: Parse checkbox tasks with inline metadata:
   - Task completion status (`[ ]` vs `[x]`)
   - GTD contexts (@home, @office, @calls)
   - Project links via wikilinks (`[[Project Name]]`)
   - Priority, energy, time estimates via emojis
   - Dates (due, scheduled, start, done)
   - Delegation info for waiting-for items
4. **Project Frontmatter**: Parse YAML frontmatter for project metadata:
   - Desired outcomes
   - Project status and area
   - Review and completion dates
5. **Link Processing**: Extract both markdown links and wikilinks
6. **Basic MCP Tools**: Expose file reading and vault setup capabilities through MCP protocol
7. **Data Structure Optimization**: Return GTD-aligned structured data for AI consumption

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
2. Set up GTD folder structure and files if missing from vault
3. Read all markdown files from the `gtd/` subfolder
4. Parse YAML frontmatter and extract GTD properties
5. Process standard markdown links within file content
6. Return structured data optimized for AI assistant consumption
7. Pass all tests demonstrating correct parsing and data structure

The deliverable enables AI assistants to understand and work with Obsidian-based GTD workflows as a foundation for future intelligent automation features.
