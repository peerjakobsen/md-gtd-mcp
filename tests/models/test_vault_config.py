"""Tests for VaultConfig data model."""

from pathlib import Path

from md_gtd_mcp.models.vault_config import VaultConfig


class TestVaultConfig:
    """Test VaultConfig data model."""

    def test_vault_config_creation(self) -> None:
        """Test creating a basic vault config."""
        config = VaultConfig(
            vault_path="/Users/test/Documents/ObsidianVault", gtd_folder="gtd"
        )
        assert config.vault_path == Path("/Users/test/Documents/ObsidianVault")
        assert config.gtd_folder == "gtd"

    def test_vault_config_with_path_object(self) -> None:
        """Test creating config with Path object."""
        vault_path = Path("/Users/test/vault")
        config = VaultConfig(vault_path=vault_path, gtd_folder="gtd")
        assert config.vault_path == vault_path
        assert config.gtd_folder == "gtd"

    def test_vault_config_default_gtd_folder(self) -> None:
        """Test default GTD folder name."""
        config = VaultConfig(vault_path="/Users/test/vault")
        assert config.gtd_folder == "gtd"

    def test_get_gtd_path(self) -> None:
        """Test getting full GTD folder path."""
        config = VaultConfig(vault_path="/Users/test/vault", gtd_folder="productivity")
        expected_path = Path("/Users/test/vault/productivity")
        assert config.get_gtd_path() == expected_path

    def test_get_inbox_path(self) -> None:
        """Test getting inbox file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/inbox.md")
        assert config.get_inbox_path() == expected_path

    def test_get_projects_path(self) -> None:
        """Test getting projects file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/projects.md")
        assert config.get_projects_path() == expected_path

    def test_get_next_actions_path(self) -> None:
        """Test getting next-actions file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/next-actions.md")
        assert config.get_next_actions_path() == expected_path

    def test_get_waiting_for_path(self) -> None:
        """Test getting waiting-for file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/waiting-for.md")
        assert config.get_waiting_for_path() == expected_path

    def test_get_someday_maybe_path(self) -> None:
        """Test getting someday-maybe file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/someday-maybe.md")
        assert config.get_someday_maybe_path() == expected_path

    def test_get_contexts_path(self) -> None:
        """Test getting contexts folder path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/contexts")
        assert config.get_contexts_path() == expected_path

    def test_get_context_file_path(self) -> None:
        """Test getting specific context file path."""
        config = VaultConfig(vault_path="/Users/test/vault")
        expected_path = Path("/Users/test/vault/gtd/contexts/@calls.md")
        assert config.get_context_file_path("@calls") == expected_path

    def test_get_all_gtd_files(self) -> None:
        """Test getting all standard GTD file paths."""
        config = VaultConfig(vault_path="/Users/test/vault")
        files = config.get_all_gtd_files()

        expected_files = [
            Path("/Users/test/vault/gtd/inbox.md"),
            Path("/Users/test/vault/gtd/projects.md"),
            Path("/Users/test/vault/gtd/next-actions.md"),
            Path("/Users/test/vault/gtd/waiting-for.md"),
            Path("/Users/test/vault/gtd/someday-maybe.md"),
        ]

        assert files == expected_files

    def test_is_gtd_file(self) -> None:
        """Test checking if a path is a GTD file."""
        config = VaultConfig(vault_path="/Users/test/vault")

        # Test standard GTD files
        assert config.is_gtd_file(Path("/Users/test/vault/gtd/inbox.md")) is True
        assert config.is_gtd_file(Path("/Users/test/vault/gtd/projects.md")) is True
        assert (
            config.is_gtd_file(Path("/Users/test/vault/gtd/contexts/@calls.md")) is True
        )

        # Test non-GTD files
        assert config.is_gtd_file(Path("/Users/test/vault/notes/random.md")) is False
        assert config.is_gtd_file(Path("/Users/other/vault/gtd/inbox.md")) is False

    def test_custom_gtd_folder(self) -> None:
        """Test with custom GTD folder name."""
        config = VaultConfig(vault_path="/Users/test/vault", gtd_folder="productivity")

        assert config.get_inbox_path() == Path(
            "/Users/test/vault/productivity/inbox.md"
        )
        assert config.get_contexts_path() == Path(
            "/Users/test/vault/productivity/contexts"
        )

        # Test is_gtd_file with custom folder
        assert (
            config.is_gtd_file(Path("/Users/test/vault/productivity/inbox.md")) is True
        )
        assert config.is_gtd_file(Path("/Users/test/vault/gtd/inbox.md")) is False
