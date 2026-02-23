# Architecture Deep Dive

Detailed technical reference. For quick overview, see [overview.md](./overview.md).

---

## Backend Architecture

### FastAPI App (`backend/web_app.py`)

- Serves React SPA from `frontend/dist/` at root `/`
- Mounts `/assets` for built JS/CSS chunks
- Catch-all `/{path}` route serves static files or `index.html` for SPA routing
- Redirects old `/app/*` URLs to root equivalents (301)
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
├── category      VARCHAR(30)  indexed (english or math)
├── topic         VARCHAR(50)  nullable, indexed (e.g. "Vocabulary", "Multiplication and Division")
├── session_slug  VARCHAR(50)  nullable, indexed (e.g. jet2-unit2, math-tens-hundreds)
├── game_type     VARCHAR(30)  indexed
├── score         INTEGER
├── max_score     INTEGER
├── accuracy      FLOAT
├── word_results  TEXT  (JSON: [{word, correct, category}])
├── user_id       INTEGER  nullable, indexed (future multi-user)
└── played_at     DATETIME(tz)  default=now(UTC)
```

**Topic derivation**: The `topic` field is auto-derived from `session_slug` via the `TOPIC_BY_SESSION` mapping in `game_service.py`. This enables analytics grouping: category → topic → session_slug.

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

### Stack
- **React 19** + **TypeScript** — component-based UI with strict types
- **MUI 7** (Material UI) — responsive components, RTL support via `stylis-plugin-rtl`
- **React Router 7** — client-side routing
- **Vite 7** — dev server with HMR + production build, proxies `/api/*` to FastAPI
- **Emotion** — CSS-in-JS (MUI's styling engine), with RTL cache

### Routes (React Router)
```
/                                              → Welcome (landing page)
/learning                                      → SubjectPicker (English/Math)
/learning/:subject                             → SessionPicker (topics or sessions)
/learning/:subject/topic/:topicSlug            → TopicSessions (sessions within a topic)
/learning/:subject/:sessionSlug                → GameMenu (4 game cards)
/learning/:subject/:sessionSlug/play/:gameId   → GameRouter → GameScreen or MathGameScreen
```

### Dev Workflow
```bash
cd frontend && npm run dev      # Vite at :5173 (proxies /api to :8000)
cd frontend && npm run build    # Production build to frontend/dist/
```

### Production Serving (FastAPI)
React SPA is served at root `/`:
- `/assets/*` → built JS/CSS chunks (via `StaticFiles` mount)
- `/{path}` → catch-all serves static files from dist or falls back to `index.html`
- `/app/*` → 301 redirect to `/*` (backward compat)

Game components are code-split with `React.lazy()` — each loads as a separate chunk.

### Config API (`/api/game/config`)
Returns all server-side config React needs:
- `version`, `changelog` — app info
- `reward_tiers` — star milestone rewards
- `sessions_by_subject` — all sessions grouped by subject
- `topics_by_subject` — topic groupings (for subjects with topics, like math)

### Project Structure (`frontend/src/`)
```
frontend/src/
├── api/
│   ├── types.ts              # TypeScript interfaces (Session, Topic, WordResult, etc.)
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
│   ├── english.ts            # Vocabulary (55 words), sentences, session planner
│   └── math.ts               # Problem generators, hints, categories, distractors, TF, bubbles
├── games/
│   ├── english/
│   │   ├── GameScreen.tsx     # Route wrapper: plan manager, game router, API save
│   │   ├── CompletionScreen.tsx # Score summary (shared by English + Math)
│   │   ├── WordTracker.tsx    # Vocabulary FAB + drawer showing practiced words
│   │   ├── WordMatch.tsx      # Game 1: emoji + Hebrew → pick English (4 options)
│   │   ├── SentenceScramble.tsx # Game 2: Hebrew → assemble English from chips
│   │   ├── ListenAndChoose.tsx  # Game 3: hear word → pick from 4
│   │   └── TrueFalse.tsx      # Game 4: English+Hebrew sentence → yes/no
│   └── math/
│       ├── MathGameScreen.tsx # Route wrapper: game router, API save
│       ├── HintButton.tsx     # Hint popover (auto-close 4s)
│       ├── QuickSolve.tsx     # Game 1: 4-option multiple choice + remainder input
│       ├── MissingNumber.tsx  # Game 2: blanked equation, 4 options
│       ├── MathTrueFalse.tsx  # Game 3: equation → yes/no
│       └── BubblePop.tsx      # Game 4: tap bubbles matching target number
├── pages/
│   ├── Welcome.tsx            # Landing page (standalone, no header)
│   ├── SubjectPicker.tsx      # English/Math selection
│   ├── SessionPicker.tsx      # Session or topic selection with subject tabs
│   ├── TopicSessions.tsx      # Sessions within a topic (e.g., math chapters)
│   └── GameMenu.tsx           # Game card grid (4 per subject) + word tracker
├── styles/
│   └── global.css             # CSS keyframe animations
├── App.tsx                    # Routes + AppProvider + GameRouter
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
- Milestone every 5 stars (overlay + confetti + celebration audio)
- Emoji parade every 10 stars (trophy + 8 floating emojis)
- Reward tier unlock popup after milestone (3s delay, 5s auto-close)
- `refreshProgress()` exposed for re-fetch after game completion

### Game Engine Hook (`useGameEngine.ts`)
Shared game loop used by all 4 English games and 3 of 4 math games (BubblePop manages its own multi-tap state):
- **Options**: `totalRounds`, `starsPerCorrect` (1 or 2), `answerDelay` (1500 or 2500ms)
- **State**: `currentRound`, `gameScore`, `maxScore`, `isAnswering`, `isFinished`, `progressPercent`, `wordResults`
- **`submitAnswer(correct, results)`**: Plays audio feedback, awards stars, accumulates results, locks input during delay, advances round or finishes

### English Games
- **Data**: `data/english.ts` — 55 typed vocab words, 20 scramble sentences, 22 T/F sentences, session planner
- **Session plan**: Cached in `sessionStorage`. Greedy set-cover allocates all 55 words across 4 games
- **GameScreen**: Route wrapper — creates plan, loads practiced words, renders game, saves result
- **WordTracker**: Fixed sidebar (desktop) or drawer+FAB (mobile) showing 55 word chips

### Math Games
- **Data**: `data/math.ts` — procedural generators for 15 categories, Hebrew hints, distractors, TF variants, bubble expressions
- **MathGameScreen**: Route wrapper — renders game, saves result, reuses `CompletionScreen`
- **GameRouter** (`App.tsx`): Checks `subject` param → English `GameScreen` or `MathGameScreen`
- **HintButton**: Shared component — icon button → MUI Popover with hint, auto-closes 4s
- **BubblePop**: Multi-tap per round — does NOT use `useGameEngine`, manages own state

---

## Vocabulary Data Structure

```typescript
// frontend/src/data/english.ts
const UNITS: Record<string, UnitData> = {
    'jet2-unit2': {
        name: 'Jet 2: Unit 2',
        nameHebrew: 'יחידה 2',
        vocabulary: [/* 55 items */],
        scrambleSentences: [/* 20 items */],
        trueFalseSentences: [/* 22 items */],
    },
};
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
| `ariel_session_completed_games_{slug}` | Games completed this session (JSON array of game IDs) |
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
- `useGameEngine.isAnswering` prevents double-click race conditions
- AudioContext requires user gesture — handled by welcome screen button

---

## Testing

### Test Suite

71 tests across unit and integration suites covering:

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

1. Add new key to `UNITS` in `frontend/src/data/english.ts`
2. Add session config to `SESSIONS_BY_SUBJECT` in `backend/defaults.py`
3. Game logic needs zero changes — it references the derived arrays
4. See `CLAUDE.md` "Navigation Architecture" section for the full guide on adding new subjects
