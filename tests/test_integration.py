"""Integration tests for GTD MCP server components."""

import tempfile
from pathlib import Path

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.services.vault_reader import VaultReader
from md_gtd_mcp.services.vault_setup import setup_gtd_vault
from tests.fixtures import create_sample_vault


class TestGTDIntegration:
    """Integration tests for all parser components with VaultReader."""

    def test_complete_vault_reading_integration(self) -> None:
        """Test complete integration of all parsers with realistic GTD vault."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            # Read all files and verify integration
            all_files = reader.read_all_gtd_files()

            # Should have all GTD file types
            assert len(all_files) >= 8  # 5 standard + 3+ context files

            file_types = {f.file_type for f in all_files}
            expected_types = {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }
            assert expected_types.issubset(file_types)

    def test_task_extraction_across_files(self) -> None:
        """Test TaskExtractor integration across different file types."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            # Get files that should contain tasks
            task_files = reader.find_files_with_tasks()

            # Should have tasks in inbox and next-actions primarily
            task_file_types = {f.file_type for f in task_files}
            expected_task_types = {"inbox", "next-actions"}
            assert expected_task_types.issubset(task_file_types)

            # Count total actionable tasks (#task tag)
            total_tasks = sum(len(f.tasks) for f in task_files)
            assert total_tasks > 20  # Should have many consolidated tasks

    def test_context_file_query_parsing(self) -> None:
        """Test that context files with query blocks are parsed gracefully."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            # Get context files
            context_files = reader.get_context_files()
            assert len(context_files) == 4  # @calls, @computer, @errands, @home

            for context_file in context_files:
                # Context files should parse without errors
                title_check = (
                    context_file.title.startswith("@")
                    or "Context" in context_file.title
                )
                assert title_check
                assert context_file.file_type == "context"
                assert context_file.content is not None

                # Should not extract tasks from query blocks
                # (Query blocks are code blocks, not task checkboxes)
                assert len(context_file.tasks) == 0

    def test_link_extraction_across_files(self) -> None:
        """Test LinkExtractor integration for wikilinks and context links."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            all_files = reader.read_all_gtd_files()

            # Collect all links
            all_links = []
            for f in all_files:
                all_links.extend(f.links)

            assert len(all_links) > 0

            # Should have various link types
            wikilinks = [link for link in all_links if not link.is_external]
            context_links = [link for link in all_links if link.target.startswith("@")]

            assert len(wikilinks) > 0
            assert len(context_links) > 0

    def test_next_actions_as_primary_task_source(self) -> None:
        """Test that next-actions.md is the primary source of actionable tasks."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            # Get next-actions file
            next_actions_files = reader.get_gtd_files_by_type("next-actions")
            assert len(next_actions_files) == 1

            next_actions = next_actions_files[0]

            # Should have the most tasks with proper context tags
            assert len(next_actions.tasks) > 15  # Consolidated from all contexts

            # Check that tasks have proper context information
            # Context is extracted into task.context field, not task.text
            task_contexts = [
                task.context for task in next_actions.tasks if task.context
            ]
            context_tags = ["@calls", "@computer", "@errands", "@home"]

            # Should have tasks for each context
            for context_tag in context_tags:
                assert any(context == context_tag for context in task_contexts)

    def test_inbox_processing_states(self) -> None:
        """Test that inbox shows mixed processing states."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            inbox_files = reader.get_inbox_files()
            assert len(inbox_files) == 1

            inbox = inbox_files[0]

            # Should have fewer tasks than next-actions (some unprocessed)
            assert len(inbox.tasks) < 10

            # Should contain some processed (#task) and unprocessed items
            # Unprocessed items are plain text, not checkboxes with #task
            processed_tasks = len(inbox.tasks)
            assert processed_tasks >= 2  # At least some processed
            assert processed_tasks <= 4  # But not everything

    def test_project_references_not_duplicates(self) -> None:
        """Test that projects file references tasks rather than duplicating them."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            project_files = reader.get_project_files()
            assert len(project_files) == 1

            projects = project_files[0]

            # Projects file should have very few or no tasks
            # (just references and project metadata)
            assert len(projects.tasks) == 0  # No duplicated tasks

            # Should have links to other files
            assert len(projects.links) > 0

    def test_waiting_for_categorization(self) -> None:
        """Test that waiting-for items are properly categorized."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            waiting_files = reader.get_waiting_for_files()
            assert len(waiting_files) == 1

            waiting_for = waiting_files[0]

            # Waiting items should not be extracted as actionable tasks
            # (they have #waiting tag, not #task tag)
            assert len(waiting_for.tasks) == 0

    def test_someday_maybe_categorization(self) -> None:
        """Test that someday/maybe items are properly categorized."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            someday_files = reader.get_someday_files()
            assert len(someday_files) == 1

            someday = someday_files[0]

            # Someday items should not be extracted as actionable tasks
            # (they have #someday tag, not #task tag)
            assert len(someday.tasks) == 0

            # Should have links for reference
            assert len(someday.links) > 0

    def test_vault_summary_with_fixtures(self) -> None:
        """Test vault summary statistics with realistic data."""
        with create_sample_vault() as vault_config:
            reader = VaultReader(vault_config)

            summary = reader.get_vault_summary()

            # Should have realistic counts
            total_files = summary["total_files"]
            total_tasks = summary["total_tasks"]
            total_links = summary["total_links"]
            assert isinstance(total_files, int)
            assert isinstance(total_tasks, int)
            assert isinstance(total_links, int)
            assert total_files >= 8
            # Many tasks consolidated in next-actions
            assert total_tasks > 20
            assert total_links > 10

            # Should have proper file type breakdown
            files_by_type = summary["files_by_type"]
            assert isinstance(files_by_type, dict)
            assert files_by_type["next-actions"] == 1
            assert files_by_type["context"] >= 4

            # Should have proper task distribution
            tasks_by_type = summary["tasks_by_type"]
            assert isinstance(tasks_by_type, dict)

            # Most tasks should be in next-actions
            next_actions_tasks = tasks_by_type.get("next-actions", 0)
            assert next_actions_tasks > 15


class TestNewUserOnboardingWorkflow:
    """Integration tests for task 5.1: New user onboarding workflow."""

    def test_complete_gtd_vault_setup_from_empty_directory(self) -> None:
        """Test new user onboarding workflow.

        Complete GTD vault setup from empty directory.

        This test verifies:
        - setup_gtd_vault creates all required files/folders
        - list_gtd_files shows proper structure
        - read_gtd_files returns expected templates
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "new_user_vault"

            # Ensure directory doesn't exist initially
            assert not vault_path.exists()

            # Step 1: Setup GTD vault structure
            setup_result = setup_gtd_vault(str(vault_path))

            # Verify setup succeeded
            assert setup_result["status"] == "success"
            assert setup_result["vault_path"] == str(vault_path)

            # Verify all expected files were created
            expected_created = {
                str(vault_path),  # vault directory itself
                "gtd/",
                "gtd/contexts/",
                "gtd/inbox.md",
                "gtd/projects.md",
                "gtd/next-actions.md",
                "gtd/waiting-for.md",
                "gtd/someday-maybe.md",
                "gtd/contexts/@calls.md",
                "gtd/contexts/@computer.md",
                "gtd/contexts/@errands.md",
                "gtd/contexts/@home.md",
            }

            created_set = set(setup_result["created"])
            assert expected_created.issubset(created_set)
            assert len(setup_result["already_existed"]) == 0  # Nothing should pre-exist

            # Verify vault directory and GTD structure exist
            assert vault_path.exists()
            assert (vault_path / "gtd").exists()
            assert (vault_path / "gtd" / "contexts").exists()

            # Step 2: Test list_gtd_files shows proper structure
            vault_config = VaultConfig(vault_path)
            vault_reader = VaultReader(vault_config)

            # Get all GTD files
            all_files = vault_reader.read_all_gtd_files()

            # Should have all expected file types
            file_types = {f.file_type for f in all_files}
            expected_types = {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }
            assert expected_types == file_types

            # Should have exactly the expected number of files
            # 5 standard files + 4 context files = 9 total
            assert len(all_files) == 9

            # Verify context files
            context_files = [f for f in all_files if f.file_type == "context"]
            assert len(context_files) == 4

            context_names = {f.path.split("/")[-1] for f in context_files}
            expected_context_names = {
                "@calls.md",
                "@computer.md",
                "@errands.md",
                "@home.md",
            }
            assert context_names == expected_context_names

            # Step 3: Verify read_gtd_files returns expected templates

            # Check inbox template
            inbox_files = [f for f in all_files if f.file_type == "inbox"]
            assert len(inbox_files) == 1
            inbox = inbox_files[0]
            assert "# Inbox" in inbox.content
            assert "capture everything here first" in inbox.content.lower()

            # Check projects template
            project_files = [f for f in all_files if f.file_type == "projects"]
            assert len(project_files) == 1
            projects = project_files[0]
            assert "# Projects" in projects.content
            assert "defined outcomes" in projects.content.lower()

            # Check next-actions template
            next_action_files = [f for f in all_files if f.file_type == "next-actions"]
            assert len(next_action_files) == 1
            next_actions = next_action_files[0]
            assert "# Next Actions" in next_actions.content
            assert "context-organized" in next_actions.content.lower()

            # Check waiting-for template
            waiting_files = [f for f in all_files if f.file_type == "waiting-for"]
            assert len(waiting_files) == 1
            waiting = waiting_files[0]
            assert "# Waiting For" in waiting.content
            assert "delegated items" in waiting.content.lower()

            # Check someday-maybe template
            someday_files = [f for f in all_files if f.file_type == "someday-maybe"]
            assert len(someday_files) == 1
            someday = someday_files[0]
            assert "# Someday / Maybe" in someday.content
            assert "future possibilities" in someday.content.lower()

            # Check context files have proper Obsidian Tasks query syntax
            for context_file in context_files:
                assert "```tasks" in context_file.content
                assert "not done" in context_file.content
                assert "```" in context_file.content

                # Context-specific checks
                if "@calls" in context_file.path:
                    assert "📞" in context_file.content
                    assert "@calls" in context_file.content
                elif "@computer" in context_file.path:
                    assert "💻" in context_file.content
                    assert "@computer" in context_file.content
                elif "@errands" in context_file.path:
                    assert "🚗" in context_file.content
                    assert "@errands" in context_file.content
                elif "@home" in context_file.path:
                    assert "🏠" in context_file.content
                    assert "@home" in context_file.content

            # Step 4: Verify files are ready for immediate use

            # All template files should be valid markdown
            for gtd_file in all_files:
                assert gtd_file.content is not None
                assert len(gtd_file.content.strip()) > 0
                assert gtd_file.title is not None

            # Templates should not contain any tasks initially
            # (they're templates, not user data)
            for gtd_file in all_files:
                if (
                    gtd_file.file_type != "context"
                ):  # Context files have query blocks, not tasks
                    assert len(gtd_file.tasks) == 0

            # Context files should contain no tasks (they have query syntax)
            for context_file in context_files:
                assert len(context_file.tasks) == 0
