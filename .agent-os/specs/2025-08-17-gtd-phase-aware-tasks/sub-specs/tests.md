# Tests Specification

This is the tests coverage details for the spec detailed in @.agent-os/specs/2025-08-17-gtd-phase-aware-tasks/spec.md

> Created: 2025-08-17
> Version: 1.0.0

## Test Coverage

### GTD Phase-Aware Task Recognition Tests

#### File Type Detection Tests
- **test_get_file_gtd_category_inbox**: Verify inbox files are correctly identified
- **test_get_file_gtd_category_projects**: Verify project files are correctly identified
- **test_get_file_gtd_category_next_actions**: Verify next action files are correctly identified
- **test_get_file_gtd_category_waiting_for**: Verify waiting for files are correctly identified
- **test_get_file_gtd_category_someday_maybe**: Verify someday/maybe files are correctly identified
- **test_get_file_gtd_category_reference**: Verify reference files are correctly identified
- **test_get_file_gtd_category_unknown_path**: Handle files outside GTD structure gracefully
- **test_get_file_gtd_category_nested_folders**: Handle nested folder structures correctly

#### Phase Classification Tests
- **test_should_extract_tasks_inbox_false**: Inbox files should not have task extraction
- **test_should_extract_tasks_projects_true**: Project files should have task extraction
- **test_should_extract_tasks_next_actions_true**: Next action files should have task extraction
- **test_should_extract_tasks_waiting_for_true**: Waiting for files should have task extraction
- **test_should_extract_tasks_someday_maybe_true**: Someday/maybe files should have task extraction
- **test_should_extract_tasks_reference_true**: Reference files should have task extraction

#### Integration with Existing Tools Tests
- **test_read_gtd_file_respects_phase**: Existing tools respect phase-aware logic
- **test_categorize_gtd_text_skips_inbox**: Categorization skips inbox items
- **test_task_extraction_backwards_compatible**: Existing functionality still works for processed files

### Inbox Capture Tool Tests

#### Basic Capture Tests
- **test_capture_inbox_item_basic**: Capture item with minimal parameters
- **test_capture_inbox_item_with_tags**: Capture item with tags
- **test_capture_inbox_item_with_urgency**: Capture item with urgency level
- **test_capture_inbox_item_with_source**: Capture item with source context
- **test_capture_inbox_item_all_parameters**: Capture item with all optional parameters

#### File Creation Tests
- **test_inbox_file_creation**: Verify file is created in correct location
- **test_inbox_filename_uniqueness**: Ensure filenames are unique even with rapid creation
- **test_inbox_filename_format**: Verify filename follows timestamp format
- **test_inbox_content_format**: Verify file content follows expected markdown format
- **test_inbox_yaml_frontmatter**: Verify YAML frontmatter is properly formatted

#### Error Handling Tests
- **test_capture_invalid_content**: Handle empty or invalid content gracefully
- **test_capture_permission_denied**: Handle file permission errors
- **test_capture_disk_full**: Handle disk space errors
- **test_capture_invalid_tags**: Handle malformed tags
- **test_capture_invalid_urgency**: Handle invalid urgency values

#### Edge Case Tests
- **test_capture_very_long_content**: Handle very long content items
- **test_capture_special_characters**: Handle special characters in content
- **test_capture_unicode_content**: Handle unicode and emoji content
- **test_capture_markdown_in_content**: Handle markdown syntax in captured content

### Integration Tests

#### Full Workflow Tests
- **test_capture_then_read**: Capture item then read it back
- **test_capture_then_categorize**: Verify captured items are not auto-categorized
- **test_phase_aware_workflow**: Full workflow respecting phases
- **test_existing_tools_still_work**: Ensure existing MCP tools continue to function

#### Cross-Feature Tests
- **test_multiple_captures_same_content**: Handle duplicate content captures
- **test_capture_during_existing_operations**: Ensure capture doesn't interfere with other operations
- **test_vault_structure_consistency**: Ensure vault structure remains consistent

## Mocking Requirements

### File System Mocking
- Mock Obsidian vault directory structure
- Mock file creation and reading operations
- Mock permission and disk space scenarios
- Mock timestamp generation for consistent testing

### GTD Folder Structure Mock
```python
@pytest.fixture
def mock_gtd_vault_structure(tmp_path):
    """Create a mock GTD vault structure for testing"""
    vault_path = tmp_path / "test_vault" / "GTD"

    # Create GTD folders
    (vault_path / "01-Inbox").mkdir(parents=True)
    (vault_path / "02-Projects").mkdir(parents=True)
    (vault_path / "03-Next-Actions").mkdir(parents=True)
    (vault_path / "04-Waiting-For").mkdir(parents=True)
    (vault_path / "05-Someday-Maybe").mkdir(parents=True)
    (vault_path / "06-Reference").mkdir(parents=True)

    return vault_path
```

### Sample Test Files
```python
@pytest.fixture
def sample_inbox_item():
    """Sample content for inbox capture testing"""
    return {
        "content": "Research new project management tools",
        "tags": ["research", "tools"],
        "urgency": "medium",
        "source": "team meeting"
    }

@pytest.fixture
def sample_project_file_content():
    """Sample project file content for phase testing"""
    return """---
title: Website Redesign
status: active
---

# Website Redesign Project

## Next Actions
- [ ] Review competitor websites
- [ ] Create wireframes
- [ ] Get stakeholder feedback
"""
```

### Time Mocking
```python
@pytest.fixture
def mock_timestamp():
    """Mock timestamp for consistent filename generation"""
    with patch('datetime.datetime') as mock_datetime:
        mock_datetime.now.return_value = datetime(2025, 8, 17, 14, 30, 22)
        mock_datetime.strftime = datetime.strftime
        yield mock_datetime
```

### MCP Tool Testing Framework
```python
@pytest.fixture
def mcp_test_client():
    """Set up MCP test client for tool testing"""
    # Configure test client for MCP tool invocation
    # Mock server responses and tool registration
    pass
```
