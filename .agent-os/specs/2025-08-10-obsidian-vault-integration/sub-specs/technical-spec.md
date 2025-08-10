# Technical Specification - Obsidian Vault Integration

## GTD Folder Structure

The vault follows the Getting Things Done methodology with this structure:

```
gtd/
├── inbox.md              # Capture everything here first
├── projects.md           # Active projects with defined outcomes
├── next-actions.md       # Context-organized actionable tasks
├── waiting-for.md        # Items delegated to others
├── someday-maybe.md      # Future possibilities, not committed
└── contexts/
    ├── @calls.md         # Phone calls context
    ├── @computer.md      # Computer-based tasks
    ├── @errands.md       # Out-and-about tasks
    └── ...               # Other context files
```

## Architecture Overview

### Core Components

1. **VaultConfig**: Configuration class for vault path management
2. **MarkdownParser**: Handles YAML frontmatter and content parsing
3. **LinkExtractor**: Processes standard markdown links
4. **TaskExtractor**: Parses Obsidian Tasks plugin format with checkboxes and inline metadata
5. **GTDFile**: Data model representing parsed GTD markdown files with tasks
6. **VaultReader**: Main service class coordinating file reading and parsing

### Data Models

#### GTDFile Structure
```python
@dataclass
class GTDFile:
    path: str
    title: str
    content: str
    file_type: str  # inbox, projects, next-actions, waiting-for, someday-maybe, context
    frontmatter: GTDFrontmatter
    tasks: List[GTDTask]
    links: List[MarkdownLink]
    raw_content: str
```

#### GTDFrontmatter Structure
```python
@dataclass
class GTDFrontmatter:
    # Project-level metadata (primarily for projects.md)
    outcome: Optional[str] = None  # Desired outcome for project
    status: Optional[str] = None  # active, completed, on-hold
    area: Optional[str] = None  # Area of responsibility
    review_date: Optional[datetime] = None  # Next review date
    created_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    # Additional properties preserved as dict
    extra: Dict[str, Any] = field(default_factory=dict)
```

#### GTDTask Structure (Obsidian Tasks + GTD Methodology)
```python
@dataclass
class GTDTask:
    # Core task information
    text: str  # Task description without metadata
    is_completed: bool  # [ ] vs [x]
    raw_text: str  # Original full task line with all metadata
    line_number: int

    # GTD methodology properties
    context: Optional[str] = None  # @home, @office, @calls, @computer, @errands
    project: Optional[str] = None  # [[Project Name]] link reference
    energy: Optional[str] = None  # 🔥 high, 💪 medium, 🪶 low
    time_estimate: Optional[int] = None  # ⏱️ minutes (e.g., ⏱️ 30m)
    delegated_to: Optional[str] = None  # 👤 person name for waiting-for items

    # Obsidian Tasks plugin metadata
    tags: List[str] = field(default_factory=list)  # #task, #waiting, #someday
    due_date: Optional[datetime] = None  # 📅 YYYY-MM-DD
    scheduled_date: Optional[datetime] = None  # ⏳ YYYY-MM-DD
    start_date: Optional[datetime] = None  # 🛫 YYYY-MM-DD
    done_date: Optional[datetime] = None  # ✅ YYYY-MM-DD
    priority: Optional[str] = None  # ⏫ high, 🔼 medium, 🔽 low
    recurrence: Optional[str] = None  # 🔁 every day/week/month
```

#### MarkdownLink Structure
```python
@dataclass
class MarkdownLink:
    text: str
    target: str
    is_external: bool
    line_number: int
```

### Implementation Strategy

#### File Reading
- Use `pathlib.Path` for cross-platform path handling
- Read files with UTF-8 encoding
- Filter for `.md` files only within `gtd/` directory
- Identify file type based on path (inbox.md, projects.md, contexts/@*.md, etc.)
- Recursive reading to support GTD subdirectories

#### YAML Frontmatter Parsing
- Use `python-frontmatter` library for reliable parsing
- Handle missing frontmatter gracefully (common in task files)
- Preserve unknown frontmatter fields in `extra` dict
- Convert string dates to datetime objects with ISO format parsing

