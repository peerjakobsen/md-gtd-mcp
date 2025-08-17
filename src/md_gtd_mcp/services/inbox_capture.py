"""Inbox capture service for GTD capture phase implementation."""

import os
from pathlib import Path
from typing import Any


def capture_inbox_item(vault_path: str, item_text: str) -> dict[str, Any]:
    """Capture item to GTD inbox following capture phase principles.

    This function implements the GTD Capture phase by adding items directly to
    the inbox without requiring metadata, contexts, or categorization. Items are
    added as simple `- [ ] {item_text}` format without #task tags, following
    GTD methodology where contexts and tags are assigned during Clarify phase.

    Args:
        vault_path: Path to the Obsidian vault directory
        item_text: Text content to capture in inbox

    Returns:
        Dictionary with status, item_text, file_path, and any error information
    """
    # Validate inputs
    if not vault_path or not vault_path.strip():
        return {
            "status": "error",
            "error": "Invalid vault path: cannot be empty",
            "item_text": item_text,
            "file_path": "",
        }

    if not item_text or not item_text.strip():
        return {
            "status": "error",
            "error": "Invalid item text: cannot be empty",
            "item_text": item_text,
            "file_path": "",
        }

    try:
        # Enhanced vault validation
        validation_result = _validate_and_prepare_vault(vault_path)
        if validation_result["status"] == "error":
            return {
                "status": "error",
                "error": validation_result["error"],
                "item_text": item_text,
                "file_path": "",
            }

        vault = validation_result["vault_path"]
        gtd_path = validation_result["gtd_path"]
        inbox_path = validation_result["inbox_path"]

        # Clean item text (handle newlines, strip whitespace)
        clean_item_text = item_text.strip().replace("\n", " ").replace("\r", "")

        # Create inbox file if it doesn't exist
        if not inbox_path.exists():
            _create_new_inbox_file_enhanced(inbox_path, clean_item_text)
        else:
            _append_to_existing_inbox_enhanced(inbox_path, clean_item_text)

        return {
            "status": "success",
            "item_text": clean_item_text,
            "file_path": str(inbox_path),
        }

    except PermissionError as e:
        return {
            "status": "error",
            "error": f"Permission denied: {str(e)}",
            "item_text": item_text,
            "file_path": str(inbox_path) if "inbox_path" in locals() else "",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to capture inbox item: {str(e)}",
            "item_text": item_text,
            "file_path": str(inbox_path) if "inbox_path" in locals() else "",
        }


