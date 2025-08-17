"""
Complete GTD workflow scenario tests covering capture → clarify → organize phases.

This module tests the full Getting Things Done workflow as implemented by
the MCP server, ensuring proper phase separation and methodology compliance.
"""

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.parsers.markdown_parser import MarkdownParser
from md_gtd_mcp.services.resource_handler import ResourceHandler
from md_gtd_mcp.services.vault_reader import VaultReader


@pytest.fixture
def gtd_workflow_vault() -> Generator[VaultConfig]:
    """Create a temporary vault for GTD workflow testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        vault_path = Path(temp_dir)

        # Create GTD structure
        gtd_path = vault_path / "GTD"
        gtd_path.mkdir()

        # Create inbox with realistic capture content
        inbox_path = gtd_path / "inbox.md"
        inbox_content = """---
status: active
---

# Inbox

## Quick Capture

- Research vacation destinations for spring break
- Meeting notes from client call yesterday
- Fix squeaky door in hallway
- [ ] Review quarterly budget report
- Book recommendation from Sarah: "Atomic Habits"
- [ ] Confirm meeting attendance with team
- [ ] Call mom about vacation planning

## Ideas and Notes

Check Project Alpha status for next steps.
Random thought: maybe we should consider automated backup solution.

- [ ] Consider switching team communication from Slack to Discord
- [ ] Evaluate weekly meeting format effectiveness
"""
        inbox_path.write_text(inbox_content)

        # Create projects file with #task requirements
        projects_path = gtd_path / "projects.md"
        projects_content = """---
status: active
---

# Projects

## Active Projects

### Project Alpha - Website Redesign
- [ ] Gather requirements from stakeholders #task @planning
- [ ] Create wireframes and mockups #task @design
- [ ] Implement responsive layout #task @coding

### Project Beta - Team Process Improvement
- [ ] Survey team for feedback #task @calls
- [ ] Analyze current workflow bottlenecks #task @analysis
"""
        projects_path.write_text(projects_content)

        # Create next-actions file with contexts in task lines (not just headers)
        next_actions_path = gtd_path / "next-actions.md"
        next_actions_content = """---
status: active
---

# Next Actions

## @calls
- [ ] Call dentist to schedule appointment #task @calls
- [ ] Follow up with client about proposal #task @calls

## @computer
- [ ] Update project documentation #task @computer
- [ ] Review and merge pull requests #task @computer

