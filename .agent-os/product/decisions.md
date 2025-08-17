# Decisions

## Decision Log

### D001: Product Planning and Agent OS Integration
- **Status**: Decided
- **Date**: 2025-08-10
- **Category**: Architecture
- **Stakeholders**: Product Owner

**Context**: Need to establish foundation for MCP server development with clear product vision, technical architecture, and development roadmap.

**Alternatives**:
1. Start coding immediately with minimal planning
2. Create comprehensive Agent OS documentation structure
3. Use lightweight documentation approach

**Decision**: Implement full Agent OS product planning structure with mission, tech-stack, roadmap, and decision logging.

**Rationale**:
- Provides clear direction for AI-assisted development
- Enables effective agent consumption of product requirements
- Establishes decision audit trail for future reference
- Aligns with Agent OS best practices for structured development

**Consequences**:
- Positive: Clear product vision and development path
- Positive: Enables effective AI agent assistance throughout development
- Positive: Provides framework for tracking progress and decisions
- Neutral: Additional upfront documentation effort

### D002: FastMCP as Core Framework
- **Status**: Decided
- **Date**: 2025-08-10
- **Category**: Technology
- **Stakeholders**: Development Team

**Context**: Need to select MCP server framework for building GTD workflow automation.

**Alternatives**:
1. FastMCP - Python-based MCP server framework
2. Custom MCP implementation from scratch
3. Node.js based MCP server

**Decision**: Use FastMCP as the core framework for MCP server development.

**Rationale**:
- Aligns with Agent OS Python-first technology standards
- Provides proven MCP protocol implementation
- Reduces development complexity and time-to-market
- Strong community support and documentation

**Consequences**:
- Positive: Faster development with proven framework
- Positive: Consistent with technology stack preferences
- Positive: Access to FastMCP community and resources
- Negative: Framework dependency and potential limitations

### D003: MCP Best Practices for LLM Integration
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Architecture
- **Stakeholders**: Development Team, Product Owner

**Context**: Research into FastMCP best practices revealed specific patterns and techniques needed to ensure optimal LLM (Claude Desktop) understanding and usage of MCP servers. Standard functional implementation is insufficient for effective AI interaction.

**Alternatives**:
1. Implement basic MCP tools with minimal descriptions
2. Focus only on functional capabilities without LLM optimization
3. Implement comprehensive FastMCP best practices for LLM interaction

**Decision**: Implement comprehensive FastMCP best practices including enhanced tool descriptions, MCP prompts, annotations, meta information, and interactive features.

**Rationale**:
- LLMs require detailed context and usage guidance to effectively use tools
- FastMCP provides proven patterns (tool descriptions, prompts, annotations) for LLM interaction
- GTD methodology benefits from structured prompts and guided workflows
- Proper tool organization and naming improves discoverability and usage

**Implementation Details**:
- Tool descriptions enhanced with GTD context and usage examples
- Behavioral annotations (readOnlyHint, destructiveHint, idempotentHint) guide LLM behavior
- Meta information indicates GTD phases and usage frequency
- Pre-configured prompts for common GTD workflows (weekly review, inbox processing)
- Tool transformation patterns for context-specific adaptations

**Consequences**:
- Positive: Optimal Claude Desktop integration and user experience
- Positive: Structured approach to GTD workflow automation
- Positive: Leverages FastMCP framework capabilities effectively
- Positive: Provides foundation for advanced AI-assisted GTD features
- Neutral: Additional implementation complexity and documentation requirements
- Negative: Increased initial development effort for comprehensive descriptions and prompts

### D004: Task Recognition Strategy
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Architecture
- **Stakeholders**: Development Team, End Users

**Context**: Real-world testing with Claude Desktop revealed that requiring #task tags for all task recognition creates incompatibility with standard Obsidian workflows and existing AI tools that naturally create tasks in standard markdown format.

**Alternatives**:
1. Maintain strict #task tag requirement for all tasks
2. Recognize standard Obsidian format (`- [ ]`) as primary with optional #task support
3. Support both formats equally with configuration options

**Decision**: Recognize standard Obsidian task format (`- [ ]` / `- [x]`) as primary method, with #task tags as optional metadata enhancement.

