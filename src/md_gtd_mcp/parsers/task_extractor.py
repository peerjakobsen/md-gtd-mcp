"""TaskExtractor for parsing Obsidian Tasks format with GTD metadata."""

import re
from datetime import datetime
from typing import Any

from ..models import GTDTask


class TaskExtractor:
    """Extract GTD tasks from Obsidian Tasks format markdown text."""

    # Regex patterns for parsing task components
    TASK_LINE_PATTERN = re.compile(r"^(\s*)- \[(.)\] (.+)$", re.MULTILINE)

    # GTD metadata patterns
    CONTEXT_PATTERN = re.compile(r"@(\w+)")
    PROJECT_PATTERN = re.compile(r"\[\[([^\]]+)\]\]")
    ENERGY_PATTERN = re.compile(r"(🔥|💪|🚶)")
    TIME_ESTIMATE_PATTERN = re.compile(r"⏱️(\d+)")
    DELEGATED_PATTERN = re.compile(r"👤(\w+)")

    # Obsidian Tasks plugin metadata patterns
    TAG_PATTERN = re.compile(r"#([\w-]+)")
    DUE_DATE_PATTERN = re.compile(r"📅(\d{4}-\d{2}-\d{2})")
    SCHEDULED_DATE_PATTERN = re.compile(r"⏳(\d{4}-\d{2}-\d{2})")
    START_DATE_PATTERN = re.compile(r"🛫(\d{4}-\d{2}-\d{2})")
    DONE_DATE_PATTERN = re.compile(r"✅(\d{4}-\d{2}-\d{2})")
    PRIORITY_PATTERN = re.compile(r"(⏫|🔼|🔽)")
    RECURRENCE_PATTERN = re.compile(r"🔁([^#\s]+(?:\s+[^#\s]+)*?)(?=\s+#|\s*$)")

    @classmethod
    def extract_tasks(cls, text: str, file_type: str | None = None) -> list[GTDTask]:
        """Extract all GTD tasks from markdown text.

        Args:
            text: Markdown text content
            file_type: Optional file type to determine task recognition behavior.
                      When file_type="inbox", all checkbox items are recognized.
                      For other file types, #task tag is required.

        Returns:
            List of GTDTask objects
        """
        if not text or not text.strip():
            return []

        tasks = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            if task := cls._parse_task_line(line, line_num, file_type):
                tasks.append(task)

        return tasks

    @classmethod
    def _parse_task_line(
        cls, line: str, line_number: int, file_type: str | None = None
    ) -> GTDTask | None:
        """Parse a single line for task content.

        Args:
            line: Single line of text
            line_number: Line number in source text
            file_type: Optional file type to determine task recognition behavior

        Returns:
            GTDTask object if line contains a valid task, None otherwise
        """
        match = cls.TASK_LINE_PATTERN.match(line)
        if not match:
            return None

        _, checkbox_state, content = match.groups()

        # Check if this line contains #task tag based on file type
        if not cls._has_task_tag(content, file_type):
            return None

        # Parse completion status
        is_completed = checkbox_state.lower() in ("x", "X")

        # Extract all metadata and clean text
        task_data = cls._extract_metadata(content)
        task_data.update(
            {
                "is_completed": is_completed,
                "raw_text": line,
                "line_number": line_number,
            }
        )

        return GTDTask(**task_data)

    @classmethod
    def _has_task_tag(cls, content: str, file_type: str | None = None) -> bool:
        """Check if content contains #task tag based on file type.

        Args:
            content: Task content to check
            file_type: Optional file type to determine task recognition behavior.
                      When file_type="inbox", always returns True.
                      For other file types, checks for #task tag.

        Returns:
            True if task should be recognized based on file type and content
        """
        # For inbox files, recognize all checkbox items without #task requirement
        if file_type == "inbox":
            return True

        # For all other file types, require #task tag (case insensitive)
        tags = cls.TAG_PATTERN.findall(content)
        return any(tag.lower() == "task" for tag in tags)

    @classmethod
    def _extract_metadata(cls, content: str) -> dict[str, Any]:
        """Extract all metadata from task content.

        Args:
            content: Raw task content with metadata

        Returns:
            Dictionary with extracted metadata and cleaned text
        """
        # Extract GTD metadata
        context_match = cls.CONTEXT_PATTERN.search(content)
        context = f"@{context_match.group(1)}" if context_match else None

        project_match = cls.PROJECT_PATTERN.search(content)
        project = project_match.group(1) if project_match else None

        energy_match = cls.ENERGY_PATTERN.search(content)
        energy = energy_match.group(1) if energy_match else None

        time_match = cls.TIME_ESTIMATE_PATTERN.search(content)
        time_estimate = int(time_match.group(1)) if time_match else None

        delegated_match = cls.DELEGATED_PATTERN.search(content)
        delegated_to = delegated_match.group(1) if delegated_match else None

        # Extract Obsidian Tasks metadata
        tags = [f"#{tag}" for tag in cls.TAG_PATTERN.findall(content)]

        due_date = cls._parse_date(cls.DUE_DATE_PATTERN.search(content))
        scheduled_date = cls._parse_date(cls.SCHEDULED_DATE_PATTERN.search(content))
        start_date = cls._parse_date(cls.START_DATE_PATTERN.search(content))
        done_date = cls._parse_date(cls.DONE_DATE_PATTERN.search(content))

        priority_match = cls.PRIORITY_PATTERN.search(content)
        priority = priority_match.group(1) if priority_match else None

        recurrence_match = cls.RECURRENCE_PATTERN.search(content)
        recurrence = recurrence_match.group(1).strip() if recurrence_match else None

        # Clean the task text by removing all metadata
        clean_text = cls._clean_task_text(content)

        return {
            "text": clean_text,
            "context": context,
            "project": project,
            "energy": energy,
            "time_estimate": time_estimate,
            "delegated_to": delegated_to,
            "tags": tags,
            "due_date": due_date,
            "scheduled_date": scheduled_date,
            "start_date": start_date,
            "done_date": done_date,
            "priority": priority,
            "recurrence": recurrence,
        }

    @classmethod
    def _parse_date(cls, match: Any) -> datetime | None:
        """Parse date from regex match.

        Args:
            match: Regex match object

        Returns:
            Datetime object if valid date, None otherwise
        """
        if not match:
            return None

        try:
            date_str = match.group(1)
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

    @classmethod
    def _clean_task_text(cls, content: str) -> str:
        """Remove all metadata from task content to get clean text.

        Args:
            content: Raw task content with metadata

        Returns:
            Clean task text without metadata
        """
        # Remove all metadata patterns
        text = content

        # Remove contexts
        text = cls.CONTEXT_PATTERN.sub("", text)

        # Remove project links
        text = cls.PROJECT_PATTERN.sub("", text)

        # Remove energy emojis
        text = cls.ENERGY_PATTERN.sub("", text)

        # Remove time estimates
        text = cls.TIME_ESTIMATE_PATTERN.sub("", text)

        # Remove delegated persons
        text = cls.DELEGATED_PATTERN.sub("", text)

        # Remove tags
        text = cls.TAG_PATTERN.sub("", text)

        # Remove date metadata
        text = cls.DUE_DATE_PATTERN.sub("", text)
        text = cls.SCHEDULED_DATE_PATTERN.sub("", text)
        text = cls.START_DATE_PATTERN.sub("", text)
        text = cls.DONE_DATE_PATTERN.sub("", text)

        # Remove priority
        text = cls.PRIORITY_PATTERN.sub("", text)

        # Remove recurrence
        text = cls.RECURRENCE_PATTERN.sub("", text)

        # Clean up extra whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text
