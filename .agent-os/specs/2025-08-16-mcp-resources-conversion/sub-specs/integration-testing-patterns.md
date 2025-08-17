# Integration Testing Patterns for MCP Resources Conversion

## Context

This document captures specific testing patterns and validation strategies for converting MCP tools to resources. These patterns address the unique challenges of migration from tool-based to resource-based access while maintaining protocol compliance and data safety.

## Core Resource Testing Principles

### 1. Test Resource URI Pattern Matching and Parameter Extraction

**Pattern**: Validate that resource templates correctly parse URIs and extract parameters.

```python
def test_resource_uri_pattern_matching(self) -> None:
    """Test resource URI patterns correctly extract vault_path and file_path parameters."""
    # Test basic patterns
    vault_path = "test_vault"
    file_path = "GTD/inbox.md"

    # Test files listing resource
    files_uri = f"gtd://{vault_path}/files"
    # Validate URI parsing extracts vault_path correctly

    # Test single file resource
    file_uri = f"gtd://{vault_path}/file/{file_path}"
    # Validate URI parsing extracts both vault_path and file_path

    # Test filtered variants
    filtered_uri = f"gtd://{vault_path}/files/inbox"
    # Validate file_type filtering parameter extraction
```

**Why**: Resource templates depend on correct URI parsing. Testing this early prevents parameter extraction failures.

### 2. Validate Resource-Tool Data Format Consistency

**Pattern**: Ensure resources return identical data formats to the tools they replace.

```python
def test_tool_resource_data_consistency(self) -> None:
    """Verify resources return identical data to tools they replace."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_sample_vault(vault_path)

        # Get data from original tool (before removal)
        tool_result = list_gtd_files(str(vault_path))

        # Get data from new resource
        resource_result = access_resource(f"gtd://{vault_path}/files")

        # Validate exact format match
        assert tool_result == json.loads(resource_result)
        assert "files" in resource_result
        assert "metadata" in resource_result
        assert "total_count" in resource_result
```

**Critical**: Resource migration must maintain perfect backward compatibility for existing clients.

### 3. Test Resource Annotations and MCP Protocol Compliance

**Pattern**: Validate that resource annotations are properly applied and understood by MCP clients.

```python
def test_resource_annotations_compliance(self) -> None:
    """Test resource annotations (readOnlyHint, idempotentHint) are properly set."""
    # Test resource registration includes proper annotations
    resource_meta = get_resource_metadata("gtd://{vault_path}/files")

    assert resource_meta.readOnlyHint is True
    assert resource_meta.idempotentHint is True
    assert "GTD" in resource_meta.description
    assert "read-only" in resource_meta.description.lower()
```

**Why**: Proper annotations guide LLM behavior and optimize client interaction patterns.

### 4. Test Complete Read-Write Workflow Separation

**Pattern**: Validate that resources handle read operations while tools handle write operations.

```python
def test_read_write_workflow_separation(self) -> None:
    """Test complete workflow using resources for reads and tools for writes."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"

        # Step 1: Create vault using tool (write operation)
        setup_result = setup_gtd_vault(str(vault_path))

        # Step 2: List files using resource (read operation)
        files_resource = access_resource(f"gtd://{vault_path}/files")
        files_data = json.loads(files_resource)

        # Step 3: Read content using resource (read operation)
        content_resource = access_resource(f"gtd://{vault_path}/content")
        content_data = json.loads(content_resource)

        # Step 4: Validate workflow coherence
        assert len(files_data["files"]) == 9  # All template files
        assert len(content_data["files"]) == 9  # Same files with content
```

**Insight**: Resources and tools must work together seamlessly for complete GTD workflows.

## Resource-Specific Testing Patterns

### 1. URI Template Validation with Edge Cases

**Pattern**: Test resource URI patterns with various edge cases and invalid inputs.

```python
def test_resource_uri_edge_cases(self) -> None:
    """Test resource URIs handle edge cases properly."""
    # Test special characters in vault paths
    vault_with_spaces = "vault with spaces"
    uri_spaces = f"gtd://{vault_with_spaces}/files"

    # Test nested file paths
    nested_file = "GTD/Projects/work/project.md"
    uri_nested = f"gtd://test_vault/file/{nested_file}"

    # Test invalid URIs return appropriate errors
    invalid_uri = "gtd://nonexistent_vault/files"
    # Should return empty result, not exception

    # Test malformed URIs
    malformed_uri = "gtd:vault/files"  # Missing //
    # Should be rejected by FastMCP URI parsing
```

**Why**: GTD systems contain user-generated paths that may include special characters or unexpected structures.

### 2. Filtered Resource Variant Testing

