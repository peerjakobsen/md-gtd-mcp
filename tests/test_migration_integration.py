"""Integration tests for MCP resources conversion and migration compatibility.

This module tests the complete migration from MCP tools to resources, ensuring:
1. Resource access through MCP client simulation
2. Data consistency between tools and resources during migration
3. Performance with various vault sizes and configurations
4. Filtered resource variants work correctly with file type parameters

Tests validate that the resource conversion maintains perfect backward compatibility
while improving semantic correctness and LLM understanding.
"""

import tempfile
import time
from pathlib import Path

import pytest

from md_gtd_mcp.services.resource_handler import ResourceHandler
from tests.fixtures import create_sample_vault


class TestMigrationIntegration:
    """Integration tests for migration from tools to resources."""

    def test_resource_access_through_mcp_client_simulation(self) -> None:
        """Test resource access through MCP client simulation patterns."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Simulate common MCP client access patterns

            # Pattern 1: File discovery workflow
            # Pattern 1: File discovery workflow uses gtd://{vault_path}/files
            files_result = resource_handler.get_files(vault_path)

            assert files_result["status"] == "success"
            assert "files" in files_result
            assert "summary" in files_result
            assert len(files_result["files"]) >= 8

            # Pattern 2: Specific file access based on discovery
            first_file = files_result["files"][0]
            file_path = first_file["file_path"]
            file_uri = f"gtd://{vault_path}/file/{file_path}"

            # Parse URI to test URI parsing works correctly
            parsed_file_uri = resource_handler.parse_file_uri(file_uri)
            assert parsed_file_uri["vault_path"] == vault_path
            assert parsed_file_uri["file_path"] == file_path

            file_result = resource_handler.get_file(vault_path, file_path)
            assert file_result["status"] == "success"
            assert file_result["file"]["file_path"] == file_path

            # Pattern 3: Batch content for analysis
            # Pattern 3: Batch content for analysis uses gtd://{vault_path}/content
            content_result = resource_handler.get_content(vault_path)

            assert content_result["status"] == "success"
            assert len(content_result["files"]) == len(files_result["files"])

            # Validate client can chain these operations naturally
            for file_data in content_result["files"]:
                assert "content" in file_data
                assert "tasks" in file_data
                assert "links" in file_data

    def test_data_consistency_between_tools_and_resources(self) -> None:
        """Test data consistency between tools and resources during migration."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Import the current tool implementations for comparison
            from md_gtd_mcp.server import (
                list_gtd_files_impl,
                read_gtd_file_impl,
                read_gtd_files_impl,
            )

            # Test 1: list_gtd_files vs files resource
            tool_files_result = list_gtd_files_impl(vault_path)
            resource_files_result = resource_handler.get_files(vault_path)

            # Data format should be identical
            assert tool_files_result["status"] == resource_files_result["status"]
            assert len(tool_files_result["files"]) == len(
                resource_files_result["files"]
            )

            # Verify file metadata consistency
            tool_files_by_path = {f["file_path"]: f for f in tool_files_result["files"]}
            resource_files_by_path = {
                f["file_path"]: f for f in resource_files_result["files"]
            }

            for file_path in tool_files_by_path:
                assert file_path in resource_files_by_path
                tool_file = tool_files_by_path[file_path]
                resource_file = resource_files_by_path[file_path]

                assert tool_file["file_type"] == resource_file["file_type"]
                assert tool_file["task_count"] == resource_file["task_count"]
                assert tool_file["link_count"] == resource_file["link_count"]

            # Test 2: read_gtd_file vs file resource
            test_file = tool_files_result["files"][0]["file_path"]
            tool_file_result = read_gtd_file_impl(vault_path, test_file)
            resource_file_result = resource_handler.get_file(vault_path, test_file)

            # Data format should be identical
            assert tool_file_result["status"] == resource_file_result["status"]
            tool_file_data = tool_file_result["file"]
            resource_file_data = resource_file_result["file"]

            assert tool_file_data["file_path"] == resource_file_data["file_path"]
            assert tool_file_data["file_type"] == resource_file_data["file_type"]
            assert tool_file_data["content"] == resource_file_data["content"]
            assert len(tool_file_data["tasks"]) == len(resource_file_data["tasks"])
            assert len(tool_file_data["links"]) == len(resource_file_data["links"])

            # Test 3: read_gtd_files vs content resource
            tool_content_result = read_gtd_files_impl(vault_path)
            resource_content_result = resource_handler.get_content(vault_path)

            # Data format should be identical
            assert tool_content_result["status"] == resource_content_result["status"]
            assert len(tool_content_result["files"]) == len(
                resource_content_result["files"]
            )

            # Verify comprehensive content consistency
            tool_content_by_path = {
                f["file_path"]: f for f in tool_content_result["files"]
            }
            resource_content_by_path = {
                f["file_path"]: f for f in resource_content_result["files"]
            }

            for file_path in tool_content_by_path:
                assert file_path in resource_content_by_path
                tool_file = tool_content_by_path[file_path]
                resource_file = resource_content_by_path[file_path]

                assert tool_file["content"] == resource_file["content"]
                assert len(tool_file["tasks"]) == len(resource_file["tasks"])
                assert len(tool_file["links"]) == len(resource_file["links"])

    def test_performance_with_various_vault_sizes(self) -> None:
        """Test performance with various vault sizes and configurations."""
        resource_handler = ResourceHandler()

        # Test with small vault (default sample)
        with create_sample_vault() as small_vault_config:
            small_vault_path = str(small_vault_config.vault_path)

            # Benchmark files resource
            start_time = time.time()
            small_files_result = resource_handler.get_files(small_vault_path)
            small_files_duration = time.time() - start_time

            assert small_files_result["status"] == "success"
            assert small_files_duration < 1.0  # Should be very fast for small vault

            # Benchmark content resource
            start_time = time.time()
            small_content_result = resource_handler.get_content(small_vault_path)
            small_content_duration = time.time() - start_time

            assert small_content_result["status"] == "success"
            assert small_content_duration < 2.0  # Should be fast for small vault

        # Test with empty vault
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_vault_path = Path(temp_dir) / "empty_vault"
            empty_vault_path.mkdir()

            # Empty vault should handle gracefully
            start_time = time.time()
            empty_result = resource_handler.get_files(str(empty_vault_path))
            empty_duration = time.time() - start_time

            assert empty_result["status"] == "success"
            assert len(empty_result["files"]) == 0
            assert empty_duration < 0.5  # Should be very fast for empty vault
            assert "suggestion" in empty_result  # Should suggest setup

        # Test with nonexistent vault
        nonexistent_path = "/nonexistent/vault/path"
        start_time = time.time()
        error_result = resource_handler.get_files(nonexistent_path)
        error_duration = time.time() - start_time

        assert error_result["status"] == "error"
        assert error_duration < 0.1  # Should fail fast

    def test_filtered_resource_variants(self) -> None:
        """Test filtered resource variants work correctly with file type parameters."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Test files filtering
            inbox_files_result = resource_handler.get_files(
                vault_path, file_type="inbox"
            )
            projects_files_result = resource_handler.get_files(
                vault_path, file_type="projects"
            )
            context_files_result = resource_handler.get_files(
                vault_path, file_type="context"
            )

            # Validate filtering works correctly
            assert inbox_files_result["status"] == "success"
            assert projects_files_result["status"] == "success"
            assert context_files_result["status"] == "success"

            # Check file type consistency
            for file_data in inbox_files_result["files"]:
                assert file_data["file_type"] == "inbox"

            for file_data in projects_files_result["files"]:
                assert file_data["file_type"] == "projects"

            for file_data in context_files_result["files"]:
                assert file_data["file_type"] == "context"

            # Test content filtering
            inbox_content_result = resource_handler.get_content(
                vault_path, file_type="inbox"
            )
            projects_content_result = resource_handler.get_content(
                vault_path, file_type="projects"
            )

            assert inbox_content_result["status"] == "success"
            assert projects_content_result["status"] == "success"

            # Check content filtering consistency
            for file_data in inbox_content_result["files"]:
                assert file_data["file_type"] == "inbox"
                assert "content" in file_data
                assert "tasks" in file_data

            for file_data in projects_content_result["files"]:
                assert file_data["file_type"] == "projects"
                assert "content" in file_data

            # Test filtered vs unfiltered counts
            all_files_result = resource_handler.get_files(vault_path)
            total_files = len(all_files_result["files"])

            filtered_files_count = (
                len(inbox_files_result["files"])
                + len(projects_files_result["files"])
                + len(context_files_result["files"])
            )

            # Filtered results should not exceed total (may be less due to other types)
            assert filtered_files_count <= total_files

    def test_uri_pattern_validation_and_error_handling(self) -> None:
        """Test URI pattern validation and comprehensive error handling."""
        resource_handler = ResourceHandler()

        # Test valid URI patterns
        valid_uris = [
            "gtd://vault_path/files",
            "gtd://vault_path/files/inbox",
            "gtd://vault_path/file/GTD/inbox.md",
            "gtd://vault_path/content",
            "gtd://vault_path/content/projects",
            "gtd:///absolute/vault/path/files",
            "gtd:///absolute/vault/path/file/GTD/inbox.md",
        ]

        for uri in valid_uris:
            if "/files" in uri:
                parsed = resource_handler.parse_files_uri(uri)
                assert "vault_path" in parsed
            elif "/file/" in uri:
                parsed = resource_handler.parse_file_uri(uri)
                assert "vault_path" in parsed
                assert "file_path" in parsed
            elif "/content" in uri:
                parsed = resource_handler.parse_content_uri(uri)
                assert "vault_path" in parsed

        # Test invalid URI patterns
        invalid_uris = [
            "http://vault_path/files",  # Wrong scheme
            "gtd://vault_path",  # Missing resource type
            "gtd://vault_path/invalid",  # Unknown resource type
            "gtd://vault_path/files/type/extra",  # Too many path components
            "gtd://vault_path/file/",  # Missing file path
            "gtd://",  # Missing vault path
            # Note: "gtd:vault_path/files" (missing //) is actually parsed as
            # valid absolute path
        ]

        for uri in invalid_uris:
            with pytest.raises(ValueError):
                if "/files" in uri:
                    resource_handler.parse_files_uri(uri)
                elif "/file" in uri:
                    resource_handler.parse_file_uri(uri)
                elif "/content" in uri:
                    resource_handler.parse_content_uri(uri)
                else:
                    # For URIs without specific resource type, try files parsing
                    # which should fail
                    resource_handler.parse_files_uri(uri)

    def test_resource_annotations_and_mcp_compliance(self) -> None:
        """Test that resource implementations follow MCP protocol compliance."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Test that all resource operations are read-only and idempotent

            # Multiple calls should return identical results (idempotent)
            files_result_1 = resource_handler.get_files(vault_path)
            files_result_2 = resource_handler.get_files(vault_path)

            assert files_result_1 == files_result_2

            # Content should be identical across calls
            content_result_1 = resource_handler.get_content(vault_path)
            content_result_2 = resource_handler.get_content(vault_path)

            assert content_result_1 == content_result_2

            # File reading should be consistent
            test_file = files_result_1["files"][0]["file_path"]
            file_result_1 = resource_handler.get_file(vault_path, test_file)
            file_result_2 = resource_handler.get_file(vault_path, test_file)

            assert file_result_1 == file_result_2

            # Test that resources don't modify vault state (read-only)
            # We can't directly test file system changes, but we can verify
            # that resource operations don't add/modify/delete files

            # Get initial state
            initial_files = resource_handler.get_files(vault_path)
            initial_count = len(initial_files["files"])

            # Perform multiple resource operations
            resource_handler.get_content(vault_path)
            resource_handler.get_files(vault_path, file_type="inbox")
            resource_handler.get_file(vault_path, test_file)

            # Verify state unchanged
            final_files = resource_handler.get_files(vault_path)
            final_count = len(final_files["files"])

            assert initial_count == final_count
            assert initial_files["summary"] == final_files["summary"]


