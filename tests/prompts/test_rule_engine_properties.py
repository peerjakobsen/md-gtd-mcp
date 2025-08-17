"""Property-based tests for Task 2.8 using hypothesis for robustness.

This module implements property-based testing to validate:
- Pattern matching edge cases with random text generation
- Consistency across spacy + rapidfuzz + textstat combinations
- Pattern conflict resolution with randomized inputs
- Robustness testing with hypothesis.strategies.text()

Property-based testing helps discover edge cases that manual testing might miss.
"""

import random

import pytest

try:
    import spacy
    import textstat  # type: ignore[import-untyped]
    from hypothesis import assume, given, seed
    from hypothesis import strategies as st
    from rapidfuzz import process as rapidfuzz_process
    from spacy.language import Language

    DEPENDENCIES_AVAILABLE = True
    HYPOTHESIS_AVAILABLE = True

    # Try to load spaCy model for testing
    try:
        nlp: Language = spacy.load("en_core_web_sm")
        SPACY_MODEL_AVAILABLE = True
    except OSError:
        SPACY_MODEL_AVAILABLE = False
        nlp = None  # type: ignore[assignment]

except ImportError:
    DEPENDENCIES_AVAILABLE = False
    HYPOTHESIS_AVAILABLE = False
    SPACY_MODEL_AVAILABLE = False
    nlp = None  # type: ignore[assignment]

# Import our modules
if DEPENDENCIES_AVAILABLE:
    from md_gtd_mcp.prompts.pattern_analyzer import GTDPatternAnalyzer


