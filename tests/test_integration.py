"""Integration tests for GTD MCP server components."""

from md_gtd_mcp.services.vault_reader import VaultReader
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
