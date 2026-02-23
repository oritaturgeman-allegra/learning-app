# Architecture Deep Dive

Detailed technical reference. For quick overview, see [overview.md](./overview.md).

---

## Backend Architecture

### FastAPI App (`backend/web_app.py`)

- Serves HTML templates via Jinja2 (English or Math based on subject)
- Mounts `/static` for favicon, background SVG, CSS, and JS files
- Global exception handlers (AppError + catch-all)
- Request ID middleware (UUID per request)
- Sentry error monitoring integration
- Uvicorn server with configurable host/port/debug

### Game Routes (`backend/routes/game.py`)

| Endpoint | Method | Pydantic Model | Purpose |
|----------|--------|---------------|---------|
| `/api/game/result` | POST | `SaveGameResultRequest` | Save completed game |
| `/api/game/progress` | GET | `ProgressResponse` | Get learning progress |
| `/api/game/reset` | POST | — | Reset practiced words (sets `reset_at` timestamp) |
| `/api/game/config` | GET | — | App config for React SPA (version, sessions, rewards, changelog) |

**Request validation:**
```python
class SaveGameResultRequest(BaseModel):
    game_type: str  # pattern: word_match|sentence_scramble|listen_choose|true_false|quick_solve|missing_number|true_false_math|bubble_pop
    score: int      # ge=0
    max_score: int  # gt=0
    word_results: List[WordResult]  # [{word, correct, category}]
    session_slug: Optional[str]    # e.g. "jet2-unit2" or "math-tens-hundreds"
```

### Game Service (`backend/services/game_service.py`)

Singleton pattern via `get_game_service()`.

**Configuration constants:**
```python
VALID_GAME_TYPES = {
    "word_match", "sentence_scramble", "listen_choose", "true_false",       # English
    "quick_solve", "missing_number", "true_false_math", "bubble_pop",       # Math
}
STARS_PER_CORRECT = {
    "word_match": 1, "sentence_scramble": 2, "listen_choose": 1, "true_false": 1,
    "quick_solve": 1, "missing_number": 1, "true_false_math": 1, "bubble_pop": 1,
}
ROUNDS_PER_GAME = {
    "word_match": 10, "sentence_scramble": 6, "listen_choose": 10, "true_false": 8,
    "quick_solve": 10, "missing_number": 8, "true_false_math": 10, "bubble_pop": 8,
}
```

**Key methods:**

| Method | Purpose |
|--------|---------|
| `save_game_result()` | Validate + persist game result to DB (with session_slug) |
| `get_progress()` | Compute total stars, stars_by_session, completed_sessions, accuracy by game, weak words, recent games |
| `get_practiced_words()` | Get words practiced since last reset (filters by `reset_at`) |
| `reset_practiced_words()` | Store current timestamp as `reset_at` in `app_state` |
| `_get_reset_at()` | Read `reset_at` timestamp from `app_state` table |

**Weak words algorithm:**
1. Aggregate per-word results across all games
2. Filter words seen at least 2 times
3. Flag words with < 70% accuracy
4. Sort by accuracy ascending (worst first)
5. Return top 10

---

## Database

### GameResult Model (`backend/models/game_result.py`)

```
game_results
├── id            INTEGER  PK, auto-increment
├── game_type     VARCHAR(30)  indexed
├── score         INTEGER
├── max_score     INTEGER
├── accuracy      FLOAT
├── word_results  TEXT  (JSON: [{word, correct, category}])
├── session_slug  VARCHAR(50)  nullable, indexed (which unit: jet2-unit2, multiply-divide)
├── user_id       INTEGER  nullable, indexed (future multi-user)
└── played_at     DATETIME(tz)  default=now(UTC)
```

### AppState Model (`backend/models/app_state.py`)

```
app_state
├── id            INTEGER  PK, auto-increment
├── key           VARCHAR(100)  unique, indexed
├── value         TEXT
└── updated_at    DATETIME(tz)  default=now(UTC), onupdate=now(UTC)
```

Key-value store for app-wide state. Currently stores:
- `reset_at` — ISO timestamp of last practiced-words reset. Used by `get_practiced_words()` to filter `game_results` to only those played after the reset.

