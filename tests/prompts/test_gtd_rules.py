"""Tests for GTD static rule engine and methodology constants."""

from md_gtd_mcp.prompts.gtd_rules import (
    GTDDecisionTree,
    GTDMethodology,
    GTDPatterns,
    GTDRuleEngine,
)


class TestGTDMethodology:
    """Test GTD methodology constants and questions."""

    def test_clarifying_questions_format(self) -> None:
        """Test that GTD clarifying questions are properly formatted."""
        questions = GTDMethodology.CLARIFYING_QUESTIONS

        # Should have all essential GTD questions
        assert len(questions) >= 5

        # Check for key actionability questions
        actionability_found = any(
            "actionable" in q.lower() or "action" in q.lower() for q in questions
        )
        assert actionability_found, "Should include actionability questions"

        # Check for outcome questions
        outcome_found = any(
            "outcome" in q.lower() or "successful" in q.lower() for q in questions
        )
        assert outcome_found, "Should include outcome questions"

        # Check for next action questions
        next_action_found = any(
            "next" in q.lower() and "action" in q.lower() for q in questions
        )
        assert next_action_found, "Should include next action questions"

    def test_clarifying_questions_completeness(self) -> None:
        """Test that clarifying questions cover all GTD decision points."""
        questions = GTDMethodology.CLARIFYING_QUESTIONS

        # Should include the core GTD clarifying questions
        expected_themes = [
            "actionable",  # Is it actionable?
            "outcome",  # What's the successful outcome?
            "next",  # What's the next action?
            "context",  # What context is needed?
            "time",  # How long will it take?
        ]

        for theme in expected_themes:
            theme_found = any(theme in q.lower() for q in questions)
            assert theme_found, f"Should include questions about {theme}"

    def test_category_descriptions_structure(self) -> None:
        """Test that category descriptions are properly structured."""
        descriptions = GTDMethodology.CATEGORY_DESCRIPTIONS

        # Should have descriptions for all GTD categories
        required_categories = [
            "next-action",
            "project",
            "waiting-for",
            "someday-maybe",
            "reference",
            "trash",
        ]

        for category in required_categories:
            assert category in descriptions, f"Missing description for {category}"
            assert isinstance(descriptions[category], str)
            assert len(descriptions[category]) > 0
            assert descriptions[category].strip() == descriptions[category]

    def test_context_definitions_structure(self) -> None:
        """Test that context definitions are properly structured."""
        definitions = GTDMethodology.CONTEXT_DEFINITIONS

        # Should have definitions for common GTD contexts
        expected_contexts = ["@home", "@computer", "@calls", "@errands", "@office"]

        for context in expected_contexts:
            assert context in definitions, f"Missing definition for {context}"
            assert isinstance(definitions[context], str)
            assert len(definitions[context]) > 0

    def test_gtd_phases_structure(self) -> None:
        """Test that GTD phases are properly defined."""
        phases = GTDMethodology.GTD_PHASES

        # Should have all 5 GTD phases
        expected_phases = ["capture", "clarify", "organize", "reflect", "engage"]

        for phase in expected_phases:
            assert phase in phases, f"Missing GTD phase: {phase}"
            assert isinstance(phases[phase], str)
            assert len(phases[phase]) > 0


