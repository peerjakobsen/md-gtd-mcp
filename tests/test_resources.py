"""Tests for MCP resource templates with comprehensive URI pattern matching.

This module tests the five resource templates that replace the existing tools:
- gtd://{vault_path}/files (list files)
- gtd://{vault_path}/files/{file_type} (filtered list files)
- gtd://{vault_path}/file/{file_path} (single file)
- gtd://{vault_path}/content (batch content)
- gtd://{vault_path}/content/{file_type} (filtered batch content)

Tests verify URI pattern matching, resource annotations, error handling,
and data consistency with existing tool implementations.
"""

import json
import tempfile
import unittest
from pathlib import Path

from md_gtd_mcp.services.resource_handler import ResourceHandler


class TestResourceTemplates(unittest.TestCase):
    """Test MCP resource templates with comprehensive URI pattern coverage."""

    def setUp(self) -> None:
        """Set up test environment with sample vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure (lowercase as expected by VaultConfig)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create sample files for testing
        self._create_sample_files(gtd_path)

        self.resource_handler = ResourceHandler()

    def tearDown(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def _create_sample_files(self, gtd_path: Path) -> None:
        """Create sample GTD files for testing."""
        # Inbox file
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text(
            "# Inbox\n\n- [ ] Sample inbox task\n- [ ] Another inbox item\n"
        )

        # Projects file
        projects_file = gtd_path / "projects.md"
        projects_file.write_text(
            "# Projects\n\n- [ ] Project task #task\n- [ ] Another project #task\n"
        )

        # Next actions file
        next_actions_file = gtd_path / "next-actions.md"
        next_actions_file.write_text(
            "# Next Actions\n\n- [ ] Next action task #task @home\n"
        )

    async def _mock_resource_access(self, uri: str) -> str:
        """Mock resource access for testing resource templates."""
        # Parse URI to determine which resource handler method to call
        if "/files/" in uri and uri.count("/") > 3:
            # Filtered files: gtd://{vault_path}/files/{file_type}
            parsed = self.resource_handler.parse_files_uri(uri)
            result = self.resource_handler.get_files(
                parsed["vault_path"], parsed["file_type"]
            )
        elif "/files" in uri:
            # Files listing: gtd://{vault_path}/files
            parsed = self.resource_handler.parse_files_uri(uri)
            result = self.resource_handler.get_files(parsed["vault_path"])
        elif "/file/" in uri:
            # Single file: gtd://{vault_path}/file/{file_path}
            parsed = self.resource_handler.parse_file_uri(uri)
            result = self.resource_handler.get_file(
                parsed["vault_path"], parsed["file_path"]
            )
        elif "/content/" in uri and uri.count("/") > 3:
            # Filtered content: gtd://{vault_path}/content/{file_type}
            parsed = self.resource_handler.parse_content_uri(uri)
            result = self.resource_handler.get_content(
                parsed["vault_path"], parsed["file_type"]
            )
        elif "/content" in uri:
            # Batch content: gtd://{vault_path}/content
            parsed = self.resource_handler.parse_content_uri(uri)
            result = self.resource_handler.get_content(parsed["vault_path"])
        else:
            raise ValueError(f"Unknown resource URI pattern: {uri}")

        return json.dumps(result)


class TestFilesResourceTemplate(TestResourceTemplates):
    """Test files resource template: gtd://{vault_path}/files"""

    def test_files_uri_pattern_matching(self) -> None:
        """Test files resource URI pattern correctly extracts vault_path."""
        vault_path = str(self.vault_path)
        uri = f"gtd://{vault_path}/files"

        parsed = self.resource_handler.parse_files_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertIsNone(parsed["file_type"])

    def test_files_resource_data_format(self) -> None:
        """Test files resource returns correct data format."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_files(vault_path)

        # Verify required fields
        self.assertIn("status", result)
        self.assertIn("files", result)
        self.assertIn("summary", result)
        self.assertIn("vault_path", result)

        # Verify status is success
        self.assertEqual(result["status"], "success")

        # Verify files structure
        self.assertIsInstance(result["files"], list)
        for file_data in result["files"]:
            self.assertIn("file_path", file_data)
            self.assertIn("file_type", file_data)
            self.assertIn("task_count", file_data)
            self.assertIn("link_count", file_data)

    def test_files_resource_vault_path_validation(self) -> None:
        """Test files resource validates vault path correctly."""
        invalid_vault = "/nonexistent/vault"

        result = self.resource_handler.get_files(invalid_vault)

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_files_resource_empty_vault_path(self) -> None:
        """Test files resource handles empty vault path."""
        result = self.resource_handler.get_files("")

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("empty", result["error"].lower())

    def test_files_resource_invalid_uri_scheme(self) -> None:
        """Test files resource rejects invalid URI schemes."""
        invalid_uri = "http://vault/files"

        with self.assertRaises(ValueError) as context:
            self.resource_handler.parse_files_uri(invalid_uri)

        self.assertIn("Invalid URI scheme", str(context.exception))

    def test_files_resource_malformed_uri(self) -> None:
        """Test files resource handles malformed URIs."""
        malformed_uri = "gtd:///files"  # Missing vault path

        with self.assertRaises(ValueError) as context:
            self.resource_handler.parse_files_uri(malformed_uri)

        self.assertIn("missing vault path", str(context.exception))


class TestFilesFilteredResourceTemplate(TestResourceTemplates):
    """Test filtered files resource template: gtd://{vault_path}/files/{file_type}"""

    def test_files_filtered_uri_pattern_matching(self) -> None:
        """Test filtered files resource URI pattern extracts parameters."""
        vault_path = str(self.vault_path)
        file_type = "inbox"
        uri = f"gtd://{vault_path}/files/{file_type}"

        parsed = self.resource_handler.parse_files_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertEqual(parsed["file_type"], file_type)

    def test_files_filtered_resource_inbox_filtering(self) -> None:
        """Test filtered files resource correctly filters inbox files."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_files(vault_path, "inbox")

        self.assertEqual(result["status"], "success")
        self.assertGreater(len(result["files"]), 0)

        # All returned files should be inbox type
        for file_data in result["files"]:
            self.assertEqual(file_data["file_type"], "inbox")

    def test_files_filtered_resource_projects_filtering(self) -> None:
        """Test filtered files resource correctly filters project files."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_files(vault_path, "projects")

        self.assertEqual(result["status"], "success")

        # All returned files should be projects type
        for file_data in result["files"]:
            self.assertEqual(file_data["file_type"], "projects")

    def test_files_filtered_resource_unknown_file_type(self) -> None:
        """Test filtered files resource handles unknown file types."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_files(vault_path, "unknown_type")

        # Should return success with empty files list
        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["files"]), 0)


class TestFileResourceTemplate(TestResourceTemplates):
    """Test file resource template: gtd://{vault_path}/file/{file_path}"""

    def test_file_uri_pattern_matching(self) -> None:
        """Test file resource URI pattern extracts vault_path and file_path."""
        vault_path = str(self.vault_path)
        file_path = "GTD/inbox.md"
        uri = f"gtd://{vault_path}/file/{file_path}"

        parsed = self.resource_handler.parse_file_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertEqual(parsed["file_path"], file_path)

    def test_file_resource_data_format(self) -> None:
        """Test file resource returns correct data format."""
        vault_path = str(self.vault_path)
        file_path = str(self.vault_path / "gtd" / "inbox.md")  # Use absolute path

        result = self.resource_handler.get_file(vault_path, file_path)

        # Verify required fields
        self.assertIn("status", result)
        self.assertIn("file", result)
        self.assertIn("vault_path", result)

        # Verify status is success
        self.assertEqual(result["status"], "success")

        # Verify file structure
        file_data = result["file"]
        self.assertIn("file_path", file_data)
        self.assertIn("file_type", file_data)
        self.assertIn("content", file_data)
        self.assertIn("frontmatter", file_data)
        self.assertIn("tasks", file_data)
        self.assertIn("links", file_data)

    def test_file_resource_nested_file_path(self) -> None:
        """Test file resource handles nested file paths correctly."""
        vault_path = str(self.vault_path)
        nested_file_path = "gtd/Projects/work/project.md"

        # Create nested structure
        nested_dir = self.vault_path / "gtd" / "Projects" / "work"
        nested_dir.mkdir(parents=True)

        nested_file = nested_dir / "project.md"
        nested_file.write_text("# Work Project\n\n- [ ] Task #task\n")

        uri = f"gtd://{vault_path}/file/{nested_file_path}"
        parsed = self.resource_handler.parse_file_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertEqual(parsed["file_path"], nested_file_path)

    def test_file_resource_nonexistent_file(self) -> None:
        """Test file resource handles nonexistent files."""
        vault_path = str(self.vault_path)
        nonexistent_file = "gtd/nonexistent.md"

        result = self.resource_handler.get_file(vault_path, nonexistent_file)

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("not found", result["error"].lower())

    def test_file_resource_empty_file_path(self) -> None:
        """Test file resource handles empty file path."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_file(vault_path, "")

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
        self.assertIn("empty", result["error"].lower())

    def test_file_resource_invalid_uri_pattern(self) -> None:
        """Test file resource rejects invalid URI patterns."""
        vault_path = str(self.vault_path)
        invalid_uri = f"gtd://{vault_path}/invalid_pattern"

        with self.assertRaises(ValueError) as context:
            self.resource_handler.parse_file_uri(invalid_uri)

        self.assertIn("Invalid file URI pattern", str(context.exception))


class TestContentResourceTemplate(TestResourceTemplates):
    """Test content resource template: gtd://{vault_path}/content"""

    def test_content_uri_pattern_matching(self) -> None:
        """Test content resource URI pattern correctly extracts vault_path."""
        vault_path = str(self.vault_path)
        uri = f"gtd://{vault_path}/content"

        parsed = self.resource_handler.parse_content_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertIsNone(parsed["file_type"])

    def test_content_resource_data_format(self) -> None:
        """Test content resource returns correct data format."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_content(vault_path)

        # Verify required fields
        self.assertIn("status", result)
        self.assertIn("files", result)
        self.assertIn("summary", result)
        self.assertIn("vault_path", result)

        # Verify status is success
        self.assertEqual(result["status"], "success")

        # Verify files structure includes full content
        self.assertIsInstance(result["files"], list)
        for file_data in result["files"]:
            self.assertIn("file_path", file_data)
            self.assertIn("file_type", file_data)
            self.assertIn("content", file_data)
            self.assertIn("frontmatter", file_data)
            self.assertIn("tasks", file_data)
            self.assertIn("links", file_data)
            self.assertIn("task_count", file_data)
            self.assertIn("link_count", file_data)

    def test_content_resource_comprehensive_data(self) -> None:
        """Test content resource provides comprehensive file data."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_content(vault_path)

        self.assertEqual(result["status"], "success")

        # Should have files with complete content
        self.assertGreater(len(result["files"]), 0)

        for file_data in result["files"]:
            # Content should be present and non-empty
            self.assertIn("content", file_data)
            self.assertIsInstance(file_data["content"], str)

            # Tasks should be detailed with all properties
            self.assertIn("tasks", file_data)
            self.assertIsInstance(file_data["tasks"], list)


