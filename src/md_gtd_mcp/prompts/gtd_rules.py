"""
GTD static rule engine and methodology constants.

This module provides static GTD methodology rules, patterns, and constants
for use in MCP prompts. Following Decision D008, this contains NO intelligent
analysis - only static patterns and rules that guide Claude Desktop's LLM reasoning.
"""

import json
from pathlib import Path
from typing import Any, cast


class GTDMethodology:
    """GTD methodology constants and questions loaded from JSON files."""

    _data_cache = None

    # Backward compatibility class attributes (set after class definition)
    CLARIFYING_QUESTIONS: list[str]
    CATEGORY_DESCRIPTIONS: dict[str, str]
    CONTEXT_DEFINITIONS: dict[str, str]
    GTD_PHASES: dict[str, str]

    @classmethod
    def _load_data(cls) -> dict[str, Any]:
        """Load GTD methodology data from JSON file with caching."""
        if cls._data_cache is None:
            json_path = Path(__file__).parent / "config" / "gtd_methodology.json"
            with open(json_path, encoding="utf-8") as f:
                cls._data_cache = json.load(f)
        return cast(dict[str, Any], cls._data_cache)

    @classmethod
    def get_clarifying_questions(cls) -> list[str]:
        """Core GTD clarifying questions from David Allen's methodology."""
        return cast(list[str], cls._load_data()["clarifying_questions"])

    @classmethod
    def get_category_descriptions(cls) -> dict[str, str]:
        """GTD category descriptions for prompt context."""
        return cast(dict[str, str], cls._load_data()["category_descriptions"])

    @classmethod
    def get_context_definitions(cls) -> dict[str, str]:
        """GTD context definitions."""
        return cast(dict[str, str], cls._load_data()["context_definitions"])

    @classmethod
    def get_gtd_phases(cls) -> dict[str, str]:
        """GTD workflow phases."""
        return cast(dict[str, str], cls._load_data()["gtd_phases"])


# Set up backward compatibility class attributes after class definition
GTDMethodology.CLARIFYING_QUESTIONS = GTDMethodology.get_clarifying_questions()
GTDMethodology.CATEGORY_DESCRIPTIONS = GTDMethodology.get_category_descriptions()
GTDMethodology.CONTEXT_DEFINITIONS = GTDMethodology.get_context_definitions()
GTDMethodology.GTD_PHASES = GTDMethodology.get_gtd_phases()


class GTDDecisionTree:
    """Static GTD decision tree templates for prompts."""

    @staticmethod
    def generate_decision_tree() -> str:
        """Generate the complete GTD decision tree text for prompt inclusion."""
        return """GTD Decision Tree for Inbox Processing:

1. IS IT ACTIONABLE?
   │
   ├─ NO → Non-Actionable Items:
   │   ├─ Reference: Useful information for future
   │   ├─ Someday/Maybe: Might want to do later
   │   └─ Trash: No value, discard
   │
   └─ YES → Actionable Items:
       │
       ├─ 2. WHAT'S THE OUTCOME?
       │   ├─ Multiple actions needed → PROJECT
       │   └─ Single action → Continue to 3
       │
       ├─ 3. WHAT'S THE NEXT ACTION?
       │   ├─ Takes less than 2 minutes → DO IT NOW
       │   └─ Takes more than 2 minutes → Continue to 4
       │
       └─ 4. WHO DOES IT?
           ├─ Someone else → DELEGATE → Waiting For
           └─ You → NEXT ACTION (with appropriate context)

Key Principles:
- Be specific about physical actions (not outcomes)
- One item = one next action (break down complex items)
- Every actionable item needs a context (@home, @computer, etc.)
- Projects need clear outcomes and support material
- Waiting For items need follow-up dates and responsible parties"""

    @staticmethod
    def generate_quick_reference() -> str:
        """Generate a concise GTD reference for quick categorization."""
        return """Quick GTD Categories:
• Next Action: Single specific action you can complete
• Project: Outcome requiring multiple actions
• Waiting For: Delegated or pending external factors
• Someday/Maybe: Future possibilities, not committed
• Reference: Info to keep, no action needed
• Trash: No value, discard

Common Contexts:
@calls @computer @home @office @errands @anywhere"""


class GTDPatterns:
    """Keyword patterns for context and category suggestions loaded from JSON files."""

    _context_cache = None
    _categorization_cache = None

    # Backward compatibility class attributes (set after class definition)
    CONTEXT_PATTERNS: dict[str, list[str]]
    TWO_MINUTE_INDICATORS: list[str]
    PROJECT_INDICATORS: list[str]
    DELEGATION_PATTERNS: list[str]
    PRIORITY_INDICATORS: dict[str, list[str]]
    TIME_INDICATORS: dict[str, list[str]]

    @classmethod
    def _load_context_patterns(cls) -> dict[str, Any]:
        """Load context patterns from JSON file with caching."""
        if cls._context_cache is None:
            json_path = Path(__file__).parent / "config" / "context_patterns.json"
            with open(json_path, encoding="utf-8") as f:
                cls._context_cache = json.load(f)
        return cast(dict[str, Any], cls._context_cache)

    @classmethod
    def _load_categorization_patterns(cls) -> dict[str, Any]:
        """Load categorization patterns from JSON file with caching."""
        if cls._categorization_cache is None:
            config_dir = Path(__file__).parent / "config"
            json_path = config_dir / "categorization_patterns.json"
            with open(json_path, encoding="utf-8") as f:
                cls._categorization_cache = json.load(f)
        return cast(dict[str, Any], cls._categorization_cache)

    @classmethod
    def get_context_patterns(cls) -> dict[str, list[str]]:
        """Context-specific keyword patterns (lowercase for matching)."""
        patterns_data = cls._load_context_patterns()["context_patterns"]
        return cast(dict[str, list[str]], patterns_data)

    @classmethod
    def get_two_minute_indicators(cls) -> list[str]:
        """Two-minute rule indicators."""
        indicators = cls._load_categorization_patterns()["two_minute_indicators"]
        return cast(list[str], indicators)

    @classmethod
    def get_project_indicators(cls) -> list[str]:
        """Project complexity indicators."""
        indicators = cls._load_categorization_patterns()["project_indicators"]
        return cast(list[str], indicators)

    @classmethod
    def get_delegation_patterns(cls) -> list[str]:
        """Delegation and waiting-for patterns."""
        patterns = cls._load_categorization_patterns()["delegation_patterns"]
        return cast(list[str], patterns)

    @classmethod
    def get_priority_indicators(cls) -> dict[str, list[str]]:
        """Priority and urgency indicators."""
        indicators = cls._load_categorization_patterns()["priority_indicators"]
        return cast(dict[str, list[str]], indicators)

    @classmethod
    def get_time_indicators(cls) -> dict[str, list[str]]:
        """Time estimate indicators."""
        indicators = cls._load_categorization_patterns()["time_indicators"]
        return cast(dict[str, list[str]], indicators)


