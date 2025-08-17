"""Resource-based integration tests for GTD workflows and MCP server functionality.

This module contains updated integration tests that use MCP resources instead of tools,
demonstrating the complete migration from tool-based to resource-based access patterns.
All tests maintain the same coverage and validation while using the new resource URIs.

Key changes from original integration tests:
- Uses ResourceHandler for data access instead of tool imports
- Validates resource URI patterns and parsing
- Tests resource annotations and MCP protocol compliance
- Maintains identical test coverage and validation logic
"""

import tempfile
from pathlib import Path
from typing import Any

from md_gtd_mcp.services.resource_handler import ResourceHandler
from md_gtd_mcp.services.vault_setup import setup_gtd_vault
from tests.fixtures import create_sample_vault


class TestGTDIntegrationResources:
    """Resource-based integration tests for all parser components with VaultReader."""

    def test_complete_vault_reading_integration_with_resources(self) -> None:
        """Test complete integration of all parsers with realistic GTD vault.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Read all files using files resource
            files_result = resource_handler.get_files(vault_path)
            assert files_result["status"] == "success"

            # Should have all GTD file types
            assert len(files_result["files"]) >= 8  # 5 standard + 3+ context files

            file_types = {f["file_type"] for f in files_result["files"]}
            expected_types = {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }
            assert expected_types.issubset(file_types)

    def test_task_extraction_across_files_with_resources(self) -> None:
        """Test TaskExtractor integration across different file types.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get content for files that should contain tasks
            content_result = resource_handler.get_content(vault_path)
            assert content_result["status"] == "success"

            # Filter files with tasks
            task_files = [f for f in content_result["files"] if len(f["tasks"]) > 0]

            # Should have tasks in inbox and next-actions primarily
            task_file_types = {f["file_type"] for f in task_files}
            expected_task_types = {"inbox", "next-actions"}
            assert expected_task_types.issubset(task_file_types)

            # Count total actionable tasks (#task tag)
            total_tasks = sum(len(f["tasks"]) for f in task_files)
            assert total_tasks > 20  # Should have many consolidated tasks

    def test_context_file_query_parsing_with_resources(self) -> None:
        """Test that context files with query blocks are parsed gracefully.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get context files using filtered resource
            context_files_result = resource_handler.get_files(
                vault_path, file_type="context"
            )
            assert context_files_result["status"] == "success"
            assert (
                len(context_files_result["files"]) == 4
            )  # @calls, @computer, @errands, @home

            # Get full content for context files
            context_content_result = resource_handler.get_content(
                vault_path, file_type="context"
            )
            assert context_content_result["status"] == "success"

            for context_file in context_content_result["files"]:
                # Context files should parse without errors
                title_check = "@" in context_file[
                    "file_path"
                ] or "Context" in context_file.get("title", "")
                assert title_check
                assert context_file["file_type"] == "context"
                assert context_file["content"] is not None

                # Should not extract tasks from query blocks
                # (Query blocks are code blocks, not task checkboxes)
                assert len(context_file["tasks"]) == 0

    def test_link_extraction_across_files_with_resources(self) -> None:
        """Test LinkExtractor integration for wikilinks and context links.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get all file content for link analysis
            content_result = resource_handler.get_content(vault_path)
            assert content_result["status"] == "success"

            # Collect all links
            all_links = []
            for f in content_result["files"]:
                all_links.extend(f["links"])

            assert len(all_links) > 0

            # Should have various link types
            wikilinks = [link for link in all_links if not link["is_external"]]
            context_links = [
                link for link in all_links if link["target"].startswith("@")
            ]

            assert len(wikilinks) > 0
            assert len(context_links) > 0

    def test_next_actions_as_primary_task_source_with_resources(self) -> None:
        """Test that next-actions.md is the primary source of actionable tasks.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get next-actions files using filtered resource
            next_actions_files_result = resource_handler.get_files(
                vault_path, file_type="next-actions"
            )
            assert next_actions_files_result["status"] == "success"
            assert len(next_actions_files_result["files"]) == 1

            # Get full content
            next_actions_file_path = next_actions_files_result["files"][0]["file_path"]
            next_actions_result = resource_handler.get_file(
                vault_path, next_actions_file_path
            )
            assert next_actions_result["status"] == "success"

            next_actions_data = next_actions_result["file"]

            # Should have the most tasks with proper context tags
            assert (
                len(next_actions_data["tasks"]) > 15
            )  # Consolidated from all contexts

            # Check that tasks have proper context information
            task_contexts = [
                task["context"]
                for task in next_actions_data["tasks"]
                if task["context"]
            ]
            context_tags = ["@calls", "@computer", "@errands", "@home"]

            # Should have tasks for each context
            for context_tag in context_tags:
                assert any(context == context_tag for context in task_contexts)

    def test_inbox_processing_states_with_resources(self) -> None:
        """Test that inbox shows mixed processing states using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get inbox files
            inbox_files_result = resource_handler.get_files(
                vault_path, file_type="inbox"
            )
            assert inbox_files_result["status"] == "success"
            assert len(inbox_files_result["files"]) == 1

            # Get inbox content
            inbox_file_path = inbox_files_result["files"][0]["file_path"]
            inbox_result = resource_handler.get_file(vault_path, inbox_file_path)
            assert inbox_result["status"] == "success"

            inbox_data = inbox_result["file"]

            # Should have fewer tasks than next-actions (some unprocessed)
            assert len(inbox_data["tasks"]) < 10

            # With GTD phase-aware recognition, inbox recognizes ALL checkbox items
            # This is correct GTD behavior - capture phase doesn't require #task tags
            processed_tasks = len(inbox_data["tasks"])
            assert processed_tasks >= 2  # At least some tasks
            assert processed_tasks <= 6  # But reasonable number for inbox

    def test_project_references_not_duplicates_with_resources(self) -> None:
        """Test that projects file references tasks rather than duplicating them.

        Uses resources for data access.
        """
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get project files
            project_files_result = resource_handler.get_files(
                vault_path, file_type="projects"
            )
            assert project_files_result["status"] == "success"
            assert len(project_files_result["files"]) == 1

            # Get projects content
            project_file_path = project_files_result["files"][0]["file_path"]
            projects_result = resource_handler.get_file(vault_path, project_file_path)
            assert projects_result["status"] == "success"

            projects_data = projects_result["file"]

            # Projects file should have very few or no tasks
            # (just references and project metadata)
            assert len(projects_data["tasks"]) == 0  # No duplicated tasks

            # Should have links to other files
            assert len(projects_data["links"]) > 0

    def test_waiting_for_categorization_with_resources(self) -> None:
        """Test that waiting-for items are properly categorized using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get waiting-for files
            waiting_files_result = resource_handler.get_files(
                vault_path, file_type="waiting-for"
            )
            assert waiting_files_result["status"] == "success"
            assert len(waiting_files_result["files"]) == 1

            # Get waiting-for content
            waiting_file_path = waiting_files_result["files"][0]["file_path"]
            waiting_result = resource_handler.get_file(vault_path, waiting_file_path)
            assert waiting_result["status"] == "success"

            waiting_data = waiting_result["file"]

            # Waiting items should not be extracted as actionable tasks
            # (they have #waiting tag, not #task tag)
            assert len(waiting_data["tasks"]) == 0

    def test_someday_maybe_categorization_with_resources(self) -> None:
        """Test that someday/maybe items are properly categorized using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get someday-maybe files
            someday_files_result = resource_handler.get_files(
                vault_path, file_type="someday-maybe"
            )
            assert someday_files_result["status"] == "success"
            assert len(someday_files_result["files"]) == 1

            # Get someday-maybe content
            someday_file_path = someday_files_result["files"][0]["file_path"]
            someday_result = resource_handler.get_file(vault_path, someday_file_path)
            assert someday_result["status"] == "success"

            someday_data = someday_result["file"]

            # Someday items should not be extracted as actionable tasks
            # (they have #someday tag, not #task tag)
            assert len(someday_data["tasks"]) == 0

            # Should have links for reference
            assert len(someday_data["links"]) > 0

    def test_vault_summary_with_fixtures_using_resources(self) -> None:
        """Test vault summary statistics with realistic data using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get files for summary analysis
            files_result = resource_handler.get_files(vault_path)
            assert files_result["status"] == "success"

            summary = files_result["summary"]

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
            assert files_by_type.get("next-actions", 0) == 1
            assert files_by_type.get("context", 0) >= 4

            # Should have proper task distribution
            tasks_by_type = summary["tasks_by_type"]
            assert isinstance(tasks_by_type, dict)

            # Most tasks should be in next-actions
            next_actions_tasks = tasks_by_type.get("next-actions", 0)
            assert next_actions_tasks > 15


class TestContextBasedTaskFilteringWorkflowResources:
    """Test context-based task filtering workflow using resources."""

    def test_context_file_type_filtering_with_files_resource(self) -> None:
        """Test using files resource with file_type='context' for context overview."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Use files resource to get lightweight context file overview
            result = resource_handler.get_files(vault_path, file_type="context")

            assert result["status"] == "success"
            assert len(result["files"]) == 4  # 4 context files

            # All returned files should be context type
            for file_data in result["files"]:
                assert file_data["file_type"] == "context"

            # Should have metadata for quick overview
            for file_data in result["files"]:
                assert "file_path" in file_data
                assert "task_count" in file_data
                assert "link_count" in file_data
                # files resource provides metadata only (no full content)
                assert "content" not in file_data

    def test_context_specific_query_content_with_file_resource(self) -> None:
        """Test reading specific context files for task queries using file resource."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Read specific context files
            calls_result = resource_handler.get_file(
                vault_path, "gtd/contexts/@calls.md"
            )

            assert calls_result["status"] == "success"
            calls_data = calls_result["file"]
            assert calls_data["file_type"] == "context"
            assert "```tasks" in calls_data["content"]
            assert "@calls" in calls_data["content"]

            computer_result = resource_handler.get_file(
                vault_path, "gtd/contexts/@computer.md"
            )

            assert computer_result["status"] == "success"
            computer_data = computer_result["file"]
            assert computer_data["file_type"] == "context"
            assert "```tasks" in computer_data["content"]
            assert "@computer" in computer_data["content"]

    def test_comprehensive_context_analysis_with_content_resource(self) -> None:
        """Test comprehensive context analysis using content resource."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Use content resource for comprehensive context analysis
            result = resource_handler.get_content(vault_path)

            assert result["status"] == "success"
            files = result["files"]

            # Filter context files from comprehensive results
            context_files = [f for f in files if f["file_type"] == "context"]
            assert len(context_files) == 4

            # Analyze context content structure
            for context_file in context_files:
                # Each context file should have Obsidian Tasks syntax
                content = context_file["content"]
                assert "```tasks" in content
                assert "not done" in content
                assert "```" in content

                # Should have appropriate context mentions
                file_path = context_file["file_path"]
                if "@calls" in file_path:
                    assert "@calls" in content
                elif "@computer" in file_path:
                    assert "@computer" in content
                elif "@errands" in file_path:
                    assert "@errands" in content
                elif "@home" in file_path:
                    assert "@home" in content


