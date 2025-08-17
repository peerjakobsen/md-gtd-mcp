"""Integration tests for MCP resources with GTD phase-aware task recognition.

This module tests the integration between ResourceHandler and the enhanced TaskExtractor
that implements file-type aware task recognition following GTD methodology:
- Inbox files: Recognize ALL `- [ ]` items without #task requirement (pure capture)
- Other GTD files: Maintain #task tag requirements for Obsidian Tasks compatibility

Tests verify that MCP resources correctly handle the new task recognition logic
while maintaining backward compatibility and format consistency.
"""

import tempfile
from pathlib import Path
from typing import Any

from md_gtd_mcp.services.resource_handler import ResourceHandler
from md_gtd_mcp.services.vault_setup import setup_gtd_vault


class TestPhaseAwareResourceIntegration:
    """Test ResourceHandler integration with phase-aware TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test environment with phase-aware GTD vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create inbox.md with items WITHOUT #task tags (pure capture phase)
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text("""---
status: active
---

# Inbox

## Quick Capture

- Research vacation destinations for spring break
- Meeting notes from client call yesterday
- Fix squeaky door in hallway
- [ ] Review quarterly budget report @computer
- Book recommendation from Sarah: "Atomic Habits"
- [ ] Confirm meeting attendance with team @calls

## Ideas and Notes

Check [[Project Alpha]] status for next steps.
Review [[Weekly Planning]] template.
Look into new project management software options.

## Mixed Processing States

- [ ] Processed item with tag #task @home
- [ ] Unprocessed item without tag
""")

        # Create projects.md with items that REQUIRE #task tags
        projects_file = gtd_path / "projects.md"
        projects_file.write_text("""# Projects

## Active Projects

### Project Alpha
- [ ] Design wireframes #task @computer
- [ ] Schedule client review #task @calls
- [x] Initial research completed #task @computer

### Project Beta
- [ ] Draft proposal #task @computer
- [ ] Review with stakeholders #task @calls

## Project References

- Some non-task content here
- [ ] This won't be recognized as task (no #task tag)
- Link to [[Meeting Notes]]
""")

        # Create next-actions.md with proper #task tags
        next_actions_file = gtd_path / "next-actions.md"
        next_actions_file.write_text("""# Next Actions

## @computer
- [ ] Update project documentation #task @computer
- [ ] Review code changes #task @computer
- [x] Deploy latest version #task @computer

## @calls
- [ ] Call insurance company #task @calls
- [ ] Schedule team meeting #task @calls

## @home
- [ ] Fix garage door #task @home
- [ ] Organize paperwork #task @home

## Mixed Content
- Some reference information
- [ ] Item without task tag (should not be recognized)
- Links to other files: [[Projects]]
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()


class TestInboxPhaseAwareRecognition:
    """Test inbox files recognize ALL checkbox items without #task requirement."""

    def setup_method(self) -> None:
        """Set up test with phase-aware inbox content."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Inbox with mixed capture states - some with #task, some without
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text("""# Inbox

## Pure Capture Items (no #task tags)
- [ ] Call dentist about appointment
- [ ] Research new laptop options
- [ ] Pick up dry cleaning
- [x] Completed inbox item

## Processed Items (have #task tags)
- [ ] Review project proposal #task @computer
- [ ] Schedule team meeting #task @calls
- [x] Finished processed item #task @home