class TestPatternMatchingProperties:
    """Property-based tests for pattern matching robustness."""

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(text=st.text(min_size=1, max_size=100))
    def test_analyzer_never_crashes(self, text: str) -> None:
        """Property: GTDPatternAnalyzer should never crash on any text input."""
        assume(text.strip())  # Assume non-empty text

        analyzer = GTDPatternAnalyzer()

        try:
            analysis = analyzer.analyze(text)

            # Basic structure should always be present
            assert "primary_category" in analysis
            assert "pattern_scores" in analysis
            assert "confidence" in analysis
            assert "matches" in analysis
            assert "recommendations" in analysis

            # Types should be consistent
            assert isinstance(analysis["primary_category"], str)
            assert isinstance(analysis["pattern_scores"], dict)
            assert isinstance(analysis["confidence"], int | float)
            assert isinstance(analysis["matches"], list)
            assert isinstance(analysis["recommendations"], dict)

            # Confidence should be in valid range
            assert 0.0 <= analysis["confidence"] <= 1.0

        except Exception as e:
            pytest.fail(f"Analyzer crashed on text '{text[:50]}...': {e}")

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        base_word=st.sampled_from(["quick", "simple", "brief", "fast", "urgent"]),
        text_suffix=st.text(
            min_size=0,
            max_size=20,
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Zs")
            ),
        ),
    )
    def test_fuzzy_matching_properties(self, base_word: str, text_suffix: str) -> None:
        """Property: Fuzzy matching should be consistent for similar words."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Create variations of the base word
        test_text = f"{base_word} {text_suffix}".strip()

        # Test with rapidfuzz
        words = test_text.split()
        if words:
            matches = rapidfuzz_process.extract(
                base_word, words, limit=1, score_cutoff=50
            )

            # If we find a match, score should be reasonable
            if matches:
                word, score, _ = matches[0]
                assert 50 <= score <= 100, f"Score {score} out of valid range"
                assert isinstance(word, str), "Matched word should be string"

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        action_verb=st.sampled_from(
            ["implement", "develop", "create", "build", "design"]
        ),
        noun=st.sampled_from(
            ["system", "feature", "application", "project", "solution"]
        ),
        prefix=st.text(
            min_size=0,
            max_size=10,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        ),
        suffix=st.text(
            min_size=0,
            max_size=10,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        ),
    )
    def test_project_pattern_consistency(
        self, action_verb: str, noun: str, prefix: str, suffix: str
    ) -> None:
        """Property: Action verb + noun patterns should consistently detect projects."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Create text with action verb + noun pattern
        text = f"{prefix} {action_verb} {noun} {suffix}".strip()
        assume(len(text.split()) <= 10)  # Keep reasonable length

        analyzer = GTDPatternAnalyzer()
        analysis = analyzer.analyze(text)

        # Should detect some level of project pattern
        project_score = analysis["pattern_scores"].get("project", 0.0)

        # If the core pattern is clear, should get some project score
        core_pattern = f"{action_verb} {noun}"
        if core_pattern.lower() in text.lower():
            assert project_score > 0.0, (
                f"Text '{text}' contains '{core_pattern}' but got project "
                f"score {project_score}"
            )

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        text_length=st.integers(min_value=1, max_value=20),
        complexity_type=st.sampled_from(["simple", "complex"]),
    )
    def test_textstat_complexity_properties(
        self, text_length: int, complexity_type: str
    ) -> None:
        """Property: Text complexity should correlate with textstat metrics."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Generate text based on complexity type
        if complexity_type == "simple":
            words = ["call", "send", "go", "do", "get", "put", "run", "see"]
            text = " ".join(random.choice(words) for _ in range(text_length))
        else:  # complex
            words = [
                "implement",
                "comprehensive",
                "sophisticated",
                "architecture",
                "infrastructure",
                "enterprise",
                "optimization",
                "algorithm",
                "methodology",
                "integration",
                "configuration",
                "documentation",
            ]
            text = " ".join(
                random.choice(words) for _ in range(min(text_length, len(words)))
            )

        # Analyze with textstat
        readability = textstat.flesch_reading_ease(text)
        lexicon_count = textstat.lexicon_count(text)
        syllable_count = textstat.syllable_count(text)

        # Properties that should hold
        assert lexicon_count >= text_length, (
            "Lexicon count should be at least word count"
        )
        assert syllable_count >= text_length, (
            "Should have at least one syllable per word"
        )
        assert isinstance(readability, int | float), "Readability should be numeric"

        # Complex text should generally have lower readability
        if complexity_type == "complex" and text_length > 3:
            # Allow some variance but trend should be towards lower readability
            assert readability < 80, (
                f"Complex text should have readability < 80, got {readability}"
            )

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        quick_word=st.sampled_from(["quick", "fast", "brief", "simple"]),
        project_word=st.sampled_from(["implement", "develop", "create", "project"]),
        order=st.sampled_from(["quick_first", "project_first"]),
    )
    def test_pattern_priority_consistency(
        self, quick_word: str, project_word: str, order: str
    ) -> None:
        """Property: Project patterns should consistently win over
        two-minute patterns."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Create text with both patterns
        if order == "quick_first":
            text = f"{quick_word} {project_word} system"
        else:
            text = f"{project_word} {quick_word} solution"

        analyzer = GTDPatternAnalyzer()
        analysis = analyzer.analyze(text)

        pattern_scores = analysis["pattern_scores"]
        project_score = pattern_scores.get("project", 0.0)
        two_minute_score = pattern_scores.get("two_minute", 0.0)

        # If both patterns are detected, project should have higher priority
        if project_score > 0.1 and two_minute_score > 0.1:
            # Project category should be chosen due to higher priority
            primary_category = analysis["primary_category"]
            assert primary_category == "project", (
                f"Text '{text}' should be categorized as 'project' when both "
                f"patterns detected, got '{primary_category}' (project: "
                f"{project_score}, two_minute: {two_minute_score})"
            )