class TestNewUserOnboardingWorkflowResources:
    """Resource-based integration tests for new user onboarding workflow."""

    def test_complete_gtd_vault_setup_with_resource_verification(self) -> None:
        """Test new user onboarding workflow with resource-based verification.

        Complete GTD vault setup from empty directory, then verify using resources.

        This test verifies:
        - setup_gtd_vault creates all required files/folders
        - files resource shows proper structure
        - content resource returns expected templates
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "new_user_vault"
            resource_handler = ResourceHandler()

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

            # Step 2: Test files resource shows proper structure
            files_result = resource_handler.get_files(str(vault_path))
            assert files_result["status"] == "success"

            # Should have all expected file types
            file_types = {f["file_type"] for f in files_result["files"]}
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
            assert len(files_result["files"]) == 9

            # Verify context files
            context_files = [
                f for f in files_result["files"] if f["file_type"] == "context"
            ]
            assert len(context_files) == 4

            context_paths = {f["file_path"] for f in context_files}
            expected_context_files = {
                "gtd/contexts/@calls.md",
                "gtd/contexts/@computer.md",
                "gtd/contexts/@errands.md",
                "gtd/contexts/@home.md",
            }
            # Check that expected context files are present
            for expected_file in expected_context_files:
                assert any(expected_file in path for path in context_paths)

            # Step 3: Verify content resource returns expected templates
            content_result = resource_handler.get_content(str(vault_path))
            assert content_result["status"] == "success"

            files_by_type: dict[str, list[dict[str, Any]]] = {}
            for file_data in content_result["files"]:
                file_type = file_data["file_type"]
                if file_type not in files_by_type:
                    files_by_type[file_type] = []
                files_by_type[file_type].append(file_data)

            # Check inbox template
            inbox_files = files_by_type["inbox"]
            assert len(inbox_files) == 1
            inbox = inbox_files[0]
            assert "# Inbox" in inbox["content"]
            assert "capture everything here first" in inbox["content"].lower()

            # Check projects template
            project_files = files_by_type["projects"]
            assert len(project_files) == 1
            projects = project_files[0]
            assert "# Projects" in projects["content"]
            assert "defined outcomes" in projects["content"].lower()

            # Check next-actions template
            next_action_files = files_by_type["next-actions"]
            assert len(next_action_files) == 1
            next_actions = next_action_files[0]
            assert "# Next Actions" in next_actions["content"]
            assert "context-organized" in next_actions["content"].lower()

            # Check waiting-for template
            waiting_files = files_by_type["waiting-for"]
            assert len(waiting_files) == 1
            waiting = waiting_files[0]
            assert "# Waiting For" in waiting["content"]
            assert "delegated items" in waiting["content"].lower()

            # Check someday-maybe template
            someday_files = files_by_type["someday-maybe"]
            assert len(someday_files) == 1
            someday = someday_files[0]
            assert "# Someday / Maybe" in someday["content"]
            assert "future possibilities" in someday["content"].lower()

            # Check context files have proper Obsidian Tasks query syntax
            context_files = files_by_type["context"]
            assert len(context_files) == 4

            for context_file in context_files:
                assert "```tasks" in context_file["content"]
                assert "not done" in context_file["content"]
                assert "```" in context_file["content"]

                # Context-specific checks
                file_path = context_file["file_path"]
                content = context_file["content"]
                if "@calls" in file_path:
                    assert "📞" in content
                    assert "@calls" in content
                elif "@computer" in file_path:
                    assert "💻" in content
                    assert "@computer" in content
                elif "@errands" in file_path:
                    assert "🚗" in content
                    assert "@errands" in content
                elif "@home" in file_path:
                    assert "🏠" in content
                    assert "@home" in content

            # Step 4: Verify files are ready for immediate use
            for file_data in content_result["files"]:
                assert file_data["content"] is not None
                assert len(file_data["content"].strip()) > 0

            # Templates should not contain any tasks initially
            # (they're templates, not user data)
            for file_data in content_result["files"]:
                if (
                    file_data["file_type"] != "context"
                ):  # Context files have query blocks, not tasks
                    assert len(file_data["tasks"]) == 0

            # Context files should contain no tasks (they have query syntax)
            for context_file in context_files:
                assert len(context_file["tasks"]) == 0


class TestExistingUserMigrationWorkflowResources:
    """Resource-based tests for existing user migration workflow."""

    def test_migration_workflow_with_resource_access(self) -> None:
        """Test migration workflow using resource access patterns."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Discover existing structure using files resource
            files_result = resource_handler.get_files(vault_path)
            assert files_result["status"] == "success"
            assert len(files_result["files"]) >= 8

            # Step 2: Analyze content structure using content resource
            content_result = resource_handler.get_content(vault_path)
            assert content_result["status"] == "success"

            # Verify migration-friendly features
            for file_data in content_result["files"]:
                # All files should have proper structure
                assert "file_type" in file_data
                assert "content" in file_data
                assert "tasks" in file_data
                assert "links" in file_data

            # Step 3: Validate task distribution
            task_counts_by_type: dict[str, int] = {}
            for file_data in content_result["files"]:
                file_type = file_data["file_type"]
                task_count = len(file_data["tasks"])
                task_counts_by_type[file_type] = (
                    task_counts_by_type.get(file_type, 0) + task_count
                )

            # Should have realistic task distribution
            assert task_counts_by_type.get("next-actions", 0) > 15
            assert task_counts_by_type.get("inbox", 0) >= 2


