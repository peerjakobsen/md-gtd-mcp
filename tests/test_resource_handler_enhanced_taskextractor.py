"""Tests for ResourceHandler methods with enhanced TaskExtractor integration.

This module specifically tests the integration between ResourceHandler and the
enhanced TaskExtractor that implements file-type aware task recognition.

Focuses on verifying that ResourceHandler methods (get_file, get_files, get_content)
correctly pass file_type information to TaskExtractor and handle the enhanced
task recognition behavior appropriately.

Tests cover:
- Inbox files showing enhanced task parsing without #task tags
- Non-inbox files maintaining #task requirements
- Batch content operations maintaining correct behavior per file type
- ResourceHandler URI handling with phase-aware files
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

from md_gtd_mcp.services.resource_handler import ResourceHandler


class TestResourceHandlerEnhancedTaskExtractor:
    """Test ResourceHandler integration with enhanced TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test environment with ResourceHandler."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()


class TestGetFileMethodWithEnhancedTaskExtractor:
    """Test ResourceHandler.get_file() with enhanced TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test with phase-aware files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create inbox.md that should recognize all checkbox items
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text("""# Inbox

- [ ] Pure capture item 1
- [ ] Pure capture item 2
- [ ] Processed item #task @computer
- [x] Completed capture item
- [ ] Another capture item

Some text content here.
""")

        # Create projects.md that should only recognize #task items
        projects_file = gtd_path / "projects.md"
        projects_file.write_text("""# Projects

## Project A
- [ ] Task with tag #task @computer
- [ ] Item without tag (not a task)
- [x] Completed task #task @computer

## Project B
- [ ] Another tagged task #task @calls
- Some reference content
- [ ] Untagged checkbox item
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_get_file_inbox_shows_enhanced_parsing(self) -> None:
        """Test get_file shows enhanced task parsing for inbox files."""
        result = self.resource_handler.get_file(str(self.vault_path), "gtd/inbox.md")

        assert result["status"] == "success"
        file_data = result["file"]
        assert file_data["file_type"] == "inbox"

        # Should recognize ALL checkbox items (5 total)
        tasks = file_data["tasks"]
        assert len(tasks) == 5

        # Verify specific task recognition
        task_descriptions = [task["description"] for task in tasks]
        assert any("Pure capture item 1" in desc for desc in task_descriptions)
        assert any("Pure capture item 2" in desc for desc in task_descriptions)
        assert any("Processed item" in desc for desc in task_descriptions)
        assert any("Completed capture item" in desc for desc in task_descriptions)
        assert any("Another capture item" in desc for desc in task_descriptions)

        # Verify completion status is correctly parsed
        completed_tasks = [task for task in tasks if task["completed"]]
        assert len(completed_tasks) == 1
        assert "Completed capture item" in completed_tasks[0]["description"]

    def test_get_file_projects_maintains_task_requirements(self) -> None:
        """Test get_file maintains #task requirements for projects files."""
        result = self.resource_handler.get_file(str(self.vault_path), "gtd/projects.md")

        assert result["status"] == "success"
        file_data = result["file"]
        assert file_data["file_type"] == "projects"

        # Should only recognize items with #task tag (3 total)
        tasks = file_data["tasks"]
        assert len(tasks) == 3

        # Verify only tagged tasks are recognized
        task_descriptions = [task["description"] for task in tasks]
        assert any("Task with tag" in desc for desc in task_descriptions)
        assert any("Completed task" in desc for desc in task_descriptions)
        assert any("Another tagged task" in desc for desc in task_descriptions)

        # Verify untagged items are NOT recognized
        assert not any("Item without tag" in desc for desc in task_descriptions)
        assert not any("Untagged checkbox item" in desc for desc in task_descriptions)

        # Verify task metadata is properly extracted
        for task in tasks:
            assert "#task" in task["tags"]
            assert task["context"] in ["@computer", "@calls"]

    def test_get_file_passes_correct_file_type_to_taskextractor(self) -> None:
        """Test that get_file correctly passes file_type to TaskExtractor."""
        with patch(
            "md_gtd_mcp.parsers.markdown_parser.TaskExtractor.extract_tasks"
        ) as mock_extract:
            # Mock TaskExtractor to verify file_type is passed correctly
            mock_extract.return_value = []

            result = self.resource_handler.get_file(
                str(self.vault_path), "gtd/inbox.md"
            )

            assert result["status"] == "success"
            # Verify TaskExtractor.extract_tasks was called with file_type
            mock_extract.assert_called_once()
            call_args = mock_extract.call_args

            # Check that file_type "inbox" was passed as the second argument
            assert len(call_args[0]) == 2  # content and file_type as positional args
            assert (
                call_args[0][1] == "inbox"
            )  # file_type passed as second positional arg


