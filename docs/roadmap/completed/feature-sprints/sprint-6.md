# Sprint 6: Feb 6 - Feb 19, 2026

## Sprint Goal
**Production Launch** - Deploy the application to production, then enhance with content discovery features.

## Sprint Theme
Infrastructure First - Get to production mid-sprint, then ship new features as live updates.

---

## Completed Features

### 1. Topic Filter Focus Ring Fix (v1.48.7)
Focus ring now only appears on keyboard navigation, not mouse clicks.

---

### 2. Podcast Category Filtering Fix (v1.48.8)
Podcast dialog now correctly filters content to only the requested categories.

---

### 3. Header Date Auto-Update (v1.48.9, fixed in v1.49.1)
Added visibilitychange listener but missed updating the `.header-date` element. Fixed in v1.49.1.

---

### 4. Podcast Voice & Content Improvements (v1.48.10 - v1.48.12)
- Lighter male voice for better listening experience
- Removed subscribe mention from podcast intro
- Marketing-friendly "Free plan" message for podcast limit
- Refined limit message with premium teaser

---

### 5. Date-Based Podcast Caching (v1.48.13)
~97% cost reduction with shared caching across users.
- Cache key: `podcast_YYYY-MM-DD_<sorted_categories>` (max 16/day)
- Same categories = same podcast for all users
- 24-hour TTL

---

### 6. Podcast Analytics & Limit Increase (v1.48.14)
Track all podcast requests and increase daily limit to 2.
- Added `cached` column to `podcast_generations` table
- Records both cache hits and misses for analytics
- Only cache misses count against daily limit

---

### 7. Environment Configuration (v1.48.15)
Production-ready environment configuration.
- `.env.example` with all 52 environment variables documented
- Fixed config duplication in `backend/models/base.py`
- Cross-field validation for email, OAuth, rate limiting
- Created `docs/deployment/production-checklist.md`

---

### 8. Supabase Migration (v1.49.0)
Migrated database from SQLite to Supabase PostgreSQL.
- 5 tables: users, newsletters, articles, feed_providers, podcast_generations
- Row Level Security enabled on user-specific tables
- Created schema and RLS scripts in `scripts/`

---

### 9. Header Date Fix (v1.49.1)
Fixed header date not updating when returning to background tab. Added `.header-date` update to `updateAllTimezones()`.

---

### 10. Sentiment History Averaging (v1.49.2)
Fixed sentiment tracker to show accurate historical data.
- Today: Shows latest sentiment from DB
- Past days: Shows average of all scheduler runs that day

---

### 11. Supabase pgbouncer Connection Fix (v1.49.3)
Fixed database connection failure with Supabase.
- Strips unsupported `pgbouncer=true` param from connection strings
- psycopg2 driver doesn't recognize this Supabase-added parameter

---

### 12. LLM Retry Key Fix (v1.49.4)
Fixed LLM retry for missing article titles.
- Retry prompt now uses actual article keys (e.g., `us:2`) instead of generic `category:0`

---

### 13. Low-Relevance Article Filter (v1.49.5)
Added minimum relevance threshold to filter out irrelevant articles.
- Political/war news filtered even if fresh
- Added explicit negative examples to scoring prompts

---

### 14. LLM Direct Article Selection (v1.49.6)
Refactored article ranking from weighted formula to LLM direct selection.
- Old: `confidence = freshness*0.50 + content*0.30 + relevance*0.20`
- New: LLM applies cascading filters (relevance → quality → freshness → dedup) in one call
- Handles wrapped responses like `{"articles": [...]}` from gpt-4o-mini

---

### 15. LLM Confidence Score per Article (v1.49.7)
LLM now returns a confidence score (0.0-1.0) for each selected article.
- Changed response format from `[3, 0, 7]` to `[{"index": 3, "score": 0.95}, ...]`
- Score represents overall article quality as judged by LLM
- Backward compatible: still parses old index-only format with default 0.8 score

---

### 16. Simplified Article Schema (v1.49.8)
Replaced `quality_metrics` JSON column with single `confidence_score` float.
- Removed legacy quality fields (freshness_score, content_score, relevance_score in DB)
- LLM-assigned score stored directly as float (0.0-1.0)
- Alembic migration: `b51548dd78c2_replace_quality_metrics_with_confidence_score`

---

### 17. Category-Aware Article Selection (v1.49.9)
Fixed LLM over-filtering articles in AI and Crypto categories.
- System prompt now category-aware: AI Industry news (product launches, talent moves) and Crypto news (price movements, ETF flows) are properly selected
- Changed prompt to encourage selecting more articles rather than being overly conservative
- Market categories still filter out political/war news without market angle

---

### 18. Extended Article Time Window (v1.49.10)
Increased article freshness window from 6 hours to 12 hours.
- More articles to choose from = better LLM selection
- Solves sparse newsletter issue during low-activity periods
- Minimal cost increase (~$0.05/month)

