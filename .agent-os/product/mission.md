# Mission

## Pitch

An MCP server that transforms Obsidian GTD workflows into AI-powered productivity systems, enabling intelligent automation of inbox processing, project planning, and reviews while maintaining the flexibility of markdown-based knowledge management.

## Users

**Primary Customer**: GTD practitioners who use Obsidian for personal productivity management

**User Personas**:

1. **The Knowledge Worker**:
   - Professional using GTD methodology for 2+ years
   - Stores projects, tasks, and notes in Obsidian
   - Struggles with consistent weekly reviews and inbox processing
   - Values automation that preserves their established workflow

2. **The Project Manager**:
   - Manages multiple concurrent projects with varying complexities
   - Uses Obsidian as a central hub for project documentation
   - Needs assistance breaking down high-level objectives into actionable tasks
   - Wants AI insights for identifying project bottlenecks

3. **The Productivity Optimizer**:
   - Power user of productivity systems and tools
   - Interested in AI automation to enhance existing GTD practice
   - Seeks data-driven insights about their productivity patterns
   - Willing to adapt workflow for significant efficiency gains

4. **The Professional Manager**:
   - Manages team of 5-15 direct reports with regular 1:1 meetings
   - Conducts career development discussions and performance reviews
   - Needs consistent structure for recurring management activities
   - Wants to follow organization-specific procedures and best practices
   - Values automation that incorporates company SOPs and methodologies

5. **The Sales Professional**:
   - Manages 10-30 active sales opportunities using methodologies like MEDDPICC
   - Tracks complex B2B sales cycles with multiple stakeholders
   - Needs to follow qualification frameworks and sales processes consistently
   - Requires integration of sales methodology with personal GTD system
   - Values workflow automation that maintains CRM-like rigor in Obsidian

## The Problem

1. **Inbox Processing Bottleneck**: GTD practitioners spend 30-60 minutes daily categorizing captured thoughts, meeting notes, and ideas. This manual process is repetitive and prone to inconsistency, leading to delayed processing and decision fatigue.

2. **Project Clarity and Support Material Chaos**: 40-60% of projects lack clear outcomes, purpose statements, and organized support material. Without proper project planning documentation, practitioners struggle to maintain focus on successful outcomes and next physical actions. Project support material (meeting notes, research, brainstorming) remains scattered across multiple locations instead of being organized around project outcomes.

3. **Ineffective Weekly Reviews**: The critical GTD weekly review process is time-consuming and often skipped. Without regular reviews, systems become cluttered with outdated information and missed opportunities.

4. **Knowledge Extraction Overhead**: Valuable insights from meeting notes, emails, and documents require manual extraction into actionable tasks, causing important items to remain buried in notes.

## Key Principles

