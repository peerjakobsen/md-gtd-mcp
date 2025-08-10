"""GTD data models for Obsidian vault integration."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class MarkdownLink:
    """Represents a markdown or wikilink in a GTD file."""

    text: str
    target: str
    is_external: bool
    line_number: int


@dataclass
class GTDFrontmatter:
    """YAML frontmatter for GTD files, especially projects."""

    # Project-level metadata
    outcome: str | None = None
    status: str | None = None  # active, completed, on-hold
    area: str | None = None
    review_date: datetime | None = None
    created_date: datetime | None = None
    completed_date: datetime | None = None
    tags: list[str] = field(default_factory=list)
    # Additional properties preserved as dict
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class GTDTask:
    """Obsidian Tasks format with GTD methodology properties."""

    # Core task information
    text: str  # Task description without metadata
    is_completed: bool  # [ ] vs [x]
    raw_text: str  # Original full task line with all metadata
    line_number: int

    # GTD methodology properties
    context: str | None = None  # @home, @office, @calls, @computer, @errands
    project: str | None = None  # [[Project Name]] link reference
    energy: str | None = None  # 🔥 high, 💪 medium, 🪶 low
    time_estimate: int | None = None  # ⏱️ minutes
    delegated_to: str | None = None  # 👤 person name for waiting-for items

    # Obsidian Tasks plugin metadata
    tags: list[str] = field(default_factory=list)  # #task, #waiting, #someday
    due_date: datetime | None = None  # 📅 YYYY-MM-DD
    scheduled_date: datetime | None = None  # ⏳ YYYY-MM-DD
    start_date: datetime | None = None  # 🛫 YYYY-MM-DD
    done_date: datetime | None = None  # ✅ YYYY-MM-DD
    priority: str | None = None  # ⏫ high, 🔼 medium, 🔽 low
    recurrence: str | None = None  # 🔁 every day/week/month


@dataclass
class GTDFile:
    """Represents a parsed GTD markdown file from Obsidian."""

    path: str
    title: str
    content: str
    file_type: str  # inbox, projects, next-actions, waiting-for, someday-maybe, context
    frontmatter: GTDFrontmatter
    tasks: list[GTDTask]
    links: list[MarkdownLink]
    raw_content: str


def detect_file_type(path: Path) -> str:
    """Detect GTD file type based on path.

    Args:
      path: Path to the file

    Returns:
      File type string: inbox, projects, next-actions, waiting-for,
      someday-maybe, context, or unknown
    """
    # Get the file name
    file_name = path.name

    # Check for standard GTD files
    if file_name == "inbox.md":
        return "inbox"
    elif file_name == "projects.md":
        return "projects"
    elif file_name == "next-actions.md":
        return "next-actions"
    elif file_name == "waiting-for.md":
        return "waiting-for"
    elif file_name == "someday-maybe.md":
        return "someday-maybe"

    # Check if it's in contexts folder
    if "contexts" in path.parts and file_name.startswith("@"):
        return "context"

    return "unknown"
