# Sprint 4: Jan 9 - Jan 22, 2026

## Sprint Goal
Complete **v2.0** features covering visualization and personalized alerts.

## Sprint Theme
Full Feature Expansion - Delivering 2 major features to transform the newsletter into a comprehensive market intelligence platform.

---

## Completed Features

### UX: Graceful Empty Category Handling
**Completed:** January 10, 2026
**Status:** SHIPPED (v1.29.2)

- Show "No news in the last 12 hours" message instead of error when category has no articles
- Applies to weekend/off-hours when markets are closed

### DB: Feed URL Storage
**Completed:** January 10, 2026
**Status:** SHIPPED (v1.29.3)

- Added `feed_url` column to `feed_providers` table (after source_name)
- RSS feed URLs now stored in database - removed from constants.py
- Market agent reads feeds from DB via `get_all_feeds()`
- URLs auto-update when feeds are fetched

### Quality Metrics: LLM-Based Article Scoring
**Completed:** January 12, 2026
**Status:** SHIPPED (v1.30.0)

**LLM-Based Scoring:**
- Replaced hardcoded keyword filtering with LLM-based quality scoring
- `calc_confidence()` combining freshness (50%), content quality (30%), relevance (20%)
- `calc_relevance_score()` - LLM evaluates category match, market keywords, sentiment
- `calc_content_quality()` - LLM evaluates title, content depth, structure
- `get_top_articles()` with smart thresholds (IDEAL_MIN=0.70, ABSOLUTE_MIN=0.50)
- LLM-based `deduplicate_articles()` replaces keyword matching
- Created `backend/quality_prompts.py` for all quality scoring prompts

**Batch Scoring Optimization:**
- Reduced LLM calls from 40+ per refresh to ~7 total
- ONE LLM call scores ALL articles (relevance + content quality)
- ONE LLM call per category for deduplication (4 calls)
- Significant cost and latency reduction

**Quality Metrics Storage:**
- All quality metrics in single `quality_metrics` JSON column
- JSON structure: `{freshness_score, content_score, relevance_score, confidence}`
- Freshness calculated from `published_at`: 1.0 (≤2h) → 0.1 (>12h)
- API response returns nested `quality_metrics` object per article

**Database Retention:**
- Changed retention from 60 days to 10 days
- Removed 4-hour throttle - now saves every request
- Created `scripts/cleanup_old_data.py` cron cleanup script
- Runs daily at 8am US Eastern (3pm Israel time)

**Refactoring:**
- Renamed `article_filter_service.py` → `quality_metrics_service.py`
- Moved `market_agent.py` from `agents/` → `services/market_data_service.py`
- Reliability score rounded to 2 decimal places

### UI: Footer Redesign & Carousel Improvements
**Completed:** January 14, 2026
**Status:** SHIPPED (v1.30.2)

**Footer Changes:**
- Added horizontal divider between footer sections
- Moved copyright to top section below brand name
- Centered "Powered by AI" in bottom section
- Added vertical divider between social icons and links
- Created custom Twitter and LinkedIn SVG icons with transparent backgrounds
- Removed underlines from footer links, increased font size

**Carousel Changes:**
- Each carousel slide now has its own header with unique IDs
- Created custom AI robot SVG icon for AI Industry section
- Flags (US, Israel) and Crypto keep emoji styling

### DB: Feed Provider Cleanup & Expansion
**Completed:** January 15, 2026
**Status:** SHIPPED (v1.30.3)

- Removed 4 low-reliability feed providers (Investing.com Commodities, Nasdaq Earnings, OpenAI Blog, VentureBeat)
- Added Wired AI feed to AI category
- Removed source-monitor UI component (reliability data now in DB)

### Fix & Optimize: Article Scoring
**Completed:** January 15, 2026
**Status:** SHIPPED (v1.30.4)

- Fixed LLM scoring truncation bug (max_tokens 1000 → 2000)
- Reduced time window from 12 hours to 6 hours
- Reduced MAX_TO_SCORE from 10 to 7 articles per category
- Optimizes LLM costs and response times

### UI: Live Market Commentary Sidebar
**Completed:** January 19, 2026
**Status:** SHIPPED (v1.30.5)

**New Component:**
- Added right-side "Live Market Commentary" sidebar (mirrors Sentiment Tracker positioning)
- Displays scrollable feed of market tweets from trusted sources
- Mixed content from all categories (US, Israel, AI, Crypto)
- Clickable tweets link to original X posts
- Subtle scrollbar styling
- Tweet content limited to 2 lines with ellipsis for scannability
- Signal type labels per tweet (News Desk, Journalist, Strategist, Official)

**Sentiment Tracker Updates:**
- Updated "Sentiment Tracker" title font to Georgia serif (matches footer-brand)
- Increased gap between "MARKET MOOD" label and title
- Slightly larger "MARKET MOOD" label font

