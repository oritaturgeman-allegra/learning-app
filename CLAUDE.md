# Ariel Learning App

Gamified English learning web app for a Gen Alpha Israeli girl (4th grade). Teaches vocabulary from Jet 2 textbook (Unit 2) through 4 interactive mini-games with rewards, animations, and sound feedback.

## Commands

```bash
# Run web app
.venv/bin/python -m backend.web_app
# Open http://localhost:8000

# Test
.venv/bin/pytest tests/unit/test_game_service.py -v  # Game tests
.venv/bin/pytest tests/ --cov=backend                 # Full suite
```

## Stack

- **Backend:** Python 3.13, FastAPI, SQLAlchemy (SQLite dev / PostgreSQL prod)
- **Frontend:** Single HTML template, vanilla JS + CSS animations
- **Audio:** Web Speech API (TTS), AudioContext (sound effects)
- **Fonts:** Google Fonts (Fredoka display, Rubik body/Hebrew)
- **Storage:** Database (game results, progress) + localStorage (fallback)
- **Languages:** Hebrew UI (RTL) + English content (LTR)
- **Testing:** pytest, pytest-cov, pytest-mock

## API Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the learning app |
| GET | `/health` | Health check |
| POST | `/api/game/result` | Save a game result (score + per-word accuracy) |
| GET | `/api/game/progress` | Get total stars, accuracy by game, weak words |
| GET | `/api/game/practiced-words` | Get practiced words since last reset |
| POST | `/api/game/reset` | Reset practiced words for fresh round (stars preserved) |

## Conventions

**Code Standards:**
- Type hints on ALL functions
- Custom exceptions (`backend/exceptions.py`) — never generic Exception
- Logging, not print()
- Pydantic validation for API inputs
- Tests required — mock all external calls

**Workflow (after each code change):**
1. Write code + tests
2. Run ONLY relevant tests (not full suite — CI handles that)
3. Bump version in `backend/defaults.py` (semantic versioning)
4. Update README.md "Recent Updates" (keep 6 items)
5. Ask user to test specific changes

**Versioning:**
- **MINOR** (x.1.x → x.2.x): New games, features, or vocabulary units
- **PATCH** (x.x.1 → x.x.2): Bug fixes, animation tweaks, UI polish

## Gotchas

- **Hebrew:** RTL on container, LTR on English content elements
- **Hebrew + emoji/punctuation:** In RTL context, put emoji BEFORE Hebrew text in source (`⭐ טקסט` not `טקסט ⭐`), and put `!` AFTER Hebrew text in source (`!יאללה` → wrong, `יאללה!` → correct). The browser renders RTL right-to-left, so source-first = visual-right.
- **AudioContext:** Requires user gesture to initialize (welcome button handles this)
- **Web Speech API:** Not available on all browsers — app works without it
- **Google Fonts:** System font fallbacks if CDN unavailable offline
- **localStorage:** Stars persist across sessions under key `ariel_stars`
- **Git push:** First push to new branch needs `--set-upstream`
- **Tests:** NEVER call real APIs — always mock

## Custom Commands

| Command | Description |
|---------|-------------|
| `/new-task [description]` | Analyze task and create implementation plan with agent recommendations |

## Agents

Task-based agents in `.claude/agents/` — use `/new-task` for recommendations.

## Git-Ignored Files (Do NOT include in commits)

These files/folders are git-ignored and should never be committed:
- `docs/architecture/` - Local architecture docs