def _validate_and_prepare_vault(vault_path: str) -> dict[str, Any]:
    """Validate vault path and prepare GTD structure with comprehensive checks.

    This function performs robust validation of the vault path and GTD structure,
    including permission checks, disk space validation, and safe directory creation.
    It follows the same safety principles as setup_gtd_vault.

    Args:
        vault_path: Path to the Obsidian vault directory

    Returns:
        Dictionary with validation status and prepared paths or error information
    """
    try:
        # Normalize and validate path
        vault = Path(vault_path).resolve()

        # Check if path is valid and accessible
        if not _is_valid_path(vault):
            return {
                "status": "error",
                "error": f"Invalid vault path: {vault_path}",
            }

        # Check parent directory permissions if vault doesn't exist
        if not vault.exists():
            parent = vault.parent
            if not parent.exists():
                # Try to create parent directories
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except (PermissionError, OSError) as e:
                    return {
                        "status": "error",
                        "error": f"Cannot create vault parent directory: {str(e)}",
                    }

            # Check parent directory is writable
            if not os.access(parent, os.W_OK):
                return {
                    "status": "error",
                    "error": (
                        f"No write permission for vault parent directory: {parent}"
                    ),
                }

        # Check vault directory permissions if it exists
        elif not os.access(vault, os.W_OK):
            return {
                "status": "error",
                "error": f"No write permission for vault directory: {vault}",
            }

        # Check available disk space (require at least 1MB free)
        if not _check_disk_space(vault.parent if not vault.exists() else vault):
            return {
                "status": "error",
                "error": "Insufficient disk space for vault operations",
            }

        # Create vault directory if needed
        if not vault.exists():
            vault.mkdir(parents=True, exist_ok=True)

        # Prepare GTD structure
        gtd_path = vault / "gtd"
        inbox_path = gtd_path / "inbox.md"

        # Create GTD directory if needed
        if not gtd_path.exists():
            gtd_path.mkdir(exist_ok=True)
        elif not gtd_path.is_dir():
            return {
                "status": "error",
                "error": f"GTD path exists but is not a directory: {gtd_path}",
            }

        # Validate inbox file if it exists
        if inbox_path.exists():
            if not inbox_path.is_file():
                return {
                    "status": "error",
                    "error": f"Inbox path exists but is not a file: {inbox_path}",
                }

            # Check if inbox file is readable and writable
            if not os.access(inbox_path, os.R_OK | os.W_OK):
                return {
                    "status": "error",
                    "error": f"Insufficient permissions for inbox file: {inbox_path}",
                }

            # Validate inbox file is not corrupted beyond repair
            try:
                content = inbox_path.read_text(encoding="utf-8")
                # Basic validation - file should be readable as text
                if len(content) > 1024 * 1024:  # 1MB limit for safety
                    return {
                        "status": "error",
                        "error": "Inbox file is too large (>1MB) - may be corrupted",
                    }
            except (UnicodeDecodeError, OSError) as e:
                return {
                    "status": "error",
                    "error": f"Cannot read inbox file: {str(e)}",
                }

        return {
            "status": "success",
            "vault_path": vault,
            "gtd_path": gtd_path,
            "inbox_path": inbox_path,
        }

    except Exception as e:
        return {
            "status": "error",
            "error": f"Vault validation failed: {str(e)}",
        }


def _is_valid_path(path: Path) -> bool:
    """Check if path is valid and safe for file operations."""
    try:
        # Convert to absolute path to check validity
        abs_path = path.resolve()

        # Basic security checks
        path_str = str(abs_path)

        # Check for dangerous path patterns
        dangerous_patterns = ["..", "/dev/", "/proc/", "/sys/"]
        if any(pattern in path_str for pattern in dangerous_patterns):
            return False

        # Check path length (some filesystems have limits)
        if len(path_str) > 4096:
            return False

        # Check for invalid characters (basic check)
        invalid_chars = ["\0", "\x00"]
        if any(char in path_str for char in invalid_chars):
            return False

        return True

    except (OSError, ValueError):
        return False


def _check_disk_space(path: Path, min_free_bytes: int = 1024 * 1024) -> bool:
    """Check if there's sufficient disk space available."""
    try:
        # Get the path that exists (walk up if necessary)
        check_path = path
        while not check_path.exists() and check_path.parent != check_path:
            check_path = check_path.parent

        if not check_path.exists():
            return False

        # Check available space
        stat = os.statvfs(check_path)
        available_bytes = stat.f_bavail * stat.f_frsize

        return available_bytes >= min_free_bytes

    except (OSError, AttributeError):
        # AttributeError for Windows (no statvfs), OSError for other issues
        # On Windows or if check fails, assume space is available
        return True


def _create_new_inbox_file_enhanced(inbox_path: Path, item_text: str) -> None:
    """Create new inbox.md file with enhanced safety and GTD structure."""
    # Enhanced content template matching vault_setup patterns
    content = f"""---
status: active
created: {_get_iso_timestamp()}
---

# Inbox

## Quick Capture

Capture everything here first, then process and organize.

- [ ] {item_text}
"""

    # Enhanced atomic write with backup and validation
    _atomic_write_with_validation(inbox_path, content)


