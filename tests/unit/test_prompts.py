"""
Unit tests for prompts module.
"""

from backend.prompts import (
    NEWSLETTER_CONTENT_SYSTEM_PROMPT,
    NEWSLETTER_CONTENT_PROMPT,
    PODCAST_DIALOG_SYSTEM_PROMPT,
    PODCAST_DIALOG_PROMPT,
)


class TestNewsletterContentPrompt:
    """Tests for newsletter content generation prompts."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert NEWSLETTER_CONTENT_SYSTEM_PROMPT is not None
        assert isinstance(NEWSLETTER_CONTENT_SYSTEM_PROMPT, str)
        assert len(NEWSLETTER_CONTENT_SYSTEM_PROMPT) > 0

    def test_prompt_exists(self):
        """Test that prompt is defined."""
        assert NEWSLETTER_CONTENT_PROMPT is not None
        assert isinstance(NEWSLETTER_CONTENT_PROMPT, str)
        assert len(NEWSLETTER_CONTENT_PROMPT) > 0

    def test_prompt_has_placeholders(self):
        """Test that prompt has required placeholders."""
        assert "{todays_date}" in NEWSLETTER_CONTENT_PROMPT
        assert "{articles_section}" in NEWSLETTER_CONTENT_PROMPT
        assert "{categories_list}" in NEWSLETTER_CONTENT_PROMPT

    def test_prompt_mentions_json(self):
        """Test that prompt requests JSON output."""
        assert "JSON" in NEWSLETTER_CONTENT_PROMPT


class TestPodcastDialogPrompt:
    """Tests for podcast dialog generation prompts."""

    def test_system_prompt_exists(self):
        """Test that system prompt is defined."""
        assert PODCAST_DIALOG_SYSTEM_PROMPT is not None
        assert isinstance(PODCAST_DIALOG_SYSTEM_PROMPT, str)
        assert len(PODCAST_DIALOG_SYSTEM_PROMPT) > 0

    def test_prompt_exists(self):
        """Test that prompt is defined."""
        assert PODCAST_DIALOG_PROMPT is not None
        assert isinstance(PODCAST_DIALOG_PROMPT, str)
        assert len(PODCAST_DIALOG_PROMPT) > 0

    def test_prompt_has_placeholders(self):
        """Test that prompt has required placeholders."""
        assert "{todays_date}" in PODCAST_DIALOG_PROMPT
        assert "{summaries_section}" in PODCAST_DIALOG_PROMPT

    def test_prompt_mentions_hosts(self):
        """Test that prompt mentions podcast hosts."""
        assert "Alex" in PODCAST_DIALOG_PROMPT
        assert "Guy" in PODCAST_DIALOG_PROMPT

    def test_prompt_mentions_json(self):
        """Test that prompt requests JSON output."""
        assert "JSON" in PODCAST_DIALOG_PROMPT
