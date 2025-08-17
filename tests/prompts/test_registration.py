"""Tests for MCP prompt registration system."""

import pytest

from md_gtd_mcp.prompts.registry import PromptInfo, PromptRegistry


class TestPromptRegistry:
    """Test the PromptRegistry for managing MCP prompts."""

    def test_registry_creation(self) -> None:
        """Test creating a new prompt registry."""
        registry = PromptRegistry()
        assert registry.get_all_prompts() == []
        assert len(registry) == 0

    def test_register_prompt(self) -> None:
        """Test registering a prompt with the registry."""
        registry = PromptRegistry()

        prompt_info = PromptInfo(
            name="inbox_clarification",
            description="Analyzes inbox items for GTD categorization",
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["categorization", "inbox", "gtd"],
        )

        registry.register(prompt_info)

        assert len(registry) == 1
        assert registry.get_prompt("inbox_clarification") == prompt_info
        assert "inbox_clarification" in registry

    def test_register_duplicate_prompt_raises_error(self) -> None:
        """Test that registering duplicate prompt names raises an error."""
        registry = PromptRegistry()

        prompt_info = PromptInfo(
            name="test_prompt",
            description="Test prompt",
            gtd_phase="capture",
            usage_frequency="medium",
            tags=["test"],
        )

        registry.register(prompt_info)

        # Attempt to register same name again
        duplicate_prompt = PromptInfo(
            name="test_prompt",
            description="Duplicate test prompt",
            gtd_phase="organize",
            usage_frequency="low",
            tags=["duplicate"],
        )

        with pytest.raises(ValueError) as exc_info:
            registry.register(duplicate_prompt)
        assert "Prompt 'test_prompt' is already registered" in str(exc_info.value)

    def test_get_nonexistent_prompt_returns_none(self) -> None:
        """Test that getting a non-existent prompt returns None."""
        registry = PromptRegistry()
        assert registry.get_prompt("nonexistent") is None

    def test_get_all_prompts(self) -> None:
        """Test getting all registered prompts."""
        registry = PromptRegistry()

        prompt1 = PromptInfo(
            name="prompt1",
            description="First prompt",
            gtd_phase="capture",
            usage_frequency="high",
            tags=["first"],
        )

        prompt2 = PromptInfo(
            name="prompt2",
            description="Second prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["second"],
        )

        registry.register(prompt1)
        registry.register(prompt2)

        all_prompts = registry.get_all_prompts()
        assert len(all_prompts) == 2
        assert prompt1 in all_prompts
        assert prompt2 in all_prompts

    def test_get_prompts_by_phase(self) -> None:
        """Test filtering prompts by GTD phase."""
        registry = PromptRegistry()

        capture_prompt = PromptInfo(
            name="capture_prompt",
            description="Capture phase prompt",
            gtd_phase="capture",
            usage_frequency="high",
            tags=["capture"],
        )

        clarify_prompt = PromptInfo(
            name="clarify_prompt",
            description="Clarify phase prompt",
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["clarify"],
        )

        organize_prompt = PromptInfo(
            name="organize_prompt",
            description="Organize phase prompt",
            gtd_phase="organize",
            usage_frequency="medium",
            tags=["organize"],
        )

        registry.register(capture_prompt)
        registry.register(clarify_prompt)
        registry.register(organize_prompt)

        clarify_prompts = registry.get_prompts_by_phase("clarify")
        assert len(clarify_prompts) == 1
        assert clarify_prompts[0] == clarify_prompt

        capture_prompts = registry.get_prompts_by_phase("capture")
        assert len(capture_prompts) == 1
        assert capture_prompts[0] == capture_prompt

    def test_get_prompts_by_frequency(self) -> None:
        """Test filtering prompts by usage frequency."""
        registry = PromptRegistry()

        high_freq_prompt = PromptInfo(
            name="high_freq",
            description="High frequency prompt",
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["frequent"],
        )

        low_freq_prompt = PromptInfo(
            name="low_freq",
            description="Low frequency prompt",
            gtd_phase="reflect",
            usage_frequency="low",
            tags=["infrequent"],
        )

        registry.register(high_freq_prompt)
        registry.register(low_freq_prompt)

        high_frequency_prompts = registry.get_prompts_by_frequency("high")
        assert len(high_frequency_prompts) == 1
        assert high_frequency_prompts[0] == high_freq_prompt

    def test_get_prompts_by_tag(self) -> None:
        """Test filtering prompts by tags."""
        registry = PromptRegistry()

        inbox_prompt = PromptInfo(
            name="inbox_prompt",
            description="Inbox processing prompt",
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["inbox", "categorization"],
        )

        project_prompt = PromptInfo(
            name="project_prompt",
            description="Project planning prompt",
            gtd_phase="organize",
            usage_frequency="medium",
            tags=["project", "planning"],
        )

        review_prompt = PromptInfo(
            name="review_prompt",
            description="Review prompt",
            gtd_phase="reflect",
            usage_frequency="low",
            tags=["review", "categorization"],
        )

        registry.register(inbox_prompt)
        registry.register(project_prompt)
        registry.register(review_prompt)

        categorization_prompts = registry.get_prompts_by_tag("categorization")
        assert len(categorization_prompts) == 2
        assert inbox_prompt in categorization_prompts
        assert review_prompt in categorization_prompts

    def test_clear_registry(self) -> None:
        """Test clearing all prompts from registry."""
        registry = PromptRegistry()

        prompt = PromptInfo(
            name="test_prompt",
            description="Test prompt",
            gtd_phase="capture",
            usage_frequency="medium",
            tags=["test"],
        )

        registry.register(prompt)
        assert len(registry) == 1

        registry.clear()
        assert len(registry) == 0
        assert registry.get_all_prompts() == []

    def test_registry_iteration(self) -> None:
        """Test iterating over registry prompts."""
        registry = PromptRegistry()

        prompt1 = PromptInfo(
            name="prompt1",
            description="First prompt",
            gtd_phase="capture",
            usage_frequency="high",
            tags=["first"],
        )

        prompt2 = PromptInfo(
            name="prompt2",
            description="Second prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["second"],
        )

        registry.register(prompt1)
        registry.register(prompt2)

        prompts_from_iteration = list(registry)
        assert len(prompts_from_iteration) == 2
        assert prompt1 in prompts_from_iteration
        assert prompt2 in prompts_from_iteration