class TestGTDDecisionTree:
    """Test GTD decision tree text generation."""

    def test_decision_tree_text_generation(self) -> None:
        """Test that decision tree generates properly formatted text."""
        tree_text = GTDDecisionTree.generate_decision_tree()

        assert isinstance(tree_text, str)
        assert len(tree_text) > 100, "Decision tree should be substantial"

        # Should include key decision points
        assert "actionable" in tree_text.lower()
        assert "project" in tree_text.lower()
        assert "next action" in tree_text.lower()
        assert "waiting" in tree_text.lower()

        # Should be well-formatted
        assert tree_text.strip() == tree_text
        lines = tree_text.split("\n")
        assert len(lines) > 5, "Should have multiple lines"

    def test_decision_tree_includes_2_minute_rule(self) -> None:
        """Test that decision tree includes the 2-minute rule."""
        tree_text = GTDDecisionTree.generate_decision_tree()

        assert "2 minute" in tree_text.lower() or "two minute" in tree_text.lower()

    def test_decision_tree_includes_delegation(self) -> None:
        """Test that decision tree includes delegation logic."""
        tree_text = GTDDecisionTree.generate_decision_tree()

        delegation_terms = ["delegate", "waiting", "someone else"]
        delegation_found = any(term in tree_text.lower() for term in delegation_terms)
        assert delegation_found, "Decision tree should include delegation concepts"

    def test_quick_reference_generation(self) -> None:
        """Test that quick reference generates concise text."""
        quick_ref = GTDDecisionTree.generate_quick_reference()

        assert isinstance(quick_ref, str)
        assert len(quick_ref) > 50
        assert len(quick_ref) < 500, "Quick reference should be concise"

        # Should include essential categories
        assert "next-action" in quick_ref.lower() or "next action" in quick_ref.lower()
        assert "project" in quick_ref.lower()
        assert "waiting" in quick_ref.lower()


class TestGTDPatterns:
    """Test GTD keyword pattern dictionaries."""

    def test_context_patterns_structure(self) -> None:
        """Test that context patterns are properly structured."""
        patterns = GTDPatterns.CONTEXT_PATTERNS

        # Should have patterns for common contexts
        expected_contexts = ["@calls", "@computer", "@home", "@errands", "@office"]

        for context in expected_contexts:
            assert context in patterns, f"Missing patterns for {context}"
            assert isinstance(patterns[context], list)
            assert len(patterns[context]) > 0

            # All patterns should be strings
            for pattern in patterns[context]:
                assert isinstance(pattern, str)
                assert len(pattern) > 0
                assert pattern.lower() == pattern, "Patterns should be lowercase"

    def test_context_patterns_content(self) -> None:
        """Test that context patterns contain logical keywords."""
        patterns = GTDPatterns.CONTEXT_PATTERNS

        # @calls should include phone-related terms
        calls_patterns = patterns["@calls"]
        phone_terms = ["call", "phone", "dial"]
        assert any(term in calls_patterns for term in phone_terms)

        # @computer should include computer-related terms
        computer_patterns = patterns["@computer"]
        computer_terms = ["email", "write", "code", "research"]
        assert any(term in computer_patterns for term in computer_terms)

        # @errands should include shopping/errand terms
        errands_patterns = patterns["@errands"]
        errand_terms = ["buy", "shop", "pick up", "store"]
        assert any(term in errands_patterns for term in errand_terms)

    def test_two_minute_indicators_structure(self) -> None:
        """Test that 2-minute rule indicators are properly structured."""
        indicators = GTDPatterns.TWO_MINUTE_INDICATORS

        assert isinstance(indicators, list)
        assert len(indicators) > 0

        # Should include common quick task indicators
        expected_indicators = ["quick", "simple", "brief", "fast"]
        for indicator in expected_indicators:
            assert indicator in indicators, f"Missing 2-minute indicator: {indicator}"

        # All should be lowercase strings
        for indicator in indicators:
            assert isinstance(indicator, str)
            assert indicator.lower() == indicator

    def test_project_indicators_structure(self) -> None:
        """Test that project indicators are properly structured."""
        indicators = GTDPatterns.PROJECT_INDICATORS

        assert isinstance(indicators, list)
        assert len(indicators) > 0

        # Should include common project indicators
        expected_indicators = ["project", "implement", "develop", "create", "build"]
        for indicator in expected_indicators:
            assert indicator in indicators, f"Missing project indicator: {indicator}"

    def test_delegation_patterns_structure(self) -> None:
        """Test that delegation patterns are properly structured."""
        patterns = GTDPatterns.DELEGATION_PATTERNS

        assert isinstance(patterns, list)
        assert len(patterns) > 0

        # Should include common delegation indicators
        expected_patterns = ["waiting", "pending", "assigned", "delegated"]
        for pattern in expected_patterns:
            assert pattern in patterns, f"Missing delegation pattern: {pattern}"