# Set up backward compatibility class attributes after class definition
GTDPatterns.CONTEXT_PATTERNS = GTDPatterns.get_context_patterns()
GTDPatterns.TWO_MINUTE_INDICATORS = GTDPatterns.get_two_minute_indicators()
GTDPatterns.PROJECT_INDICATORS = GTDPatterns.get_project_indicators()
GTDPatterns.DELEGATION_PATTERNS = GTDPatterns.get_delegation_patterns()
GTDPatterns.PRIORITY_INDICATORS = GTDPatterns.get_priority_indicators()
GTDPatterns.TIME_INDICATORS = GTDPatterns.get_time_indicators()


class GTDRuleEngine:
    """Main GTD rule engine for static pattern matching and validation."""

    def __init__(self) -> None:
        """Initialize the GTD rule engine."""
        self.methodology = GTDMethodology()
        self.patterns = GTDPatterns()
        self.decision_tree = GTDDecisionTree()

        # Initialize advanced pattern matcher for enhanced context detection
        try:
            from .pattern_matcher import AdvancedPatternMatcher

            self.advanced_matcher: AdvancedPatternMatcher | None = (
                AdvancedPatternMatcher()
            )
        except ImportError:
            self.advanced_matcher = None

        # Initialize hybrid pattern analyzer (Task 2.6)
        try:
            from .pattern_analyzer import GTDPatternAnalyzer

            self.pattern_analyzer: GTDPatternAnalyzer | None = GTDPatternAnalyzer()
        except ImportError:
            self.pattern_analyzer = None

    def get_context_patterns(self) -> dict[str, list[str]]:
        """Get all context keyword patterns."""
        return self.patterns.get_context_patterns().copy()

    def get_clarifying_questions(self) -> list[str]:
        """Get GTD clarifying questions for prompt inclusion."""
        return self.methodology.get_clarifying_questions().copy()

    def get_decision_tree(self) -> str:
        """Get the GTD decision tree text for prompt inclusion."""
        return self.decision_tree.generate_decision_tree()

    def get_quick_reference(self) -> str:
        """Get quick GTD reference for prompt inclusion."""
        return self.decision_tree.generate_quick_reference()

    def build_prompt_context(self) -> dict[str, Any]:
        """Build comprehensive GTD context for prompt generation."""
        return {
            "clarifying_questions": self.get_clarifying_questions(),
            "decision_tree": self.get_decision_tree(),
            "quick_reference": self.get_quick_reference(),
            "context_patterns": self.get_context_patterns(),
            "category_descriptions": (
                self.methodology.get_category_descriptions().copy()
            ),
            "context_definitions": self.methodology.get_context_definitions().copy(),
            "gtd_phases": self.methodology.get_gtd_phases().copy(),
            "two_minute_indicators": self.patterns.get_two_minute_indicators().copy(),
            "project_indicators": self.patterns.get_project_indicators().copy(),
            "delegation_patterns": self.patterns.get_delegation_patterns().copy(),
            "priority_indicators": self.patterns.get_priority_indicators().copy(),
            "time_indicators": self.patterns.get_time_indicators().copy(),
        }

    def validate_category(self, category: str) -> bool:
        """Validate that a category is a valid GTD category."""
        valid_categories = {
            "next-action",
            "project",
            "waiting-for",
            "someday-maybe",
            "reference",
            "trash",
        }
        return category in valid_categories

    def validate_context(self, context: str) -> bool:
        """Validate that a context is a valid GTD context."""
        valid_contexts = set(self.methodology.get_context_definitions().keys())
        return context in valid_contexts

    def suggest_contexts_for_text(self, text: str) -> list[str]:
        """
        Suggest possible GTD contexts based on text content using static patterns.

        Note: This is simple keyword matching, not intelligent analysis.
        The actual reasoning happens in Claude Desktop via MCP prompts.
        """
        if not text or not text.strip():
            return []

        text_lower = text.lower()
        suggested_contexts = []

        # Basic keyword matching (original functionality)
        for context, keywords in self.patterns.get_context_patterns().items():
            for keyword in keywords:
                if keyword in text_lower:
                    if context not in suggested_contexts:
                        suggested_contexts.append(context)
                    break  # Found match for this context, move to next

        return suggested_contexts

    def suggest_contexts_advanced(self, text: str, max_contexts: int = 3) -> list[str]:
        """
        Suggest contexts using advanced pattern matching with fuzzy/semantic analysis.

        Args:
            text: Input text to analyze
            max_contexts: Maximum number of contexts to return

        Returns:
            List of suggested contexts using advanced matching techniques
        """
        if not text or not text.strip():
            return []

        # Fallback to basic matching if advanced features unavailable
        if (
            self.advanced_matcher is None
            or not self.advanced_matcher.has_advanced_features()
        ):
            return self.suggest_contexts_for_text(text)

        # Use advanced pattern matching
        suggested = self.advanced_matcher.suggest_multiple_contexts(
            text, self.patterns.get_context_patterns(), max_contexts
        )

        return suggested

    def suggest_contexts_with_confidence(self, text: str) -> list[tuple[str, float]]:
        """
        Suggest contexts with confidence scores using advanced pattern matching.

        Args:
            text: Input text to analyze

        Returns:
            List of (context, confidence_score) tuples sorted by confidence
        """
        if not text or not text.strip():
            return []

        # Fallback to basic matching if advanced features unavailable
        if (
            self.advanced_matcher is None
            or not self.advanced_matcher.has_advanced_features()
        ):
            basic_contexts = self.suggest_contexts_for_text(text)
            return [(context, 1.0) for context in basic_contexts]

        # Use combined scoring from advanced matcher
        return self.advanced_matcher.suggest_contexts_combined(
            text, self.patterns.get_context_patterns()
        )

    def suggest_contexts_fuzzy(
        self, text: str, threshold: float = 80.0
    ) -> list[tuple[str, float]]:
        """
        Suggest contexts using fuzzy string matching.

        Args:
            text: Input text to analyze
            threshold: Minimum fuzzy match score (0-100)

        Returns:
            List of (context, score) tuples for fuzzy matches above threshold
        """
        if not text or not text.strip():
            return []

        if self.advanced_matcher is None:
            return []

        return self.advanced_matcher.suggest_contexts_fuzzy(
            text, self.patterns.get_context_patterns(), threshold
        )

    def get_context_suggestions_with_explanations(self, text: str) -> dict[str, Any]:
        """
        Get comprehensive context suggestions with explanations for prompts.

        Returns detailed context analysis for inclusion in MCP prompts.
        """
        if not text or not text.strip():
            return {"contexts": [], "explanations": [], "confidence": "low"}

        # Get basic suggestions
        basic_contexts = self.suggest_contexts_for_text(text)

        # Get advanced suggestions if available
        advanced_available = (
            self.advanced_matcher is not None
            and self.advanced_matcher.has_advanced_features()
        )

        if advanced_available:
            advanced_contexts = self.suggest_contexts_with_confidence(text)
            fuzzy_matches = self.suggest_contexts_fuzzy(text, threshold=70.0)
        else:
            advanced_contexts = [(ctx, 1.0) for ctx in basic_contexts]
            fuzzy_matches = []

        # Determine confidence level
        if advanced_contexts and advanced_contexts[0][1] > 0.8:
            confidence = "high"
        elif advanced_contexts and advanced_contexts[0][1] > 0.4:
            confidence = "medium"
        else:
            confidence = "low"

        # Create explanations for prompts
        explanations = []
        for context, score in advanced_contexts[:3]:  # Top 3 suggestions
            if advanced_available:
                explanations.append(f"{context}: {score:.2f} confidence")
            else:
                explanations.append(f"{context}: keyword match")

        return {
            "contexts": [ctx for ctx, _ in advanced_contexts[:3]],
            "basic_matches": basic_contexts,
            "advanced_matches": advanced_contexts[:5] if advanced_available else [],
            "fuzzy_matches": fuzzy_matches[:3],
            "explanations": explanations,
            "confidence": confidence,
            "advanced_available": advanced_available,
        }

    def detect_two_minute_task(self, text: str) -> bool:
        """
        Detect if text suggests a two-minute task using static patterns.

        Returns True if text contains two-minute rule indicators.
        """
        text_lower = text.lower()
        two_minute_indicators = self.patterns.get_two_minute_indicators()
        return any(indicator in text_lower for indicator in two_minute_indicators)

    def detect_project_indicators(self, text: str) -> bool:
        """
        Detect if text suggests a project using static patterns.

        Returns True if text contains project complexity indicators.
        """
        text_lower = text.lower()
        project_indicators = self.patterns.get_project_indicators()
        return any(indicator in text_lower for indicator in project_indicators)

    def detect_delegation_indicators(self, text: str) -> bool:
        """
        Detect if text suggests delegation using static patterns.

        Returns True if text contains delegation/waiting patterns.
        """
        text_lower = text.lower()
        return any(
            pattern in text_lower for pattern in self.patterns.get_delegation_patterns()
        )

    def estimate_priority_hints(self, text: str) -> str | None:
        """
        Provide priority hints based on static keyword patterns.

        Returns 'high', 'medium', 'low', or None if no clear indicators.
        """
        text_lower = text.lower()
        priority_indicators = self.patterns.get_priority_indicators()

        # Check high priority indicators first
        for indicator in priority_indicators["high"]:
            if indicator in text_lower:
                return "high"

        # Check low priority indicators
        for indicator in priority_indicators["low"]:
            if indicator in text_lower:
                return "low"

        # Check medium priority indicators
        for indicator in priority_indicators["medium"]:
            if indicator in text_lower:
                return "medium"

        return None

    def estimate_time_hints(self, text: str) -> str | None:
        """
        Provide time estimate hints based on static keyword patterns.

        Returns 'quick', 'medium', 'long', or None if no clear indicators.
        """
        text_lower = text.lower()

        # Check each time category for indicators
        for time_category, indicators in self.patterns.get_time_indicators().items():
            for indicator in indicators:
                if indicator in text_lower:
                    return time_category

        return None

    def analyze_comprehensive(self, text: str) -> dict[str, Any]:
        """
        Comprehensive analysis using hybrid pattern analyzer (Task 2.6).

        Combines spaCy linguistic analysis, rapidfuzz fuzzy matching, and
        textstat complexity scoring for intelligent GTD categorization hints.

        Returns:
            Detailed analysis with pattern matches, confidence scores,
            and categorization recommendations for MCP prompt inclusion.
        """
        if not text or not text.strip():
            return self._get_empty_analysis_result()

        # Use hybrid pattern analyzer if available
        if self.pattern_analyzer is not None:
            return self.pattern_analyzer.analyze(text)

        # Fallback to basic analysis
        return self._get_basic_analysis_result(text)

    def get_two_minute_indicators(self, text: str) -> dict[str, Any]:
        """
        Detect two-minute rule indicators using advanced pattern matching.

        Uses rapidfuzz for fuzzy keyword matching and textstat for complexity.
        Returns structured indicators for MCP prompt guidance.
        """
        if not self.pattern_analyzer:
            # Fallback to basic detection
            is_two_minute = self.detect_two_minute_task(text)
            return {
                "is_two_minute": is_two_minute,
                "confidence": 0.5 if is_two_minute else 0.0,
                "method": "basic_keywords",
                "indicators": [],
            }

        # Use advanced two-minute analyzer
        matches = self.pattern_analyzer.two_minute_analyzer.analyze(text)

        return {
            "is_two_minute": len(matches) > 0,
            "confidence": max([m.confidence for m in matches], default=0.0),
            "method": "hybrid_analysis",
            "indicators": [m.explanation for m in matches],
            "matches": [self.pattern_analyzer._match_to_dict(m) for m in matches],
        }

    def get_project_complexity_indicators(self, text: str) -> dict[str, Any]:
        """
        Detect project complexity using spaCy patterns and textstat metrics.

        Identifies verb+noun patterns, multi-step indicators, and complexity
        scores for intelligent project vs. next-action categorization.
        """
        if not self.pattern_analyzer:
            # Fallback to basic detection
            is_project = self.detect_project_indicators(text)
            return {
                "is_project": is_project,
                "confidence": 0.5 if is_project else 0.0,
                "method": "basic_keywords",
                "complexity_factors": [],
            }

        # Use advanced project analyzer
        matches = self.pattern_analyzer.project_analyzer.analyze(text)

        return {
            "is_project": len(matches) > 0,
            "confidence": max([m.confidence for m in matches], default=0.0),
            "method": "hybrid_analysis",
            "complexity_factors": [m.explanation for m in matches],
            "matches": [self.pattern_analyzer._match_to_dict(m) for m in matches],
        }

    def get_delegation_indicators(self, text: str) -> dict[str, Any]:
        """
        Detect delegation patterns using spaCy dependency parsing.

        Identifies waiting/pending structures and delegation verbs with
        person entities for waiting-for categorization guidance.
        """
        if not self.pattern_analyzer:
            # Fallback to basic detection
            is_delegation = self.detect_delegation_indicators(text)
            return {
                "is_delegation": is_delegation,
                "confidence": 0.5 if is_delegation else 0.0,
                "method": "basic_keywords",
                "delegation_patterns": [],
            }

        # Use advanced delegation analyzer
        matches = self.pattern_analyzer.delegation_analyzer.analyze(text)

        return {
            "is_delegation": len(matches) > 0,
            "confidence": max([m.confidence for m in matches], default=0.0),
            "method": "hybrid_analysis",
            "delegation_patterns": [m.explanation for m in matches],
            "matches": [self.pattern_analyzer._match_to_dict(m) for m in matches],
        }

    def get_priority_urgency_indicators(self, text: str) -> dict[str, Any]:
        """
        Detect priority and urgency patterns using phrase matching.

        Identifies ASAP, urgent, deadline patterns with fuzzy matching
        for deadline variations and typo tolerance.
        """
        if not self.pattern_analyzer:
            # Fallback to basic detection
            priority = self.estimate_priority_hints(text)
            return {
                "priority_level": priority,
                "confidence": 0.5 if priority else 0.0,
                "method": "basic_keywords",
                "urgency_indicators": [],
            }

        # Use advanced priority analyzer
        matches = self.pattern_analyzer.priority_analyzer.analyze(text)

        # Determine priority level from matches
        priority_level = None
        if matches:
            # Look for priority level in match metadata
            for match in matches:
                if "PRIORITY_HIGH" in match.explanation:
                    priority_level = "high"
                    break
                elif "PRIORITY_MEDIUM" in match.explanation:
                    priority_level = "medium"
                    break
                elif "PRIORITY_LOW" in match.explanation:
                    priority_level = "low"
                    break

        return {
            "priority_level": priority_level,
            "confidence": max([m.confidence for m in matches], default=0.0),
            "method": "hybrid_analysis",
            "urgency_indicators": [m.explanation for m in matches],
            "matches": [self.pattern_analyzer._match_to_dict(m) for m in matches],
        }

    def build_enhanced_prompt_context(self, text: str) -> dict[str, Any]:
        """
        Build enhanced GTD context for MCP prompts with advanced pattern analysis.

        Combines static GTD rules with intelligent pattern detection to provide
        comprehensive guidance for Claude Desktop's LLM reasoning.
        """
        base_context = self.build_prompt_context()

        if not text or not text.strip():
            return base_context

        # Add advanced analysis if available
        if self.pattern_analyzer:
            analysis = self.analyze_comprehensive(text)

            base_context.update(
                {
                    "pattern_analysis": analysis,
                    "intelligent_hints": {
                        "two_minute_indicators": self.get_two_minute_indicators(text),
                        "project_complexity": self.get_project_complexity_indicators(
                            text
                        ),
                        "delegation_patterns": self.get_delegation_indicators(text),
                        "priority_urgency": self.get_priority_urgency_indicators(text),
                    },
                    "context_suggestions_advanced": (
                        self.get_context_suggestions_with_explanations(text)
                    ),
                    "categorization_confidence": analysis.get("confidence", 0.0),
                    "recommended_category": analysis.get(
                        "primary_category", "next-action"
                    ),
                }
            )
        else:
            # Basic analysis fallback
            base_context.update(
                {
                    "basic_hints": {
                        "two_minute_task": self.detect_two_minute_task(text),
                        "project_indicators": self.detect_project_indicators(text),
                        "delegation_indicators": self.detect_delegation_indicators(
                            text
                        ),
                        "priority_hints": self.estimate_priority_hints(text),
                        "time_hints": self.estimate_time_hints(text),
                    },
                    "context_suggestions_basic": self.suggest_contexts_for_text(text),
                }
            )

        return base_context

    def _get_empty_analysis_result(self) -> dict[str, Any]:
        """Get empty analysis result structure."""
        if self.pattern_analyzer:
            return self.pattern_analyzer._empty_result()

        return {
            "text": "",
            "primary_category": "next-action",
            "confidence": 0.0,
            "matches": [],
            "recommendations": {
                "suggested_category": "next-action",
                "confidence_level": "low",
            },
        }

    def _get_basic_analysis_result(self, text: str) -> dict[str, Any]:
        """Get basic analysis result using simple keyword matching."""
        return {
            "text": text,
            "primary_category": "next-action",
            "confidence": 0.3,
            "matches": [],
            "recommendations": {
                "suggested_category": "next-action",
                "confidence_level": "low",
                "method": "basic_keywords",
            },
            "basic_indicators": {
                "two_minute": self.detect_two_minute_task(text),
                "project": self.detect_project_indicators(text),
                "delegation": self.detect_delegation_indicators(text),
            },
        }

    def get_documentation(self) -> "GTDDocumentation":
        """Get access to comprehensive GTD methodology documentation."""
        return GTDDocumentation()

    def get_prompt_builder(self) -> "GTDPromptBuilder":
        """Get prompt builder for MCP prompt generation with pattern integration."""
        return GTDPromptBuilder(self)

    def get_enhanced_documentation_context(self) -> dict[str, Any]:
        """
        Get enhanced documentation context for MCP prompt generation.

        Combines base GTD context with advanced documentation and utilities
        for comprehensive prompt building capabilities.
        """
        base_context = self.build_prompt_context()
        documentation = self.get_documentation()

        # Add enhanced documentation components
        enhanced_context = base_context.copy()
        enhanced_context.update(
            {
                "enhanced_decision_tree": (
                    documentation.get_decision_tree_with_pattern_integration()
                ),
                "category_descriptions_with_thresholds": (
                    documentation.get_category_descriptions_with_thresholds()
                ),
                "context_pattern_strategies": (
                    documentation.get_context_pattern_strategies()
                ),
                "prompt_template_utilities": (
                    documentation.get_prompt_template_utilities()
                ),
                "performance_benchmarks": documentation.get_performance_benchmarks(),
                "complete_documentation": (
                    documentation.generate_complete_documentation()
                ),
            }
        )

        return enhanced_context

    def build_mcp_prompt_with_patterns(
        self,
        prompt_type: str,
        text: str = "",
        items: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Build MCP prompts with integrated pattern analysis.

        Args:
            prompt_type: Type of prompt ('quick', 'comprehensive', 'batch')
            text: Single text item to analyze (for quick/comprehensive)
            items: Multiple items for batch processing
            **kwargs: Additional prompt customization options

        Returns:
            Generated MCP prompt with pattern analysis integration
        """
        prompt_builder = self.get_prompt_builder()

        if prompt_type == "quick" and text:
            return prompt_builder.build_quick_categorization_prompt(text)
        elif prompt_type == "comprehensive" and text:
            return prompt_builder.build_comprehensive_analysis_prompt(text)
        elif prompt_type == "batch" and items:
            return prompt_builder.build_batch_processing_prompt(items, **kwargs)
        else:
            raise ValueError(
                f"Invalid prompt type '{prompt_type}' or missing required parameters"
            )

    def get_pattern_integration_summary(self) -> dict[str, Any]:
        """
        Get summary of pattern integration capabilities for system monitoring.

        Returns information about available pattern matching features,
        performance characteristics, and integration status.
        """
        # Get pattern analyzer features if available
        spacy_available = False
        dependencies_available = False
        if self.pattern_analyzer:
            features = self.pattern_analyzer.get_available_features()
            spacy_available = features["spacy_model_available"]
            dependencies_available = features["dependencies_available"]

        return {
            "pattern_matching_available": {
                "advanced_matcher": self.advanced_matcher is not None,
                "pattern_analyzer": self.pattern_analyzer is not None,
                "spacy_available": spacy_available,
                "dependencies_available": dependencies_available,
            },
            "documentation_components": {
                "decision_tree_integration": True,
                "category_thresholds": True,
                "context_strategies": True,
                "prompt_utilities": True,
                "performance_benchmarks": True,
            },
            "prompt_building_capabilities": {
                "quick_categorization": True,
                "comprehensive_analysis": True,
                "batch_processing": True,
                "token_optimization": True,
                "pattern_hint_integration": True,
            },
            "performance_targets": {
                "single_item_analysis": "<100ms",
                "batch_processing": "<50ms per item",
                "memory_usage": "<300MB",
                "accuracy_threshold": ">90%",
            },
        }


class GTDDocumentation:
    """
    Comprehensive GTD methodology documentation with pattern matching integration.

    This class provides detailed documentation of GTD decision trees, pattern matching
    strategies, and utility functions for building MCP prompts that guide Claude Desktop
    through proper GTD methodology using static server-side patterns.
    """

    _decision_tree_cache = None

    @classmethod
    def get_decision_tree_with_pattern_integration(cls) -> str:
        """
        Generate comprehensive GTD decision tree with pattern matching integration.

        Documents when to use spacy vs rapidfuzz vs textstat for each decision node,
        providing guidance for MCP prompts to leverage static pattern analysis.
        """
        if cls._decision_tree_cache is None:
            config_dir = Path(__file__).parent / "config"
            txt_path = config_dir / "decision_tree_pattern_integration.txt"
            with open(txt_path, encoding="utf-8") as f:
                cls._decision_tree_cache = f.read()
        return cls._decision_tree_cache

    _category_thresholds_cache = None

    @classmethod
    def get_category_descriptions_with_thresholds(cls) -> dict[str, dict[str, Any]]:
        """
        Get GTD category descriptions with pattern matching confidence thresholds.

        Returns detailed category information including confidence thresholds for
        each pattern matching library and troubleshooting guidance.
        """
        if cls._category_thresholds_cache is None:
            filename = "category_descriptions_with_thresholds.json"
            json_path = Path(__file__).parent / "config" / filename
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
                cls._category_thresholds_cache = data[
                    "category_descriptions_with_thresholds"
                ]
        return cast(dict[str, dict[str, Any]], cls._category_thresholds_cache)

    _context_strategies_cache = None

    @classmethod
    def get_context_pattern_strategies(cls) -> dict[str, dict[str, Any]]:
        """
        Get context definitions mapped to pattern detection strategies.

        Returns comprehensive mapping of GTD contexts to pattern detection approaches
        with performance characteristics and hybrid detection examples.
        """
        if cls._context_strategies_cache is None:
            json_path = Path(__file__).parent / "config" / "context_strategies.json"
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
                cls._context_strategies_cache = cast(
                    dict[str, dict[str, Any]], data["context_pattern_strategies"]
                )
        return cls._context_strategies_cache

    _prompt_utilities_cache = None

    @classmethod
    def get_prompt_template_utilities(cls) -> dict[str, Any]:
        """
        Generate prompt template building utilities for pattern-to-prompt conversion.

        Provides utilities to convert pattern matching results into prompt context,
        documenting how static patterns inform Claude's reasoning process with
        token optimization strategies.
        """
        if cls._prompt_utilities_cache is None:
            json_path = Path(__file__).parent / "config" / "prompt_utilities.json"
            with open(json_path, encoding="utf-8") as f:
                data = cast(dict[str, Any], json.load(f))

            # Load the template files
            template_dir = Path(__file__).parent / "config"

            # Add the templates from existing .txt files
            data["prompt_template_examples"] = {
                "inbox_clarification_with_patterns": cls._load_template_file(
                    template_dir / "prompt_template_inbox_clarification.txt"
                ),
                "quick_categorization_optimized": cls._load_template_file(
                    template_dir / "prompt_template_quick_categorization.txt"
                ),
                "batch_processing_with_grouping": cls._load_template_file(
                    template_dir / "prompt_template_batch_processing.txt"
                ),
            }

            cls._prompt_utilities_cache = data
        return cls._prompt_utilities_cache

    @staticmethod
    def _load_template_file(template_path: Path) -> str:
        """Load template content from .txt file."""
        with open(template_path, encoding="utf-8") as f:
            return f.read()

    _performance_benchmarks_cache = None

    @classmethod
    def get_performance_benchmarks(cls) -> dict[str, dict[str, Any]]:
        """
        Get pattern matching strategy documentation with performance benchmarks.

        Provides comprehensive performance data for spacy, rapidfuzz, and textstat
        approaches with memory usage guidelines and offline operation confirmation.
        """
        if cls._performance_benchmarks_cache is None:
            json_path = Path(__file__).parent / "config" / "performance_benchmarks.json"
            with open(json_path, encoding="utf-8") as f:
                data = json.load(f)
                cache_data = cast(dict[str, dict[str, Any]], data)
                cls._performance_benchmarks_cache = cache_data
        return cls._performance_benchmarks_cache

    @classmethod
    def generate_complete_documentation(cls) -> str:
        """
        Generate complete GTD methodology documentation for MCP prompt integration.

        Combines all documentation components into a comprehensive guide for
        pattern matching strategy, prompt building, and performance optimization.
        """
        decision_tree = cls.get_decision_tree_with_pattern_integration()
        categories = cls.get_category_descriptions_with_thresholds()
        contexts = cls.get_context_pattern_strategies()
        utilities = cls.get_prompt_template_utilities()
        benchmarks = cls.get_performance_benchmarks()

        # Extract long variable for f-string formatting
        optimization = utilities["prompt_optimization_strategies"]
        window_optimization = optimization["context_window_optimization"]
        context_limit = window_optimization["claude_context_limit"]

        return f"""
# GTD Methodology Documentation and Pattern Matching Integration Guide

This comprehensive guide documents the integration of David Allen's Getting Things Done
methodology with intelligent pattern matching for MCP prompt generation. The system uses
static server-side pattern analysis to guide Claude Desktop's LLM reasoning through
proper GTD categorization and workflow processes.

## Table of Contents
1. [GTD Decision Tree with Pattern Integration](#decision-tree)
2. [Category Descriptions with Pattern Thresholds](#categories)
3. [Context Pattern Detection Strategies](#contexts)
4. [Prompt Template Building Utilities](#templates)
5. [Performance Benchmarks and Optimization](#performance)

## GTD Decision Tree with Pattern Integration {{#decision-tree}}

{decision_tree}

## Category Descriptions with Pattern Thresholds {{#categories}}

### Overview
Each GTD category has specific pattern matching requirements and confidence thresholds
to ensure accurate categorization while maintaining proper GTD methodology integrity.

{
            chr(10).join(
                [
                    f"### {category.upper()}{chr(10)}{chr(10)}"
                    f"{data['description']}{chr(10)}{chr(10)}"
                    f"**Pattern Matching Configuration:**{chr(10)}"
                    f"- spaCy: {data['pattern_matching']['spacy_patterns']}{chr(10)}"
                    f"- rapidfuzz: N/A{chr(10)}"
                    f"- Thresholds: {data['confidence_thresholds']}{chr(10) * 2}"
                    f"**Common Patterns:**{chr(10)}"
                    f"{chr(10).join([f'- {p}' for p in data['common_patterns']])}"
                    for category, data in categories.items()
                ]
            )
        }

## Context Pattern Detection Strategies {{#contexts}}

### Overview
GTD contexts are detected using hybrid approaches combining linguistic analysis,
fuzzy matching, and automatic pattern recognition for optimal accuracy and performance.

{
            chr(10).join(
                [
                    f"### {context.upper()}{chr(10)}{chr(10)}"
                    f"{data['definition']}{chr(10)}{chr(10)}"
                    f"**Detection Strategy:**{chr(10)}"
                    f"- Primary: N/A{chr(10)}"
                    f"- Secondary: N/A{chr(10)}"
                    f"- Validation: N/A{chr(10) * 2}"
                    f"**Performance:**{chr(10)}"
                    f"- Performance: N/A" + f"{chr(10) * 2}"
                    f"**Use Cases:**{chr(10)}"
                    f"- Use cases: N/A"
                    for context, data in contexts.items()
                ]
            )
        }

## Prompt Template Building Utilities {{#templates}}

### Pattern-to-Prompt Conversion

The system provides utilities to convert pattern matching results into structured
prompt context that guides Claude Desktop through GTD methodology:

**Context Hints Conversion:**
```python
{utilities["pattern_to_prompt_converters"]["context_hints"]["example"]["output"]}
```

**Category Hints Integration:**
```python
{utilities["pattern_to_prompt_converters"]["category_hints"]["example"]["output"]}
```

**Token Optimization Strategies:**
- Maximum {
            utilities["prompt_optimization_strategies"]["token_efficiency"][
                "max_tokens_per_analysis"
            ]
        } tokens per analysis
- Prioritization: {
            chr(10).join(
                utilities["prompt_optimization_strategies"]["token_efficiency"][
                    "prioritization"
                ]
            )
        }
- Context window: {context_limit:,} total tokens

### Example Prompt Templates

**Comprehensive Analysis:**
```
{utilities["prompt_template_examples"]["inbox_clarification_with_patterns"].strip()}
```

**Quick Categorization:**
```
{utilities["prompt_template_examples"]["quick_categorization_optimized"].strip()}
```

## Performance Benchmarks and Optimization {{#performance}}

### Library Performance Profiles

**spaCy Performance:**
- Initialization: {
            benchmarks["library_performance_profiles"]["spacy"][
                "performance_characteristics"
            ]["initialization_time"]
        }
- Per-text analysis: {
            benchmarks["library_performance_profiles"]["spacy"][
                "performance_characteristics"
            ]["per_text_analysis"]
        }
- Memory usage: {
            benchmarks["library_performance_profiles"]["spacy"][
                "performance_characteristics"
            ]["memory_usage"]
        }
- Offline capability: {
            benchmarks["library_performance_profiles"]["spacy"]["offline_capability"]
        }

**rapidfuzz Performance:**
- Initialization: {
            benchmarks["library_performance_profiles"]["rapidfuzz"][
                "performance_characteristics"
            ]["initialization_time"]
        }
- Per-text analysis: {
            benchmarks["library_performance_profiles"]["rapidfuzz"][
                "performance_characteristics"
            ]["per_text_analysis"]
        }
- Memory usage: {
            benchmarks["library_performance_profiles"]["rapidfuzz"][
                "performance_characteristics"
            ]["memory_usage"]
        }
- Offline capability: {
            benchmarks["library_performance_profiles"]["rapidfuzz"][
                "offline_capability"
            ]
        }

**textstat Performance:**
- Initialization: {
            benchmarks["library_performance_profiles"]["textstat"][
                "performance_characteristics"
            ]["initialization_time"]
        }
- Per-text analysis: {
            benchmarks["library_performance_profiles"]["textstat"][
                "performance_characteristics"
            ]["per_text_analysis"]
        }
- Memory usage: {
            benchmarks["library_performance_profiles"]["textstat"][
                "performance_characteristics"
            ]["memory_usage"]
        }
- Offline capability: {
            benchmarks["library_performance_profiles"]["textstat"]["offline_capability"]
        }

### Hybrid Strategy Performance

**Combination Overhead:**
{
            chr(10).join(
                [
                    f"- {combo}: {time}"
                    for combo, time in benchmarks["hybrid_strategy_performance"][
                        "combination_overhead"
                    ].items()
                ]
            )
        }

**Performance Targets:**
{
            chr(10).join(
                [
                    f"- {metric}: {target}"
                    for metric, target in benchmarks["hybrid_strategy_performance"][
                        "performance_targets"
                    ].items()
                ]
            )
        }

### Production Deployment

**Resource Requirements:**
- Minimum RAM: {
            benchmarks["production_deployment_considerations"]["resource_requirements"][
                "minimum_ram"
            ]
        }
- Recommended RAM: {
            benchmarks["production_deployment_considerations"]["resource_requirements"][
                "recommended_ram"
            ]
        }
- CPU: {
            benchmarks["production_deployment_considerations"]["resource_requirements"][
                "cpu_requirements"
            ]
        }
- Disk space: {
            benchmarks["production_deployment_considerations"]["resource_requirements"][
                "disk_space"
            ]
        }

**Monitoring Metrics:**
{
            chr(10).join(
                [
                    f"- {metric}: {description}"
                    for metric, description in benchmarks[
                        "production_deployment_considerations"
                    ]["monitoring_metrics"].items()
                ]
            )
        }

## Implementation Guidelines

### For MCP Prompt Developers

1. **Use Pattern Hints Judiciously:** Include pattern analysis in prompts but don't
   overwhelm Claude with too much technical detail
2. **Optimize for Token Efficiency:** Follow token optimization strategies to stay
   within context limits
3. **Provide Fallback Guidance:** Always include basic GTD rules as fallback when
   pattern analysis is unavailable
4. **Test Across Categories:** Validate prompt effectiveness across all GTD
   categories and contexts

### For System Administrators

1. **Monitor Performance:** Track response times and memory usage in production
2. **Plan for Scaling:** Implement caching and load balancing strategies
3. **Prepare Fallbacks:** Ensure graceful degradation when advanced features
   are unavailable
4. **Validate Accuracy:** Regularly test categorization accuracy against
   ground truth data

### For Advanced Users

1. **Customize Thresholds:** Adjust confidence thresholds based on your
   specific use patterns
2. **Extend Patterns:** Add domain-specific keywords and patterns for
   specialized workflows
3. **Optimize Caching:** Implement result caching for frequently processed item types
4. **Monitor Accuracy:** Track and improve pattern matching accuracy over time

## Conclusion

This documentation provides a comprehensive foundation for integrating GTD methodology
with intelligent pattern matching in MCP servers. The hybrid approach combining
spaCy, rapidfuzz, and textstat provides robust, fast, and accurate categorization
hints while maintaining complete offline operation and graceful fallback capabilities.

The system is designed to guide Claude Desktop's LLM reasoning through proper GTD
methodology while providing intelligent pattern-based hints that improve accuracy
and consistency in categorization decisions.
"""


class GTDPromptBuilder:
    """
    Utility class for building MCP prompts with pattern analysis integration.

    Converts pattern matching results into structured prompt context that guides
    Claude Desktop through GTD methodology while optimizing for token efficiency.
    """

    def __init__(self, rule_engine: GTDRuleEngine) -> None:
        """Initialize with GTD rule engine for pattern analysis."""
        self.rule_engine = rule_engine
        self.max_tokens_per_analysis = 200
        self.max_contexts = 3
        self.max_explanations = 2

    def convert_context_analysis_to_prompt_hints(
        self, text: str, max_length: int = 150
    ) -> str:
        """
        Convert context analysis to compact prompt hints.

        Args:
            text: Input text to analyze
            max_length: Maximum length for prompt hints

        Returns:
            Formatted string with context suggestions for prompt inclusion
        """
        if not text or not text.strip():
            return "Context Analysis: No clear context indicators detected."

        # Get context analysis
        analysis = self.rule_engine.get_context_suggestions_with_explanations(text)

        contexts = analysis.get("contexts", [])[: self.max_contexts]
        confidence = analysis.get("confidence", "low")
        explanations = analysis.get("explanations", [])[: self.max_explanations]

        if not contexts:
            return "Context Analysis: No strong context matches found."

        # Format compact hint
        context_list = ", ".join(contexts)
        reasoning = "; ".join(explanations) if explanations else "Pattern matching"

        hint = (
            f"Context Analysis: {context_list} ({confidence} confidence) - {reasoning}"
        )

        # Truncate if too long
        if len(hint) > max_length:
            hint = hint[: max_length - 3] + "..."

        return hint

    def convert_categorization_analysis_to_prompt_guidance(
        self, text: str, max_length: int = 200
    ) -> str:
        """
        Convert comprehensive analysis to categorization guidance for prompts.

        Args:
            text: Input text to analyze
            max_length: Maximum length for guidance text

        Returns:
            Formatted categorization guidance for Claude Desktop
        """
        if not text or not text.strip():
            return "Category Analysis: Insufficient information for categorization."

        # Get comprehensive analysis
        analysis = self.rule_engine.analyze_comprehensive(text)

        category = analysis.get("primary_category", "next-action")
        confidence = analysis.get("confidence", 0.0)
        confidence_pct = int(confidence * 100)
        recommendations = analysis.get("recommendations", {})

        # Extract key indicators
        indicators = []
        if analysis.get("pattern_scores", {}).get("project", 0) > 0.5:
            indicators.append("multi-step complexity")
        if analysis.get("pattern_scores", {}).get("delegation", 0) > 0.5:
            indicators.append("delegation patterns")
        if analysis.get("pattern_scores", {}).get("two_minute", 0) > 0.5:
            indicators.append("quick task indicators")
        if analysis.get("pattern_scores", {}).get("priority", 0) > 0.5:
            indicators.append("urgency markers")

        # Build guidance text
        guidance = (
            f"Category Analysis: Recommended '{category}' "
            f"({confidence_pct}% confidence)"
        )

        if indicators:
            guidance += f" - Detected: {', '.join(indicators)}"

        if recommendations.get("flags"):
            guidance += f" - Flags: {', '.join(recommendations['flags'])}"

        # Truncate if needed
        if len(guidance) > max_length:
            guidance = guidance[: max_length - 3] + "..."

        return guidance

    def convert_complexity_analysis_to_prompt_context(
        self, text: str, include_details: bool = False
    ) -> str:
        """
        Convert complexity indicators to structured prompt context.

        Args:
            text: Input text to analyze
            include_details: Whether to include detailed explanations

        Returns:
            Formatted complexity analysis for prompt inclusion
        """
        if not text or not text.strip():
            return "Complexity: Unable to assess"

        # Get individual indicator analyses
        two_minute = self.rule_engine.get_two_minute_indicators(text)
        project = self.rule_engine.get_project_complexity_indicators(text)
        delegation = self.rule_engine.get_delegation_indicators(text)

        # Build compact analysis
        parts = []

        if two_minute.get("is_two_minute"):
            conf = int(two_minute.get("confidence", 0) * 100)
            parts.append(f"Quick task: Yes ({conf}%)")
        else:
            parts.append("Quick task: No")

        if project.get("is_project"):
            conf = int(project.get("confidence", 0) * 100)
            parts.append(f"Project complexity: Yes ({conf}%)")
        else:
            parts.append("Project complexity: No")

        if delegation.get("is_delegation"):
            conf = int(delegation.get("confidence", 0) * 100)
            parts.append(f"Delegation: Yes ({conf}%)")
        else:
            parts.append("Delegation: No")

        complexity_analysis = "Complexity Analysis: " + " | ".join(parts)

        # Add details if requested and space permits
        if include_details and len(complexity_analysis) < 120:
            details = []
            if two_minute.get("indicators"):
                details.extend(two_minute["indicators"][:1])  # First indicator only
            if project.get("complexity_factors"):
                details.extend(project["complexity_factors"][:1])
            if delegation.get("delegation_patterns"):
                details.extend(delegation["delegation_patterns"][:1])

            if details:
                detail_text = "; ".join(details)
                if len(complexity_analysis + detail_text) < 180:
                    complexity_analysis += f" - {detail_text}"

        return complexity_analysis

    def build_pattern_enhanced_prompt(
        self,
        base_prompt: str,
        text: str,
        include_context_hints: bool = True,
        include_category_hints: bool = True,
        include_complexity_hints: bool = True,
        optimize_tokens: bool = True,
    ) -> str:
        """
        Build enhanced prompt with pattern analysis integration.

        Args:
            base_prompt: Base prompt template with placeholders
            text: Text to analyze for pattern hints
            include_context_hints: Whether to include context suggestions
            include_category_hints: Whether to include category guidance
            include_complexity_hints: Whether to include complexity analysis
            optimize_tokens: Whether to optimize for token efficiency

        Returns:
            Enhanced prompt with pattern analysis hints
        """
        hints = {}

        if include_context_hints:
            hints["context_hints"] = self.convert_context_analysis_to_prompt_hints(
                text, max_length=100 if optimize_tokens else 200
            )

        if include_category_hints:
            hints["category_hints"] = (
                self.convert_categorization_analysis_to_prompt_guidance(
                    text, max_length=150 if optimize_tokens else 250
                )
            )

        if include_complexity_hints:
            hints["complexity_hints"] = (
                self.convert_complexity_analysis_to_prompt_context(
                    text, include_details=not optimize_tokens
                )
            )

        # Add GTD methodology references
        hints.update(
            {
                "decision_tree": self.rule_engine.get_decision_tree(),
                "quick_reference": self.rule_engine.get_quick_reference(),
                "clarifying_questions": "\n".join(
                    self.rule_engine.get_clarifying_questions()[:5]
                ),  # First 5 questions
            }
        )

        # Format base prompt with hints
        try:
            enhanced_prompt = base_prompt.format(**hints, text=text)
        except KeyError:
            # Fallback if template has missing placeholders
            enhanced_prompt = f"{base_prompt}\n\nPattern Analysis Hints:\n"
            for key, value in hints.items():
                if key != "decision_tree":  # Skip large decision tree in fallback
                    enhanced_prompt += f"- {key}: {value}\n"
            enhanced_prompt += f"\nText to analyze: {text}"

        return enhanced_prompt

    def build_quick_categorization_prompt(self, text: str) -> str:
        """
        Build optimized prompt for quick categorization with minimal tokens.

        Args:
            text: Text to categorize

        Returns:
            Token-optimized prompt for quick categorization
        """
        # Get compressed analysis
        context_hint = self.convert_context_analysis_to_prompt_hints(
            text, max_length=50
        )
        category_hint = self.convert_categorization_analysis_to_prompt_guidance(
            text, max_length=80
        )

        prompt = f"""Quick GTD categorization for: "{text}"

{context_hint}
{category_hint}

Categories: next-action|project|waiting-for|someday-maybe|reference|trash
Contexts: @calls|@computer|@home|@office|@errands|@anywhere

Apply GTD methodology. Return JSON:
{{"category": "...", "context": "...", "confidence": "high|medium|low"}}"""

        return prompt

    def build_comprehensive_analysis_prompt(self, text: str) -> str:
        """
        Build detailed prompt with full pattern analysis for complex items.

        Args:
            text: Text to analyze comprehensively

        Returns:
            Comprehensive prompt with detailed GTD guidance
        """
        # Get full analysis
        context_hints = self.convert_context_analysis_to_prompt_hints(
            text, max_length=200
        )
        category_hints = self.convert_categorization_analysis_to_prompt_guidance(
            text, max_length=250
        )
        complexity_hints = self.convert_complexity_analysis_to_prompt_context(
            text, include_details=True
        )

        # Get GTD methodology context
        decision_tree = self.rule_engine.get_decision_tree()
        clarifying_questions = "\n".join(
            f"{i + 1}. {q}"
            for i, q in enumerate(self.rule_engine.get_clarifying_questions()[:8])
        )

        prompt = f"""Comprehensive GTD analysis for inbox item: "{text}"

PATTERN ANALYSIS:
{context_hints}
{category_hints}
{complexity_hints}

GTD CLARIFYING QUESTIONS:
{clarifying_questions}

GTD DECISION TREE:
{decision_tree}

Apply David Allen's GTD methodology to analyze this item.
Use the pattern analysis as hints
but rely on GTD principles for final categorization decisions.

Consider:
1. Is this actionable? (Can you visualize doing something about it?)
2. If actionable, what's the successful outcome?
3. What's the very next physical action required?
4. What context/tool is needed for this action?
5. How much time and energy will this take?

Return detailed JSON:
{{
  "actionable": true/false,
  "category": "next-action|project|waiting-for|someday-maybe|reference|trash",
  "suggested_text": "clarified action text if applicable",
  "context": "@context if actionable",
  "project": "associated project name or null",
  "confidence": "high|medium|low",
  "reasoning": "detailed explanation for decision",
  "two_minute_rule": true/false/null,
  "next_steps": ["list of follow-up actions if project"]
}}"""

        return prompt

    def build_batch_processing_prompt(
        self, items: list[str], max_items: int = 20, include_grouping: bool = True
    ) -> str:
        """
        Build prompt for efficient batch processing of multiple items.

        Args:
            items: List of items to process
            max_items: Maximum items to include in single batch
            include_grouping: Whether to suggest grouping similar items

        Returns:
            Batch processing prompt with grouping suggestions
        """
        if not items:
            return "No items to process."

        # Limit batch size
        batch_items = items[:max_items]

        # Analyze items for grouping hints if requested
        grouping_hints = ""
        if include_grouping and len(batch_items) > 3:
            # Quick analysis for grouping suggestions
            project_items = []
            context_groups: dict[str, list[str]] = {}

            for i, item in enumerate(batch_items):
                # Quick pattern check
                if self.rule_engine.detect_project_indicators(item):
                    project_items.append(f"Item {i + 1}")

                contexts = self.rule_engine.suggest_contexts_for_text(item)
                for context in contexts[:1]:  # First context only
                    if context not in context_groups:
                        context_groups[context] = []
                    context_groups[context].append(f"Item {i + 1}")

            grouping_suggestions = []
            if project_items:
                grouping_suggestions.append(
                    f"Potential projects: {', '.join(project_items)}"
                )
            for context, context_items in context_groups.items():
                if len(context_items) > 1:
                    grouping_suggestions.append(
                        f"{context}: {', '.join(context_items)}"
                    )

            if grouping_suggestions:
                grouping_hints = "\nGROUPING HINTS:\n" + "\n".join(
                    f"- {hint}" for hint in grouping_suggestions
                )

        # Format items list
        items_list = "\n".join(f"{i + 1}. {item}" for i, item in enumerate(batch_items))

        prompt = f"""Batch GTD processing for {len(batch_items)} inbox items:

ITEMS TO PROCESS:
{items_list}{grouping_hints}

GTD BATCH PROCESSING GUIDELINES:
- Apply consistent categorization logic across all items
- Look for patterns and relationships between items
- Group related items that could form projects
- Maintain GTD methodology integrity for each categorization

For efficiency:
1. Identify any obvious patterns across items
2. Group related items when beneficial
3. Apply consistent context assignment
4. Suggest project creation for multi-item outcomes

Return JSON:
{{
  "categorizations": [
    {{
      "item_number": 1,
      "item": "original text",
      "category": "...",
      "context": "...",
      "confidence": "...",
      "reasoning": "brief explanation"
    }}
  ],
  "groups": [
    {{
      "name": "suggested group/project name",
      "item_numbers": [1, 3, 5],
      "reasoning": "why these items are related"
    }}
  ]
}}"""

        return prompt

    def estimate_prompt_tokens(self, prompt: str) -> int:
        """
        Estimate token count for prompt (rough approximation).

        Args:
            prompt: Prompt text to estimate

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English text
        return len(prompt) // 4

    def optimize_prompt_for_tokens(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Optimize prompt length to fit within token limits.

        Args:
            prompt: Original prompt text
            max_tokens: Maximum allowed tokens

        Returns:
            Optimized prompt within token limits
        """
        current_tokens = self.estimate_prompt_tokens(prompt)

        if current_tokens <= max_tokens:
            return prompt

        # Calculate compression ratio needed
        target_length = int(
            len(prompt) * (max_tokens / current_tokens) * 0.9
        )  # 10% buffer

        # Simple truncation strategy
        if target_length < len(prompt):
            # Try to preserve important sections first
            lines = prompt.split("\n")
            important_markers = ["GTD", "ANALYSIS", "PATTERN", "Return JSON"]

            # Keep lines with important markers and truncate others
            optimized_lines = []
            current_length = 0

            for line in lines:
                if any(marker in line.upper() for marker in important_markers):
                    # For important lines, include them but respect length limits
                    if current_length + len(line) + 1 <= target_length:
                        optimized_lines.append(line)
                        current_length += len(line) + 1
                    else:
                        # Truncate even important lines if needed
                        remaining_space = target_length - current_length - 1
                        if (
                            remaining_space > 10
                        ):  # Only truncate if we have meaningful space
                            optimized_lines.append(line[:remaining_space] + "...")
                        break
                elif current_length + len(line) + 1 <= target_length:
                    optimized_lines.append(line)
                    current_length += len(line) + 1
                else:
                    # If we can fit part of this line, truncate it
                    remaining_space = target_length - current_length - 1
                    if (
                        remaining_space > 10
                    ):  # Only truncate if we have meaningful space
                        optimized_lines.append(line[:remaining_space] + "...")
                    break

            optimized_prompt = "\n".join(optimized_lines)

            # Fallback: if we still don't have meaningful reduction, just truncate
            if len(optimized_prompt) >= len(prompt) * 0.9:
                optimized_prompt = prompt[:target_length]
                if not optimized_prompt.endswith("..."):
                    optimized_prompt = optimized_prompt.rstrip() + "..."

            return optimized_prompt

        return prompt
