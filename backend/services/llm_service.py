"""
LLM Service - Simple abstraction for multiple LLM providers.

Supports OpenAI and Google Gemini for text generation.
"""

import logging
from typing import Optional

from backend.config import config
from backend.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMService:
    """
    Unified LLM service that handles both OpenAI and Gemini.

    The provider is determined by config.llm_provider at initialization.
    """

    def __init__(self):
        self.provider = config.llm_provider

        if self.provider == "openai":
            self._init_openai()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            raise LLMError(f"Unsupported LLM provider: {self.provider}")

    def _init_openai(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=config.openai_api_key)
            self._model = config.openai_model
            logger.info(f"LLM service initialized: OpenAI ({self._model})")
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenAI: {e}")

    def _init_gemini(self) -> None:
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config.gemini_api_key)
            self._client = genai.GenerativeModel(config.gemini_model)
            self._model = config.gemini_model
            logger.info(f"LLM service initialized: Gemini ({self._model})")
        except Exception as e:
            raise LLMError(f"Failed to initialize Gemini: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: int = 4000,
    ) -> str:
        """
        Generate text from prompt.

        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Creativity level (0-1)
            max_tokens: Maximum response length

        Returns:
            Generated text string
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
        else:
            return self._generate_gemini(prompt, system_prompt, temperature, max_tokens)

    def _generate_openai(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate using OpenAI API."""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},  # Guarantees valid JSON
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise LLMError(f"OpenAI generation failed: {e}")

    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str],
        temperature: float,
        max_tokens: int,
    ) -> str:
        """Generate using Gemini API."""
        try:
            # Gemini doesn't have separate system prompt, so combine them
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = self._client.generate_content(
                full_prompt, generation_config=generation_config
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            raise LLMError(f"Gemini generation failed: {e}")


# Singleton instance
_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    """
    Get the shared LLM service instance.

    Use this when you want to share the same client across multiple services.
    Benefits:
    - Single client instance (memory efficient)
    - Easy to add rate limiting later
    - Centralized logging/metrics
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
