# Simple Categorization Logic

## Context

The MCP server needs to provide intelligent inbox categorization suggestions through MCP prompts that guide Claude Desktop's LLM intelligence, implementing Decision D008's API-free approach. This feature enables users to efficiently process their GTD inbox by leveraging Claude's reasoning capabilities without requiring external API keys.

## Summary

Implement MCP prompts that orchestrate GTD inbox processing workflows through Claude Desktop. The prompts will analyze inbox items and suggest appropriate GTD categories (Next Action, Project, Waiting For, Someday/Maybe, Reference) while respecting the GTD phase separation between Capture and Clarify.

## Approach

### Core Architecture

1. **MCP Prompt Design Pattern**
   - Use `@mcp.prompt()` decorator from FastMCP framework
   - Accept current GTD state as structured arguments (inbox items, existing projects)
   - Return structured instructions that guide Claude through GTD methodology
   - Leverage Claude's natural language understanding for intelligent categorization

2. **GTD Methodology Integration**
   - Respect Capture phase: Process items that have no #task tags (pure captures)
   - Guide Clarify phase: Add #task tags and suggest categories with reasoning
   - Follow David Allen's 2-minute rule and actionability criteria
   - Provide context-aware suggestions based on existing projects and patterns

3. **Prompt Workflow Orchestration**
   - Read inbox items using MCP resources
   - Analyze each item for actionability and complexity
   - Suggest appropriate GTD category with explanation
   - Guide context assignment (@home, @computer, @calls, @errands)
   - Recommend project associations when relevant

### Key MCP Prompts to Implement

1. **inbox_clarification**
   - Primary prompt for processing inbox items
   - Analyzes captured thoughts for actionability
   - Suggests GTD categories with reasoning
   - Guides context and project assignment

2. **quick_categorize**
   - Lightweight prompt for simple categorization
   - Fast processing for clear-cut items
   - Minimal analysis for obvious categories

3. **batch_process_inbox**
   - Handles multiple inbox items simultaneously
   - Maintains consistency across batch processing
   - Groups similar items for efficiency

### Implementation Strategy

1. **Phase 1: Core Prompt Structure**
   - Define prompt arguments schema
   - Create base categorization logic
   - Implement GTD rule engine

2. **Phase 2: Intelligence Layer**
   - Add pattern recognition for common item types
   - Implement project association suggestions
   - Create context inference logic

3. **Phase 3: User Experience**
   - Provide clear explanations for suggestions
   - Include confidence levels in categorization
   - Offer alternative suggestions when ambiguous

## User Stories

### Story 1: Basic Inbox Processing
**As a** GTD practitioner
**I want to** process my inbox items with intelligent suggestions
**So that** I can quickly clarify and organize my captured thoughts

**Acceptance Criteria:**
- Inbox items without #task tags are recognized as needing processing
- Claude suggests appropriate GTD categories for each item
- Suggestions include reasoning for the categorization
- Context assignments are recommended based on item content

### Story 2: Project Association
**As a** project manager
**I want** inbox items automatically associated with relevant projects
**So that** I maintain organized project support material

**Acceptance Criteria:**
- Claude identifies items related to existing projects
- Suggestions include project associations with confidence levels
- New project creation is suggested when appropriate
- Project outcomes are considered in categorization

### Story 3: Batch Processing Efficiency
**As a** busy professional
**I want to** process multiple inbox items at once
**So that** I can efficiently clear my inbox during dedicated processing time

**Acceptance Criteria:**
- Multiple items can be processed in a single prompt invocation
- Consistent categorization logic across batch processing
- Similar items are grouped for review
- Processing time is optimized through intelligent batching

### Story 4: Actionability Analysis
**As a** GTD practitioner
**I want** clear actionability assessments
**So that** I only track truly actionable items

**Acceptance Criteria:**
- Non-actionable items are identified (Reference, Trash)
- 2-minute rule is applied with suggestions
- Someday/Maybe items are recognized
- Clear next actions are extracted from vague items

## Capabilities

### Required Capabilities
- FastMCP prompt decorator usage
- Access to vault resources (read inbox, projects)
- GTD methodology rule implementation
- Natural language analysis through Claude

