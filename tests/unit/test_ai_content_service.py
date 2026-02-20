"""
Unit tests for AI content service module.
"""

from unittest.mock import patch, MagicMock

from backend.services.ai_content_service import AIContentService
from backend.defaults import EMPTY_NEWSLETTER_CONTENT


class TestAIContentService:
    """Tests for AIContentService class."""

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_init_success(self, mock_config, mock_get_llm):
        """Test successful initialization."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()

        assert service.llm is not None
        mock_get_llm.assert_called_once()

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_generate_newsletter_content_empty_metadata(self, mock_config, mock_get_llm):
        """Test that empty metadata returns empty content."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()
        result = service.generate_newsletter_content({})

        assert result == EMPTY_NEWSLETTER_CONTENT

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_generate_newsletter_content_no_text(self, mock_config, mock_get_llm):
        """Test that articles without text return empty content."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()
        result = service.generate_newsletter_content(
            {
                "us": [{"source": "test"}],  # No "text" field
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )

        assert result == EMPTY_NEWSLETTER_CONTENT

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_generate_newsletter_content_success(self, mock_config, mock_get_llm):
        """Test successful content generation."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = """{
            "ai_titles": {"us:0": "Test summary"},
            "ai_titles_en": {"us:0": "Test summary"},
            "podcast_dialog": [["female", "Hello"], ["male", "Hi"]]
        }"""
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        result = service.generate_newsletter_content(
            {
                "us": [{"text": "Test article about markets"}],
                "israel": [],
                "ai": [],
                "crypto": [],
            }
        )

        assert "ai_titles" in result
        assert result["ai_titles"]["us:0"] == "Test summary"
        assert len(result["podcast_dialog"]) == 2

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_generate_newsletter_content_with_markdown(self, mock_config, mock_get_llm):
        """Test that markdown code blocks are cleaned from response."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        mock_llm.generate.return_value = """```json
{
    "ai_titles": {},
    "ai_titles_en": {},
    "podcast_dialog": []
}
```"""
        mock_get_llm.return_value = mock_llm

        service = AIContentService()
        result = service.generate_newsletter_content(
            {
                "us": [{"text": "Test article"}],
            }
        )

        assert "ai_titles" in result
        assert "podcast_dialog" in result

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_clean_json_response(self, mock_config, mock_get_llm):
        """Test JSON response cleaning."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()

        # Test with markdown code block
        result = service._clean_json_response('```json\n{"key": "value"}\n```')
        assert result == '{"key": "value"}'

        # Test without markdown
        result = service._clean_json_response('{"key": "value"}')
        assert result == '{"key": "value"}'

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_parse_json_response_hebrew_quotes(self, mock_config, mock_get_llm):
        """Test JSON parsing handles Hebrew quote escaping."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()

        # Standard JSON should parse fine
        result = service._parse_json_response('{"key": "value"}')
        assert result == {"key": "value"}

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_apply_content_to_metadata(self, mock_config, mock_get_llm):
        """Test applying generated content to article metadata."""
        mock_config.llm_provider = "openai"
        mock_get_llm.return_value = MagicMock()

        service = AIContentService()

        sources_metadata = {
            "us": [{"text": "Original text", "source": "Test"}],
            "israel": [],
            "ai": [],
            "crypto": [],
        }

        newsletter_content = {
            "ai_titles": {"us:0": "AI generated summary"},
        }

        result = service.apply_content_to_metadata(sources_metadata, newsletter_content)

        assert result["us"][0]["ai_title"] == "AI generated summary"

    @patch("backend.services.ai_content_service.get_llm_service")
    @patch("backend.services.ai_content_service.config")
    def test_apply_content_to_metadata_retry_missing(self, mock_config, mock_get_llm):
        """Test that missing titles trigger a retry LLM call."""
        mock_config.llm_provider = "openai"

        mock_llm = MagicMock()
        # Mock the retry call to return a title
        mock_llm.generate.return_value = '{"us:0": "LLM generated retry title"}'
        mock_get_llm.return_value = mock_llm

        service = AIContentService()

        sources_metadata = {
            "us": [{"text": "Original text that is quite long", "source": "Test"}],
            "israel": [],
            "ai": [],
            "crypto": [],
        }

        # Empty newsletter content - no AI titles (triggers retry)
        newsletter_content = {"ai_titles": {}, "ai_titles_en": {}}

        result = service.apply_content_to_metadata(sources_metadata, newsletter_content)

        # Should have called LLM to generate missing title
        mock_llm.generate.assert_called_once()
        assert result["us"][0]["ai_title"] == "LLM generated retry title"
