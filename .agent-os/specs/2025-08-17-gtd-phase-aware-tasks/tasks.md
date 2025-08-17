# Tasks - GTD Phase-Aware Task Recognition and Inbox Capture

## Task Breakdown

### 1. Enhance TaskExtractor for File-Type Aware Recognition
- [x] 1.1 Write tests for file-type aware task recognition behavior
  - Test inbox files recognize ALL `- [ ]` items without #task requirement
  - Test non-inbox files maintain existing #task tag requirement
  - Test backward compatibility when no file_type parameter provided
  - Test edge cases: empty files, malformed tasks, mixed content
- [x] 1.2 Add optional file_type parameter to TaskExtractor.extract_tasks() method
- [x] 1.3 Implement inbox-specific recognition logic in TaskExtractor._parse_task_line()
  - Skip #task tag requirement when file_type="inbox"
  - Maintain existing logic for all other file types
- [x] 1.4 Update TaskExtractor._has_task_tag() to respect file_type parameter
- [x] 1.5 Verify all TaskExtractor tests pass with enhanced behavior

### 2. Update MarkdownParser Integration
- [x] 2.1 Write tests for MarkdownParser passing file_type to TaskExtractor
  - Test that detect_file_type() output is correctly passed to TaskExtractor
  - Test inbox.md files get parsed with inbox-specific task recognition
  - Test projects.md, next-actions.md maintain existing behavior
- [x] 2.2 Modify MarkdownParser.parse_file() to pass detected file_type to TaskExtractor.extract_tasks()
- [x] 2.3 Verify detect_file_type() function correctly identifies all GTD file types
- [x] 2.4 Verify all MarkdownParser integration tests pass

### 3. Implement Inbox Capture Tool
- [x] 3.1 Write tests for capture_inbox_item MCP tool functionality
  - Test successful item capture to existing inbox.md
  - Test inbox.md creation when file doesn't exist
  - Test vault path validation and error handling
  - Test atomic file operations and concurrent access
  - Test various input formats and edge cases
- [x] 3.2 Create capture_inbox_item function with @mcp.tool() decorator in server.py
  - Accept vault_path and item_text as required parameters
  - Include GTD-focused tool description and usage examples
- [x] 3.3 Implement vault validation and inbox.md file handling
  - Validate GTD structure exists or create if needed
  - Handle both existing and new inbox.md files safely
- [x] 3.4 Add atomic file writing operations for thread safety
  - Use temporary files and atomic moves for safe concurrent access
  - Handle file encoding and newline consistency
- [x] 3.5 Verify all capture_inbox_item tool tests pass

### 4. Integration Testing and MCP Resource Compatibility
- [x] 4.1 Write integration tests for MCP resources with new task recognition
  - Test ResourceHandler.get_file() with inbox files shows enhanced task parsing
  - Test ResourceHandler.get_content() maintains format compatibility
  - Test existing MCP resource URIs continue working unchanged
  - Test resource caching works correctly with new task recognition logic
- [x] 4.2 Test that ResourceHandler methods work correctly with enhanced TaskExtractor
  - Verify gtd://{vault_path}/file/gtd/inbox.md shows tasks without #task tags
  - Verify gtd://{vault_path}/file/gtd/projects.md maintains #task requirements
  - Test batch content operations maintain correct behavior per file type
- [x] 4.3 Run comprehensive regression testing
  - Execute full existing test suite to ensure no breaking changes
  - Test all existing MCP tools maintain exact same behavior
  - Verify server startup and resource registration unchanged
- [x] 4.4 Verify all integration and regression tests pass

### 5. Update Test Fixtures and Documentation
- [x] 5.1 Write comprehensive edge case tests for both recognition modes
  - Test complex inbox scenarios: mixed processed/unprocessed items
  - Test non-inbox files with various #task tag patterns
  - Test file type detection edge cases and unknown file types
- [x] 5.2 Update test fixtures to reflect new inbox behavior
  - Remove #task tags from tests/fixtures/sample_vault/gtd/inbox.md
  - Add realistic inbox content: meeting notes, quick captures, thoughts
  - Maintain existing #task patterns in projects.md and other GTD files
- [x] 5.3 Update relevant docstrings and type hints
  - Document new file_type parameter in TaskExtractor methods
  - Add GTD methodology context to tool descriptions
  - Include usage examples for capture_inbox_item tool
- [x] 5.4 Test complete GTD workflow scenarios
  - Test full capture → clarify → organize workflow
  - Verify inbox processing maintains GTD phase separation
  - Test integration with weekly review and planning workflows
- [x] 5.5 Verify all updated tests and documentation are complete

## Task Dependencies

- Task 1 must complete before Tasks 2 and 4 (enhanced TaskExtractor required)
- Task 2 can begin after Task 1.2 (MarkdownParser integration needs TaskExtractor changes)
- Task 3 can be done in parallel with Tasks 1 and 2 (independent MCP tool)
- Task 4 depends on Tasks 1, 2, and 3 (needs all components for integration testing)
- Task 5 depends on all previous tasks (final validation and documentation)

## Estimated Complexity

- **Task 1**: Medium complexity (3-4 hours) - Core logic enhancement with careful backward compatibility
- **Task 2**: Low complexity (1-2 hours) - Simple integration point modification
- **Task 3**: Medium complexity (2-3 hours) - New MCP tool with file operations and validation
- **Task 4**: High complexity (4-5 hours) - Comprehensive integration testing across all MCP resources
- **Task 5**: Medium complexity (2-3 hours) - Test fixture updates and documentation

**Total Estimate**: 12-17 hours of development time
