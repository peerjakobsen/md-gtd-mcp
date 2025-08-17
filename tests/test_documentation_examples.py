"""
Documentation tests for MCP Resource URI examples and usage patterns.

This test suite serves as executable documentation demonstrating all resource
URI patterns and real-world GTD workflow usage examples. Each test verifies
that documented examples work correctly and provides comprehensive coverage
of resource functionality for users and developers.

Test Structure:
- Resource URI Pattern Examples
- GTD Workflow Integration Examples
- Real-world Usage Scenarios
- Error Handling Documentation
- Performance and Best Practice Examples

Note: This file uses print statements for educational/documentation purposes.
"""
# ruff: noqa: T201

import unittest

from md_gtd_mcp.services.resource_handler import ResourceHandler
from tests.fixtures import create_sample_vault


class TestResourceURIPatterns(unittest.TestCase):
    """Test all documented resource URI patterns with comprehensive examples."""

    def test_files_resource_pattern_documentation(self) -> None:
        """
        Document and test: gtd://{vault_path}/files

        Purpose: Lightweight file discovery and vault overview
        Best for: Initial vault exploration, weekly review preparation
        Returns: File metadata without content for quick navigation
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Example 1: Basic vault overview
            result = resource_handler.get_files(vault_path)

            # Verify documented structure
            self.assertIn("status", result)
            self.assertIn("files", result)
            self.assertIn("summary", result)
            self.assertIn("vault_path", result)

            # Document expected file metadata fields
            if result["files"]:
                file_info = result["files"][0]
                expected_fields = ["file_path", "file_type", "task_count", "link_count"]
                for field in expected_fields:
                    self.assertIn(
                        field,
                        file_info,
                        f"File metadata should include '{field}' field",
                    )

            # Document usage context
            print("\n📋 Basic Vault Overview Example:")
            print(f"Resource URI: gtd://{vault_path}/files")
            print("Use Case: 'Show me all GTD files in my vault'")
            print(f"Returns: {result['summary']['total_files']} files with metadata")

    def test_files_filtered_resource_pattern_documentation(self) -> None:
        """
        Document and test: gtd://{vault_path}/files/{file_type}

        Purpose: Type-specific file discovery for focused workflows
        Best for: Phase-specific GTD operations, targeted reviews
        Supports: inbox, projects, next-actions, waiting-for, someday-maybe, context
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Example 1: Inbox-focused workflow
            inbox_result = resource_handler.get_files(vault_path, "inbox")

            # Example 2: Project review preparation
            projects_result = resource_handler.get_files(vault_path, "projects")

            # Example 3: Context-based planning
            context_result = resource_handler.get_files(vault_path, "context")

            # Verify filtering works correctly
            for result in [inbox_result, projects_result, context_result]:
                self.assertIn("status", result)
                self.assertIn("files", result)

            # Document GTD phase mapping
            gtd_phase_examples = {
                "inbox": "Clarify phase - Process captured items",
                "projects": "Reflect phase - Weekly project review",
                "next-actions": "Engage phase - Daily action planning",
                "context": "Engage phase - Context-based task selection",
                "waiting-for": "Reflect phase - Follow-up tracking",
                "someday-maybe": "Reflect phase - Future possibilities review",
            }

            print("\n🎯 Filtered File Discovery Examples:")
            for file_type, description in gtd_phase_examples.items():
                print(f"Resource URI: gtd://{vault_path}/files/{file_type}")
                print(f"GTD Context: {description}")

    def test_file_resource_pattern_documentation(self) -> None:
        """
        Document and test: gtd://{vault_path}/file/{file_path}

        Purpose: Complete single file analysis with full content
        Best for: Detailed task processing, comprehensive file review
        Returns: Full content, frontmatter, tasks, links with metadata
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Example 1: Inbox item analysis
            inbox_file = "gtd/inbox.md"
            inbox_result = resource_handler.get_file(vault_path, inbox_file)

            # Verify comprehensive file data structure
            self.assertIn("status", inbox_result)
            self.assertIn("file", inbox_result)

            if inbox_result["file"]:
                file_data = inbox_result["file"]
                expected_sections = ["content", "frontmatter", "tasks", "links"]
                for section in expected_sections:
                    self.assertIn(
                        section,
                        file_data,
                        f"File data should include '{section}' section",
                    )

                # Document task structure for GTD processing
                if file_data["tasks"]:
                    task = file_data["tasks"][0]
                    task_fields = [
                        "description",
                        "completed",
                        "line_number",
                        "raw_text",
                    ]
                    for field in task_fields:
                        self.assertIn(
                            field, task, f"Task should include '{field}' field"
                        )

            print("\n📄 Single File Analysis Examples:")
            print(f"Resource URI: gtd://{vault_path}/file/{inbox_file}")
            print("Use Case: 'Analyze my inbox file for processing'")
            print("GTD Phase: Clarify - Detailed item review")

    def test_content_resource_pattern_documentation(self) -> None:
        """
        Document and test: gtd://{vault_path}/content

        Purpose: Complete vault analysis with all file content
        Best for: Weekly reviews, comprehensive system analysis
        Returns: All files with complete content, tasks, and links
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Example: Comprehensive weekly review
            result = resource_handler.get_content(vault_path)

            # Verify comprehensive content structure
            self.assertIn("status", result)
            self.assertIn("files", result)
            self.assertIn("summary", result)

            # Document summary statistics for weekly reviews
            if "summary" in result:
                summary = result["summary"]
                review_metrics = [
                    "total_files",
                    "total_tasks",
                    "completed_tasks",
                    "total_links",
                ]
                for metric in review_metrics:
                    if metric in summary:
                        print(f"Weekly Review Metric - {metric}: {summary[metric]}")

            print("\n📊 Complete Vault Analysis Example:")
            print(f"Resource URI: gtd://{vault_path}/content")
            print("Use Case: 'Generate comprehensive weekly review'")
            print("GTD Phase: Reflect - Complete system review")

    def test_content_filtered_resource_pattern_documentation(self) -> None:
        """
        Document and test: gtd://{vault_path}/content/{file_type}

        Purpose: Focused comprehensive analysis by file type
        Best for: Category-specific reviews, targeted processing
        Combines: Filtering + complete content analysis
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Example 1: Project portfolio review
            projects_content = resource_handler.get_content(vault_path, "projects")

            # Example 2: Inbox processing session
            inbox_content = resource_handler.get_content(vault_path, "inbox")

            # Verify filtered comprehensive data
            for result in [projects_content, inbox_content]:
                self.assertIn("status", result)
                self.assertIn("files", result)

                # Each file should have complete content
                if result["files"]:
                    file_data = result["files"][0]
                    content_sections = ["content", "tasks", "links"]
                    for section in content_sections:
                        self.assertIn(section, file_data)

            # Document category-specific workflow patterns
            workflow_patterns = {
                "projects": {
                    "frequency": "Weekly",
                    "purpose": "Project portfolio review and next action planning",
                    "typical_actions": [
                        "Update project status",
                        "Identify next actions",
                        "Review milestones",
                    ],
                },
                "inbox": {
                    "frequency": "Daily",
                    "purpose": "Process captured items and clarify actions",
                    "typical_actions": [
                        "Categorize items",
                        "Assign contexts",
                        "Create projects",
                    ],
                },
                "next-actions": {
                    "frequency": "Daily",
                    "purpose": "Select and prioritize immediate actions",
                    "typical_actions": [
                        "Choose context",
                        "Estimate time/energy",
                        "Sequence tasks",
                    ],
                },
            }

            print("\n🔍 Filtered Content Analysis Examples:")
            for file_type, pattern in workflow_patterns.items():
                print(f"Resource URI: gtd://{vault_path}/content/{file_type}")
                print(f"Frequency: {pattern['frequency']}")
                print(f"Purpose: {pattern['purpose']}")


class TestGTDWorkflowIntegration(unittest.TestCase):
    """Document real-world GTD workflow integration with resource patterns."""

    def test_capture_to_clarify_workflow_documentation(self) -> None:
        """
        Document: Capture → Clarify workflow using resources

        Scenario: User has captured thoughts and needs to process them
        Resources: Files listing → File content → Content analysis
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Step 1: Discover inbox files for processing
            inbox_files = resource_handler.get_files(vault_path, "inbox")

            # Step 2: Read specific inbox file for detailed analysis
            if inbox_files["files"]:
                inbox_file_path = inbox_files["files"][0]["file_path"]
                _inbox_content = resource_handler.get_file(vault_path, inbox_file_path)

                # Step 3: Analyze all inbox content for batch processing
                _all_inbox_content = resource_handler.get_content(vault_path, "inbox")

                print("\n🔄 Capture → Clarify Workflow:")
                print(f"1. Discover: gtd://{vault_path}/files/inbox")
                print(f"2. Analyze: gtd://{vault_path}/file/{inbox_file_path}")
                print(f"3. Process: gtd://{vault_path}/content/inbox")
                print("GTD Principle: Process inbox items from capture to actionable")

    def test_weekly_review_workflow_documentation(self) -> None:
        """
        Document: Weekly Review workflow using comprehensive resources

        Scenario: Systematic review of entire GTD system
        Resources: Complete content → Category analysis → Project review
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Step 1: Complete system overview
            _complete_system = resource_handler.get_content(vault_path)

            # Step 2: Category-specific reviews
            categories = ["projects", "next-actions", "waiting-for", "someday-maybe"]
            category_reviews = {}

            for category in categories:
                category_reviews[category] = resource_handler.get_content(
                    vault_path, category
                )

            print("\n📅 Weekly Review Workflow:")
            print(f"1. System Overview: gtd://{vault_path}/content")
            print("2. Category Reviews:")
            for category in categories:
                print(f"   - {category.title()}: gtd://{vault_path}/content/{category}")
            print("GTD Principle: Comprehensive review ensures system trustworthiness")

    def test_context_based_engagement_documentation(self) -> None:
        """
        Document: Context-based task selection using filtered resources

        Scenario: User wants to work on tasks for current context
        Resources: Context discovery → Next actions → Specific context tasks
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Step 1: Discover available contexts
            _context_files = resource_handler.get_files(vault_path, "context")

            # Step 2: Get all next actions for context selection
            _next_actions = resource_handler.get_content(vault_path, "next-actions")

            print("\n🎯 Context-Based Engagement:")
            print(f"1. Context Discovery: gtd://{vault_path}/files/context")
            print(f"2. Action Selection: gtd://{vault_path}/content/next-actions")
            print("GTD Principle: Choose actions based on context, time, and energy")


