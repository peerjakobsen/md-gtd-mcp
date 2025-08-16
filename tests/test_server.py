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


class TestListGTDFiles:
    """Test list_gtd_files MCP tool."""

    def setup_method(self) -> None:
        """Set up test vault directory with comprehensive GTD structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create a complete GTD structure
        setup_gtd_vault(str(self.vault_path))
        self.gtd_path = self.vault_path / "gtd"

        # Add sample content to various GTD files for testing
        self._create_sample_inbox()
        self._create_sample_projects()
        self._create_sample_next_actions()
        self._create_sample_context_files()

    def _create_sample_inbox(self) -> None:
        """Create inbox file with sample content."""
        inbox_path = self.gtd_path / "inbox.md"
        content = """---
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
        inbox_path.write_text(content)

    def _create_sample_projects(self) -> None:
        """Create projects file with sample content."""
        projects_path = self.gtd_path / "projects.md"
        content = """---
status: active
---

# Projects

## Active Projects

### Project Alpha
- [ ] Define project scope @computer #task
- [ ] Schedule kickoff meeting @calls #task

### Website Redesign
- [x] Research design trends @computer #task ✅2025-01-05
- [ ] Create wireframes @computer #task
"""
        projects_path.write_text(content)

    def _create_sample_next_actions(self) -> None:
        """Create next-actions file with sample content."""
        next_actions_path = self.gtd_path / "next-actions.md"
        content = """---
status: active
---

# Next Actions

## Priority Items

- [ ] Submit expense report @computer #task #high-priority
- [ ] Call insurance agent @calls #task

## Regular Tasks

- [ ] Update weekly status report @computer #task
"""
        next_actions_path.write_text(content)

    def _create_sample_context_files(self) -> None:
        """Add custom content to context files."""
        contexts_path = self.gtd_path / "contexts"

        # Add task to @calls context
        calls_path = contexts_path / "@calls.md"
        existing_content = calls_path.read_text()
        calls_path.write_text(
            existing_content + "\n- [ ] Follow up with client @calls #task\n"
        )

    def test_list_gtd_files_success(self) -> None:
        """Test successfully listing all GTD files."""
        # Import the implementation function (will be created)
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        result = list_gtd_files(str(self.vault_path))

        # Verify response structure
        assert "status" in result
        assert "files" in result
        assert "vault_path" in result
        assert result["status"] == "success"
        assert result["vault_path"] == str(self.vault_path)

        # Verify files list structure
        files = result["files"]
        assert isinstance(files, list)
        assert len(files) > 0

        # Check that standard GTD files are included
        file_types = [f["file_type"] for f in files]
        assert "inbox" in file_types
        assert "projects" in file_types
        assert "next-actions" in file_types
        assert "context" in file_types

        # Verify each file has required metadata structure (no full content)
        for file_data in files:
            assert "file_path" in file_data
            assert "file_type" in file_data
            assert "task_count" in file_data
            assert "link_count" in file_data
            # list_gtd_files should NOT include full content
            assert "content" not in file_data
            assert "tasks" not in file_data
            assert "links" not in file_data
            assert "frontmatter" not in file_data

        # Should not have suggestion when files exist
        assert "suggestion" not in result

    def test_list_gtd_files_with_file_type_filter(self) -> None:
        """Test listing GTD files filtered by file type."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        # Test filtering by inbox
        result = list_gtd_files(str(self.vault_path), file_type="inbox")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 1
        for file_data in files:
            assert file_data["file_type"] == "inbox"

        # Test filtering by projects
        result = list_gtd_files(str(self.vault_path), file_type="projects")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 1
        for file_data in files:
            assert file_data["file_type"] == "projects"

        # Test filtering by context
        result = list_gtd_files(str(self.vault_path), file_type="context")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 4  # @calls, @computer, @errands, @home
        for file_data in files:
            assert file_data["file_type"] == "context"

    def test_list_gtd_files_with_summary_stats(self) -> None:
        """Test that list includes summary statistics."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        result = list_gtd_files(str(self.vault_path))

        assert result["status"] == "success"
        assert "summary" in result

        summary = result["summary"]
        assert "total_files" in summary
        assert "total_tasks" in summary
        assert "total_links" in summary
        assert "files_by_type" in summary
        assert "tasks_by_type" in summary

        # Verify summary data makes sense
        assert summary["total_files"] > 0
        assert summary["total_tasks"] >= 0
        assert summary["total_links"] >= 0
        assert isinstance(summary["files_by_type"], dict)
        assert isinstance(summary["tasks_by_type"], dict)

    def test_list_gtd_files_no_gtd_structure_suggests_setup(self) -> None:
        """Test that tool suggests setup_gtd_vault when no GTD structure exists."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        # Create empty vault without GTD structure
        empty_vault = Path(self.temp_dir) / "empty_vault"
        empty_vault.mkdir()

        result = list_gtd_files(str(empty_vault))

        # Should succeed but include helpful suggestion
        assert result["status"] == "success"
        assert len(result["files"]) == 0
        assert result["summary"]["total_files"] == 0

        # Should include suggestion to run setup_gtd_vault
        assert "suggestion" in result
        suggestion = result["suggestion"]
        assert "setup_gtd_vault" in suggestion
        assert "GTD structure" in suggestion or "gtd structure" in suggestion

    def test_list_gtd_files_nonexistent_vault_suggests_setup(self) -> None:
        """Test that tool suggests setup when vault directory doesn't exist."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        nonexistent_vault = str(Path(self.temp_dir) / "nonexistent_vault")

        result = list_gtd_files(nonexistent_vault)

        # Should succeed and include helpful suggestion
        assert result["status"] == "success"
        assert len(result["files"]) == 0
        assert result["summary"]["total_files"] == 0

        # Should include suggestion to run setup_gtd_vault
        assert "suggestion" in result
        suggestion = result["suggestion"]
        assert "setup_gtd_vault" in suggestion
        assert "create" in suggestion.lower() or "setup" in suggestion.lower()

    def test_list_gtd_files_partial_gtd_structure_no_suggestion(self) -> None:
        """Test that no suggestion appears when some GTD files exist."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        # Create vault with only some GTD files
        partial_vault = Path(self.temp_dir) / "partial_vault"
        partial_vault.mkdir()
        gtd_path = partial_vault / "gtd"
        gtd_path.mkdir()

        # Create only inbox file
        inbox_path = gtd_path / "inbox.md"
        inbox_path.write_text("# Inbox\n\n- [ ] Test task @calls #task")

        result = list_gtd_files(str(partial_vault))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) == 1
        assert files[0]["file_type"] == "inbox"
        assert files[0]["task_count"] == 1

        # Should not suggest setup when some files exist
        assert "suggestion" not in result

    def test_list_gtd_files_invalid_vault_path(self) -> None:
        """Test error handling for invalid vault path."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        result = list_gtd_files("")
        assert result["status"] == "error"
        assert "error" in result

        result = list_gtd_files("   ")
        assert result["status"] == "error"
        assert "error" in result

    def test_list_gtd_files_invalid_file_type_filter(self) -> None:
        """Test filtering with invalid file type."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        result = list_gtd_files(str(self.vault_path), file_type="invalid-type")

        # Should succeed but return empty files list
        assert result["status"] == "success"
        assert len(result["files"]) == 0

    def test_list_gtd_files_task_and_link_counts(self) -> None:
        """Test that individual files include task and link counts (metadata only)."""
        from md_gtd_mcp.server import list_gtd_files_impl as list_gtd_files

        result = list_gtd_files(str(self.vault_path))

        assert result["status"] == "success"
        files = result["files"]

        # Verify files have counts but no detailed content
        for file_data in files:
            assert isinstance(file_data["task_count"], int)
            assert isinstance(file_data["link_count"], int)
            assert file_data["task_count"] >= 0
            assert file_data["link_count"] >= 0

        # Verify that some files have non-zero counts (basic sanity check)
        total_tasks = sum(f["task_count"] for f in files)
        assert total_tasks > 0  # We added tasks to various files


class TestReadGTDFiles:
    """Test read_gtd_files MCP tool."""

    def setup_method(self) -> None:
        """Set up test vault directory with comprehensive GTD structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create a complete GTD structure
        setup_gtd_vault(str(self.vault_path))
        self.gtd_path = self.vault_path / "gtd"

        # Add sample content to various GTD files for testing
        self._create_sample_content()

    def _create_sample_content(self) -> None:
        """Create comprehensive sample content across multiple GTD files."""
        # Inbox with multiple tasks
        inbox_path = self.gtd_path / "inbox.md"
        inbox_content = """---
status: active
capture_date: 2025-01-15
---

# Inbox

## Quick Capture

- Research vacation destinations for spring break
- [ ] Review quarterly budget report @computer #task
- [ ] Confirm meeting attendance with team @calls #task
- [ ] Pick up dry cleaning @errands #task

## Ideas and Notes

Check [[Project Alpha]] status and [[Project Beta]] dependencies.
Visit [External Resource](https://example.com) for research.
"""
        inbox_path.write_text(inbox_content)

        # Projects with complex structure
        projects_path = self.gtd_path / "projects.md"
        projects_content = """---
status: active
review_date: 2025-01-20
---

# Projects

## Active Projects

### Project Alpha
- [ ] Define project scope @computer #task #high-priority
- [ ] Schedule kickoff meeting @calls #task
- [x] Research requirements @computer #task ✅2025-01-10

### Project Beta
- [ ] Review dependencies on [[Project Alpha]]
- [ ] Create project timeline @computer #task
- [ ] Set up project repository @computer #task #development

## On Hold

### Website Redesign
- [x] Research design trends @computer #task ✅2025-01-05
- [ ] Create wireframes @computer #task
"""
        projects_path.write_text(projects_content)

        # Next Actions with priorities
        next_actions_path = self.gtd_path / "next-actions.md"
        next_actions_content = """---
status: active
---

# Next Actions

## High Priority

- [ ] Submit expense report @computer #task #high-priority
- [ ] Call insurance agent @calls #task #urgent

## This Week

- [ ] Update weekly status report @computer #task
- [ ] Review team performance metrics @computer #task
- [ ] Schedule quarterly planning meeting @calls #task

## Someday

- [ ] Organize digital photo library @computer #task #low-priority
"""
        next_actions_path.write_text(next_actions_content)

        # Waiting For with tracking
        waiting_path = self.gtd_path / "waiting-for.md"
        waiting_content = """---
status: active
---

# Waiting For

## Pending Responses

- [ ] Response from vendor about pricing @waiting #task
- [ ] Approval from manager for vacation request @waiting #task
- [ ] Client feedback on proposal draft @waiting #task

## Follow-up Needed

- [ ] Follow up with IT about server access @calls #task
"""
        waiting_path.write_text(waiting_content)

        # Someday Maybe with categorization
        someday_path = self.gtd_path / "someday-maybe.md"
        someday_content = """---
status: active
---

# Someday / Maybe

## Personal Development

- [ ] Learn Spanish language @self-development #task
- [ ] Take photography course @learning #task

## Travel Ideas

- [ ] Plan trip to Japan @travel #task
- [ ] Visit European museums @travel #task

## Home Projects

- [ ] Renovate home office @home #task #big-project
- [ ] Install smart home system @home #task
"""
        someday_path.write_text(someday_content)

        # Add content to context files
        contexts_path = self.gtd_path / "contexts"

        # @calls with additional tasks
        calls_path = contexts_path / "@calls.md"
        existing_content = calls_path.read_text()
        calls_path.write_text(
            existing_content + "\n- [ ] Schedule dentist appointment @calls #task\n"
            "- [ ] Call bank about mortgage rates @calls #task #financial\n"
        )

        # @computer with project tasks
        computer_path = contexts_path / "@computer.md"
        existing_content = computer_path.read_text()
        computer_path.write_text(
            existing_content + "\n- [ ] Update LinkedIn profile @computer #task\n"
            "- [ ] Backup important files @computer #task #maintenance\n"
        )

    def test_read_gtd_files_success(self) -> None:
        """Test successfully reading GTD files with comprehensive data."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files(str(self.vault_path))

        # Verify response structure
        assert "status" in result
        assert "files" in result
        assert "vault_path" in result
        assert "summary" in result
        assert result["status"] == "success"
        assert result["vault_path"] == str(self.vault_path)

        # Verify comprehensive file listing
        files = result["files"]
        assert isinstance(files, list)
        assert len(files) >= 9  # 5 standard + 4 context files

        # Check that all GTD file types are included
        file_types = [f["file_type"] for f in files]
        assert "inbox" in file_types
        assert "projects" in file_types
        assert "next-actions" in file_types
        assert "waiting-for" in file_types
        assert "someday-maybe" in file_types
        assert "context" in file_types

        # Verify each file has complete structure
        for file_data in files:
            assert "file_path" in file_data
            assert "file_type" in file_data
            assert "content" in file_data
            assert "frontmatter" in file_data
            assert "tasks" in file_data
            assert "links" in file_data
            assert "task_count" in file_data
            assert "link_count" in file_data

        # Verify summary statistics
        summary = result["summary"]
        assert summary["total_files"] >= 9
        assert summary["total_tasks"] >= 20  # We added many tasks
        assert summary["total_links"] >= 3  # Project links and external links

    def test_read_gtd_files_comprehensive_task_analysis(self) -> None:
        """Test that all tasks across all files are properly extracted and analyzed."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files(str(self.vault_path))
        assert result["status"] == "success"

        files = result["files"]
        all_tasks = []
        for file_data in files:
            all_tasks.extend(file_data["tasks"])

        # Verify we have comprehensive task data
        assert len(all_tasks) >= 20

        # Check for specific task properties
        high_priority_tasks = [
            t for t in all_tasks if "#high-priority" in t.get("tags", [])
        ]
        assert len(high_priority_tasks) >= 2

        completed_tasks = [t for t in all_tasks if t["completed"]]
        assert len(completed_tasks) >= 2

        context_tasks = [t for t in all_tasks if t.get("context")]
        assert len(context_tasks) >= 10

        # Verify task contexts are properly extracted
        contexts = {t["context"] for t in context_tasks if t["context"]}
        assert "@computer" in contexts
        assert "@calls" in contexts
        assert "@errands" in contexts

    def test_read_gtd_files_comprehensive_link_analysis(self) -> None:
        """Test that all links across all files are properly extracted."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files(str(self.vault_path))
        assert result["status"] == "success"

        files = result["files"]
        all_links = []
        for file_data in files:
            all_links.extend(file_data["links"])

        # Verify comprehensive link extraction
        assert len(all_links) >= 5

        # Check for different link types
        wikilinks = [link for link in all_links if link["type"] == "wikilink"]
        external_links = [link for link in all_links if link["type"] == "external"]
        context_links = [link for link in all_links if link["target"].startswith("@")]

        assert len(wikilinks) >= 2  # Project Alpha, Project Beta
        assert len(external_links) >= 1  # Example.com
        assert len(context_links) >= 4  # Context file references

        # Verify specific project links
        project_targets = {link["target"] for link in wikilinks}
        assert "Project Alpha" in project_targets
        assert "Project Beta" in project_targets

    def test_read_gtd_files_empty_vault_suggests_setup(self) -> None:
        """Test that tool suggests setup_gtd_vault when vault is empty."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        # Create empty vault
        empty_vault = Path(self.temp_dir) / "empty_vault"
        empty_vault.mkdir()

        result = read_gtd_files(str(empty_vault))

        # Should succeed but include helpful suggestion
        assert result["status"] == "success"
        assert len(result["files"]) == 0
        assert result["summary"]["total_files"] == 0

        # Should include suggestion to run setup_gtd_vault
        assert "suggestion" in result
        suggestion = result["suggestion"]
        assert "setup_gtd_vault" in suggestion
        assert "GTD structure" in suggestion or "gtd structure" in suggestion

    def test_read_gtd_files_nonexistent_vault_suggests_setup(self) -> None:
        """Test that tool suggests setup when vault directory doesn't exist."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        nonexistent_vault = str(Path(self.temp_dir) / "nonexistent_vault")

        result = read_gtd_files(nonexistent_vault)

        # Should succeed and include helpful suggestion
        assert result["status"] == "success"
        assert len(result["files"]) == 0
        assert result["summary"]["total_files"] == 0

        # Should include suggestion to run setup_gtd_vault
        assert "suggestion" in result
        suggestion = result["suggestion"]
        assert "setup_gtd_vault" in suggestion
        assert "create" in suggestion.lower() or "setup" in suggestion.lower()

    def test_read_gtd_files_file_type_distribution(self) -> None:
        """Test that files are properly distributed across GTD categories."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files(str(self.vault_path))
        assert result["status"] == "success"

        # Verify file type distribution in summary
        summary = result["summary"]
        files_by_type = summary["files_by_type"]

        assert files_by_type.get("inbox", 0) >= 1
        assert files_by_type.get("projects", 0) >= 1
        assert files_by_type.get("next-actions", 0) >= 1
        assert files_by_type.get("waiting-for", 0) >= 1
        assert files_by_type.get("someday-maybe", 0) >= 1
        assert files_by_type.get("context", 0) >= 4

        # Verify task distribution by file type
        tasks_by_type = summary["tasks_by_type"]
        assert tasks_by_type.get("inbox", 0) >= 3
        assert tasks_by_type.get("projects", 0) >= 6
        assert tasks_by_type.get("next-actions", 0) >= 6
        assert tasks_by_type.get("context", 0) >= 4

    def test_read_gtd_files_invalid_vault_path(self) -> None:
        """Test error handling for invalid vault paths."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files("")
        assert result["status"] == "error"
        assert "error" in result

        result = read_gtd_files("   ")
        assert result["status"] == "error"
        assert "error" in result

    def test_read_gtd_files_partial_gtd_structure(self) -> None:
        """Test reading when only partial GTD structure exists."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        # Create vault with only some GTD files
        partial_vault = Path(self.temp_dir) / "partial_vault"
        partial_vault.mkdir()
        gtd_path = partial_vault / "gtd"
        gtd_path.mkdir()

        # Create only inbox and projects files
        inbox_path = gtd_path / "inbox.md"
        inbox_path.write_text("# Inbox\n\n- [ ] Test task @calls #task")

        projects_path = gtd_path / "projects.md"
        projects_path.write_text("# Projects\n\n- [ ] Test project @computer #task")

        result = read_gtd_files(str(partial_vault))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) == 2

        file_types = [f["file_type"] for f in files]
        assert "inbox" in file_types
        assert "projects" in file_types

        # Should not suggest setup when some files exist
        assert "suggestion" not in result

    def test_read_gtd_files_comprehensive_content_validation(self) -> None:
        """Test that file content is completely preserved and accessible."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        result = read_gtd_files(str(self.vault_path))
        assert result["status"] == "success"

        files = result["files"]

        # Find inbox file and verify content preservation
        inbox_file = next((f for f in files if f["file_type"] == "inbox"), None)
        assert inbox_file is not None
        assert "Research vacation destinations" in inbox_file["content"]
        assert "Project Alpha" in inbox_file["content"]
        assert "example.com" in inbox_file["content"]

        # Verify frontmatter is properly parsed
        assert inbox_file["frontmatter"]["status"] == "active"
        assert "capture_date" in inbox_file["frontmatter"]["extra"]

        # Find projects file and verify complex structure
        projects_file = next((f for f in files if f["file_type"] == "projects"), None)
        assert projects_file is not None
        assert "Project Alpha" in projects_file["content"]
        assert "Project Beta" in projects_file["content"]
        assert "On Hold" in projects_file["content"]

    def test_read_gtd_files_performance_with_many_files(self) -> None:
        """Test that the tool handles larger numbers of files efficiently."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        # Add additional context files to simulate larger vault
        contexts_path = self.gtd_path / "contexts"
        additional_contexts = ["@office.md", "@phone.md", "@agenda.md", "@waiting.md"]

        for context_file in additional_contexts:
            context_path = contexts_path / context_file
            content = (
                f"# {context_file[1:-3].title()} Context\n\n"
                f"- [ ] Sample task {context_file} #task\n"
            )
            context_path.write_text(content)

        result = read_gtd_files(str(self.vault_path))

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 13  # Original files + additional contexts

        # Verify all context files are included
        context_files = [f for f in files if f["file_type"] == "context"]
        assert len(context_files) >= 8  # 4 original + 4 additional

    def test_read_gtd_files_with_file_type_filter(self) -> None:
        """Test reading GTD files with file type filtering."""
        from md_gtd_mcp.server import read_gtd_files_impl as read_gtd_files

        # Test filtering by inbox
        result = read_gtd_files(str(self.vault_path), file_type="inbox")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 1
        for file_data in files:
            assert file_data["file_type"] == "inbox"
            # Should include full content since this is read_gtd_files
            assert "content" in file_data
            assert "tasks" in file_data
            assert "links" in file_data

        # Test filtering by projects
        result = read_gtd_files(str(self.vault_path), file_type="projects")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 1
        for file_data in files:
            assert file_data["file_type"] == "projects"
            assert "content" in file_data

        # Test filtering by context
        result = read_gtd_files(str(self.vault_path), file_type="context")

        assert result["status"] == "success"
        files = result["files"]
        assert len(files) >= 4  # @calls, @computer, @errands, @home
        for file_data in files:
            assert file_data["file_type"] == "context"
            assert "content" in file_data


