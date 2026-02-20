# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
Ship **v1.3.7 - v1.13.0** with podcast optimization, source monitoring, database storage, crypto coverage, polished UI, and FastAPI migration.

## Sprint Theme
Foundation, Expansion & Polish - Enterprise-grade infrastructure, crypto market coverage, professional UI design, and modern async framework.

---

## ✅ Completed Features

### Feature: User Authentication System 🔐
**Completed:** December 11, 2025
**Status:** SHIPPED (v1.23.0 - v1.23.2)
**User Value:** Users can create accounts and log in to access personalized newsletter experience

**Pain Point Solved:**
- ✅ No user accounts - everyone saw the same generic newsletter
- ✅ No way to save preferences persistently
- ✅ No foundation for personalized content delivery

**Implementation Completed:**
- ✅ Login/Sign Up modals with smooth transitions (280ms + 80ms delay)
- ✅ 5th "Ultra-Personalized" feature card on landing page
- ✅ Users database table with proper schema
- ✅ user_id foreign key on newsletters table
- ✅ Signup/Login API endpoints (`/api/auth/signup`, `/api/auth/login`, `/api/auth/me`)
- ✅ bcrypt password hashing for secure credential storage
- ✅ Password strength validation (8+ chars, uppercase, lowercase, number)
- ✅ Inline error messages styled to match design system
- ✅ Password visibility toggle (eye icon)
- ✅ Password requirements tooltip on info icon hover

**Database Schema:**
```
users:
├── id, name, email, preferred_categories
├── is_active, last_login_at
├── password_hash, google_id (for future OAuth)
├── email_notifications
└── created_at, updated_at

newsletters:
├── user_id (FK) - links newsletter to user
└── ... existing columns
```

**Files Created/Modified:**
- `backend/models/user.py` (NEW) - User SQLAlchemy model
- `backend/routes/auth.py` (NEW) - Auth endpoints with bcrypt
- `backend/services/db_service.py` - User CRUD methods
- `backend/web_app.py` - Registered auth router
- `frontend/templates/index.html` - Login/Signup modals, password fields
- `frontend/static/css/components.css` - Modal styles, auth-error, tooltips
- `frontend/static/js/main.js` - Auth handlers, modal transitions
- Alembic migrations for users table and newsletters FK

**Success Metrics:**
- ✅ All tests passing
- ✅ Secure password storage with bcrypt
- ✅ UI matches design system aesthetic
- ✅ Foundation ready for Google OAuth and personalization

---

### Feature: Category Filtering & Smart Caching 🎛️
**Completed:** December 7, 2025
**Status:** SHIPPED (v1.16.1)
**User Value:** Personalize your newsletter by selecting specific market categories; smart caching reduces API costs

**Pain Point Solved:**
- ✅ Users had to see all categories even when only interested in specific markets
- ✅ No way to customize content to user preferences
- ✅ Separate filter combinations triggered redundant OpenAI API calls

**Implementation Completed:**
- ✅ Category filter toggles (US Market, Israeli Market, AI Industry, Crypto)
- ✅ Filter state persists in localStorage (first visit defaults to all selected)
- ✅ Button disabled until at least one category selected
- ✅ API accepts `categories` parameter to filter RSS feeds
- ✅ Smart subset caching: reuses superset cache data (e.g., "all categories" cache serves "US only" request)
- ✅ UI hides unselected category sections from results
- ✅ Stats bar shows only selected categories

**Files Modified:**
- `frontend/templates/index.html` - Filter toggle UI, section visibility
- `frontend/static/css/components.css` - Toggle pill styles with checkboxes
- `frontend/static/js/main.js` - Filter state management, localStorage, display filtering
- `backend/web_app.py` - Categories query parameter
- `backend/agents/market_agent.py` - Filter feeds by category
- `backend/services/newsletter_cache_service.py` - Smart superset caching logic