### Session Management (`backend/models/base.py`)

- SQLAlchemy declarative base with `session_scope()` context manager
- Auto-commit on success, rollback on exception
- `init_db()` creates tables if not exist
- SQLite (dev) / PostgreSQL (prod) via `DATABASE_URL`

---

## Frontend Architecture

> **Migration in progress:** The frontend is being migrated to React + MUI + TypeScript. The legacy Jinja2 frontend remains active at `:8000` during migration. The new React SPA runs at `:5173` (Vite dev server). See "New React Frontend" section below.

### Legacy: Two Templates + Modular Static Files

The app uses **two HTML templates** (one per subject) backed by **modular CSS and JS files**:

| Template | Subject | Served When |
|----------|---------|-------------|
| `english-fun.html` | English | `subject != "math"` |
| `math-fun.html` | Math | `subject == "math"` |

Both share the same design tokens, animations, reward system, and star tracking (same localStorage keys, same API). They differ in game logic: English uses static vocabulary; Math uses algorithmic problem generation.

### File Architecture

CSS and JS are extracted into modular static files. Templates contain only HTML markup, inline Jinja2 variables, and state initialization.

**CSS files (`frontend/static/css/`):**
| File | Lines | Contents |
|------|-------|----------|
| `shared.css` | ~1500 | Design tokens, global styles, animations, all shared components |
| `english.css` | ~480 | Word tracker, scramble drop zone, English game card colors |
| `math.css` | ~350 | Equation display, hint tooltips, bubbles, `:root` override (`--bg: #f0f7ff`) |

**JS files (`frontend/static/js/`):**
| File | Lines | Contents |
|------|-------|----------|
| `shared.js` | ~360 | API calls, audio, shuffle, stars, confetti, milestones, rewards, collection, screen nav |
| `english-data.js` | ~140 | `UNITS` vocabulary (55 words, 20 scramble, 22 T/F), `GAME_TYPE_MAP` |
| `english-game.js` | ~970 | Session planner, word tracker, 4 English games, navigation |
| `math-data.js` | ~70 | `CATEGORIES_BY_SESSION`, `MATH_HINTS`, `GAME_TYPE_MAP`, config consts |
| `math-game.js` | ~1040 | Problem generators, 4 math games, hint system, navigation |

**Load order in templates:**
```
1. Inline <script> in <head>: Jinja2 vars (REWARD_TIERS, SUBJECT, SESSION_SLUG)
2. <script src="/static/js/shared.js">
3. <script src="/static/js/{subject}-data.js">
4. <script src="/static/js/{subject}-game.js">
5. Inline <script> at end of body: state init + DOMContentLoaded
```

**What stays inline in templates (Jinja2-dependent):**
- `const REWARD_TIERS = {{ reward_tiers | tojson }};` — server-side data
- `const SUBJECT = '{{ subject|default("...") }}';` — route context
- `const SESSION_SLUG = '{{ session_slug|default("") }}';` — route context
- `let state = { ... }` — references localStorage
- `window.addEventListener('DOMContentLoaded', ...)` — init logic
- `v{{ version }}` in footer

### English Template (`frontend/templates/english-fun.html`)

### Screen Flow

```
Welcome Screen → Menu Screen → Game Screen → Complete Screen
     │                │              │              │
     │                ├── Game 1 ────┤              │
     │                ├── Game 2 ────┤              │
     │                ├── Game 3 ────┤              │
     │                └── Game 4 ────┘              │
     │                                              │
     └──────────────────────────────────────────────┘
                    (back to menu)
```

### State Object

```javascript
let state = {
    currentGame: null,     // 1-4
    currentRound: 0,
    totalRounds: 0,
    gameScore: 0,
    totalStars: 0,         // persisted to localStorage + API
    gameData: [],          // shuffled questions for current game
    answering: false,      // prevents double-clicks
    wordResults: [],       // per-word results for API
    scrambleWords: [],     // Game 2 specific: ordered word slots
    sessionPlan: null,     // planned word/sentence sets for full vocabulary coverage
};
```

### Audio System