**Pattern**: Validate filtered resource variants work correctly with GTD file type classification.

```python
def test_filtered_resource_variants(self) -> None:
    """Test filtered resource variants correctly categorize GTD files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_sample_vault(vault_path)

        # Test file type filtering
        inbox_files = access_resource(f"gtd://{vault_path}/files/inbox")
        inbox_data = json.loads(inbox_files)

        project_files = access_resource(f"gtd://{vault_path}/files/projects")
        project_data = json.loads(project_files)

        # Validate filtering works correctly
        assert all(f["file_type"] == "inbox" for f in inbox_data["files"])
        assert all(f["file_type"] == "projects" for f in project_data["files"])

        # Test content filtering
        inbox_content = access_resource(f"gtd://{vault_path}/content/inbox")
        inbox_content_data = json.loads(inbox_content)
        assert all(f["file_type"] == "inbox" for f in inbox_content_data["files"])
```

**Insight**: File type filtering is crucial for GTD workflows where users need to focus on specific types of content.

### 3. Performance Comparison Testing

**Pattern**: Compare resource access performance with original tool performance.

```python
def test_resource_performance_vs_tools(self) -> None:
    """Compare resource access performance with original tool performance."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_large_sample_vault(vault_path, file_count=100)

        # Benchmark tool access (before removal)
        tool_start = time.time()
        tool_result = list_gtd_files(str(vault_path))
        tool_duration = time.time() - tool_start

        # Benchmark resource access
        resource_start = time.time()
        resource_result = access_resource(f"gtd://{vault_path}/files")
        resource_duration = time.time() - resource_start

        # Performance should be comparable or better
        assert resource_duration <= tool_duration * 1.5  # Allow 50% overhead
        assert json.loads(resource_result) == tool_result  # Data consistency
```

**Why**: Resource access should not introduce significant performance degradation for large vaults.

### 4. Client Compatibility Testing

**Pattern**: Test resource access with different MCP client patterns.

```python
def test_claude_desktop_compatibility(self) -> None:
    """Test resource access patterns expected by Claude Desktop."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_sample_vault(vault_path)

        # Test common Claude Desktop resource access patterns

        # Pattern 1: File discovery
        files_resource = access_resource(f"gtd://{vault_path}/files")
        files_data = json.loads(files_resource)

        # Pattern 2: Specific file access based on discovery
        first_file = files_data["files"][0]["path"]
        file_resource = access_resource(f"gtd://{vault_path}/file/{first_file}")
        file_data = json.loads(file_resource)

        # Pattern 3: Batch content for analysis
        content_resource = access_resource(f"gtd://{vault_path}/content")
        content_data = json.loads(content_resource)

        # Validate Claude Desktop can chain these operations
        assert len(files_data["files"]) > 0
        assert file_data["content"] is not None
        assert len(content_data["files"]) == len(files_data["files"])
```

**Insight**: Resources must support natural discovery and access patterns that AI assistants use.

## Migration Safety Patterns

### 1. Parallel Operation Validation

**Pattern**: During migration, validate tools and resources return identical results.

```python
def test_parallel_tool_resource_operation(self) -> None:
    """During migration, ensure tools and resources return identical data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_sample_vault(vault_path)

        # Test all three conversions in parallel
        conversions = [
            ("list_gtd_files", f"gtd://{vault_path}/files"),
            ("read_gtd_file", f"gtd://{vault_path}/file/GTD/inbox.md"),
            ("read_gtd_files", f"gtd://{vault_path}/content")
        ]

        for tool_name, resource_uri in conversions:
            tool_result = call_tool(tool_name, vault_path)
            resource_result = access_resource(resource_uri)

            assert tool_result == json.loads(resource_result)
```

**Critical**: Migration must preserve exact data compatibility during transition period.

### 2. Error Handling Consistency

**Pattern**: Ensure resources handle errors the same way as tools.

```python
def test_error_handling_consistency(self) -> None:
    """Test resources handle errors consistently with tools."""
    # Test nonexistent vault
    tool_error = None
    resource_error = None

    try:
        list_gtd_files("nonexistent_vault")
    except Exception as e:
        tool_error = type(e)

    try:
        access_resource("gtd://nonexistent_vault/files")
    except Exception as e:
        resource_error = type(e)

    # Both should handle errors gracefully (return empty vs. exception)
    # Document the expected behavior for each error scenario
```

**Why**: Consistent error handling ensures reliable client behavior across migration.

### 3. Backward Compatibility Testing

**Pattern**: Test that existing client code continues working with minimal changes.