class TestGTDRuleEngine:
    """Test GTD rule engine functions and utilities."""

    def test_rule_engine_initialization(self) -> None:
        """Test that rule engine can be initialized."""
        engine = GTDRuleEngine()
        assert engine is not None

    def test_get_context_patterns(self) -> None:
        """Test getting context patterns from rule engine."""
        engine = GTDRuleEngine()
        patterns = engine.get_context_patterns()

        assert isinstance(patterns, dict)
        assert "@calls" in patterns
        assert "@computer" in patterns
        assert len(patterns) > 0

    def test_get_clarifying_questions(self) -> None:
        """Test getting clarifying questions from rule engine."""
        engine = GTDRuleEngine()
        questions = engine.get_clarifying_questions()

        assert isinstance(questions, list)
        assert len(questions) > 0

        # Should return the same as methodology constant
        assert questions == GTDMethodology.CLARIFYING_QUESTIONS

    def test_get_decision_tree(self) -> None:
        """Test getting decision tree from rule engine."""
        engine = GTDRuleEngine()
        tree = engine.get_decision_tree()

        assert isinstance(tree, str)
        assert len(tree) > 0
        assert "actionable" in tree.lower()

    def test_build_prompt_context(self) -> None:
        """Test building prompt context with GTD rules."""
        engine = GTDRuleEngine()
        context = engine.build_prompt_context()

        assert isinstance(context, dict)

        # Should include all essential components
        assert "clarifying_questions" in context
        assert "decision_tree" in context
        assert "context_patterns" in context
        assert "category_descriptions" in context

        # Components should be properly typed
        assert isinstance(context["clarifying_questions"], list)
        assert isinstance(context["decision_tree"], str)
        assert isinstance(context["context_patterns"], dict)
        assert isinstance(context["category_descriptions"], dict)

    def test_validate_category(self) -> None:
        """Test category validation function."""
        engine = GTDRuleEngine()

        # Valid categories should return True
        valid_categories = [
            "next-action",
            "project",
            "waiting-for",
            "someday-maybe",
            "reference",
            "trash",
        ]

        for category in valid_categories:
            assert engine.validate_category(category), (
                f"Category {category} should be valid"
            )

        # Invalid categories should return False
        invalid_categories = ["invalid", "", "next_action", "project-task"]

        for category in invalid_categories:
            assert not engine.validate_category(category), (
                f"Category {category} should be invalid"
            )

    def test_validate_context(self) -> None:
        """Test context validation function."""
        engine = GTDRuleEngine()

        # Valid contexts should return True
        valid_contexts = ["@home", "@computer", "@calls", "@errands", "@office"]

        for context in valid_contexts:
            assert engine.validate_context(context), (
                f"Context {context} should be valid"
            )

        # Invalid contexts should return False
        invalid_contexts = ["home", "@invalid", "", "computer"]

        for context in invalid_contexts:
            assert not engine.validate_context(context), (
                f"Context {context} should be invalid"
            )

    def test_suggest_contexts_for_text(self) -> None:
        """Test context suggestion based on text content."""
        engine = GTDRuleEngine()

        # Test phone-related text
        phone_text = "Call the insurance company about policy"
        suggested = engine.suggest_contexts_for_text(phone_text)
        assert "@calls" in suggested or "@phone" in suggested

        # Test computer-related text
        computer_text = "Send email to team about project update"
        suggested = engine.suggest_contexts_for_text(computer_text)
        assert "@computer" in suggested

        # Test errand-related text
        errand_text = "Buy groceries from the store"
        suggested = engine.suggest_contexts_for_text(errand_text)
        assert "@errands" in suggested

        # Test text with no clear context
        unclear_text = "Think about vacation plans"
        suggested = engine.suggest_contexts_for_text(unclear_text)
        # Should return empty list or @anywhere
        assert isinstance(suggested, list)
