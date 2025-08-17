# Tasks - Simple Categorization Logic

## Task Breakdown

### 1. Set up prompt infrastructure and schemas
- [ ] 1.1 Write tests for InboxItem, Categorization, and ItemGroup Pydantic models
- [ ] 1.2 Implement base prompt schemas in prompts/schemas.py
- [ ] 1.3 Create prompt package structure with __init__.py
- [ ] 1.4 Write tests for prompt registration system
- [ ] 1.5 Implement prompt discovery and registration mechanism
- [ ] 1.6 Add FastMCP prompt decorator imports
- [ ] 1.7 Verify all schema tests pass

### 2. Implement GTD rule engine
- [ ] 2.1 Write tests for GTDRuleEngine actionability detection
- [ ] 2.2 Implement actionability questions and decision tree
- [ ] 2.3 Write tests for context pattern matching
- [ ] 2.4 Implement context inference patterns (@home, @computer, @calls)
- [ ] 2.5 Write tests for 2-minute rule detection
- [ ] 2.6 Implement project indicator patterns
- [ ] 2.7 Create rule engine documentation with GTD methodology
- [ ] 2.8 Verify all rule engine tests pass

### 3. Create core MCP prompts
- [ ] 3.1 Write tests for inbox_clarification prompt generation
- [ ] 3.2 Implement inbox_clarification prompt with GTD template
  - Include actionability assessment logic
  - Add categorization decision tree
  - Implement project association suggestions
  - Create confidence scoring mechanism
- [ ] 3.3 Write tests for quick_categorize prompt
- [ ] 3.4 Implement quick_categorize for simple items
- [ ] 3.5 Write tests for batch_process_inbox prompt
- [ ] 3.6 Implement batch_process_inbox with grouping logic
  - Add similarity detection for related items
  - Implement efficient batch processing up to 20 items
  - Create item grouping suggestions
- [ ] 3.7 Test prompt response formatting and JSON structure
- [ ] 3.8 Verify all prompt tests pass

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

### 6. Implement pattern recognition
- [ ] 6.1 Write tests for email pattern detection
- [ ] 6.2 Implement email-specific categorization patterns
- [ ] 6.3 Write tests for meeting note patterns
- [ ] 6.4 Implement meeting note analysis logic
- [ ] 6.5 Write tests for delegation patterns
- [ ] 6.6 Implement task delegation detection
- [ ] 6.7 Create extensible pattern system for future additions
- [ ] 6.8 Verify all pattern recognition tests pass

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
  - Process items requiring different contexts
  - Verify appropriate context suggestions
  - Validate context inference accuracy
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

## Task Dependencies

- Task 1 must complete before Tasks 2 and 3 (foundational schemas)
- Task 2 can proceed independently after Task 1
- Task 3 depends on Tasks 1 and 2 (needs schemas and rules)
- Task 4 can proceed in parallel with Task 3
- Task 5 depends on Task 3 (needs prompts to register)
- Task 6 can proceed independently after Task 2
- Task 7 depends on all previous tasks (final integration)

## Estimated Complexity

- **Task 1**: Low complexity (2-3 hours) - Pydantic schemas and structure
- **Task 2**: Medium complexity (3-4 hours) - GTD methodology encoding
- **Task 3**: High complexity (5-6 hours) - Core prompt implementation
- **Task 4**: Medium complexity (2-3 hours) - Validation layer
- **Task 5**: Low complexity (2-3 hours) - Server integration
- **Task 6**: Medium complexity (3-4 hours) - Pattern recognition
- **Task 7**: High complexity (6-8 hours) - Comprehensive testing and documentation

**Total Estimate**: 23-31 hours of development time

## Success Criteria

- ✅ All prompts properly registered with MCP server
- ✅ 90% accurate categorization for standard inbox items
- ✅ Response time < 2 seconds for single item processing
- ✅ Batch processing handles 20 items efficiently
- ✅ Zero API key configuration required
- ✅ Clear explanations provided for all categorizations
- ✅ GTD methodology properly implemented
- ✅ All tests passing with >90% code coverage
