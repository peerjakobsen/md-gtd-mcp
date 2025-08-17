"""
GTD static rule engine and methodology constants.

This module provides static GTD methodology rules, patterns, and constants
for use in MCP prompts. Following Decision D008, this contains NO intelligent
analysis - only static patterns and rules that guide Claude Desktop's LLM reasoning.
"""

from typing import Any


class GTDMethodology:
    """Static GTD methodology constants and questions."""

    # Core GTD clarifying questions from David Allen's methodology
    CLARIFYING_QUESTIONS = [
        "What is this item about?",
        "Is this actionable? (Can you visualize yourself doing something about it?)",
        "If actionable: What's the successful outcome or purpose?",
        "If actionable: What's the very next physical action required?",
        "What context or tool is needed for this action?",
        "How much time will this action take?",
        "What energy level is required?",
        "Am I the right person to do this, or should it be delegated?",
        "If not actionable: Is this reference material, someday/maybe, or trash?",
        "Does this relate to any existing projects or areas of focus?",
    ]

    # GTD category descriptions for prompt context
    CATEGORY_DESCRIPTIONS = {
        "next-action": (
            "A single, specific physical action that can be completed in one session. "
            "Must be concrete and doable."
        ),
        "project": (
            "A desired outcome requiring multiple actions. "
            "Has a clear definition of 'done' and needs planning."
        ),
        "waiting-for": (
            "Actions delegated to others or pending external factors. "
            "Track what you're waiting to receive."
        ),
        "someday-maybe": (
            "Things you might want to do someday but are not committed to right now. "
            "Future possibilities."
        ),
        "reference": (
            "Information that might be useful later but requires no action. "
            "Keep for potential future reference."
        ),
        "trash": (
            "Items with no value that can be discarded. "
            "Neither actionable nor worth keeping as reference."
        ),
    }

    # GTD context definitions
    CONTEXT_DEFINITIONS = {
        "@home": "Actions that can only be done at home or require home resources",
        "@computer": "Actions requiring a computer, internet, or digital tools",
        "@calls": "Actions requiring phone calls or voice conversations",
        "@phone": (
            "Actions that can be done on a mobile phone (calls, texts, mobile apps)"
        ),
        "@errands": ("Actions to do while out and about (shopping, banking, etc.)"),
        "@office": "Actions that require being at the office or workplace",
        "@agenda": "Items to discuss with specific people during meetings",
        "@waiting": "Items delegated to others or waiting on external factors",
        "@anywhere": (
            "Actions that can be done in any location (thinking, reading, etc.)"
        ),
    }

    # GTD workflow phases
    GTD_PHASES = {
        "capture": (
            "Collect and gather all inputs and commitments in trusted external systems"
        ),
        "clarify": (
            "Process captured items to determine what they mean and "
            "what action is required"
        ),
        "organize": (
            "Sort and categorize clarified items into appropriate lists and folders"
        ),
        "reflect": (
            "Review your system regularly to maintain perspective and make choices"
        ),
        "engage": (
            "Make choices about actions to take based on context, time, and energy"
        ),
    }


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
    """Static keyword patterns for context and category suggestions."""

    # Context-specific keyword patterns (lowercase for matching)
    CONTEXT_PATTERNS = {
        "@calls": [
            "call",
            "phone",
            "dial",
            "contact",
            "reach out",
            "speak with",
            "discuss with",
            "talk to",
            "ring",
            "telephone",
            "voicemail",
            "conference call",
            "zoom",
            "meeting call",
        ],
        "@computer": [
            "email",
            "write",
            "code",
            "research",
            "analyze",
            "review",
            "type",
            "document",
            "spreadsheet",
            "presentation",
            "website",
            "online",
            "internet",
            "browse",
            "download",
            "upload",
            "backup",
            "design",
            "edit",
            "format",
            "calculate",
            "database",
            "software",
        ],
        "@home": [
            "home",
            "house",
            "family",
            "personal",
            "weekend",
            "evening",
            "kitchen",
            "garden",
            "yard",
            "garage",
            "basement",
            "attic",
            "laundry",
            "cleaning",
            "maintenance",
            "repair",
            "organize closet",
        ],
        "@office": [
            "office",
            "work",
            "workplace",
            "meeting",
            "colleague",
            "boss",
            "conference room",
            "desk",
            "workplace",
            "team",
            "department",
            "business hours",
            "during work",
            "at work",
        ],
        "@errands": [
            "buy",
            "pick up",
            "shop",
            "store",
            "bank",
            "post office",
            "pharmacy",
            "grocery",
            "mall",
            "shopping",
            "purchase",
            "get",
            "collect",
            "return",
            "exchange",
            "drop off",
            "deliver",
            "gas station",
            "dry cleaner",
            "library",
        ],
        "@phone": [
            "text",
            "sms",
            "mobile",
            "smartphone",
            "app",
            "notification",
            "mobile app",
            "check phone",
            "mobile call",
            "cell phone",
        ],
        "@anywhere": [
            "think",
            "brainstorm",
            "consider",
            "reflect",
            "meditate",
            "plan",
            "read",
            "review notes",
            "ponder",
            "contemplate",
            "decide",
        ],
    }

    # Two-minute rule indicators
    TWO_MINUTE_INDICATORS = [
        "quick",
        "simple",
        "just",
        "quickly",
        "brief",
        "short",
        "fast",
        "immediately",
        "rapid",
        "swift",
        "instant",
        "moment",
        "second",
        "minute",
        "easy",
        "straightforward",
        "simple",
    ]

    # Project complexity indicators
    PROJECT_INDICATORS = [
        "project",
        "initiative",
        "implement",
        "develop",
        "create",
        "build",
        "design",
        "plan",
        "organize",
        "establish",
        "set up",
        "launch",
        "complete",
        "finish",
        "multiple",
        "several",
        "various",
        "many",
        "comprehensive",
        "full",
        "entire",
        "whole",
        "system",
        "process",
        "workflow",
        "procedure",
        "program",
        "campaign",
        "strategy",
    ]

    # Delegation and waiting-for patterns
    DELEGATION_PATTERNS = [
        "waiting",
        "pending",
        "assigned",
        "delegated",
        "asked",
        "requested",
        "depends on",
        "blocked by",
        "waiting for",
        "expecting",
        "anticipating",
        "scheduled",
        "follow up",
        "check with",
        "remind",
        "chase",
        "waiting to hear",
        "pending response",
        "outstanding",
    ]

    # Priority and urgency indicators
    PRIORITY_INDICATORS = {
        "high": [
            "urgent",
            "asap",
            "immediately",
            "critical",
            "emergency",
            "priority",
            "important",
        ],
        "medium": ["soon", "timely", "reasonable", "normal", "standard"],
        "low": [
            "someday",
            "eventually",
            "when possible",
            "low priority",
            "nice to have",
        ],
    }

    # Time estimate indicators
    TIME_INDICATORS = {
        "quick": ["minute", "minutes", "quick", "fast", "brief", "short"],
        "medium": ["hour", "hours", "session", "morning", "afternoon"],
        "long": ["day", "days", "week", "weeks", "month", "months", "long term"],
    }


