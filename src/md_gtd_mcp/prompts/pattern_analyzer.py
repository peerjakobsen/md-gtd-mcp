"""Advanced pattern analyzer for GTD categorization using hybrid NLP approaches.

This module implements Task 2.6 - static indicator pattern collections with:
- Two-minute rule detection using spaCy and rapidfuzz
- Project complexity analysis using spaCy patterns and textstat
- Delegation pattern recognition using spaCy dependency parsing
- Priority/urgency detection using phrase matching
- Hybrid analyzer combining all approaches with configurable thresholds
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

try:
    import spacy
    import textstat  # type: ignore[import-untyped]
    from rapidfuzz import fuzz
    from rapidfuzz import process as rapidfuzz_process
    from spacy.language import Language
    from spacy.matcher import Matcher, PhraseMatcher

    DEPENDENCIES_AVAILABLE = True

    # Try to load spaCy model
    try:
        nlp: Language | None = spacy.load("en_core_web_sm")
        SPACY_MODEL_AVAILABLE = True
    except OSError:
        SPACY_MODEL_AVAILABLE = False
        nlp = None

except ImportError:
    DEPENDENCIES_AVAILABLE = False
    SPACY_MODEL_AVAILABLE = False
    nlp = None


class PatternType(Enum):
    """Pattern type enumeration for priority ordering."""

    PRIORITY = "priority"
    PROJECT = "project"
    DELEGATION = "delegation"
    TWO_MINUTE = "two_minute"


@dataclass
class PatternMatch:
    """Represents a pattern match with confidence and context."""

    pattern_type: PatternType
    confidence: float
    matched_text: str
    explanation: str
    metadata: dict[str, Any]


class TwoMinuteRuleAnalyzer:
    """Analyzer for two-minute rule detection using spaCy and rapidfuzz."""

    def __init__(self) -> None:
        """Initialize the two-minute rule analyzer."""
        self.matcher: Matcher | None
        self.quick_keywords = [
            "quick",
            "simple",
            "brief",
            "fast",
            "short",
            "easy",
            "rapid",
            "swift",
            "instant",
            "moment",
            "second",
            "minute",
        ]

        self.time_indicators = [
            "just a second",
            "real quick",
            "one minute",
            "couple minutes",
            "30 seconds",
            "quick sec",
            "real fast",
            "super quick",
        ]

        # Initialize spaCy matcher if available
        if SPACY_MODEL_AVAILABLE and nlp is not None:
            self.matcher = Matcher(nlp.vocab)
            self._setup_spacy_patterns()
        else:
            self.matcher = None

    def _setup_spacy_patterns(self) -> None:
        """Set up spaCy patterns for two-minute rule detection."""
        if not self.matcher:
            return

        # Pattern for quick task indicators
        quick_pattern = [
            {"LOWER": {"IN": ["quick", "simple", "brief", "fast", "short", "easy"]}}
        ]
        self.matcher.add("QUICK_TASK", [quick_pattern])

        # Pattern for time expressions
        time_patterns = [
            [{"LOWER": "just"}, {"LOWER": "a"}, {"LOWER": "second"}],
            [{"LOWER": "real"}, {"LOWER": "quick"}],
            [{"LOWER": "one"}, {"LOWER": "minute"}],
            [
                {"LIKE_NUM": True},
                {"LOWER": {"IN": ["second", "seconds", "minute", "minutes"]}},
            ],
        ]

        for i, pattern in enumerate(time_patterns):
            if self.matcher is not None:
                self.matcher.add(f"TIME_EXPR_{i}", [pattern])  # type: ignore[list-item]

    def analyze(self, text: str) -> list[PatternMatch]:
        """Analyze text for two-minute rule indicators."""
        if not text or not text.strip():
            return []

        matches = []

        # SpaCy-based detection
        if SPACY_MODEL_AVAILABLE and self.matcher:
            spacy_matches = self._analyze_with_spacy(text)
            matches.extend(spacy_matches)

        # Rapidfuzz-based detection
        if DEPENDENCIES_AVAILABLE:
            rapidfuzz_matches = self._analyze_with_rapidfuzz(text)
            matches.extend(rapidfuzz_matches)

        # Textstat-based complexity analysis
        if DEPENDENCIES_AVAILABLE:
            complexity_matches = self._analyze_complexity(text)
            matches.extend(complexity_matches)

        return matches

    def _analyze_with_spacy(self, text: str) -> list[PatternMatch]:
        """Analyze using spaCy rule-based patterns."""
        if not nlp or not self.matcher:
            return []

        doc = nlp(text)
        matches = self.matcher(doc)

        results = []
        for match_id, start, end in matches:
            span = doc[start:end]
            label = nlp.vocab.strings[match_id]

            confidence = 0.9  # High confidence for exact pattern matches

            results.append(
                PatternMatch(
                    pattern_type=PatternType.TWO_MINUTE,
                    confidence=confidence,
                    matched_text=span.text,
                    explanation=f"SpaCy pattern match: {label}",
                    metadata={"method": "spacy", "label": label, "span": (start, end)},
                )
            )

        return results

    def _analyze_with_rapidfuzz(self, text: str) -> list[PatternMatch]:
        """Analyze using rapidfuzz fuzzy matching."""
        words = text.lower().split()
        results = []

        for keyword in self.quick_keywords:
            matches = rapidfuzz_process.extract(
                keyword,
                words,
                limit=1,
                score_cutoff=85,  # Threshold from specification
            )

            if matches:
                matched_word, score, _ = matches[0]
                confidence = score / 100.0  # Convert to 0-1 range

                results.append(
                    PatternMatch(
                        pattern_type=PatternType.TWO_MINUTE,
                        confidence=confidence,
                        matched_text=matched_word,
                        explanation=f"Fuzzy match for '{keyword}' (score: {score})",
                        metadata={
                            "method": "rapidfuzz",
                            "keyword": keyword,
                            "score": score,
                        },
                    )
                )

        return results

    def _analyze_complexity(self, text: str) -> list[PatternMatch]:
        """Analyze text complexity for two-minute rule estimation."""
        word_count = len(text.split())
        readability = textstat.flesch_reading_ease(text)

        # Two-minute rule: <10 words + high readability = 2-minute task
        is_two_minute = word_count < 10 and readability > 60

        if is_two_minute:
            confidence = min(0.8, (70 - word_count) / 70 + (readability - 60) / 40)

            return [
                PatternMatch(
                    pattern_type=PatternType.TWO_MINUTE,
                    confidence=confidence,
                    matched_text=text,
                    explanation=(
                        f"Simple task: {word_count} words, "
                        f"readability {readability:.1f}"
                    ),
                    metadata={
                        "method": "textstat",
                        "word_count": word_count,
                        "readability": readability,
                    },
                )
            ]

        return []


class ProjectComplexityAnalyzer:
    """Analyzer for project complexity indicators using spaCy and textstat."""

    def __init__(self) -> None:
        """Initialize the project complexity analyzer."""
        self.matcher: Matcher | None
        self.phrase_matcher: PhraseMatcher | None
        self.project_verbs = [
            "implement",
            "develop",
            "create",
            "build",
            "design",
            "establish",
            "launch",
            "complete",
            "organize",
            "plan",
        ]

        self.complexity_indicators = [
            "multi-step",
            "multi-phase",
            "comprehensive",
            "enterprise",
            "architecture",
            "system",
            "platform",
            "framework",
        ]

        # Initialize spaCy matchers if available
        if SPACY_MODEL_AVAILABLE and nlp is not None:
            self.matcher = Matcher(nlp.vocab)
            self.phrase_matcher = PhraseMatcher(nlp.vocab)
            self._setup_spacy_patterns()
        else:
            self.matcher = None
            self.phrase_matcher = None

    def _setup_spacy_patterns(self) -> None:
        """Set up spaCy patterns for project complexity detection."""
        if not self.matcher:
            return

        # Pattern for [verb + noun] combinations (implement system, develop feature)
        verb_noun_pattern = [{"LOWER": {"IN": self.project_verbs}}, {"POS": "NOUN"}]
        self.matcher.add("PROJECT_VERB_NOUN", [verb_noun_pattern])  # type: ignore[list-item]

        # Pattern for complex multi-word expressions
        multi_patterns = [
            [{"LOWER": "multi"}, {"LOWER": {"IN": ["step", "phase", "part", "stage"]}}],
            [{"LOWER": {"IN": ["comprehensive", "complete", "full", "entire"]}}],
            [
                {"LOWER": {"IN": ["research", "analyze"]}},
                {"LOWER": "and"},
                {"LOWER": {"IN": ["develop", "implement"]}},
            ],
        ]

        for i, pattern in enumerate(multi_patterns):
            self.matcher.add(f"COMPLEX_PATTERN_{i}", [pattern])  # type: ignore[list-item]

        # Phrase matcher for complexity indicators
        if self.phrase_matcher and nlp is not None:
            complexity_phrases = [nlp(phrase) for phrase in self.complexity_indicators]
            self.phrase_matcher.add("COMPLEXITY_PHRASES", complexity_phrases)

    def analyze(self, text: str) -> list[PatternMatch]:
        """Analyze text for project complexity indicators."""
        if not text or not text.strip():
            return []

        matches = []

        # SpaCy linguistic pattern analysis
        if SPACY_MODEL_AVAILABLE and self.matcher:
            spacy_matches = self._analyze_with_spacy(text)
            matches.extend(spacy_matches)

        # Textstat complexity analysis
        if DEPENDENCIES_AVAILABLE:
            complexity_matches = self._analyze_textstat_complexity(text)
            matches.extend(complexity_matches)

        return matches

    def _analyze_with_spacy(self, text: str) -> list[PatternMatch]:
        """Analyze using spaCy linguistic patterns."""
        if not nlp or not self.matcher:
            return []

        doc = nlp(text)
        matches = self.matcher(doc)

        results = []
        for match_id, start, end in matches:
            span = doc[start:end]
            label = nlp.vocab.strings[match_id]

            confidence = 0.85  # High confidence for linguistic patterns

            results.append(
                PatternMatch(
                    pattern_type=PatternType.PROJECT,
                    confidence=confidence,
                    matched_text=span.text,
                    explanation=f"Project pattern: {label}",
                    metadata={"method": "spacy_linguistic", "label": label},
                )
            )

        # Check phrase matcher
        if self.phrase_matcher:
            phrase_matches = self.phrase_matcher(doc)
            for _match_id, start, end in phrase_matches:
                span = doc[start:end]

                results.append(
                    PatternMatch(
                        pattern_type=PatternType.PROJECT,
                        confidence=0.8,
                        matched_text=span.text,
                        explanation="Complexity phrase detected",
                        metadata={"method": "spacy_phrases"},
                    )
                )

        return results

    def _analyze_textstat_complexity(self, text: str) -> list[PatternMatch]:
        """Analyze using textstat complexity metrics."""
        word_count = len(text.split())
        readability = textstat.flesch_reading_ease(text)

        # Complex project indicators: low readability OR high word count
        is_complex = readability < 50 or word_count > 20

        if is_complex:
            # Calculate confidence based on complexity
            readability_factor = max(0, (50 - readability) / 50)
            word_count_factor = min(1.0, (word_count - 20) / 30)
            confidence = max(readability_factor, word_count_factor) * 0.7

            explanation = (
                f"Complex text: {word_count} words, readability {readability:.1f}"
            )

            return [
                PatternMatch(
                    pattern_type=PatternType.PROJECT,
                    confidence=confidence,
                    matched_text=text,
                    explanation=explanation,
                    metadata={
                        "method": "textstat_complexity",
                        "word_count": word_count,
                        "readability": readability,
                    },
                )
            ]

        return []


class DelegationPatternAnalyzer:
    """Analyzer for delegation patterns using spaCy dependency parsing."""

    def __init__(self) -> None:
        """Initialize the delegation pattern analyzer."""
        self.matcher: Matcher | None
        self.waiting_verbs = ["wait", "pend", "depend", "expect", "anticipate"]
        self.delegation_verbs = ["assign", "delegate", "ask", "request", "hand"]

        # Initialize spaCy matcher if available
        if SPACY_MODEL_AVAILABLE and nlp is not None:
            self.matcher = Matcher(nlp.vocab)
            self._setup_spacy_patterns()
        else:
            self.matcher = None

    def _setup_spacy_patterns(self) -> None:
        """Set up spaCy patterns for delegation detection."""
        if not self.matcher:
            return

        # Pattern for "waiting on/for [PERSON]" structures
        waiting_patterns = [
            [
                {"LOWER": {"IN": ["waiting", "pending"]}},
                {"LOWER": {"IN": ["on", "for"]}},
                {"POS": "NOUN"},
            ],
            [
                {"LOWER": {"IN": ["waiting", "pending"]}},
                {"LOWER": {"IN": ["on", "for"]}},
                {"ENT_TYPE": "PERSON"},
            ],
            [{"LOWER": "blocked"}, {"LOWER": "by"}, {"POS": "NOUN"}],
        ]

        for i, pattern in enumerate(waiting_patterns):
            self.matcher.add(f"WAITING_PATTERN_{i}", [pattern])  # type: ignore[list-item]

        # Pattern for delegation verbs with person/noun objects
        delegation_patterns = [
            [
                {"LOWER": {"IN": self.delegation_verbs}},
                {"LOWER": {"IN": ["to", "for"]}},
                {"POS": "NOUN"},
            ],
            [{"LOWER": {"IN": self.delegation_verbs}}, {"ENT_TYPE": "PERSON"}],
        ]

        for i, pattern in enumerate(delegation_patterns):
            self.matcher.add(f"DELEGATION_PATTERN_{i}", [pattern])  # type: ignore[list-item]

    def analyze(self, text: str) -> list[PatternMatch]:
        """Analyze text for delegation patterns."""
        if not text or not text.strip():
            return []

        matches = []

        # SpaCy dependency parsing
        if SPACY_MODEL_AVAILABLE:
            spacy_matches = self._analyze_with_spacy(text)
            matches.extend(spacy_matches)

        # Rapidfuzz fuzzy matching for delegation verbs
        if DEPENDENCIES_AVAILABLE:
            rapidfuzz_matches = self._analyze_with_rapidfuzz(text)
            matches.extend(rapidfuzz_matches)

        return matches

    def _analyze_with_spacy(self, text: str) -> list[PatternMatch]:
        """Analyze using spaCy dependency parsing and pattern matching."""
        if not nlp or not self.matcher:
            return []

        doc = nlp(text)
        results = []

        # Pattern-based matches
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            label = nlp.vocab.strings[match_id]

            confidence = 0.85

            results.append(
                PatternMatch(
                    pattern_type=PatternType.DELEGATION,
                    confidence=confidence,
                    matched_text=span.text,
                    explanation=f"Delegation pattern: {label}",
                    metadata={"method": "spacy_patterns", "label": label},
                )
            )

        # Dependency parsing for delegation structures
        for token in doc:
            if token.lemma_.lower() in self.waiting_verbs + self.delegation_verbs:
                # Look for relevant dependencies
                for child in token.children:
                    if child.dep_ in ["prep", "dobj", "agent", "pobj"]:
                        confidence = 0.75

                        # Check if involves a person
                        if child.ent_type_ == "PERSON":
                            confidence = 0.9

                        results.append(
                            PatternMatch(
                                pattern_type=PatternType.DELEGATION,
                                confidence=confidence,
                                matched_text=f"{token.text} {child.text}",
                                explanation=(
                                    f"Dependency: {token.lemma_} -> {child.dep_}"
                                ),
                                metadata={
                                    "method": "spacy_dependencies",
                                    "verb": token.lemma_,
                                    "dependency": child.dep_,
                                },
                            )
                        )

        return results

    def _analyze_with_rapidfuzz(self, text: str) -> list[PatternMatch]:
        """Analyze using rapidfuzz for delegation verb variations."""
        words = text.lower().split()
        results = []

        all_delegation_words = self.waiting_verbs + self.delegation_verbs

        for word in all_delegation_words:
            matches = rapidfuzz_process.extract(word, words, limit=1, score_cutoff=80)

            if matches:
                matched_word, score, _ = matches[0]
                confidence = (
                    score / 100.0
                ) * 0.8  # Slightly lower confidence for fuzzy

                results.append(
                    PatternMatch(
                        pattern_type=PatternType.DELEGATION,
                        confidence=confidence,
                        matched_text=matched_word,
                        explanation=f"Fuzzy delegation match: {word} -> {matched_word}",
                        metadata={
                            "method": "rapidfuzz",
                            "target_word": word,
                            "score": score,
                        },
                    )
                )

        return results


class PriorityUrgencyAnalyzer:
    """Analyzer for priority/urgency keywords using phrase matching."""

    def __init__(self) -> None:
        """Initialize the priority/urgency analyzer."""
        self.phrase_matcher: PhraseMatcher | None
        self.priority_phrases = {
            "high": [
                "ASAP",
                "urgent",
                "critical",
                "emergency",
                "priority",
                "important",
                "immediate",
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

        self.deadline_patterns = [
            "due today",
            "due tomorrow",
            "EOD",
            "COB",
            "by end of week",
            "by friday",
            "deadline",
            "due date",
            "overdue",
        ]

        # Initialize spaCy phrase matcher if available
        if SPACY_MODEL_AVAILABLE and nlp is not None:
            self.phrase_matcher = PhraseMatcher(nlp.vocab)
            self._setup_phrase_patterns()
        else:
            self.phrase_matcher = None

    def _setup_phrase_patterns(self) -> None:
        """Set up phrase patterns for priority detection."""
        if not self.phrase_matcher:
            return

        # Add priority phrases
        if nlp is not None:
            for priority_level, phrases in self.priority_phrases.items():
                phrase_docs = [nlp(phrase.lower()) for phrase in phrases]
                self.phrase_matcher.add(
                    f"PRIORITY_{priority_level.upper()}", phrase_docs
                )

            # Add deadline patterns
            deadline_docs = [nlp(pattern.lower()) for pattern in self.deadline_patterns]
            self.phrase_matcher.add("DEADLINE", deadline_docs)

    def analyze(self, text: str) -> list[PatternMatch]:
        """Analyze text for priority/urgency indicators."""
        if not text or not text.strip():
            return []

        matches = []

        # SpaCy phrase matching
        if SPACY_MODEL_AVAILABLE and self.phrase_matcher:
            spacy_matches = self._analyze_with_spacy(text)
            matches.extend(spacy_matches)

        # Rapidfuzz for deadline patterns with typos
        if DEPENDENCIES_AVAILABLE:
            rapidfuzz_matches = self._analyze_with_rapidfuzz(text)
            matches.extend(rapidfuzz_matches)

        return matches

    def _analyze_with_spacy(self, text: str) -> list[PatternMatch]:
        """Analyze using spaCy phrase matcher."""
        if not nlp or not self.phrase_matcher:
            return []

        doc = nlp(text.lower())
        matches = self.phrase_matcher(doc)

        results = []
        for match_id, start, end in matches:
            span = doc[start:end]
            label = nlp.vocab.strings[match_id]

            confidence = 0.9  # High confidence for exact phrase matches

            results.append(
                PatternMatch(
                    pattern_type=PatternType.PRIORITY,
                    confidence=confidence,
                    matched_text=span.text,
                    explanation=f"Priority indicator: {label}",
                    metadata={"method": "spacy_phrases", "label": label},
                )
            )

        return results

    def _analyze_with_rapidfuzz(self, text: str) -> list[PatternMatch]:
        """Analyze using rapidfuzz for deadline pattern variations."""
        text_lower = text.lower()
        results = []

        for pattern in self.deadline_patterns:
            # Use partial ratio for substring matching
            score = fuzz.partial_ratio(pattern, text_lower)

            if score >= 85:  # High threshold for deadline patterns
                confidence = (score / 100.0) * 0.8

                results.append(
                    PatternMatch(
                        pattern_type=PatternType.PRIORITY,
                        confidence=confidence,
                        matched_text=pattern,
                        explanation=f"Deadline pattern match: {pattern}",
                        metadata={
                            "method": "rapidfuzz_deadline",
                            "pattern": pattern,
                            "score": score,
                        },
                    )
                )

        return results


class GTDPatternAnalyzer:
    """Hybrid analyzer combining all approaches with configurable thresholds."""

    def __init__(self, thresholds: dict[str, float] | None = None) -> None:
        """
        Initialize the hybrid GTD pattern analyzer.

        Args:
            thresholds: Configuration for pattern matching thresholds
        """
        self.thresholds = thresholds or {
            "two_minute_confidence": 0.7,
            "project_confidence": 0.6,
            "delegation_confidence": 0.7,
            "priority_confidence": 0.8,
        }

        # Initialize individual analyzers
        self.two_minute_analyzer = TwoMinuteRuleAnalyzer()
        self.project_analyzer = ProjectComplexityAnalyzer()
        self.delegation_analyzer = DelegationPatternAnalyzer()
        self.priority_analyzer = PriorityUrgencyAnalyzer()

        # Pattern priority system: priority > project > delegation > two-minute
        self.pattern_priority = {
            PatternType.PRIORITY: 4,
            PatternType.PROJECT: 3,
            PatternType.DELEGATION: 2,
            PatternType.TWO_MINUTE: 1,
        }

    def analyze(self, text: str) -> dict[str, Any]:
        """
        Comprehensive analysis combining all pattern types.

        Returns:
            Dictionary with analysis results and recommendations
        """
        if not text or not text.strip():
            return self._empty_result()

        # Collect all pattern matches
        all_matches = []

        # Run individual analyzers
        all_matches.extend(self.two_minute_analyzer.analyze(text))
        all_matches.extend(self.project_analyzer.analyze(text))
        all_matches.extend(self.delegation_analyzer.analyze(text))
        all_matches.extend(self.priority_analyzer.analyze(text))

        # Apply confidence thresholds
        filtered_matches = self._filter_by_confidence(all_matches)

        # Resolve conflicts using priority system
        resolved_matches = self._resolve_conflicts(filtered_matches)

        # Calculate overall scores
        pattern_scores = self._calculate_pattern_scores(resolved_matches)

        # Determine primary category
        primary_category = self._determine_primary_category(pattern_scores)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            resolved_matches, pattern_scores
        )

        return {
            "text": text,
            "primary_category": primary_category,
            "pattern_scores": pattern_scores,
            "matches": [self._match_to_dict(match) for match in resolved_matches],
            "recommendations": recommendations,
            "confidence": self._calculate_overall_confidence(resolved_matches),
            "metadata": {
                "total_matches": len(all_matches),
                "filtered_matches": len(filtered_matches),
                "resolved_matches": len(resolved_matches),
                "dependencies_available": DEPENDENCIES_AVAILABLE,
                "spacy_available": SPACY_MODEL_AVAILABLE,
            },
        }

    def _filter_by_confidence(self, matches: list[PatternMatch]) -> list[PatternMatch]:
        """Filter matches by confidence thresholds."""
        filtered = []

        for match in matches:
            threshold_key = f"{match.pattern_type.value}_confidence"
            threshold = self.thresholds.get(threshold_key, 0.5)

            if match.confidence >= threshold:
                filtered.append(match)

        return filtered

    def _resolve_conflicts(self, matches: list[PatternMatch]) -> list[PatternMatch]:
        """Resolve conflicts using pattern priority system."""
        if not matches:
            return []

        # Group matches by pattern type
        by_type: dict[PatternType, list[PatternMatch]] = {}
        for match in matches:
            if match.pattern_type not in by_type:
                by_type[match.pattern_type] = []
            by_type[match.pattern_type].append(match)

        # Sort pattern types by priority
        sorted_types = sorted(
            by_type.keys(), key=lambda t: self.pattern_priority[t], reverse=True
        )

        resolved = []

        # Take best matches from each type, prioritizing higher-priority types
        for pattern_type in sorted_types:
            type_matches = by_type[pattern_type]
            # Sort by confidence within type
            type_matches.sort(key=lambda m: m.confidence, reverse=True)

            # Take top matches (limit to avoid overwhelming results)
            resolved.extend(type_matches[:3])

        return resolved

    def _calculate_pattern_scores(
        self, matches: list[PatternMatch]
    ) -> dict[str, float]:
        """Calculate aggregate scores for each pattern type."""
        scores = {pattern_type.value: 0.0 for pattern_type in PatternType}

        for match in matches:
            pattern_key = match.pattern_type.value
            # Use weighted confidence based on priority
            priority_weight = self.pattern_priority[match.pattern_type] / 4.0
            weighted_score = match.confidence * priority_weight
            scores[pattern_key] = max(scores[pattern_key], weighted_score)

        return scores

    def _determine_primary_category(self, pattern_scores: dict[str, float]) -> str:
        """Determine primary GTD category based on pattern scores."""
        # Map pattern types to GTD categories
        category_mapping = {
            "priority": "next-action",  # High priority usually means immediate action
            "project": "project",
            "delegation": "waiting-for",
            "two_minute": "next-action",
        }

        # Find highest scoring pattern
        max_score = 0.0
        primary_pattern = None

        for pattern_type, score in pattern_scores.items():
            if score > max_score:
                max_score = score
                primary_pattern = pattern_type

        if primary_pattern and max_score > 0.3:
            return category_mapping.get(primary_pattern, "next-action")

        return "next-action"  # Default fallback

    def _generate_recommendations(
        self, matches: list[PatternMatch], scores: dict[str, float]
    ) -> dict[str, Any]:
        """Generate recommendations based on analysis."""
        recommendations: dict[str, Any] = {
            "suggested_category": self._determine_primary_category(scores),
            "suggested_contexts": list[str](),
            "confidence_level": "medium",
            "reasoning": list[str](),
            "flags": list[str](),
        }

        # Generate reasoning based on matches
        for match in matches:
            recommendations["reasoning"].append(match.explanation)

        # Suggest contexts based on pattern types
        if scores.get("delegation", 0) > 0.5:
            recommendations["suggested_contexts"].append("@waiting")
        if scores.get("project", 0) > 0.5:
            recommendations["suggested_contexts"].extend(["@computer", "@office"])
        if scores.get("two_minute", 0) > 0.5:
            recommendations["flags"].append("two_minute_rule")

        # Set confidence level
        max_score = max(scores.values()) if scores else 0
        if max_score > 0.8:
            recommendations["confidence_level"] = "high"
        elif max_score > 0.5:
            recommendations["confidence_level"] = "medium"
        else:
            recommendations["confidence_level"] = "low"

        return recommendations

    def _calculate_overall_confidence(self, matches: list[PatternMatch]) -> float:
        """Calculate overall confidence in the analysis."""
        if not matches:
            return 0.0

        # Weight by pattern priority and take average
        total_weighted_confidence = 0.0
        total_weight = 0.0

        for match in matches:
            weight = self.pattern_priority[match.pattern_type]
            total_weighted_confidence += match.confidence * weight
            total_weight += weight

        return total_weighted_confidence / total_weight if total_weight > 0 else 0.0

    def _match_to_dict(self, match: PatternMatch) -> dict[str, Any]:
        """Convert PatternMatch to dictionary for serialization."""
        return {
            "pattern_type": match.pattern_type.value,
            "confidence": match.confidence,
            "matched_text": match.matched_text,
            "explanation": match.explanation,
            "metadata": match.metadata,
        }

    def _empty_result(self) -> dict[str, Any]:
        """Return empty result structure."""
        return {
            "text": "",
            "primary_category": "next-action",
            "pattern_scores": {t.value: 0.0 for t in PatternType},
            "matches": [],
            "recommendations": {
                "suggested_category": "next-action",
                "suggested_contexts": [],
                "confidence_level": "low",
                "reasoning": [],
                "flags": [],
            },
            "confidence": 0.0,
            "metadata": {
                "total_matches": 0,
                "filtered_matches": 0,
                "resolved_matches": 0,
                "dependencies_available": DEPENDENCIES_AVAILABLE,
                "spacy_available": SPACY_MODEL_AVAILABLE,
            },
        }

    def get_available_features(self) -> dict[str, bool]:
        """Get information about available features."""
        return {
            "dependencies_available": DEPENDENCIES_AVAILABLE,
            "spacy_model_available": SPACY_MODEL_AVAILABLE,
            "rapidfuzz_available": DEPENDENCIES_AVAILABLE,
            "textstat_available": DEPENDENCIES_AVAILABLE,
        }
