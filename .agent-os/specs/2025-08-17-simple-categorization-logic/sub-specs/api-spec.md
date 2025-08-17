# API Specification - Simple Categorization Logic

## MCP Prompt API

### inbox_clarification

Comprehensive GTD inbox processing with detailed analysis.

#### Request Schema (Python)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class InboxClarificationRequest(BaseModel):
    inbox_items: List[str] = Field(
        description="Raw captured items from inbox"
    )
    existing_projects: Optional[List[str]] = Field(
        default=[],
        description="Current project names for association"
    )
    common_contexts: Optional[List[str]] = Field(
        default=['@home', '@computer', '@calls', '@errands', '@office'],
        description="Available GTD contexts"
    )
```

#### Response Schema (Python)

```python
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class Categorization(BaseModel):
    item: str = Field(
        description="Original or clarified item text"
    )
    actionable: bool = Field(
        description="Whether item requires action"
    )
    category: Literal[
        'next-action',
        'project',
        'waiting-for',
        'someday-maybe',
        'reference',
        'trash'
    ] = Field(
        description="GTD category assignment"
    )
    suggested_text: Optional[str] = Field(
        default=None,
        description="Clarified action text"
    )
    context: Optional[str] = Field(
        default=None,
        description="GTD context (@home, @computer, etc.)"
    )
    project: Optional[str] = Field(
        default=None,
        description="Associated project name"
    )
    confidence: Literal['high', 'medium', 'low'] = Field(
        description="Certainty of categorization"
    )
    reasoning: str = Field(
        description="Explanation for decision"
    )
    two_minute_rule: Optional[bool] = Field(
        default=None,
        description="Falls under 2-minute rule"
    )

class InboxClarificationResponse(BaseModel):
    categorizations: List[Categorization]
```

#### Example Usage (Python)

```python
# Using the MCP client
result = await mcp_client.invoke_prompt(
    'inbox_clarification',
    inbox_items=[
        'Call dentist about appointment',
        'Research new project management tools',
        'Waiting for Sarah to send report'
    ],
    existing_projects=['Health', 'Productivity Systems'],
    common_contexts=['@calls', '@computer', '@office']
)
```

#### Example Response (JSON)

```json
{
  "categorizations": [
    {
      "item": "Call dentist about appointment",
      "actionable": true,
      "category": "next-action",
      "suggested_text": "Call Dr. Smith to schedule cleaning appointment",
      "context": "@calls",
      "project": "Health",
      "confidence": "high",
      "reasoning": "Single, clear action requiring a phone call. Associated with Health project.",
      "two_minute_rule": false
    },
    {
      "item": "Research new project management tools",
      "actionable": true,
      "category": "project",
      "suggested_text": "Implement new project management system",
      "context": "@computer",
      "project": "Productivity Systems",
      "confidence": "high",
      "reasoning": "Multi-step outcome requiring research, evaluation, and implementation phases.",
      "two_minute_rule": false
    },
    {
      "item": "Waiting for Sarah to send report",
      "actionable": true,
      "category": "waiting-for",
      "suggested_text": "Report from Sarah - Q4 analysis",
      "context": null,
      "project": null,
      "confidence": "high",
      "reasoning": "Already delegated, tracking what we're waiting to receive.",
      "two_minute_rule": null
    }
  ]
}
```

### quick_categorize

Fast, lightweight categorization for simple items.

#### Request Schema (Python)

```python
from typing import Optional, List
from pydantic import BaseModel, Field

class QuickCategorizeRequest(BaseModel):
    item: str = Field(
        description="Single inbox item"
    )
    existing_projects: Optional[List[str]] = Field(
        default=[],
        description="Project list for association"
    )
```

#### Response Schema (Python)

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field

class QuickCategorizeResponse(BaseModel):
    category: Literal[
        'next-action',
        'project',
        'waiting-for',
        'someday-maybe',
        'reference',
        'trash'
    ]
    confidence: Literal['high', 'medium', 'low']
    reasoning: str
    project: Optional[str] = None
```

#### Example Usage (Python)

```python
result = await mcp_client.invoke_prompt(
    'quick_categorize',
    item='Buy milk',
    existing_projects=[]
)
```

#### Example Response (JSON)

```json
{
  "category": "next-action",
  "confidence": "high",
  "reasoning": "Simple, single action errand task"
}
```

### batch_process_inbox

Efficient processing of multiple inbox items with grouping.

#### Request Schema (Python)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class BatchProcessRequest(BaseModel):
    inbox_items: List[str] = Field(
        description="Multiple items to process"
    )
    group_similar: bool = Field(
        default=True,
        description="Group related items"
    )
    existing_projects: Optional[List[str]] = Field(
        default=[],
        description="Current projects"
    )
```

#### Response Schema (Python)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class ItemGroup(BaseModel):
    name: str = Field(
        description="Suggested group/project name"
    )
    item_indices: List[int] = Field(
        description="Indices of related items"
    )
    reasoning: str = Field(
        description="Why items are related"
    )

class BatchProcessResponse(BaseModel):
    categorizations: List[Categorization]
    groups: Optional[List[ItemGroup]] = Field(
        default=None,
        description="Optional grouping suggestions"
    )
```

