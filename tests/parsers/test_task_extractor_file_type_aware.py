"""Tests for TaskExtractor file-type aware task recognition."""

from md_gtd_mcp.parsers.task_extractor import TaskExtractor


class TestTaskExtractorFileTypeAware:
    """Test TaskExtractor file-type aware recognition behavior."""

    def test_inbox_file_recognizes_all_checkboxes(self) -> None:
        """Test that inbox files recognize ALL checkbox items without #task tag."""
        text = """# Inbox

## Quick Capture

- [ ] Call dentist about appointment
- [x] Completed item without tag
- [ ] Review quarterly budget @computer
- Book recommendation from Sarah
- [ ] Meeting notes from yesterday

## Ideas

- [ ] Research vacation destinations
- [ ] Fix squeaky door in hallway"""

        # When file_type="inbox", should recognize all checkbox items
        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 6  # All checkbox items should be recognized

        # Verify specific tasks are found
        task_texts = [task.text for task in tasks]
        assert "Call dentist about appointment" in task_texts
        assert "Completed item without tag" in task_texts
        assert "Review quarterly budget" in task_texts
        assert "Meeting notes from yesterday" in task_texts
        assert "Research vacation destinations" in task_texts
        assert "Fix squeaky door in hallway" in task_texts

        # Verify completion status is preserved
        completed_tasks = [task for task in tasks if task.is_completed]
        assert len(completed_tasks) == 1
        assert completed_tasks[0].text == "Completed item without tag"

        # Verify contexts are still parsed when present
        context_tasks = [task for task in tasks if task.context]
        assert len(context_tasks) == 1
        assert context_tasks[0].context == "@computer"

    def test_non_inbox_files_require_task_tag(self) -> None:
        """Test that non-inbox files maintain existing #task tag requirement."""
        text = """# Projects

- [ ] Regular checkbox without tag
- [x] Completed checkbox without tag
- [ ] Task with tag @office #task
- [ ] Another task #task #work
- Regular list item"""

        # When file_type is not "inbox", should only recognize items with #task
        tasks = TaskExtractor.extract_tasks(text, file_type="projects")

        assert len(tasks) == 2  # Only items with #task should be recognized

        task_texts = [task.text for task in tasks]
        assert "Task with tag" in task_texts
        assert "Another task" in task_texts

        # Items without #task should be ignored
        assert "Regular checkbox without tag" not in task_texts
        assert "Completed checkbox without tag" not in task_texts

    def test_backward_compatibility_no_file_type(self) -> None:
        """Test backward compatibility when no file_type parameter provided."""
        text = """- [ ] Task without tag
- [ ] Task with tag #task
- [x] Completed task #task"""

        # When no file_type specified, should maintain current behavior (require #task)
        tasks = TaskExtractor.extract_tasks(text)

        assert len(tasks) == 2  # Only items with #task should be recognized

        task_texts = [task.text for task in tasks]
        assert "Task with tag" in task_texts
        assert "Completed task" in task_texts
        assert "Task without tag" not in task_texts

    def test_multiple_file_types_behavior(self) -> None:
        """Test different file types maintain appropriate behavior."""
        text = """- [ ] Checkbox item without tag
- [ ] Task with tag #task @context"""

        # Test various GTD file types
        gtd_file_types = [
            "projects",
            "next-actions",
            "waiting-for",
            "someday-maybe",
            "context",
        ]

        for file_type in gtd_file_types:
            tasks = TaskExtractor.extract_tasks(text, file_type=file_type)
            assert len(tasks) == 1  # Only tagged item should be found
            assert tasks[0].text == "Task with tag"
            assert tasks[0].context == "@context"
            assert "#task" in tasks[0].tags

    def test_inbox_with_mixed_content(self) -> None:
        """Test inbox files with mix of processed and unprocessed items."""
        text = """# Inbox

## Quick Capture (Unprocessed)
- [ ] Call dentist
- [ ] Research vacation spots
- Meeting notes from yesterday

## Partially Processed
- [ ] Review budget @computer #task
- [ ] Confirm meeting #waiting
- [ ] Buy groceries @errands #task

## Non-task Content
Some random notes and thoughts.
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 5  # All checkbox items should be recognized

        task_texts = [task.text for task in tasks]
        assert "Call dentist" in task_texts
        assert "Research vacation spots" in task_texts
        assert "Review budget" in task_texts
        assert "Confirm meeting" in task_texts
        assert "Buy groceries" in task_texts

        # Verify metadata parsing still works for tagged items
        budget_task = next(task for task in tasks if task.text == "Review budget")
        assert budget_task.context == "@computer"
        assert "#task" in budget_task.tags

        groceries_task = next(task for task in tasks if task.text == "Buy groceries")
        assert groceries_task.context == "@errands"
        assert "#task" in groceries_task.tags

    def test_edge_cases_empty_and_malformed_content(self) -> None:
        """Test edge cases with empty files and malformed content."""
        # Empty content
        assert TaskExtractor.extract_tasks("", file_type="inbox") == []
        assert TaskExtractor.extract_tasks("   \n\n   ", file_type="inbox") == []

        # Content without any checkboxes
        text_no_checkboxes = """# Inbox

