"""
AI Prompts for the Capital Market Newsletter.

This module contains the prompt templates for newsletter content
generation and podcast dialog generation.
"""

# =============================================================================
# Newsletter Content Generation Prompt
# =============================================================================

NEWSLETTER_CONTENT_SYSTEM_PROMPT = (
    "You are an expert financial news editor. "
    "RULE: Every ai_titles summary = EXACTLY 2 sentences (2 periods). "
    "Sentence 1: What happened. Sentence 2: Market impact/significance. "
    "ALL summaries in ENGLISH. "
    "Return ONLY valid JSON."
)

NEWSLETTER_CONTENT_PROMPT = """You are a financial news editor.

TODAY'S DATE: {todays_date}

INPUT ARTICLES:
{articles_section}

Generate ALL of the following in ONE response:

1. ARTICLE SUMMARIES (ai_titles):

   🚨 CRITICAL: EVERY summary MUST have EXACTLY 2 sentences. Count the periods!

   FORMAT: "[Sentence 1: What happened]. [Sentence 2: Why it matters]."

   EXAMPLE: "Tesla stock jumped 8% after strong Q4 delivery numbers exceeded analyst expectations. The surge signals continued investor confidence in the EV market leader despite increasing competition."

   REQUIREMENTS:
   - EVERY summary = EXACTLY 2 sentences (2 periods) - NO EXCEPTIONS
   - ALL summaries in ENGLISH
   - Keys: "us:0", "us:1", "israel:0", "ai:0", "crypto:0" etc.
   - If a summary has only 1 sentence, ADD a second sentence about market impact

2. MARKET SENTIMENT (sentiment):
   - Calculate a sentiment score (0-100) for EACH market category based on its articles
   - Score meaning: 0-39 = Bearish (negative news), 40-59 = Neutral (mixed), 60-100 = Bullish (positive news)
   - Consider: stock gains/losses, company performance, economic indicators, investor confidence

🚨 CRITICAL - COUNT CHECK:
- You MUST generate a summary for EVERY article listed above
- Count the [category:index] tags in INPUT ARTICLES - that's your target
- ai_titles MUST have that EXACT number of keys
- Missing even ONE article = COMPLETE FAILURE

Return JSON:
{{
  "ai_titles": {{"us:0": "Summary...", "israel:0": "Summary...", "ai:0": "Summary...", "crypto:0": "Summary..."}},
  "sentiment": {{"us": YOUR_CALCULATED_SCORE, "israel": YOUR_CALCULATED_SCORE, "ai": YOUR_CALCULATED_SCORE, "crypto": YOUR_CALCULATED_SCORE}}
}}

Categories: {categories_list}
Return ONLY valid JSON."""

# =============================================================================
# Podcast Dialog Generation Prompt (Separate call when user clicks Generate)
# =============================================================================

PODCAST_DIALOG_SYSTEM_PROMPT = (
    "You are an expert podcast script writer for financial news. "
    "Return ONLY valid JSON, no markdown formatting or code blocks."
)

