"""Tests for MCP server tools."""

import tempfile
from pathlib import Path

import pytest

from md_gtd_mcp.server import read_gtd_file_impl as read_gtd_file
from md_gtd_mcp.services.vault_setup import setup_gtd_vault


class TestSetupGTDVault:
    """Test setup_gtd_vault MCP tool."""

    def setup_method(self) -> None:
        """Set up test vault directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"

    def test_setup_gtd_vault_empty_directory(self) -> None:
        """Test creating complete GTD structure in empty vault."""
        # Create empty vault directory
        self.vault_path.mkdir(parents=True)

        result = setup_gtd_vault(str(self.vault_path))

        # Verify response structure
        assert "status" in result
        assert "created" in result
        assert "already_existed" in result
        assert "vault_path" in result
        assert result["status"] == "success"
        assert result["vault_path"] == str(self.vault_path)

        # Check that GTD folder was created
        gtd_path = self.vault_path / "gtd"
        assert gtd_path.exists()
        assert "gtd/" in result["created"]

        # Check standard GTD files were created
        expected_files = [
            "gtd/inbox.md",
            "gtd/projects.md",
            "gtd/next-actions.md",
            "gtd/waiting-for.md",
            "gtd/someday-maybe.md",
        ]

        for file_path in expected_files:
            full_path = self.vault_path / file_path
            assert full_path.exists(), f"{file_path} was not created"
            assert file_path in result["created"]

        # Check contexts folder was created
        contexts_path = gtd_path / "contexts"
        assert contexts_path.exists()
        assert "gtd/contexts/" in result["created"]

        # Check context files were created with query syntax
        context_files = ["@calls.md", "@computer.md", "@errands.md", "@home.md"]
        for context_file in context_files:
            context_path = contexts_path / context_file
            assert context_path.exists(), f"Context file {context_file} was not created"
            assert f"gtd/contexts/{context_file}" in result["created"]

            # Verify content contains Obsidian Tasks query syntax
            content = context_path.read_text()
            assert "```tasks" in content
            assert "not done" in content
            assert f"description includes @{context_file[1:-3]}" in content
            assert "sort by due" in content
            assert "```" in content

        # Verify no files were marked as already existed
        assert len(result["already_existed"]) == 0

    def test_setup_gtd_vault_nonexistent_directory(self) -> None:
        """Test creating GTD structure when vault directory doesn't exist."""
        result = setup_gtd_vault(str(self.vault_path))

        # Should create the vault directory and all GTD structure
        assert self.vault_path.exists()
        assert result["status"] == "success"
        assert str(self.vault_path) in result["created"]

    def test_setup_gtd_vault_existing_files_not_overwritten(self) -> None:
        """CRITICAL TEST: Ensure existing files are never overwritten."""
        # Create vault structure
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        contexts_path = gtd_path / "contexts"
        contexts_path.mkdir()

        # Create some existing files with custom content
        existing_inbox = gtd_path / "inbox.md"
        original_content = "# My Custom Inbox\n\n- [ ] Important existing task"
        existing_inbox.write_text(original_content)

        existing_calls = contexts_path / "@calls.md"
        original_calls_content = "# My Custom Calls\n\n- [ ] Existing call task"
        existing_calls.write_text(original_calls_content)

        result = setup_gtd_vault(str(self.vault_path))

        # Verify existing files were not overwritten
        assert result["status"] == "success"
        assert "gtd/inbox.md" in result["already_existed"]
        assert "gtd/contexts/@calls.md" in result["already_existed"]

        # Verify original content is preserved
        assert existing_inbox.read_text() == original_content
        assert existing_calls.read_text() == original_calls_content

        # Verify missing files were still created
        projects_path = gtd_path / "projects.md"
        assert projects_path.exists()
        assert "gtd/projects.md" in result["created"]

        computer_path = contexts_path / "@computer.md"
        assert computer_path.exists()
        assert "gtd/contexts/@computer.md" in result["created"]

    def test_setup_gtd_vault_partial_existing_structure(self) -> None:
        """Test setup when some GTD files and folders already exist."""
        # Create partial structure
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create only inbox and projects files
        inbox_path = gtd_path / "inbox.md"
        inbox_path.write_text("# Existing Inbox")

        projects_path = gtd_path / "projects.md"
        projects_path.write_text("# Existing Projects")

        result = setup_gtd_vault(str(self.vault_path))

        # Check mixed results
        assert result["status"] == "success"

        # Existing files should be preserved
        assert "gtd/inbox.md" in result["already_existed"]
        assert "gtd/projects.md" in result["already_existed"]

        # Missing files should be created
        assert "gtd/next-actions.md" in result["created"]
        assert "gtd/waiting-for.md" in result["created"]
        assert "gtd/someday-maybe.md" in result["created"]
        assert "gtd/contexts/" in result["created"]

        # Verify contexts folder and files were created
        contexts_path = gtd_path / "contexts"
        assert contexts_path.exists()
        for context_file in ["@calls.md", "@computer.md", "@errands.md", "@home.md"]:
            assert (contexts_path / context_file).exists()

    def test_setup_gtd_vault_complete_existing_structure(self) -> None:
        """Test setup when complete GTD structure already exists."""
        # Create complete GTD structure
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        contexts_path = gtd_path / "contexts"
        contexts_path.mkdir()

        # Create all standard files
        standard_files = [
            "inbox.md",
            "projects.md",
            "next-actions.md",
            "waiting-for.md",
            "someday-maybe.md",
        ]
        for file_name in standard_files:
            (gtd_path / file_name).write_text(f"# Existing {file_name}")

        # Create all context files
        context_files = ["@calls.md", "@computer.md", "@errands.md", "@home.md"]
        for context_file in context_files:
            (contexts_path / context_file).write_text(f"# Existing {context_file}")

        result = setup_gtd_vault(str(self.vault_path))

        # Everything should already exist
        assert result["status"] == "success"
        assert len(result["created"]) == 0
        assert (
            len(result["already_existed"]) >= 10
        )  # 5 standard + 4 context + 2 folders

        # Verify files are preserved
        for file_name in standard_files:
            content = (gtd_path / file_name).read_text()
            assert f"# Existing {file_name}" in content

    def test_setup_gtd_vault_context_files_content(self) -> None:
        """Test that context files are created with correct Obsidian Tasks query."""
        self.vault_path.mkdir(parents=True)

        setup_gtd_vault(str(self.vault_path))

        contexts_path = self.vault_path / "gtd" / "contexts"

        # Test @calls.md content
        calls_content = (contexts_path / "@calls.md").read_text()
        assert "# 📞 Calls Context" in calls_content
        assert "```tasks" in calls_content
        assert "not done" in calls_content
        assert "description includes @calls" in calls_content
        assert "sort by due" in calls_content
        assert "```" in calls_content

        # Test @computer.md content
        computer_content = (contexts_path / "@computer.md").read_text()
        assert "# 💻 Computer Context" in computer_content
        assert "description includes @computer" in computer_content

        # Test @errands.md content
        errands_content = (contexts_path / "@errands.md").read_text()
        assert "# 🚗 Errands Context" in errands_content
        assert "description includes @errands" in errands_content

        # Test @home.md content
        home_content = (contexts_path / "@home.md").read_text()
        assert "# 🏠 Home Context" in home_content
        assert "description includes @home" in home_content

    def test_setup_gtd_vault_standard_files_content(self) -> None:
        """Test that standard GTD files are created with appropriate content."""
        self.vault_path.mkdir(parents=True)

        setup_gtd_vault(str(self.vault_path))

        gtd_path = self.vault_path / "gtd"

        # Test inbox.md content
        inbox_content = (gtd_path / "inbox.md").read_text()
        assert "# Inbox" in inbox_content
        assert "## Quick Capture" in inbox_content

        # Test projects.md content
        projects_content = (gtd_path / "projects.md").read_text()
        assert "# Projects" in projects_content
        assert "## Active Projects" in projects_content

        # Test next-actions.md content
        actions_content = (gtd_path / "next-actions.md").read_text()
        assert "# Next Actions" in actions_content

        # Test waiting-for.md content
        waiting_content = (gtd_path / "waiting-for.md").read_text()
        assert "# Waiting For" in waiting_content

        # Test someday-maybe.md content
        someday_content = (gtd_path / "someday-maybe.md").read_text()
        assert "# Someday / Maybe" in someday_content

    def test_setup_gtd_vault_invalid_path(self) -> None:
        """Test error handling for invalid vault paths."""
        with pytest.raises(ValueError, match="Invalid vault path"):
            setup_gtd_vault("")

        with pytest.raises(ValueError, match="Invalid vault path"):
            setup_gtd_vault("   ")

    def test_setup_gtd_vault_permission_error(self) -> None:
        """Test handling of permission errors during setup."""
        # Create a read-only directory to simulate permission error
        readonly_path = Path(self.temp_dir) / "readonly"
        readonly_path.mkdir()
        readonly_path.chmod(0o444)  # Read-only

        try:
            result = setup_gtd_vault(str(readonly_path))
            # Should handle permission error gracefully
            assert result["status"] == "error"
            assert "permission" in result.get("error", "").lower()
        finally:
            # Clean up - restore permissions
            readonly_path.chmod(0o755)