class GTDRuleEngine:
    """Main GTD rule engine for static pattern matching and validation."""

    def __init__(self) -> None:
        """Initialize the GTD rule engine."""
        self.methodology = GTDMethodology()
        self.patterns = GTDPatterns()
        self.decision_tree = GTDDecisionTree()

    def get_context_patterns(self) -> dict[str, list[str]]:
        """Get all context keyword patterns."""
        return self.patterns.CONTEXT_PATTERNS.copy()

    def get_clarifying_questions(self) -> list[str]:
        """Get GTD clarifying questions for prompt inclusion."""
        return self.methodology.CLARIFYING_QUESTIONS.copy()

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
            "category_descriptions": self.methodology.CATEGORY_DESCRIPTIONS.copy(),
            "context_definitions": self.methodology.CONTEXT_DEFINITIONS.copy(),
            "gtd_phases": self.methodology.GTD_PHASES.copy(),
            "two_minute_indicators": self.patterns.TWO_MINUTE_INDICATORS.copy(),
            "project_indicators": self.patterns.PROJECT_INDICATORS.copy(),
            "delegation_patterns": self.patterns.DELEGATION_PATTERNS.copy(),
            "priority_indicators": self.patterns.PRIORITY_INDICATORS.copy(),
            "time_indicators": self.patterns.TIME_INDICATORS.copy(),
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
        valid_contexts = set(self.methodology.CONTEXT_DEFINITIONS.keys())
        return context in valid_contexts

    def suggest_contexts_for_text(self, text: str) -> list[str]:
        """
        Suggest possible GTD contexts based on text content using static patterns.

        Note: This is simple keyword matching, not intelligent analysis.
        The actual reasoning happens in Claude Desktop via MCP prompts.
        """
        text_lower = text.lower()
        suggested_contexts = []

        # Check each context pattern for matches
        for context, keywords in self.patterns.CONTEXT_PATTERNS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if context not in suggested_contexts:
                        suggested_contexts.append(context)
                    break  # Found match for this context, move to next

        return suggested_contexts

    def detect_two_minute_task(self, text: str) -> bool:
        """
        Detect if text suggests a two-minute task using static patterns.

        Returns True if text contains two-minute rule indicators.
        """
        text_lower = text.lower()
        return any(
            indicator in text_lower for indicator in self.patterns.TWO_MINUTE_INDICATORS
        )

    def detect_project_indicators(self, text: str) -> bool:
        """
        Detect if text suggests a project using static patterns.

        Returns True if text contains project complexity indicators.
        """
        text_lower = text.lower()
        return any(
            indicator in text_lower for indicator in self.patterns.PROJECT_INDICATORS
        )

    def detect_delegation_indicators(self, text: str) -> bool:
        """
        Detect if text suggests delegation using static patterns.

        Returns True if text contains delegation/waiting patterns.
        """
        text_lower = text.lower()
        return any(
            pattern in text_lower for pattern in self.patterns.DELEGATION_PATTERNS
        )

    def estimate_priority_hints(self, text: str) -> str | None:
        """
        Provide priority hints based on static keyword patterns.

        Returns 'high', 'medium', 'low', or None if no clear indicators.
        """
        text_lower = text.lower()

        # Check high priority indicators first
        for indicator in self.patterns.PRIORITY_INDICATORS["high"]:
            if indicator in text_lower:
                return "high"

        # Check low priority indicators
        for indicator in self.patterns.PRIORITY_INDICATORS["low"]:
            if indicator in text_lower:
                return "low"

        # Check medium priority indicators
        for indicator in self.patterns.PRIORITY_INDICATORS["medium"]:
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
        for time_category, indicators in self.patterns.TIME_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    return time_category

        return None
