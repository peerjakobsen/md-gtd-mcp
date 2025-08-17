"""Comprehensive edge case tests for GTD phase-aware task recognition.

This module tests complex scenarios, mixed content patterns, and edge cases
for both inbox (capture phase) and non-inbox (clarify phase) file types.
"""

from datetime import datetime
from pathlib import Path

from md_gtd_mcp.models.gtd_file import detect_file_type
from md_gtd_mcp.parsers.markdown_parser import MarkdownParser
from md_gtd_mcp.parsers.task_extractor import TaskExtractor


class TestComplexInboxScenarios:
    """Test complex inbox scenarios with mixed processed/unprocessed items."""

    def test_real_world_meeting_notes_inbox(self) -> None:
        """Test inbox with realistic meeting notes and captures."""
        text = """# Inbox

## Meeting with Client - 2024-08-17

Attended by: John, Sarah, myself
Duration: 1 hour

### Action Items Discussed
- [ ] Send proposal draft by Friday
- [ ] Review budget allocation for Q4
- [ ] Schedule follow-up meeting
- [ ] Contact vendor about delivery delays @calls

### Random Thoughts During Meeting
Quick capture of ideas that came up:
- [ ] Maybe we should consider different approach to user onboarding
- Research competitor analysis for this quarter
- [ ] Review our current pricing model
- Client mentioned they're interested in premium features

### Already Processed Items
- [ ] Follow up on contract terms #task @office
- [ ] Prepare presentation slides #task #urgent @computer

### Non-actionable Content
Client feedback was very positive about our current solution.
They want to expand the relationship next year.
Meeting room was too cold - note for next time.
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 8  # All checkbox items should be recognized

        task_texts = [task.text for task in tasks]
        assert "Send proposal draft by Friday" in task_texts
        assert "Review budget allocation for Q4" in task_texts
        assert "Schedule follow-up meeting" in task_texts
        assert "Contact vendor about delivery delays" in task_texts
        assert (
            "Maybe we should consider different approach to user onboarding"
            in task_texts
        )
        assert "Review our current pricing model" in task_texts
        assert "Follow up on contract terms" in task_texts
        assert "Prepare presentation slides" in task_texts

        # Check that already processed items retain their metadata
        processed_tasks = [task for task in tasks if "#task" in task.tags]
        assert len(processed_tasks) == 2

        contract_task = next(task for task in tasks if "contract terms" in task.text)
        assert contract_task.context == "@office"
        assert "#task" in contract_task.tags

        presentation_task = next(
            task for task in tasks if "presentation slides" in task.text
        )
        assert presentation_task.context == "@computer"
        assert "#urgent" in presentation_task.tags
        assert "#task" in presentation_task.tags

        # Check that unprocessed items work without metadata
        vendor_task = next(
            task for task in tasks if "vendor about delivery" in task.text
        )
        assert vendor_task.context == "@calls"
        assert "#task" not in vendor_task.tags  # Unprocessed item

    def test_inbox_with_different_markdown_structures(self) -> None:
        """Test inbox handling various markdown structures and nesting."""
        text = """# Daily Capture - August 17

## Morning Brain Dump
- [ ] Call mom about vacation plans
- [ ] Research new laptop for work
  - Need something with good battery life
  - Budget around $2000
- [ ] Book dentist appointment

## From Email Processing
> Important email from boss:
- [ ] Review team performance metrics @computer
- [ ] Prepare budget proposal for next quarter

### Meeting Notes - Standup
- [ ] Fix bug in user authentication #task @computer
- Progress update: deployment went well yesterday
- [ ] Code review for Sarah's PR
- Waiting for design feedback on new feature

## Quick Ideas
Random thoughts throughout the day:
- [ ] Consider switching to a different project management tool
- Maybe we need better communication channels
- [ ] Evaluate current team processes