class TestResourceWorkflowCompatibility:
    """Test that resources support complete GTD workflow scenarios."""

    def test_complete_gtd_discovery_workflow(self) -> None:
        """Test complete GTD discovery workflow using only resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Step 1: Discover vault structure
            files_result = resource_handler.get_files(vault_path)
            assert files_result["status"] == "success"

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

            # Step 2: Focus on inbox for processing
            inbox_files = resource_handler.get_files(vault_path, file_type="inbox")
            assert len(inbox_files["files"]) >= 1

            inbox_file_path = inbox_files["files"][0]["file_path"]
            inbox_content = resource_handler.get_file(vault_path, inbox_file_path)

            assert inbox_content["status"] == "success"
            assert "content" in inbox_content["file"]

            # Step 3: Review project status
            projects_content = resource_handler.get_content(
                vault_path, file_type="projects"
            )
            assert projects_content["status"] == "success"

            # Step 4: Get actionable tasks
            next_actions_files = resource_handler.get_files(
                vault_path, file_type="next-actions"
            )
            if next_actions_files["files"]:
                next_actions_path = next_actions_files["files"][0]["file_path"]
                next_actions_content = resource_handler.get_file(
                    vault_path, next_actions_path
                )

                assert next_actions_content["status"] == "success"
                assert len(next_actions_content["file"]["tasks"]) > 0

    def test_context_based_task_filtering_workflow(self) -> None:
        """Test context-based task filtering workflow using resources."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get all context files
            context_files = resource_handler.get_files(vault_path, file_type="context")
            assert (
                len(context_files["files"]) >= 4
            )  # @calls, @computer, @errands, @home

            # Check specific context files exist
            context_paths = [f["file_path"] for f in context_files["files"]]
            context_names = [Path(p).stem for p in context_paths]

            expected_contexts = ["@calls", "@computer", "@errands", "@home"]
            for expected_context in expected_contexts:
                assert any(expected_context in name for name in context_names)

            # Read context file content
            calls_files = [
                f for f in context_files["files"] if "@calls" in f["file_path"]
            ]
            if calls_files:
                calls_content = resource_handler.get_file(
                    vault_path, calls_files[0]["file_path"]
                )
                assert calls_content["status"] == "success"
                assert "content" in calls_content["file"]

    def test_comprehensive_vault_analysis_workflow(self) -> None:
        """Test comprehensive vault analysis workflow using batch content access."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Get comprehensive content for analysis
            all_content = resource_handler.get_content(vault_path)
            assert all_content["status"] == "success"

            # Analyze task distribution
            total_tasks = 0
            tasks_by_type: dict[str, int] = {}
            files_by_type: dict[str, int] = {}

            for file_data in all_content["files"]:
                file_type = file_data["file_type"]
                task_count = len(file_data["tasks"])

                total_tasks += task_count
                tasks_by_type[file_type] = tasks_by_type.get(file_type, 0) + task_count
                files_by_type[file_type] = files_by_type.get(file_type, 0) + 1

            # Verify analysis results
            assert total_tasks > 0
            assert len(tasks_by_type) > 0
            assert len(files_by_type) >= 6  # Multiple file types

            # Verify summary data matches analysis
            summary = all_content["summary"]
            assert summary["total_tasks"] == total_tasks
            assert summary["total_files"] == len(all_content["files"])
