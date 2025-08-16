"""Tests for ResourceHandler service with URI parsing and data consistency."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from md_gtd_mcp.services.resource_handler import ResourceHandler


class TestResourceHandler:
    """Test ResourceHandler service for MCP resource templates."""

    def setup_method(self) -> None:
        """Set up test environment with temporary vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create basic GTD structure
        gtd_path = self.vault_path / "GTD"
        gtd_path.mkdir()

        # Create sample files
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text("# Inbox\n\n- [ ] Sample inbox task #task\n")

        projects_file = gtd_path / "projects.md"
        projects_file.write_text("# Projects\n\n- [ ] Project task #task\n")

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()


class TestResourceHandlerURIParsing:
    """Test URI parameter extraction and validation."""

    def setup_method(self) -> None:
        """Set up ResourceHandler for URI parsing tests."""
        self.resource_handler = ResourceHandler()

    def test_parse_files_uri_basic(self) -> None:
        """Test parsing basic files URI pattern."""
        vault_path = "test_vault"
        uri = f"gtd://{vault_path}/files"

        parsed = self.resource_handler.parse_files_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_type"] is None

    def test_parse_files_uri_with_filter(self) -> None:
        """Test parsing files URI with file type filter."""
        vault_path = "test_vault"
        file_type = "inbox"
        uri = f"gtd://{vault_path}/files/{file_type}"

        parsed = self.resource_handler.parse_files_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_type"] == file_type

    def test_parse_file_uri(self) -> None:
        """Test parsing single file URI pattern."""
        vault_path = "test_vault"
        file_path = "GTD/inbox.md"
        uri = f"gtd://{vault_path}/file/{file_path}"

        parsed = self.resource_handler.parse_file_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_path"] == file_path

    def test_parse_content_uri_basic(self) -> None:
        """Test parsing basic content URI pattern."""
        vault_path = "test_vault"
        uri = f"gtd://{vault_path}/content"

        parsed = self.resource_handler.parse_content_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_type"] is None

    def test_parse_content_uri_with_filter(self) -> None:
        """Test parsing content URI with file type filter."""
        vault_path = "test_vault"
        file_type = "projects"
        uri = f"gtd://{vault_path}/content/{file_type}"

        parsed = self.resource_handler.parse_content_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_type"] == file_type

    def test_parse_uri_with_spaces(self) -> None:
        """Test URI parsing with spaces in vault path."""
        vault_path = "vault with spaces"
        uri = f"gtd://{vault_path}/files"

        parsed = self.resource_handler.parse_files_uri(uri)

        assert parsed["vault_path"] == vault_path

    def test_parse_uri_with_nested_file_path(self) -> None:
        """Test URI parsing with nested file paths."""
        vault_path = "test_vault"
        file_path = "GTD/Projects/work/project.md"
        uri = f"gtd://{vault_path}/file/{file_path}"

        parsed = self.resource_handler.parse_file_uri(uri)

        assert parsed["vault_path"] == vault_path
        assert parsed["file_path"] == file_path

    def test_parse_invalid_uri_scheme(self) -> None:
        """Test parsing URI with invalid scheme."""
        invalid_uri = "http://test_vault/files"

        with pytest.raises(ValueError, match="Invalid URI scheme"):
            self.resource_handler.parse_files_uri(invalid_uri)

    def test_parse_malformed_uri(self) -> None:
        """Test parsing malformed URI structure."""
        malformed_uri = "gtd:test_vault/files"  # Missing //

        with pytest.raises(ValueError, match="Malformed URI"):
            self.resource_handler.parse_files_uri(malformed_uri)


