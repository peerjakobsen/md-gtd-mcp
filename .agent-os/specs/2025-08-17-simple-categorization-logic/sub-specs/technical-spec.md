# Technical Specification - Simple Categorization Logic

## Architecture Overview

The Simple Categorization Logic feature implements MCP prompts that orchestrate GTD inbox processing through Claude Desktop's LLM intelligence, eliminating the need for server-side API access.

## Core Components

### 1. Prompt Registry System

```python
# src/md_gtd_mcp/prompts/__init__.py
from fastmcp import mcp
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class InboxItem(BaseModel):
    '''Schema for inbox items to be processed'''
    content: str = Field(description='Raw captured text from inbox')
    created_date: Optional[str] = Field(description='When item was captured')
    source: Optional[str] = Field(description='Source of capture (meeting, email, etc.)')

class CategorizationResult(BaseModel):
    '''Schema for categorization suggestions'''
    item: str = Field(description='Original or clarified item text')
    actionable: bool = Field(description='Whether item is actionable')
    category: str = Field(description='GTD category: next-action, project, waiting-for, someday-maybe, reference, trash')
    suggested_text: Optional[str] = Field(description='Clarified action text if applicable')
    context: Optional[str] = Field(description='Suggested GTD context (@home, @computer, etc.)')
    project: Optional[str] = Field(description='Associated project if identified')
    confidence: str = Field(description='Confidence level: high, medium, low')
    reasoning: str = Field(description='Explanation for categorization decision')
    two_minute_rule: Optional[bool] = Field(description='Whether item falls under 2-minute rule')
```

### 2. Core MCP Prompts

```python
# src/md_gtd_mcp/prompts/inbox_clarification.py

@mcp.prompt(
    name='inbox_clarification',
    description='Analyze inbox items and suggest GTD categorization with reasoning',
    tags=['gtd', 'inbox', 'categorization', 'clarify-phase']
)
async def inbox_clarification(
    inbox_items: List[str],
    existing_projects: List[str] = [],
    common_contexts: List[str] = ['@home', '@computer', '@calls', '@errands', '@office']
) -> str:
    '''
    Guides Claude through GTD inbox clarification process.

    This prompt orchestrates the transition from Capture to Clarify phase,
    analyzing raw inbox items for actionability and suggesting appropriate
    GTD categories with explanations.
    '''

    prompt_template = '''
    You are helping process GTD inbox items. For each item, apply David Allen's GTD methodology:

    INBOX ITEMS TO PROCESS:
    {inbox_items_formatted}

    EXISTING PROJECTS:
    {projects_formatted}

    AVAILABLE CONTEXTS:
    {contexts_formatted}

    For each inbox item, determine:

    1. ACTIONABILITY ASSESSMENT
       - Is this actionable? (Can you visualize doing it?)
       - If not actionable: Is it Reference, Someday/Maybe, or Trash?
       - If actionable: What's the successful outcome?

    2. CATEGORIZATION DECISION
       - Single action → next-action
       - Multiple actions → project (create or associate)
       - Delegated/waiting → waiting-for
       - Future possibility → someday-maybe
       - Information only → reference

    3. NEXT ACTION CLARIFICATION
       - What's the very next physical action?
       - Can it be done in 2 minutes?
       - What context is required?
       - Is special equipment/location needed?

    4. PROJECT ASSOCIATION
       - Does this relate to existing projects?
       - Should a new project be created?
       - What would the project outcome be?

    Return a JSON array with categorization for each item:
    {
      "categorizations": [
        {
          "item": "original or clarified text",
          "actionable": true/false,
          "category": "next-action|project|waiting-for|someday-maybe|reference|trash",
          "suggested_text": "clarified action if applicable",
          "context": "@context if actionable",
          "project": "associated project name or null",
          "confidence": "high|medium|low",
          "reasoning": "explanation for decision",
          "two_minute_rule": true/false/null
        }
      ]
    }

    Apply these GTD principles:
    - Capture ≠ Clarify (we're now in Clarify phase)
    - Be specific about physical actions
    - Consider energy levels and contexts
    - Group related items into projects
    - Non-actionable ≠ not useful
    '''

    # Format the prompt with actual data
    formatted_prompt = prompt_template.format(
        inbox_items_formatted='\n'.join(f'- {item}' for item in inbox_items),
        projects_formatted='\n'.join(f'- {proj}' for proj in existing_projects) if existing_projects else 'No existing projects',
        contexts_formatted=', '.join(common_contexts)
    )

    return formatted_prompt
```

