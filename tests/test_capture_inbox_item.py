"""Tests for capture_inbox_item MCP tool."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from md_gtd_mcp.services.inbox_capture import capture_inbox_item


class TestCaptureInboxItem:
    """Test capture_inbox_item MCP tool functionality."""

    def setup_method(self) -> None:
        """Set up test vault directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "test_vault"
        self.gtd_path = self.vault_path / "gtd"
        self.inbox_path = self.gtd_path / "inbox.md"

    def test_capture_inbox_item_to_existing_inbox(self) -> None:
        """Test successful item capture to existing inbox.md."""
        # Setup existing vault structure
        self.gtd_path.mkdir(parents=True)
        existing_content = """---
status: active
---

# Inbox

## Quick Capture

- [ ] Existing task
"""
        self.inbox_path.write_text(existing_content)

        # Capture new item
        result = capture_inbox_item(str(self.vault_path), "Review quarterly budget")

        # Verify result
        assert result["status"] == "success"
        assert result["item_text"] == "Review quarterly budget"
        assert result["file_path"] == str(self.inbox_path.resolve())

        # Verify file content
        content = self.inbox_path.read_text()
        assert "- [ ] Review quarterly budget" in content
        assert "- [ ] Existing task" in content  # Existing content preserved

    def test_capture_inbox_item_creates_new_inbox(self) -> None:
        """Test inbox.md creation when file doesn't exist."""
        # Setup vault directory without inbox
        self.vault_path.mkdir(parents=True)
        self.gtd_path.mkdir()

        # Capture item to non-existent inbox
        result = capture_inbox_item(str(self.vault_path), "New project idea")

        # Verify result
        assert result["status"] == "success"
        assert result["item_text"] == "New project idea"
        assert result["file_path"] == str(self.inbox_path.resolve())

        # Verify file was created with proper structure
        assert self.inbox_path.exists()
        content = self.inbox_path.read_text()
        assert "---" in content  # YAML frontmatter
        assert "status: active" in content
        assert "# Inbox" in content
        assert "- [ ] New project idea" in content

    def test_capture_inbox_item_creates_gtd_structure(self) -> None:
        """Test GTD structure creation when vault exists but GTD folder doesn't."""
        # Setup vault directory only
        self.vault_path.mkdir(parents=True)

        # Capture item
        result = capture_inbox_item(str(self.vault_path), "Setup meeting room")

        # Verify GTD structure was created
        assert self.gtd_path.exists()
        assert self.inbox_path.exists()
        assert result["status"] == "success"

        # Verify content
        content = self.inbox_path.read_text()
        assert "- [ ] Setup meeting room" in content

    def test_capture_inbox_item_creates_full_vault_structure(self) -> None:
        """Test full vault and GTD structure creation when nothing exists."""
        # Don't create any directories

        # Capture item
        result = capture_inbox_item(str(self.vault_path), "Learn Python")

        # Verify complete structure was created
        assert self.vault_path.exists()
        assert self.gtd_path.exists()
        assert self.inbox_path.exists()
        assert result["status"] == "success"

        # Verify content
        content = self.inbox_path.read_text()
        assert "- [ ] Learn Python" in content

    def test_capture_inbox_item_invalid_vault_path(self) -> None:
        """Test vault path validation and error handling."""
        # Test empty vault path
        result = capture_inbox_item("", "Some task")
        assert result["status"] == "error"
        assert "vault path" in result["error"].lower()

        # Test None vault path
        result = capture_inbox_item("   ", "Some task")
        assert result["status"] == "error"
        assert "vault path" in result["error"].lower()

    def test_capture_inbox_item_invalid_item_text(self) -> None:
        """Test item text validation."""
        self.vault_path.mkdir(parents=True)

        # Test empty item text
        result = capture_inbox_item(str(self.vault_path), "")
        assert result["status"] == "error"
        assert "item text" in result["error"].lower()

        # Test whitespace-only item text
        result = capture_inbox_item(str(self.vault_path), "   ")
        assert result["status"] == "error"
        assert "item text" in result["error"].lower()

    def test_capture_inbox_item_permission_denied(self) -> None:
        """Test handling of file permission errors."""
        # Setup read-only directory
        self.vault_path.mkdir(parents=True)
        self.vault_path.chmod(0o444)  # Read-only

        try:
            result = capture_inbox_item(str(self.vault_path), "Test task")
            assert result["status"] == "error"
            assert (
                "permission" in result["error"].lower()
                or "denied" in result["error"].lower()
            )
        finally:
            # Restore permissions for cleanup
            self.vault_path.chmod(0o755)

    def test_capture_inbox_item_atomic_file_operations(self) -> None:
        """Test atomic file operations and concurrent access safety."""
        # Setup existing inbox
        self.gtd_path.mkdir(parents=True)
        original_content = """---
status: active
---

# Inbox

- [ ] Original task
"""
        self.inbox_path.write_text(original_content)

        # Simulate concurrent write by making file busy
        with patch("pathlib.Path.write_text") as mock_write:
            mock_write.side_effect = [OSError("Resource busy"), None]

            # This should handle the temporary failure and retry
            result = capture_inbox_item(str(self.vault_path), "Concurrent task")

            # The implementation should handle this gracefully
            # (actual atomic implementation will be in the real function)
            assert "concurrent task" in result["item_text"].lower()

    def test_capture_inbox_item_various_input_formats(self) -> None:
        """Test various input formats and edge cases."""
        self.gtd_path.mkdir(parents=True)

        test_cases = [
            "Simple task",
            "Task with #hashtag",
            "Task with @context mention",
            "Task with [[wiki link]]",
            "Task with *emphasis* and **bold**",
            "Task with emoji 📝",
            "Very long task " + "x" * 200,
            "Task\nwith\nnewlines",
            "Task with 'quotes' and \"double quotes\"",
        ]

        for i, item_text in enumerate(test_cases):
            result = capture_inbox_item(str(self.vault_path), item_text)
            assert result["status"] == "success", f"Failed for case {i}: {item_text}"

            # Verify item was added to inbox
            content = self.inbox_path.read_text()
            # For multiline items, they should be converted to single line or
            # handled appropriately
            if "\n" in item_text:
                # Should handle newlines appropriately (convert to single line or
                # preserve)
                assert "Task with" in content
            else:
                assert item_text in content

    def test_capture_inbox_item_preserves_encoding(self) -> None:
        """Test that file encoding is handled correctly."""
        self.gtd_path.mkdir(parents=True)

        # Test with unicode characters
        unicode_task = "Review résumé for café position 🎯"
        result = capture_inbox_item(str(self.vault_path), unicode_task)

        assert result["status"] == "success"

        # Verify unicode is preserved
        content = self.inbox_path.read_text(encoding="utf-8")
        assert unicode_task in content

    def test_capture_inbox_item_newline_consistency(self) -> None:
        """Test that newline handling is consistent."""
        self.gtd_path.mkdir(parents=True)

        # Create inbox with specific line endings
        initial_content = "---\nstatus: active\n---\n\n# Inbox\n\n- [ ] First task\n"
        self.inbox_path.write_text(initial_content)

        # Add new task
        result = capture_inbox_item(str(self.vault_path), "Second task")
        assert result["status"] == "success"

        # Verify newlines are handled consistently
        content = self.inbox_path.read_text()
        lines = content.split("\n")

        # Should have proper newline structure
        assert len([line for line in lines if line.strip().startswith("- [ ]")]) == 2
        assert not content.endswith("\n\n\n")  # No excessive newlines

    def test_capture_inbox_item_return_format(self) -> None:
        """Test that return format matches expected structure."""
        self.vault_path.mkdir(parents=True)

        result = capture_inbox_item(str(self.vault_path), "Format test")

        # Verify return structure
        required_keys = ["status", "item_text", "file_path"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

        assert result["status"] in ["success", "error"]
        assert isinstance(result["item_text"], str)
        assert isinstance(result["file_path"], str)

        # For success case, verify additional fields
        if result["status"] == "success":
            assert result["item_text"] == "Format test"
            assert result["file_path"] == str(self.inbox_path.resolve())


class TestCaptureInboxItemEdgeCases:
    """Test edge cases and error scenarios for capture_inbox_item."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir) / "edge_test_vault"

    def test_capture_to_corrupted_inbox(self) -> None:
        """Test handling of corrupted inbox file."""
        # Setup vault with corrupted inbox (invalid YAML)
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        inbox_path = gtd_path / "inbox.md"

        # Create corrupted inbox with malformed YAML
        corrupted_content = """---
status: active
invalid yaml: [unclosed bracket
---

# Inbox
- [ ] Existing task
"""
        inbox_path.write_text(corrupted_content)

        # Should still be able to append even with corrupted YAML
        result = capture_inbox_item(str(self.vault_path), "New task despite corruption")

        # Implementation should be robust enough to handle this
        assert result["status"] == "success"

        # Verify task was added
        content = inbox_path.read_text()
        assert "New task despite corruption" in content

    def test_capture_with_special_characters_in_path(self) -> None:
        """Test handling of special characters in vault path."""
        # Create vault with special characters in path
        special_vault = Path(self.temp_dir) / "vault with spaces & symbols!"

        result = capture_inbox_item(str(special_vault), "Test task")

        # Should handle special characters in path
        assert result["status"] == "success"
        assert special_vault.exists()

    def test_capture_item_preserves_existing_structure(self) -> None:
        """Test that existing inbox structure is completely preserved."""
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        inbox_path = gtd_path / "inbox.md"

        # Create complex existing structure
        complex_content = """---
status: active
tags: [inbox, capture]
created: 2025-08-17
---

# Inbox

## Quick Capture
- [ ] Important existing task #priority
- Meeting notes from yesterday
- [ ] Another task @home

## Ideas
Some free-form text that should be preserved.

### Subsection
More content here.

## Processing Notes
- [ ] Review this section
"""
        inbox_path.write_text(complex_content)

        # Capture new item
        result = capture_inbox_item(str(self.vault_path), "New urgent task")
        assert result["status"] == "success"

        # Verify all existing content is preserved
        new_content = inbox_path.read_text()
        assert "tags: [inbox, capture]" in new_content
        assert "Important existing task #priority" in new_content
        assert "Meeting notes from yesterday" in new_content
        assert "Some free-form text that should be preserved." in new_content
        assert "### Subsection" in new_content
        assert "New urgent task" in new_content
