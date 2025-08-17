"""
Core MCP prompts for GTD workflow orchestration.

This module implements the essential MCP prompts that guide Claude Desktop through
GTD methodology workflows without requiring server-side LLM processing.
Following Decision D008, these prompts leverage Claude Desktop's intelligence
to provide sophisticated GTD automation without API key barriers.
"""


def inbox_clarification_prompt(
    inbox_item: str,
    existing_projects: list[str] | None = None,
    common_contexts: list[str] | None = None,
) -> str:
    """
    Analyzes an inbox item and suggests GTD categorization with reasoning.

    This prompt guides Claude Desktop through the GTD Clarify phase,
    helping users process captured thoughts into actionable items following
    David Allen's methodology.

    Args:
        inbox_item: The captured thought or item text to process
        existing_projects: List of current project names for association
        common_contexts: List of available GTD contexts (@home, @computer, etc.)

    Returns:
        Structured prompt guiding Claude through GTD categorization
    """
    existing_projects = existing_projects or []
    common_contexts = common_contexts or [
        "@home",
        "@computer",
        "@calls",
        "@errands",
        "@office",
    ]

    project_context = ""
    if existing_projects:
        project_context = f"""
### Existing Projects for Association
{chr(10).join(f"- {project}" for project in existing_projects)}
"""

    context_list = ""
    if common_contexts:
        context_list = f"""
### Available GTD Contexts
{chr(10).join(f"- {context}" for context in common_contexts)}
"""

    return f"""# GTD Inbox Clarification

Analyze this captured inbox item following David Allen's GTD methodology:

**Inbox Item:** "{inbox_item}"

{project_context}
{context_list}

## GTD Clarification Process

Follow these steps to properly categorize this item:

### 1. Actionability Assessment
- **Is this actionable?** Does it require any action from me?
- **If not actionable:** Categorize as Reference (save for later) or Trash (delete)
- **If actionable:** Continue to step 2

### 2. Outcome Definition
- **What successful outcome would look like?** Be specific
- **Is this a single action or multiple steps?**
- **If single action:** It's a Next Action
- **If multiple steps:** It's a Project (outcome + next action)

### 3. Time Assessment
- **Can this be done in 2 minutes or less?** If yes, recommend doing it now
- **If longer:** Proceed with categorization

### 4. Category Assignment
Choose the most appropriate GTD category:
- **Next Action:** Single physical action ready to be done
- **Project:** Outcome requiring multiple steps (extract first next action)
- **Waiting For:** Delegated or dependent on others
- **Someday/Maybe:** Not committed to doing now but might later
- **Reference:** Information to keep for future use

### 5. Context Assignment
If it's a Next Action, assign appropriate context:
- **@calls:** Requires making phone calls
- **@computer:** Requires computer/internet
- **@home:** Can only be done at home
- **@errands:** Done while out running errands
- **@office:** Requires being at the office

### 6. Project Association
If relevant to existing projects, identify which project this supports.

## Required Response Format

Provide your analysis in this JSON structure:

```json
{{
  "item": "{inbox_item}",
  "actionable": true/false,
  "category": "next-action" | "project" | "waiting-for" | "someday-maybe" |
              "reference" | "trash",
  "suggested_text": "Improved clear action description",
  "context": "@context" or null,
  "creates_new_project": true/false,
  "new_project": {{
    "project_name": "Clear project name",
    "outcome": "Specific successful outcome",
    "first_next_action": "First physical action",
    "context": "@context",
    "reasoning": "Why this needs to be a project"
  }} or null,
  "associates_existing_project": true/false,
  "existing_project": {{
    "project_name": "Existing project name",
    "relevance_score": 0.0-1.0,
    "reasoning": "Why this relates to this project",
    "suggested_action": "Specific action to add"
  }} or null,
  "confidence": "high" | "medium" | "low",
  "reasoning": "Step-by-step explanation of categorization decision",
  "time_estimate": minutes_to_complete or null,
  "energy_level": "high" | "medium" | "low" or null,
  "delegated_to": "person_name" or null
}}
```

Focus on clarity, actionability, and proper GTD methodology. Provide detailed
reasoning for your categorization decisions."""