### 3. Quick Categorization Prompt

```python
# src/md_gtd_mcp/prompts/quick_categorize.py

@mcp.prompt(
    name='quick_categorize',
    description='Lightweight categorization for simple inbox items',
    tags=['gtd', 'inbox', 'quick']
)
async def quick_categorize(
    item: str,
    existing_projects: List[str] = []
) -> str:
    '''
    Fast categorization for clear-cut inbox items.
    '''

    prompt = f'''
    Quick GTD categorization for: "{item}"

    Existing projects: {', '.join(existing_projects) if existing_projects else 'None'}

    Apply GTD rules:
    - Clear single action → next-action
    - Multi-step outcome → project
    - Delegated → waiting-for
    - Future/unclear → someday-maybe

    Return: {{"category": "...", "confidence": "high|medium|low", "reasoning": "brief explanation"}}
    '''

    return prompt
```

### 4. Batch Processing Prompt

```python
# src/md_gtd_mcp/prompts/batch_process.py

@mcp.prompt(
    name='batch_process_inbox',
    description='Process multiple inbox items with consistency',
    tags=['gtd', 'inbox', 'batch', 'efficiency']
)
async def batch_process_inbox(
    inbox_items: List[str],
    group_similar: bool = True,
    existing_projects: List[str] = []
) -> str:
    '''
    Efficiently process multiple inbox items with grouping logic.
    '''

    prompt = f'''
    Batch process {len(inbox_items)} GTD inbox items.

    {"Group similar items for efficiency." if group_similar else "Process each item independently."}

    Items to process:
    {chr(10).join(f"{i+1}. {item}" for i, item in enumerate(inbox_items))}

    Existing projects: {', '.join(existing_projects[:10]) if existing_projects else 'None'}

    For efficiency:
    1. Identify patterns across items
    2. Group related items
    3. Suggest batch actions where appropriate
    4. Maintain consistency in categorization

    Return categorizations with grouping suggestions if applicable.
    '''

    return prompt
```

### 5. GTD Rule Engine

```python
# src/md_gtd_mcp/prompts/rules.py

class GTDRuleEngine:
    '''
    Encodes GTD methodology rules for categorization decisions.
    '''

    ACTIONABILITY_QUESTIONS = [
        'Can you visualize yourself doing this?',
        'Is there a physical next action?',
        'Does this require action from you?',
        'Is this a desired outcome requiring multiple steps?'
    ]

    CONTEXT_PATTERNS = {
        '@calls': ['call', 'phone', 'dial', 'contact', 'reach out'],
        '@computer': ['email', 'write', 'code', 'research', 'analyze', 'review'],
        '@home': ['home', 'house', 'family', 'personal', 'weekend'],
        '@office': ['office', 'work', 'meeting', 'colleague', 'boss'],
        '@errands': ['buy', 'pick up', 'shop', 'store', 'errand'],
        '@anywhere': ['think', 'brainstorm', 'consider', 'reflect']
    }

    TWO_MINUTE_INDICATORS = [
        'quick', 'simple', 'just', 'quickly', 'brief',
        'short', 'fast', 'immediately'
    ]

    PROJECT_INDICATORS = [
        'project', 'initiative', 'implement', 'develop',
        'create', 'build', 'design', 'plan', 'organize'
    ]

    @staticmethod
    def build_rule_context() -> str:
        '''Generate GTD rules for prompt context'''
        return '''
        GTD Decision Tree:
        1. Is it actionable?
           NO → Reference (keep for info) | Someday/Maybe (might do later) | Trash (no value)
           YES → Continue to 2

        2. Will it take multiple steps?
           YES → Project (needs planning and multiple actions)
           NO → Continue to 3

        3. Will it take less than 2 minutes?
           YES → Do it now (don't track, just complete)
           NO → Continue to 4

        4. Am I the right person?
           NO → Delegate → Waiting For (track what you're waiting on)
           YES → Next Action (single clear action to take)

        Context Assignment:
        - @calls: Requires phone
        - @computer: Requires computer/internet
        - @office: Must be at office
        - @home: Must be at home
        - @errands: Out and about
        - @anywhere: Can be done anywhere
        '''
```

