# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
Ship **v1.0.0 → v2.5.0** — Build a complete gamified English learning app with 4 mini-games, persistent progress tracking, and a polished kid-friendly UI.

## Sprint Theme
Foundation & Polish — Core game engine, vocabulary content, star rewards, word tracker, and visual delight for a Gen Alpha learner.

---

## Completed Features

### 1. Initial Release (v1.0.0)
Core app with 4 English learning mini-games: Word Match, Sentence Scramble, Listen & Choose, True or False.
- Vanilla JS game engine with star rewards
- Hebrew UI (RTL) with English content (LTR)
- Web Speech API text-to-speech for pronunciation

---

### 2. Backend + DB Integration (v1.1.0)
FastAPI backend with SQLAlchemy models for persistent game results and progress tracking.
- SQLite database with GameResult model
- POST `/api/game/result` — save scores and per-word accuracy
- GET `/api/game/progress` — stars, accuracy by game, weak words

---

### 3. Clean Codebase (v1.2.0)
Stripped all newsletter project code, established clean learning app foundation.

---

### 4. UI Polish + Voice (v1.3.0)
Kid-friendly visual design with pink bows background, pastel gradient cards, and American English female TTS voice.
- Pink bow favicon
- RTL layout fixes
- Polished menu screen

---

### 5. Full Vocabulary + Shuffle (v1.4.1)
Expanded from sample words to all 55 Jet 2 Unit 2 vocabulary words across 11 categories.
- Shuffle button for word order variety
- Semantic card classes for each game type

---

### 6. Session Celebration (v1.4.2)
Fireworks + trophy popup after completing all 4 games in a session.
- Confetti and celebration melody
- Session tracking with visual progress

---

### 7. Subject Tabs (v1.5.0)
Sidebar navigation ready for multi-subject support (English now, Math future).
- Gray out completed game cards during session
- Menu spacing adjustments

---

### 8. Checkmark Badges (v1.5.1)
Green checkmark badge on completed game cards with pop animation.
- Hebrew translations on answer buttons
- Speaker emoji fix for TTS

---

### 9. Word Tracker Sidebar (v1.6.0)
Fixed panel showing all 55 vocabulary words, aligned with game cards.
- Dynamic JS positioning to match card grid
- Pastel gradient background
- Responsive word count display

---

### 10. Word Chips (v1.6.1)
Transformed plain text words into colorful pill-shaped chips with two visual states.
- Flex-wrap centered layout
- Practiced/unpracticed chip states

---

### 11. DB Persistence for Practiced Words (v1.6.2)
Practiced words derived from existing game_results table — no new table needed.
- GET `/api/game/practiced-words` endpoint
- Words persist across page refresh
- 3 new unit tests (14 total passing)

---

### 12. Word Chip Makeover (v1.6.3)
Purple/lavender unpracticed chips, muted sage green practiced state with bounce animation and strikethrough.
- Session checkmarks persist across page refresh (localStorage)
- `chipDone` keyframe animation with cubic-bezier easing

---

### 13. Reset Button — Fresh Practice Round (v1.7.0)
Reset button replaces shuffle — start a new practice round while keeping lifetime stars and game history.
- New `app_state` table with `reset_at` timestamp for filtering practiced words
- `POST /api/game/reset` endpoint
- Confirmation dialog in Hebrew before reset
- 7 new tests (5 unit + 2 integration, 36 total)

---

### 14. Full Vocabulary Coverage (v1.8.0)
Session Word Planner guarantees all 55 words are practiced when all 4 games are completed.
- Greedy set-cover algorithm allocates words across games on session start
- 12 new sentences added (6 scramble + 6 T/F) covering 17 previously orphaned words
- Games 1 & 3 have flexible round counts to absorb remaining uncovered words
- `freshShuffle()` removed — replaced by `planSession()`, `buildCoverageMap()`, `validateSessionPlan()`

---

### 15. Collectible Reward Cards (v1.9.0)
Star milestone rewards — 6 collectible cards unlocked at 25, 50, 100, 150, 200, 300 stars with Gen Alpha-themed names.
- Trophy button in header opens collection gallery (earned = vibrant, locked = grey silhouettes)
- Reward popup with bounce animation on unlock, auto-dismiss after 5s
- Progress bar showing distance to next reward
- Backend `earned_rewards` + `next_reward` in progress API (derived from total_stars, no new DB table)
- 5 new unit tests (59 total passing, 81% coverage)

---

### 16. Reward Card Animation Fix (v1.9.1)
Replaced broken 3D card flip with reliable bounce-reveal animation.
- Card shows reward name, emoji, and description immediately
- Auto-dismiss after 5 seconds so it doesn't block gameplay
- Click overlay background to dismiss early

---

### 17. Word Tracker Coverage Fix (v2.0.0)
Games 2 & 4 now save individual vocabulary words (not sentences) to the backend, so the word tracker correctly persists all practiced words across page refresh.
- `checkGame2Answer()` and `checkGame4Answer()` extract vocab via `getWordsInSentence()`
- Session popup "close" button no longer triggers a reset — just returns to menu

---

