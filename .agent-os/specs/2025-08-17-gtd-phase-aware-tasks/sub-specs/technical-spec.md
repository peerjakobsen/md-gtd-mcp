# Technical Specification

This is the technical specification for the spec detailed in @.agent-os/specs/2025-08-17-gtd-phase-aware-tasks/spec.md

## Technical Requirements

### File-Type Aware Task Recognition

- **TaskExtractor.extract_tasks() Enhancement**: Add optional `file_type` parameter to enable different parsing behavior based on GTD file type
- **Inbox Recognition Logic**: For `file_type="inbox"`, recognize ALL `- [ ]` checkbox items as tasks without requiring #task tags
- **Non-Inbox Recognition Logic**: For all other file types (projects, next-actions, waiting-for, someday-maybe, context), maintain existing #task tag requirement
- **Backward Compatibility**: Default behavior (no file_type specified) maintains current #task tag requirement for all existing code

### MCP Resource Integration

- **ResourceHandler Compatibility**: Ensure TaskExtractor changes work seamlessly with existing MCP resource templates (gtd://{vault_path}/file/{file_path}, gtd://{vault_path}/content)
- **MarkdownParser Integration**: Update MarkdownParser.parse_file() to pass detected file_type to TaskExtractor.extract_tasks()
- **File Type Detection**: Leverage existing detect_file_type() function to determine appropriate parsing behavior

### Inbox Capture Tool

- **MCP Tool Implementation**: Create new @mcp.tool() decorator function `capture_inbox_item` for adding items to inbox
- **Parameter Requirements**: Accept vault_path (string) and item_text (string) as required parameters
- **File Operations**: Append new items to inbox.md as simple `- [ ] {item_text}` format without metadata
- **Error Handling**: Validate vault structure exists, create inbox.md if missing, handle file permissions and encoding issues
- **Atomic Operations**: Ensure file writes are atomic to prevent corruption during concurrent access

### Testing Strategy

- **TaskExtractor Unit Tests**: Test both inbox and non-inbox file type behaviors with comprehensive edge cases
- **Integration Tests**: Verify MCP resource reading works correctly with new task recognition logic
- **Regression Tests**: Ensure all existing functionality continues working exactly as before
- **Inbox Capture Tests**: Test the new MCP tool with various input scenarios and error conditions

### Performance Considerations

- **Minimal Overhead**: File type detection should add negligible performance impact to existing parsing operations
- **Memory Efficiency**: No additional memory allocation required for enhanced task recognition
- **Caching Compatibility**: New logic must work with existing MCP resource caching mechanisms
