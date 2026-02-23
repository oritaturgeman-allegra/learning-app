# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
Ship **v1.0.0 → v3.0.3** — Build a complete gamified English + Math learning app with 8 mini-games, persistent progress tracking, and a polished kid-friendly React SPA.

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

### 29. Chapter C: Long Division + Hint System (v2.11.0)
Chapter C unlocked — long division with remainder (dual-input UI), clean division, and reverse verification problems.
- Hint system (💡) with per-problem solving clues across all 4 games
- Quick Solve shows quotient + remainder inputs for division-with-remainder
- Missing Number adapts for `division_verify` and `divide_remainder` categories

---

### 30. DB-Derived Session Checkmarks (v2.11.1)
Session completion checkmarks now derived from database via `/api/game/progress` instead of localStorage.
- Added `completed_sessions` field to progress API response
- Removed `markSessionCompleted` localStorage approach from both templates
- 4 new unit tests for completed_sessions logic

---

### 31. Game Card Completion Badge Polish (v2.11.2)
Changed game card completion indicator from green ✓ circle to ⭐ star — avoids visual conflict with session completion checkmark.
- Math True/False emoji changed from ✅ to 🤔 for consistency with English

---

### 32. Chapter D: Primes & Divisibility (v2.12.0)
Chapter D unlocked — divisibility rules (3, 6, 9), prime vs composite identification, and prime factorization across all 4 math games.
- 3 new problem categories with Hebrew hints explaining solving strategies
- True/False game shows "מספר ראשוני / מספר פריק" for prime identification
- Prime factorization uses curated numbers (12–100) with find-the-missing-factor format

---

### 33. Smart Hints Rewrite — Natural Hebrew (v2.12.1)
Rewrote all math hints across 4 chapters in natural, kid-friendly Hebrew and centralized them in a `MATH_HINTS` const object.
- Hints use warm teacher language (נסי ככה, הטריק, זכרי, שימי לב) instead of robotic phrasing
- Feminine singular address throughout (תחשבי, תוסיפי, תורידי)
- Hints teach method, not intermediate results
- All 20+ hint strings in one organized object for easy editing

### 34. Modular CSS/JS Extraction (v2.13.0)
Extracted all CSS and JS from monolithic HTML templates into modular static files. Templates reduced from 6,618 lines to 532 lines (92% reduction).
- 3 CSS files: `shared.css`, `english.css`, `math.css`
- 5 JS files: `shared.js`, `english-data.js`, `english-game.js`, `math-data.js`, `math-game.js`
- Templates now contain only HTML markup, inline Jinja2 vars, and state init
- Load order: inline Jinja2 vars → shared.js → data.js → game.js

### 35. Custom SVG Subject Icons (v2.13.1)
Replaced emoji icons (🔢, 🇺🇸, 🔤) with custom SVG icons for a more polished look across both subjects.
- `input-numbers-light.svg` — blue gradient card with 1-2-3-4 grid (replaces 🔢 for math)
- `input-letters-light.svg` — orange gradient card with A-B-C-D grid (replaces 🇺🇸 for English)
- `.math-icon` and `.english-icon` CSS classes auto-scale with parent font-size
- Applied to subject tabs, subject cards, session picker titles, game cards, and math-primes session card

---

### 36. Math Game Correct Answer Fix (v2.13.2)
Fixed math games freezing on correct answers — `updateStarDisplay()` crashed on null elements missing from math template.
- Added null checks to `updateStarDisplay()` matching existing `updateTrophyCount()` pattern
- Also fixed star counter not loading on math pages (same root cause)

---

### 37. Word Tracker Session Scoping + Env Cleanup (v2.13.3)
Word tracker now scoped to session — math equations no longer inflate English word count. Cleaned up `.env` to remove newsletter project's Supabase config.
- Added `session_slug` query param to `GET /api/game/practiced-words` endpoint
- Frontend passes `SESSION_SLUG` when fetching practiced words
- Removed newsletter Supabase `DATABASE_URL`, API keys, and OAuth config from `.env`
- Replaced `.env.example` with learning-app-specific template

