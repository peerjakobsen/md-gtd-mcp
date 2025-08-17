"""Tests for MCP prompt schemas."""
# mypy: disable-error-code=call-arg

from datetime import datetime

import pytest
from pydantic import ValidationError

from md_gtd_mcp.prompts.schemas import (
    BatchProcessingResult,
    Categorization,
    ConfidenceLevel,
    ExistingProject,
    GTDCategory,
    GTDContext,
    InboxItem,
    ItemGroup,
    NewProject,
)


class TestInboxItem:
    """Test InboxItem Pydantic model."""

    def test_inbox_item_creation(self) -> None:
        """Test creating a valid inbox item."""
        item = InboxItem(
            text="Schedule dentist appointment",
            line_number=5,
            captured_date=datetime(2024, 1, 15, 10, 30),
            source="meeting notes",
        )
        assert item.text == "Schedule dentist appointment"
        assert item.line_number == 5
        assert item.captured_date == datetime(2024, 1, 15, 10, 30)
        assert item.source == "meeting notes"

    def test_inbox_item_minimal(self) -> None:
        """Test creating inbox item with only required fields."""
        item = InboxItem(text="Buy groceries")
        assert item.text == "Buy groceries"
        assert item.line_number is None
        assert item.captured_date is None
        assert item.source is None

    def test_inbox_item_strips_whitespace(self) -> None:
        """Test that inbox item text is stripped of whitespace."""
        item = InboxItem(text="  Review document  ")
        assert item.text == "Review document"

    def test_inbox_item_empty_text_validation(self) -> None:
        """Test that empty text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InboxItem(text="")
        assert "Inbox item text cannot be empty" in str(exc_info.value)

    def test_inbox_item_whitespace_only_validation(self) -> None:
        """Test that whitespace-only text raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            InboxItem(text="   ")
        assert "Inbox item text cannot be empty" in str(exc_info.value)

    def test_inbox_item_length_limit(self) -> None:
        """Test that text longer than 500 characters raises validation error."""
        long_text = "a" * 501
        with pytest.raises(ValidationError) as exc_info:
            InboxItem(text=long_text)
        assert "must be 500 characters or less" in str(exc_info.value)

    def test_inbox_item_length_at_limit(self) -> None:
        """Test that text at 500 characters is valid."""
        text_at_limit = "a" * 500
        item = InboxItem(text=text_at_limit)
        assert len(item.text) == 500


class TestNewProject:
    """Test NewProject Pydantic model."""

    def test_new_project_creation(self) -> None:
        """Test creating a new project."""
        project = NewProject(
            project_name="Company Retreat Planning",
            outcome="Successfully execute a team-building company retreat",
            first_next_action="Research potential venue locations",
            context=GTDContext.COMPUTER,
            reasoning="Complex multi-step initiative requiring coordination",
        )
        assert project.project_name == "Company Retreat Planning"
        assert project.outcome == "Successfully execute a team-building company retreat"
        assert project.first_next_action == "Research potential venue locations"
        assert project.context == GTDContext.COMPUTER
        assert (
            project.reasoning == "Complex multi-step initiative requiring coordination"
        )

    def test_new_project_without_context(self) -> None:
        """Test creating project without context."""
        project = NewProject(
            project_name="Website Redesign",
            outcome="Launch new company website",
            first_next_action="Meet with design team",
            reasoning="Major initiative spanning multiple months",
        )
        assert project.context is None


class TestExistingProject:
    """Test ExistingProject Pydantic model."""

    def test_existing_project_creation(self) -> None:
        """Test creating existing project association."""
        project = ExistingProject(
            project_name="Q4 Marketing Campaign",
            relevance_score=0.85,
            reasoning="This task directly supports the campaign goals",
            suggested_action="Create social media content calendar",
        )
        assert project.project_name == "Q4 Marketing Campaign"
        assert project.relevance_score == 0.85
        assert project.reasoning == "This task directly supports the campaign goals"
        assert project.suggested_action == "Create social media content calendar"

    def test_existing_project_without_action(self) -> None:
        """Test existing project without suggested action."""
        project = ExistingProject(
            project_name="Budget Review",
            relevance_score=0.75,
            reasoning="Related to ongoing budget analysis",
            suggested_action=None,
        )
        assert project.suggested_action is None

    def test_existing_project_relevance_score_validation(self) -> None:
        """Test relevance score validation."""
        # Test below range
        with pytest.raises(ValidationError) as exc_info:
            ExistingProject(
                project_name="Test",
                relevance_score=-0.1,
                reasoning="Test",
                suggested_action=None,
            )
        assert "must be between 0.0 and 1.0" in str(exc_info.value)

        # Test above range
        with pytest.raises(ValidationError) as exc_info:
            ExistingProject(
                project_name="Test",
                relevance_score=1.1,
                reasoning="Test",
                suggested_action=None,
            )
        assert "must be between 0.0 and 1.0" in str(exc_info.value)

        # Test valid range
        project = ExistingProject(
            project_name="Test",
            relevance_score=0.5,
            reasoning="Test",
            suggested_action=None,
        )
        assert project.relevance_score == 0.5


