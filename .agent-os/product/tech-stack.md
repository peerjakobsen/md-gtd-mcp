# Tech Stack

## Context

Technical architecture for the MD-GTD-MCP server, based on global Agent OS standards with MCP-specific adaptations.

## Core Framework & Language
- **MCP Server Framework**: FastMCP 0.2+
- **Language**: Python 3.13+
- **Package Manager**: uv (preferred) / pip
- **Virtual Environment**: uv / venv

## Development & Code Quality
- **Testing Framework**: pytest
- **Code Quality**: ruff + mypy
- **Code Linting**: ruff check
- **Code Formatting**: ruff format
- **Type Checking**: mypy

## File Processing & Data
- **Markdown Processing**: python-frontmatter + markdown libraries
- **File System Operations**: pathlib + os
- **Text Processing**: Regular expressions + NLP libraries (if needed)
- **Configuration**: pydantic for settings validation

## MCP Integration
- **Protocol Version**: MCP 1.0
- **Server Type**: FastMCP server
- **Communication**: JSON-RPC over stdio/SSE
- **Tools**: File operations, text analysis, markdown parsing
- **Resources**: Obsidian vault access, GTD templates

## MCP Implementation Details
- **Tool Descriptions**: Enhanced descriptions with GTD context and usage examples for optimal LLM understanding
- **Tool Annotations**: Behavioral hints (readOnlyHint, destructiveHint, idempotentHint, openWorldHint) to guide LLM tool selection
- **Tool Meta Information**: GTD phase indicators (capture/clarify/organize/reflect/engage), usage frequency, and categorization
- **Tool Tags**: Organized by GTD workflow, frequency, and functionality for filtering and discovery
- **Prompt Templates**: Pre-configured @mcp.prompt decorators for orchestrating GTD workflows through Claude Desktop's LLM intelligence (Decision D008)
- **Tool Transformation**: Tool.from_tool() patterns for context-specific tool adaptations (meeting notes vs email processing)
- **Server Instructions**: Comprehensive FastMCP server instructions explaining GTD methodology and workflow integration

## MCP Prompts Architecture
- **Design Philosophy**: Leverage Claude Desktop's LLM intelligence rather than requiring server-side API access (Decision D008)
- **Workflow Orchestration**: MCP prompts guide Claude through GTD methodology without server complexity
- **Core GTD Prompts**:
  - `inbox_clarification` - Analyze and categorize inbox items following GTD principles
  - `weekly_review` - Structure comprehensive weekly review process with project status
  - `project_decomposition` - Break high-level projects into actionable next steps
  - `daily_planning` - Prioritize tasks based on context, energy, and available time
  - `stall_detection` - Identify and address projects without recent activity
  - `context_switching` - Suggest tasks appropriate for current context (@home, @office, etc.)
- **Prompt Structure**: Accept GTD state as arguments, return structured instructions for Claude Desktop
- **Resource Integration**: Prompts guide Claude to read GTD data using resource templates
- **Tool Integration**: Prompts guide Claude to perform actions using appropriate tools
- **API-Free Operation**: Zero dependency on external LLM APIs (Anthropic, OpenAI, AWS Bedrock)
- **User Accessibility**: No API key configuration required for end users

## SOP Integration
- **Design Philosophy**: Enable organization-specific workflows through Standard Operating Procedures (Decision D009)
- **Simple Architecture**: Single `projects.md` file with SOP metadata linking to procedures in `GTD/SOPs/` folder
- **Project-SOP Linking**: Projects reference SOPs via simple metadata format: `sop: <sop-name>`
- **SOP Storage**: Separate markdown files in `GTD/SOPs/` folder for user-controlled content
- **Prompt Enhancement**: MCP prompts dynamically read and incorporate relevant SOPs during workflow processing
- **Template Support**: Starter SOP templates for common business procedures:
  - `1-1-meetings.md` - Manager 1:1 meeting structure and follow-up patterns
  - `MEDDPICC.md` - Sales opportunity qualification methodology
  - `monthly-reports.md` - Recurring business report templates and requirements
  - `career-development.md` - Employee growth discussion frameworks
  - `code-review.md` - Technical review process and quality gates
  - `incident-response.md` - Issue handling and escalation procedures
- **User Control**: SOPs maintained entirely by users through direct Obsidian editing
- **Reusability**: SOPs can be linked to multiple projects for consistent workflow execution
- **Discovery**: Auto-suggestion of relevant SOPs based on project patterns and naming

### SOP Template Structure
All SOPs follow a standardized template with 7 GTD-integrated sections to ensure reliable parsing by MCP prompts:

1. **GTD Clarification Questions**: Standard questions MCP prompts use to determine actionability (Is this actionable? What's the successful outcome? What's the next physical action? What context is needed? Time/energy required?)

2. **Project Decomposition Template**: Structured breakdown patterns including standard subtasks for this work type, common dependencies to verify, and typical blockers to anticipate

3. **Context Assignment Rules**: Guidelines for assigning GTD contexts including default contexts for this work type (@home, @office, @calls), context-specific considerations, and optimal timing

4. **Review Checkpoints**: Structured review criteria defining what to check daily, weekly, and at project milestones to maintain GTD review discipline

5. **Success Criteria**: Clear completion definitions including deliverables checklist, quality gates, and measurable outcomes

6. **Common Patterns**: Documented workflow sequences including typical task progression, best practices, and integration points with other systems or procedures

7. **Anti-patterns to Avoid**: Failure mode prevention including common mistakes, warning signs of derailment, and pitfalls specific to this type of work

This structure enables MCP prompts to systematically parse and apply SOPs while maintaining proper GTD methodology, transforming organization-specific procedures into actionable workflow guidance for Claude Desktop.

## Obsidian Integration
- **File Format**: Markdown with YAML frontmatter
- **Vault Structure**: Flexible folder organization
- **Link Support**: Obsidian-style [[wikilinks]] and standard markdown links
- **Tag Support**: Obsidian hashtag format
- **Template Support**: Obsidian template syntax

## GTD Workflow Support
- **Categories**: Projects, Next Actions, Waiting For, Someday/Maybe, Reference
- **Contexts**: Location-based and tool-based contexts
- **Reviews**: Daily, weekly, monthly review templates
- **Capture**: Inbox processing and quick capture

## Development Environment
- **Python Version**: 3.13+
- **Dependency Management**: pyproject.toml with uv
- **Environment**: Local development with file system access
- **Configuration**: Environment variables + config files

## Deployment & Distribution
- **Distribution**: PyPI package for easy installation
- **Installation**: pip/uv installable MCP server
- **Configuration**: JSON config file for vault paths and preferences
- **Client Integration**: Compatible with Claude Code, Claude Desktop, and other MCP clients

## Security & Access
- **File Access**: Read/write access to specified Obsidian vault directories
- **Permissions**: User-controlled access to vault contents
- **Data Privacy**: Local processing, no external data transmission
- **Validation**: Input sanitization for file operations
