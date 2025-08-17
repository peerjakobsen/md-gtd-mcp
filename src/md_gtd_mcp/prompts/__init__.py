"""
Prompts package for MCP GTD workflow orchestration.

This package contains MCP prompts that guide Claude Desktop through
GTD methodology workflows without requiring server-side LLM processing.
"""

from .schemas import Categorization, InboxItem, ItemGroup

__all__ = ["InboxItem", "Categorization", "ItemGroup"]
