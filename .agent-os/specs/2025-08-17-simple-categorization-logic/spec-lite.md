# Simple Categorization Logic - Spec Lite

## Summary
Implement MCP prompts that guide Claude Desktop through intelligent GTD inbox categorization without requiring API keys, following Decision D008's approach of leveraging client-side LLM intelligence.

## Core Features
- **inbox_clarification** prompt for analyzing and categorizing inbox items
- **GTD category suggestions** with reasoning (Next Action, Project, Waiting For, Someday/Maybe)
- **Context assignment** recommendations (@home, @computer, @calls, @errands)
- **Project association** for linking items to existing projects
- **Batch processing** support for multiple inbox items

## Key Benefits
- Zero API key requirements
- Leverages Claude Desktop's existing intelligence
- Maintains GTD methodology integrity
- Provides clear explanations for suggestions

## Technical Approach
- FastMCP `@mcp.prompt()` decorator
- Structured argument schemas for GTD state
- JSON response format with confidence levels
- Pattern recognition for common item types

## Success Criteria
- 90% accurate categorization for standard items
- <2 second single item processing
- Clear reasoning for all suggestions
- No external API dependencies