### Out of Scope
- Server-side LLM processing (violates Decision D008)
- Direct API calls to Anthropic/OpenAI
- Complex NLP models within server
- Automatic categorization without user confirmation

## Internal Dependencies

### Existing Components
- `ResourceHandler` service for reading GTD files
- `VaultReader` for accessing inbox items
- `MarkdownParser` for content extraction
- FastMCP server infrastructure

### Required Additions
- Prompt registry system
- GTD rule engine
- Categorization response schema
- Prompt argument validators

## External Dependencies

### MCP Protocol
- FastMCP 0.2+ with prompt support
- MCP client (Claude Desktop) with prompt handling
- JSON-RPC communication layer

### User Environment
- Claude Desktop for prompt execution
- Obsidian vault with GTD structure
- No API keys required (key benefit)

## Design Decisions

### Decision: Prompt-Based Intelligence
**Choice:** Use MCP prompts to guide Claude's existing intelligence
**Rationale:** Eliminates API key barriers and leverages client-side LLM
**Alternative Rejected:** Server-side categorization would require API access

### Decision: Structured Response Format
**Choice:** Return categorization as structured JSON with reasoning
**Rationale:** Enables programmatic handling while maintaining explainability
**Alternative Rejected:** Free-form text would be harder to process

### Decision: Confidence Scoring
**Choice:** Include confidence levels (high/medium/low) in suggestions
**Rationale:** Helps users understand when manual review is needed
**Alternative Rejected:** Binary decisions would hide uncertainty

## Task Breakdown

### Implementation Tasks
1. [x] Create spec directory and documentation
2. [ ] Define prompt argument schemas (S)
3. [ ] Implement inbox_clarification prompt (M)
4. [ ] Create GTD rule engine for categorization (M)
5. [ ] Add pattern recognition for common items (M)
6. [ ] Implement quick_categorize prompt (S)
7. [ ] Create batch_process_inbox prompt (M)
8. [ ] Add project association logic (M)
9. [ ] Implement context inference system (S)
10. [ ] Create confidence scoring mechanism (S)
11. [ ] Add explanation generation (S)
12. [ ] Write comprehensive tests (M)
13. [ ] Create user documentation (S)
14. [ ] Add example prompts and workflows (S)

### Testing Requirements
- Unit tests for prompt schema validation
- Integration tests with mock Claude responses
- End-to-end workflow testing
- Edge case handling (empty inbox, malformed items)
- Performance testing for batch processing

## Success Metrics

### Quantitative
- 90% of standard inbox items correctly categorized
- <2 second response time for single item processing
- Batch processing handles 20+ items efficiently
- Zero API key configuration required

### Qualitative
- Clear explanations for categorization decisions
- Intuitive prompt interactions
- Reduced friction in inbox processing
- Maintained GTD methodology integrity

## Example Interactions

### Single Item Processing
```python
@mcp.prompt()
async def inbox_clarification(
    inbox_item: str,
    existing_projects: list[str],
    common_contexts: list[str]
) -> str:
    '''
    Analyzes an inbox item and suggests GTD categorization.

    Returns structured guidance for Claude to:
    1. Assess actionability
    2. Suggest GTD category
    3. Recommend context
    4. Associate with projects
    5. Provide reasoning
    '''
```

### Claude's Response Structure
```json
{
  "item": "Schedule dentist appointment",
  "actionable": true,
  "category": "next-action",
  "suggested_text": "Call dentist to schedule appointment",
  "context": "@calls",
  "project": null,
  "confidence": "high",
  "reasoning": "Clear, single physical action requiring a phone call"
}
```

## Risk Mitigation

### Technical Risks
- **Prompt compatibility**: Test with multiple Claude Desktop versions
- **Performance at scale**: Implement batching and caching strategies
- **Error handling**: Graceful degradation when Claude unavailable

### User Experience Risks
- **Over-automation**: Maintain user control over final decisions
- **Methodology confusion**: Clear documentation of GTD principles
- **Learning curve**: Provide example workflows and templates
