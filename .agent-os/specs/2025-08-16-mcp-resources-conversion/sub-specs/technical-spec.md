# Technical Specification: MCP Resources Conversion

## Architecture Overview

Convert three existing MCP tools to MCP resources using FastMCP's resource template system. This migration follows MCP protocol semantics where resources provide read-only data access and tools perform actions.

## Current Tool Analysis

### Existing Tools to Convert

1. **`list_gtd_files`** - Returns file listings with metadata
   - Parameters: `vault_path`, `file_type` (optional)
   - Returns: List of GTD files with metadata

2. **`read_gtd_file`** - Reads single GTD file with content parsing
   - Parameters: `vault_path`, `file_path`
   - Returns: File content with parsed tasks, frontmatter, links

3. **`read_gtd_files`** - Batch reads multiple GTD files
   - Parameters: `vault_path`, `file_type` (optional), `include_content`
   - Returns: Comprehensive content extraction from multiple files

## Resource Template Design

### Resource URI Patterns

```
gtd://{vault_path}/files                    # File listings
gtd://{vault_path}/files/{file_type}        # Filtered file listings
gtd://{vault_path}/file/{file_path}         # Single file content
gtd://{vault_path}/content                  # Batch content access
gtd://{vault_path}/content/{file_type}      # Filtered batch content
```

### Resource Template Implementation

```python
@mcp.resource_template("gtd://{vault_path}/files")
async def list_files_resource(vault_path: str) -> str:
    """List all GTD files in vault with metadata"""

@mcp.resource_template("gtd://{vault_path}/files/{file_type}")
async def list_files_filtered_resource(vault_path: str, file_type: str) -> str:
    """List GTD files filtered by type (inbox, projects, etc.)"""

@mcp.resource_template("gtd://{vault_path}/file/{file_path}")
async def read_file_resource(vault_path: str, file_path: str) -> str:
    """Read single GTD file with full content parsing"""

@mcp.resource_template("gtd://{vault_path}/content")
async def read_content_resource(vault_path: str) -> str:
    """Read all GTD files with comprehensive content extraction"""

@mcp.resource_template("gtd://{vault_path}/content/{file_type}")
async def read_content_filtered_resource(vault_path: str, file_type: str) -> str:
    """Read GTD files filtered by type with content extraction"""
```

## Implementation Details

### FastMCP Resource Annotations

All resources include proper MCP annotations:

```python
@mcp.resource_template(
    "gtd://{vault_path}/files",
    name="GTD File Listings",
    description="List GTD files in vault with metadata for file system navigation",
    readOnlyHint=True,
    idempotentHint=True
)
```

### Error Handling Strategy

- **Invalid vault paths**: Return empty result with warning message
- **Missing files**: Return structured empty response rather than errors
- **Malformed URIs**: FastMCP handles with standard error responses
- **Permission issues**: Log errors and return safe empty responses

### Data Format Consistency

Resources maintain exact same JSON response format as existing tools to ensure compatibility:

```json
{
  "files": [...],
  "metadata": {...},
  "total_count": 0
}
```

### Migration Strategy

1. **Phase 1**: Implement resource templates alongside existing tools
2. **Phase 2**: Update all tests to use resource reading
3. **Phase 3**: Remove tool implementations
4. **Phase 4**: Update documentation and examples

## Code Organization

### File Structure Changes

```
src/md_gtd_mcp/
├── server.py                 # Remove tool decorators, add resource templates
├── services/
│   ├── vault_reader.py       # Reuse existing VaultReader class
│   └── resource_handler.py   # New: Resource-specific logic
└── tests/
    ├── test_resources.py     # New: Resource testing
    └── test_tools.py         # Remove tool tests
```

### Dependency Changes

- **No new dependencies**: Uses existing FastMCP resource capabilities
- **Existing services**: Reuse VaultReader, MarkdownParser, TaskExtractor
- **Configuration**: No changes to VaultConfig system

## Performance Considerations

### Resource Access Patterns

- **Caching**: Rely on MCP client-side caching mechanisms
- **Batch Operations**: Maintain efficient batch reading for content resources
- **Memory Usage**: Stream large vault content rather than loading entirely in memory

### URI Parameter Handling

- **File Type Filtering**: Support standard GTD types (inbox, projects, next-actions, etc.)
- **Path Validation**: Sanitize file paths to prevent directory traversal
- **Encoding**: Handle special characters in vault and file paths properly

## Testing Strategy

### Resource Testing Approach

1. **Direct Resource Access**: Test resource templates with various URI patterns
2. **Data Consistency**: Verify resources return same data as original tools
3. **Error Scenarios**: Test invalid URIs, missing files, permission issues
4. **Performance**: Validate resource access performance vs. tool performance

### Migration Testing

1. **Before/After Comparison**: Ensure resource data matches tool data exactly
2. **Integration Tests**: Update existing integration scenarios to use resources
3. **Client Compatibility**: Test with Claude Desktop and other MCP clients
