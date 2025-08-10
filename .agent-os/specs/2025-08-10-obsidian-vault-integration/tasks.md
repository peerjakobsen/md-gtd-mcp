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
- [ ] 2.3 Write tests for context detection and project links
- [ ] 2.4 Write tests for LinkExtractor with markdown links and wikilinks
- [ ] 2.5 Implement LinkExtractor class in parsers/link_extractor.py
- [ ] 2.6 Write tests for MarkdownParser frontmatter extraction
- [ ] 2.7 Implement MarkdownParser class in parsers/markdown_parser.py
- [ ] 2.8 Verify all parser tests pass

### 3. Create vault reading service
- [ ] 3.1 Write tests for VaultReader with GTD folder structure
- [ ] 3.2 Implement VaultReader class with file type detection
- [ ] 3.3 Test inbox, projects, next-actions, waiting-for, someday files
- [ ] 3.4 Test contexts folder with @calls, @computer, @errands files
- [ ] 3.5 Create GTD test fixtures in tests/fixtures/sample_vault/gtd/
- [ ] 3.6 Test integration of all parser components with VaultReader
- [ ] 3.7 Verify all service tests pass

### 4. Implement MCP tools interface
- [ ] 4.1 Write tests for MCP tool responses and JSON structure
- [ ] 4.2 Update server.py with read_gtd_file tool
- [ ] 4.3 Implement list_gtd_files tool in server.py
- [ ] 4.4 Implement read_all_gtd_files tool in server.py
- [ ] 4.5 Test MCP server startup with vault configuration
- [ ] 4.6 Verify all MCP tool tests pass

### 5. Integration testing and documentation
- [ ] 5.1 Create comprehensive integration test with sample vault
- [ ] 5.2 Test end-to-end workflow from vault config to MCP response
- [ ] 5.3 Update CLAUDE.md with implementation details
- [ ] 5.4 Run full test suite with pytest
- [ ] 5.5 Run code quality checks (ruff, mypy)
- [ ] 5.6 Verify all tests and quality checks pass

## Task Dependencies

- Task 1 must complete before Tasks 2 and 3 (foundational models)
- Tasks 2 and 3 can be done in parallel after Task 1
- Task 4 depends on Tasks 2 and 3 (needs parser and reader)
- Task 5 depends on all previous tasks (final integration)

## Estimated Complexity

- **Task 1**: Medium complexity (3-4 hours) - GTD-aligned data structures
- **Task 2**: High complexity (4-5 hours) - Obsidian Tasks parsing with GTD metadata
- **Task 3**: Medium complexity (3-4 hours) - GTD folder structure handling
- **Task 4**: Low-Medium complexity (2-3 hours) - MCP integration
- **Task 5**: Low complexity (1-2 hours) - Testing and documentation

**Total Estimate**: 13-18 hours of development time