**IMPORTANT**: This decision is partially superseded by Decision D006 for inbox files. D006 requires that inbox files NEVER have #task tags during capture phase. This decision (D004) applies only to non-inbox GTD files (projects.md, next-actions.md, etc.) where #task tags remain required for Obsidian Tasks plugin compatibility.

**Rationale**:
- Standard Obsidian format is widely adopted and expected by users
- Claude Desktop and other AI tools naturally create tasks in standard format
- #task requirement creates unnecessary friction and incompatibility
- Optional #task support maintains enhanced functionality when desired
- Aligns with principle of least surprise for Obsidian users

**Implementation Details**:
- Remove mandatory #task tag requirement from TaskExtractor._has_task_tag()
- Primary task detection based on `- [ ]` and `- [x]` patterns
- #task tags treated as optional metadata for enhanced categorization
- Maintain backward compatibility with existing #task tagged content

**Consequences**:
- Positive: Better compatibility with Claude Desktop and AI assistants
- Positive: Follows standard Obsidian conventions users expect
- Positive: Reduces friction for quick task capture
- Positive: Maintains optional enhanced functionality
- Neutral: Requires updating existing task detection logic
- Negative: May initially detect more items as tasks than intended

### D005: GTD Phase Separation for Context Assignment
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Methodology
- **Stakeholders**: Product Owner, End Users

**Context**: Analysis of Claude Desktop's natural task creation revealed that contexts (@home, @computer, etc.) are not added during initial capture, which aligns with proper GTD methodology where contexts are assigned during the Clarify phase, not Capture phase.

**Alternatives**:
1. Require contexts on all tasks at capture time
2. Make contexts optional but encourage during capture
3. Strictly separate Capture (no contexts required) and Clarify (contexts assigned) phases

**Decision**: Implement strict GTD phase separation where Capture phase requires no contexts and Clarify phase guides context assignment.

**Rationale**:
- Follows David Allen's original GTD methodology correctly
- Reduces friction during quick capture (key GTD principle)
- Aligns with how AI assistants naturally create inbox items
- Enables proper workflow from Capture → Clarify → Organize → Reflect → Engage
- Provides opportunity for intelligent context suggestion during Clarify

**Implementation Details**:
- Inbox capture tools accept tasks without context requirements
- Separate "process_inbox" tool guides Clarify phase with context suggestions
- Clear tool descriptions indicate which GTD phase each tool supports
- Enhanced prompts guide users through proper GTD phase transitions

**Consequences**:
- Positive: Proper GTD methodology implementation
- Positive: Reduced friction for quick capture
- Positive: Natural workflow for AI assistant integration
- Positive: Clear separation of concerns between GTD phases
- Neutral: Requires user education about GTD phase separation
- Negative: Two-step process may feel more complex initially

### D006: Inbox Task Tag Separation - Pure Capture Phase
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Architecture
- **Stakeholders**: Development Team, End Users

**Context**: Analysis of GTD methodology revealed that the inbox should be a pure capture zone where items don't yet have task metadata. Current implementation inconsistently requires #task tags in inbox, violating the principle that capture should be friction-free and clarification should be a separate conscious step.

**Alternatives**:
1. Continue current mixed approach with some inbox items having #task tags
2. Require all inbox items to have #task tags for consistency
3. Implement pure capture phase - inbox items NEVER have #task tags until clarified

**Decision**: Implement pure GTD capture phase where inbox items NEVER have #task tags. The #task tag is only added during the Clarify phase when items are consciously processed and moved to appropriate GTD files.

**Rationale**:
- Aligns perfectly with David Allen's GTD methodology (capture first, clarify later)
- Creates clear distinction between captured and clarified items
- Enables true friction-free capture without metadata decisions
- #task tag becomes a processing status indicator (processed vs unprocessed)
- Better Obsidian Tasks plugin integration (only queries truly actionable items)
- Matches natural AI assistant behavior (dumps thoughts without immediate categorization)

**Implementation Details**:
- TaskExtractor becomes file-type aware:
  - Inbox files: Recognize ALL `- [ ]` items without #task requirement
  - Other GTD files: Maintain #task requirement for Obsidian Tasks compatibility
