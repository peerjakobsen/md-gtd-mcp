"""ResourceHandler service for MCP resource templates.

This service provides centralized resource logic for GTD vault operations,
reusing existing VaultReader, MarkdownParser, and TaskExtractor services.
Implements URI parsing and data format consistency with existing tool responses.
"""

import urllib.parse
from pathlib import Path
from typing import Any

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.services.vault_reader import VaultReader


class ResourceHandler:
    """Centralized handler for MCP resource operations on GTD vaults.

    Provides URI parsing, data consistency, and error handling for resource templates.
    Maintains compatibility with existing tool response formats while adding
    semantic correctness for MCP resource access patterns.
    """

    def parse_files_uri(self, uri: str) -> dict[str, Any]:
        """Parse files resource URI to extract vault path and optional file type.

        Supports patterns:
        - gtd://{vault_path}/files
        - gtd://{vault_path}/files/{file_type}

        Args:
            uri: Resource URI to parse

        Returns:
            Dictionary with vault_path and file_type (None if not specified)

        Raises:
            ValueError: If URI scheme is invalid or URI is malformed
        """
        parsed = urllib.parse.urlparse(uri)

        if parsed.scheme != "gtd":
            raise ValueError(f"Invalid URI scheme: {parsed.scheme}, expected 'gtd'")

        # Handle both netloc and path for vault path extraction
        # For absolute paths, netloc might be empty and path starts with vault path
        if parsed.netloc:
            vault_path = parsed.netloc
            path_parts = parsed.path.strip("/").split("/")
        elif parsed.path:
            # Handle case where vault path is in the path (absolute paths)
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError(
                    f"Malformed URI: missing vault path or resource pattern in {uri}"
                )

            # Find the "files" component to split vault path from resource path
            try:
                files_index = path_parts.index("files")
                vault_path = "/" + "/".join(path_parts[:files_index])
                path_parts = path_parts[files_index:]
            except ValueError:
                raise ValueError(
                    f"Invalid files URI pattern: missing 'files' component in {uri}"
                ) from None
        else:
            raise ValueError(f"Malformed URI: missing vault path in {uri}")

        # Handle gtd://{vault_path}/files pattern
        if len(path_parts) == 1 and path_parts[0] == "files":
            return {"vault_path": vault_path, "file_type": None}

        # Handle gtd://{vault_path}/files/{file_type} pattern
        if len(path_parts) == 2 and path_parts[0] == "files":
            return {"vault_path": vault_path, "file_type": path_parts[1]}

        raise ValueError(f"Invalid files URI pattern: {uri}")

    def parse_file_uri(self, uri: str) -> dict[str, Any]:
        """Parse file resource URI to extract vault path and file path.

        Supports pattern:
        - gtd://{vault_path}/file/{file_path}

        Args:
            uri: Resource URI to parse

        Returns:
            Dictionary with vault_path and file_path

        Raises:
            ValueError: If URI scheme is invalid or URI is malformed
        """
        parsed = urllib.parse.urlparse(uri)

        if parsed.scheme != "gtd":
            raise ValueError(f"Invalid URI scheme: {parsed.scheme}, expected 'gtd'")

        # Handle both netloc and path for vault path extraction
        if parsed.netloc:
            vault_path = parsed.netloc
            path_parts = parsed.path.strip("/").split("/", 1)  # Split on first / only
        elif parsed.path:
            # Handle case where vault path is in the path (absolute paths)
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 3:  # Need vault_path + "file" + file_path
                raise ValueError(f"Malformed URI: missing components in {uri}")

            # Find the "file" component to split vault path from file path
            try:
                file_index = path_parts.index("file")
                vault_path = "/" + "/".join(path_parts[:file_index])
                # Reconstruct path_parts as ["file", "remaining/path"]
                if file_index + 1 < len(path_parts):
                    remaining_path = "/".join(path_parts[file_index + 1 :])
                    path_parts = ["file", remaining_path]
                else:
                    raise ValueError(
                        f"Invalid file URI pattern: missing file path in {uri}"
                    )
            except ValueError:
                raise ValueError(
                    f"Invalid file URI pattern: missing 'file' component in {uri}"
                ) from None
        else:
            raise ValueError(f"Malformed URI: missing vault path in {uri}")

        # Handle gtd://{vault_path}/file/{file_path} pattern
        if len(path_parts) == 2 and path_parts[0] == "file":
            return {"vault_path": vault_path, "file_path": path_parts[1]}

        raise ValueError(f"Invalid file URI pattern: {uri}")

    def parse_content_uri(self, uri: str) -> dict[str, Any]:
        """Parse content resource URI to extract vault path and optional file type.

        Supports patterns:
        - gtd://{vault_path}/content
        - gtd://{vault_path}/content/{file_type}

        Args:
            uri: Resource URI to parse

        Returns:
            Dictionary with vault_path and file_type (None if not specified)

        Raises:
            ValueError: If URI scheme is invalid or URI is malformed
        """
        parsed = urllib.parse.urlparse(uri)

        if parsed.scheme != "gtd":
            raise ValueError(f"Invalid URI scheme: {parsed.scheme}, expected 'gtd'")

        # Handle both netloc and path for vault path extraction
        if parsed.netloc:
            vault_path = parsed.netloc
            path_parts = parsed.path.strip("/").split("/")
        elif parsed.path:
            # Handle case where vault path is in the path (absolute paths)
            path_parts = parsed.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError(
                    f"Malformed URI: missing vault path or resource pattern in {uri}"
                )

            # Find the "content" component to split vault path from resource path
            try:
                content_index = path_parts.index("content")
                vault_path = "/" + "/".join(path_parts[:content_index])
                path_parts = path_parts[content_index:]
            except ValueError:
                raise ValueError(
                    f"Invalid content URI pattern: missing 'content' component in {uri}"
                ) from None
        else:
            raise ValueError(f"Malformed URI: missing vault path in {uri}")

        # Handle gtd://{vault_path}/content pattern
        if len(path_parts) == 1 and path_parts[0] == "content":
            return {"vault_path": vault_path, "file_type": None}

        # Handle gtd://{vault_path}/content/{file_type} pattern
        if len(path_parts) == 2 and path_parts[0] == "content":
            return {"vault_path": vault_path, "file_type": path_parts[1]}

        raise ValueError(f"Invalid content URI pattern: {uri}")

    def validate_vault_path(self, vault_path: str) -> dict[str, Any]:
        """Validate vault path and return validation result.

        Args:
            vault_path: Path to the vault directory

        Returns:
            Dictionary with validation status and error message if invalid
        """
        if not vault_path or not vault_path.strip():
            return {"valid": False, "error": "Invalid vault path: path cannot be empty"}

        vault_path_obj = Path(vault_path)
        if not vault_path_obj.exists():
            return {"valid": False, "error": f"Vault directory not found: {vault_path}"}

        return {"valid": True, "vault_path": vault_path}

    def validate_file_path(self, vault_path: str, file_path: str) -> dict[str, Any]:
        """Validate file path and return resolved absolute path.

        Args:
            vault_path: Path to the vault directory
            file_path: Path to the file (absolute or relative to vault)

        Returns:
            Dictionary with validation status and resolved path or error message
        """
        if not file_path or not file_path.strip():
            return {"valid": False, "error": "Invalid file path: path cannot be empty"}

        vault_path_obj = Path(vault_path)

        # Handle both absolute and relative file paths
        if Path(file_path).is_absolute():
            file_path_obj = Path(file_path)
        else:
            file_path_obj = vault_path_obj / file_path

        if not file_path_obj.exists():
            return {"valid": False, "error": f"GTD file not found: {file_path}"}

        return {"valid": True, "resolved_path": str(file_path_obj)}

    def get_files(
        self, vault_path: str, file_type: str | None = None
    ) -> dict[str, Any]:
        """Get GTD files with metadata only (equivalent to list_gtd_files_impl).

        Args:
            vault_path: Path to the Obsidian vault directory
            file_type: Optional filter by file type

        Returns:
            Dictionary with status, lightweight file metadata, summary stats,
            and vault path. Maintains exact format compatibility with
            list_gtd_files_impl.
        """
        try:
            # Validate vault path
            vault_validation = self.validate_vault_path(vault_path)
            if not vault_validation["valid"]:
                return {
                    "status": "error",
                    "error": vault_validation["error"],
                    "vault_path": vault_path,
                }

            # Convert to Path object
            vault_path_obj = Path(vault_path)

            # Check GTD structure existence
            gtd_path = vault_path_obj / "gtd"
            gtd_exists = gtd_path.exists()

            # Initialize vault configuration and reader
            vault_config = VaultConfig(vault_path_obj)
            vault_reader = VaultReader(vault_config)

            # Get all GTD files with optional filtering
            try:
                if gtd_exists:
                    gtd_files = vault_reader.list_gtd_files(file_type=file_type)
                else:
                    gtd_files = []
            except Exception:
                # If there's an error reading files, return empty list
                gtd_files = []

            # Convert GTD files to metadata-only format (no full content)
            files_data = []
            for gtd_file in gtd_files:
                file_data = {
                    "file_path": str(gtd_file.path),
                    "file_type": gtd_file.file_type,
                    "task_count": len(gtd_file.tasks),
                    "link_count": len(gtd_file.links),
                }
                files_data.append(file_data)

            # Generate summary statistics
            try:
                if gtd_files:
                    vault_summary = vault_reader.get_vault_summary()
                else:
                    vault_summary = {
                        "total_files": 0,
                        "total_tasks": 0,
                        "total_links": 0,
                        "files_by_type": {},
                        "tasks_by_type": {},
                    }
            except Exception:
                # Fallback summary if vault_reader fails
                total_tasks = 0
                total_links = 0
                for file_data in files_data:
                    task_count = file_data["task_count"]
                    link_count = file_data["link_count"]
                    assert isinstance(task_count, int)
                    assert isinstance(link_count, int)
                    total_tasks += task_count
                    total_links += link_count

                vault_summary = {
                    "total_files": len(files_data),
                    "total_tasks": total_tasks,
                    "total_links": total_links,
                    "files_by_type": {},
                    "tasks_by_type": {},
                }

            # Prepare response
            response = {
                "status": "success",
                "files": files_data,
                "summary": vault_summary,
                "vault_path": vault_path,
            }

            # Add suggestion if no GTD structure exists
            if not gtd_exists or len(files_data) == 0:
                if not gtd_exists:
                    response["suggestion"] = (
                        "No GTD structure found in this vault. "
                        "Use the setup_gtd_vault tool to create the GTD folder "
                        "structure: setup_gtd_vault(vault_path)"
                    )

            return response

        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error listing GTD files: {e}",
                "vault_path": vault_path,
            }

    def get_file(self, vault_path: str, file_path: str) -> dict[str, Any]:
        """Get single GTD file with full content (equivalent to read_gtd_file_impl).

        Args:
            vault_path: Path to the Obsidian vault directory
            file_path: Path to the GTD file to read

        Returns:
            Dictionary with status, file data, and vault path.
            Maintains exact format compatibility with read_gtd_file_impl.
        """
        try:
            # Validate vault path
            vault_validation = self.validate_vault_path(vault_path)
            if not vault_validation["valid"]:
                return {
                    "status": "error",
                    "error": vault_validation["error"],
                    "vault_path": vault_path,
                }

            # Validate file path
            file_validation = self.validate_file_path(vault_path, file_path)
            if not file_validation["valid"]:
                return {
                    "status": "error",
                    "error": file_validation["error"],
                    "vault_path": vault_path,
                }

            # Convert to Path objects
            vault_path_obj = Path(vault_path)
            resolved_file_path = Path(file_validation["resolved_path"])

            # Initialize vault configuration and reader
            vault_config = VaultConfig(vault_path_obj)
            vault_reader = VaultReader(vault_config)

            # Read the GTD file
            gtd_file = vault_reader.read_gtd_file(resolved_file_path)

            # Convert GTD file to dictionary format (exact match with
            # read_gtd_file_impl)
            file_data = {
                "file_path": gtd_file.path,
                "file_type": gtd_file.file_type,
                "content": gtd_file.content,
                "frontmatter": gtd_file.frontmatter.model_dump()
                if gtd_file.frontmatter
                else {},
                "tasks": [
                    {
                        "description": task.text,
                        "completed": task.is_completed,
                        "completion_date": task.done_date.isoformat()
                        if task.done_date
                        else None,
                        "context": task.context,
                        "project": task.project,
                        "energy": task.energy,
                        "time_estimate": task.time_estimate,
                        "delegated_to": task.delegated_to,
                        "tags": task.tags,
                        "priority": task.priority,
                        "due_date": task.due_date.isoformat()
                        if task.due_date
                        else None,
                        "scheduled_date": task.scheduled_date.isoformat()
                        if task.scheduled_date
                        else None,
                        "start_date": task.start_date.isoformat()
                        if task.start_date
                        else None,
                        "raw_text": task.raw_text,
                        "line_number": task.line_number,
                    }
                    for task in gtd_file.tasks
                ],
                "links": [
                    {
                        "type": "external" if link.is_external else "wikilink",
                        "text": link.text,
                        "target": link.target,
                        "is_external": link.is_external,
                        "line_number": link.line_number,
                    }
                    for link in gtd_file.links
                ],
            }

            return {
                "status": "success",
                "file": file_data,
                "vault_path": vault_path,
            }

        except FileNotFoundError as e:
            return {
                "status": "error",
                "error": f"GTD file not found: {e}",
                "vault_path": vault_path,
            }
        except ValueError as e:
            return {
                "status": "error",
                "error": f"Invalid GTD file: {e}",
                "vault_path": vault_path,
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error reading GTD file: {e}",
                "vault_path": vault_path,
            }

    def get_content(
        self, vault_path: str, file_type: str | None = None
    ) -> dict[str, Any]:
        """Get GTD files with comprehensive content (equivalent to read_gtd_files_impl).

        Args:
            vault_path: Path to the Obsidian vault directory
            file_type: Optional filter by file type

        Returns:
            Dictionary with status, files with complete content, summary stats,
            and vault path. Maintains exact format compatibility with
            read_gtd_files_impl.
        """
        try:
            # Validate vault path
            vault_validation = self.validate_vault_path(vault_path)
            if not vault_validation["valid"]:
                return {
                    "status": "error",
                    "error": vault_validation["error"],
                    "vault_path": vault_path,
                }

            # Convert to Path object
            vault_path_obj = Path(vault_path)

            # Check GTD structure existence
            gtd_path = vault_path_obj / "gtd"
            gtd_exists = gtd_path.exists()

            # Initialize vault configuration and reader
            vault_config = VaultConfig(vault_path_obj)
            vault_reader = VaultReader(vault_config)

            # Get all GTD files with optional filtering
            try:
                if gtd_exists:
                    gtd_files = vault_reader.list_gtd_files(file_type=file_type)
                else:
                    gtd_files = []
            except Exception:
                # If there's an error reading files, return empty list
                gtd_files = []

            # Convert GTD files to complete format with full content
            files_data = []
            for gtd_file in gtd_files:
                file_data = {
                    "file_path": str(gtd_file.path),
                    "file_type": gtd_file.file_type,
                    "content": gtd_file.content,
                    "frontmatter": gtd_file.frontmatter.model_dump()
                    if gtd_file.frontmatter
                    else {},
                    "tasks": [
                        {
                            "description": task.text,
                            "completed": task.is_completed,
                            "completion_date": task.done_date.isoformat()
                            if task.done_date
                            else None,
                            "context": task.context,
                            "project": task.project,
                            "energy": task.energy,
                            "time_estimate": task.time_estimate,
                            "delegated_to": task.delegated_to,
                            "tags": task.tags,
                            "priority": task.priority,
                            "due_date": task.due_date.isoformat()
                            if task.due_date
                            else None,
                            "scheduled_date": task.scheduled_date.isoformat()
                            if task.scheduled_date
                            else None,
                            "start_date": task.start_date.isoformat()
                            if task.start_date
                            else None,
                            "raw_text": task.raw_text,
                            "line_number": task.line_number,
                        }
                        for task in gtd_file.tasks
                    ],
                    "links": [
                        {
                            "type": "external" if link.is_external else "wikilink",
                            "text": link.text,
                            "target": link.target,
                            "is_external": link.is_external,
                            "line_number": link.line_number,
                        }
                        for link in gtd_file.links
                    ],
                    "task_count": len(gtd_file.tasks),
                    "link_count": len(gtd_file.links),
                }
                files_data.append(file_data)

            # Generate comprehensive summary statistics
            try:
                if gtd_files:
                    vault_summary = vault_reader.get_vault_summary()
                else:
                    vault_summary = {
                        "total_files": 0,
                        "total_tasks": 0,
                        "total_links": 0,
                        "files_by_type": {},
                        "tasks_by_type": {},
                    }
            except Exception:
                # Fallback summary if vault_reader fails
                total_tasks = 0
                total_links = 0
                for file_data in files_data:
                    task_count = file_data["task_count"]
                    link_count = file_data["link_count"]
                    assert isinstance(task_count, int)
                    assert isinstance(link_count, int)
                    total_tasks += task_count
                    total_links += link_count

                vault_summary = {
                    "total_files": len(files_data),
                    "total_tasks": total_tasks,
                    "total_links": total_links,
                    "files_by_type": {},
                    "tasks_by_type": {},
                }

            # Prepare comprehensive response
            response = {
                "status": "success",
                "files": files_data,
                "summary": vault_summary,
                "vault_path": vault_path,
            }

            # Add suggestion if no GTD structure exists
            if not gtd_exists or len(files_data) == 0:
                if not gtd_exists:
                    response["suggestion"] = (
                        "No GTD structure found in this vault. "
                        "Use the setup_gtd_vault tool to create the GTD folder "
                        "structure: setup_gtd_vault(vault_path)"
                    )

            return response

        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error reading GTD files: {e}",
                "vault_path": vault_path,
            }
