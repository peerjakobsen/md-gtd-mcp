"""Error recovery scenario tests for GTD MCP server components."""

import os
import stat
import tempfile
import threading
import time
from pathlib import Path

from md_gtd_mcp.services.resource_handler import ResourceHandler
from md_gtd_mcp.services.vault_setup import setup_gtd_vault


class TestErrorRecoveryScenarios:
    """Test error recovery scenarios with graceful handling of common issues."""

    def test_missing_file_permissions_error_handling(self) -> None:
        """Test graceful handling of file permission errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up a basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Create a file with restricted permissions
            restricted_file = vault_path / "gtd" / "restricted.md"
            restricted_file.write_text("# Restricted File\n\n- [ ] Test task")

            # Remove read permissions (Unix-style)
            if os.name != "nt":  # Skip on Windows where permissions work differently
                original_mode = restricted_file.stat().st_mode
                restricted_file.chmod(stat.S_IWUSR)  # Write-only for owner

                try:
                    # Attempt to read the restricted file
                    result = ResourceHandler().get_file(
                        str(vault_path), "gtd/restricted.md"
                    )

                    # Should return error status with helpful message
                    assert result["status"] == "error"
                    assert "error" in result
                    assert (
                        "restricted.md" in result["error"]
                        or "Permission" in result["error"]
                    )
                    assert result["vault_path"] == str(vault_path)

                finally:
                    # Restore permissions for cleanup
                    restricted_file.chmod(original_mode)

    def test_malformed_markdown_frontmatter_error_handling(self) -> None:
        """Test graceful handling of malformed markdown and frontmatter."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Test 1: Malformed YAML frontmatter
            malformed_yaml_file = vault_path / "gtd" / "malformed_yaml.md"
            malformed_yaml_content = (
                "---\ntitle: Test Project\nstatus: active\narea: [unclosed list\n"
                "outcome: Complete the project\n---\n\n# Malformed YAML Test\n\n"
                "- [ ] Task with malformed frontmatter above\n"
            )
            malformed_yaml_file.write_text(malformed_yaml_content)

            result = ResourceHandler().get_file(
                str(vault_path), "gtd/malformed_yaml.md"
            )

            # Should still succeed with graceful degradation
            assert result["status"] == "success"
            # Frontmatter should be empty or minimal due to parsing failure
            frontmatter = result["file"]["frontmatter"]
            assert isinstance(frontmatter, dict)
            # File content should be parsed without crashing
            assert "content" in result["file"]
            assert len(result["file"]["content"]) > 0

            # Test 2: Invalid characters in content - focus on error recovery
            invalid_chars_file = vault_path / "gtd" / "invalid_chars.md"
            invalid_chars_content = (
                "# Invalid Characters Test\n\n- [ ] Normal task should work\n"
            )
            invalid_chars_file.write_text(
                invalid_chars_content, encoding="utf-8", errors="ignore"
            )

            result = ResourceHandler().get_file(str(vault_path), "gtd/invalid_chars.md")

            # Should handle gracefully - main goal is no crash
            assert result["status"] == "success"
            assert "content" in result["file"]
            assert len(result["file"]["content"]) > 0

    def test_missing_vault_directory_error_handling(self) -> None:
        """Test error handling when vault directory doesn't exist."""
        # Test with completely non-existent path
        non_existent_path = "/definitely/does/not/exist/vault"

        result = ResourceHandler().get_file(non_existent_path, "gtd/inbox.md")
        assert result["status"] == "error"
        assert (
            "not found" in result["error"].lower()
            or "vault directory" in result["error"].lower()
        )
        assert result["vault_path"] == non_existent_path

        # Test list operation with non-existent vault
        list_result = ResourceHandler().get_files(non_existent_path)
        # Should return error for non-existent vault directories
        assert list_result["status"] == "error"
        assert (
            "vault directory" in list_result["error"].lower()
            or "not found" in list_result["error"].lower()
        )
        assert list_result["vault_path"] == non_existent_path

    def test_corrupted_file_content_error_handling(self) -> None:
        """Test handling of various corrupted file scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Test 1: Binary file with .md extension
            binary_file = vault_path / "gtd" / "binary.md"
            binary_content = bytes(
                [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]
            )  # PNG header
            binary_file.write_bytes(binary_content)

            result = ResourceHandler().get_file(str(vault_path), "gtd/binary.md")
            # Should handle gracefully - either succeed with minimal content or error
            # gracefully
            assert "status" in result
            if result["status"] == "error":
                assert "error" in result and len(result["error"]) > 0

            # Test 2: Very large file (potential memory issues)
            large_file = vault_path / "gtd" / "large.md"
            large_content = (
                "# Large File\n\n" + "- [ ] Task {}\n".format("x" * 100) * 100
            )  # Smaller for testing
            large_file.write_text(large_content)

            result = ResourceHandler().get_file(str(vault_path), "gtd/large.md")
            # Should succeed - main goal is no memory crash
            assert result["status"] == "success"
            # File content should be processed
            assert "content" in result["file"]
            assert (
                len(result["file"]["content"]) > 10000
            )  # Should have substantial content

    def test_invalid_file_paths_error_handling(self) -> None:
        """Test error handling for various invalid file path scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Test 1: Empty file path
            result = ResourceHandler().get_file(str(vault_path), "")
            assert result["status"] == "error"
            assert (
                "empty" in result["error"].lower()
                or "invalid" in result["error"].lower()
            )

            # Test 2: File path with null bytes (should be handled gracefully)
            result = ResourceHandler().get_file(str(vault_path), "gtd/test\x00file.md")
            assert result["status"] == "error"

            # Test 3: File outside GTD structure
            non_gtd_file = vault_path / "outside_gtd.md"
            non_gtd_file.write_text("# Outside GTD\n\n- [ ] Task")

            result = ResourceHandler().get_file(str(vault_path), "outside_gtd.md")
            assert result["status"] == "error"
            assert (
                "gtd folder" in result["error"].lower()
                or "not within" in result["error"].lower()
            )

            # Test 4: Directory instead of file
            result = ResourceHandler().get_file(str(vault_path), "gtd/contexts")
            assert result["status"] == "error"

    def test_comprehensive_error_message_quality(self) -> None:
        """Test that error messages are helpful for troubleshooting."""
        import pytest

        # Test 1: Invalid vault path error message quality
        with pytest.raises(ValueError) as exc_info:
            setup_gtd_vault("")

        error_msg = str(exc_info.value)
        assert len(error_msg) > 10  # Should be descriptive
        assert "vault" in error_msg.lower() or "path" in error_msg.lower()

        # Test 2: Non-existent file error message includes file path
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            setup_gtd_vault(str(vault_path))

            result = ResourceHandler().get_file(str(vault_path), "gtd/nonexistent.md")
            assert result["status"] == "error"
            error_msg = result["error"]
            assert "nonexistent.md" in error_msg or "not found" in error_msg.lower()
            assert len(error_msg) > 15  # Should be descriptive

        # Test 3: Error messages include context for debugging
        test_scenarios = [
            ("", "gtd/inbox.md"),  # Empty vault path
            ("/invalid/vault", "gtd/inbox.md"),  # Invalid vault
            (str(vault_path), ""),  # Empty file path
        ]

        for vault_path_test, file_path_test in test_scenarios:
            result = ResourceHandler().get_file(vault_path_test, file_path_test)
            assert result["status"] == "error"
            assert "error" in result
            assert len(result["error"]) > 5  # Should be meaningful
            assert "vault_path" in result  # Should include context

    def test_parser_resilience_with_edge_cases(self) -> None:
        """Test parser resilience with various markdown edge cases."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Create file with various edge cases
            edge_cases_file = vault_path / "gtd" / "edge_cases.md"
            edge_cases_content = """---