#### Task Extraction (Obsidian Tasks Plugin)
- Regex pattern for tasks: `^(\s*)- \[([ xX])\] (.+)$`
- Parse inline metadata with emoji patterns:
  - Context: `@\w+` (GTD contexts)
  - Project: `\[\[([^\]]+)\]\]` (wikilinks to projects)
  - Due: `📅 (\d{4}-\d{2}-\d{2})`
  - Priority: `(⏫|🔼|🔽)`
  - Energy: `(🔥|💪|🪶)`
  - Time: `⏱️ (\d+)m`
  - Person: `👤 ([^\s]+)`
- Extract #tags from task text
- Preserve task hierarchy based on indentation

#### Markdown Link Processing
- Use regex pattern: `\[([^\]]+)\]\(([^)]+)\)`
- Also extract wikilinks: `\[\[([^\]]+)\]\]`
- Track line numbers for link context
- Distinguish internal vs external links by URL scheme detection
- Handle relative paths relative to vault root

#### MCP Integration
- Implement as FastMCP tools using `@mcp.tool()` decorator
- Provide tools for individual file reading and batch processing
- Return structured JSON responses compatible with MCP protocol

### Configuration

#### Vault Path Configuration
```python
@dataclass
class VaultConfig:
    vault_path: Path
    gtd_folder: str = "gtd"

    @property
    def gtd_path(self) -> Path:
        return self.vault_path / self.gtd_folder
```

### MCP Tools Interface

#### Primary Tools
1. `read_gtd_file(file_path: str) -> GTDFile` - Read and parse single GTD file
2. `list_gtd_files() -> List[str]` - List all GTD files in vault
3. `read_all_gtd_files() -> List[GTDFile]` - Batch read all GTD files

### Dependencies

#### Required Libraries
- `python-frontmatter` - YAML frontmatter parsing
- `fastmcp` - MCP server framework (existing)
- `pathlib` - Path handling (standard library)
- `dataclasses` - Data models (standard library)
- `datetime` - Date handling (standard library)
- `re` - Regex for link parsing (standard library)

### File Organization

```
src/md_gtd_mcp/
├── models/
│   ├── __init__.py
│   ├── gtd_file.py      # GTDFile, GTDFrontmatter, GTDTask, MarkdownLink
│   └── vault_config.py  # VaultConfig
├── parsers/
│   ├── __init__.py
│   ├── markdown_parser.py  # MarkdownParser (frontmatter)
│   ├── task_extractor.py   # TaskExtractor (Obsidian Tasks format)
│   └── link_extractor.py   # LinkExtractor (markdown & wikilinks)
├── services/
│   ├── __init__.py
│   └── vault_reader.py     # VaultReader
└── server.py               # MCP tools and server setup
```

### Testing Strategy

#### Unit Tests
- Test frontmatter parsing with project metadata
- Test task extraction with Obsidian Tasks format and GTD properties
- Test context detection (@home, @office, @calls)
- Test project link extraction from tasks
- Test emoji metadata parsing (priority, energy, time estimates)
- Test file type identification based on path

#### Integration Tests
- Test complete GTD file parsing workflow
- Test inbox.md with uncategorized tasks
- Test projects.md with project definitions and outcomes
- Test next-actions.md with context-organized tasks
- Test waiting-for.md with delegation info
- Test contexts/@*.md files with context-specific tasks
- Test MCP tool responses and JSON structure

#### Test Data Structure
```
tests/fixtures/sample_vault/gtd/
├── inbox.md              # Mixed tasks with #task tags
├── projects.md           # Projects with frontmatter and task lists
├── next-actions.md       # Tasks organized by context
├── waiting-for.md        # Tasks with 👤 delegation
├── someday-maybe.md      # Tasks with #someday tag
└── contexts/
    ├── @calls.md         # Phone call tasks
    ├── @computer.md      # Computer tasks with project links
    └── @errands.md       # Errand tasks with locations
```
