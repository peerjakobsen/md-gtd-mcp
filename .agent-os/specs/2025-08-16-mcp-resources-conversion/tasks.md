# Tasks - MCP Resources Conversion

## Task Breakdown

### 1. Core Resource Template Implementation
- [ ] 1.1 Write tests for ResourceHandler service with URI parsing and data consistency
  - Create `tests/test_resource_handler.py` testing URI parameter extraction
  - Test vault path and file path validation
  - Test data format consistency with existing tool responses
  - Test error handling for invalid paths and missing files
- [ ] 1.2 Implement ResourceHandler service in services/resource_handler.py
  - Implement centralized resource logic reusing existing VaultReader, MarkdownParser, TaskExtractor
  - Implement URI parsing and parameter extraction for resource templates
  - Add error handling and validation for vault paths and file paths
  - Ensure data format consistency with existing tool responses
- [ ] 1.3 Write tests for resource templates with comprehensive URI pattern matching
  - Create `tests/test_resources.py` with coverage for all five resource templates
  - Test URI pattern matching for `gtd://{vault_path}/files`, `gtd://{vault_path}/file/{path}`, `gtd://{vault_path}/content`
  - Test filtered variants with file type parameters
  - Verify resource annotations (readOnlyHint, idempotentHint) are properly applied
  - Test error handling for invalid URIs and resource access scenarios
- [ ] 1.4 Implement resource templates in server.py with proper annotations
  - Add five resource template decorators with readOnlyHint=True, idempotentHint=True
  - Implement resource handler integration for each template
  - Add comprehensive docstrings with GTD context and usage examples
  - Ensure FastMCP resource registration and URI routing
- [ ] 1.5 Write tests for integration scenarios and migration compatibility
  - Test resource access through MCP client simulation
  - Test data consistency between tools and resources during migration
  - Test performance with various vault sizes and configurations
  - Test filtered resource variants work correctly with file type parameters
- [ ] 1.6 Update integration tests to use resources instead of tools
  - Modify existing integration tests in `tests/test_integration.py` to use resources
  - Update test scenarios to access `gtd://` URIs for read operations
  - Verify integration test suite passes with resource-based approach
  - Maintain test coverage for all GTD workflow scenarios
  - Ensure backwards compatibility verification during transition
- [ ] 1.7 Write tests for tool removal and cleanup verification
  - Test that removed tools are no longer accessible
  - Test that all functionality is preserved through resources
  - Test server instructions reflect resource-based access patterns
- [ ] 1.8 Remove tool implementations and update server documentation
  - Remove `list_gtd_files`, `read_gtd_file`, and `read_gtd_files` tool decorators from server.py
  - Clean up tool-specific code that's no longer needed
  - Update server docstrings and meta information to reflect resource-based approach
  - Verify no remaining references to removed tools exist in codebase
  - Update server instructions to describe resource access patterns
- [ ] 1.9 Verify all tests pass with complete resource implementation

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
