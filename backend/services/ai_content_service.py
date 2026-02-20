"""
AI Content Service - AI-generated content from news articles.
"""

import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from backend.config import config
from backend.services.llm_service import get_llm_service
from backend.exceptions import LLMError
from backend.prompts import (
    NEWSLETTER_CONTENT_SYSTEM_PROMPT,
    NEWSLETTER_CONTENT_PROMPT,
    PODCAST_DIALOG_SYSTEM_PROMPT,
    PODCAST_DIALOG_PROMPT,
)
from backend.defaults import NEWS_CATEGORIES, CATEGORY_LABELS, EMPTY_NEWSLETTER_CONTENT

logger = logging.getLogger(__name__)


class AIContentService:
    """
    Service for generating AI content from market news.

    This service:
    - Takes raw article data from RSS feeds
    - Generates AI summaries for each article (ai_titles)
    - Generates podcast dialogue on-demand (when user clicks Generate Podcast)
    """

    def __init__(self):
        self.llm = get_llm_service()  # Use shared instance
        logger.info(f"AIContentService initialized with LLM provider: {config.llm_provider}")

    @retry(
        retry=retry_if_exception_type(LLMError),
        wait=wait_exponential(multiplier=2, min=4, max=120),
        stop=stop_after_attempt(5),
    )
    def generate_newsletter_content(
        self, sources_metadata: Dict[str, List[Dict]]
    ) -> Dict[str, Any]:
        """
        Generate AI titles for articles.

        Args:
            sources_metadata: Dict with category keys and list of article dicts.

        Returns:
            Dict with ai_titles and ai_titles_en.
        """
        if not sources_metadata:
            logger.warning("generate_newsletter_content: sources_metadata is empty")
            return EMPTY_NEWSLETTER_CONTENT

        # Build articles by category
        articles_by_category: Dict[str, List[Dict]] = {}
        for category in NEWS_CATEGORIES:
            articles = sources_metadata.get(category, [])
            if articles:
                articles_by_category[category] = [
                    {"index": i, "text": a.get("text", "")[:500]}
                    for i, a in enumerate(articles)
                    if a.get("text")
                ]

        if not any(articles_by_category.values()):
            logger.warning("No articles with text found")
            return EMPTY_NEWSLETTER_CONTENT

        total_articles = sum(len(a) for a in articles_by_category.values())
        articles_per_cat = {cat: len(arts) for cat, arts in articles_by_category.items()}
        logger.info(f"Generating content for: {articles_per_cat} ({total_articles} total articles)")

        # Build prompt
        articles_section = ""
        for category, articles in articles_by_category.items():
            if articles:
                articles_section += f"\n{CATEGORY_LABELS[category]}:\n"
                for a in articles:
                    articles_section += f"[{category}:{a['index']}] {a['text']}\n"

        categories_list = ", ".join(c for c in NEWS_CATEGORIES if articles_by_category.get(c))

        todays_date = datetime.now().strftime("%A, %B %-d, %Y")

        # Add explicit article count to help LLM
        article_count_line = f"\n⚠️ TOTAL ARTICLES TO SUMMARIZE: {total_articles} (generate exactly {total_articles} ai_titles entries)\n"

        prompt = NEWSLETTER_CONTENT_PROMPT.format(
            todays_date=todays_date,
            articles_section=articles_section + article_count_line,
            categories_list=categories_list,
        )

        try:
            logger.info(
                f"Sending newsletter content request to {config.llm_provider} "
                f"(prompt length: {len(prompt)})"
            )

            result_text = self.llm.generate(
                prompt=prompt,
                system_prompt=NEWSLETTER_CONTENT_SYSTEM_PROMPT,
                temperature=0.5,
                max_tokens=8192,  # Increased for long podcast scripts
            )

            logger.info(f"LLM response received (length: {len(result_text)})")

            # Clean up markdown if present
            result_text = self._clean_json_response(result_text)

            # Parse JSON with fallback for common issues
            result = self._parse_json_response(result_text)

            # Log which keys were generated and validate title lengths
            ai_titles = result.get("ai_titles", {})
            ai_titles_keys = list(ai_titles.keys())
            logger.info(
                f"Generated newsletter content: {len(ai_titles_keys)} titles {ai_titles_keys}"
            )

            # Validate: exactly 2 sentences per summary
            single_sentence = []
            for key, title in ai_titles.items():
                if title:
                    # Count periods that end sentences (not abbreviations)
                    period_count = title.count(". ") + (1 if title.rstrip().endswith(".") else 0)
                    if period_count < 2:
                        single_sentence.append(
                            f"{key}: '{title[:60]}...' ({period_count} sentence)"
                        )
            if single_sentence:
                logger.warning(f"SINGLE-SENTENCE summaries (need 2): {single_sentence}")

            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response length: {len(result_text) if result_text else 0} chars")
            logger.error(
                f"Raw response (first 1000 chars): {result_text[:1000] if result_text else 'N/A'}"
            )
            logger.error(
                f"Raw response (last 500 chars): {result_text[-500:] if result_text and len(result_text) > 500 else 'N/A'}"
            )
            return EMPTY_NEWSLETTER_CONTENT
        except LLMError:
            logger.warning("LLM API error during newsletter content generation, retrying...")
            raise
        except Exception as e:
            logger.error(f"Newsletter content generation failed: {type(e).__name__}: {e}")
            return EMPTY_NEWSLETTER_CONTENT

    def _clean_json_response(self, text: str) -> str:
        """Remove markdown code blocks from JSON response."""
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        if text.endswith("```"):
            text = text[:-3]
        return text.strip()

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON with fallback for common LLM output issues."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            fixed_text = text
            # Fix 1: Remove trailing commas before ] or } (common Gemini issue)
            fixed_text = re.sub(r",(\s*[\]\}])", r"\1", fixed_text)
            # Fix 2: Unescaped quotes in Hebrew (e.g., ת"א for Tel Aviv)
            fixed_text = re.sub(r'([א-ת])"([א-ת0-9])', r'\1\\"\2', fixed_text)
            return json.loads(fixed_text)

    def _generate_missing_titles(
        self,
        missing_keys: List[str],
        sources_metadata: Dict[str, List[Dict]],
    ) -> Dict[str, str]:
        """Generate AI titles for articles that were missed in the main generation.

        Uses a focused prompt to generate just the missing titles.
        """
        if not missing_keys:
            return {}

        # Build a focused prompt for just the missing articles
        articles_text = []
        for key in missing_keys:
            category, idx_str = key.split(":")
            idx = int(idx_str)
            articles = sources_metadata.get(category, [])
            if idx < len(articles):
                text = articles[idx].get("text", "")[:500]
                articles_text.append(f"[{key}] {text}")

        if not articles_text:
            return {}

        # Build example using actual missing keys
        example_keys = missing_keys[:2] if len(missing_keys) >= 2 else missing_keys
        example_json = ", ".join(f'"{k}": "First sentence. Second sentence."' for k in example_keys)

        prompt = f"""Generate 2-SENTENCE summaries for each article in ENGLISH.
Format: "[What happened]. [Why it matters/market impact]."

Articles:
{chr(10).join(articles_text)}

Return ONLY valid JSON with EXACT keys from above: {{{example_json}}}"""

        try:
            logger.info(f"Generating {len(missing_keys)} missing titles...")
            result_text = self.llm.generate(
                prompt=prompt,
                system_prompt="Financial news editor. Every summary = 2 sentences. Return only valid JSON.",
                temperature=0.3,
                max_tokens=2048,
            )
            result_text = self._clean_json_response(result_text)
            titles = self._parse_json_response(result_text)
            logger.info(f"Generated {len(titles)} missing titles: {list(titles.keys())}")
            return titles
        except Exception as e:
            logger.warning(f"Failed to generate missing titles: {e}")
            return {}

    def apply_content_to_metadata(
        self, sources_metadata: Dict[str, List[Dict]], newsletter_content: Dict[str, Any]
    ) -> Dict[str, List[Dict]]:
        """
        Apply AI-generated titles to sources_metadata articles.

        Args:
            sources_metadata: Original article metadata.
            newsletter_content: Generated content with ai_titles.

        Returns:
            Updated sources_metadata with ai_title fields.
        """
        ai_titles = newsletter_content.get("ai_titles", {})

        # Calculate expected keys
        expected_keys = []
        for category in NEWS_CATEGORIES:
            for i in range(len(sources_metadata.get(category, []))):
                expected_keys.append(f"{category}:{i}")

        actual_keys = list(ai_titles.keys())
        missing_keys = [k for k in expected_keys if k not in actual_keys]

        logger.info(
            f"apply_content_to_metadata: expected {len(expected_keys)} keys, got {len(actual_keys)}"
        )

        # Retry: generate missing titles with a focused LLM call
        if missing_keys:
            logger.warning(f"MISSING ai_titles for: {missing_keys}, attempting retry...")
            retry_titles = self._generate_missing_titles(missing_keys, sources_metadata)
            for key, title in retry_titles.items():
                ai_titles[key] = title
            # Update missing keys after retry
            missing_keys = [k for k in expected_keys if k not in ai_titles]
            if missing_keys:
                logger.warning(f"Still missing after retry: {missing_keys}")

        for category in NEWS_CATEGORIES:
            for i, article in enumerate(sources_metadata.get(category, [])):
                key = f"{category}:{i}"
                if key in ai_titles:
                    article["ai_title"] = ai_titles[key]
                    article["ai_title_error"] = False
                    logger.debug(f"Applied ai_title for {key}: {ai_titles[key][:50]}...")
                else:
                    # LLM failed to generate title - mark as error for UI to display
                    original = article.get("original_title", "Unknown")
                    source = article.get("source", "Unknown")
                    logger.error(
                        f"LLM failed to generate title for {key} "
                        f"(source: {source}, original: {original[:50]}...)"
                    )
                    article["ai_title"] = f"⚠️ [Error] {original}"
                    article["ai_title_error"] = True
                    article["ai_title_error_msg"] = (
                        f"LLM failed to generate summary for this article from {source}"
                    )

        return sources_metadata

    @retry(
        retry=retry_if_exception_type(LLMError),
        wait=wait_exponential(multiplier=2, min=4, max=120),
        stop=stop_after_attempt(3),
    )
    def generate_podcast_dialog(
        self,
        sources_metadata: Dict[str, List[Dict]],
        categories: Optional[List[str]] = None,
    ) -> List[List[str]]:
        """
        Generate podcast dialogue from article summaries.

        This is called separately when user clicks "Generate Podcast",
        not during the initial /api/analyze call.

        Args:
            sources_metadata: Dict with category keys and list of article dicts.
                Each article should have 'ai_title' for the summary.
            categories: Optional list of categories to include. If None, uses
                all categories present in sources_metadata. Provides defensive
                filtering to ensure dialog matches the requested categories.

        Returns:
            List of dialogue lines: [["female", "text"], ["male", "text"], ...]
        """
        if not sources_metadata:
            logger.warning("generate_podcast_dialog: sources_metadata is empty")
            return []

        # Use provided categories or fall back to all NEWS_CATEGORIES
        # This ensures dialog only covers requested categories
        categories_to_include = categories if categories else NEWS_CATEGORIES

        # Build summaries section from article titles
        summaries_section = ""
        for category in categories_to_include:
            articles = sources_metadata.get(category, [])
            if articles:
                summaries_section += f"\n{CATEGORY_LABELS[category]}:\n"
                for article in articles:
                    title = article.get("ai_title", "")
                    if title:
                        summaries_section += f"- {title}\n"

        if not summaries_section.strip():
            logger.warning("No article summaries found for podcast")
            return []

        # Scale dialog length based on number of categories with articles
        category_count = sum(1 for cat in sources_metadata if sources_metadata.get(cat))
        # Per-category: ~40 lines. Fixed overhead (intro/recap/outro): ~40 lines
        min_lines = 40 + (category_count * 35)
        max_lines = min_lines + 30
        too_short_lines = max(50, min_lines - 30)
        duration_map = {1: "2-3 minutes", 2: "3-4 minutes", 3: "4-5 minutes"}
        target_duration = duration_map.get(category_count, "5-6 minutes")

        todays_date = datetime.now().strftime("%A, %B %-d, %Y")
        prompt = PODCAST_DIALOG_PROMPT.format(
            todays_date=todays_date,
            summaries_section=summaries_section,
            min_lines=min_lines,
            max_lines=max_lines,
            too_short_lines=too_short_lines,
            target_duration=target_duration,
        )

        try:
            logger.info(f"Generating podcast dialog (prompt length: {len(prompt)})")

            result_text = self.llm.generate(
                prompt=prompt,
                system_prompt=PODCAST_DIALOG_SYSTEM_PROMPT,
                temperature=0.7,  # Slightly higher for more creative dialogue
                max_tokens=8192,
            )

            logger.info(f"Podcast dialog response received (length: {len(result_text)})")

            # Clean and parse
            result_text = self._clean_json_response(result_text)
            result = self._parse_json_response(result_text)

            podcast_dialog = result.get("podcast_dialog", [])
            logger.info(f"Generated podcast dialog: {len(podcast_dialog)} lines")
            return podcast_dialog

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse podcast dialog response as JSON: {e}")
            return []
        except LLMError:
            logger.warning("LLM API error during podcast dialog generation, retrying...")
            raise
        except Exception as e:
            logger.error(f"Podcast dialog generation failed: {type(e).__name__}: {e}")
            return []
