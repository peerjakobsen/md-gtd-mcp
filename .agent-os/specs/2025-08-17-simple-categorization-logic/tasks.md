# Tasks - Simple Categorization Logic

## Task Breakdown

### 1. Set up prompt infrastructure and schemas
- [x] 1.1 Write tests for InboxItem, Categorization, and ItemGroup Pydantic models
- [x] 1.2 Implement base prompt schemas in prompts/schemas.py
- [x] 1.3 Create prompt package structure with __init__.py
- [x] 1.4 Write tests for prompt registration system
- [x] 1.5 Implement prompt discovery and registration mechanism
- [x] 1.6 Add FastMCP prompt decorator imports
- [x] 1.7 Verify all schema tests pass

### 2. Implement GTD static rule engine (server-side)
**Note: Following Decision D008, this provides static GTD methodology rules for MCP prompts, NOT intelligent analysis**
**Note: You can use python libraries rapidfuzz, rank_bm25 and sentence-transformers for text pattern matching. You can use them in combination **

- [x] 2.1 Write tests for GTD methodology constants and static patterns
  - Test GTD clarifying questions format and completeness
  - Test keyword pattern dictionaries structure
  - Test decision tree text generation
  - Test response schema validation helpers
- [x] 2.2 Implement GTD methodology questions and decision tree templates
  - Static GTD clarifying questions for prompt inclusion
  - Decision tree text templates for prompt context
  - Category validation rules and definitions
  - GTD phase indicators and workflow constants
- [x] 2.3 Write tests for simple keyword pattern matching
  - Test context keyword pattern dictionaries
  - Test pattern lookup functions
  - Test multiple pattern matching for overlapping contexts
  - Test pattern case-insensitivity
- [x] 2.4 Implement context keyword pattern dictionaries
  - Static keyword lists for each GTD context (@calls, @computer, etc.)
  - Simple pattern matching utilities (no LLM but ok to use python libraries rapidfuzz, rank_bm25 and sentence-transformers)
  - Context suggestion helpers based on keyword presence
  - Multiple context support for items matching several patterns
- [ ] 2.5 Write tests for time/complexity indicator patterns
  - Test keyword patterns for quick tasks (2-minute rule hints)
  - Test project complexity indicators
  - Test delegation/waiting patterns
  - Test pattern priority when multiple matches occur
- [ ] 2.6 Implement static indicator pattern collections
  - Two-minute rule keyword indicators (quick, simple, brief, etc.)
  - Project complexity indicators (implement, develop, create, etc.)
  - Delegation patterns (waiting, pending, depends, etc.)
  - Priority/urgency keywords for prompt context
- [ ] 2.7 Create GTD methodology documentation and constants
  - Document GTD decision tree logic for prompts
  - Define category descriptions and usage rules
  - Create context definitions and typical use cases
  - Generate prompt template building utilities
- [ ] 2.8 Verify all static rule engine tests pass
  - Integration tests with prompt generation
  - Validation of rule consistency
  - Performance tests for pattern matching
  - Coverage verification for all GTD methodology areas

### 3. Create core MCP prompts (Claude Desktop intelligence)
**Note: These prompts use static rules from Task 2 to guide Claude Desktop's LLM reasoning**

- [ ] 3.1 Write tests for inbox_clarification prompt generation
  - Test prompt includes GTD decision tree from rule engine
  - Test clarifying questions integration from static rules
  - Test context pattern hints inclusion
  - Test project indicator guidance
- [ ] 3.2 Implement inbox_clarification prompt with GTD template
  - Include GTD methodology questions from rule engine
  - Add decision tree text from static rules
  - Include context keyword hints for Claude's reasoning
  - Reference project indicators for multi-step detection
  - Guide Claude through confidence assessment
- [ ] 3.3 Write tests for quick_categorize prompt
  - Test streamlined decision process
  - Test integration with static rule patterns
  - Test fallback to full clarification when needed