class TestDailyInboxProcessingWorkflowResources:
    """Resource-based tests for daily inbox processing workflow."""

    def test_inbox_discovery_and_processing_with_resources(self) -> None:
        """Test inbox discovery and processing using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Discover inbox using filtered files resource
            inbox_files_result = resource_handler.get_files(
                vault_path, file_type="inbox"
            )
            assert inbox_files_result["status"] == "success"
            assert len(inbox_files_result["files"]) == 1

            # Step 2: Read inbox content using file resource
            inbox_file_path = inbox_files_result["files"][0]["file_path"]
            inbox_result = resource_handler.get_file(vault_path, inbox_file_path)
            assert inbox_result["status"] == "success"

            inbox_data = inbox_result["file"]
            assert inbox_data["file_type"] == "inbox"
            assert "content" in inbox_data
            assert len(inbox_data["tasks"]) >= 2  # Some processed items

            # Step 3: Analyze task processing state
            for task in inbox_data["tasks"]:
                # Processed inbox items should have task structure
                assert "description" in task
                assert "completed" in task
                assert isinstance(task["completed"], bool)


class TestWeeklyReviewWorkflowResources:
    """Resource-based tests for weekly review workflow."""

    def test_comprehensive_weekly_review_with_content_resource(self) -> None:
        """Test comprehensive weekly review using content resource."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get comprehensive vault content for review
            content_result = resource_handler.get_content(vault_path)
            assert content_result["status"] == "success"

            # Analyze review metrics
            total_files = len(content_result["files"])
            total_tasks = sum(len(f["tasks"]) for f in content_result["files"])
            total_links = sum(len(f["links"]) for f in content_result["files"])

            assert total_files >= 8
            assert total_tasks > 20
            assert total_links > 10

            # Verify review can access all GTD areas
            file_types = {f["file_type"] for f in content_result["files"]}
            gtd_areas = {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }
            assert gtd_areas.issubset(file_types)

            # Verify summary data matches detailed analysis
            summary = content_result["summary"]
            assert summary["total_files"] == total_files
            assert summary["total_tasks"] == total_tasks
            assert summary["total_links"] == total_links