class TestMCPServerStartup:
    """Test MCP server startup and configuration."""

    def test_mcp_server_initialization(self) -> None:
        """Test that MCP server can be initialized without errors."""
        from md_gtd_mcp.server import mcp

        # Verify MCP server instance is created
        assert mcp is not None
        assert hasattr(mcp, "name")
        assert mcp.name == "Markdown GTD"

    def test_mcp_server_main_function_exists(self) -> None:
        """Test that main function for server startup exists."""
        from md_gtd_mcp.server import main

        # Verify main function is callable
        assert callable(main)

        # Note: We don't actually call main() as it would start the server and block
        # In a real scenario, you might use mock or subprocess for full testing

    def test_mcp_server_implementation_functions_exist(self) -> None:
        """Test that all MCP tool implementation functions exist and are callable."""
        # Test that the implementation functions are available and callable
        from md_gtd_mcp.server import (
            list_gtd_files_impl,
            read_gtd_file_impl,
            read_gtd_files_impl,
        )
        from md_gtd_mcp.services.vault_setup import setup_gtd_vault

        # Verify all implementation functions are callable
        assert callable(list_gtd_files_impl)
        assert callable(read_gtd_file_impl)
        assert callable(read_gtd_files_impl)
        assert callable(setup_gtd_vault)

    def test_mcp_server_can_handle_basic_tool_calls(self) -> None:
        """Test that MCP server implementation functions can handle basic calls."""
        import tempfile
        from pathlib import Path

        from md_gtd_mcp.server import list_gtd_files_impl

        # Test list_gtd_files with empty vault (should handle gracefully)
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_vault = Path(temp_dir) / "empty"
            empty_vault.mkdir()

            result = list_gtd_files_impl(str(empty_vault))
            assert result["status"] == "success"
            assert len(result["files"]) == 0
            assert "suggestion" in result  # Should suggest setup

    def test_mcp_server_tools_are_registered(self) -> None:
        """Test that MCP server has tools registered (basic validation)."""
        from md_gtd_mcp.server import mcp

        # Verify that the server exists and is properly configured
        assert mcp is not None
        assert mcp.name == "Markdown GTD"

        # Verify that the decorated functions exist in the server module
        # This indirectly confirms the tools are registered
        from md_gtd_mcp import server

        expected_tool_functions = [
            "hello_world",
            "setup_gtd_vault",
            "read_gtd_file",
            "list_gtd_files",
            "read_gtd_files",
        ]

        for tool_name in expected_tool_functions:
            assert hasattr(server, tool_name), (
                f"Tool function {tool_name} not found in server module"
            )
