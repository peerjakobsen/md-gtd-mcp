"""
Pydantic schemas for MCP prompt arguments and responses.

These schemas define the data structures used by MCP prompts to orchestrate
GTD workflows through Claude Desktop's LLM intelligence.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class GTDCategory(str, Enum):
    """Valid GTD categories for inbox item classification."""

    NEXT_ACTION = "next-action"
    WAITING_FOR = "waiting-for"
    SOMEDAY_MAYBE = "someday-maybe"
    REFERENCE = "reference"
    TRASH = "trash"


class ConfidenceLevel(str, Enum):
    """Confidence levels for categorization suggestions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GTDContext(str, Enum):
    """Valid GTD contexts for action assignment."""

    HOME = "@home"
    COMPUTER = "@computer"
    CALLS = "@calls"
    ERRANDS = "@errands"
    OFFICE = "@office"
    PHONE = "@phone"
    AGENDA = "@agenda"
    WAITING = "@waiting"


class InboxItem(BaseModel):
    """Represents a captured item in the GTD inbox for processing."""

    text: str = Field(..., description="The captured thought or item text")
    line_number: int | None = Field(None, description="Line number in inbox file")
    captured_date: datetime | None = Field(None, description="When item was captured")
    source: str | None = Field(
        None, description="Source of capture (meeting, email, etc.)"
    )

    @field_validator("text")
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate that inbox item text is not empty and within length limit."""
        if not v or not v.strip():
            raise ValueError("Inbox item text cannot be empty")

        v = v.strip()
        if len(v) > 500:
            raise ValueError("Inbox item text must be 500 characters or less")

        return v


class NewProject(BaseModel):
    """Schema for creating a new project from an inbox item."""

    project_name: str = Field(..., description="Suggested name for the new project")
    outcome: str = Field(..., description="Clear project outcome statement")
    first_next_action: str = Field(
        ..., description="First actionable step for the project"
    )
    context: GTDContext | None = Field(None, description="Context for the first action")
    reasoning: str = Field(..., description="Why this should be a new project")


class ExistingProject(BaseModel):
    """Schema for associating an item with an existing project."""

    project_name: str = Field(..., description="Name of the existing project")
    relevance_score: float = Field(..., description="Relevance score (0.0-1.0)")
    reasoning: str = Field(..., description="Why this item relates to this project")
    suggested_action: str | None = Field(
        None, description="Specific action to add to project"
    )

    @field_validator("relevance_score")
    @classmethod
    def validate_relevance_score(cls, v: float) -> float:
        """Validate relevance score is between 0 and 1."""
        if v < 0.0 or v > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        return v


class Categorization(BaseModel):
    """Response schema for GTD categorization suggestions."""

    item: str = Field(..., description="Original inbox item text")
    actionable: bool = Field(..., description="Whether the item is actionable")

    # Primary classification - what immediate action/category this item represents
    category: GTDCategory | None = Field(
        None, description="Primary GTD category for this item"
    )
    suggested_text: str | None = Field(None, description="Improved task description")
    context: GTDContext | None = Field(None, description="Suggested GTD context")

    # Project relationships (mutually exclusive)
    creates_new_project: bool = Field(
        False, description="Whether this item should create a new project"
    )
    new_project: NewProject | None = Field(
        None, description="New project details if applicable"
    )

    associates_existing_project: bool = Field(
        False, description="Whether this relates to existing project"
    )
    existing_project: ExistingProject | None = Field(
        None, description="Existing project association if applicable"
    )

    # Additional metadata
    confidence: ConfidenceLevel = Field(..., description="Confidence in categorization")
    reasoning: str = Field(..., description="Explanation for the categorization")
    time_estimate: int | None = Field(None, description="Estimated minutes to complete")
    energy_level: str | None = Field(
        None, description="Required energy level (high/medium/low)"
    )
    delegated_to: str | None = Field(
        None, description="Person name for waiting-for items"
    )

    @field_validator("reasoning")
    @classmethod
    def validate_reasoning(cls, v: str) -> str:
        """Validate that reasoning is provided."""
        if not v or not v.strip():
            raise ValueError("Reasoning must be provided for categorization")
        return v.strip()

    @field_validator("time_estimate")
    @classmethod
    def validate_time_estimate(cls, v: int | None) -> int | None:
        """Validate time estimate is within reasonable range."""
        if v is not None and (v < 1 or v > 480):  # 1 minute to 8 hours
            raise ValueError("Time estimate must be between 1 and 480 minutes")
        return v

    @model_validator(mode="after")
    def validate_project_relationships(self) -> "Categorization":
        """Validate project relationship consistency and mutual exclusivity."""
        # Check new project consistency
        if self.creates_new_project and self.new_project is None:
            raise ValueError(
                "new_project must be provided when creates_new_project is True"
            )
        if not self.creates_new_project and self.new_project is not None:
            raise ValueError(
                "new_project should be None when creates_new_project is False"
            )

        # Check existing project consistency
        if self.associates_existing_project and self.existing_project is None:
            raise ValueError(
                "existing_project must be provided when "
                "associates_existing_project is True"
            )
        if not self.associates_existing_project and self.existing_project is not None:
            raise ValueError(
                "existing_project should be None when "
                "associates_existing_project is False"
            )

        # Check mutual exclusivity
        if self.creates_new_project and self.associates_existing_project:
            raise ValueError(
                "Cannot both create new project and associate with existing project"
            )

        return self


class ItemGroup(BaseModel):
    """Represents a group of related inbox items for batch processing."""

    items: list[InboxItem] = Field(..., description="List of related inbox items")
    group_type: str = Field(
        ..., description="Type of grouping (project, context, theme)"
    )
    description: str = Field(..., description="Description of what groups these items")
    suggested_project: str | None = Field(
        None, description="Suggested project name for group"
    )
    processing_order: list[int] = Field(
        default_factory=list, description="Suggested processing order by item index"
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[InboxItem]) -> list[InboxItem]:
        """Validate that item group contains valid number of items."""
        if not v:
            raise ValueError("Item group must contain at least one item")
        if len(v) > 20:
            raise ValueError("Item group cannot contain more than 20 items")
        return v

    @model_validator(mode="after")
    def validate_processing_order(self) -> "ItemGroup":
        """Validate processing order indices are valid item indices."""
        if self.processing_order:
            items_count = len(self.items)
            if any(i < 0 or i >= items_count for i in self.processing_order):
                raise ValueError("Processing order indices must be valid item indices")
        return self


class BatchProcessingResult(BaseModel):
    """Response schema for batch inbox processing."""

    categorizations: list[Categorization] = Field(
        ..., description="Individual categorizations"
    )
    groups: list[ItemGroup] = Field(
        default_factory=list, description="Suggested item groupings"
    )
    processing_summary: str = Field(
        ..., description="Summary of batch processing results"
    )

    @field_validator("categorizations")
    @classmethod
    def validate_categorizations(cls, v: list[Categorization]) -> list[Categorization]:
        """Validate that batch result contains categorizations."""
        if not v:
            raise ValueError(
                "Batch processing must contain at least one categorization"
            )
        return v
