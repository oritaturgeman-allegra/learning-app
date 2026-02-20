"""
Quality Metrics Service - LLM-based article selection for newsletters.

This service handles article selection using a single LLM call that applies:
- Relevance filtering (must be about capital markets/finance)
- Content quality ranking
- Freshness as tiebreaker
- Deduplication (same story = pick best)
"""

import json
import logging
from dataclasses import dataclass, field
from typing import List, TypeVar, Protocol, Dict, Any

from backend.services.llm_service import get_llm_service
from backend.quality_prompts import (
    SELECT_ARTICLES_SYSTEM_PROMPT,
    SELECT_ARTICLES_PROMPT,
)


logger = logging.getLogger(__name__)


@dataclass
class SelectionResult:
    """Result of article selection including metadata for analytics."""

    selected_articles: List[Any] = field(default_factory=list)
    selection_records: List[Dict[str, Any]] = field(default_factory=list)


class ArticleLike(Protocol):
    """Protocol for article-like objects with a text attribute."""

    text: str


# TypeVar bound to ArticleLike for proper return type inference
T = TypeVar("T", bound=ArticleLike)


def select_top_articles_llm(articles: List[T], category: str, max_count: int = 5) -> List[T]:
    """
    Select top articles using LLM direct ranking.

    Uses a single LLM call that directly selects and ranks articles.

    The LLM applies these criteria in order:
    1. Relevance (must be about capital markets/finance)
    2. Content quality (data, insights, structure)
    3. Freshness (as tiebreaker)
    4. Deduplication (same story = pick best)

    Args:
        articles: List of articles to select from
        category: Category name for context (us, israel, ai, crypto)
        max_count: Maximum number of articles to return

    Returns:
        Selected articles in ranked order (best first)
    """
    if not articles:
        return []

    if len(articles) <= max_count:
        # If we have fewer articles than max, still filter for relevance
        pass  # Continue to LLM call to filter irrelevant ones

    # Build articles list for LLM with freshness scores
    def format_article(i: int, article: T) -> str:
        parts = [f"[{i}]"]
        # Include freshness score
        freshness = getattr(article, "freshness_score", 0.5)
        parts.append(f"[F:{freshness:.1f}]")
        # Include source if available
        if hasattr(article, "source") and article.source:
            parts.append(f"({article.source})")
        # Include original_title if available
        if hasattr(article, "original_title") and article.original_title:
            parts.append(f"{article.original_title[:100]}:")
        # Include text snippet
        parts.append(article.text[:200])
        return " ".join(parts)

    articles_list = "\n".join(format_article(i, article) for i, article in enumerate(articles))

    # Map category codes to display names
    category_display = {
        "us": "US Market",
        "israel": "Israel Market",
        "ai": "AI Industry",
        "crypto": "Crypto",
    }.get(category, category)

    prompt = SELECT_ARTICLES_PROMPT.format(
        max_articles=max_count,
        category=category_display,
        articles_list=articles_list,
    )

    try:
        llm = get_llm_service()
        response = llm.generate(
            prompt=prompt,
            system_prompt=SELECT_ARTICLES_SYSTEM_PROMPT,
            temperature=0.1,
            max_tokens=200,  # Just need a short array of indices
        )

        # Parse JSON response
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
        if response.endswith("```"):
            response = response[:-3]

        parsed_response = json.loads(response.strip())

        # Handle various response formats
        if isinstance(parsed_response, dict):
            # Check if it's a single selection object: {"index": 3, "score": 0.95}
            if "index" in parsed_response:
                selected_items = [parsed_response]
            else:
                # Try common wrapper keys: {"articles": [...]} or {"result": [...]}
                for key in ["articles", "result", "indices", "selected"]:
                    if key in parsed_response and isinstance(parsed_response[key], list):
                        selected_items = parsed_response[key]
                        break
                else:
                    # No recognized key found
                    logger.warning(f"LLM returned dict without recognized key: {parsed_response}")
                    return articles[:max_count]
        elif isinstance(parsed_response, list):
            selected_items = parsed_response
        else:
            logger.warning(f"LLM returned unexpected type: {type(parsed_response)}")
            return articles[:max_count]

        # Parse items - can be either:
        # - New format: [{"index": 3, "score": 0.95}, ...]
        # - Old format: [3, 0, 7, ...]  (backward compatibility)
        valid_selections: List[tuple] = []  # List of (index, score) tuples
        seen = set()
        for item in selected_items:
            if isinstance(item, dict):
                # New format: {"index": 3, "score": 0.95}
                idx = item.get("index")
                score = item.get("score", 0.8)  # Default score if missing
            elif isinstance(item, int):
                # Old format: just index (backward compatibility)
                idx = item
                score = 0.8  # Default score for old format
            else:
                continue  # Skip invalid items

            if isinstance(idx, int) and 0 <= idx < len(articles) and idx not in seen:
                valid_selections.append((idx, float(score)))
                seen.add(idx)

        # Build result list with confidence scores attached
        result = []
        for idx, score in valid_selections[:max_count]:
            article = articles[idx]
            # Set confidence_score on the article (Article dataclass has this field)
            if hasattr(article, "confidence_score"):
                article.confidence_score = score
            result.append(article)
        valid_indices = [idx for idx, _ in valid_selections[:max_count]]

        # Log selected articles
        logger.info(
            f"LLM selected {len(result)}/{len(articles)} articles for {category} "
            f"(indices: {valid_indices[:max_count]})"
        )

        # Debug: show what was selected vs rejected
        if len(result) < len(articles):
            rejected_indices = [i for i in range(len(articles)) if i not in seen]
            for idx in rejected_indices:
                art = articles[idx]
                title = getattr(art, "original_title", art.text[:50])
                source = getattr(art, "source", "unknown")
                logger.info(f"  ❌ REJECTED [{idx}] ({source}): {title[:60]}...")
        for i, idx in enumerate(valid_indices[:max_count]):
            art = articles[idx]
            title = getattr(art, "original_title", art.text[:50])
            source = getattr(art, "source", "unknown")
            logger.info(f"  ✓ SELECTED #{i+1} [{idx}] ({source}): {title[:60]}...")

        return result

    except Exception as e:
        logger.warning(f"LLM selection failed for {category}, falling back to freshness sort: {e}")
        # Fallback: sort by freshness and return top N
        sorted_articles = sorted(
            articles,
            key=lambda a: getattr(a, "freshness_score", 0.5),
            reverse=True,
        )
        return sorted_articles[:max_count]


def select_top_articles_with_metadata(
    articles: List[T], category: str, max_count: int = 5
) -> SelectionResult:
    """
    Select top articles using LLM and return selection metadata for analytics.

    This is a wrapper around select_top_articles_llm that also captures
    which articles were selected vs rejected for the analytics service.

    Args:
        articles: List of articles to select from
        category: Category name for context (us, israel, ai, crypto)
        max_count: Maximum number of articles to return

    Returns:
        SelectionResult with selected_articles and selection_records
    """
    if not articles:
        return SelectionResult(selected_articles=[], selection_records=[])

    # Get selected articles using existing function
    selected = select_top_articles_llm(articles, category, max_count)
    selected_links = {getattr(a, "link", "") for a in selected}

    # Build selection records for ALL articles (selected + rejected)
    selection_records = []
    for article in articles:
        link = getattr(article, "link", "")
        is_selected = link in selected_links

        record = {
            "source_name": getattr(article, "source", "Unknown"),
            "category": category,
            "title": getattr(article, "original_title", "")[:500]
            or getattr(article, "text", "")[:500],
            "link": link,
            "selected": is_selected,
        }
        selection_records.append(record)

    return SelectionResult(
        selected_articles=selected,
        selection_records=selection_records,
    )