- [ ] 3.4 Implement quick_categorize for simple items
  - Lightweight prompt for obvious categorizations
  - Use subset of static patterns for speed
  - Include escalation logic for complex items
- [ ] 3.5 Write tests for batch_process_inbox prompt
  - Test batch consistency using same static rules
  - Test grouping logic guidance for Claude
  - Test processing up to 20 items efficiently
- [ ] 3.6 Implement batch_process_inbox with grouping logic
  - Guide Claude to identify similar patterns
  - Use static indicators for grouping suggestions
  - Maintain categorization consistency across batch
- [ ] 3.7 Test prompt response formatting and JSON structure
  - Validate schema compliance with existing Pydantic models
  - Test error handling for malformed Claude responses
  - Test response parsing and validation
- [ ] 3.8 Verify all prompt tests pass
  - Integration tests with static rule engine
  - End-to-end prompt generation and validation
  - Performance testing for prompt token efficiency

### 4. Add validation and error handling
- [ ] 4.1 Write tests for input validation functions
- [ ] 4.2 Implement inbox item validation and sanitization
  - Limit item length to 500 characters
  - Remove excessive whitespace
  - Handle empty or malformed items
- [ ] 4.3 Write tests for response validation
- [ ] 4.4 Implement categorization result validation
  - Verify required fields present
  - Validate category values
  - Check confidence levels
- [ ] 4.5 Write tests for error scenarios
- [ ] 4.6 Implement error handling with proper error codes
- [ ] 4.7 Verify all validation tests pass

### 5. Integrate prompts with MCP server
- [ ] 5.1 Write tests for prompt registration in server.py
- [ ] 5.2 Register all prompts with MCP server
  - Add inbox_clarification prompt
  - Add quick_categorize prompt
  - Add batch_process_inbox prompt
- [ ] 5.3 Write tests for prompt meta information
- [ ] 5.4 Add prompt discovery meta information
  - Include GTD phase indicators
  - Add usage frequency hints
  - Create categorization tags
- [ ] 5.5 Update server instructions with prompt usage
- [ ] 5.6 Test prompt invocation through MCP protocol
- [ ] 5.7 Verify all integration tests pass

### 6. Extend static pattern recognition (server-side)
**Note: Extends Task 2 with domain-specific keyword patterns for prompt hints**

- [ ] 6.1 Write tests for email keyword pattern detection
  - Test email-specific action keywords (reply, forward, send)
  - Test email context patterns (@computer required)
  - Test urgency indicators in email content
- [ ] 6.2 Implement email-specific static keyword patterns
  - Email action verb patterns (reply, respond, send, forward)
  - Email urgency keywords (urgent, asap, deadline)
  - Email delegation patterns (cc, bcc, forward to)
- [ ] 6.3 Write tests for meeting note keyword patterns
  - Test meeting-specific keywords (discuss, agenda, follow-up)
  - Test action item extraction patterns (action, todo, assign)
  - Test meeting context hints (@office, @calls for follow-ups)
- [ ] 6.4 Implement meeting note static keyword collections
  - Meeting action keywords (follow-up, schedule, prepare)
  - Meeting outcome patterns (decided, agreed, action item)
  - Meeting delegation keywords (assigned to, responsible for)
- [ ] 6.5 Write tests for delegation keyword patterns
  - Test waiting-for indicators (waiting, pending, depends on)
  - Test delegation verbs (assigned, delegated, asked)
  - Test person name extraction hints for prompts
- [ ] 6.6 Implement delegation detection keyword patterns
  - Waiting-for trigger words (waiting, pending, blocked by)
  - Delegation action verbs (asked, assigned, delegated, requested)
  - Follow-up reminder keywords (check, follow up, remind)
- [ ] 6.7 Create extensible static pattern system
  - Pattern category framework for new domains
  - Priority ordering for overlapping pattern matches
  - Pattern composition utilities for prompt building