**Text-to-Speech:**
- Web Speech API with `SpeechSynthesisUtterance`
- Preferred voice: American English female (en-US)
- Fallback: any English voice available
- Not available on all browsers — app works without it

**Sound Effects (AudioContext):**
- `playCorrectSound()` — ascending tones (success)
- `playWrongSound()` — descending tones (failure)
- `playStarSound()` — sparkle effect
- Requires user gesture to initialize (welcome button handles this)

### Session Word Planner

Replaces the old per-game `freshShuffle()` with session-level allocation that guarantees full vocabulary coverage.

**Core functions:**

| Function | Purpose |
|----------|---------|
| `buildCoverageMap()` | Maps each vocab word → which sentences (G2/G4) contain it |
| `sentenceCoverage(sentence, uncovered)` | Counts how many uncovered words a sentence covers |
| `getWordsInSentence(sentence)` | Extracts vocab words from a sentence (same logic as `markPracticedWords()`) |
| `planSession()` | Greedy set-cover: picks 6 scramble + 8 T/F sentences, assigns remaining to Games 1 & 3 |
| `validateSessionPlan(plan)` | Asserts all 55 words are covered; logs warning if any missed |

**Algorithm (greedy set-cover):**
```
1. uncovered = Set(all 55 words)
2. Greedy pick 6 scramble sentences → each pick maximizes uncovered word coverage
3. Greedy pick 8 T/F sentences → same approach on remaining uncovered
4. Remaining uncovered → split evenly between Game 1 and Game 3
5. Games 1 & 3 have flexible round counts (matching their word count)
6. Shuffle all 4 sets for variety
7. Store in state.sessionPlan
```

**Called from:** `goToMenu()` (once per session), `executeReset()`, `closeSessionPopup()`

**Session plan shape:**
```javascript
state.sessionPlan = {
    game1Words: [...],       // vocab items (flexible count, ~9-13)
    game2Sentences: [...],   // 6 scramble sentences
    game3Words: [...],       // vocab items (flexible count, ~9-13)
    game4Sentences: [...],   // 8 T/F sentences
}
```

---

### Math Template (`frontend/templates/math-fun.html`)

HTML-only template for math games. Game logic in `math-game.js`, data/hints in `math-data.js`. No vocabulary data — problems generated algorithmically.

**Math-specific features:**
- **Problem Generator:** `generateProblem()` / `generateProblemByCategory(cat)` — session-aware, picks categories from `CATEGORIES_BY_SESSION[SESSION_SLUG]`
- **Israeli Notation:** `×` for multiplication, `:` for division (e.g., `450 : 9 = 50`)
- **Distractor Generator:** `generateDistractors(answer, count)` — near-miss wrong answers for multiple choice
- **Bubble Pop:** `generateExpressionsForTarget(target, count)` — session-aware, finds multiplication/division/power expressions equaling a target number
- **No word tracker** — math doesn't track vocabulary
- **No session planner** — each round generates fresh problems

**Problem categories (Chapter A — כפל וחילוק בעשרות ובמאות):**

| Category | Example | Answer Range |
|----------|---------|-------------|
| `multiply_tens` | `30 × 4 = ?` | 20–8100 |
| `multiply_hundreds` | `7 × 100 = ?` | 200–9000 |
| `divide_single` | `450 : 9 = ?` | 10–100 |
| `divide_tens` | `3000 : 100 = ?` | 2–80 |
| `properties_0_1` | `0 × 847 = ?`, `1 × 56 = ?` | 0 or n |
| `order_of_operations` | `3 + 4 × 5 = ?`, `(3+4) × 5 = ?` | varies |

**Problem categories (Chapter B — כפל דו-ספרתי):**

| Category | Example | Answer Range |
|----------|---------|-------------|
| `two_digit_x_one_digit` | `23 × 4 = ?` | ≤ 500 |
| `two_digit_x_two_digit` | `15 × 12 = ?` | ≤ 2000 |
| `powers` | `5² = ?` | 4–144 |

**Problem categories (Chapter C — חילוק ארוך):**