---

### 38. React Frontend Scaffolding (v2.14.0)
React + MUI + TypeScript project initialized alongside legacy frontend for mobile-responsive redesign.
- Vite build toolchain with dev proxy to FastAPI
- MUI theme with all design tokens migrated from shared.css
- RTL support via stylis-plugin-rtl + Emotion cache
- React Router with 4 routes matching existing URL structure
- Placeholder pages — real components in upcoming phases

---

### 39. Backend Serves React SPA (v2.14.1)
FastAPI now serves the React build at `/app/` and provides a config API for the React SPA.
- New `/api/game/config` endpoint returns version, changelog, reward tiers, sessions
- React build served from `frontend/dist/` with SPA catch-all at `/app/{path}`
- Vite uses `/app/` base path for production builds, `/` for dev
- Legacy Jinja2 frontend continues to work alongside React

---

### 40. React Navigation Screens (v2.15.0)
All 4 navigation screens ported to React with MUI components, responsive layout, and live API data.
- API client (`api/game.ts`) with TypeScript types for all endpoints
- AppContext provider for progress + config state (stars, rewards, sessions)
- Layout component with sticky header (star counter, trophy gallery, home button)
- Welcome page with animated gradient background
- SubjectPicker with SVG icon cards for English/Math
- SessionPicker with subject tabs, session cards, per-session star counts
- GameMenu with colored game cards (games placeholder until Phases 5-6)
- CSS keyframe animations ported from legacy shared.css
- RewardCollection dialog with earned/locked reward cards + progress bar

---

### 41. Audio & Reward Systems for React (v2.16.0)
Audio feedback, confetti, milestone celebrations, and reward unlock popups ported to React.
- `useAudio.ts` — AudioContext tones (correct chime, wrong buzz, celebration melody) + Web Speech API TTS
- `Confetti.tsx` — 30-piece confetti overlay with random colors/shapes/delays
- `MilestoneOverlay.tsx` — celebration every 5 stars, emoji parade every 10 stars
- `RewardPopup.tsx` — reward tier unlock popup with rewardReveal animation
- `useRewards.ts` — orchestrates milestone → reward flow with correct timing
- `AppContext` updated with `awardStars()` for optimistic star updates
- Layout renders all celebration overlays

---

### 42. RTL Emoji Fix + Version Footer + Unified Gradient (v2.16.1)
Fixed RTL emoji placement across all React pages and added version footer.
- All emojis moved to end of source strings (render on left in RTL per user preference)
- Version footer in lavender strip at bottom using flex column layout
- Animated gradient background moved from individual pages to Layout for consistency
- Removed per-page `minHeight: calc(100vh - 72px)` — Layout handles viewport fill

---

### 43. React English Games — Phase 5 Complete (v2.17.0)
Ported all 4 English mini-games from vanilla JS to React + TypeScript + MUI.
- **Data module** (`data/english.ts`): 55 typed vocabulary words, 20 scramble sentences, 22 T/F sentences, greedy set-cover session planner
- **Game engine hook** (`useGameEngine.ts`): Shared round/scoring/delay logic for all games
- **4 game components**: WordMatch, SentenceScramble, ListenAndChoose, TrueFalse
- **GameScreen**: Route wrapper managing session plan, practiced words, API save
- **CompletionScreen**: Score summary with celebration audio and replay/back buttons
- **WordTracker**: Fixed sidebar (desktop) / drawer (mobile) with 55 word chips
- **GameMenu**: Cards navigate to games, show completion checkmarks
- **Layout**: Milestone watcher auto-triggers celebrations when stars increase
- Architecture docs updated

---

