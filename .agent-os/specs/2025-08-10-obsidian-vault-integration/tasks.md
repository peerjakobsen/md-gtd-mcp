# Tasks - Obsidian Vault Integration

## Task Breakdown

### 1. Set up data models and configuration
- [x] 1.1 Write tests for GTDFile, GTDFrontmatter, GTDTask, and MarkdownLink data models
- [x] 1.2 Implement GTDFile with file_type detection in models/gtd_file.py
- [x] 1.3 Implement GTDTask with GTD properties and Obsidian Tasks metadata
- [x] 1.4 Write tests for VaultConfig with GTD folder structure
- [x] 1.5 Implement VaultConfig class in models/vault_config.py
- [x] 1.6 Add python-frontmatter dependency to pyproject.toml
- [x] 1.7 Verify all model tests pass

### 2. Implement parsing components
- [x] 2.1 Write tests for TaskExtractor with Obsidian Tasks format
- [x] 2.2 Implement TaskExtractor for checkbox tasks and GTD metadata
- [x] 2.3 Write tests for context detection and project links
- [x] 2.4 Write tests for LinkExtractor with markdown links and wikilinks
- [x] 2.5 Implement LinkExtractor class in parsers/link_extractor.py
- [x] 2.6 Write tests for MarkdownParser frontmatter extraction
- [x] 2.7 Implement MarkdownParser class in parsers/markdown_parser.py
- [x] 2.8 Verify all parser tests pass

### 3. Create vault reading service
- [x] 3.1 Write tests for VaultReader with GTD folder structure
- [x] 3.2 Implement VaultReader class with file type detection
- [x] 3.3 Test inbox, projects, next-actions, waiting-for, someday files
- [x] 3.4 Test contexts folder with @calls, @computer, @errands files
- [x] 3.5 Create GTD test fixtures in tests/fixtures/sample_vault/gtd/
- [x] 3.6 Test integration of all parser components with VaultReader
- [x] 3.7 Verify all service tests pass

### 4. Implement MCP tools interface
- [x] 4.1 Write tests for setup_gtd_vault tool (creates missing GTD files/folders)
  - **CRITICAL**: Test that existing files are NEVER overwritten (data safety)
  - Test complete GTD structure creation when vault is empty
  - Test selective creation when some files already exist
  - Test context files creation with Obsidian Tasks query syntax
- [x] 4.2 Implement setup_gtd_vault tool in server.py
  - **CRITICAL**: Only create files/folders that don't exist - NEVER overwrite existing files
  - Use Path.exists() checks before creating any file or folder
  - Return detailed status report of what was created vs. already existed
- [x] 4.3 Write tests for read_gtd_file MCP tool
- [x] 4.4 Implement read_gtd_file tool in server.py
- [x] 4.5 Write tests for list_gtd_files MCP tool
- [x] 4.6 Implement list_gtd_files tool in server.py
- [x] 4.7 Refactor list_gtd_files to return metadata only (file paths, types, counts)
  - **REFACTOR**: Remove full content from list_gtd_files response
  - **KEEP**: File metadata, task/link counts, summary statistics, filtering
  - **PURPOSE**: Lightweight listing for GTD system overview
- [x] 4.8 Write tests for read_gtd_files MCP tool (full content with optional filtering)
- [x] 4.9 Implement read_gtd_files tool in server.py (comprehensive content reading)
- [x] 4.10 Write tests for GTDFrontmatter Pydantic conversion
- [x] 4.11 Convert GTDFrontmatter from dataclass to Pydantic BaseModel
  - **BENEFIT**: Built-in model_dump() for MCP tool serialization
  - **BENEFIT**: Automatic validation and JSON schema generation
  - **BENEFIT**: Better datetime handling for API responses
- [x] 4.12 Test MCP server startup with vault configuration
- [x] 4.13 Verify all MCP tool tests pass

### 5. Integration testing and documentation
- [x] 5.1 Test new user onboarding workflow - Complete GTD vault setup from empty directory
  - Verify setup_gtd_vault creates all required files/folders
  - Confirm list_gtd_files shows proper structure
  - Validate read_gtd_files returns expected templates
- [ ] 5.2 Test existing user migration workflow - Partial vault completion without data loss
  - Create vault with some existing GTD files containing user data
  - Run setup_gtd_vault and verify it preserves existing content
  - Confirm new files are created only where missing
- [ ] 5.3 Test daily inbox processing workflow - Reading and categorizing captured items
  - Read inbox file with mixed processed/unprocessed items
  - Verify task extraction distinguishes actionable items
  - Validate proper categorization suggestions in response
- [ ] 5.4 Test weekly review workflow - Complete system overview and statistics
  - Call read_gtd_files for full vault content
  - Verify aggregation of tasks by context and project
  - Validate identification of completed vs pending items
- [ ] 5.5 Test context-based task filtering - Finding tasks for focused work sessions
  - Use list_gtd_files with file_type="context" filter
  - Read specific context files (@calls, @computer)
  - Verify proper task grouping by context across all files
- [ ] 5.6 Test project tracking workflow - Following project references and dependencies
  - Read projects file and extract project definitions
  - Follow wikilinks to related tasks in other files
  - Validate project-task relationships are preserved
- [ ] 5.7 Test cross-file navigation - Validating link integrity across GTD system
  - Extract all links from read_gtd_files response
  - Verify internal links point to valid targets
  - Validate wikilink resolution to actual files/sections
- [ ] 5.8 Test incremental vault updates - Handling changes between reads
  - Initial read of vault state
  - Modify fixture files programmatically
  - Re-read and verify changes are detected
- [ ] 5.9 Test error recovery scenarios - Graceful handling of common issues
  - Test with missing permissions on files
  - Test with malformed markdown/frontmatter
  - Verify helpful error messages for troubleshooting
- [ ] 5.10 Test performance with realistic GTD vault - 100+ tasks across multiple files
  - Generate larger test fixtures programmatically
  - Measure response times for all MCP tools
  - Verify memory usage remains reasonable
- [ ] 5.11 Update CLAUDE.md with implementation details
- [ ] 5.12 Run full test suite with pytest

## Task Dependencies

- Task 1 must complete before Tasks 2 and 3 (foundational models)
- Tasks 2 and 3 can be done in parallel after Task 1
- Task 4 depends on Tasks 2 and 3 (needs parser and reader)
- Task 5 depends on all previous tasks (final integration)

## Estimated Complexity

- **Task 1**: Medium complexity (3-4 hours) - GTD-aligned data structures
- **Task 2**: High complexity (4-5 hours) - Obsidian Tasks parsing with GTD metadata
- **Task 3**: Medium complexity (3-4 hours) - GTD folder structure handling
- **Task 4**: Medium complexity (3-4 hours) - MCP integration + vault setup tool
- **Task 5**: High complexity (6-8 hours) - Comprehensive integration testing and documentation covering 10 end-to-end GTD workflow scenarios

**Total Estimate**: 19-25 hours of development time