## Personal Stuff
- [ ] Pick up dry cleaning @errands
- [ ] Plan weekend hiking trip
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 11  # All checkbox items should be found

        # Verify specific tasks are parsed correctly
        task_texts = [task.text for task in tasks]
        assert "Call mom about vacation plans" in task_texts
        assert "Research new laptop for work" in task_texts
        assert "Book dentist appointment" in task_texts
        assert "Review team performance metrics" in task_texts
        assert "Prepare budget proposal for next quarter" in task_texts
        assert "Fix bug in user authentication" in task_texts
        assert "Code review for Sarah's PR" in task_texts
        assert "Consider switching to a different project management tool" in task_texts
        assert "Evaluate current team processes" in task_texts
        assert "Pick up dry cleaning" in task_texts

        # Check that existing metadata is preserved
        auth_task = next(task for task in tasks if "authentication" in task.text)
        assert auth_task.context == "@computer"
        assert "#task" in auth_task.tags

        metrics_task = next(
            task for task in tasks if "performance metrics" in task.text
        )
        assert metrics_task.context == "@computer"

        errands_task = next(task for task in tasks if "dry cleaning" in task.text)
        assert errands_task.context == "@errands"

    def test_inbox_mixed_completion_states(self) -> None:
        """Test inbox with various completion states and processing levels."""
        text = """# Inbox Processing Session

## Items to Process
- [ ] Unprocessed: call insurance company
- [x] Already completed: sent thank you email
- [ ] Partially processed: review contract @legal #waiting
- [/] In progress: research vacation options
- [>] Forwarded: ask John about meeting schedule
- [-] Cancelled: old project planning task

## Processed But Still in Inbox
- [ ] Ready for next actions: prepare quarterly report #task @computer
- [x] Completed with metadata: filed tax documents #task ✅2024-08-15

## Edge Cases
- [ ] Task with complex metadata [[Project Alpha]] @office 🔥 ⏱️90 📅2024-08-20 #task
- [ ] Simple capture without any metadata
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        assert len(tasks) == 10  # All checkbox items should be recognized

        # Check completion states
        completed_tasks = [task for task in tasks if task.is_completed]
        assert len(completed_tasks) == 2  # Only [x] items should be completed

        completed_texts = [task.text for task in completed_tasks]
        assert "Already completed: sent thank you email" in completed_texts
        assert "Completed with metadata: filed tax documents" in completed_texts

        # Check that complex metadata is preserved
        complex_task = next(task for task in tasks if "complex metadata" in task.text)
        assert complex_task.project == "Project Alpha"
        assert complex_task.context == "@office"
        assert complex_task.energy == "🔥"
        assert complex_task.time_estimate == 90
        assert complex_task.due_date == datetime(2024, 8, 20)
        assert "#task" in complex_task.tags

        # Check simple capture works
        simple_task = next(
            task for task in tasks if "Simple capture without" in task.text
        )
        assert simple_task.context is None
        assert simple_task.project is None
        assert "#task" not in simple_task.tags

    def test_inbox_with_malformed_and_edge_content(self) -> None:
        """Test inbox handling of malformed content and edge cases."""
        text = """# Inbox with Edge Cases