Some random thoughts and notes.
No checkboxes here."""
        assert TaskExtractor.extract_tasks(text_no_checkboxes, file_type="inbox") == []

        # Malformed checkboxes
        text_malformed = """# Inbox

- [ Malformed checkbox without closing bracket
- [] Empty checkbox
- [ ] Valid checkbox item"""

        tasks = TaskExtractor.extract_tasks(text_malformed, file_type="inbox")
        assert len(tasks) == 1  # Only the valid checkbox should be found
        assert tasks[0].text == "Valid checkbox item"

    def test_inbox_preserves_all_metadata_when_present(self) -> None:
        """Test that inbox files still parse metadata when present."""
        text = """# Inbox

- [ ] Complex task [[Project]] @office 🔥 ⏱️60 📅2024-12-25 #task #urgent
- [ ] Simple task without metadata
- [ ] Task with context only @calls"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 3

        # Complex task should have all metadata parsed
        complex_task = next(task for task in tasks if "Complex task" in task.text)
        assert complex_task.text == "Complex task"
        assert complex_task.project == "Project"
        assert complex_task.context == "@office"
        assert complex_task.energy == "🔥"
        assert complex_task.time_estimate == 60
        assert complex_task.due_date is not None
        assert "#task" in complex_task.tags
        assert "#urgent" in complex_task.tags

        # Simple task should work without metadata
        simple_task = next(task for task in tasks if "Simple task" in task.text)
        assert simple_task.text == "Simple task without metadata"
        assert simple_task.context is None
        assert simple_task.project is None

        # Task with only context
        context_task = next(task for task in tasks if "Task with context" in task.text)
        assert context_task.text == "Task with context only"
        assert context_task.context == "@calls"

    def test_different_checkbox_states_inbox(self) -> None:
        """Test that inbox recognizes different checkbox states."""
        text = """# Inbox

- [ ] Uncompleted task
- [x] Completed task
- [X] Capital X completed
- [/] In progress task
- [>] Forwarded task
- [-] Cancelled task"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 6

        # Check completion states
        uncompleted = [task for task in tasks if not task.is_completed]
        completed = [task for task in tasks if task.is_completed]

        # Only [x] and [X] should be considered completed
        assert len(completed) == 2
        assert len(uncompleted) == 4

        completed_texts = [task.text for task in completed]
        assert "Completed task" in completed_texts
        assert "Capital X completed" in completed_texts

    def test_unknown_file_type_defaults_to_tag_requirement(self) -> None:
        """Test that unknown file types default to requiring #task tags."""
        text = """- [ ] Task without tag
- [ ] Task with tag #task"""

        # Unknown file type should default to current behavior
        tasks = TaskExtractor.extract_tasks(text, file_type="unknown-type")

        assert len(tasks) == 1
        assert tasks[0].text == "Task with tag"
        assert "#task" in tasks[0].tags

    def test_file_type_parameter_none_maintains_backward_compatibility(self) -> None:
        """Test that file_type=None maintains backward compatibility."""
        text = """- [ ] Task without tag
- [ ] Task with tag #task"""

        # Explicitly passing None should maintain current behavior
        tasks = TaskExtractor.extract_tasks(text, file_type=None)

        assert len(tasks) == 1
        assert tasks[0].text == "Task with tag"
        assert "#task" in tasks[0].tags