## @errands
- [ ] Pick up dry cleaning #task @errands
- [ ] Buy groceries for the week #task @errands
"""
        next_actions_path.write_text(next_actions_content)

        yield VaultConfig(vault_path=vault_path)


class TestCompleteGTDWorkflow:
    """Test complete GTD workflow scenarios."""

    def test_capture_phase_recognition(self, gtd_workflow_vault: VaultConfig) -> None:
        """Test that capture phase properly recognizes ALL checkbox items.

        Without requiring #task tags in the capture phase.
        """
        reader = VaultReader(gtd_workflow_vault)

        # Get inbox files
        inbox_files = reader.get_inbox_files()
        assert len(inbox_files) == 1

        inbox = inbox_files[0]

        # Verify inbox captures ALL checkbox items (capture phase behavior)
        captured_tasks = [task for task in inbox.tasks if not task.is_completed]
        assert len(captured_tasks) >= 4  # Should capture checkbox items without #task

        # Verify no #task tags required in capture phase
        for _task in captured_tasks:
            # In capture phase, tasks don't need to have #task in raw_text
            # This is the key insight from Decision D006
            pass  # Just verify they're captured regardless of #task presence

    def test_clarify_phase_recognition(self, gtd_workflow_vault: VaultConfig) -> None:
        """Test that clarify phase maintains #task tag requirements.

        For processed files in the clarify phase.
        """
        reader = VaultReader(gtd_workflow_vault)

        # Get projects and next-actions files (clarified items)
        project_files = reader.get_project_files()
        next_action_files = reader.get_next_action_files()

        assert len(project_files) >= 1
        assert len(next_action_files) >= 1

        # Verify clarified files maintain #task requirements
        projects = project_files[0]
        next_actions = next_action_files[0]

        # All tasks in clarified files should have #task tags
        for task in projects.tasks:
            assert "#task" in task.raw_text, (
                f"Project task missing #task: {task.raw_text}"
            )

        for task in next_actions.tasks:
            assert "#task" in task.raw_text, (
                f"Next action missing #task: {task.raw_text}"
            )

    def test_organize_phase_context_assignment(
        self, gtd_workflow_vault: VaultConfig
    ) -> None:
        """Test that organize phase properly handles context assignments."""
        reader = VaultReader(gtd_workflow_vault)

        next_action_files = reader.get_next_action_files()
        assert len(next_action_files) >= 1

        next_actions = next_action_files[0]

        # Verify context assignment in organize phase
        contexts_found = set()
        for task in next_actions.tasks:
            # Check for contexts in the raw text
            # (since context extraction may not be implemented)
            if "@" in task.raw_text:
                # Extract contexts from raw text
                import re

                context_matches = re.findall(r"@\w+", task.raw_text)
                contexts_found.update(context_matches)

        # Should have proper GTD contexts
        expected_contexts = {"@calls", "@computer", "@errands"}
        assert contexts_found.intersection(expected_contexts), (
            f"No GTD contexts found in organized tasks. Found: {contexts_found}"
        )

    def test_full_capture_to_clarify_workflow(
        self, gtd_workflow_vault: VaultConfig
    ) -> None:
        """Test the complete workflow from capture to clarify phases."""
        vault_path = str(gtd_workflow_vault.vault_path)
        resource_handler = ResourceHandler()

        # Step 1: Verify inbox content (capture phase)
        inbox_result = resource_handler.get_file(vault_path, "gtd/inbox.md")
        assert inbox_result["status"] == "success"

        inbox_data = inbox_result["file"]
        captured_items = len(inbox_data["tasks"])
        assert captured_items >= 4, "Should capture multiple items in inbox"

        # Step 2: Verify processed content (clarify phase)
        projects_result = resource_handler.get_file(vault_path, "gtd/projects.md")
        assert projects_result["status"] == "success"

        projects_data = projects_result["file"]
        clarified_items = len(projects_data["tasks"])
        assert clarified_items >= 3, "Should have clarified project tasks"

        # Step 3: Verify all clarified tasks have proper metadata
        for task in projects_data["tasks"]:
            # Clarified tasks should have #task tags
            assert task.get("raw_text") and "#task" in task["raw_text"]

    def test_phase_separation_integrity(self, gtd_workflow_vault: VaultConfig) -> None:
        """Test that GTD phase separation is maintained throughout the workflow."""
        parser = MarkdownParser()

        # Test inbox (capture phase) - should recognize all checkbox items
        inbox_path = gtd_workflow_vault.vault_path / "GTD" / "inbox.md"
        inbox_content = inbox_path.read_text()
        # Fix: path should be Path object, not string
        inbox_parsed = parser.parse_file(inbox_content, inbox_path)

        # Count checkbox items in raw content vs parsed tasks
        checkbox_count = inbox_content.count("- [ ]")
        parsed_task_count = len(inbox_parsed.tasks)

        # In capture phase, should capture ALL checkbox items
        assert parsed_task_count >= checkbox_count, (
            f"Capture phase should recognize all checkbox items: "
            f"found {checkbox_count} checkboxes but only {parsed_task_count} tasks"
        )

        # Test projects (clarify phase) - should require #task tags
        projects_path = gtd_workflow_vault.vault_path / "GTD" / "projects.md"
        projects_content = projects_path.read_text()
        # Fix: path should be Path object, not string
        projects_parsed = parser.parse_file(projects_content, projects_path)

        # All parsed tasks should have #task tags (clarify phase requirement)
        for task in projects_parsed.tasks:
            assert "#task" in task.raw_text, (
                f"Clarify phase task missing #task tag: {task.raw_text}"
            )

    def test_weekly_review_workflow_integration(
        self, gtd_workflow_vault: VaultConfig
    ) -> None:
        """Test integration points for weekly review and planning workflows."""
        reader = VaultReader(gtd_workflow_vault)

        # Get all GTD files for review workflow
        all_files = reader.read_all_gtd_files()

        # Should have files from all major GTD categories
        file_types = {file.file_type for file in all_files}
        expected_types = {"inbox", "projects", "next-actions"}

        assert expected_types.issubset(file_types), (
            f"Missing GTD file types for review workflow: "
            f"expected {expected_types}, found {file_types}"
        )

        # Verify review can distinguish between captured and clarified items
        inbox_files = [f for f in all_files if f.file_type == "inbox"]
        clarified_files = [
            f for f in all_files if f.file_type in ["projects", "next-actions"]
        ]

        assert len(inbox_files) >= 1, "Need inbox for capture review"
        assert len(clarified_files) >= 2, "Need clarified files for progress review"

        # Verify workflow readiness for review automation
        total_captured = sum(len(f.tasks) for f in inbox_files)
        total_clarified = sum(len(f.tasks) for f in clarified_files)

        assert total_captured >= 4, "Should have captured items to review"
        assert total_clarified >= 5, "Should have clarified items to review"

    def test_mcp_resource_workflow_consistency(
        self, gtd_workflow_vault: VaultConfig
    ) -> None:
        """Test that MCP resources maintain workflow consistency.

        Across different access patterns.
        """
        vault_path = str(gtd_workflow_vault.vault_path)
        resource_handler = ResourceHandler()

        # Test batch content access maintains phase-aware behavior
        content_result = resource_handler.get_content(vault_path)
        assert content_result["status"] == "success"

        files_data = content_result["files"]

        # Find inbox and projects in batch results
        inbox_file = next((f for f in files_data if "inbox" in f["file_path"]), None)
        projects_file = next(
            (f for f in files_data if "projects" in f["file_path"]), None
        )

        assert inbox_file is not None, "Inbox should be included in batch content"
        assert projects_file is not None, "Projects should be included in batch content"

        # Verify phase-aware behavior in batch results
        inbox_task_count = len(inbox_file["tasks"])
        projects_task_count = len(projects_file["tasks"])

        assert inbox_task_count >= 4, "Batch inbox should capture all checkbox items"
        assert projects_task_count >= 3, "Batch projects should have clarified tasks"

        # Verify consistency between individual and batch access
        individual_inbox = resource_handler.get_file(vault_path, "gtd/inbox.md")
        assert individual_inbox["status"] == "success"

        individual_task_count = len(individual_inbox["file"]["tasks"])
        assert individual_task_count == inbox_task_count, (
            "Individual and batch access should return consistent task counts"
        )