class TestErrorHandlingDocumentation(unittest.TestCase):
    """Document error handling patterns and troubleshooting guidance."""

    def test_missing_vault_documentation(self) -> None:
        """Document behavior with missing or invalid vault paths."""
        resource_handler = ResourceHandler()
        invalid_vault = "/nonexistent/vault/path"

        # Test all resource patterns with invalid vault
        result = resource_handler.get_files(invalid_vault)

        # Document expected error response structure
        self.assertIn("status", result)
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)

        print("\n⚠️ Missing Vault Error Handling:")
        print(f"Resource URI: gtd://{invalid_vault}/files")
        print(f"Response: {result['status']} - {result.get('error', 'No vault found')}")
        print("Guidance: Check vault path or run setup_gtd_vault tool")

    def test_missing_file_documentation(self) -> None:
        """Document behavior with missing GTD files."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            resource_handler = ResourceHandler()
            vault_path = tmp_dir
            missing_file = "GTD/nonexistent.md"

            result = resource_handler.get_file(vault_path, missing_file)

            print("\n📄 Missing File Error Handling:")
            print(f"Resource URI: gtd://{vault_path}/file/{missing_file}")
            print(f"Response: {result.get('status', 'error')}")
            print("Guidance: Verify file path or use files resource for discovery")


class TestPerformanceAndBestPractices(unittest.TestCase):
    """Document performance characteristics and usage best practices."""

    def test_resource_selection_guidance(self) -> None:
        """Document when to use each resource type for optimal performance."""

        performance_guide = {
            "gtd://{vault}/files": {
                "purpose": "Quick file discovery",
                "performance": "Fastest - metadata only",
                "best_for": "Initial exploration, file counts",
                "avoid_for": "Content analysis, task processing",
            },
            "gtd://{vault}/files/{type}": {
                "purpose": "Filtered file discovery",
                "performance": "Fast - filtered metadata",
                "best_for": "Category-specific navigation",
                "avoid_for": "Cross-category analysis",
            },
            "gtd://{vault}/file/{path}": {
                "purpose": "Single file analysis",
                "performance": "Medium - full parsing",
                "best_for": "Detailed item review",
                "avoid_for": "Bulk processing multiple files",
            },
            "gtd://{vault}/content": {
                "purpose": "Complete system analysis",
                "performance": "Slowest - all content",
                "best_for": "Weekly reviews, comprehensive analysis",
                "avoid_for": "Quick checks, frequent polling",
            },
            "gtd://{vault}/content/{type}": {
                "purpose": "Filtered comprehensive analysis",
                "performance": "Medium-slow - filtered content",
                "best_for": "Category-specific processing",
                "avoid_for": "Simple file discovery",
            },
        }

        print("\n⚡ Resource Selection Performance Guide:")
        for pattern, guide in performance_guide.items():
            print(f"\n{pattern}:")
            print(f"  Purpose: {guide['purpose']}")
            print(f"  Performance: {guide['performance']}")
            print(f"  Best for: {guide['best_for']}")
            print(f"  Avoid for: {guide['avoid_for']}")

    def test_caching_and_idempotency_documentation(self) -> None:
        """Document caching behavior and idempotency guarantees."""
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            # Demonstrate idempotency - multiple calls return same result
            first_call = resource_handler.get_files(vault_path)
            second_call = resource_handler.get_files(vault_path)

            # Results should be identical for caching optimization
            self.assertEqual(first_call, second_call)

            print("\n🔄 Caching and Idempotency:")
            print(
                "All resources are idempotent - repeated calls return identical results"
            )
            print("MCP clients can safely cache resource responses")
            print("readOnlyHint: true - resources never modify data")
            print("idempotentHint: true - safe for aggressive caching")


class TestRealWorldScenarios(unittest.TestCase):
    """Document complete real-world usage scenarios with multiple resources."""

    def test_new_user_onboarding_scenario(self) -> None:
        """
        Scenario: New user exploring GTD system for first time
        Goal: Understand vault structure and available content
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            print("\n👋 New User Onboarding Scenario:")

            # Step 1: Get overview of available files
            files_overview = resource_handler.get_files(vault_path)
            print(f"1. Vault Overview: gtd://{vault_path}/files")
            files_count = files_overview.get("total_count", 0)
            print(f"   Result: {files_count} GTD files discovered")

            # Step 2: Explore each category to understand structure
            categories = ["inbox", "projects", "next-actions", "context"]
            for category in categories:
                category_files = resource_handler.get_files(vault_path, category)
                count = len(category_files.get("files", []))
                print(
                    f"2.{categories.index(category) + 1} {category.title()}: gtd://{vault_path}/files/{category}"
                )
                print(f"     Found: {count} {category} files")

    def test_daily_review_scenario(self) -> None:
        """
        Scenario: Daily review and task selection
        Goal: Quick review and context-based task selection
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            print("\n☀️ Daily Review Scenario:")

            # Step 1: Quick inbox check
            inbox_files = resource_handler.get_files(vault_path, "inbox")
            inbox_count = len(inbox_files.get("files", []))
            print(f"1. Inbox Check: gtd://{vault_path}/files/inbox")
            print(f"   Items to process: {inbox_count}")

            # Step 2: Review next actions for current context
            next_actions = resource_handler.get_content(vault_path, "next-actions")
            action_count = sum(
                len(f.get("tasks", [])) for f in next_actions.get("files", [])
            )
            print(f"2. Available Actions: gtd://{vault_path}/content/next-actions")
            print(f"   Ready actions: {action_count}")

    def test_project_planning_scenario(self) -> None:
        """
        Scenario: Project planning and decomposition
        Goal: Review project status and plan next steps
        """
        with create_sample_vault() as vault_config:
            resource_handler = ResourceHandler()
            vault_path = str(vault_config.vault_path)

            print("\n🎯 Project Planning Scenario:")

            # Step 1: Get project portfolio overview
            project_files = resource_handler.get_files(vault_path, "projects")
            print(f"1. Project Portfolio: gtd://{vault_path}/files/projects")
            print(f"   Active projects: {len(project_files.get('files', []))}")

            # Step 2: Detailed project analysis
            projects_content = resource_handler.get_content(vault_path, "projects")
            total_tasks = sum(
                len(f.get("tasks", [])) for f in projects_content.get("files", [])
            )
            print(f"2. Project Details: gtd://{vault_path}/content/projects")
            print(f"   Total project tasks: {total_tasks}")

    def test_troubleshooting_scenario(self) -> None:
        """
        Scenario: Troubleshooting common issues
        Goal: Provide guidance for common problems
        """
        print("\n🔧 Troubleshooting Common Issues:")

        troubleshooting_guide = {
            "No files found": {
                "resource": "gtd://vault/files",
                "likely_cause": "Vault not set up or wrong path",
                "solution": "Run setup_gtd_vault tool or verify vault path",
            },
            "Empty content": {
                "resource": "gtd://vault/content",
                "likely_cause": "No GTD files or empty files",
                "solution": "Add content to GTD files or run setup for templates",
            },
            "Missing file type": {
                "resource": "gtd://vault/files/inbox",
                "likely_cause": "No files of specified type",
                "solution": "Create files of that type or check file naming",
            },
            "Slow performance": {
                "resource": "gtd://vault/content",
                "likely_cause": "Large vault or many files",
                "solution": "Use filtered resources or file-specific access",
            },
        }

        for issue, guide in troubleshooting_guide.items():
            print(f"\nIssue: {issue}")
            print(f"  Resource: {guide['resource']}")
            print(f"  Likely Cause: {guide['likely_cause']}")
            print(f"  Solution: {guide['solution']}")
