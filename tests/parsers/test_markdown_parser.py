"""Tests for MarkdownParser class."""

from datetime import datetime
from pathlib import Path

from md_gtd_mcp.parsers.markdown_parser import MarkdownParser


class TestMarkdownParser:
    """Test MarkdownParser parsing of complete markdown files."""

    def test_parse_file_with_frontmatter_only(self) -> None:
        """Test parsing file with only frontmatter, no content."""
        content = """---
outcome: Complete home renovation project
status: active
area: Personal
review_date: 2025-03-15
created_date: 2025-01-01
tags:
  - important
  - quarterly
---
"""
        path = Path("gtd/projects/home-renovation.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.frontmatter.outcome == "Complete home renovation project"
        assert gtd_file.frontmatter.status == "active"
        assert gtd_file.frontmatter.area == "Personal"
        assert gtd_file.frontmatter.review_date == datetime(2025, 3, 15)
        assert gtd_file.frontmatter.created_date == datetime(2025, 1, 1)
        assert gtd_file.frontmatter.tags == ["important", "quarterly"]
        assert len(gtd_file.tasks) == 0
        assert len(gtd_file.links) == 0

    def test_parse_file_with_frontmatter_and_content(self) -> None:
        """Test parsing file with frontmatter and markdown content."""
        content = """---
outcome: Complete quarterly review
status: active
area: Work
---

# Q1 Planning Project

This project focuses on quarterly planning and review processes.

## Context

Review budget with [[Finance Team]] @office
Call vendors @calls
"""
        path = Path("gtd/projects/q1-planning.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.title == "Q1 Planning Project"
        assert gtd_file.frontmatter.outcome == "Complete quarterly review"
        assert gtd_file.frontmatter.status == "active"
        assert gtd_file.frontmatter.area == "Work"
        assert len(gtd_file.links) == 3  # @office, Finance Team, @calls

        # Check extracted links
        finance_link = next(
            link for link in gtd_file.links if link.text == "Finance Team"
        )
        assert finance_link.target == "Finance Team"
        assert finance_link.is_external is False

        calls_link = next(link for link in gtd_file.links if link.text == "calls")
        assert calls_link.target == "@calls"
        assert calls_link.is_external is False

    def test_parse_frontmatter_with_extra_fields(self) -> None:
        """Test parsing frontmatter with custom extra fields."""
        content = """---
outcome: Launch new feature
status: active
priority: high
estimated_hours: 40
stakeholders:
  - Product Manager
  - Engineering Team
custom_field: custom_value
---

# Feature Launch
"""
        path = Path("gtd/projects/feature-launch.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.frontmatter.outcome == "Launch new feature"
        assert gtd_file.frontmatter.status == "active"
        # Extra fields should be preserved
        assert gtd_file.frontmatter.extra["priority"] == "high"
        assert gtd_file.frontmatter.extra["estimated_hours"] == 40
        assert gtd_file.frontmatter.extra["stakeholders"] == [
            "Product Manager",
            "Engineering Team",
        ]
        assert gtd_file.frontmatter.extra["custom_field"] == "custom_value"

    def test_parse_file_without_frontmatter(self) -> None:
        """Test parsing file with no frontmatter."""
        content = """# Inbox

## Quick Capture

- [ ] Call dentist @calls
- [ ] Buy groceries @errands
- [x] Send email ✅2024-01-10

## Notes

Check [[Project Alpha]] status
Visit [example site](https://example.com)
"""
        path = Path("gtd/inbox.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.title == "Inbox"
        assert gtd_file.frontmatter.outcome is None
        assert gtd_file.frontmatter.status is None
        assert gtd_file.frontmatter.tags == []
        assert gtd_file.frontmatter.extra == {}

        # Should still extract links and tasks
        assert (
            len(gtd_file.links) == 4
        )  # @calls, @errands, [[Project Alpha]], example.com
        assert len(gtd_file.tasks) == 0  # No tasks with #task tag in this content

    def test_parse_frontmatter_with_dates(self) -> None:
        """Test parsing frontmatter with various date formats."""
        content = """---
outcome: Complete project
status: completed
created_date: 2025-01-01
review_date: 2025-03-15T10:30:00
completed_date: 2025-01-31 15:45:30
---

# Completed Project
"""
        path = Path("gtd/projects/completed-project.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.frontmatter.created_date == datetime(2025, 1, 1)
        assert gtd_file.frontmatter.review_date == datetime(2025, 3, 15, 10, 30)
        assert gtd_file.frontmatter.completed_date == datetime(2025, 1, 31, 15, 45, 30)

    def test_parse_frontmatter_with_empty_values(self) -> None:
        """Test parsing frontmatter with null/empty values."""
        content = """---
outcome: null
status:
area: Personal
review_date:
tags: []
---

# Project with Empty Values
"""
        path = Path("gtd/projects/empty-values.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.frontmatter.outcome is None
        assert gtd_file.frontmatter.status is None
        assert gtd_file.frontmatter.area == "Personal"
        assert gtd_file.frontmatter.review_date is None
        assert gtd_file.frontmatter.tags == []

    def test_parse_complete_gtd_file(self) -> None:
        """Test parsing complete GTD file with all elements."""
        content = """---
outcome: Organize home office workspace
status: active
area: Personal
review_date: 2025-02-01
created_date: 2025-01-01
tags:
  - organizing
  - workspace
---

# Home Office Organization

## Overview

This project aims to create an organized and efficient home office workspace.

## Action Items

- [ ] Declutter desk surface @office 🔥 ⏱️ 30m #task
- [ ] Install shelving unit [[Home Depot|Hardware Store]] @errands #task
- [x] Order office supplies ✅2025-01-05 #task
- [ ] Set up filing system @office ⏫ #task

## Waiting For

- [ ] Delivery of new desk 👤 Furniture Store #waiting

## Reference Links

Check organizing tips at [Marie Kondo](https://konmari.com)
Review setup in [[Office Design Ideas]]

## Project Notes

This links to other projects like [[Spring Cleaning]] and [[Productivity System]].
"""
        path = Path("gtd/projects/home-office.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        # Test frontmatter
        assert gtd_file.title == "Home Office Organization"
        assert gtd_file.frontmatter.outcome == "Organize home office workspace"
        assert gtd_file.frontmatter.status == "active"
        assert gtd_file.frontmatter.area == "Personal"
        assert gtd_file.frontmatter.tags == ["organizing", "workspace"]

        # Test task extraction
        tasks = gtd_file.tasks
        assert len(tasks) == 4  # Only tasks with #task tag are extracted

        # Check specific task details
        declutter_task = next(task for task in tasks if "Declutter desk" in task.text)
        assert declutter_task.is_completed is False
        assert "@office" in declutter_task.raw_text
        assert "🔥" in declutter_task.raw_text  # High energy
        assert "⏱️ 30m" in declutter_task.raw_text  # Time estimate

        completed_task = next(
            task for task in tasks if "Order office supplies" in task.text
        )
        assert completed_task.is_completed is True

        # Note: waiting task is not extracted because it has #waiting tag, not #task tag

        # Test link extraction
        links = gtd_file.links
        assert len(links) >= 7  # Various wikilinks, context links, and web links

        # Check specific links
        context_links = [link for link in links if link.target.startswith("@")]
        assert len(context_links) >= 2  # @office, @errands

        wikilinks = [
            link for link in links if not link.target.startswith(("@", "http"))
        ]
        assert (
            len(wikilinks) >= 4
        )  # Home Depot, Office Design Ideas, Spring Cleaning, Productivity System

        external_links = [link for link in links if link.is_external]
        assert len(external_links) >= 1  # Marie Kondo website

    def test_parse_malformed_frontmatter(self) -> None:
        """Test parsing file with malformed YAML frontmatter."""
        content = """---
outcome: Test project
status: [invalid: yaml: structure
area Personal  # Missing colon
---

# Test Project

Content here.
"""
        path = Path("gtd/test-malformed.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        # Should handle malformed YAML gracefully
        assert gtd_file.title == "Test Project"
        # Frontmatter should be empty/default when parsing fails
        assert (
            gtd_file.frontmatter.outcome is None
            or gtd_file.frontmatter.outcome == "Test project"
        )

    def test_parse_file_types_detection(self) -> None:
        """Test that file type is correctly detected from path."""
        inbox_content = "# Inbox\n\n- [ ] Quick task"
        projects_content = "# Projects\n\n## Active Projects"

        inbox_file = MarkdownParser.parse_file(inbox_content, Path("gtd/inbox.md"))
        projects_file = MarkdownParser.parse_file(
            projects_content, Path("gtd/projects.md")
        )

        assert inbox_file.file_type == "inbox"
        assert projects_file.file_type == "projects"

    def test_extract_title_from_content(self) -> None:
        """Test title extraction from various markdown formats."""
        # Test H1 with #
        content1 = """# Project Alpha

Content here."""
        gtd_file1 = MarkdownParser.parse_file(content1, Path("test.md"))
        assert gtd_file1.title == "Project Alpha"

        # Test multiple headers - should use first H1
        content2 = """## Sub Header

# Main Title

## Another Sub
"""
        gtd_file2 = MarkdownParser.parse_file(content2, Path("test.md"))
        assert gtd_file2.title == "Main Title"

        # Test no headers - should derive from filename
        content3 = """Just content with no headers."""
        gtd_file3 = MarkdownParser.parse_file(content3, Path("my-project.md"))
        assert gtd_file3.title == "my-project"  # Filename without extension

    def test_preserve_raw_content(self) -> None:
        """Test that raw content is preserved exactly."""
        content = """---
status: active
---

# Test

- [ ] Task @context
"""
        path = Path("test.md")
        gtd_file = MarkdownParser.parse_file(content, path)

        assert gtd_file.raw_content == content
        assert gtd_file.content != content  # Should be content without frontmatter
