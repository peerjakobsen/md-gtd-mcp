"""Advanced pattern matching for GTD context detection using fuzzy/semantic analysis."""

from typing import Any

try:
    import numpy as np
    from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]
    from rapidfuzz import fuzz
    from sentence_transformers import SentenceTransformer

    ADVANCED_MATCHING_AVAILABLE = True
except ImportError:
    ADVANCED_MATCHING_AVAILABLE = False


class AdvancedPatternMatcher:
    """Advanced pattern matching for GTD context suggestions with fuzzy/semantic AI."""

    def __init__(self) -> None:
        """Initialize the advanced pattern matcher."""
        self.model: Any | None = None
        self.context_embeddings: dict[str, Any] = {}
        self.bm25_matchers: dict[str, Any] = {}
        self._initialize_advanced_features()

    def _initialize_advanced_features(self) -> None:
        """Initialize advanced matching features if dependencies are available."""
        if not ADVANCED_MATCHING_AVAILABLE:
            return

        try:
            # Use a lightweight sentence transformer model
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            # Fallback if model loading fails
            self.model = None

    def suggest_contexts_fuzzy(
        self, text: str, patterns: dict[str, list[str]], threshold: float = 80.0
    ) -> list[tuple[str, float]]:
        """
        Suggest contexts using fuzzy string matching.

        Args:
            text: Input text to analyze
            patterns: Context patterns dictionary
            threshold: Minimum fuzzy match score (0-100)

        Returns:
            List of (context, score) tuples sorted by score
        """
        if not ADVANCED_MATCHING_AVAILABLE:
            return []

        text_lower = text.lower()
        context_scores: dict[str, float] = {}

        for context, keywords in patterns.items():
            best_score = 0.0

            for keyword in keywords:
                # Use partial ratio for substring matching
                score = fuzz.partial_ratio(keyword, text_lower)
                best_score = max(best_score, score)

                # Also check token sort ratio for word order flexibility
                token_score = fuzz.token_sort_ratio(keyword, text_lower)
                best_score = max(best_score, token_score)

            if best_score >= threshold:
                context_scores[context] = best_score

        # Sort by score descending
        return sorted(context_scores.items(), key=lambda x: x[1], reverse=True)

    def suggest_contexts_bm25(
        self, text: str, patterns: dict[str, list[str]], top_k: int = 5
    ) -> list[tuple[str, float]]:
        """
        Suggest contexts using BM25 ranking.

        Args:
            text: Input text to analyze
            patterns: Context patterns dictionary
            top_k: Maximum number of contexts to return

        Returns:
            List of (context, score) tuples sorted by relevance
        """
        if not ADVANCED_MATCHING_AVAILABLE:
            return []

        # Prepare documents for BM25 (combine all keywords per context)
        context_docs = []
        context_names = []

        for context, keywords in patterns.items():
            doc = " ".join(keywords)
            context_docs.append(doc.split())
            context_names.append(context)

        if not context_docs:
            return []

        # Create BM25 index
        bm25 = BM25Okapi(context_docs)

        # Query BM25 with input text
        query_tokens = text.lower().split()
        scores = bm25.get_scores(query_tokens)

        # Create (context, score) pairs and sort
        context_scores = list(zip(context_names, scores, strict=False))
        context_scores.sort(key=lambda x: x[1], reverse=True)

        # Filter out zero scores and limit results
        return [(ctx, score) for ctx, score in context_scores[:top_k] if score > 0]

    def suggest_contexts_semantic(
        self, text: str, patterns: dict[str, list[str]], threshold: float = 0.3
    ) -> list[tuple[str, float]]:
        """
        Suggest contexts using semantic similarity.

        Args:
            text: Input text to analyze
            patterns: Context patterns dictionary
            threshold: Minimum cosine similarity score (0-1)

        Returns:
            List of (context, similarity) tuples sorted by similarity
        """
        if not ADVANCED_MATCHING_AVAILABLE or self.model is None:
            return []

        try:
            # Get text embedding
            text_embedding = self.model.encode([text])

            context_similarities: dict[str, float] = {}

            for context, keywords in patterns.items():
                # Get embeddings for context keywords
                keyword_embeddings = self.model.encode(keywords)

                # Calculate similarity with text
                similarities = np.dot(text_embedding, keyword_embeddings.T).flatten()
                best_similarity = float(np.max(similarities))

                if best_similarity >= threshold:
                    context_similarities[context] = best_similarity

            # Sort by similarity descending
            return sorted(
                context_similarities.items(), key=lambda x: x[1], reverse=True
            )

        except Exception:
            # Fallback if semantic matching fails
            return []

    def suggest_contexts_combined(
        self,
        text: str,
        patterns: dict[str, list[str]],
        weights: dict[str, float] | None = None,
    ) -> list[tuple[str, float]]:
        """
        Suggest contexts using combined scoring from multiple methods.

        Args:
            text: Input text to analyze
            patterns: Context patterns dictionary
            weights: Weights for different methods (fuzzy, bm25, semantic)

        Returns:
            List of (context, combined_score) tuples sorted by score
        """
        if weights is None:
            weights = {"fuzzy": 0.4, "bm25": 0.4, "semantic": 0.2}

        # Get results from each method
        fuzzy_results = dict(
            self.suggest_contexts_fuzzy(text, patterns, threshold=70.0)
        )
        bm25_results = dict(self.suggest_contexts_bm25(text, patterns))
        semantic_results = dict(
            self.suggest_contexts_semantic(text, patterns, threshold=0.25)
        )

        # Normalize scores to 0-1 range
        def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
            if not scores:
                return {}
            max_score = max(scores.values())
            if max_score == 0:
                return scores
            return {k: v / max_score for k, v in scores.items()}

        fuzzy_norm = normalize_scores(fuzzy_results)
        bm25_norm = normalize_scores(bm25_results)
        semantic_norm = normalize_scores(semantic_results)

        # Combine scores
        all_contexts: set[str] = set()
        all_contexts.update(fuzzy_norm.keys())
        all_contexts.update(bm25_norm.keys())
        all_contexts.update(semantic_norm.keys())

        combined_scores = {}
        for context in all_contexts:
            score = (
                weights["fuzzy"] * fuzzy_norm.get(context, 0.0)
                + weights["bm25"] * bm25_norm.get(context, 0.0)
                + weights["semantic"] * semantic_norm.get(context, 0.0)
            )
            combined_scores[context] = score

        # Sort by combined score
        return sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    def suggest_multiple_contexts(
        self, text: str, patterns: dict[str, list[str]], max_contexts: int = 3
    ) -> list[str]:
        """
        Suggest multiple contexts for items that might fit several categories.

        Args:
            text: Input text to analyze
            patterns: Context patterns dictionary
            max_contexts: Maximum number of contexts to return

        Returns:
            List of context strings sorted by relevance
        """
        # Use combined scoring for best results
        scored_contexts = self.suggest_contexts_combined(text, patterns)

        # Filter contexts with reasonable scores and limit count
        good_contexts = [
            context
            for context, score in scored_contexts
            if score > 0.1  # Minimum threshold for relevance
        ]

        return good_contexts[:max_contexts]

    def has_advanced_features(self) -> bool:
        """Check if advanced pattern matching features are available."""
        return ADVANCED_MATCHING_AVAILABLE and self.model is not None