1. **GTD Phase Integrity**: Respect the five GTD phases (Capture → Clarify → Organize → Reflect → Engage) by providing appropriate tools for each phase. Quick capture requires minimal friction with NO metadata decisions (inbox items NEVER have #task tags). Clarification phase consciously adds #task tags, contexts, and categories, creating clear distinction between captured and processed items.

2. **Universal Compatibility**: Support standard Obsidian markdown format (`- [ ]` tasks) as the primary interface, ensuring compatibility with existing tools like Claude Desktop and other AI assistants while maintaining optional enhanced functionality.

3. **Project Support Material Separation & Non-Duplication**: Maintain David Allen's fundamental distinction between project support material (planning, research, reference information) and action lists. Project files serve as repositories for project outcomes, planning notes, and reference material - NOT as task containers. Actions are extracted to appropriate GTD category files (next-actions.md, waiting-for.md, someday-maybe.md) with inline context tags (@home, @computer, @calls). Context files serve as query views only - never storing duplicate tasks.

4. **Single Source of Truth**: Each task exists in exactly ONE file based on its GTD category status. Tasks are never duplicated across files - instead, context files (@computer.md, @home.md) contain Obsidian Tasks queries that filter tasks by inline tags. This prevents synchronization issues and maintains data integrity while enabling flexible multi-dimensional views.

5. **Workflow Preservation**: Enhance existing Obsidian GTD setups without forcing users to abandon their established systems, muscle memory, or preferred folder structures.

## Differentiators

1. **Proper GTD Methodology**: Unlike tools that mix capture and organization phases, maintains strict separation where inbox items require no contexts initially, and intelligent assistance is provided during the appropriate clarification phase.

2. **AI Assistant Integration**: Designed specifically for seamless integration with Claude Desktop and other AI assistants that naturally create tasks in standard markdown format, reducing friction between human and AI workflow collaboration.

3. **Context-Aware Intelligence**: Leverages the rich interconnected knowledge graph in Obsidian to provide contextually relevant suggestions, understanding project relationships and priorities that standalone AI assistants cannot grasp.

4. **Transparent Automation**: All AI decisions and suggestions are logged in markdown format, maintaining the transparency and reviewability that GTD practitioners value while enabling human oversight and correction.

## Key Features

### Inbox Processing
- **Frictionless Capture**: Accept and store inbox items in standard Obsidian format without requiring contexts, categories, or detailed metadata during the initial capture phase
- **Intelligent Clarification**: During the clarify phase, analyze captured thoughts and suggest GTD categories (project, next action, waiting for, someday/maybe) with contextual reasoning
- **Action Extraction**: Automatically extract actionable tasks from meeting notes, emails, and free-form text while respecting the capture → clarify workflow
- **Context Assignment Guidance**: Suggest appropriate GTD contexts (@home, @computer, @calls, @errands) during clarification, not capture
- **Batch Processing**: Process multiple inbox items simultaneously with consistent categorization logic during dedicated clarification sessions

### Project Support Material Management
- **Project Outcome Clarity**: Help define clear project outcomes, success criteria, and purpose statements that guide all related activities
- **Support Material Organization**: Organize meeting notes, research, brainstorming sessions, and reference documents around project outcomes for easy access during planning and review
- **Action Extraction**: Intelligently extract actionable next steps from project support material and route them to appropriate GTD category files (next-actions.md, waiting-for.md, someday-maybe.md) with inline context tags (@home, @computer, @calls, @errands)
- **SOP-Enhanced Planning**: Integrate organization-specific Standard Operating Procedures (SOPs) with project planning workflows for consistent execution of business processes like 1:1 meetings, sales methodologies (MEDDPICC), reporting cycles, and career development discussions
- **Project Status Tracking**: Monitor project health through clear outcomes, recent activity in support material, and linked actions across GTD category files (tracked via inline tags and queries)
- **Dependency and Resource Mapping**: Identify and document project dependencies, required resources, and stakeholder information within project support material

### Review Automation
- **Weekly Review Generation**: Create automated summaries of completed actions, stalled projects, and upcoming priorities
- **Pattern Analysis**: Identify productivity patterns, common bottlenecks, and workflow optimization opportunities
- **Focus Recommendations**: Suggest priority areas based on project urgency, energy requirements, and available time
- **Completion Insights**: Track and analyze completion rates across different project types and contexts

### Integration & Workflow
- **Native Obsidian Integration**: Work directly with existing folder structures, tags, and linking patterns
- **MCP Protocol Support**: Enable any Claude Code-compatible AI assistant to interact with GTD systems
- **Semantic API Design**: Clean separation between resources (read-only GTD data access) and tools (write operations) following MCP protocol best practices for optimal caching, client understanding, and REST-like patterns
- **LLM-Optimized Tool Descriptions**: Enhanced tool descriptions with GTD context, usage examples, and behavioral annotations for optimal Claude Desktop understanding and interaction
- **Pre-configured GTD Workflow Prompts**: Ready-to-use prompt templates for weekly reviews, inbox processing, project planning, and daily planning that guide Claude through proper GTD methodology
- **Context-Aware Tool Suggestions**: Intelligent tool adaptation based on user context (meeting notes vs email processing) with specialized parameter defaults and descriptions
- **Markdown Preservation**: Maintain all data in human-readable markdown format with clear version history
- **Customizable Templates**: Allow users to adapt AI suggestions to match their specific GTD implementation and preferences