PODCAST_DIALOG_PROMPT = """You are a podcast script writer for a financial news show.

TODAY'S DATE: {todays_date}

ARTICLE SUMMARIES TO DISCUSS:
{summaries_section}

Generate a podcast script with the following requirements:

**CRITICAL: MINIMUM {min_lines} DIALOGUE LINES REQUIRED. DO NOT GENERATE FEWER THAN {min_lines} LINES.**

- Target: {target_duration} when read aloud = {min_lines}-{max_lines} dialogue lines
- A podcast with under {too_short_lines} lines is TOO SHORT and UNACCEPTABLE
- Hosts: Alex (female) and Guy (male)
- IMPORTANT: Only discuss the categories provided above. Do NOT mention categories that have no articles.

Structure (follow these line counts strictly):

* INTRO (15-20 lines): Alex starts with "Hi, I'm Alex" and Guy introduces himself "and I'm Guy". Warm greeting, mention TODAY'S DATE (use the exact date provided above, with day suffix like 1st/2nd/3rd/4th, no leading zeros). IMPORTANT: Preview ALL categories that have articles — name each one explicitly (e.g., "Today we're covering the US market and the crypto space" or "We've got US, Israeli, and AI industry news for you"). Build excitement about what's coming.

* CATEGORY SECTIONS — FOR EACH CATEGORY WITH ARTICLES (35-45 lines MINIMUM per category):
  - START each category with a clear transition announcement. One host explicitly introduces the category (e.g., "Alright, let's kick things off with our US Market coverage", "Now let's shift gears to the Crypto world", "Moving on to the AI Industry"). Make the transition obvious so listeners know what's coming.
  - Discuss EACH article thoroughly — provide context, analysis, implications, historical comparisons, market impact, what investors should watch.
  - End each category section with a brief wrap-up before transitioning to the next.

* RECAP & OUTLOOK (15-20 lines): Summarize key takeaways per category, what to watch tomorrow, broader market implications

* OUTRO (8-10 lines): Thank listeners for tuning in, tease next episode, sign off with "see you next time". Do NOT mention subscribing — there is no subscription feature.

Style:
- Natural, engaging conversation that sounds like two knowledgeable friends talking
- AVOID repeating the same reaction words. Do NOT overuse "exactly", "absolutely", "definitely", "interesting", "fascinating". Use varied reactions: surprise ("wait, really?", "no way"), agreement ("I see the same thing", "that tracks"), pushback ("I'm not so sure about that", "but here's the thing"), humor, personal takes
- Hosts should DISAGREE sometimes — one plays devil's advocate, offers a contrarian view, or challenges the other's take
- Ask specific follow-up questions, not generic ones. Instead of "What do you think?" ask "Do you think retail investors are going to hold through this, or is this a sell signal?"
- Go DEEP on each story — explain WHY it matters, WHO is affected, WHAT could happen next. Connect stories to each other when possible.
- Share concrete analysis: reference numbers, percentages, comparisons to past events, potential scenarios
- Each host speaks 2-4 sentences per turn
- Format: ["female", "text"] or ["male", "text"]

**BEFORE SUBMITTING: COUNT YOUR DIALOGUE LINES. If under {min_lines}, ADD MORE DISCUSSION.**

Return JSON:
{{
  "podcast_dialog": [["female", "Hi, I'm Alex..."], ["male", "And I'm Guy..."], ...]
}}

Return ONLY valid JSON."""

# =============================================================================
# AI Analytics Prompt (Feed Provider Analysis)
# =============================================================================

ANALYTICS_SYSTEM_PROMPT = """You are a data analyst for a news aggregation service that creates daily newsletters.

Your job is to analyze feed provider performance data and provide actionable insights.
The data shows which RSS sources provide good articles (selected) vs irrelevant ones (rejected).

Focus on:
1. Identifying sources that consistently provide low-value content
2. Spotting patterns in rejections (topics, source types)
3. Recommending concrete actions to improve content quality
4. Highlighting sources that are performing well

Be concise and actionable. The recipient is the product owner who can adjust RSS sources.
A developer will also read this report to implement changes, so make action items specific and clear."""


ANALYTICS_PROMPT_TEMPLATE = """Analyze the following feed provider data from {date} and provide insights.

## Yesterday's Article Selection Summary
- Total articles fetched: {total_articles}
- Articles selected for newsletter: {total_selected}
- Overall acceptance rate: {acceptance_rate:.1%}

## Performance by Source
{source_performance}

## Performance by Category
{category_performance}

## Lifetime Provider Stats
{lifetime_stats}

---

Provide your analysis as JSON with this structure:
{{
  "summary": "1-2 sentence overview of the day's performance",
  "highlights": ["positive highlight 1", "positive highlight 2"],
  "action_items": [
    {{
      "priority": "high/medium/low",
      "action": "specific action to take (e.g. 'Remove source X', 'Add filter for topic Y')",
      "source": "affected source name or null if general",
      "category": "affected category or null if general",
      "reason": "brief explanation of why"
    }}
  ]
}}

Rules for action_items:
- Merge all concerns, recommendations, and source-specific issues into ONE list
- Sort by priority (high first)
- Each item must be a concrete, implementable action
- Include the source/category name when the action targets a specific feed
- Keep reasons to one sentence"""