| Category | Example | Answer Range | Notes |
|----------|---------|-------------|-------|
| `divide_remainder` | `47 : 5 = 9 שארית 2` | quotient ≤ 17 | Dual-input: quotient + remainder |
| `long_division` | `156 : 12 = 13` | 11–100 | 3-digit ÷ 1-digit, clean result |
| `division_verify` | `? × 7 = 63` | 2–17 | Reverse multiplication check |

**Problem categories (Chapter D — מספרים ראשוניים):**

| Category | Example | Answer Range | Notes |
|----------|---------|-------------|-------|
| `divisibility_rules` | `123 : 3 = ?` | 4–33 | Division by 3, 6, or 9; hint explains digit-sum rule |
| `prime_composite` | `? × 3 = 21` | 2–50 | Primes shown as `1 × ? = p`, composites as `? × factor = n` |
| `prime_factorization` | `36 = 2 × 2 × 3 × _` | prime factor | 20 curated numbers (12–100) with known factorizations |

**Hint system (all chapters):**
- All problem categories include a `hint` field with a natural Hebrew solving clue
- Hints centralized in `MATH_HINTS` const object (organized by chapter/category)
- 💡 button appears next to the equation, tap to show tooltip
- Auto-closes after 4 seconds

**localStorage keys (math-specific):**

| Key | Purpose |
|-----|---------|
| `ariel_math_session_games` | Math games completed this session (JSON array) |

---

## New React Frontend (Migration In Progress)

