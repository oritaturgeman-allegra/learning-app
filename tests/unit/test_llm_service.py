"""
Unit tests for LLM service module.
"""

import pytest
from unittest.mock import patch, MagicMock

from backend.services.llm_service import LLMService, get_llm_service
from backend.exceptions import LLMError


class TestLLMServiceInit:
    """Tests for LLMService initialization."""

    @patch("backend.services.llm_service.config")
    def test_init_openai_success(self, mock_config):
        """Test successful OpenAI initialization."""
        mock_config.llm_provider = "openai"
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4o-mini"

        with patch("openai.OpenAI") as mock_openai:
            service = LLMService()

            assert service.provider == "openai"
            assert service._model == "gpt-4o-mini"
            mock_openai.assert_called_once()

    @patch("backend.services.llm_service.config")
    def test_init_gemini_success(self, mock_config):
        """Test successful Gemini initialization."""
        mock_config.llm_provider = "gemini"
        mock_config.gemini_api_key = "test-gemini-key"
        mock_config.gemini_model = "gemini-2.0-flash"

        with patch("google.generativeai.configure") as mock_configure, patch(
            "google.generativeai.GenerativeModel"
        ):
            service = LLMService()

            assert service.provider == "gemini"
            assert service._model == "gemini-2.0-flash"
            mock_configure.assert_called_once_with(api_key="test-gemini-key")

    @patch("backend.services.llm_service.config")
    def test_init_unsupported_provider(self, mock_config):
        """Test that unsupported provider raises LLMError."""
        mock_config.llm_provider = "unsupported"

        with pytest.raises(LLMError) as exc_info:
            LLMService()

        assert "Unsupported LLM provider" in str(exc_info.value)

    @patch("backend.services.llm_service.config")
    def test_init_openai_failure(self, mock_config):
        """Test OpenAI initialization failure raises LLMError."""
        mock_config.llm_provider = "openai"
        mock_config.openai_api_key = "sk-test-key"

        with patch("openai.OpenAI", side_effect=Exception("API error")):
            with pytest.raises(LLMError) as exc_info:
                LLMService()

            assert "Failed to initialize OpenAI" in str(exc_info.value)

    @patch("backend.services.llm_service.config")
    def test_init_gemini_failure(self, mock_config):
        """Test Gemini initialization failure raises LLMError."""
        mock_config.llm_provider = "gemini"
        mock_config.gemini_api_key = "test-key"

        with patch("google.generativeai.configure", side_effect=Exception("Config error")):
            with pytest.raises(LLMError) as exc_info:
                LLMService()

            assert "Failed to initialize Gemini" in str(exc_info.value)


class TestLLMServiceGenerate:
    """Tests for LLMService.generate method."""

    @patch("backend.services.llm_service.config")
    def test_generate_openai_success(self, mock_config):
        """Test successful OpenAI generation."""
        mock_config.llm_provider = "openai"
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4o-mini"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "  Generated text  "

        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response

            service = LLMService()
            result = service.generate("Test prompt", "System prompt")

            assert result == "Generated text"
            mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch("backend.services.llm_service.config")
    def test_generate_openai_failure(self, mock_config):
        """Test OpenAI generation failure raises LLMError."""
        mock_config.llm_provider = "openai"
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4o-mini"

        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.side_effect = Exception("API error")

            service = LLMService()

            with pytest.raises(LLMError) as exc_info:
                service.generate("Test prompt")

            assert "OpenAI generation failed" in str(exc_info.value)

    @patch("backend.services.llm_service.config")
    def test_generate_gemini_success(self, mock_config):
        """Test successful Gemini generation."""
        mock_config.llm_provider = "gemini"
        mock_config.gemini_api_key = "test-key"
        mock_config.gemini_model = "gemini-2.0-flash"

        mock_response = MagicMock()
        mock_response.text = "  Gemini response  "

        with patch("google.generativeai.configure"), patch(
            "google.generativeai.GenerativeModel"
        ) as mock_model_class:
            mock_model_class.return_value.generate_content.return_value = mock_response

            service = LLMService()
            result = service.generate("Test prompt", "System prompt")

            assert result == "Gemini response"

    @patch("backend.services.llm_service.config")
    def test_generate_gemini_combines_prompts(self, mock_config):
        """Test that Gemini combines system and user prompts."""
        mock_config.llm_provider = "gemini"
        mock_config.gemini_api_key = "test-key"
        mock_config.gemini_model = "gemini-2.0-flash"

        mock_response = MagicMock()
        mock_response.text = "Response"

        with patch("google.generativeai.configure"), patch(
            "google.generativeai.GenerativeModel"
        ) as mock_model_class:
            mock_model = MagicMock()
            mock_model.generate_content.return_value = mock_response
            mock_model_class.return_value = mock_model

            service = LLMService()
            service.generate("User prompt", "System prompt")

            # Check that prompts were combined
            call_args = mock_model.generate_content.call_args[0][0]
            assert "System prompt" in call_args
            assert "User prompt" in call_args

    @patch("backend.services.llm_service.config")
    def test_generate_gemini_failure(self, mock_config):
        """Test Gemini generation failure raises LLMError."""
        mock_config.llm_provider = "gemini"
        mock_config.gemini_api_key = "test-key"
        mock_config.gemini_model = "gemini-2.0-flash"

        with patch("google.generativeai.configure"), patch(
            "google.generativeai.GenerativeModel"
        ) as mock_model_class:
            mock_model_class.return_value.generate_content.side_effect = Exception("API error")

            service = LLMService()

            with pytest.raises(LLMError) as exc_info:
                service.generate("Test prompt")

            assert "Gemini generation failed" in str(exc_info.value)

    @patch("backend.services.llm_service.config")
    def test_generate_without_system_prompt(self, mock_config):
        """Test generation without system prompt."""
        mock_config.llm_provider = "openai"
        mock_config.openai_api_key = "sk-test-key"
        mock_config.openai_model = "gpt-4o-mini"

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Response"

        with patch("openai.OpenAI") as mock_openai:
            mock_openai.return_value.chat.completions.create.return_value = mock_response

            service = LLMService()
            service.generate("Test prompt")  # No system prompt

            call_args = mock_openai.return_value.chat.completions.create.call_args
            messages = call_args.kwargs["messages"]
            # Should only have user message, no system message
            assert len(messages) == 1
            assert messages[0]["role"] == "user"


class TestGetLLMService:
    """Tests for get_llm_service singleton function."""

    def test_returns_same_instance(self):
        """Test that get_llm_service returns the same instance."""
        import backend.services.llm_service as llm_module

        # Reset singleton
        llm_module._llm_service = None

        with patch.object(llm_module, "LLMService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            # First call creates instance
            result1 = get_llm_service()
            # Second call returns same instance
            result2 = get_llm_service()

            assert result1 is result2
            mock_class.assert_called_once()  # Only created once

        # Reset for other tests
        llm_module._llm_service = None

    def test_creates_instance_on_first_call(self):
        """Test that instance is created on first call."""
        import backend.services.llm_service as llm_module

        # Reset singleton
        llm_module._llm_service = None

        with patch.object(llm_module, "LLMService") as mock_class:
            mock_instance = MagicMock()
            mock_class.return_value = mock_instance

            result = get_llm_service()

            assert result == mock_instance
            mock_class.assert_called_once()

        # Reset for other tests
        llm_module._llm_service = None
