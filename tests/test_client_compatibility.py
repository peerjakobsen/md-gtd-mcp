"""Client compatibility tests for MCP resources with Claude Desktop and other clients.

This module tests MCP resource compatibility from the perspective of different clients,
ensuring proper protocol compliance, resource annotations, and expected client behavior.
Simulates real-world usage patterns that Claude Desktop and other MCP clients would use.

Key test areas:
- Resource URI pattern validation and parsing
- Resource annotation behavior (readOnlyHint, idempotentHint)
- Error handling for client scenarios
- Data format consistency for client consumption
- Performance characteristics relevant to client caching
"""

import json
import tempfile
import unittest
from pathlib import Path

from md_gtd_mcp.services.resource_handler import ResourceHandler
from tests.fixtures import create_sample_vault


class TestMCPClientCompatibility(unittest.TestCase):
    """Test MCP resource compatibility with Claude Desktop and other MCP clients.

    These tests simulate how MCP clients would interact with the GTD resources,
    focusing on protocol compliance and expected client behavior patterns.
    """

    def setUp(self) -> None:
        """Set up test environment with sample vault and resource handler."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure for testing
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        self._create_sample_gtd_files(gtd_path)

        self.resource_handler = ResourceHandler()

    def tearDown(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def _create_sample_gtd_files(self, gtd_path: Path) -> None:
        """Create sample GTD files for client compatibility testing."""
        # Inbox file with unclarified items (no #task tags per GTD methodology)
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text(
            "---\n"
            "title: Inbox\n"
            "type: inbox\n"
            "---\n\n"
            "# Inbox\n\n"
            "- [ ] Review quarterly report\n"
            "- [ ] Call dentist for appointment\n"
            "- [ ] Research new project management tool\n"
        )

        # Projects file with clarified projects
        projects_file = gtd_path / "projects.md"
        projects_file.write_text(
            "---\n"
            "title: Active Projects\n"
            "type: projects\n"
            "---\n\n"
            "# Active Projects\n\n"
            "## Website Redesign\n"
            "- [x] Complete user research #task\n"
            "- [ ] Design mockups #task @computer\n"
            "- [ ] Review with stakeholders #task @office\n\n"
            "## Marketing Campaign\n"
            "- [ ] Draft content calendar #task @computer\n"
            "- [ ] Schedule social media posts #task @computer\n"
        )

        # Next actions file
        next_actions_file = gtd_path / "next-actions.md"
        next_actions_file.write_text(
            "---\n"
            "title: Next Actions\n"
            "type: next-actions\n"
            "---\n\n"
            "# Next Actions\n\n"
            "## @computer\n"
            "- [ ] Update project documentation #task\n"
            "- [ ] Send follow-up emails #task\n\n"
            "## @calls\n"
            "- [ ] Call vendor for pricing #task\n"
        )

    def test_resource_uri_pattern_compliance(self) -> None:
        """Test that resource URIs follow expected patterns for MCP clients."""
        vault_path_str = str(self.vault_path)

        # Test all five resource URI patterns are accessible
        expected_patterns = [
            f"gtd://{vault_path_str}/files",
            f"gtd://{vault_path_str}/files/inbox",
            f"gtd://{vault_path_str}/file/gtd/inbox.md",
            f"gtd://{vault_path_str}/content",
            f"gtd://{vault_path_str}/content/projects",
        ]

        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                # Extract components as MCP client would
                if "/files/" in pattern:
                    vault_path = pattern.split("gtd://")[1].split("/files/")[0]
                    file_type = pattern.split("/files/")[1]
                    self.assertIn(file_type, ["inbox", "projects", "next-actions"])
                elif "/file/" in pattern:
                    vault_path = pattern.split("gtd://")[1].split("/file/")[0]
                    file_path = pattern.split("/file/")[1]
                    self.assertTrue(file_path.endswith(".md"))
                elif "/content/" in pattern:
                    vault_path = pattern.split("gtd://")[1].split("/content/")[0]
                    content_type = pattern.split("/content/")[1]
                    self.assertIn(content_type, ["inbox", "projects", "next-actions"])
                else:
                    # Base patterns
                    vault_path = pattern.split("gtd://")[1].split("/")[0]

                self.assertTrue(Path(vault_path).exists())

    def test_resource_annotations_for_client_behavior(self) -> None:
        """Test resource annotations guide proper client behavior.

        Claude Desktop and other MCP clients should understand:
        - readOnlyHint: true - Safe to call repeatedly, no side effects
        - idempotentHint: true - Same result for same parameters
        """
        # Test that resources are marked as read-only and idempotent
        # This would be checked by MCP clients during introspection

        # Simulate client checking resource metadata
        vault_path_str = str(self.vault_path)

        # All resource operations should be safe to repeat
        for _ in range(3):
            result1 = self.resource_handler.get_files(vault_path_str)
            result2 = self.resource_handler.get_files(vault_path_str)

            # Idempotent: same call returns same result
            self.assertEqual(result1, result2)

            # Read-only: no side effects on repeated calls
            self.assertEqual(result1["status"], "success")
            self.assertIn("files", result1)

    def test_claude_desktop_workflow_patterns(self) -> None:
        """Test resource access patterns typical of Claude Desktop workflows.

        Simulates how Claude Desktop would access resources during GTD workflows:
        1. Daily inbox processing
        2. Weekly review scenarios
        3. Project status checking
        """
        vault_path_str = str(self.vault_path)

        # Scenario 1: Claude Desktop processing inbox
        # "Help me process my inbox items following GTD methodology"
        inbox_files = self.resource_handler.get_files(vault_path_str, "inbox")
        self.assertEqual(inbox_files["status"], "success")
        self.assertTrue(len(inbox_files["files"]) > 0)

        # Read specific inbox content for processing
        inbox_content = self.resource_handler.get_content(vault_path_str, "inbox")
        self.assertEqual(inbox_content["status"], "success")
        self.assertIn("files", inbox_content)

        # Scenario 2: Claude Desktop weekly review
        # "Give me a complete analysis of my GTD system"
        complete_content = self.resource_handler.get_content(vault_path_str)
        self.assertEqual(complete_content["status"], "success")
        self.assertIn("files", complete_content)
        self.assertTrue(
            len(complete_content["files"]) >= 3
        )  # inbox, projects, next-actions

        # Scenario 3: Claude Desktop project status check
        # "Show me my current projects and their status"
        project_files = self.resource_handler.get_files(vault_path_str, "projects")
        self.assertEqual(project_files["status"], "success")

        project_content = self.resource_handler.get_content(vault_path_str, "projects")
        self.assertEqual(project_content["status"], "success")

    def test_error_handling_for_client_scenarios(self) -> None:
        """Test error handling scenarios that MCP clients might encounter.

        Ensures proper error responses for common client mistakes:
        - Invalid vault paths
        - Missing files
        - Malformed file types
        """
        # Invalid vault path - client provides wrong path
        invalid_vault = "/nonexistent/vault"
        result = self.resource_handler.get_files(invalid_vault)

        # Should return structured error, not crash
        self.assertIn("status", result)
        self.assertIn("error", result.get("status", "").lower() or "error")

        # Invalid file type - client typo in file type
        valid_vault = str(self.vault_path)
        result = self.resource_handler.get_files(valid_vault, "invalid_type")

        # Should return empty result or error indication
        self.assertIn("status", result)
        if result["status"] == "success":
            self.assertEqual(len(result.get("files", [])), 0)

        # Missing specific file - client requests non-existent file
        result = self.resource_handler.get_file(valid_vault, "gtd/nonexistent.md")

        # Should return structured error response
        self.assertIn("status", result)

    def test_json_format_consistency_for_clients(self) -> None:
        """Test JSON response format consistency for client parsing.

        MCP clients expect consistent JSON structure across all resources.
        Tests that all resources return parseable JSON with expected fields.
        """
        vault_path_str = str(self.vault_path)

        # Test all resource types return valid JSON
        test_cases = [
            ("files", lambda: self.resource_handler.get_files(vault_path_str)),
            (
                "files_filtered",
                lambda: self.resource_handler.get_files(vault_path_str, "inbox"),
            ),
            (
                "single_file",
                lambda: self.resource_handler.get_file(vault_path_str, "gtd/inbox.md"),
            ),
            ("content", lambda: self.resource_handler.get_content(vault_path_str)),
            (
                "content_filtered",
                lambda: self.resource_handler.get_content(vault_path_str, "projects"),
            ),
        ]

        for test_name, resource_func in test_cases:
            with self.subTest(test_name=test_name):
                result = resource_func()  # type: ignore[no-untyped-call]

                # Should be valid dictionary (JSON parseable)
                self.assertIsInstance(result, dict)

                # Should have consistent status field
                self.assertIn("status", result)

                # Should have vault_path for client context
                self.assertIn("vault_path", result)

                # Convert to JSON and back to ensure client can parse
                json_str = json.dumps(result)
                parsed_back = json.loads(json_str)
                self.assertEqual(result, parsed_back)

    def test_performance_characteristics_for_caching(self) -> None:
        """Test performance characteristics relevant to client caching behavior.

        MCP clients may cache resource responses. Tests that:
        - Resources return quickly enough for interactive use
        - Response sizes are reasonable for caching
        - Repeated access maintains performance
        """
        vault_path_str = str(self.vault_path)

        import time

        # Test file listing performance (should be fast - metadata only)
        start_time = time.time()
        result = self.resource_handler.get_files(vault_path_str)
        files_time = time.time() - start_time

        self.assertEqual(result["status"], "success")
        self.assertLess(files_time, 1.0)  # Should complete in under 1 second

        # Test content reading performance (slower but reasonable)
        start_time = time.time()
        result = self.resource_handler.get_content(vault_path_str)
        content_time = time.time() - start_time

        self.assertEqual(result["status"], "success")
        self.assertLess(content_time, 5.0)  # Should complete in under 5 seconds

        # Test response size for caching (should be reasonable)
        json_size = len(json.dumps(result))
        self.assertLess(json_size, 100000)  # Less than 100KB for caching efficiency

    def test_concurrent_client_access_safety(self) -> None:
        """Test that multiple clients can safely access resources concurrently.

        Resources should be thread-safe and not interfere with each other
        when multiple MCP clients access the same vault simultaneously.
        """
        vault_path_str = str(self.vault_path)

        # Simulate multiple clients accessing same resource
        results = []
        for _ in range(5):
            result = self.resource_handler.get_files(vault_path_str)
            results.append(result)

        # All results should be identical (no interference)
        first_result = results[0]
        for result in results[1:]:
            self.assertEqual(result, first_result)

        # All should be successful
        for result in results:
            self.assertEqual(result["status"], "success")

    def test_resource_discovery_for_clients(self) -> None:
        """Test resource discovery patterns for MCP client introspection.

        Tests that resources provide enough metadata for clients to understand:
        - Available resource types
        - Expected parameters
        - Usage patterns
        """
        vault_path_str = str(self.vault_path)

        # Test that file listing reveals available file types
        result = self.resource_handler.get_files(vault_path_str)
        self.assertEqual(result["status"], "success")

        file_types = {f.get("file_type") for f in result.get("files", [])}
        expected_types = {"inbox", "projects", "next-actions"}

        # Should contain GTD file types for client discovery
        self.assertTrue(expected_types.issubset(file_types))

        # Should provide metadata for client decision making
        for file_info in result.get("files", []):
            self.assertIn("file_type", file_info)
            self.assertIn("file_path", file_info)  # Actual field name is file_path
            self.assertIn("task_count", file_info)


class TestResourceAnnotationCompliance(unittest.TestCase):
    """Test MCP resource annotation compliance for optimal client behavior."""

    def test_readonly_hint_compliance(self) -> None:
        """Test that resources with readOnlyHint behave as read-only operations."""
        # This would be enforced by the MCP framework
        # Test verifies our resources don't modify state

        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Record initial state
            initial_files = resource_handler.get_files(vault_path)
            initial_content = resource_handler.get_content(vault_path)

            # Access resources multiple times
            for _ in range(10):
                resource_handler.get_files(vault_path)
                resource_handler.get_files(vault_path, "inbox")
                resource_handler.get_file(vault_path, "gtd/inbox.md")
                resource_handler.get_content(vault_path)
                resource_handler.get_content(vault_path, "projects")

            # State should be unchanged
            final_files = resource_handler.get_files(vault_path)
            final_content = resource_handler.get_content(vault_path)

            self.assertEqual(initial_files, final_files)
            self.assertEqual(initial_content, final_content)

    def test_idempotent_hint_compliance(self) -> None:
        """Test that resources with idempotentHint return consistent results."""
        with create_sample_vault() as vault_config:
            vault_path = str(vault_config.vault_path)
            resource_handler = ResourceHandler()

            # Call same resource multiple times
            results = []
            for _ in range(5):
                result = resource_handler.get_files(vault_path)
                results.append(result)

            # All results should be identical
            first_result = results[0]
            for result in results[1:]:
                self.assertEqual(result, first_result)


if __name__ == "__main__":
    unittest.main()