### Stack
- **React 19** + **TypeScript** — component-based UI with strict types
- **MUI 7** (Material UI) — responsive components, RTL support via `stylis-plugin-rtl`
- **React Router 7** — client-side routing matching existing URL structure
- **Vite 7** — dev server with HMR + production build, proxies `/api/*` to FastAPI
- **Emotion** — CSS-in-JS (MUI's styling engine), with RTL cache

### Project Structure (`frontend/src/`)
```
src/
├── main.tsx          # Root mount: StrictMode → CacheProvider (RTL) → ThemeProvider → App
├── App.tsx           # BrowserRouter + Routes (placeholder pages during scaffolding)
├── theme.ts          # MUI theme: design tokens migrated from shared.css
└── vite-env.d.ts     # Vite type declarations
```

### MUI Theme (`theme.ts`)
Design tokens migrated from `shared.css` CSS custom properties:

| Token | MUI Mapping | Value |
|-------|------------|-------|
| `--purple` | `palette.primary.main` | `#a855f7` |
| `--pink` | `palette.secondary.main` | `#ec4899` |
| `--green` | `palette.success.main` | `#22c55e` |
| `--red` | `palette.error.main` | `#ef4444` |
| `--blue` | `palette.info.main` | `#3b82f6` |
| `--gold` | `palette.warning.main` | `#f59e0b` |
| `--bg` | `palette.background.default` | `#f5f0ff` |
| `--font-display` | `typography.h1-h6, button` | Fredoka |
| `--font-body` | `typography.fontFamily` | Rubik |
| `--radius-md` | `shape.borderRadius` | `16` |
| `--radius-pill` | `MuiButton.borderRadius` | `9999` |

Direction set to `rtl`. Emotion cache uses `stylis-plugin-rtl` to flip all CSS.

### Routes (React Router)
```
/                                              → Welcome (landing page)
/learning                                      → SubjectPicker (English/Math)
/learning/:subject                             → SessionPicker
/learning/:subject/:sessionSlug                → GameMenu
/learning/:subject/:sessionSlug/play/:gameId   → GameScreen (English games)
```

### Dev Workflow
```bash
cd frontend && npm run dev      # Vite at :5173 (proxies /api to :8000)
cd frontend && npm run build    # Production build to frontend/dist/
```

### Production Serving (FastAPI)
During migration, React is served under `/app/*` so both frontends coexist:
- Legacy Jinja2: `http://localhost:8000/` (unchanged)
- React SPA: `http://localhost:8000/app/` (new)

FastAPI mounts `frontend/dist/assets/` at `/app/assets` and serves `index.html` via a catch-all route at `/app/{path}`. Vite builds with `base: "/app/"` so all asset paths are correct.

### Config API (`/api/game/config`)
Replaces Jinja2 template context injection. Returns all server-side config React needs:
- `version` — app version string
- `changelog` — recent changelog entries (Hebrew)
- `reward_tiers` — star milestone rewards
- `sessions_by_subject` — all sessions grouped by subject
- `subject` / `session_slug` — optional query params for context

### React Project Structure (Phases 3-5)
```
frontend/src/
├── api/
│   ├── types.ts              # TypeScript interfaces for API responses (incl. WordResult)
│   └── game.ts               # Typed API client (fetch wrapper)
├── context/
│   └── AppContext.tsx         # React Context for progress + config + awardStars()
├── hooks/
│   ├── useAudio.ts           # AudioContext tones (correct/wrong/celebration) + TTS
│   ├── useGameEngine.ts      # Shared game loop: rounds, scoring, answer delays
│   └── useRewards.ts         # Milestone checks, reward unlocks, confetti orchestration
├── components/
│   ├── Layout.tsx             # Header shell + celebration overlays + milestone watcher
│   ├── StarCounter.tsx        # Gold pill star counter
│   ├── RewardCollection.tsx   # Trophy gallery dialog
│   ├── Confetti.tsx           # 30-piece confetti overlay (portal)
│   ├── MilestoneOverlay.tsx   # 5-star / 10-star celebration
│   └── RewardPopup.tsx        # Reward tier unlock popup
├── data/
│   ├── games.ts              # Game card metadata per subject
│   └── english.ts            # Vocabulary (55 words), sentences, session planner
├── games/
│   └── english/
│       ├── GameScreen.tsx     # Route wrapper: plan manager, game router, API save
│       ├── CompletionScreen.tsx # Score summary after finishing a game
│       ├── WordTracker.tsx    # Vocabulary sidebar (desktop) / drawer (mobile)
│       ├── WordMatch.tsx      # Game 1: emoji + Hebrew → pick English (4 options)
│       ├── SentenceScramble.tsx # Game 2: Hebrew → assemble English from chips
│       ├── ListenAndChoose.tsx  # Game 3: hear word → pick from 4 (emoji+English+Hebrew)
│       └── TrueFalse.tsx      # Game 4: English+Hebrew sentence → yes/no
├── pages/
│   ├── Welcome.tsx            # Landing page (standalone, no header)
│   ├── SubjectPicker.tsx      # English/Math selection
│   ├── SessionPicker.tsx      # Unit selection with subject tabs
│   └── GameMenu.tsx           # Game card grid (4 per subject) + word tracker
├── styles/
│   └── global.css             # CSS keyframe animations from shared.css
├── App.tsx                    # Routes + AppProvider
├── main.tsx                   # React root with MUI + RTL providers
└── theme.ts                   # MUI theme (design tokens)
```

### State Management
- `AppContext` provides progress + config data to all pages, plus `awardStars()` for optimistic star updates
- Fetches `/api/game/config` (once) and `/api/game/progress` (on mount + after games)
- Falls back to localStorage (`ariel_stars`, `ariel_earned_rewards`) for instant display

### Audio System (`useAudio.ts`)
- Pure functions (not a React hook) — AudioContext singleton
- `playCorrect()`: C5-E5-G5 ascending sine chime
- `playWrong()`: 150Hz sawtooth buzz
- `playCelebration()`: C5-E5-G5-C6 four-note melody
- `speak(text)`: Web Speech API TTS (en-US, Samantha voice preferred)

### Reward System (`useRewards.ts`)
- Milestone every 5 stars (🎉 overlay + confetti + celebration audio)
- Emoji parade every 10 stars (🏆 + 8 floating emojis)
- Reward tier unlock popup after milestone (3s delay, 5s auto-close)
- localStorage keys: `ariel_last_milestone`, `ariel_earned_rewards`
- `refreshProgress()` exposed for re-fetch after game completion

### Game Engine Hook (`useGameEngine.ts`)
Shared game loop used by all 4 English game components:
- **Options**: `totalRounds`, `starsPerCorrect` (1 or 2), `answerDelay` (1500 or 2500ms)
- **State**: `currentRound`, `gameScore`, `maxScore`, `isAnswering`, `isFinished`, `progressPercent`, `wordResults`
- **`submitAnswer(correct, results)`**: Plays audio feedback, awards stars via `awardStars()`, accumulates word results, locks input during delay, then advances round or sets `isFinished`
- Layout's milestone watcher (`useEffect` on `totalStars`) auto-triggers celebrations when stars increase

### English Games (Phase 5)
- **Data**: `data/english.ts` — 55 typed vocabulary words, 20 scramble sentences, 22 T/F sentences, Fisher-Yates shuffle, greedy set-cover session planner
- **Session plan**: Cached in `sessionStorage` per session slug. 6 scramble + 8 T/F sentences (greedy, max coverage) → remaining words split between Games 1 & 3
- **GameScreen**: Route wrapper (`/play/:gameId`) — creates plan, loads practiced words, renders game component, saves result to API on finish
- **CompletionScreen**: Score summary with celebration audio, replay/back buttons
- **WordTracker**: Fixed sidebar (desktop ≥1100px) or drawer+FAB (mobile) showing 55 word chips, practiced words get teal background + strikethrough
- **Game 1 (WordMatch)**: Emoji + Hebrew → 4 English options, 1 star/correct
- **Game 2 (SentenceScramble)**: Hebrew → assemble English from chip tap, 2 stars/correct, 6 rounds
- **Game 3 (ListenAndChoose)**: Auto-speak → 4 options (emoji+English+Hebrew), 1 star/correct
- **Game 4 (TrueFalse)**: English+Hebrew sentence → yes/no, 1 star/correct, 8 rounds

### Migration Plan
See `docs/roadmap/react-migration-implementation.md` for the full 7-phase plan. Phases 1-5 complete. Next: Phase 6 (math games) → Phase 7 (cleanup).

---

## Vocabulary Data Structure

```javascript
const UNITS = {
    'jet2-unit2': {
        name: 'Jet 2: Unit 2',
        nameHebrew: 'יחידה 2',
        vocabulary: [/* 55 items */],
        scrambleSentences: [/* 20 items */],
        trueFalseSentences: [/* 22 items */],
    },
    // Future units added here
};

// Backward-compatible aliases (game logic references these)
const ACTIVE_UNIT = UNITS['jet2-unit2'];
const vocabulary = ACTIVE_UNIT.vocabulary;
const scrambleSentences = ACTIVE_UNIT.scrambleSentences;
const trueFalseSentences = ACTIVE_UNIT.trueFalseSentences;
```

**Vocabulary item shape:** `{ english, hebrew, emoji, category }`
**Scramble sentence shape:** `{ english, hebrew }`
**True/false sentence shape:** `{ english, hebrew, answer }`

**11 Categories:** clothes (7), seasons (4), weather (4), nature (7), actions (11), people (6), body (3), food (1), places (3), descriptions (5), things (4)

---

## Reward System

### Reward Tiers (Final)

Collectible cards unlocked at star milestones. Defined in `backend/defaults.py` as `REWARD_TIERS`.

| Stars | ID | English | Hebrew | Emoji |
|-------|----|---------|--------|-------|
| 25 | spark | Spark | ניצוץ | ✨ |
| 50 | slay | Slay | סלייי | 💅 |
| 100 | fire | Fire | פייר | 🔥 |
| 150 | unicorn | Unicorn | חד-קרן | 🦄 |
| 200 | goat | GOAT | גואט | 🐐 |
| 300 | main_character | Main Character | שחקנית ראשית | 👑 |

### How It Works

- **No new DB table** — rewards are derived from `total_stars` in `get_progress()`
- **Backend:** `earned_rewards` = list of tier IDs where `tier.stars <= total_stars`; `next_reward` = first unearned tier or null
- **Frontend cache:** `ariel_earned_rewards` localStorage key prevents re-showing popups; API recalculates on load
- **Reward popup:** Bounce animation, auto-dismiss after 5s, triggered from `checkRewardUnlock()` after milestones
- **Collection gallery:** Trophy button in header opens overlay with 2x3 grid (earned = vibrant + gold border, locked = grey + dashed border)

---

## Math Sessions (`backend/defaults.py`)

4 chapter-based session cards under Math, matching the 4th-grade textbook (פרקים א׳–ד׳):

| Slug | Hebrew Name | Topics | Status |
|------|-------------|--------|--------|
| `math-tens-hundreds` | כפל וחילוק בעשרות ובמאות | ×10/100/1000, ÷ single digit, order of operations, properties of 0 and 1 | Active |
| `math-two-digit` | כפל דו-ספרתי | 2-digit multiplication, vertical multiplication, powers | Active |
| `math-long-division` | חילוק ארוך | Division with remainder, long division, division verification | Active |
| `math-primes` | מספרים ראשוניים | Divisibility rules (3, 6, 9), prime/composite numbers, prime factorization | Active |

### Session Completion (`completed_sessions`)

- **Derived from DB** — `get_progress()` groups game results by `session_slug` and checks if all required game types have been played
- **Required games:** Math sessions need `{quick_solve, missing_number, true_false_math, bubble_pop}`; English sessions need `{word_match, sentence_scramble, listen_choose, true_false}`
- **Frontend:** `restoreSessionCheckmarks()` receives the list from the API and adds `session-completed` class to matching session cards (green border + ✓ badge)

---

## Configuration

### AppConfig (`backend/config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `DATABASE_URL` | `sqlite:///learning_app.db` | SQLAlchemy connection string |
| `FLASK_HOST` | `0.0.0.0` | Server bind address |
| `FLASK_PORT` | `8000` | Server port |
| `FLASK_DEBUG` | `true` | Debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `SENTRY_DSN` | `""` | Sentry error monitoring |

### localStorage Keys

| Key | Purpose |
|-----|---------|
| `ariel_stars` | Total stars (fallback when API unavailable) — shared across subjects |
| `ariel_session_games` | English games completed this session (JSON array of game numbers) |
| `ariel_math_session_games` | Math games completed this session (JSON array of game numbers) |
| `ariel_earned_rewards` | Earned reward tier IDs (prevents re-showing popups) — shared across subjects |
| `ariel_last_milestone` | Last milestone star count shown (prevents re-showing) |

---

## Error Handling

### Backend
- Custom `AppError` → `GameError` hierarchy (`backend/exceptions.py`)
- All service methods raise `GameError` on failure
- Routes catch `GameError` → HTTP 400/500 with message
- Global catch-all → HTTP 500 + Sentry capture
- Never exposes internal errors to client

### Frontend
- API calls wrapped in try/catch
- Falls back to localStorage if API unavailable
- `state.answering` flag prevents double-click race conditions
- AudioContext requires user gesture — handled by welcome screen button

---

## Testing

### Test Suite (`tests/unit/test_game_service.py`)

24 tests covering:

| Test | What it verifies |
|------|-----------------|
| `test_save_valid_result` | Basic save works |
| `test_save_perfect_score` | 100% score accepted |
| `test_save_zero_score` | 0 score accepted |
| `test_save_invalid_game_type_raises` | Bad game type rejected |
| `test_save_negative_score_raises` | Negative score rejected |
| `test_save_score_exceeds_max_raises` | Score > max rejected |
| `test_save_sentence_scramble_result` | 2-star game type works |
| `test_empty_progress` | Empty DB returns zeros |
| `test_progress_after_games` | Stars + accuracy calculated |
| `test_weak_words_detection` | Low-accuracy words flagged |
| `test_recent_games_limited_to_10` | Recent games capped at 10 |

**Run:** `.venv/bin/pytest tests/unit/test_game_service.py -v`

---

## Adding a New Unit (Future)

1. Add new key to `UNITS` in `frontend/static/js/english-data.js`:
```javascript
'jet2-unit3': {
    name: 'Jet 2: Unit 3',
    vocabulary: [...],
    scrambleSentences: [...],
    trueFalseSentences: [...],
}
```

2. Add unit selection UI to menu screen
3. Change `ACTIVE_UNIT` to be dynamic based on selection
4. Game logic needs zero changes — it references the derived arrays
