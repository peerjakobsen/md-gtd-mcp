"""Tests for GTD static rule engine and methodology constants."""

import pytest

from md_gtd_mcp.prompts.gtd_rules import (
    GTDDecisionTree,
    GTDDocumentation,
    GTDMethodology,
    GTDPatterns,
    GTDPromptBuilder,
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

    @pytest.mark.slow
    def test_rule_engine_initialization(self) -> None:
        """Test that rule engine can be initialized."""
        engine = GTDRuleEngine()
        assert engine is not None

    @pytest.mark.slow
    def test_get_context_patterns(self) -> None:
        """Test getting context patterns from rule engine."""
        engine = GTDRuleEngine()
        patterns = engine.get_context_patterns()

        assert isinstance(patterns, dict)
        assert "@calls" in patterns
        assert "@computer" in patterns
        assert len(patterns) > 0

    @pytest.mark.slow
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

    @pytest.mark.slow
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


class TestKeywordPatternMatching:
    """Test simple keyword pattern matching functionality (Task 2.3)."""

    def test_context_keyword_pattern_dictionaries(self) -> None:
        """Test context keyword pattern dictionaries structure."""
        patterns = GTDPatterns.CONTEXT_PATTERNS

        # Test basic structure
        assert isinstance(patterns, dict)
        assert len(patterns) > 0

        # Test all contexts have keyword lists
        for context, keywords in patterns.items():
            assert isinstance(keywords, list)
            assert len(keywords) > 0
            assert context.startswith("@"), f"Context {context} should start with @"

            # All keywords should be strings and lowercase
            for keyword in keywords:
                assert isinstance(keyword, str)
                assert len(keyword) > 0
                assert keyword == keyword.lower(), (
                    f"Keyword '{keyword}' should be lowercase"
                )

    @pytest.mark.slow
    def test_pattern_lookup_functions_basic(self) -> None:
        """Test basic pattern lookup functions (string-in-list operations)."""
        engine = GTDRuleEngine()

        # Test exact keyword matches
        test_cases = [
            ("call mom", ["@calls"]),
            ("send email", ["@computer"]),
            ("buy milk", ["@errands"]),
            ("work meeting", ["@office"]),
            ("home maintenance", ["@home"]),
        ]

        for text, expected_contexts in test_cases:
            suggested = engine.suggest_contexts_for_text(text)
            for expected in expected_contexts:
                assert expected in suggested, f"Text '{text}' should suggest {expected}"

    @pytest.mark.slow
    def test_multiple_pattern_matching_overlapping_contexts(self) -> None:
        """Test multiple pattern matching for overlapping contexts."""
        engine = GTDRuleEngine()

        # Test cases that should match multiple contexts
        overlapping_cases = [
            ("call work about meeting", ["@calls", "@office"]),
            ("email from home computer", ["@computer", "@home"]),
            ("phone app research", ["@phone", "@computer"]),
            ("buy work supplies", ["@errands", "@office"]),
        ]

        for text, expected_contexts in overlapping_cases:
            suggested = engine.suggest_contexts_for_text(text)
            # Should find at least one of the expected contexts
            found_any = any(ctx in suggested for ctx in expected_contexts)
            assert found_any, (
                f"Text '{text}' should match at least one of {expected_contexts}, "
                f"got {suggested}"
            )

    def test_pattern_case_insensitivity(self) -> None:
        """Test pattern case-insensitivity."""
        engine = GTDRuleEngine()

        # Test same text with different cases
        test_cases = [
            "CALL the client",
            "Call the client",
            "call the client",
            "CaLl ThE cLiEnT",
        ]

        # All should produce the same result
        first_result = engine.suggest_contexts_for_text(test_cases[0])
        assert "@calls" in first_result or "@phone" in first_result

        for text in test_cases[1:]:
            result = engine.suggest_contexts_for_text(text)
            # Should contain same contexts (order doesn't matter)
            assert set(result) == set(first_result), (
                f"Case variation '{text}' should give same result"
            )

    def test_pattern_matching_edge_cases(self) -> None:
        """Test pattern matching edge cases."""
        engine = GTDRuleEngine()

        # Empty string
        result = engine.suggest_contexts_for_text("")
        assert result == []

        # Only whitespace
        result = engine.suggest_contexts_for_text("   ")
        assert result == []

        # No matching patterns
        result = engine.suggest_contexts_for_text("xyz abc def")
        assert isinstance(result, list)

        # Very long text with patterns
        long_text = "This is a very long text " * 50 + " call someone"
        result = engine.suggest_contexts_for_text(long_text)
        assert "@calls" in result or "@phone" in result

    def test_partial_word_matching(self) -> None:
        """Test that patterns match within words appropriately."""
        engine = GTDRuleEngine()

        # Should match patterns within larger words
        test_cases = [
            ("telephone call", "@calls"),
            ("research project", "@computer"),
            ("shopping list", "@errands"),
        ]

        for text, expected_context in test_cases:
            suggested = engine.suggest_contexts_for_text(text)
            assert expected_context in suggested, (
                f"Text '{text}' should suggest {expected_context}"
            )

    def test_pattern_priority_no_duplicates(self) -> None:
        """Test that each context appears only once in suggestions."""
        engine = GTDRuleEngine()

        # Text that could match same context multiple times
        text = "call phone telephone contact"  # Multiple @calls triggers
        suggested = engine.suggest_contexts_for_text(text)

        # Should not have duplicates
        assert len(suggested) == len(set(suggested)), (
            "Should not have duplicate contexts"
        )
        assert "@calls" in suggested or "@phone" in suggested

    def test_context_pattern_completeness(self) -> None:
        """Test that all defined contexts have meaningful patterns."""
        patterns = GTDPatterns.CONTEXT_PATTERNS

        # Each context should have reasonable number of patterns
        for context, keywords in patterns.items():
            assert len(keywords) >= 3, (
                f"Context {context} should have at least 3 keywords"
            )

            # No empty or whitespace-only keywords
            for keyword in keywords:
                assert keyword.strip() == keyword, (
                    f"Keyword '{keyword}' should not have extra whitespace"
                )
                assert len(keyword.strip()) > 0, "Keyword should not be empty"

    def test_suggest_contexts_return_type_consistency(self) -> None:
        """Test that suggest_contexts_for_text always returns consistent types."""
        engine = GTDRuleEngine()

        test_inputs = [
            "call someone",
            "",
            "no matches here xyz",
            "multiple call email errands",
            "UPPERCASE TEXT",
        ]

        for text in test_inputs:
            result = engine.suggest_contexts_for_text(text)
            assert isinstance(result, list), f"Should always return list for '{text}'"
            for item in result:
                assert isinstance(item, str), (
                    f"All items should be strings for '{text}'"
                )
                assert item.startswith("@"), (
                    f"All contexts should start with @ for '{text}'"
                )


class TestGTDDocumentation:
    """Test GTD methodology documentation with pattern matching integration."""

    def test_decision_tree_with_pattern_integration(self) -> None:
        """Test decision tree includes pattern matching integration points."""
        decision_tree = GTDDocumentation.get_decision_tree_with_pattern_integration()

        # Verify core GTD decision nodes are present
        assert "ACTIONABILITY ASSESSMENT" in decision_tree
        assert "OUTCOME ASSESSMENT" in decision_tree
        assert "TIME ASSESSMENT" in decision_tree
        assert "RESPONSIBILITY ASSESSMENT" in decision_tree
        assert "CONTEXT ASSIGNMENT" in decision_tree

        # Verify pattern matching integration points
        assert "spaCy" in decision_tree
        assert "rapidfuzz" in decision_tree
        assert "textstat" in decision_tree

        # Verify library-specific usage guidance
        assert "threshold:" in decision_tree.lower()
        assert "linguistic analysis" in decision_tree.lower()
        assert "fuzzy matching" in decision_tree.lower()

        # Verify performance characteristics mentioned
        assert "performance" in decision_tree.lower()
        assert "offline" in decision_tree.lower()

    def test_category_descriptions_with_thresholds(self) -> None:
        """Test category descriptions include pattern matching thresholds."""
        categories = GTDDocumentation.get_category_descriptions_with_thresholds()

        # Verify all GTD categories are present
        expected_categories = {
            "next-action",
            "project",
            "waiting-for",
            "someday-maybe",
            "reference",
            "trash",
        }
        assert set(categories.keys()) == expected_categories

        # Test next-action category structure
        next_action = categories["next-action"]
        assert "description" in next_action
        assert "pattern_matching" in next_action
        assert "confidence_thresholds" in next_action
        assert "context_assignment" in next_action
        assert "validation_rules" in next_action
        assert "common_patterns" in next_action

        # Test confidence thresholds structure
        thresholds = next_action["confidence_thresholds"]
        assert "spacy_linguistic" in thresholds
        assert "rapidfuzz_fuzzy" in thresholds
        assert "textstat_complexity" in thresholds
        assert "combined_minimum" in thresholds

        # Verify threshold values are reasonable
        assert 0.0 <= thresholds["spacy_linguistic"] <= 1.0
        assert 0.0 <= thresholds["rapidfuzz_fuzzy"] <= 1.0
        assert 0.0 <= thresholds["combined_minimum"] <= 1.0

    def test_context_pattern_strategies(self) -> None:
        """Test context definitions mapped to pattern detection strategies."""
        contexts = GTDDocumentation.get_context_pattern_strategies()

        # Verify all standard GTD contexts are present
        expected_contexts = {
            "@calls",
            "@computer",
            "@home",
            "@office",
            "@errands",
            "@anywhere",
        }
        assert set(contexts.keys()) == expected_contexts

        # Test @calls context structure
        calls_context = contexts["@calls"]
        assert "definition" in calls_context
        assert "detection_strategy" in calls_context
        assert "pattern_approaches" in calls_context
        assert "hybrid_detection" in calls_context
        assert "use_cases" in calls_context

        # Test detection strategy structure
        strategy = calls_context["detection_strategy"]
        assert "primary_method" in strategy
        assert "secondary_method" in strategy
        assert "validation_method" in strategy

        # Test pattern approaches include all three libraries
        approaches = calls_context["pattern_approaches"]
        assert "rapidfuzz" in approaches
        assert "spacy" in approaches
        assert (
            "textstat" in approaches
            or "automatic" in approaches
            or "temporal" in approaches
        )

        # Test performance data is included
        for approach_data in approaches.values():
            assert "performance" in approach_data

    def test_prompt_template_utilities(self) -> None:
        """Test prompt template building utilities structure."""
        utilities = GTDDocumentation.get_prompt_template_utilities()

        # Verify main utility categories
        assert "pattern_to_prompt_converters" in utilities
        assert "prompt_optimization_strategies" in utilities
        assert "claude_guidance_integration" in utilities
        assert "prompt_template_examples" in utilities

        # Test converter structure
        converters = utilities["pattern_to_prompt_converters"]
        assert "context_hints" in converters
        assert "category_hints" in converters
        assert "complexity_hints" in converters

        # Test optimization strategies
        optimization = utilities["prompt_optimization_strategies"]
        assert "token_efficiency" in optimization
        assert "context_window_optimization" in optimization
        assert "dynamic_prompt_adaptation" in optimization

        # Verify token limits are reasonable
        assert optimization["token_efficiency"]["max_tokens_per_analysis"] > 0
        assert (
            optimization["context_window_optimization"]["claude_context_limit"] > 1000
        )

    def test_performance_benchmarks(self) -> None:
        """Test performance benchmarks documentation structure."""
        benchmarks = GTDDocumentation.get_performance_benchmarks()

        # Verify main benchmark categories
        assert "library_performance_profiles" in benchmarks
        assert "hybrid_strategy_performance" in benchmarks
        assert "production_deployment_considerations" in benchmarks
        assert "integration_testing_guidelines" in benchmarks

        # Test library profiles
        profiles = benchmarks["library_performance_profiles"]
        assert "spacy" in profiles
        assert "rapidfuzz" in profiles
        assert "textstat" in profiles

        # Test spaCy profile structure
        spacy_profile = profiles["spacy"]
        assert "performance_characteristics" in spacy_profile
        assert "scaling_characteristics" in spacy_profile
        assert "benchmarks" in spacy_profile
        assert "offline_capability" in spacy_profile

        # Verify offline capability is documented
        assert spacy_profile["offline_capability"] is not None
        assert profiles["rapidfuzz"]["offline_capability"] is not None
        assert profiles["textstat"]["offline_capability"] is not None

    @pytest.mark.slow
    def test_complete_documentation_generation(self) -> None:
        """Test complete documentation generation."""
        doc = GTDDocumentation.generate_complete_documentation()

        # Verify document structure
        assert "# GTD Methodology Documentation" in doc
        assert "## Table of Contents" in doc
        assert "## GTD Decision Tree" in doc
        assert "## Category Descriptions" in doc
        assert "## Context Pattern Detection" in doc
        assert "## Performance Benchmarks" in doc
        assert "## Conclusion" in doc

        # Verify all categories are documented
        for category in [
            "next-action",
            "project",
            "waiting-for",
            "someday-maybe",
            "reference",
            "trash",
        ]:
            assert category in doc

        # Verify all contexts are documented
        for context in [
            "@calls",
            "@computer",
            "@home",
            "@office",
            "@errands",
            "@anywhere",
        ]:
            assert context in doc

        # Verify performance data is included
        assert "spaCy Performance:" in doc
        assert "rapidfuzz Performance:" in doc
        assert "textstat Performance:" in doc

        # Verify implementation guidelines are present
        assert "Implementation Guidelines" in doc
        assert "For MCP Prompt Developers" in doc
        assert "For System Administrators" in doc


class TestGTDPromptBuilder:
    """Test GTD prompt builder for MCP prompt generation."""

    @pytest.fixture(scope="session")
    def rule_engine(self) -> GTDRuleEngine:
        """Create GTD rule engine for testing (shared across all tests)."""
        return GTDRuleEngine()

    @pytest.fixture(scope="session")
    def prompt_builder(self, rule_engine: GTDRuleEngine) -> GTDPromptBuilder:
        """Create prompt builder for testing (shared across all tests)."""
        return GTDPromptBuilder(rule_engine)

    def test_prompt_builder_initialization(self, rule_engine: GTDRuleEngine) -> None:
        """Test prompt builder initialization."""
        builder = GTDPromptBuilder(rule_engine)

        assert builder.rule_engine == rule_engine
        assert builder.max_tokens_per_analysis == 200
        assert builder.max_contexts == 3
        assert builder.max_explanations == 2

    def test_convert_context_analysis_to_prompt_hints(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test context analysis conversion to prompt hints."""
        # Test with call-related text
        call_text = "Call John about the project meeting"
        hint = prompt_builder.convert_context_analysis_to_prompt_hints(call_text)

        assert "Context Analysis:" in hint
        assert len(hint) <= 150  # Default max length

        # Test with empty text
        empty_hint = prompt_builder.convert_context_analysis_to_prompt_hints("")
        assert "No clear context indicators" in empty_hint

    def test_convert_categorization_analysis_to_prompt_guidance(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test categorization analysis conversion to guidance."""
        # Test with project-like text
        project_text = (
            "Implement new customer management system with reporting features"
        )
        guidance = prompt_builder.convert_categorization_analysis_to_prompt_guidance(
            project_text
        )

        assert "Category Analysis:" in guidance
        assert "Recommended" in guidance
        assert "confidence" in guidance
        assert len(guidance) <= 200  # Default max length

    def test_convert_complexity_analysis_to_prompt_context(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test complexity analysis conversion to context."""
        # Test with quick task
        quick_text = "Quick call to confirm meeting time"
        context = prompt_builder.convert_complexity_analysis_to_prompt_context(
            quick_text
        )

        assert "Complexity Analysis:" in context
        assert "Quick task:" in context
        assert "Project complexity:" in context
        assert "Delegation:" in context

    def test_build_quick_categorization_prompt(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test quick categorization prompt building."""
        text = "Send email to team about deadline"
        prompt = prompt_builder.build_quick_categorization_prompt(text)

        # Verify prompt structure
        assert f'"{text}"' in prompt
        assert "Quick GTD categorization" in prompt
        assert "Context Analysis:" in prompt
        assert "Category Analysis:" in prompt
        assert "Categories:" in prompt
        assert "Contexts:" in prompt
        assert "Return JSON:" in prompt

        # Verify all GTD categories are listed
        assert "next-action" in prompt
        assert "project" in prompt
        assert "waiting-for" in prompt

        # Verify all standard contexts are listed
        assert "@calls" in prompt
        assert "@computer" in prompt
        assert "@home" in prompt

    @pytest.mark.slow
    def test_build_comprehensive_analysis_prompt(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test comprehensive analysis prompt building."""
        text = "Develop comprehensive training program for new employees"
        prompt = prompt_builder.build_comprehensive_analysis_prompt(text)

        # Verify prompt structure
        assert f'"{text}"' in prompt
        assert "Comprehensive GTD analysis" in prompt
        assert "PATTERN ANALYSIS:" in prompt
        assert "GTD CLARIFYING QUESTIONS:" in prompt
        assert "GTD DECISION TREE:" in prompt
        assert "Return detailed JSON:" in prompt

        # Verify GTD methodology elements
        assert "actionable" in prompt.lower()
        assert "successful outcome" in prompt.lower()
        assert "next physical action" in prompt.lower()
        assert "context" in prompt.lower()

        # Verify JSON structure requirements
        assert '"actionable": true/false' in prompt
        assert '"category":' in prompt
        assert '"reasoning":' in prompt

    def test_build_batch_processing_prompt(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test batch processing prompt building."""
        items = [
            "Call supplier about delivery",
            "Update website pricing page",
            "Schedule team meeting for Friday",
            "Review quarterly sales report",
        ]
        prompt = prompt_builder.build_batch_processing_prompt(items)

        # Verify prompt structure
        assert f"Batch GTD processing for {len(items)} inbox items" in prompt
        assert "ITEMS TO PROCESS:" in prompt
        assert "GTD BATCH PROCESSING GUIDELINES:" in prompt
        assert "Return JSON:" in prompt

        # Verify all items are included
        for i, item in enumerate(items):
            assert f"{i + 1}. {item}" in prompt

        # Verify batch processing guidance
        assert "consistent categorization" in prompt.lower()
        assert "group related items" in prompt.lower()
        assert "patterns" in prompt.lower()

    @pytest.mark.slow
    def test_build_batch_processing_with_grouping_hints(
        self, prompt_builder: GTDPromptBuilder
    ) -> None:
        """Test batch processing with grouping suggestions."""
        items = [
            "Implement user authentication system",
            "Create database schema for users",
            "Design login interface",
            "Buy groceries for dinner",
        ]
        prompt = prompt_builder.build_batch_processing_prompt(
            items, include_grouping=True
        )

        # Should include grouping hints for project-related items
        assert "GROUPING HINTS:" in prompt

        # Test without grouping
        prompt_no_grouping = prompt_builder.build_batch_processing_prompt(
            items, include_grouping=False
        )
        assert "GROUPING HINTS:" not in prompt_no_grouping

    def test_estimate_prompt_tokens(self, prompt_builder: GTDPromptBuilder) -> None:
        """Test prompt token estimation."""
        short_prompt = "Quick test"
        long_prompt = "This is a much longer prompt that should have more tokens " * 10

        short_tokens = prompt_builder.estimate_prompt_tokens(short_prompt)
        long_tokens = prompt_builder.estimate_prompt_tokens(long_prompt)

        assert short_tokens > 0
        assert long_tokens > short_tokens
        assert short_tokens < 10  # Should be very few tokens
        assert long_tokens > 50  # Should be many more tokens

    def test_optimize_prompt_for_tokens(self, prompt_builder: GTDPromptBuilder) -> None:
        """Test prompt token optimization."""
        long_prompt = "GTD Analysis: " + "This is repeated content. " * 100

        # Test optimization to smaller limit
        optimized = prompt_builder.optimize_prompt_for_tokens(
            long_prompt, max_tokens=50
        )

        assert len(optimized) < len(long_prompt)
        assert prompt_builder.estimate_prompt_tokens(optimized) <= 55  # 10% buffer

        # Should preserve important content
        assert "GTD" in optimized

        # Test when no optimization needed
        short_prompt = "Short GTD prompt"
        unchanged = prompt_builder.optimize_prompt_for_tokens(
            short_prompt, max_tokens=1000
        )
        assert unchanged == short_prompt

    @pytest.mark.slow
    def test_rule_engine_integration_methods(self, rule_engine: GTDRuleEngine) -> None:
        """Test GTDRuleEngine integration with documentation and prompt builder."""
        # Test documentation access
        documentation = rule_engine.get_documentation()
        assert isinstance(documentation, GTDDocumentation)

        # Test prompt builder access
        prompt_builder = rule_engine.get_prompt_builder()
        assert isinstance(prompt_builder, GTDPromptBuilder)
        assert prompt_builder.rule_engine == rule_engine

        # Test enhanced documentation context
        enhanced_context = rule_engine.get_enhanced_documentation_context()
        assert "enhanced_decision_tree" in enhanced_context
        assert "category_descriptions_with_thresholds" in enhanced_context
        assert "context_pattern_strategies" in enhanced_context
        assert "complete_documentation" in enhanced_context

        # Test MCP prompt building
        quick_prompt = rule_engine.build_mcp_prompt_with_patterns(
            "quick", "Call dentist"
        )
        assert "Quick GTD categorization" in quick_prompt

        comprehensive_prompt = rule_engine.build_mcp_prompt_with_patterns(
            "comprehensive", "Implement new system"
        )
        assert "Comprehensive GTD analysis" in comprehensive_prompt

        batch_prompt = rule_engine.build_mcp_prompt_with_patterns(
            "batch", items=["Task 1", "Task 2"]
        )
        assert "Batch GTD processing" in batch_prompt

    @pytest.mark.slow
    def test_pattern_integration_summary(self, rule_engine: GTDRuleEngine) -> None:
        """Test pattern integration capabilities summary."""
        summary = rule_engine.get_pattern_integration_summary()

        # Verify summary structure
        assert "pattern_matching_available" in summary
        assert "documentation_components" in summary
        assert "prompt_building_capabilities" in summary
        assert "performance_targets" in summary

        # Test pattern matching availability flags
        pattern_availability = summary["pattern_matching_available"]
        assert "advanced_matcher" in pattern_availability
        assert "pattern_analyzer" in pattern_availability
        assert "spacy_available" in pattern_availability
        assert "dependencies_available" in pattern_availability

        # Test documentation components flags
        doc_components = summary["documentation_components"]
        assert doc_components["decision_tree_integration"] is True
        assert doc_components["category_thresholds"] is True
        assert doc_components["context_strategies"] is True
        assert doc_components["prompt_utilities"] is True
        assert doc_components["performance_benchmarks"] is True

        # Test prompt building capabilities
        prompt_capabilities = summary["prompt_building_capabilities"]
        assert prompt_capabilities["quick_categorization"] is True
        assert prompt_capabilities["comprehensive_analysis"] is True
        assert prompt_capabilities["batch_processing"] is True
        assert prompt_capabilities["token_optimization"] is True
        assert prompt_capabilities["pattern_hint_integration"] is True

        # Test performance targets format
        targets = summary["performance_targets"]
        assert "single_item_analysis" in targets
        assert "batch_processing" in targets
        assert "memory_usage" in targets
        assert "accuracy_threshold" in targets
