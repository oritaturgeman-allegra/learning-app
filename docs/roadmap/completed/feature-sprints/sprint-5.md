# Sprint 5: Jan 23 - Feb 5, 2026

## Sprint Goal
**Production Readiness** - Prepare the application for public launch with authentication, legal compliance, analytics, and infrastructure hardening.

## Sprint Theme
Launch Preparation - Everything needed to go live safely and legally.

---

## Completed Features

### 1. Google OAuth Sign-Up (v1.33.0)
**Completed:** January 26, 2026

Users can now sign in with their Google account instead of creating a password.

**What was built:**
- `/api/auth/google` - Redirects to Google consent screen
- `/api/auth/google/callback` - Handles OAuth callback, creates/links user
- Name verification popup - Users confirm/update their name after Google sign-in
- `/api/auth/update-name` - API to update user name

**Edge cases handled:**
- New user via Google (signup mode) → Create account with google_id
- Existing user via Google (signup mode) → Show "Email already registered" error
- Existing email with password (login mode) → Show "Use password" error (no silent linking)
- Returning Google user (login mode) → Login and update last_login
- Non-existent user (login mode) → Show "Sign up first" error
- Missing name from Google → Prompt user to enter name

**Tests:** 18 tests (11 unit, 7 integration)

---

### 2. Email Verification System (v1.34.0)
**Completed:** January 26, 2026

Users must verify their email address before logging in.

**What was built:**
- SendGrid integration for email delivery
- Verification email with branded HTML template
- `/api/auth/verify-email/<token>` - Verify email with token
- `/api/auth/resend-verification` - Resend verification email
- Block login for unverified users (403 error)
- Token expiration (24 hours)
- "Check Your Email" message after signup

**Database changes:**
- Added `email_verified` boolean column
- Added `verification_token` column
- Added `verification_token_expires_at` column

**Tests:** 13 integration tests, 7 unit tests

---

### 3. Auth UX Improvements (v1.34.1 - v1.34.3)
**Completed:** January 27, 2026

Clearer error messages that tell users exactly how their account was registered.

- v1.34.1: Show error instead of silent account linking
- v1.34.2: Signup rejects existing users
- v1.34.3: Context-aware error messages (Google vs password accounts) + error page styling

---

### 4. Privacy Policy & Terms of Use (v1.35.0)
**Completed:** January 27, 2026

Legal pages required for production launch.

- `/privacy` - Privacy Policy with 9 sections (data collection, usage, GDPR/CCPA rights, cookies)
- `/terms` - Terms of Use with 12 sections + financial disclaimer
- Footer links open in new tabs
- Responsive design following design system

---

### 5. Cookie Consent Banner (v1.36.0)
**Completed:** January 27, 2026

GDPR-compliant cookie consent banner for EU users and global best practices.

**What was built:**
- Cookie consent banner component with slide-up animation
- Three options: Accept All, Reject Non-Essential, Customize
- Customize view with toggles for Analytics and Preferences categories
- Consent stored in localStorage with 12-month expiry
- `hasConsent(category)` function for gating analytics
- "Manage Cookies" link in footer to reopen settings
- Link to Privacy Policy cookie section from banner

**Cookie categories:**
- Essential (always on): session, auth
- Analytics (optional): usage tracking
- Preferences (optional): language, theme

---

### 6. Scheduled Content Generation (v1.37.0 - v1.40.4)
**Completed:** February 1, 2026

Pre-generate newsletter content 4x daily (11:00, 14:00, 18:00, 20:00 UTC).
Reduces API costs from ~$1,500/month (1000 users) to ~$20/month fixed.

**What was built:**
- APScheduler with BackgroundScheduler for 4x daily content generation
- Content job: RSS fetch → AI analysis → save to DB
- `/api/analyze` serves pre-generated content instantly
- `/api/admin/refresh` for on-demand refresh (API key protected, rate limited)
- v1.40.3: Fixed race condition where `/api/podcast/latest` could return URL for expired audio
- v1.40.4: Increased audio cache TTL to 24h (was 1h, expired between scheduler runs)

**Tests:** 47 tests (unit + integration)

---

### 7. Security Headers & CORS (v1.41.0 - v1.42.0)
**Completed:** February 1, 2026

