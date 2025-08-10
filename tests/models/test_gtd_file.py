"""Tests for GTD data models."""

from datetime import datetime
from pathlib import Path

from md_gtd_mcp.models.gtd_file import (
    GTDFile,
    GTDFrontmatter,
    GTDTask,
    MarkdownLink,
    detect_file_type,
)


class TestMarkdownLink:
    """Test MarkdownLink data model."""

    def test_markdown_link_creation(self) -> None:
        """Test creating a markdown link."""
        link = MarkdownLink(
            text="Link Text",
            target="https://example.com",
            is_external=True,
            line_number=5,
        )
        assert link.text == "Link Text"
        assert link.target == "https://example.com"
        assert link.is_external is True
        assert link.line_number == 5

    def test_internal_link(self) -> None:
        """Test internal link creation."""
        link = MarkdownLink(
            text="Project Name",
            target="[[Project Name]]",
            is_external=False,
            line_number=10,
        )
        assert link.is_external is False
        assert link.target == "[[Project Name]]"


class TestGTDFrontmatter:
    """Test GTDFrontmatter data model."""

    def test_frontmatter_creation(self) -> None:
        """Test creating frontmatter with GTD properties."""
        frontmatter = GTDFrontmatter(
            outcome="Complete project successfully",
            status="active",
            area="Personal",
            review_date=datetime(2025, 1, 15),
            created_date=datetime(2025, 1, 1),
            tags=["important", "quarterly"],
            extra={"custom": "value"},
        )
        assert frontmatter.outcome == "Complete project successfully"
        assert frontmatter.status == "active"
        assert frontmatter.area == "Personal"
        assert frontmatter.review_date == datetime(2025, 1, 15)
        assert frontmatter.tags == ["important", "quarterly"]
        assert frontmatter.extra == {"custom": "value"}

    def test_frontmatter_defaults(self) -> None:
        """Test frontmatter with default values."""
        frontmatter = GTDFrontmatter()
        assert frontmatter.outcome is None
        assert frontmatter.status is None
        assert frontmatter.tags == []
        assert frontmatter.extra == {}


class TestGTDTask:
    """Test GTDTask data model."""

    def test_task_creation_basic(self) -> None:
        """Test creating a basic task."""
        task = GTDTask(
            text="Call dentist to schedule appointment",
            is_completed=False,
            raw_text="- [ ] Call dentist to schedule appointment @calls #task",
            line_number=5,
        )
        assert task.text == "Call dentist to schedule appointment"
        assert task.is_completed is False
        assert (
            task.raw_text == "- [ ] Call dentist to schedule appointment @calls #task"
        )
        assert task.line_number == 5

    def test_task_with_gtd_properties(self) -> None:
        """Test task with GTD methodology properties."""
        task = GTDTask(
            text="Review project proposal",
            is_completed=False,
            raw_text=(
                "- [ ] Review project proposal @office [[Q1 Planning]] 🔥 ⏱️ 30m #task"
            ),
            line_number=10,
            context="@office",
            project="Q1 Planning",
            energy="high",
            time_estimate=30,
            tags=["task"],
        )
        assert task.context == "@office"
        assert task.project == "Q1 Planning"
        assert task.energy == "high"
        assert task.time_estimate == 30
        assert task.tags == ["task"]

    def test_task_with_obsidian_metadata(self) -> None:
        """Test task with Obsidian Tasks plugin metadata."""
        task = GTDTask(
            text="Complete report",
            is_completed=False,
            raw_text="- [ ] Complete report 📅 2025-01-20 ⏫ #task",
            line_number=15,
            due_date=datetime(2025, 1, 20),
            priority="high",
            tags=["task"],
        )
        assert task.due_date == datetime(2025, 1, 20)
        assert task.priority == "high"

    def test_completed_task(self) -> None:
        """Test completed task."""
        task = GTDTask(
            text="Send email",
            is_completed=True,
            raw_text="- [x] Send email ✅ 2025-01-10",
            line_number=20,
            done_date=datetime(2025, 1, 10),
        )
        assert task.is_completed is True
        assert task.done_date == datetime(2025, 1, 10)

    def test_waiting_for_task(self) -> None:
        """Test waiting-for task with delegation."""
        task = GTDTask(
            text="Budget approval",
            is_completed=False,
            raw_text="- [ ] Budget approval 👤 John #waiting",
            line_number=25,
            delegated_to="John",
            tags=["waiting"],
        )
        assert task.delegated_to == "John"
        assert "waiting" in task.tags


class TestGTDFile:
    """Test GTDFile data model."""

    def test_gtd_file_creation(self) -> None:
        """Test creating a GTD file."""
        frontmatter = GTDFrontmatter(status="active")
        task = GTDTask(
            text="Test task",
            is_completed=False,
            raw_text="- [ ] Test task",
            line_number=5,
        )
        link = MarkdownLink(
            text="Reference", target="reference.md", is_external=False, line_number=10
        )

        gtd_file = GTDFile(
            path="gtd/inbox.md",
            title="Inbox",
            content="# Inbox\n\n- [ ] Test task",
            file_type="inbox",
            frontmatter=frontmatter,
            tasks=[task],
            links=[link],
            raw_content="---\nstatus: active\n---\n# Inbox\n\n- [ ] Test task",
        )

        assert gtd_file.path == "gtd/inbox.md"
        assert gtd_file.title == "Inbox"
        assert gtd_file.file_type == "inbox"
        assert len(gtd_file.tasks) == 1
        assert len(gtd_file.links) == 1


class TestFileTypeDetection:
    """Test file type detection based on path."""

    def test_detect_inbox(self) -> None:
        """Test detecting inbox file."""
        assert detect_file_type(Path("gtd/inbox.md")) == "inbox"

    def test_detect_projects(self) -> None:
        """Test detecting projects file."""
        assert detect_file_type(Path("gtd/projects.md")) == "projects"

    def test_detect_next_actions(self) -> None:
        """Test detecting next-actions file."""
        assert detect_file_type(Path("gtd/next-actions.md")) == "next-actions"

    def test_detect_waiting_for(self) -> None:
        """Test detecting waiting-for file."""
        assert detect_file_type(Path("gtd/waiting-for.md")) == "waiting-for"

    def test_detect_someday_maybe(self) -> None:
        """Test detecting someday-maybe file."""
        assert detect_file_type(Path("gtd/someday-maybe.md")) == "someday-maybe"

    def test_detect_context_file(self) -> None:
        """Test detecting context files."""
        assert detect_file_type(Path("gtd/contexts/@calls.md")) == "context"
        assert detect_file_type(Path("gtd/contexts/@computer.md")) == "context"
        assert detect_file_type(Path("gtd/contexts/@errands.md")) == "context"

    def test_detect_unknown_file(self) -> None:
        """Test detecting unknown file type."""
        assert detect_file_type(Path("gtd/random.md")) == "unknown"
        assert detect_file_type(Path("notes/something.md")) == "unknown"
