# Ariel's English Adventure

Gamified English learning web app for a 9.5-year-old Israeli girl. Teaches vocabulary from Jet 2 textbook (Unit 2) through 4 interactive mini-games with rewards, animations, and sound feedback.

## Commands

```bash
# Run the app — just open in browser
open english-fun.html

# Or serve locally
python3 -m http.server 8000
# Open http://localhost:8000/english-fun.html
```

## Stack

- **Frontend:** Single HTML file, vanilla JS + CSS animations
- **Audio:** Web Speech API (TTS), AudioContext (sound effects)
- **Fonts:** Google Fonts (Fredoka display, Rubik body/Hebrew)
- **Storage:** localStorage for star persistence
- **Languages:** Hebrew UI (RTL) + English content (LTR)
- **Dependencies:** None (no build tools, no backend)

## Key References

| Doc | Purpose |
|-----|---------|
| [docs/roadmap/current-sprint.md](./docs/roadmap/current-sprint.md) | Current sprint tasks |

## App Structure

| Screen | Description |
|--------|-------------|
| Welcome | Animated gradient, "!שלום אריאל", auto-transitions to menu |
| Main Menu | 4 game cards with star counter |
| Game 1: ?מה המילה | Emoji + Hebrew → pick correct English word (10 rounds, +1⭐) |
| Game 2: תרגמי את המשפט | Hebrew sentence → arrange English words (6 rounds, +2⭐) |
| Game 3: האזיני ובחרי | Listen to word → pick matching card (10 rounds, +1⭐) |
| Game 4: ?כן או לא | English sentence → True/False (8 rounds, +1⭐) |
| Complete | Score summary, replay or return to menu |

## Conventions

**Code Standards:**
- Well-commented sections within single HTML file
- CSS custom properties for design tokens
- Structured vocabulary data (easy to add words)
- Semantic HTML with accessibility considerations

**Workflow (after each code change):**
1. Make changes to `english-fun.html`
2. Open in browser and test manually
3. Bump version in `backend/defaults.py` (semantic versioning)
4. Update README.md "Recent Updates" (keep 6 items)
5. Ask user to test specific changes

**Versioning:**
- **MINOR** (x.1.x → x.2.x): New games, features, or vocabulary units
- **PATCH** (x.x.1 → x.x.2): Bug fixes, animation tweaks, UI polish

## Gotchas

- **Hebrew:** RTL on container, LTR on English content elements
- **AudioContext:** Requires user gesture to initialize (welcome button handles this)
- **Web Speech API:** Not available on all browsers — app works without it
- **Google Fonts:** System font fallbacks if CDN unavailable offline
- **localStorage:** Stars persist across sessions under key `ariel_stars`
- **Git push:** First push to new branch needs `--set-upstream`

## Custom Commands

| Command | Description |
|---------|-------------|
| `/new-task [description]` | Analyze task and create implementation plan with agent recommendations |

## Agents

Task-based agents in `.claude/agents/` — use `/new-task` for recommendations.

## Notes for Claude

- Use `/new-task` to create structured implementation plans
- Use Playwright MCP for browser automation and testing
- The app is a single HTML file — no backend needed
- Vocabulary is structured as JS objects — easy to add new units
- Test changes by opening the file in Chrome or Safari

## Git-Ignored Files (Do NOT include in commits)

These files/folders are git-ignored and should never be committed:
- `docs/architecture/` - Local architecture docs

## Legacy Code (Pending Cleanup)

The `backend/`, `frontend/`, `tests/`, `alembic/` directories contain the old Capital Market Newsletter app. These will be removed in a future cleanup task.
