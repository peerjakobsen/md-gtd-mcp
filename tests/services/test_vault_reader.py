"""Tests for VaultReader service."""

import tempfile
from pathlib import Path

import pytest

from md_gtd_mcp.models import VaultConfig
from md_gtd_mcp.services.vault_reader import VaultReader


class TestVaultReader:
    """Test VaultReader service for reading GTD vaults."""

    def setup_method(self) -> None:
        """Set up test vault structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.vault_config = VaultConfig(self.vault_path)

        # Create vault directory structure
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_config.get_gtd_path()
        gtd_path.mkdir(parents=True)

        # Create contexts folder
        contexts_path = self.vault_config.get_contexts_path()
        contexts_path.mkdir(parents=True)

        # Create sample GTD files
        self._create_sample_files()

    def _create_sample_files(self) -> None:
        """Create sample GTD files for testing."""
        # Inbox file
        inbox_content = """---
status: active
---

# Inbox

## Quick Capture

- [ ] Call dentist @calls #task
- [ ] Buy groceries @errands #task
- [ ] Research vacation options #task

## Notes

Check [[Project Alpha]] status.
"""
        self.vault_config.get_inbox_path().write_text(inbox_content)

        # Projects file
        projects_content = """---
status: active
---

# Projects

## Active Projects

### [[Project Alpha]]
- outcome: Complete product launch
- status: active
- review_date: 2025-03-01

### [[Home Office Setup]]
- outcome: Organize workspace
- status: active
- area: Personal
"""
        self.vault_config.get_projects_path().write_text(projects_content)

        # Next Actions file
        next_actions_content = """---
status: active
---

# Next Actions

## Work

- [ ] Draft project proposal @computer #task
- [ ] Schedule team meeting @calls #task
- [x] Review code changes ✅2025-01-05 #task

## Personal

- [ ] Schedule doctor appointment @calls #task
- [ ] Fix kitchen faucet @home #task
"""
        self.vault_config.get_next_actions_path().write_text(next_actions_content)

        # Waiting For file
        waiting_for_content = """---
status: active
---

# Waiting For

## Work Items

- [ ] Approval from manager 👤 John Smith #waiting
- [ ] Budget approval 👤 Finance Team #waiting

## Personal Items

- [ ] Package delivery 👤 UPS #waiting
"""
        self.vault_config.get_waiting_for_path().write_text(waiting_for_content)

        # Someday Maybe file
        someday_content = """---
status: someday
---

# Someday / Maybe

## Future Projects

- [ ] Learn Spanish language #someday
- [ ] Build home workshop #someday
- [ ] Write a book #someday

## Travel Ideas