- [ ] 6.8 Verify all pattern recognition tests pass
  - Integration with core rule engine (Task 2)
  - Performance testing for large pattern sets
  - Validation of pattern precedence rules

### 7. Integration testing and documentation
- [ ] 7.1 Test single item categorization workflow
  - Invoke inbox_clarification with one item
  - Verify correct GTD category suggestion
  - Validate reasoning and confidence
- [ ] 7.2 Test batch processing workflow with 20 items
  - Create diverse test items
  - Verify grouping suggestions
  - Validate consistent categorization
- [ ] 7.3 Test project association workflow
  - Provide existing projects list
  - Verify items linked to relevant projects
  - Validate new project suggestions
- [ ] 7.4 Test context assignment workflow
  - Test prompts provide context keyword hints to Claude
  - Verify Claude receives static pattern guidance
  - Validate context suggestions in Claude's responses
- [ ] 7.5 Test quick categorization performance
  - Measure response time < 2 seconds
  - Verify minimal token usage
  - Validate accuracy for simple items
- [ ] 7.6 Test error recovery scenarios
  - Test with malformed JSON responses
  - Test with timeout scenarios
  - Verify graceful degradation
- [ ] 7.7 Write user documentation with GTD primer
  - Explain GTD methodology basics
  - Provide prompt usage examples
  - Create troubleshooting guide
- [ ] 7.8 Write API documentation
  - Document all prompt schemas
  - Provide response examples
  - Create integration guide
- [ ] 7.9 Create example workflows
  - Daily inbox processing
  - Weekly review preparation
  - Project planning session
- [ ] 7.10 Performance optimization
  - Minimize prompt token usage
  - Implement response caching
  - Optimize for Claude's context window

## Architecture Notes

**Key Change from Original Plan**: Following Decision D008 analysis, Tasks 2 and 6 now implement **static keyword patterns and GTD methodology rules** (server-side) rather than intelligent text analysis. The actual intelligence happens in Claude Desktop via MCP prompts (Task 3) that reference these static rules.

**Server-Side (No LLM)**: Static patterns, keyword lists, GTD methodology constants, validation rules
**Client-Side (Claude Desktop)**: Natural language understanding, confidence assessment, intelligent categorization

## Task Dependencies

- Task 1 must complete before Tasks 2 and 3 (foundational schemas)
- Task 2 can proceed independently after Task 1 (static rules only)
- Task 3 depends on Tasks 1 and 2 (needs schemas and static rules for prompt generation)
- Task 4 can proceed in parallel with Task 3
- Task 5 depends on Task 3 (needs prompts to register)
- Task 6 can proceed independently after Task 2 (extends static patterns)
- Task 7 depends on all previous tasks (final integration)

## Estimated Complexity (Revised)

- **Task 1**: Low complexity (2-3 hours) - Pydantic schemas and structure
- **Task 2**: Low-Medium complexity (2-3 hours) - Static GTD rules and patterns (simplified from intelligent analysis)
- **Task 3**: High complexity (5-6 hours) - Core prompt implementation with static rule integration
- **Task 4**: Medium complexity (2-3 hours) - Validation layer
- **Task 5**: Low complexity (2-3 hours) - Server integration
- **Task 6**: Low-Medium complexity (2-3 hours) - Static pattern extensions (simplified from intelligent analysis)
- **Task 7**: High complexity (6-8 hours) - Comprehensive testing and documentation

**Total Estimate**: 21-29 hours of development time (reduced due to simpler static approach)

## Success Criteria

- ✅ All prompts properly registered with MCP server
- ✅ 90% accurate categorization for standard inbox items
- ✅ Response time < 2 seconds for single item processing
- ✅ Batch processing handles 20 items efficiently
- ✅ Zero API key configuration required
- ✅ Clear explanations provided for all categorizations
- ✅ GTD methodology properly implemented
- ✅ All tests passing with >90% code coverage