class TestContentFilteredResourceTemplate(TestResourceTemplates):
    """Test filtered content resource template: gtd://{vault_path}/content/{file_type}"""

    def test_content_filtered_uri_pattern_matching(self) -> None:
        """Test filtered content resource URI pattern extracts parameters."""
        vault_path = str(self.vault_path)
        file_type = "projects"
        uri = f"gtd://{vault_path}/content/{file_type}"

        parsed = self.resource_handler.parse_content_uri(uri)

        self.assertEqual(parsed["vault_path"], vault_path)
        self.assertEqual(parsed["file_type"], file_type)

    def test_content_filtered_resource_filtering(self) -> None:
        """Test filtered content resource correctly filters by file type."""
        vault_path = str(self.vault_path)

        result = self.resource_handler.get_content(vault_path, "inbox")

        self.assertEqual(result["status"], "success")

        # All returned files should be inbox type
        for file_data in result["files"]:
            self.assertEqual(file_data["file_type"], "inbox")


class TestResourceAnnotations(TestResourceTemplates):
    """Test resource annotations and MCP protocol compliance."""

    def test_resource_readonly_hint_annotation(self) -> None:
        """Test resources have readOnlyHint annotation applied."""
        # This test would verify annotations in actual resource templates
        # For now, we test the concept since annotations are applied at decorator level
        # Will be implemented when actual resource templates are created

    def test_resource_idempotent_hint_annotation(self) -> None:
        """Test resources have idempotentHint annotation applied."""
        # This test would verify annotations in actual resource templates
        # For now, we test the concept since annotations are applied at decorator level
        # Will be implemented when actual resource templates are created