def _append_to_existing_inbox_enhanced(inbox_path: Path, item_text: str) -> None:
    """Append item to existing inbox.md file with enhanced safety measures."""
    # Create backup before modification
    backup_path = inbox_path.with_suffix(".bak")

    try:
        # Read and validate current content
        current_content = inbox_path.read_text(encoding="utf-8")

        # Create backup
        backup_path.write_text(current_content, encoding="utf-8")

        # Process content
        lines = current_content.split("\n")
        insert_index = _find_insertion_point(lines)

        # Insert new item with timestamp comment for traceability
        timestamp = _get_iso_timestamp()
        new_item = f"- [ ] {item_text}  <!-- captured: {timestamp} -->"
        lines.insert(insert_index, new_item)

        # Ensure proper line ending
        new_content = "\n".join(lines)
        if not new_content.endswith("\n"):
            new_content += "\n"

        # Validate content before writing
        if len(new_content) > 1024 * 1024:  # 1MB safety limit
            raise ValueError("Inbox content would exceed safety limit")

        # Atomic write with validation
        _atomic_write_with_validation(inbox_path, new_content)

        # Remove backup on success
        if backup_path.exists():
            backup_path.unlink()

    except Exception as e:
        # Restore from backup if it exists
        if backup_path.exists():
            try:
                backup_content = backup_path.read_text(encoding="utf-8")
                inbox_path.write_text(backup_content, encoding="utf-8")
            except Exception:
                pass  # Best effort restore
            finally:
                backup_path.unlink()
        raise e


def _atomic_write_with_validation(file_path: Path, content: str) -> None:
    """Perform atomic write with content validation and rollback capability."""
    temp_path = file_path.with_suffix(".tmp")

    try:
        # Write to temporary file
        temp_path.write_text(content, encoding="utf-8")

        # Validate written content
        written_content = temp_path.read_text(encoding="utf-8")
        if written_content != content:
            raise ValueError("Content validation failed after write")

        # Atomic move
        temp_path.replace(file_path)

    except Exception:
        # Cleanup temp file on any failure
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass  # Best effort cleanup
        raise


def _get_iso_timestamp() -> str:
    """Get current timestamp in ISO format for metadata."""
    from datetime import datetime

    return datetime.now().isoformat()


def _find_insertion_point(lines: list[str]) -> int:
    """Find the best place to insert new item in inbox file."""
    # Look for Quick Capture section
    for i, line in enumerate(lines):
        if line.strip().lower() in ["## quick capture", "# quick capture"]:
            # Insert after this header, looking for first empty line or existing task
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "" or lines[j].strip().startswith("- [ ]"):
                    return j
            # If no empty line found, insert right after header
            return i + 1

    # Look for any task section or existing tasks
    for i, line in enumerate(lines):
        if line.strip().startswith("- [ ]"):
            # Insert before first existing task to keep new items at top
            return i

    # Look for end of content (before empty lines at end)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            return i + 1

    # Fallback: insert at end
    return len(lines)


# Legacy functions for backward compatibility
def _create_new_inbox_file(inbox_path: Path, item_text: str) -> None:
    """Create new inbox.md file with proper GTD structure."""
    content = f"""---
status: active
---

# Inbox

## Quick Capture

- [ ] {item_text}
"""

    # Use atomic write operation for thread safety
    temp_path = inbox_path.with_suffix(".tmp")
    try:
        temp_path.write_text(content, encoding="utf-8")
        temp_path.replace(inbox_path)
    except Exception:
        # Cleanup temp file if atomic write fails
        if temp_path.exists():
            temp_path.unlink()
        raise


def _append_to_existing_inbox(inbox_path: Path, item_text: str) -> None:
    """Append item to existing inbox.md file safely."""
    # Read current content
    current_content = inbox_path.read_text(encoding="utf-8")

    # Find appropriate place to insert new item
    # Look for Quick Capture section or end of file
    lines = current_content.split("\n")

    # Find best insertion point
    insert_index = _find_insertion_point(lines)

    # Insert new item
    new_item = f"- [ ] {item_text}"
    lines.insert(insert_index, new_item)

    # Ensure proper line ending
    new_content = "\n".join(lines)
    if not new_content.endswith("\n"):
        new_content += "\n"

    # Use atomic write operation for thread safety
    temp_path = inbox_path.with_suffix(".tmp")
    try:
        temp_path.write_text(new_content, encoding="utf-8")
        temp_path.replace(inbox_path)
    except Exception:
        # Cleanup temp file if atomic write fails
        if temp_path.exists():
            temp_path.unlink()
        raise