class TestPromptInfo:
    """Test the PromptInfo data class."""

    def test_prompt_info_creation(self) -> None:
        """Test creating PromptInfo with all fields."""
        prompt_info = PromptInfo(
            name="inbox_clarification",
            description="Analyzes inbox items and suggests GTD categorization",
            gtd_phase="clarify",
            usage_frequency="high",
            tags=["categorization", "inbox", "gtd"],
            argument_schema={"inbox_item": "str", "existing_projects": "list[str]"},
            return_schema={"categorization": "Categorization"},
            examples=["Example 1", "Example 2"],
        )

        assert prompt_info.name == "inbox_clarification"
        assert (
            prompt_info.description
            == "Analyzes inbox items and suggests GTD categorization"
        )
        assert prompt_info.gtd_phase == "clarify"
        assert prompt_info.usage_frequency == "high"
        assert prompt_info.tags == ["categorization", "inbox", "gtd"]
        assert prompt_info.argument_schema == {
            "inbox_item": "str",
            "existing_projects": "list[str]",
        }
        assert prompt_info.return_schema == {"categorization": "Categorization"}
        assert prompt_info.examples == ["Example 1", "Example 2"]

    def test_prompt_info_minimal(self) -> None:
        """Test creating PromptInfo with minimal required fields."""
        prompt_info = PromptInfo(
            name="simple_prompt",
            description="A simple prompt",
            gtd_phase="capture",
            usage_frequency="low",
            tags=["simple"],
        )

        assert prompt_info.name == "simple_prompt"
        assert prompt_info.description == "A simple prompt"
        assert prompt_info.gtd_phase == "capture"
        assert prompt_info.usage_frequency == "low"
        assert prompt_info.tags == ["simple"]
        assert prompt_info.argument_schema is None
        assert prompt_info.return_schema is None
        assert prompt_info.examples is None

    def test_prompt_info_equality(self) -> None:
        """Test PromptInfo equality comparison."""
        prompt1 = PromptInfo(
            name="test_prompt",
            description="Test prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["test"],
        )

        prompt2 = PromptInfo(
            name="test_prompt",
            description="Test prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["test"],
        )

        prompt3 = PromptInfo(
            name="different_prompt",
            description="Different prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["test"],
        )

        assert prompt1 == prompt2
        assert prompt1 != prompt3

    def test_prompt_info_repr(self) -> None:
        """Test PromptInfo string representation."""
        prompt_info = PromptInfo(
            name="test_prompt",
            description="Test prompt",
            gtd_phase="clarify",
            usage_frequency="medium",
            tags=["test"],
        )

        repr_str = repr(prompt_info)
        assert "test_prompt" in repr_str
        assert "clarify" in repr_str
        assert "medium" in repr_str


