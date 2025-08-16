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

## The Problem

1. **Inbox Processing Bottleneck**: GTD practitioners spend 30-60 minutes daily categorizing captured thoughts, meeting notes, and ideas. This manual process is repetitive and prone to inconsistency, leading to delayed processing and decision fatigue.

2. **Project Stagnation**: 40-60% of projects in GTD systems lack clear next actions, causing work to stall. Breaking down complex projects into actionable steps requires cognitive effort that busy professionals often defer.

3. **Ineffective Weekly Reviews**: The critical GTD weekly review process is time-consuming and often skipped. Without regular reviews, systems become cluttered with outdated information and missed opportunities.

4. **Knowledge Extraction Overhead**: Valuable insights from meeting notes, emails, and documents require manual extraction into actionable tasks, causing important items to remain buried in notes.

## Key Principles

1. **GTD Phase Integrity**: Respect the five GTD phases (Capture → Clarify → Organize → Reflect → Engage) by providing appropriate tools for each phase. Quick capture requires minimal friction, while clarification phase provides intelligent context and category suggestions.

2. **Universal Compatibility**: Support standard Obsidian markdown format (`- [ ]` tasks) as the primary interface, ensuring compatibility with existing tools like Claude Desktop and other AI assistants while maintaining optional enhanced functionality.

3. **Workflow Preservation**: Enhance existing Obsidian GTD setups without forcing users to abandon their established systems, muscle memory, or preferred folder structures.

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

### Project Management
- **Project Decomposition**: Break down high-level projects into specific, actionable next steps
- **Stall Detection**: Identify projects without recent activity or clear next actions
- **Dependency Mapping**: Recognize and highlight project dependencies and prerequisites
- **Progress Tracking**: Monitor project advancement through completed actions and milestones

### Review Automation
- **Weekly Review Generation**: Create automated summaries of completed actions, stalled projects, and upcoming priorities
- **Pattern Analysis**: Identify productivity patterns, common bottlenecks, and workflow optimization opportunities
- **Focus Recommendations**: Suggest priority areas based on project urgency, energy requirements, and available time
- **Completion Insights**: Track and analyze completion rates across different project types and contexts

### Integration & Workflow
- **Native Obsidian Integration**: Work directly with existing folder structures, tags, and linking patterns
- **MCP Protocol Support**: Enable any Claude Code-compatible AI assistant to interact with GTD systems
- **LLM-Optimized Tool Descriptions**: Enhanced tool descriptions with GTD context, usage examples, and behavioral annotations for optimal Claude Desktop understanding and interaction
- **Pre-configured GTD Workflow Prompts**: Ready-to-use prompt templates for weekly reviews, inbox processing, project planning, and daily planning that guide Claude through proper GTD methodology
- **Context-Aware Tool Suggestions**: Intelligent tool adaptation based on user context (meeting notes vs email processing) with specialized parameter defaults and descriptions
- **Interactive Processing with Elicitation**: Structured data gathering during GTD workflows using interactive prompts to ensure comprehensive capture of task details, project information, and review criteria
- **Markdown Preservation**: Maintain all data in human-readable markdown format with clear version history
- **Customizable Templates**: Allow users to adapt AI suggestions to match their specific GTD implementation and preferences
