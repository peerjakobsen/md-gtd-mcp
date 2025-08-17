"""
Prompt registry system for managing MCP GTD workflow prompts.

This module provides a centralized registry for managing and discovering
MCP prompts that orchestrate GTD workflows through Claude Desktop's intelligence.
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any


@dataclass
class PromptInfo:
    """
    Information about an MCP prompt for GTD workflows.

    This class encapsulates metadata about prompts including their purpose,
    GTD phase alignment, usage patterns, and schema information for optimal
    Claude Desktop integration.
    """

    name: str
    """The unique name of the prompt (used for MCP registration)."""

    description: str
    """Human-readable description of what the prompt does."""

    gtd_phase: str
    """GTD phase this prompt supports: capture, clarify, organize, reflect, engage."""

    usage_frequency: str
    """Expected usage frequency: high, medium, low."""

    tags: list[str]
    """Tags for categorization and discovery (e.g., 'core', 'inbox')."""

    argument_schema: dict[str, str] | None = None
    """Schema definition for prompt arguments (optional)."""

    return_schema: dict[str, str] | None = None
    """Schema definition for expected return format (optional)."""

    examples: list[str] | None = None
    """Example usage scenarios for documentation (optional)."""

    def __post_init__(self) -> None:
        """Validate prompt info after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Prompt name cannot be empty")

        if not self.description or not self.description.strip():
            raise ValueError("Prompt description cannot be empty")

        valid_phases = {"capture", "clarify", "organize", "reflect", "engage"}
        if self.gtd_phase not in valid_phases:
            raise ValueError(f"GTD phase must be one of: {valid_phases}")

        valid_frequencies = {"high", "medium", "low"}
        if self.usage_frequency not in valid_frequencies:
            raise ValueError(f"Usage frequency must be one of: {valid_frequencies}")

        if not self.tags:
            raise ValueError("Prompt must have at least one tag")


class PromptRegistry:
    """
    Centralized registry for managing MCP GTD prompts.

    The registry provides discovery, filtering, and organization capabilities
    for MCP prompts, enabling efficient prompt management and integration
    with FastMCP server infrastructure.
    """

    def __init__(self) -> None:
        """Initialize an empty prompt registry."""
        self._prompts: dict[str, PromptInfo] = {}

    def register(self, prompt_info: PromptInfo) -> None:
        """
        Register a prompt with the registry.

        Args:
            prompt_info: The prompt information to register

        Raises:
            ValueError: If a prompt with the same name is already registered
        """
        if prompt_info.name in self._prompts:
            raise ValueError(f"Prompt '{prompt_info.name}' is already registered")

        self._prompts[prompt_info.name] = prompt_info

    def get_prompt(self, name: str) -> PromptInfo | None:
        """
        Get a specific prompt by name.

        Args:
            name: The name of the prompt to retrieve

        Returns:
            The prompt info if found, None otherwise
        """
        return self._prompts.get(name)

    def get_all_prompts(self) -> list[PromptInfo]:
        """
        Get all registered prompts.

        Returns:
            List of all prompt info objects
        """
        return list(self._prompts.values())

    def get_prompts_by_phase(self, phase: str) -> list[PromptInfo]:
        """
        Get prompts filtered by GTD phase.

        Args:
            phase: The GTD phase to filter by

        Returns:
            List of prompts for the specified phase
        """
        return [
            prompt for prompt in self._prompts.values() if prompt.gtd_phase == phase
        ]

    def get_prompts_by_frequency(self, frequency: str) -> list[PromptInfo]:
        """
        Get prompts filtered by usage frequency.

        Args:
            frequency: The usage frequency to filter by

        Returns:
            List of prompts with the specified frequency
        """
        return [
            prompt
            for prompt in self._prompts.values()
            if prompt.usage_frequency == frequency
        ]

    def get_prompts_by_tag(self, tag: str) -> list[PromptInfo]:
        """
        Get prompts filtered by tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of prompts containing the specified tag
        """
        return [prompt for prompt in self._prompts.values() if tag in prompt.tags]

    def clear(self) -> None:
        """Remove all prompts from the registry."""
        self._prompts.clear()

    def __contains__(self, name: str) -> bool:
        """Check if a prompt with the given name is registered."""
        return name in self._prompts

    def __len__(self) -> int:
        """Get the number of registered prompts."""
        return len(self._prompts)

    def __iter__(self) -> Iterator[PromptInfo]:
        """Iterate over all registered prompts."""
        return iter(self._prompts.values())