### 6. Integration with Existing Server

```python
# src/md_gtd_mcp/server.py updates

from .prompts import (
    inbox_clarification,
    quick_categorize,
    batch_process_inbox
)

# Register prompts with the MCP server
mcp.add_prompt(inbox_clarification)
mcp.add_prompt(quick_categorize)
mcp.add_prompt(batch_process_inbox)

# Optional: Add meta information for prompt discovery
mcp.meta(
    prompts_info={
        'categorization': {
            'description': 'GTD inbox processing and categorization prompts',
            'prompts': ['inbox_clarification', 'quick_categorize', 'batch_process_inbox'],
            'usage': 'Use these prompts to guide Claude through GTD methodology'
        }
    }
)
```

## Data Flow

1. **User Invocation**
   - User triggers prompt through Claude Desktop
   - Provides inbox items and context

2. **Prompt Processing**
   - Server receives prompt request via MCP protocol
   - Formats prompt with GTD rules and context
   - Returns structured instructions to Claude

3. **Claude Analysis**
   - Claude processes prompt with its LLM intelligence
   - Applies GTD methodology rules
   - Generates categorization suggestions

4. **Response Handling**
   - Claude returns structured JSON response
   - User reviews suggestions
   - Approves or modifies categorizations

5. **Action Execution**
   - Approved categorizations trigger tool calls
   - Items moved to appropriate GTD files
   - #task tags added during clarification

## Error Handling

### Prompt Validation
```python
def validate_inbox_items(items: List[str]) -> List[str]:
    '''Validate and sanitize inbox items before processing'''
    validated = []
    for item in items:
        if not item or not item.strip():
            continue
        # Remove excessive whitespace
        cleaned = ' '.join(item.split())
        # Limit length to prevent prompt overflow
        if len(cleaned) > 500:
            cleaned = cleaned[:497] + '...'
        validated.append(cleaned)
    return validated
```

### Response Validation
```python
def validate_categorization_result(result: dict) -> bool:
    '''Ensure categorization result has required fields'''
    required_fields = ['item', 'actionable', 'category', 'reasoning']
    valid_categories = ['next-action', 'project', 'waiting-for',
                       'someday-maybe', 'reference', 'trash']

    if not all(field in result for field in required_fields):
        return False

    if result['category'] not in valid_categories:
        return False

    return True
```

## Performance Considerations

### Batching Strategy
- Process up to 20 items per batch
- Group similar items to reduce analysis time
- Cache project lists for session

### Prompt Optimization
- Limit context to 10 most recent projects
- Use quick_categorize for obvious items
- Implement progressive disclosure for complex items

## Testing Strategy

### Unit Tests
```python
def test_inbox_clarification_prompt_generation():
    '''Test prompt generates correct structure'''
    result = await inbox_clarification(
        inbox_items=['Call dentist', 'Research new CRM'],
        existing_projects=['Health', 'Business Systems']
    )
    assert 'Call dentist' in result
    assert 'GTD methodology' in result
    assert 'categorizations' in result
```

### Integration Tests
```python
def test_end_to_end_categorization():
    '''Test full categorization workflow'''
    # 1. Read inbox items via resources
    # 2. Invoke categorization prompt
    # 3. Validate response structure
    # 4. Verify suggested categories
```

### Edge Cases
- Empty inbox
- Malformed items
- Very long items
- Special characters
- Non-English content

## Security Considerations

### Input Sanitization
- Escape special characters in prompts
- Limit item length to prevent overflow
- Validate JSON responses

### Prompt Injection Prevention
- Sanitize user input before prompt inclusion
- Use structured schemas for responses
- Limit prompt template modification

## Documentation Requirements

### User Guide
- GTD methodology primer
- Prompt usage examples
- Common categorization patterns
- Troubleshooting guide

### Developer Documentation
- Prompt extension guide
- Custom rule creation
- Integration patterns
- Testing guidelines
