"""Test GTDFrontmatter Pydantic conversion functionality."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from md_gtd_mcp.models import GTDFrontmatter


class TestGTDFrontmatterPydantic:
    """Test GTDFrontmatter Pydantic BaseModel functionality."""

    def test_pydantic_model_creation(self) -> None:
        """Test creating GTDFrontmatter as Pydantic model."""
        frontmatter = GTDFrontmatter(
            outcome="Complete project successfully",
            status="active",
            area="Personal",
            review_date=datetime(2025, 1, 15),
            created_date=datetime(2025, 1, 1),
            tags=["important", "quarterly"],
            extra={"custom": "value"},
        )
        assert frontmatter.outcome == "Complete project successfully"
        assert frontmatter.status == "active"
        assert frontmatter.area == "Personal"
        assert frontmatter.review_date == datetime(2025, 1, 15)
        assert frontmatter.tags == ["important", "quarterly"]
        assert frontmatter.extra == {"custom": "value"}

    def test_model_dump_for_mcp_serialization(self) -> None:
        """Test model_dump() method for MCP tool serialization."""
        frontmatter = GTDFrontmatter(
            outcome="Complete project successfully",
            status="active",
            area="Personal",
            review_date=datetime(2025, 1, 15),
            created_date=datetime(2025, 1, 1),
            tags=["important", "quarterly"],
            extra={"custom": "value"},
        )

        # Test model_dump() returns proper dict for JSON serialization
        dumped = frontmatter.model_dump()
        expected = {
            "outcome": "Complete project successfully",
            "status": "active",
            "area": "Personal",
            "review_date": datetime(2025, 1, 15),
            "created_date": datetime(2025, 1, 1),
            "completed_date": None,
            "tags": ["important", "quarterly"],
            "extra": {"custom": "value"},
        }
        assert dumped == expected

    def test_model_dump_json_serializable(self) -> None:
        """Test model_dump() with datetime serialization for JSON."""
        frontmatter = GTDFrontmatter(
            outcome="Complete project successfully",
            review_date=datetime(2025, 1, 15),
            created_date=datetime(2025, 1, 1),
        )

        # Test model_dump() with serialization mode for JSON compatibility
        dumped = frontmatter.model_dump(mode="json")
        assert isinstance(dumped["review_date"], str)
        assert isinstance(dumped["created_date"], str)
        assert dumped["review_date"] == "2025-01-15T00:00:00"
        assert dumped["created_date"] == "2025-01-01T00:00:00"

    def test_model_validation_with_invalid_data(self) -> None:
        """Test Pydantic validation with invalid data types."""
        with pytest.raises(ValidationError) as exc_info:
            GTDFrontmatter(
                tags="not a list",  # type: ignore[arg-type]  # Should be list[str]
                review_date="invalid date",  # type: ignore[arg-type]  # Should be datetime
            )

        errors = exc_info.value.errors()
        assert len(errors) >= 2

        # Check for tags validation error
        tags_error = next((e for e in errors if e["loc"] == ("tags",)), None)
        assert tags_error is not None
        assert "list" in tags_error["msg"].lower()

        # Check for date validation error
        date_error = next((e for e in errors if e["loc"] == ("review_date",)), None)
        assert date_error is not None

    def test_model_with_partial_data(self) -> None:
        """Test creating model with partial data (defaults work)."""
        frontmatter = GTDFrontmatter(outcome="Test outcome")

        # Test defaults are applied correctly
        assert frontmatter.outcome == "Test outcome"
        assert frontmatter.status is None
        assert frontmatter.area is None
        assert frontmatter.review_date is None
        assert frontmatter.created_date is None
        assert frontmatter.completed_date is None
        assert frontmatter.tags == []
        assert frontmatter.extra == {}

    def test_datetime_field_handling(self) -> None:
        """Test datetime field parsing and validation."""
        # Test with datetime objects
        now = datetime.now()
        frontmatter = GTDFrontmatter(
            created_date=now,
            review_date=now,
            completed_date=now,
        )
        assert frontmatter.created_date == now
        assert frontmatter.review_date == now
        assert frontmatter.completed_date == now

    def test_extra_field_preserves_additional_data(self) -> None:
        """Test that extra field preserves unknown frontmatter properties."""
        extra_data = {
            "priority": "high",
            "effort": "medium",
            "context": ["@office", "@computer"],
            "nested": {"deep": {"value": 42}},
        }

        frontmatter = GTDFrontmatter(
            outcome="Test project",
            extra=extra_data,
        )

        assert frontmatter.extra == extra_data

        # Test that extra data is preserved in model_dump
        dumped = frontmatter.model_dump()
        assert dumped["extra"] == extra_data

    def test_model_json_schema_generation(self) -> None:
        """Test that Pydantic generates JSON schema for MCP."""
        schema = GTDFrontmatter.model_json_schema()

        # Verify schema has required structure
        assert "type" in schema
        assert schema["type"] == "object"
        assert "properties" in schema

        # Check key properties are defined
        properties = schema["properties"]
        assert "outcome" in properties
        assert "status" in properties
        assert "tags" in properties
        assert "extra" in properties

        # Verify tags is properly defined as array
        assert properties["tags"]["type"] == "array"
        assert properties["tags"]["items"]["type"] == "string"

    def test_backwards_compatibility_with_existing_usage(self) -> None:
        """Test that existing code patterns still work after Pydantic conversion."""
        # Test that all existing usage patterns from the current tests still work

        # Pattern 1: Simple creation
        frontmatter = GTDFrontmatter()
        assert frontmatter.outcome is None
        assert frontmatter.tags == []

        # Pattern 2: Creation with keyword args
        frontmatter = GTDFrontmatter(
            outcome="Complete project successfully",
            status="active",
            area="Personal",
            review_date=datetime(2025, 1, 15),
            tags=["important"],
        )
        assert frontmatter.outcome == "Complete project successfully"
        assert frontmatter.status == "active"

        # Pattern 3: Attribute access
        assert frontmatter.area == "Personal"
        assert frontmatter.review_date == datetime(2025, 1, 15)