### 44. React Math Games + Topic Navigation — Phase 6 Complete (v2.18.0)
Ported all 4 math mini-games from vanilla JS to React + TypeScript + MUI, with topic-based navigation for multi-chapter math.
- **Data module** (`data/math.ts`): Algorithmic problem generators for all 4 chapters (tens/hundreds, two-digit multiply, long division, primes & divisibility)
- **4 game components**: QuickSolve, MissingNumber, MathTrueFalse, BubblePop — with Israeli notation (× and :)
- **MathGameScreen**: Route wrapper managing problem generation, scoring, API save
- **HintButton**: Shared lightbulb popover with per-problem Hebrew hints, auto-close after 4s
- **Topic navigation**: TopicSessions page for multi-chapter subjects, `TOPICS_BY_SUBJECT` config
- **GameMenu**: Session-aware, loads correct game data per session slug
- **Games registry** (`data/games.ts`): Centralized game metadata with subject-specific game lists

---

### 45. Cleanup & Polish — Phase 7 / v3.0.0 (v3.0.0)
Final React migration step: deleted legacy Jinja2/vanilla JS frontend, promoted React SPA from `/app/` to root `/`, added code splitting, polished touch targets. ~5,000 lines of dead code removed.
- **Legacy deletion**: Removed 11 files — 2 Jinja2 templates, 3 CSS, 5 JS, 1 unused SVG
- **React at root**: SPA served from `/` instead of `/app/`, catch-all route for client-side routing
- **Backward compat**: `/app/{path}` → `/{path}` 301 redirect for old bookmarks
- **Code splitting**: `React.lazy()` + Suspense for all 8 game components + CompletionScreen (separate chunks)
- **Static assets**: Migrated favicon + SVG icons to Vite `public/` directory
- **Touch polish**: All game buttons meet 48px min-height, HintButton bumped to 48×48
- **Dependency cleanup**: Removed Jinja2 from requirements.txt
- **Vite simplification**: Base path always `/`, removed conditional build config
- **Tests updated**: Page route tests rewritten for React SPA behavior (71 tests passing)

---

### 46. Session Card Lavender Tint (v3.0.1)
Lavender background on session cards in TopicSessions to visually distinguish them from white topic cards in SessionPicker.
- `backgroundColor: "#ede9fe"` on Card and CardActionArea in TopicSessions.tsx
- Topic card in SessionPicker stays white — clear navigation hierarchy

---

### 47. Navigation Polish — Session Names, Back Button, Title (v3.0.2)
UI consistency pass across game screens and session navigation.
- GameMenu: Session slug replaced with Hebrew name (math) or English name (English) subtitle
- GameScreen + MathGameScreen: Back button header constrained to `maxWidth: 500` + centered — matches TopicSessions layout
- TopicSessions: Title changed from "בחרי שיעור" to "בחרי נושא" for clearer hierarchy

---

### 48. Reset Button — Fresh Word Rounds (v3.0.3)
Restored the 🔄 reset button (lost during React migration) so the child can start a fresh round with new words.
- 🔄 IconButton next to title in GameMenu (English sessions only — math is algorithmic)
- Hebrew confirmation dialog: "להתחיל סבב חדש?" with "⭐ הכוכבים נשארים, המילים מתחלפות"
- On confirm: calls `POST /api/game/reset`, clears sessionStorage plan + completed games cache
- Next game entry regenerates `planSession()` with freshly shuffled words/sentences
- Stars always preserved — only word tracking and completion state reset
- Spin animation on button for visual feedback

---

## Sprint Summary

**Versions Shipped:** v1.0.0 → v3.0.3 (48 releases)
**Features Completed:** 48 (28 features, 8 UX polish, 1 content expansion, 3 chores, 8 bug fixes)
**Test Coverage:** 71 tests, 83% coverage, 100% pass rate
**Key Achievements:**
- Full React + TypeScript + MUI rewrite — single modern SPA
- 8 complete mini-games (4 English, 4 Math) with star rewards and sound feedback
- 55 vocabulary words from Jet 2 Unit 2 — full coverage guaranteed per session
- 4 math chapters covering 4th-grade Israeli curriculum (tens/hundreds through primes)
- Persistent progress tracking in SQLite with per-session stars
- Code-split game components for faster initial load
- Collectible reward cards with trophy gallery (6 tiers, 25–300 stars)
- Topic-based navigation for multi-chapter subjects
- Kid-friendly pastel UI with Hebrew RTL support
- American English female voice for pronunciation

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