Production security hardening with HTTP security headers and CORS support.

**v1.41.0 - Security Headers:**
- `SecurityHeadersMiddleware` with all security headers
- X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- Content-Security-Policy (allows Google OAuth/Fonts)
- Referrer-Policy, Permissions-Policy
- HSTS when `FORCE_HTTPS=true`
- HTTPS redirect middleware for production

**v1.42.0 - CORS Support:**
- `CORSMiddleware` for future external clients/mobile apps
- Config: `CORS_ENABLED`, `CORS_ORIGINS`, `CORS_ALLOW_CREDENTIALS`
- Disabled by default (same-origin app doesn't need it)

**Tests:** 19 tests (13 security headers, 6 CORS)

---

### 8. Financial Disclaimer (v1.43.0)
**Completed:** February 1, 2026

Legal disclaimer on homepage and newsletter page to protect against investment liability.

- Reusable `_disclaimer.html` partial with info icon
- Displayed on homepage and newsletter page
- Links to Terms of Use (opens in new tab)

---

### 9. Accessibility Foundation (v1.44.0 - v1.44.6)
**Completed:** February 2, 2026

WCAG 2.1 AA compliance with 7 implementation phases:

- **Phase 1:** Focus states, reduced motion, high contrast support
- **Phase 2:** Skip link, semantic HTML landmarks
- **Phase 3:** ARIA labels on buttons, tabs, controls
- **Phase 4:** Modal focus trap, dialog ARIA attributes
- **Phase 5:** Keyboard navigation (carousel, sentiment tabs, podcast)
- **Phase 6:** Form accessibility (aria-required, aria-invalid, error linking)
- **Phase 7:** Live regions for dynamic content announcements

---

### 10. Rate Limiting (v1.45.0)
**Completed:** February 2, 2026

In-memory rate limiting for auth endpoints to prevent brute force attacks.

**Endpoints protected:**
- `/api/auth/login`: 5 attempts per 15 minutes per IP
- `/api/auth/signup`: 3 attempts per hour per IP
- `/api/auth/resend-verification`: 3 attempts per hour per IP

**Features:** Returns 429 with Retry-After header, per-IP tracking, configurable via env vars.

**Tests:** 24 tests (18 unit, 6 integration)

---

### 11. Leave Feedback (v1.46.0 - v1.46.1)
**Completed:** February 3, 2026

"Leave Feedback" button in header with modal for submitting feedback via email.

- Feedback button on both landing page and newsletter page (color: #7a9ab8)
- Modal with textarea, file upload (images/videos), and send button
- Server-side file validation (10MB images, 50MB videos, 5 files max)
- SendGrid email delivery to project inbox with base64-encoded attachments
- v1.46.1: Emails include logged-in user's name and email (falls back to generic for anonymous)
- Shared `modals.js` for DRY cross-page modal functions

**Tests:** 16 tests

---

### 12. On-Demand Podcast with Category Filtering (v1.47.0)
**Completed:** February 3, 2026

Changed podcast from pre-generated (all categories) to on-demand per user with category filtering and combination caching.

**What was built:**
- `POST /api/podcast/generate` - Generate podcast for user-selected categories
- Combination-based caching (max 15 combos) - second user with same combo gets cached version instantly
- Daily generation limit (1 per user per UTC day, cache hits don't count)
- Dynamic dialog length scaling - fewer categories = shorter podcast (2 cats → 3-4 min, 4 cats → 5-6 min)
- Generate Podcast button in sidebar, replaces auto-loading player
- `podcast_dialog` returned in API response for transcript display
- `podcast_generations` DB table for tracking and rate limiting
- Deprecated `GET /api/podcast/latest` (returns 410 Gone)
- Removed podcast generation from scheduled content job

**Database changes:**
- Added `podcast_generations` table (user_id, categories, cache_key, created_at)

**Tests:** 25 tests (unit + integration)

---

### 13. Scheduler Misfire Grace Time (v1.47.1)
**Completed:** February 3, 2026

Added `misfire_grace_time` (15 min) to scheduler jobs so delayed jobs still execute instead of being silently skipped.

---

### 14. Error Monitoring & Logging (v1.48.0)
**Completed:** February 3, 2026

Sentry error monitoring with global exception handlers, structured logging, and sensitive data scrubbing.

**What was built:**
- Sentry SDK integration with FastAPI (`sentry-sdk[fastapi]`)
- `backend/sentry_config.py` - Initialization with `before_send` hook for data scrubbing
- Global exception handlers for `NewsletterError` and unhandled `Exception`
- Request context middleware - attaches request ID and endpoint tags to Sentry events
- `X-Request-ID` response header for log-to-Sentry correlation
- Switched from `logging.basicConfig` to `setup_logging()` (structured logging with JSON output option)
- Sensitive data scrubbing: passwords, tokens, API keys, cookies never sent to Sentry
- Sentry alerts configured in dashboard for critical errors
- Config fields: `SENTRY_DSN`, `SENTRY_ENVIRONMENT`, `SENTRY_TRACES_SAMPLE_RATE`, `LOG_FORMAT`, `LOG_LEVEL`

**Tests:** 16 unit tests

---

### 15. Scheduler Job Execution Fix (v1.48.1)
**Completed:** February 5, 2026

Fixed scheduled jobs only firing once then stopping. Replaced deprecated `asyncio.new_event_loop()` + `set_event_loop()` pattern with `asyncio.run()` for reliable event loop handling across APScheduler thread pool reuse in Python 3.13.

**What was fixed:**
- `generate_content_job.py` - Replaced deprecated asyncio event loop pattern with `asyncio.run()`
- `scheduler_service.py` - Added APScheduler event listeners (`EVENT_JOB_EXECUTED`, `EVENT_JOB_ERROR`, `EVENT_JOB_MISSED`) for diagnostics
- `test_scheduler_service.py` - Fixed hardcoded job count assertions to use config dynamically

---

### 16. Podcast Dialog Quality Improvements (v1.48.2)
**Completed:** February 5, 2026

Improved podcast dialog prompt for better category coverage, clearer transitions, and more engaging conversation.

- Intro now names all selected categories explicitly
- Clear transition announcements between category sections
- Reduced repetitive filler words, added varied reactions and occasional disagreement between hosts

---

### 17. AsyncIOScheduler for ASGI Compatibility (v1.48.3)
**Completed:** February 5, 2026

Switched from BackgroundScheduler to AsyncIOScheduler to fix scheduler jobs not triggering in uvicorn/ASGI environment. BackgroundScheduler's thread wasn't waking up at scheduled times.

---

### 18. Filter KeyboardInterrupt from Sentry (v1.48.4)
**Completed:** February 5, 2026

Filter out `KeyboardInterrupt` exceptions from Sentry error reporting. Server shutdown via Ctrl+C is expected behavior, not an error.

---

### 19. Sentiment Tracker Rolling 7-Day Window (v1.48.5)
**Completed:** February 5, 2026

Fixed Sentiment Tracker chart to show a rolling 7-day window where today is always the rightmost point.

**Before:** Static Mon-Sun labels regardless of current day
**After:** Dynamic labels showing last 7 days (e.g., if today is Thu: Fri, Sat, Sun, Mon, Tue, Wed, Thu)

---

### 20. Improved Article Deduplication (v1.48.6)
**Completed:** February 5, 2026

Enhanced deduplication to catch more duplicate articles from different sources covering the same story.

**Improvements:**
- Dedup prompt now includes `source` and `original_title` (not just truncated text)
- Updated LLM prompt to explicitly identify cross-source duplicates
- Better detection of Hebrew articles covering same event

---

## Sprint Summary

**Versions Shipped:** v1.33.0 - v1.48.6
**Features Completed:** 20 features (Google OAuth, Email Verification, Auth UX, Legal Pages, Cookie Consent, Scheduled Content Generation, Security Headers & CORS, Financial Disclaimer, Accessibility Foundation, Rate Limiting, Leave Feedback, On-Demand Podcast, Scheduler Misfire Fix, Error Monitoring & Logging, Scheduler Job Execution Fix, Podcast Dialog Quality, AsyncIOScheduler Fix, Sentry KeyboardInterrupt Filter, Sentiment Tracker Rolling Window, Improved Deduplication)

---

**Sprint Start:** January 23, 2026
**Sprint End:** February 5, 2026
