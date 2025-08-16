# Roadmap

## Phase 1: Foundation & Core MCP Server (MVP)
**Status**: ~67% Complete (10/15 features implemented)

**Goal**: Build a functional MCP server that can read and analyze Obsidian GTD markdown files

**Success Criteria**:
- ✅ MCP server responds to queries about GTD system (setup_gtd_vault, read_gtd_file, list_gtd_files, read_gtd_files)
- ✅ Can read and parse Obsidian markdown files with frontmatter (MarkdownParser, TaskExtractor, LinkExtractor)
- ✅ Can create and manage GTD vault structure (setup_gtd_vault with safe file creation)
- ⏳ Provides simple inbox categorization suggestions (not yet implemented)

**Features**:
- [x] MCP Server Setup (S) - FastMCP server with basic tool registration, server instructions, and meta information for GTD context
- [x] Obsidian Vault Integration (M) - Read markdown files, parse frontmatter and links. Implemented with MarkdownParser, LinkExtractor, and VaultReader
- [x] File System Navigation (S) - Browse GTD folder structure and find relevant files. VaultReader handles file type detection
- [x] Basic Markdown Parsing (M) - Extract tasks, projects, and GTD categories from markdown. TaskExtractor, LinkExtractor, MarkdownParser complete
- [📋] GTD Phase-Aware Task Recognition (M) - **DESIGNED** (Decision D006 made, implementation pending). Implement file-type aware task recognition respecting GTD phases. Inbox files recognize ALL `- [ ]` items without #task requirement (pure capture). Other GTD files require #task tags for Obsidian Tasks plugin compatibility. Creates clear distinction between captured and clarified items
- [ ] Inbox Capture Tool (S) - MCP tool for adding items directly to inbox without requiring contexts or detailed metadata. Follows GTD quick-capture principle where contexts are assigned during Clarify phase, not Capture phase
- [ ] Simple Categorization Logic (L) - Suggest GTD categories for inbox items using basic heuristics
- [🔧] MCP Tool Descriptions & Annotations (M) - **BASIC** (basic descriptions exist, GTD enhancements needed). Enhanced tool descriptions with GTD context, usage examples, and behavioral hints (readOnlyHint, destructiveHint, idempotentHint) to guide LLM behavior. Tools include meta information indicating GTD phase (capture/clarify/organize/reflect/engage) and typical usage frequency
- [ ] MCP Prompts for GTD Workflows (M) - Pre-configured prompt templates using @mcp.prompt decorator for common GTD workflows: weekly_review, inbox_processing, project_planning, daily_planning. Each prompt provides structured guidance to help Claude understand specific GTD methodology steps and decision criteria
- [x] Configuration System (S) - JSON config for vault paths and basic preferences. VaultConfig class implemented
- [x] Vault Setup Tool (S) - setup_gtd_vault creates complete GTD folder structure safely without overwriting existing files
- [x] Read GTD File Tool (S) - read_gtd_file for parsing single GTD files with frontmatter and tasks
- [x] List GTD Files Tool (S) - list_gtd_files for vault overview with metadata and filtering
- [x] Read GTD Files Tool (M) - read_gtd_files for batch reading with comprehensive content extraction
- [x] Integration Testing Suite (L) - 10 end-to-end workflow scenarios tested (onboarding, migration, processing, review, etc.)
- [x] Error Handling & Validation (M) - Robust error handling for file operations and invalid inputs. Comprehensive error recovery tested

## Phase 2: Intelligent Processing & Project Management
**Goal**: Add AI-powered insights for project decomposition and workflow automation

**Success Criteria**:
- Can break down projects into actionable next steps
- Identifies stalled projects and suggests improvements
- Processes multiple inbox items efficiently

**Features**:
- [ ] Advanced Text Analysis (L) - NLP-based extraction of actions, contexts, and priorities from text with automatic context detection (@home, @office, @calls, @errands). Focus on Clarify phase analysis rather than Capture phase requirements
- [ ] Intelligent Context Assignment (M) - Suggest appropriate GTD contexts during Clarify phase based on task content analysis. Respects GTD methodology by NOT requiring contexts during initial capture
- [ ] Process Inbox Tool (L) - Guide transition from Capture to Clarify phase. Analyze inbox items and suggest GTD categories, contexts, and priority assignments with explanations. Adds #task tag when processing items, transforming raw captures into actionable tasks with processing audit trail
- [ ] Project Decomposition Engine (XL) - Break high-level projects into specific, actionable tasks
- [ ] Stall Detection System (M) - Identify projects without recent activity or clear next actions
- [ ] Batch Inbox Processing (L) - Handle multiple captured thoughts simultaneously with consistent logic
- [ ] Context & Priority Recognition (L) - Identify GTD contexts (@calls, @errands) and priority indicators during appropriate GTD phases
- [ ] Intelligent Tool Naming & Organization (S) - GTD-specific tool names (process_inbox, capture_item, review_projects) with proper categorization and tags for LLM understanding
- [ ] Context-Aware Tool Transformation (M) - Dynamic tool adaptation using Tool.from_tool() patterns to create specialized versions based on user context (e.g., transform generic "process_item" into "process_meeting_notes" or "process_email_capture" with appropriate parameter defaults)
- [ ] Template System (M) - Customizable templates for different project types and workflows
- [ ] Linking Intelligence (M) - Understand and suggest connections between related projects and notes

## Phase 3: Review Automation & Analytics
**Goal**: Automate GTD reviews and provide productivity insights

**Success Criteria**:
- Generates comprehensive weekly review summaries
- Provides actionable productivity insights
- Reduces review time by 50% through automation

**Features**:
- [ ] Weekly Review Generator (L) - Automated summaries of completed actions and project status
- [ ] Productivity Pattern Analysis (XL) - Identify trends, bottlenecks, and optimization opportunities
- [ ] Focus Recommendations (L) - Suggest priority areas based on context, energy, and available time
- [ ] Progress Tracking Dashboard (M) - Visual insights into project advancement and completion rates
- [ ] Custom Review Templates (M) - Flexible review formats for different review types and frequencies
- [ ] LLM Sampling Integration (L) - Use Claude's capabilities for complex GTD decisions through ctx.sample() for nuanced analysis of project status, priority assessment, and workflow optimization recommendations
- [ ] Interactive Elicitation (M) - Gather structured input during reviews and processing using ctx.elicit() with dataclasses for TaskDetails, ProjectInfo, and ReviewCriteria to ensure comprehensive GTD metadata capture
- [ ] Historical Trend Analysis (L) - Track productivity patterns over time for continuous improvement
- [ ] Integration Optimization (M) - Performance improvements for large vault processing

**Dependencies**:
- Phase 1 must be complete for vault integration
- Phase 2 project analysis required for meaningful review automation
- Requires substantial user testing to validate productivity improvements