## Mixed Content
Some meeting notes here...
- [ ] Action item from meeting
- Regular text content
- [ ] Another action without tag
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_inbox_file_resource_recognizes_all_checkbox_items(self) -> None:
        """Test that inbox file resource recognizes ALL checkbox items."""
        inbox_result = self.resource_handler.get_file(
            str(self.vault_path), "gtd/inbox.md"
        )

        assert inbox_result["status"] == "success"
        inbox_data = inbox_result["file"]
        assert inbox_data["file_type"] == "inbox"

        # Should recognize ALL checkbox items, regardless of #task tag
        tasks = inbox_data["tasks"]

        # Verify we have the expected number of tasks (all checkbox items)
        assert len(tasks) >= 8  # All checkbox items should be recognized

        # Verify specific tasks are recognized
        task_descriptions = [task["description"] for task in tasks]

        # Pure capture items (no #task tag) should be recognized
        assert any("Call dentist" in desc for desc in task_descriptions)
        assert any("Research new laptop" in desc for desc in task_descriptions)
        assert any("Pick up dry cleaning" in desc for desc in task_descriptions)
        assert any("Action item from meeting" in desc for desc in task_descriptions)
        assert any("Another action without tag" in desc for desc in task_descriptions)

        # Processed items (with #task tag) should also be recognized
        assert any("Review project proposal" in desc for desc in task_descriptions)
        assert any("Schedule team meeting" in desc for desc in task_descriptions)

    def test_inbox_content_resource_phase_aware_recognition(self) -> None:
        """Test content resource shows phase-aware task recognition for inbox."""
        content_result = self.resource_handler.get_content(
            str(self.vault_path), file_type="inbox"
        )

        assert content_result["status"] == "success"
        assert len(content_result["files"]) == 1

        inbox_file = content_result["files"][0]
        assert inbox_file["file_type"] == "inbox"

        # Should have high task count due to phase-aware recognition
        assert len(inbox_file["tasks"]) >= 8

        # Verify task metadata structure
        for task in inbox_file["tasks"]:
            assert "description" in task
            assert "completed" in task
            assert "raw_text" in task
            assert "line_number" in task


class TestNonInboxPhaseAwareRecognition:
    """Test non-inbox files maintain #task tag requirements."""

    def setup_method(self) -> None:
        """Set up test with non-inbox GTD files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Projects file with mixed task recognition patterns
        projects_file = gtd_path / "projects.md"
        projects_file.write_text("""# Projects

## Project A
- [ ] Task with tag #task @computer
- [ ] Task without tag (should not be recognized)
- [x] Completed task with tag #task @computer

## Project B
- [ ] Another task with tag #task @calls
- Some reference text
- [ ] Checkbox without tag
- [ ] Final task with tag #task @home
""")

        # Next-actions file with similar patterns
        next_actions_file = gtd_path / "next-actions.md"
        next_actions_file.write_text("""# Next Actions

## @computer
- [ ] Code review #task @computer
- [ ] Update docs #task @computer
- [ ] Item without tag

## @calls
- [ ] Client call #task @calls
- [ ] Another item without tag
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_projects_file_requires_task_tags(self) -> None:
        """Test that projects file only recognizes items with #task tags."""
        projects_result = self.resource_handler.get_file(
            str(self.vault_path), "gtd/projects.md"
        )

        assert projects_result["status"] == "success"
        projects_data = projects_result["file"]
        assert projects_data["file_type"] == "projects"

        # Should only recognize tasks with #task tag
        tasks = projects_data["tasks"]
        assert len(tasks) == 4  # Only items with #task tag

        task_descriptions = [task["description"] for task in tasks]

        # Items with #task tag should be recognized
        assert any("Task with tag" in desc for desc in task_descriptions)
        assert any("Completed task with tag" in desc for desc in task_descriptions)
        assert any("Another task with tag" in desc for desc in task_descriptions)
        assert any("Final task with tag" in desc for desc in task_descriptions)

        # Items without #task tag should NOT be recognized
        assert not any("Task without tag" in desc for desc in task_descriptions)
        assert not any("Checkbox without tag" in desc for desc in task_descriptions)

    def test_next_actions_file_requires_task_tags(self) -> None:
        """Test that next-actions file only recognizes items with #task tags."""
        next_actions_result = self.resource_handler.get_file(
            str(self.vault_path), "gtd/next-actions.md"
        )

        assert next_actions_result["status"] == "success"
        next_actions_data = next_actions_result["file"]
        assert next_actions_data["file_type"] == "next-actions"

        # Should only recognize tasks with #task tag
        tasks = next_actions_data["tasks"]
        assert len(tasks) == 3  # Only items with #task tag

        task_descriptions = [task["description"] for task in tasks]

        # Items with #task tag should be recognized
        assert any("Code review" in desc for desc in task_descriptions)
        assert any("Update docs" in desc for desc in task_descriptions)
        assert any("Client call" in desc for desc in task_descriptions)

        # Items without #task tag should NOT be recognized
        assert not any("Item without tag" in desc for desc in task_descriptions)
        assert not any("Another item without tag" in desc for desc in task_descriptions)