def quick_categorize_prompt(inbox_item: str) -> str:
    """
    Fast categorization for obvious inbox items requiring minimal analysis.

    This prompt is optimized for simple, clear-cut items that don't require
    extensive analysis. It focuses on speed while maintaining GTD accuracy.

    Args:
        inbox_item: The simple captured item to quickly categorize

    Returns:
        Streamlined prompt for rapid categorization
    """
    return f"""# Quick GTD Categorization

Quickly categorize this simple inbox item:

**Item:** "{inbox_item}"

## Fast Assessment Rules

1. **Obvious Actions:** If it's clearly a single action, categorize as Next Action
   with context
2. **Clear References:** If it's obviously information to save, mark as Reference
3. **Simple Delegations:** If it's waiting on someone specific, mark as Waiting For
4. **Future Ideas:** If it's clearly a someday/maybe item, categorize accordingly
5. **Complex Items:** If unclear or complex, recommend using full inbox_clarification

## Quick Response Format

```json
{{
  "item": "{inbox_item}",
  "actionable": true/false,
  "category": "next-action" | "project" | "waiting-for" | "someday-maybe" |
              "reference" | "trash",
  "suggested_text": "Clear action if needed",
  "context": "@context" or null,
  "confidence": "high" | "medium" | "low",
  "reasoning": "Brief explanation",
  "time_estimate": minutes or null,
  "needs_full_analysis": true/false
}}
```

If `needs_full_analysis` is true, recommend using the full inbox_clarification
prompt instead."""


def batch_process_inbox_prompt(
    inbox_items: list[str],
    existing_projects: list[str] | None = None,
    max_items: int = 20,
) -> str:
    """
    Process multiple inbox items efficiently with grouping and consistency.

    This prompt handles batch processing of inbox items, identifying patterns
    and grouping related items for efficient processing while maintaining
    categorization consistency.

    Args:
        inbox_items: List of captured items to process
        existing_projects: List of current project names
        max_items: Maximum number of items to process (default 20)

    Returns:
        Comprehensive prompt for batch inbox processing
    """
    existing_projects = existing_projects or []

    # Limit items to max_items
    items_to_process = inbox_items[:max_items]

    items_list = ""
    for i, item in enumerate(items_to_process, 1):
        items_list += f"{i}. {item}\n"

    project_context = ""
    if existing_projects:
        project_context = f"""
### Existing Projects
{chr(10).join(f"- {project}" for project in existing_projects)}
"""

    return f"""# GTD Batch Inbox Processing

Process these {len(items_to_process)} inbox items efficiently following GTD methodology:

## Items to Process
{items_list}
{project_context}

## Batch Processing Strategy

### 1. Pattern Recognition
- **Group Similar Items:** Identify items that relate to the same project or theme
- **Common Contexts:** Notice items requiring the same context (@calls, @computer, etc.)
- **Delegation Patterns:** Identify items waiting on the same person
- **Project Indicators:** Spot items that suggest new projects

### 2. Efficiency Guidelines
- **Process Similar Items Together:** Group by context or project for consistency
- **Identify Project Clusters:** Multiple related items may indicate a new project
- **Batch Context Assignment:** Assign contexts consistently across similar items
- **Standard Processing:** Use same quality standards as individual processing

### 3. Grouping Logic
Create logical groups based on:
- **Project Relevance:** Items supporting the same outcome
- **Context Similarity:** Items requiring the same physical context
- **Theme Coherence:** Items related to the same area of responsibility
- **Processing Order:** Dependencies between items

## Required Response Format

```json
{{
  "categorizations": [
    {{
      "item": "Original item text",
      "actionable": true/false,
      "category": "next-action" | "project" | "waiting-for" | "someday-maybe" |
                  "reference" | "trash",
      "suggested_text": "Improved description",
      "context": "@context" or null,
      "creates_new_project": true/false,
      "new_project": {{ ... }} or null,
      "associates_existing_project": true/false,
      "existing_project": {{ ... }} or null,
      "confidence": "high" | "medium" | "low",
      "reasoning": "Categorization explanation",
      "time_estimate": minutes or null,
      "energy_level": "high" | "medium" | "low" or null
    }}
  ],
  "groups": [
    {{
      "items": ["item1", "item2", "item3"],
      "group_type": "project" | "context" | "theme",
      "description": "What groups these items",
      "suggested_project": "Project name if applicable",
      "processing_order": [0, 1, 2]
    }}
  ],
  "processing_summary": "Overview of batch processing results and patterns identified"
}}
```

Focus on efficiency, consistency, and identifying natural groupings while
maintaining GTD quality standards."""