**Success Metrics:**
- ✅ 27 cache service tests passing (4 new superset tests)
- ✅ 13 new category filtering tests (unit + integration)
- ✅ Zero extra API calls when requesting subset of cached categories

---

### Feature: Category-Aware Podcast Caching 🎙️
**Completed:** December 8, 2025
**Status:** SHIPPED (v1.18.0)
**User Value:** Podcasts now respect selected categories with smart superset reuse, saving OpenAI TTS API costs

**Pain Point Solved:**
- ✅ Podcast was generated for all 4 categories regardless of user selection
- ✅ No caching based on category combinations
- ✅ Users couldn't get category-specific podcasts

**Implementation Completed:**
- ✅ Frontend sends selected categories with podcast request
- ✅ Cache key includes categories (different combinations = different cache)
- ✅ Smart superset caching: if all 4 categories cached, reuses for US+Israel request
- ✅ Podcast metadata includes categories for cache lookup
- ✅ Cache TTL aligned with newsletter (60 min) to prevent stale content

**Files Modified:**
- `backend/routes/api.py` - Added categories field to PodcastRequest
- `backend/services/tts_service.py` - Category-aware cache key, superset finder
- `frontend/static/js/main.js` - Send categories with podcast request
- `backend/config.py` - Aligned audio_cache_ttl with newsletter (60 min)

**Success Metrics:**
- ✅ 34 podcast tests passing (8 new category-aware tests)
- ✅ Zero extra TTS API calls when requesting subset of cached categories
- ✅ Cache TTL consistency between newsletter and podcast

---

### Refactor: Flask to FastAPI Migration 🚀
**Completed:** December 4, 2025
**Status:** SHIPPED (v1.13.0)
**User Value:** Cleaner async code, auto-generated API documentation, faster performance

**Pain Point Solved:**
- ✅ Flask required sync wrappers for async RSS fetching
- ✅ No automatic API documentation
- ✅ Threading for background tasks (less elegant than native async)
- ✅ Redundant CLI entry point (main.py) when web UI exists

**Implementation Completed:**
- ✅ Migrated all routes from Flask to FastAPI
- ✅ Native async/await for RSS fetching (no more `asyncio.run()` wrapper in routes)
- ✅ Auto-generated Swagger docs at `/docs` and ReDoc at `/redoc`
- ✅ FastAPI's `BackgroundTasks` for podcast generation
- ✅ Pydantic models for request validation (already used, now native)
- ✅ `StreamingResponse` for SSE podcast progress
- ✅ Removed `main.py` CLI (use web UI or curl instead)
- ✅ Updated all tests to use FastAPI's `TestClient`

**Files Modified:**
- `backend/web_app.py` - Complete rewrite to FastAPI
- `backend/agents/market_agent.py` - Removed sync wrapper
- `backend/agents/__init__.py` - Export async function
- `tests/integration/test_web_api.py` - FastAPI TestClient
- `tests/integration/test_podcast_api.py` - FastAPI TestClient
- `tests/unit/test_market_agent.py` - Local sync helper for tests
- `tests/integration/test_crew_execution.py` - Local sync helper for tests
- `CLAUDE.md` - Updated commands and docs
- `README.md` - Updated run instructions

**Files Deleted:**
- `backend/main.py` - CLI removed (use web UI instead)

**New Endpoints:**
| Route | Purpose |
|-------|---------|
| `/docs` | Swagger API documentation |
| `/redoc` | ReDoc API documentation |

**Success Metrics:**
- ✅ 207/207 tests passing (100% test success rate)
- ✅ Native async throughout (cleaner code)
- ✅ Auto API docs improve developer experience

---

### Feature: Enhanced UI & Design System 🎨
**Completed:** December 3, 2025
**Status:** SHIPPED (v1.12.0)
**User Value:** Professional, polished interface with better UX and consistent design language