---

### 19. Podcast Male Voice Update (v1.49.11)
Changed male podcast voice from "onyx" to "fable" for better audio quality.
- Fable provides better volume balance with nova (female host)
- No cost change (same OpenAI tts-1-hd pricing)

---

### 20. AI Analytics Service (v1.50.0)
Daily feed provider analysis with automated email reports.
- AIAnalyticsService: LLM-powered analysis of article selection patterns
- ArticleSelection model: Tracks selected/rejected articles per source
- Scheduled daily at 08:00 UTC (10:00 AM Israel)
- Email report with highlights, concerns, and actionable recommendations
- ~$0.03/month additional cost (gpt-4o-mini)

---

### 21. Feed Provider Cleanup (v1.50.1)
Removed paywalled/broken RSS sources and synced test fixtures with production DB.
- Removed paywalled sources: FT, TheMarker, MIT Tech Review, Calcalist
- Added free alternatives: MarketWatch, Reuters Business, Ynet Calcala
- Added AI sources: AI Business, AI News, Google AI Blog, Hacker News AI, NVIDIA AI Blog, Wired AI, The AI Journal
- Updated test MOCK_FEEDS to match production Supabase (18 sources)

---

### 22. Newsletter Button Loading UX (v1.50.2)
Simplified newsletter loading to match podcast button UX.
- Removed progress bar loader (0% Fetching data...)
- Button now shows inline spinner with "Loading..." text (like podcast button)

---

### 23. Sentry Integration & TTS Validation (v1.50.3)
Added `/sentry` command for monitoring and fixed TTS voice configuration.
- `/sentry` command: Fetches, analyzes, auto-fixes, and documents Sentry issues
- TTS voice validation: Prevents invalid OpenAI/Gemini voice combinations at startup
- Disabled Sentry in tests: Test errors no longer pollute Sentry dashboard

---

### 24. Railway Deployment Setup (v1.51.0)
Production deployment configuration for Railway platform.
- `Dockerfile`: Python 3.13 + ffmpeg with health check
- `.dockerignore`: Excludes dev files, secrets, caches
- `railway.toml`: Health check, restart policy configuration
- `.github/workflows/deploy.yml`: CI/CD auto-deploy on push to main
- Persistent volume ready for `audio_cache/` (manual Railway step)

---

### 25. Google OAuth Unified Login/Signup (v1.51.1)
Simplified Google OAuth flow - login auto-creates account if user doesn't exist.
- Removed "No account found. Please sign up first" error for new Google users
- Users can now click "Log in with Google" even on first visit
- Still rejects password accounts trying to use Google OAuth (security)

---

### 26. Sentry Fixes - Podcast ffmpeg Merge (v1.51.2)
Fixed ffmpeg exit code 254 crash during podcast audio merge in production.
- Fix: Replaced `-c copy` (stream copy) with re-encoding via libmp3lame for concat compatibility
- Fix: Added input file validation (existence + non-empty) before merge
- Fix: Improved ffmpeg error logging - extracts actual error lines instead of dumping full version info
- Fix: Added ffmpeg-specific error handling for Gemini WAV→MP3 conversion

---

### 27. Responsive Layout for 14-inch Screens (v1.51.3 - v1.51.5)
Sidebars and center content scale fluidly on 14-inch screens.
- Fix: Fluid sidebar widths with `clamp(260px, 20vw, 320px)` and offsets with `clamp(16px, 3vw, 60px)`
- Fix: Center content max-width adapts to sidebar footprint via `min(850px, calc(...))`
- Fix: Lowered hide breakpoint from 1400px to 1200px
- Fix: Filter chips wrap and action section padding scales on medium screens
- Fix: Footer gradient now opaque so content doesn't bleed through
- Fix: Button removed from absolute positioning to flex document flow (v1.51.6)
- Fix: Action row uses flex-wrap with proper gap for responsive wrapping

---

### 28. Podcast Sidebar Card Redesign (v1.51.7)
Compact podcast sidebar with redesigned button layout and subtitle placement.
- Reduced card padding and margins for tighter alignment with commentary sidebar
- Moved "Generate Podcast" button to normal flow below title with squared shape (8px radius)
- Relocated subtitle text inline with AUDIO header label via CSS pseudo-element
- Commentary tweets max-height reduced to show 3 items
- Sentiment card bottom padding reduced for better spacing

---

### 29. Version Update Popup (v1.52.0)
"What's New" popup that shows changelog when the app version changes.
- Auto-shows for returning users on page load when version differs from localStorage
- Stale tab detection via `visibilitychange` + `GET /api/version` — prompts refresh
- `APP_CHANGELOG` in defaults.py as single source of truth for recent updates
- Reuses existing modal infrastructure (overlay, focus trap, Escape dismiss)

