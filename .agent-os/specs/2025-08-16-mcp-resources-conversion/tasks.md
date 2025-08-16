# Tasks - MCP Resources Conversion

## Task Breakdown

### 1. Core Resource Template Implementation
- [x] 1.1 Write tests for ResourceHandler service with URI parsing and data consistency
  - Create `tests/test_resource_handler.py` testing URI parameter extraction
  - Test vault path and file path validation
  - Test data format consistency with existing tool responses
  - Test error handling for invalid paths and missing files
- [x] 1.2 Implement ResourceHandler service in services/resource_handler.py
  - Implement centralized resource logic reusing existing VaultReader, MarkdownParser, TaskExtractor
  - Implement URI parsing and parameter extraction for resource templates
  - Add error handling and validation for vault paths and file paths
  - Ensure data format consistency with existing tool responses
- [x] 1.3 Write tests for resource templates with comprehensive URI pattern matching
  - Create `tests/test_resources.py` with coverage for all five resource templates
  - Test URI pattern matching for `gtd://{vault_path}/files`, `gtd://{vault_path}/file/{path}`, `gtd://{vault_path}/content`
  - Test filtered variants with file type parameters
  - Verify resource annotations (readOnlyHint, idempotentHint) are properly applied
  - Test error handling for invalid URIs and resource access scenarios/
- [x] 1.4 Implement resource templates in server.py with proper annotations
  - Add five resource template decorators with readOnlyHint=True, idempotentHint=True
  - Implement resource handler integration for each template
  - Add comprehensive docstrings with GTD context and usage examples
  - Ensure FastMCP resource registration and URI routing
- [x] 1.5 Write tests for integration scenarios and migration compatibility
  - Test resource access through MCP client simulation
  - Test data consistency between tools and resources during migration
  - Test performance with various vault sizes and configurations
  - Test filtered resource variants work correctly with file type parameters
- [x] 1.6 Update integration tests to use resources instead of tools
  - Modify existing integration tests in `tests/test_integration.py` to use resources
  - Update test scenarios to access `gtd://` URIs for read operations
  - Verify integration test suite passes with resource-based approach
  - Maintain test coverage for all GTD workflow scenarios
  - Ensure backwards compatibility verification during transition
- [ ] 1.7 Write comprehensive tests for tool removal and cleanup verification
  - Test that removed tools (`read_gtd_file`, `list_gtd_files`, `read_gtd_files`) are no longer accessible via MCP protocol
  - Test that implementation functions are either removed or properly refactored for resource use
  - Test that all functionality is preserved through resources with identical data formats
  - Test server instructions reflect resource-based access patterns
  - Verify no orphaned imports remain in the codebase after cleanup
  - Test error scenarios for removed tools return appropriate "tool not found" responses
- [ ] 1.8 Remove tool implementations and perform comprehensive server cleanup
  **Server.py cleanup:**
  - Remove `@mcp.tool()` decorators for `list_gtd_files`, `read_gtd_file`, and `read_gtd_files` (lines 278, 292, 472)
  - Evaluate whether to keep *_impl functions for resource handlers or refactor into ResourceHandler service
  - Remove tool wrapper functions that only call implementation functions
  - Clean up imports that are no longer needed after tool removal
  - Update module docstrings and meta information to reflect resource-based architecture
  **Test file comprehensive cleanup (4 files with 100+ tool references):**
  - **test_server.py**: Remove/refactor TestReadGTDFile, TestListGTDFiles, TestReadGTDFiles classes (lines 285-1326)
  - **test_integration.py**: Update 30+ test scenarios to use resource URIs instead of tool calls
  - **test_error_recovery.py**: Convert 20+ error tests to resource-based error scenarios
  - **test_performance.py**: Update performance benchmarks to measure resource access instead of tool calls
  - Update all imports from `*_impl` functions to resource access methods
  - Convert test assertions to validate resource responses instead of tool returns
  **Documentation updates:**
  - Update server instructions to describe resource access patterns for Claude Desktop
  - Remove tool descriptions from docstrings and replace with resource URI examples
  - Update CLAUDE.md to reflect resource-based approach
- [ ] 1.9 Verify complete migration and test suite stability
  - Run full test suite with pytest to ensure all tests pass after cleanup
  - Use grep/search to verify no remaining references to removed tools exist in codebase
  - Check that VaultReader service methods remain functional and unchanged
  - Validate that integration tests cover all GTD workflow scenarios using resources
  - Performance validation comparing resource access vs previous tool performance
  - Verify MCP protocol compliance with resource-only read operations
  - Test server startup and resource registration without removed tools

### 2. Documentation and Validation
- [ ] 2.1 Write documentation tests for resource URI examples and usage patterns
- [ ] 2.2 Update server instructions to describe resource-based access for Claude Desktop
- [ ] 2.3 Performance validation - benchmark resource vs tool access performance
- [ ] 2.4 Client compatibility testing with Claude Desktop and other MCP clients
- [ ] 2.5 Final integration verification with complete test suite execution

## Implementation Notes

**TDD Approach**: Each major task starts with writing tests to define expected behavior before implementation.

**Focus**: This specification implements only Task 1 (Core Resource Template Implementation) as the primary deliverable. Task 2 provides additional validation and documentation updates.

**Dependencies**: Uses existing VaultReader, MarkdownParser, and TaskExtractor services without modification.

**Protocol Compliance**: Follows MCP resource template patterns and FastMCP best practices throughout implementation.

## Cleanup Scope Analysis

### Files Requiring Changes
- **server.py**: 6 functions to remove/refactor (3 tools + 3 implementations)
- **test_server.py**: 3 test classes, ~50 test methods
- **test_integration.py**: 30+ integration scenarios
- **test_error_recovery.py**: 20+ error handling tests
- **test_performance.py**: Performance benchmarks for all three tools

### Migration Strategy
1. **Parallel Implementation**: Implement resources alongside existing tools initially
2. **Incremental Test Migration**: Update tests file-by-file to use resources
3. **Validation Phase**: Ensure data consistency between tools and resources
4. **Tool Removal**: Remove tool decorators once all tests pass with resources
5. **Implementation Cleanup**: Decide whether to keep *_impl functions for resource handlers
6. **Final Verification**: Complete test suite validation and performance comparison

### Critical Success Factors
- **Data Format Consistency**: Resources must return identical JSON structure as tools
- **Error Handling Preservation**: All error scenarios must work with resources
- **Performance Maintenance**: Resource access should not degrade performance
- **Test Coverage**: 100% of existing functionality must be covered by resource tests
