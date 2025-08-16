"""GTD vault setup service for creating folder structure and template files."""

from pathlib import Path
from typing import Any

# GTD file content templates
GTD_TEMPLATES = {
    "inbox.md": """---
status: active
---

# Inbox

## Quick Capture

Capture everything here first, then process and organize.

""",
    "projects.md": """---
status: active
---

# Projects

## Active Projects

Projects with defined outcomes that require multiple steps.

""",
    "next-actions.md": """---
status: active
---

# Next Actions

## By Context

Context-organized actionable tasks that can be done immediately.

""",
    "waiting-for.md": """---
status: active
---

# Waiting For

## Delegated Items

Items waiting for someone else's response or action.

""",
    "someday-maybe.md": """---
status: someday
---

# Someday / Maybe

## Future Possibilities

Items that might be done someday but are not committed to now.

""",
}

# Context files configuration
CONTEXT_FILES = {
    "@calls.md": {"title": "📞 Calls Context", "context": "calls"},
    "@computer.md": {"title": "💻 Computer Context", "context": "computer"},
    "@errands.md": {"title": "🚗 Errands Context", "context": "errands"},
    "@home.md": {"title": "🏠 Home Context", "context": "home"},
}


def _create_context_file_content(title: str, context: str) -> str:
    """Create content for a context file with Obsidian Tasks query syntax."""
    return f"""---
context: {context}
---

# {title}

```tasks
not done
description includes @{context}
sort by due
```
"""


def setup_gtd_vault(vault_path: str) -> dict[str, Any]:
    """Create GTD folder structure if missing.

    CRITICAL SAFETY: Only creates files/folders that don't exist - NEVER overwrites
    existing files.

    Args:
        vault_path: Path to the Obsidian vault directory

    Returns:
        Dictionary with status, created items, and already existed items
    """
    if not vault_path or not vault_path.strip():
        raise ValueError("Invalid vault path: cannot be empty")

    try:
        vault = Path(vault_path)
        created: list[str] = []
        already_existed: list[str] = []

        # Create vault directory if it doesn't exist
        if not vault.exists():
            vault.mkdir(parents=True)
            created.append(str(vault))

        # Create GTD folder
        gtd_path = vault / "gtd"
        if not gtd_path.exists():
            gtd_path.mkdir()
            created.append("gtd/")
        else:
            already_existed.append("gtd/")

        # Create contexts folder
        contexts_path = gtd_path / "contexts"
        if not contexts_path.exists():
            contexts_path.mkdir()
            created.append("gtd/contexts/")
        else:
            already_existed.append("gtd/contexts/")

        # Create standard GTD files
        for filename, content in GTD_TEMPLATES.items():
            file_path = gtd_path / filename
            if not file_path.exists():
                file_path.write_text(content)
                created.append(f"gtd/{filename}")
            else:
                already_existed.append(f"gtd/{filename}")

        # Create context files
        for filename, config in CONTEXT_FILES.items():
            file_path = contexts_path / filename
            if not file_path.exists():
                content = _create_context_file_content(
                    config["title"], config["context"]
                )
                file_path.write_text(content)
                created.append(f"gtd/contexts/{filename}")
            else:
                already_existed.append(f"gtd/contexts/{filename}")

        return {
            "status": "success",
            "vault_path": str(vault),
            "created": created,
            "already_existed": already_existed,
        }

    except PermissionError as e:
        return {
            "status": "error",
            "error": f"Permission denied: {str(e)}",
            "vault_path": vault_path,
            "created": [],
            "already_existed": [],
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Failed to setup GTD vault: {str(e)}",
            "vault_path": vault_path,
            "created": [],
            "already_existed": [],
        }