class TestPromptDiscovery:
    """Test prompt discovery functionality."""

    def test_discover_core_prompts(self) -> None:
        """Test discovering core GTD prompts from registry."""
        registry = PromptRegistry()

        # Register core prompts
        core_prompts = [
            PromptInfo(
                name="inbox_clarification",
                description="Primary inbox processing prompt",
                gtd_phase="clarify",
                usage_frequency="high",
                tags=["core", "inbox", "categorization"],
            ),
            PromptInfo(
                name="quick_categorize",
                description="Fast categorization for obvious items",
                gtd_phase="clarify",
                usage_frequency="high",
                tags=["core", "quick", "categorization"],
            ),
            PromptInfo(
                name="batch_process_inbox",
                description="Process multiple inbox items efficiently",
                gtd_phase="clarify",
                usage_frequency="medium",
                tags=["core", "batch", "inbox"],
            ),
        ]

        for prompt in core_prompts:
            registry.register(prompt)

        # Discover core prompts
        discovered_core = registry.get_prompts_by_tag("core")
        assert len(discovered_core) == 3

        core_names = [p.name for p in discovered_core]
        assert "inbox_clarification" in core_names
        assert "quick_categorize" in core_names
        assert "batch_process_inbox" in core_names

    def test_discover_high_frequency_prompts(self) -> None:
        """Test discovering high frequency prompts."""
        registry = PromptRegistry()

        # Register mixed frequency prompts
        prompts = [
            PromptInfo(
                name="daily_prompt",
                description="Daily use prompt",
                gtd_phase="engage",
                usage_frequency="high",
                tags=["daily"],
            ),
            PromptInfo(
                name="weekly_prompt",
                description="Weekly use prompt",
                gtd_phase="reflect",
                usage_frequency="medium",
                tags=["weekly"],
            ),
            PromptInfo(
                name="monthly_prompt",
                description="Monthly use prompt",
                gtd_phase="reflect",
                usage_frequency="low",
                tags=["monthly"],
            ),
        ]

        for prompt in prompts:
            registry.register(prompt)

        # Discover high frequency prompts
        high_freq_prompts = registry.get_prompts_by_frequency("high")
        assert len(high_freq_prompts) == 1
        assert high_freq_prompts[0].name == "daily_prompt"

    def test_discover_prompts_by_gtd_workflow(self) -> None:
        """Test discovering prompts organized by GTD workflow phases."""
        registry = PromptRegistry()

        # Register prompts for each GTD phase
        phase_prompts = [
            PromptInfo(
                "capture_item", "Capture thoughts", "capture", "high", ["capture"]
            ),
            PromptInfo(
                "clarify_item", "Clarify actions", "clarify", "high", ["clarify"]
            ),
            PromptInfo(
                "organize_actions",
                "Organize by context",
                "organize",
                "medium",
                ["organize"],
            ),
            PromptInfo("review_system", "Weekly review", "reflect", "low", ["reflect"]),
            PromptInfo(
                "engage_actions", "Do next actions", "engage", "high", ["engage"]
            ),
        ]

        for prompt in phase_prompts:
            registry.register(prompt)

        # Test discovery by each phase
        capture_prompts = registry.get_prompts_by_phase("capture")
        assert len(capture_prompts) == 1
        assert capture_prompts[0].name == "capture_item"

        clarify_prompts = registry.get_prompts_by_phase("clarify")
        assert len(clarify_prompts) == 1
        assert clarify_prompts[0].name == "clarify_item"

        organize_prompts = registry.get_prompts_by_phase("organize")
        assert len(organize_prompts) == 1
        assert organize_prompts[0].name == "organize_actions"

        reflect_prompts = registry.get_prompts_by_phase("reflect")
        assert len(reflect_prompts) == 1
        assert reflect_prompts[0].name == "review_system"

        engage_prompts = registry.get_prompts_by_phase("engage")
        assert len(engage_prompts) == 1
        assert engage_prompts[0].name == "engage_actions"