class TestCategorization:
    """Test Categorization Pydantic model."""

    def test_simple_categorization(self) -> None:
        """Test simple categorization without project relationships."""
        categorization = Categorization(
            item="Call insurance company",
            actionable=True,
            category=GTDCategory.NEXT_ACTION,
            suggested_text="Call insurance company about policy renewal",
            context=GTDContext.CALLS,
            creates_new_project=False,
            new_project=None,
            associates_existing_project=False,
            existing_project=None,
            confidence=ConfidenceLevel.HIGH,
            reasoning="Clear actionable task requiring a phone call",
            time_estimate=None,
            energy_level=None,
            delegated_to=None,
        )
        assert categorization.item == "Call insurance company"
        assert categorization.actionable is True
        assert categorization.category == GTDCategory.NEXT_ACTION
        assert categorization.context == GTDContext.CALLS
        assert categorization.creates_new_project is False
        assert categorization.associates_existing_project is False

    def test_categorization_with_new_project(self) -> None:
        """Test categorization that creates a new project."""
        new_project = NewProject(
            project_name="Office Relocation",
            outcome="Successfully relocate office by Q2",
            first_next_action="Research commercial real estate options",
            context=GTDContext.COMPUTER,
            reasoning="Multi-month complex initiative",
        )

        categorization = Categorization(
            item="Plan office move",
            actionable=True,
            category=GTDCategory.NEXT_ACTION,
            suggested_text=None,
            context=None,
            creates_new_project=True,
            new_project=new_project,
            associates_existing_project=False,
            existing_project=None,
            confidence=ConfidenceLevel.HIGH,
            reasoning="Complex initiative requiring project planning",
            time_estimate=None,
            energy_level=None,
            delegated_to=None,
        )
        assert categorization.creates_new_project is True
        assert categorization.new_project == new_project
        assert categorization.associates_existing_project is False

    def test_categorization_with_existing_project(self) -> None:
        """Test categorization that associates with existing project."""
        existing_project = ExistingProject(
            project_name="Website Redesign",
            relevance_score=0.9,
            reasoning="Directly related to website content updates",
            suggested_action="Update product descriptions on website",
        )

        categorization = Categorization(
            item="Update product descriptions",
            actionable=True,
            category=GTDCategory.NEXT_ACTION,
            suggested_text=None,
            context=None,
            creates_new_project=False,
            new_project=None,
            associates_existing_project=True,
            existing_project=existing_project,
            confidence=ConfidenceLevel.HIGH,
            reasoning="Supports ongoing website redesign project",
            time_estimate=None,
            energy_level=None,
            delegated_to=None,
        )
        assert categorization.associates_existing_project is True
        assert categorization.existing_project == existing_project
        assert categorization.creates_new_project is False

    def test_categorization_empty_reasoning_validation(self) -> None:
        """Test that empty reasoning raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test item",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=None,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        assert "Reasoning must be provided" in str(exc_info.value)

    def test_categorization_new_project_consistency(self) -> None:
        """Test validation of new project consistency."""
        # Test missing new_project when creates_new_project is True
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=True,
                new_project=None,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        assert "new_project must be provided when creates_new_project is True" in str(
            exc_info.value
        )

        # Test unexpected new_project when creates_new_project is False
        new_project = NewProject(
            project_name="Test",
            outcome="Test",
            first_next_action="Test",
            reasoning="Test",
        )
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=new_project,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        assert "new_project should be None when creates_new_project is False" in str(
            exc_info.value
        )

    def test_categorization_existing_project_consistency(self) -> None:
        """Test validation of existing project consistency."""
        # Test missing existing_project when associates_existing_project is True
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=None,
                associates_existing_project=True,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        assert (
            "existing_project must be provided when associates_existing_project is True"
            in str(exc_info.value)
        )

    def test_categorization_mutual_exclusivity(self) -> None:
        """Test that new and existing project associations are mutually exclusive."""
        new_project = NewProject(
            project_name="Test",
            outcome="Test",
            first_next_action="Test",
            reasoning="Test",
        )
        existing_project = ExistingProject(
            project_name="Test",
            relevance_score=0.5,
            reasoning="Test",
            suggested_action=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=True,
                new_project=new_project,
                associates_existing_project=True,
                existing_project=existing_project,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        assert (
            "Cannot both create new project and associate with existing project"
            in str(exc_info.value)
        )

    def test_categorization_time_estimate_validation(self) -> None:
        """Test time estimate validation."""
        # Test below range
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=None,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=0,
                energy_level=None,
                delegated_to=None,
            )
        assert "must be between 1 and 480 minutes" in str(exc_info.value)

        # Test above range
        with pytest.raises(ValidationError) as exc_info:
            Categorization(
                item="Test",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=None,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test",
                time_estimate=500,
                energy_level=None,
                delegated_to=None,
            )
        assert "must be between 1 and 480 minutes" in str(exc_info.value)

        # Test valid range
        categorization = Categorization(
            item="Test",
            actionable=True,
            category=None,
            suggested_text=None,
            context=None,
            creates_new_project=False,
            new_project=None,
            associates_existing_project=False,
            existing_project=None,
            confidence=ConfidenceLevel.HIGH,
            reasoning="Test",
            time_estimate=30,
            energy_level=None,
            delegated_to=None,
        )
        assert categorization.time_estimate == 30


class TestItemGroup:
    """Test ItemGroup Pydantic model."""

    def test_item_group_creation(self) -> None:
        """Test creating an item group."""
        items = [
            InboxItem(text="Book conference room"),
            InboxItem(text="Send meeting invites"),
            InboxItem(text="Prepare agenda"),
        ]

        group = ItemGroup(
            items=items,
            group_type="project",
            description="Meeting preparation tasks",
            suggested_project="Q1 Planning Meeting",
            processing_order=[2, 0, 1],
        )
        assert len(group.items) == 3
        assert group.group_type == "project"
        assert group.description == "Meeting preparation tasks"
        assert group.suggested_project == "Q1 Planning Meeting"
        assert group.processing_order == [2, 0, 1]

    def test_item_group_empty_items_validation(self) -> None:
        """Test that empty items list raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            ItemGroup(
                items=[],
                group_type="test",
                description="test",
                suggested_project=None,
            )
        assert "Item group must contain at least one item" in str(exc_info.value)

    def test_item_group_items_limit(self) -> None:
        """Test that more than 20 items raises validation error."""
        items = [InboxItem(text=f"Item {i}") for i in range(21)]
        with pytest.raises(ValidationError) as exc_info:
            ItemGroup(
                items=items,
                group_type="test",
                description="test",
                suggested_project=None,
            )
        assert "cannot contain more than 20 items" in str(exc_info.value)

    def test_item_group_processing_order_validation(self) -> None:
        """Test processing order validation."""
        items = [
            InboxItem(text="Item 1"),
            InboxItem(text="Item 2"),
            InboxItem(text="Item 3"),
        ]

        # Test invalid index
        with pytest.raises(ValidationError) as exc_info:
            ItemGroup(
                items=items,
                group_type="test",
                description="test",
                suggested_project=None,
                processing_order=[0, 1, 5],  # Index 5 doesn't exist
            )
        assert "Processing order indices must be valid item indices" in str(
            exc_info.value
        )

        # Test negative index
        with pytest.raises(ValidationError) as exc_info:
            ItemGroup(
                items=items,
                group_type="test",
                description="test",
                suggested_project=None,
                processing_order=[-1, 0, 1],
            )
        assert "Processing order indices must be valid item indices" in str(
            exc_info.value
        )

        # Test valid processing order
        group = ItemGroup(
            items=items,
            group_type="test",
            description="test",
            suggested_project=None,
            processing_order=[2, 0, 1],
        )
        assert group.processing_order == [2, 0, 1]


class TestBatchProcessingResult:
    """Test BatchProcessingResult Pydantic model."""

    def test_batch_processing_result_creation(self) -> None:
        """Test creating batch processing result."""
        categorizations = [
            Categorization(
                item="Test item",
                actionable=True,
                category=None,
                suggested_text=None,
                context=None,
                creates_new_project=False,
                new_project=None,
                associates_existing_project=False,
                existing_project=None,
                confidence=ConfidenceLevel.HIGH,
                reasoning="Test reasoning",
                time_estimate=None,
                energy_level=None,
                delegated_to=None,
            )
        ]

        result = BatchProcessingResult(
            categorizations=categorizations,
            processing_summary="Processed 1 item successfully",
        )
        assert len(result.categorizations) == 1
        assert result.processing_summary == "Processed 1 item successfully"
        assert len(result.groups) == 0

    def test_batch_processing_result_empty_categorizations(self) -> None:
        """Test that empty categorizations raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BatchProcessingResult(categorizations=[], processing_summary="Test")
        assert "Batch processing must contain at least one categorization" in str(
            exc_info.value
        )