class TestGetFilesMethodWithEnhancedTaskExtractor:
    """Test ResourceHandler.get_files() with enhanced TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test with multiple file types."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Multiple files with different recognition patterns
        files_content = {
            "inbox.md": """# Inbox
- [ ] Capture 1
- [ ] Capture 2
- [ ] Tagged item #task
""",
            "projects.md": """# Projects
- [ ] Project task #task @computer
- [ ] Non-task item
- [ ] Another task #task @calls
""",
            "next-actions.md": """# Next Actions
- [ ] Action 1 #task @computer
- [ ] Action 2 #task @calls
- [ ] Untagged action
""",
        }

        for filename, content in files_content.items():
            (gtd_path / filename).write_text(content)

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_get_files_shows_correct_task_counts_per_file_type(self) -> None:
        """Test get_files shows correct task counts based on file type recognition."""
        result = self.resource_handler.get_files(str(self.vault_path))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) == 3

        # Create lookup by file type
        files_by_type = {f["file_type"]: f for f in files}

        # Inbox should show higher task count (all checkbox items)
        inbox_file = files_by_type["inbox"]
        assert inbox_file["task_count"] == 3  # All checkbox items

        # Projects should show lower task count (only #task items)
        projects_file = files_by_type["projects"]
        assert projects_file["task_count"] == 2  # Only items with #task tag

        # Next-actions should show lower task count (only #task items)
        next_actions_file = files_by_type["next-actions"]
        assert next_actions_file["task_count"] == 2  # Only items with #task tag

    def test_get_files_filtered_respects_file_type_recognition(self) -> None:
        """Test get_files with filtering respects file type recognition."""
        # Test inbox filtering
        inbox_result = self.resource_handler.get_files(
            str(self.vault_path), file_type="inbox"
        )

        assert inbox_result["status"] == "success"
        assert len(inbox_result["files"]) == 1

        inbox_file = inbox_result["files"][0]
        assert inbox_file["file_type"] == "inbox"
        assert inbox_file["task_count"] == 3  # All checkbox items

        # Test projects filtering
        projects_result = self.resource_handler.get_files(
            str(self.vault_path), file_type="projects"
        )

        assert projects_result["status"] == "success"
        assert len(projects_result["files"]) == 1

        projects_file = projects_result["files"][0]
        assert projects_file["file_type"] == "projects"
        assert projects_file["task_count"] == 2  # Only #task items

    def test_get_files_summary_reflects_enhanced_recognition(self) -> None:
        """Test get_files summary statistics reflect enhanced task recognition."""
        result = self.resource_handler.get_files(str(self.vault_path))

        assert result["status"] == "success"
        summary = result["summary"]

        # Total tasks should reflect enhanced recognition
        # inbox: 3, projects: 2, next-actions: 2 = 7 total
        assert summary["total_tasks"] == 7

        # Tasks by type should be accurate
        tasks_by_type = summary["tasks_by_type"]
        assert tasks_by_type.get("inbox", 0) == 3  # All checkbox items
        assert tasks_by_type.get("projects", 0) == 2  # Only #task items
        assert tasks_by_type.get("next-actions", 0) == 2  # Only #task items


class TestGetContentMethodWithEnhancedTaskExtractor:
    """Test ResourceHandler.get_content() with enhanced TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test with comprehensive content."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create files with different task recognition needs
        files_content = {
            "inbox.md": """# Inbox

## Rapid Capture
- [ ] Call doctor
- [ ] Buy milk
- [ ] Review proposal #task @computer

## Meeting Notes
- [ ] Follow up with client
- [ ] Send thank you note
""",
            "projects.md": """# Projects

## Work Projects
- [ ] Website redesign #task @computer
- [ ] Team meeting prep #task @calls
- [ ] Reference material (not a task)

## Personal Projects
- [ ] Home renovation #task @home
- [ ] Vacation planning notes
""",
            "waiting-for.md": """# Waiting For

- [ ] Response from vendor #waiting
- [ ] Insurance claim update #waiting
- [ ] Not a waiting item (just reference)
""",
        }

        for filename, content in files_content.items():
            (gtd_path / filename).write_text(content)

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_get_content_maintains_file_type_behavior(self) -> None:
        """Test get_content maintains correct behavior per file type."""
        result = self.resource_handler.get_content(str(self.vault_path))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) == 3

        # Organize by file type for analysis
        files_by_type = {f["file_type"]: f for f in files}

        # Inbox should recognize all checkbox items
        inbox_data = files_by_type["inbox"]
        assert len(inbox_data["tasks"]) == 5  # All checkbox items

        inbox_descriptions = [t["description"] for t in inbox_data["tasks"]]
        assert any("Call doctor" in desc for desc in inbox_descriptions)
        assert any("Buy milk" in desc for desc in inbox_descriptions)
        assert any("Review proposal" in desc for desc in inbox_descriptions)
        assert any("Follow up with client" in desc for desc in inbox_descriptions)
        assert any("Send thank you note" in desc for desc in inbox_descriptions)

        # Projects should only recognize #task items
        projects_data = files_by_type["projects"]
        assert len(projects_data["tasks"]) == 3  # Only #task items

        projects_descriptions = [t["description"] for t in projects_data["tasks"]]
        assert any("Website redesign" in desc for desc in projects_descriptions)
        assert any("Team meeting prep" in desc for desc in projects_descriptions)
        assert any("Home renovation" in desc for desc in projects_descriptions)
        assert not any("Reference material" in desc for desc in projects_descriptions)
        assert not any("Vacation planning" in desc for desc in projects_descriptions)

        # Waiting-for should not recognize any items (has #waiting, not #task)
        waiting_data = files_by_type["waiting-for"]
        assert len(waiting_data["tasks"]) == 0  # No #task items

    def test_get_content_filtered_by_file_type(self) -> None:
        """Test get_content with file_type filtering maintains correct recognition."""
        # Test inbox content filtering
        inbox_result = self.resource_handler.get_content(
            str(self.vault_path), file_type="inbox"
        )

        assert inbox_result["status"] == "success"
        assert len(inbox_result["files"]) == 1

        inbox_file = inbox_result["files"][0]
        assert inbox_file["file_type"] == "inbox"
        assert len(inbox_file["tasks"]) == 5  # All checkbox items

        # Test projects content filtering
        projects_result = self.resource_handler.get_content(
            str(self.vault_path), file_type="projects"
        )

        assert projects_result["status"] == "success"
        assert len(projects_result["files"]) == 1

        projects_file = projects_result["files"][0]
        assert projects_file["file_type"] == "projects"
        assert len(projects_file["tasks"]) == 3  # Only #task items

    def test_get_content_task_metadata_consistency(self) -> None:
        """Test get_content maintains task metadata consistency across file types."""
        result = self.resource_handler.get_content(str(self.vault_path))

        assert result["status"] == "success"

        # Check task metadata structure for each file type
        for file_data in result["files"]:
            for task in file_data["tasks"]:
                # All tasks should have required fields
                assert "description" in task
                assert "completed" in task
                assert "raw_text" in task
                assert "line_number" in task
                assert "tags" in task
                assert "context" in task

                # Verify line numbers are positive
                assert task["line_number"] > 0

                # Verify completion status is boolean
                assert isinstance(task["completed"], bool)