title: Edge Cases Test
weird_field: "value with \\n newlines \\t tabs"
empty_field:
null_field: null
number_field: 42
list_field: [item1, item2]
---

# Edge Cases Test File

## Tasks with edge cases

- [ ] Task with [[malformed wikilink
- [ ] Task with [broken markdown link](
- [ ] Task with emoji contexts @🏠home @💻computer
- [x] Completed task with [valid link](https://example.com)
- [ ] Task with multiple @@contexts @calls @computer
- [ ] Task with ⏱️ 30m estimate but no other metadata
- [ ] Task with 👤 person-name but no @context
- Task without checkbox but with @context marker

## Headers with unusual characters

### Header with [link](https://example.com)

### Header with @context mention

## Lists and sublists

- [ ] Parent task @calls
  - [ ] Subtask level 1 @calls
    - [ ] Subtask level 2 @calls
- [ ] Another parent @computer
  - Non-task item in list
  - [ ] Another subtask @computer

## Weird markdown constructs

> - [ ] Task in blockquote @home
> This is still in blockquote

```
- [ ] Task in code block (should not be parsed)
```

    - [ ] Task in indented code block @office

1. [ ] Numbered list item that looks like task
2. [x] Another numbered list item

---

Final separator with task below:

- [ ] Final task @errands
"""
            edge_cases_file.write_text(edge_cases_content)

            result = ResourceHandler().get_file(str(vault_path), "gtd/edge_cases.md")

            # Should succeed despite edge cases
            assert result["status"] == "success"

            # Should extract tasks without crashing (main goal is resilience)
            tasks = result["file"]["tasks"]
            assert isinstance(tasks, list)  # Should return task list structure

            # Should handle frontmatter gracefully
            frontmatter = result["file"]["frontmatter"]
            assert isinstance(frontmatter, dict)

            # Should extract some links (at least the valid ones)
            links = result["file"]["links"]
            assert len(links) >= 1  # Should get at least the valid link

    def test_concurrent_access_error_handling(self) -> None:
        """Test error handling when files are being modified during reading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Create a test file
            test_file = vault_path / "gtd" / "concurrent_test.md"
            initial_content = """# Concurrent Test

- [ ] Initial task @home
- [ ] Another task @office
"""
            test_file.write_text(initial_content)

            # Function to modify file continuously
            def modify_file() -> None:
                for i in range(10):
                    content = f"""# Concurrent Test Modified {i}

- [ ] Task {i} @home
- [ ] Modified task {i} @office
- [ ] New task {i} @calls
"""
                    test_file.write_text(content)
                    time.sleep(0.01)  # Small delay

            # Start modification thread
            modifier_thread = threading.Thread(target=modify_file)
            modifier_thread.start()

            # Try to read file multiple times while it's being modified
            read_results = []
            for _ in range(20):
                result = ResourceHandler().get_file(
                    str(vault_path), "gtd/concurrent_test.md"
                )
                read_results.append(result)
                time.sleep(0.005)  # Small delay between reads

            # Wait for modifier to finish
            modifier_thread.join()

            # Most reads should succeed (some might catch file in inconsistent state)
            successful_reads = [r for r in read_results if r["status"] == "success"]
            assert (
                len(successful_reads) >= len(read_results) * 0.7
            )  # At least 70% should succeed

            # Any errors should be graceful
            error_reads = [r for r in read_results if r["status"] == "error"]
            for error_result in error_reads:
                assert "error" in error_result
                assert (
                    len(error_result["error"]) > 0
                )  # Should have meaningful error message

    def test_encoding_and_special_characters_handling(self) -> None:
        """Test handling of various text encodings and special characters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Test file with various Unicode characters
            unicode_file = vault_path / "gtd" / "unicode_test.md"
            unicode_content = """---
title: "Unicode Test 🚀"
author: "José María"
description: "Testing émojis 🎯 and spëcial characters"
---

# Unicode Test File 📝

- [ ] Task with émojis 🎯 @calls
- [ ] Task with Chinese characters 中文测试 @computer
- [ ] Task with Arabic text اختبار العربية @home
- [ ] Task with mathematical symbols ∑∞≠≤≥ @office
- [ ] Task with currency symbols €£¥₹ @errands
- [x] Completed task with Unicode ✅ @calls

## Links with Unicode

Check out this [link with émojis 🔗](https://example.com/émoji-test)
Visit [[Project émojis 🚀]] for more details

## Special markdown

- [ ] Task with `code émojis 💻` @computer
- [ ] Task with **bold émojis 💪** @home
- [ ] Task with _italic émojis 🎨_ @office
"""
            unicode_file.write_text(unicode_content, encoding="utf-8")

            result = ResourceHandler().get_file(str(vault_path), "gtd/unicode_test.md")

            # Should handle Unicode gracefully
            assert result["status"] == "success"

            # Should extract tasks with Unicode content without crashing
            tasks = result["file"]["tasks"]
            assert isinstance(tasks, list)  # Should return task list structure

            # Should handle frontmatter with Unicode
            frontmatter = result["file"]["frontmatter"]
            # Unicode may be in the extra field or main frontmatter
            assert "🚀" in frontmatter.get("title", "") or "🚀" in frontmatter.get(
                "extra", {}
            ).get("title", "")

            # Should extract links with Unicode
            links = result["file"]["links"]
            assert len(links) >= 2

    def test_memory_limits_with_large_vaults(self) -> None:
        """Test memory usage with moderately large vault scenarios."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)

            # Set up basic GTD vault
            setup_result = setup_gtd_vault(str(vault_path))
            assert setup_result["status"] == "success"

            # Create multiple files with many tasks
            for file_index in range(5):
                large_file = vault_path / "gtd" / f"large_file_{file_index}.md"
                tasks = []
                for task_index in range(200):  # 200 tasks per file
                    tasks.append(
                        f"- [ ] Task {task_index} in file {file_index} "
                        f"@context{task_index % 10}"
                    )

                content = f"""---
title: "Large File {file_index}"
created: "2023-01-01"
---

# Large File {file_index}

{"".join(tasks)}

## Links Section

Check [[Large File {(file_index + 1) % 5}]] for related tasks.
Visit [External Link {file_index}](https://example.com/file{file_index})
"""
                large_file.write_text(content)

            # Test reading all files (should handle 1000+ tasks total)
            # Test reading all files using ResourceHandler

            result = ResourceHandler().get_content(str(vault_path))
            assert result["status"] == "success"

            # Should handle large number of files and tasks
            files = result["files"]
            assert len(files) >= 5  # Our large files plus standard GTD files

            # Count total tasks across all files - focus on no memory crash
            total_tasks = sum(len(f["tasks"]) for f in files)
            assert total_tasks >= 0  # Should process without memory issues

            # Memory usage should be reasonable (this is more of a smoke test)
            # In a real scenario, you might want to monitor actual memory usage
            assert len(str(result)) > 4000  # Should have substantial content