**Header Redesign:**
- Removed timezone display (US/Israel times)
- Added date display in header-right (e.g., "Mon, Jan 19, 2026")
- Added vertical divider between date and user greeting
- User greeting now uses footer-link style (text, not button)
- Hover color changed to pink (#d8a5bb)

**Note:** Currently using mock tweet data. X API (v2) integration planned for future sprint.

### UI: Landing Page Carousel Redesign
**Completed:** January 20, 2026
**Status:** SHIPPED (v1.30.6)

**Carousel Changes:**
- Redesigned to show 3 cards horizontally (instead of 1)
- Arrow navigation (left/right) replaces dot indicators
- Cards aligned with action-wrapper borders (850px width)
- Arrows positioned outside the card area
- Loop behavior: returns to first card after last
- Created `_carousel_cards.html` template partial for card content
- Removed box-shadow from cards for cleaner look

**Other UI Updates:**
- Dynamic footer year using Jinja2 `{{ current_year }}` (no longer hardcoded)
- Sign Up button styling: #d8a5bb background, rounded corners, proper padding
- Added 50px gap between action section and carousel

### Refactor: CSS File Split
**Completed:** January 20, 2026
**Status:** SHIPPED (v1.30.7)

Split `components.css` (1306 lines) into 6 focused files:
- `badges.css` (54 lines) - date, version, datetime badges
- `buttons.css` (202 lines) - run button, filters, topic chips
- `carousel.css` (295 lines) - landing + newsletter carousels
- `features.css` (318 lines) - why signup, features section
- `progress.css` (144 lines) - progress bars, cache status
- `modals.css` (353 lines) - auth modals

Updated HTML templates to include new CSS files. Max file size now 353 lines (was 1306).

### UI: Landing Page Redesign
**Completed:** January 20, 2026
**Status:** SHIPPED (v1.31.0)

**Hero Banner:**
- Full-width hero banner with `landing-page.png` background image
- "Faster, Smarter, and All in One Place" subtitle overlay (left-aligned)
- Bottom fade gradient to blend with content below
- Responsive breakpoints for tablet/mobile

**Simplified Layout:**
- Removed filter chips from landing page (kept on /newsletter page)
- New flow: Hero banner → Carousel cards → "Get My Newsletter" button
- Button renamed from `run-button` to `get-newsletter-btn`
- Button styled to match Sign Up button (#d8a5bb, pill shape)

**Reduced Footer Padding:**
- Footer padding reduced for cleaner look

### UI: Carousel Cards Update
**Completed:** January 21, 2026
**Status:** SHIPPED (v1.32.0)

**New Cards:**
- Added "See the Market Mood at a Glance" card (Sentiment Tracker feature)
- Added "Real-Time Insights from Trusted Voices" card (Live Market Commentary feature)
- Removed "Built for Busy People" and "Always Up to Date" cards

**Card Order (optimized for conversion):**
1. Ultra-Personalized to Your Interests (Soft Pink)
2. One Newsletter Instead of 10 Tabs (Dusty Blue)
3. Real-Time Insights from Trusted Voices (Soft Lavender)
4. A Podcast Version — Automatically (Warm Taupe)
5. See the Market Mood at a Glance (Light Sage Green)

**Icon Colors Updated:**
- Refreshed all 5 icon gradients to match app's warm, earthy palette
- Colors: Dusty Blue, Light Sage Green, Soft Lavender, Warm Taupe, Soft Pink

**Copy Improvements:**
- Changed "Your AI" to "Our AI" (more honest)
- Added "last 12 hours" timeframe to newsletter description
- Made Live Market description generic (no specific source names)

### UI: Podcast Sidebar & Carousel Nav Redesign
**Completed:** January 21, 2026
**Status:** SHIPPED (v1.32.1)

- Podcast moved to left sidebar (below Sentiment Tracker) with compact single-row controls
- Carousel nav simplified: arrows beside title (`< 🇺🇸 U.S. Market >`), dots removed
- AI emoji replaced with SVG icon in topic chips and sentiment tabs

---

## Sprint Summary

**Versions Shipped:** v1.29.2, v1.29.3, v1.30.0, v1.30.1, v1.30.2, v1.30.3, v1.30.4, v1.30.5, v1.30.6, v1.30.7, v1.31.0, v1.32.0, v1.32.1
**Features Completed:** 10 (UX Empty Handling, Feed URL Storage, Quality Metrics, UI Footer Redesign, Feed Provider Cleanup, Live Market Commentary, Landing Page Carousel, Landing Page Redesign, Carousel Cards Update, Podcast Sidebar & Carousel Nav Redesign)
**Refactors:** v1.30.7 (CSS file split)
**Bug Fixes:** v1.30.4 (LLM scoring optimization)

---

**Sprint Start:** January 9, 2026
**Sprint End:** January 22, 2026