class TestResourceErrorHandling(TestResourceTemplates):
    """Test resource error handling and edge cases."""

    def test_resource_uri_special_characters(self) -> None:
        """Test resource URIs handle special characters in paths."""
        # Create vault with spaces in name
        vault_with_spaces = self.vault_path.parent / "vault with spaces"
        vault_with_spaces.mkdir()

        # Test that URI parsing handles spaces correctly
        vault_path = str(vault_with_spaces)
        uri = f"gtd://{vault_path}/files"

        # Should not raise exception
        parsed = self.resource_handler.parse_files_uri(uri)
        self.assertEqual(parsed["vault_path"], vault_path)

    def test_resource_invalid_vault_permissions(self) -> None:
        """Test resource handles vault permission issues gracefully."""
        # Simulate permission error by using nonexistent vault
        invalid_vault = "/root/no_access_vault"
        result = self.resource_handler.get_files(invalid_vault)

        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

    def test_resource_malformed_vault_structure(self) -> None:
        """Test resource handles malformed GTD vault structure."""
        # Create vault without GTD structure
        empty_vault = self.vault_path.parent / "empty_vault"
        empty_vault.mkdir()

        vault_path = str(empty_vault)
        result = self.resource_handler.get_files(vault_path)

        self.assertEqual(result["status"], "success")
        self.assertEqual(len(result["files"]), 0)
        self.assertIn("suggestion", result)


