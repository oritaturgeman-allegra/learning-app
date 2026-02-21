# Sprint 1: Feb 20 - Mar 5, 2026

## Sprint Goal
Ship **v1.0.0 → v1.6.3** — Build a complete gamified English learning app with 4 mini-games, persistent progress tracking, and a polished kid-friendly UI.

## Sprint Theme
Foundation & Polish — Core game engine, vocabulary content, star rewards, word tracker, and visual delight for a 9-year-old learner.

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

## Sprint Summary

**Versions Shipped:** v1.0.0 → v1.9.1 (16 releases)
**Features Completed:** 16 (10 features, 3 UX polish, 1 content expansion, 1 chore, 1 bug fix)
**Test Coverage:** 59 tests, 81% coverage, 100% pass rate
**Key Achievements:**
- 4 complete mini-games with star rewards and sound feedback
- 55 vocabulary words from Jet 2 Unit 2 — full coverage guaranteed per session
- Persistent progress tracking in SQLite
- Word tracker sidebar with practiced/unpracticed chip states
- Session celebration with fireworks after all 4 games
- Collectible reward cards with trophy gallery
- Kid-friendly pastel UI with Hebrew RTL support
- American English female voice for pronunciation

---

**Sprint Start:** February 20, 2026
**Sprint End:** March 5, 2026
**Next Sprint Planning:** March 6, 2026