Check out [[Travel Bucket List]] for inspiration.
Visit [National Parks](https://www.nps.gov) website.
"""
        self.vault_config.get_someday_maybe_path().write_text(someday_content)

        # Context files
        calls_context = """---
context: calls
---

# @calls

## Work Calls

- [ ] Call client about project update #task
- [ ] Schedule quarterly review #task

## Personal Calls

- [ ] Call insurance company #task
- [ ] Schedule dentist appointment #task
"""
        (self.vault_config.get_contexts_path() / "@calls.md").write_text(calls_context)

        computer_context = """---
context: computer
---

# @computer

## Development Tasks

- [ ] Refactor authentication module #task
- [ ] Update project documentation #task
- [ ] Review pull requests #task

## Admin Tasks

- [ ] Update system backups #task
"""
        (self.vault_config.get_contexts_path() / "@computer.md").write_text(
            computer_context
        )

        errands_context = """---
context: errands
---

# @errands

## Shopping

- [ ] Buy office supplies #task
- [ ] Pick up dry cleaning #task
- [ ] Get groceries for dinner #task

## Appointments

- [ ] Drop off tax documents #task
"""
        (self.vault_config.get_contexts_path() / "@errands.md").write_text(
            errands_context
        )

    def test_read_gtd_file_success(self) -> None:
        """Test reading a single GTD file successfully."""
        reader = VaultReader(self.vault_config)

        gtd_file = reader.read_gtd_file(self.vault_config.get_inbox_path())

        assert gtd_file.title == "Inbox"
        assert gtd_file.file_type == "inbox"
        assert gtd_file.frontmatter.status == "active"
        assert len(gtd_file.tasks) == 3  # Only tasks with #task tag
        assert len(gtd_file.links) >= 3  # @calls, @errands, [[Project Alpha]]

    def test_read_gtd_file_not_found(self) -> None:
        """Test reading non-existent GTD file."""
        reader = VaultReader(self.vault_config)

        with pytest.raises(FileNotFoundError):
            reader.read_gtd_file(Path("non_existent.md"))

    def test_read_gtd_file_invalid_path(self) -> None:
        """Test reading file outside GTD folder structure."""
        reader = VaultReader(self.vault_config)

        # Create file outside GTD folder
        outside_file = self.vault_path / "outside.md"
        outside_file.write_text("# Outside File\n\nNot a GTD file.")

        with pytest.raises(ValueError, match="not within GTD folder"):
            reader.read_gtd_file(outside_file)

    def test_list_gtd_files(self) -> None:
        """Test listing all GTD files in vault."""
        reader = VaultReader(self.vault_config)

        gtd_files = reader.list_gtd_files()

        # Should include all standard GTD files plus context files
        assert len(gtd_files) >= 8  # 5 standard + 3 context files

        # Check standard files are included
        file_paths = [gtd_file.path for gtd_file in gtd_files]
        assert str(self.vault_config.get_inbox_path()) in file_paths
        assert str(self.vault_config.get_projects_path()) in file_paths
        assert str(self.vault_config.get_next_actions_path()) in file_paths
        assert str(self.vault_config.get_waiting_for_path()) in file_paths
        assert str(self.vault_config.get_someday_maybe_path()) in file_paths

        # Check context files are included
        calls_path = str(self.vault_config.get_contexts_path() / "@calls.md")
        computer_path = str(self.vault_config.get_contexts_path() / "@computer.md")
        errands_path = str(self.vault_config.get_contexts_path() / "@errands.md")

        assert calls_path in file_paths
        assert computer_path in file_paths
        assert errands_path in file_paths

    def test_list_gtd_files_by_type(self) -> None:
        """Test listing GTD files filtered by file type."""
        reader = VaultReader(self.vault_config)

        # Test filtering by inbox type
        inbox_files = reader.list_gtd_files(file_type="inbox")
        assert len(inbox_files) == 1
        assert inbox_files[0].file_type == "inbox"

        # Test filtering by context type
        context_files = reader.list_gtd_files(file_type="context")
        assert len(context_files) == 3
        for context_file in context_files:
            assert context_file.file_type == "context"

        # Test filtering by projects type
        project_files = reader.list_gtd_files(file_type="projects")
        assert len(project_files) == 1
        assert project_files[0].file_type == "projects"

    def test_read_all_gtd_files(self) -> None:
        """Test reading all GTD files in vault."""
        reader = VaultReader(self.vault_config)

        all_files = reader.read_all_gtd_files()

        assert len(all_files) >= 8  # 5 standard + 3 context files

        # Check that each file type is represented
        file_types = {gtd_file.file_type for gtd_file in all_files}
        expected_types = {
            "inbox",
            "projects",
            "next-actions",
            "waiting-for",
            "someday-maybe",
            "context",
        }
        assert expected_types.issubset(file_types)

        # Verify each file has been properly parsed
        for gtd_file in all_files:
            assert gtd_file.title is not None
            assert gtd_file.content is not None
            assert gtd_file.raw_content is not None
            assert gtd_file.file_type is not None

    def test_inbox_file_parsing(self) -> None:
        """Test specific parsing of inbox file."""
        reader = VaultReader(self.vault_config)

        inbox_file = reader.read_gtd_file(self.vault_config.get_inbox_path())

        assert inbox_file.title == "Inbox"
        assert inbox_file.file_type == "inbox"
        assert inbox_file.frontmatter.status == "active"

        # Check tasks extraction
        tasks = inbox_file.tasks
        assert len(tasks) == 3

        # Verify specific tasks
        task_texts = [task.text for task in tasks]
        assert "Call dentist" in " ".join(task_texts)
        assert "Buy groceries" in " ".join(task_texts)
        assert "Research vacation options" in " ".join(task_texts)

        # Check context links
        context_links = [
            link for link in inbox_file.links if link.target.startswith("@")
        ]
        assert len(context_links) >= 2  # @calls, @errands

    def test_projects_file_parsing(self) -> None:
        """Test specific parsing of projects file."""
        reader = VaultReader(self.vault_config)

        projects_file = reader.read_gtd_file(self.vault_config.get_projects_path())

        assert projects_file.title == "Projects"
        assert projects_file.file_type == "projects"
        assert projects_file.frontmatter.status == "active"

        # Check wikilinks to projects
        project_links = [
            link
            for link in projects_file.links
            if not link.target.startswith(("@", "http"))
        ]
        assert len(project_links) >= 2  # Project Alpha, Home Office Setup

    def test_next_actions_file_parsing(self) -> None:
        """Test specific parsing of next-actions file."""
        reader = VaultReader(self.vault_config)

        next_actions_file = reader.read_gtd_file(
            self.vault_config.get_next_actions_path()
        )

        assert next_actions_file.title == "Next Actions"
        assert next_actions_file.file_type == "next-actions"

        # Should have both completed and incomplete tasks
        tasks = next_actions_file.tasks
        assert len(tasks) == 5

        completed_tasks = [task for task in tasks if task.is_completed]
        assert len(completed_tasks) == 1

        incomplete_tasks = [task for task in tasks if not task.is_completed]
        assert len(incomplete_tasks) == 4

    def test_waiting_for_file_parsing(self) -> None:
        """Test specific parsing of waiting-for file."""
        reader = VaultReader(self.vault_config)

        waiting_file = reader.read_gtd_file(self.vault_config.get_waiting_for_path())

        assert waiting_file.title == "Waiting For"
        assert waiting_file.file_type == "waiting-for"

        # Note: waiting items have #waiting tag, not #task tag
        # So they won't be extracted as tasks by TaskExtractor
        # This is expected behavior based on GTD categorization

    def test_someday_file_parsing(self) -> None:
        """Test specific parsing of someday-maybe file."""
        reader = VaultReader(self.vault_config)

        someday_file = reader.read_gtd_file(self.vault_config.get_someday_maybe_path())

        assert someday_file.title == "Someday / Maybe"
        assert someday_file.file_type == "someday-maybe"
        assert someday_file.frontmatter.status == "someday"

        # Check links
        links = someday_file.links
        assert len(links) >= 2  # Travel Bucket List, National Parks website

        # Check for external link
        external_links = [link for link in links if link.is_external]
        assert len(external_links) >= 1

    def test_context_calls_file_parsing(self) -> None:
        """Test specific parsing of @calls context file."""
        reader = VaultReader(self.vault_config)

        calls_path = self.vault_config.get_contexts_path() / "@calls.md"
        calls_file = reader.read_gtd_file(calls_path)

        assert calls_file.title == "@calls"
        assert calls_file.file_type == "context"
        assert calls_file.frontmatter.extra.get("context") == "calls"

        # Check tasks
        tasks = calls_file.tasks
        assert len(tasks) == 4

        # All tasks should be related to calling
        for task in tasks:
            assert any(
                keyword in task.text.lower()
                for keyword in ["call", "schedule", "appointment"]
            )

    def test_context_computer_file_parsing(self) -> None:
        """Test specific parsing of @computer context file."""
        reader = VaultReader(self.vault_config)

        computer_path = self.vault_config.get_contexts_path() / "@computer.md"
        computer_file = reader.read_gtd_file(computer_path)

        assert computer_file.title == "@computer"
        assert computer_file.file_type == "context"
        assert computer_file.frontmatter.extra.get("context") == "computer"

        # Check tasks
        tasks = computer_file.tasks
        assert len(tasks) == 4

        # Tasks should be computer-related
        task_texts = " ".join(task.text for task in tasks).lower()
        assert any(
            keyword in task_texts
            for keyword in ["refactor", "documentation", "review", "update"]
        )

    def test_context_errands_file_parsing(self) -> None:
        """Test specific parsing of @errands context file."""
        reader = VaultReader(self.vault_config)

        errands_path = self.vault_config.get_contexts_path() / "@errands.md"
        errands_file = reader.read_gtd_file(errands_path)

        assert errands_file.title == "@errands"
        assert errands_file.file_type == "context"
        assert errands_file.frontmatter.extra.get("context") == "errands"

        # Check tasks
        tasks = errands_file.tasks
        assert len(tasks) == 4

        # Tasks should be errands-related
        task_texts = " ".join(task.text for task in tasks).lower()
        assert any(
            keyword in task_texts for keyword in ["buy", "pick up", "get", "drop off"]
        )

    def test_vault_reader_with_missing_files(self) -> None:
        """Test VaultReader behavior when some GTD files are missing."""
        # Remove some files
        self.vault_config.get_someday_maybe_path().unlink()
        (self.vault_config.get_contexts_path() / "@calls.md").unlink()

        reader = VaultReader(self.vault_config)

        # list_gtd_files should only return existing files
        gtd_files = reader.list_gtd_files()
        file_paths = [gtd_file.path for gtd_file in gtd_files]

        assert str(self.vault_config.get_someday_maybe_path()) not in file_paths
        assert (
            str(self.vault_config.get_contexts_path() / "@calls.md") not in file_paths
        )

        # Other files should still be present
        assert str(self.vault_config.get_inbox_path()) in file_paths
        assert str(self.vault_config.get_projects_path()) in file_paths

    def test_vault_reader_integration_with_parsers(self) -> None:
        """Test integration between VaultReader and all parser components."""
        reader = VaultReader(self.vault_config)

        # Read all files and verify parser integration
        all_files = reader.read_all_gtd_files()

        for gtd_file in all_files:
            # Verify MarkdownParser integration
            assert hasattr(gtd_file, "frontmatter")
            assert hasattr(gtd_file, "raw_content")

            # Verify TaskExtractor integration
            assert hasattr(gtd_file, "tasks")
            assert isinstance(gtd_file.tasks, list)

            # Verify LinkExtractor integration
            assert hasattr(gtd_file, "links")
            assert isinstance(gtd_file.links, list)

            # Verify file type detection
            assert gtd_file.file_type in {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }

    def test_vault_reader_error_handling(self) -> None:
        """Test VaultReader error handling scenarios."""
        reader = VaultReader(self.vault_config)

        # Test with corrupted file content
        corrupted_path = self.vault_config.get_gtd_path() / "corrupted.md"
        corrupted_path.write_text("---\ninvalid: yaml: [content\n---\n# Corrupted")

        # Should handle malformed YAML gracefully
        gtd_file = reader.read_gtd_file(corrupted_path)
        assert gtd_file.title == "Corrupted"
        # Frontmatter parsing should fail gracefully
