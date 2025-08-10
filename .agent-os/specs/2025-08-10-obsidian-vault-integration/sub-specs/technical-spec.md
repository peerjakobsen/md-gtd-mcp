# Technical Specification - Obsidian Vault Integration

## Architecture Overview

### Core Components

1. **VaultConfig**: Configuration class for vault path management
2. **MarkdownParser**: Handles YAML frontmatter and content parsing
3. **LinkExtractor**: Processes standard markdown links
4. **GTDFile**: Data model representing parsed GTD markdown files
5. **VaultReader**: Main service class coordinating file reading and parsing

### Data Models

#### GTDFile Structure
```python
@dataclass
class GTDFile:
    path: str
    title: str
    content: str
    frontmatter: GTDFrontmatter
    links: List[MarkdownLink]
    raw_content: str
```

#### GTDFrontmatter Structure
```python
@dataclass
class GTDFrontmatter:
    status: Optional[str] = None  # active, completed, someday, waiting
    context: Optional[str] = None  # @home, @computer, @office
    priority: Optional[Union[str, int]] = None  # high/medium/low or 1-5
    due_date: Optional[datetime] = None
    project: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    # Additional properties preserved as dict
    extra: Dict[str, Any] = field(default_factory=dict)
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
- Recursive reading to support GTD subdirectories

#### YAML Frontmatter Parsing
- Use `python-frontmatter` library for reliable parsing
- Handle missing frontmatter gracefully
- Preserve unknown frontmatter fields in `extra` dict
- Convert string dates to datetime objects with ISO format parsing

#### Markdown Link Processing
- Use regex pattern: `\[([^\]]+)\]\(([^)]+)\)`
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
│   ├── gtd_file.py      # GTDFile, GTDFrontmatter, MarkdownLink
│   └── vault_config.py  # VaultConfig
├── parsers/
│   ├── __init__.py
│   ├── markdown_parser.py  # MarkdownParser
│   └── link_extractor.py   # LinkExtractor
├── services/
│   ├── __init__.py
│   └── vault_reader.py     # VaultReader
└── server.py               # MCP tools and server setup
```

### Testing Strategy

#### Unit Tests
- Test frontmatter parsing with various GTD property combinations
- Test markdown link extraction with different link formats
- Test file reading with different folder structures
- Test data model serialization/deserialization

#### Integration Tests
- Test complete file parsing workflow
- Test MCP tool responses and JSON structure
- Test with sample GTD vault structure

#### Test Data
- Create `tests/fixtures/sample_vault/gtd/` with representative markdown files
- Include files with various frontmatter configurations
- Include files with different link patterns
