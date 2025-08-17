"""
Prompts package for MCP GTD workflow orchestration.

This package contains MCP prompts that guide Claude Desktop through
GTD methodology workflows without requiring server-side LLM processing.
"""

from .gtd_rules import (
    GTDDecisionTree,
    GTDMethodology,
    GTDPatterns,
    GTDRuleEngine,
)
from .registry import (
    PromptDiscovery,
    PromptInfo,
    PromptRegistry,
    get_discovery_service,
    get_global_registry,
    register_core_prompts,
)
from .schemas import Categorization, InboxItem, ItemGroup

__all__ = [
    "InboxItem",
    "Categorization",
    "ItemGroup",
    "GTDMethodology",
    "GTDDecisionTree",
    "GTDPatterns",
    "GTDRuleEngine",
    "PromptInfo",
    "PromptRegistry",
    "PromptDiscovery",
    "get_global_registry",
    "get_discovery_service",
    "register_core_prompts",
]
