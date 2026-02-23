# Architecture Overview

Quick reference for Ariel Learning App. For details, see [deep-dive.md](./deep-dive.md).

---

## What This App Does

Gamified English + Math learning for a 9.5-year-old Israeli girl. Teaches vocabulary from the Jet 2 textbook through 4 English mini-games, and 4th-grade math through 4 math mini-games — with star rewards, animations, and audio feedback.

---

## Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy |
| **Frontend** | React 19 + TypeScript + MUI 7 + Vite, SPA with RTL support |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Audio** | Web Speech API (TTS), AudioContext (sound effects) |
| **Fonts** | Google Fonts (Fredoka display, Rubik body/Hebrew) |
| **Languages** | Hebrew UI (RTL) + English/Math content (LTR) |
| **Testing** | pytest, pytest-cov, pytest-mock |

---

## Data Flow

```
App Start:
  GET /                                              → React SPA (Welcome screen)
  All navigation handled client-side by React Router
         ↓
  AppContext loads config + progress from API on mount
  Fallback to localStorage for instant display

Navigation Flow:
  Welcome → Subject Picker → Session Picker → Game Menu → Play Game → Complete
  URL:  /    →  /learning   → /learning/english  → /learning/english/jet2-unit2

English Game Session:
  Enter menu → planSession() allocates all 55 words across 4 games (greedy set-cover)
         ↓
  User picks game → reads pre-planned word/sentence set from state.sessionPlan
         ↓
  Play rounds → track score + per-word results
         ↓
  POST /api/game/result (with session_slug) → save to database + localStorage
         ↓
  Show completion screen with stars earned

Math Game Session:
  Enter menu → problems generated algorithmically per round (no static word bank)
         ↓
  User picks game → generateProblem() creates equations using Israeli notation (× and :)
         ↓
  Play rounds → track score + per-problem results
         ↓
  POST /api/game/result (with session_slug) → save to database + localStorage
         ↓
  Show completion screen with stars earned

Star Tracking:
  Header star-count = global total (sum of all sessions, drives reward tiers)
  Session card star-count = per-session (stars_by_session[slug], each card independent)
```

---

## API Routes

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/game/result` | Save game result (score + per-word accuracy + session_slug) |
| GET | `/api/game/progress` | Get total stars, stars_by_session, accuracy by game, weak words |
| GET | `/api/game/practiced-words` | Get practiced words since last reset |
| POST | `/api/game/reset` | Reset practiced words, sets `reset_at` timestamp |
| GET | `/api/game/config` | App config (version, sessions, topics, rewards, changelog) |
| GET | `/app/{path}` | 301 redirect to `/{path}` (backward compat) |
| GET | `/{path}` | React SPA catch-all (serves static files or `index.html`) |

---

## English Games

| # | Game | Component | Data Source | Rounds | Stars |
|---|------|-----------|-------------|--------|-------|
| 1 | Word Match | `WordMatch.tsx` | `vocabulary` (55 words) | flexible (9-13) | 1/correct |
| 2 | Sentence Scramble | `SentenceScramble.tsx` | `scrambleSentences` (20) | 6 | 2/correct |
| 3 | Listen & Choose | `ListenAndChoose.tsx` | `vocabulary` (55 words) | flexible (9-13) | 1/correct |
| 4 | True or False | `TrueFalse.tsx` | `trueFalseSentences` (22) | 8 | 1/correct |

## Math Games

| # | Game | Component | Data Source | Rounds | Stars |
|---|------|-----------|-------------|--------|-------|
| 1 | Quick Solve | `QuickSolve.tsx` | `generateProblem()` algorithmic | 10 | 1/correct |
| 2 | Missing Number | `MissingNumber.tsx` | `generateMissingNumberProblem()` | 8 | 1/correct |
| 3 | True or False | `MathTrueFalse.tsx` | `generateTFProblem()` | 10 | 1/correct |
| 4 | Bubble Pop | `BubblePop.tsx` | `generateBubbles()` | 8 | 1/correct bubble |

---

## Vocabulary Structure

```typescript
// frontend/src/data/english.ts
const UNITS: Record<string, UnitData> = {
    'jet2-unit2': {
        name: 'Jet 2: Unit 2',
        vocabulary: [...],        // 55 words across 11 categories
        scrambleSentences: [...], // 20 sentences
        trueFalseSentences: [...] // 22 sentences
    },
};
```

**Categories (11):** clothes, seasons, weather, nature, actions, people, body, food, places, descriptions, things

---

## Key Files

```
backend/
├── web_app.py                 # FastAPI app, serves React SPA + API
├── config.py                  # AppConfig (DB URL, environment)
├── defaults.py                # Version, changelog, sessions, topics config
├── exceptions.py              # Custom exceptions
├── logging_config.py          # Structured logging setup
├── sentry_config.py           # Error monitoring
├── routes/
│   └── game.py                # /api/game/* endpoints + Pydantic models
├── services/
│   └── game_service.py        # Save results, compute progress, weak words
└── models/
    ├── base.py                # SQLAlchemy base + session management
    ├── game_result.py         # GameResult ORM model
    └── app_state.py           # AppState ORM model (key-value store)

frontend/
├── public/                    # Static assets (favicon, SVG icons)
├── src/
│   ├── main.tsx               # React root mount with MUI theme + RTL providers
│   ├── App.tsx                # React Router routes + AppProvider + GameRouter
│   ├── theme.ts               # MUI theme with design tokens
│   ├── api/                   # Typed API client (types.ts, game.ts)
│   ├── context/               # AppContext — progress + config state
│   ├── components/            # Layout, StarCounter, RewardCollection, overlays
│   ├── hooks/                 # useAudio, useGameEngine, useRewards
│   ├── pages/                 # Welcome, SubjectPicker, SessionPicker, TopicSessions, GameMenu
│   ├── data/                  # games.ts, english.ts (vocab + planner), math.ts (generators)
│   ├── games/english/         # 4 English game components + GameScreen + WordTracker + CompletionScreen
│   ├── games/math/            # 4 Math game components + MathGameScreen + HintButton
│   └── styles/                # CSS keyframe animations (global.css)
├── package.json               # Node dependencies (React, MUI, Vite)
├── vite.config.ts             # Vite build config + dev proxy to FastAPI
├── tsconfig.json              # TypeScript strict config
└── index.html                 # SPA entry point (Google Fonts, RTL, viewport)

tests/
├── unit/
│   └── test_game_service.py   # 28 unit tests for game service
└── integration/
    └── test_game_api.py       # Integration tests for API + page routes
```

---

## Session Word Planner

Guarantees all 55 vocabulary words are practiced when all 4 games are completed:

1. `planSession()` runs on menu entry — uses greedy set-cover to allocate words across games
2. Picks 6 scramble sentences + 8 T/F sentences maximizing vocabulary coverage
3. Remaining uncovered words split evenly between Games 1 & 3 (direct vocab)
4. `validateSessionPlan()` confirms all 55 words are assigned
5. Re-plans on reset or session completion

---

## Reset Feature

Resets practiced words progress so the child can start fresh:

1. User clicks reset button on menu → confirmation dialog appears
2. `POST /api/game/reset` → stores `reset_at` timestamp in `app_state` table
3. `get_practiced_words()` filters results to only include games played after `reset_at`
4. Word tracker sidebar reflects the reset immediately

---

See [deep-dive.md](./deep-dive.md) for implementation details and [design.md](./design.md) for the visual design system.
