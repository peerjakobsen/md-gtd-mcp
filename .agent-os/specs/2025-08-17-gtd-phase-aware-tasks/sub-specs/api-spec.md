# API Specification

This is the API specification for the spec detailed in @.agent-os/specs/2025-08-17-gtd-phase-aware-tasks/spec.md

> Created: 2025-08-17
> Version: 1.0.0

## Endpoints

### New MCP Tool: capture_inbox_item

**Purpose**: Capture items directly to GTD inbox for later clarification

**Parameters**:
- `content` (required, string): The item content to capture
- `tags` (optional, list of strings): Tags to associate with the item
- `urgency` (optional, string): Urgency level ("high", "medium", "low")
- `source` (optional, string): Context about the source of this item

**Response**:
```json
{
  "success": true,
  "file_path": "/vault/GTD/01-Inbox/2025-08-17-143022-captured-item.md",
  "message": "Item captured successfully to inbox"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Failed to create inbox file: permission denied",
  "details": "Unable to write to inbox directory"
}
```

**Example Usage**:
```json
{
  "tool": "capture_inbox_item",
  "arguments": {
    "content": "Research new project management tools for the team",
    "tags": ["research", "team", "tools"],
    "urgency": "medium",
    "source": "team meeting discussion"
  }
}
```

### Modified Functions: Task Recognition Enhancement

#### Enhanced get_file_gtd_category()

**Purpose**: Determine GTD category and phase for a given file path

**Parameters**:
- `file_path` (string): Path to the GTD file

**Returns**:
```python
{
  "category": "INBOX",
  "phase": "CAPTURE",
  "folder_path": "/vault/GTD/01-Inbox/",
  "should_extract_tasks": false
}
```

#### Enhanced Task Recognition in Existing Tools

**Modified Behavior**: All existing tools that perform task recognition will now:

1. Check file GTD category before processing
2. Skip task extraction for inbox files
3. Continue normal processing for clarified files
4. Log phase-aware decisions for debugging

**Affected Tools**:
- `read_gtd_file` - will indicate if file is in capture phase
- `categorize_gtd_text` - will refuse to categorize inbox items
- Any future task extraction tools

## Controllers

### GTDPhaseManager

**Purpose**: Central controller for managing GTD phase logic

**Methods**:

#### `get_file_category(file_path: str) -> GTDCategory`
- Analyzes file path to determine GTD category
- Returns category enum with phase information
- Handles edge cases and unknown paths

#### `should_extract_tasks(file_path: str) -> bool`
- Determines if task extraction should be performed
- Returns `False` for inbox files, `True` for processed files
- Used by all task recognition functions

#### `is_capture_phase(file_path: str) -> bool`
- Quick check if file is in capture phase (inbox)
- Used for conditional logic throughout the system

### InboxCaptureManager

**Purpose**: Handles inbox item capture and file creation

**Methods**:

#### `capture_item(content: str, tags: List[str] = None, urgency: str = None, source: str = None) -> dict`
- Creates new inbox file with provided content
- Generates unique filename with timestamp
- Formats file with proper YAML frontmatter
- Returns success/failure information

#### `generate_filename(content: str) -> str`
- Creates timestamp-based filename with content slug
- Ensures filename uniqueness
- Handles special characters and length limits

#### `format_inbox_item(content: str, metadata: dict) -> str`
- Formats content as markdown with YAML frontmatter
- Includes creation timestamp and metadata
- Adds capture phase indicators

### File Structure Integration

**GTD Folder Detection Logic**:
```
/vault/GTD/
  ├── 01-Inbox/          -> INBOX (CAPTURE phase)
  ├── 02-Projects/       -> PROJECTS (CLARIFY phase)
  ├── 03-Next-Actions/   -> NEXT_ACTIONS (CLARIFY phase)
  ├── 04-Waiting-For/    -> WAITING_FOR (CLARIFY phase)
  ├── 05-Someday-Maybe/  -> SOMEDAY_MAYBE (CLARIFY phase)
  └── 06-Reference/      -> REFERENCE (CLARIFY phase)
```

**Path Analysis Algorithm**:
1. Extract relative path from vault root
2. Check for GTD folder patterns in path
3. Map folder names to GTD categories
4. Determine phase based on category
5. Handle nested folders and edge cases
