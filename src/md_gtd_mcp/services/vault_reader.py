"""VaultReader service for reading GTD vaults."""

from pathlib import Path

from ..models import GTDFile, VaultConfig
from ..parsers import MarkdownParser


class VaultReader:
    """Service for reading GTD files from Obsidian vaults."""

    def __init__(self, vault_config: VaultConfig) -> None:
        """Initialize VaultReader with vault configuration.

        Args:
            vault_config: Configuration for the GTD vault
        """
        self.vault_config = vault_config

    def read_gtd_file(self, file_path: Path) -> GTDFile:
        """Read and parse a single GTD file.

        Args:
            file_path: Path to the GTD file to read

        Returns:
            Parsed GTDFile object

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not within the GTD folder structure
        """
        # Validate file exists
        if not file_path.exists():
            raise FileNotFoundError(f"GTD file not found: {file_path}")

        # Validate file is within GTD folder structure
        if not self.vault_config.is_gtd_file(file_path):
            raise ValueError(f"File {file_path} is not within GTD folder structure")

        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Parse using MarkdownParser
        return MarkdownParser.parse_file(content, file_path)

    def list_gtd_files(self, file_type: str | None = None) -> list[GTDFile]:
        """List all GTD files in the vault.

        Args:
            file_type: Optional filter by file type (inbox, projects, etc.)

        Returns:
            List of parsed GTDFile objects
        """
        gtd_files = []

        # Get all standard GTD files
        standard_files = self.vault_config.get_all_gtd_files()
        for file_path in standard_files:
            if file_path.exists():
                try:
                    gtd_file = self.read_gtd_file(file_path)
                    gtd_files.append(gtd_file)
                except Exception:
                    # Skip files that can't be parsed
                    continue

        # Get context files
        contexts_path = self.vault_config.get_contexts_path()
        if contexts_path.exists():
            for context_file in contexts_path.glob("*.md"):
                try:
                    gtd_file = self.read_gtd_file(context_file)
                    gtd_files.append(gtd_file)
                except Exception:
                    # Skip files that can't be parsed
                    continue

        # Filter by file type if specified
        if file_type:
            gtd_files = [f for f in gtd_files if f.file_type == file_type]

        return gtd_files

    def read_all_gtd_files(self) -> list[GTDFile]:
        """Read all GTD files in the vault.

        Returns:
            List of all parsed GTDFile objects in the vault
        """
        return self.list_gtd_files()

    def get_gtd_files_by_type(self, file_type: str) -> list[GTDFile]:
        """Get GTD files of a specific type.

        Args:
            file_type: The file type to filter by

        Returns:
            List of GTDFile objects of the specified type
        """
        return self.list_gtd_files(file_type=file_type)

    def get_inbox_files(self) -> list[GTDFile]:
        """Get inbox files.

        Returns:
            List of inbox GTDFile objects
        """
        return self.get_gtd_files_by_type("inbox")

    def get_project_files(self) -> list[GTDFile]:
        """Get project files.

        Returns:
            List of project GTDFile objects
        """
        return self.get_gtd_files_by_type("projects")

    def get_next_action_files(self) -> list[GTDFile]:
        """Get next-actions files.

        Returns:
            List of next-actions GTDFile objects
        """
        return self.get_gtd_files_by_type("next-actions")

    def get_waiting_for_files(self) -> list[GTDFile]:
        """Get waiting-for files.

        Returns:
            List of waiting-for GTDFile objects
        """
        return self.get_gtd_files_by_type("waiting-for")

    def get_someday_files(self) -> list[GTDFile]:
        """Get someday-maybe files.

        Returns:
            List of someday-maybe GTDFile objects
        """
        return self.get_gtd_files_by_type("someday-maybe")

    def get_context_files(self) -> list[GTDFile]:
        """Get context files.

        Returns:
            List of context GTDFile objects
        """
        return self.get_gtd_files_by_type("context")

    def find_files_by_context(self, context: str) -> list[GTDFile]:
        """Find files containing references to a specific context.

        Args:
            context: Context name (e.g., '@calls', '@errands')

        Returns:
            List of GTDFile objects containing the specified context
        """
        all_files = self.read_all_gtd_files()
        matching_files = []

        for gtd_file in all_files:
            # Check if any links match the context
            for link in gtd_file.links:
                if link.target == context or link.text == context.lstrip("@"):
                    matching_files.append(gtd_file)
                    break

        return matching_files

    def find_files_with_tasks(self) -> list[GTDFile]:
        """Find files that contain tasks.

        Returns:
            List of GTDFile objects containing tasks
        """
        all_files = self.read_all_gtd_files()
        return [f for f in all_files if f.tasks]

    def get_vault_summary(self) -> dict[str, int | dict[str, int]]:
        """Get summary statistics for the vault.

        Returns:
            Dictionary with counts of files, tasks, links by type
        """
        all_files = self.read_all_gtd_files()

        summary: dict[str, int | dict[str, int]] = {
            "total_files": len(all_files),
            "total_tasks": sum(len(f.tasks) for f in all_files),
            "total_links": sum(len(f.links) for f in all_files),
            "files_by_type": {},
            "tasks_by_type": {},
        }

        for gtd_file in all_files:
            file_type = gtd_file.file_type

            # Count files by type
            files_by_type = summary["files_by_type"]
            assert isinstance(files_by_type, dict)
            files_by_type[file_type] = files_by_type.get(file_type, 0) + 1

            # Count tasks by file type
            tasks_by_type = summary["tasks_by_type"]
            assert isinstance(tasks_by_type, dict)
            tasks_by_type[file_type] = tasks_by_type.get(file_type, 0) + len(
                gtd_file.tasks
            )

        return summary