class TestConsistencyProperties:
    """Property-based tests for consistency across libraries."""

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        base_text=st.text(
            min_size=1,
            max_size=50,
            alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Zs")),
        ),
        typo_count=st.integers(min_value=0, max_value=3),
    )
    def test_fuzzy_matching_consistency(self, base_text: str, typo_count: int) -> None:
        """Property: Similar texts should produce similar analysis results."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        assume(base_text.strip() and len(base_text.split()) >= 1)

        analyzer = GTDPatternAnalyzer()

        # Original analysis
        original_analysis = analyzer.analyze(base_text)

        # Create typo-ed version by introducing character changes
        words = base_text.split()
        typo_text = base_text

        for _ in range(min(typo_count, len(words))):
            # Simple typo: swap adjacent characters in a random word
            if len(words) > 0:
                word_idx = random.randrange(len(words))
                word = words[word_idx]
                if len(word) > 2:
                    char_idx = random.randrange(len(word) - 1)
                    typo_word = (
                        word[:char_idx]
                        + word[char_idx + 1]
                        + word[char_idx]
                        + word[char_idx + 2 :]
                    )
                    typo_text = typo_text.replace(word, typo_word, 1)

        # Analysis with typos
        typo_analysis = analyzer.analyze(typo_text)

        # Confidence might be lower but category should be similar for small typo counts
        if typo_count <= 1:
            original_category = original_analysis["primary_category"]
            typo_category = typo_analysis["primary_category"]

            # Allow some flexibility but look for consistency
            if original_analysis["confidence"] > 0.6:
                # High confidence results should be stable to small typos
                assert (
                    typo_category == original_category
                    or typo_analysis["confidence"] < 0.4
                ), (
                    f"Small typos shouldn't dramatically change categorization: "
                    f"'{base_text}' -> '{original_category}' vs '{typo_text}' -> "
                    f"'{typo_category}'"
                )

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        word_count=st.integers(min_value=1, max_value=15),
        complexity_factor=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_textstat_consistency_across_lengths(
        self, word_count: int, complexity_factor: float
    ) -> None:
        """Property: Textstat metrics should scale predictably with text length."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Generate words based on complexity factor
        simple_words = [
            "go",
            "do",
            "run",
            "see",
            "get",
            "put",
            "cat",
            "dog",
            "car",
            "book",
        ]
        complex_words = [
            "implementation",
            "sophisticated",
            "architecture",
            "infrastructure",
            "optimization",
            "methodology",
            "configuration",
            "enterprise",
        ]

        # Blend simple and complex words based on complexity factor
        use_complex = random.random() < complexity_factor
        word_pool = complex_words if use_complex else simple_words

        # Generate text
        words = [random.choice(word_pool) for _ in range(word_count)]
        text = " ".join(words)

        # Measure textstat metrics
        lexicon_count = textstat.lexicon_count(text)
        syllable_count = textstat.syllable_count(text)
        readability = textstat.flesch_reading_ease(text)

        # Consistency properties
        assert lexicon_count == word_count, (
            f"Lexicon count {lexicon_count} should equal word count {word_count}"
        )
        assert syllable_count >= word_count, (
            "Should have at least one syllable per word"
        )

        # Complex words should generally reduce readability
        if complexity_factor > 0.7 and word_count > 3:
            assert readability < 70, (
                f"High complexity text should have readability < 70, got {readability} "
                f"for text: '{text[:50]}...'"
            )

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        pattern_type=st.sampled_from(
            ["project", "delegation", "priority", "two_minute"]
        ),
        text_variations=st.lists(
            st.text(min_size=1, max_size=20), min_size=1, max_size=5
        ),
    )
    def test_pattern_detection_stability(
        self, pattern_type: str, text_variations: list[str]
    ) -> None:
        """Property: Pattern detection should be stable across text variations."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Create base text with clear pattern
        pattern_texts = {
            "project": ["implement comprehensive system"],
            "delegation": ["waiting for John to respond"],
            "priority": ["urgent critical issue"],
            "two_minute": ["quick call to mom"],
        }

        base_text = pattern_texts[pattern_type][0]
        analyzer = GTDPatternAnalyzer()

        # Test base pattern
        base_analysis = analyzer.analyze(base_text)
        base_score = base_analysis["pattern_scores"].get(pattern_type, 0.0)

        # Should detect the intended pattern
        assume(base_score > 0.2)  # Assume pattern is clearly detected

        # Test variations (add/modify text)
        for variation in text_variations:
            # Create modified text
            modified_text = f"{base_text} {variation}".strip()

            # Skip if text becomes too long or contains only noise
            assume(len(modified_text.split()) <= 15)
            assume(len(variation.strip()) <= 10)

            modified_analysis = analyzer.analyze(modified_text)
            modified_score = modified_analysis["pattern_scores"].get(pattern_type, 0.0)

            # Pattern should still be detectable (though possibly weaker)
            if base_score > 0.5:  # Strong original pattern
                assert modified_score > 0.1, (
                    f"Strong {pattern_type} pattern should survive text variation: "
                    f"'{base_text}' -> '{modified_text}' "
                    f"(base score: {base_score}, modified: {modified_score})"
                )


class TestRobustnessProperties:
    """Property-based tests for robustness across edge cases."""

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        text=st.text(
            min_size=0,
            max_size=200,
            alphabet=st.characters(
                whitelist_categories=("Lu", "Ll", "Nd", "Pc", "Pd", "Po", "Zs"),
                blacklist_characters="\x00\x01\x02\x03\x04\x05\x06\x07\x08\x0b\x0c\x0e\x0f",
            ),
        )
    )
    def test_unicode_and_special_chars_robustness(self, text: str) -> None:
        """Property: System should handle any Unicode text without crashing."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        analyzer = GTDPatternAnalyzer()

        try:
            analysis = analyzer.analyze(text)

            # Should always return valid structure
            assert isinstance(analysis, dict)
            assert "primary_category" in analysis
            assert analysis["primary_category"] in [
                "next-action",
                "project",
                "waiting-for",
                "someday-maybe",
                "reference",
                "trash",
            ]

            # Confidence should be in valid range
            assert 0.0 <= analysis["confidence"] <= 1.0

        except Exception as e:
            pytest.fail(f"System should handle Unicode text '{text[:30]}...': {e}")

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        text_length=st.integers(min_value=0, max_value=1000),
        repetition_factor=st.integers(min_value=1, max_value=100),
    )
    def test_performance_properties(
        self, text_length: int, repetition_factor: int
    ) -> None:
        """Property: Performance should degrade gracefully with text length."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Skip extremely long combinations
        assume(text_length * repetition_factor < 10000)

        # Create test text of specified length
        base_words = ["implement", "system", "quick", "call", "waiting", "urgent"]
        words_needed = max(1, text_length // 8)  # Approximate words for length
        words = [random.choice(base_words) for _ in range(words_needed)]
        text = " ".join(words)

        analyzer = GTDPatternAnalyzer()

        import time

        start_time = time.time()

        # Run analysis multiple times
        for _ in range(repetition_factor):
            analysis = analyzer.analyze(text)
            assert analysis is not None

        elapsed_time = time.time() - start_time

        # Performance should be reasonable
        time_per_analysis = elapsed_time / repetition_factor

        # More lenient for property-based testing
        max_time_per_analysis = 0.5  # 500ms per analysis
        assert time_per_analysis < max_time_per_analysis, (
            f"Analysis took too long: {time_per_analysis:.3f}s per analysis "
            f"(text length: ~{len(text)}, repetitions: {repetition_factor})"
        )

    @pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
    @given(
        confidence_threshold=st.floats(min_value=0.0, max_value=1.0),
        pattern_strength=st.sampled_from(["weak", "medium", "strong"]),
    )
    def test_confidence_calibration_properties(
        self, confidence_threshold: float, pattern_strength: str
    ) -> None:
        """Property: Confidence scores should correlate with pattern strength."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        # Create texts with different pattern strengths
        if pattern_strength == "weak":
            texts = ["do something", "make thing", "go place"]
        elif pattern_strength == "medium":
            texts = [
                "quick email to team",
                "simple task completion",
                "brief meeting notes",
            ]
        else:  # strong
            texts = [
                "implement comprehensive enterprise system architecture",
                "urgent critical production system failure requiring "
                "immediate attention",
                "waiting for senior management approval on strategic initiative",
            ]

        analyzer = GTDPatternAnalyzer()

        for text in texts:
            analysis = analyzer.analyze(text)
            confidence = analysis["confidence"]

            # Confidence properties
            assert 0.0 <= confidence <= 1.0, "Confidence must be in [0, 1] range"

            # Strong patterns should generally have higher confidence
            if pattern_strength == "strong":
                # Allow some variance but expect higher confidence for clear patterns
                assert confidence > 0.3, (
                    f"Strong pattern text '{text}' should have confidence > 0.3, "
                    f"got {confidence}"
                )
            elif pattern_strength == "weak":
                # Weak patterns should have lower confidence
                assert confidence < 0.8, (
                    f"Weak pattern text '{text}' should have confidence < 0.8, "
                    f"got {confidence}"
                )


# Run with specific seeds for reproducibility
@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not available")
class TestReproducibleProperties:
    """Property-based tests with fixed seeds for reproducible results."""

    @seed(42)
    @given(text=st.text(min_size=1, max_size=50))
    def test_reproducible_analysis(self, text: str) -> None:
        """Test that analysis is deterministic for the same input."""
        if not DEPENDENCIES_AVAILABLE:
            pytest.skip("Dependencies not available")

        assume(text.strip())

        analyzer = GTDPatternAnalyzer()

        # Run analysis twice
        analysis1 = analyzer.analyze(text)
        analysis2 = analyzer.analyze(text)

        # Results should be identical
        assert analysis1["primary_category"] == analysis2["primary_category"]
        assert analysis1["confidence"] == analysis2["confidence"]
        assert analysis1["pattern_scores"] == analysis2["pattern_scores"]