class TestReadGTDFile:
    """Test read_gtd_file MCP tool."""

    def setup_method(self) -> None:
        """Set up test vault directory with sample GTD files."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create a complete GTD structure
        setup_gtd_vault(str(self.vault_path))

        # Add sample content to inbox for testing
        self.gtd_path = self.vault_path / "gtd"
        inbox_path = self.gtd_path / "inbox.md"
        sample_content = """---
status: active
---

# Inbox

## Quick Capture

- Research vacation destinations for spring break
- [ ] Review quarterly budget report @computer #task
- [ ] Confirm meeting attendance with team @calls #task

## Ideas and Notes

Check [[Project Alpha]] status for next steps.
"""
        inbox_path.write_text(sample_content)

    def test_read_gtd_file_success(self) -> None:
        """Test successfully reading a GTD file."""
        inbox_path = str(self.gtd_path / "inbox.md")

        result = read_gtd_file(str(self.vault_path), inbox_path)

        # Verify response structure
        assert "status" in result
        assert "file" in result
        assert "vault_path" in result
        assert result["status"] == "success"
        assert result["vault_path"] == str(self.vault_path)

        # Verify file data structure
        file_data = result["file"]
        assert "file_path" in file_data
        assert "file_type" in file_data
        assert "content" in file_data
        assert "frontmatter" in file_data
        assert "tasks" in file_data
        assert "links" in file_data

        # Verify parsed content
        assert file_data["file_type"] == "inbox"
        assert "# Inbox" in file_data["content"]
        assert file_data["frontmatter"]["status"] == "active"

        # Verify tasks were extracted
        assert len(file_data["tasks"]) >= 2
        task_descriptions = [task["description"] for task in file_data["tasks"]]
        assert any("quarterly budget report" in desc for desc in task_descriptions)
        assert any("meeting attendance" in desc for desc in task_descriptions)

    def test_read_gtd_file_with_relative_path(self) -> None:
        """Test reading GTD file using relative path from vault."""
        relative_path = "gtd/inbox.md"

        result = read_gtd_file(str(self.vault_path), relative_path)

        assert result["status"] == "success"
        assert result["file"]["file_type"] == "inbox"

    def test_read_gtd_file_context_file(self) -> None:
        """Test reading a context file."""
        calls_path = str(self.gtd_path / "contexts" / "@calls.md")

        result = read_gtd_file(str(self.vault_path), calls_path)

        assert result["status"] == "success"
        file_data = result["file"]
        assert file_data["file_type"] == "context"
        assert "📞 Calls Context" in file_data["content"]

    def test_read_gtd_file_projects_file(self) -> None:
        """Test reading the projects file."""
        projects_path = str(self.gtd_path / "projects.md")

        result = read_gtd_file(str(self.vault_path), projects_path)

        assert result["status"] == "success"
        file_data = result["file"]
        assert file_data["file_type"] == "projects"
        assert "# Projects" in file_data["content"]

    def test_read_gtd_file_nonexistent_file(self) -> None:
        """Test reading a file that doesn't exist."""
        nonexistent_path = str(self.gtd_path / "nonexistent.md")

        result = read_gtd_file(str(self.vault_path), nonexistent_path)

        assert result["status"] == "error"
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_read_gtd_file_invalid_vault_path(self) -> None:
        """Test reading with invalid vault path."""
        inbox_path = str(self.gtd_path / "inbox.md")
        invalid_vault = "/nonexistent/vault"

        result = read_gtd_file(invalid_vault, inbox_path)

        assert result["status"] == "error"
        assert "error" in result
        assert "vault" in result["error"].lower()

    def test_read_gtd_file_outside_gtd_structure(self) -> None:
        """Test reading a file outside the GTD folder structure."""
        # Create a file outside GTD folder
        outside_file = self.vault_path / "not_gtd.md"
        outside_file.write_text("# Not a GTD file")

        result = read_gtd_file(str(self.vault_path), str(outside_file))

        assert result["status"] == "error"
        assert "error" in result
        assert "gtd" in result["error"].lower()

    def test_read_gtd_file_empty_paths(self) -> None:
        """Test error handling for empty paths."""
        result1 = read_gtd_file("", str(self.gtd_path / "inbox.md"))
        assert result1["status"] == "error"

        result2 = read_gtd_file(str(self.vault_path), "")
        assert result2["status"] == "error"

    def test_read_gtd_file_with_tasks_and_links(self) -> None:
        """Test reading file with complex tasks and links."""
        # Create a file with various task formats and links
        complex_file = self.gtd_path / "complex.md"
        complex_content = """---
priority: high
project: test-project
---

# Complex GTD File

## Tasks with contexts
- [ ] Call client about proposal @calls #task
- [x] Update project documentation @computer #task ✅2025-01-05
- [ ] Buy groceries for meeting @errands #task

## Project Links
See [[Project Alpha]] for details.
Check out [External Link](https://example.com) for reference.

## Waiting Items
- [ ] Response from vendor #waiting
"""
        complex_file.write_text(complex_content)

        result = read_gtd_file(str(self.vault_path), str(complex_file))

        assert result["status"] == "success"
        file_data = result["file"]

        # Verify frontmatter parsing - custom fields are in the 'extra' dict
        frontmatter = file_data["frontmatter"]
        assert frontmatter["extra"]["priority"] == "high"
        assert frontmatter["extra"]["project"] == "test-project"

        # Verify task extraction with contexts
        tasks = file_data["tasks"]
        assert len(tasks) >= 3  # 3 checkbox tasks are parsed

        # Check for specific task with context
        call_task = next((t for t in tasks if "client" in t["description"]), None)
        assert call_task is not None
        assert call_task["context"] == "@calls"
        assert not call_task["completed"]

        # Check completed task
        completed_task = next((t for t in tasks if t["completed"]), None)
        assert completed_task is not None
        assert "documentation" in completed_task["description"]

        # Verify link extraction
        links = file_data["links"]
        assert len(links) >= 4  # Context links + Project Alpha + External link

        # Check for Project Alpha wikilink
        project_link = next(
            (link for link in links if "Project Alpha" in link["target"]), None
        )
        assert project_link is not None
        assert project_link["type"] == "wikilink"
        assert not project_link["is_external"]

        # Check for external markdown link
        external_link = next((link for link in links if link["is_external"]), None)
        assert external_link is not None
        assert external_link["type"] == "external"
        assert "example.com" in external_link["target"]
