# Architecture Overview

Quick reference for Ariel's English Adventure. For details, see [deep-dive.md](./deep-dive.md).

---

## What This App Does

Gamified English learning for a 9.5-year-old Israeli girl. Teaches vocabulary from the Jet 2 textbook (Unit 2) through 4 interactive mini-games with star rewards, animations, and audio feedback.

---

## Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.13, FastAPI, SQLAlchemy |
| **Frontend (legacy)** | Two HTML templates + modular static CSS/JS files, vanilla JS |
| **Frontend (new — in progress)** | React 19 + TypeScript + MUI 7 + Vite, SPA with RTL support |
| **Database** | SQLite (dev) / PostgreSQL (prod) |
| **Audio** | Web Speech API (TTS), AudioContext (sound effects) |
| **Fonts** | Google Fonts (Fredoka display, Rubik body/Hebrew) |
| **Languages** | Hebrew UI (RTL) + English content (LTR) |
| **Testing** | pytest, pytest-cov, pytest-mock |

> **Migration in progress:** The frontend is being migrated from Jinja2-served vanilla JS to a React SPA. Both frontends coexist during migration — legacy at `:8000` (Jinja2), new at `:5173` (Vite dev). See `frontend/src/` for the React codebase.

---

## Data Flow

```
App Start (four entry points):
  GET /                                  → Welcome screen (landing page)
  GET /learning                          → Subject picker (choose English or Math)
  GET /learning/{subject}                → Session picker (choose a learning unit)
  GET /learning/{subject}/{session_slug} → Game menu for that session (refresh-safe)
  GET /learning/{session_slug}           → 301 redirect to /learning/english/{slug} (backward compat)
         ↓
  Load vocabulary from UNITS[session_slug] (55 words, 20 scramble sentences, 22 T/F sentences)
         ↓
  Derive backward-compatible arrays: vocabulary, scrambleSentences, trueFalseSentences
         ↓
  Load stars from API → fallback to localStorage

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
| GET | `/` | Serve landing page (welcome screen) |
| GET | `/learning` | Serve subject picker screen |
| GET | `/learning/{subject}` | Serve session picker for a subject |
| GET | `/learning/{subject}/{session_slug}` | Serve game menu for a session |
| GET | `/learning/{session_slug}` | 301 redirect to `/learning/english/{slug}` (backward compat) |
| GET | `/health` | Health check |
| POST | `/api/game/result` | Save game result (score + per-word accuracy + session_slug) |
| GET | `/api/game/progress` | Get total stars, stars_by_session, accuracy by game, weak words |
| POST | `/api/game/reset` | Reset practiced words, sets `reset_at` timestamp |
| GET | `/api/game/config` | App config for React SPA (version, sessions, rewards, changelog) |
| GET | `/app/{path}` | React SPA catch-all (serves `index.html` from `frontend/dist/`) |

---

## English Games (english-fun.html)

| # | Game | Class Name | Data Source | Rounds | Stars |
|---|------|-----------|-------------|--------|-------|
| 1 | Word Match | `game-card-word-match` | `vocabulary` (55 words) | flexible (9-13) | 1/correct |
| 2 | Sentence Builder | `game-card-sentence-builder` | `scrambleSentences` (20) | 6 | 2/correct |
| 3 | Listen & Choose | `game-card-listen-choose` | `vocabulary` (55 words) | flexible (9-13) | 1/correct |
| 4 | True or False | `game-card-true-false` | `trueFalseSentences` (22) | 8 | 1/correct |

## Math Games (math-fun.html)

| # | Game | Class Name | Data Source | Rounds | Stars |
|---|------|-----------|-------------|--------|-------|
| 1 | Quick Solve | `game-card-quick-solve` | `generateProblem()` algorithmic | 10 | 1/correct |
| 2 | Missing Number | `game-card-missing-number` | `generateProblem()` with blank | 8 | 1/correct |
| 3 | True or False | `game-card-true-false-math` | `generateTFProblem()` | 10 | 1/correct |
| 4 | Bubble Pop | `game-card-bubble-pop` | `generateExpressionsForTarget()` | 8 | 1/correct bubble |

---

## Vocabulary Structure

```javascript
const UNITS = {
    'jet2-unit2': {
        name: 'Jet 2: Unit 2',
        vocabulary: [...],        // 55 words across 11 categories
        scrambleSentences: [...], // 20 sentences
        trueFalseSentences: [...] // 22 sentences
    },
    // Future: 'jet2-unit3': { ... }
};

// SESSION_SLUG set from Jinja2 template context (e.g., 'jet2-unit2')
const ACTIVE_UNIT = UNITS[SESSION_SLUG] || UNITS['jet2-unit2'];
const vocabulary = ACTIVE_UNIT.vocabulary;  // backward-compatible
```

**Categories (11):** clothes, seasons, weather, nature, actions, people, body, food, places, descriptions, things

---

## Key Files

```
backend/
├── web_app.py                 # FastAPI app, static files, template serving
├── config.py                  # AppConfig (DB URL, environment)
├── defaults.py                # Version, changelog, sessions config
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
├── templates/                 # LEGACY — Jinja2 templates (active until React migration complete)
│   ├── english-fun.html       # English template (HTML + inline Jinja2 vars + init)
│   └── math-fun.html          # Math template (HTML + inline Jinja2 vars + init)
├── static/                    # LEGACY — vanilla CSS/JS (active until React migration complete)
│   ├── css/
│   │   ├── shared.css         # Shared design tokens, animations, components
│   │   ├── english.css        # English-specific styles (word tracker, scramble)
│   │   └── math.css           # Math-specific styles (equations, hints, bubbles)
│   └── js/
│       ├── shared.js          # Shared functions (audio, rewards, API, UI)
│       ├── english-data.js    # UNITS vocabulary data, GAME_TYPE_MAP
│       ├── english-game.js    # English game logic, word tracker, planner
│       ├── math-data.js       # CATEGORIES_BY_SESSION, MATH_HINTS, config
│       └── math-game.js       # Math game logic, problem generators
├── src/                       # NEW — React + TypeScript SPA (migration in progress)
│   ├── main.tsx               # React root mount with MUI theme + RTL providers
│   ├── App.tsx                # React Router routes + AppProvider
│   ├── theme.ts               # MUI theme with design tokens from shared.css
│   ├── api/                   # Typed API client (types.ts, game.ts)
│   ├── context/               # AppContext — progress + config state
│   ├── components/            # Layout, StarCounter, RewardCollection, overlays
│   ├── hooks/                 # useAudio, useGameEngine, useRewards
│   ├── pages/                 # Welcome, SubjectPicker, SessionPicker, GameMenu
│   ├── data/                  # games.ts (card metadata), english.ts (vocab + planner)
│   ├── games/english/         # 4 English game components + GameScreen + WordTracker
│   └── styles/                # CSS keyframe animations (global.css)
├── package.json               # Node dependencies (React, MUI, Vite)
├── vite.config.ts             # Vite build config + dev proxy to FastAPI
├── tsconfig.json              # TypeScript strict config
└── index.html                 # SPA entry point (Google Fonts, RTL, viewport)

tests/
└── unit/
    └── test_game_service.py   # 28 tests for game service
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

See [deep-dive.md](./deep-dive.md) for backend details and [design.md](./design.md) for visual design system.