**Pain Point Solved:**
- ✅ Single timezone display - users in different regions couldn't see relevant times
- ✅ No progress feedback during analysis - only endless spinner
- ✅ Dark footer didn't match the app's pastel aesthetic
- ✅ No centralized design system for consistent styling
- ✅ Documentation files scattered in root directory

**Implementation Completed:**
- ✅ Multi-timezone clocks in header (US/Israel/UK)
- ✅ Progress bar with stages for "Run Market Analysis" (replaces spinner)
- ✅ Pastel-themed footer with social links (X, LinkedIn)
- ✅ "Powered by Crew AI" branding in footer
- ✅ "Covering news from the last 12 hours" text in header
- ✅ Cache status shows "Refresh in Xm" countdown
- ✅ Version badge moved to right side of header
- ✅ Created `docs/design.md` with official color palette
- ✅ Reorganized docs into `docs/` folder

**Color Palette Defined:**
| Color | Hex | Usage |
|-------|-----|-------|
| Mint Light | `#dcffe2` | Backgrounds, success |
| Lavender | `#f1d7ff` | Accents |
| Lavender Light | `#f7e5ff` | Backgrounds |
| Mint | `#c8ffe5` | Cards |
| Sage Green | `#a0e3bc` | Hover states |
| Sky Blue | `#b1edff` | Information |
| Purple Muted | `#b69ac9` | Primary accent |

**Files Modified:**
- `frontend/templates/index.html` - Header, footer, progress bar, timezones
- `docs/design.md` (NEW) - Design system documentation
- `CLAUDE.md` - Updated paths to docs/
- `README.md` - Updated roadmap links

**Files Reorganized:**
- `PYTHON_BEST_PRACTICES.md` → `docs/PYTHON_BEST_PRACTICES.md`
- `CLAUDE_MD_GUIDELINES.md` → `docs/CLAUDE_MD_GUIDELINES.md`
- `roadmap/` → `docs/roadmap/`

**Success Metrics:**
- ✅ 200/200 tests passing (100% test success rate)
- ✅ Consistent design language across UI
- ✅ Better organized documentation structure

---

### Feature: Crypto Market Sources ₿
**Completed:** November 30, 2025
**Status:** SHIPPED (v1.9.0)
**User Value:** Cryptocurrency market news coverage alongside traditional markets

**Pain Point Solved:**
- ✅ No crypto coverage - users had to check separate sources for crypto news
- ✅ Podcast didn't mention crypto developments
- ✅ Newsletter was missing a major asset class for traders

**Implementation Completed:**
- ✅ Added 5 crypto RSS feeds to `backend/constants.py`:
  - CoinDesk, Cointelegraph, Bitcoin Magazine, CryptoPotato, Decrypt
- ✅ Updated `market_agent.py` to fetch crypto feeds (sync + async)
- ✅ Updated AI prompt to include crypto in analysis
- ✅ Added Crypto section to UI (next to AI, below Israel)
- ✅ Podcast now includes crypto news and recap segment
- ✅ Added crypto templates to `podcast_templates.py`

**Files Modified:**
- `backend/constants.py` - Added CRYPTO_FEEDS list
- `backend/agents/market_agent.py` - Fetch crypto in both sync/async
- `backend/prompts.py` - Include crypto in analysis prompt
- `backend/services/tts_service.py` - Crypto section in dialogue
- `backend/services/podcast_templates.py` - Crypto templates and recap
- `backend/web_app.py` - Include crypto in input_counts
- `frontend/templates/index.html` - Crypto UI section

**Success Metrics:**
- ✅ 183/183 tests passing (100% test success rate)
- ✅ 5 crypto sources now fetched alongside other feeds
- ✅ Crypto news in UI and podcast

---

### Feature: Database Storage for Analytics 🗄️
**Completed:** November 30, 2025
**Status:** SHIPPED (v1.6.0)
**User Value:** Historical tracking of newsletters and source health for analytics

**Pain Point Solved:**
- ✅ No historical data - each analysis was ephemeral (lost on refresh)
- ✅ Can't track which RSS sources are reliable over time
- ✅ No foundation for future analytics dashboard