class TestProjectTrackingWorkflowResources:
    """Resource-based tests for project tracking workflow."""

    def test_project_tracking_workflow_with_resources(self) -> None:
        """Test project tracking workflow using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Get project overview using filtered resource
            projects_files_result = resource_handler.get_files(
                vault_path, file_type="projects"
            )
            assert projects_files_result["status"] == "success"
            assert len(projects_files_result["files"]) == 1

            # Step 2: Read project details using file resource
            projects_file_path = projects_files_result["files"][0]["file_path"]
            projects_result = resource_handler.get_file(vault_path, projects_file_path)
            assert projects_result["status"] == "success"

            projects_data = projects_result["file"]
            assert projects_data["file_type"] == "projects"
            assert "content" in projects_data

            # Step 3: Get actionable tasks from next-actions
            next_actions_files_result = resource_handler.get_files(
                vault_path, file_type="next-actions"
            )
            if next_actions_files_result["files"]:
                next_actions_file_path = next_actions_files_result["files"][0][
                    "file_path"
                ]
                next_actions_result = resource_handler.get_file(
                    vault_path, next_actions_file_path
                )

                assert next_actions_result["status"] == "success"
                next_actions_data = next_actions_result["file"]
                assert len(next_actions_data["tasks"]) > 15  # Project tasks


class TestCrossFileNavigationWorkflowResources:
    """Resource-based tests for cross-file navigation workflow."""

    def test_cross_file_navigation_with_resources(self) -> None:
        """Test cross-file navigation workflow using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Get comprehensive content for link analysis
            content_result = resource_handler.get_content(vault_path)
            assert content_result["status"] == "success"

            # Step 2: Extract all links for navigation
            all_links = []
            for file_data in content_result["files"]:
                all_links.extend(file_data["links"])

            assert len(all_links) > 10  # Should have many interconnections

            # Step 3: Verify link types and targets
            wikilinks = [link for link in all_links if not link["is_external"]]
            context_links = [
                link for link in all_links if link["target"].startswith("@")
            ]

            assert len(wikilinks) > 0
            assert len(context_links) > 0

            # Step 4: Test following specific links by reading referenced files
            for link in wikilinks[:3]:  # Test first few wikilinks
                target = link["target"]
                if ".md" not in target:
                    target += ".md"

                # Try to read the linked file
                try:
                    linked_file_result = resource_handler.get_file(
                        vault_path, f"gtd/{target}"
                    )
                    if linked_file_result["status"] == "success":
                        assert "content" in linked_file_result["file"]
                except Exception:
                    # Some links might not be valid file references
                    pass


