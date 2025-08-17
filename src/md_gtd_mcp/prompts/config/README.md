# GTD Configuration Files

This directory contains all the configuration data that was extracted from the main `gtd_rules.py` Python module to improve code maintainability and separation of concerns.

## Purpose

These files separate static configuration data from business logic, making the codebase more:
- **Maintainable**: Configuration changes don't require code changes
- **Readable**: Python code focuses on logic, not large data structures
- **Modular**: Different types of data are organized in appropriate file formats
- **Cacheable**: Files are loaded once and cached for performance

## File Inventory

### JSON Configuration Files

#### Core GTD Methodology
- **`gtd_methodology.json`** - Core GTD methodology data including David Allen's clarifying questions, category descriptions, context definitions, and workflow phases. Used by `GTDMethodology` class.

#### Pattern Matching Data
- **`context_patterns.json`** - Keyword patterns for detecting GTD contexts (@calls, @computer, etc.). Used by `GTDPatterns` class for context suggestion.
- **`categorization_patterns.json`** - Patterns for categorizing items (two-minute rule indicators, project indicators, delegation patterns). Used by `GTDPatterns` class.
- **`category_descriptions_with_thresholds.json`** - Comprehensive GTD category definitions with pattern matching confidence thresholds for spaCy, rapidfuzz, and textstat libraries. Used by `GTDDocumentation` class.

#### Advanced Configuration
- **`context_strategies.json`** - Detailed context detection strategies with hybrid approaches combining linguistic analysis, fuzzy matching, and automatic pattern recognition. Maps each GTD context to specific detection methods and performance characteristics.
- **`prompt_utilities.json`** - Pattern-to-prompt converters and optimization strategies for building efficient MCP prompts. Documents how to convert pattern analysis results into structured prompts for Claude Desktop.
- **`performance_benchmarks.json`** - Library performance profiles for spaCy, rapidfuzz, and textstat with benchmarks, memory usage, and deployment considerations.

#### Legacy Files (from previous extractions)
- **`advanced_patterns.json`** - Advanced pattern matching configurations (legacy)

### Text Template Files

#### Decision Tree
- **`decision_tree_pattern_integration.txt`** - Large ASCII decision tree for GTD inbox processing with pattern integration guidance. Used by `GTDDocumentation.get_decision_tree_with_pattern_integration()`.

#### Prompt Templates
- **`prompt_template_inbox_clarification.txt`** - Template for inbox item clarification prompts
- **`prompt_template_quick_categorization.txt`** - Template for quick GTD categorization with pattern hints
- **`prompt_template_batch_processing.txt`** - Template for batch processing multiple inbox items

## File Format Strategy

We use a **mixed file format approach** based on content type:

- **JSON files** - For structured configuration data, nested objects, arrays, and numeric values
- **TXT files** - For templates, decision trees, and large text blocks that are primarily human-readable

This approach follows the user feedback: *"Some of this data is json, other is text. Maybe we should use txt files for the blocks that are mostly purely text instead of forcing a text block into json."*

## How the Caching System Works

Each class in `gtd_rules.py` implements lazy loading with caching:

```python
class GTDMethodology:
    _data_cache = None

    @classmethod
    def _load_data(cls) -> dict[str, Any]:
        if cls._data_cache is None:
            json_path = Path(__file__).parent / "config" / "gtd_methodology.json"
            with open(json_path, encoding="utf-8") as f:
                cls._data_cache = json.load(f)
        return cls._data_cache
```

**Benefits:**
- Files are only loaded when first accessed
- Subsequent calls use cached data (no repeated I/O)
- Memory efficient - only loads what's needed
- Thread-safe after initial loading

## Backward Compatibility

The refactoring maintains 100% backward compatibility:

- **Old API**: `GTDMethodology.CLARIFYING_QUESTIONS` (class attribute access)
- **New API**: `GTDMethodology.get_clarifying_questions()` (method call)
- **Both work**: Old tests and code continue to function unchanged

This is achieved by setting class attributes after class definition:
```python
GTDMethodology.CLARIFYING_QUESTIONS = GTDMethodology.get_clarifying_questions()
```

## Development Workflow

### Modifying Configuration Data

1. **To update GTD methodology**: Edit `gtd_methodology.json`
2. **To adjust pattern matching**: Edit `context_patterns.json` or `categorization_patterns.json`
3. **To modify templates**: Edit the appropriate `.txt` file
4. **To tune performance**: Edit `performance_benchmarks.json`

### Modifying Business Logic

1. **For new methods**: Add to the appropriate class in `gtd_rules.py`
2. **For new file types**: Update loading methods and add caching
3. **For new classes**: Follow the established caching pattern

### Testing Changes

The project uses a two-tier testing strategy optimized for development speed:

**Fast Development Tests (default - 26 seconds):**
```bash
uv run pytest tests/prompts/test_gtd_rules.py
# Runs 38 core tests, excludes slow integration tests
```

**Comprehensive Tests (63 seconds):**
```bash
uv run pytest tests/prompts/test_gtd_rules.py -m ""
# Runs all 49 tests including slow integration scenarios
```

**Slow Tests Only:**
```bash
uv run pytest tests/prompts/test_gtd_rules.py -m slow
# Runs only the 11 slow tests (19 seconds)
```

Always run the fast test suite after configuration changes. Use comprehensive tests before major commits or releases.

## File Size Impact

This reorganization significantly reduced the main Python file:

- **Original `gtd_rules.py`**: 2,836+ lines
- **After extractions**: 1,760 lines
- **Total reduction**: 1,076 lines (38% smaller)
- **Configuration files**: 12 files (8 JSON + 4 TXT)

## Architecture Benefits

1. **Separation of Concerns**: Configuration is cleanly separated from business logic
2. **Single Responsibility**: Each file has a clear, focused purpose
3. **Easy Maintenance**: Configuration changes don't require code deployments
4. **Performance**: Efficient caching prevents repeated file I/O
5. **Flexibility**: Different teams can work on config vs code independently
6. **Debugging**: Issues can be isolated to configuration vs logic

## Integration with MCP Prompts

These configuration files power the MCP (Model Context Protocol) server's ability to:

1. **Guide Claude Desktop** through proper GTD methodology
2. **Provide intelligent hints** based on pattern analysis
3. **Optimize prompts** for token efficiency and accuracy
4. **Support offline operation** with comprehensive static data
5. **Scale performance** through caching and efficient data structures

The system follows Decision D008: use static server-side pattern analysis to guide Claude Desktop's LLM reasoning rather than performing intelligent analysis server-side.