class TestBatchContentOperationsEnhanced:
    """Test batch content operations with enhanced TaskExtractor."""

    def setup_method(self) -> None:
        """Set up test with multiple files for batch operations."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create contexts folder with context files
        contexts_path = gtd_path / "contexts"
        contexts_path.mkdir()

        # Context files should follow same pattern as other non-inbox files
        context_files = {
            "@computer.md": """# @computer Context

```tasks
not done
context includes @computer
```

- [ ] Context task #task @computer
- [ ] Non-task item
""",
            "@calls.md": """# @calls Context

```tasks
not done
context includes @calls
```

- [ ] Call task #task @calls
- [ ] Another call task #task @calls
""",
        }

        for filename, content in context_files.items():
            (contexts_path / filename).write_text(content)

        # Standard GTD files
        (gtd_path / "inbox.md").write_text("""# Inbox
- [ ] Inbox item 1
- [ ] Inbox item 2
""")

        (gtd_path / "projects.md").write_text("""# Projects
- [ ] Project task #task @computer
""")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_batch_operations_maintain_file_type_behavior(self) -> None:
        """Test batch operations maintain correct behavior per file type."""
        result = self.resource_handler.get_content(str(self.vault_path))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 4  # inbox, projects, 2 context files

        # Verify each file type behaves correctly
        for file_data in files:
            file_type = file_data["file_type"]
            tasks = file_data["tasks"]

            if file_type == "inbox":
                # Inbox should recognize all checkbox items
                assert len(tasks) == 2
            elif file_type == "projects":
                # Projects should only recognize #task items
                assert len(tasks) == 1
            elif file_type == "context":
                # Context files should only recognize #task items
                # Should not extract tasks from ```tasks query blocks
                task_descriptions = [t["description"] for t in tasks]
                if "computer" in file_data["file_path"]:
                    assert len(tasks) == 1
                    assert any("Context task" in desc for desc in task_descriptions)
                elif "calls" in file_data["file_path"]:
                    assert len(tasks) == 2
                    assert any("Call task" in desc for desc in task_descriptions)

    def test_batch_operations_with_filtering(self) -> None:
        """Test batch operations with file type filtering."""
        # Test context files filtering
        context_result = self.resource_handler.get_content(
            str(self.vault_path), file_type="context"
        )

        assert context_result["status"] == "success"
        context_files = context_result["files"]
        assert len(context_files) == 2

        # All should be context files
        for file_data in context_files:
            assert file_data["file_type"] == "context"

            # Should only have tasks with #task tags, not query blocks
            for task in file_data["tasks"]:
                assert "#task" in task["tags"]
                assert "@" in task["context"]  # Should have context

    def test_batch_operations_summary_accuracy(self) -> None:
        """Test batch operations produce accurate summary statistics."""
        result = self.resource_handler.get_content(str(self.vault_path))

        assert result["status"] == "success"

        # Calculate expected totals
        expected_tasks = 0
        for file_data in result["files"]:
            expected_tasks += len(file_data["tasks"])

        # Summary should match calculated totals
        summary = result["summary"]
        assert summary["total_tasks"] == expected_tasks
        assert summary["total_files"] == len(result["files"])

        # Verify files by type breakdown
        files_by_type = summary["files_by_type"]
        assert files_by_type.get("inbox", 0) == 1
        assert files_by_type.get("projects", 0) == 1
        assert files_by_type.get("context", 0) == 2
