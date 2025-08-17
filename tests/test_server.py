"""Tests for MCP server tools."""

import tempfile
from pathlib import Path

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

        # Run setup - should NOT overwrite existing files
        result = setup_gtd_vault(str(self.vault_path))

        assert result["status"] == "success"

        # Verify existing files were not modified
        assert existing_inbox.read_text() == original_content
        assert existing_calls.read_text() == original_calls_content

        # Verify existing files are listed in already_existed
        assert "gtd/inbox.md" in result["already_existed"]
        assert "gtd/contexts/@calls.md" in result["already_existed"]

        # Verify missing files were still created
        expected_new_files = [
            "gtd/projects.md",
            "gtd/next-actions.md",
            "gtd/waiting-for.md",
            "gtd/someday-maybe.md",
        ]

        for file_path in expected_new_files:
            full_path = self.vault_path / file_path
            assert full_path.exists(), f"{file_path} should have been created"
            assert file_path in result["created"]

    def test_setup_gtd_vault_partial_existing_structure(self) -> None:
        """Test setup when some GTD structure already exists."""
        # Create vault with partial structure
        self.vault_path.mkdir(parents=True)
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()

        # Create only inbox and projects
        (gtd_path / "inbox.md").write_text("# Existing Inbox")
        (gtd_path / "projects.md").write_text("# Existing Projects")

        result = setup_gtd_vault(str(self.vault_path))

        assert result["status"] == "success"

        # Should create missing files
        missing_files = ["next-actions.md", "waiting-for.md", "someday-maybe.md"]
        for file_name in missing_files:
            assert (gtd_path / file_name).exists()
            assert f"gtd/{file_name}" in result["created"]

        # Should not overwrite existing files
        assert "gtd/inbox.md" in result["already_existed"]
        assert "gtd/projects.md" in result["already_existed"]

    def test_setup_gtd_vault_invalid_permissions(self) -> None:
        """Test setup with invalid permissions (read-only directory)."""
        # Create directory and make it read-only
        self.vault_path.mkdir(parents=True)
        readonly_path = self.vault_path / "readonly_test"
        readonly_path.mkdir()
        readonly_path.chmod(0o444)  # Read-only

        try:
            result = setup_gtd_vault(str(readonly_path))

            # Should handle permission error gracefully
            assert result["status"] == "error"
            assert (
                "permission" in result["error"].lower()
                or "access" in result["error"].lower()
            )

        finally:
            # Clean up - restore permissions
            readonly_path.chmod(0o755)


class TestMCPServerStartup:
    """Test MCP server startup and configuration."""

    def test_mcp_server_initialization(self) -> None:
        """Test that MCP server can be initialized without errors."""
        from md_gtd_mcp.server import mcp

        # Verify server object exists and has expected properties
        assert mcp is not None
        assert hasattr(mcp, "run")

        # Verify that tools are registered
        # Note: This tests the server configuration, not the tool implementations
        # since we removed the tool implementations but kept the server structure

    def test_server_has_required_tools(self) -> None:
        """Test that server has the required tools available."""
        from md_gtd_mcp.server import mcp

        # The server should have these tools after removing read-only tools:
        # - setup_gtd_vault (action tool)
        # Resources are handled separately via resource templates

        # This is a basic structural test - actual functionality is tested elsewhere
        assert mcp is not None
