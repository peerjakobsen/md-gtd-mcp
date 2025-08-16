"""Performance tests for GTD MCP server with realistic large vaults."""

import gc
import tempfile
import time
import tracemalloc
from pathlib import Path

from md_gtd_mcp.models.vault_config import VaultConfig
from md_gtd_mcp.server import (
    list_gtd_files_impl,
    read_gtd_file_impl,
    read_gtd_files_impl,
)
from md_gtd_mcp.services.vault_reader import VaultReader
from md_gtd_mcp.services.vault_setup import setup_gtd_vault


class LargeVaultGenerator:
    """Generate realistic large GTD vaults for performance testing."""

    def __init__(self, vault_path: Path) -> None:
        """Initialize generator with target vault path."""
        self.vault_path = vault_path
        self.gtd_path = vault_path / "gtd"

    def generate_large_vault(self, target_tasks: int = 100) -> dict[str, int]:
        """Generate a large GTD vault with specified number of tasks.

        Args:
          target_tasks: Target number of tasks to generate across all files

        Returns:
          Statistics about the generated vault
        """
        # Ensure GTD structure exists
        setup_gtd_vault(str(self.vault_path))

        # Distribution of tasks across file types
        task_distribution = {
            "inbox": int(target_tasks * 0.25),  # 25% in inbox
            "next-actions": int(target_tasks * 0.35),  # 35% in next-actions
            "projects": int(target_tasks * 0.20),  # 20% in projects
            "waiting-for": int(target_tasks * 0.10),  # 10% waiting-for
            "someday-maybe": int(target_tasks * 0.10),  # 10% someday-maybe
        }

        stats = {}

        # Generate tasks for each file type
        stats["inbox"] = self._generate_inbox_tasks(task_distribution["inbox"])
        stats["next-actions"] = self._generate_next_actions_tasks(
            task_distribution["next-actions"]
        )
        stats["projects"] = self._generate_project_tasks(task_distribution["projects"])
        stats["waiting-for"] = self._generate_waiting_tasks(
            task_distribution["waiting-for"]
        )
        stats["someday-maybe"] = self._generate_someday_tasks(
            task_distribution["someday-maybe"]
        )

        # Generate context-specific tasks (these are included in next-actions count)
        self._generate_context_tasks()

        stats["total_tasks"] = sum(stats.values())
        return stats

    def _generate_inbox_tasks(self, count: int) -> int:
        """Generate inbox tasks with varied complexity."""
        inbox_file = self.gtd_path / "inbox.md"

        tasks = []
        for i in range(count):
            completed = "x" if i % 10 == 0 else " "  # 10% completed
            task_types = [
                f"- [{completed}] Review document #{i:03d} @computer #task",
                f"- [{completed}] Call client about project #{i:03d} @calls #task",
                f"- [{completed}] Research presentation topic #{i:03d} @computer #task",
                f"- [{completed}] Schedule team meeting #{i:03d} @calls #task",
                f"- [{completed}] Buy office supplies #{i:03d} @errands #task",
                f"- [{completed}] Review budget proposal #{i:03d} @computer #task",
                f"- [{completed}] Update documentation #{i:03d} @computer #task",
                f"- [{completed}] Follow up with client #{i:03d} @calls #task",
            ]
            tasks.append(task_types[i % len(task_types)])

        content = f"""---
status: active
tags: [gtd, inbox]
---

# Inbox

## Quick Capture

{chr(10).join(tasks)}

## Ideas and Notes

Generated for performance testing with {count} tasks.
Check [[Project Alpha]] status for next steps.
Review [[Weekly Planning]] template.

"""

        inbox_file.write_text(content, encoding="utf-8")
        return count

    def _generate_next_actions_tasks(self, count: int) -> int:
        """Generate next-actions tasks organized by context."""
        next_actions_file = self.gtd_path / "next-actions.md"

        contexts = ["@computer", "@calls", "@errands", "@home", "@office"]
        tasks_per_context = count // len(contexts)

        sections = []
        for ctx_idx, context in enumerate(contexts):
            context_tasks = []
            for i in range(tasks_per_context):
                task_idx = ctx_idx * tasks_per_context + i
                completed = "x" if task_idx % 15 == 0 else " "  # ~7% completed

                if context == "@computer":
                    task = f"- [{completed}] Update Q{(i % 4) + 1} sheet ⏱️ 30m 🔼 #task"
                elif context == "@calls":
                    task = f"- [{completed}] Follow up #{task_idx:03d} ⏱️ 15m #task"
                elif context == "@errands":
                    task = f"- [{completed}] Pick up #{task_idx:03d} ⏱️ 45m #task"
                elif context == "@home":
                    task = f"- [{completed}] Organize office ⏱️ 60m 💪 #task"
                else:  # @office
                    task = f"- [{completed}] Review #{task_idx:03d} ⏱️ 30m 🔼 #task"

                context_tasks.append(task)

            sections.append(f"## {context.title()}\n\n" + "\n".join(context_tasks))

        content = f"""---
status: active
tags: [gtd, actions]
---

# Next Actions

{chr(10).join(sections)}

## Notes

Generated for performance testing with {count} tasks across {len(contexts)} contexts.

"""

        next_actions_file.write_text(content, encoding="utf-8")
        return count

    def _generate_project_tasks(self, count: int) -> int:
        """Generate project definitions with associated tasks."""
        projects_file = self.gtd_path / "projects.md"

        project_count = max(1, count // 5)  # ~5 tasks per project
        projects: list[str] = []

        for i in range(project_count):
            project_name = f"Project {chr(65 + (i % 26))}{i:02d}"
            project_tasks = []

            tasks_in_project = min(5, count - len(projects) * 5)
            for j in range(tasks_in_project):
                task_idx = i * 5 + j
                completed = "x" if task_idx % 12 == 0 else " "
                project_tasks.append(
                    f"  - [{completed}] Task {j + 1} for {project_name} @computer #task"
                )

            project_section = f"""## {project_name}

**Outcome**: Deliver high-quality {project_name.lower()} by end of quarter
**Status**: active
**Area**: Strategic Initiatives

{chr(10).join(project_tasks)}

"""
            projects.append(project_section)

        content = f"""---
status: active
tags: [gtd, projects]
---

# Projects

{chr(10).join(projects)}

## Notes

Generated for performance testing with {count} tasks across {project_count} projects.

"""

        projects_file.write_text(content, encoding="utf-8")
        return count

    def _generate_waiting_tasks(self, count: int) -> int:
        """Generate waiting-for tasks with delegation info."""
        waiting_file = self.gtd_path / "waiting-for.md"

        people = ["Alice", "Bob", "Carol", "David", "Eve"]
        tasks = []

        for i in range(count):
            person = people[i % len(people)]
            completed = "x" if i % 8 == 0 else " "  # ~12% completed

            task_types = [
                f"- [{completed}] Proposal response 👤 {person} #task",
                f"- [{completed}] Budget approval 👤 {person} #task",
                f"- [{completed}] Tech specs 👤 {person} #task",
                f"- [{completed}] Meeting confirmation 👤 {person} #task",
            ]
            tasks.append(task_types[i % len(task_types)])

        content = f"""---
status: active
tags: [gtd, waiting]
---

# Waiting For

## Pending Responses

{chr(10).join(tasks)}

## Notes

Generated for performance testing with {count} waiting tasks.

"""

        waiting_file.write_text(content, encoding="utf-8")
        return count

    def _generate_someday_tasks(self, count: int) -> int:
        """Generate someday/maybe tasks for future consideration."""
        someday_file = self.gtd_path / "someday-maybe.md"

        tasks = []
        for i in range(count):
            task_types = [
                f"- [ ] Learn new language (Go/Rust) #{i:03d} #task #someday 🪶",
                f"- [ ] Plan European vacation #{i:03d} #task #someday",
                f"- [ ] Reorganize home office #{i:03d} #task #someday 💪",
                f"- [ ] Write blog post series #{i:03d} #task #someday 🔥",
                f"- [ ] Research project tools #{i:03d} #task #someday",
            ]
            tasks.append(task_types[i % len(task_types)])

        content = f"""---
status: active
tags: [gtd, someday]
---

# Someday / Maybe

## Future Projects

{chr(10).join(tasks)}

## Notes

Generated for performance testing with {count} someday/maybe items.

"""

        someday_file.write_text(content, encoding="utf-8")
        return count

    def _generate_context_tasks(self) -> None:
        """Generate context-specific files with query syntax."""
        contexts_dir = self.gtd_path / "contexts"

        context_configs = {
            "@calls.md": ("📞 Calls Context", "description includes @calls"),
            "@computer.md": ("💻 Computer Context", "description includes @computer"),
            "@errands.md": ("🏃 Errands Context", "description includes @errands"),
            "@home.md": ("🏠 Home Context", "description includes @home"),
        }

        for filename, (title, query_filter) in context_configs.items():
            context_file = contexts_dir / filename
            content = f"""# {title}

```tasks
not done
{query_filter}
sort by due
limit 50
```

## Notes

Generated context file for performance testing.

"""
            context_file.write_text(content, encoding="utf-8")


class TestPerformanceWithRealisticGTDVault:
    """Performance tests with realistic GTD vault containing 100+ tasks."""

    def test_performance_with_large_vault(self) -> None:
        """Test performance with realistic GTD vault with 100+ tasks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "large_vault"
            vault_path.mkdir(parents=True)

            # Step 1: Generate larger test fixtures programmatically
            generator = LargeVaultGenerator(vault_path)
            target_tasks = 120  # Slightly over 100 for good measure

            generation_start = time.time()
            vault_stats = generator.generate_large_vault(target_tasks)
            generation_time = time.time() - generation_start

            # Verify we generated the expected number of tasks
            assert vault_stats["total_tasks"] >= 100, (
                f"Expected 100+ tasks, got {vault_stats['total_tasks']}"
            )

            # Validation with performance metrics in assertion messages

            # Step 2: Measure response times for all MCP tools
            vault_config = VaultConfig(vault_path)

            # Test setup_gtd_vault performance (should be fast since files exist)
            setup_start = time.time()
            setup_gtd_vault(str(vault_path))
            setup_time = time.time() - setup_start

            assert setup_time < 1.0, (
                f"setup_gtd_vault took {setup_time:.3f}s, expected < 1.0s"
            )

            # Test list_gtd_files performance
            list_start = time.time()
            file_list = list_gtd_files_impl(str(vault_path), None)["files"]
            list_time = time.time() - list_start

            assert list_time < 2.0, (
                f"list_gtd_files took {list_time:.3f}s, expected < 2.0s. "
                f"Found {len(file_list)} files"
            )
            assert len(file_list) >= 9, f"Expected 9+ files, got {len(file_list)}"

            # Test read_gtd_file performance (single file)
            single_read_start = time.time()
            inbox_content = read_gtd_file_impl(str(vault_path), "gtd/inbox.md")["file"]
            single_read_time = time.time() - single_read_start

            assert single_read_time < 0.5, (
                f"read_gtd_file took {single_read_time:.3f}s, expected < 0.5s. "
                f"Processed {len(inbox_content['tasks'])} tasks"
            )
            assert len(inbox_content["tasks"]) >= 20, (
                "Inbox should have substantial number of tasks"
            )

            # Test read_gtd_files performance (all files)
            batch_read_start = time.time()
            all_content = read_gtd_files_impl(str(vault_path), None)
            batch_read_time = time.time() - batch_read_start

            total_tasks = sum(
                len(file_data["tasks"]) for file_data in all_content["files"]
            )
            assert batch_read_time < 5.0, (
                f"read_gtd_files took {batch_read_time:.3f}s, expected < 5.0s. "
                f"Processed {total_tasks} total tasks"
            )
            assert total_tasks >= 100, f"Expected 100+ total tasks, got {total_tasks}"

            # Step 3: Verify memory usage remains reasonable
            tracemalloc.start()

            # Perform memory-intensive operations
            reader = VaultReader(vault_config)
            all_files = reader.read_all_gtd_files()

            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            # Memory usage should be reasonable (< 50MB for 100+ tasks)
            peak_mb = peak / 1024 / 1024
            assert peak_mb < 50, (
                f"Peak memory usage {peak_mb:.1f}MB exceeded 50MB limit"
            )

            # Step 4: Verify data integrity with large dataset
            file_types = {f.file_type for f in all_files}
            expected_types = {
                "inbox",
                "projects",
                "next-actions",
                "waiting-for",
                "someday-maybe",
                "context",
            }
            assert expected_types.issubset(file_types), "Missing expected file types"

            # Verify task extraction worked correctly
            task_counts = {f.file_type: len(f.tasks) for f in all_files}
            total_extracted_tasks = sum(task_counts.values())

            # Allow some variance due to parsing differences
            performance_summary = (
                f"Performance: gen={generation_time:.3f}s, "
                f"setup={setup_time:.3f}s, list={list_time:.3f}s, "
                f"read={single_read_time:.3f}s, batch={batch_read_time:.3f}s, "
                f"mem={peak_mb:.1f}MB"
            )
            assert abs(total_extracted_tasks - vault_stats["total_tasks"]) <= 10, (
                f"Task extraction mismatch: gen={vault_stats['total_tasks']}, "
                f"extracted={total_extracted_tasks}. "
                f"Counts: {task_counts}. {performance_summary}"
            )

            # Cleanup
            gc.collect()

    def test_performance_scaling_with_context_filtering(self) -> None:
        """Test performance of context-based filtering with large dataset."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir) / "scaling_vault"
            vault_path.mkdir(parents=True)

            # Generate large vault
            generator = LargeVaultGenerator(vault_path)
            generator.generate_large_vault(150)  # Even larger for scaling test

            # Test context filtering performance
            filter_start = time.time()
            context_files = list_gtd_files_impl(str(vault_path), file_type="context")[
                "files"
            ]
            filter_time = time.time() - filter_start

            assert filter_time < 1.0, (
                f"Context filtering took {filter_time:.3f}s, expected < 1.0s. "
                f"Found {len(context_files)} context files"
            )
            assert len(context_files) >= 4, "Should have at least 4 context files"

            # Test reading specific context files
            context_read_start = time.time()
            read_gtd_file_impl(str(vault_path), "gtd/contexts/@computer.md")["file"]
            context_read_time = time.time() - context_read_start

            assert context_read_time < 0.2, (
                f"Context file reading took {context_read_time:.3f}s, expected < 0.2s"
            )