class TestResourceCompatibilityPhaseAware:
    """Test that MCP resources maintain compatibility with phase-aware recognition."""

    def setup_method(self) -> None:
        """Set up comprehensive GTD vault with phase-aware content."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"

        # Use setup_gtd_vault for proper structure
        setup_result = setup_gtd_vault(str(self.vault_path))
        assert setup_result["status"] == "success"

        # Customize inbox with phase-aware content
        inbox_file = self.vault_path / "gtd" / "inbox.md"
        inbox_file.write_text("""# Inbox

## Pure Capture
- [ ] Call dentist
- [ ] Buy groceries
- [ ] Fix leaky faucet

## Processed
- [ ] Review budget #task @computer
- [ ] Team meeting #task @calls
""")

        # Customize projects with #task requirements
        projects_file = self.vault_path / "gtd" / "projects.md"
        projects_file.write_text("""# Projects

## Active
- [ ] Project task #task @computer
- [ ] Non-task item
- [ ] Another task #task @calls
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_files_resource_shows_phase_aware_task_counts(self) -> None:
        """Test files resource shows correct task counts with phase-aware logic."""
        files_result = self.resource_handler.get_files(str(self.vault_path))

        assert files_result["status"] == "success"

        # Find inbox and projects files
        inbox_file = next(f for f in files_result["files"] if f["file_type"] == "inbox")
        projects_file = next(
            f for f in files_result["files"] if f["file_type"] == "projects"
        )

        # Inbox should show higher task count (all checkbox items)
        assert inbox_file["task_count"] == 5  # All checkbox items

        # Projects should show lower task count (only #task items)
        assert projects_file["task_count"] == 2  # Only items with #task tag

    def test_content_resource_maintains_phase_aware_behavior(self) -> None:
        """Test content resource maintains phase-aware behavior across file types."""
        content_result = self.resource_handler.get_content(str(self.vault_path))

        assert content_result["status"] == "success"

        # Analyze task recognition by file type
        files_by_type: dict[str, dict[str, Any]] = {}
        for file_data in content_result["files"]:
            files_by_type[file_data["file_type"]] = file_data

        # Inbox should recognize all checkbox items
        inbox_data = files_by_type["inbox"]
        assert len(inbox_data["tasks"]) == 5

        # Projects should only recognize #task items
        projects_data = files_by_type["projects"]
        assert len(projects_data["tasks"]) == 2

        # Verify task content matches expectations
        inbox_descriptions = [t["description"] for t in inbox_data["tasks"]]
        assert any("Call dentist" in desc for desc in inbox_descriptions)
        assert any("Review budget" in desc for desc in inbox_descriptions)

        projects_descriptions = [t["description"] for t in projects_data["tasks"]]
        assert any("Project task" in desc for desc in projects_descriptions)
        assert any("Another task" in desc for desc in projects_descriptions)
        assert not any("Non-task item" in desc for desc in projects_descriptions)

    def test_filtered_resources_respect_phase_aware_recognition(self) -> None:
        """Test filtered resources respect phase-aware task recognition."""
        # Test inbox filtering
        inbox_content = self.resource_handler.get_content(
            str(self.vault_path), file_type="inbox"
        )
        assert inbox_content["status"] == "success"
        assert len(inbox_content["files"]) == 1

        inbox_file = inbox_content["files"][0]
        assert inbox_file["file_type"] == "inbox"
        assert len(inbox_file["tasks"]) == 5  # All checkbox items

        # Test projects filtering
        projects_content = self.resource_handler.get_content(
            str(self.vault_path), file_type="projects"
        )
        assert projects_content["status"] == "success"
        assert len(projects_content["files"]) == 1

        projects_file = projects_content["files"][0]
        assert projects_file["file_type"] == "projects"
        assert len(projects_file["tasks"]) == 2  # Only #task items