class TestIncrementalVaultUpdatesWorkflowResources:
    """Resource-based tests for incremental vault updates workflow."""

    def test_incremental_updates_detection_with_resources(self) -> None:
        """Test incremental updates detection using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Get initial state using files resource
            initial_files_result = resource_handler.get_files(vault_path)
            assert initial_files_result["status"] == "success"
            initial_file_count = len(initial_files_result["files"])

            # Step 2: Get comprehensive initial content
            initial_content_result = resource_handler.get_content(vault_path)
            assert initial_content_result["status"] == "success"
            # Track initial task count for completeness
            _initial_task_count = sum(
                len(f["tasks"]) for f in initial_content_result["files"]
            )

            # Step 3: Verify consistent resource access
            # Multiple calls should return identical results (idempotent)
            repeat_files_result = resource_handler.get_files(vault_path)
            repeat_content_result = resource_handler.get_content(vault_path)

            assert repeat_files_result == initial_files_result
            assert repeat_content_result == initial_content_result

            # Step 4: Verify filtering consistency
            inbox_count = len(
                resource_handler.get_files(vault_path, file_type="inbox")["files"]
            )
            context_count = len(
                resource_handler.get_files(vault_path, file_type="context")["files"]
            )

            assert inbox_count == 1
            assert context_count == 4

            # Total should match filtered sums plus other types
            all_file_types = [
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            ]
            filtered_total = sum(
                len(resource_handler.get_files(vault_path, file_type=ft)["files"])
                for ft in all_file_types
            )
            assert filtered_total == initial_file_count
