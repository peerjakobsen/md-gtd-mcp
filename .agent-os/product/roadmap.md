# Roadmap

## Phase 1: Foundation & Core MCP Server (MVP)
**Status**: ~14% Complete (1/7 features implemented)

**Goal**: Build a functional MCP server that can read and analyze Obsidian GTD markdown files

**Success Criteria**:
- MCP server responds to basic queries about GTD system
- Can read and parse Obsidian markdown files with frontmatter
- Provides simple inbox categorization suggestions

**Features**:
- [x] MCP Server Setup (S) - FastMCP server with basic tool registration
- [ ] Obsidian Vault Integration (M) - Read markdown files, parse frontmatter and links
- [ ] File System Navigation (S) - Browse GTD folder structure and find relevant files
- [ ] Basic Markdown Parsing (M) - Extract tasks, projects, and GTD categories from markdown
- [ ] Simple Categorization Logic (L) - Suggest GTD categories for inbox items using basic heuristics
- [ ] Configuration System (S) - JSON config for vault paths and basic preferences
- [ ] Error Handling & Validation (M) - Robust error handling for file operations and invalid inputs

## Phase 2: Intelligent Processing & Project Management
**Goal**: Add AI-powered insights for project decomposition and workflow automation

**Success Criteria**:
- Can break down projects into actionable next steps
- Identifies stalled projects and suggests improvements
- Processes multiple inbox items efficiently

**Features**:
- [ ] Advanced Text Analysis (L) - NLP-based extraction of actions, contexts, and priorities from text
- [ ] Project Decomposition Engine (XL) - Break high-level projects into specific, actionable tasks
- [ ] Stall Detection System (M) - Identify projects without recent activity or clear next actions
- [ ] Batch Inbox Processing (L) - Handle multiple captured thoughts simultaneously with consistent logic
- [ ] Context & Priority Recognition (L) - Identify GTD contexts (@calls, @errands) and priority indicators
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
- [ ] Historical Trend Analysis (L) - Track productivity patterns over time for continuous improvement
- [ ] Integration Optimization (M) - Performance improvements for large vault processing

**Dependencies**:
- Phase 1 must be complete for vault integration
- Phase 2 project analysis required for meaningful review automation
- Requires substantial user testing to validate productivity improvements