**Implementation Completed:**
- ✅ Added SQLAlchemy ORM with Newsletter and SourceStat models
- ✅ Set up Alembic migrations for schema management
- ✅ Created DatabaseService for high-level DB operations
- ✅ Each "Run Market Analysis" saves to database automatically
- ✅ Support SQLite (dev) and PostgreSQL (prod) via DATABASE_URL env var
- ✅ Fixed duplicate source names (Nasdaq/Investing.com) in constants

**Database Schema:**
```
newsletters:
├── id, summary, language, articles (JSON)
├── audio_url, confidence_score
└── created_at, updated_at

source_stats:
├── id, newsletter_id (FK), category
├── source_name, status, article_count
└── confidence_score, created_at
```

**Files Created:**
- `backend/models/base.py` - Engine, session, connection pooling
- `backend/models/newsletter.py` - Newsletter model
- `backend/models/source_stat.py` - SourceStat model
- `backend/services/db_service.py` - High-level database operations
- `alembic/` - Migration infrastructure
- `tests/unit/test_db_service.py` - 11 unit tests

**Success Metrics:**
- ✅ 181/181 tests passing (100% test success rate)
- ✅ Source stats recorded for all 12 RSS feeds per analysis
- ✅ Foundation ready for analytics dashboard and confidence scoring

---

### Fix: Source Link Accuracy & Code Organization 🔗
**Completed:** November 30, 2025
**Status:** SHIPPED (v1.4.9)
**User Value:** Guaranteed correct source links and cleaner codebase

**Pain Point Solved:**
- ✅ Fixed AI hallucination causing wrong source links (AI was inventing news)
- ✅ News items now display original RSS titles with guaranteed correct links
- ✅ Language selector moved to Market Summary only (less confusing UX)
- ✅ Section titles always in English (US/Israeli/AI news categories)
- ✅ Code organization improved with separated constants and prompts

**Implementation Completed:**
- ✅ Created `backend/constants.py` - RSS feed URLs separated from business logic
- ✅ Created `backend/prompts.py` - AI prompts in English and Hebrew
- ✅ Simplified `backend/agents/market_agent.py` (42% code reduction)
- ✅ Frontend displays original RSS article titles (not AI-generated)
- ✅ Added 2-line CSS limit for consistent bullet display
- ✅ Updated PYTHON_BEST_PRACTICES.md with constants/prompts separation pattern
- ✅ Updated CLAUDE.md with link to CLAUDE_MD_GUIDELINES.md

**Files Modified:**
- `backend/constants.py` (NEW) - RSS feed URL constants
- `backend/prompts.py` (NEW) - AI agent prompts (EN/HE)
- `backend/agents/market_agent.py` - Simplified, imports from new files
- `frontend/templates/index.html` - Original titles, language selector moved
- `tests/unit/test_market_agent.py` - Updated for new prompt structure
- `PYTHON_BEST_PRACTICES.md` - Added constants/prompts separation section
- `CLAUDE.md` - Added CLAUDE_MD_GUIDELINES.md link

**Success Metrics:**
- ✅ 161/161 tests passing (100% test success rate)
- ✅ Source links now 100% accurate (guaranteed by using original RSS data)
- ✅ market_agent.py reduced from 510 lines to 296 lines (42% reduction)
- ✅ Cleaner code organization following PYTHON_BEST_PRACTICES.md

---

### Refactor: Python Best Practices Implementation 🔧
**Completed:** November 29, 2025
**Status:** SHIPPED (v1.4.1)
**User Value:** Improved code quality, maintainability, and reliability through enterprise-grade refactoring

**Pain Point Solved:**
- ✅ Inconsistent error handling with generic exceptions replaced by custom exception hierarchy
- ✅ Untyped code replaced with comprehensive type hints and dataclasses
- ✅ print() debugging replaced with structured logging (100+ instances)
- ✅ Configuration scattered across files centralized in AppConfig dataclass
- ✅ Fragile RSS feeds now have retry logic with exponential backoff
- ✅ Better test maintainability with all 161 tests passing

