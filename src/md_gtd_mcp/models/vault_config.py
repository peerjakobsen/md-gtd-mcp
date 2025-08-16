"""VaultConfig data model for Obsidian vault configuration."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VaultConfig:
    """Configuration for Obsidian vault with GTD folder structure."""

    vault_path: Path
    gtd_folder: str = "gtd"

    def __init__(self, vault_path: str | Path, gtd_folder: str = "gtd"):
        """Initialize vault config with path normalization."""
        self.vault_path = Path(vault_path)
        self.gtd_folder = gtd_folder

    def get_gtd_path(self) -> Path:
        """Get the full path to the GTD folder."""
        return self.vault_path / self.gtd_folder

    def get_inbox_path(self) -> Path:
        """Get the path to the inbox file."""
        return self.get_gtd_path() / "inbox.md"

    def get_projects_path(self) -> Path:
        """Get the path to the projects file."""
        return self.get_gtd_path() / "projects.md"

    def get_next_actions_path(self) -> Path:
        """Get the path to the next-actions file."""
        return self.get_gtd_path() / "next-actions.md"

    def get_waiting_for_path(self) -> Path:
        """Get the path to the waiting-for file."""
        return self.get_gtd_path() / "waiting-for.md"

    def get_someday_maybe_path(self) -> Path:
        """Get the path to the someday-maybe file."""
        return self.get_gtd_path() / "someday-maybe.md"

    def get_contexts_path(self) -> Path:
        """Get the path to the contexts folder."""
        return self.get_gtd_path() / "contexts"

    def get_context_file_path(self, context_name: str) -> Path:
        """Get the path to a specific context file.

        Args:
            context_name: Context name (e.g., '@calls')

        Returns:
            Path to the context file
        """
        return self.get_contexts_path() / f"{context_name}.md"

    def get_all_gtd_files(self) -> list[Path]:
        """Get all standard GTD file paths.

        Returns:
            List of paths to standard GTD files (excludes contexts)
        """
        return [
            self.get_inbox_path(),
            self.get_projects_path(),
            self.get_next_actions_path(),
            self.get_waiting_for_path(),
            self.get_someday_maybe_path(),
        ]

    def is_gtd_file(self, file_path: Path) -> bool:
        """Check if a file path is within the GTD folder structure.

        Args:
            file_path: Path to check

        Returns:
            True if the file is within the GTD folder structure
        """
        try:
            # Check if the file path is relative to the GTD folder
            file_path.relative_to(self.get_gtd_path())
            return True
        except ValueError:
            # File is not within the GTD folder
            return False
