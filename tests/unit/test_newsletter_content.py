"""
Unit tests for AIContentService newsletter content generation.
"""

import json
from unittest.mock import patch, MagicMock

from backend.services.ai_content_service import AIContentService


class TestGenerateNewsletterContent:
    """Tests for the AIContentService.generate_newsletter_content method."""

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_returns_empty_when_no_sources_metadata(self, mock_config, mock_get_llm):
        """Test that empty content is returned when sources_metadata is None or empty."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()

        result = service.generate_newsletter_content(None)
        assert result["ai_titles"] == {}
        # Note: podcast_dialog is now generated separately when user clicks "Generate"

        result = service.generate_newsletter_content({})
        assert result["ai_titles"] == {}

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_returns_empty_when_no_articles(self, mock_config, mock_get_llm):
        """Test that empty content is returned when no articles in any category."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()
        sources_metadata = {"us": [], "israel": [], "ai": [], "crypto": []}
        result = service.generate_newsletter_content(sources_metadata)
        assert result["ai_titles"] == {}

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_generates_all_content_in_single_call(self, mock_config, mock_get_llm):
        """Test that all content is generated in a single LLM call."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = json.dumps(
            {
                "ai_titles": {"us:0": "US Summary", "israel:0": "סיכום"},
                "ai_titles_en": {"us:0": "US Summary", "israel:0": "Israel Summary"},
            }
        )
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        sources_metadata = {
            "us": [{"text": "US Stock Market Rises", "link": "http://example.com"}],
            "israel": [{"text": "מדד תל אביב עלה", "link": "http://example.com"}],
        }

        result = service.generate_newsletter_content(sources_metadata)

        # Verify single LLM call
        assert mock_llm.generate.call_count == 1

        # Verify all fields present (podcast_dialog is generated separately now)
        assert "ai_titles" in result
        assert "ai_titles_en" in result

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_handles_markdown_wrapped_json(self, mock_config, mock_get_llm):
        """Test that markdown-wrapped JSON response is properly parsed."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = '```json\n{"ai_titles": {"us:0": "Test Title"}, "ai_titles_en": {"us:0": "Test Title"}}\n```'
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        sources_metadata = {"us": [{"text": "US News"}]}
        result = service.generate_newsletter_content(sources_metadata)

        assert result["ai_titles"]["us:0"] == "Test Title"

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_returns_empty_on_llm_error(self, mock_config, mock_get_llm):
        """Test that empty content is returned when LLM call fails."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.side_effect = Exception("API Error")
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        sources_metadata = {"us": [{"text": "US News"}]}
        result = service.generate_newsletter_content(sources_metadata)

        assert result["ai_titles"] == {}

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_includes_all_categories_in_prompt(self, mock_config, mock_get_llm):
        """Test that all categories with news are included in the prompt."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = json.dumps(
            {
                "ai_titles": {},
                "ai_titles_en": {},
            }
        )
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        sources_metadata = {
            "us": [{"text": "US News"}],
            "israel": [{"text": "Israel News"}],
            "ai": [{"text": "AI News"}],
            "crypto": [{"text": "Crypto News"}],
        }

        service.generate_newsletter_content(sources_metadata)

        call_args = mock_llm.generate.call_args
        prompt = call_args.kwargs["prompt"]
        assert "US MARKET" in prompt
        assert "ISRAEL MARKET" in prompt
        assert "AI INDUSTRY" in prompt
        assert "CRYPTO" in prompt


class TestApplyContentToMetadata:
    """Tests for the AIContentService.apply_content_to_metadata method."""

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_applies_ai_titles_to_articles(self, mock_config, mock_get_llm):
        """Test that AI titles are correctly applied to articles."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()
        sources_metadata = {
            "us": [{"text": "Original US text", "link": "http://example.com"}],
            "israel": [{"text": "Original Israel text", "link": "http://example.com"}],
            "ai": [],
            "crypto": [],
        }
        # All summaries are now in English
        newsletter_content = {
            "ai_titles": {"us:0": "US Summary", "israel:0": "Israel Summary"},
        }

        result = service.apply_content_to_metadata(sources_metadata, newsletter_content)

        assert result["us"][0]["ai_title"] == "US Summary"
        assert result["israel"][0]["ai_title"] == "Israel Summary"

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_marks_error_when_llm_fails(self, mock_config, mock_get_llm):
        """Test that articles are marked with error when LLM fails."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()
        sources_metadata = {
            "us": [
                {
                    "text": "Article text here",
                    "original_title": "Original RSS Title",
                    "source": "TestSource",
                    "link": "http://example.com",
                }
            ],
            "israel": [],
            "ai": [],
            "crypto": [],
        }
        newsletter_content = {"ai_titles": {}, "ai_titles_en": {}}

        result = service.apply_content_to_metadata(sources_metadata, newsletter_content)

        # Should mark as error with visible indicator for UI
        assert result["us"][0]["ai_title_error"] is True
        assert "⚠️ [Error]" in result["us"][0]["ai_title"]
        assert "Original RSS Title" in result["us"][0]["ai_title"]
        assert "ai_title_error_msg" in result["us"][0]