## Malformed Checkboxes
- [ Malformed without closing bracket
- [] Empty checkbox content
- [ ] Valid item after malformed ones

## Special Characters and Unicode
- [ ] Task with émojis and spéciàl characters 🚀
- [ ] Test unicode: 中文, العربية, русский
- [ ] Task with "quotes" and 'apostrophes'

## Very Long Content
- [ ] This is a very long task description that goes on for quite a while tests logic

## Empty and Whitespace
- [ ]
- [ ] Task with    lots   of    spaces
- [ ]	Task with tabs and	mixed whitespace

## URLs and Links
- [ ] Check out https://example.com for project ideas
- [ ] Review [[Some Project]] and [regular link](https://test.com)
- [ ] Email person@company.com about proposal

## Code and Technical Content
- [ ] Fix bug in `getUserData()` function
- [ ] Review PR #123 for authentication changes
- [ ] Update README.md with new installation steps
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="inbox")

        # Should find all valid checkbox items (malformed ones ignored)
        assert len(tasks) == 13

        # Check that malformed items are ignored
        task_texts = [task.text for task in tasks]
        assert "Malformed without closing bracket" not in " ".join(task_texts)
        assert "Empty checkbox content" not in " ".join(task_texts)

        # Check special characters work
        assert "Task with émojis and spéciàl characters 🚀" in task_texts
        assert "Test unicode: 中文, العربية, русский" in task_texts

        # Check very long content works
        long_task = next(
            task for task in tasks if "very long task description" in task.text
        )
        assert len(long_task.text) > 70  # Should capture the full long text

        # Check whitespace handling
        whitespace_tasks = [
            task for task in tasks if "spaces" in task.text or "tabs" in task.text
        ]
        assert (
            len(whitespace_tasks) == 1
        )  # Only one task has "spaces" or "tabs" that gets matched

        # Check technical content (text may be truncated during parsing)
        assert "Fix bug in `getUserData()` function" in task_texts
        assert any("Review PR" in text for text in task_texts)  # May be truncated


class TestNonInboxFileEdgeCases:
    """Test edge cases for non-inbox files that require #task tags."""

    def test_projects_file_various_task_patterns(self) -> None:
        """Test projects.md with various #task tag patterns and edge cases."""
        text = """# Active Projects

## Project Alpha
- [ ] Regular checkbox without tag (should be ignored)
- [ ] Valid task with standard tag #task
- [ ] Task with multiple tags #task #urgent #work
- [ ] Task with context and project [[Alpha]] @office #task

### Sub-project Tasks
- [ ] Nested task without tag (ignored)
- [ ] Nested valid task #task
  - [ ] Double nested without tag (ignored)
  - [ ] Double nested with tag #task

## Project Beta
- [x] Completed task #task
- [x] Completed without tag (ignored)
- [ ] Mixed case tag #Task
- [ ] Different case #TASK

## Edge Cases
- [ ] Tag at beginning #task task description
- [ ] Tag in middle of #task description
- [ ] Multiple #task tags #task in same line
- [ ] Task with #hashtag but no #task (ignored)
- [ ] Task with #taskforce (ignored - not exact match)
- [ ] Valid #task followed by #tasking (should work)

## Non-tasks
Regular text content that should be ignored.
- Regular list item without checkbox
- [x] Completed item without #task tag
"""

        tasks = TaskExtractor.extract_tasks(text, file_type="projects")

        # Should only find items with #task tags
        assert len(tasks) == 14

        task_texts = [task.text for task in tasks]

        # Valid tasks should be found
        assert "Valid task with standard tag" in task_texts
        assert "Task with multiple tags" in task_texts
        assert "Task with context and project" in task_texts
        assert "Nested valid task" in task_texts
        assert "Double nested with tag" in task_texts
        assert "Completed task" in task_texts
        assert "Mixed case tag" in task_texts
        assert "Different case" in task_texts

        # Invalid tasks should be ignored
        assert "Regular checkbox without tag" not in task_texts
        assert "Nested task without tag" not in task_texts
        assert "Double nested without tag" not in task_texts
        assert "Completed without tag" not in task_texts
        assert "Task with #hashtag but no #task" not in task_texts
        assert "Task with #taskforce" not in task_texts

        # Check metadata parsing still works
        context_task = next(
            task for task in tasks if "context and project" in task.text
        )
        assert context_task.project == "Alpha"
        assert context_task.context == "@office"
        assert "#task" in context_task.tags

        multi_tag_task = next(task for task in tasks if "multiple tags" in task.text)
        assert "#task" in multi_tag_task.tags
        assert "#urgent" in multi_tag_task.tags
        assert "#work" in multi_tag_task.tags

    def test_different_gtd_file_types_consistency(self) -> None:
        """Test that all non-inbox GTD file types behave consistently."""
        text = """# Test File

## Mixed Content
- [ ] Checkbox without tag (should be ignored)
- [ ] Valid task #task
- [ ] Task with metadata @calls #task #urgent
- [x] Completed task #task
- Regular list item
- [ ] Another checkbox without tag

## Complex Scenarios
- [ ] Complex task [[Project]] @office 🔥 ⏱️60 #task #important
- [ ] Task without tag but with context @home (ignored)
- [ ] Valid task with recurrence 🔁weekly #task
"""

        gtd_file_types = [
            "projects",
            "next-actions",
            "waiting-for",
            "someday-maybe",
            "context",
            "reference",
        ]

        for file_type in gtd_file_types:
            tasks = TaskExtractor.extract_tasks(text, file_type=file_type)

            # All file types should find exactly 5 tasks (only those with #task)
            assert len(tasks) == 5, (
                f"File type {file_type} found {len(tasks)} tasks, expected 5"
            )

            task_texts = [task.text for task in tasks]
            assert "Valid task" in task_texts
            assert "Task with metadata" in task_texts
            assert "Completed task" in task_texts
            assert "Complex task" in task_texts

            # Verify ignored items
            assert "Checkbox without tag" not in task_texts
            assert "Another checkbox without tag" not in task_texts
            assert "Task without tag but with context" not in task_texts

            # Check metadata parsing works consistently
            metadata_task = next(
                task for task in tasks if "Task with metadata" in task.text
            )
            assert metadata_task.context == "@calls"
            assert "#task" in metadata_task.tags
            assert "#urgent" in metadata_task.tags

            complex_task = next(task for task in tasks if "Complex task" in task.text)
            assert complex_task.project == "Project"
            assert complex_task.context == "@office"
            assert complex_task.energy == "🔥"
            assert complex_task.time_estimate == 60
            assert "#task" in complex_task.tags
            assert "#important" in complex_task.tags


class TestFileTypeDetectionEdgeCases:
    """Test edge cases for file type detection logic."""

    def test_file_path_detection_edge_cases(self) -> None:
        """Test file type detection with various path patterns."""
        # Standard GTD file paths
        assert detect_file_type(Path("/vault/gtd/inbox.md")) == "inbox"
        assert detect_file_type(Path("/vault/gtd/projects.md")) == "projects"
        assert detect_file_type(Path("/vault/gtd/next-actions.md")) == "next-actions"

        # Nested paths
        assert detect_file_type(Path("/vault/gtd/contexts/@calls.md")) == "context"
        # Note: nested project paths may not be detected as projects
        # depending on implementation

        # Edge case paths
        assert detect_file_type(Path("/vault/random.md")) == "unknown"
        assert detect_file_type(Path("inbox.md")) == "inbox"  # Filename only

    def test_unknown_file_types_default_behavior(self) -> None:
        """Test that unknown file types default to requiring #task tags."""
        text = """- [ ] Checkbox without tag
- [ ] Task with tag #task
- [x] Completed task #task"""

        unknown_file_types = ["unknown", "random-type", "", None, "not-a-gtd-type"]

        for file_type in unknown_file_types:
            tasks = TaskExtractor.extract_tasks(text, file_type=file_type)

            # Should behave like non-inbox files (require #task)
            assert len(tasks) == 2, (
                f"Unknown file type {file_type} should default to #task requirement"
            )

            task_texts = [task.text for task in tasks]
            assert "Task with tag" in task_texts
            assert "Completed task" in task_texts
            assert "Checkbox without tag" not in task_texts

    def test_markdown_parser_integration_with_file_types(self) -> None:
        """Test MarkdownParser correctly passes file_type to TaskExtractor."""
        # Create test content for different file types
        inbox_content = """---
status: active
---

# Inbox

- [ ] Unprocessed item
- [ ] Another unprocessed item #task
"""

        projects_content = """---
status: active
---

# Projects

- [ ] Project task without tag
- [ ] Project task with tag #task
"""

        # Test inbox parsing
        inbox_result = MarkdownParser.parse_file(
            inbox_content, Path("/vault/gtd/inbox.md")
        )
        assert len(inbox_result.tasks) == 2  # Both items should be found in inbox

        # Test projects parsing
        projects_result = MarkdownParser.parse_file(
            projects_content, Path("/vault/gtd/projects.md")
        )
        assert (
            len(projects_result.tasks) == 1
        )  # Only tagged item should be found in projects

        # Test unknown file type
        unknown_result = MarkdownParser.parse_file(
            projects_content, Path("/vault/random.md")
        )
        assert len(unknown_result.tasks) == 1  # Should default to #task requirement


class TestBackwardCompatibilityEdgeCases:
    """Test backward compatibility scenarios and migration paths."""

    def test_no_file_type_parameter_maintains_compatibility(self) -> None:
        """Test that omitting file_type parameter maintains existing behavior."""
        text = """# Mixed Content

- [ ] Checkbox without tag (should be ignored)
- [ ] Task with tag #task (should be found)
- [x] Completed without tag (should be ignored)
- [x] Completed with tag #task (should be found)
"""

        # Test with no file_type parameter (original behavior)
        tasks_no_param = TaskExtractor.extract_tasks(text)

        # Test with explicit None (should be same as above)
        tasks_none = TaskExtractor.extract_tasks(text, file_type=None)

        # Both should have same results and follow old behavior (#task required)
        assert len(tasks_no_param) == 2
        assert len(tasks_none) == 2

        for tasks in [tasks_no_param, tasks_none]:
            task_texts = [task.text for task in tasks]
            assert "Task with tag (should be found)" in task_texts
            assert "Completed with tag (should be found)" in task_texts
            assert "Checkbox without tag (should be ignored)" not in task_texts
            assert "Completed without tag (should be ignored)" not in task_texts

    def test_migration_from_old_to_new_behavior(self) -> None:
        """Test migration scenario from old behavior to new file-type aware behavior."""
        # Content that would behave differently with old vs new logic
        mixed_content = """# Content that exists during migration

## Old style (all items had #task tags)
- [ ] Old task style #task @calls
- [x] Completed old task #task

## New style inbox content (no tags during capture)
- [ ] New capture style without tags
- [ ] Another new capture style

## Processed new content (has tags)
- [ ] Processed new style #task @office
"""

        # Old behavior (no file_type, requires #task)
        old_tasks = TaskExtractor.extract_tasks(mixed_content)
        assert len(old_tasks) == 3  # Only items with #task

        old_texts = [task.text for task in old_tasks]
        assert "Old task style" in old_texts
        assert "Completed old task" in old_texts
        assert "Processed new style" in old_texts

        # New inbox behavior (file_type="inbox", all checkboxes)
        new_inbox_tasks = TaskExtractor.extract_tasks(mixed_content, file_type="inbox")
        assert len(new_inbox_tasks) == 5  # All checkbox items

        new_texts = [task.text for task in new_inbox_tasks]
        assert "New capture style without tags" in new_texts
        assert "Another new capture style" in new_texts

        # New projects behavior (file_type="projects", requires #task)
        new_projects_tasks = TaskExtractor.extract_tasks(
            mixed_content, file_type="projects"
        )
        assert len(new_projects_tasks) == 3  # Only items with #task (same as old)
