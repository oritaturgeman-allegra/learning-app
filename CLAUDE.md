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
| GET | `/` | Serve the landing page |
| GET | `/learning` | Serve the subject picker screen |
| GET | `/learning/{subject}` | Serve the session picker for a subject |
| GET | `/learning/{subject}/{session_slug}` | Serve the game menu for a session |
| GET | `/learning/{session_slug}` | Redirect to `/learning/english/{session_slug}` (backward compat) |
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
3. **BEFORE version bump** — check: Do architecture docs need updating? (`docs/architecture/`) If new API fields, services, routes, data flows, or DB changes → update them. Never skip this step.
4. Bump version in `backend/defaults.py` (semantic versioning)
5. Update README.md "Recent Updates" (keep 6 items)
6. Ask user to test specific changes

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

## /new-task Output Checklist

When running `/new-task`, the output MUST include ALL these sections in order:
1. Task Analysis (type, complexity, priority)
2. Relevant Agents
3. Implementation Plan (phases)
4. Files to Modify/Create
5. Testing Strategy
6. **Documentation Updates Required** — NEVER skip this. State Yes/No for architecture docs and reason.
7. Security Review
8. Potential Issues
9. Next Steps
