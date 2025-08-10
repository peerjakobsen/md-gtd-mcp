"""MarkdownParser for parsing complete GTD markdown files."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import frontmatter  # type: ignore[import-not-found]

from ..models import GTDFile, GTDFrontmatter, detect_file_type
from .link_extractor import LinkExtractor
from .task_extractor import TaskExtractor


class MarkdownParser:
    """Parse complete GTD markdown files with frontmatter, content, tasks, and links."""

    @classmethod
    def parse_file(cls, content: str, path: Path) -> GTDFile:
        """Parse a complete GTD markdown file.

        Args:
            content: Raw file content with optional frontmatter
            path: File path for type detection and metadata

        Returns:
            GTDFile object with all parsed components
        """
        # Parse frontmatter and content using python-frontmatter
        try:
            post = frontmatter.loads(content)
            frontmatter_dict = post.metadata
            content_without_frontmatter = post.content
        except Exception:
            # If frontmatter parsing fails, treat entire content as body
            frontmatter_dict = {}
            content_without_frontmatter = content

        # Extract GTD frontmatter properties
        gtd_frontmatter = cls._extract_gtd_frontmatter(frontmatter_dict)

        # Extract title from content or filename
        title = cls._extract_title(content_without_frontmatter, path)

        # Extract tasks using TaskExtractor
        tasks = TaskExtractor.extract_tasks(content_without_frontmatter)

        # Extract links using LinkExtractor
        links = LinkExtractor.extract_links(content_without_frontmatter)

        # Detect file type from path
        file_type = detect_file_type(path)

        return GTDFile(
            path=str(path),
            title=title,
            content=content_without_frontmatter,
            file_type=file_type,
            frontmatter=gtd_frontmatter,
            tasks=tasks,
            links=links,
            raw_content=content,
        )

    @classmethod
    def _extract_gtd_frontmatter(
        cls, frontmatter_dict: dict[str, Any]
    ) -> GTDFrontmatter:
        """Extract GTD-specific frontmatter properties.

        Args:
            frontmatter_dict: Raw frontmatter dictionary

        Returns:
            GTDFrontmatter object with parsed properties
        """
        # Extract known GTD properties
        outcome = frontmatter_dict.get("outcome")
        status = frontmatter_dict.get("status")
        area = frontmatter_dict.get("area")
        tags = frontmatter_dict.get("tags", [])

        # Parse date fields
        review_date = cls._parse_frontmatter_date(frontmatter_dict.get("review_date"))
        created_date = cls._parse_frontmatter_date(frontmatter_dict.get("created_date"))
        completed_date = cls._parse_frontmatter_date(
            frontmatter_dict.get("completed_date")
        )

        # Handle empty string values as None
        if outcome == "":
            outcome = None
        if status == "":
            status = None
        if area == "":
            area = None

        # Collect extra fields (anything not in standard GTD properties)
        standard_fields = {
            "outcome",
            "status",
            "area",
            "review_date",
            "created_date",
            "completed_date",
            "tags",
        }
        extra = {
            key: value
            for key, value in frontmatter_dict.items()
            if key not in standard_fields
        }

        return GTDFrontmatter(
            outcome=outcome,
            status=status,
            area=area,
            review_date=review_date,
            created_date=created_date,
            completed_date=completed_date,
            tags=tags if isinstance(tags, list) else [],
            extra=extra,
        )

    @classmethod
    def _parse_frontmatter_date(cls, date_value: Any) -> datetime | None:
        """Parse date from frontmatter value.

        Args:
            date_value: Date value from frontmatter (string, datetime, or None)

        Returns:
            Parsed datetime object or None
        """
        if date_value is None or date_value == "":
            return None

        if isinstance(date_value, datetime):
            return date_value

        # Handle date objects from YAML parsing
        if (
            hasattr(date_value, "year")
            and hasattr(date_value, "month")
            and hasattr(date_value, "day")
        ):
            # This is likely a date object, convert to datetime
            return datetime.combine(date_value, datetime.min.time())

        if isinstance(date_value, str):
            # Try various date formats
            date_formats = [
                "%Y-%m-%d",  # 2025-01-15
                "%Y-%m-%dT%H:%M:%S",  # 2025-01-15T10:30:00
                "%Y-%m-%d %H:%M:%S",  # 2025-01-15 10:30:00
                "%Y-%m-%dT%H:%M",  # 2025-01-15T10:30
            ]

            for fmt in date_formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

        # If all parsing attempts fail, return None
        return None

    @classmethod
    def _extract_title(cls, content: str, path: Path) -> str:
        """Extract title from markdown content or filename.

        Args:
            content: Markdown content without frontmatter
            path: File path

        Returns:
            Extracted title string
        """
        # Look for first H1 header
        h1_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if h1_match:
            return h1_match.group(1).strip()

        # Fall back to filename without extension
        return path.stem