### 18. URL Routing — Refresh-Safe Game Menu (v2.1.0)
Dedicated `/learning` route so the game menu persists on page refresh instead of resetting to the landing page.
- Backend: new `GET /learning` route serving same template with `initial_screen="menu"`
- Frontend: Jinja2 conditional `active` class + `history.pushState` URL sync
- Browser back/forward button support via `popstate` handler

---

### 19. Session Picker Screen (v2.2.0)
New intermediate screen at `/learning` showing session cards — pick a unit and jump straight to the games at `/learning/{slug}`.
- Session picker with animated pastel gradient background and RTL session cards
- Unified header (stars + trophy) across session picker and games menu
- `/learning/{session_slug}` route with slug validation (404 for invalid)
- Client-side navigation via `pushState` + `popstate` for 3 URL states
- 4 new integration tests for page routes

---

### 20. Subject-Based URL Routing (v2.3.0)
Multi-subject URL structure — `/learning/english/jet2-unit2` replaces `/learning/jet2-unit2`, preparing for math support.
- New route `/learning/{subject}/{session_slug}` with subject validation
- `VALID_SUBJECTS` allow-list in defaults.py
- 301 redirect from old URLs for backward compatibility
- Frontend JS updated: `SUBJECT` constant, `selectSession`, `goToMenu`, `popstate`

---

### 21. Subject Picker Screen (v2.4.0)
New subject picker at `/learning` — choose English or Math before picking a unit. Stepped navigation flow: subject → sessions → game menu.
- New `subject-picker-screen` with large subject cards (English clickable, Math locked with shake)
- `/learning` now serves subject picker, `/learning/{subject}` serves session picker
- Back arrow on session picker to return to subject picker
- Updated popstate handler for 4-level URL navigation

---

### 22. Math Subject + Subject Tabs Everywhere (v2.5.0)
Math is now a real subject with its own session picker at `/learning/math`. Subject tabs on session picker and game menu for quick switching.
- `SESSIONS_BY_SUBJECT` dict in defaults.py — sessions keyed by subject
- Math session "כפל וחילוק" with locked card (coming soon)
- Subject tabs on session-picker-screen and menu-screen for quick navigation
- `switchSubject()` now navigates to `/learning/{subject}` from any screen

---

### 23. Per-Session Star Tracking (v2.6.0)
Each session card now shows its own star count — stars earned in English stay on English, math stays at zero until math games arrive.
- `session_slug` column added to GameResult model
- `stars_by_session` dict in progress API response
- Frontend sends `session_slug` with every game result save
- Session picker cards display per-session stars (not global total)

---

### 24. Math Session Cards (v2.7.0)
4 chapter-based math session cards replacing the single locked "כפל וחילוק" card, matching Ariel's 4th-grade textbook syllabus.
- Tens & Hundreds (unlocked), Two-Digit Multiply, Long Division, Primes & Divisibility (locked)
- Each chapter maps to textbook פרקים א׳–ד׳
- 2 new integration tests (29 total)

---

### 25. Math Game Engine (v2.8.0)
Separate math-fun.html template with 4 playable math games and algorithmic Chapter A problem generator.
- Quick Solve, Missing Number, True or False, Bubble Pop — all with Israeli notation (× and :)
- Problem categories: multiply tens/hundreds, divide, properties of 0/1, order of operations
- Distractor generator for near-miss wrong answers
- Floating bubble CSS animations, session celebration, reward system
- 4 new math game types registered in backend (72 tests total)

---

### 26. Math Difficulty Tuning + Layout Shift Fix (v2.8.1)
Tuned math problem difficulty to kid-friendly ranges and fixed game card jump on page refresh.
- Capped multiply bases at 10–90, removed ×1000, quotients ≤ 50
- Bubble Pop targets capped at 100, expressions use small factors
- Properties of 0/1 uses curated numbers (5–100) instead of random up to 999
- Removed slideUp entrance animation on page refresh (both templates)

---

### 27. Home Button Navigation (v2.9.0)
Home button (🏠) in the sticky header on session picker and game menu screens — navigates back to `/learning` (subject picker).
- Appears on both English and Math templates
- Pill-shaped button matching existing header style
- Not shown on subject picker (already there) or during gameplay (prevents accidental navigation)

---

### 28. Chapter B: Two-Digit Multiply (v2.10.0)
Session-aware problem generator — Chapter B unlocked with 2-digit × 1-digit, 2-digit × 2-digit, and powers (n²).
- `generateProblem()` picks categories based on `SESSION_SLUG`
- Bubble Pop targets and expression generators adapted for Chapter B ranges
- All 4 math games work with Chapter B content

---

## Sprint Summary

**Versions Shipped:** v1.0.0 → v2.10.0 (28 releases)
**Features Completed:** 28 (20 features, 3 UX polish, 1 content expansion, 1 chore, 3 bug fixes)
**Test Coverage:** 72 tests, 82% coverage, 100% pass rate
**Key Achievements:**
- 4 complete mini-games with star rewards and sound feedback
- 55 vocabulary words from Jet 2 Unit 2 — full coverage guaranteed per session
- Persistent progress tracking in SQLite
- Word tracker sidebar with practiced/unpracticed chip states
- Session celebration with fireworks after all 4 games
- Collectible reward cards with trophy gallery
- Session picker for multi-unit support
- Kid-friendly pastel UI with Hebrew RTL support
- American English female voice for pronunciation

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