- New `clarify_inbox_item()` MCP tool adds #task tag during processing
- Test fixtures updated to remove #task from inbox.md
- Processing workflow: Capture (no #task) → Clarify (add #task) → Organize (move to appropriate file)

**Consequences**:
- Positive: True GTD methodology implementation with proper phase separation
- Positive: Clear processing status indication via #task presence
- Positive: Friction-free capture experience
- Positive: Better integration with Obsidian Tasks plugin (cleaner task queries)
- Positive: Natural workflow for AI assistant collaboration
- Neutral: Requires updating existing TaskExtractor logic and test fixtures
- Negative: May require user education about new inbox behavior

### D007: Convert Read-Only Operations to MCP Resources
- **Status**: Decided
- **Date**: 2025-08-16 (Proposed), 2025-08-17 (Implemented)
- **Category**: Architecture
- **Stakeholders**: Development Team, Product Owner

**Context**: Current implementation uses MCP tools for read-only file operations (list_gtd_files, read_gtd_file, read_gtd_files). Analysis of MCP protocol documentation reveals that these operations should be resources rather than tools.

**Alternatives**:
1. Keep current tool-based implementation
2. Convert to resources following MCP protocol best practices
3. Hybrid approach with both tools and resources

**Decision**: Convert read-only file operations to MCP resources using resource templates, maintaining tools only for write operations.

**Rationale - Benefits of Resources for Read-Only Operations**:
- **Semantic clarity**: Resources explicitly communicate that operations are read-only and stateless, making the API more self-documenting
- **Caching optimization**: Resources are designed with caching in mind; clients can implement caching strategies since resources are guaranteed to be idempotent
- **Simpler client implementation**: For simple read operations, resources provide a straightforward pattern without worrying about side effects
- **Better separation of concerns**: Resources cleanly separate data retrieval from actions, making architecture more maintainable
- **Standardized patterns**: Resources follow REST-like conventions that developers are familiar with
- **MCP protocol compliance**: Resources are semantically correct for file reading operations
- **Better LLM understanding**: Resources support readOnlyHint annotation for improved AI assistant interaction

**Trade-offs Acknowledged**:
- **Limited flexibility**: Resources are more rigid for complex queries with multiple parameters or dynamic filtering
- **Potential duplication**: Might need both resources and tools for similar functionality if complex queries are required later
- **Less discoverable parameters**: Tools provide richer parameter schemas while resources have simpler URI-based parameters

**Implementation Details**:
- Convert list_gtd_files to resource template: `gtd://{vault_path}/files`
- Add filtered variant: `gtd://{vault_path}/files/{file_type}`
- Convert read_gtd_file to resource template: `gtd://{vault_path}/file/{file_path}`
- Convert read_gtd_files to resource template: `gtd://{vault_path}/content`
- Add filtered content variant: `gtd://{vault_path}/content/{file_type}`
- Add resource annotations: readOnlyHint: true, idempotentHint: true
- Update tests to use resource reading instead of tool calling

**Consequences**:
- Positive: Semantically correct use of MCP protocol
- Positive: Better LLM understanding through readOnlyHint annotations
- Positive: Improved caching and performance characteristics
- Positive: More intuitive URI-based access patterns
- Positive: Follows REST-like design principles
- Neutral: Requires updating existing implementation and tests
- Negative: Breaking change for current tool-based clients
- Negative: Additional implementation effort for resource templates

**Outcome**:
Implementation successfully completed with all 5 resource templates functioning correctly:
- `gtd://{vault_path}/files` - File listings
- `gtd://{vault_path}/files/{file_type}` - Filtered file listings
- `gtd://{vault_path}/file/{file_path}` - Single file content
- `gtd://{vault_path}/content` - Batch content access
- `gtd://{vault_path}/content/{file_type}` - Filtered batch content

Only write operations remain as tools (setup_gtd_vault), establishing clean separation between read operations (resources) and write operations (tools). All tests updated and passing with resource-based approach.

### D008: Use MCP Prompts for LLM-Powered GTD Workflows
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Architecture
- **Stakeholders**: Development Team, Product Owner, End Users

**Context**: Initial roadmap considered implementing LLM capabilities within the MCP server requiring API access to Anthropic, OpenAI, or AWS Bedrock. This creates barriers for average Claude Desktop users who would need to configure API keys to use GTD automation features.

**Alternatives**:
1. Implement LLM processing within MCP server (requires API keys)
2. Use MCP prompts to guide Claude Desktop's existing LLM capabilities
3. Hybrid approach with both server-side and client-side LLM features

**Decision**: Use MCP prompts to orchestrate GTD workflows through Claude Desktop's LLM intelligence, eliminating server-side LLM API requirements.

**Rationale**:
- MCP prompts are designed to guide LLM clients through complex workflows
- Leverages Claude Desktop's existing intelligence without additional API costs
- Removes barrier of API key configuration for average users
- Keeps MCP server lightweight and focused on data/actions
- Follows MCP protocol best practices for workflow orchestration
- Enables sophisticated GTD reasoning without server complexity
- Claude Desktop naturally handles multi-step reasoning and decision-making

**Implementation Details**:
- Design prompts for core GTD workflows:
  - `inbox_clarification` - Analyze and categorize inbox items
  - `weekly_review` - Structure comprehensive weekly review process
  - `project_decomposition` - Break projects into actionable next steps
  - `daily_planning` - Prioritize tasks based on context and energy
  - `stall_detection` - Identify and address stalled projects
  - `context_switching` - Suggest tasks for current context
- Prompts accept GTD state as arguments (inbox items, projects, contexts)
- Return structured instructions for Claude Desktop to follow
- Guide Claude to use appropriate resources (read operations) and tools (write operations)
- Implement proper GTD methodology through guided reasoning

**Consequences**:
- Positive: Zero API key requirements for end users
- Positive: Leverages Claude Desktop's full LLM capabilities
- Positive: Lightweight server focused on file operations
- Positive: Natural workflow orchestration through prompts
- Positive: Accessible to all Claude Desktop users
- Positive: Follows MCP protocol design principles
- Positive: Enables sophisticated GTD automation democratically
- Neutral: Requires learning MCP prompt patterns and GTD methodology integration
- Negative: Processing happens client-side rather than server-optimized environment

### D009: SOP-Enhanced Prompts for Context-Aware GTD Workflows
- **Status**: Decided
- **Date**: 2025-08-16
- **Category**: Feature Design
- **Stakeholders**: Development Team, Professional Users, Enterprise Customers

**Context**: Generic GTD prompts work well for general workflows but lack context for organization-specific procedures. Professional users need GTD workflows that incorporate their company's standard operating procedures (SOPs) for activities like 1:1 meetings, sales processes (MEDDPICC), reporting cycles, and other business-specific workflows.

**Alternatives**:
1. Keep prompts generic and rely on users to manually incorporate SOPs
2. Build SOPs into prompt templates with complex project folder structures
3. Use simple SOP linking with single projects.md file for easy maintenance
4. Create SOP-specific tools rather than enhancing prompts

**Decision**: Implement SOP-enhanced prompts using simple project-SOP linking via metadata in a single projects.md file, with SOPs stored as separate markdown files in GTD/SOPs/ folder.

**Rationale**:
- Enables context-aware workflows for professional and enterprise users
- Maintains simplicity with single projects.md file approach
- Users control SOP content directly in Obsidian for full customization
- MCP prompts can dynamically incorporate relevant SOPs during processing
- Bridges gap between generic GTD and organization-specific procedures
- Supports enterprise adoption without complexity overhead
- SOPs are reusable across multiple projects
- Follows GTD principle of reducing friction and cognitive overhead

**Implementation Details**:
- Single `projects.md` file contains all projects with optional SOP references
- Project metadata format: `sop: <sop-name>` to link to relevant procedure
- SOPs stored in `GTD/SOPs/` folder as markdown files (e.g., MEDDPICC.md, 1-1-meetings.md)
- MCP prompts read project SOPs and incorporate procedures into workflow guidance
- SOP template creation tool provides starter templates for common procedures
- SOP discovery system suggests relevant SOPs based on project patterns
- Users maintain full control over SOP content through direct Obsidian editing

**Standard SOP Template Structure**:
All SOPs follow a standardized template with GTD-integrated sections to ensure reliable parsing and application by MCP prompts:

1. **GTD Clarification Questions** - Standard questions for determining actionability, successful outcomes, next physical actions, required contexts (@home, @office, @calls), time estimates, and energy levels
2. **Project Decomposition Template** - Standard subtasks for this type of work, dependencies to check, and common blockers to anticipate
3. **Context Assignment Rules** - Default GTD contexts for this work type, context-specific considerations, and time-of-day preferences
4. **Review Checkpoints** - What to check daily, weekly, and at key milestones for this type of project
5. **Success Criteria** - Definition of done, quality gates, and deliverables checklist
6. **Common Patterns** - Typical workflow sequence, best practices, and integration points with other systems
7. **Anti-patterns to Avoid** - Common mistakes, warning signs of going off-track, and failure modes to prevent

This structure ensures SOPs are actionable workflow guides rather than passive documentation, enabling MCP prompts to systematically apply organization-specific procedures while maintaining proper GTD methodology.

**Example SOPs**:
- `1-1-meetings.md` - Manager 1:1 meeting structure and follow-up patterns
- `MEDDPICC.md` - Sales opportunity qualification methodology
- `monthly-reports.md` - Recurring business report templates and requirements
- `career-development.md` - Employee growth discussion frameworks
- `code-review.md` - Technical review process and quality gates
- `incident-response.md` - Issue handling and escalation procedures

**Consequences**:
- Positive: Enables organization-specific GTD implementations
- Positive: Supports enterprise and professional use cases
- Positive: Maintains user control over procedures and content
- Positive: Creates reusable workflow patterns across projects
- Positive: Simple structure reduces maintenance overhead
- Positive: Natural fit with GTD weekly review processes
- Neutral: Requires SOP creation and maintenance by users
- Neutral: Can evolve to more complex structures if needed
- Negative: Additional implementation complexity for SOP-prompt integration

### D010: Hybrid Tool/Resource Architecture Pattern
- **Status**: Decided
- **Date**: 2025-08-17
- **Category**: Architecture
- **Stakeholders**: Development Team, Future Contributors

**Context**: With the successful implementation of MCP resources for read-only operations (D007), the server now uses a hybrid approach with both tools and resources. Clear guidance is needed for future development to maintain architectural consistency and help contributors choose the appropriate pattern.

**Alternatives**:
1. Establish no formal guidelines and decide case-by-case
2. Convert everything to one pattern (all tools or all resources)
3. Create clear decision criteria for when to use each pattern
4. Allow both patterns without restriction

**Decision**: Establish clear architectural guidelines for choosing between tools and resources based on operation characteristics and complexity.

**Decision Criteria**:

**Use Resources When**:
- **Simple, cacheable data** that can be identified by a URI pattern (e.g., file contents, configuration settings)
- **Read-only operations** that benefit from REST-like access patterns
- **Idempotent operations** where repeated calls return identical results
- **Data that clients might cache** for performance optimization
- **Straightforward GET-style operations** without complex processing logic

**Use Tools When**:
- **Write operations** that modify state or create/update files
- **Complex queries** requiring extensive parameters or validation rules
- **Multi-step processing operations** with business logic
- **Operations requiring rich parameter schemas** with detailed validation
- **Actions with side effects** or non-idempotent behavior

**Rationale**:
- **Semantic clarity**: Tools and resources have distinct purposes in MCP protocol
- **Performance optimization**: Resources enable better caching strategies
- **Developer experience**: Clear patterns reduce decision fatigue and improve API consistency
- **Client compatibility**: Follows MCP best practices for optimal LLM understanding
- **Maintainability**: Consistent architecture patterns are easier to maintain and extend

**Implementation Examples**:
- **Resources**: `gtd://{vault_path}/files` (file listings), `gtd://{vault_path}/file/{path}` (file content)
- **Tools**: `setup_gtd_vault` (creates files), future `process_inbox` (complex workflow), `create_project` (state modification)

**Consequences**:
- Positive: Clear architectural guidance for all future MCP server features
- Positive: Consistent API design that follows MCP protocol semantics
- Positive: Optimal performance through appropriate use of caching (resources) vs. actions (tools)
- Positive: Better LLM understanding through semantic correctness
- Neutral: Requires training new contributors on decision criteria
- Negative: May occasionally require implementing both patterns for edge cases