---

### 30. Action Row Responsive Fix + Deploy Cleanup (v1.52.1)
Action row stacks vertically on narrow screens; removed stray CSS brace.
- `.action-row` switches to `flex-direction: column` at `max-width: 900px`
- Removed redundant `deploy.yml` — Railway auto-deploy is sufficient
- Cleaned up `workflow_call` trigger from `unit-tests.yml`

---

### 31. Version Popup Double-Fire Fix (v1.52.2)
Stale-tab refresh no longer triggers a second "Got it" popup.
- `checkVersionUpdate()` now detects page reloads via `performance.getEntriesByType('navigation')` and silently saves the version instead of showing "What's New"

---

### 32. Run Button Alignment Fix (v1.52.3)
"Get My Newsletter" button now sits inline with filter chips on all screen sizes.
- Removed `flex-wrap: wrap` from `.action-row` so the button stays on the same line
- Reduced button padding and font-size to be proportional with topic chips
- Replaced `min-width` with `flex-shrink: 0` to prevent squishing without forcing width

---

### 33. Version Popup — Show Latest 3 Only (v1.52.4)
Reduced changelog entries in the "What's New" popup from 5 to 3 for a cleaner, less cluttered display.

---

### 34. Topic Selector Refactor (v1.52.5)
Restructured topic selector for better responsiveness and breathing room.
- Moved "Get My Newsletter" button below chips, centered
- Removed redundant "Selected: X, Y, Z" text (chip state already shows selection)
- Chips centered horizontally with responsive spacing

### 35. Analytics Report Redesign + Chip Trackpad Scroll (v1.52.6)
Redesigned analytics email report and enabled trackpad scrolling for topic chips.
- Consolidated Concerns/Recommendations/Sources into single "Action Required" section with priority tags
- Added 📋 copy-to-clipboard web page (`/api/analytics/report`) linked from email header
- Widened email template from 800px to 900px
- Enabled trackpad scrolling on topic chips with hidden scrollbar
- "+N more" chip overflow always wraps to start (removed "← back" button)

---

### 36. Analytics Report Supabase Persistence (v1.52.7)
Migrated analytics report storage from local JSON file to Supabase database.
- New `analytics_reports` table with upsert-by-date pattern
- Copy-to-clipboard page now works after Railway deploys/restarts
- In-memory cache kept for fast access, DB as persistent fallback

---

### 37. New News Categories: Space, Infrastructure, Energy (v1.53.0)
Added 3 new topic categories with RSS feed sources and UI chip selectors.
- Space (SpaceNews), Infrastructure (Construction Dive), Energy (CleanTechnica, Utility Dive)
- Updated `NEWS_CATEGORIES`, `CATEGORY_LABELS`, `CATEGORY_TO_COUNT_KEY` in backend defaults
- Frontend config and chip selector updated to include all 7 categories
- Narrowed action section width so only 3 chips visible with "+N more" overflow

---

### 38. Full Category Pipeline: Carousel + Sentiment + DB (v1.53.1)
Fixed new categories not displaying articles in carousel or saving to database.
- Replaced hardcoded `DB_CATEGORIES` with `NEWS_CATEGORIES` from defaults (single source of truth)
- Dynamic `input_counts` in API using `CATEGORY_TO_COUNT_KEY`
- Added carousel slides and sentiment tabs for Space, Infrastructure, Energy
- Removed dead `TOPIC_LABELS` from JS

---

### 39. News Category Tabs (v1.53.2)
Replaced carousel arrow navigation with horizontal tab bar for direct category access.
- One-click access to any of the 7 categories (was up to 6 arrow clicks)
- Tab style matches existing sentiment tabs pattern
- Removed arrow buttons, dots, and arrow keyboard navigation

### 40. Landing Page Topic Selector (v1.54.0)
Topic selector (category chips + "Get My Newsletter" button) now appears on the landing page, letting users personalize before signing up.
- Extracted shared `_topic_selector.html` partial and `filters.js` for DRY code
- Why-signup carousel relocated below the topic selector
- Selected categories persist to localStorage for seamless signup → newsletter flow

---

### 41. Instant Newsletter Load + Auth Modal Redesign (v1.54.1)
Pre-fetches newsletter data before navigation so /newsletter renders with no skeleton screens.
- Login-first auth flow with Google at top, simplified signup with confirm password
- Removed action section border/background for cleaner chip layout

---

## Sprint Summary

**Versions Shipped:** v1.48.7 - v1.54.1
**Features Completed:** 41 (16 fixes, 25 enhancements/infrastructure)

---

## Retrospective

_To be completed after sprint_

---

**Sprint Start:** February 6, 2026
**Sprint End:** February 19, 2026
**Next Sprint Planning:** February 20, 2026