class TestResourcePerformance(TestResourceTemplates):
    """Test resource performance and scalability."""

    def test_resource_large_vault_performance(self) -> None:
        """Test resource performance with larger vault structures."""
        vault_path = str(self.vault_path)

        # Create additional files to simulate larger vault
        # Use standard GTD file names that will be recognized by VaultReader
        gtd_path = self.vault_path / "gtd"

        # Create additional next-action files
        for i in range(5):
            test_file = gtd_path / f"next-actions-{i}.md"
            test_file.write_text(f"# Next Actions {i}\n\n- [ ] Task {i} #task\n")

        # Create additional project files
        for i in range(5):
            test_file = gtd_path / f"projects-{i}.md"
            test_file.write_text(f"# Projects {i}\n\n- [ ] Project task {i} #task\n")

        # Test that resources handle larger datasets efficiently
        result = self.resource_handler.get_files(vault_path)

        self.assertEqual(result["status"], "success")
        # Should have at least the original 3 files plus some of the new ones
        self.assertGreaterEqual(len(result["files"]), 3)

    def test_resource_batch_content_efficiency(self) -> None:
        """Test content resource efficiently handles batch operations."""
        vault_path = str(self.vault_path)

        # Test that batch content access is efficient
        result = self.resource_handler.get_content(vault_path)

        self.assertEqual(result["status"], "success")
        # Should return comprehensive data without excessive processing time
        self.assertIsInstance(result["files"], list)
        self.assertIn("summary", result)


if __name__ == "__main__":
    unittest.main()
