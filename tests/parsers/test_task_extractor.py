"""Tests for TaskExtractor class."""

from datetime import datetime

from md_gtd_mcp.parsers.task_extractor import TaskExtractor


class TestTaskExtractor:
    """Test TaskExtractor parsing of Obsidian Tasks format."""

    def test_simple_uncompleted_task(self) -> None:
        """Test parsing simple uncompleted task with #task tag."""
        text = "- [ ] Buy groceries #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Buy groceries"
        assert task.is_completed is False
        assert task.raw_text == "- [ ] Buy groceries #task"
        assert task.line_number == 1
        assert "#task" in task.tags

    def test_simple_completed_task(self) -> None:
        """Test parsing simple completed task with #task tag."""
        text = "- [x] Buy groceries #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Buy groceries"
        assert task.is_completed is True
        assert task.raw_text == "- [x] Buy groceries #task"
        assert task.line_number == 1
        assert "#task" in task.tags

    def test_checkbox_without_task_tag_ignored(self) -> None:
        """Test that checkboxes without #task tag are ignored."""
        text = """- [ ] Regular checkbox item
- [x] Another checkbox item
- [ ] Buy groceries #task
- [ ] Meeting notes checklist item"""

        tasks = TaskExtractor.extract_tasks(text)

        # Only the item with #task should be extracted
        assert len(tasks) == 1
        task = tasks[0]
        assert task.text == "Buy groceries"
        assert "#task" in task.tags

    def test_task_with_context(self) -> None:
        """Test parsing task with GTD context."""
        text = "- [ ] Call dentist about appointment @calls #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Call dentist about appointment"
        assert task.context == "@calls"
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Call dentist about appointment @calls #task"

    def test_task_with_project_link(self) -> None:
        """Test parsing task with project wikilink."""
        text = "- [ ] Review budget [[Home Renovation]] #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Review budget"
        assert task.project == "Home Renovation"
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Review budget [[Home Renovation]] #task"

    def test_task_with_energy_level(self) -> None:
        """Test parsing task with energy level emoji."""
        text = "- [ ] Write quarterly report 🔥 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Write quarterly report"
        assert task.energy == "🔥"
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Write quarterly report 🔥 #task"

    def test_task_with_time_estimate(self) -> None:
        """Test parsing task with time estimate."""
        text = "- [ ] Review document ⏱️30 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Review document"
        assert task.time_estimate == 30
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Review document ⏱️30 #task"

    def test_task_with_delegated_person(self) -> None:
        """Test parsing task with delegated person."""
        text = "- [ ] Get approval from manager 👤John #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Get approval from manager"
        assert task.delegated_to == "John"
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Get approval from manager 👤John #task"

    def test_task_with_due_date(self) -> None:
        """Test parsing task with due date."""
        text = "- [ ] Submit tax forms 📅2024-04-15 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Submit tax forms"
        assert task.due_date == datetime(2024, 4, 15)
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Submit tax forms 📅2024-04-15 #task"

    def test_task_with_scheduled_date(self) -> None:
        """Test parsing task with scheduled date."""
        text = "- [ ] Team meeting ⏳2024-03-20 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Team meeting"
        assert task.scheduled_date == datetime(2024, 3, 20)
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Team meeting ⏳2024-03-20 #task"

    def test_task_with_start_date(self) -> None:
        """Test parsing task with start date."""
        text = "- [ ] Begin project planning 🛫2024-02-01 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Begin project planning"
        assert task.start_date == datetime(2024, 2, 1)
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Begin project planning 🛫2024-02-01 #task"

    def test_completed_task_with_done_date(self) -> None:
        """Test parsing completed task with done date."""
        text = "- [x] Finish presentation ✅2024-01-15 #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Finish presentation"
        assert task.is_completed is True
        assert task.done_date == datetime(2024, 1, 15)
        assert "#task" in task.tags
        assert task.raw_text == "- [x] Finish presentation ✅2024-01-15 #task"

    def test_task_with_priority(self) -> None:
        """Test parsing task with priority levels."""
        high_priority = "- [ ] Critical bug fix ⏫ #task"
        medium_priority = "- [ ] Update documentation 🔼 #task"
        low_priority = "- [ ] Clean desk 🔽 #task"

        # Test high priority
        tasks = TaskExtractor.extract_tasks(high_priority)
        assert len(tasks) == 1
        assert tasks[0].priority == "⏫"
        assert "#task" in tasks[0].tags

        # Test medium priority
        tasks = TaskExtractor.extract_tasks(medium_priority)
        assert len(tasks) == 1
        assert tasks[0].priority == "🔼"
        assert "#task" in tasks[0].tags

        # Test low priority
        tasks = TaskExtractor.extract_tasks(low_priority)
        assert len(tasks) == 1
        assert tasks[0].priority == "🔽"
        assert "#task" in tasks[0].tags

    def test_task_with_recurrence(self) -> None:
        """Test parsing task with recurrence pattern."""
        text = "- [ ] Water plants 🔁every week #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Water plants"
        assert task.recurrence == "every week"
        assert "#task" in task.tags
        assert task.raw_text == "- [ ] Water plants 🔁every week #task"

    def test_task_with_multiple_tags(self) -> None:
        """Test parsing task with multiple hashtags including #task."""
        text = "- [ ] Review code #task #work #urgent"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Review code"
        assert set(task.tags) == {"#task", "#work", "#urgent"}
        assert task.raw_text == "- [ ] Review code #task #work #urgent"

    def test_complex_task_with_multiple_metadata(self) -> None:
        """Test parsing task with multiple GTD and Obsidian metadata."""
        text = (
            "- [ ] Prepare presentation [[Client Meeting]] @office 🔥 ⏱️120 "
            "📅2024-06-15 #task #work #important"
        )
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        assert task.text == "Prepare presentation"
        assert task.project == "Client Meeting"
        assert task.context == "@office"
        assert task.energy == "🔥"
        assert task.time_estimate == 120
        assert task.due_date == datetime(2024, 6, 15)
        assert set(task.tags) == {"#task", "#work", "#important"}
        assert task.raw_text == text

    def test_multiple_tasks_in_text(self) -> None:
        """Test parsing multiple tasks from text block."""
        text = """## Today's Tasks

- [ ] Morning standup @office #task
- [x] Send email to client ✅2024-01-10 #task
- [ ] Grocery shopping @errands #personal
- [ ] Non-task checkbox item

Some other text that's not a task.

- [ ] Call dentist [[Health Maintenance]] 👤receptionist #task #waiting"""

        tasks = TaskExtractor.extract_tasks(text)

        # Only 3 tasks should be found (items with #task tag)
        assert len(tasks) == 3

        # Check first task
        assert tasks[0].text == "Morning standup"
        assert tasks[0].context == "@office"
        assert tasks[0].is_completed is False
        assert tasks[0].line_number == 3
        assert "#task" in tasks[0].tags

        # Check completed task
        assert tasks[1].text == "Send email to client"
        assert tasks[1].is_completed is True
        assert tasks[1].done_date == datetime(2024, 1, 10)
        assert tasks[1].line_number == 4
        assert "#task" in tasks[1].tags

        # Check delegated task (last one with #task)
        assert tasks[2].text == "Call dentist"
        assert tasks[2].project == "Health Maintenance"
        assert tasks[2].delegated_to == "receptionist"
        assert tasks[2].line_number == 10
        assert set(tasks[2].tags) == {"#task", "#waiting"}

    def test_indented_tasks(self) -> None:
        """Test parsing indented task lists with #task tags."""
        text = """- [ ] Main project task #task
  - [ ] Subtask one @calls #task
    - [ ] Sub-subtask with details #task
  - [ ] Regular checklist item without task tag"""

        tasks = TaskExtractor.extract_tasks(text)

        # Only 3 tasks should be found (items with #task tag)
        assert len(tasks) == 3
        assert tasks[0].text == "Main project task"
        assert tasks[1].text == "Subtask one"
        assert tasks[1].context == "@calls"
        assert tasks[2].text == "Sub-subtask with details"

        # All should have #task tag
        for task in tasks:
            assert "#task" in task.tags

    def test_different_checkbox_formats_with_task_tag(self) -> None:
        """Test parsing different checkbox formats with #task tag."""
        text = """- [ ] Regular uncompleted #task
- [x] Regular completed #task
- [X] Capital X completed #task
- [/] In progress #task
- [>] Forwarded #task
- [<] Scheduled #task
- [!] Important #task
- [-] Cancelled #task
- [?] Question #task
- [ ] Regular checkbox without task tag"""

        tasks = TaskExtractor.extract_tasks(text)

        # Only 9 tasks should be found (items with #task tag)
        assert len(tasks) == 9

        # Regular tasks
        assert tasks[0].is_completed is False
        assert tasks[1].is_completed is True
        assert tasks[2].is_completed is True  # Capital X should also be completed

        # Special statuses should be treated as uncompleted for GTD purposes
        for i in range(3, 9):
            assert tasks[i].is_completed is False

        # All should have #task tag
        for task in tasks:
            assert "#task" in task.tags

    def test_empty_text(self) -> None:
        """Test parsing empty or whitespace-only text."""
        assert TaskExtractor.extract_tasks("") == []
        assert TaskExtractor.extract_tasks("   \n\n   ") == []

    def test_text_without_tasks(self) -> None:
        """Test parsing text with checkboxes but no #task tags."""
        text = """# Project Notes

This is some regular markdown content.

- [ ] Regular checklist item
- [x] Completed checklist item
- [ ] Another checklist item

1. Numbered list item
2. Another numbered item"""

        tasks = TaskExtractor.extract_tasks(text)
        assert tasks == []

    def test_invalid_date_formats(self) -> None:
        """Test handling of invalid date formats."""
        text = "- [ ] Task with invalid date 📅invalid-date #task"
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        # Invalid dates should be ignored, not cause errors
        assert task.due_date is None
        assert "📅invalid-date" in task.raw_text
        assert "#task" in task.tags

    def test_malformed_metadata(self) -> None:
        """Test handling of malformed metadata."""
        text = (
            "- [ ] Task with malformed metadata ⏱️abc [[unclosed link @incomplete #task"
        )
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 1
        task = tasks[0]

        # Malformed metadata should be handled gracefully
        assert task.time_estimate is None  # Invalid number
        assert task.project is None  # Unclosed link
        assert task.context == "@incomplete"  # Context works even if incomplete
        assert "#task" in task.tags
        assert task.raw_text == text

    def test_task_tag_case_insensitive(self) -> None:
        """Test that #task tag matching is case insensitive."""
        text_variants = [
            "- [ ] Test task #task",
            "- [ ] Test task #Task",
            "- [ ] Test task #TASK",
            "- [ ] Test task #tAsK",
        ]

        for text in text_variants:
            tasks = TaskExtractor.extract_tasks(text)
            assert len(tasks) == 1
            assert tasks[0].text == "Test task"

    def test_task_tag_position_flexible(self) -> None:
        """Test that #task tag can appear anywhere in the task line."""
        text_variants = [
            "- [ ] #task Test task with tag at beginning",
            "- [ ] Test task #task with tag in middle",
            "- [ ] Test task with tag at end #task",
        ]

        for text in text_variants:
            tasks = TaskExtractor.extract_tasks(text)
            assert len(tasks) == 1
            assert "#task" in tasks[0].tags