class PromptDiscovery:
    """
    Discovery service for finding and organizing prompts by various criteria.

    This class provides advanced discovery capabilities for prompts,
    enabling efficient categorization and filtering for different use cases.
    """

    def __init__(self, registry: PromptRegistry) -> None:
        """
        Initialize discovery service with a prompt registry.

        Args:
            registry: The prompt registry to discover from
        """
        self.registry = registry

    def discover_core_prompts(self) -> list[PromptInfo]:
        """
        Discover core GTD prompts essential for basic workflows.

        Returns:
            List of core prompts tagged with 'core'
        """
        return self.registry.get_prompts_by_tag("core")

    def discover_high_frequency_prompts(self) -> list[PromptInfo]:
        """
        Discover prompts intended for daily or frequent use.

        Returns:
            List of high-frequency prompts
        """
        return self.registry.get_prompts_by_frequency("high")

    def discover_workflow_prompts(self) -> dict[str, list[PromptInfo]]:
        """
        Discover prompts organized by GTD workflow phases.

        Returns:
            Dictionary mapping GTD phases to their associated prompts
        """
        phases = ["capture", "clarify", "organize", "reflect", "engage"]
        return {phase: self.registry.get_prompts_by_phase(phase) for phase in phases}

    def discover_categorization_prompts(self) -> list[PromptInfo]:
        """
        Discover prompts specifically for inbox categorization.

        Returns:
            List of prompts tagged with 'categorization'
        """
        return self.registry.get_prompts_by_tag("categorization")

    def discover_batch_processing_prompts(self) -> list[PromptInfo]:
        """
        Discover prompts designed for batch processing workflows.

        Returns:
            List of prompts tagged with 'batch'
        """
        return self.registry.get_prompts_by_tag("batch")

    def discover_project_prompts(self) -> list[PromptInfo]:
        """
        Discover prompts for project planning and management.

        Returns:
            List of prompts tagged with 'project'
        """
        return self.registry.get_prompts_by_tag("project")

    def discover_review_prompts(self) -> list[PromptInfo]:
        """
        Discover prompts for GTD review processes.

        Returns:
            List of prompts tagged with 'review'
        """
        return self.registry.get_prompts_by_tag("review")

    def get_prompt_summary(self) -> dict[str, Any]:
        """
        Get a comprehensive summary of all registered prompts.

        Returns:
            Dictionary containing prompt statistics and organization
        """
        all_prompts = self.registry.get_all_prompts()

        # Count by phase
        phase_counts = {}
        for phase in ["capture", "clarify", "organize", "reflect", "engage"]:
            phase_counts[phase] = len(self.registry.get_prompts_by_phase(phase))

        # Count by frequency
        frequency_counts = {}
        for frequency in ["high", "medium", "low"]:
            frequency_counts[frequency] = len(
                self.registry.get_prompts_by_frequency(frequency)
            )

        # Collect all unique tags
        all_tags = set()
        for prompt in all_prompts:
            all_tags.update(prompt.tags)

        return {
            "total_prompts": len(all_prompts),
            "prompts_by_phase": phase_counts,
            "prompts_by_frequency": frequency_counts,
            "available_tags": sorted(all_tags),
            "core_prompts": len(self.discover_core_prompts()),
            "categorization_prompts": len(self.discover_categorization_prompts()),
            "batch_prompts": len(self.discover_batch_processing_prompts()),
        }


# Global registry instance for application-wide prompt management
_global_registry = PromptRegistry()


def get_global_registry() -> PromptRegistry:
    """
    Get the global prompt registry instance.

    Returns:
        The global prompt registry
    """
    return _global_registry


def register_core_prompts() -> None:
    """
    Register the core GTD prompts with the global registry.

    This function registers the essential prompts needed for basic
    GTD workflow automation through MCP.
    """
    core_prompts = [
        PromptInfo(
            name="inbox_clarification",
            description=(
                "Analyzes inbox items and suggests GTD categorization with reasoning"
            ),
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["core", "inbox", "categorization"],
            argument_schema={
                "inbox_item": "str",
                "existing_projects": "list[str]",
                "common_contexts": "list[str]",
            },
            return_schema={"categorization": "Categorization"},
            examples=[
                "Process captured thought: 'Schedule dentist appointment'",
                "Categorize meeting note: 'Discuss Q4 budget with finance team'",
            ],
        ),
        PromptInfo(
            name="quick_categorize",
            description=(
                "Fast categorization for obvious inbox items requiring minimal analysis"
            ),
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["core", "quick", "categorization"],
            argument_schema={"inbox_item": "str"},
            return_schema={"categorization": "Categorization"},
            examples=[
                "Quick process: 'Buy milk'",
                "Simple task: 'Call John about meeting'",
            ],
        ),
        PromptInfo(
            name="batch_process_inbox",
            description=(
                "Process multiple inbox items efficiently with grouping and consistency"
            ),
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["core", "batch", "inbox"],
            argument_schema={
                "inbox_items": "list[str]",
                "existing_projects": "list[str]",
                "max_items": "int",
            },
            return_schema={"batch_result": "BatchProcessingResult"},
            examples=[
                "Process 15 meeting notes from today",
                "Batch categorize weekly email captures",
            ],
        ),
    ]

    registry = get_global_registry()
    for prompt in core_prompts:
        registry.register(prompt)


def get_discovery_service() -> PromptDiscovery:
    """
    Get a discovery service for the global prompt registry.

    Returns:
        PromptDiscovery instance for the global registry
    """
    return PromptDiscovery(get_global_registry())
