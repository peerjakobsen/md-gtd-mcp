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
- Interactive features (elicitation, sampling) enable complex decision-making workflows
- Proper tool organization and naming improves discoverability and usage

**Implementation Details**:
- Tool descriptions enhanced with GTD context and usage examples
- Behavioral annotations (readOnlyHint, destructiveHint, idempotentHint) guide LLM behavior
- Meta information indicates GTD phases and usage frequency
- Pre-configured prompts for common GTD workflows (weekly review, inbox processing)
- Tool transformation patterns for context-specific adaptations
- Interactive elicitation for structured data gathering during GTD processes

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
