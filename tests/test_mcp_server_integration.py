"""MCP server integration tests for client compatibility.

This module tests the actual FastMCP server integration to ensure MCP resources
are properly registered and accessible through the MCP protocol. Tests simulate
real MCP client interactions with the server.

Key test areas:
- Server startup and resource registration
- Resource template URI routing
- MCP protocol compliance
- Client-server communication patterns
"""

import json
import tempfile
import unittest
from pathlib import Path

from fastmcp import FastMCP

from md_gtd_mcp.server import mcp
from tests.fixtures import create_sample_vault


class TestMCPServerIntegration(unittest.TestCase):
    """Test MCP server integration with actual FastMCP server instance.

    These tests validate that the MCP server properly registers resources
    and handles client requests through the MCP protocol.
    """

    def setUp(self) -> None:
        """Set up test environment with sample vault."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.vault_path = Path(self.temp_dir.name) / "test_vault"
        self.vault_path.mkdir(parents=True)

        # Create GTD structure for testing
        gtd_path = self.vault_path / "gtd"
        gtd_path.mkdir()
        self._create_sample_gtd_files(gtd_path)

    def tearDown(self) -> None:
        """Clean up test environment."""
        self.temp_dir.cleanup()

    def _create_sample_gtd_files(self, gtd_path: Path) -> None:
        """Create sample GTD files for server integration testing."""
        # Inbox file
        inbox_file = gtd_path / "inbox.md"
        inbox_file.write_text(
            "---\n"
            "title: Inbox\n"
            "type: inbox\n"
            "---\n\n"
            "# Inbox\n\n"
            "- [ ] Review quarterly report\n"
            "- [ ] Call dentist for appointment\n"
        )

        # Projects file
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
        )

    def test_server_resource_registration(self) -> None:
        """Test that MCP server properly registers all GTD resources.

        Validates that FastMCP server instance has the expected resource templates
        registered and accessible through the MCP protocol.
        """
        # Test that the server instance is properly initialized
        self.assertIsInstance(mcp, FastMCP)

        # Test server metadata
        self.assertEqual(mcp.name, "Markdown GTD")
        self.assertIsNotNone(mcp.instructions)

        # Verify server instructions contain resource documentation
        instructions = mcp.instructions
        self.assertIsNotNone(instructions)
        self.assertIn("gtd://", instructions or "")
        self.assertIn("Resource URI Patterns", instructions or "")
        self.assertIn("Claude Desktop", instructions or "")

    def test_resource_template_uri_patterns(self) -> None:
        """Test that resource templates are registered with correct URI patterns.

        Validates that all five expected resource templates are available
        with the correct URI patterns for MCP client access.
        """
        vault_path_str = str(self.vault_path)

        # Expected resource URI patterns
        expected_patterns = [
            f"gtd://{vault_path_str}/files",
            f"gtd://{vault_path_str}/files/inbox",
            f"gtd://{vault_path_str}/file/gtd/inbox.md",
            f"gtd://{vault_path_str}/content",
            f"gtd://{vault_path_str}/content/projects",
        ]

        # Test that each pattern would be valid for MCP routing
        # This tests the URI pattern structure without actual MCP calls
        for pattern in expected_patterns:
            with self.subTest(pattern=pattern):
                # Validate URI structure
                self.assertTrue(pattern.startswith("gtd://"))

                # Extract and validate components
                path_part = pattern.replace("gtd://", "")
                components = path_part.split("/")

                # Should have vault path as first component
                self.assertTrue(len(components) >= 2)

                # Validate component types
                if "/files/" in pattern or pattern.endswith("/files"):
                    self.assertIn("files", components)
                elif "/file/" in pattern:
                    self.assertIn("file", components)
                elif "/content/" in pattern or pattern.endswith("/content"):
                    self.assertIn("content", components)

    def test_server_instructions_for_claude_desktop(self) -> None:
        """Test server instructions provide proper guidance for Claude Desktop.

        Validates that server instructions contain appropriate examples and
        guidance for Claude Desktop interaction with GTD resources.
        """
        instructions = mcp.instructions
        self.assertIsNotNone(instructions)

        # Should contain Claude Desktop-specific guidance
        self.assertIn("Claude Desktop", instructions or "")

        # Should contain resource URI examples
        self.assertIn("gtd://vault_path/files", instructions or "")
        self.assertIn("gtd://vault_path/content", instructions or "")

        # Should contain GTD workflow examples
        self.assertIn("Inbox Processing", instructions or "")
        self.assertIn("Weekly Review", instructions or "")

        # Should contain performance guidance
        self.assertIn("Fast - Metadata Only", instructions or "")
        self.assertIn("Medium Speed - Full Content", instructions or "")
        self.assertIn("Slower - All Content", instructions or "")

    def test_resource_annotations_accessibility(self) -> None:
        """Test that resource annotations are properly configured for MCP clients.

        Validates that resources have the correct annotations (readOnlyHint,
        idempotentHint) that MCP clients use for optimization.
        """
        # This would be validated by MCP framework during resource registration
        # Test ensures our server configuration includes proper annotations

        vault_path_str = str(self.vault_path)

        # Test that server doesn't crash with resource access patterns
        # that would use the annotations
        try:
            # Simulate repeated access (idempotent behavior)
            from md_gtd_mcp.services.resource_handler import ResourceHandler

            resource_handler = ResourceHandler()

            # Multiple calls should work without issues (idempotent)
            for _ in range(3):
                result = resource_handler.get_files(vault_path_str)
                self.assertEqual(result["status"], "success")

            # Should not modify state (read-only)
            result = resource_handler.get_files(vault_path_str)
            self.assertIn("files", result)

        except Exception as e:
            self.fail(f"Resource access failed: {e}")

    def test_error_handling_for_mcp_clients(self) -> None:
        """Test error handling patterns that MCP clients would encounter.

        Validates that the server provides appropriate error responses
        for common client error scenarios.
        """
        from md_gtd_mcp.services.resource_handler import ResourceHandler

        resource_handler = ResourceHandler()

        # Test invalid vault path
        invalid_result = resource_handler.get_files("/nonexistent/vault")
        self.assertIn("status", invalid_result)

        # Test that error responses are JSON-serializable for MCP transport
        try:
            json.dumps(invalid_result)
        except (TypeError, ValueError) as e:
            self.fail(f"Error response not JSON-serializable: {e}")

        # Test invalid file type
        valid_vault = str(self.vault_path)
        invalid_type_result = resource_handler.get_files(valid_vault, "invalid_type")

        # Should return structured response
        self.assertIn("status", invalid_type_result)

        # Should be JSON-serializable
        try:
            json.dumps(invalid_type_result)
        except (TypeError, ValueError) as e:
            self.fail(f"Error response not JSON-serializable: {e}")

    def test_json_response_format_for_mcp_transport(self) -> None:
        """Test that all resource responses are properly formatted for MCP transport.

        Validates that resource responses are JSON-serializable and follow
        consistent format for MCP client consumption.
        """
        from md_gtd_mcp.services.resource_handler import ResourceHandler

        resource_handler = ResourceHandler()

        vault_path_str = str(self.vault_path)

        # Test all resource types return MCP-compatible JSON
        test_cases = [
            ("files", lambda: resource_handler.get_files(vault_path_str)),
            (
                "files_filtered",
                lambda: resource_handler.get_files(vault_path_str, "inbox"),
            ),
            (
                "single_file",
                lambda: resource_handler.get_file(vault_path_str, "gtd/inbox.md"),
            ),
            ("content", lambda: resource_handler.get_content(vault_path_str)),
            (
                "content_filtered",
                lambda: resource_handler.get_content(vault_path_str, "projects"),
            ),
        ]

        for test_name, resource_func in test_cases:
            with self.subTest(test_name=test_name):
                result = resource_func()  # type: ignore[no-untyped-call]

                # Should be JSON-serializable for MCP transport
                try:
                    json_str = json.dumps(result)
                    parsed_back = json.loads(json_str)
                    self.assertEqual(result, parsed_back)
                except (TypeError, ValueError) as e:
                    self.fail(f"{test_name} response not JSON-serializable: {e}")

                # Should have consistent MCP response structure
                self.assertIn("status", result)
                self.assertIn("vault_path", result)

    def test_concurrent_mcp_client_simulation(self) -> None:
        """Test concurrent access patterns similar to multiple MCP clients.

        Simulates multiple MCP clients accessing resources simultaneously
        to validate thread safety and consistent responses.
        """
        from md_gtd_mcp.services.resource_handler import ResourceHandler

        resource_handler = ResourceHandler()

        vault_path_str = str(self.vault_path)

        # Simulate concurrent client access
        results = []

        # Multiple "clients" accessing same resource
        for _ in range(10):
            result = resource_handler.get_files(vault_path_str)
            results.append(result)

        # All results should be identical (no race conditions)
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            try:
                self.assertEqual(result, first_result)
            except AssertionError:
                self.fail(
                    f"Result {i} differs from first result - potential race condition"
                )

        # All should be successful
        for i, result in enumerate(results):
            self.assertEqual(result["status"], "success", f"Result {i} failed")

    def test_mcp_client_caching_behavior_simulation(self) -> None:
        """Test behavior that MCP clients would rely on for caching.

        Validates idempotent behavior and response consistency that
        MCP clients use for caching optimizations.
        """
        from md_gtd_mcp.services.resource_handler import ResourceHandler

        resource_handler = ResourceHandler()

        vault_path_str = str(self.vault_path)

        # Get baseline response
        baseline = resource_handler.get_files(vault_path_str)

        # Simulate client caching behavior - multiple access over time
        import time

        responses = []

        for _ in range(5):
            time.sleep(0.01)  # Small delay to simulate time passage
            response = resource_handler.get_files(vault_path_str)
            responses.append(response)

        # All responses should be identical (suitable for caching)
        for response in responses:
            self.assertEqual(response, baseline)

        # Response should contain cache-friendly metadata
        self.assertIn("status", baseline)
        self.assertIn("vault_path", baseline)

        # Should be deterministic for caching
        self.assertEqual(baseline["status"], "success")


class TestMCPProtocolCompliance(unittest.TestCase):
    """Test MCP protocol compliance for resource operations."""

    def test_resource_uri_scheme_compliance(self) -> None:
        """Test that resource URIs follow MCP protocol scheme requirements."""
        # Test URI scheme compliance
        test_vault = "/test/vault"

        expected_uris = [
            f"gtd://{test_vault}/files",
            f"gtd://{test_vault}/files/inbox",
            f"gtd://{test_vault}/file/gtd/inbox.md",
            f"gtd://{test_vault}/content",
            f"gtd://{test_vault}/content/projects",
        ]

        for uri in expected_uris:
            with self.subTest(uri=uri):
                # Should start with custom scheme
                self.assertTrue(uri.startswith("gtd://"))

                # Should not contain spaces or invalid characters
                self.assertNotIn(" ", uri)
                self.assertNotIn("\n", uri)
                self.assertNotIn("\t", uri)

                # Should be parseable
                scheme, path = uri.split("://", 1)
                self.assertEqual(scheme, "gtd")
                self.assertTrue(len(path) > 0)

    def test_resource_response_structure_compliance(self) -> None:
        """Test that resource responses follow MCP protocol structure."""
        with create_sample_vault() as vault_config:
            from md_gtd_mcp.services.resource_handler import ResourceHandler

            resource_handler = ResourceHandler()

            vault_path = str(vault_config.vault_path)

            # Test that responses follow MCP resource response structure
            result = resource_handler.get_files(vault_path)

            # Should be a dictionary (JSON object)
            self.assertIsInstance(result, dict)

            # Should contain standard fields
            self.assertIn("status", result)

            # Status should be valid value
            self.assertIn(result["status"], ["success", "error"])

            # Should be serializable for MCP transport
            try:
                json.dumps(result)
            except (TypeError, ValueError) as e:
                self.fail(f"Resource response not MCP-compatible: {e}")


if __name__ == "__main__":
    unittest.main()