class TestResourceHandlerVaultValidation:
    """Test vault path and file path validation."""

    def setup_method(self) -> None:
        """Set up ResourceHandler and temporary vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)
        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def test_validate_vault_path_exists(self) -> None:
        """Test validation of existing vault path."""
        result = self.resource_handler.validate_vault_path(str(self.vault_path))

        assert result["valid"] is True
        assert result["vault_path"] == str(self.vault_path)
        assert "error" not in result

    def test_validate_vault_path_not_exists(self) -> None:
        """Test validation of non-existent vault path."""
        nonexistent_path = str(self.vault_path) + "_nonexistent"

        result = self.resource_handler.validate_vault_path(nonexistent_path)

        assert result["valid"] is False
        assert "not found" in result["error"]

    def test_validate_vault_path_empty(self) -> None:
        """Test validation of empty vault path."""
        result = self.resource_handler.validate_vault_path("")

        assert result["valid"] is False
        assert "cannot be empty" in result["error"]

    def test_validate_file_path_absolute(self) -> None:
        """Test validation of absolute file path."""
        absolute_file = self.vault_path / "test.md"
        absolute_file.write_text("test content")

        result = self.resource_handler.validate_file_path(
            str(self.vault_path), str(absolute_file)
        )

        assert result["valid"] is True
        assert result["resolved_path"] == str(absolute_file)

    def test_validate_file_path_relative(self) -> None:
        """Test validation of relative file path."""
        relative_file = "GTD/inbox.md"
        full_file = self.vault_path / relative_file
        full_file.parent.mkdir(parents=True)
        full_file.write_text("test content")

        result = self.resource_handler.validate_file_path(
            str(self.vault_path), relative_file
        )

        assert result["valid"] is True
        assert result["resolved_path"] == str(full_file)

    def test_validate_file_path_not_exists(self) -> None:
        """Test validation of non-existent file path."""
        result = self.resource_handler.validate_file_path(
            str(self.vault_path), "nonexistent.md"
        )

        assert result["valid"] is False
        assert "not found" in result["error"]


class TestResourceHandlerDataConsistency:
    """Test data format consistency with existing tool responses."""

    def setup_method(self) -> None:
        """Set up test environment with sample GTD vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure with sample content
        gtd_path = self.vault_path / "GTD"
        gtd_path.mkdir()

        # Inbox file
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text(
            "# Inbox\n\n"
            "- [ ] Process email backlog #task\n"
            "- [ ] Review project requirements #task\n"
        )

        # Projects file
        projects_file = gtd_path / "projects.md"
        projects_file.write_text(
            "# Projects\n\n"
            "- [ ] Launch new feature #task @computer\n"
            "- [x] Complete documentation #task @computer\n"
        )

        self.resource_handler = ResourceHandler()

    def teardown_method(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    @patch("md_gtd_mcp.services.resource_handler.VaultReader")
    def test_get_files_data_consistency(self, mock_vault_reader_class: Mock) -> None:
        """Test that get_files returns same format as list_gtd_files_impl."""
        # Mock VaultReader to return predictable data
        mock_vault_reader = Mock()
        mock_vault_reader_class.return_value = mock_vault_reader

        # Mock GTD files data
        mock_gtd_files = [
            Mock(
                path="GTD/inbox.md",
                file_type="inbox",
                tasks=[Mock(), Mock()],  # 2 tasks
                links=[Mock()],  # 1 link
            ),
            Mock(
                path="GTD/projects.md",
                file_type="projects",
                tasks=[Mock()],  # 1 task
                links=[],  # 0 links
            ),
        ]
        mock_vault_reader.list_gtd_files.return_value = mock_gtd_files

        # Mock vault summary
        mock_vault_reader.get_vault_summary.return_value = {
            "total_files": 2,
            "total_tasks": 3,
            "total_links": 1,
            "files_by_type": {"inbox": 1, "projects": 1},
            "tasks_by_type": {"inbox": 2, "projects": 1},
        }

        result = self.resource_handler.get_files(str(self.vault_path))

        # Verify response structure matches list_gtd_files_impl
        assert "status" in result
        assert "files" in result
        assert "summary" in result
        assert "vault_path" in result
        assert result["status"] == "success"

        # Verify files data structure
        files = result["files"]
        assert len(files) == 2

        for file_data in files:
            assert "file_path" in file_data
            assert "file_type" in file_data
            assert "task_count" in file_data
            assert "link_count" in file_data

            # Verify data types
            assert isinstance(file_data["file_path"], str)
            assert isinstance(file_data["file_type"], str)
            assert isinstance(file_data["task_count"], int)
            assert isinstance(file_data["link_count"], int)

    @patch("md_gtd_mcp.services.resource_handler.VaultReader")
    def test_get_file_data_consistency(self, mock_vault_reader_class: Mock) -> None:
        """Test that get_file returns same format as read_gtd_file_impl."""
        # Mock VaultReader and GTD file
        mock_vault_reader = Mock()
        mock_vault_reader_class.return_value = mock_vault_reader

        # Mock task data
        mock_task = Mock()
        mock_task.text = "Sample task"
        mock_task.is_completed = False
        mock_task.done_date = None
        mock_task.context = "@computer"
        mock_task.project = None
        mock_task.energy = None
        mock_task.time_estimate = None
        mock_task.delegated_to = None
        mock_task.tags = ["task"]
        mock_task.priority = None
        mock_task.due_date = None
        mock_task.scheduled_date = None
        mock_task.start_date = None
        mock_task.raw_text = "- [ ] Sample task #task @computer"
        mock_task.line_number = 3

        # Mock link data
        mock_link = Mock()
        mock_link.is_external = False
        mock_link.text = "related note"
        mock_link.target = "related-note"
        mock_link.line_number = 5

        # Mock GTD file
        mock_gtd_file = Mock()
        mock_gtd_file.path = "GTD/inbox.md"
        mock_gtd_file.file_type = "inbox"
        mock_gtd_file.content = (
            "# Inbox\n\n- [ ] Sample task #task @computer\n\n[[related note]]"
        )
        mock_gtd_file.frontmatter = None
        mock_gtd_file.tasks = [mock_task]
        mock_gtd_file.links = [mock_link]

        mock_vault_reader.read_gtd_file.return_value = mock_gtd_file

        result = self.resource_handler.get_file(str(self.vault_path), "GTD/inbox.md")

        # Verify response structure matches read_gtd_file_impl
        assert "status" in result
        assert "file" in result
        assert "vault_path" in result
        assert result["status"] == "success"

        # Verify file data structure
        file_data = result["file"]
        assert "file_path" in file_data
        assert "file_type" in file_data
        assert "content" in file_data
        assert "frontmatter" in file_data
        assert "tasks" in file_data
        assert "links" in file_data

        # Verify task data structure
        task_data = file_data["tasks"][0]
        expected_task_fields = [
            "description",
            "completed",
            "completion_date",
            "context",
            "project",
            "energy",
            "time_estimate",
            "delegated_to",
            "tags",
            "priority",
            "due_date",
            "scheduled_date",
            "start_date",
            "raw_text",
            "line_number",
        ]
        for field in expected_task_fields:
            assert field in task_data

        # Verify link data structure
        link_data = file_data["links"][0]
        expected_link_fields = ["type", "text", "target", "is_external", "line_number"]
        for field in expected_link_fields:
            assert field in link_data


class TestResourceHandlerErrorHandling:
    """Test error handling for invalid paths and missing files."""

    def setup_method(self) -> None:
        """Set up ResourceHandler for error testing."""
        self.resource_handler = ResourceHandler()

    def test_get_files_invalid_vault_path(self) -> None:
        """Test get_files with invalid vault path."""
        result = self.resource_handler.get_files("")

        assert result["status"] == "error"
        assert "cannot be empty" in result["error"]
        assert "vault_path" in result

    def test_get_files_nonexistent_vault(self) -> None:
        """Test get_files with non-existent vault."""
        result = self.resource_handler.get_files("nonexistent_vault")

        assert result["status"] == "error"
        assert "not found" in result["error"]

    def test_get_file_invalid_paths(self) -> None:
        """Test get_file with invalid vault and file paths."""
        # Test empty vault path
        result = self.resource_handler.get_file("", "test.md")
        assert result["status"] == "error"
        assert "cannot be empty" in result["error"]

        # Test empty file path with temporary valid vault
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "test_vault"
            vault_path.mkdir()

            result = self.resource_handler.get_file(str(vault_path), "")
            assert result["status"] == "error"
            assert "cannot be empty" in result["error"]

    def test_get_content_error_handling(self) -> None:
        """Test get_content with various error conditions."""
        # Test invalid vault path
        result = self.resource_handler.get_content("")

        assert result["status"] == "error"
        assert "cannot be empty" in result["error"]

    def test_error_response_format(self) -> None:
        """Test that error responses maintain consistent format."""
        result = self.resource_handler.get_files("")

        # All error responses should have these fields
        assert "status" in result
        assert "error" in result
        assert "vault_path" in result
        assert result["status"] == "error"
        assert isinstance(result["error"], str)


class TestResourceHandlerFiltering:
    """Test file type filtering functionality."""

    def setup_method(self) -> None:
        """Set up ResourceHandler for filtering tests."""
        self.resource_handler = ResourceHandler()

    @patch("md_gtd_mcp.services.resource_handler.VaultReader")
    def test_get_files_with_filter(self, mock_vault_reader_class: Mock) -> None:
        """Test get_files with file type filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "test_vault"
            vault_path.mkdir()
            gtd_path = vault_path / "gtd"
            gtd_path.mkdir()

            mock_vault_reader = Mock()
            mock_vault_reader_class.return_value = mock_vault_reader

            # Mock filtered GTD files
            mock_gtd_files = [
                Mock(
                    path="GTD/inbox.md",
                    file_type="inbox",
                    tasks=[Mock(), Mock()],
                    links=[Mock()],
                )
            ]
            mock_vault_reader.list_gtd_files.return_value = mock_gtd_files
            mock_vault_reader.get_vault_summary.return_value = {
                "total_files": 1,
                "total_tasks": 2,
                "total_links": 1,
                "files_by_type": {"inbox": 1},
                "tasks_by_type": {"inbox": 2},
            }

            result = self.resource_handler.get_files(str(vault_path), file_type="inbox")

            # Verify filter was passed to VaultReader
            mock_vault_reader.list_gtd_files.assert_called_once_with(file_type="inbox")

            # Verify filtered results
            assert result["status"] == "success"
            assert len(result["files"]) == 1
            assert result["files"][0]["file_type"] == "inbox"

    @patch("md_gtd_mcp.services.resource_handler.VaultReader")
    def test_get_content_with_filter(self, mock_vault_reader_class: Mock) -> None:
        """Test get_content with file type filtering."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "test_vault"
            vault_path.mkdir()
            gtd_path = vault_path / "gtd"
            gtd_path.mkdir()

            mock_vault_reader = Mock()
            mock_vault_reader_class.return_value = mock_vault_reader

            # Mock filtered GTD files with content
            mock_gtd_file = Mock()
            mock_gtd_file.path = "GTD/projects.md"
            mock_gtd_file.file_type = "projects"
            mock_gtd_file.content = "# Projects\n\n- [ ] Test project #task"
            mock_gtd_file.frontmatter = None
            mock_gtd_file.tasks = [Mock()]
            mock_gtd_file.links = []

            mock_vault_reader.list_gtd_files.return_value = [mock_gtd_file]
            mock_vault_reader.get_vault_summary.return_value = {
                "total_files": 1,
                "total_tasks": 1,
                "total_links": 0,
                "files_by_type": {"projects": 1},
                "tasks_by_type": {"projects": 1},
            }

            result = self.resource_handler.get_content(
                str(vault_path), file_type="projects"
            )

            # Verify filter was applied
            mock_vault_reader.list_gtd_files.assert_called_once_with(
                file_type="projects"
            )

            # Verify content response structure
            assert result["status"] == "success"
            assert len(result["files"]) == 1
            assert result["files"][0]["file_type"] == "projects"
            assert "content" in result["files"][0]