class TestResourceCachingPhaseAware:
    """Test that resource caching works correctly with phase-aware recognition."""

    def setup_method(self) -> None:
        """Set up test environment for caching tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create inbox with phase-aware content
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text("""# Inbox
- [ ] Task 1
- [ ] Task 2 #task
- [ ] Task 3
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_resource_idempotent_behavior_phase_aware(self) -> None:
        """Test that resources return identical results on repeated calls."""
        # First call
        result1 = self.resource_handler.get_file(str(self.vault_path), "gtd/inbox.md")

        # Second call
        result2 = self.resource_handler.get_file(str(self.vault_path), "gtd/inbox.md")

        # Results should be identical (idempotent)
        assert result1 == result2
        assert result1["status"] == "success"
        assert len(result1["file"]["tasks"]) == 3  # All checkbox items in inbox

    def test_resource_consistency_across_access_patterns(self) -> None:
        """Test consistency between different resource access patterns."""
        # Access via single file resource
        single_file_result = self.resource_handler.get_file(
            str(self.vault_path), "gtd/inbox.md"
        )

        # Access via content resource
        content_result = self.resource_handler.get_content(
            str(self.vault_path), file_type="inbox"
        )

        # Data should be consistent
        assert single_file_result["status"] == "success"
        assert content_result["status"] == "success"

        single_file_data = single_file_result["file"]
        content_file_data = content_result["files"][0]

        # Task counts should match
        assert len(single_file_data["tasks"]) == len(content_file_data["tasks"])
        assert len(single_file_data["tasks"]) == 3  # All checkbox items

        # Task content should match
        single_descriptions = {t["description"] for t in single_file_data["tasks"]}
        content_descriptions = {t["description"] for t in content_file_data["tasks"]}
        assert single_descriptions == content_descriptions


class TestResourceURICompatibilityPhaseAware:
    """Test that resource URIs work correctly with phase-aware recognition."""

    def setup_method(self) -> None:
        """Set up test environment for URI compatibility tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Multiple file types with different recognition patterns
        files_content = {
            "inbox.md": """# Inbox
- [ ] Capture item 1
- [ ] Capture item 2
- [ ] Processed item #task
""",
            "projects.md": """# Projects
- [ ] Project task #task @computer
- [ ] Non-task item
""",
            "next-actions.md": """# Next Actions
- [ ] Action 1 #task @computer
- [ ] Action 2 #task @calls
""",
        }

        for filename, content in files_content.items():
            (gtd_path / filename).write_text(content)

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_uri_parsing_compatibility_phase_aware(self) -> None:
        """Test that URI parsing works with phase-aware file access."""
        vault_path = str(self.vault_path)

        # Test files URI parsing
        files_uri = f"gtd://{vault_path}/files"
        files_parsed = self.resource_handler.parse_files_uri(files_uri)
        assert files_parsed["vault_path"] == vault_path
        assert files_parsed["file_type"] is None

        # Test filtered files URI parsing
        inbox_files_uri = f"gtd://{vault_path}/files/inbox"
        inbox_parsed = self.resource_handler.parse_files_uri(inbox_files_uri)
        assert inbox_parsed["vault_path"] == vault_path
        assert inbox_parsed["file_type"] == "inbox"

        # Test file URI parsing
        file_uri = f"gtd://{vault_path}/file/gtd/inbox.md"
        file_parsed = self.resource_handler.parse_file_uri(file_uri)
        assert file_parsed["vault_path"] == vault_path
        assert file_parsed["file_path"] == "gtd/inbox.md"

    def test_resource_template_consistency_phase_aware(self) -> None:
        """Test all resource templates work consistently with phase-aware logic."""
        vault_path = str(self.vault_path)

        # Test each resource template

        # 1. Files resource (metadata only)
        files_result = self.resource_handler.get_files(vault_path)
        assert files_result["status"] == "success"
        assert len(files_result["files"]) == 3

        # 2. Files filtered resource
        inbox_files_result = self.resource_handler.get_files(
            vault_path, file_type="inbox"
        )
        assert inbox_files_result["status"] == "success"
        assert len(inbox_files_result["files"]) == 1
        assert inbox_files_result["files"][0]["task_count"] == 3  # All checkbox items

        # 3. Single file resource
        inbox_file_result = self.resource_handler.get_file(vault_path, "gtd/inbox.md")
        assert inbox_file_result["status"] == "success"
        assert len(inbox_file_result["file"]["tasks"]) == 3

        # 4. Content resource (full content)
        content_result = self.resource_handler.get_content(vault_path)
        assert content_result["status"] == "success"
        assert len(content_result["files"]) == 3

        # 5. Content filtered resource
        projects_content_result = self.resource_handler.get_content(
            vault_path, file_type="projects"
        )
        assert projects_content_result["status"] == "success"
        assert len(projects_content_result["files"]) == 1
        assert (
            len(projects_content_result["files"][0]["tasks"]) == 1
        )  # Only #task items