#### Example Usage (Python)

```python
result = await mcp_client.invoke_prompt(
    'batch_process_inbox',
    inbox_items=[
        'Update website homepage',
        'Fix broken contact form',
        'Add new blog post',
        'Call plumber about leak',
        'Schedule HVAC maintenance'
    ],
    group_similar=True,
    existing_projects=['Website Redesign', 'Home Maintenance']
)
```

#### Example Response (JSON)

```json
{
  "categorizations": [
    {
      "item": "Update website homepage",
      "category": "next-action",
      "context": "@computer",
      "project": "Website Redesign",
      "confidence": "high",
      "reasoning": "Website-related task"
    },
    {
      "item": "Fix broken contact form",
      "category": "next-action",
      "context": "@computer",
      "project": "Website Redesign",
      "confidence": "high",
      "reasoning": "Website-related task"
    }
  ],
  "groups": [
    {
      "name": "Website Redesign",
      "item_indices": [0, 1, 2],
      "reasoning": "All website-related tasks"
    },
    {
      "name": "Home Maintenance",
      "item_indices": [3, 4],
      "reasoning": "Home repair and maintenance items"
    }
  ]
}
```

## Supporting Tools API

### process_inbox (Tool)

Executes categorization decisions after prompt analysis.

#### Request Schema (Python)

```python
from typing import List, Optional
from pydantic import BaseModel, Field

class ProcessInboxRequest(BaseModel):
    categorizations: List[Categorization] = Field(
        description="Approved categorizations from prompt"
    )
    add_task_tags: bool = Field(
        default=True,
        description="Add #task during processing"
    )
    create_projects: bool = Field(
        default=False,
        description="Create new project files if needed"
    )
```

#### Response Schema (Python)

```python
from typing import List
from pydantic import BaseModel, Field

class ProcessingError(BaseModel):
    item: str
    error: str

class ProcessInboxResponse(BaseModel):
    processed: int = Field(
        description="Items successfully processed"
    )
    created_projects: List[str] = Field(
        default=[],
        description="New projects created"
    )
    errors: List[ProcessingError] = Field(
        default=[],
        description="Any errors encountered"
    )
```

## Resource APIs Used

### Reading Inbox Items

```python
# Resource URI: gtd://{vault_path}/file/inbox.md
from typing import List, Dict, Any
from pydantic import BaseModel

class Task(BaseModel):
    text: str
    completed: bool
    has_tag: bool
    metadata: Dict[str, Any]

class InboxContent(BaseModel):
    tasks: List[Task]
    content: str
    metadata: Dict[str, Any]
```

### Reading Projects List

```python
# Resource URI: gtd://{vault_path}/files/project
from typing import List
from pydantic import BaseModel

class FileInfo(BaseModel):
    name: str
    path: str
    type: str
    modified: str

class ProjectFiles(BaseModel):
    files: List[FileInfo]
    count: int
```

## Error Handling

```python
from enum import Enum

class PromptErrorCode(str, Enum):
    INVALID_ITEMS = "PROMPT_001"
    TIMEOUT = "PROMPT_002"
    INVALID_RESPONSE = "PROMPT_003"
    PROJECT_NOT_FOUND = "PROMPT_004"
    CONTEXT_NOT_RECOGNIZED = "PROMPT_005"

class PromptError(Exception):
    def __init__(self, code: PromptErrorCode, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")
```

## Error Reference

| Code | Description | Resolution |
|------|-------------|------------|
| `PROMPT_001` | Invalid inbox items | Ensure items are non-empty strings |
| `PROMPT_002` | Prompt timeout | Reduce batch size or use quick_categorize |
| `PROMPT_003` | Invalid response format | Check Claude Desktop version compatibility |
| `PROMPT_004` | Project not found | Verify project exists or create new |
| `PROMPT_005` | Context not recognized | Use standard GTD contexts |

## Rate Limiting

```python
class RateLimits:
    MAX_ITEMS_PER_BATCH = 20
    MAX_CONCURRENT_PROMPTS = 3
    MAX_ITEM_LENGTH = 500  # characters
```

## Versioning

```python
API_VERSION = "1.0.0"
MCP_PROTOCOL_VERSION = "1.0"
FASTMCP_MIN_VERSION = "0.2.0"
```

## Authentication

No authentication required - prompts execute in user's Claude Desktop context.

## Usage Example

```python
from md_gtd_mcp.client import GTDClient

async def process_my_inbox():
    client = GTDClient()

    # Read inbox items
    inbox = await client.read_resource('gtd://~/obsidian/file/inbox.md')

    # Get categorization suggestions
    suggestions = await client.invoke_prompt(
        'inbox_clarification',
        inbox_items=[task.text for task in inbox.tasks if not task.has_tag]
    )

    # Process approved categorizations
    result = await client.call_tool(
        'process_inbox',
        categorizations=suggestions.categorizations
    )

    print(f"Processed {result.processed} items")
```