```python
def test_backward_compatibility_simulation(self) -> None:
    """Simulate existing client usage patterns with new resources."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir) / "test_vault"
        create_sample_vault(vault_path)

        # Simulate old client pattern (tool-based)
        old_pattern_result = simulate_old_client_workflow(vault_path)

        # Simulate new client pattern (resource-based)
        new_pattern_result = simulate_new_client_workflow(vault_path)

        # Results should be functionally equivalent
        assert old_pattern_result["file_count"] == new_pattern_result["file_count"]
        assert old_pattern_result["content_hash"] == new_pattern_result["content_hash"]
```

**Insight**: Migration should feel seamless to existing users and integrations.

## Test Organization for Resource Conversion

### 1. Migration-Specific Test Classes

**Pattern**: Organize tests by migration concerns rather than technical components.

```python
class TestResourceUriPatterns:
    """Test resource URI pattern matching and parameter extraction."""

class TestToolResourceDataConsistency:
    """Test data format consistency between tools and resources."""

class TestResourcePerformance:
    """Test resource access performance and scalability."""

class TestMigrationSafety:
    """Test safe migration from tools to resources."""
```

**Benefits**: Clear test organization by migration concerns and validation requirements.

### 2. Progressive Migration Validation

**Pattern**: Structure tests to validate each migration step independently.

```python
def test_migration_step_by_step(self) -> None:
    """Test migration steps independently for safer deployment."""
    # Step 1: Implement resources alongside tools
    test_parallel_operation()

    # Step 2: Validate resource functionality
    test_resource_uri_patterns()
    test_resource_annotations()

    # Step 3: Test client compatibility
    test_claude_desktop_compatibility()

    # Step 4: Validate tool removal readiness
    test_resource_complete_functionality()
```

**Why**: Enables gradual migration with validation at each step.

### 3. Resource-Specific Assertion Patterns

**Pattern**: Group assertions by resource concerns with clear validation intent.

```python
# URI Pattern Validation
assert parsed_vault_path == expected_vault_path
assert parsed_file_path == expected_file_path
assert parsed_file_type == expected_file_type

# Data Format Validation
assert "files" in resource_response
assert "metadata" in resource_response
assert resource_response == tool_response

# Protocol Compliance Validation
assert resource_meta.readOnlyHint is True
assert resource_meta.idempotentHint is True
assert "read-only" in resource_meta.description.lower()
```

**Benefits**: Clear test intent and easier debugging when resource-specific validations fail.

## Resource Conversion Lessons

### 1. URI Parameter Encoding

**Learning**: File paths in URIs may contain special characters that need proper encoding.

**Pattern**: Test URI encoding/decoding explicitly:
```python
def test_uri_parameter_encoding(self) -> None:
    """Test URI parameter encoding for special characters."""
    special_file = "GTD/Projects/project with spaces & symbols.md"
    encoded_uri = f"gtd://vault/file/{urllib.parse.quote(special_file)}"
    # Test that resource correctly decodes the file path
```

### 2. Resource Template Registration Order

**Learning**: Resource template registration order may affect URI matching priority.

**Pattern**: Test that more specific patterns are matched before general ones:
```python
# More specific pattern should match first
gtd://{vault_path}/files/{file_type}  # Should match before general pattern
gtd://{vault_path}/files              # General fallback pattern
```

### 3. Annotation Impact on LLM Behavior

**Learning**: Resource annotations significantly affect how Claude Desktop uses resources.

**Pattern**: Test annotation effectiveness through usage simulation:
```python
def test_annotation_impact_on_usage(self) -> None:
    """Test that resource annotations guide LLM usage correctly."""
    # Resources with readOnlyHint should be preferred for data discovery
    # Resources with idempotentHint should be safely repeatable
```

## Recommendations for Resource Conversion

### 1. Test Data Format Consistency First

Ensure resources return identical data formats before testing advanced features.

### 2. Validate Resource Annotations Early

Test that readOnlyHint and idempotentHint are properly applied and guide client behavior.

### 3. Use Realistic URI Patterns

Test with actual GTD vault structures and file paths, not just simple examples.

### 4. Test Performance at Scale

Validate resource access performance with realistically large GTD vaults (100+ files).

### 5. Document Migration Path Clearly

Provide clear testing validation for each step of the tool-to-resource migration.

## Conclusion

Converting MCP tools to resources requires comprehensive testing of URI patterns, data consistency, protocol compliance, and migration safety. The patterns documented here ensure that resource conversion maintains functionality while improving semantic correctness and LLM understanding.

The key insight for resource conversion is that resources must be both functionally equivalent to the tools they replace AND semantically superior through proper protocol compliance and annotations. Effective testing validates both aspects simultaneously.