**Implementation Completed:**
- ✅ Created `backend/exceptions.py` with 7 custom exception classes (NewsletterError, FeedFetchError, TTSError, etc.)
- ✅ Refactored `backend/config.py` to use AppConfig dataclass with validation
- ✅ Added Article and SourceStats dataclasses for type-safe data models
- ✅ Implemented retry logic with tenacity (3 attempts, exponential backoff)
- ✅ Replaced 100+ print() statements with structured logging
- ✅ Added Pydantic validation for API inputs
- ✅ Created `/health` endpoint for production monitoring
- ✅ Updated all 161 tests to work with new architecture (100% pass rate)

**Technical Changes:**
```python
# New exception hierarchy
backend/exceptions.py - 7 custom exception classes

# Dataclass-based configuration
backend/config.py - AppConfig with from_env(), validate()

# Type-safe data models
@dataclass
class Article:
    text: str
    source: str
    timestamp: str
    title: str
    link: str

# Retry logic for RSS feeds
@retry(
    retry=retry_if_exception_type((Timeout, ConnectionError)),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3)
)
def fetch_rss_feed(...) -> List[Article]

# Pydantic API validation
class AnalyzeRequest(BaseModel):
    language: str = Field(default='en', pattern='^(en|he)$')
    force_refresh: bool = Field(default=False)
```

**Files Refactored:**
- `backend/exceptions.py` (NEW) - Custom exception hierarchy
- `backend/config.py` - AppConfig dataclass with validation
- `backend/agents/market_agent.py` - Dataclasses, retry logic, logging
- `backend/services/tts_service.py` - Logging, error handling, config integration
- `backend/crew_setup.py` - Type hints, ValidationError
- `backend/web_app.py` - Pydantic validation, /health endpoint, request IDs
- `backend/main.py` - Structured logging, exit codes
- All test files updated (161 tests, 100% pass rate)

**Documentation:**
- ✅ Created PYTHON_BEST_PRACTICES.md with refactoring guidelines
- ✅ Rewrote CLAUDE.md from 425 lines → 111 lines following CLAUDE_MD_GUIDELINES.md
- ✅ Updated README.md with refactoring announcement

**Success Metrics:**
- ✅ 161/161 tests passing (100% test success rate)
- ✅ 63% test coverage maintained
- ✅ 100+ print() → logging conversions
- ✅ 7 custom exception classes for precise error handling
- ✅ RSS feed retry logic reduces transient failures
- ✅ Type hints on all functions improve IDE support
- ✅ Health endpoint enables production monitoring

---

### Feature: Podcast Generation Optimization ⚡🎙️
**Completed:** November 29, 2025
**Status:** SHIPPED (v1.4.0)
**User Value:** Dramatically faster podcast generation (2+ minutes → 30-60 seconds) with no quality loss

**Pain Point Solved:**
- ✅ Podcast generation reduced from 2+ minutes to 30-60 seconds (60-70% faster)
- ✅ Sequential API calls replaced with parallel batch processing (10 concurrent)
- ✅ Real-time progress feedback with percentage and status messages
- ✅ Users can now cancel long-running generation
- ✅ Dramatically improved UX for core feature

**Implementation Completed:**
- ✅ Implemented parallel API calls using asyncio (10 lines concurrently per batch)
- ✅ Added real-time progress updates via Server-Sent Events (SSE)
- ✅ Created progress endpoint: `GET /api/podcast-progress/<task_id>`
- ✅ Added cancellation support: `POST /api/cancel-podcast/<task_id>`
- ✅ Optimized audio merging to handle concurrent chunks
- ✅ Background threading for non-blocking API responses

