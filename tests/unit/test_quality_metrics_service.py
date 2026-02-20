"""Tests for quality_metrics_service.py - LLM-based article selection."""

from dataclasses import dataclass
from unittest.mock import patch, MagicMock

from backend.services.quality_metrics_service import select_top_articles_llm


@dataclass
class MockArticle:
    """Mock article for testing."""

    text: str
    source: str = "TestSource"
    freshness_score: float = 0.5
    original_title: str = ""
    confidence_score: float = 0.0  # Will be set by LLM selection


class TestSelectTopArticlesLLM:
    """Tests for LLM direct selection function."""

    def test_empty_list_returns_empty(self):
        """Empty list returns empty without LLM call."""
        result = select_top_articles_llm([], category="us", max_count=5)
        assert result == []

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_selects_articles_in_ranked_order_with_scores(self, mock_get_llm):
        """LLM returns indices with scores and function returns articles in that order."""
        mock_llm = MagicMock()
        # LLM selects articles 2, 0, 1 with confidence scores
        mock_llm.generate.return_value = '[{"index": 2, "score": 0.95}, {"index": 0, "score": 0.88}, {"index": 1, "score": 0.75}]'
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A", source="Source1", freshness_score=0.9),
            MockArticle(text="Article B", source="Source2", freshness_score=0.8),
            MockArticle(text="Article C", source="Source3", freshness_score=0.7),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 3
        assert result[0].text == "Article C"  # Index 2
        assert result[1].text == "Article A"  # Index 0
        assert result[2].text == "Article B"  # Index 1
        # Verify confidence scores were set
        assert result[0].confidence_score == 0.95
        assert result[1].confidence_score == 0.88
        assert result[2].confidence_score == 0.75

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_respects_max_count(self, mock_get_llm):
        """Respects max_count even if LLM returns more indices."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = '[{"index": 0, "score": 0.9}, {"index": 1, "score": 0.85}, {"index": 2, "score": 0.8}, {"index": 3, "score": 0.75}, {"index": 4, "score": 0.7}]'
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text=f"Article {i}", freshness_score=0.9 - i * 0.1) for i in range(5)
        ]
        result = select_top_articles_llm(articles, category="us", max_count=3)

        assert len(result) == 3

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_returns_fewer_if_llm_selects_fewer(self, mock_get_llm):
        """If LLM selects fewer articles (filtering irrelevant), return fewer."""
        mock_llm = MagicMock()
        # LLM only selects 2 out of 5 (filtered out irrelevant ones)
        mock_llm.generate.return_value = '[{"index": 1, "score": 0.9}, {"index": 3, "score": 0.85}]'
        mock_get_llm.return_value = mock_llm

        articles = [MockArticle(text=f"Article {i}", freshness_score=0.9) for i in range(5)]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 2
        assert result[0].text == "Article 1"
        assert result[1].text == "Article 3"
        assert result[0].confidence_score == 0.9
        assert result[1].confidence_score == 0.85

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_returns_empty_if_llm_selects_none(self, mock_get_llm):
        """If LLM returns empty array (no relevant articles), return empty."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = "[]"
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Political news about war"),
            MockArticle(text="Sports news"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 0

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_ignores_invalid_indices(self, mock_get_llm):
        """Invalid indices (out of range, duplicates) are ignored."""
        mock_llm = MagicMock()
        # LLM returns invalid indices: 10 (out of range), 0 (duplicate)
        mock_llm.generate.return_value = '[{"index": 0, "score": 0.9}, {"index": 10, "score": 0.8}, {"index": 0, "score": 0.7}, {"index": 1, "score": 0.6}, {"index": -1, "score": 0.5}]'
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A"),
            MockArticle(text="Article B"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        # Should only get valid indices: 0, 1 (10, duplicate 0, -1 ignored)
        assert len(result) == 2
        assert result[0].text == "Article A"
        assert result[1].text == "Article B"

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_handles_wrapped_response_articles_key(self, mock_get_llm):
        """Handles LLM response wrapped in {'articles': [...]}."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            '{"articles": [{"index": 2, "score": 0.9}, {"index": 0, "score": 0.8}]}'
        )
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A"),
            MockArticle(text="Article B"),
            MockArticle(text="Article C"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 2
        assert result[0].text == "Article C"  # Index 2
        assert result[1].text == "Article A"  # Index 0

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_handles_wrapped_response_result_key(self, mock_get_llm):
        """Handles LLM response wrapped in {'result': [...]}."""
        mock_llm = MagicMock()
        mock_llm.generate.return_value = (
            '{"result": [{"index": 1, "score": 0.88}, {"index": 2, "score": 0.75}]}'
        )
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A"),
            MockArticle(text="Article B"),
            MockArticle(text="Article C"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 2
        assert result[0].text == "Article B"  # Index 1
        assert result[1].text == "Article C"  # Index 2

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_handles_single_object_response(self, mock_get_llm):
        """Handles LLM returning single object instead of array."""
        mock_llm = MagicMock()
        # LLM returns single object (not wrapped in array)
        mock_llm.generate.return_value = '{"index": 1, "score": 0.92}'
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A"),
            MockArticle(text="Article B"),
            MockArticle(text="Article C"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 1
        assert result[0].text == "Article B"  # Index 1
        assert result[0].confidence_score == 0.92

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_backward_compatible_with_old_format(self, mock_get_llm):
        """Handles old LLM response format (just indices, no scores)."""
        mock_llm = MagicMock()
        # Old format: just array of indices
        mock_llm.generate.return_value = "[2, 0, 1]"
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Article A"),
            MockArticle(text="Article B"),
            MockArticle(text="Article C"),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=5)

        assert len(result) == 3
        assert result[0].text == "Article C"  # Index 2
        assert result[1].text == "Article A"  # Index 0
        assert result[2].text == "Article B"  # Index 1
        # Default score of 0.8 for old format
        assert result[0].confidence_score == 0.8
        assert result[1].confidence_score == 0.8

    @patch("backend.services.quality_metrics_service.get_llm_service")
    def test_fallback_on_llm_error(self, mock_get_llm):
        """On LLM error, falls back to freshness-sorted articles."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = Exception("LLM Error")
        mock_get_llm.return_value = mock_llm

        articles = [
            MockArticle(text="Older", freshness_score=0.3),
            MockArticle(text="Newest", freshness_score=0.9),
            MockArticle(text="Medium", freshness_score=0.6),
        ]
        result = select_top_articles_llm(articles, category="us", max_count=2)

        # Should fall back to freshness sort
        assert len(result) == 2
        assert result[0].text == "Newest"  # Highest freshness
        assert result[1].text == "Medium"  # Second highest