**UX Design Implemented:**
- ✅ Replaced spinner with animated progress bar (0-100%)
- ✅ Live status messages: "Generated 45/64 lines... (70%)"
- ✅ "Cancel Generation" button during podcast creation
- ✅ Smooth real-time progress updates (every 1 second via SSE)
- ✅ Updated loading message: "30-60 seconds ⚡" (was "5-10 minutes ☕")

**Technical Implementation:**
```python
# Async parallel audio generation with progress tracking
1. generate_podcast_async() method with task_id tracking
2. Split dialogue into batches of 10 lines
3. Use asyncio.gather() to generate batches concurrently
4. Track progress in active_tasks dict, emit SSE events
5. Support cancellation via cancelled_tasks set
6. Merge audio chunks and save with metadata
```

**Performance Achieved:**
- ✅ **60-70% faster generation** (from 120+ seconds to 30-60 seconds)
- ✅ Maintained tts-1-hd quality (no compromise on audio quality)
- ✅ Progress updates every 1 second via SSE
- ✅ Cancellation with proper cleanup of temp files
- ✅ Batch size of 10 concurrent requests optimized for OpenAI rate limits

**Files Modified:**
- `backend/services/tts_service.py` - Added generate_podcast_async() method, task tracking, AsyncOpenAI client
- `backend/web_app.py` - New SSE endpoint, cancel endpoint, background threading
- `frontend/templates/index.html` - Progress bar UI, SSE client, cancel button
- `tests/integration/test_podcast_api.py` - Updated tests for async API

**Success Metrics:**
- ✅ All 132 tests passing (100% test success rate)
- ✅ Generation time 30-60 seconds for typical newsletters (64 lines)
- ✅ Real-time progress reduces perceived wait time significantly
- ✅ Cancellation support prevents resource waste

---

### Feature: Source Monitoring UI 📡
**Completed:** November 29, 2025
**Status:** SHIPPED (v1.3.7)
**User Value:** Transparency into which RSS sources are providing data vs. failing/inactive

**Problem Solved:**
- Users couldn't see why AI category was empty during intraday updates
- No visibility into which sources were active/inactive
- Difficult to debug RSS feed issues
- No foundation for future source confidence scoring

**Implementation:**
- **Backend tracking:** Records article count and status for all RSS sources (active/inactive)
- **Visual component:** Collapsible "Sources" panel below each market category
- **Status indicators:** ✓ Green badges for active sources with article counts, ⊘ Gray badges for inactive
- **"No news" messaging:** Replaced empty sections with "No news in the last 12 hours"
- **API response:** Added `source_stats` object with per-category source health data

**Technical Details:**
- `backend/agents/market_agent.py`: Track source stats during RSS fetch
- `backend/web_app.py`: Include source_stats in API response and cache
- `frontend/templates/index.html`: Render collapsible source monitor component
- Starts collapsed to avoid UI clutter

**Impact:**
- Users can now see which of 8 US, 2 Israeli, and 2 AI sources provided articles
- Foundation for future confidence scoring system
- Improved trust through transparency
- Better debugging capability for feed issues

---

## Sprint Summary

**Versions Shipped:** v1.3.7, v1.4.0, v1.4.1, v1.4.9, v1.6.0, v1.9.0, v1.12.0, v1.13.0, v1.16.1, v1.18.0, v1.19.0, v1.20.0, v1.23.0, v1.23.1, v1.23.2
**Features Completed:** 11 (8 features, 1 fix, 2 refactors)
**Test Coverage:** 54% (220+ tests, 100% pass rate)
**Key Achievements:**
- User authentication system (signup/login with bcrypt)
- Category filtering with smart subset caching
- Category-aware podcast caching with superset reuse
- Flask → FastAPI migration (native async, auto API docs)
- 60-70% faster podcast generation
- Database foundation for analytics
- Crypto market coverage added
- Enterprise-grade code quality
- Professional UI with design system
- Marketing content and "How it works" feature cards

---

**Sprint Start:** November 28, 2025
**Sprint End:** December 11, 2025
